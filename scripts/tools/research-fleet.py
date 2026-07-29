#!/usr/bin/env python3
"""research-fleet.py — search/fetch provider abstraction for REWRITE-PIPELINE Stage 1.

Why this exists (2026-07-24 外送專法 session): running 4 parallel Sonnet research
agents for one article burned ~500K tokens and hit an account session limit before
they all finished. Most of that cost is mechanical labor (run a query, open a page,
pull out text) that doesn't need Sonnet-level judgment. This tool moves that labor
off the Claude meter: a script calls real search/fetch APIs directly, so Claude's
role shrinks to query design (Stage 0) and synthesis/falsification (the manual §2-§7
consolidation done in reports/research/2026-07/外送專法.md).

Provider abstraction (per MANIFESTO §架構解 第二例證，2026-07-24): every provider is
swappable behind SearchProvider / FetchProvider. Bing Search API retired 2025-08-11,
Google Custom Search closed to new signups in 2025, Brave dropped its free tier in
2026-02 — three "normal" vendors gone or repriced within a year. Call sites depend on
the interface, not the vendor name, so losing a provider means adding one class, not
rewriting the pipeline.

Usage:
    python3 scripts/tools/research-fleet.py search "外送專法 施行細則" --count 10
    python3 scripts/tools/research-fleet.py fetch "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=N0020024"
    python3 scripts/tools/research-fleet.py batch task.json --out reports/research/2026-07/外送專法-fleet-E.json

Credentials read from ~/.config/taiwan-md/credentials/.env (same convention as
fetch-cloudflare.py / openrouter-translate.py) — BRAVE_API_KEY, SERPER_API_KEY,
optional JINA_API_KEY. Never commit real keys; this repo's own .env guard
(fetch-cloudflare.py) fails loud if credentials end up inside the repo.
"""

import argparse
import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

CREDS_DIR = Path.home() / ".config/taiwan-md/credentials"
ENV_FILE = CREDS_DIR / ".env"


def load_env() -> dict:
    import os

    env = dict(os.environ)
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip("'\"")
    return env


ENV = load_env()


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str = ""
    provider: str = ""


@dataclass
class FetchedDoc:
    url: str
    title: str
    text: str
    provider: str
    articles: Optional[dict] = None
    ok: bool = True
    error: str = ""


class SearchProvider(ABC):
    name = "abstract"

    def available(self) -> bool:
        return True

    @abstractmethod
    def search(self, query: str, count: int = 10, country: str = "tw", lang: str = "zh-hant") -> list[SearchResult]:
        ...


class FetchProvider(ABC):
    name = "abstract"

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        ...

    @abstractmethod
    def fetch(self, url: str) -> FetchedDoc:
        ...


class BraveSearch(SearchProvider):
    name = "brave"

    def __init__(self):
        self.key = ENV.get("BRAVE_API_KEY")

    def available(self) -> bool:
        return bool(self.key)

    def search(self, query, count=10, country="tw", lang="zh-hant"):
        params = {"q": query, "country": country, "search_lang": lang, "count": str(count)}
        url = "https://api.search.brave.com/res/v1/web/search?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"Accept": "application/json", "X-Subscription-Token": self.key})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
        return [
            SearchResult(title=r.get("title", ""), url=r.get("url", ""), snippet=r.get("description", ""), provider=self.name)
            for r in data.get("web", {}).get("results", [])
        ]


