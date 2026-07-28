#!/usr/bin/env python3
"""sc-query.py — Search Console 查詢 CLI（ANALYSIS-PIPELINE Stage 1 原料）

用法:
  # Computex 頁的查詢詞（page contains filter）
  sc-query.py --dims query --filter 'page~Computex' --start 2026-05-22 --end 2026-06-05

  # 全站 top pages 近 14 天
  sc-query.py --dims page --start 14d --end today --limit 30

filter: dimension~value (contains) / dimension=value (equals) / dimension!value (notContains)
  dimensions: query / page / device / country / searchAppearance / date
日期: YYYY-MM-DD / today / NNd（→ N 天前）。
輸出: 表格（key... clicks impr ctr% pos）；--json / --save。

來源: 2026-06-05 ANALYSIS-PIPELINE 造橋。
"""
import argparse
import json
import sys
import re
import pathlib
from datetime import date, timedelta

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib.sense_client import reexec_in_venv  # noqa: E402
reexec_in_venv()
from lib.sense_client import sc_query  # noqa: E402


def norm_date(d):
    if d == "today":
        return date.today().isoformat()
    m = re.match(r"^(\d+)d(aysAgo)?$", d)
    if m:
        return (date.today() - timedelta(days=int(m.group(1)))).isoformat()
    return d


def parse_filter(s):
    for op, name in (("~", "contains"), ("!", "notContains"), ("=", "equals")):
        if op in s:
            dim, _, expr = s.partition(op)
            return {"dimension": dim.strip(), "operator": name, "expression": expr.strip()}
    raise ValueError(f"bad filter (need ~/!/=): {s}")


def main():
    ap = argparse.ArgumentParser(description="Search Console query CLI")
    ap.add_argument("--dims", default="query", help="comma-separated: query/page/device/country/date/searchAppearance")
    ap.add_argument("--filter", action="append", default=[], help="dim~contains / dim=equals / dim!notContains (repeatable)")
    ap.add_argument("--start", default="28d")
    ap.add_argument("--end", default="today")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--save", default=None)
    a = ap.parse_args()

    dims = [d.strip() for d in a.dims.split(",") if d.strip()]
    flt = [parse_filter(f) for f in a.filter] if a.filter else None
    rows = sc_query(dims, norm_date(a.start), norm_date(a.end), dim_filters=flt, row_limit=a.limit)

    payload = {"meta": {"dims": dims, "start": norm_date(a.start), "end": norm_date(a.end),
                        "filter": a.filter}, "rowCount": len(rows), "rows": rows}
    if a.save:
        pathlib.Path(a.save).parent.mkdir(parents=True, exist_ok=True)
        json.dump(payload, open(a.save, "w"), ensure_ascii=False, indent=2)
        print(f"💾 {a.save} ({len(rows)} rows)", file=sys.stderr)
    if a.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print("  ".join(dims + ["clicks", "impr", "ctr%", "pos"]))
    for r in rows:
        keys = r.get("keys", [])
        print("  ".join(keys + [str(r["clicks"]), str(r["impressions"]),
                                f"{r['ctr']*100:.1f}", f"{r['position']:.1f}"]))
    print(f"\n({len(rows)} rows)", file=sys.stderr)


if __name__ == "__main__":
    main()
