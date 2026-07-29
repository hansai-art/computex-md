"""minimal frontmatter parser 的測試 —— **強制走 stdlib 路徑**。

為什麼要一支專門的檔案：`_parse_frontmatter_minimal` 第一件事是 `import yaml`，
有 PyYAML 就走 fast path。開發機的 venv 裝了 PyYAML（terminology-yaml-audit 需要），
而 `article-health.py` CLI 是純 stdlib 跑的 —— 於是：

    測試環境走 PyYAML → 全綠
    CI gate 走 minimal parser → hard fail

2026-07-29 就是這樣被咬的。Prettier 把長的 tags 折成多行 flow array
（`tags:` 換行後接 `  [` … `  ]`），minimal parser 讀不懂回傳空字串，
frontmatter-format 判定「tags 不是陣列」直接擋 push。而 pytest 一路綠燈。

所以這裡的每一支都 monkeypatch 掉 yaml，逼 parser 走生產環境那條路。
測試環境必須跟生產環境走同一條路，否則測試在測別的東西。
"""

import builtins
from pathlib import Path

import pytest

from lib.article_health.loader import load_target


@pytest.fixture
def no_yaml(monkeypatch):
    """讓 `import yaml` 失敗，逼 loader 走 minimal parser（等同 CLI 的環境）。"""
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "yaml":
            raise ImportError("forced: exercise the stdlib path")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)


def _load(tmp_path: Path, frontmatter: str):
    f = tmp_path / "test.md"
    f.write_text(f"---\n{frontmatter}---\n\n內文。\n", encoding="utf-8")
    return load_target(f).frontmatter


TAGS = ["COMPUTEX", "COMPUTEX 2027", "台北國際電腦展", "TAITRA"]


def test_single_line_flow_array(tmp_path, no_yaml):
    fm = "title: 't'\ntags: ['COMPUTEX', 'TAITRA']\n"
    assert _load(tmp_path, fm)["tags"] == ["COMPUTEX", "TAITRA"]


def test_block_sequence(tmp_path, no_yaml):
    fm = "title: 't'\ntags:\n  - COMPUTEX\n  - 'COMPUTEX 2027'\n"
    assert _load(tmp_path, fm)["tags"] == ["COMPUTEX", "COMPUTEX 2027"]


def test_prettier_wrapped_flow_array(tmp_path, no_yaml):
    """Prettier 對長 tags 的實際輸出形狀。這一支就是 2026-07-29 咬人的那個。"""
    body = ",\n".join(f"    '{t}'" for t in TAGS)
    fm = f"title: 't'\ntags:\n  [\n{body},\n  ]\nauthor: 'X'\n"
    parsed = _load(tmp_path, fm)
    assert parsed["tags"] == TAGS
    assert parsed["author"] == "X", "flow array 收尾後要能繼續讀後面的欄位"


def test_wrapped_flow_array_of_one(tmp_path, no_yaml):
    fm = "title: 't'\ntags:\n  ['COMPUTEX']\nauthor: 'X'\n"
    parsed = _load(tmp_path, fm)
    assert parsed["tags"] == ["COMPUTEX"]
    assert parsed["author"] == "X"


def test_empty_wrapped_flow_array(tmp_path, no_yaml):
    fm = "title: 't'\ntags: []\nauthor: 'X'\n"
    parsed = _load(tmp_path, fm)
    assert parsed["tags"] == []
    assert parsed["author"] == "X"


def test_nested_mapping_still_works(tmp_path, no_yaml):
    """flow array 的分支不能吃掉巢狀 mapping 的分支。"""
    fm = "title: 't'\nrationale:\n  why_this_hook: '因為 A'\n  whats_excluded: '略過 B'\n"
    parsed = _load(tmp_path, fm)
    assert parsed["rationale"]["why_this_hook"] == "因為 A"
    assert parsed["rationale"]["whats_excluded"] == "略過 B"


def test_scalar_tags_stays_scalar(tmp_path, no_yaml):
    """放寬的是陣列的寫法，不是「字串也算陣列」。"""
    parsed = _load(tmp_path, "title: 't'\ntags: 'COMPUTEX'\n")
    assert parsed["tags"] == "COMPUTEX"


def test_the_real_corpus_parses_under_stdlib(no_yaml):
    """實際 knowledge/ 全掃：CLI 用哪條路，這裡就驗哪條路。

    只驗到 tags 這一層就夠了 —— 它是 frontmatter-format 唯一會 hard fail 的
    結構欄位，也是 Prettier 唯一會折行的欄位。
    """
    repo = Path(__file__).resolve().parents[2]
    bad = []
    for md in (repo / "knowledge").rglob("*.md"):
        if md.name.startswith("_"):
            continue
        tags = load_target(md).frontmatter.get("tags")
        if tags is not None and not isinstance(tags, list):
            bad.append((md.relative_to(repo).as_posix(), repr(tags)))
    assert bad == [], f"這些檔案在純 stdlib 環境下 tags 讀不成陣列：{bad}"


def test_the_fixture_actually_bites(tmp_path, no_yaml):
    """證明 no_yaml 真的把 fast path 關掉了，不是測試自我感覺良好。

    區辨點：PyYAML 會把 `date: 2026-07-29` 解成 datetime.date，
    minimal parser 解成字串。讀到字串 = 確實走了 minimal parser。
    """
    parsed = _load(tmp_path, "title: 't'\ndate: 2026-07-29\n")
    assert parsed["date"] == "2026-07-29"
    assert isinstance(parsed["date"], str)