class SerperSearch(SearchProvider):
    name = "serper"

    def __init__(self):
        self.key = ENV.get("SERPER_API_KEY")

    def available(self) -> bool:
        return bool(self.key)

    def search(self, query, count=10, country="tw", lang="zh-hant"):
        body = json.dumps({"q": query, "gl": country, "hl": "zh-tw", "num": count}).encode()
        req = urllib.request.Request(
            "https://google.serper.dev/search",
            data=body,
            headers={"X-API-KEY": self.key, "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
        return [
            SearchResult(title=r.get("title", ""), url=r.get("link", ""), snippet=r.get("snippet", ""), provider=self.name)
            for r in data.get("organic", [])
        ]


class SearchCascade:
    """Tries providers in order, skips unavailable/failed ones. Same shape as the babel 4-tier cascade."""

    def __init__(self, providers: list[SearchProvider]):
        self.providers = providers

    def search(self, query, count=10, **kw) -> list[SearchResult]:
        errors = []
        for p in self.providers:
            if not p.available():
                continue
            try:
                results = p.search(query, count=count, **kw)
                if results:
                    return results
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
                errors.append(f"{p.name}: {e}")
        raise RuntimeError(f"all search providers failed/unavailable: {errors or 'no provider has a key set'}")


class MojLawFetch(FetchProvider):
    """全國法規資料庫 dedicated parser — returns exact article-numbered verbatim text.

    Built 2026-07-24: WebFetch could not get full articles from this exact domain across
    4 separate research agents (125-char truncation policy, PDF binary failures). The
    site's HTML has article numbers in a separate <a name="N"> tag per row, so a plain
    regex gets clean, article-numbered text with zero LLM cost.
    """

    name = "moj-law"
    URL_RE = re.compile(r"law\.moj\.gov\.tw/LawClass/LawAll\.aspx\?pcode=([\w-]+)")
    ROW_RE = re.compile(
        r'<div class="row"><div class="col-no"> <a[^>]*name="(\d+)">第\s*\d+\s*條</a></div>'
        r'<div class="col-data">(.*?)</div>\s*</div>\s*</div>',
        re.S,
    )
    TITLE_RE = re.compile(r"<title>([^<]+)</title>")

    def can_handle(self, url: str) -> bool:
        return bool(self.URL_RE.search(url))

    # law.moj.gov.tw's cert chain omits Subject Key Identifier, which Python's
    # default strict SSL context rejects (curl tolerates it). Scoped relaxation
    # for this one government legal-database domain only — read-only public
    # law text, no credentials involved.
    _GOV_TLS_CTX = ssl._create_unverified_context()

    def fetch(self, url: str) -> FetchedDoc:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=30, context=self._GOV_TLS_CTX) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            return FetchedDoc(url=url, title="", text="", provider=self.name, ok=False, error=str(e))
        rows = self.ROW_RE.findall(html)
        articles = {int(num): re.sub(r"<[^>]+>", "", content).strip() for num, content in rows}
        title_m = self.TITLE_RE.search(html)
        title = title_m.group(1).strip() if title_m else url
        full_text = "\n\n".join(f"第{n}條：{t}" for n, t in sorted(articles.items()))
        return FetchedDoc(url=url, title=title, text=full_text, provider=self.name, articles=articles, ok=bool(articles))


class JinaFetch(FetchProvider):
    """Universal fallback: r.jina.ai converts any URL (incl. PDFs, JS-rendered pages) to clean markdown.
    Free without a key (rate-limited ~20 req/min); set JINA_API_KEY for higher limits."""

    name = "jina"
    TITLE_RE = re.compile(r"^Title:\s*(.+)$", re.M)

    def __init__(self):
        self.key = ENV.get("JINA_API_KEY")

    def can_handle(self, url: str) -> bool:
        return True

    def fetch(self, url: str) -> FetchedDoc:
        # Jina 403s requests with urllib's default User-Agent string.
        headers = {"Accept": "text/plain", "User-Agent": "Mozilla/5.0"}
        if self.key:
            headers["Authorization"] = f"Bearer {self.key}"
        req = urllib.request.Request("https://r.jina.ai/" + url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                text = resp.read().decode("utf-8", errors="ignore")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            return FetchedDoc(url=url, title="", text="", provider=self.name, ok=False, error=str(e))
        title_m = self.TITLE_RE.search(text)
        title = title_m.group(1).strip() if title_m else url
        return FetchedDoc(url=url, title=title, text=text, provider=self.name, ok=bool(text.strip()))


class DigestProvider(ABC):
    """LLM completion for turning raw fetched text into structured findings.
    Deliberately generic (system+user → text), not research-specific, so the
    same interface could serve other digest needs later."""

    name = "abstract"

    def available(self) -> bool:
        return True

    @abstractmethod
    def complete(self, system: str, user: str, max_tokens: int = 2000) -> str:
        ...


class OpenRouterDigest(DigestProvider):
    """Free-tier cloud digest. Same key-rotation pool as lang-sync/openrouter-translate.py
    (~/.config/taiwan-md/credentials/openrouter.key + openrouter-keys/*.key)."""

    name = "openrouter"
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    # openai/gpt-oss-120b:free (lang-sync's own default) was retired by OpenRouter
    # sometime before 2026-07-24 — hit live during this tool's own test run
    # ("model unavailable for free, use openai/gpt-oss-120b instead"). Free-tier
    # model slugs drift; this default may need re-checking against
    # https://openrouter.ai/api/v1/models (filter `:free`) periodically.
    DEFAULT_MODEL = "google/gemma-4-31b-it:free"

    def __init__(self, model: str = None):
        self.model = model or ENV.get("OPENROUTER_MODEL", self.DEFAULT_MODEL)

    def _keys(self) -> list[str]:
        keys = []
        if ENV.get("OPENROUTER_API_KEY"):
            keys.append(ENV["OPENROUTER_API_KEY"])
        rotation_dir = CREDS_DIR / "openrouter-keys"
        if rotation_dir.is_dir():
            for f in sorted(rotation_dir.glob("*.key")):
                v = f.read_text().strip()
                if v and v not in keys:
                    keys.append(v)
        key_file = CREDS_DIR / "openrouter.key"
        if key_file.exists():
            v = key_file.read_text().strip()
            if v and v not in keys:
                keys.append(v)
        return keys

    def available(self) -> bool:
        return bool(self._keys())

    def complete(self, system, user, max_tokens=2000):
        keys = self._keys()
        if not keys:
            raise RuntimeError("no OpenRouter key available")
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                "temperature": 0.3,
                "max_tokens": max_tokens,
            }
        ).encode("utf-8")
        last_err = "no keys tried"
        for key in keys:
            req = urllib.request.Request(
                self.API_URL,
                data=payload,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://computex.taiwanai.ngo",
                    "X-Title": "research-fleet digest",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = json.load(resp)
                return data["choices"][0]["message"]["content"]
            except urllib.error.HTTPError as e:
                last_err = f"HTTP {e.code}"
                if e.code == 429:
                    continue  # rotate to next key
                raise RuntimeError(f"OpenRouter {last_err}: {e.read().decode('utf-8', errors='replace')[:300]}")
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                last_err = str(e)
                continue
        raise RuntimeError(f"all OpenRouter keys failed: {last_err}")


class OllamaDigest(DigestProvider):
    """Local GPU fallback — sovereignty backbone per REFLEXES #49, always available,
    no rate limit. Mirrors lang-sync/backends/ollama.py's num_ctx sizing: without an
    explicit num_ctx, Ollama silently truncates to a small server default regardless
    of what the model card advertises (2026-07-24 fleet-dispatch bug, same day as this
    tool's build)."""

    name = "ollama"

    def __init__(self, host: str = None, model: str = None):
        self.host = host or ENV.get("OLLAMA_HOST", "http://localhost:11434")
        self.model = model or ENV.get("OLLAMA_MODEL", "qwen3.6:35b-a3b-coding-nvfp4")

    def available(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.host}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.load(resp)
            names = [m.get("name", "") for m in data.get("models", [])]
            return any(n.startswith(self.model.split(":")[0]) for n in names)
        except (urllib.error.URLError, OSError):
            return False

    def complete(self, system, user, max_tokens=2000):
        prompt_chars = len(system) + len(user)
        est_tokens = prompt_chars // 3 + 512
        num_ctx = min(max(est_tokens + max_tokens + 2048, 8192), 131072)
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                "stream": False,
                "think": False,
                "options": {"temperature": 0.3, "num_predict": max_tokens, "num_ctx": num_ctx},
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{self.host}/api/chat", data=payload, headers={"Content-Type": "application/json"}, method="POST"
        )
        # 600s not 300s: this GPU node may be shared with concurrent lang-sync
        # batches (per check-parallel-actor.sh), and queued requests can wait
        # behind a full babel job before this one even starts running.
        with urllib.request.urlopen(req, timeout=600) as resp:
            data = json.load(resp)
        return data.get("message", {}).get("content", "")


