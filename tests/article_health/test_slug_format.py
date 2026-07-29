"""檔名就是網址，所以檔名要能當網址看。

2026-07-29 出生時第一篇就踩到：`COMPUTEX 2027.md` 產出
`/editions/COMPUTEX%202027/`，既不是可讀的中文（母體 CJK 檔名的好處），
也不是乾淨的 ASCII slug，兩邊的好處都沒拿到。

出生階段擋下來只要改一個檔名；等 30-50 家廠商頁灌完才發現，代價是全站 redirect。
"""

from pathlib import Path

import pytest

from lib.article_health.checks import slug_format
from lib.article_health.loader import load_target
from lib.article_health.types import Severity


def _check(tmp_path: Path, filename: str):
    d = tmp_path / "knowledge" / "Vendors"
    d.mkdir(parents=True, exist_ok=True)
    f = d / filename
    f.write_text("---\ntitle: 't'\ndescription: 'd'\n---\n\nbody.\n", encoding="utf-8")
    return list(slug_format.check(load_target(f), {}))


@pytest.mark.parametrize(
    "name",
    ["computex-2027.md", "gigabyte.md", "asus-rog-2027.md", "supermicro.md", "h200.md"],
)
def test_good_ascii_slugs_pass(tmp_path, name):
    assert _check(tmp_path, name) == []


@pytest.mark.parametrize(
    "name",
    [
        "COMPUTEX 2027.md",  # 空白 + 大寫，實際踩到的那個
        "COMPUTEX-2027.md",  # 只有大寫
        "computex_2027.md",  # 底線
        "computex 2027.md",  # 只有空白
    ],
)
def test_bad_ascii_slugs_are_hard(tmp_path, name):
    violations = _check(tmp_path, name)
    assert len(violations) == 1
    assert violations[0].severity is Severity.HARD


def test_message_names_the_actual_problem(tmp_path):
    v = _check(tmp_path, "COMPUTEX 2027.md")[0]
    assert "空白" in v.message
    assert "大寫" in v.message


def test_fix_suggestion_is_a_usable_filename(tmp_path):
    v = _check(tmp_path, "COMPUTEX 2027.md")[0]
    assert "`computex-2027.md`" in v.fix_suggestion


def test_cjk_filename_passes(tmp_path):
    """含 CJK 的檔名沿用母體慣例，中文標題本身就是可讀的網址。"""
    assert _check(tmp_path, "台達電子.md") == []


def test_cjk_filename_with_space_still_fails(tmp_path):
    """CJK 放行的是中文字，不是空白。"""
    violations = _check(tmp_path, "台達電子 2027.md")
    assert len(violations) == 1
    assert "空白" in violations[0].message


def test_hub_pages_are_skipped(tmp_path):
    """`_` 開頭是 hub 頁，由樣板產生，不走文章路由。"""
    assert _check(tmp_path, "_Vendors.md") == []


def test_the_real_corpus_is_clean():
    """實際 knowledge/ 全掃 —— 規則寫了但現有檔案沒過，等於沒寫。"""
    repo = Path(__file__).resolve().parents[2]
    offenders = []
    for md in (repo / "knowledge").rglob("*.md"):
        if md.name.startswith("_"):
            continue
        if list(slug_format.check(load_target(md), {})):
            offenders.append(md.relative_to(repo).as_posix())
    assert offenders == [], f"這些檔名會產出難看的網址：{offenders}"
