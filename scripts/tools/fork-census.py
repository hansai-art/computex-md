#!/usr/bin/env python3
"""fork-census.py — 子代普查雷達（繁殖器官的感知層）

為什麼存在：COMPUTEX.md 的 GA4 measurement ID (G-JGC5W00N7T) 寫死在 Layout.astro。
任何 fork 沒換掉它，pageview 就漏進我們的 GA property。哲宇 2026-06-25 決定「不修，
這樣可以探測很有趣」—— 把漏水當成繁殖雷達。但 GA 只保留 ~14 個月滾動窗，子代指紋會
在我看見牠之前滾出視窗（Sweden.md 這次就沒出現）。

這支 probe 把「哲宇剛好截到 GA 圖」這條泥巴路鋪成高速公路（REFLEXES #15 反覆浮現要儀器化）：
定期撈 GA 的 hostName + pageTitle，分類、去重、append 到一份永久子代名冊。漏水照漏、
探測照玩，但每次 sighting 都被永久存下來。

設計分層（關鍵）：
  - GA-derived 欄位（views / users / last_seen / hostnames / title_brands）= 每次跑自動更新
  - investigation-derived 欄位（github / credits / type / cognitive_layer / notes）= sticky，
    probe 永不覆寫，只有人/agent 調查後手動填。新偵測到的 fork metadata 標 "(unverified)"。

用法:
  fork-census.py                      # 跑普查，更新 registry，印 diff
  fork-census.py --window 90daysAgo   # 自訂回看窗（預設 365daysAgo）
  fork-census.py --dry-run            # 只印不寫檔
  fork-census.py --json               # 印 registry JSON

退出碼: 0 OK / 1 GA 失敗（fail-loud，不寫空 registry — REFLEXES #60）/ 2 參數錯。

來源: 2026-06-25 fork-census 造橋（哲宇「探測很有趣，完整自我進化」directive）。
"""
import argparse
import json
import re
import sys
import pathlib
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
REGISTRY = HERE.parent.parent / "reports" / "fork-census" / "registry.json"

sys.path.insert(0, str(HERE))
from lib.sense_client import reexec_in_venv  # noqa: E402
reexec_in_venv()
from lib.sense_client import ga_run  # noqa: E402

# ── hostName 分類 ────────────────────────────────────────────────────────────
# OURS：我們自己（含 Google 翻譯代理 / Cloudflare 預覽）
RE_OURS = re.compile(r"(^|\.)taiwan\.md$|^taiwan-md\.(translate\.goog|pages\.dev)$", re.I)
# DEV：本機開發 noise（含所有 fork 開發者跑 localhost）—— 不算子代，但記總量當「孵化中」訊號
RE_DEV = re.compile(
    r"^(localhost|127\.0\.0\.1|0\.0\.0\.0|"
    r"192\.168\.|10\.\d|172\.(1[6-9]|2\d|3[01])\.)|\.local$", re.I)
# PROXY：第三方代理存取我們（不是 fork）
RE_PROXY = re.compile(r"proxysite|\.nyud\.net$|webcache", re.I)


def classify_host(host):
    if RE_OURS.search(host):
        return "ours"
    if RE_DEV.search(host):
        return "dev"
    if RE_PROXY.search(host):
        return "proxy"
    return "fork"


def title_brand(title):
    """從頁面標題抽 fork 品牌。標題格式 '<page> | <SiteBrand>' 或 '<page> — <Brand> | <Brand>'。
    回傳最後一段 '| ' 後的品牌；非 fork（COMPUTEX.md / 空）回 None。"""
    if "|" not in title:
        return None
    brand = title.rsplit("|", 1)[-1].strip()
    if not brand or re.search(r"taiwan\.md", brand, re.I) or "台灣" in brand and ".md" not in brand.lower():
        return None
    return brand


def ym():
    return datetime.now(timezone.utc).strftime("%Y-%m")


def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ── registry I/O ─────────────────────────────────────────────────────────────
def load_registry():
    if REGISTRY.exists():
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {"_meta": {"created": today(), "ga_id": "G-JGC5W00N7T",
                      "note": "Auto fields (ga/last_seen/hostnames/title_brands) "
                              "refreshed by fork-census.py. Investigation fields "
                              "(github/credits/type/cognitive_layer/notes) are "
                              "sticky — only humans/agents fill them."},
            "forks": []}


def find_entry(forks, host=None, brand=None):
    """Match a sighting to an existing entry by EXACT hostname or title-brand
    membership. No fuzzy substring linking — it over-matched (stuffed unrelated
    brands onto entries, caught on first dogfood 2026-06-25). The curated
    registry lists BOTH fingerprints per fork, so exact membership suffices:
    a fork's hostname AND its title-brand both resolve to the same entry."""
    for e in forks:
        if host and host in e.get("hostnames", []):
            return e
        if brand and brand in e.get("title_brands", []):
            return e
    return None


STUB = {"id": "", "label": "", "hostnames": [], "title_brands": [],
        "type": "(unverified)", "topic": "(unverified)", "language": "",
        "github": "", "network_fork": None, "credits_upstream": None,
        "cognitive_layer": "(unverified)", "ga_leaking": True,
        "deployment": "", "health": "", "confidence": "low",
        "notes": "auto-detected via GA leak — needs investigation"}


