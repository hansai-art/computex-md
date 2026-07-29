"""門檻跟著文體走 —— per_category 機制與實際 config 的守門測試。

母體 taiwan.md 全站只有一種文體（敘事長文），所以 word-count 4500 字、
image-health 3 張媒體，全站一個值就對。COMPUTEX.md 同時養兩種東西：

    Topics    產業觀察長文   → 沿用母體深度門檻
    Vendors   廠商事實頁     → 一張填滿來源的事實表 900 字就完整了

把 4500 字套到事實頁只會逼作者灌水，而灌水正好摧毀這個檔案庫唯一的價值
（被 AI 引用）。這份測試同時守兩件事：機制本身會動，以及**實際 config
真的有設**（不然機制在、設定漏掉，跟沒做一樣）。
"""

from pathlib import Path

import pytest

from lib.article_health.checks import word_count
from lib.article_health.config import load_config, option_for_category
from lib.article_health.loader import load_target

REPO_ROOT = Path(__file__).resolve().parents[2]


# ── 機制 ─────────────────────────────────────────────────────────────────────


def test_per_category_wins_over_flat_key():
    cfg = {"min_chars": 900, "per_category": {"Topics": 4500}}
    assert option_for_category(cfg, "Topics", "min_chars", 0) == 4500


def test_unlisted_category_falls_back_to_flat_key():
    cfg = {"min_chars": 900, "per_category": {"Topics": 4500}}
    assert option_for_category(cfg, "Vendors", "min_chars", 0) == 900


def test_missing_config_falls_back_to_default():
    assert option_for_category(None, "Vendors", "min_chars", 4500) == 4500


def test_empty_category_does_not_crash():
    cfg = {"min_chars": 900, "per_category": {"Topics": 4500}}
    assert option_for_category(cfg, "", "min_chars", 0) == 900


# ── 實際 config：設定漏掉的話，機制在也沒用 ─────────────────────────────────


@pytest.fixture(scope="module")
def real_config():
    return load_config(REPO_ROOT / "scripts" / "tools" / "article-health.config.toml")


def test_word_count_baseline_is_the_fact_page_not_the_essay(real_config):
    opts = real_config.get_check_config("word-count").options
    assert opts["min_chars"] < 2000, (
        "基準門檻要用事實頁（Vendors / Products）的尺度。"
        "基準留在長文尺度的話，每新增一家廠商就多一條假警報。"
    )
    assert opts["per_category"]["Topics"] >= 4000, "產業觀察長文仍要守深度門檻"


def test_image_floor_does_not_demand_stock_photos_on_fact_pages(real_config):
    opts = real_config.get_check_config("image-health").options
    assert opts["min_images"] <= 1
    assert opts["length_scaled"] is False, (
        "length_scaled 是「長文要更多媒體」的規則，事實表不是靠篇幅長出來的"
    )


def test_no_profile_silently_overrides_the_flat_threshold(real_config):
    """profile 的 options_overrides 是淺層 update，一寫 min_chars 就蓋掉基準。

    這是真的踩過的形狀：per_category 只在有列到的分類生效，基準被 profile
    蓋成 4500 之後，Vendors / Products 又被綁回長文門檻，而且完全無聲。
    """
    offenders = []
    for name, profile in real_config.profiles.items():
        for check in ("word-count", "image-health"):
            over = profile.options_overrides.get(check, {})
            for key in ("min_chars", "min_images"):
                if key in over:
                    offenders.append(f"{name}.{check}.{key}")
    assert offenders == [], (
        f"這些 profile 又把門檻寫了第二份：{offenders}。"
        "門檻只准放在 [checks.*].options，profile 只調嚴重度。"
    )


# ── 端對端：同一篇字數，換分類就換判定 ───────────────────────────────────────


def _write(tmp_path: Path, category: str, chars: int) -> Path:
    d = tmp_path / "knowledge" / category
    d.mkdir(parents=True, exist_ok=True)
    f = d / "t.md"
    f.write_text(
        f"---\ntitle: 't'\ndescription: 'd'\n---\n\n" + ("展" * chars) + "\n",
        encoding="utf-8",
    )
    return f


def _short_violations(path: Path, opts: dict):
    return [
        v
        for v in word_count.check(load_target(path), opts)
        if "篇幅不足" in v.message
    ]


def test_same_length_passes_as_vendor_and_fails_as_topic(tmp_path):
    opts = {"min_chars": 900, "per_category": {"Topics": 4500}}
    assert _short_violations(_write(tmp_path / "a", "Vendors", 1000), opts) == []
    assert _short_violations(_write(tmp_path / "b", "Topics", 1000), opts) != []
