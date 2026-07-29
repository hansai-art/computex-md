#!/usr/bin/env python3
"""generate-vendor-pages.py — 把官方展商事實層產成 knowledge/Vendors/*.md。

設計立場（重要，不要改掉）
    這支**只寫事實層**。每一格都來自 `harvest-exhibitors.py` 抓下來的官方參展廠商頁，
    附 source_url 與查證日期。策展層（供應鏈位置、跟去年比變了什麼、跟誰競爭）
    **刻意留白**，因為我們現在沒有可查證的來源可以寫它。

    留白不是偷懶，是這個檔案庫的賣點：官方沒公布的、我們查不到的，就是空的。
    補空格的誘惑正是展會資訊在網路上失真的主要原因：「往年是這樣所以今年
    應該也是」被寫成肯定句，然後被搜尋引擎與模型一起吃進去。

    留白處放「認領這一頁」的入口，那本來就是拉廠商進來共編的鉤子。

用法
    python3 scripts/tools/generate-vendor-pages.py data/exhibitors/*.json
    python3 scripts/tools/generate-vendor-pages.py --dry-run data/exhibitors/x.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any

OUT_DIR = Path("knowledge/Vendors")

#: 展區英文 → 中文（官方沒有提供中文展區名，這是本站的譯法，標明是我們譯的）
AREA_ZH = {
    "AI Computing & System Integration Solution": "AI 運算與系統整合方案",
    "AI Computing & Tech": "AI 運算與技術",
    "AI Service Technology": "AI 服務技術",
    "Components & Advanced Power Tech": "零組件與先進電源技術",
    "Advanced Communication & Networking": "先進通訊與網路",
}

#: 場館英文 → 中文
VENUE_ZH = [
    ("Taipei Nangang Exhibition Center, Hall 1 (TaiNEX 1)", "台北南港展覽館 1 館（TaiNEX 1）"),
    ("Taipei Nangang Exhibition Center, Hall 2 (TaiNEX 2)", "台北南港展覽館 2 館（TaiNEX 2）"),
    ("Taipei World Trade Center", "台北世界貿易中心"),
]

_CORP_SUFFIX = re.compile(
    r"[,\s]*(co\.?,?\s*ltd\.?|corporation|corp\.?|inc\.?|company|limited|ltd\.?|"
    r"pte\.?|technologies?|technology)\s*$",
    re.I,
)


def slugify(name: str) -> str:
    """公司名 → lowercase-hyphen slug（對齊 slug-format gate）。

    保留公司主體名，砍掉 Co., Ltd. / Inc. 這類後綴：它們對辨識沒有貢獻，
    但會讓網址長一倍。要反覆砍，因為後綴會疊（「Pte Ltd」「Co., Ltd.」），
    砍一次只會留下半截。砍到空字串時退回完整名稱。
    """
    base = name.strip()
    for _ in range(4):
        stripped = _CORP_SUFFIX.sub("", base).strip()
        if stripped == base or not stripped:
            break
        base = stripped
    base = base or name
    base = unicodedata.normalize("NFKD", base)
    base = base.encode("ascii", "ignore").decode("ascii")
    base = re.sub(r"[^A-Za-z0-9]+", "-", base).strip("-").lower()
    base = re.sub(r"-+", "-", base)
    return base or re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def zh_venue(venue: str) -> str:
    for en, zh in VENUE_ZH:
        if en in venue:
            return zh
    return venue


def zh_area(area: str) -> str:
    zh = AREA_ZH.get(area)
    return f"{zh}（{area}）" if zh else area


#: 全形標點。它們的字身本來就含左右留白，後面再補半形空格會看起來像斷開。
_FULLWIDTH_TAIL = "）」』】》〉、，。：；？！"


def cjk_join(prefix: str, value: str) -> str:
    """中文前綴接一個可能以西文開頭的值，中間補一個空格。

    「展區為AI 運算與技術」讀起來是黏的，86 頁的 description 與概覽段各出現一次。

    兩個不補的情況：
      - 值本身以中文開頭（「零組件與先進電源技術」）—— 補空格反而多一個洞
      - 前綴結尾是全形標點（「⋯⋯（TaiNEX 1）」接攤位號）—— 全形字身自帶留白
    """
    head_is_latin = value[:1].isascii() and value[:1].isalnum()
    tail_is_fullwidth = prefix[-1:] in _FULLWIDTH_TAIL
    return (
        f"{prefix} {value}" if head_is_latin and not tail_is_fullwidth else f"{prefix}{value}"
    )


def is_computex(show: str) -> bool:
    """這一列是不是 COMPUTEX 本身。

    官方的 `Exhibiting Record` 收的是這家公司參加過的**所有外貿協會展會**：
    TAITRONICS、TAIPEI AMPA、TIMTOS、台灣形象展（馬來西亞 / 印尼 / 美國 / 印度
    / 越南 / 菲律賓 / 歐洲 / 日本）、台北國際自行車展、醫療展、食品展⋯⋯
    86 家共 634 列裡，467 列是 COMPUTEX，其餘 167 列不是。

    2026-07-29 抓到：本檔原本把整包 record 當成 COMPUTEX 屆數在算，於是每一頁的
    「官方名錄記載它參展過 N 屆」都可能多算，`/explore` 的「在 COMPUTEX 待最久的
    廠商」榜也排錯人。表照列全部（那是官方名錄的原貌），但**凡是掛 COMPUTEX 名字
    的計數，就只能數 COMPUTEX**。
    """
    return show.strip().upper().startswith("COMPUTEX")


def _yaml_escape(s: str) -> str:
    return s.replace("'", "''")


#: 本站已存在、可安全連過去的展會頁（link-target gate 會驗檔案真的在）
EDITION_PAGE = ("/editions/computex-2027/", "COMPUTEX 2027：目前已公布的事實")


def render(rec: dict[str, Any], siblings: list[tuple[str, str]]) -> str:
    name = rec["name"]
    checked = rec["last_checked_at"]
    src = rec["source_url"]
    area = rec.get("show_area") or ""
    venue = rec.get("venue") or ""
    booth = rec.get("booth") or ""
    url = rec.get("official_url") or ""
    record = rec.get("exhibiting_record") or []
    cx_rows = [r for r in record if is_computex(r["show"])]
    other_rows = [r for r in record if not is_computex(r["show"])]

    years = sorted({r["edition_year"] for r in cx_rows}, reverse=True)
    latest = years[0] if years else ""
    span = f"{years[-1]} 至 {years[0]}" if len(years) > 1 else (latest or "")

    title = f"{name}：COMPUTEX {latest} 參展資料" if latest else f"{name}：COMPUTEX 參展資料"

    desc_bits = [f"{name} 在 COMPUTEX {latest} 的官方參展資料"]
    if area:
        desc_bits.append(cjk_join("展區為", zh_area(area)))
    if venue:
        desc_bits.append(cjk_join("場館為", zh_venue(venue)))
    if booth:
        desc_bits.append(f"攤位號 {booth}")
    if len(years) > 1:
        desc_bits.append(f"官方名錄記載的 COMPUTEX 參展年份涵蓋 {span}，共 {len(years)} 屆")
    if other_rows:
        desc_bits.append(
            f"官方名錄另記載 {len(other_rows)} 筆其他外貿協會展會紀錄，本頁一併列出但不計入 COMPUTEX 屆數"
        )
    desc_bits.append(
        "本頁事實層每一項均附官方出處連結與查證日期，由程式從官方名錄機械抽取，"
        "不經語言模型改寫；官方名錄未提供的欄位一律留白，"
        "不從公司官網文案、新聞稿、往年慣例或第三方彙整站推測"
    )
    description = "，".join(desc_bits) + "。"

    tags = ["COMPUTEX", f"COMPUTEX {latest}" if latest else "COMPUTEX", "參展廠商"]
    if area:
        tags.append(AREA_ZH.get(area, area))
    tags.append("AI 硬體")
    tags = list(dict.fromkeys(t for t in tags if t))

    # flow array 一行，不是 block sequence。理由是冪等：pre-commit 的 prettier
    # 會把 block list 收成 flow array，產生器若輸出 block list，每重跑一次就是
    # 86 檔的純格式 diff，資料真的變了反而看不出來。產生器要輸出「格式化後的
    # 樣子」，而不是輸出後等別人改。同理，frontmatter 收尾與 H1 之間不留空行。
    fm_tags = "[" + ", ".join(f"'{_yaml_escape(t)}'" for t in tags) + "]"

    # ── 事實表 ────────────────────────────────────────────────────────────
    rows = [("公司名稱（官方名錄登錄）", name)]
    if area:
        rows.append(("展區", zh_area(area)))
    if venue:
        rows.append(("場館", zh_venue(venue)))
    if booth:
        rows.append(("攤位號", booth))
    if url:
        rows.append(("官方網站", f"<{url}>"))
    brands = rec.get("brands") or []
    if brands:
        rows.append(("品牌名", "、".join(brands)))
    otags = rec.get("official_tags") or []
    if otags:
        # 官方自己的分類碼。附上代碼，別人要重查得回官方名錄才有辦法。
        rows.append(
            ("官方展品分類標籤", "、".join(f"{t['label']}（{t['code']}）" for t in otags))
        )

    fact_rows = "\n".join(
        f"| {k} | {v} | [官方參展廠商頁]({src}) | {checked} |" for k, v in rows
    )

    # ── 歷年參展紀錄 ──────────────────────────────────────────────────────
    if record:
        rec_rows = "\n".join(
            f"| {r['edition_year']} | {r['start_date']} 至 {r['end_date']} | {r['show']} |"
            for r in record
        )
        # 官方名錄本身就有「屆別年份 ≠ 展期年份」的列（2020 屆的展期寫成 2021），
        # 那是疫情延期留下的紀錄。照抄不修，但要講一句，否則讀者會以為是我們抄錯。
        offset_rows = [
            r for r in record if r["start_date"][:4] != r["edition_year"]
        ]
        note = (
            "\n\n注意：其中 "
            + "、".join(
                cjk_join(f"{r['edition_year']} 年的", r["show"]) for r in offset_rows
            )
            + "，展期年份與屆別年份不一致，這是官方名錄原本就這樣記載，本頁照抄不修改。"
            if offset_rows
            else ""
        )
        # 表列全部（官方名錄的原貌），但一句話先講清楚哪些是 COMPUTEX、哪些不是。
        # 這一段以前只有一個「共 N 屆」，N 是整包紀錄的列數 —— 讀者會直接把它讀成
        # 「來過 COMPUTEX N 次」，而那是錯的。
        if other_rows:
            lead = (
                f"官方參展廠商頁列出 {len(record)} 筆參展紀錄，其中 {len(cx_rows)} 筆是 COMPUTEX"
                + (f"（{len(years)} 屆，涵蓋 {span}）" if len(years) > 1 else "")
                + f"，另外 {len(other_rows)} 筆是外貿協會主辦的其他展會。"
                "下表照官方名錄原樣列出全部，展會名稱那一欄可以分辨。\n\n"
            )
        else:
            lead = (
                f"官方參展廠商頁列出的參展紀錄全部是 COMPUTEX，共 {len(years)} 屆"
                + (f"，涵蓋 {span}。\n\n" if len(years) > 1 else "。\n\n")
            )
        record_block = (
            "## 歷年參展紀錄\n\n"
            + lead
            + "| 年份 | 展期 | 展會 |\n| --- | --- | --- |\n"
            + rec_rows
            + f"\n\n出處：[官方參展廠商頁]({src})，查證日期 {checked}。{note}\n"
        )
    else:
        record_block = (
            "## 歷年參展紀錄\n\n"
            f"官方參展廠商頁在查證當日（{checked}）沒有列出歷年參展紀錄，本頁留白。\n"
        )

    # ── 30 秒概覽 ─────────────────────────────────────────────────────────
    # 這段是給 AI 引擎的答案單元：一句話回答「這家在哪、展什麼、來過幾次」。
    ov = [f"{name} 是 COMPUTEX {latest} 的參展廠商"]
    if booth:
        ov.append(cjk_join(f"攤位在{zh_venue(venue) if venue else '會場'}", booth))
    if area:
        ov.append(cjk_join("歸屬展區為", zh_area(area)))
    ov.append(
        f"官方名錄記載它參展過 {len(years)} 屆 COMPUTEX（{span}）" if len(years) > 1
        else (f"官方名錄目前只記載 {latest} 這一屆 COMPUTEX" if latest else "官方名錄未列出 COMPUTEX 參展紀錄")
    )
    overview = "，".join(ov) + "。"

    # ── 延伸閱讀 ──────────────────────────────────────────────────────────
    further = [f"- [{EDITION_PAGE[1]}]({EDITION_PAGE[0]})"]
    if siblings:
        further += [f"- [{n}](/vendors/{s}/)" for n, s in siblings]
    further_block = "\n".join(further)
    sib_note = (
        f"同一展區（{zh_area(area)}）的其他參展廠商："
        if siblings and area
        else "本站其他相關頁面："
    )

    body = f"""# {title}

