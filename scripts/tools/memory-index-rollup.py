#!/usr/bin/env python3
"""
memory-index-rollup.py — MEMORY.md / DIARY.md index 月度彙整（蒸餾債清償儀器）

背景：MEMORY.md index 曾累積 709 rows（觸發線 80，2026-04-14 蒸餾設計從未實作，
alert 每天黃燈無 routine 認領 — 2026-07-05 dna-audit S4）。本工具做最小可行蒸餾：

- inline 只保留最新 KEEP 列（memory 40 / diary 60），甦醒讀取（wake-context date-aware）不受影響
- 較舊列 **verbatim 原文搬移**到 index-archive/{YYYY-MM}.md（append-only，
  raw 永不刪除 per REFLEXES #22；歸檔列可 grep、有 git 歷史）
- 每個被清空的月份在表內留一列月度摘要（digest row，date 欄用 YYYY-MM 不含日 →
  不會被 memory-index-lint / 本工具當一般列處理）
- 列守恆斷言（REFLEXES #38 檔案改寫 dry-run 變體）：kept + moved == 原列數，
  歸檔檔新增行數 == moved 對應數，任一不合 = abort 不寫入
- dry-run 是預設；--apply 才落地

v2（2026-07-11 wake-evolution）：--diary 泛化到 DIARY.md（S5 殼核不對稱補平：
memory 有蒸餾 diary 沒有，DIARY.md 曾脹到 274KB）。「較舊」的判定改為 date-aware
（依列內日期排序取最舊，不依檔案位置）——MEMORY 新在下、DIARY 新在上，位置假設
在兩檔間必錯其一（REFLEXES #65 量尺共路徑；同日內以檔案位置 tiebreak，
跨方向的邊界日混排屬 cosmetic）。digest 列插在被搬列的最前檔案位置
（兩種方向下都落在舊列群的頂端）。

擁有權（detection ≠ remediation，REFLEXES #58）：twmd-distill-weekly 每週跑
`--apply` 與 `--diary --apply` 各一次，SOP 在 MEMORY-PIPELINE §索引蒸餾。
"""
import argparse
import re
import sys
from collections import OrderedDict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FULL_DATE_RE = re.compile(r"^\s*(20\d\d)-(\d\d)-(\d\d)\s*$")

TARGETS = {
    "memory": {
        "file": REPO / "docs/semiont/MEMORY.md",
        "archive": REPO / "docs/semiont/memory/index-archive",
        "keep": 40,
        "link_prefix": "memory/index-archive",
        "columns": "| 日期 | Session | 摘要 | 關鍵教訓 | 完整 |",
        "source_name": "MEMORY.md §心跳日誌",
    },
    "diary": {
        "file": REPO / "docs/semiont/DIARY.md",
        "archive": REPO / "docs/semiont/diary/index-archive",
        "keep": 60,
        "link_prefix": "diary/index-archive",
        "columns": "| 日期 | session | 標題 | 核心思考 | 日記 |",
        "source_name": "DIARY.md §日記索引",
    },
}

ARCHIVE_HEADER = """# {source} index archive — {month}

> 由 `scripts/tools/memory-index-rollup.py` 從 [{fname}](../../{fname}) verbatim 搬入。
> 列內容一字未改（raw 永不刪除，REFLEXES #22）；raw 檔在上層資料夾。append-only。

{columns}
| --- | --- | --- | --- | --- |
"""


def is_index_row(line: str):
    parts = line.split("|")
    if len(parts) < 7:
        return None
    m = FULL_DATE_RE.match(parts[1])
    return (m.group(0).strip(), m.group(1) + "-" + m.group(2)) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="真的寫入（預設 dry-run）")
    ap.add_argument("--diary", action="store_true", help="彙整 DIARY.md（預設 MEMORY.md）")
    ap.add_argument("--keep", type=int, default=None, help="inline 保留列數（memory 40 / diary 60）")
    args = ap.parse_args()

    cfg = TARGETS["diary" if args.diary else "memory"]
    keep = args.keep if args.keep is not None else cfg["keep"]
    target = cfg["file"]

    lines = target.read_text(encoding="utf-8").split("\n")
    rows = []  # (file_index, date_str, month)
    for i, l in enumerate(lines):
        r = is_index_row(l)
        if r:
            rows.append((i, r[0], r[1]))
    total = len(rows)
    if total <= keep:
        print(f"✅ {target.name} inline rows {total} ≤ keep {keep}，無需 rollup")
        return 0

    # date-aware：最舊的 total-keep 列搬走（同日以檔案位置 tiebreak），方向假設為零
    by_age = sorted(rows, key=lambda t: (t[1], t[0]))
    to_move = by_age[: total - keep]
    kept_months = {month for _, _, month in by_age[total - keep :]}
    by_month = OrderedDict()
    for month in sorted({m for _, _, m in to_move}):
        idxs = sorted(i for i, d, m in to_move if m == month)
        by_month[month] = idxs

    print(f"📦 rollup 計畫（{target.name}）：inline {total} → keep {keep}，搬 {len(to_move)} 列：")
    for month, idxs in by_month.items():
        tag = "" if month not in kept_months else "（該月仍有 inline 列 → 不產 digest）"
        print(f"   {month}: {len(idxs)} 列 → {cfg['link_prefix']}/{month}.md {tag}")

    if not args.apply:
        print("（dry-run。--apply 落地）")
        return 0

    header_tpl = ARCHIVE_HEADER.replace("{columns}", cfg["columns"])
    moved_set = set()
    for month, idxs in by_month.items():
        cfg["archive"].mkdir(parents=True, exist_ok=True)
        p = cfg["archive"] / f"{month}.md"
        chunk = "\n".join(lines[i] for i in idxs) + "\n"
        header = header_tpl.format(source=cfg["source_name"], month=month, fname=target.name)
        before = p.read_text(encoding="utf-8").count("\n") if p.exists() else 0
        if not p.exists():
            p.write_text(header + chunk, encoding="utf-8")
        else:
            p.write_text(p.read_text(encoding="utf-8") + chunk, encoding="utf-8")
        after = p.read_text(encoding="utf-8").count("\n")
        gained = after - before
        expected = len(idxs) if before else len(idxs) + header.count("\n")
        if gained != expected:
            print(f"❌ 守恆斷言失敗：{p.name} 增 {gained} 行 ≠ 預期 {expected}，abort（{target.name} 未動）")
            return 1
        moved_set.update(idxs)

    digest_lines = [
        f"| {month} | 月度彙整 | {len(idxs)} 篇，完整列已 verbatim 歸檔 | — | [→]({cfg['link_prefix']}/{month}.md) |"
        for month, idxs in by_month.items()
        if month not in kept_months
    ]
    first_moved = min(moved_set)
    out = []
    inserted = False
    for i, l in enumerate(lines):
        if i in moved_set:
            if not inserted and i == first_moved:
                out.extend(digest_lines)
                inserted = True
            continue
        out.append(l)

    kept_rows = sum(1 for l in out if is_index_row(l))
    if kept_rows != keep:
        print(f"❌ 守恆斷言失敗：留下 {kept_rows} 列 ≠ keep {keep}，abort")
        return 1
    if len(out) != len(lines) - len(moved_set) + len(digest_lines):
        print("❌ 行數守恆斷言失敗，abort")
        return 1

    target.write_text("\n".join(out), encoding="utf-8")
    print(f"✅ rollup 完成：{target.name} inline {total} → {kept_rows} 列 + {len(digest_lines)} digest；歸檔 {len(moved_set)} 列")
    return 0


if __name__ == "__main__":
    sys.exit(main())
