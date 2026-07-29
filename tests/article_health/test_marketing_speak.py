"""Tests for marketing_speak plugin.

擋「沒有出處的絕對宣稱」。這是 COMPUTEX.md 對母體 terminology plugin 的同位語：
母體守「用台灣人的話」，我們守「用規格的話，不用行銷的話」。

規則的形狀是刻意的 —— 不禁止「業界領先」這個詞，只禁止**沒有出處的**它。
有第三方可查證來源就放行，那正是我們希望參展廠商去做的事。

Canonical: docs/editorial/TERMINOLOGY.md §Layer 2 規格詞彙 vs 行銷詞彙
"""

from pathlib import Path

from lib.article_health.checks import marketing_speak
from lib.article_health.loader import load_target
from lib.article_health.types import Severity


def _violations(tmp_path: Path, body: str):
    doc = "---\ntitle: 測試\ndescription: 測試\n---\n\n" + body + "\n"
    f = tmp_path / "test.md"
    f.write_text(doc, encoding="utf-8")
    return list(marketing_speak.check(load_target(f), {}))


def _hards(vs):
    return [v for v in vs if v.severity is Severity.HARD]


def _warns(vs):
    return [v for v in vs if v.severity is Severity.WARN]


# ── HARD：裸的絕對宣稱 ────────────────────────────────────────────────────────


def test_bare_chinese_claim_is_hard(tmp_path):
    vs = _hards(_violations(tmp_path, "這家公司是業界領先的散熱方案供應商。"))
    assert len(vs) == 1
    assert "業界領先" in vs[0].message


def test_bare_english_claim_is_hard(tmp_path):
    vs = _hards(_violations(tmp_path, "Their platform is world-leading in throughput."))
    assert len(vs) == 1
    assert "world-leading" in vs[0].message


def test_english_claim_is_case_insensitive(tmp_path):
    assert len(_hards(_violations(tmp_path, "An INDUSTRY-LEADING cooling design."))) == 1


def test_multiple_claims_on_one_line_each_reported(tmp_path):
    body = "這是全球首創而且業界領先的方案。"
    assert len(_hards(_violations(tmp_path, body))) == 2


# ── 放行：有出處 ─────────────────────────────────────────────────────────────


def test_markdown_link_on_same_line_passes(tmp_path):
    body = "這家公司是業界領先的供應商，見 [2026 年度報告](https://example.com/r)。"
    assert _hards(_violations(tmp_path, body)) == []


def test_bare_url_on_same_line_passes(tmp_path):
    body = "Their platform is world-leading. https://example.com/benchmark"
    assert _hards(_violations(tmp_path, body)) == []


def test_footnote_marker_on_same_line_passes(tmp_path):
    body = "Their platform is world-leading in throughput[^1].\n\n[^1]: https://e.com"
    assert _hards(_violations(tmp_path, body)) == []


# ── 放行：引號內是轉述，不是我們的宣稱 ────────────────────────────────────────


def test_quoted_chinese_claim_passes(tmp_path):
    body = "該公司自稱「全球首創液冷機櫃」，但未提供第三方驗證。"
    assert _hards(_violations(tmp_path, body)) == []


def test_quoted_english_claim_passes(tmp_path):
    body = 'The vendor calls it "world-leading", without third-party data.'
    assert _hards(_violations(tmp_path, body)) == []


def test_claim_outside_quotes_still_caught(tmp_path):
    """引號放行只涵蓋引號內。同一行引號外的宣稱照樣要擋。"""
    body = "該公司自稱「效能翻倍」，而且確實是業界領先的方案。"
    assert len(_hards(_violations(tmp_path, body))) == 1


# ── WARN：緩和表述 ───────────────────────────────────────────────────────────


def test_hedged_claim_is_warn_not_hard(tmp_path):
    vs = _violations(tmp_path, "這家在散熱這一段數一數二。")
    assert _hards(vs) == []
    assert len(_warns(vs)) == 1


def test_hedged_claim_with_source_passes(tmp_path):
    body = "這家在散熱這一段數一數二，見 https://example.com/share。"
    assert _violations(tmp_path, body) == []


# ── 邊界 ─────────────────────────────────────────────────────────────────────


def test_clean_article_has_no_violations(tmp_path):
    body = "2027 年會期為 6 月 1 日至 4 日，地點在南港展覽館 1 館與 2 館。"
    assert _violations(tmp_path, body) == []


def test_code_fence_line_is_skipped(tmp_path):
    assert _violations(tmp_path, "```") == []


def test_line_numbers_point_at_the_body_not_the_frontmatter(tmp_path):
    """行號要能直接跳到出事的那一行 —— loader 會把 frontmatter 的行數補回來。"""
    body = "第一段沒問題。\n\n這家公司是業界領先的供應商。"
    vs = _hards(_violations(tmp_path, body))
    assert len(vs) == 1
    doc_lines = (
        "---\ntitle: 測試\ndescription: 測試\n---\n\n" + body + "\n"
    ).split("\n")
    assert "業界領先" in doc_lines[vs[0].line - 1]
