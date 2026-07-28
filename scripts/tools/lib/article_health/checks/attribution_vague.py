"""attribution_vague — 知識庫版「模糊歸屬」檢測。

抓「研究顯示」「專家認為」這類沒有具名主詞、也沒有腳註的權威鋪墊句 ——
讀者無法追溯這句話的來源是誰說的、哪份研究，只能選擇相信或不信。

判準（per 2026-07-16 上游決策 + 校準後收緊，見 calibration report）：
  1. 命中 pattern 後，先看同一段落（至下一個空行為界）內是否有腳註標記
     `[^` —— 有 = 放行（作者已經在段落裡某處交代來源，只是這句話本身
     沒有直接掛腳註，不算模糊歸屬）。
  2. 命中詞緊接在「的」前面（X的研究顯示/指出）或緊接在「的」後面
     （研究顯示的...，名詞化比較句）→ 放行。校準時實測抓到兩個假陽性都
     是「X的研究顯示」結構（X = 具名人物+機構縮寫，全稱機構清單抓不到
     的簡稱如「中研院」「台大」），以及一個「比數據顯示的更複雜」比較句
     誤判 —— 加了這條後兩類都收斂。
  3. 沒被 2 放行的話，看命中處前後 50 字內是否有引號框住的具名主詞（人名/
     機構名）—— 難判就從寬，只要窗口內出現任何引號片語或常見機構全稱後綴
     （大學/研究院/中心/協會/基金會...），就當作已具名，放行。
  4. 都沒有 → WARN：無源權威鋪墊，留判斷或補腳註。

已知取捨：規則 2 用「的」這個純句法信號放行，不驗證「的」前面到底是不是
真的具名實體 —— 代價是像「台灣政治學者的研究顯示」（政治學者是泛稱，不是
具名）這種案例也會被放行漏掉。這是刻意的「難判就從寬」選擇：機器沒有真正
的 NER，規則 2 抓到的假陽性（具名人物被誤判模糊）比它漏掉的假陰性（泛稱
偽裝成有主詞）更傷讀者對這個工具的信任，所以優先降假陽性。

誤殺防護：
  - blockquote（30 秒概覽）不掃 —— 那是摘要框，本來就不會逐句掛腳註。
  - frontmatter 不掃 —— FileTarget.body 本來就已經是去除 frontmatter 後
    的內文，天然排除。

Severity: WARN（留判斷，不是鐵證 —— 「業界普遍認為」可能真的是業界共識，
也可能是作者偷懶，機器分不出來，只能提醒去核對）。

Canonical: docs/editorial/CITATION-GUIDE.md + EDITORIAL.md §引用規範
（模糊歸屬這個具體 pattern 清單目前只在本 plugin 儀器化，canonical 文件
待後續補上對應章節）。
"""

from __future__ import annotations

import re
from typing import Any, Iterator

from ..types import FileTarget, Severity, Violation


CHECK_NAME = "attribution-vague"
DIMENSION = "citation"
DEFAULT_SEVERITY = Severity.WARN
EDITORIAL_REF = "CITATION-GUIDE.md + EDITORIAL.md §引用規範（模糊歸屬，2026-07 新增）"
APPLIES_TO = ["zh-TW"]


_VAGUE_PHRASES = [
    "研究顯示", "研究指出", "專家認為", "業界普遍認為",
    "有觀點指出", "被廣泛認為", "普遍被認為", "數據顯示",
]
_RE_VAGUE = re.compile("|".join(re.escape(p) for p in _VAGUE_PHRASES))

# 引號框住的具名主詞（人名/機構名）—— 難判就從寬，任何引號片語都算數。
_RE_QUOTED_NAME = re.compile(
    "[「『" + '"' + "]" + r"[^」』" + '"' + r"\n]{1,24}[」』" + '"' + "]"
)

# 常見機構/單位後綴 —— 窗口內出現視為已具名，放行。
_RE_INSTITUTION = re.compile(
    r"(?:大學|學院|研究院|研究所|中心|基金會|協會|智庫|機構|實驗室|"
    r"期刊|團隊|政府|部|局|署|公司)"
)

_WINDOW = 50


