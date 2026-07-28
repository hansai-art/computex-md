#!/usr/bin/env python3
"""sense_client.py — 共用 GA4 + Search Console client（ANALYSIS-PIPELINE 地基）

把 fetch-ga4.py / fetch-search-console.py 的憑證機制抽成可重用 module，
讓 ga-query / sc-query / ga-window-compare / referral-attribution 共享同一條
auth 路徑，不各自重打。

憑證來源（沿用 fetch-ga4.py 慣例）:
    ~/.config/taiwan-md/credentials/google-service-account.json
    ~/.config/taiwan-md/credentials/.env  →  GA4_PROPERTY_ID / SC_SITE_URL
    venv: ~/.config/taiwan-md/venv/（自動 re-exec）

用法（在每支 script main 最前面）:
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from lib.sense_client import reexec_in_venv
    reexec_in_venv()                       # 必須在 import google 之前
    from lib.sense_client import ga_client, sc_service, property_id, sc_site_url

設計鐵律:
    - google library 一律 lazy import（function 內），module load 時不碰 google，
      否則 reexec 前就會 ImportError。
    - cred 檔在 repo 內 = SECURITY abort（不可把金鑰 commit 進 git）。

來源: 2026-06-05 ANALYSIS-PIPELINE 造橋（design: reports/analysis-pipeline-design-2026-06-05.md）
"""
import os
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "taiwan-md"
CREDENTIALS_DIR = CONFIG_DIR / "credentials"
VENV_DIR = CONFIG_DIR / "venv"
ENV_FILE = CREDENTIALS_DIR / ".env"
SERVICE_ACCOUNT_FILE = CREDENTIALS_DIR / "google-service-account.json"
SETUP_GUIDE = "docs/pipelines/SENSE-FETCHER-SETUP.md"


def fail(msg, code=1):
    print(f"❌ {msg}", file=sys.stderr)
    print(f"   Setup guide: {SETUP_GUIDE}", file=sys.stderr)
    sys.exit(code)


def reexec_in_venv():
    """Re-exec into ~/.config/taiwan-md/venv if it exists and we're not already in it.

    Must be called BEFORE any google library import. venv python is usually a symlink
    to system python, so compare sys.prefix vs sys.base_prefix (Python's venv detection)
    rather than executable paths.
    """
    venv_python = VENV_DIR / "bin" / "python3"
    if not venv_python.exists():
        return  # no venv, proceed with system python
    in_venv = sys.prefix != sys.base_prefix
    if in_venv and Path(sys.prefix).resolve() == VENV_DIR.resolve():
        return  # already in the right venv
    os.execv(str(venv_python), [str(venv_python), *sys.argv])


def load_env():
    env = dict(os.environ)
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip("'\"")
    return env


def _cred_path():
    env = load_env()
    cred_path = env.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if cred_path:
        cred_path = Path(cred_path).expanduser()
    elif SERVICE_ACCOUNT_FILE.exists():
        cred_path = SERVICE_ACCOUNT_FILE
    else:
        fail(
            f"Google service account key not found at {SERVICE_ACCOUNT_FILE}\n"
            f"   Set GOOGLE_APPLICATION_CREDENTIALS or put the JSON key there."
        )
    # Guard rail: never read a key that lives inside the repo (would mean it's committed)
    try:
        if cred_path.resolve().is_relative_to(Path.cwd().resolve()):
            fail(f"SECURITY: service account key {cred_path} is inside the repo!")
    except AttributeError:  # py<3.9 fallback
        if str(Path.cwd().resolve()) in str(cred_path.resolve()):
            fail(f"SECURITY: service account key {cred_path} is inside the repo!")
    return cred_path


def property_id():
    pid = load_env().get("GA4_PROPERTY_ID", "").strip()
    if not pid:
        fail(f"GA4_PROPERTY_ID not set in {ENV_FILE}")
    return pid


def sc_site_url():
    url = load_env().get("SC_SITE_URL", "").strip() or load_env().get(
        "SEARCH_CONSOLE_SITE_URL", "").strip()
    if not url:
        fail(f"SC_SITE_URL not set in {ENV_FILE}")
    return url


