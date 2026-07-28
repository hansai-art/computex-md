#!/usr/bin/env python3
"""
converter-demand.py — 台灣用語轉換器「需求回饋環」：用 GA4 event 讀「大家實際查哪些詞」

把詞庫成長從「作者猜」翻轉成「需求驅動」。converter.astro 埋的 5 個 event
（converter_term_lookup / converter_convert / converter_example_click /
converter_copy / converter_direction_toggle）餵進來，回答四件事：

  1. 詞需求排行（PRIMARY）：哪些 term_id 被查最多 → 那些詞值得最好的 per-term 頁 /
     專文。filter eventName == converter_term_lookup，group by customEvent:term_id。
  2. 方向使用：cn2tw vs tw2cn — 有人在用反向 (tw2cn) 嗎？
  3. 範例分類熱度：converter_example_click by customEvent:category。
  4. 漏斗：converter_convert / converter_copy 事件數（粗略 convert→copy 比）。

═══════════════════════════════════════════════════════════════════════════
⚠️ 已知限制（不要 over-trust 這份數據）
═══════════════════════════════════════════════════════════════════════════
converter_term_lookup 只在「資料庫裡已經有的詞」（matched rule）被命中時 fire。
所以這份排行量的是【現有 ~1,800 個詞之中】的需求分佈 —— 它**看不到「缺漏的詞」**
（使用者輸入了、但我們還沒收進對映表的中國用語）。

換句話說：這份工具告訴你「現有的哪些詞最該被照顧」，但**不會**告訴你「該新增哪些
詞」。偵測缺漏詞需要不同的未來訊號，例如：
  - 追蹤「轉換後台灣化指數仍偏低」的輸入（代表大部分沒被換掉 = 可能有缺漏詞）
  - 前端加一顆「回報缺漏詞」按鈕，讓使用者主動告訴我們

在那個訊號存在以前，這份排行是「已知需求」的鏡子，不是「未知需求」的鏡子。

═══════════════════════════════════════════════════════════════════════════
GA4 custom-dimension 現實（graceful degradation）
═══════════════════════════════════════════════════════════════════════════
event param（term_id / direction / category / fork_type ...）只有先用 Admin API
註冊成 event-scoped custom dimension，才能在 Data API 當 DIMENSION group by。
Data API 引用方式：customEvent:term_id、customEvent:direction、customEvent:category。

註冊腳本：scripts/tools/register-ga4-custom-dimensions.py
（截至 2026-06-13，converter 的 param 還沒進那份 SSOT 的 *_DIMENSIONS list —
 orchestrator 會補一個 CONVERTER_DIMENSIONS block 再跑）。

本工具對兩種「還沒準備好」的情況都不 crash：
  (a) 維度還沒註冊 → GA4 回維度不存在的錯 → CATCH + 印 hint「跑 register 腳本」，
      該 report 留空、其他 report 照跑。
  (b) 事件剛上線、資料還沒累積 → report 空 → 印友善「instrumentation just shipped」。

用法:
    python3 scripts/tools/converter-demand.py                 # 90d + 28d
    python3 scripts/tools/converter-demand.py --json          # 純 JSON 輸出
    python3 scripts/tools/converter-demand.py --windows 90,28 # 自訂窗口（預設 90,28）
    python3 scripts/tools/converter-demand.py --limit 50      # 詞排行筆數（預設 50）

輸出:
    人類可讀 section 報表（同 converter-analytics.py 風格）
    raw JSON → ~/.config/taiwan-md/cache/converter-demand-latest.json

憑證 / venv 同 fetch-ga4.py（~/.config/taiwan-md/credentials/）。
來源: 2026-06-13 converter-demand-loop session
"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "taiwan-md"
CREDENTIALS_DIR = CONFIG_DIR / "credentials"
CACHE_DIR = CONFIG_DIR / "cache"
VENV_DIR = CONFIG_DIR / "venv"
ENV_FILE = CREDENTIALS_DIR / ".env"
SERVICE_ACCOUNT_FILE = CREDENTIALS_DIR / "google-service-account.json"
REGISTER_SCRIPT = "scripts/tools/register-ga4-custom-dimensions.py"

# Converter events emitted by src/pages/terminology/converter.astro.
EVT_LOOKUP = "converter_term_lookup"
EVT_CONVERT = "converter_convert"
EVT_EXAMPLE = "converter_example_click"
EVT_COPY = "converter_copy"
EVT_TOGGLE = "converter_direction_toggle"
ALL_EVENTS = [EVT_LOOKUP, EVT_CONVERT, EVT_EXAMPLE, EVT_COPY, EVT_TOGGLE]


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


# ─────────────────────────────────────────────────────────────────────────
# Custom-dimension graceful degradation
# ─────────────────────────────────────────────────────────────────────────
def _is_unregistered_dimension_error(exc):
    """Heuristic: did GA4 reject the request because a customEvent dimension
    isn't a registered event-scoped custom dimension yet?

    The Data API returns an INVALID_ARGUMENT whose message mentions the field
    is not a valid dimension / not compatible. We match loosely so a wording
    change on Google's side still degrades gracefully rather than crashing."""
    msg = str(exc).lower()
    needles = [
        "did not match",
        "not a valid",
        "is not a valid dimension",
        "incompatib",          # "are incompatible"
        "not compatible",
        "customevent",
        "field",
    ]
    return any(n in msg for n in needles)


