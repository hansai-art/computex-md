#!/usr/bin/env python3
"""ga-window-compare.py — before/after 影響比較器（ANALYSIS-PIPELINE Stage 2-4）

把首頁改版 D+10 報告的方法論儀器化。給兩個窗口 + 一個 page filter，吐出一張
「率紀律 + 尺度消歧 + lag 自偵測」的 before/after 表，幫你不踩分析幻覺（H1-H9）。

內建的判斷:
  - H1 尺度混淆: 同時報 session 級 avgSessionDuration **和** page 級
    userEngagementDuration/user，分開標，不讓你把 session 級當 page 級。
  - H2 率量混淆: 同時報率（engagementRate/bounceRate）跟量（users/sessions），
    當兩窗口 user 數差 >15% 時印警告「看率不看量」。
  - H3 結算延遲: 自動掃每窗口每日，engRate<2% 且 bounce>98% = lag 汙染日，警告排除。
  - H6 新鮮感: 不自動判，但 --daily 印逐日讓你看有沒有 launch spike。
  - H7 自我驗證: 印「最強反解釋提示」提醒跑 Stage 5 FALSIFY。

用法:
  ga-window-compare.py --filter 'pagePath=/' \\
     --before 2026-05-19 2026-05-25 --after 2026-05-29 2026-06-03
  ga-window-compare.py --filter 'pagePath=/' --before A B --after C D --cohort   # 新/回訪拆
  ga-window-compare.py --filter 'pagePath=/' --before A B --after C D --daily --json --save out.json

filter: 同 ga-query（field=value / field~contains / field^begins）。
退出碼: 0 OK / 1 lag 汙染未排除（警告）/ 2 參數錯。

來源: 2026-06-05 ANALYSIS-PIPELINE 造橋（design §四 + homepage-redesign-impact-D+10 報告方法論）。
"""
import argparse
import json
import math
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib.sense_client import reexec_in_venv  # noqa: E402
reexec_in_venv()
from lib.sense_client import ga_run  # noqa: E402


def two_prop_z(eng_b, n_b, eng_a, n_a):
    """Two-proportion z-test on engaged-session rate. Returns (z, significant).
    H11: 顯著性守衛 — 小樣本的 rate 差可能純雜訊。|z|>=2 ≈ 95%。"""
    if n_b == 0 or n_a == 0:
        return 0.0, False
    pb, pa = eng_b / n_b, eng_a / n_a
    se = math.sqrt(pb * (1 - pb) / n_b + pa * (1 - pa) / n_a)
    if se == 0:
        return 0.0, False
    z = (pa - pb) / se
    return z, abs(z) >= 2.0

CORE_METRICS = ["activeUsers", "sessions", "screenPageViews", "userEngagementDuration",
                "averageSessionDuration", "engagementRate", "bounceRate", "engagedSessions"]


def parse_filter(s):
    for op, tag in (("~", "contains"), ("^", "begins"), ("#", "regex"), ("=", "exact")):
        if op in s:
            f, _, v = s.partition(op)
            return (f.strip(), tag, v.strip())
    raise ValueError(f"bad filter: {s}")


def agg(flt, start, end):
    rows = ga_run([], CORE_METRICS, start, end, dim_filter=flt)
    m = {k: float(v) for k, v in zip(CORE_METRICS, rows[0]["mets"])} if rows else {k: 0.0 for k in CORE_METRICS}
    u = m["activeUsers"] or 1
    s = m["sessions"] or 1
    return {
        "users": int(m["activeUsers"]), "sessions": int(m["sessions"]),
        "pv": int(m["screenPageViews"]), "engagedSessions": int(m["engagedSessions"]),
        "avgSessionDur_s": m["averageSessionDuration"],            # session-scoped (H1!)
        "pageEngDur_per_user_s": m["userEngagementDuration"] / u,   # page-scoped
        "pageEngDur_per_sess_s": m["userEngagementDuration"] / s,
        "engagementRate": m["engagementRate"], "bounceRate": m["bounceRate"],
    }


def daily(flt, start, end):
    rows = ga_run(["date"], ["screenPageViews", "engagementRate", "bounceRate", "averageSessionDuration"],
                  start, end, dim_filter=flt, order_by=None)
    out = []
    for r in sorted(rows, key=lambda x: x["dims"][0]):
        out.append({"date": r["dims"][0], "pv": int(r["mets"][0]),
                    "engRate": float(r["mets"][1]), "bounce": float(r["mets"][2]),
                    "avgDur": float(r["mets"][3])})
    return out


