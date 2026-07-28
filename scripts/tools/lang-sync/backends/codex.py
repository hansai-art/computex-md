"""
backends/codex.py — Codex CLI subprocess backend (gpt-5.5 via OpenAI subscription).

Use case: when OpenRouter free-tier is exhausted (Z2.1 rate-budget burn) AND Sonnet
sub-agent is disabled. Bypasses OpenRouter entirely by calling `codex exec` which
authenticates via ~/.codex/auth.json against the user's personal OpenAI subscription.

Cost profile: subscription-fixed (no per-token billing in user's tier), but
high per-call overhead (~10K tokens for session bootstrap before actual translation).
Latency ~200-260s per depth article.

Maturity: introduced 2026-05-12 admiring-montalcini-post-finale session when OpenRouter
全 free-tier rate-limited + Hy3 turned paid. 12 P0 missing articles × 5 langs needed
ship → codex pivot worked first try.

Per哲宇 sovereignty preservation lens: OpenAI is Western provider, no PRC content policy.
For sovereignty-sensitive Taiwan content (228 / 戒嚴 / 兩岸) this is safe path.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from ._base import (
    BackendBadOutput,
    BackendCapabilities,
    BackendTimeout,
    BackendUnavailable,
    TranslationBackend,
)


class CodexBackend(TranslationBackend):
    CAPABILITIES = BackendCapabilities(
        name="codex",
        provider_kind="codex-cli",
        model="gpt-5.5",
        cost_kind="subscription",
        typical_latency_s=240,
        max_context_chars=300_000,    # gpt-5.5 has large context, but Codex session has overhead
        prc_refusal_risk_low=True,
        multilingual_strength=0.95,
        notes="OpenAI personal subscription via codex CLI. High quality + low refusal risk. "
              "~10K token overhead per invocation (session bootstrap).",
    )

    DEFAULT_TIMEOUT = int(os.environ.get("CODEX_TIMEOUT", "600"))  # 2026-07-18 hi 天城文大檔 600s 不夠，env 覆蓋（SQUEEZE per-lang timeout 倍率的最小實作）
    AUTH_FILE = Path.home() / ".codex" / "auth.json"

    def is_available(self) -> bool:
        if not shutil.which("codex"):
            return False
        if not self.AUTH_FILE.exists():
            return False
        return True

    def translate(self, system: str, user: str, *, max_tokens: int = 32000, timeout: int = None) -> str:
        timeout = timeout or self.DEFAULT_TIMEOUT
        full_prompt = (
            "System instructions (follow strictly):\n"
            "================================================================\n"
            f"{system}\n\n"
            "================================================================\n"
            "User request:\n"
            f"{user}"
        )

        try:
            result = subprocess.run(
                ["codex", "exec", "--skip-git-repo-check"],
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, "TERM": "dumb"},
            )
        except subprocess.TimeoutExpired:
            self._record_failure("timeout", f"codex exec timed out after {timeout}s")
            raise BackendTimeout(f"codex exec timed out after {timeout}s")
        except FileNotFoundError:
            self._record_failure("unavailable", "codex CLI not found in PATH")
            raise BackendUnavailable("codex CLI not installed")

        if result.returncode != 0:
            err_text = (result.stderr or result.stdout)[:500]
            self._record_failure("bad_output", f"exit {result.returncode}: {err_text}")
            raise BackendBadOutput(f"codex exec exit {result.returncode}: {err_text}")

        output = _extract_codex_output(result.stdout)
        if not output or len(output) < 100:
            self._record_failure("bad_output", f"empty/tiny output: {len(output)} chars")
            raise BackendBadOutput(f"codex produced empty/tiny output ({len(output)} chars)")

        self._record_success()
        return output


# ────────────────── helpers ──────────────────

def _extract_codex_output(stdout: str) -> str:
    """Strip codex exec wrapper (preamble + 'codex' marker + 'tokens used' suffix).

    Codex output format:
        OpenAI Codex v0.125.0 (research preview)
        --------
        workdir: /path
        model: gpt-5.5
        ...
        --------
        user
        <prompt echo>
        codex
        <ACTUAL CONTENT>      ← we want this
        tokens used
        XXXXX
    """
    lines = stdout.splitlines()
    start = -1
    for i, line in enumerate(lines):
        if line.strip() == "codex":
            start = i + 1
            break
    if start < 0:
        return stdout.strip()

    end = len(lines)
    for i in range(start, len(lines)):
        s = lines[i].strip()
        if s == "tokens used" or s.startswith("tokens used"):
            end = i
            break
        if "failed to record rollout items" in lines[i]:
            end = i
            break

    return "\n".join(lines[start:end]).strip()