> **30 秒概覽**：{overview}本頁只寫官方名錄查得到的事實，每一項附出處連結與查證日期；官方沒公布的欄位留白，不推測。

這一頁分兩層：下面的事實層全部由程式從 COMPUTEX 官方名錄抽取，逐項可回查；
策展層（產業位置、跨年度變化）目前留白，等有可查證的來源才寫。

## 官方名錄記載的事實

| 項目 | 內容 | 出處 | 查證日期 |
| --- | --- | --- | --- |
{fact_rows}

{record_block}
## 官方名錄未提供的

以下項目不在官方參展廠商名錄的欄位裡，因此本頁留白，不從公司官網文案、新聞稿或
第三方彙整站推測：

- 公司中文正式名稱與統一編號
- 主要產品線與技術規格
- 在 AI 硬體供應鏈中的位置與客戶關係
- 員工數、營收、產能等經營數字
- 本屆展出的具體產品

補這些格子需要可查證的第一手來源。歡迎附出處開 Pull Request，我們不收沒有出處的內容。

## 這頁是怎麼來的

本頁的事實層由 `scripts/tools/harvest-exhibitors.py` 從官方參展廠商頁機械抽取，
不經語言模型改寫，因此不會出現「看起來合理但查不到出處」的句子。

策展層（這家公司在供應鏈的位置、跟去年比變了什麼、跟誰競爭）目前是空的。
那部分需要編輯判斷與可查證的來源，我們寧可讓它空著，也不用模型補。

