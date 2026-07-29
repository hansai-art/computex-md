#!/usr/bin/env python3
"""generate-organism.py：把語料算成「生命體」的細胞資料。

這支產生 /organism 那一頁要用的 src/data/organism.json。

## 為什麼這一頁存在

本站的核心概念不是「一個資料收集網站」，是**一個會長大的數位生命體**：
每一次有人補進一項可查證的事實，它就長大一點。/organism 就是它此刻的體檢表。

繼承自母體時，這個位置放的是 /graph：一張 12 個台灣主題分類的力導向圖
（歷史 / 地理 / 文化 / 美食 …），跟本站沒有任何關係。母體作者自己也否定過
那個東西，`OrganismPreview.astro` 的註解原文：「12-category force-directed
graph is a database visualization」。所以這一頁不是把 /graph 換皮，是換掉。

## 一顆細胞 = 一家廠商，每個視覺變數都對應一個真實欄位

    位置   = 真實攤位座標（館別 → 走道字母 → 攤位號）
    大小   = COMPUTEX 屆數（它在這個展會活了幾屆）
    亮度   = 生命力分數（下面的十項機械計分）
    顏色   = 館別（TaiNEX 1 / 2）

沒有一個是裝飾用的隨機值。這條是硬規則：**這一頁上任何會動、會亮、會排
位置的東西，都必須追得回語料裡的某一個欄位**。做不到就不要放。

## 生命力分數（十項，各 10 分，公開演算法，任何人可重算）

事實層（官方名錄查得到的，60 分）
    1  官方名錄連結（exhibitor_id + 出處 URL）
    2  官網連結
    3  攤位號
    4  展區
    5  場館
    6  參展歷史（屆數）

策展層（要人寫、要查證的，40 分）
    7  產業位置（這家在產業裡做什麼）
    8  跨年度變化（今年跟去年比）
    9  產品與技術
   10  人工複核（lastHumanReview）

2026-07-29 首跑的實況：事實層幾乎滿分，策展層 **全站 0 分**。所以整個生命體
會是半亮的。這是對的，不要去修：它就是還沒被餵養的樣子，而那正是這一頁要
講的事。任何讓分數看起來比較好看的加權，都是在對讀者說謊。

## 輸出

    src/data/organism.json

跑法：`python3 scripts/tools/generate-organism.py`（build 的 prebuild 會跑）。
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VENDOR_DIR = ROOT / "knowledge" / "Vendors"
OUT = ROOT / "src" / "data" / "organism.json"

# 生命力十項的公開定義。key 會原樣輸出到 JSON，頁面直接讀來畫圖例，
# 不在頁面那邊再寫一份（寫兩份就會有一天對不上）。
CRITERIA = [
    ("official_listing", "官方名錄連結", "Official listing link", "fact"),
    ("official_url", "官網連結", "Company website", "fact"),
    ("booth", "攤位號", "Booth number", "fact"),
    ("show_area", "展區", "Show area", "fact"),
    ("venue", "場館", "Venue", "fact"),
    ("history", "參展歷史", "Exhibiting history", "fact"),
    ("position", "產業位置", "Position in the industry", "curation"),
    ("year_over_year", "跨年度變化", "Year-over-year change", "curation"),
    ("products", "產品與技術", "Products and technology", "curation"),
    ("human_review", "人工複核", "Human review", "curation"),
]


@dataclass
class Cell:
    slug: str
    name: str
    hall: int  # 1 | 2（TaiNEX 1 / 2）
    aisle: str  # 攤位號的字母前綴，例如 J1310 的 J
    booth: str
    booth_num: int  # 攤位號的數字部分，用來排走道內的位置
    area: str
    editions: int  # COMPUTEX 屆數；0 = 官方名錄沒給
    first_year: int
    last_year: int
    vitality: int  # 0-100
    have: list[str]  # 已達成的 criteria key
    missing: list[str]  # 還缺的 criteria key（= 可以餵什麼）
    last_verified: str


def read_frontmatter(text: str) -> str:
    parts = text.split("---", 2)
    return parts[1] if len(parts) >= 3 else ""


def field(fm: str, key: str) -> str:
    m = re.search(rf"^\s*{re.escape(key)}:\s*'([^']*)'", fm, re.M)
    return m.group(1) if m else ""


def parse_booth(booth: str) -> tuple[str, int]:
    """`J1310` → ('J', 1310)。抓不到就回 ('', 0)，呼叫端自己決定怎麼辦。"""
    m = re.match(r"^\s*([A-Za-z]*)\s*(\d+)", booth)
    if not m:
        return "", 0
    return m.group(1).upper(), int(m.group(2))


def parse_years(text: str) -> tuple[int, int, int]:
    """從描述句抓 (起, 迄, 屆數)。抓不到回 (0, 0, 0)。

    語料裡的句型有兩種，都由 generate-vendor-pages.py 產生：
      「…參展年份涵蓋 2012 至 2026，共 7 屆…」
      「…官方名錄只記載 2026 這一屆…」
    """
    m = re.search(r"涵蓋 (\d{4}) 至 (\d{4})[^，]*，共 (\d+) 屆", text)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    m = re.search(r"只記載 (\d{4}) 這一屆", text)
    if m:
        return int(m.group(1)), int(m.group(1)), 1
    return 0, 0, 0


def evaluate(text: str, fm: str) -> tuple[list[str], list[str]]:
    """回傳 (達成的 criteria key, 缺的 criteria key)。

    策展層四項現在必然全缺，因為語料裡每一頁的策展層都寫著「目前留白」。
    這裡照樣逐項檢查而不是寫死 0，因為之後一旦有人真的補了，這支不用改。
    """
    body = text.split("---", 2)[-1]
    have: list[str] = []

    if field(fm, "exhibitor_id") and "https://www.computextaipei.com.tw" in text:
        have.append("official_listing")
    if field(fm, "official_url"):
        have.append("official_url")
    if field(fm, "booth"):
        have.append("booth")
    if field(fm, "show_area"):
        have.append("show_area")
    if "展覽館" in body:
        have.append("venue")
    if parse_years(text)[2] > 0:
        have.append("history")

    # 策展層：那一段有沒有被寫過。留白的頁面會有「策展層…目前留白」這句，
    # 由 generate-vendor-pages.py 產生；有人補寫時會連那句一起換掉。
    curated = "策展層" in body and "留白" not in body
    if curated:
        # 這四項現在無法逐項機械分辨（策展層是自由散文）。有人真的寫了策展層
        # 之後再細分；在那之前一次給三項，寧可低估不要高估。
        have += ["position", "year_over_year", "products"]
    if re.search(r"^lastHumanReview:\s*true", fm, re.M):
        have.append("human_review")

    keys = [k for k, *_ in CRITERIA]
    return have, [k for k in keys if k not in have]


def build_cells() -> list[Cell]:
    cells: list[Cell] = []
    for f in sorted(VENDOR_DIR.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        fm = read_frontmatter(text)

        title = field(fm, "title") or f.stem
        name = title.split("：")[0].strip()

        booth = field(fm, "booth")
        aisle, booth_num = parse_booth(booth)
        hall = 2 if "TaiNEX 2" in text or "展覽館 2 館" in text else 1
        first_year, last_year, editions = parse_years(text)
        have, missing = evaluate(text, fm)

        cells.append(
            Cell(
                slug=f.stem,
                name=name,
                hall=hall,
                aisle=aisle,
                booth=booth,
                booth_num=booth_num,
                area=field(fm, "show_area"),
                editions=editions,
                first_year=first_year,
                last_year=last_year,
                vitality=len(have) * 10,
                have=have,
                missing=missing,
                last_verified=(
                    re.search(r"^lastVerified:\s*(\S+)", fm, re.M).group(1)
                    if re.search(r"^lastVerified:\s*(\S+)", fm, re.M)
                    else ""
                ),
            )
        )
    return cells


def edits_last_7_days() -> int:
    """近 7 天動到 knowledge/ 的 commit 數。驅動生命體的變形速度。"""
    try:
        out = subprocess.run(
            [
                "git",
                "log",
                "--since=7 days ago",
                "--pretty=%H",
                "--",
                "knowledge",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        ).stdout
    except Exception:
        return 0
    return len([x for x in out.splitlines() if x.strip()])


def shape_signals(cells: list[Cell], vitality: int) -> dict:
    """六條「指標 → 形狀」的輸入值（2026-07-28 定案，見專案記憶）。

        條目數      → 體積
        反向連結數  → 瓣數
        AI 抓取次數 → 心跳
        Booth Score → 線亮度
        七日編輯數  → 變形速度
        語言數      → 殘影層數

    其中兩條現在**沒有資料源**：反向連結要外部 backlink 資料，AI 抓取要
    Cloudflare 的爬蟲統計，兩邊都還沒接。

    這種情況本站只有一種處置：`live: false` + `value: null`，頁面照實
    標「未接」，形狀用一個寫在這裡、看得到的預設值。NEVER 塞一個看起來
    合理的假數字進去 —— 這一頁講的就是「每個視覺變數都追得回一個真實
    欄位」，塞假數字等於當場推翻它自己。
    """
    langs = sorted(
        {
            p.name
            for p in (ROOT / "knowledge").iterdir()
            if p.is_dir() and p.name in {"en", "ja", "ko", "es", "fr"}
        }
    )
    return {
        "entries": {
            "key": "entries",
            "zh": "條目數",
            "en": "Entries",
            "drives_zh": "體積",
            "drives_en": "volume",
            "value": len(cells),
            "live": True,
            "source_zh": "knowledge/Vendors/*.md 檔數",
            "source_en": "file count in knowledge/Vendors",
        },
        "backlinks": {
            "key": "backlinks",
            "zh": "反向連結數",
            "en": "Backlinks",
            "drives_zh": "瓣數",
            "drives_en": "lobe count",
            "value": None,
            "fallback": 5,
            "live": False,
            "source_zh": "尚未接：需要外部反向連結資料源",
            "source_en": "not wired yet: needs an external backlink source",
        },
        "ai_fetches": {
            "key": "ai_fetches",
            "zh": "AI 抓取次數",
            "en": "AI crawler fetches",
            "drives_zh": "心跳",
            "drives_en": "pulse rate",
            "value": None,
            "fallback": 0,
            "live": False,
            "source_zh": "尚未接：需要 Cloudflare 的逐爬蟲請求數",
            "source_en": "not wired yet: needs Cloudflare per-crawler request counts",
        },
        "booth_score": {
            "key": "booth_score",
            "zh": "Booth Score",
            "en": "Booth Score",
            "drives_zh": "線亮度",
            "drives_en": "wire brightness",
            "value": vitality,
            "live": True,
            "source_zh": "本頁下方十項機械計分的全站平均",
            "source_en": "site-wide mean of the ten mechanical checks below",
        },
        "edits_7d": {
            "key": "edits_7d",
            "zh": "七日編輯數",
            "en": "Edits (7 days)",
            "drives_zh": "變形速度",
            "drives_en": "morph speed",
            "value": edits_last_7_days(),
            "live": True,
            "source_zh": "git log --since=7.days -- knowledge",
            "source_en": "git log --since=7.days -- knowledge",
        },
        "languages": {
            "key": "languages",
            "zh": "語言數",
            "en": "Languages",
            "drives_zh": "殘影層數",
            "drives_en": "afterimage layers",
            "value": len(langs) + 1,  # +1 = zh-TW（正本在 knowledge/ 根目錄）
            "live": True,
            "source_zh": "knowledge/ 底下的語言目錄數 + 正本語言",
            "source_en": "language directories under knowledge/ plus the source language",
        },
    }


def heartbeat() -> list[dict]:
    """近 90 天每日 commit 數，也就是生命體的心跳。

    直接讀 git，不經任何中間快取：心跳要是真的，不能是別人算好的數字。
    在沒有 .git 的環境（例如某些 CI 的 shallow 產物）回空陣列，
    頁面那邊會據此隱藏心跳區塊，而不是畫一條假的線。
    """
    try:
        out = subprocess.run(
            ["git", "log", "--since=90 days ago", "--date=short", "--pretty=%ad"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        ).stdout
    except Exception:
        return []
    counts: dict[str, int] = {}
    for line in out.splitlines():
        d = line.strip()
        if d:
            counts[d] = counts.get(d, 0) + 1
    return [{"date": d, "commits": c} for d, c in sorted(counts.items())]


def main() -> None:
    cells = build_cells()
    if not cells:
        # 母體那邊最常見的失敗是「產出 0 筆，但印綠色成功訊息」。
        # 這裡明確擋下來：0 顆細胞的生命體是壞掉，不是空。
        raise SystemExit(
            f"❌ [organism] 在 {VENDOR_DIR} 掃到 0 個廠商檔，不寫出空的 organism.json。\n"
            f"   先確認 knowledge/Vendors/ 有內容（或 generate-vendor-pages.py 有跑過）。"
        )

    total_criteria = len(cells) * len(CRITERIA)
    achieved = sum(len(c.have) for c in cells)
    beats = heartbeat()

    payload = {
        "_generated_by": "scripts/tools/generate-organism.py",
        "_note": (
            "每一個視覺變數都對應語料裡的一個真實欄位；沒有裝飾用的隨機值。"
            "生命力偏低是實況不是 bug：策展層目前全站留白。"
        ),
        "criteria": [
            {"key": k, "zh": zh, "en": en, "layer": layer}
            for k, zh, en, layer in CRITERIA
        ],
        "summary": {
            "cells": len(cells),
            "vitality": round(achieved / total_criteria * 100),
            "facts_filled": achieved,
            "facts_possible": total_criteria,
            "halls": sorted({c.hall for c in cells}),
            "areas": sorted({c.area for c in cells if c.area}),
            "editions_max": max((c.editions for c in cells), default=0),
            "with_history": sum(1 for c in cells if c.editions > 0),
            "curated": sum(1 for c in cells if "position" in c.have),
        },
        "shape": shape_signals(cells, round(achieved / total_criteria * 100)),
        "heartbeat": beats,
        "cells": [asdict(c) for c in cells],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )

    s = payload["summary"]
    print(
        f"✅ [organism] {s['cells']} 顆細胞 → {OUT.relative_to(ROOT)}\n"
        f"   整體生命力 {s['vitality']}%"
        f"（{s['facts_filled']}/{s['facts_possible']} 項）"
        f" · 有參展歷史 {s['with_history']}"
        f" · 有策展層 {s['curated']}"
        f" · 心跳 {len(beats)} 天有 commit"
    )


if __name__ == "__main__":
    main()
