#!/usr/bin/env python3
"""
converter-analytics.py — 台灣用語轉換器 (/terminology/*) 的 GA4 + Search Console 深掃

回答「大家怎麼用轉換器」這個問題，page-filtered 到 /terminology 區段，
跨 90d / 28d 兩個窗口。GA4 看「誰來了 + 站內怎麼動」，SC 看「誰想來、搜什麼進來」。

⚠️ 已知盲區：轉換器前端零互動埋點（無 convert/copy/example/direction event），
所以 GA4 只能看 page-level（pageview / engagement time / source），看不到
實際轉換次數、查哪些詞、複製率、方向偏好。這支工具量的是「可量的那一半」。

用法:
    python3 scripts/tools/converter-analytics.py            # 90d + 28d
    python3 scripts/tools/converter-analytics.py --json     # 純 JSON 輸出
憑證 / venv 同 fetch-ga4.py（~/.config/taiwan-md/）。
來源: 2026-06-13 converter-research session
"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "taiwan-md"
CREDENTIALS_DIR = CONFIG_DIR / "credentials"
VENV_DIR = CONFIG_DIR / "venv"
ENV_FILE = CREDENTIALS_DIR / ".env"
SERVICE_ACCOUNT_FILE = CREDENTIALS_DIR / "google-service-account.json"
SECTION = "/terminology"          # beginsWith filter
CONVERTER = "/terminology/converter"


def load_env():
    env = dict(os.environ)
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip("'\"")
    return env


def reexec_in_venv():
    venv_python = VENV_DIR / "bin" / "python3"
    if not venv_python.exists():
        return
    in_venv = sys.prefix != sys.base_prefix
    if in_venv and Path(sys.prefix).resolve() == VENV_DIR.resolve():
        return
    os.execv(str(venv_python), [str(venv_python), *sys.argv])


def daterange(days):
    end = datetime.now()
    start = end - timedelta(days=days)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def fetch_ga4(property_id, cred_path, days):
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange, Dimension, Filter, FilterExpression, Metric,
        RunReportRequest, OrderBy,
    )
    from google.oauth2 import service_account

    creds = service_account.Credentials.from_service_account_file(str(cred_path))
    client = BetaAnalyticsDataClient(credentials=creds)
    start, end = daterange(days)
    dr = DateRange(start_date=start, end_date=end)
    prop = f"properties/{property_id}"

    section_filter = FilterExpression(
        filter=Filter(
            field_name="pagePath",
            string_filter=Filter.StringFilter(
                match_type=Filter.StringFilter.MatchType.BEGINS_WITH,
                value=SECTION,
            ),
        )
    )

    def run(req):
        return client.run_report(req)

    out = {"window_days": days, "start": start, "end": end}

    # 1) per-page metrics under /terminology
    r = run(RunReportRequest(
        property=prop, date_ranges=[dr],
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers"),
                 Metric(name="newUsers"), Metric(name="userEngagementDuration"),
                 Metric(name="engagementRate"), Metric(name="bounceRate"),
                 Metric(name="eventCount")],
        dimension_filter=section_filter,
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=50,
    ))
    out["pages"] = [{
        "path": row.dimension_values[0].value,
        "views": int(row.metric_values[0].value),
        "users": int(row.metric_values[1].value),
        "newUsers": int(row.metric_values[2].value),
        "engagementSec": round(float(row.metric_values[3].value)),
        "engagementRate": round(float(row.metric_values[4].value), 4),
        "bounceRate": round(float(row.metric_values[5].value), 4),
        "events": int(row.metric_values[6].value),
    } for row in r.rows]

    # 2) converter-only: source / medium
    conv_filter = FilterExpression(
        filter=Filter(field_name="pagePath", string_filter=Filter.StringFilter(
            match_type=Filter.StringFilter.MatchType.CONTAINS, value=CONVERTER))
    )
    r = run(RunReportRequest(
        property=prop, date_ranges=[dr],
        dimensions=[Dimension(name="sessionSourceMedium")],
        metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers")],
        dimension_filter=conv_filter,
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=15,
    ))
    out["converter_sources"] = [{
        "sourceMedium": row.dimension_values[0].value,
        "views": int(row.metric_values[0].value),
        "users": int(row.metric_values[1].value),
    } for row in r.rows]

    # 3) converter-only: device
    r = run(RunReportRequest(
        property=prop, date_ranges=[dr],
        dimensions=[Dimension(name="deviceCategory")],
        metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers"),
                 Metric(name="engagementRate")],
        dimension_filter=conv_filter,
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=5,
    ))
    out["converter_devices"] = [{
        "device": row.dimension_values[0].value,
        "views": int(row.metric_values[0].value),
        "users": int(row.metric_values[1].value),
        "engagementRate": round(float(row.metric_values[2].value), 4),
    } for row in r.rows]

    # 4) converter-only: country
    r = run(RunReportRequest(
        property=prop, date_ranges=[dr],
        dimensions=[Dimension(name="country")],
        metrics=[Metric(name="activeUsers"), Metric(name="screenPageViews")],
        dimension_filter=conv_filter,
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="activeUsers"), desc=True)],
        limit=15,
    ))
    out["converter_countries"] = [{
        "country": row.dimension_values[0].value,
        "users": int(row.metric_values[0].value),
        "views": int(row.metric_values[1].value),
    } for row in r.rows]

    # 5) converter-only: new vs returning
    r = run(RunReportRequest(
        property=prop, date_ranges=[dr],
        dimensions=[Dimension(name="newVsReturning")],
        metrics=[Metric(name="activeUsers"), Metric(name="screenPageViews")],
        dimension_filter=conv_filter,
        limit=5,
    ))
    out["converter_new_vs_returning"] = [{
        "type": row.dimension_values[0].value or "(unknown)",
        "users": int(row.metric_values[0].value),
        "views": int(row.metric_values[1].value),
    } for row in r.rows]

    # 6) converter-only: weekly time series (date dim, bucket in caller)
    r = run(RunReportRequest(
        property=prop, date_ranges=[dr],
        dimensions=[Dimension(name="date")],
        metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers")],
        dimension_filter=conv_filter,
        order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"))],
        limit=400,
    ))
    out["converter_daily"] = [{
        "date": row.dimension_values[0].value,
        "views": int(row.metric_values[0].value),
        "users": int(row.metric_values[1].value),
    } for row in r.rows]

    return out


def fetch_sc(site_url, cred_path, days):
    from googleapiclient.discovery import build
    from google.oauth2 import service_account

    creds = service_account.Credentials.from_service_account_file(
        str(cred_path),
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
    )
    service = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
    start, end = daterange(days)

    def q(dimensions, row_limit=1000, page_filter=True):
        body = {
            "startDate": start, "endDate": end,
            "dimensions": dimensions, "rowLimit": row_limit,
        }
        if page_filter:
            body["dimensionFilterGroups"] = [{
                "filters": [{
                    "dimension": "page", "operator": "contains",
                    "expression": CONVERTER,
                }]
            }]
        return service.searchanalytics().query(siteUrl=site_url, body=body).execute().get("rows", [])

    out = {"window_days": days, "start": start, "end": end}

    # converter page totals (no extra dim, page-filtered)
    tot = q([], row_limit=1, page_filter=True)
    out["converter_totals"] = ({
        "clicks": tot[0].get("clicks", 0),
        "impressions": tot[0].get("impressions", 0),
        "ctr": round(tot[0].get("ctr", 0), 4),
        "position": round(tot[0].get("position", 0), 1),
    } if tot else {})

    # queries -> converter
    rows = q(["query"], row_limit=500)
    rows.sort(key=lambda r: -r.get("impressions", 0))
    out["converter_queries"] = [{
        "query": r["keys"][0],
        "clicks": r.get("clicks", 0),
        "impressions": r.get("impressions", 0),
        "ctr": round(r.get("ctr", 0), 4),
        "position": round(r.get("position", 0), 1),
    } for r in rows]

    # device split for converter
    rows = q(["device"], row_limit=5)
    out["converter_devices"] = [{
        "device": r["keys"][0], "clicks": r.get("clicks", 0),
        "impressions": r.get("impressions", 0),
        "ctr": round(r.get("ctr", 0), 4),
        "position": round(r.get("position", 0), 1),
    } for r in rows]

    # country split for converter
    rows = q(["country"], row_limit=15)
    rows.sort(key=lambda r: -r.get("clicks", 0))
    out["converter_countries"] = [{
        "country": r["keys"][0], "clicks": r.get("clicks", 0),
        "impressions": r.get("impressions", 0),
        "ctr": round(r.get("ctr", 0), 4),
        "position": round(r.get("position", 0), 1),
    } for r in rows]

    # weekly time series
    rows = q(["date"], row_limit=400)
    rows.sort(key=lambda r: r["keys"][0])
    out["converter_daily"] = [{
        "date": r["keys"][0], "clicks": r.get("clicks", 0),
        "impressions": r.get("impressions", 0),
        "position": round(r.get("position", 0), 1),
    } for r in rows]

    return out


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Converter (/terminology) GA4 + SC deep scan")
    parser.add_argument("--json", action="store_true", help="raw JSON only")
    parser.add_argument("--windows", default="90,28", help="comma days windows")
    args = parser.parse_args()

    reexec_in_venv()

    env = load_env()
    property_id = env.get("GA4_PROPERTY_ID", "").strip()
    site_url = env.get("SC_SITE_URL", "").strip()
    cred_path = SERVICE_ACCOUNT_FILE
    if not cred_path.exists():
        print("❌ service account missing", file=sys.stderr)
        sys.exit(1)

    result = {"fetched_at": datetime.now().isoformat(), "ga": {}, "sc": {}}
    for w in [int(x) for x in args.windows.split(",")]:
        try:
            result["ga"][str(w)] = fetch_ga4(property_id, cred_path, w)
        except Exception as e:
            result["ga"][str(w)] = {"error": str(e)}
        try:
            result["sc"][str(w)] = fetch_sc(site_url, cred_path, w)
        except Exception as e:
            result["sc"][str(w)] = {"error": str(e)}

    out_path = CONFIG_DIR / "cache" / "converter-analytics-latest.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # Human summary
    for w in [int(x) for x in args.windows.split(",")]:
        ga = result["ga"].get(str(w), {})
        sc = result["sc"].get(str(w), {})
        print(f"\n{'='*60}\n📅 窗口 {w}d  ({ga.get('start','?')} → {ga.get('end','?')})\n{'='*60}")
        if "error" in ga:
            print("  GA4 error:", ga["error"])
        else:
            print("  ── GA4 誰來了 ──")
            for p in ga.get("pages", []):
                print(f"    {p['path']:<32} views={p['views']:>6} users={p['users']:>5} "
                      f"newU={p['newUsers']:>5} engmt={p['engagementSec']//60}m eng={p['engagementRate']*100:.0f}% bounce={p['bounceRate']*100:.0f}%")
            print("  converter sources:", ", ".join(f"{s['sourceMedium']}={s['users']}" for s in ga.get("converter_sources", [])[:8]))
            print("  converter devices:", ", ".join(f"{d['device']}={d['users']}({d['engagementRate']*100:.0f}%eng)" for d in ga.get("converter_devices", [])))
            print("  new vs returning:", ", ".join(f"{x['type']}={x['users']}" for x in ga.get("converter_new_vs_returning", [])))
            print("  top countries:", ", ".join(f"{c['country']}={c['users']}" for c in ga.get("converter_countries", [])[:6]))
        if "error" in sc:
            print("  SC error:", sc["error"])
        else:
            t = sc.get("converter_totals", {})
            print(f"  ── SC 誰想來 ── totals: clicks={t.get('clicks')} impr={t.get('impressions')} ctr={(t.get('ctr',0))*100:.1f}% pos={t.get('position')}")
            print("  top queries→converter:")
            for q in sc.get("converter_queries", [])[:20]:
                print(f"    {q['impressions']:>5} impr | {q['clicks']:>3} clk | ctr {q['ctr']*100:>5.1f}% | pos {q['position']:>5.1f} | {q['query']}")
            print("  SC devices:", ", ".join(f"{d['device']}: {d['clicks']}clk/{d['impressions']}impr" for d in sc.get("converter_devices", [])))
    print(f"\n💾 saved → {out_path}")


if __name__ == "__main__":
    main()
