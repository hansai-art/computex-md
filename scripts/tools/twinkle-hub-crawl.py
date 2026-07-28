#!/usr/bin/env python3
"""
twinkle-hub-crawl.py — 完整盤點 Twinkle Hub MCP surface，落 src/data/opendata-curation.json

給 /opendata（OpenData 策展頁）的資料層。重用 twinkle-hub-verify.py 的
session 握手與呼叫邏輯（per MANIFESTO §指標 over 複寫，不複寫 MCP client）。

抓三層：
  1. tools/list      — 全部工具的 name + description + inputSchema
  2. list_domains    — 19 domain 的 scope / typical_questions / anchor_examples
  3. get_dataset ×N  — pilot 文章引用的 showcase 資料集完整 metadata

Rate limit 紀律：每 call 間隔 1.2s（2026-06-10 實測 query_rows 曾 429）。

Usage:
    python3 scripts/tools/twinkle-hub-crawl.py            # 全量爬 + 寫 JSON
    python3 scripts/tools/twinkle-hub-crawl.py --dry-run  # 只印 summary 不寫檔
"""

import importlib.util
import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "src" / "data" / "opendata-curation.json"

# 載入 twinkle-hub-verify.py 當 module（檔名含 dash 不能直接 import）
spec = importlib.util.spec_from_file_location(
    "twinkle_hub_verify", pathlib.Path(__file__).parent / "twinkle-hub-verify.py"
)
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)

PAUSE = 1.2

# pilot 文章（2026-06-10 公開數據指標 pilot commit 7678a430b）引用的 showcase 資料集
SHOWCASE_IDS = [
    "10859",   # 台電近10年核能發電績效及減碳效益
    "10858",   # 台電核能發電廠位置及機組設備
    "133848",  # 核能後端營運基金回饋要點
    "121267",  # 北市國民住宅配售(租)情形
    "155779",  # 北市社宅包租代管媒合統計
    "lvr-trades",  # 全國實價登錄・買賣（Twinkle 自策 namespace）
    "20254",   # 健保保險對象人數按類別性別年齡層
    "7554",    # 健保會議事錄
    "23719",   # 健保各級政府補助弱勢保險對象
    "10918",   # 攤販經營概況調查
    "85028",   # 臺中市列管夜市
    "14208",   # 機動車輛登記數統計
    "25932",   # 桃園A1A2事故傷亡(91-114年)
    "27491",   # 選舉人數（中選會）
    "15035",   # 違反選罷法裁判確定人數
]


def wall_clock():
    return subprocess.check_output(["date", "+%Y-%m-%dT%H:%M:%S%z"]).decode().strip()


def main():
    dry = "--dry-run" in sys.argv

    print("1/3 tools/list …", file=sys.stderr)
    tools_raw = hub.mcp_call("tools/list", params={}, request_id=10)
    tools = [
        {
            "name": t["name"],
            "description": t.get("description", ""),
            "inputSchema": t.get("inputSchema", {}),
        }
        for t in tools_raw.get("result", {}).get("tools", [])
    ]
    time.sleep(PAUSE)

    print("2/3 list_domains …", file=sys.stderr)
    domains_res = hub.call_tool("list_domains", {})
    domains = domains_res.get("data", {}).get("domains", []) if domains_res["ok"] else []
    domains_version = domains_res.get("data", {}).get("version") if domains_res["ok"] else None
    time.sleep(PAUSE)

    print(f"3/3 get_dataset × {len(SHOWCASE_IDS)} …", file=sys.stderr)
    showcase = []
    for ds_id in SHOWCASE_IDS:
        res = hub.call_tool("get_dataset", {"dataset_id": ds_id})
        if res["ok"]:
            d = res["data"]
            showcase.append(
                {
                    "dataset_id": d.get("dataset_id", ds_id),
                    "name": d.get("name"),
                    "agency": d.get("agency"),
                    "primary_domain": d.get("primary_domain"),
                    "domains": d.get("domains", []),
                    "quality_tier": d.get("quality_tier"),
                    "update_freq": d.get("update_freq"),
                    "formats": d.get("formats", []),
                    "license": d.get("license"),
                    "actual_columns": d.get("actual_columns", []),
                    "join_keys": d.get("join_keys", []),
                    "join_keys_domain_hint": d.get("join_keys_domain_hint", []),
                    "data_volume_total": d.get("data_volume_total"),
                    "description": d.get("description", ""),
                    "metadata_updated": d.get("metadata_updated"),
                }
            )
            print(f"   ✓ {ds_id} {d.get('name','')[:30]}", file=sys.stderr)
        else:
            showcase.append({"dataset_id": ds_id, "error": str(res["error"])[:200]})
            print(f"   ✗ {ds_id}: {str(res['error'])[:80]}", file=sys.stderr)
        time.sleep(PAUSE)

    payload = {
        "crawled_at": wall_clock(),
        "source": {
            "endpoint": "https://api.twinkleai.tw/mcp/",
            "hub": "https://hub.twinkleai.tw/",
            "note": "tool inventory + domain taxonomy 為 MCP API 即時爬取；總量數字（49,343 datasets / 13.5 萬採購紀錄）為 2026-06-05 hub.twinkleai.tw 頁面盤點",
        },
        "totals": {
            "datasets_claimed": 49343,
            "datasets_claimed_asof": "2026-06-05",
            "procurement_records_claimed": 135000,
            "tools": len(tools),
            "domains": len(domains),
        },
        "domains_version": domains_version,
        "tools": tools,
        "domains": domains,
        "showcase_datasets": showcase,
    }

    if dry:
        print(json.dumps(payload["totals"], ensure_ascii=False, indent=2))
        return

    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ok_n = sum(1 for s in showcase if "error" not in s)
    print(f"✅ {OUT.relative_to(ROOT)} — tools={len(tools)} domains={len(domains)} showcase={ok_n}/{len(SHOWCASE_IDS)}")


if __name__ == "__main__":
    main()
