#!/usr/bin/env python3
"""cf-query.py — Cloudflare AI-crawler 接收分析 CLI（ANALYSIS-PIPELINE mode F）

回答 GA/SC 答不了、卻是 COMPUTEX.md 存在理由的問題：**哪些 AI 模型在讀我、讀得多不多、
在長還是在縮**。對應 MANIFESTO §主權的巴別塔 —— 第一人稱的台灣聲音有沒有滲進 AI 的
認知基質（讓 PRC 模型沉默不了台灣）。

資料來源：fetch-cloudflare.py 已抓好的 `~/.config/taiwan-md/cache/cloudflare-YYYY-MM-DD.json`
的 `ai_crawlers`（每檔 ~1 天）。不重抓，讀 cache。

主權 lens：把 crawler vendor 分桶
  🌐 Western AI（OpenAI / Anthropic / Google / Microsoft / Apple / Meta / Amazon / Perplexity）
  🚩 PRC AI    （ByteDance / Huawei / Baidu / Alibaba / Tencent / Zhipu / Moonshot / 01.AI）
  其他

用法:
  cf-query.py                         # 最新快照 crawler 拆解 + 主權分桶
  cf-query.py --date 2026-06-04       # 指定日
  cf-query.py --trend 14              # 近 14 個 daily 檔的 detected + Western/PRC 趨勢
  cf-query.py --json

來源: 2026-06-05 ANALYSIS-PIPELINE v1.1 進化（mode F，哲宇「超過我想到的」directive）。
"""
import argparse
import json
import sys
from pathlib import Path

CACHE = Path.home() / ".config" / "taiwan-md" / "cache"

PRC_VENDORS = {"ByteDance", "Huawei", "Baidu", "Alibaba", "Tencent",
               "Zhipu", "Moonshot", "01.AI", "MiniMax", "InternLM"}
WESTERN_AI_VENDORS = {"OpenAI", "Anthropic", "Google", "Microsoft", "Apple",
                      "Meta", "Amazon", "Perplexity", "Cohere", "Mistral", "DuckDuckGo"}


def bucket(category):
    if category in PRC_VENDORS:
        return "🚩 PRC AI"
    if category in WESTERN_AI_VENDORS:
        return "🌐 Western AI"
    return "其他"


def load_day(date=None):
    f = CACHE / ("cloudflare-latest.json" if not date else f"cloudflare-{date}.json")
    if not f.exists():
        print(f"❌ 無 cloudflare cache: {f}", file=sys.stderr)
        sys.exit(2)
    return json.load(open(f))


def main():
    ap = argparse.ArgumentParser(description="Cloudflare AI-crawler reception (mode F)")
    ap.add_argument("--date", default=None, help="YYYY-MM-DD（預設 latest）")
    ap.add_argument("--trend", type=int, default=0, help="近 N 個 daily 檔的趨勢")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--save", default=None)
    a = ap.parse_args()

    if a.trend:
        files = sorted(CACHE.glob("cloudflare-2026-*.json"))[-a.trend:]
        trend = []
        for f in files:
            d = json.load(open(f))
            ac = d.get("ai_crawlers") or {}
            crs = ac.get("crawlers") or []
            west = sum(c["requests"] for c in crs if bucket(c["category"]) == "🌐 Western AI")
            prc = sum(c["requests"] for c in crs if bucket(c["category"]) == "🚩 PRC AI")
            det = (ac.get("totals") or {}).get("detectedRequests", 0)
            trend.append({"file": f.name.replace("cloudflare-", "").replace(".json", ""),
                          "detected": det, "western_ai": west, "prc_ai": prc})
        if a.json:
            print(json.dumps({"trend": trend}, ensure_ascii=False, indent=2))
            return
        print(f"{'date':<12}{'detected':>10}{'🌐West':>9}{'🚩PRC':>8}")
        for t in trend:
            print(f"{t['file']:<12}{t['detected']:>10}{t['western_ai']:>9}{t['prc_ai']:>8}")
        return

    d = load_day(a.date)
    ac = d.get("ai_crawlers") or {}
    crs = sorted(ac.get("crawlers") or [], key=lambda c: -c["requests"])
    totals = ac.get("totals") or {}

    buckets = {}
    for c in crs:
        b = bucket(c["category"])
        buckets.setdefault(b, {"requests": 0, "http200": 0, "names": []})
        buckets[b]["requests"] += c["requests"]
        buckets[b]["http200"] += c.get("http200", 0)
        buckets[b]["names"].append(c["name"])
    grand = sum(b["requests"] for b in buckets.values()) or 1

    payload = {
        "period": ac.get("period"), "totals": totals,
        "crawlers": crs,
        "sovereignty_buckets": {k: {**v, "share": round(v["requests"] / grand, 3)} for k, v in buckets.items()},
    }
    if a.save:
        Path(a.save).parent.mkdir(parents=True, exist_ok=True)
        json.dump(payload, open(a.save, "w"), ensure_ascii=False, indent=2)
        print(f"💾 {a.save}", file=sys.stderr)
    if a.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    p = ac.get("period") or {}
    print(f"AI crawler 接收 — {p.get('start','?')[:10]}..{p.get('end','?')[:10]}  "
          f"(detected {totals.get('detectedRequests','?')} req)\n")
    print(f"{'crawler':<20}{'vendor':<14}{'req':>7}{'200%':>7}  bucket")
    print("-" * 62)
    for c in crs[:20]:
        rate = c.get("http200", 0) / c["requests"] * 100 if c["requests"] else 0
        print(f"{c['name']:<20}{c['category']:<14}{c['requests']:>7}{rate:>6.0f}%  {bucket(c['category'])}")
    print("\n=== 主權分桶（誰在讀台灣的聲音）===")
    for b in ("🌐 Western AI", "🚩 PRC AI", "其他"):
        if b in buckets:
            v = buckets[b]
            print(f"  {b:<14} {v['requests']:>6} req ({v['share']*100 if False else round(v['requests']/grand*100):>2}%)  "
                  f"{', '.join(sorted(set(v['names']))[:6])}")
    print("\n💡 sovereignty 讀法：Western AI 讀我 = 台灣第一人稱聲音進入 cognitive substrate；"
          "PRC AI 讀我但低 200% = 可能 content policy 過濾。趨勢看 --trend。")


if __name__ == "__main__":
    main()
