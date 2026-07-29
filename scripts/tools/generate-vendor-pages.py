#!/usr/bin/env python3
"""generate-vendor-pages.py — 把官方展商事實層產成廠商頁（zh-TW 與 en）。

設計立場（重要，不要改掉）
    這支**只寫事實層**。每一格都來自 `harvest-exhibitors.py` 抓下來的官方參展廠商頁，
    附 source_url 與查證日期。策展層（供應鏈位置、跟去年比變了什麼、跟誰競爭）
    **刻意留白**，因為我們現在沒有可查證的來源可以寫它。

    留白不是偷懶，是這個檔案庫的賣點：官方沒公布的、我們查不到的，就是空的。
    補空格的誘惑正是展會資訊在網路上失真的主要原因：「往年是這樣所以今年
    應該也是」被寫成肯定句，然後被搜尋引擎與模型一起吃進去。

    留白處放「認領這一頁」的入口，那本來就是拉廠商進來共編的鉤子。

雙語（2026-07-29 加）
    英文版**不是中文版的翻譯**，是同一份事實的另一次渲染。理由不是省事，是準確：
    官方名錄的原始欄位（公司名、展區、場館、展會名）本來就是英文，中文頁那幾格
    才是我們譯的。把英文頁寫成「中文頁的翻譯」會多繞一手，繞的過程只會掉精度。

    所以這支拆成 `Facts`（語言中立的事實）+ `render_zh` / `render_en` 兩支渲染器。
    兩支各自用自己語言的句法寫，不共用句型模板 —— 共用模板產出的是翻譯腔，而這個
    站的英文頁要給英語圈的模型引用，翻譯腔會直接反映在引用品質上。

    英文檔的 frontmatter 帶 `translatedFrom`，那是全站語言配對的 SSOT
    （`sync-translations-json.py` → `_translations.json` → lang-switch-map）。

用法
    python3 scripts/tools/generate-vendor-pages.py data/exhibitors/*.json
    python3 scripts/tools/generate-vendor-pages.py --lang en data/exhibitors/*.json
    python3 scripts/tools/generate-vendor-pages.py --lang all data/exhibitors/*.json
    python3 scripts/tools/generate-vendor-pages.py --dry-run data/exhibitors/x.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

#: lang → 輸出目錄。zh-TW 是預設語言，不帶語言碼子目錄（對齊 knowledge/ 既有結構）。
OUT_DIRS = {
    "zh-TW": Path("knowledge/Vendors"),
    "en": Path("knowledge/en/Vendors"),
}

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


#: 本站已存在、可安全連過去的展會頁（link-target gate 會驗檔案真的在）。
#: 路徑不帶語言前綴，由 render 依語言補 `/en`。
EDITION_SLUG = "editions/computex-2027"
EDITION_TITLE_ZH = "COMPUTEX 2027：目前已公布的事實"
EDITION_TITLE_EN = "COMPUTEX 2027: what has been announced so far"


@dataclass(frozen=True)
class Facts:
    """語言中立的事實層。兩支渲染器都只從這裡取值，不各自重算。

    重算是雙語頁最容易長出來的裂縫：中文頁說 7 屆、英文頁說 8 屆，兩邊各自
    「正確」，因為它們數的是不同的東西。所以計數只在這裡做一次。
    """

    slug: str
    name: str
    checked: str
    src: str
    area: str
    venue: str
    booth: str
    url: str
    brands: list[str]
    official_tags: list[dict[str, str]]
    exhibitor_id: str
    source_type: str
    record: list[dict[str, str]]
    cx_rows: list[dict[str, str]]
    other_rows: list[dict[str, str]]
    years: list[str]
    offset_rows: list[dict[str, str]]

    @property
    def latest(self) -> str:
        return self.years[0] if self.years else ""

    @property
    def editions(self) -> int:
        return len(self.years)


def build_facts(slug: str, rec: dict[str, Any]) -> Facts:
    record = rec.get("exhibiting_record") or []
    cx_rows = [r for r in record if is_computex(r["show"])]
    return Facts(
        slug=slug,
        name=rec["name"],
        checked=rec["last_checked_at"],
        src=rec["source_url"],
        area=rec.get("show_area") or "",
        venue=rec.get("venue") or "",
        booth=rec.get("booth") or "",
        url=rec.get("official_url") or "",
        brands=rec.get("brands") or [],
        official_tags=rec.get("official_tags") or [],
        exhibitor_id=rec["exhibitor_id"],
        source_type=rec.get("source_type", "official"),
        record=record,
        cx_rows=cx_rows,
        other_rows=[r for r in record if not is_computex(r["show"])],
        years=sorted({r["edition_year"] for r in cx_rows}, reverse=True),
        # 官方名錄本身就有「屆別年份 ≠ 展期年份」的列（2020 屆的展期寫成 2021），
        # 那是疫情延期留下的紀錄。照抄不修，但兩種語言都要講一句，否則讀者會
        # 以為是我們抄錯。
        offset_rows=[r for r in record if r["start_date"][:4] != r["edition_year"]],
    )


def _fm_common(f: Facts, title: str, description: str, tags_yaml: str, subcategory: str) -> str:
    """兩語共用的 frontmatter 欄位。

    兩個欄位值得解釋，但解釋要留在這裡，NEVER 寫成 YAML 註解：那會把
    「給產生器維護者看的話」複製 172 份進公開的內容檔。

      lastHumanReview: false  機器抽的事實層，還沒有人逐頁核對過。prose-health
          讀它，所以這些頁會一直在報表上叫。那是對的，不要為了讓報表安靜改 true。
      status: 'published'     這些頁真的在線上被服務。站內目前沒有任何地方拿
          status 過濾（schema 有 enum、消費端沒有），寫 'draft' 只是讓 frontmatter 說謊。
    """
    today = date.today().isoformat()
    return f"""title: '{_yaml_escape(title)}'