class DigestCascade:
    def __init__(self, providers: list[DigestProvider]):
        self.providers = providers

    def complete(self, system, user, max_tokens=2000) -> tuple[str, str]:
        errors = []
        for p in self.providers:
            if not p.available():
                continue
            try:
                out = p.complete(system, user, max_tokens=max_tokens)
                if out and out.strip():
                    return out, p.name
            except (RuntimeError, urllib.error.URLError, TimeoutError, OSError) as e:
                errors.append(f"{p.name}: {e}")
        raise RuntimeError(f"all digest providers failed/unavailable: {errors}")


def build_default_digest() -> DigestCascade:
    return DigestCascade([OpenRouterDigest(), OllamaDigest()])


SOURCE_DIGEST_SYSTEM = (
    "你是 COMPUTEX.md 的研究助理，只根據提供的原始網頁內容整理事實，絕不編造、絕不用網頁沒寫的內容補空。"
    "查不到就明說查不到，不要用「合理推測」填空。"
)


def _digest_source_prompt(subtopic_scope: str, query: str, title: str, url: str, text: str) -> str:
    return f"""問題脈絡：{subtopic_scope}
原始查詢：「{query}」
來源標題：{title}
來源網址：{url}

原始內容（可能是節錄）：
---
{text[:8000]}
---

請輸出下面格式（純文字，不要多餘的開場白或結語）：
【來源】{url} — 一句話標注這是什麼媒體或頁面性質
【發現】一到三句話：這頁對回答「{subtopic_scope}」這個問題脈絡最重要的具體事實、數字、日期或人名
【逐字】如果內容裡有適合直接引用的原句（人物發言、法條原文、官方聲明），完整抄錄；沒有就寫「無」
【信度】一手 / 權威二手 / 存疑（依內容判斷來源性質，不是猜測）
【falsify 註記】這則內容有沒有跟常見說法不一致的地方？沒有就寫「無」
"""


