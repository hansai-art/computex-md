"""廠商頁的四條不變條件，直接掃真實 corpus。

為什麼掃輸出而不是測產生器：廠商頁的寫入口不只有 `generate-vendor-pages.py`。
「認領這一頁」的設計就是要讓廠商自己送 PR 改事實層，所以守門必須守在**檔案**
上，不是守在產生它的那支程式上。產生器改壞、或某個 PR 手改壞，這裡都要叫。

四條：
1. 事實表每一列都要有出處連結 + 查證日期 —— 這是這個檔案庫唯一的賣點，
   一列沒有出處，整頁的可信度就跟隨便一個彙整站一樣了。
2. 不准出現破折號（Hans 的全域寫作規則，改用冒號）。
3. 檔名 lowercase-hyphen（`slug-format` gate 的同一把尺，這裡再守一次是因為
   廠商 PR 可能用公司全名當檔名）。
4. 每頁都要有「官方名錄未提供的」留白段 —— 留白是刻意的產品決策，
   不是還沒寫完。哪天有人為了讓頁面「看起來完整」把它刪掉，這裡要擋。
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
VENDOR_DIR = REPO_ROOT / "knowledge" / "Vendors"

VENDOR_FILES = sorted(VENDOR_DIR.glob("*.md")) if VENDOR_DIR.exists() else []

_RE_GOOD_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_RE_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_RE_LINK = re.compile(r"\[[^\]]+\]\(https?://[^)]+\)")


def test_there_are_vendor_pages_at_all():
    """守住「掃了 0 個檔所以全部通過」這種假綠燈。"""
    assert len(VENDOR_FILES) >= 20, f"只找到 {len(VENDOR_FILES)} 個廠商頁"


@pytest.mark.parametrize("path", VENDOR_FILES, ids=lambda p: p.stem)
def test_every_fact_row_carries_a_source_and_a_check_date(path: Path):
    text = path.read_text(encoding="utf-8")
    body = text.split("---", 2)[-1]

    section = re.search(r"## 官方名錄記載的事實\n(.*?)\n## ", body, re.S)
    assert section, "缺「官方名錄記載的事實」段"

    # 欄寬要正規化再比對：prettier 會把表格補成對齊的樣子（`| 項目      | 內容 …`、
    # 分隔列補成 `| ------ |`），所以任何靠 `"| 項目 |" in ln` 或 `startswith("| ---")`
    # 的過濾在格式化前後會得到不同答案。這支測試守的是內容，不能被排版左右。
    rows = []
    for ln in section.group(1).splitlines():
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if not ln.strip().startswith("|"):
            continue
        if cells[0] == "項目":  # 表頭
            continue
        if all(set(c) <= {"-", ":"} and c for c in cells):  # 分隔列
            continue
        rows.append(ln)
    assert rows, "事實表是空的"

    for row in rows:
        assert _RE_LINK.search(row), f"這一列沒有出處連結：{row[:60]}"
        assert _RE_DATE.search(row), f"這一列沒有查證日期：{row[:60]}"


@pytest.mark.parametrize("path", VENDOR_FILES, ids=lambda p: p.stem)
def test_no_em_dash(path: Path):
    text = path.read_text(encoding="utf-8")
    assert "—" not in text, "破折號要改成冒號"


@pytest.mark.parametrize("path", VENDOR_FILES, ids=lambda p: p.stem)
def test_filename_is_a_clean_slug(path: Path):
    assert _RE_GOOD_SLUG.match(path.stem), (
        f"檔名 `{path.stem}` 會產生帶 %20 或大寫的網址"
    )


@pytest.mark.parametrize("path", VENDOR_FILES, ids=lambda p: p.stem)
def test_the_blank_list_is_still_there(path: Path):
    text = path.read_text(encoding="utf-8")
    assert "## 官方名錄未提供的" in text, (
        "留白段被刪了。留白是產品決策：官方沒公布的就是空的，"
        "補滿它需要可查證來源，不是需要看起來完整。"
    )


# ── 2026-07-29 新增的兩條 ────────────────────────────────────────────────
#
# 起因：官方的 `Exhibiting Record` 收的是這家公司參加過的**所有外貿協會展會**
# （TAITRONICS、TAIPEI AMPA、TIMTOS、各國台灣形象展⋯⋯），86 家共 634 列裡只有
# 467 列是 COMPUTEX。產生器原本把整包當成 COMPUTEX 屆數在算，於是每一頁的
# 「參展過 N 屆」都可能多算，`/explore` 的「在 COMPUTEX 待最久的廠商」榜也排錯人。
#
# 這條測試不需要外部資料：頁面上的宣稱（散文裡的 N）與證據（同一頁的表）本來就
# 該對得起來，直接互相驗證。這也正是這個站對讀者的承諾 —— 每一個數字都能在同一
# 頁被回推。


#: 頁面上會出現屆數宣稱的四種句型。單屆與多屆寫法不同，全部都要抓得到 ——
#: 抓不到的句型會被算成「這頁沒有宣稱」，測試就從守門變成放行。
_RE_CX_CLAIMS = (
    re.compile(r"(\d+)\s*屆\s*COMPUTEX"),  # 概覽段：參展過 7 屆 COMPUTEX
    re.compile(r"COMPUTEX 參展年份涵蓋[^，。]*，共\s*(\d+)\s*屆"),  # description
    re.compile(r"筆是 COMPUTEX（(\d+)\s*屆"),  # 歷年紀錄段導言（有其他展會時）
    re.compile(r"參展紀錄全部是 COMPUTEX，共\s*(\d+)\s*屆"),  # 同上（沒有其他展會時）
)
#: 只有一屆的句型不帶數字：「官方名錄目前只記載 2026 這一屆 COMPUTEX」。
_RE_CX_SINGLE = re.compile(r"只記載\s*\d{4}\s*這一屆\s*COMPUTEX")

_RE_TABLE_ROW = re.compile(
    r"^\|\s*(\d{4})\s*\|[^|]*\|\s*([^|]+?)\s*\|\s*$", re.M
)


def _computex_editions_from_table(text: str) -> int | None:
    """從「歷年參展紀錄」表數出不重複的 COMPUTEX 屆別年份。"""
    section = re.search(r"## 歷年參展紀錄\n(.*?)(?:\n## |\Z)", text, re.S)
    if not section:
        return None
    years = {
        y
        for y, show in _RE_TABLE_ROW.findall(section.group(1))
        if show.strip().upper().startswith("COMPUTEX")
    }
    return len(years)


@pytest.mark.parametrize("path", VENDOR_FILES, ids=lambda p: p.stem)
def test_computex_edition_count_matches_the_table_on_the_same_page(path: Path):
    text = path.read_text(encoding="utf-8")
    actual = _computex_editions_from_table(text)
    assert actual, "歷年參展紀錄表裡數不到任何 COMPUTEX 列"

    claims = {int(n) for rx in _RE_CX_CLAIMS for n in rx.findall(text)}
    if _RE_CX_SINGLE.search(text):
        claims.add(1)
    assert claims, "頁面沒有任何 COMPUTEX 屆數宣稱（概覽段應該要有）"
    for claimed in claims:
        assert claimed == actual, (
            f"頁面宣稱 {claimed} 屆 COMPUTEX，但同一頁的表只數得出 {actual} 屆。"
            f"最常見的原因是把其他外貿協會展會（TAITRONICS / TAIPEI AMPA / "
            f"台灣形象展⋯⋯）一起算進 COMPUTEX 屆數。"
        )


@pytest.mark.parametrize("path", VENDOR_FILES, ids=lambda p: p.stem)
def test_no_cjk_latin_collision(path: Path):
    """中文字後面直接接西文字母，中間要有空格。

    「展區為AI 運算與技術」是產生器 f-string 拼出來的，一次就是 86 頁 ×2 處。
    只掃散文，不掃表格與 frontmatter：表格欄位（`| 展區 | AI Computing…`）本來就
    靠 `|` 分隔，YAML 值同理。
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
