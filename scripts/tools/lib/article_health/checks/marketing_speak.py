"""marketing_speak — 沒有出處的絕對宣稱，一律擋下。

這是 COMPUTEX.md 對母體 `terminology` plugin 的同位語。母體守的是「用台灣人的話」，
我們額外要守的是「用規格的話，不用行銷的話」——因為這個檔案庫的核心矛盾在這裡：

    參展廠商有商業動機，他們送來的每一段文字天然帶著行銷語氣。
    而 AI 引擎不引用行銷文案。一旦頁面變成廣告牆，GEO 價值歸零，
    廠商就不來了，飛輪反轉。

所以「業界領先」「全球首創」「唯一」這類詞不是品味問題，是專案的存亡問題。
本 plugin 不禁止這些詞——禁止的是**沒有出處的**這些詞。有第三方可查證的來源就放行，
那正是我們希望廠商去做的事。

判準（HARD）
    同一行出現絕對宣稱詞，且該行沒有任何一種佐證：
      - Markdown 連結 `[...](http...)`
      - 裸 URL
      - 腳註標記 `[^n]`
      - 表格列裡含出處欄（該行有 `|` 且有 http）

判準（WARN）
    緩和詞（「業界少見」「相對領先」）不擋，但提醒改成可量化表述。

放行的情況
    - 引號內的原文引述（我們在轉述別人說了什麼，不是自己宣稱）
    - code block / frontmatter（protected_regions 已由 loader 標出）
    - 英文譯本沿用中文版已查證的宣稱時，同樣要求該行帶出處（雙語一致）

Canonical: docs/editorial/TERMINOLOGY.md §Layer 2 規格詞彙 vs 行銷詞彙
"""

from __future__ import annotations

import re
from typing import Any, Iterator

from ..types import FileTarget, Severity, Violation

CHECK_NAME = "marketing-speak"
DIMENSION = "terminology"
DEFAULT_SEVERITY = Severity.HARD
EDITORIAL_REF = "TERMINOLOGY.md §Layer 2 規格詞彙 vs 行銷詞彙"
APPLIES_TO = ["*"]


#: 絕對宣稱。中英並列，因為本站是雙語 corpus，英文譯本一樣要守。
_ABSOLUTE_CLAIMS = [
    # 中文
    "業界領先",
    "業界第一",
    "全球首創",
    "世界首創",
    "全球第一",
    "世界第一",
    "全台第一",
    "唯一一家",
    "市場唯一",
    "最強",
    "最佳選擇",
    "領導品牌",
    "革命性",
    "顛覆性",
    "劃時代",
    "無人能及",
    "完美",
    "無可取代",
    "獨步全球",
    "遙遙領先",
    # 英文
    "world-leading",
    "world's first",
    "industry-leading",
    "industry first",
    "first-ever",
    "best-in-class",
    "unrivaled",
    "unrivalled",
    "unmatched",
    "revolutionary",
    "game-changing",
    "cutting-edge",
    "state-of-the-art",
    "the only",
    "market leader",
]

#: 緩和表述。不擋，但提醒改成可量化的說法。
_HEDGED_CLAIMS = [
    "業界少見",
    "相對領先",
    "數一數二",
    "名列前茅",
    "among the first",
    "one of the leading",
]

_RE_MD_LINK = re.compile(r"\[[^\]]*\]\(\s*https?://")
_RE_BARE_URL = re.compile(r"https?://\S+")
_RE_FOOTNOTE = re.compile(r"\[\^[^\]]+\]")
#: 引號內的原文引述——我們在轉述，不是自己宣稱
_RE_QUOTED = re.compile(r"[「『\"“]([^」』\"”]{0,200})[」』\"”]")


def _has_evidence(line: str) -> bool:
    return bool(
        _RE_MD_LINK.search(line)
        or _RE_BARE_URL.search(line)
        or _RE_FOOTNOTE.search(line)
    )


def _quoted_spans(line: str) -> list[tuple[int, int]]:
    return [m.span() for m in _RE_QUOTED.finditer(line)]


def _inside(pos: int, spans: list[tuple[int, int]]) -> bool:
    return any(a <= pos < b for a, b in spans)


def _find_terms(line: str, terms: list[str]) -> list[tuple[str, int]]:
    """回傳 (詞, 位置)。英文不分大小寫，中文原樣比對。"""
    low = line.lower()
    out: list[tuple[str, int]] = []
    for term in terms:
        needle = term.lower()
        start = 0
        while True:
            idx = low.find(needle, start)
            if idx == -1:
                break
            out.append((term, idx))
            start = idx + len(needle)
    return out


def check(target: FileTarget, config: dict[str, Any]) -> Iterator[Violation]:
    body = target.body
    if not body:
        return

    # loader 已經在 body 前面補了與 frontmatter 等量的空行，所以 body 的行號
    # 就是檔案行號。NEVER 再加 body_pad_lines，那會加兩次。
    for offset, raw in enumerate(body.split("\n")):
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("```"):
            continue

        line_no = offset + 1
        quoted = _quoted_spans(line)

        for term, pos in _find_terms(line, _ABSOLUTE_CLAIMS):
            if _inside(pos, quoted):
                continue  # 引述別人的話，不是我們的宣稱
            if _has_evidence(line):
                continue  # 有出處就放行，這正是我們要廠商做的事
            yield Violation(
                check=CHECK_NAME,
                severity=Severity.HARD,
                message=(
                    f"絕對宣稱「{term}」沒有出處。"
                    f"AI 引擎不引用行銷文案，這類句子會讓整頁失去被引用的價值。"
                ),
                line=line_no,
                snippet=stripped[:100],
                editorial_ref=EDITORIAL_REF,
                fix_suggestion=(
                    "三選一：(1) 同一行補上可查證的來源連結或腳註；"
                    "(2) 改成可量化的中性表述（「2026 年市佔 X%，來源 Y」）；"
                    "(3) 如果是轉述廠商說法，用引號標明是誰說的。"
                ),
            )

        for term, pos in _find_terms(line, _HEDGED_CLAIMS):
            if _inside(pos, quoted) or _has_evidence(line):
                continue
            yield Violation(
                check=CHECK_NAME,
                severity=Severity.WARN,
                message=(
                    f"緩和宣稱「{term}」沒有出處。不擋，但讀者無法驗證的形容詞對 GEO 沒有貢獻。"
                ),
                line=line_no,
                snippet=stripped[:100],
                editorial_ref=EDITORIAL_REF,
                fix_suggestion="改成具體數字，或補來源。",
            )