## 認領這一頁

如果你是 {name} 的人：這一頁的**事實層**你可以直接送 Pull Request 修改，
條件是每一項宣稱附上可查證的來源連結。策展層由中立編輯撰寫，你可以在 PR 提出異議。

行銷文案不會被合併。「業界領先」「全球首創」這類沒有出處的絕對宣稱由 CI 自動擋下
（`marketing-speak` 檢查）。原因很實際：AI 引擎不引用行銷文案，那對你的曝光沒有幫助，
帶得出第三方數據的說法才會留下來。

## 延伸閱讀

{sib_note}

{further_block}

---

> **本站定位**：COMPUTEX.md 是獨立的開放資料專案，不是 COMPUTEX 或中華民國對外貿易發展協會（TAITRA）的官方網站。
> COMPUTEX.md is an independent open-data project. It is not the official website of COMPUTEX or TAITRA.
"""

    # frontmatter 兩個欄位值得解釋，但解釋要留在這裡，NEVER 寫成 YAML 註解：
    # 那會把「給產生器維護者看的話」複製 86 份進公開的內容檔。
    #
    #   lastHumanReview: false  機器抽的事實層，還沒有人逐頁核對過。prose-health
    #       讀它，所以這 86 頁會一直在報表上叫。那是對的，不要為了讓報表安靜改 true。
    #   status: 'published'     這些頁真的在線上被服務。站內目前沒有任何地方拿
    #       status 過濾（schema 有 enum、消費端沒有），寫 'draft' 只是讓 frontmatter 說謊。
    frontmatter = f"""---