description: '{_yaml_escape(description)}'
date: {today}
category: 'Vendors'
tags: {tags_yaml}
subcategory: '{_yaml_escape(subcategory)}'
author: 'COMPUTEX.md Editors'
featured: false
lastVerified: {f.checked}
lastHumanReview: false
status: 'published'
difficulty: 'beginner'
readingTime: 2
lastUpdated: {today}
vendor:
  exhibitor_id: '{f.exhibitor_id}'
  official_url: '{_yaml_escape(f.url)}'
  booth: '{_yaml_escape(f.booth)}'
  show_area: '{_yaml_escape(f.area)}'
  source_type: '{f.source_type}'
"""


# ═══════════════════════════════════════════════════════════════════════════
# 中文渲染
# ═══════════════════════════════════════════════════════════════════════════


def render_zh(f: Facts, siblings: list[tuple[str, str]]) -> str:
    latest, years = f.latest, f.years
    span = f"{years[-1]} 至 {years[0]}" if len(years) > 1 else (latest or "")

    title = f"{f.name}：COMPUTEX {latest} 參展資料" if latest else f"{f.name}：COMPUTEX 參展資料"

    desc_bits = [f"{f.name} 在 COMPUTEX {latest} 的官方參展資料"]
    if f.area:
        desc_bits.append(cjk_join("展區為", zh_area(f.area)))
    if f.venue:
        desc_bits.append(cjk_join("場館為", zh_venue(f.venue)))
    if f.booth:
        desc_bits.append(f"攤位號 {f.booth}")
    if len(years) > 1:
        desc_bits.append(f"官方名錄記載的 COMPUTEX 參展年份涵蓋 {span}，共 {len(years)} 屆")
    if f.other_rows:
        desc_bits.append(
            f"官方名錄另記載 {len(f.other_rows)} 筆其他外貿協會展會紀錄，本頁一併列出但不計入 COMPUTEX 屆數"
        )
    desc_bits.append(
        "本頁事實層每一項均附官方出處連結與查證日期，由程式從官方名錄機械抽取，"
        "不經語言模型改寫；官方名錄未提供的欄位一律留白，"
        "不從公司官網文案、新聞稿、往年慣例或第三方彙整站推測"
    )
    description = "，".join(desc_bits) + "。"

    tags = ["COMPUTEX", f"COMPUTEX {latest}" if latest else "COMPUTEX", "參展廠商"]
    if f.area:
        tags.append(AREA_ZH.get(f.area, f.area))
    tags.append("AI 硬體")
    tags = list(dict.fromkeys(t for t in tags if t))

    # flow array 一行，不是 block sequence。理由是冪等：pre-commit 的 prettier
    # 會把 block list 收成 flow array，產生器若輸出 block list，每重跑一次就是
    # 一包純格式 diff，資料真的變了反而看不出來。產生器要輸出「格式化後的
    # 樣子」，而不是輸出後等別人改。同理，frontmatter 收尾與 H1 之間不留空行。
    fm_tags = "[" + ", ".join(f"'{_yaml_escape(t)}'" for t in tags) + "]"

    # ── 事實表 ────────────────────────────────────────────────────────────
    rows = [("公司名稱（官方名錄登錄）", f.name)]
    if f.area:
        rows.append(("展區", zh_area(f.area)))
    if f.venue:
        rows.append(("場館", zh_venue(f.venue)))
    if f.booth:
        rows.append(("攤位號", f.booth))
    if f.url:
        rows.append(("官方網站", f"<{f.url}>"))
    if f.brands:
        rows.append(("品牌名", "、".join(f.brands)))
    if f.official_tags:
        # 官方自己的分類碼。附上代碼，別人要重查得回官方名錄才有辦法。
        rows.append(
            ("官方展品分類標籤", "、".join(f"{t['label']}（{t['code']}）" for t in f.official_tags))
        )

    fact_rows = "\n".join(
        f"| {k} | {v} | [官方參展廠商頁]({f.src}) | {f.checked} |" for k, v in rows
    )

    # ── 歷年參展紀錄 ──────────────────────────────────────────────────────
    if f.record:
        rec_rows = "\n".join(
            f"| {r['edition_year']} | {r['start_date']} 至 {r['end_date']} | {r['show']} |"
            for r in f.record
        )
        note = (
            "\n\n注意：其中 "
            + "、".join(
                cjk_join(f"{r['edition_year']} 年的", r["show"]) for r in f.offset_rows
            )
            + "，展期年份與屆別年份不一致，這是官方名錄原本就這樣記載，本頁照抄不修改。"
            if f.offset_rows
            else ""
        )
        # 表列全部（官方名錄的原貌），但一句話先講清楚哪些是 COMPUTEX、哪些不是。
        # 這一段以前只有一個「共 N 屆」，N 是整包紀錄的列數 —— 讀者會直接把它讀成
        # 「來過 COMPUTEX N 次」，而那是錯的。
        if f.other_rows:
            lead = (
                f"官方參展廠商頁列出 {len(f.record)} 筆參展紀錄，其中 {len(f.cx_rows)} 筆是 COMPUTEX"
                + (f"（{len(years)} 屆，涵蓋 {span}）" if len(years) > 1 else "")
                + f"，另外 {len(f.other_rows)} 筆是外貿協會主辦的其他展會。"
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
            + f"\n\n出處：[官方參展廠商頁]({f.src})，查證日期 {f.checked}。{note}\n"
        )
    else:
        record_block = (
            "## 歷年參展紀錄\n\n"
            f"官方參展廠商頁在查證當日（{f.checked}）沒有列出歷年參展紀錄，本頁留白。\n"
        )

    # ── 30 秒概覽 ─────────────────────────────────────────────────────────
    # 這段是給 AI 引擎的答案單元：一句話回答「這家在哪、展什麼、來過幾次」。
    ov = [f"{f.name} 是 COMPUTEX {latest} 的參展廠商"]
    if f.booth:
        ov.append(cjk_join(f"攤位在{zh_venue(f.venue) if f.venue else '會場'}", f.booth))
    if f.area:
        ov.append(cjk_join("歸屬展區為", zh_area(f.area)))
    ov.append(
        f"官方名錄記載它參展過 {len(years)} 屆 COMPUTEX（{span}）" if len(years) > 1
        else (f"官方名錄目前只記載 {latest} 這一屆 COMPUTEX" if latest else "官方名錄未列出 COMPUTEX 參展紀錄")
    )
    overview = "，".join(ov) + "。"

    # ── 延伸閱讀 ──────────────────────────────────────────────────────────
    further = [f"- [{EDITION_TITLE_ZH}](/{EDITION_SLUG}/)"]
    further += [f"- [{n}](/vendors/{s}/)" for n, s in siblings]
    further_block = "\n".join(further)
    sib_note = (
        f"同一展區（{zh_area(f.area)}）的其他參展廠商："
        if siblings and f.area
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

如果你是 {f.name} 的人：這一頁的**事實層**你可以直接送 Pull Request 修改，
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

    frontmatter = (
        "---\n"
        + _fm_common(
            f, title, description, fm_tags, zh_area(f.area) if f.area else "參展廠商"
        )
        + f"sources:\n  - '{f.src}'\n---\n"
    )
    return frontmatter + body


# ═══════════════════════════════════════════════════════════════════════════
# 英文渲染
# ═══════════════════════════════════════════════════════════════════════════


def _en_count(n: int, singular: str, plural: str | None = None) -> str:
    return f"{n} {singular if n == 1 else (plural or singular + 's')}"


def render_en(f: Facts, siblings: list[tuple[str, str]]) -> str:
    """英文頁。事實跟中文頁同源，句子各寫各的。

    英文是官方名錄的原始語言，所以這一頁的每一格都是直接引用，沒有經過翻譯。
    這件事本身值得對讀者講一句，因為它決定了這一頁的可信度高於中文頁。
    """
    latest, years = f.latest, f.years
    span = f"{years[-1]} to {years[0]}" if len(years) > 1 else (latest or "")

    title = (
        f"{f.name}: COMPUTEX {latest} exhibitor record"
        if latest
        else f"{f.name}: COMPUTEX exhibitor record"
    )

    # description 是完整句子接完整句子，不是用逗號串成一長串。
    # 中文那邊靠頓號串接讀得動，英文串起來就是 comma splice，而這一段會原樣進
    # meta description 與 JSON-LD，是機器最常引用的一段。
    where = []
    if f.area:
        where.append(f"in the {f.area} show area")
    if f.venue:
        where.append(f"at {f.venue}")
    if f.booth:
        where.append(f"booth {f.booth}")
    sentences = [
        (
            f"The official COMPUTEX {latest} exhibitor listing for {f.name}"
            if latest
            else f"The official COMPUTEX exhibitor listing for {f.name}"
        )
        + (", " + ", ".join(where) if where else "")
        + "."
    ]
    if len(years) > 1:
        counted = (
            f"The official directory records COMPUTEX appearances from {span}, "
            f"{_en_count(len(years), 'edition')} in total"
        )
        if f.other_rows:
            counted += (
                f", plus {_en_count(len(f.other_rows), 'record')} from other TAITRA shows "
                "that this page reproduces but does not count toward the COMPUTEX total"
            )
        sentences.append(counted + ".")
    elif f.other_rows:
        sentences.append(
            f"The directory also lists {_en_count(len(f.other_rows), 'record')} from other "
            "TAITRA shows, reproduced here but not counted toward the COMPUTEX total."
        )
    sentences.append(
        "Every fact on this page carries a source link and a checked date, extracted "
        "mechanically from the official directory without passing through a language "
        "model. Fields the directory does not publish are left blank rather than inferred "
        "from company marketing pages, press releases, past practice or third-party "
        "aggregators."
    )
    description = " ".join(sentences)

    tags = ["COMPUTEX", f"COMPUTEX {latest}" if latest else "COMPUTEX", "exhibitor"]
    if f.area:
        tags.append(f.area)
    tags.append("AI hardware")
    tags = list(dict.fromkeys(t for t in tags if t))
    fm_tags = "[" + ", ".join(f"'{_yaml_escape(t)}'" for t in tags) + "]"

    # ── Facts table ──────────────────────────────────────────────────────
    rows = [("Company name as registered", f.name)]
    if f.area:
        rows.append(("Show area", f.area))
    if f.venue:
        rows.append(("Venue", f.venue))
    if f.booth:
        rows.append(("Booth", f.booth))
    if f.url:
        rows.append(("Official website", f"<{f.url}>"))
    if f.brands:
        rows.append(("Brands", ", ".join(f.brands)))
    if f.official_tags:
        rows.append(
            (
                "Official product categories",
                ", ".join(f"{t['label']} ({t['code']})" for t in f.official_tags),
            )
        )

    fact_rows = "\n".join(
        f"| {k} | {v} | [Official exhibitor page]({f.src}) | {f.checked} |" for k, v in rows
    )

    # ── Exhibiting record ────────────────────────────────────────────────
    if f.record:
        rec_rows = "\n".join(
            f"| {r['edition_year']} | {r['start_date']} to {r['end_date']} | {r['show']} |"
            for r in f.record
        )
        note = (
            "\n\nNote: for "
            + ", ".join(f"{r['show']} {r['edition_year']}" for r in f.offset_rows)
            + ", the run dates fall in a different calendar year than the edition year. "
            "That is how the official directory records it, and this page reproduces it "
            "unchanged."
            if f.offset_rows
            else ""
        )
        if f.other_rows:
            lead = (
                f"The official exhibitor page lists {_en_count(len(f.record), 'record')}: "
                f"{len(f.cx_rows)} for COMPUTEX"
                + (f" ({_en_count(len(years), 'edition')}, {span})" if len(years) > 1 else "")
                + f", and {len(f.other_rows)} for other trade shows organized by TAITRA. "
                "The table below reproduces all of them as the directory has them; the "
                "show column tells them apart.\n\n"
            )
        else:
            lead = (
                "Every record on the official exhibitor page is COMPUTEX, "
                f"{_en_count(len(years), 'edition')} in total"
                + (f", spanning {span}.\n\n" if len(years) > 1 else ".\n\n")
            )
        record_block = (
            "## Exhibiting record\n\n"
            + lead
            + "| Year | Run dates | Show |\n| --- | --- | --- |\n"
            + rec_rows
            + f"\n\nSource: [official exhibitor page]({f.src}), checked {f.checked}.{note}\n"
        )
    else:
        record_block = (
            "## Exhibiting record\n\n"
            f"On the date this page was checked ({f.checked}), the official exhibitor page "
            "listed no past editions. This section is left blank.\n"
        )

    # ── 30-second overview ───────────────────────────────────────────────
    ov = [
        f"{f.name} is an exhibitor at COMPUTEX {latest}"
        if latest
        else f"{f.name} is a COMPUTEX exhibitor"
    ]
    if f.booth:
        ov.append(f"at booth {f.booth}" + (f" in {f.venue}" if f.venue else ""))
    if f.area:
        ov.append(f"in the {f.area} show area")
    if len(years) > 1:
        ov.append(
            f"and the official directory records {_en_count(len(years), 'COMPUTEX edition')} "
            f"for it, spanning {span}"
        )
    elif latest:
        ov.append(f"and the official directory records only the {latest} edition for it")
    else:
        ov.append("and the official directory lists no past COMPUTEX editions for it")
    overview = ", ".join(ov) + "."

    # ── Further reading ──────────────────────────────────────────────────
    further = [f"- [{EDITION_TITLE_EN}](/en/{EDITION_SLUG}/)"]
    further += [f"- [{n}](/en/vendors/{s}/)" for n, s in siblings]
    further_block = "\n".join(further)
    sib_note = (
        f"Other exhibitors in the same show area ({f.area}):"
        if siblings and f.area
        else "Related pages on this site:"
    )

    body = f"""# {title}