def cmd_digest(args):
    raw = json.loads(Path(args.raw).read_text())
    digest = build_default_digest()
    blocks, quote_bank, negatives = [], [], []
    used_providers: set[str] = set()

    for s in raw.get("sources", []):
        if not s.get("ok"):
            negatives.append(f"- {s['url']} 擷取失敗（{s.get('fetch_provider')}）：{s.get('error', '')}")
            continue
        prompt = _digest_source_prompt(args.subtopic, s["query"], s["title"], s["url"], s["text"])
        try:
            out, provider = digest.complete(SOURCE_DIGEST_SYSTEM, prompt, max_tokens=600)
        except RuntimeError as e:
            negatives.append(f"- {s['url']} digest 失敗：{e}")
            continue
        used_providers.add(provider)
        blocks.append(out.strip())
        for line in out.splitlines():
            stripped = line.strip()
            if stripped.startswith("【逐字】") and not stripped[4:].strip().startswith("無"):
                quote_bank.append(f"- {stripped[4:].strip()} — {s['url']}")
        time.sleep(args.delay)

    for q in raw.get("queries", []):
        if q.get("error"):
            negatives.append(f"- 查詢「{q['query']}」失敗：{q['error']}")
        elif q.get("hit_count", 0) == 0:
            negatives.append(f"- 查詢「{q['query']}」無命中結果")

    sources_by_query: dict[str, list[dict]] = {}
    for s in raw.get("sources", []):
        sources_by_query.setdefault(s["query"], []).append(s)

    search_log_lines = []
    for i, q in enumerate(raw.get("queries", [])):
        search_log_lines.append(f"{i + 1}. 「{q['query']}」 → {q.get('hit_count', 0)} 筆結果 [{q.get('provider', '?')}]")
        for s in sources_by_query.get(q["query"], []):
            status = "✓" if s.get("ok") else f"✗ {s.get('error', '')}"
            search_log_lines.append(f"   - {s['url']} [{s.get('fetch_provider', '?')}] {status}")
    search_log = "\n".join(search_log_lines)
    findings = "\n\n".join(blocks) if blocks else "（本批次無成功 digest 的來源）"
    quotes = "\n".join(quote_bank) if quote_bank else "（本批次無適合逐字引用內容）"
    neg = "\n".join(negatives) if negatives else "（無）"
    provider_label = "/".join(sorted(used_providers)) or "n/a"

    report = f"""# {args.slug} — Research {args.letter}：{args.subtopic}

執行摘要：research-fleet 自動 fan-out（digest provider: {provider_label}），{len(raw.get('sources', []))} 個來源、{len(raw.get('queries', []))} 次查詢。本報告由機械 search/fetch + LLM digest 產生，非人工逐條研究，§2 每條 finding 需視為線索，高風險 atom 仍須人工或 Path A agent 複驗。

## §1 搜尋軌跡（fleet 自動化，非人工逐條）
{search_log}

## §2 Findings
{findings}

## §3 引語庫
{quotes}

## §4 Negative findings
{neg}

## §5 質地素材
（research-fleet 自動化路徑不產出質地素材，由主 session 或 Path A agent 補）
"""
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"✅ digest 完成，provider={provider_label} → {out_path}")


