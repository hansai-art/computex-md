#!/usr/bin/env python3
"""geo-fidelity-check.py — 譯文地理主權保真度檢查（幻覺式地點遷移偵測）。

2026-07-18 出生戰役 heal agent 揭露：vi 譯文把「台北圓環」（二二八事件引爆點）
譯成「Bắc Kinh」（北京）——把台灣的定義性歷史創傷遷到中國首都。這是 CJK 殘留
檢查結構上抓不到的語意錯誤，且是 sovereignty red line（MANIFESTO §10 幻覺鐵律
＋主權的巴別塔：譯文不該把台灣的事搬到中國）。

機制：對每個 (zh source, translation) 對，數中國地名標記在譯文 vs zh 源的出現數。
兩道訊號：
  (1) 強訊號 — 譯文提北京/上海/中國大陸但 zh 源完全零對應原詞 → 逐行 flag（幻覺遷移）
  (2) 計數不符 — zh 源有 N 次但譯文有 M 次且 M-N ≥ 3 → 標整檔人審。這道補 (1) 的
      file-level 盲點：一篇同時有合法北京提及＋台北→北京 幻覺的文章（如整篇民主化文
      被搬到北京），(1) 會因 zh 源含北京而整檔豁免，(2) 靠計數超額抓多出來的替換。
      閾值 ≥3 因為外交/兩岸類文章翻譯常把裸「中國」展開成北京，+1~2 是措辭差非錯。
      2026-07-19 讀者揭露 file-level 盲點後補上（occurrence-based 兩邊同單位）。

用法：
    python3 geo-fidelity-check.py --lang vi           # 掃 knowledge/vi/ 全部
    python3 geo-fidelity-check.py --files a.md b.md
Exit 1 = 有可疑遷移。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
KNOWLEDGE = REPO / "knowledge"

# 中國地名/主權標記在各語言的形式。key = zh 源要對照的原詞（zh 源有這詞才算合法）。
# 每個 marker：譯文形式的 regex（各語言）＋ zh 源對照詞（source 有任一即豁免該行）。
MARKERS = [
    {
        "name": "Beijing 北京",
        # 只有 zh 源真的含「北京」才整檔豁免。京劇/天安門 不放檔級豁免——否則一篇
        # 同時有合法天安門對照段＋台北→北京 幻覺的文章（如 taiwan-democratization）
        # 會被整檔跳過，真錯藏住（2026-07-18 首版踩過）。Beijing opera 走行級豁免。
        "zh_terms": ["北京"],
        # ar/ru 2026-07-25 birth: بكين (Beijing, Arabic Wikipedia canonical) /
        # Пекин (Beijing, Russian — long-settled exonym, not a sovereignty-framing
        # choice like the person/place tables elsewhere in this guide family).
        "target": re.compile(
            r"\bBắc Kinh\b|\bBeijing\b|\bPequim\b|बीजिंग|بكين|Пекин|北京", re.I
        ),
        # 譯文行本身是 Beijing/Peking opera（京劇）語境 → 該行合法（Tiananmen「Thiên An
        # Môn」等本就不被 target 命中，不需豁免）
        "line_exempt": re.compile(
            r"opera|ópera|ôpêra|kinh kịch|ओपेरा|أوبرا|опера|京剧|京劇|京戲", re.I
        ),
    },
    {
        "name": "Shanghai 上海",
        "zh_terms": ["上海"],
        "target": re.compile(
            r"\bThượng Hải\b|\bShanghai\b|\bXangai\b|शंघाई|شنغهاي|Шанхай|上海", re.I
        ),
    },
    {
        "name": "China-mainland 中國大陸",
        # 加 外省/眷村（1949 mainlander 移民史是台灣史正題，譯文說 mainland 合法）
        "zh_terms": ["中國大陸", "中国大陆", "大陸", "大陆", "外省", "眷村"],
        # 只抓明確「中國大陸」複合詞，不抓單獨 China（正常提及中國太多）
        # ar: الصين القارية（mainland China 常見形）; ru: материковый Китай（標準用語）
        "target": re.compile(
            r"Trung Quốc đại lục|Tiongkok daratan|China continental|"
            r"चीन की मुख्य भूमि|الصين القارية|материковый Китай|中國大陸|中国大陆",
            re.I,
        ),
    },
]


def strip_frontmatter(text: str) -> str:
    m = re.match(r"^---\n.*?\n---\n", text, re.S)
    return text[m.end():] if m else text


def find_zh_source(trans_path: Path) -> Path | None:
    """從 translatedFrom frontmatter 找 zh 源。"""
    text = trans_path.read_text(encoding="utf-8")
    m = re.search(r"^translatedFrom:\s*['\"]?([^'\"\n]+)['\"]?", text, re.M)
    if not m:
        return None
    zh_rel = m.group(1).strip()
    p = KNOWLEDGE / zh_rel
    return p if p.exists() else None


def check_file(trans_path: Path):
    zh_path = find_zh_source(trans_path)
    if zh_path is None:
        return [("NO_ZH_SOURCE", 0, "translatedFrom 指向不存在的 zh 源")]
    zh_body = strip_frontmatter(zh_path.read_text(encoding="utf-8"))
    trans_text = trans_path.read_text(encoding="utf-8")
    trans_body = strip_frontmatter(trans_text)
    offset = trans_text[: len(trans_text) - len(trans_body)].count("\n")

    hits = []
    for marker in MARKERS:
        line_exempt = marker.get("line_exempt")
        # 譯文命中該 marker 的所有行（扣掉行級合法語境如 Beijing opera），逐行記 occurrence 數
        marker_lines = []  # (line_no, line, occ_count)
        for i, line in enumerate(trans_body.splitlines(), start=offset + 1):
            if line_exempt and line_exempt.search(line):
                continue
            occ = len(marker["target"].findall(line))
            if occ:
                marker_lines.append((i, line, occ))
        if not marker_lines:
            continue

        trans_count = sum(occ for _, _, occ in marker_lines)  # occurrence-based（與 zh 同單位）
        zh_count = sum(zh_body.count(t) for t in marker["zh_terms"])
        if zh_count == 0:
            # zh 源零對應，但譯文出現 → 逐行 flag（幻覺遷移強訊號）
            for i, line, _ in marker_lines:
                hits.append((marker["name"], i, line.strip()[:90]))
        elif trans_count - zh_count >= 3:
            # zh 源有 N 次但譯文有 M 次且 M-N ≥ 2 → 多出的疑似 台北→北京 類替換藏在
            # 合法 Beijing 提及底下（file-level 豁免的盲點，2026-07-19 讀者揭露）。
            # 閾值 ≥3：+1~2 幾乎都是翻譯把裸「中國」展開（外交類文章尤其）成 Pequim/北京 的措辭差，
            # 系統性地名幻覺（如整篇台北→北京）會多出好幾次。標整檔供人審——per-line
            # 對齊太難，先給計數訊號。occurrence-based 兩邊同單位（同行多次也算數）。
            hits.append((
                f"{marker['name']} 計數不符",
                marker_lines[0][0],
                f"譯文 {trans_count} 次 > zh 源 {zh_count} 次（多 {trans_count - zh_count}）——疑似地名幻覺，逐行對照 zh",
            ))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang")
    ap.add_argument("--files", nargs="*")
    args = ap.parse_args()

    if args.files:
        files = [Path(f) for f in args.files]
    elif args.lang:
        files = sorted((KNOWLEDGE / args.lang).rglob("*.md"))
    else:
        ap.error("--lang or --files required")

    total = 0
    for f in files:
        hits = check_file(f)
        if hits:
            total += len(hits)
            rel = f.relative_to(REPO) if f.is_absolute() else f
            print(f"⚠️  {rel}")
            for name, line_no, ctx in hits[:6]:
                print(f"    [{name}] L{line_no}: {ctx}")
    if total:
        print(f"\n❌ {total} 處可疑地理遷移（譯文提中國地點但 zh 源無對應原詞）— 需人審")
        sys.exit(1)
    print(f"✅ {len(files)} 檔無可疑地理遷移")


if __name__ == "__main__":
    main()
