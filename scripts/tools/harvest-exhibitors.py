#!/usr/bin/env python3
"""harvest-exhibitors.py — 從 COMPUTEX 官方參展廠商名錄抽取事實層資料。

為什麼這支存在（而不是叫 LLM 寫廠商頁）
    這個檔案庫的全部價值在於「每一項宣稱都帶得走出處」。廠商頁的事實層若由
    語言模型憑訓練語料生成，產出的正好是這個站存在的意義所要消滅的東西：
    看起來合理、查不到出處、而且會被下一個模型吃進去。

    所以事實層一律機械抽取，來源是官方參展廠商頁，每一筆都記下 source_url 與
    抓取日期。抽不到的欄位留白，NEVER 從往年或第三方彙整站推測。

官方頁提供的欄位（截至 2026-07-29 實測）
    公司名 / 場館 + 展區 / 攤位號 / 官方網站 / 品牌名 / **歷年參展紀錄**
    最後一項是這個專案的脊椎：一家公司跨年度的參展軌跡，官方自己就有，
    而且沒有任何地方把它整理成機器可讀的形式。

用法
    # 列出展區與家數
    python3 scripts/tools/harvest-exhibitors.py --list-areas

    # 抓某個展區的全部展商（事實層 JSON）
    python3 scripts/tools/harvest-exhibitors.py \\
        --area "AI Computing & System Integration Solution" \\
        --out data/exhibitors/ai-computing-sis.json

禮貌
    預設每次請求間隔 1.5 秒，帶可識別的 User-Agent 與聯絡方式。我們正要去跟
    TAITRA 談合作，不會去打他們的站。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

BASE = "https://www.computextaipei.com.tw"
UA = (
    "COMPUTEX.md-research/0.1 "
    "(+https://github.com/hansai-art/computex-md; hans@groupg.org)"
)
DEFAULT_DELAY = 1.5

_RE_LIST_ENTRY = re.compile(
    r'/en/exhibitor/([0-9A-Za-z]{6,})/info\.html[^>]*>(.*?)</a>', re.S
)
_RE_AREA_LINK = re.compile(r'/en/exhibitor/show-area-data/([^/"\']+)/list\.html')
_RE_COMPANY_BLOCK = re.compile(
    r'<div class="company_info".*?</div>\s*</div>', re.S
)
_RE_NAME = re.compile(r"<h2>(.*?)</h2>", re.S)
_RE_LOCATION = re.compile(
    r'<i class="i_location"></i>(.*?)<a[^>]*>(.*?)</a>', re.S
)
_RE_WEBSITE = re.compile(
    r'<i class="i_global"></i><a href="([^"]+)"', re.S
)
_RE_TAG = re.compile(r"<[^>]+>")


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", _RE_TAG.sub("", s)).strip()


#: 抓下來的原始 HTML 快取。解析規則改版時重跑不必再打人家的站一次。
CACHE_DIR = Path(".cache/exhibitor-html")


def fetch(url: str, delay: float = DEFAULT_DELAY, cache: bool = True) -> str:
    key = CACHE_DIR / (
        re.sub(r"[^A-Za-z0-9]+", "_", url.replace(BASE, "")).strip("_") + ".html"
    )
    if cache and key.exists():
        return key.read_text(encoding="utf-8")

    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        html = r.read().decode("utf-8", "replace")
    if cache:
        key.parent.mkdir(parents=True, exist_ok=True)
        key.write_text(html, encoding="utf-8")
    time.sleep(delay)
    return html


def list_areas() -> list[str]:
    html = fetch(f"{BASE}/en/exhibitor/show-area-data/index.html")
    areas = {urllib.parse.unquote(a) for a in _RE_AREA_LINK.findall(html)}
    return sorted(a for a in areas if a != "index.html")


def area_members(area: str, delay: float) -> list[dict[str, str]]:
    """展區成員清單。`pageSize` 讓 26 頁變 1 頁，也少打站 26 次。"""
    url = (
        f"{BASE}/en/exhibitor/show-area-data/"
        f"{urllib.parse.quote(area)}/list.html?pageSize=500&currentPage=1"
    )
    html = fetch(url, delay)
    out: dict[str, dict[str, str]] = {}
    for eid, raw in _RE_LIST_ENTRY.findall(html):
        name = _clean(raw)
        if not name or len(name) > 150:
            continue
        out.setdefault(eid, {"exhibitor_id": eid, "name": name})
    return list(out.values())


_RE_TIMELINE = re.compile(r'<ul class="timeline">(.*?)</ul>\s*</section>', re.S)
_RE_YEAR_BLOCK = re.compile(
    r'<span class="year"[^>]*>\s*(\d{4})\s*</span>(.*?)(?=<span class="year"|\Z)',
    re.S,
)
_RE_SHOW_ROW = re.compile(
    r'<span class="date-range">\s*(\d{4}/\d{2}/\d{2})\s*-\s*(\d{4}/\d{2}/\d{2})\s*'
    r"</span>\s*<p>(.*?)</p>",
    re.S,
)


def _parse_exhibiting_record(html: str) -> list[dict[str, str]]:
    """歷年參展紀錄。

    官方的結構是巢狀的：外層一個 `<li>` 是一個**年份**，內層 `<ul>` 才是那一年
    參加過的**每一場展**。同一年可以有好幾場（外貿協會辦的展不只 COMPUTEX）。

    2026-07-29 修掉的兩個抽取錯誤（都會讓事實層失真，而且不會有人發現）：

    1. **一年只留一列**。舊版把整段壓平成純文字後逐列比對，遇到同一年第二列就
       `continue`。AAEON 2022 那年參加了「TAIWAN EXPO in Malaysia」與
       「Taiwan Expo in India」兩場，我們只留了馬來西亞那場，印度那場憑空消失。

    2. **展名被截斷**。舊版展名用 `([A-Za-z ]+)` 抓，只吃得下英文字母與空格，
       於是含 `'`、`&`、數字的展名全部在第一個非字母字元斷掉：
       `Taiwan Int'l Fastener Show` → 「Taiwan Int」、
       `Taipei Aerospace & Defense Technology Exhibition` → 「Taipei Aerospace」。
       站上因此出現一批看起來像展名、其實是半截字串的資料。

    改成照官方的 DOM 結構抽（年份 span + 該年的每一列 date-range/`<p>`），
    展名整段照收不做字元過濾。

    完全相同的重複列（年份、起訖日、展名四項全等）收成一列：官方頁面自己會重複
    （AAEON 的 2026 COMPUTEX TAIPEI 就印了兩次），照抄過來只會讓我們的表格看起來
    像抄錯。這是唯一做的正規化，其餘一律照抄 —— 包括屆別年份與展期年份對不上的
    那些列（疫情延期留下的），那些在廠商頁會另外註明。
    """
    m = _RE_TIMELINE.search(html)
    if not m:
        return []

    out: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for year, block in _RE_YEAR_BLOCK.findall(m.group(1)):
        for start, end, show_raw in _RE_SHOW_ROW.findall(block):
            show = _clean(show_raw)
            if not show:
                continue
            key = (year, start, end, show)
            if key in seen:
                continue
            seen.add(key)
            out.append(
                {
                    "edition_year": year,
                    "start_date": start.replace("/", "-"),
                    "end_date": end.replace("/", "-"),
                    "show": show,
                }
            )
    return out


def _parse_brands(html: str) -> list[str]:
    """品牌名。官方結構是 `<h3>Brand Name</h3><p>A,B</p>`。

    NEVER 放寬成「Brand Name 之後到下一個 section」：Brand Name 後面緊接的是
    `<h3>Description</h3>` 那段廠商自撰行銷文案，抓寬一格就會把「world's first」
    「industry's first」當成事實欄位寫進表格（2026-07-29 實際踩過）。
    """
    m = re.search(r"<h3>\s*Brand Name\s*</h3>\s*<p>(.*?)</p>", html, re.S)
    if not m:
        return []
    raw = _clean(m.group(1))
    return [b.strip() for b in raw.split(",") if b.strip()][:10]


def _parse_tags(html: str) -> list[dict[str, str]]:
    """官方展品分類標籤（`<div class="tag_group">`）。

    這是官方自己的機器可讀分類碼（OPT00347 = AI 之類），比任何第三方標籤都硬。
    """
    m = re.search(r'<div class="tag_group">(.*?)</div>', html, re.S)
    if not m:
        return []
    out = []
    for code, label in re.findall(
        r"searchExhTag\('([^']+)'\)[^>]*>(.*?)</a>", m.group(1), re.S
    ):
        text = _clean(label)
        if text:
            out.append({"code": code, "label": text})
    return out


def exhibitor_detail(eid: str, delay: float) -> dict[str, Any]:
    url = f"{BASE}/en/exhibitor/{eid}/info.html"
    html = fetch(url, delay)

    block_m = _RE_COMPANY_BLOCK.search(html)
    block = block_m.group(0) if block_m else html

    name_m = _RE_NAME.search(block)
    loc_m = _RE_LOCATION.search(block)
    web_m = _RE_WEBSITE.search(block)

    venue_area = _clean(loc_m.group(1)) if loc_m else ""
    booth = _clean(loc_m.group(2)) if loc_m else ""

    # 「Taipei Nangang Exhibition Center, Hall 1 (TaiNEX 1) AI Computing & Tech」
    venue, show_area = venue_area, ""
    tail = re.search(r"\(TaiNEX \d\)\s*(.*)$|\(TWTC[^)]*\)\s*(.*)$", venue_area)
    if tail:
        show_area = (tail.group(1) or tail.group(2) or "").strip()
        venue = venue_area[: tail.start()].strip() + venue_area[
            tail.start() : tail.start() + (tail.end(1) or tail.end(2) or 0) * 0
        ]
        venue = venue_area.replace(show_area, "").strip()

    return {
        "exhibitor_id": eid,
        "name": _clean(name_m.group(1)) if name_m else "",
        "venue": venue,
        "show_area": show_area,
        "booth": booth,
        "official_url": web_m.group(1).strip() if web_m else "",
        "brands": _parse_brands(html),
        "official_tags": _parse_tags(html),
        "exhibiting_record": _parse_exhibiting_record(html),
        "source_url": url,
        "source_type": "official",
        "last_checked_at": date.today().isoformat(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list-areas", action="store_true")
    ap.add_argument("--area", help="展區名稱（用 --list-areas 查）")
    ap.add_argument("--out", help="輸出 JSON 路徑")
    ap.add_argument("--limit", type=int, default=0, help="只抓前 N 家（試跑用）")
    ap.add_argument("--delay", type=float, default=DEFAULT_DELAY)
    args = ap.parse_args()

    if args.list_areas:
        for a in list_areas():
            print(a)
        return 0

    if not args.area or not args.out:
        ap.error("需要 --area 與 --out（或用 --list-areas）")

    members = area_members(args.area, args.delay)
    if args.limit:
        members = members[: args.limit]
    print(f"展區「{args.area}」：{len(members)} 家", file=sys.stderr)

    records = []
    for i, m in enumerate(members, 1):
        try:
            rec = exhibitor_detail(m["exhibitor_id"], args.delay)
        except Exception as e:  # noqa: BLE001 — 單一家失敗不該中斷整批
            print(f"  [{i}/{len(members)}] {m['name']} 失敗：{e}", file=sys.stderr)
            continue
        if not rec["name"]:
            rec["name"] = m["name"]
        rec["harvested_from_area"] = args.area
        records.append(rec)
        print(f"  [{i}/{len(members)}] {rec['name']} {rec['booth']}", file=sys.stderr)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "_generated": date.today().isoformat(),
                "_source": "COMPUTEX official exhibitor directory",
                "_area": args.area,
                "count": len(records),
                "exhibitors": records,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"寫入 {out}（{len(records)} 家）", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
