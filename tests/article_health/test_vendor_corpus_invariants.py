"""廠商頁的不變條件，直接掃真實 corpus（zh-TW 與 en 兩份）。

為什麼掃輸出而不是測產生器：廠商頁的寫入口不只有 `generate-vendor-pages.py`。
「認領這一頁」的設計就是要讓廠商自己送 PR 改事實層，所以守門必須守在**檔案**
上，不是守在產生它的那支程式上。產生器改壞、或某個 PR 手改壞，這裡都要叫。

為什麼兩種語言都要掃（2026-07-29 加英文頁時補）：英文頁不是中文頁的翻譯，是同
一份事實的另一次渲染，兩支渲染器各寫各的句子。共用同一份 `Facts` 讓「兩邊數字
不一樣」在**當下**是結構上做不到的事，但這種保證會隨著有人手改單一語言的頁面而
消失 —— 而「事實層雙語一致」正是這個站的賣點本身。所以它必須是機器守的，不是
架構順便給的。

單語條件（兩種語言各自成立）
1. 事實表每一列都要有出處連結 + 查證日期 —— 這是這個檔案庫唯一的賣點，
   一列沒有出處，整頁的可信度就跟隨便一個彙整站一樣了。
2. 不准出現破折號（Hans 的全域寫作規則，改用冒號）。
3. 檔名 lowercase-hyphen（`slug-format` gate 的同一把尺，這裡再守一次是因為
   廠商 PR 可能用公司全名當檔名）。
4. 每頁都要有留白段 —— 留白是刻意的產品決策，不是還沒寫完。哪天有人為了讓頁面
   「看起來完整」把它刪掉，這裡要擋。
5. 頁面上的 COMPUTEX 屆數宣稱，要等於同一頁的表數得出來的屆數。

跨語言條件
6. 每一頁中文版都要有英文版，`translatedFrom` 指回存在的中文檔。
7. 同一家廠商的中英文頁，COMPUTEX 屆數必須一樣。
"""

import re
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

_RE_GOOD_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_RE_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_RE_LINK = re.compile(r"\[[^\]]+\]\(https?://[^)]+\)")

#: 中英文的表格列長得一樣（年份 | 展期 | 展會），所以共用。欄寬由 prettier 補，
#: 正規化交給 `\s*`。
_RE_TABLE_ROW = re.compile(r"^\|\s*(\d{4})\s*\|[^|]*\|\s*([^|]+?)\s*\|\s*$", re.M)


@dataclass(frozen=True)
class Corpus:
    """一種語言的廠商頁，以及它的段落標題與句型。

    句型清單只准變長，不准變短：抓不到的句型會被算成「這頁沒有宣稱」，測試就從
    守門變成放行 —— 這是這一類測試最容易失效的方式，而且失效時是靜悄悄的。
    """

    lang: str
    directory: Path
    fact_heading: str
    fact_table_header: str
    record_heading: str
    blank_heading: str
    #: 頁面上會出現屆數宣稱的句型（每一條抓一個數字）
    claim_patterns: tuple[re.Pattern[str], ...]
    #: 只有一屆時的句型（不帶數字，命中就等於宣稱 1 屆）
    single_pattern: re.Pattern[str]

    @property
    def files(self) -> list[Path]:
        return sorted(self.directory.glob("*.md")) if self.directory.exists() else []


ZH = Corpus(
    lang="zh-TW",
    directory=REPO_ROOT / "knowledge" / "Vendors",
    fact_heading="## 官方名錄記載的事實",
    fact_table_header="項目",
    record_heading="## 歷年參展紀錄",
    blank_heading="## 官方名錄未提供的",
    claim_patterns=(
        re.compile(r"(\d+)\s*屆\s*COMPUTEX"),  # 概覽段：參展過 7 屆 COMPUTEX
        re.compile(r"COMPUTEX 參展年份涵蓋[^，。]*，共\s*(\d+)\s*屆"),  # description
        re.compile(r"筆是 COMPUTEX（(\d+)\s*屆"),  # 歷年紀錄段導言（有其他展會時）
        re.compile(r"參展紀錄全部是 COMPUTEX，共\s*(\d+)\s*屆"),  # 同上（沒有其他展會時）
    ),
    single_pattern=re.compile(r"只記載\s*\d{4}\s*這一屆\s*COMPUTEX"),
)

