#!/usr/bin/env python3
"""
diary-translation-audit.py — Instrumented integrity gate for diary translations.

The diary cascade tool (diary-translate.py) only gates on `size >= 1024 bytes`,
which cannot catch the silent failure modes of bulk local-LLM translation:
truncation (large diaries near num_ctx), refusal stubs > 1KB, dropped
sections/footers, structural drift, and LLM preamble leak.

This audit compares every translation against its zh-TW source on structural
and integrity dimensions, classifying issues CRITICAL (silent content loss /
refusal) vs WARNING (structural drift). Output: human report + JSON artifact
(reports/diary-translation-audit-<date>.json passed via --out).

Usage:
  python3 diary-translation-audit.py --langs en,ja,ko,es,fr
  python3 diary-translation-audit.py --langs en --verbose
  python3 diary-translation-audit.py --langs en,ja,ko,es,fr --out /tmp/audit.json
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

# Skip files written within this window — they may still be mid-write (the
# cascade worker is actively streaming the translation), which yields bogus
# length ratios. Audit only settled output.
SETTLE_SECS = 15

REPO = Path(__file__).resolve().parent.parent.parent.parent
DIARY_ZH = REPO / "docs/semiont/diary"

# Per-lang plausible length ratio (tgt_chars / src_chars). CJK→alphabetic
# expands; CJK→ja/ko stays dense. Bounds are generous — only flag clear loss.
LEN_BOUNDS = {
    "en": (0.7, 2.8), "es": (0.8, 3.0), "fr": (0.8, 3.0),
    "ja": (0.45, 1.6), "ko": (0.5, 1.7),
}
DEFAULT_BOUNDS = (0.45, 3.0)

REFUSAL_RE = re.compile(
    r"\b(I cannot|I can't|I'm unable|I am unable|cannot translate|can not translate|"
    r"as an AI|I apologize|I'm sorry|I am sorry|unable to (?:provide|assist|translate)|"
    r"I'm not able)\b|无法|對不起|抱歉，我",
    re.I,
)
PREAMBLE_RE = re.compile(
    r"^\s*(here is|here's|below is|the following is|translation:|sure[,!]|"
    r"certainly[,!]|of course[,!]|i'll translate|here are)",
    re.I,
)


def count_headings(t): return len(re.findall(r"^#{1,6}\s", t, re.M))
def count_blockquotes(t): return len(re.findall(r"^\s*>", t, re.M))
def count_fences(t): return t.count("```")
def count_footnote_refs(t): return len(re.findall(r"\[\^[^\]]+\]", t))
def count_footer_meta(t):
    # italic single-line footer blocks: _..._  (the diary reflective metadata)
    return len(re.findall(r"^_[^_].*_\s*$", t, re.M))
def count_media(t):
    return len(re.findall(r"!\[[^\]]*\]\(|<img|/api/|\.png|\.svg|\.jpg", t))
def has_sig(t): return "🧬" in t


def ends_cleanly(t):
    """Truncation heuristic: does the body end on terminal punctuation/structure?
    🧬 is the canonical diary ending (183/206 diaries close on a bare signature)."""
    tail = t.rstrip()
    if not tail:
        return False
    last = tail[-1]
    # terminal punctuation, closing quote/paren, italic footer underscore, 🧬 sig
    return last in '.!?。！？」』）)"”_*`>-:🧬' or tail.endswith("---")


def audit_one(diary, lang):
    src_p = DIARY_ZH / diary
    tgt_p = DIARY_ZH / lang / diary
    if not tgt_p.exists() or tgt_p.stat().st_size < 1:
        return None  # not translated yet
    if time.time() - tgt_p.stat().st_mtime < SETTLE_SECS:
        return {"in_flight": True}  # mid-write — re-audit after settle
    src = src_p.read_text(encoding="utf-8", errors="replace")
    tgt = tgt_p.read_text(encoding="utf-8", errors="replace")

    crit, warn = [], []

    # 1. refusal stub — only real if the output is DOMINATED by the refusal
    # (short stub). A refusal phrase mid-body in a full-length structured
    # translation is the diary legitimately QUOTING a refusal: lang-sync diaries
    # quote PRC '无法给到相关内容' (simplified 无法 only ever appears as a faithful
    # quote in a Traditional-Chinese-sourced corpus), and "I cannot" is ordinary
    # English prose ("a good idea I cannot execute"). Gate on length to separate.
    m = REFUSAL_RE.search(tgt)
    if m and len(tgt) < 800:
        crit.append(f"refusal-stub:'{m.group(0)}'(len={len(tgt)})")

    # 2. length ratio — content drop or hallucination
    lo, hi = LEN_BOUNDS.get(lang, DEFAULT_BOUNDS)
    ratio = len(tgt) / max(len(src), 1)
    if ratio < lo:
        crit.append(f"length-low:{ratio:.2f}<{lo}")
    elif ratio > hi:
        warn.append(f"length-high:{ratio:.2f}>{hi}")

    # 3. truncation — footer metadata dropped + non-clean end
    src_footers = count_footer_meta(src)
    tgt_footers = count_footer_meta(tgt)
    if src_footers >= 1 and tgt_footers == 0:
        crit.append(f"footer-dropped:{src_footers}→0")
    # only a truncation if the SOURCE ended cleanly but the translation didn't
    # (source complete, output cut) — avoids flagging diaries whose own ending
    # is non-terminal by style
    if ends_cleanly(src) and not ends_cleanly(tgt):
        crit.append("truncation:non-terminal-end")

    # 4. signature lost
    if has_sig(src) and not has_sig(tgt):
        warn.append("signature-lost:🧬")

    # 5. structural drift — headings
    sh, th = count_headings(src), count_headings(tgt)
    if abs(sh - th) > max(1, sh // 5):
        warn.append(f"heading-drift:{sh}→{th}")

    # 6. blockquote drop
    sb, tb = count_blockquotes(src), count_blockquotes(tgt)
    if sb >= 2 and tb < sb * 0.5:
        warn.append(f"blockquote-drop:{sb}→{tb}")

    # 7. code fence imbalance (broken/truncated fence)
    if count_fences(tgt) % 2 != 0:
        crit.append(f"fence-odd:{count_fences(tgt)}")

    # 8. footnote refs mismatch (rare but exact when present)
    sf, tf = count_footnote_refs(src), count_footnote_refs(tgt)
    if sf >= 1 and tf < sf:
        warn.append(f"footnote-drop:{sf}→{tf}")

    # 9. media refs dropped/broken
    sm, tm = count_media(src), count_media(tgt)
    if sm >= 1 and tm < sm:
        warn.append(f"media-drop:{sm}→{tm}")

    # 10. preamble leak (first non-empty line)
    first = next((ln for ln in tgt.splitlines() if ln.strip()), "")
    if PREAMBLE_RE.match(first):
        warn.append(f"preamble:'{first[:40]}'")

    if not crit and not warn:
        return {"ok": True, "ratio": round(ratio, 2)}
    return {"ok": False, "critical": crit, "warning": warn, "ratio": round(ratio, 2),
            "src_chars": len(src), "tgt_chars": len(tgt)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--langs", default="en,ja,ko,es,fr")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--out", help="write JSON report to path")
    args = ap.parse_args()
    langs = args.langs.split(",")

    diaries = sorted(p.name for p in DIARY_ZH.glob("*.md"))
    report = {"total_audited": 0, "clean": 0, "critical": 0, "warning_only": 0,
              "in_flight": 0, "per_lang": {}, "flagged": []}

    for lang in langs:
        lc = {"audited": 0, "clean": 0, "critical": 0, "warning_only": 0}
        for diary in diaries:
            res = audit_one(diary, lang)
            if res is None:
                continue
            if res.get("in_flight"):
                report["in_flight"] += 1
                continue
            lc["audited"] += 1
            report["total_audited"] += 1
            if res["ok"]:
                lc["clean"] += 1
                report["clean"] += 1
            else:
                rec = {"lang": lang, "diary": diary, **res}
                report["flagged"].append(rec)
                if res["critical"]:
                    lc["critical"] += 1
                    report["critical"] += 1
                else:
                    lc["warning_only"] += 1
                    report["warning_only"] += 1
        report["per_lang"][lang] = lc

    # Print report
    print(f"📋 Diary translation integrity audit — {report['total_audited']} translations audited")
    print(f"  ✅ clean: {report['clean']}  🔴 critical: {report['critical']}  🟡 warning-only: {report['warning_only']}")
    print("\nPer lang (audited / clean / 🔴crit / 🟡warn):")
    for lang, lc in report["per_lang"].items():
        print(f"  {lang}: {lc['audited']} / {lc['clean']} / {lc['critical']} / {lc['warning_only']}")

    crit_flags = [f for f in report["flagged"] if f["critical"]]
    if crit_flags:
        print(f"\n🔴 CRITICAL ({len(crit_flags)}) — silent content loss / refusal:")
        for f in crit_flags[:40]:
            print(f"  [{f['lang']}] {f['diary']} (ratio {f['ratio']}): {', '.join(f['critical'])}")
        if len(crit_flags) > 40:
            print(f"  … +{len(crit_flags)-40} more")

    if args.verbose:
        warn_flags = [f for f in report["flagged"] if not f["critical"]]
        if warn_flags:
            print(f"\n🟡 WARNING ({len(warn_flags)}):")
            for f in warn_flags[:60]:
                print(f"  [{f['lang']}] {f['diary']} (ratio {f['ratio']}): {', '.join(f['warning'])}")

    if args.out:
        Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2))
        print(f"\n💾 JSON report → {args.out}")

    # Exit non-zero if any critical (gate semantics)
    sys.exit(1 if report["critical"] else 0)


if __name__ == "__main__":
    main()