def main():
    ap = argparse.ArgumentParser(description="COMPUTEX.md fork-census radar")
    ap.add_argument("--window", default="365daysAgo", help="GA lookback (default 365daysAgo)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        hosts = ga_run(["hostName"], ["screenPageViews", "activeUsers"],
                       args.window, "today", order_by="screenPageViews")
        titles = ga_run(["pageTitle"], ["screenPageViews", "activeUsers"],
                        args.window, "today", order_by="screenPageViews")
    except Exception as e:  # fail-loud: never write an empty registry on GA failure
        print(f"❌ GA query failed: {e}", file=sys.stderr)
        return 1

    reg = load_registry()
    forks = reg["forks"]
    new_hits = []

    def zero(win):
        return {"window": win, "views": 0, "users": 0}

    # reset GA-derived counters so a fork's multiple fingerprints ACCUMULATE
    # (e.g. su-chiao-hui's 3 hosts sum; 嘉義's 2 title brands sum) rather than
    # the last-processed fingerprint overwriting the rest.
    for e in forks:
        e["ga"] = zero(args.window)
        e["title_ga"] = zero(args.window)

    # ── pass 1: hostName forks ────────────────────────────────────────────────
    host_buckets = {"ours": [0, 0], "dev": [0, 0], "proxy": [0, 0]}
    for row in hosts:
        host = row["dims"][0]
        views, users = int(row["mets"][0]), int(row["mets"][1])
        kind = classify_host(host)
        if kind != "fork":
            host_buckets[kind][0] += views
            host_buckets[kind][1] += users
            continue
        e = find_entry(forks, host=host)
        if e is None:
            e = dict(STUB); e["id"] = host; e["label"] = host
            e["hostnames"] = [host]; e["deployment"] = host
            e["ga"] = zero(args.window); e["title_ga"] = zero(args.window)
            forks.append(e); new_hits.append(host)
        elif host not in e["hostnames"]:
            e["hostnames"].append(host)
        e["ga"]["views"] += views
        e["ga"]["users"] += users
        e["last_seen"] = ym()
        e.setdefault("first_seen", ym())

    # ── pass 2: pageTitle forks (run on localhost/intranet → no public host) ──
    brand_views = {}
    for row in titles:
        b = title_brand(row["dims"][0])
        if not b:
            continue
        v, u = int(row["mets"][0]), int(row["mets"][1])
        agg = brand_views.setdefault(b, [0, 0])
        agg[0] += v; agg[1] = max(agg[1], u)
    for brand, (v, u) in sorted(brand_views.items(), key=lambda x: -x[1][0]):
        e = find_entry(forks, brand=brand)
        if e is None:
            e = dict(STUB); e["id"] = brand; e["label"] = brand
            e["title_brands"] = [brand]
            e["deployment"] = "not public (localhost/intranet — title leak only)"
            e["ga"] = zero(args.window); e["title_ga"] = zero(args.window)
            forks.append(e); new_hits.append(f"title:{brand}")
        elif brand not in e["title_brands"]:
            e["title_brands"].append(brand)
        e["title_ga"]["views"] += v
        e["title_ga"]["users"] = max(e["title_ga"]["users"], u)
        e["last_seen"] = ym()
        e.setdefault("first_seen", ym())

    reg["_meta"]["last_census"] = today()
    reg["_meta"]["self_traffic"] = {"views": host_buckets["ours"][0], "users": host_buckets["ours"][1]}
    reg["_meta"]["dev_noise"] = {"views": host_buckets["dev"][0], "users": host_buckets["dev"][1]}
    reg["forks"] = sorted(forks, key=lambda e: -(e.get("ga", {}).get("views", 0)
                                                 + e.get("title_ga", {}).get("views", 0)))

    if args.json:
        print(json.dumps(reg, ensure_ascii=False, indent=2))
        return 0

    # ── human summary ─────────────────────────────────────────────────────────
    print(f"🛰️  fork-census {today()}  (window={args.window})")
    print(f"   self (computex.md): {host_buckets['ours'][0]:,} views / {host_buckets['ours'][1]:,} users")
    print(f"   dev noise (localhost etc): {host_buckets['dev'][0]:,} views")
    print(f"   forks in registry: {len(forks)}")
    if new_hits:
        print(f"   🆕 NEW sightings: {', '.join(new_hits)}")
    fork_only = [e for e in reg["forks"] if e.get("ga", {}).get("views") or e.get("title_ga", {}).get("views")]
    print("   ── living offspring ──")
    for e in fork_only:
        gv = e.get("ga", {}).get("views", 0)
        tv = e.get("title_ga", {}).get("views", 0)
        seen = f"{e.get('first_seen','?')}→{e.get('last_seen','?')}"
        print(f"   • {e['label']:<28} {e.get('type','?'):<14} "
              f"host={gv:>4}v title={tv:>4}v  {seen}  {e.get('topic','')[:40]}")

    if not args.dry_run:
        REGISTRY.parent.mkdir(parents=True, exist_ok=True)
        REGISTRY.write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"   ✍️  written → {REGISTRY.relative_to(HERE.parent.parent)}")
    else:
        print("   (dry-run — not written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
