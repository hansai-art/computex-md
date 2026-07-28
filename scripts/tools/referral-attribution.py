#!/usr/bin/env python3
"""referral-attribution.py — 流量來源 forensics + 遮蔽渠道偵測（ANALYSIS-PIPELINE mode B）

把 PTT 報告的發現儀器化（design §四「PTT 偵測器」）。很多最有黏性的來源（PTT 及其
鏡像 / app）因為連結帶 rel="noreferrer" → referrer 被擦空 → 在 GA 記成「直接造訪」，
讓最在乎你的讀者隱形（分析幻覺 H9 遮蔽渠道盲視）。

這支工具:
  1. 拆 pageReferrer + landingPage×source，找出某頁的真實來源結構
  2. 比對已知「遮蔽渠道指紋」（PTT 生態：disp.cc 鏡像 / jptt app / reurl 短網址 / ptt.cc）
  3. 算 repost 簽名分數：大量 (direct) 落地 + 生態尾巴 + 地理高度集中 + 行動裝置為主
     四訊號同時亮 = 高機率被外部論壇轉錄、referrer 被 noreferrer 洗白

用法:
  referral-attribution.py --filter 'pagePath~Computex' --start 3daysAgo --end today
  referral-attribution.py --filter 'pagePath=/technology/Computex/' --start 3d --end today --json

退出碼: 0 OK / 1 偵測到 repost 簽名（提醒去查外部來源）/ 2 參數錯。

來源: 2026-06-05 ANALYSIS-PIPELINE 造橋（ptt-computex-discussion-analysis 報告 §二 noreferrer 發現）。
"""
import argparse
import json
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib.sense_client import reexec_in_venv  # noqa: E402
reexec_in_venv()
from lib.sense_client import ga_run  # noqa: E402

# 已知遮蔽渠道指紋（referrer 或 source 子字串 → 人話）。可擴充（dcard / mobile01 …）。
MASKED_FINGERPRINTS = {
    "disp.cc": "PTT 網頁鏡像站",
    "jptt": "JPTT（PTT Android app）",
    "ptt.cc": "PTT 直接",
    "pttweb": "PTT web",
    "reurl.cc": "短網址（常見於 PTT 推文）",
    "term.ptt": "PTT 終端機 web",
}


def parse_filter(s):
    for op, tag in (("~", "contains"), ("^", "begins"), ("#", "regex"), ("=", "exact")):
        if op in s:
            f, _, v = s.partition(op)
            return (f.strip(), tag, v.strip())
    raise ValueError(f"bad filter: {s}")


def norm_date(d):
    import re
    m = re.match(r"^(\d+)d$", d)
    return f"{m.group(1)}daysAgo" if m else d


def main():
    ap = argparse.ArgumentParser(description="Referral forensics + masked-channel detector")
    ap.add_argument("--filter", action="append", default=[], required=True)
    ap.add_argument("--start", default="3daysAgo")
    ap.add_argument("--end", default="today")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--save", default=None)
    a = ap.parse_args()
    flt = [parse_filter(f) for f in a.filter]
    start, end = norm_date(a.start), norm_date(a.end)

    referrer = ga_run(["pageReferrer"], ["screenPageViews", "activeUsers"], start, end,
                      dim_filter=flt, order_by="screenPageViews", limit=50)
    geo = ga_run(["country"], ["activeUsers"], start, end, dim_filter=flt,
                 order_by="activeUsers", limit=30)
    device = ga_run(["deviceCategory"], ["activeUsers"], start, end, dim_filter=flt,
                    order_by="activeUsers", limit=10)

    # blank / direct referrer volume (the masked bucket)
    blank_pv = sum(int(r["mets"][0]) for r in referrer if r["dims"][0].strip() == "")
    total_pv = sum(int(r["mets"][0]) for r in referrer) or 1
    blank_share = blank_pv / total_pv

    # ecosystem-tail fingerprints present?
    found = []
    for r in referrer:
        ref = r["dims"][0].lower()
        for fp, human in MASKED_FINGERPRINTS.items():
            if fp in ref:
                found.append({"referrer": r["dims"][0], "pv": int(r["mets"][0]), "channel": human})

    # geo concentration + mobile share
    geo_total = sum(int(r["mets"][0]) for r in geo) or 1
    top_country = (geo[0]["dims"][0], int(geo[0]["mets"][0]) / geo_total) if geo else ("?", 0)
    dev_total = sum(int(r["mets"][0]) for r in device) or 1
    mobile_share = sum(int(r["mets"][0]) for r in device if r["dims"][0] == "mobile") / dev_total

    # repost signature: 4 signals
    sig = {
        "blank_referrer_heavy": blank_share >= 0.30,
        "ecosystem_tail_present": len(found) > 0,
        "geo_concentrated": top_country[1] >= 0.70,
        "mobile_heavy": mobile_share >= 0.45,
    }
    score = sum(sig.values())
    verdict = ("🚨 高機率被外部論壇轉錄（referrer 被 noreferrer 洗白）" if score >= 3
               else "⚠️ 部分訊號，可能有遮蔽來源" if score == 2
               else "— 無明顯 repost 簽名")

    payload = {
        "filter": a.filter, "start": start, "end": end,
        "total_referrer_pv": total_pv, "blank_referrer_pv": blank_pv, "blank_share": round(blank_share, 3),
        "masked_fingerprints": found,
        "top_country": {"name": top_country[0], "share": round(top_country[1], 3)},
        "mobile_share": round(mobile_share, 3),
        "repost_signals": sig, "repost_score": score, "verdict": verdict,
        "referrer_breakdown": [{"referrer": r["dims"][0] or "(direct/blank)", "pv": int(r["mets"][0])} for r in referrer[:20]],
    }
    if a.save:
        pathlib.Path(a.save).parent.mkdir(parents=True, exist_ok=True)
        json.dump(payload, open(a.save, "w"), ensure_ascii=False, indent=2)
        print(f"💾 {a.save}", file=sys.stderr)
    if a.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        sys.exit(1 if score >= 3 else 0)

    print(f"頁面 filter={a.filter}  {start}..{end}\n")
    print(f"(direct/blank) referrer：{blank_pv} pv（占 {blank_share*100:.0f}%）← noreferrer 洗白的主體可能在這")
    print(f"top country：{top_country[0]} {top_country[1]*100:.0f}%   mobile：{mobile_share*100:.0f}%\n")
    if found:
        print("遮蔽渠道指紋（漏出來、可追溯的尾巴）：")
        for f in found:
            print(f"  {f['referrer']:<40} {f['pv']:>4} pv  → {f['channel']}")
    else:
        print("（無已知遮蔽渠道指紋）")
    print(f"\nrepost 4 訊號：blank≥30%={sig['blank_referrer_heavy']} / 生態尾巴={sig['ecosystem_tail_present']} / "
          f"地理集中≥70%={sig['geo_concentrated']} / 行動≥45%={sig['mobile_heavy']}  → 分數 {score}/4")
    print(f"判定：{verdict}")
    if score >= 3:
        print("\n→ 去搜尋外部論壇（PTT / Dcard / Mobile01 等）確認被轉錄的串，跑 ANALYSIS-PIPELINE mode D 接收分析")
    sys.exit(1 if score >= 3 else 0)


if __name__ == "__main__":
    main()