def _ga_credentials():
    from google.oauth2 import service_account
    return service_account.Credentials.from_service_account_file(str(_cred_path()))


def ga_client():
    """Return a GA4 BetaAnalyticsDataClient (Data API: runReport + runRealtimeReport)."""
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
    except ImportError as e:
        fail(
            f"Missing library {e.name}. Install into venv:\n"
            f"   {VENV_DIR}/bin/pip install google-analytics-data google-auth"
        )
    return BetaAnalyticsDataClient(credentials=_ga_credentials())


def sc_service():
    """Return a Search Console API service (webmasters v1, readonly)."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError as e:
        fail(
            f"Missing library {e.name}. Install into venv:\n"
            f"   {VENV_DIR}/bin/pip install google-api-python-client google-auth"
        )
    creds = service_account.Credentials.from_service_account_file(
        str(_cred_path()),
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
    )
    return build("searchconsole", "v1", credentials=creds)


# ── GA4 query helpers (used by ga-query.py / ga-window-compare.py) ────────────

def ga_run(dimensions, metrics, start, end, dim_filter=None, order_by=None,
           desc=True, limit=None):
    """Run a GA4 report. dim_filter: list of (field, op, value); op in
    {exact, contains, begins, regex}, joined with AND. Returns list of
    {"dims": [...], "mets": [...]}."""
    from google.analytics.data_v1beta.types import (
        DateRange, Dimension, Filter, FilterExpression, FilterExpressionList,
        Metric, RunReportRequest, OrderBy,
    )
    client = ga_client()

    def _one(field, op, value):
        sf = Filter.StringFilter
        mt = {
            "exact": sf.MatchType.EXACT,
            "contains": sf.MatchType.CONTAINS,
            "begins": sf.MatchType.BEGINS_WITH,
            "regex": sf.MatchType.FULL_REGEXP,
        }.get(op, sf.MatchType.EXACT)
        return FilterExpression(filter=Filter(
            field_name=field, string_filter=sf(match_type=mt, value=value)))

    expr = None
    if dim_filter:
        exprs = [_one(f, o, v) for (f, o, v) in dim_filter]
        expr = exprs[0] if len(exprs) == 1 else FilterExpression(
            and_group=FilterExpressionList(expressions=exprs))

    req = RunReportRequest(
        property=f"properties/{property_id()}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        dimension_filter=expr,
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name=order_by), desc=desc)]
        if order_by else None,
        limit=limit,
    )
    resp = client.run_report(req)
    return [{"dims": [d.value for d in r.dimension_values],
             "mets": [m.value for m in r.metric_values]} for r in resp.rows]


def ga_realtime(dimensions, metrics, limit=None):
    from google.analytics.data_v1beta.types import (
        Dimension, Metric, RunRealtimeReportRequest)
    client = ga_client()
    req = RunRealtimeReportRequest(
        property=f"properties/{property_id()}",
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        limit=limit,
    )
    resp = client.run_realtime_report(req)
    return [{"dims": [d.value for d in r.dimension_values],
             "mets": [m.value for m in r.metric_values]} for r in resp.rows]


def sc_query(dimensions, start, end, dim_filters=None, row_limit=1000):
    """Run a Search Console query. dim_filters: list of dicts
    {dimension, operator, expression}. Returns list of
    {keys, clicks, impressions, ctr, position}."""
    body = {"startDate": start, "endDate": end,
            "dimensions": dimensions, "rowLimit": row_limit}
    if dim_filters:
        body["dimensionFilterGroups"] = [{"filters": dim_filters}]
    rows = sc_service().searchanalytics().query(
        siteUrl=sc_site_url(), body=body).execute().get("rows", [])
    return rows


if __name__ == "__main__":
    # smoke test
    reexec_in_venv()
    print("property_id:", property_id())
    print("sc_site_url:", sc_site_url())
    print("cred:", _cred_path())
    print("✅ sense_client OK")