def lag_days(daily_rows):
    return [d["date"] for d in daily_rows if d["engRate"] < 0.02 and d["bounce"] > 0.98]


def cohort(flt, start, end):
    rows = ga_run(["newVsReturning"], ["activeUsers", "sessions", "averageSessionDuration",
                  "userEngagementDuration", "engagementRate"], start, end, dim_filter=flt)
    out = {}
    for r in rows:
        k = r["dims"][0]
        u = float(r["mets"][0]) or 1
        out[k] = {"users": int(float(r["mets"][0])), "avgSessionDur_s": float(r["mets"][2]),
                  "pageEngDur_per_user_s": float(r["mets"][3]) / u,
                  "engagementRate": float(r["mets"][4])}
    return out


def pct(b, a):
    return (a - b) / b * 100 if b else float("nan")


def main():
    ap = argparse.ArgumentParser(description="GA4 before/after impact comparator")
    ap.add_argument("--filter", action="append", default=[], help="page filter (e.g. pagePath=/)")
    ap.add_argument("--control", action="append", default=[], help="H10 控制組 filter（沒被改的表面，如 pagePath~/technology/）→ 算 DiD 減掉大盤趨勢")
    ap.add_argument("--before", nargs=2, metavar=("START", "END"), required=True)
    ap.add_argument("--after", nargs=2, metavar=("START", "END"), required=True)
    ap.add_argument("--cohort", action="store_true", help="add new-vs-returning split")
    ap.add_argument("--daily", action="store_true", help="print per-day rows (spot novelty spikes)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--save", default=None)
    a = ap.parse_args()

    flt = [parse_filter(f) for f in a.filter] if a.filter else None
    B = agg(flt, *a.before)
    A = agg(flt, *a.after)
    bd, ad = daily(flt, *a.before), daily(flt, *a.after)
    blag, alag = lag_days(bd), lag_days(ad)

    # H11 顯著性：engaged session rate 兩比例 z 檢定
    z, signif = two_prop_z(B["engagedSessions"], B["sessions"], A["engagedSessions"], A["sessions"])

    # H10 控制組 / DiD：減掉大盤趨勢
    diff_in_diff = None
    C = CA = None
    if a.control:
        cflt = [parse_filter(f) for f in a.control]
        C = agg(cflt, *a.before)
        CA = agg(cflt, *a.after)
        target_d = (A["engagementRate"] - B["engagementRate"]) * 100      # pp
        control_d = (CA["engagementRate"] - C["engagementRate"]) * 100    # pp
        diff_in_diff = {"target_delta_pp": round(target_d, 1),
                        "control_delta_pp": round(control_d, 1),
                        "net_pp": round(target_d - control_d, 1)}

    rows = [
        ("avgSessionDuration (s) [session 級·H1]", B["avgSessionDur_s"], A["avgSessionDur_s"], "{:.0f}"),
        ("pageEngDur/user (s) [page 級·H1]", B["pageEngDur_per_user_s"], A["pageEngDur_per_user_s"], "{:.1f}"),
        ("engagementRate [率·H2]", B["engagementRate"] * 100, A["engagementRate"] * 100, "{:.0f}%"),
        ("bounceRate [率·H2]", B["bounceRate"] * 100, A["bounceRate"] * 100, "{:.0f}%"),
        ("activeUsers [量·H2]", B["users"], A["users"], "{:.0f}"),
        ("sessions [量·H2]", B["sessions"], A["sessions"], "{:.0f}"),
        ("engagedSessions [量·H2]", B["engagedSessions"], A["engagedSessions"], "{:.0f}"),
    ]

    warnings = []
    if blag:
        warnings.append(f"⚠️ H3 lag: BEFORE 窗有 attribution-lag 汙染日 {blag} → 應排除重跑")
    if alag:
        warnings.append(f"⚠️ H3 lag: AFTER 窗有 attribution-lag 汙染日 {alag} → 應排除重跑")
    if B["users"] and abs(A["users"] - B["users"]) / B["users"] > 0.15:
        warnings.append(f"⚠️ H2 率量: user 數差 {pct(B['users'], A['users']):+.0f}% (>15%) → 結論一律用率(engagementRate/bounce/page級)，不用絕對量")
    if pct(B["avgSessionDur_s"], A["avgSessionDur_s"]) > 50 and pct(B["pageEngDur_per_user_s"], A["pageEngDur_per_user_s"]) < 50:
        warnings.append("⚠️ H1 尺度: avgSessionDuration 大漲但 page 級 engDur 沒跟上 → 是 session 變深(往下走)，不是首頁本身停更久。別把 session 級講成 page 級")
    if not signif:
        warnings.append(f"⚠️ H11 顯著性: engaged-rate 差異 z={z:.1f} (<2) → 可能是雜訊，樣本不夠別當勝利")
    if a.control and diff_in_diff and B["engagementRate"] > 0:
        cd = diff_in_diff["control_delta_pp"]
        if abs(cd) >= 3:
            warnings.append(f"⚠️ H10 控制組: 控制組 engagementRate 同期也動了 {cd:+.1f}pp（大盤趨勢）→ 淨效果 = {diff_in_diff['net_pp']:+.1f}pp，不是 target 的全部變化")

    payload = {
        "filter": a.filter, "before": a.before, "after": a.after,
        "before_agg": B, "after_agg": A, "before_lag_days": blag, "after_lag_days": alag,
        "deltas": {r[0]: {"before": r[1], "after": r[2], "pct": pct(r[1], r[2])} for r in rows},
        "significance": {"engaged_rate_z": round(z, 2), "significant_95": signif},
        "diff_in_diff": diff_in_diff,
        "warnings": warnings,
    }
    if a.cohort:
        payload["cohort_before"] = cohort(flt, *a.before)
        payload["cohort_after"] = cohort(flt, *a.after)
    if a.daily:
        payload["before_daily"], payload["after_daily"] = bd, ad

    if a.save:
        pathlib.Path(a.save).parent.mkdir(parents=True, exist_ok=True)
        json.dump(payload, open(a.save, "w"), ensure_ascii=False, indent=2)
        print(f"💾 {a.save}", file=sys.stderr)
    if a.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(f"filter={a.filter}  BEFORE {a.before[0]}..{a.before[1]}  vs  AFTER {a.after[0]}..{a.after[1]}\n")
    print(f"{'metric':<40}{'BEFORE':>12}{'AFTER':>12}{'Δ':>10}")
    print("-" * 74)
    for label, b, av, fmt in rows:
        d = pct(b, av)
        ds = ("+" if d >= 0 else "") + (f"{d:.0f}%" if d == d else "n/a")
        print(f"{label:<40}{fmt.format(b):>12}{fmt.format(av):>12}{ds:>10}")
    sig_tag = "✅顯著(95%)" if signif else "⚠️雜訊範圍"
    print(f"\nengaged-rate 顯著性 [H11]: z={z:.1f}  {sig_tag}")
    if diff_in_diff:
        print(f"控制組 DiD [H10]: target {diff_in_diff['target_delta_pp']:+.1f}pp − "
              f"控制組 {diff_in_diff['control_delta_pp']:+.1f}pp = 淨效果 {diff_in_diff['net_pp']:+.1f}pp（已減大盤趨勢）")
    if a.cohort:
        print("\n— new vs returning —")
        for win, c in (("BEFORE", payload.get("cohort_before", {})), ("AFTER", payload.get("cohort_after", {}))):
            for k, v in c.items():
                print(f"  {win} {k:<10} users={v['users']:<6} pageEngDur/user={v['pageEngDur_per_user_s']:.0f}s engRate={v['engagementRate']*100:.0f}%")
    if a.daily:
        for win, dd in (("BEFORE", bd), ("AFTER", ad)):
            print(f"\n— {win} daily —")
            for d in dd:
                flag = " ⚠lag" if (d["engRate"] < 0.02 and d["bounce"] > 0.98) else ""
                print(f"  {d['date']}  pv={d['pv']:<5} engRate={d['engRate']*100:.0f}% bounce={d['bounce']*100:.0f}% avgDur={d['avgDur']:.0f}s{flag}")
    if warnings:
        print("\n=== confounder 旗標 ===")
        for w in warnings:
            print(" " + w)
    print("\n💡 Stage 5 FALSIFY 提示：最強反解釋通常是「率上升其實是流量混入(壞流量退場)」——"
          "用 per-user 指標(page級 engDur/新訪客)繞過，那是跟流量量無關的證據。")
    sys.exit(1 if (blag or alag) else 0)


if __name__ == "__main__":
    main()
