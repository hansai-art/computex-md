"""Tests for frontmatter_format plugin.

This is the formatter counterpart to `frontmatter-title`: it checks the
REWRITE-PIPELINE Stage 4 YAML shape, field order, and Prettier-stable style.
"""

from pathlib import Path

from lib.article_health import registry
from lib.article_health.checks import frontmatter_format
from lib.article_health.config import Config, ProfileConfig
from lib.article_health.loader import load_target
from lib.article_health.runner import run_checks
from lib.article_health.types import Severity


GOOD_FRONTMATTER = """\
title: '泛科學：從科學新聞黑洞到演算法裡的知識工業'
description: 'desc'
date: 2026-05-07
category: 'Society'
tags: ['媒體', '科學傳播']
subcategory: '媒體與言論'
author: 'COMPUTEX.md'
featured: false
lastVerified: 2026-05-07
lastHumanReview: false
researchReport: reports/research/2026-05/泛科學.md
"""


def _write_article(tmp_path: Path, frontmatter: str) -> Path:
    f = tmp_path / "knowledge" / "Society" / "test.md"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(f"---\n{frontmatter}---\n\nbody.\n", encoding="utf-8")
    return f


def _violations(tmp_path: Path, frontmatter: str):
    target = load_target(_write_article(tmp_path, frontmatter))
    return list(frontmatter_format.check(target, {}))


def test_good_frontmatter_passes(tmp_path):
    assert _violations(tmp_path, GOOD_FRONTMATTER) == []


def test_missing_required_field_is_hard(tmp_path):
    fm = GOOD_FRONTMATTER.replace("featured: false\n", "")
    violations = _violations(tmp_path, fm)
    hard = [v for v in violations if v.severity == Severity.HARD]
    assert any("featured" in v.message for v in hard)


def test_required_field_order_warns_by_default(tmp_path):
    fm = GOOD_FRONTMATTER.replace(
        "category: 'Society'\ntags: ['媒體', '科學傳播']\n",
        "tags: ['媒體', '科學傳播']\ncategory: 'Society'\n",
    )
    violations = _violations(tmp_path, fm)
    assert any("欄位順序錯" in v.message for v in violations)
    assert all(v.severity != Severity.HARD for v in violations)


def test_stage4_promotes_formatter_warns_to_hard(tmp_path):
    fm = GOOD_FRONTMATTER.replace(
        "category: 'Society'\ntags: ['媒體', '科學傳播']\n",
        "tags: ['媒體', '科學傳播']\ncategory: 'Society'\n",
    )
    target = load_target(_write_article(tmp_path, fm))
    cfg = Config()
    cfg.profiles["rewrite-stage-4"] = ProfileConfig(
        name="rewrite-stage-4",
        checks=["frontmatter-format"],
        severity_overrides={"frontmatter-format": Severity.HARD},
    )
    report = run_checks(target, cfg, profile_name="rewrite-stage-4")
    hard = [v for v in report.all_violations if v.severity == Severity.HARD]
    assert any("欄位順序錯" in v.message for v in hard)


def test_prettier_wrapped_flow_tags_passes(tmp_path):
    fm = GOOD_FRONTMATTER.replace(
        "tags: ['媒體', '科學傳播']\n",
        "tags:\n  [\n    '媒體',\n    '科學傳播',\n  ]\n",
    )
    assert _violations(tmp_path, fm) == []


def test_block_sequence_tags_passes(tmp_path):
    """block sequence（`- item`）是合法 YAML 陣列，不該被擋。

    2026-07-29 COMPUTEX.md 政策改動（母體是 WARN，要求一律 flow array）：
    loader 那支 minimal parser 只認單行 flow array，block sequence 讀成空字串，
    於是 frontmatter-format 判定「tags 不是 array」直接 hard fail；而 Prettier
    會把長的 flow array 折成多行，同樣讀不到。兩種合法寫法都被擋，作者只好把
    tags 縮短到一行塞得下 —— 變成工具在決定內容。正解是修 parser（已修），
    並讓檢查接受兩種 YAML 陣列寫法。
    """
    fm = GOOD_FRONTMATTER.replace(
        "tags: ['媒體', '科學傳播']\n",
        "tags:\n  - 媒體\n  - 科學傳播\n",
    )
    assert _violations(tmp_path, fm) == []


def test_scalar_tags_still_hard_fails(tmp_path):
    """放寬只涵蓋「陣列的兩種寫法」。純字串 tags 依然要擋。"""
    fm = GOOD_FRONTMATTER.replace(
        "tags: ['媒體', '科學傳播']\n",
        "tags: '媒體'\n",
    )
    violations = _violations(tmp_path, fm)
    assert any("tags" in v.message and "陣列" in v.message for v in violations)


