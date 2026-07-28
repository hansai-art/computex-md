#!/usr/bin/env python3
"""flatten-translation-wikilinks.py — 譯文 wikilink 扁平化為純文字。

2026-07-18 出生戰役：翻譯模型把 wikilink 目標譯壞——`[[林義雄 (Lin Chi-hsiung)]]`
（漢字目標＋羅馬拼音注記塞進括號）、`[[semicondutores]]`（目標譯成葡文）——全都
不再解析（wikilink-target 檢查要求目標 == 某 zh-TW 文章 slug basename）。es/fr 的
譯文 wikilink 同樣是壞的，只是 commit 早於 hard gate 被祖父級豁免。

神經迴路鐵律：譯文 wikilink 目標語言無對應 → 轉純文字（延伸閱讀用標準 markdown link
不用 [[wikilink]]）。本工具把 knowledge/{lang}/ 的 [[...]] 扁平成純文字：

  [[X|Y]]                    → Y            （pipe display 優先）
  [[漢字 (Latin gloss)]]     → Latin gloss  （漢字目標＋拉丁注記 → 用注記，不留 CJK）
  [[semicondutores]]         → semicondutores（純拉丁目標 → 目標文字）
  [[漢字]]（無注記無 pipe）  → 漢字         （罕見；會被 cjk-residue-check 下游接住）

只動非預設語言（zh-TW 保留 wikilink——它是 SSOT，target 解析基準）。

用法：
    python3 flatten-translation-wikilinks.py --lang vi --apply
    python3 flatten-translation-wikilinks.py --files a.md b.md --apply   # 省略 --apply = dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
KNOWLEDGE = REPO / "knowledge"

WIKILINK = re.compile(r"\[\[(?P<target>[^\]|\n]+?)(?:\|(?P<display>[^\]\n]+))?\]\]")
# 漢字目標 + 拉丁注記：「林義雄 (Lin Chi-hsiung)」「二二八事件 (Incidente ...)」
CJK = re.compile(r"[一-鿿㐀-䶿]")
GLOSS = re.compile(r"^(?P<han>[^(]*?)\s*[(（](?P<gloss>[^)）]+)[)）]\s*$")


def flatten_one(m: re.Match) -> str:
    target = m.group("target").strip()
    display = (m.group("display") or "").strip()
    if display:
        return display
    g = GLOSS.match(target)
    if g and CJK.search(g.group("han")):
        # 漢字目標帶拉丁注記 → 用注記（丟掉 CJK 目標，不留殘留）
        return g.group("gloss").strip()
    return target


def process(path: Path, apply: bool) -> int:
    text = path.read_text(encoding="utf-8")
    # 只動 body，不動 frontmatter
    m = re.match(r"^(---\n.*?\n---\n)", text, re.S)
    head = m.group(1) if m else ""
    body = text[len(head):]
    new_body, n = WIKILINK.subn(flatten_one, body)
    if n and apply:
        path.write_text(head + new_body, encoding="utf-8")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang")
    ap.add_argument("--files", nargs="*")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    if args.files:
        files = [Path(f) for f in args.files]
    elif args.lang:
        if args.lang == "zh-TW":
            sys.exit("❌ zh-TW 是 SSOT，wikilink 不扁平")
        files = sorted((KNOWLEDGE / args.lang).rglob("*.md"))
    else:
        ap.error("--lang or --files required")

    total_links = total_files = 0
    for f in files:
        n = process(f, args.apply)
        if n:
            total_links += n
            total_files += 1
            print(f"{'✏️ ' if args.apply else '🔎'} {f.relative_to(REPO) if f.is_absolute() else f}: {n} wikilink")
    verb = "扁平" if args.apply else "待扁平（dry-run，加 --apply）"
    print(f"\n{total_links} wikilink / {total_files} 檔 {verb}")


if __name__ == "__main__":
    main()