EN = Corpus(
    lang="en",
    directory=REPO_ROOT / "knowledge" / "en" / "Vendors",
    fact_heading="## What the official directory records",
    fact_table_header="Field",
    record_heading="## Exhibiting record",
    blank_heading="## What the official directory does not provide",
    claim_patterns=(
        # 概覽段：records 7 COMPUTEX editions for it
        re.compile(r"(\d+)\s+COMPUTEX editions?"),
        # description：COMPUTEX appearances from 2012 to 2026, 7 editions in total
        re.compile(r"COMPUTEX appearances from[^.]*?,\s*(\d+)\s+editions? in total"),
        # 歷年紀錄段導言（有其他展會時）：7 for COMPUTEX (7 editions, 2012 to 2026)
        #   只抓括號裡的屆數。括號外那個是**列數**，跟屆數是兩回事（同一年可能
        #   有兩列 COMPUTEX 家族展會），拿它來比會製造假失敗。
        re.compile(r"for COMPUTEX \((\d+)\s+editions?"),
        # 同上（沒有其他展會時）：is COMPUTEX, 7 editions in total
        re.compile(r"is COMPUTEX,\s*(\d+)\s+editions? in total"),
    ),
    single_pattern=re.compile(r"only the \d{4} edition for it"),
)

CORPORA = (ZH, EN)

#: (corpus, path) 攤平成參數，讓失敗訊息直接指出是哪一語言的哪一頁。
ALL_PAGES = [(c, p) for c in CORPORA for p in c.files]
PAGE_IDS = [f"{c.lang}:{p.stem}" for c, p in ALL_PAGES]


@pytest.mark.parametrize("corpus", CORPORA, ids=lambda c: c.lang)
def test_there_are_vendor_pages_at_all(corpus: Corpus):
    """守住「掃了 0 個檔所以全部通過」這種假綠燈。"""
    assert len(corpus.files) >= 20, (
        f"{corpus.lang} 只找到 {len(corpus.files)} 個廠商頁（{corpus.directory}）"
    )


@pytest.mark.parametrize(("corpus", "path"), ALL_PAGES, ids=PAGE_IDS)
def test_every_fact_row_carries_a_source_and_a_check_date(corpus: Corpus, path: Path):
    text = path.read_text(encoding="utf-8")
    body = text.split("---", 2)[-1]

    section = re.search(rf"{re.escape(corpus.fact_heading)}\n(.*?)\n## ", body, re.S)
    assert section, f"缺「{corpus.fact_heading}」段"

    # 欄寬要正規化再比對：prettier 會把表格補成對齊的樣子（`| 項目      | 內容 …`、
    # 分隔列補成 `| ------ |`），所以任何靠 `"| 項目 |" in ln` 或 `startswith("| ---")`
    # 的過濾在格式化前後會得到不同答案。這支測試守的是內容，不能被排版左右。
    rows = []
    for ln in section.group(1).splitlines():
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if not ln.strip().startswith("|"):
            continue
        if cells[0] == corpus.fact_table_header:  # 表頭
            continue
        if all(set(c) <= {"-", ":"} and c for c in cells):  # 分隔列
            continue
        rows.append(ln)
    assert rows, "事實表是空的"

    for row in rows:
        assert _RE_LINK.search(row), f"這一列沒有出處連結：{row[:60]}"
        assert _RE_DATE.search(row), f"這一列沒有查證日期：{row[:60]}"


