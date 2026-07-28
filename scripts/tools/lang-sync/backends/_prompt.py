"""
backends/_prompt.py — Shared translation prompt builder.

Single source of truth for the system + user prompt used across ALL translation
backends (OpenRouter / Codex / Gemini / Ollama / future Anthropic SDK).

Currently re-exports from `openrouter-translate.py` for back-compat during the
2026-05-12 backend abstraction refactor. Once all production paths use this
module, the prompt can be moved here as canonical and openrouter-translate.py
can import back from us.

Per哲宇 callout 「儘可能模組化 抽象化」— prompt logic is single-source-of-truth.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Re-export from openrouter-translate.py (current canonical home).
# This module uses a hyphen in filename so we need importlib.
_LANG_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_LANG_DIR))

from importlib import import_module as _import_module

_or = _import_module("openrouter-translate")

build_translation_prompt = _or.build_translation_prompt
extract_zh_frontmatter_fields = _or.extract_zh_frontmatter_fields

# Convenience: lang code → display name (used in prompts).
LANG_NAMES = _or.LANG_NAMES


__all__ = [
    "build_translation_prompt",
    "extract_zh_frontmatter_fields",
    "LANG_NAMES",
]