def _line_at(body: str, pos: int) -> int:
    if pos < 0 or pos > len(body):
        return 1
    return body.count("\n", 0, pos) + 1


def _context(body: str, start: int, end: int, before: int = 20, after: int = 20) -> str:
    body_len = len(body)
    ctx_start = max(0, start - before)
    ctx_end = min(body_len, end + after)
    pre = body[ctx_start:start].replace("\n", "⏎")
    mid = body[start:end].replace("\n", "⏎")
    post = body[end:ctx_end].replace("\n", "⏎")
    leading = "…" if ctx_start > 0 else ""
    trailing = "…" if ctx_end < body_len else ""
    return f"{leading}{pre}《{mid}》{post}{trailing}"


def _paragraph_spans(body: str) -> list[tuple[int, int]]:
    """(start, end) char spans for each blank-line-separated paragraph."""
    spans: list[tuple[int, int]] = []
    start: int | None = None
    last_nonblank_end = 0
    offset = 0
    for line in body.split("\n"):
        line_len = len(line)
        if line.strip():
            if start is None:
                start = offset
            last_nonblank_end = offset + line_len
        else:
            if start is not None:
                spans.append((start, last_nonblank_end))
                start = None
        offset += line_len + 1
    if start is not None:
        spans.append((start, last_nonblank_end))
    return spans


def _find_span(spans: list[tuple[int, int]], pos: int) -> tuple[int, int] | None:
    for s, e in spans:
        if s <= pos <= e:
            return (s, e)
    return None


def check(target: FileTarget, config: dict[str, Any]) -> Iterator[Violation]:
    body = target.body_without_protected()
    spans = _paragraph_spans(body)

    for m in _RE_VAGUE.finditer(body):
        pos = m.start()

        # blockquote 誤殺防護：命中所在行以 `>` 開頭 → 跳過（30 秒概覽摘要框）。
        line_start = body.rfind("\n", 0, pos) + 1
        line_end = body.find("\n", pos)
        if line_end == -1:
            line_end = len(body)
        current_line = body[line_start:line_end]
        if current_line.lstrip().startswith(">"):
            continue

        span = _find_span(spans, pos)
        if span is not None:
            paragraph_text = body[span[0]:span[1]]
            if "[^" in paragraph_text:
                continue  # 同段有腳註 → 放行

        # 直接鄰接的「的」判準（2026-07-16 校準後加入 — 見 calibration report）：
        #   「X的研究顯示/指出」：X 緊接在「的」前面，語法上一定是某個具體
        #     所有格主詞（人名/頭銜/機構，含縮寫如「中研院」「台大」這種
        #     _RE_INSTITUTION 全稱清單抓不到的簡稱）—— 從寬視為已具名，放行。
        #     (校準時抓到「中研院研究員王甫昌的研究指出」「台大地質科學系
        #     宋聖榮教授的研究顯示」兩個假陽性，都是這個結構。)
        #   「研究顯示的...」：phrase 後面直接接「的」代表整個 phrase 被
        #     名詞化成句子的修飾語/比較對象（例如「比數據顯示的更複雜」=
        #     「比...更複雜」的比較句，不是「數據顯示，X」的鋪墊句型）——
        #     不是引用鋪墊用法，放行。
        prev_char = body[pos - 1] if pos > 0 else ""
        next_char = body[m.end()] if m.end() < len(body) else ""
        if prev_char == "的" or next_char == "的":
            continue

        window = body[max(0, pos - _WINDOW):min(len(body), m.end() + _WINDOW)]
        if _RE_QUOTED_NAME.search(window) or _RE_INSTITUTION.search(window):
            continue  # 鄰近有具名主詞/機構 → 放行（從寬判準）

        line_no = _line_at(body, pos)
        ctx = _context(body, m.start(), m.end())
        yield Violation(
            check=CHECK_NAME,
            severity=DEFAULT_SEVERITY,
            message=f"無源權威鋪墊「{m.group(0)}」：{ctx}",
            line=line_no,
            snippet=m.group(0),
            editorial_ref=EDITORIAL_REF,
            fix_suggestion="補腳註 [^n] 標明來源，或加上具名主詞（人名/機構名），否則留判斷是否要保留這句話",
        )