class _Ctx:
    """Per-report helpers bound to one window: builds requests + runs them
    with custom-dimension-aware error handling. Each report writes a
    structured result dict so the caller can render hint / empty / data."""

    def __init__(self, client, prop, date_range, types):
        self.client = client
        self.prop = prop
        self.dr = date_range
        self.t = types  # the imported types module-ish namespace (a dict)

    def _event_filter(self, event_name):
        T = self.t
        return T["FilterExpression"](
            filter=T["Filter"](
                field_name="eventName",
                string_filter=T["Filter"].StringFilter(
                    match_type=T["Filter"].StringFilter.MatchType.EXACT,
                    value=event_name,
                ),
            )
        )

    def run_dimensioned(self, event_name, custom_dim, value_label):
        """One event filtered, grouped by a customEvent:<param> dimension,
        ordered by eventCount desc. Returns a structured status dict:
          {status: data|hint|empty|error, rows|message, dimension}
        """
        T = self.t
        try:
            req = T["RunReportRequest"](
                property=self.prop,
                date_ranges=[self.dr],
                dimensions=[T["Dimension"](name=custom_dim)],
                metrics=[T["Metric"](name="eventCount")],
                dimension_filter=self._event_filter(event_name),
                order_bys=[
                    T["OrderBy"](
                        metric=T["OrderBy"].MetricOrderBy(metric_name="eventCount"),
                        desc=True,
                    )
                ],
                limit=10000,
            )
            resp = self.client.run_report(req)
        except Exception as e:  # noqa: BLE001 — degrade, never crash
            if _is_unregistered_dimension_error(e):
                return {
                    "status": "hint",
                    "dimension": custom_dim,
                    "message": (
                        f"⚠️  custom dimension {custom_dim} not registered yet — "
                        f"add it to {REGISTER_SCRIPT} (CONVERTER_DIMENSIONS), run it, "
                        f"then wait for events to accumulate"
                    ),
                }
            return {"status": "error", "dimension": custom_dim, "message": f"{type(e).__name__}: {e}"}

        rows = [
            {value_label: (r.dimension_values[0].value or "(not set)"),
             "count": int(r.metric_values[0].value)}
            for r in resp.rows
        ]
        if not rows:
            return {"status": "empty", "dimension": custom_dim, "rows": []}
        return {"status": "data", "dimension": custom_dim, "rows": rows}

    def event_count(self, event_name):
        """Total eventCount for one event (no dimension). Returns int or None
        on error. Empty (event never fired) reads as 0, not error."""
        T = self.t
        try:
            req = T["RunReportRequest"](
                property=self.prop,
                date_ranges=[self.dr],
                metrics=[T["Metric"](name="eventCount")],
                dimension_filter=self._event_filter(event_name),
            )
            resp = self.client.run_report(req)
        except Exception:  # noqa: BLE001
            return None
        if not resp.rows:
            return 0
        return int(resp.rows[0].metric_values[0].value)


