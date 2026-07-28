"""Tests for cjk_punct plugin.

Critical test: test_wikilink_url_preserved guards against the 2026-05-04
黃魚鴞 incident where `[name](/url)` got converted to `[name](/url）`.
"""

import textwrap
from pathlib import Path

from lib.article_health import registry
from lib.article_health.checks import cjk_punct
from lib.article_health.loader import load_target
from lib.article_health.types import Severity


def _write_tmp(tmp_path: Path, content: str, name: str = "test.md") -> Path:
    f = tmp_path / name
    f.write_text(content, encoding="utf-8")
    return f


def _violations(tmp_path: Path, body: str, frontmatter: str = ""):
    if frontmatter:
        content = f"---\n{frontmatter}---\n{body}"
    else:
        content = body
    f = _write_tmp(tmp_path, content)
    target = load_target(f)
    return list(cjk_punct.check(target, {})), target


# ════════════════════════════════════════════════════════════════════════
# CRITICAL regression: 黃魚鴞 wikilink incident
# ════════════════════════════════════════════════════════════════════════


def test_wikilink_url_preserved(tmp_path):
    """`[名稱](/nature/CJK)` MUST NOT trigger CJK paren conversion.

    The closing `)` is preceded by CJK and followed by space — pattern
    would normally match, but it's inside protected_regions (link-url).
    """
    body = "- [福爾摩沙鳥類學](/nature/福爾摩沙鳥類學) — 黃魚鴞 1916 年才被命名\n"
    violations, _ = _violations(tmp_path, body)
    # No violations from rparen rule — the `)` is inside a protected region
    rparen_v = [v for v in violations if "（" in (v.fix_suggestion or "") or "）" in (v.fix_suggestion or "")]
    assert not rparen_v, f"link URL `)` should be protected, got {rparen_v}"


def test_wikilink_url_preserved_after_fix(tmp_path):
    """fix() must not corrupt the link URL."""
    body = "- [福爾摩沙鳥類學](/nature/福爾摩沙鳥類學) — 黃魚鴞 1916 年才被命名\n"
    f = _write_tmp(tmp_path, body)
    target = load_target(f)
    cjk_punct.fix(target, {})
    new_text = f.read_text(encoding="utf-8")
    assert "(/nature/福爾摩沙鳥類學)" in new_text
    assert "(/nature/福爾摩沙鳥類學）" not in new_text


def test_multiple_wikilinks_in_further_reading(tmp_path):
    """Mimic the actual 黃魚鴞 延伸閱讀 block."""
    body = textwrap.dedent(
        """\
        **延伸閱讀**：

        - [福爾摩沙鳥類學](/nature/福爾摩沙鳥類學) — 黃魚鴞 1916 年才被命名
        - [櫻花鉤吻鮭](/nature/櫻花鉤吻鮭) — 兩者共享七家灣溪生態系
        - [台灣黑熊](/nature/台灣黑熊) — 同為屏東科技大學
        """
    )
    f = _write_tmp(tmp_path, body)
    target = load_target(f)
    cjk_punct.fix(target, {})
    new_text = f.read_text(encoding="utf-8")
    # All 3 link URLs intact
    assert "(/nature/福爾摩沙鳥類學)" in new_text
    assert "(/nature/櫻花鉤吻鮭)" in new_text
    assert "(/nature/台灣黑熊)" in new_text
    # No fullwidth ） introduced
    assert "（/nature" not in new_text


# ════════════════════════════════════════════════════════════════════════
# Standard CJK punct cases
# ════════════════════════════════════════════════════════════════════════


def test_comma_between_cjk(tmp_path):
    violations, _ = _violations(tmp_path, "黃魚鴞,六公里溪流養一對\n")
    assert len(violations) == 1
    assert violations[0].fix_suggestion == "，"


def test_colon_between_cjk(tmp_path):
    violations, _ = _violations(tmp_path, "原因不複雜:牠晝伏夜出\n")
    assert any("：" in (v.fix_suggestion or "") for v in violations)


def test_comma_cjk_to_digit(tmp_path):
    """`對,1800` should match (CJK→digit boundary)."""
    violations, _ = _violations(tmp_path, "六公里溪流養一對,1800 公尺\n")
    assert any("，" in (v.fix_suggestion or "") for v in violations)


def test_intra_number_comma_preserved(tmp_path):
    """`1,800` (digit,digit) MUST NOT trigger conversion."""
    violations, _ = _violations(tmp_path, "海拔 1,800 公尺烏心石\n")
    # No violation for the comma in `1,800` (both sides are digits)
    assert not violations


