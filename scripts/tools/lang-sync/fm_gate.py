"""fm_gate — frontmatter 完整性閘（寫檔前，壞的不落盤）。

translate.py（canonical orchestrator）2026-07-10 P0-3 已內建同款閘；本模組
把它抽成共用件給 legacy wrapper（openrouter-translate / ollama-translate /
codex-translate）用——2026-07-18 撇號批次修復時發現三個 legacy 寫檔路徑
全裸寫，是 107 檔 YAML 病灶（fr 99）持續新生的產出端缺口。

用法：
    from fm_gate import frontmatter_ok
    ok, reason = frontmatter_ok(result)
    if not ok:
        return False, f"{reason} — not saved"
"""
from __future__ import annotations

import yaml


def frontmatter_ok(text: str) -> tuple[bool, str]:
    if not text.startswith("---"):
        return False, "frontmatter missing opening fence"
    fm_end = text.find("\n---", 3)
    if fm_end == -1:
        return False, "frontmatter missing closing fence"
    try:
        fm = yaml.safe_load(text[3:fm_end])
    except yaml.YAMLError as e:
        return False, f"frontmatter YAML broken: {str(e).splitlines()[0][:80]}"
    if not isinstance(fm, dict) or "title" not in fm:
        return False, "frontmatter not a mapping with title"
    return True, "ok"
