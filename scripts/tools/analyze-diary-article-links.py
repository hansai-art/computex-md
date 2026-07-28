#!/usr/bin/env python3
"""analyze-diary-article-links.py — retroactively reconstruct which diary belongs
to which knowledge/ article, so the relatedDiary back-link can be collectively
back-filled (READ-ONLY analysis; writing is done by sync-diary-links.py).

## Why

sync-diary-links.py (2026-06-24) instruments the diary→article relatedDiary
back-link going FORWARD (every new write-session links its diary). But 246
historical diaries predate that gate, and only 8 zh articles carry a
relatedDiary today. 哲宇 directive: deep-research which diaries+articles are
connected and back-fill them collectively — WITHOUT moving any article's
/latest position (no fake-fresh edit date).

This tool does the RECONSTRUCTION half (the hard "which-diary-belongs-to-which-
article" inference) and emits a tiered plan. It writes nothing to articles.

## How it infers the pairing (multi-signal, falsifiable)

For each diary docs/semiont/diary/{slug}.md:

  S1 git time-window (primary, era-robust): the diary's own add-commit time T
     anchors the session. knowledge/ zh articles ADDED or MODIFIED by *content*
     commits (rewrite/evolve/heal/NEW — cosmetic/routine/babel/spore/media
     filtered out) in (T - LOOKBACK, T + GRACE], bounded below by the previous
     diary's commit (session boundary) to limit parallel-session bleed.
     ADDED  → strong (a NEW article shipped in this session).
     MODIFIED → weaker (could be an EVOLVE, or an incidental cross-link edit).

  S2 session-id in commit subject (booster): commits whose subject contains the
     diary's session-id (the modern memory-commit convention) — unambiguous when
     present.

  S3 paired memory file (corroboration): memory/{slug}.md body references to
     knowledge/Cat/X.md or /cat/slug/ URLs.

  S4 slug topic hint (disambiguator): the diary handle with the timestamp +
     type-suffix stripped (龜山島-rewrite → 龜山島, 呂冠緯-evolve → 呂冠緯), matched
     against an existing zh article filename. Romanised handles (xiaohudui,
     kuma-academy) won't match — that's fine, they fall to S1/S3.

## Tiering (REFLEXES #31 — corroborate, don't just confirm)

  A (auto-safe): exactly ONE article, and ≥2 signals agree (or a single ADDED
     article that also slug- or memory-matches). Safe to back-fill unattended.
  B (likely): one article from a single strong signal (ADDED-in-window, or
     session-id co-commit) with no contradiction. Back-fill recommended, quick
     human skim.
  C (review): multiple candidate articles (batch/Merge sessions), generic handle
     (manual / greek) with only weak MODIFIED hits, or contradictory signals.
     Needs 哲宇 judgement.
  META (skip): no knowledge article in scope — a pure consciousness diary
     (manifesto-hope / multicore-git / 跑了不等於到了). Nothing to link.

## Output

  --report   human-readable tiered table (default)
  --json OUT machine plan (consumed by a back-fill driver / re-run)
  --plan     emit ready-to-run sync-diary-links.py commands for tier(s)
  --tier A   restrict --plan/--json to given tiers (repeatable; default A,B)

## Edit-date safety (the other half — NOT done here)

Back-filling relatedDiary edits article frontmatter. /latest + sitemap lastmod +
JSON-LD dateModified all derive from src/data/content-dates.json, which takes the
newest NON-COSMETIC commit per article (scripts/core/build-content-dates.mjs).
That generator already excludes sporeLinks-pointer + media-only commits for this
exact reason ("補圖不該把文章擠到最新文章今天"). relatedDiary is the same kind of
pointer → add it to the exclusion regex and commit the back-fill with a matching
subject; content-dates.json will then ignore it and no article moves in /latest.
Verify with a before/after diff of content-dates.json (must be empty).

2026-06-24 | born from 哲宇 directive「回溯分析哪些日記＋文章是連在一起的，集體回補，不動編輯日期」
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DIARY_DIR = REPO / "docs/semiont/diary"
MEMORY_DIR = REPO / "docs/semiont/memory"
KNOWLEDGE_ROOT = REPO / "knowledge"
MIRROR_LANGS = {"en", "ja", "ko", "es", "fr", "zh-TW"}

LOOKBACK = timedelta(hours=8)   # a deep rewrite (research→write→ship→diary) can span this
GRACE = timedelta(minutes=20)   # diary sometimes commits a hair before the finale memory

# A commit subject that is NOT a real article-content event (mirror of
# build-content-dates.mjs COSMETIC/SPORE_POINTER/MEDIA_ONLY — kept in sync by intent).
NON_CONTENT = re.compile(
    r"(\[routine\]|babel|prettier|\blint\b|chore|format-only|translate\(|apostrophe"
    r"|繁簡|simplified-char|WebP|媒體增補|媒體落地|影像後處理|image-ingest|land-media"
    r"|migrate-images|spore|harvest|sporeLinks|孢子|data.?refresh|refresh:|memory:"
    r"|memory\+diary|diary:|wire:|distill|evolve: (?:CORRECTION|DIARY-PIPELINE|REWRITE)"
    r"|relatedDiary)",
    re.I,
)

# Strip emoji + timestamp + type suffix to get the topic hint from a diary handle.
_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-(?:\d{6}-)?")
_SUFFIX_RE = re.compile(
    r"-(rewrite|evolve|media-evolve|i18n|recat|heal|merge|new|draft)$", re.I
)


def sh(args: list[str]) -> str:
    return subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=REPO, text=True, capture_output=True,
    ).stdout


def zh_article_slugs() -> dict[str, str]:
    """{slug: 'knowledge/Cat/slug.md'} for every zh canonical article."""
    out: dict[str, str] = {}
    for md in KNOWLEDGE_ROOT.rglob("*.md"):
        rel = md.relative_to(KNOWLEDGE_ROOT)
        if not rel.parts or rel.parts[0] in MIRROR_LANGS:
            continue
        if len(rel.parts) != 2 or rel.parts[1].startswith("_"):
            continue
        out[md.stem] = str(md.relative_to(REPO))
    return out


def parse_path_to_zh_slug(path: str) -> str | None:
    m = re.match(r"knowledge/([^/]+)/(.+)\.md$", path)
    if not m or m.group(1) in MIRROR_LANGS:
        return None
    return m.group(2)


def diary_add_time(rel_path: str) -> datetime | None:
    out = sh(["log", "--diff-filter=A", "--format=%aI", "--", rel_path]).strip().splitlines()
    if not out:
        out = sh(["log", "--format=%aI", "--", rel_path]).strip().splitlines()
    if not out:
        return None
    return datetime.fromisoformat(out[-1])  # oldest = first add


def existing_related(zh_articles: dict[str, str]) -> set[str]:
    """Articles that already carry a relatedDiary block (skip — idempotent)."""
    have = set()
    for slug, rel in zh_articles.items():
        txt = (REPO / rel).read_text(encoding="utf-8", errors="ignore")
        fm_end = txt.find("\n---", 3)
        if "relatedDiary:" in (txt[: fm_end if fm_end > 0 else 4000]):
            have.add(slug)
    return have


def window_signals(t: datetime, prev_t: datetime | None, zh: dict[str, str]):
    """Return {slug: {'added'|'modified', subjects:[...]}} for content commits in window."""
    lo = t - LOOKBACK
    if prev_t and prev_t > lo:
        lo = prev_t  # don't cross the previous diary's session boundary
    hi = t + GRACE
    log = sh([
        "log", "--no-merges",
        f"--since={lo.isoformat()}", f"--until={hi.isoformat()}",
        "--name-status", "--format=%x00COMMIT%x00%aI%x00%s", "--", "knowledge/",
    ])
    res: dict[str, dict] = {}
    subj, is_content = "", False
    for raw in log.split("\0"):
        if raw == "COMMIT":
            continue
        chunk = raw.strip("\n")
        if not chunk:
            continue
        # a COMMIT marker is followed by "<aI>\x00<subject>" — detect by the date head
        m = re.match(r"^(\d{4}-\d{2}-\d{2}T[\d:+\-]+)\x00(.*)$", chunk, re.S)
        if m:
            subj = m.group(2).splitlines()[0]
            is_content = not NON_CONTENT.search(subj)
            continue
        for line in chunk.splitlines():
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            status, path = parts[0], parts[-1]
            slug = parse_path_to_zh_slug(path)
            if not slug or slug not in zh:
                continue
            if not is_content:
                continue
            kind = "added" if status.startswith("A") else "modified"
            e = res.setdefault(slug, {"kind": "modified", "subjects": []})
            if kind == "added":
                e["kind"] = "added"
            e["subjects"].append(subj)
    return res


# A co-commit only proves a diary↔article pairing if the commit is a genuine
# ARTICLE-WRITE event. Spore-ship / babel / pipeline-evolve commits also touch
# article frontmatter while carrying the session-id, but the diary is NOT about
# that article (2026-06-24 falsification: 周蕙 RESHIPPED spore, 外省人 bundled into
# 巴別塔 evolve, drone spore-fix — all false). Require a positive write marker.
ARTICLE_WRITE = re.compile(r"(rewrite:|\bEVOLVE\b|\bNEW\b|深度文)")
NOT_WRITE = re.compile(r"(spore|harvest|孢子|babel|巴別塔|translate|繁簡|prettier|\blint\b|data.?refresh)", re.I)


def sessionid_cocommit(session_id: str, zh: dict[str, str]) -> set[str]:
    """zh articles touched by an ARTICLE-WRITE commit carrying this session-id."""
    # Each commit → one "\0" token shaped "<subject>\n<file>\n<file>…" (after a
    # leading "C" marker token we skip).
    out = sh(["log", "--all", f"--grep={session_id}", "--name-only", "--format=%x00%s"])
    found = set()
    for raw in out.split("\0"):
        lines = raw.strip("\n").splitlines()
        if not lines:
            continue
        subject = lines[0]
        keep = bool(ARTICLE_WRITE.search(subject)) and not NOT_WRITE.search(subject)
        if not keep:
            continue
        for line in lines[1:]:
            slug = parse_path_to_zh_slug(line.strip())
            if slug and slug in zh:
                found.add(slug)
    return found


def memory_refs(slug: str, zh: dict[str, str]) -> set[str]:
    mem = MEMORY_DIR / f"{slug}.md"
    if not mem.exists():
        return set()
    txt = mem.read_text(encoding="utf-8", errors="ignore")
    found = set()
    for m in re.finditer(r"knowledge/[^/\s]+/([^/\s)]+)\.md", txt):
        if m.group(1) in zh:
            found.add(m.group(1))
    return found


def slug_hint(diary_slug: str, zh: dict[str, str]) -> str | None:
    handle = _TS_RE.sub("", diary_slug)
    handle = _SUFFIX_RE.sub("", handle).strip()
    return handle if handle in zh else None


def analyze():
    zh = zh_article_slugs()
    already = existing_related(zh)
    diaries = sorted(
        p for p in DIARY_DIR.glob("*.md")
        if not re.search(r"README|index|template|TEMPLATE", p.name)
    )
    # precompute each diary's add-time for session-boundary chaining
    times: dict[str, datetime | None] = {}
    for p in diaries:
        times[p.stem] = diary_add_time(str(p.relative_to(REPO)))

    ordered = sorted([d for d in diaries if times[d.stem]], key=lambda p: times[p.stem])
    prev_by_stem: dict[str, datetime | None] = {}
    last = None
    for p in ordered:
        prev_by_stem[p.stem] = last
        last = times[p.stem]

    results = []
    for p in diaries:
        slug = p.stem
        t = times[slug]
        rec = {"diary": slug, "tier": "META", "articles": [], "signals": {}, "candidates": {}}
        if not t:
            results.append(rec); continue

        win = window_signals(t, prev_by_stem.get(slug), zh)
        co = sessionid_cocommit(slug, zh)
        mem = memory_refs(slug, zh)
        hint = slug_hint(slug, zh)

        cand: dict[str, set] = {}
        for s, e in win.items():
            cand.setdefault(s, set()).add("added" if e["kind"] == "added" else "modified")
        for s in co:
            cand.setdefault(s, set()).add("cocommit")
        for s in mem:
            cand.setdefault(s, set()).add("memory")
        if hint:
            cand.setdefault(hint, set()).add("slug")

        rec["candidates"] = {s: sorted(sig) for s, sig in cand.items()}
        rec["signals"] = {
            "window": {s: e["kind"] for s, e in win.items()},
            "cocommit": sorted(co), "memory": sorted(mem), "slug": hint,
        }

        # score per candidate
        def strength(sig: set) -> int:
            sc = 0
            if "added" in sig: sc += 3
            if "cocommit" in sig: sc += 3
            if "slug" in sig: sc += 2
            if "memory" in sig: sc += 2
            if "modified" in sig: sc += 1
            return sc

        scored = sorted(cand.items(), key=lambda kv: strength(kv[1]), reverse=True)
        rec["articles"] = [s for s, _ in scored]

        # A "strong" candidate has ≥1 of added/cocommit/slug (strength ≥ 3 with the
        # slug+modified combo, or any single added/cocommit). Weak = modified-only:
        # incidental cross-link edits to a neighbour article, NOT this diary's subject.
        # REFLEXES #31: never auto-write weak-only candidates.
        strong_cands = [s for s, sig in scored if ({"added", "cocommit", "slug"} & sig)]

        if not strong_cands:
            # no strong signal anywhere: META if nothing at all, else weak-only → review
            rec["tier"] = "META" if not scored else "C"
        elif len(strong_cands) == 1:
            sig = cand[strong_cands[0]]
            rec["tier"] = "A" if len(sig) >= 2 else "B"  # corroborated → A, single signal → B
        else:
            rec["tier"] = "C"  # multiple strong candidates = batch/multi-article session, 哲宇 picks

        # write-set: only strong candidates, minus already-linked (idempotent)
        rec["already_linked"] = [s for s in strong_cands if s in already]
        rec["to_write"] = [s for s in strong_cands if s not in already]
        results.append(rec)

    return results, zh, already


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None, metavar="OUT")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--tier", action="append", default=[])
    ap.add_argument("--show", default=None, help="print full signals for one diary slug")
    args = ap.parse_args()

    results, zh, already = analyze()
    tiers = [t.upper() for t in (args.tier or ["A", "B"])]

    if args.show:
        r = next((x for x in results if x["diary"] == args.show), None)
        print(json.dumps(r, ensure_ascii=False, indent=2)); return 0

    counts = {}
    for r in results:
        counts[r["tier"]] = counts.get(r["tier"], 0) + 1

    print("===== diary↔article link reconstruction =====")
    print(f"  diaries analyzed : {len(results)}")
    print(f"  zh articles      : {len(zh)}  (already relatedDiary: {len(already)})")
    print(f"  tiers            : " + "  ".join(f"{k}={counts.get(k,0)}" for k in ["A","B","C","META"]))
    writes = sum(len(r["to_write"]) for r in results if r["tier"] in ("A","B"))
    print(f"  A+B article writes (fresh, excl. already-linked): {writes}")
    print()

    for tier in ["A", "B", "C"]:
        rows = [r for r in results if r["tier"] == tier and r["to_write"]]
        if not rows:
            continue
        print(f"── Tier {tier} ({len(rows)}) " + "─" * 40)
        for r in rows:
            arts = ", ".join(r["to_write"][:4]) + ("…" if len(r["to_write"]) > 4 else "")
            sig = "+".join(sorted({s for sigs in r["candidates"].values() for s in sigs}))
            print(f"  {r['diary'][:46]:46}  → {arts}   [{sig}]")
        print()

    if args.json:
        Path(args.json).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  wrote {args.json}")

    if args.plan:
        print("\n── back-fill commands (tiers " + ",".join(tiers) + ") " + "─" * 24)
        for r in results:
            if r["tier"] not in tiers:
                continue
            for art in r["to_write"]:
                print(f"python3 scripts/tools/sync-diary-links.py --diary {r['diary']} --article {art} --apply")

    return 0


if __name__ == "__main__":
    sys.exit(main())
