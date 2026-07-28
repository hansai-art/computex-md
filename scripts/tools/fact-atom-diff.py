#!/usr/bin/env python3
"""fact-atom-diff.py — REWRITE-PIPELINE Step 3.8「定稿手」硬閘門

誕生背景（2026-07-26）：Step 3.8 是事實查核全部跑完之後才進場的一位 Opus agent，
專職只做一件事——把文章的語感、段落節奏順過一輪，讓讀者讀起來不卡。它不准碰任何
事實：不准改數字、不准改引語一個字、不准動腳註、不准動 viz 資料模組、不准改小標。
但「順稿」跟「動了事實」之間的界線，光靠 agent 自己宣稱「我只動語感」不可靠——
上一次順稿事故就是段落被拆開時，一個逗點後面的數字被連著改掉都沒人發現。

這支工具不判斷「順得好不好」（那是人或另一個 agent 的事），只判斷一件更窄、更
可機械驗證的事：把 BEFORE／AFTER 兩份 markdown 各自拆成「事實原子」（frontmatter
／引語／數字／腳註引用／腳註定義／URL／wikilink／H2 小標／表格與程式碼區塊），
逐類做 multiset 或逐項比對。任何原子集合對不上 = FAIL，順稿這次不能進閘。

用法:
  python3 scripts/tools/fact-atom-diff.py before.md after.md
  python3 scripts/tools/fact-atom-diff.py before.md after.md --json
  python3 scripts/tools/fact-atom-diff.py --selftest

Hard gate：PASS exit 0，FAIL exit 1，usage error exit 2。
stdlib-only，python3.9 相容（不用 `X | Y` 標註語法，一律用 Optional[...] 或不標註）。
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ─────────────────────────── 原子抽取 regex ───────────────────────────

# frontmatter：只在檔案最開頭抓一次，group(1) 是 --- 之間的內容（不含分隔線本身）
_RE_FRONTMATTER = re.compile(r"\A---[ \t]*\r?\n(.*?\r?\n)---[ \t]*\r?\n", re.DOTALL)

# 直接引語「...」— 用負向字元集排除 」避免跨越多個引語連著吃
_RE_QUOTE = re.compile(r"「[^」]*」")

# 數字原子：阿拉伯數字（含千分位逗號、小數點），可選緊接（可隔一個半形空格）的
# CJK 單位字或 %。單位表照題目給定順序，多字單位（公斤／公里）排前面純粹是可讀性，
# regex alternation 本身不需要 longest-match-first（每個 alt 都是完整字面比對）。
_NUM_UNITS = ("公斤", "公里", "年", "月", "日", "億", "萬", "元", "人", "家", "座")
_RE_NUMBER = re.compile(
    r"(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
    r"(?P<unit> ?(?:" + "|".join(_NUM_UNITS) + r"|%))?"
)

# 腳註引用 [^n]（不含定義行的 [^n]:）— 沿用 format_structure.py 既有 pattern
_RE_FOOTNOTE_REF = re.compile(r"\[\^([0-9a-zA-Z_-]+)\](?!:)")

# 腳註定義行（整行必須逐位元組相同）
_RE_FOOTNOTE_DEF = re.compile(r"^\[\^([0-9a-zA-Z_-]+)\]:.*$", re.MULTILINE)

# 腳註標記本身（含冒號變體）——數字類掃描前先挖掉，避免 [^19] 的 19 被當成事實數字，
# 跟腳註引用/定義那兩個類別重複計分（那兩類本身就是更精確的腳註比對）
_RE_FOOTNOTE_MARKER = re.compile(r"\[\^[0-9a-zA-Z_-]+\]:?")

# URL（http/https）— 在半形收尾符號／全形標點／空白處斷尾
_RE_URL = re.compile(r"https?://[^\s\)\]\}，。、；：！？」』\"']+")

# wikilink [[...]]（含 | 別名部分，題目要求「完整內部字串」全比對，不拆別名）
_RE_WIKILINK = re.compile(r"\[\[([^\[\]]+)\]\]")

# H2 小標（排除 H3+）
_RE_H2 = re.compile(r"^##[ \t]+(?!#)(.*)$", re.MULTILINE)

# 表格分隔列（| --- | :--: | 這種，只由 | - : 空白組成，且至少一個 -）
_RE_TABLE_SEP = re.compile(r"^\|?[\s:\-|]+\|?$")

CLASS_ORDER = [
    "frontmatter",
    "quotes",
    "numbers",
    "footnote_refs",
    "footnote_defs",
    "urls",
    "wikilinks",
    "h2_headings",
    "structural_blocks",
]

CLASS_LABELS = {
    "frontmatter": "Frontmatter 逐位元組",
    "quotes": "直接引語「...」",
    "numbers": "數字原子",
    "footnote_refs": "腳註引用 [^n]",
    "footnote_defs": "腳註定義 [^n]:",
    "urls": "URL",
    "wikilinks": "Wikilink [[...]]",
    "h2_headings": "H2 小標（順序）",
    "structural_blocks": "表格／程式碼區塊／HTML 區塊",
}


# ─────────────────────────── 拆解輔助 ───────────────────────────


def _split_frontmatter(text: str) -> Tuple[Optional[str], str]:
    """回傳 (frontmatter 內文 or None, body)。body = frontmatter 以後全部原文，不動任何字元。"""
    m = _RE_FRONTMATTER.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end() :]


def _parse_frontmatter_keys(fm_inner: str) -> Tuple[List[str], Dict[str, str]]:
    """把 frontmatter 內文切成 top-level key -> 該 key 完整區塊文字（含巢狀縮排內容）。

    Top-level key 判定：整行從欄位 0 開始、符合 `key:` 的行。巢狀值（縮排）跟前一個
    top-level key 併在同一個區塊裡，直到下一個 top-level key 或內文結尾。
    """
    lines = fm_inner.split("\n")
    starts: List[Tuple[str, int]] = []
    for i, line in enumerate(lines):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):", line)
        if m:
            starts.append((m.group(1), i))

    order: List[str] = []
    blocks: Dict[str, str] = {}
    for idx, (key, start) in enumerate(starts):
        end = starts[idx + 1][1] if idx + 1 < len(starts) else len(lines)
        blocks[key] = "\n".join(lines[start:end])
        order.append(key)
    return order, blocks


def _extract_numbers(body: str) -> List[str]:
    stripped = _RE_FOOTNOTE_MARKER.sub("", body)
    atoms = []
    for m in _RE_NUMBER.finditer(stripped):
        unit = m.group("unit")
        atoms.append(m.group("num") + (unit.lstrip() if unit else ""))
    return atoms


def _extract_footnote_defs(body: str) -> Dict[str, str]:
    d: Dict[str, str] = {}
    for m in _RE_FOOTNOTE_DEF.finditer(body):
        fid = m.group(1)
        d.setdefault(fid, m.group(0))  # 重複 id 保留第一次出現（正常文章不該發生）
    return d


def _extract_h2(body: str) -> List[str]:
    return [m.group(1).rstrip() for m in _RE_H2.finditer(body)]


def _is_table_separator(line: str) -> bool:
    s = line.strip()
    if not s or "-" not in s:
        return False
    return bool(_RE_TABLE_SEP.match(s))


def _extract_structural_blocks(body: str) -> List[Tuple[str, str]]:
    """依序抓「必須逐位元組相同」的結構區塊：fence（含 tw-* viz 模組）／表格／HTML-ish 區塊。"""
    lines = body.split("\n")
    n = len(lines)
    blocks: List[Tuple[str, str]] = []
    i = 0
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            start = i
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                i += 1
            if i < n:
                i += 1  # 含收尾 fence 那一行
            blocks.append(("fence", "\n".join(lines[start:i])))
            continue

        if "|" in line and i + 1 < n and _is_table_separator(lines[i + 1]):
            start = i
            i += 2  # 表頭 + 分隔列
            while i < n and "|" in lines[i] and lines[i].strip() != "":
                i += 1
            blocks.append(("table", "\n".join(lines[start:i])))
            continue

        if stripped.startswith("<"):
            start = i
            i += 1
            while i < n and lines[i].strip().startswith("<"):
                i += 1
            blocks.append(("html", "\n".join(lines[start:i])))
            continue

        i += 1
    return blocks


# ─────────────────────────── 比對輔助 ───────────────────────────


def _multiset_diff(
    before_items: List[str], after_items: List[str]
) -> Tuple[List[Tuple[str, int]], List[Tuple[str, int]]]:
    """回傳 (missing, added)，missing=before 比 after 多出來的項目（連帶多出的次數），
    added=after 比 before 多出來的項目。"""
    b = Counter(before_items)
    a = Counter(after_items)
    missing: List[Tuple[str, int]] = []
    added: List[Tuple[str, int]] = []
    for item in sorted(set(b) | set(a)):
        delta = b[item] - a[item]
        if delta > 0:
            missing.append((item, delta))
        elif delta < 0:
            added.append((item, -delta))
    return missing, added


def _append_multiset_drifts(
    drifts: List[Dict[str, Any]],
    class_name: str,
    before_items: List[str],
    after_items: List[str],
) -> None:
    missing, added = _multiset_diff(before_items, after_items)
    for item, cnt in missing:
        label = item if cnt == 1 else f"{item} (x{cnt})"
        drifts.append({"class": class_name, "kind": "missing", "before": label, "after": None})
    for item, cnt in added:
        label = item if cnt == 1 else f"{item} (x{cnt})"
        drifts.append({"class": class_name, "kind": "added", "before": None, "after": label})


def _append_ordered_drifts(
    drifts: List[Dict[str, Any]],
    class_name: str,
    before_list: List[str],
    after_list: List[str],
) -> None:
    if before_list == after_list:
        return
    maxlen = max(len(before_list), len(after_list))
    for i in range(maxlen):
        b = before_list[i] if i < len(before_list) else None
        a = after_list[i] if i < len(after_list) else None
        if b != a:
            drifts.append(
                {"class": class_name, "kind": f"order_or_rename[{i}]", "before": b, "after": a}
            )


def _append_block_drifts(
    drifts: List[Dict[str, Any]],
    class_name: str,
    before_blocks: List[Tuple[str, str]],
    after_blocks: List[Tuple[str, str]],
) -> None:
    if before_blocks == after_blocks:
        return
    maxlen = max(len(before_blocks), len(after_blocks))
    for i in range(maxlen):
        b = before_blocks[i] if i < len(before_blocks) else None
        a = after_blocks[i] if i < len(after_blocks) else None
        if b != a:
            b_label = f"[{b[0]}] {b[1]}" if b else None
            a_label = f"[{a[0]}] {a[1]}" if a else None
            drifts.append(
                {"class": class_name, "kind": f"block_diff[{i}]", "before": b_label, "after": a_label}
            )


def _diff_frontmatter(before_inner: str, after_inner: str) -> List[Dict[str, Any]]:
    if before_inner == after_inner:
        return []

    _, before_blocks = _parse_frontmatter_keys(before_inner)
    _, after_blocks = _parse_frontmatter_keys(after_inner)
    before_keys = set(before_blocks)
    after_keys = set(after_blocks)

    out: List[Dict[str, Any]] = []
    for k in sorted(before_keys - after_keys):
        out.append({"class": "frontmatter", "kind": "key_removed", "before": f"[{k}] {before_blocks[k]}", "after": None})
    for k in sorted(after_keys - before_keys):
        out.append({"class": "frontmatter", "kind": "key_added", "before": None, "after": f"[{k}] {after_blocks[k]}"})
    for k in sorted(before_keys & after_keys):
        if before_blocks[k] != after_blocks[k]:
            out.append(
                {
                    "class": "frontmatter",
                    "kind": "key_changed",
                    "before": f"[{k}] {before_blocks[k]}",
                    "after": f"[{k}] {after_blocks[k]}",
                }
            )
    if not out:
        # raw 文字有差但逐 key 比對不出差異 → 純排序或空白差異，仍算 FAIL（逐位元組要求）
        out.append(
            {
                "class": "frontmatter",
                "kind": "reordered_or_whitespace",
                "before": before_inner,
                "after": after_inner,
            }
        )
    return out


# ─────────────────────────── 主比對邏輯 ───────────────────────────


def compare_texts(before_text: str, after_text: str) -> Dict[str, Any]:
    drifts: List[Dict[str, Any]] = []

    before_fm, before_body = _split_frontmatter(before_text)
    after_fm, after_body = _split_frontmatter(after_text)

    if before_fm is None and after_fm is None:
        pass
    elif before_fm is None or after_fm is None:
        drifts.append(
            {
                "class": "frontmatter",
                "kind": "frontmatter_presence_mismatch",
                "before": "(無 frontmatter)" if before_fm is None else "(有 frontmatter)",
                "after": "(無 frontmatter)" if after_fm is None else "(有 frontmatter)",
            }
        )
    else:
        drifts.extend(_diff_frontmatter(before_fm, after_fm))

    _append_multiset_drifts(drifts, "quotes", _RE_QUOTE.findall(before_body), _RE_QUOTE.findall(after_body))

    _append_multiset_drifts(drifts, "numbers", _extract_numbers(before_body), _extract_numbers(after_body))

    before_refs = [f"[^{fid}]" for fid in _RE_FOOTNOTE_REF.findall(before_body)]
    after_refs = [f"[^{fid}]" for fid in _RE_FOOTNOTE_REF.findall(after_body)]
    _append_multiset_drifts(drifts, "footnote_refs", before_refs, after_refs)

    before_defs = _extract_footnote_defs(before_body)
    after_defs = _extract_footnote_defs(after_body)
    for k in sorted(set(before_defs) - set(after_defs)):
        drifts.append({"class": "footnote_defs", "kind": "def_removed", "before": before_defs[k], "after": None})
    for k in sorted(set(after_defs) - set(before_defs)):
        drifts.append({"class": "footnote_defs", "kind": "def_added", "before": None, "after": after_defs[k]})
    for k in sorted(set(before_defs) & set(after_defs)):
        if before_defs[k] != after_defs[k]:
            drifts.append(
                {"class": "footnote_defs", "kind": "def_changed", "before": before_defs[k], "after": after_defs[k]}
            )

    _append_multiset_drifts(drifts, "urls", _RE_URL.findall(before_body), _RE_URL.findall(after_body))

    _append_multiset_drifts(drifts, "wikilinks", _RE_WIKILINK.findall(before_body), _RE_WIKILINK.findall(after_body))

    _append_ordered_drifts(drifts, "h2_headings", _extract_h2(before_body), _extract_h2(after_body))

    _append_block_drifts(
        drifts, "structural_blocks", _extract_structural_blocks(before_body), _extract_structural_blocks(after_body)
    )

    return {"pass": len(drifts) == 0, "drifts": drifts}


# ─────────────────────────── 輸出 ───────────────────────────


def _fmt(val: Optional[str], maxlen: int = 100) -> str:
    if val is None:
        return "（無）"
    v = val.replace("\n", "⏎")
    if len(v) > maxlen:
        v = v[: maxlen - 1] + "…"
    return v


def print_report(before_path: str, after_path: str, result: Dict[str, Any]) -> None:
    print(f"🧬 fact-atom-diff  BEFORE={before_path}  AFTER={after_path}")
    by_class: Dict[str, List[Dict[str, Any]]] = {c: [] for c in CLASS_ORDER}
    for d in result["drifts"]:
        by_class.setdefault(d["class"], []).append(d)

    for c in CLASS_ORDER:
        items = by_class.get(c, [])
        label = CLASS_LABELS.get(c, c)
        if not items:
            print(f"   ✅ {label}")
            continue
        print(f"   ❌ {label}（{len(items)} 處 drift）")
        for d in items:
            print(f"      - [{d['kind']}] before={_fmt(d['before'])}")
            print(f"                 after ={_fmt(d['after'])}")

    n = len(result["drifts"])
    if result["pass"]:
        print("\nfact-atom-diff: PASS")
    else:
        print(f"\nfact-atom-diff: FAIL ({n} drifts)")


# ─────────────────────────── selftest ───────────────────────────

_FM = """---
title: '測試文章'
description: '測試用 frontmatter'
date: 2026-07-26
category: 'Test'
---
"""

_BODY_BASE = """
# 測試文章

