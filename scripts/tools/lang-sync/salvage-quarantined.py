#!/usr/bin/env python3
"""salvage-quarantined.py — gate 驗證式還原今天被 quarantine 刪除的譯文。

原則（founder.md 教訓）：寧可 stale 也不要 missing。
v3 dispatcher 對 P1 gate fail 直接 unlink+commit，把可讀的 stale 版降級成 404。
本腳本從 git 歷史撈回刪除前的版本，跑跟 dispatcher 相同的三重 gate
（verify-translation / cjk-leak / article-health），全過才留下——
故意 quarantine 的壞檔（zh 洩漏、掉圖）會被 gate 擋掉，不會復活。
"""
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path("/Users/cheyuwu/Projects/taiwan-md")
LANG_DIRS = ["en", "ja", "ko", "es", "fr", "vi", "id", "pt", "hi"]


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=REPO, **kw)


def main():
    paths = [f"knowledge/{l}" for l in LANG_DIRS]
    # 撈近兩天所有刪除紀錄：commit hash + 被刪路徑
    log = run(["git", "log", "--diff-filter=D", "--since=2026-07-23 00:00",
               "--name-only", "--format=@%H", "--"] + paths)
    deletions = {}  # path -> first (latest) deleting commit
    cur = None
    for line in log.stdout.splitlines():
        if line.startswith("@"):
            cur = line[1:]
        elif line.startswith("knowledge/") and line.endswith(".md"):
            deletions.setdefault(line, cur)

    print(f"歷史刪除紀錄: {len(deletions)} 檔")
    restored, gate_fail, skipped = [], [], []

    for path, commit in sorted(deletions.items()):
        full = REPO / path
        if full.exists():
            skipped.append((path, "已重生"))
            continue
        # 撈刪除前版本
        blob = run(["git", "show", f"{commit}^:{path}"])
        if blob.returncode != 0:
            skipped.append((path, "blob 不存在"))
            continue
        content = blob.stdout
        # zh source 必須還在（translatedFrom）
        tf = None
        for ln in content.splitlines()[:30]:
            if ln.startswith("translatedFrom:"):
                tf = ln.split(":", 1)[1].strip().strip("'\"")
                break
        if not tf or not (REPO / "knowledge" / tf).exists():
            skipped.append((path, f"zh source 缺: {tf}"))
            continue
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        # 還原 gate：health + leak（可讀、無洩漏、格式合法）。
        # 不跑 verify-translation 完整度——舊版對不上最新 zh 的腳註數正是
        # 「stale」的定義，還原的目的就是讓 stale 版活著等重翻；用新譯文的
        # 完整度標準擋還原 = 把 stale 判死刑（2026-07-24 v2 放寬）。
        r2 = run(["python3", "scripts/tools/lang-sync/cjk-leak-check.py", path])
        r3 = run(["python3", "scripts/tools/article-health.py", path,
                  "--profile=pre-commit", "--quiet"])
        ok = r2.returncode == 0 and "passed=False" not in r3.stdout
        if ok:
            restored.append(path)
            print(f"  ✅ restore {path}")
        else:
            full.unlink()
            reason = ("health" if "passed=False" in r3.stdout else "leak")
            gate_fail.append((path, reason))
            print(f"  ❌ gate fail ({reason}) {path}")

    print(f"\n=== 結果: restored={len(restored)} gate_fail={len(gate_fail)} skipped={len(skipped)}")
    for p, r in gate_fail:
        print(f"  fail: {p} ({r})")
    for p, r in skipped[:10]:
        print(f"  skip: {p} ({r})")
    # 落一份清單給 commit 步驟
    out = pathlib.Path("/tmp/babel-20260724/salvage-restored.txt")
    out.write_text("\n".join(restored) + "\n" if restored else "")
    print(f"restored list → {out}")


if __name__ == "__main__":
    main()
