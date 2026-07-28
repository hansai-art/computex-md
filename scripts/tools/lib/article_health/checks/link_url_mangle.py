"""link-url-mangle — catch prettier-mangled & at-risk image-caption link URLs.

Two patterns, both rooted in one prettier behaviour:

  HARD — a markdown link destination contains a literal `*` (e.g.
         `](https://commons.wikimedia.org/wiki/File:…立柱*2025-12-02.jpg)`).
         `*` is never valid in a real URL (it would be `%2A`); its presence
         means prettier rewrote an emphasis `_` into `*`. The link is broken
         (404). Restore the `_` AND de-link the caption (see WARN below).

  WARN — a markdown link to a percent-encoded (CJK) Wikimedia Commons URL whose
         filename ends in `_<digits>` (e.g. `_05.jpg`, `_2025-12-02.jpg`,
         `_13.jpg`) sits INSIDE an italic caption line (`_…_`). This has not
         mangled yet but WILL on the next `prettier --write`: prettier pairs
         the URL's trailing `_NN` with the caption's closing `_` italic
         delimiter and flips the span to `*`. Pure-ASCII Commons URLs are safe
         (CommonMark intraword-underscore rule); only percent-encoded CJK
         filenames trigger it. Mitigation: move the clickable link OUT of the
         `_…_` caption — keep plain-text attribution in the caption, put the
         `[link](url)` in the article's `## 圖片來源` section (not italic, so
         prettier leaves it alone). `<…>` angle-bracket wrapping does NOT help
         inside italic.

Trigger: 2026-06-21 cicada-media EVOLVE — a hero caption's Commons URL
(`…翠池_汪大智_05.jpg`) got silently mangled to `*05.jpg` by pre-commit
prettier; a later audit found 13 already-broken files (科技園區發展 /
houtong-cat-village / 沈伯洋 across langs) plus ~49 at-risk. The breakage is
silent (build green, link 404 only on click). LESSONS-INBOX pattern
`prettier-cjk-url-italic-mangle`.
"""

from __future__ import annotations

import re
from typing import Any, Iterator

from ..types import FileTarget, Severity, Violation

CHECK_NAME = "link-url-mangle"
DIMENSION = "structure"
DEFAULT_SEVERITY = Severity.HARD
EDITORIAL_REF = "EDITORIAL §媒體編織（caption 不放 CJK-Commons-URL 連結，連結走 §圖片來源）+ REWRITE Step 4.3.6"
APPLIES_TO = ["*"]

# HARD: a markdown image link whose destination contains a literal `*` (mangled).
# `\S*\*\S*` lets the URL include balanced internal parens (houtong `(cropped*2022).jpg`).
_MANGLED = re.compile(r"\]\(<?(https?://\S*\*\S*?)>?\)")

# WARN at-risk: percent-encoded Commons URL ending in `_<digits>` before the
# image extension, sitting in an italic caption line.
_ATRISK_URL = re.compile(
    r"\]\(<?https?://commons\.wikimedia\.org[^\s)]*%[0-9A-Fa-f]{2}"
    r"[^\s)]*_[0-9][0-9-]*\.(?:jpg|JPG|jpeg|png|webp)>?\)"
)


def _is_italic_caption(line: str) -> bool:
    s = line.strip()
    # Caption convention: a paragraph wrapped in single underscores `_…_`.
    return len(s) >= 2 and s.startswith("_") and (s.endswith("_") or s.endswith("*") or s.endswith("\\_"))


def check(target: FileTarget, config: dict[str, Any]) -> Iterator[Violation]:
    text = target.text
    if not text:
        return

    for line_no, line in enumerate(text.split("\n"), start=1):
        # HARD — already mangled (`*` in a link URL).
        # Scope to the actual bug mechanism: a literal `*` in a link URL is a
        # prettier-mangle only when the link sits in an italic caption, OR the URL is a
        # wiki(m|p)edia URL (Commons filenames never contain a literal `*` — it'd be
        # %2A). A `*` in a non-wiki footnote query string (1111.com.tw `sa0=50000*`,
        # ly.gov.tw `NO%3DE01961*`) is legitimate — don't false-positive (2026-06-21).
        m = _MANGLED.search(line)
        if m and (
            _is_italic_caption(line)
            or "wikimedia.org" in m.group(1)
            or "wikipedia.org" in m.group(1)
        ):
            yield Violation(
                check=CHECK_NAME,
                severity=Severity.HARD,
                message=(
                    "連結 URL 含 `*`（prettier 把斜體 caption 裡的 `_NN` 弄壞成 `*NN`，連結已 404）："
                    f"…{m.group(1)[-48:]}。修：URL 的 `*` 還原成 `_`，並把連結移出 `_斜體_` caption（連結走 §圖片來源）。"
                ),
                line=line_no,
                snippet=line.strip()[:90],
                editorial_ref=EDITORIAL_REF,
                fix_suggestion=(
                    "caption 留純文字 attribution（`Photo: X / Wikimedia Commons, CC BY-SA 4.0`），"
                    "可點連結放文末 `## 圖片來源`（非斜體，prettier 不動）。`<…>` 在斜體內無效。"
                ),
            )
            continue

        # WARN — at-risk: CJK Commons URL with trailing `_NN` inside an italic caption.
        if _is_italic_caption(line) and _ATRISK_URL.search(line):
            yield Violation(
                check=CHECK_NAME,
                severity=Severity.WARN,
                message=(
                    "斜體 caption 內含 percent-encoded CJK Commons URL 的 `_NN.jpg`，"
                    "下次 prettier 會弄壞成 `*NN`（連結 404）。建議現在就把連結移出 caption。"
                ),
                line=line_no,
                snippet=line.strip()[:90],
                editorial_ref=EDITORIAL_REF,
                fix_suggestion=(
                    "把 `[…](commons-url)` 移到 `## 圖片來源`，caption 只留純文字授權標示。"
                ),
            )
