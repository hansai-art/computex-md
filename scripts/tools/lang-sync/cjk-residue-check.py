#!/usr/bin/env python3
"""cjk-residue-check.py — 非 CJK 語言譯文的漢字殘留檢查。

2026-07-18 vi/id/pt/hi 出生戰役造：codex 把「封杀」譯成「phong杀」（漢越音 phong +
未譯殘字 杀）穿過所有既有 gate。對拉丁/天城文語言，正文裡的 CJK 字元除了
「括號內的人名/原文注記」（per-language 指南 §2 明文允許，如 `Thái Anh Văn (蔡英文)`）
之外都是翻譯缺陷。

用法：
    python3 cjk-residue-check.py --lang vi            # 掃 knowledge/vi/ 全部
    python3 cjk-residue-check.py --files a.md b.md
Exit 1 = 有殘留（供 batch QA 當 gate）。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

# 對拉丁/天城文語言，正文不該有任何 CJK / Hangul / Kana——除括號注記外全是譯漏。
# 2026-07-18 出生戰役：qwen 除了漏簡體漢字，也漏過 Hangul（野百合世代的「白」寫成
# 백）與可能的 Kana；Han-only regex 抓不到，擴含韓日假名。
CJK = re.compile(r"[一-鿿㐀-䶿가-힣ぁ-ゟァ-ヿ]")
# 合法 CJK 位置（提及 vs 洩漏之別）：
#  - 括號注記（含全形）、wikilink、code span、markdown 連結目標
#    （譯文常連到中文檔名的 repo 路徑，如 reports/research/2026-07/台灣BIM….md）
#  - 引號內的外語詞（該詞是被「討論的對象」不是譯漏，如〈台灣感性〉一文正文
#    反覆提到韓文造詞「대만감성」——2026-07-18 出生戰役 Hangul regex 擴充後浮現的
#    mention-vs-leak 邊界）。真洩漏（qwen 漏簡體）幾乎都是裸詞不帶引號，引號豁免
#    保留洩漏偵測。
PAREN = re.compile(
    r"\([^)]*\)|（[^）]*）|\[\[[^\]]*\]\]|`[^`]*`|\]\([^)]*\)"
    r"|\"[^\"]*\"|“[^”]*”|'[^']*'|‘[^’]*’|「[^」]*」|『[^』]*』"
)

# 這些語言的正文不該有裸 CJK；ja/ko 混寫合法不在此清單
TARGET_LANGS = {"en", "es", "fr", "vi", "id", "pt", "hi", "ar", "ru"}


MULTILINE_LINK = re.compile(r"\]\([^)]*?\)", re.S)  # 連結目標可被 prettier 摺行
BARE_URL = re.compile(r'https?://[^\s"\')]+')  # 裸 URL（含 zh.wikipedia CJK path）合法


def check_file(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n.*?\n---\n", text, re.S)
    body = text[m.end():] if m else text
    offset = text[: m.end()].count("\n") if m else 0
    # 跨行連結目標先全文級挖掉（保行數：換行以外置空）
    body = MULTILINE_LINK.sub(lambda mm: "".join(c if c == "\n" else " " for c in mm.group(0)), body)
    body = BARE_URL.sub(lambda mm: " " * len(mm.group(0)), body)
    hits = []
    for i, line in enumerate(body.splitlines(), start=offset + 1):
        stripped = PAREN.sub("", line)
        found = CJK.findall(stripped)
        if found:
            hits.append((i, "".join(found)[:20], line.strip()[:80]))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang")
    ap.add_argument("--files", nargs="*")
    args = ap.parse_args()

    files = []
    if args.files:
        files = [Path(f) for f in args.files]
    elif args.lang:
        if args.lang not in TARGET_LANGS:
            sys.exit(f"❌ {args.lang} 不在檢查對象（ja/ko 混寫合法）")
        files = sorted((REPO / "knowledge" / args.lang).rglob("*.md"))
    else:
        ap.error("--lang or --files required")

    total = 0
    for f in files:
        hits = check_file(f)
        if hits:
            total += len(hits)
            rel = f.relative_to(REPO) if f.is_absolute() else f
            print(f"⚠️  {rel}")
            for line_no, chars, ctx in hits[:5]:
                print(f"    L{line_no} [{chars}] {ctx}")
            if len(hits) > 5:
                print(f"    … 共 {len(hits)} 行")
    if total:
        print(f"\n❌ {total} 行裸 CJK 殘留（括號注記外）")
        sys.exit(1)
    print(f"✅ {len(files)} 檔無裸 CJK 殘留")


if __name__ == "__main__":
    main()