def test_unquoted_string_scalar_warns(tmp_path):
    fm = GOOD_FRONTMATTER.replace("category: 'Society'\n", "category: Society\n")
    violations = _violations(tmp_path, fm)
    assert any("category" in v.message and "單引號" in v.message for v in violations)


def test_quoted_date_warns(tmp_path):
    fm = GOOD_FRONTMATTER.replace("date: 2026-05-07\n", "date: '2026-05-07'\n")
    violations = _violations(tmp_path, fm)
    assert any("日期不需加引號" in v.message for v in violations)


def test_string_tags_are_hard(tmp_path):
    fm = GOOD_FRONTMATTER.replace(
        "tags: ['媒體', '科學傳播']\n",
        "tags: '媒體, 科學傳播'\n",
    )
    violations = _violations(tmp_path, fm)
    hard = [v for v in violations if v.severity == Severity.HARD]
    assert any("tags" in v.message and "array" in v.message for v in hard)


def test_category_must_match_path(tmp_path):
    fm = GOOD_FRONTMATTER.replace("category: 'Society'\n", "category: 'Culture'\n")
    violations = _violations(tmp_path, fm)
    hard = [v for v in violations if v.severity == Severity.HARD]
    assert any("必須符合路徑分類" in v.message for v in hard)


def test_no_frontmatter_is_hard(tmp_path):
    f = tmp_path / "knowledge" / "Society" / "test.md"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("body only\n", encoding="utf-8")
    violations = list(frontmatter_format.check(load_target(f), {}))
    assert len(violations) == 1
    assert violations[0].severity == Severity.HARD
    assert "缺 frontmatter" in violations[0].message


def test_translation_files_skipped_at_runner_level(tmp_path):
    f = tmp_path / "knowledge" / "en" / "Society" / "test.md"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(f"---\n{GOOD_FRONTMATTER}---\n\nbody.\n", encoding="utf-8")
    cfg = Config()
    report = run_checks(load_target(f), cfg, check_name="frontmatter-format")
    assert report.results == []


def test_plugin_registered():
    registry.reset_registry()
    found = registry.discover_checks()
    assert "frontmatter-format" in found, list(found.keys())


# ── fix() tests (2026-05-08 #884 root-cause fix) ──────────────────────────


def _fix_and_reload(tmp_path: Path, frontmatter: str) -> tuple[int, str]:
    f = _write_article(tmp_path, frontmatter)
    target = load_target(f)
    n = frontmatter_format.fix(target, {})
    return n, f.read_text(encoding="utf-8")


def test_fix_idempotent_on_canonical_frontmatter(tmp_path):
    n, _ = _fix_and_reload(tmp_path, GOOD_FRONTMATTER)
    assert n == 0


def test_fix_reorders_canonical_fields(tmp_path):
    fm = GOOD_FRONTMATTER.replace(
        "category: 'Society'\ntags: ['媒體', '科學傳播']\nsubcategory: '媒體與言論'\n",
        "subcategory: '媒體與言論'\ntags: ['媒體', '科學傳播']\ncategory: 'Society'\n",
    )
    n, body = _fix_and_reload(tmp_path, fm)
    assert n >= 1
    # Re-validate: order warning should be gone
    f = _write_article(tmp_path, "")  # no-op to get path
    f.write_text(body, encoding="utf-8")
    target = load_target(f)
    violations = list(frontmatter_format.check(target, {}))
    assert not any("欄位順序錯" in v.message for v in violations), (
        f"reorder did not produce canonical order:\n{body}"
    )


def test_fix_converts_list_mode_tags_to_flow_array(tmp_path):
    fm = GOOD_FRONTMATTER.replace(
        "tags: ['媒體', '科學傳播']\n",
        "tags:\n  - 媒體\n  - 科學傳播\n",
    )
    n, body = _fix_and_reload(tmp_path, fm)
    assert n >= 1
    assert "tags: ['媒體', '科學傳播']" in body, (
        f"flow array conversion failed:\n{body}"
    )


def test_fix_preserves_prettier_wrapped_flow_array(tmp_path):
    """Prettier wraps long flow arrays; we must not touch that style."""
    fm = GOOD_FRONTMATTER.replace(
        "tags: ['媒體', '科學傳播']\n",
        "tags:\n  [\n    '媒體',\n    '科學傳播',\n  ]\n",
    )
    n, body = _fix_and_reload(tmp_path, fm)
    # No fix needed if frontmatter is otherwise canonical and tags is valid flow
    assert "tags:\n  [" in body, f"prettier wrap was destroyed:\n{body}"


