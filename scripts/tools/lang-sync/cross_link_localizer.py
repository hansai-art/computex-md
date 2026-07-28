#!/usr/bin/env python3
"""cross_link_localizer.py — 站內連結在地化的共用核心（純函式庫，無 CLI）。

背景：reports/cross-link-localization-2026-07-27.md。抽出自
`localize-cross-links.py`（存量批次修復工具），供兩邊共用同一份判準：

  1. `localize-cross-links.py` —— 批次修復既有譯文（CLI，見該檔）
  2. `translate.py` / `structured-translate.py` / `patch-translate.py` —— 送模型
     「之前」先把 body 裡的站內連結改好，讓「URL 原樣保留」這句 prompt 指示對
     站內連結也變成對的（見 `localize_body()`，三個引擎在送模型前呼叫它）

判準（保守，寧可不動也不要製造新 404）跟 localize-cross-links.py 檔頭同一份，
不重複列——這裡只留函式，語意變更兩邊都要跟著動，改一處。

Public API：
  - `load_index(knowledge_root=None)` → LocalizerIndex（快取，供長跑的翻譯行程重用）
  - `localize_url(url, lang, index)` → (new_url_or_None, status)
  - `localize_body(text, lang, index)` → (改寫後文字, 改了幾個)
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[3]
KNOWLEDGE = REPO / "knowledge"
TRANSLATIONS_JSON = KNOWLEDGE / "_translations.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from langs import ALL_TRANSLATION_LANGS  # noqa: E402

LANGS = set(ALL_TRANSLATION_LANGS)

# 沒有 per-article 路由的分類（astro CATEGORY_MAPPING 沒收這個 key，
# `/resources/{slug}/` 沒有任何 route file 會 serve）。改寫了格式也還是 404。
EXCLUDED_CATEGORIES = {"resources"}

# CJK 判斷：Unified Ideographs + Extension A + Compatibility Ideographs，
# 涵蓋絕大多數中文 slug（繁中檔名不太會落在更冷門的 Extension B 以後）。
_CJK_RANGES = [
    (0x4E00, 0x9FFF),
    (0x3400, 0x4DBF),
    (0xF900, 0xFAFF),
]

LINK_RE = re.compile(r"\[([^\]]*)\]\((/[^)\s]+)\)")
_URL_SPLIT_RE = re.compile(r"^(/[^#?]*)([#?].*)?$")


def has_cjk(s: str) -> bool:
    return any(any(lo <= ord(ch) <= hi for lo, hi in _CJK_RANGES) for ch in s)


def build_category_map(knowledge_root: Path = KNOWLEDGE) -> dict[str, str]:
    """{分類小寫: 分類原樣} — 只收真的 zh 內容分類（排除語言目錄 / resources / _ 開頭）。"""
    cat_map: dict[str, str] = {}
    for entry in sorted(knowledge_root.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("_") or entry.name.startswith(".") or entry.name in LANGS or entry.name in EXCLUDED_CATEGORIES:
            continue
        cat_map[entry.name.lower()] = entry.name
    return cat_map


def build_indexes(translations: dict) -> tuple[dict[str, dict[str, str]], dict[str, set[str]]]:
    """回傳 (zh_to_lang_slug, lang_slug_set)。

    zh_to_lang_slug: "Category/中文slug.md" -> {lang: "category小寫/slug"}
    lang_slug_set:   lang -> {"category小寫/slug", ...}（該語言真的存在的譯文）
    """
    zh_to_lang_slug: dict[str, dict[str, str]] = {}
    lang_slug_set: dict[str, set[str]] = {lang: set() for lang in LANGS}

    for key, zh_val in translations.items():
        if "/" not in key:
            continue
        lang, rest = key.split("/", 1)
        if lang not in LANGS or not rest.endswith(".md"):
            continue
        rest_noext = rest[: -len(".md")]
        if "/" not in rest_noext:
            continue
        cat, slug = rest_noext.split("/", 1)
        cat_lower = cat.lower()
        if cat_lower in EXCLUDED_CATEGORIES:
            continue
        lang_target = f"{cat_lower}/{slug}"
        zh_to_lang_slug.setdefault(zh_val, {})[lang] = lang_target
        lang_slug_set[lang].add(lang_target)

    return zh_to_lang_slug, lang_slug_set


def split_url(url: str) -> tuple[str, str, bool]:
    """url -> (path 不含尾斜線, suffix 含 #/?, 原本有沒有尾斜線)。"""
    m = _URL_SPLIT_RE.match(url)
    if not m:
        return url, "", False
    path = m.group(1)
    suffix = m.group(2) or ""
    had_slash = len(path) > 1 and path.endswith("/")
    if had_slash:
        path = path[:-1]
    return path, suffix, had_slash


@dataclass
class LocalizerIndex:
    cat_map: dict[str, str]
    zh_to_lang_slug: dict[str, dict[str, str]]
    lang_slug_set: dict[str, set[str]]


_CACHE: LocalizerIndex | None = None


def load_index(knowledge_root: Path = KNOWLEDGE, *, force_reload: bool = False) -> LocalizerIndex:
    """載入 + 快取索引（供長跑行程如翻譯引擎重用，不必每篇都重讀 _translations.json）。

    `force_reload=True` 給測試 / 長駐行程在 _translations.json 可能中途更新時用
    （例如 babel-dispatch 一次跑很多語言，翻譯過程中其他 worker 可能新增譯文）。
    """
    global _CACHE
    if _CACHE is not None and not force_reload:
        return _CACHE
    translations_path = knowledge_root / "_translations.json"
    translations = json.loads(translations_path.read_text(encoding="utf-8"))
    cat_map = build_category_map(knowledge_root)
    zh_to_lang_slug, lang_slug_set = build_indexes(translations)
    _CACHE = LocalizerIndex(cat_map, zh_to_lang_slug, lang_slug_set)
    return _CACHE


def localize_url(url: str, lang: str, index: LocalizerIndex) -> tuple[str | None, str]:
    """回傳 (new_url_or_None, status)。

    status ∈ {"rewritten", "no-translation", "already-correct", "skip"}
      rewritten        — 改寫了，new_url 非 None
      no-translation   — 查無對應譯文，完全不動（可能之後批次補上）
      already-correct  — 格式本來就對，沒事做
      skip             — 不是文章連結（外部 / 圖片資產 / 靜態頁 / 未知分類）
    """
    if url.startswith("http") or url.startswith("//"):
        return None, "skip"

    path, suffix, had_slash = split_url(url)
    segs = [s for s in path.strip("/").split("/") if s]
    if not segs:
        return None, "skip"

    had_lang_prefix = segs[0] in LANGS
    rest = segs[1:] if had_lang_prefix else segs
    if len(rest) != 2:
        return None, "skip"

    cat_raw, slug_raw = rest
    cat_lower = cat_raw.lower()
    if cat_lower not in index.cat_map:
        return None, "skip"

    slug = unquote(slug_raw)

    def rebuild(lang_cat_slug: str) -> str:
        new_path = f"/{lang}/{lang_cat_slug}"
        if had_slash:
            new_path += "/"
        return new_path + suffix

    # 1) 優先查 zh_path 反查表 —— 不論 slug 是不是中文，zh 正本檔名本身就可能是拉丁字
    #    （如 `People/Hello-Nico.md` 譯文 slug 卻是 `hello-nico-band`）。這條路徑最準：
    #    直接對到「同一篇文章」的譯文，不管原連結有沒有語言前綴、前綴對不對、分類大
    #    小寫對不對，一律用反查結果重建。
    zh_path = f"{index.cat_map[cat_lower]}/{slug}.md"
    lang_map = index.zh_to_lang_slug.get(zh_path)
    if lang_map and lang in lang_map:
        new_url = rebuild(lang_map[lang])
        return (None, "already-correct") if new_url == url else (new_url, "rewritten")

    # 2) zh 反查沒中 —— 若 slug 本身沒有中文字，它可能「本來就是」目標語言自己的
    #    slug，只是缺前綴、前綴指錯語言、或分類大小寫不對（4,024 桶）。直接查該語言
    #    是否存在這個 slug 再決定要不要動。
    if not has_cjk(slug):
        candidate = f"{cat_lower}/{slug}"
        if candidate in index.lang_slug_set.get(lang, set()):
            new_url = rebuild(candidate)
            return (None, "already-correct") if new_url == url else (new_url, "rewritten")

    return None, "no-translation"


def localize_body(text: str, lang: str, index: LocalizerIndex | None = None) -> tuple[str, int]:
    """把 `text` 裡所有 `[文字](/path)` 站內連結改成 `lang` 的譯文網址（能改才改，
    查無對應保守不動）。回傳 (改寫後文字, 改了幾個)。

    給翻譯引擎在送模型「之前」呼叫（見 translate.py / structured-translate.py /
    patch-translate.py 各自的注入點）—— 模型看到的 URL 已經是目標語言的，
    「URL 原樣保留」的指示對站內連結也變成對的，防新增同一種 bug。

    `lang` 不在 LANGS（例如呼叫端傳了 zh-TW 或拼錯）→ 直接原樣回傳，不丟例外
    （翻譯引擎的呼叫路徑不該因為這個小工具掛掉整個翻譯流程）。
    """
    if lang not in LANGS:
        return text, 0
    idx = index if index is not None else load_index()
    count = 0

    def _sub(m: re.Match) -> str:
        nonlocal count
        title, url = m.group(1), m.group(2)
        new_url, status = localize_url(url, lang, idx)
        if status == "rewritten" and new_url:
            count += 1
            return f"[{title}]({new_url})"
        return m.group(0)

    new_text = LINK_RE.sub(_sub, text)
    return new_text, count
