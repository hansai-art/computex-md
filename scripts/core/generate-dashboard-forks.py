#!/usr/bin/env python3
"""generate-dashboard-forks.py — registry.json → public dashboard-forks.json

把子代名冊（reports/fork-census/registry.json，由 fork-census.py 維護）投影成公開
dashboard 資料。

公開安全鐵律（§自主權邊界 對外輸出）：
  - 只公開「有公開 GitHub repo + 公開部署」的子代具名（Russia.md / lagunabeach.md /
    嘉義國本學堂 / HongKong.md 這類自己已經公開存在的）
  - 私有/內部/未證實的（Micron 內部 KB / 政治人物 gated wiki / 查無 repo 的 Malaysia）
    只進**總數**，不具名、不公開推測 —— 尊重它們的隱私，也不把 INFERRED 當事實公開
  - 完整含推測的名冊留在 reports/fork-census/registry.json（internal）

來源：2026-06-25 fork-census 接 dashboard（哲宇「連接到 dna/routine/pipeline + dashboard 常態 section」directive）。
"""
import json
import pathlib

SRC = pathlib.Path("reports/fork-census/registry.json")
OUT = pathlib.Path("public/api/dashboard-forks.json")


def is_public(f):
    """有真實 GitHub repo path（含 '/' 且非『查無』）才算可公開具名。"""
    gh = f.get("github", "") or ""
    return "/" in gh and "查無" not in gh


def credit_tier(f):
    c = str(f.get("credits_upstream", "") or "")
    if c.startswith("explicit") or c.startswith("yes"):
        return "yes"
    if "weak" in c or "leftover" in c or "殘字" in c:
        return "weak"
    if "inherited" in c or "vanilla" in c or "繼承" in c:
        return "inherited"
    return "unknown"


def project(f):
    gh = f.get("github", "") or ""
    site = next((h for h in f.get("hostnames", []) if "." in h and "github.io" not in h), None)
    if not site and f.get("hostnames"):
        site = f["hostnames"][0]
    views = (f.get("ga", {}).get("views", 0) or 0) + (f.get("title_ga", {}).get("views", 0) or 0)
    cog = (f.get("cognitive_layer", "") or "").split("—")[0].split("(")[0].strip()
    return {
        "label": f["label"],
        "type": f.get("type", "").split("(")[0].strip(),
        "topic": f.get("topic", ""),
        "language": f.get("language", ""),
        "github": f"https://github.com/{gh}" if gh else "",
        "site": f"https://{site}" if site else "",
        "networkFork": f.get("network_fork"),
        "credits": credit_tier(f),
        "cognitiveLayer": cog[:28],
        "health": f.get("health", ""),
        "firstSeen": f.get("first_seen", ""),
        "views365d": views,
    }


def main():
    reg = json.loads(SRC.read_text(encoding="utf-8"))
    forks = [f for f in reg["forks"] if f["id"] != "(ephemeral-experiments)"]
    public = [f for f in forks if is_public(f)]
    private = [f for f in forks if not is_public(f)]

    species = sorted({f.get("type", "").split("(")[0].split("/")[0].strip()
                      for f in forks if f.get("type")})

    out = {
        "lastUpdated": reg["_meta"].get("last_census"),
        "totalDetected": len(forks),
        "publicConfirmed": len(public),
        "privateOrUnconfirmed": len(private),
        "active": sum(1 for f in forks if f.get("health") in ("active", "semi-active")),
        "speciesTypes": species,
        "forks": sorted([project(f) for f in public], key=lambda x: -x["views365d"]),
        "privateNote": (f"另偵測到 {len(private)} 個未公開/未證實部署"
                        "（內部 KB / 私有 / gated），尊重隱私不具名"),
        "method": "GA radar：fork 繼承未改的 measurement ID，pageview 漏進母體 property → "
                  "靠 hostName + 繼承的頁面標題偵測野外子代",
        "registrySSOT": "reports/fork-census/registry.json (internal, 含推測)",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✅ dashboard-forks.json: {len(public)} public 具名 + {len(private)} private 計數 "
          f"(total {len(forks)} forks, {out['active']} active)")


if __name__ == "__main__":
    main()
