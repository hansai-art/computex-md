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

    rows = [
        ln
        for ln in section.group(1).splitlines()
        if ln.startswith("|") and not ln.startswith("| ---") and "| 項目 |" not in ln
    ]
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
