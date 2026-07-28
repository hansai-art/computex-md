#!/usr/bin/env python3
"""
semantic-noop-check.py — 判定一篇 stale 翻譯的 zh diff 是否「語意無關」（只動標點/空白）。

背景（reports/semantic-noop-stale-2026-07-27.md）：全站 642 篇 stale 抽樣 40 對，
25 對可判定裡 52% 的 zh diff 只是標點/空白正規化（半形逗號→全形、句中分號改句號、
破折號改冒號之類）。這類改動對譯文完全沒有語意影響——譯文用自己語言的標點規範，
不會因為中文標點怎麼改就跟著要動。這種 stale 不必呼叫任何模型重翻，只要把譯文
frontmatter 的三個 provenance 欄位（sourceCommitSha / sourceContentHash /
sourceBodyHash）bump 到 zh 最新版本即可（bump-source-sha.py 的 bump_one() 已有這段
寫入邏輯，本工具只負責「判定」，不負責寫檔）。

判定邏輯（保守：寧可漏判不可誤判——判不出來就不是 no-op，走原本的翻譯路徑）：
  1. 用 `git diff --unified=0 <sourceCommitSha>..HEAD -- knowledge/<zh_path>` 取 zh diff。
  2. 掃過 diff hunk：任何 hunk 的行號範圍落在 frontmatter 區塊（第一組 `---` 到第二組
     `---` 之間，新舊版本都算）→ 直接判「不是 no-op」。frontmatter 欄位變動可能有語意
     （例如 title 改標點其實是改標題），一律不冒險。
  3. 抽出所有 `+` 行與 `-` 行的內容（用 hunk header 定位，不靠 `---`/`+++` 檔頭字串
     比對，避免內容行剛好也以 `---` 開頭時誤判成檔頭）。
  4. 分別對 `+` 行與 `-` 行的串接內容做「正規化」：移除所有 Unicode 標點字元
     （category 開頭 P：Pc/Pd/Pe/Pf/Pi/Po/Ps）與所有空白/格式字元（Unicode
     whitespace + category Cf，涵蓋全形空格 U+3000、零寬空格 U+200B、BOM 等）。
  5. 正規化後兩邊字串完全相同（含順序）→ 語意無關（no-op）。任何差異（包含中文用字
     替換如「台灣」↔「臺灣」、數字改動、語句重排）都不會被正規化抹掉，會判「不是
     no-op」。
  6. diff 是空的、抓不到舊版內容、sha 解析不出來 → 一律「不是 no-op」。

Usage:
  python3 semantic-noop-check.py <zh_path> <translation_path>
    zh_path            相對 knowledge/，如 "Culture/xxx.md"
    translation_path   相對 repo root 或 knowledge/，如 "en/Culture/xxx.md"
  python3 semantic-noop-check.py <zh_path> --sha <sha>
    手動指定 sourceCommitSha（測試 / 不依賴翻譯檔存在時用）

Options:
  --json     JSON 輸出到 stdout（給呼叫端 / dispatcher 解析）
  --quiet    抑制人類可讀輸出（--json 已內含 --quiet 效果，仍可疊加）

Exit codes:
  0 = semantic no-op（diff 只有標點/空白，frontmatter 未被動到）
  1 = 不是 no-op（有實質內容改動 / 動到 frontmatter / 無法判定的任何情況）
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
KNOWLEDGE = REPO / "knowledge"

_FM_LINE_RE = re.compile(r"^(\w+):\s*['\"]?([^'\"\n]+?)['\"]?\s*$")
_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


# ---------- small helpers ----------

def norm_zh_path(raw: str) -> str:
    p = raw
    if p.startswith("knowledge/"):
        p = p[len("knowledge/"):]
    return p.lstrip("/")


def norm_translation_path(raw: str) -> str:
    """Returns path relative to REPO (with leading 'knowledge/')."""
    p = raw
    if p.startswith("knowledge/"):
        return p
    if p.startswith("/"):
        return p.lstrip("/")
    return f"knowledge/{p}"


def read_frontmatter_field(content: str, key: str) -> str | None:
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    fm = content[3:end]
    for line in fm.splitlines():
        m = _FM_LINE_RE.match(line)
        if m and m.group(1) == key:
            return m.group(2)
    return None


def frontmatter_end_line(content: str) -> int | None:
    """1-indexed line number of the CLOSING '---' delimiter, or None if the
    content has no (well-formed) frontmatter block."""
    if not content.startswith("---"):
        return None
    lines = content.split("\n")
    if lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i + 1  # 1-indexed
    return None


def git_show(rev: str, repo_rel_path: str) -> str | None:
    r = subprocess.run(
        ["git", "show", f"{rev}:{repo_rel_path}"],
        cwd=REPO, capture_output=True, text=True,
    )
    if r.returncode != 0:
        return None
    return r.stdout


def _is_noise_char(ch: str) -> bool:
    if ch.isspace():
        return True
    cat = unicodedata.category(ch)
    return cat.startswith("P") or cat == "Cf"


def normalize(text: str) -> str:
    """Strip all punctuation (any Unicode P* category) and all whitespace/
    format characters (Unicode whitespace + Cf, covers full-width space
    U+3000, zero-width space U+200B, BOM, etc.)."""
    return "".join(ch for ch in text if not _is_noise_char(ch))


# ---------- core judgment ----------

def check(zh_rel: str, sha: str) -> dict:
    zh_full = KNOWLEDGE / zh_rel
    zh_git_path = f"knowledge/{zh_rel}"

    if not zh_full.exists():
        return {"noop": False, "reason": "zh-missing"}
    if not sha or not re.fullmatch(r"[0-9a-fA-F]{4,40}", sha):
        return {"noop": False, "reason": f"invalid-sha({sha!r})"}

    old_content = git_show(sha, zh_git_path)
    if old_content is None:
        return {"noop": False, "reason": f"cannot-read-old-revision({sha})"}

    new_content = git_show("HEAD", zh_git_path)
    if new_content is None:
        # Fall back to working tree (should be rare — zh files are committed
        # by contributors/editors, not left dirty by the babel pipelines).
        new_content = zh_full.read_text(encoding="utf-8")

    diff_out = subprocess.run(
        ["git", "diff", "--unified=0", f"{sha}..HEAD", "--", zh_git_path],
        cwd=REPO, capture_output=True, text=True,
    ).stdout
    if not diff_out.strip():
        return {"noop": False, "reason": "empty-diff(possible rename/path drift)"}

    old_fm_end = frontmatter_end_line(old_content)
    new_fm_end = frontmatter_end_line(new_content)

    removed_lines: list[str] = []
    added_lines: list[str] = []
    fm_touched = False
    in_hunk = False

    for line in diff_out.splitlines():
        m = _HUNK_RE.match(line)
        if m:
            in_hunk = True
            old_start = int(m.group(1))
            old_count = int(m.group(2)) if m.group(2) is not None else 1
            new_start = int(m.group(3))
            new_count = int(m.group(4)) if m.group(4) is not None else 1
            # Zero-count (pure insert/delete point) hunks still get checked
            # against old_start/new_start — conservative: an insertion right
            # at the frontmatter boundary counts as "touched".
            if old_fm_end is not None and old_start <= old_fm_end:
                fm_touched = True
            if new_fm_end is not None and new_start <= new_fm_end:
                fm_touched = True
            continue
        if not in_hunk:
            # Still inside `diff --git` / `index ...` / `--- a/...` / `+++ b/...`
            # preamble — never treat these as content lines (a real removed/
            # added line whose content happens to start with '---' would
            # otherwise be misread as the file header).
            continue
        if line.startswith("+"):
            added_lines.append(line[1:])
        elif line.startswith("-"):
            removed_lines.append(line[1:])
        # context lines (starting with ' ') and "\ No newline..." markers:
        # ignored — --unified=0 shouldn't emit context lines anyway.

    if fm_touched:
        return {"noop": False, "reason": "frontmatter-touched"}

    if not removed_lines and not added_lines:
        return {"noop": False, "reason": "no-body-lines-changed"}

    norm_removed = normalize("\n".join(removed_lines))
    norm_added = normalize("\n".join(added_lines))

    if norm_removed == norm_added:
        return {
            "noop": True,
            "reason": "punct-whitespace-only",
            "removed_lines": len(removed_lines),
            "added_lines": len(added_lines),
        }
    return {
        "noop": False,
        "reason": "content-diff",
        "removed_lines": len(removed_lines),
        "added_lines": len(added_lines),
    }


# ---------- CLI ----------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zh_path")
    ap.add_argument("translation_path", nargs="?", default=None,
                     help="讀取其 frontmatter sourceCommitSha（與 --sha 二選一，優先用 --sha）")
    ap.add_argument("--sha", default=None, help="手動指定 sourceCommitSha，略過讀 translation_path")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    zh_rel = norm_zh_path(args.zh_path)

    sha = args.sha
    trans_rel = None
    if not sha:
        if not args.translation_path:
            ap.error("需要 translation_path 或 --sha 其中之一")
        trans_rel = norm_translation_path(args.translation_path)
        trans_full = REPO / trans_rel
        if not trans_full.exists():
            result = {"noop": False, "reason": "translation-missing", "zh_path": zh_rel}
            _emit(result, args)
            return 1
        sha = read_frontmatter_field(trans_full.read_text(encoding="utf-8"), "sourceCommitSha")
        if not sha:
            result = {"noop": False, "reason": "no-source-sha-in-frontmatter", "zh_path": zh_rel}
            _emit(result, args)
            return 1

    result = check(zh_rel, sha)
    result["zh_path"] = zh_rel
    result["sha"] = sha
    if trans_rel:
        result["translation_path"] = trans_rel
    _emit(result, args)
    return 0 if result.get("noop") else 1


def _emit(result: dict, args) -> None:
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
        return
    if args.quiet:
        return
    mark = "✅ no-op" if result.get("noop") else "❌ not no-op"
    print(f"{mark}  {result.get('zh_path')} @ {result.get('sha')}  ({result.get('reason')})")


if __name__ == "__main__":
    sys.exit(main())
