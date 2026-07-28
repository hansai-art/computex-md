"""ai_residue — 抓「作者用了 AI 沒校對」的鐵證級殘留物。

不是風格判斷（那是 prose_health 的地盤），是可驗證的機械殘留物：
  (a) URL 追蹤參數殘留 — utm_source=chatgpt.com/openai/copilot.com、
      referrer=grok.com。讀者從 AI 工具分享連結貼過來，忘記清 query string。
  (b) 引用佔位殘碼 — `turn0search1` / `citeturn3` 這類瀏覽工具內部
      citation token，以及 Unicode 私有使用區字元 (U+E000–F8FF，部分 AI
      工具用來標記 tool-call 邊界，肉眼不可見但會被貼進正文)。
  (c) 對話殘留句 — 「以下是修改後的版本」「希望這對你有幫助」等 AI 助理
      的前後綴，作者複製貼上時漏刪。

Severity: HARD（鐵證級 — 不是判斷題，抓到就是抓到，不需要人工複核語意）。
Report only — 沒有 --fix。這些殘留物的正確修法是「刪掉」，但刪的位置/
上下文因案例而異，機器貿然刪字有破壞文章語意的風險，留給人工看 line+context
自己動手。

排除 code fence（```...```）：程式碼範例裡出現 utm_source 字串（教學文
示範網址格式）不算殘留，但刻意「不」排除 inline code / link-url — 追蹤參數
最常見的藏身處正是 markdown 連結網址本身，若比照 cjk_punct 那樣連
link-url 都遮罩，會直接漏掉最大宗的 (a) 案例。

Canonical: speak-human-tw patterns #37 / #30（MIT, Raymond Hou）+
docs/editorial/EDITORIAL.md。
"""

from __future__ import annotations

import re
from typing import Any, Iterator

from ..types import FileTarget, Severity, Violation


CHECK_NAME = "ai-residue"
DIMENSION = "factcheck"
DEFAULT_SEVERITY = Severity.HARD
EDITORIAL_REF = "speak-human-tw patterns #37 / #30（MIT, Raymond Hou）+ EDITORIAL.md"
APPLIES_TO = ["*"]


# (a) URL 追蹤參數殘留 — AI 工具分享連結的 utm/referrer 指紋。
_RE_URL_RESIDUE = re.compile(
    r"utm_source=(?:chatgpt\.com|openai|copilot\.com)|referrer=grok\.com",
    re.IGNORECASE,
)

# (b) 引用佔位殘碼 — 瀏覽工具內部 citation token（`turn0search1` /
# `citeturn3` / `citeturn0search3` 系列）。用 \d+ 而非單一 \d 是為了涵蓋
# 多位數索引（turn10search23 這類長文常見的高索引號），比題目給的字面
# regex 稍微放寬比對範圍，見校準報告。`(?:cite)?turn\d+search\d+` 排在
# `citeturn\d+` 前面，讓「citeturn0search3」整個 token 一次比對到，不會
# 被拆成「citeturn0」+ 殘留未比對的「search3」。
_RE_CITE_PLACEHOLDER = re.compile(r"(?:cite)?turn\d+search\d+|citeturn\d+")

# (b) Unicode 私有使用區字元 (Private Use Area) U+E000-U+F8FF.
# 用 chr(0x...) 組字元類別而不是把實際字元直接嵌進原始碼 -- 這個範圍的字元
# 本身不可見/不可渲染，直接貼進 .py 檔案容易被編輯器/git diff 靜默吃掉或
# 顯示錯亂，chr() 讓原始碼本身保持純 ASCII 可讀。
_PUA_RANGE_LOW, _PUA_RANGE_HIGH = chr(0xE000), chr(0xF8FF)
_RE_PUA_CHAR = re.compile(f"[{_PUA_RANGE_LOW}-{_PUA_RANGE_HIGH}]")

# (c) 對話殘留句 — AI 助理常見的前後綴，作者複製貼上時漏刪。
_DIALOGUE_RESIDUE_PHRASES = [
    "以下是修改後的版本",
    "希望這對你有幫助",
    "以下是清理後的版本",
]
_RE_DIALOGUE_RESIDUE = re.compile(
    "|".join(re.escape(p) for p in _DIALOGUE_RESIDUE_PHRASES)
)


def _body_excluding_fenced_code(target: FileTarget) -> str:
    """Body with ONLY fenced-code regions blanked (not inline-code /
    link-url / html-tag) — see module docstring for why link-url must
    stay visible for this check."""
    body = target.body
    fenced = [
        (start, end)
        for start, end, kind in target.protected_regions
        if kind == "fenced-code"
    ]
    if not fenced:
        return body
    chars = list(body)
    for start, end in fenced:
        for i in range(start, min(end, len(chars))):
            chars[i] = " "
    return "".join(chars)


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


def check(target: FileTarget, config: dict[str, Any]) -> Iterator[Violation]:
    body = _body_excluding_fenced_code(target)

    for m in _RE_URL_RESIDUE.finditer(body):
        line_no = _line_at(body, m.start())
        ctx = _context(body, m.start(), m.end(), before=30, after=30)
        yield Violation(
            check=CHECK_NAME,
            severity=DEFAULT_SEVERITY,
            message=f"AI 工具 URL 追蹤參數殘留：{ctx}",
            line=line_no,
            snippet=m.group(0)[:80],
            editorial_ref=EDITORIAL_REF,
            fix_suggestion="移除 URL 中的 utm_source/referrer 追蹤參數（AI 工具分享連結的指紋）",
        )

    for m in _RE_CITE_PLACEHOLDER.finditer(body):
        line_no = _line_at(body, m.start())
        ctx = _context(body, m.start(), m.end())
        yield Violation(
            check=CHECK_NAME,
            severity=DEFAULT_SEVERITY,
            message=f"AI 引用佔位殘碼殘留：{ctx}",
            line=line_no,
            snippet=m.group(0)[:40],
            editorial_ref=EDITORIAL_REF,
            fix_suggestion="刪除殘留的 citation token，改成正式腳註 [^n] 或直接移除",
        )

    for m in _RE_PUA_CHAR.finditer(body):
        line_no = _line_at(body, m.start())
        ctx = _context(body, m.start(), m.end())
        yield Violation(
            check=CHECK_NAME,
            severity=DEFAULT_SEVERITY,
            message=f"Unicode 私有使用區字元殘留 (U+{ord(m.group(0)):04X})：{ctx}",
            line=line_no,
            snippet=f"U+{ord(m.group(0)):04X}",
            editorial_ref=EDITORIAL_REF,
            fix_suggestion="移除不可見/異常字元（常見於 AI 工具內部 tool-call 標記外洩）",
        )

    for m in _RE_DIALOGUE_RESIDUE.finditer(body):
        line_no = _line_at(body, m.start())
        ctx = _context(body, m.start(), m.end(), before=15, after=15)
        yield Violation(
            check=CHECK_NAME,
            severity=DEFAULT_SEVERITY,
            message=f"AI 對話殘留句「{m.group(0)}」：{ctx}",
            line=line_no,
            snippet=m.group(0),
            editorial_ref=EDITORIAL_REF,
            fix_suggestion="刪除 AI 助理對話式前後綴，只留正文本身",
        )