def test_fix_quotes_unquoted_scalar_string(tmp_path):
    fm = GOOD_FRONTMATTER.replace("category: 'Society'\n", "category: Society\n")
    n, body = _fix_and_reload(tmp_path, fm)
    assert n >= 1
    assert "category: 'Society'" in body, f"category was not quoted:\n{body}"


def test_fix_unquotes_quoted_date(tmp_path):
    fm = GOOD_FRONTMATTER.replace("date: 2026-05-07\n", "date: '2026-05-07'\n")
    n, body = _fix_and_reload(tmp_path, fm)
    assert n >= 1
    assert "date: 2026-05-07\n" in body, f"date was not unquoted:\n{body}"


def test_fix_unquotes_quoted_boolean(tmp_path):
    fm = GOOD_FRONTMATTER.replace("featured: false\n", "featured: 'false'\n")
    n, body = _fix_and_reload(tmp_path, fm)
    assert n >= 1
    assert "featured: false\n" in body, f"featured was not unquoted:\n{body}"


def test_fix_combined_reorder_and_flow_conversion(tmp_path):
    """The original 5/7 #884 conflict pattern: contributor PR has subcategory
    before tags AND list-mode tags. Our fix must handle both in one pass."""
    fm = GOOD_FRONTMATTER.replace(
        "category: 'Society'\ntags: ['媒體', '科學傳播']\nsubcategory: '媒體與言論'\n",
        "subcategory: '媒體與言論'\ntags:\n  - 媒體\n  - 科學傳播\ncategory: 'Society'\n",
    )
    n, body = _fix_and_reload(tmp_path, fm)
    assert n >= 2
    assert "tags: ['媒體', '科學傳播']" in body, "flow conversion failed"

    f = _write_article(tmp_path, "")
    f.write_text(body, encoding="utf-8")
    target = load_target(f)
    violations = list(frontmatter_format.check(target, {}))
    assert not any("欄位順序錯" in v.message for v in violations)
    assert not any("flow array" in v.message for v in violations)


def test_fix_preserves_trailing_comments(tmp_path):
    """Trailing # design_rationale: blocks must survive reordering."""
    fm = GOOD_FRONTMATTER.replace(
        "category: 'Society'\ntags: ['媒體', '科學傳播']\n",
        "tags: ['媒體', '科學傳播']\ncategory: 'Society'\n",
    ) + "# design_rationale:\n#   why_this_hook: 'test'\n"
    n, body = _fix_and_reload(tmp_path, fm)
    assert n >= 1
    assert "# design_rationale:" in body, f"trailing comment was lost:\n{body}"
    assert "#   why_this_hook: 'test'" in body, f"trailing comment was lost:\n{body}"


def test_fix_reorder_does_not_concat_last_block(tmp_path):
    """Regression: loader strips trailing \\n before closing ---. After
    reorder, original-last block (no \\n) must not concat with next block.
    巧固球 case 2026-05-08: featured/date/readingTime/lastVerified/lastHumanReview
    in scrambled order produced `lastHumanReview: falsereadingTime: 12`."""
    fm = (
        "title: 'Foo'\n"
        "description: 'Bar'\n"
        "category: 'Society'\n"
        "tags: ['x']\n"
        "subcategory: 'sub'\n"
        "author: 'COMPUTEX.md'\n"
        "featured: false\n"
        "date: 2026-03-27\n"
        "readingTime: 12\n"  # unknown key — will be moved to other_blocks
        "lastVerified: 2026-03-27\n"
        "lastHumanReview: false\n"  # was last; will be moved earlier
    )
    n, body = _fix_and_reload(tmp_path, fm)
    assert n >= 1
    assert "lastHumanReview: false\n" in body, (
        f"trailing newline regression — fields concatenated:\n{body}"
    )
    assert "lastHumanReview: falsereadingTime" not in body
    assert "lastHumanReview: falseimage" not in body


def test_fix_quotes_unquoted_flow_array_items(tmp_path):
    """`tags: [foo, bar]` (no quotes) → `tags: ['foo', 'bar']`."""
    fm = GOOD_FRONTMATTER.replace(
        "tags: ['媒體', '科學傳播']\n",
        "tags: [媒體, 科學傳播]\n",
    )
    n, body = _fix_and_reload(tmp_path, fm)
    assert n >= 1
    assert "tags: ['媒體', '科學傳播']" in body, (
        f"unquoted flow tags were not quoted:\n{body}"
    )