def fetch_window(property_id, cred_path, days, limit):
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

    types = {
        "DateRange": DateRange, "Dimension": Dimension, "Filter": Filter,
        "FilterExpression": FilterExpression, "Metric": Metric,
        "RunReportRequest": RunReportRequest, "OrderBy": OrderBy,
    }
    ctx = _Ctx(client, prop, dr, types)

    out = {"window_days": days, "start": start, "end": end}

    # ── Sanity: which converter_* events have ANY data in this window? ──────
    # Single grouped query by eventName, filtered to our 5 events. This is the
    # "did instrumentation produce anything yet?" probe and never needs a
    # custom dimension (eventName is a built-in dimension), so it works from
    # day one even before register-ga4-custom-dimensions.py runs.
    event_totals = {}
    try:
        in_filter = FilterExpression(
            filter=Filter(
                field_name="eventName",
                in_list_filter=Filter.InListFilter(values=ALL_EVENTS),
            )
        )
        resp = client.run_report(RunReportRequest(
            property=prop, date_ranges=[dr],
            dimensions=[Dimension(name="eventName")],
            metrics=[Metric(name="eventCount")],
            dimension_filter=in_filter,
            order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)],
            limit=25,
        ))
        for r in resp.rows:
            event_totals[r.dimension_values[0].value] = int(r.metric_values[0].value)
    except Exception as e:  # noqa: BLE001
        out["event_totals_error"] = f"{type(e).__name__}: {e}"
    out["event_totals"] = event_totals
    out["any_converter_events"] = sum(event_totals.values()) > 0

    # ── Report 1 (PRIMARY): term demand ranking ────────────────────────────
    term_rank = ctx.run_dimensioned(EVT_LOOKUP, "customEvent:term_id", "term_id")
    if term_rank.get("status") == "data":
        term_rank["rows"] = term_rank["rows"][:limit]
    out["term_demand"] = term_rank

    # ── Report 2: direction usage (convert split by direction) ─────────────
    # Primary: split converter_convert by customEvent:direction.
    out["direction_convert"] = ctx.run_dimensioned(
        EVT_CONVERT, "customEvent:direction", "direction")
    # Secondary cross-check: converter_direction_toggle by customEvent:to —
    # answers "how often did people actively flip the toggle, and to what".
    out["direction_toggle"] = ctx.run_dimensioned(
        EVT_TOGGLE, "customEvent:to", "to")

    # ── Report 3: example category popularity ──────────────────────────────
    out["example_categories"] = ctx.run_dimensioned(
        EVT_EXAMPLE, "customEvent:category", "category")

    # ── Report 4: funnel counts (convert → copy) ───────────────────────────
    convert_n = ctx.event_count(EVT_CONVERT)
    copy_n = ctx.event_count(EVT_COPY)
    lookup_n = ctx.event_count(EVT_LOOKUP)
    ratio = None
    if convert_n and copy_n is not None and convert_n > 0:
        ratio = round(copy_n / convert_n, 4)
    out["funnel"] = {
        "converter_convert": convert_n,
        "converter_copy": copy_n,
        "converter_term_lookup": lookup_n,
        "copy_per_convert": ratio,
    }

    return out


def _render_dim_report(title, rep, *, value_key, label_w=40, top=None):
    """Pretty-print one dimensioned report's status dict."""
    print(f"  ── {title} ──")
    if rep is None:
        print("    (report not run)")
        return
    st = rep.get("status")
    if st == "hint":
        print(f"    {rep['message']}")
        return
    if st == "error":
        print(f"    ⚠️  {rep['dimension']} error: {rep['message']}")
        return
    if st == "empty":
        print(f"    (no rows yet for {rep['dimension']} — instrumentation just shipped)")
        return
    rows = rep.get("rows", [])
    if top:
        rows = rows[:top]
    for i, row in enumerate(rows, 1):
        val = str(row.get(value_key, "(not set)"))
        print(f"    {i:>3}. {val:<{label_w}} {row['count']:>7}")