@pytest.mark.parametrize(("corpus", "path"), ALL_PAGES, ids=PAGE_IDS)
def test_no_em_dash(corpus: Corpus, path: Path):
    text = path.read_text(encoding="utf-8")
    assert "—" not in text, "破折號要改成冒號"


@pytest.mark.parametrize(("corpus", "path"), ALL_PAGES, ids=PAGE_IDS)
def test_filename_is_a_clean_slug(corpus: Corpus, path: Path):
    assert _RE_GOOD_SLUG.match(path.stem), (
        f"檔名 `{path.stem}` 會產生帶 %20 或大寫的網址"
    )


@pytest.mark.parametrize(("corpus", "path"), ALL_PAGES, ids=PAGE_IDS)
def test_the_blank_list_is_still_there(corpus: Corpus, path: Path):
    text = path.read_text(encoding="utf-8")
    assert corpus.blank_heading in text, (
        "留白段被刪了。留白是產品決策：官方沒公布的就是空的，"
        "補滿它需要可查證來源，不是需要看起來完整。"
    )


# ── 屆數宣稱 vs 同一頁的表 ───────────────────────────────────────────────
#
# 起因（2026-07-29）：官方的 `Exhibiting Record` 收的是這家公司參加過的**所有外貿
# 協會展會**（TAITRONICS、TAIPEI AMPA、TIMTOS、各國台灣形象展⋯⋯），86 家共 634 列
# 裡只有 467 列是 COMPUTEX。產生器原本把整包當成 COMPUTEX 屆數在算，於是每一頁的
# 「參展過 N 屆」都可能多算，`/explore` 的「在 COMPUTEX 待最久的廠商」榜也排錯人。
#
# 這條測試不需要外部資料：頁面上的宣稱（散文裡的 N）與證據（同一頁的表）本來就
# 該對得起來，直接互相驗證。這也正是這個站對讀者的承諾 —— 每一個數字都能在同一
# 頁被回推。


def _computex_editions_from_table(corpus: Corpus, text: str) -> int | None:
    """從歷年參展紀錄表數出不重複的 COMPUTEX 屆別年份。"""
    section = re.search(
        rf"{re.escape(corpus.record_heading)}\n(.*?)(?:\n## |\Z)", text, re.S
    )
    if not section:
        return None
    years = {
        y
        for y, show in _RE_TABLE_ROW.findall(section.group(1))
        if show.strip().upper().startswith("COMPUTEX")
    }
    return len(years)


def _claimed_editions(corpus: Corpus, text: str) -> set[int]:
    claims = {int(n) for rx in corpus.claim_patterns for n in rx.findall(text)}
    if corpus.single_pattern.search(text):
        claims.add(1)
    return claims


@pytest.mark.parametrize(("corpus", "path"), ALL_PAGES, ids=PAGE_IDS)
def test_computex_edition_count_matches_the_table_on_the_same_page(
    corpus: Corpus, path: Path
):
    text = path.read_text(encoding="utf-8")
    actual = _computex_editions_from_table(corpus, text)
    assert actual, "歷年參展紀錄表裡數不到任何 COMPUTEX 列"

    claims = _claimed_editions(corpus, text)
    assert claims, "頁面沒有任何 COMPUTEX 屆數宣稱（概覽段應該要有）"
    for claimed in claims:
        assert claimed == actual, (
            f"頁面宣稱 {claimed} 屆 COMPUTEX，但同一頁的表只數得出 {actual} 屆。"
            f"最常見的原因是把其他外貿協會展會（TAITRONICS / TAIPEI AMPA / "
            f"台灣形象展⋯⋯）一起算進 COMPUTEX 屆數。"
        )


