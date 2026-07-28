#!/usr/bin/env python3
"""generate-spore-records.py — 孢子完整記錄層 + 靜態 API 生成器（v2 JSON SSOT 輸入）。

Input (structured SSOT, written via scripts/tools/spore-db.py):
  docs/factory/spore-log.json      identity registry
  docs/factory/spore-metrics.json  metric event stream

Output:
  src/data/spores.json   (git tracked, build-time import for SporeFootprint join)
  public/api/spores.json (gitignored, regenerated each prebuild, ships with the site)

Why (reports/spore-data-architecture-2026-06-10.md + spore-json-ssot-2026-06-10.md):
  Engagement numbers live in their own data layer; articles keep an immutable
  identity pointer. v1 parsed SPORE-LOG.md / SPORE-HARVESTS markdown tables —
  v2 reads the JSON SSOT, retiring the brittle table parsers entirely.

Record shape (per spore):
  id / slug / articlePath / articleUrl / lang / platform / date / url / template
  metrics      — per-field last-non-null fold over events {views..shares}
  metricsAsOf  — {dPlus, harvestDate, batch, source: harvest|harvest+backfill|frontmatter-seed}
  history      — harvest events ascending (seed events fold into metrics only)

Determinism: file rewritten only when payload (minus _generated) changes —
a no-op regen produces no git diff.

Usage:
  python3 scripts/tools/generate-spore-records.py            # regen
  python3 scripts/tools/generate-spore-records.py --check    # exit 1 if stale

2026-06-10 | v1 markdown parse → v2 JSON SSOT input (same output shape + template)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LOG_PATH = REPO / "docs/factory/spore-log.json"
METRICS_PATH = REPO / "docs/factory/spore-metrics.json"
KNOWLEDGE_ROOT = REPO / "knowledge"
OUT_DATA = REPO / "src/data/spores.json"
OUT_API = REPO / "public/api/spores.json"

TPE = timezone(timedelta(hours=8))
METRIC_KEYS = ("views", "likes", "reposts", "comments", "shares")
LANG_DIRS = {"en", "ja", "ko", "es", "fr", "zh-TW"}

# knowledge/ category dir (Capitalized) → URL slug (matches content-dates keys)
CAT_TO_SLUG = {
    "About": "about", "Art": "art", "Culture": "culture", "Economy": "economy",
    "Food": "food", "Geography": "geography", "History": "history",
    "Lifestyle": "lifestyle", "Music": "music", "Nature": "nature",
    "People": "people", "Politics": "politics", "Society": "society",
    "Technology": "technology",
}


def _normalize_slug(slug):
    """Strip emoji prefix + parenthetical version markers from log slug."""
    s = re.sub(r"^[\U0001F300-\U0001FAFF☀-➿\s]+", "", slug or "")
    s = re.sub(r"[（(].*?[）)]\s*$", "", s)
    return s.strip()


def _article_lookup():
    """One walk of knowledge/ → {(lang, filename-stem): (path, category)}."""
    table = {}
    for md in KNOWLEDGE_ROOT.rglob("*.md"):
        rel = md.relative_to(KNOWLEDGE_ROOT)
        parts = rel.parts
        if parts[-1].startswith("_"):
            continue
        if parts[0] in LANG_DIRS:
            if len(parts) != 3:
                continue
            lang, cat = parts[0], parts[1]
        else:
            if len(parts) != 2:
                continue
            lang, cat = "zh", parts[0]
        if cat not in CAT_TO_SLUG:
            continue
        table[(lang, md.stem)] = (str(rel), cat)
    return table


def resolve_article(lookup, lang, slug):
    """→ (slug_norm, articlePath, articleUrl) — Nones when unresolved."""
    cand = [slug, _normalize_slug(slug)]
    lang_key = "zh" if lang in ("zh", "zh-tw", "") else lang
    for c in cand:
        if not c:
            continue
        hit = lookup.get((lang_key, c))
        if hit:
            rel, cat = hit
            cat_slug = CAT_TO_SLUG[cat]
            prefix = "" if lang_key == "zh" else f"/{lang_key}"
            return c, f"knowledge/{rel}", f"{prefix}/{cat_slug}/{c}/"
    return _normalize_slug(slug) or None, None, None


def _event_sort_key(e):
    return (e["dPlus"] if e.get("dPlus") is not None else -1, e.get("at") or "")


def build_records():
    log = [s for s in json.loads(LOG_PATH.read_text(encoding="utf-8"))["spores"]
           if not s.get("deleted")]  # 已刪除孢子排除於衍生記錄層（spore-log SSOT 仍保留供溯源）
    all_events = json.loads(METRICS_PATH.read_text(encoding="utf-8"))["events"]
    lookup = _article_lookup()

    events_by_spore = defaultdict(list)
    for e in all_events:
        events_by_spore[e["spore"]].append(e)
    for n in events_by_spore:
        events_by_spore[n].sort(key=_event_sort_key)

    records, by_article = [], defaultdict(list)
    for s in sorted(log, key=lambda x: x["id"]):
        n = s["id"]
        slug_norm, path, url_path = resolve_article(lookup, s.get("lang", "zh"),
                                                    s.get("slug", ""))
        evs = events_by_spore.get(n, [])
        harvest_evs = [e for e in evs if e.get("batch")]

        # metrics = per-field last-non-null fold (seed events sort first, so a
        # later harvest value always wins; older observed values survive nulls)
        metrics = {k: None for k in METRIC_KEYS}
        contributing = set()
        for e in evs:
            for k in METRIC_KEYS:
                if e.get(k) is not None:
                    metrics[k] = e[k]
                    contributing.add(id(e))

        metrics_as_of = None
        if evs and any(v is not None for v in metrics.values()):
            last = evs[-1]
            if last.get("batch"):
                # did any field survive from an earlier event than the last?
                backfilled = any(
                    metrics[k] is not None and last.get(k) is None
                    for k in METRIC_KEYS
                )
                metrics_as_of = {
                    "dPlus": last.get("dPlus"),
                    "harvestDate": last.get("at"),
                    "batch": last.get("batch"),
                    "source": "harvest+backfill" if backfilled else "harvest",
                }
            else:
                metrics_as_of = {"dPlus": None, "harvestDate": None, "batch": None,
                                 "source": "frontmatter-seed"}

        rec = {
            "id": n,
            "slug": slug_norm,
            "articlePath": path,
            "articleUrl": url_path,
            "lang": s.get("lang", "zh"),
            "platform": s.get("platform"),
            "date": s.get("date"),
            "url": s.get("url"),
            "template": s.get("template"),
            "metrics": metrics,
            "metricsAsOf": metrics_as_of,
            "history": [
                {"dPlus": e.get("dPlus"), "harvestDate": e.get("at"),
                 "batch": e.get("batch"),
                 **{k: e.get(k) for k in METRIC_KEYS}}
                for e in harvest_evs
            ],
        }
        records.append(rec)
        if path and slug_norm:
            by_article[slug_norm].append(n)

    payload = {
        "schemaVersion": 1,
        "counts": {
            "spores": len(records),
            "articles": len(by_article),
            "withMetrics": sum(1 for r in records if r["metricsAsOf"]),
        },
        "spores": records,
        "byArticle": {k: sorted(v) for k, v in sorted(by_article.items())},
    }
    return payload


def _stable(payload):
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def write_if_changed(path, payload, compact):
    """Write only when payload (minus _generated) differs. Returns changed?"""
    old_core = None
    if path.exists():
        try:
            old = json.loads(path.read_text(encoding="utf-8"))
            old.pop("_generated", None)
            old_core = _stable(old)
        except (json.JSONDecodeError, OSError):
            pass
    if old_core == _stable(payload):
        return False
    out = {"_generated": datetime.now(TPE).isoformat(timespec="seconds"), **payload}
    path.parent.mkdir(parents=True, exist_ok=True)
    if compact:
        path.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    else:
        # indent=2 matches the repo prettier config — keeps regen byte-stable
        # against the pre-commit format hook (no phantom format-only diffs).
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if regen would change src/data/spores.json")
    args = ap.parse_args()

    if not LOG_PATH.exists() or not METRICS_PATH.exists():
        print("❌ spore-log.json / spore-metrics.json 缺檔 — "
              "見 reports/spore-json-ssot-2026-06-10.md（bootstrap-spore-ssot.py）",
              file=sys.stderr)
        return 2

    payload = build_records()

    if args.check:
        old_core = None
        if OUT_DATA.exists():
            try:
                old = json.loads(OUT_DATA.read_text(encoding="utf-8"))
                old.pop("_generated", None)
                old_core = _stable(old)
            except (json.JSONDecodeError, OSError):
                pass
        stale = old_core != _stable(payload)
        print(f"spores.json {'STALE' if stale else 'fresh'} "
              f"({payload['counts']['spores']} spores)")
        return 1 if stale else 0

    changed_data = write_if_changed(OUT_DATA, payload, compact=False)
    changed_api = write_if_changed(OUT_API, payload, compact=True)
    c = payload["counts"]
    print(f"✓ spore records: {c['spores']} spores / {c['articles']} articles / "
          f"{c['withMetrics']} with metrics"
          f" → src/data/spores.json{' (updated)' if changed_data else ' (unchanged)'}"
          f", public/api/spores.json{' (updated)' if changed_api else ' (unchanged)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
