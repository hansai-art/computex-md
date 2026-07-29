"""slug_format — 檔名就是網址，所以檔名要能當網址看。

母體的檔名慣例是「檔名 = 中文標題」（`黃魚鴞.md` → `/nature/黃魚鴞/`）。中文檔名
在網址列會被 percent-encode，但瀏覽器與搜尋引擎都會還原顯示，讀起來仍然是人話，
所以那個慣例對它成立。

這個物種的主體是 ASCII 專有名詞（廠商名、產品型號、年份），照抄那個慣例會長出
`/editions/COMPUTEX%202027/` 這種東西：既不是可讀的中文，也不是乾淨的 ASCII slug，
兩邊的好處都沒拿到。2026-07-29 出生時第一篇就踩到。

規則
    檔名若是純 ASCII，MUST 是 lowercase-hyphen slug：小寫字母、數字、連字號。
    含 CJK 的檔名不受此限（沿用母體慣例，中文標題本身就是可讀的網址）。

    永遠不准出現：空白、底線、百分號、以及大寫混雜的 ASCII 檔名。

為什麼是 HARD：改檔名等於改網址。內容灌進來之後才發現慣例錯了，代價是全站
redirect 表加一輪；出生階段擋下來只要改一個檔名。
"""

from __future__ import annotations

import re
from typing import Any, Iterator

from ..types import FileTarget, Severity, Violation

CHECK_NAME = "slug-format"
DIMENSION = "structure"
DEFAULT_SEVERITY = Severity.HARD
EDITORIAL_REF = "README §分類（ASCII 檔名一律 lowercase-hyphen）"
APPLIES_TO = ["*"]

_RE_CJK = re.compile(r"[㐀-䶿一-鿿]")
_RE_GOOD_ASCII_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def check(target: FileTarget, config: dict[str, Any]) -> Iterator[Violation]:
    stem = target.path.stem

    # hub 頁（_index.md 之類）由樣板產生，不走文章路由
    if stem.startswith("_"):
        return

    # 含 CJK 的檔名沿用母體慣例：中文標題本身就是可讀的網址
    if _RE_CJK.search(stem):
        if " " in stem:
            yield Violation(
                check=CHECK_NAME,
                severity=Severity.HARD,
                message=f"檔名含空白：「{stem}」。網址會出現 %20。",
                snippet=stem,
                editorial_ref=EDITORIAL_REF,
                fix_suggestion="移除空白，或改用連字號。",
            )
        return

    if _RE_GOOD_ASCII_SLUG.match(stem):
        return

    problems = []
    if " " in stem:
        problems.append("空白（網址會變成 %20）")
    if "_" in stem:
        problems.append("底線（網址慣例用連字號）")
    if stem != stem.lower():
        problems.append("大寫字母")

    yield Violation(
        check=CHECK_NAME,
        severity=Severity.HARD,
        message=(
            f"ASCII 檔名「{stem}」不是 lowercase-hyphen slug"
            + ("：" + "、".join(problems) if problems else "")
            + "。檔名就是網址，改檔名等於改網址。"
        ),
        snippet=stem,
        editorial_ref=EDITORIAL_REF,
        fix_suggestion=(
            f"改成 `{re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', stem.lower())).strip('-')}.md`"
            "，並同步更新譯文的 translatedFrom 與 knowledge/_translations.json。"
        ),
    )
