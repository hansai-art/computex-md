#!/usr/bin/env python3
"""rescue-orphans.py — 搶救工作區裡「已翻好但沒被 commit」的譯文。

為什麼有這支（2026-07-27，同日第三次手動做同一件事 → 儀器化門檻到了）：
babel-dispatch 每 50 篇才 commit 一次，所以產線被重啟／機器重開時，工作區
常留著幾十到幾百篇「通過閘門但還沒進 git」的譯文。它們是已經燒掉的算力，
卻不算進覆蓋率。

但重啟也把 report.jsonl 的閘門記錄清掉了，所以**不能假設它們通過過**——
唯一誠實的路是逐篇重跑三重驗證（跟 dispatcher 同一套尺：verify-translation
／cjk-leak-check／article-health --profile=pre-commit），通過才收。

用法：
    python3 scripts/tools/lang-sync/rescue-orphans.py            # 驗證並印報告
    python3 scripts/tools/lang-sync/rescue-orphans.py --commit   # 通過的直接 commit

排除：並行 session 正在寫的檔案（--exclude 可加關鍵字，預設排除苯駢芘）。
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
LANGS = ("en", "ja", "ko", "es", "fr", "vi", "id", "pt", "hi", "ar", "ru")


def orphans(exclude: list[str]) -> list[str]:
    r = subprocess.run(["git", "status", "--porcelain", "knowledge/"],
                       cwd=REPO, capture_output=True, text=True)
    out = []
    for line in r.stdout.splitlines():
        if not line[:2] in ("??", " M", "M "):
            continue
        p = line[3:].strip()
        if not any(p.startswith(f"knowledge/{l}/") for l in LANGS):
            continue
        if any(x in p for x in exclude):
            continue
        if p.endswith(".md"):
            out.append(p)
    return sorted(out)


def zh_source(trans_path: str) -> str | None:
    """從譯文 frontmatter 的 translatedFrom 反查 zh 來源。"""
    import re
    try:
        t = (REPO / trans_path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = re.search(r"^translatedFrom:\s*['\"]?(.+?)['\"]?\s*$", t, re.M)
    if not m:
        return None
    rel = m.group(1).strip()
    for cand in (rel, f"knowledge/{rel}"):
        if (REPO / cand).exists():
            return cand
    return None


def verify_trio(trans_path: str) -> tuple[bool, str]:
    """dispatcher 用的同一套三重驗證——刻意不簡化，兩套尺分歧比多花幾秒更貴。"""
    # dispatcher 的 collect_and_filter_groups 會丟掉 slug 解析失敗的任務，這條路
    # 徑當初沒跟著收斂，於是 2026-07-27 的搶救把 8 個 TBD-NEEDS-SLUG 檔收進版控
    # ——內容其實是四篇好譯文，卻落在同一個佔位檔名上：同分類同語言的下一篇會
    # 直接覆蓋掉前一篇，而且網址是 /es/lifestyle/tbd-needs-slug。譯文本身沒問題，
    # 是路徑沒問題可言，所以擋在三重驗證之前。要收下它得先給文章一個真 slug
    # （knowledge/_slug-map.json）再重跑產線。同型病要 grep 全部呼叫端。
    if "TBD-NEEDS-SLUG" in trans_path:
        return False, "slug 未解析（需 _slug-map.json 條目）"
    zh = zh_source(trans_path)
    if not zh:
        return False, "translatedFrom 無法解析"
    r1 = subprocess.run(["python3", "scripts/tools/lang-sync/verify-translation.py",
                         zh, trans_path, "--json"], cwd=REPO, capture_output=True, text=True)
    import json
    try:
        fails = json.loads(r1.stdout).get("fails", 1)
    except Exception:
        fails = -1
    if fails != 0:
        return False, f"verify={fails}"
    r2 = subprocess.run(["python3", "scripts/tools/lang-sync/cjk-leak-check.py", trans_path],
                        cwd=REPO, capture_output=True, text=True)
    if r2.returncode != 0:
        return False, "leak"
    r3 = subprocess.run(["python3", "scripts/tools/article-health.py", trans_path,
                         "--profile=pre-commit", "--quiet"], cwd=REPO, capture_output=True, text=True)
    if "passed=False" in r3.stdout:
        return False, "health"
    return True, "ok"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true", help="通過的直接 commit")
    ap.add_argument("--exclude", nargs="*", default=["苯駢芘"],
                    help="排除關鍵字（並行 session 正在寫的檔案）")
    ap.add_argument("--limit", type=int, default=0, help="只驗前 N 篇（測試用）")
    ap.add_argument(
        "--quarantine-failed",
        action="store_true",
        help="把未過 gate 的衍生檔移到 /tmp 隔離，避免 status.py 誤算 fresh",
    )
    args = ap.parse_args()

    items = orphans(args.exclude)
    if args.limit:
        items = items[:args.limit]
    print(f"▸ 待驗孤兒譯文：{len(items)} 篇", flush=True)

    passed, failed = [], {}
    for i, p in enumerate(items, 1):
        ok, reason = verify_trio(p)
        if ok:
            passed.append(p)
        else:
            failed.setdefault(reason, []).append(p)
        if i % 10 == 0 or i == len(items):
            print(f"   {i}/{len(items)}  通過 {len(passed)}", flush=True)

    print(f"\n▸ 通過 {len(passed)} / 擋下 {sum(len(v) for v in failed.values())}")
    for reason, ps in sorted(failed.items(), key=lambda kv: -len(kv[1])):
        print(f"   {len(ps):3}  {reason}")

    if failed and args.quarantine_failed:
        # 未過 gate 的 untracked 譯文若留在 knowledge/，status.py 仍會把它們
        # 算成 fresh，dispatcher 也就看不到原本的 missing 任務。搬到 /tmp
        # 保留診斷樣本，同時讓缺口回到誠實狀態；不用 unlink，避免丟掉已燒算力。
        qroot = Path("/tmp") / (
            "babel-rejected-orphans-" + datetime.now().strftime("%Y%m%d-%H%M%S")
        )
        moved = 0
        for ps in failed.values():
            for rel in ps:
                src = REPO / rel
                if not src.exists():
                    continue
                dst = qroot / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                src.replace(dst)
                moved += 1
        print(f"🧪 已隔離 {moved} 篇未過 gate 的衍生檔：{qroot}")

    if passed and args.commit:
        # 精確路徑 add——絕不 `git add -A`，工作區有並行 session 的檔案
        subprocess.run(["git", "add", "--"] + passed, cwd=REPO, check=True)
        msg = (f"🧬 [semiont] babel: 搶救 {len(passed)} 篇孤兒譯文\n\n"
               f"產線重啟留在工作區、未達 commit 門檻的譯文。閘門記錄隨重啟\n"
               f"清空，故逐篇重跑三重驗證後才收——通過 {len(passed)}、"
               f"擋下 {sum(len(v) for v in failed.values())}。")
        subprocess.run(["git", "commit", "-q", "-m", msg], cwd=REPO)
        print(f"✅ 已 commit {len(passed)} 篇")
    elif passed:
        print("   （加 --commit 收下）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
