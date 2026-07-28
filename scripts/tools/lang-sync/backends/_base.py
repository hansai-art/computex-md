"""
backends/_base.py — Translation backend abstract interface.

Designed for the SQUEEZE-MODELS-MAX-PIPELINE v4 (post-2026-05-12 admiring-montalcini-post-finale
abstraction refactor). Lets pipeline cascade across:

- OpenRouter HTTP API (owl-alpha / gpt-oss-120b / nemotron / etc free-tier models)
- OpenAI Codex CLI subprocess (gpt-5.5 via personal subscription)
- Google Gemini CLI subprocess (workspace subscription)
- Local Ollama HTTP API (qwen3.6 / gemma-4 / taide-gemma3)

…without pipeline knowing which one is in use. New providers slot in by subclassing
`TranslationBackend` and registering.

Per哲宇 callout 2026-05-12: 「儘可能模組化 抽象化 可抽換化 讓系統獨立於模型與服務類別能運作」
"""
from __future__ import annotations

import abc
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


# ────────────────── Error hierarchy ──────────────────

class BackendError(Exception):
    """Base for all backend-raised errors. Caller catches this to try next backend."""


class BackendUnavailable(BackendError):
    """Backend cannot be used (auth missing / network down / CLI not installed)."""


class BackendRateLimited(BackendError):
    """Backend hit rate limit. cool_down_until indicates retry window."""

    def __init__(self, message: str, cool_down_until: Optional[datetime] = None):
        super().__init__(message)
        self.cool_down_until = cool_down_until


class BackendRefusal(BackendError):
    """Backend explicitly refused content (PRC content policy / safety classifier)."""


class BackendTimeout(BackendError):
    """Backend call exceeded timeout. Often transient — caller may retry."""


class BackendBadOutput(BackendError):
    """Backend returned malformed / truncated / empty output."""


# ────────────────── Backend metadata ──────────────────

@dataclass
class BackendStats:
    """Per-session running counters. Backends update on each call."""
    calls: int = 0
    successes: int = 0
    rate_limited: int = 0
    refusals: int = 0
    timeouts: int = 0
    last_error: Optional[str] = None
    last_call_at: Optional[datetime] = None


@dataclass
class BackendCapabilities:
    """Self-reported properties for cascade routing decisions.

    Cascade orchestrator uses these to pick the right backend for a given article:
    - sovereignty-sensitive Taiwan content → prefer high `prc_refusal_risk_low` backends
    - depth article > 30KB → require `max_context_chars` ≥ size
    - latency-critical batch → prefer low `typical_latency_s`
    """
    name: str
    provider_kind: str            # 'openrouter' | 'codex-cli' | 'gemini-cli' | 'ollama' | 'anthropic-sdk' | ...
    model: str                    # canonical model id (e.g. 'openrouter/owl-alpha', 'gpt-5.5', 'qwen3.6:35b-a3b')
    cost_kind: str                # 'free-tier' | 'subscription' | 'paid-per-token' | 'local-compute'
    typical_latency_s: int        # rough wall-clock per article (depth ~10K chars)
    max_context_chars: int        # hard limit
    prc_refusal_risk_low: bool    # True if provider origin = Western (Google/OpenAI/Nvidia/Meta) or Local
    multilingual_strength: float  # 0-1; how strong on zh→{en,ja,ko,es,fr} translation specifically
    notes: str = ""


# ────────────────── Abstract base ──────────────────

class TranslationBackend(abc.ABC):
    """
    Abstract translation backend.

    Concrete subclasses implement provider-specific dispatch. The cascade orchestrator
    (see `scripts/tools/lang-sync/translate.py`) holds an ordered list of backends and
    calls `translate()` on each in order until one succeeds.

    Implementation pattern (concrete subclass):

        class XBackend(TranslationBackend):
            CAPABILITIES = BackendCapabilities(
                name='X', provider_kind='...', model='...', cost_kind='...',
                typical_latency_s=..., max_context_chars=..., prc_refusal_risk_low=True,
                multilingual_strength=0.85,
            )

            def is_available(self) -> bool:
                # Check auth / CLI / network
                ...

            def translate(self, system: str, user: str, **kw) -> str:
                # Make call; raise BackendRateLimited / BackendRefusal / etc on failure
                # Update self.stats on success
                ...
    """

    CAPABILITIES: BackendCapabilities = None  # subclass must set

    def __init__(self, **config):
        self.config = config
        self.stats = BackendStats()
        self._cool_down_until: Optional[datetime] = None

    # ── canonical accessors ──

    @property
    def name(self) -> str:
        return self.CAPABILITIES.name if self.CAPABILITIES else self.__class__.__name__

    def cool_down_until(self) -> Optional[datetime]:
        """When can we retry after rate limit? None = no cool-down active."""
        if self._cool_down_until and self._cool_down_until <= _now():
            self._cool_down_until = None
        return self._cool_down_until

    def in_cooldown(self) -> bool:
        return self.cool_down_until() is not None

    def mark_cool_down(self, seconds: int = 300):
        """Set cool-down window. Caller (cascade) uses cool_down_until() to skip."""
        from datetime import timedelta
        self._cool_down_until = _now() + timedelta(seconds=seconds)

    # ── abstract methods (subclasses MUST implement) ──

    @abc.abstractmethod
    def is_available(self) -> bool:
        """Pre-flight: backend ready to receive calls (auth/network/CLI)."""

    @abc.abstractmethod
    def translate(self, system: str, user: str, *, max_tokens: int = 32000, timeout: int = 600) -> str:
        """Single translation call.

        Args:
            system: system instructions (translator role + rules)
            user: user message (the actual article + frontmatter scaffold + manifest entry)
            max_tokens: cap on completion tokens
            timeout: hard wall-clock limit per call (seconds)

        Returns:
            Raw output string (caller strips markdown code fence wrapper)

        Raises:
            BackendUnavailable, BackendRateLimited, BackendRefusal, BackendTimeout, BackendBadOutput
        """

    # ── shared helpers ──

    def _record_success(self):
        self.stats.calls += 1
        self.stats.successes += 1
        self.stats.last_call_at = _now()

    def _record_failure(self, error_type: str, msg: str):
        self.stats.calls += 1
        self.stats.last_error = f"{error_type}: {msg[:200]}"
        self.stats.last_call_at = _now()
        if error_type == "rate_limited":
            self.stats.rate_limited += 1
        elif error_type == "refusal":
            self.stats.refusals += 1
        elif error_type == "timeout":
            self.stats.timeouts += 1

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} model={self.CAPABILITIES.model if self.CAPABILITIES else '?'!r}>"


def _now() -> datetime:
    return datetime.now(timezone.utc)
