"""中國用語 gate 不准是空砲彈。

2026-07-29 發現：出生時 `knowledge/` 清空的同時 `data/terminology/` 也一起沒了，
而 terminology plugin 的設計是「TSV 不存在就 graceful skip」—— 於是全站掃描
`terminology hard=0` 一路綠燈，看起來守得好好的，實際上一個詞都沒在比對。

這正是母體 langs.py 那個病的同一個形狀（讀不到 registry 就靜默沿用保底清單，
「看起來會動」）。守門的東西壞掉時必須有聲音，不能安靜地放行。

順帶說明為什麼這個 gate 對展會版比對母體**更**重要：AI 硬體的詞彙正是中國用語
最容易滲進來的地方 —— 原廠 datasheet、翻譯過的廠商文案、跨海轉載的新聞稿，
軟件 / 硬件 / 內存 / 服務器 / 芯片 / 展台 一整串跟著規格表整段搬進來。
"""

from pathlib import Path

import pytest

from lib.article_health.checks import terminology
from lib.article_health.loader import load_target
from lib.article_health.types import Severity

REPO_ROOT = Path(__file__).resolve().parents[2]
DETECTION_TSV = REPO_ROOT / "data" / "terminology" / ".china-terms.detection.tsv"


def _rows():
    if not DETECTION_TSV.exists():
        return []
    return [
        ln.split("\t")
        for ln in DETECTION_TSV.read_text(encoding="utf-8").splitlines()
        if ln and not ln.startswith("#")
    ]


def test_detection_table_exists():
    assert DETECTION_TSV.exists(), (
        f"{DETECTION_TSV} 不見了 → terminology plugin 會 graceful skip，"
        "全站掃描照樣 hard=0，但一個詞都沒比對。跑 "
        "`npm run prebuild:terms` 重新產生。"
    )


def test_detection_table_is_not_empty():
    rows = _rows()
    assert len(rows) >= 20, (
        f"偵測詞表只有 {len(rows)} 筆 —— 詞庫可能被清空或 extractor 沒讀到 YAML。"
    )


def test_hardware_vocabulary_is_covered():
    """這幾個是 AI 硬體 corpus 一定會遇到的，缺任何一個代表詞庫沒為這個物種調過。"""
    terms = {r[0] for r in _rows()}
    must_have = {"軟件", "硬件", "內存", "服務器", "芯片", "存儲", "帶寬", "顯卡"}
    assert must_have <= terms, f"詞庫缺這些硬體用語：{sorted(must_have - terms)}"


def test_trade_show_vocabulary_is_covered():
    """展會用語是這個物種獨有的加碼，母體詞庫沒有。"""
    terms = {r[0] for r in _rows()}
    must_have = {"展台", "展商"}
    assert must_have <= terms, f"詞庫缺這些展會用語：{sorted(must_have - terms)}"


@pytest.mark.parametrize(
    "china,taiwan",
    [("服務器", "伺服器"), ("芯片", "晶片"), ("展台", "攤位"), ("內存", "記憶體")],
)
def test_gate_actually_fires(tmp_path, china, taiwan, monkeypatch):
    """端對端：不是只驗表存在，而是驗 plugin 真的會叫。"""
    monkeypatch.chdir(REPO_ROOT)  # plugin 用相對路徑讀 TSV
    d = tmp_path / "knowledge" / "Topics"
    d.mkdir(parents=True)
    f = d / "t.md"
    f.write_text(
        f"---\ntitle: 't'\ndescription: 'd'\n---\n\n這段提到{china}。\n",
        encoding="utf-8",
    )
    violations = list(terminology.check(load_target(f), {}))
    hits = [v for v in violations if china in v.message]
    assert hits, f"「{china}」沒被抓到"
    assert hits[0].severity is Severity.HARD
    assert taiwan in hits[0].message, "訊息要直接給台灣用語，不要只說錯了"


def test_clean_taiwanese_prose_passes(tmp_path, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    d = tmp_path / "knowledge" / "Topics"
    d.mkdir(parents=True)
    f = d / "t.md"
    f.write_text(
        "---\ntitle: 't'\ndescription: 'd'\n---\n\n"
        "這台伺服器用的晶片與記憶體規格都列在攤位資料上。\n",
        encoding="utf-8",
    )
    assert list(terminology.check(load_target(f), {})) == []