def test_fix_preserves_already_quoted_flow_items(tmp_path):
    """If items already quoted, don't double-quote them."""
    n, body = _fix_and_reload(tmp_path, GOOD_FRONTMATTER)
    assert n == 0
    assert "tags: ['媒體', '科學傳播']" in body


def test_fix_handles_mixed_quoted_unquoted_items(tmp_path):
    """Some items quoted, some not — quote the unquoted ones only."""
    fm = GOOD_FRONTMATTER.replace(
        "tags: ['媒體', '科學傳播']\n",
        "tags: ['媒體', 科學傳播]\n",
    )
    n, body = _fix_and_reload(tmp_path, fm)
    assert n >= 1
    assert "tags: ['媒體', '科學傳播']" in body, (
        f"mixed quote fix failed:\n{body}"
    )


def test_fix_converts_double_quoted_scalars_to_single(tmp_path):
    """Legacy double-quoted scalars (`category: "Society"`) → single-quoted."""
    fm = GOOD_FRONTMATTER.replace(
        "title: '泛科學：從科學新聞黑洞到演算法裡的知識工業'\n",
        'title: "泛科學：從科學新聞黑洞到演算法裡的知識工業"\n',
    ).replace(
        "category: 'Society'\n",
        'category: "Society"\n',
    ).replace(
        "tags: ['媒體', '科學傳播']\n",
        'tags: ["媒體", "科學傳播"]\n',
    )
    n, body = _fix_and_reload(tmp_path, fm)
    assert n >= 1
    assert "title: '泛科學：" in body
    assert "category: 'Society'" in body
    assert "tags: ['媒體', '科學傳播']" in body, f"flow item double→single failed:\n{body}"


def test_fix_preserves_double_quoted_with_escape_sequences(tmp_path):
    """If `\\n` or `\\t` escapes are present, leave double-quoted (single can't)."""
    fm = GOOD_FRONTMATTER.replace(
        "description: 'desc'\n",
        'description: "line1\\nline2"\n',
    )
    n, body = _fix_and_reload(tmp_path, fm)
    # description should remain double-quoted because of \n escape
    assert 'description: "line1\\nline2"' in body, (
        f"escape sequence preservation failed:\n{body}"
    )


def test_fix_handles_apostrophe_in_quoted_value(tmp_path):
    """`description: \"I'm here\"` → `description: 'I''m here'` (YAML escape)."""
    fm = GOOD_FRONTMATTER.replace(
        "description: 'desc'\n",
        'description: "I\'m here"\n',
    )
    n, body = _fix_and_reload(tmp_path, fm)
    assert n >= 1
    assert "description: 'I''m here'" in body, (
        f"apostrophe-in-double-quote handling failed:\n{body}"
    )


def test_fix_does_not_introduce_blank_line_before_closing_fence(tmp_path):
    """Regression: after reorder, fm_text ended with \\n which combined with
    hardcoded `\\n---\\n` to produce `\\n\\n---\\n` (blank line inside FM)."""
    fm = (
        "title: '原住民文學'\n"
        "description: 'desc'\n"
        "category: 'Society'\n"
        "tags: ['x']\n"
        "subcategory: '文學'\n"
        "author: 'COMPUTEX.md'\n"
        "featured: false\n"
        "date: 2026-03-24\n"
        "readingTime: 7\n"  # unknown — gets pushed to end after reorder
        "lastVerified: 2026-03-24\n"
        "lastHumanReview: false\n"
    )
    f = _write_article(tmp_path, fm)
    target = load_target(f)
    n = frontmatter_format.fix(target, {})
    assert n >= 1
    body = f.read_text(encoding="utf-8")
    # Must NOT have a blank line before closing fence
    assert "\n\n---\n" not in body, (
        f"blank line before closing fence regression:\n{body}"
    )


def test_fix_handles_empty_tags_list_mode_safely(tmp_path):
    """Edge case: `tags:` followed by nothing (empty value, no items).
    Should NOT explode and should leave the field alone."""
    fm = GOOD_FRONTMATTER.replace(
        "tags: ['媒體', '科學傳播']\n",
        "tags:\n",
    )
    # No items to convert; flow conversion should no-op on this case.
    # (This is technically a HARD violation since tags must be a list,
    # but our flow conversion should be idempotent on empty.)
    n, body = _fix_and_reload(tmp_path, fm)
    # tags: should still be there (don't write `tags: []` since we can't
    # tell if user meant empty or forgot to fill in)
    assert "tags:" in body