def test_english_comma_preserved(tmp_path):
    """`Sun, Y. H.,` (English citation) should not trigger."""
    violations, _ = _violations(tmp_path, "Sun, Y. H., Wang, Y.\n")
    assert not violations


def test_footnote_ref_followed_by_punct(tmp_path):
    """`[^1],1994 年` should convert to `[^1]，1994 年`."""
    body = "首次記錄[^1],1994 年才有第一個巢被找到\n"
    violations, _ = _violations(tmp_path, body)
    assert any(v.fix_suggestion and "，" in v.fix_suggestion for v in violations)


def test_bold_marker_followed_by_colon(tmp_path):
    """`**延伸閱讀**:` should convert to `**延伸閱讀**：`."""
    body = "**延伸閱讀**:這是一個列表\n"
    violations, _ = _violations(tmp_path, body)
    assert violations  # should match bold-colon


def test_parens_between_cjk(tmp_path):
    """`其他三種(褐魚鴞)腳趾裸露` — both sides CJK, paren should convert."""
    body = "其他三種(褐魚鴞)腳趾裸露\n"
    violations, _ = _violations(tmp_path, body)
    assert any("（" in (v.fix_suggestion or "") for v in violations)


def test_english_in_parens_preserved(tmp_path):
    """`(*Ketupa flavipes*)` — Latin text in parens, should stay halfwidth."""
    violations, _ = _violations(tmp_path, "黃魚鴞(*Ketupa flavipes*)是台灣最大\n")
    # 鴞( CJK→Latin: not caught by CJK→CJK rule
    # *) Latin→CJK: not caught (not preceded by CJK)
    # Should yield zero rparen / lparen violations
    fix_chars = [v.fix_suggestion for v in violations if v.fix_suggestion]
    assert "（" not in fix_chars
    assert "）" not in fix_chars


# ════════════════════════════════════════════════════════════════════════
# Protected region: code blocks
# ════════════════════════════════════════════════════════════════════════


def test_fenced_code_block_preserved(tmp_path):
    body = textwrap.dedent(
        """\
        前文段落。

        ```python
        # comment with comma,colon:in code
        x = (1,2)
        ```

        後文段落。
        """
    )
    f = _write_tmp(tmp_path, body)
    target = load_target(f)
    cjk_punct.fix(target, {})
    new_text = f.read_text(encoding="utf-8")
    # Code block unchanged
    assert "comma,colon:in code" in new_text
    assert "(1,2)" in new_text


def test_inline_code_preserved(tmp_path):
    body = "前文 `foo,bar:baz` 後文。\n"
    f = _write_tmp(tmp_path, body)
    target = load_target(f)
    cjk_punct.fix(target, {})
    assert "`foo,bar:baz`" in f.read_text(encoding="utf-8")


# ════════════════════════════════════════════════════════════════════════
# Plugin protocol smoke
# ════════════════════════════════════════════════════════════════════════


def test_plugin_metadata():
    """Module exposes the 5 required attrs."""
    assert cjk_punct.CHECK_NAME == "cjk-punct"
    assert cjk_punct.DEFAULT_SEVERITY == Severity.HARD
    assert "EDITORIAL.md" in cjk_punct.EDITORIAL_REF
    assert callable(cjk_punct.check)
    assert callable(cjk_punct.fix)


def test_plugin_only_zh_tw():
    assert "zh-TW" in cjk_punct.APPLIES_TO


def test_plugin_validates_against_registry():
    """Registry-level discovery should pick up cjk_punct."""
    registry.reset_registry()
    found = registry.discover_checks()
    assert "cjk-punct" in found, f"got {list(found.keys())}"


# ════════════════════════════════════════════════════════════════════════
# Frontmatter exempted (cjk_punct only checks BODY)
# ════════════════════════════════════════════════════════════════════════


def test_frontmatter_exempted_from_body_check(tmp_path):
    """cjk_punct should not flag punct in frontmatter — that's title-format's job."""
    content = textwrap.dedent(
        """\
        ---
        title: '黃魚鴞:六公里溪流養一對,1,800 公尺'
        ---

        內文沒有半形標點。
        """
    )
    f = _write_tmp(tmp_path, content)
    target = load_target(f)
    violations = list(cjk_punct.check(target, {}))
    # frontmatter has half-width punct but cjk_punct only checks body
    assert violations == [], f"expected no body violations, got {violations}"