@pytest.mark.parametrize(("corpus", "path"), ALL_PAGES, ids=PAGE_IDS)
def test_no_cjk_latin_collision(corpus: Corpus, path: Path):
    """中文字後面直接接西文字母，中間要有空格。

    「展區為AI 運算與技術」是產生器 f-string 拼出來的，一次就是 86 頁 ×2 處。
    只掃散文，不掃表格與 frontmatter：表格欄位（`| 展區 | AI Computing…`）本來就
    靠 `|` 分隔，YAML 值同理。

    英文頁也掃：它的 frontmatter 有 `chineseTitle`，正文理論上沒有中文，真的長出
    中文時多半是有人手動補了譯註，那一樣要遵守同一條排版規則。
    """
    text = path.read_text(encoding="utf-8")
    body = text.split("---", 2)[-1]
    bad = []
    for ln in body.splitlines():
        if ln.startswith("|") or ln.startswith("["):
            continue
        for m in re.finditer(r"[一-鿿][A-Za-z]", ln):
            bad.append(ln[max(0, m.start() - 12) : m.end() + 12])
    assert not bad, "中文與西文之間少一個空格：" + " / ".join(bad[:3])


# ── 跨語言：同一家廠商，兩份頁面，同一組事實 ─────────────────────────────

_RE_TRANSLATED_FROM = re.compile(r"^translatedFrom:\s*'([^']+)'", re.M)


@pytest.mark.parametrize("path", ZH.files, ids=lambda p: p.stem)
def test_every_vendor_has_an_english_page(path: Path):
    """中文有、英文沒有 = 英語圈的模型問到這家公司時，站上沒有東西可以被引用。

    這個站的整個論點就是「讓世界的 AI 回答台灣 AI 硬體時引用這裡」，缺英文頁
    等於在最重要的那個語言上缺席，而缺席是不會有人回報的。
    """
    en_page = EN.directory / path.name
    assert en_page.exists(), (
        f"{path.stem} 有中文頁但沒有英文頁。"
        f"補法：python3 scripts/tools/generate-vendor-pages.py --lang en data/exhibitors/*.json"
    )


@pytest.mark.parametrize("path", EN.files, ids=lambda p: p.stem)
def test_english_page_points_back_at_an_existing_chinese_page(path: Path):
    """`translatedFrom` 是全站語言配對的 SSOT（sync-translations-json.py 讀它）。

    指到不存在的檔案時，語言切換鈕會指向 404，而 lang-switch-map 產出時不會叫。
    """
    text = path.read_text(encoding="utf-8")
    m = _RE_TRANSLATED_FROM.search(text)
    assert m, "英文頁缺 translatedFrom，語言切換會配不到中文頁"
    target = REPO_ROOT / "knowledge" / m.group(1)
    assert target.exists(), f"translatedFrom 指向不存在的檔案：{m.group(1)}"


@pytest.mark.parametrize("path", EN.files, ids=lambda p: p.stem)
def test_both_languages_claim_the_same_edition_count(path: Path):
    """同一家廠商，中英文頁的 COMPUTEX 屆數必須一樣。

    兩邊各自跟自己頁上的表對得起來還不夠：兩份表可能都是舊的、或只有一邊被手動
    更新過。這條直接比兩種語言的宣稱，是雙語事實層唯一真正的守門。
    """
    zh_page = ZH.directory / path.name
    if not zh_page.exists():
        pytest.skip("沒有對應的中文頁，由 test_every_vendor_has_an_english_page 負責")

    en_claims = _claimed_editions(EN, path.read_text(encoding="utf-8"))
    zh_claims = _claimed_editions(ZH, zh_page.read_text(encoding="utf-8"))
    assert en_claims and zh_claims, (
        f"有一邊數不到屆數宣稱（en={en_claims or '無'}, zh={zh_claims or '無'}）"
    )
    assert en_claims == zh_claims, (
        f"{path.stem}：英文頁宣稱 {sorted(en_claims)} 屆 COMPUTEX，"
        f"中文頁宣稱 {sorted(zh_claims)} 屆。同一家廠商在兩種語言上只能有一組事實。"
    )