> **30-second overview**: {overview} This page carries only what the official directory publishes, each item with a source link and a checked date. Fields the directory leaves empty are left empty here too.

This page has two layers. The fact layer below is extracted by a program from the
COMPUTEX official exhibitor directory and every row can be traced back to it. The
curation layer, meaning where this company sits in the supply chain and what changed
year over year, is deliberately blank until there is a citable source for it.

Note on language: the official directory publishes these fields in English, so every
value in the table below is quoted directly rather than translated.

## What the official directory records

| Field | Value | Source | Checked |
| --- | --- | --- | --- |
{fact_rows}

{record_block}
## What the official directory does not provide

The following are not fields in the official exhibitor directory, so this page leaves
them blank rather than inferring them from company marketing pages, press releases or
third-party aggregators:

- Registered Chinese company name and tax ID
- Product lines and technical specifications
- Position in the AI hardware supply chain, and customer relationships
- Headcount, revenue, production capacity
- The specific products shown at this edition

Filling these in requires citable primary sources. Pull requests are welcome if they
carry them. Content without sources is not merged.

## How this page was made

The fact layer is extracted by `scripts/tools/harvest-exhibitors.py` from the official
exhibitor page. No language model rewrites it, which is why you will not find sentences
here that read plausibly but cannot be traced to a source.

