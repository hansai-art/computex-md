"""事實頁（Vendors / Products）踩到的兩個門檻誤報，以及它們的修法。

背景：Stage 4 一次灌進 86 個廠商事實頁之後，全站掃描出現兩種 86 份一模一樣的
警告。86 份一樣的警告不是 86 個問題，是一個規則沒見過這種文體 —— 而且它會把
真正的訊號淹掉，那才是最貴的損失。

這裡守兩件事：

1. `image-health` 的「缺靜態圖」分支在 min_images = 0 時會誤報。
   那條守的是「媒體夠但全是影片 → OG card 沒有靜態圖可用」，零媒體時
   `0 >= 0` 成立，印出來是「0 影片但 0 圖」，訊息本身自相矛盾。
   零媒體歸下一條 elif 管，不歸它。

2. `footnote-density` 對事實頁判 C（有 inline URL、無正式腳註）。
   事實頁的引用長在表格「出處」欄，每列自帶連結 + 查證日期，比腳註**更好**
   稽核：欄位缺了產生器會擋，腳註漏了不會。所以降級為 INFO，等級照算照報，
   長文型別（Topics / Editions）維持 WARN 不動。

兩條都是降級 / 修條件，NEVER 刪 gate、NEVER 關整支（Rule 56）。
"""

from pathlib import Path

import pytest

from lib.article_health.checks import footnote_density, image_health
from lib.article_health.config import load_config
from lib.article_health.loader import load_target
from lib.article_health.types import Severity

REPO_ROOT = Path(__file__).resolve().parents[2]


def _write(tmp_path: Path, category: str, body: str) -> Path:
    d = tmp_path / "knowledge" / category
    d.mkdir(parents=True, exist_ok=True)
    f = d / "t.md"
    f.write_text(
        f"---\ntitle: 't'\ndescription: 'd'\ncategory: '{category}'\n---\n\n{body}\n",
        encoding="utf-8",
    )
    return f


# ── 1. image-health：零媒體 + min_images=0 不該喊「缺靜態圖」 ────────────────

_FACT_BODY = "# 標題\n\n| 項目 | 內容 |\n| --- | --- |\n| 攤位 | J0106 |\n" + "展" * 500


def _static_image_warnings(path: Path, opts: dict) -> list[str]:
    return [
        v.message
        for v in image_health.check(load_target(path), opts)
        if "缺靜態圖" in v.message
    ]


def test_zero_media_fact_page_does_not_claim_missing_static_image(tmp_path):
    opts = {"min_images": 1, "length_scaled": False, "per_category": {"Vendors": 0}}
    assert _static_image_warnings(_write(tmp_path, "Vendors", _FACT_BODY), opts) == []


def test_the_message_would_have_been_self_contradictory(tmp_path):
    """回歸測試：修之前這裡會冒出「0 影片但 0 圖」。

    留這支是因為它抓的是訊息的荒謬，不只是計數。一條說「你有 0 支影片，
    所以缺靜態圖」的規則，讀的人只會學會忽略這支檢查。
    """
    opts = {"min_images": 0, "length_scaled": False}
    msgs = _static_image_warnings(_write(tmp_path, "Vendors", _FACT_BODY), opts)
    assert not any("0 影片" in m for m in msgs), msgs


def test_the_original_rule_still_fires_when_there_is_video_but_no_image(tmp_path):
    """守住修法沒有把規則本體弄壞：有影片、沒靜態圖，還是要喊。"""
    body = _FACT_BODY + '\n\n<iframe src="https://www.youtube.com/embed/x"></iframe>\n'
    opts = {"min_images": 1, "length_scaled": False}
    assert _static_image_warnings(_write(tmp_path, "Topics", body), opts) != []


# ── 2. footnote-density：事實頁降 INFO，長文維持 WARN ───────────────────────

_SOURCED_TABLE = (
    "# 標題\n\n| 項目 | 出處 |\n| --- | --- |\n"
    "| 攤位 | [官方頁](https://example.com/a) |\n"
    "| 展區 | [官方頁](https://example.com/b) |\n"
    "| 官網 | [官方頁](https://example.com/c) |\n"
)


def _severities(path: Path, opts: dict) -> list[Severity]:
    return [v.severity for v in footnote_density.check(load_target(path), opts)]


def test_fact_page_citation_grade_is_reported_not_silenced(tmp_path):
    opts = {"severity": "warn", "per_category": {"Vendors": "info"}}
    sev = _severities(_write(tmp_path, "Vendors", _SOURCED_TABLE), opts)
    assert sev == [Severity.INFO], "等級要照報，只是不佔 WARN 的注意力預算"


def test_long_form_still_takes_the_warn(tmp_path):
    opts = {"severity": "warn", "per_category": {"Vendors": "info"}}
    assert _severities(_write(tmp_path, "Topics", _SOURCED_TABLE), opts) == [
        Severity.WARN
    ]


def test_garbage_severity_falls_back_instead_of_crashing(tmp_path):
    opts = {"per_category": {"Vendors": "不存在的等級"}}
    assert _severities(_write(tmp_path, "Vendors", _SOURCED_TABLE), opts) == [
        Severity.WARN
    ]


# ── 3. 實際 config 真的有設（機制在、設定漏掉 = 等於沒做）───────────────────


@pytest.fixture(scope="module")
def real_config():
    return load_config(REPO_ROOT / "scripts" / "tools" / "article-health.config.toml")


@pytest.mark.parametrize("check_name", ["image-health", "media-richness"])
def test_both_image_plugins_exempt_fact_pages(real_config, check_name):
    """兩支各有一份 min_images，只調一支的話事實頁會被另一支攔下。"""
    per_cat = real_config.get_check_config(check_name).options["per_category"]
    assert per_cat["Vendors"] == 0
    assert per_cat["Products"] == 0


def test_footnote_density_downgrade_is_configured(real_config):
    opts = real_config.get_check_config("footnote-density").options
    assert opts["severity"] == "warn", "長文仍吃 WARN"
    assert opts["per_category"]["Vendors"] == "info"
    assert opts["per_category"]["Products"] == "info"
