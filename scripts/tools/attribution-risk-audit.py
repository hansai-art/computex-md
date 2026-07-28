#!/usr/bin/env python3
"""attribution-risk-audit — 跨文章「歸屬密集 × 引用稀薄 × 未審 × featured」風險排行.

儀器化 REFLEXES #15：把 2026-06-01 配樂讀者 callout 後手動跑的「待重新審理佇列」
heredoc 升級為可重跑工具。原 ad-hoc python 每次重打、結果不可追溯；本工具讓佇列
隨時可 regen，並可餵 ARTICLE-INBOX。

風險模型（A↔B 歸屬密集主題是 AI 幻覺高風險區，per 2026-06-01 影視配樂教訓）：
    surface  = 《》+〈〉 work-title 數（歸屬表面積）
    risk     = surface
             + 40            if fns==0 and surface>=8      # 零腳註密集 = 紅旗
             + min(surface/max(fns,1), 10) * 3   otherwise  # claims-per-citation
             + 15            if 早期批次 (2026-03，pipeline 最不成熟)
             + 12            if featured (放大傷害)
    只算 lastHumanReview != true 的文章（已人工審 = 低優先）。

Tier:
    T1  早期批次 + featured + (零腳註 or surface>=40)，或 零腳註 + surface>=15
    T2  早期批次 + featured，或 surface>=60，或 零腳註 + surface>=10
    T3  其餘入列者

用法：
    python3 scripts/tools/attribution-risk-audit.py                 # 印 summary + Tier1/2
    python3 scripts/tools/attribution-risk-audit.py --out FILE.md   # 寫完整 markdown 佇列
    python3 scripts/tools/attribution-risk-audit.py --json          # JSON 給 routine/dashboard
    python3 scripts/tools/attribution-risk-audit.py --min-works 10  # 入列門檻（預設 10）

Canonical: reports/reader-callout-pipeline-diagnosis-2026-06-01.md §5 + REWRITE-PIPELINE.md §Step 0.2-bis
"""

from __future__ import annotations
import argparse
import glob
import json
import os
import re
import sys

LANG_DIRS = {"en", "ja", "ko", "es", "fr"}
ROOT = "knowledge"


def is_zh(path: str) -> bool:
    parts = path.split(os.sep)
    return len(parts) > 1 and parts[1] not in LANG_DIRS


def parse(path: str) -> dict | None:
    try:
        t = open(path, encoding="utf-8").read()
    except Exception:
        return None
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", t, re.S)
    if not m:
        return None
    head, body = m.group(1), m.group(2)

    def g(k):
        mm = re.search(rf"^{k}:\s*(.*)$", head, re.M)
        return mm.group(1).strip().strip("'\"") if mm else None

    works = len(re.findall(r"《[^》]+》", body)) + len(re.findall(r"〈[^〉]+〉", body))
    fns = len(re.findall(r"^\[\^\d+\]:", body, re.M))
    return dict(
        path=path,
        date=g("date") or "",
        rev=g("lastHumanReview"),
        featured=(g("featured") == "true"),
        category=g("category") or "?",
        works=works,
        fns=fns,
        is_hub=os.path.basename(path).startswith("_"),
    )


def early(d: str) -> bool:
    return d[:7] == "2026-03"


def score(r: dict) -> float:
    s = float(r["works"])
    if r["fns"] == 0 and r["works"] >= 8:
        s += 40
    else:
        s += min(r["works"] / max(r["fns"], 1), 10) * 3
    if early(r["date"]):
        s += 15
    if r["featured"]:
        s += 12
    return round(s, 1)


def tier(r: dict) -> str:
    if early(r["date"]) and r["featured"] and (r["fns"] == 0 or r["works"] >= 40):
        return "T1"
    if r["fns"] == 0 and r["works"] >= 15:
        return "T1"
    if early(r["date"]) and r["featured"]:
        return "T2"
    if r["works"] >= 60 or (r["fns"] == 0 and r["works"] >= 10):
        return "T2"
    return "T3"


def build_queue(min_works: int):
    files = [f for f in glob.glob(f"{ROOT}/**/*.md", recursive=True) if is_zh(f)]
    rows = [r for r in (parse(f) for f in files) if r]
    unrev = [r for r in rows if r["rev"] != "true"]
    queue = [r for r in unrev if r["works"] >= min_works or (r["fns"] == 0 and r["works"] >= 8)]
    for r in queue:
        r["score"] = score(r)
        r["tier"] = tier(r)
    queue.sort(key=lambda r: -r["score"])
    return rows, unrev, queue


def main():
    ap = argparse.ArgumentParser(description="跨文章歸屬風險排行 → 待重新審理佇列")
    ap.add_argument("--min-works", type=int, default=10, help="入列門檻（《》/〈〉 數，預設 10）")
    ap.add_argument("--out", default=None, help="寫完整 markdown 佇列到此路徑")
    ap.add_argument("--json", action="store_true", help="輸出 JSON（給 routine/dashboard）")
    ap.add_argument("--top", type=int, default=0, help="只印前 N（0=印 Tier1+Tier2）")
    args = ap.parse_args()

    rows, unrev, queue = build_queue(args.min_works)
    tiers = {"T1": 0, "T2": 0, "T3": 0}
    for r in queue:
        tiers[r["tier"]] += 1

    if args.json:
        print(json.dumps({
            "total_zh": len(rows),
            "unreviewed": len(unrev),
            "queue_size": len(queue),
            "tiers": tiers,
            "queue": [{k: r[k] for k in ("tier", "score", "works", "fns", "date",
                                         "featured", "category", "path", "is_hub")}
                      for r in queue],
        }, ensure_ascii=False, indent=2))
        return

    def md_table(items):
        lines = ["| tier | score | works | fns | date | feat | hub | category | file |",
                 "|------|------:|------:|----:|------|:----:|:---:|----------|------|"]
        for r in items:
            fe = "★" if r["featured"] else ""
            hub = "_" if r["is_hub"] else ""
            lines.append(f"| {r['tier']} | {r['score']} | {r['works']} | {r['fns']} | "
                         f"{r['date']} | {fe} | {hub} | {r['category']} | "
                         f"{os.path.basename(r['path'])} |")
        return "\n".join(lines)

    header = (f"# 待重新審理佇列（attribution-risk-audit）\n\n"
              f"全站 {len(rows)} 篇 zh SSOT；未人工審 {len(unrev)} 篇。\n"
              f"入列（《》/〈〉 ≥ {args.min_works} 或 零腳註 ≥8 且未審）= **{len(queue)} 篇**。\n"
              f"Tier1={tiers['T1']} / Tier2={tiers['T2']} / Tier3={tiers['T3']}。\n"
              f"（`_*.md` = 內部 Hub/scaffold，重審時排除。）\n\n"
              f"風險分 = 歸屬表面 + 零腳註懲罰(+40) 或 claims/footnote 比 + 早期批次(+15) + featured(+12)。\n")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(header + "\n" + md_table(queue) + "\n")
        print(f"WROTE {args.out}  ({len(queue)} rows; T1={tiers['T1']} T2={tiers['T2']} T3={tiers['T3']})")
        return

    print(header)
    show = queue[:args.top] if args.top else [r for r in queue if r["tier"] in ("T1", "T2")]
    print(md_table(show))
    if not args.top:
        print(f"\n（只印 Tier1+Tier2 {len(show)} 篇；完整 {len(queue)} 篇用 --out FILE.md 或 --top N）")


if __name__ == "__main__":
    main()