The curation layer is empty. That part needs editorial judgment and citable sources, and
we would rather leave it visibly blank than have a model fill it in.

## Claim this page

If you work at {f.name}: you can send a pull request against the **fact layer** of this
page directly, on one condition, that every claim carries a verifiable source link. The
curation layer is written by neutral editors, and you can raise an objection in the pull
request.

Marketing copy is not merged. Unsourced absolute claims like "industry leading" or
"world's first" are blocked automatically by CI (the `marketing-speak` check). The reason
is practical rather than editorial: AI engines do not quote marketing copy, so it does
nothing for your visibility. Statements backed by third-party numbers are what survive.

## Further reading

{sib_note}

{further_block}

---

> **About this site**: COMPUTEX.md is an independent open-data project. It is not the
> official website of COMPUTEX or the Taiwan External Trade Development Council (TAITRA).
"""

    zh_title = (
        f"{f.name}：COMPUTEX {latest} 參展資料" if latest else f"{f.name}：COMPUTEX 參展資料"
    )
    frontmatter = (
        "---\n"
        + _fm_common(f, title, description, fm_tags, f.area or "Exhibitor")
        + f"chineseTitle: '{_yaml_escape(zh_title)}'\n"
        + f"translatedFrom: 'Vendors/{f.slug}.md'\n"
        + "translationStatus: 'complete'\n"
        + f"sources:\n  - '{f.src}'\n---\n"
    )
    return frontmatter + body


RENDERERS = {"zh-TW": render_zh, "en": render_en}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("inputs", nargs="+", help="harvest-exhibitors.py 產出的 JSON")
    ap.add_argument(
        "--lang",
        default="all",
        choices=["zh-TW", "en", "all"],
        help="產哪一種語言的頁（預設 all：兩種都產）",
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--no-format",
        action="store_true",
        help="跳過 prettier（沒有 node 的環境用；輸出會跟 commit 後不一致）",
    )
    args = ap.parse_args()

    langs = list(OUT_DIRS) if args.lang == "all" else [args.lang]

    # 先把全部讀進來再產檔：延伸閱讀要指到同展區的其他廠商，那需要看得到全表。
    seen: dict[str, str] = {}
    records: list[Facts] = []
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
            records.append(build_facts(slug, rec))

    by_area: dict[str, list[tuple[str, str]]] = {}
    for f in records:
        by_area.setdefault(f.area, []).append((f.name, f.slug))

    touched: list[Path] = []
    for lang in langs:
        out_dir = OUT_DIRS[lang]
        render = RENDERERS[lang]
        if not args.dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)

        written = 0
        for f in records:
            # 取同展區鄰居。取代碼順序的前 5 個，不隨機：同一份輸入要產出同一份檔案，
            # 否則每次重跑都是一包無意義的 diff。
            peers = [x for x in by_area.get(f.area, []) if x[1] != f.slug][:5]
            out = out_dir / f"{f.slug}.md"
            if args.dry_run:
                print(f"  would write {out}（同展區鄰居 {len(peers)}）")
                continue
            out.write_text(render(f, peers), encoding="utf-8")
            written += 1

        print(
            f"{'would write' if args.dry_run else '寫入'} {written or len(records)} 個廠商頁"
            f"（{lang} → {out_dir}）",
            file=sys.stderr,
        )
        if written:
            touched.append(out_dir)

    if touched and not args.no_format:
        # 產完就跑 prettier，讓「產生器的輸出」就是「commit 進去的樣子」。
        #
        # 不這樣做的話：pre-commit 的 prettier 會重排 markdown 表格欄寬，於是
        # 重跑一次產生器就是一包純格式 diff，資料真的變了反而看不出來。
        # 在 Python 這邊手工複刻 prettier 的表格對齊是打不贏的仗（欄寬算的是
        # 顯示寬度，CJK 全形要算 2），所以直接叫它本人。
        try:
            subprocess.run(
                ["npx", "prettier", "--write", "--log-level", "warn", *map(str, touched)],
                check=True,
            )
        except (OSError, subprocess.CalledProcessError) as e:
            print(
                f"  prettier 沒跑成（{e}）。檔案已寫入，但格式會跟 commit 後不一致，"
                f"下次重跑會出現純格式 diff。手動補跑："
                f"npx prettier --write {' '.join(map(str, touched))}",
                file=sys.stderr,
            )
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
