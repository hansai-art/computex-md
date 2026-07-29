"""harvest-exhibitors.py 的歷年參展紀錄抽取。

守的是 2026-07-29 抓到的兩個「抽取到的東西看起來很正常，但少了東西」的錯。
兩個都不會讓任何程式當掉，也不會讓任何既有 gate 變紅 —— 產出的是**合法但不完整
的事實**，而這個檔案庫的全部價值就在事實完整。

1. **一年只留一列**。官方的結構是巢狀的：外層 `<li>` 是年份，內層 `<ul>` 才是那
   一年參加過的每一場展。舊版把整段壓平成文字後逐列比對，遇到同年第二列就跳過。
   AAEON 2022 那年同時參加了 TAIWAN EXPO in Malaysia 與 Taiwan Expo in India，
   我們只留了前者。全站修好後總列數從 542 變成 634，也就是原本掉了 92 列。

2. **展名被截斷**。舊版展名用 `[A-Za-z ]+` 抓，遇到 `'`、`&`、數字就斷：
   `Taiwan Int'l Lighting Show` → 「Taiwan Int」。站上因此存在一批看起來像展名、
   其實是半截字串的資料。

fixture 直接用官方頁面當日的真實結構（縮短過，但巢狀關係、class 名、`<p>` 前的
空白都照原樣），因為這兩個錯都是「結構讀錯」，用理想化的假 HTML 測不出來。
"""

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC = REPO_ROOT / "scripts" / "tools" / "harvest-exhibitors.py"


def _load():
    """檔名有連字號，不能直接 import，用 spec loader。"""
    spec = importlib.util.spec_from_file_location("harvest_exhibitors", _SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


harvest = _load()


#: 取自 AAEON 官方參展廠商頁（2026-07-29），保留巢狀結構與重複列。
FIXTURE = """
<h3>Exhibiting Record </h3>
<ul class="timeline">
  <li>
    <div class="sticky-panel"><span class="year" data-sticky>2026</span></div>
    <ul>
      <li><span class="date-range">2026/06/02 - 2026/06/05</span><p> COMPUTEX TAIPEI</p></li>
      <li><span class="date-range">2026/06/02 - 2026/06/05</span><p> COMPUTEX TAIPEI</p></li>
    </ul>
  </li>
  <li>
    <div class="sticky-panel"><span class="year" data-sticky>2022</span></div>
    <ul>
      <li><span class="date-range">2022/08/03 - 2022/08/05</span><p> TAIWAN EXPO in Malaysia</p></li>
      <li><span class="date-range">2022/09/28 - 2022/09/30</span><p> Taiwan Expo in India</p></li>
    </ul>
  </li>
  <li>
    <div class="sticky-panel"><span class="year" data-sticky>2019</span></div>
    <ul>
      <li><span class="date-range">2019/05/28 - 2019/06/01</span><p> Taiwan Int'l Lighting Show</p></li>
    </ul>
  </li>
</ul>
</section>
"""


@pytest.fixture(scope="module")
def rows():
    return harvest._parse_exhibiting_record(FIXTURE)


def test_a_year_with_two_shows_keeps_both(rows):
    y2022 = [r for r in rows if r["edition_year"] == "2022"]
    shows = [r["show"] for r in y2022]
    assert shows == ["TAIWAN EXPO in Malaysia", "Taiwan Expo in India"], (
        f"同一年的第二場展被吃掉了：{shows}"
    )


def test_show_names_with_apostrophes_are_not_truncated(rows):
    names = [r["show"] for r in rows]
    assert "Taiwan Int'l Lighting Show" in names, (
        f"展名在非字母字元處被截斷：{names}"
    )


def test_exact_duplicate_rows_collapse(rows):
    """官方頁面自己會重複列（AAEON 的 2026 印了兩次）。四項全等才收成一列。"""
    y2026 = [r for r in rows if r["edition_year"] == "2026"]
    assert len(y2026) == 1, f"完全相同的重複列沒有收斂：{y2026}"


def test_dates_are_normalised_to_iso(rows):
    assert all(
        r["start_date"].count("-") == 2 and "/" not in r["start_date"] for r in rows
    )


def test_missing_section_returns_empty_not_crash():
    assert harvest._parse_exhibiting_record("<html>no record here</html>") == []
