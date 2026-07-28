#!/usr/bin/env python3
"""
bump-source-sha.py — 把 metadata-stale／語意無關 stale 翻譯 frontmatter 升級到 zh latest commit。

Body 已 valid，不重翻只 bump metadata：
  sourceCommitSha → zh latest commit
  sourceContentHash → zh latest contentHash
  sourceBodyHash → zh latest bodyHash（同一個值）

兩種來源：
  1. metadata-stale（REFLEXES #38 第 2 次 instantiation：bodyHash 沒變——trailer /
     footnote URL 之類的變動，body 完全沒動）。預設行為，一直都有。
  2. `--include-punct-only`（2026-07-27，見 reports/semantic-noop-stale-2026-07-27.md）：
     status 判定為 `stale`（bodyHash 真的變了）但 zh diff 本身只是標點/空白正規化——
     半形逗號改全形、句中分號改句號之類——對譯文完全沒有語意影響。判定丟給
     semantic-noop-check.py（單一職責、保守：寧可漏判不可誤判，任何不確定都不算
     no-op）。**這條路徑風險比 metadata-stale 高**（body hash 真的變了，只是變動內容
     被正規化判定為噪音），所以每筆命中的候選在寫入後都會補跑一次
     verify-translation.py 硬 gate；沒過的立刻還原成原內容，不留在「假 fresh」狀態
     （實測：pt/Art/li-poetry-society.md 一例就是靠這道 gate 攔下——它的 zh diff 確實
     只是標點，但譯文本身有跟這次改動無關的既有 passthrough drift，不該被判定為安全
     bump）。預設關閉，需要顯式加旗標。

對 metadata-stale（+ 選配 punct-only-stale）翻譯批次 bump。**不動 body content**。
省下不需要的 cascade translation cost。

Usage:
  python3 bump-source-sha.py                                        # dry-run（無 --apply 就是 dry-run），metadata-stale only
  python3 bump-source-sha.py --apply                                # write
  python3 bump-source-sha.py --apply --lang en                      # 限定 single lang
  python3 bump-source-sha.py --include-punct-only                   # dry-run + 語意無關 stale 判定
  python3 bump-source-sha.py --apply --include-punct-only           # + 寫入（含 post-bump verify gate）
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
KNOWLEDGE = REPO / "knowledge"
NOOP_CHECKER = REPO / "scripts" / "tools" / "lang-sync" / "semantic-noop-check.py"
VERIFY_TRANSLATION = REPO / "scripts" / "tools" / "lang-sync" / "verify-translation.py"
from langs import ALL_TRANSLATION_LANGS
LANGS = ALL_TRANSLATION_LANGS  # SSOT via langs.py (2026-07-18)


def run_status_json() -> dict:
    out = subprocess.check_output(
        ["python3", str(REPO / "scripts/tools/lang-sync/status.py"), "--json", "--no-write"],
        cwd=REPO,
    )
    return json.loads(out.decode())


def find_metadata_stale(status: dict, lang_filter: str | None = None) -> list[dict]:
    """Return list of {lang, zh_path, target_path, new_src_sha, new_content_hash, new_body_hash}."""
    out = []
    by_article = status["byArticle"]
    for zh_path, entry in by_article.items():
        zh_data = entry["zh"]
        for lang, t in entry["translations"].items():
            if lang_filter and lang != lang_filter:
                continue
            if t.get("status") != "metadata-stale":
                continue
            out.append({
                "lang": lang,
                "zh_path": zh_path,
                "target_path": t.get("path", ""),
                "new_src_sha": zh_data["lastCommit"],
                "new_content_hash": zh_data["contentHash"],
                "new_body_hash": zh_data["bodyHash"],
            })
    return out


def find_punct_only_stale(status: dict, lang_filter: str | None = None) -> list[dict]:
    """Like find_metadata_stale, but scans `stale` (real bodyHash drift) entries and
    keeps only the ones semantic-noop-check.py judges as punctuation/whitespace-only
    zh diffs. See module docstring §2 for the risk profile — callers MUST run the
    post-bump verify gate (verify_bump_or_revert) on anything this returns."""
    out = []
    by_article = status["byArticle"]
    for zh_path, entry in by_article.items():
        zh_data = entry["zh"]
        for lang, t in entry["translations"].items():
            if lang_filter and lang != lang_filter:
                continue
            if t.get("status") != "stale":
                continue
            target_path = t.get("path", "")
            if not target_path:
                continue
            r = subprocess.run(
                ["python3", str(NOOP_CHECKER), zh_path, target_path, "--json"],
                cwd=REPO, capture_output=True, text=True,
            )
            try:
                verdict = json.loads(r.stdout) if r.stdout.strip() else {}
            except json.JSONDecodeError:
                verdict = {}
            if not verdict.get("noop"):
                continue
            out.append({
                "lang": lang,
                "zh_path": zh_path,
                "target_path": target_path,
                "new_src_sha": zh_data["lastCommit"],
                "new_content_hash": zh_data["contentHash"],
                "new_body_hash": zh_data["bodyHash"],
                "via": "punct-only-stale",
                "noop_reason": verdict.get("reason"),
            })
    return out


def verify_bump_or_revert(target_md: Path, zh_path: str, target_path: str, original_bytes: bytes) -> tuple[bool, str | None]:
    """Post-bump hard gate for the riskier --include-punct-only path (see module
    docstring). Runs verify-translation.py against the just-written file; on any
    HARD fail, restores original_bytes so the article stays exactly as it was
    (still 'stale', will fall through to the normal translate pipeline next run)
    instead of being silently left in a false-fresh state. Returns (kept, reason)."""
    r = subprocess.run(
        ["python3", str(VERIFY_TRANSLATION), zh_path, target_path, "--json"],
        cwd=REPO, capture_output=True, text=True,
    )
    try:
        out = json.loads(r.stdout) if r.stdout.strip() else {"fails": -1}
    except json.JSONDecodeError:
        out = {"fails": -1}
    fails = out.get("fails", -1)
    if fails == 0:
        return True, None
    target_md.write_bytes(original_bytes)
    return False, f"verify-translation fails={fails}"


def bump_one(target_md: Path, new_sha: str, new_content_hash: str, new_body_hash: str, apply: bool) -> bool:
    """Update frontmatter sourceCommitSha + sourceContentHash + sourceBodyHash. Returns True if changed."""
    content = target_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return False
    end = content.find("---", 3)
    if end == -1:
        return False
    fm_text = content[3:end]
    body = content[end + 3:]

    # Replace or insert each key
    def upsert(text: str, key: str, val: str) -> str:
        if re.search(rf"^{re.escape(key)}:\s.*$", text, flags=re.MULTILINE):
            return re.sub(rf"^{re.escape(key)}:\s.*$", f"{key}: '{val}'", text, count=1, flags=re.MULTILINE)
        # Append at end of frontmatter
        return text.rstrip() + f"\n{key}: '{val}'\n"

    new_fm = fm_text
    new_fm = upsert(new_fm, "sourceCommitSha", new_sha)
    new_fm = upsert(new_fm, "sourceContentHash", new_content_hash)
    new_fm = upsert(new_fm, "sourceBodyHash", new_body_hash)

    new_content = "---" + new_fm + "---" + body
    if new_content == content:
        return False
    if apply:
        target_md.write_text(new_content, encoding="utf-8")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--lang", default=None)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--include-punct-only", action="store_true",
                     help="also bump `stale` (real bodyHash drift) entries whose zh diff is "
                          "punctuation/whitespace-only per semantic-noop-check.py (2026-07-27, "
                          "default off — see reports/semantic-noop-stale-2026-07-27.md)")
    args = ap.parse_args()

    print("📊 Fetching status.json...")
    status = run_status_json()
    targets = find_metadata_stale(status, args.lang)
    for t in targets:
        t["via"] = "metadata-stale"
    print(f"📋 {len(targets)} metadata-stale translation(s) to bump")

    if args.include_punct_only:
        print("🔍 checking `stale` entries for punctuation-only zh diffs (semantic-noop-check.py)...")
        punct_targets = find_punct_only_stale(status, args.lang)
        print(f"📋 {len(punct_targets)} punct-only-stale translation(s) additionally eligible")
        targets += punct_targets

    if not targets:
        print("✅ Nothing to bump")
        return

    counts = {"bumped": 0, "skipped": 0, "reverted": 0}
    by_via = {"metadata-stale": 0, "punct-only-stale": 0}
    for t in targets:
        target_md = KNOWLEDGE / t["target_path"]
        if not target_md.exists():
            counts["skipped"] += 1
            continue
        original_bytes = target_md.read_bytes() if (args.apply and t["via"] == "punct-only-stale") else None
        changed = bump_one(target_md, t["new_src_sha"], t["new_content_hash"], t["new_body_hash"], args.apply)
        if not changed:
            counts["skipped"] += 1
            continue

        if args.apply and t["via"] == "punct-only-stale":
            kept, reason = verify_bump_or_revert(target_md, t["zh_path"], t["target_path"], original_bytes)
            if not kept:
                counts["reverted"] += 1
                if not args.quiet:
                    print(f"  ↩ reverted {t['lang']}/{t['target_path'].replace(t['lang']+'/', '')} — {reason}")
                continue

        counts["bumped"] += 1
        by_via[t["via"]] += 1
        if not args.quiet:
            action = "✓ bumped" if args.apply else "~ would-bump"
            tag = " [punct-only]" if t["via"] == "punct-only-stale" else ""
            print(f"  {action} {t['lang']}/{t['target_path'].replace(t['lang']+'/', '')} → {t['new_src_sha'][:8]}{tag}")

    print()
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"📊 bump-source-sha [{mode}]")
    print(f"  {'bumped' if args.apply else 'would-bump'}: {counts['bumped']} "
          f"(metadata-stale={by_via['metadata-stale']}, punct-only-stale={by_via['punct-only-stale']})")
    print(f"  skipped: {counts['skipped']}")
    if args.include_punct_only:
        print(f"  reverted (post-bump verify fail): {counts['reverted']}")


if __name__ == "__main__":
    main()
