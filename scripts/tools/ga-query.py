#!/usr/bin/env python3
"""ga-query.py — 正確的 GA4 查詢 CLI（ANALYSIS-PIPELINE Stage 1 原料）

為什麼存在：ga4-analytics skill 的 runReport **把 filters 參數 destructure 掉但從沒放進
request** → 任何人下 filter 拿到的是「沒過濾的全站數字」而不自知（REFLEXES #24 工具在說謊：
靜默給錯答案比 crash 危險）。這支 CLI 的 filter 真的會作用。

用法:
  # 首頁 zh-TW daily 停留/互動
  ga-query.py --dims date --metrics screenPageViews,averageSessionDuration,engagementRate,bounceRate \\
              --filter pagePath=/ --start 2026-05-19 --end 2026-06-05

  # Computex 頁 referrer 拆解（contains 用 ~）
  ga-query.py --dims pageReferrer --metrics screenPageViews,activeUsers \\
              --filter 'pagePath~omputex' --start 3daysAgo --end today --order screenPageViews

  # 此刻誰在線（realtime）
  ga-query.py --realtime --dims unifiedScreenName --metrics activeUsers

filter 運算子: field=value (exact) / field~value (contains) / field^value (begins) / field#regex
日期: YYYY-MM-DD 或 GA4 相對格式（today / 7daysAgo / 14daysAgo …）。--start NNd 也接受。
輸出: 預設表格；--json 出 JSON；--save FILE 落檔。
退出碼: 0 OK / 2 參數錯。

來源: 2026-06-05 ANALYSIS-PIPELINE 造橋。
"""
import argparse
import json
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib.sense_client import reexec_in_venv  # noqa: E402
reexec_in_venv()
from lib.sense_client import ga_run, ga_realtime  # noqa: E402


def parse_filter(s):
    for op, tag in (("~", "contains"), ("^", "begins"), ("#", "regex"), ("=", "exact")):
        if op in s:
            f, _, v = s.partition(op)
            return (f.strip(), tag, v.strip())
    raise ValueError(f"bad filter (need =/~/^/#): {s}")


def norm_date(d):
    # accept "7d" shorthand → "7daysAgo"
    import re
    m = re.match(r"^(\d+)d$", d)
    return f"{m.group(1)}daysAgo" if m else d


def main():
    ap = argparse.ArgumentParser(description="GA4 query CLI (filters actually work)")
    ap.add_argument("--dims", default="", help="comma-separated dimensions (e.g. date,pagePath). customEvent:foo allowed")
    ap.add_argument("--metrics", required=True, help="comma-separated metrics")
    ap.add_argument("--filter", action="append", default=[], help="field=value / field~contains / field^begins / field#regex (repeatable, AND)")
    ap.add_argument("--start", default="28daysAgo")
    ap.add_argument("--end", default="today")
    ap.add_argument("--order", default=None, help="metric name to sort desc by")
    ap.add_argument("--asc", action="store_true", help="sort ascending")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--realtime", action="store_true", help="run a realtime report (ignores dates/filter)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--save", default=None, help="write JSON to this path")
    a = ap.parse_args()

    dims = [d.strip() for d in a.dims.split(",") if d.strip()]
    mets = [m.strip() for m in a.metrics.split(",") if m.strip()]

    if a.realtime:
        rows = ga_realtime(dims, mets, limit=a.limit)
        meta = {"mode": "realtime", "dims": dims, "metrics": mets}
    else:
        flt = [parse_filter(f) for f in a.filter] if a.filter else None
        rows = ga_run(dims, mets, norm_date(a.start), norm_date(a.end),
                      dim_filter=flt, order_by=a.order, desc=not a.asc, limit=a.limit)
        meta = {"mode": "report", "start": norm_date(a.start), "end": norm_date(a.end),
                "dims": dims, "metrics": mets, "filter": a.filter}

    payload = {"meta": meta, "rowCount": len(rows), "rows": rows}
    if a.save:
        pathlib.Path(a.save).parent.mkdir(parents=True, exist_ok=True)
        json.dump(payload, open(a.save, "w"), ensure_ascii=False, indent=2)
        print(f"💾 {a.save} ({len(rows)} rows)", file=sys.stderr)

    if a.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    # table
    hdr = dims + mets
    print("  ".join(hdr))
    print("  ".join("-" * len(h) for h in hdr))
    for r in rows:
        print("  ".join(r["dims"] + r["mets"]))
    print(f"\n({len(rows)} rows)", file=sys.stderr)


if __name__ == "__main__":
    main()
