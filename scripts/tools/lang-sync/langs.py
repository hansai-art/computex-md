"""langs.py — lang-sync 工具鏈的語言清單 SSOT bridge。

病根（2026-07-18 vi/id/pt/hi 出生戰役揭露）：`src/config/languages.ts` 2026-04-14
重構後宣稱「15 個 touchpoint → 2」，但 lang-sync python 工具鏈不在那次重構視野內，
六個工具各自 hardcode `["en", "ja", "ko", "es", "fr"]` —— 正是神經迴路
「新語言出生時感知系統不會自動更新」的 python 層復發。

本模組把 `src/config/languages.mjs`（registry mirror，機器穩定格式）text-parse 成
python 可用的清單。加第 N 個語言 = 改 registry 兩檔，整條 python 工具鏈自動跟上。

Fail-loud selftest（REFLEXES #65：儀器自身要 cross-verify）：parse 結果少於出生
戰役當下已知的語言數（10）即 raise —— registry 格式改了會當場叫，不會靜默回空。
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
_REGISTRY = REPO / "src" / "config" / "languages.mjs"

_ENTRY_RE = re.compile(
    r"code:\s*'(?P<code>[\w-]+)'.*?enabled:\s*(?P<enabled>true|false)",
    re.DOTALL,
)


def _parse():
    text = _REGISTRY.read_text(encoding="utf-8")
    entries = []
    # 逐 entry block 掃（registry 是 array of object literals，順序即權威順序）
    for block in re.split(r"\n\s*\{", text):
        m_code = re.search(r"code:\s*'([\w-]+)'", block)
        m_enabled = re.search(r"enabled:\s*(true|false)", block)
        if m_code and m_enabled:
            entries.append((m_code.group(1), m_enabled.group(1) == "true"))
    # 這條斷言防的是「registry 格式被改壞、parser 靜默讀到空清單」，不是「語言要夠多」。
    # 母體 12 語所以基線寫 10；COMPUTEX.md 起手 zh-TW + en，基線重設為 2。
    # 加語言時把這個數字一起往上調，斷言才繼續有防守力。
    _BASELINE = 2
    if len(entries) < _BASELINE:
        raise RuntimeError(
            f"langs.py selftest FAIL: 只 parse 到 {len(entries)} 個語言"
            f"（基線 ≥ {_BASELINE}）。languages.mjs 格式可能改了，"
            f"修 langs.py 的 parser 而不是靜默沿用舊清單。"
        )
    if entries[0][0] != "zh-TW":
        raise RuntimeError("langs.py selftest FAIL: 第一個 entry 不是 zh-TW default")
    return entries


_ENTRIES = _parse()

#: 所有翻譯目標語言（含 scaffolded / disabled），排除 zh-TW default。
#: 翻譯產線工具（status / bump / backfill / diff-patch / prepare）用這個 ——
#: scaffolded 語言的 knowledge/{lang}/ 一有內容就要被狀態機看見。
ALL_TRANSLATION_LANGS = [code for code, _ in _ENTRIES if code != "zh-TW"]

#: 已啟用（有路由）的翻譯語言。站體層 audit（cross-lang-audit 等）用這個。
ENABLED_TRANSLATION_LANGS = [
    code for code, enabled in _ENTRIES if enabled and code != "zh-TW"
]


if __name__ == "__main__":
    print("ALL_TRANSLATION_LANGS =", ALL_TRANSLATION_LANGS)
    print("ENABLED_TRANSLATION_LANGS =", ENABLED_TRANSLATION_LANGS)