title: '{_yaml_escape(title)}'
description: '{_yaml_escape(description)}'
date: {date.today().isoformat()}
category: 'Vendors'
tags: {fm_tags}
subcategory: '{_yaml_escape(zh_area(area) if area else "參展廠商")}'
author: 'COMPUTEX.md Editors'
featured: false
lastVerified: {checked}
lastHumanReview: false
status: 'published'
difficulty: 'beginner'
readingTime: 2
lastUpdated: {date.today().isoformat()}
vendor:
  exhibitor_id: '{rec["exhibitor_id"]}'
  official_url: '{_yaml_escape(url)}'
  booth: '{_yaml_escape(booth)}'
  show_area: '{_yaml_escape(area)}'
  source_type: '{rec.get("source_type", "official")}'
sources:
  - '{src}'
---
"""
    return frontmatter + body


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("inputs", nargs="+", help="harvest-exhibitors.py 產出的 JSON")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--no-format",
        action="store_true",
        help="跳過 prettier（沒有 node 的環境用；輸出會跟 commit 後不一致）",
    )
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 先把全部讀進來再產檔：延伸閱讀要指到同展區的其他廠商，那需要看得到全表。
    seen: dict[str, str] = {}
    records: list[tuple[str, dict[str, Any]]] = []
    for path in args.inputs:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for rec in data["exhibitors"]:
            slug = slugify(rec["name"])
            if slug in seen:
                print(
                    f"  跳過重複 slug {slug}（{rec['name']} vs {seen[slug]}）",
                    file=sys.stderr,
                )
                continue
            seen[slug] = rec["name"]
            records.append((slug, rec))

    by_area: dict[str, list[tuple[str, str]]] = {}
    for slug, rec in records:
        by_area.setdefault(rec.get("show_area") or "", []).append((rec["name"], slug))

    written = 0
    for slug, rec in records:
        # 取同展區鄰居。取代碼順序的前 5 個，不隨機：同一份輸入要產出同一份檔案，
        # 否則每次重跑都是一包無意義的 diff。
        peers = [x for x in by_area.get(rec.get("show_area") or "", []) if x[1] != slug]
        out = OUT_DIR / f"{slug}.md"
        if args.dry_run:
            print(f"  would write {out}（同展區鄰居 {len(peers[:5])}）")
            continue
        out.write_text(render(rec, peers[:5]), encoding="utf-8")
        written += 1

    print(
        f"{'would write' if args.dry_run else '寫入'} {written or len(records)} 個廠商頁",
        file=sys.stderr,
    )

    if written and not args.no_format:
        # 產完就跑 prettier，讓「產生器的輸出」就是「commit 進去的樣子」。
        #
        # 不這樣做的話：pre-commit 的 prettier 會重排 markdown 表格欄寬，於是
        # 重跑一次產生器就是 86 檔的純格式 diff，資料真的變了反而看不出來。
        # 在 Python 這邊手工複刻 prettier 的表格對齊是打不贏的仗（欄寬算的是
        # 顯示寬度，CJK 全形要算 2），所以直接叫它本人。
        try:
            subprocess.run(
                ["npx", "prettier", "--write", "--log-level", "warn", str(OUT_DIR)],
                check=True,
            )
        except (OSError, subprocess.CalledProcessError) as e:
            print(
                f"  prettier 沒跑成（{e}）。檔案已寫入，但格式會跟 commit 後不一致，"
                f"下次重跑會出現純格式 diff。手動補跑："
                f"npx prettier --write {OUT_DIR}",
                file=sys.stderr,
            )
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
