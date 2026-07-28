"""
backends/gemini.py — Google Gemini CLI subprocess backend.

Uses the `gemini` CLI tool (gemini-cli) which authenticates via Google Workspace
subscription (~/.gemini/oauth_creds.json). Provides direct access to Gemini models
without going through OpenRouter — independent quota.

Strengths: large context, strong multilingual (especially ja/ko/es/fr from a Google
training corpus), Google Workspace subscription absorbs cost.

Weaknesses: requires --skip-trust flag for non-interactive use; CLI overhead per call;
quota may hit "exhausted your capacity on this model. Your quota will reset after Xs"
but auto-retries.

Per哲宇 callout 2026-05-12 alongside codex: "用我的 gemini 訂閱處理".
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

from ._base import (
    BackendBadOutput,
    BackendCapabilities,
    BackendRateLimited,
    BackendTimeout,
    BackendUnavailable,
    TranslationBackend,
)


class GeminiBackend(TranslationBackend):
    CAPABILITIES = BackendCapabilities(
        name="gemini",
        provider_kind="gemini-cli",
        model="gemini-2.5-pro",  # default; CLI may select via --model
        cost_kind="subscription",
        typical_latency_s=30,         # gemini CLI is faster than codex per call
        max_context_chars=1_000_000,  # gemini-2.5-pro has 1M context
        prc_refusal_risk_low=True,
        multilingual_strength=0.90,
        notes="Google Workspace subscription via gemini-cli. Strong multilingual + low refusal. "
              "Lower per-call overhead than codex but tighter QPM throttling.",
    )

    DEFAULT_TIMEOUT = 300
    AUTH_FILE = Path.home() / ".gemini" / "oauth_creds.json"

    def __init__(self, model: str = None, **config):
        super().__init__(**config)
        if model:
            self.CAPABILITIES = BackendCapabilities(**{**self.CAPABILITIES.__dict__, "model": model})

    def is_available(self) -> bool:
        if not shutil.which("gemini"):
            return False
        if not self.AUTH_FILE.exists():
            return False
        return True

    def translate(self, system: str, user: str, *, max_tokens: int = 32000, timeout: int = None) -> str:
        timeout = timeout or self.DEFAULT_TIMEOUT
        # gemini CLI doesn't have separate system/user roles — concatenate
        full_prompt = (
            "SYSTEM INSTRUCTIONS (follow strictly, do not echo):\n"
            "================================================================\n"
            f"{system}\n\n"
            "================================================================\n"
            "USER REQUEST:\n"
            f"{user}\n\n"
            "OUTPUT: ONLY the translated markdown content. No preamble, no commentary."
        )

        # TERM=dumb 是舊版 CLI 的選擇；gemini-cli ≥0.41 對 dumb terminal 直接 exit 1
        # （2026-07-18 出生戰役 health-check 病根），改給真實 TERM。
        env = {**os.environ, "TERM": "xterm-256color", "GEMINI_CLI_TRUST_WORKSPACE": "true"}
        cmd = ["gemini", "--skip-trust", "--prompt", full_prompt]
        if self.CAPABILITIES.model and self.CAPABILITIES.model != "default":
            cmd.extend(["--model", self.CAPABILITIES.model])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )
        except subprocess.TimeoutExpired:
            self._record_failure("timeout", f"gemini CLI timed out after {timeout}s")
            raise BackendTimeout(f"gemini CLI timed out after {timeout}s")
        except FileNotFoundError:
            self._record_failure("unavailable", "gemini CLI not installed")
            raise BackendUnavailable("gemini CLI not found in PATH")

        if result.returncode != 0:
            err = (result.stderr or result.stdout)[:500]
            # Quota exhaustion message
            if "exhausted your capacity" in err or "quota" in err.lower():
                self.mark_cool_down(300)
                self._record_failure("rate_limited", err)
                raise BackendRateLimited(err[:200], cool_down_until=self.cool_down_until())
            self._record_failure("bad_output", f"exit {result.returncode}: {err}")
            raise BackendBadOutput(f"gemini exit {result.returncode}: {err}")

        output = _extract_gemini_output(result.stdout)
        if not output or len(output) < 100:
            self._record_failure("bad_output", f"empty/tiny output: {len(output)} chars")
            raise BackendBadOutput(f"gemini produced empty/tiny output ({len(output)} chars)")

        self._record_success()
        return output


# ────────────────── helpers ──────────────────

_GEMINI_NOISE_PATTERNS = (
    re.compile(r"^Warning: 256-color support not detected.*$", re.MULTILINE),
    re.compile(r"^Ripgrep is not available.*$", re.MULTILINE),
    re.compile(r"^Attempt \d+ failed: .*Retrying after \d+ms\.\.\.$", re.MULTILINE),
    re.compile(r"^Loaded cached credentials\.$", re.MULTILINE),
)


def _extract_gemini_output(stdout: str) -> str:
    """Strip gemini CLI noise (color warnings, ripgrep fallback, retry messages)."""
    out = stdout
    for pat in _GEMINI_NOISE_PATTERNS:
        out = pat.sub("", out)
    return out.strip()