## 第一節

第一句話有「引用內容」跟 45 元。第二句話有 2026 年的資料，來源是 [^1]，連結 https://example.com/a ，還提到 [[台灣]]。

```tw-stat
45 元 | 測試數據 | 來源說明
```

| 欄位 | 數值 |
| ---- | ---- |
| 甲   | 100  |

## 第二節

第三句話補充 350% 的成長率，另外還有 [^2] 這條註記。

[^1]: 第一條註腳說明原文
[^2]: 第二條註腳說明原文
"""

_BODY_SMOOTHED = """
# 測試文章

## 第一節

第二句話有 2026 年的資料，來源是 [^1]，連結 https://example.com/a ，還提到 [[台灣]]。

第一句話有「引用內容」跟 45 元。

```tw-stat
45 元 | 測試數據 | 來源說明
```

| 欄位 | 數值 |
| ---- | ---- |
| 甲   | 100  |

## 第二節

另外還有 [^2] 這條註記，第三句話補充 350% 的成長率。

[^1]: 第一條註腳說明原文
[^2]: 第二條註腳說明原文
"""


def _mk(body: str) -> str:
    return _FM + body


def _selftest_fixtures() -> List[Tuple[str, str, str, bool]]:
    """回傳 (name, before_text, after_text, expect_pass) list。"""
    fixtures = []

    # (a) 完全相同 → PASS
    fixtures.append(("(a) identical", _mk(_BODY_BASE), _mk(_BODY_BASE), True))

    # (b) 順稿式改動：長段拆兩段＋句子重排，事實原子全部保留 → PASS
    fixtures.append(("(b) smoothing-only reorder/split", _mk(_BODY_BASE), _mk(_BODY_SMOOTHED), True))

    # (c) 引語被改一個字 → FAIL
    body_c = _BODY_BASE.replace("「引用內容」", "「引用內客」")
    fixtures.append(("(c) quote altered by 1 char", _mk(_BODY_BASE), _mk(body_c), False))

    # (d) 數字 350% → 35% → FAIL
    body_d = _BODY_BASE.replace("350% 的成長率", "35% 的成長率")
    fixtures.append(("(d) number 350%→35%", _mk(_BODY_BASE), _mk(body_d), False))

    # (e) 腳註定義被改寫 → FAIL
    body_e = _BODY_BASE.replace("[^1]: 第一條註腳說明原文", "[^1]: 第一條註腳說明原文（修訂版）")
    fixtures.append(("(e) footnote def reworded", _mk(_BODY_BASE), _mk(body_e), False))

    # (f) H2 被改名 → FAIL
    body_f = _BODY_BASE.replace("## 第一節", "## 第一節（修訂）")
    fixtures.append(("(f) H2 renamed", _mk(_BODY_BASE), _mk(body_f), False))

    # (g) bonus：frontmatter title 被改 → FAIL
    fm_g = _FM.replace("title: '測試文章'", "title: '測試文章（改版）'")
    fixtures.append(("(g) frontmatter key changed", _mk(_BODY_BASE), fm_g + _BODY_BASE, False))

    # (h) bonus：表格資料被改 → FAIL
    body_h = _BODY_BASE.replace("| 甲   | 100  |", "| 甲   | 101  |")
    fixtures.append(("(h) table cell altered", _mk(_BODY_BASE), _mk(body_h), False))

    # (i) bonus：URL 被改 → FAIL
    body_i = _BODY_BASE.replace("https://example.com/a", "https://example.com/b")
    fixtures.append(("(i) URL altered", _mk(_BODY_BASE), _mk(body_i), False))

    # (j) bonus：wikilink 被改 → FAIL
    body_j = _BODY_BASE.replace("[[台灣]]", "[[台灣史]]")
    fixtures.append(("(j) wikilink altered", _mk(_BODY_BASE), _mk(body_j), False))

    return fixtures


def run_selftest() -> bool:
    fixtures = _selftest_fixtures()
    all_ok = True
    print("🧬 fact-atom-diff --selftest\n")
    for name, before_text, after_text, expect_pass in fixtures:
        result = compare_texts(before_text, after_text)
        got_pass = result["pass"]
        ok = got_pass == expect_pass
        all_ok = all_ok and ok
        status = "✅" if ok else "❌"
        expect_label = "PASS" if expect_pass else "FAIL"
        got_label = "PASS" if got_pass else "FAIL"
        print(f"{status} {name:<32} expect={expect_label:<4} got={got_label:<4} drifts={len(result['drifts'])}")
        if not ok:
            for d in result["drifts"]:
                print(f"      unexpected drift: [{d['class']}/{d['kind']}] before={_fmt(d['before'])} after={_fmt(d['after'])}")

    print()
    if all_ok:
        print("selftest: ALL PASS")
    else:
        print("selftest: FAILURES ABOVE")
    return all_ok


# ─────────────────────────── main ───────────────────────────


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("before", nargs="?", help="BEFORE 版 markdown 檔案路徑")
    ap.add_argument("after", nargs="?", help="AFTER 版 markdown 檔案路徑")
    ap.add_argument("--json", action="store_true", help="輸出機器可讀 JSON")
    ap.add_argument("--selftest", action="store_true", help="跑內建 fixture selftest，不需要 before/after")
    args = ap.parse_args()

    if args.selftest:
        ok = run_selftest()
        sys.exit(0 if ok else 1)

    if not args.before or not args.after:
        print("usage: fact-atom-diff.py <before.md> <after.md> [--json]", file=sys.stderr)
        sys.exit(2)

    before_path = Path(args.before)
    after_path = Path(args.after)
    if not before_path.exists():
        print(f"❌ 找不到 BEFORE 檔案：{before_path}", file=sys.stderr)
        sys.exit(2)
    if not after_path.exists():
        print(f"❌ 找不到 AFTER 檔案：{after_path}", file=sys.stderr)
        sys.exit(2)

    before_text = before_path.read_text(encoding="utf-8", errors="ignore")
    after_text = after_path.read_text(encoding="utf-8", errors="ignore")

    result = compare_texts(before_text, after_text)

    if args.json:
        import json

        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_report(str(before_path), str(after_path), result)

    sys.exit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