def render_human(result, windows, limit):
    for w in windows:
        ga = result["windows"].get(str(w), {})
        print(f"\n{'='*64}")
        print(f"📅 窗口 {w}d  ({ga.get('start','?')} → {ga.get('end','?')})")
        print(f"{'='*64}")

        if "error" in ga:
            print("  ❌ window error:", ga["error"])
            continue

        totals = ga.get("event_totals", {})
        if "event_totals_error" in ga:
            print("  ⚠️  event-totals probe error:", ga["event_totals_error"])
        if not ga.get("any_converter_events"):
            print("  ℹ️  no converter_* events in this window yet "
                  "(instrumentation just shipped — give it days/weeks).")
        else:
            print("  event totals:",
                  ", ".join(f"{ev}={totals.get(ev,0)}" for ev in ALL_EVENTS))

        # 1. PRIMARY — term demand
        print()
        _render_dim_report(
            f"① 詞需求排行 (top {limit} 查詢最多的 term_id) — PRIMARY",
            ga.get("term_demand"), value_key="term_id", label_w=40, top=limit)

        # 2. direction
        print()
        _render_dim_report("② 方向使用 — converter_convert by direction",
                           ga.get("direction_convert"), value_key="direction", label_w=12)
        _render_dim_report("   方向切換 — converter_direction_toggle (to)",
                           ga.get("direction_toggle"), value_key="to", label_w=12)

        # 3. example categories
        print()
        _render_dim_report("③ 範例分類熱度 — converter_example_click by category",
                           ga.get("example_categories"), value_key="category", label_w=28)

        # 4. funnel
        print()
        f = ga.get("funnel", {})
        print("  ── ④ 漏斗 convert → copy ──")

        def _fmt(v):
            return "(error)" if v is None else v
        print(f"    converter_convert     = {_fmt(f.get('converter_convert'))}")
        print(f"    converter_copy        = {_fmt(f.get('converter_copy'))}")
        print(f"    converter_term_lookup = {_fmt(f.get('converter_term_lookup'))}")
        cpc = f.get("copy_per_convert")
        print(f"    copy / convert ratio  = {cpc if cpc is not None else '(n/a — no converts yet)'}")

    print(f"\n💾 saved → {CACHE_DIR / 'converter-demand-latest.json'}")
    print("ℹ️  限制：此排行只含【現有詞】的需求，看不到缺漏詞（見 docstring）。")


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Converter demand-loop: read which terms people actually look up (GA4 events)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Reports (per 90d + 28d window):\n"
            "  ① term demand ranking  — converter_term_lookup × customEvent:term_id (PRIMARY)\n"
            "  ② direction usage      — converter_convert × customEvent:direction (+ toggle)\n"
            "  ③ example categories   — converter_example_click × customEvent:category\n"
            "  ④ funnel               — converter_convert / converter_copy counts\n\n"
            "Custom dims not registered yet → prints a hint and keeps going.\n"
            "No data yet → prints 'instrumentation just shipped' (events just deployed).\n"
            "LIMITATION: ranks demand among EXISTING terms only; does NOT reveal\n"
            "MISSING terms users typed that we don't yet map (see module docstring)."
        ),
    )
    parser.add_argument("--json", action="store_true", help="raw JSON only")
    parser.add_argument("--windows", default="90,28", help="comma-separated day windows (default 90,28)")
    parser.add_argument("--limit", type=int, default=50, help="how many top term_ids to show (default 50)")
    args = parser.parse_args()

    reexec_in_venv()

    env = load_env()
    property_id = env.get("GA4_PROPERTY_ID", "").strip()
    if not property_id:
        print(f"❌ GA4_PROPERTY_ID not set in {ENV_FILE}", file=sys.stderr)
        sys.exit(1)
    cred_path = SERVICE_ACCOUNT_FILE
    if not cred_path.exists():
        print(f"❌ service account missing at {cred_path}", file=sys.stderr)
        sys.exit(1)

    try:
        windows = [int(x) for x in args.windows.split(",") if x.strip()]
    except ValueError:
        print(f"❌ --windows must be comma-separated ints, got {args.windows!r}", file=sys.stderr)
        sys.exit(1)
    if not windows:
        windows = [90, 28]

    result = {
        "fetched_at": datetime.now().isoformat(),
        "property_id": property_id,
        "primary_signal": EVT_LOOKUP,
        "limitation": (
            "Ranks demand among EXISTING terms only (converter_term_lookup fires "
            "only on matched rules). Does NOT reveal missing terms users typed that "
            "we don't yet map — that needs a different future signal."
        ),
        "windows": {},
    }
    for w in windows:
        try:
            result["windows"][str(w)] = fetch_window(property_id, cred_path, w, args.limit)
        except Exception as e:  # noqa: BLE001 — one window failing shouldn't kill the rest
            result["windows"][str(w)] = {"error": f"{type(e).__name__}: {e}"}

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CACHE_DIR / "converter-demand-latest.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    render_human(result, windows, args.limit)


if __name__ == "__main__":
    main()