class FetchCascade:
    def __init__(self, providers: list[FetchProvider]):
        self.providers = providers

    def fetch(self, url: str) -> FetchedDoc:
        for p in self.providers:
            if p.can_handle(url):
                doc = p.fetch(url)
                if doc.ok:
                    return doc
        return FetchedDoc(url=url, title="", text="", provider="none", ok=False, error="all fetch providers failed")


def build_default_search() -> SearchCascade:
    return SearchCascade([BraveSearch(), SerperSearch()])


def build_default_fetch() -> FetchCascade:
    return FetchCascade([MojLawFetch(), JinaFetch()])


def cmd_search(args):
    results = build_default_search().search(args.query, count=args.count, country=args.country, lang=args.lang)
    out = [asdict(r) for r in results]
    if args.out:
        Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2))
        print(f"✅ {len(out)} results → {args.out}")
    else:
        print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_fetch(args):
    doc = build_default_fetch().fetch(args.url)
    if args.out:
        Path(args.out).write_text(json.dumps(asdict(doc), ensure_ascii=False, indent=2))
        print(f"{'✅' if doc.ok else '❌'} provider={doc.provider} → {args.out}")
    else:
        print(json.dumps(asdict(doc), ensure_ascii=False, indent=2)[:3000])


def cmd_batch(args):
    spec = json.loads(Path(args.spec).read_text())
    search_cascade = build_default_search()
    fetch_cascade = build_default_fetch()
    results: dict = {"queries": [], "sources": []}
    seen_urls: set[str] = set()
    for q in spec.get("queries", []):
        try:
            hits = search_cascade.search(
                q, count=spec.get("count_per_query", 5), country=spec.get("country", "tw"), lang=spec.get("lang", "zh-hant")
            )
        except RuntimeError as e:
            results["queries"].append({"query": q, "error": str(e)})
            continue
        results["queries"].append({"query": q, "hit_count": len(hits), "provider": hits[0].provider if hits else None})
        for h in hits[: spec.get("fetch_top_k", 3)]:
            if h.url in seen_urls:
                continue
            seen_urls.add(h.url)
            doc = fetch_cascade.fetch(h.url)
            results["sources"].append(
                {
                    "query": q,
                    "title": h.title,
                    "url": h.url,
                    "snippet": h.snippet,
                    "search_provider": h.provider,
                    "fetch_provider": doc.provider,
                    "ok": doc.ok,
                    "error": doc.error,
                    "text": doc.text[: spec.get("max_chars", 20000)],
                    "articles": doc.articles,
                }
            )
            time.sleep(spec.get("delay_sec", 1.0))
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"✅ {len(results['sources'])} sources fetched → {out_path}")


def main():
    ap = argparse.ArgumentParser(description="research-fleet — search/fetch provider abstraction for REWRITE-PIPELINE Stage 1")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("search")
    sp.add_argument("query")
    sp.add_argument("--count", type=int, default=10)
    sp.add_argument("--country", default="tw")
    sp.add_argument("--lang", default="zh-hant")
    sp.add_argument("--out")
    sp.set_defaults(func=cmd_search)

    fp = sub.add_parser("fetch")
    fp.add_argument("url")
    fp.add_argument("--out")
    fp.set_defaults(func=cmd_fetch)

    bp = sub.add_parser("batch")
    bp.add_argument("spec", help="JSON file: {queries: [...], count_per_query, fetch_top_k, country, lang, max_chars, delay_sec}")
    bp.add_argument("--out", required=True)
    bp.set_defaults(func=cmd_batch)

    dp = sub.add_parser("digest", help="turn a batch's raw JSON into a RESEARCH-AGENT-PROMPT-format markdown report")
    dp.add_argument("raw", help="path to batch's --out JSON")
    dp.add_argument("--slug", required=True, help="article slug, e.g. 外送專法")
    dp.add_argument("--letter", default="X", help="facet/agent letter, e.g. A")
    dp.add_argument("--subtopic", required=True, help="one-line subtopic scope, matches the batch task's intent")
    dp.add_argument("--out", required=True)
    dp.add_argument("--delay", type=float, default=1.0)
    dp.set_defaults(func=cmd_digest)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
