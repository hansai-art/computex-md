#!/usr/bin/env python3
"""sync-spore-links.py — regenerate knowledge/{...}.md sporeLinks frontmatter from SSOT.

Phase 3 of reports/spore-ssot-pipeline-cleanup-2026-05-08.md;
v2 identity-only per reports/spore-data-architecture-2026-06-10.md.

## Why

knowledge/*.md frontmatter `sporeLinks` is a DERIVED VIEW regenerated from
SPORE-LOG (identity SSOT). v2 (2026-06-10): entries carry IDENTITY ONLY —
engagement numbers moved to src/data/spores.json (generate-spore-records.py).
Mutable metrics in article frontmatter polluted git timestamps → content-dates
→ /latest ordering + sitemap lastmod faked freshness on every harvest backfill.
After v2 an article file changes only when a NEW spore ships for it.

Layer map:
  - docs/factory/spore-log.json         = identity SSOT (spore-db.py add-spore)
  - docs/factory/spore-metrics.json     = harvest event SSOT (spore-db.py add-metrics)
  - src/data/spores.json                = full records + history (generate-spore-records.py)
  - knowledge/*.md sporeLinks           = identity pointer (THIS script, append-only in practice)
  - src/content/*.md sporeLinks         = mirror of knowledge (gitignored projection)

Entry shape (v2 — immutable identity, no metrics):
  - id:       <spore #>                  ← SPORE-LOG 發文紀錄 row number
  - platform: 'threads' | 'x'
  - date:     'YYYY-MM-DD'
  - url:      '<canonical URL>'

## Usage

  python3 scripts/tools/sync-spore-links.py                 # dry-run (default)
  python3 scripts/tools/sync-spore-links.py --apply         # write changes
  python3 scripts/tools/sync-spore-links.py --diff          # show full diff
  python3 scripts/tools/sync-spore-links.py --article SLUG  # only this article

## Safety

- Default mode is dry-run — no writes without --apply.
- Each article diff shown explicitly before write.
- Articles without spores in SPORE-LOG → sporeLinks block REMOVED (was orphan).

2026-05-08 laughing-goldstine | Phase 3 of spore SSOT cleanup
2026-06-10 | v2 identity-only — metrics decoupled to spores.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SPORE_LOG_JSON = REPO / "docs/factory/spore-log.json"
KNOWLEDGE_ROOT = REPO / "knowledge"
SRC_CONTENT_ROOT = REPO / "src/content/zh-TW"  # mirror target

# Map knowledge/ category dir → src/content/zh-TW/ slug dir
# (knowledge uses Capitalized names; src/content uses lowercased)
_CAT_MAP = {
    "Art": "art",
    "Culture": "culture",
    "Economics": "economics",
    "History": "history",
    "Music": "music",
    "Nature": "nature",
    "People": "people",
    "Society": "society",
    "Technology": "technology",
}


# ────────────────── parsers ──────────────────


def parse_publication_table():
    """Identity rows from spore-log.json (v2.1, 2026-06-10 JSON SSOT flip).

    Keeps the v1 row shape {n, date, lang, platform, slug, url} so the rest of
    this script is untouched. SPORE-LOG.md 發文紀錄 is frozen history —
    new spores enter via `spore-db.py add-spore`.
    """
    if not SPORE_LOG_JSON.exists():
        return []
    data = json.loads(SPORE_LOG_JSON.read_text(encoding="utf-8"))
    rows = []
    for s in data.get("spores", []):
        if s.get("deleted"):  # 已刪除孢子不寫進文章 sporeLinks（避免死連結）
            continue
        rows.append({
            "n": s["id"],
            "date": s.get("date") or "",
            "lang": (s.get("lang") or "").lower(),
            "platform": (s.get("platform") or "").lower(),
            "slug": s.get("slug") or "",
            "url": s.get("url"),
        })
    return rows


# ────────────────── helpers ──────────────────


def _normalize_slug(slug):
    """Strip emoji prefix + parenthetical version markers from SPORE-LOG slug.

    Examples (Phase 6 — handle versioned slugs that pre-Phase-6 were unmatched):
      '🌋 李洋（v2，留言更正）'    → '李洋'
      '李洋（v3 場景修正）'        → '李洋'
      '李洋（⚠️ 已撤回）'          → '李洋'
      '草東沒有派對（v2.1 首例）'  → '草東沒有派對'
      '台灣高鐵（v3 事實修正版）'  → '台灣高鐵'
    """
    s = re.sub(r"^[\U0001F300-\U0001FAFF☀-➿\s]+", "", slug)
    s = re.sub(r"[（(].*?[）)]\s*$", "", s)
    return s.strip()


def find_article_path(slug):
    """Find knowledge/{Cat}/{slug}.md (zh canonical, skip multilingual mirrors).

    Tries the literal slug first, then a normalized form (strip emoji/parens).
    """
    candidates = [slug, _normalize_slug(slug)]
    seen = set()
    for cand in candidates:
        if not cand or cand in seen:
            continue
        seen.add(cand)
        for md in KNOWLEDGE_ROOT.rglob(f"{cand}.md"):
            rel = md.relative_to(KNOWLEDGE_ROOT)
            # Skip multilingual mirror dirs — sync targets zh canonical only
            if rel.parts and rel.parts[0] in {"en", "ja", "ko", "es", "fr", "zh-TW"}:
                continue
            return md
    return None


def src_content_mirror(knowledge_path):
    """Map knowledge/Cat/{slug}.md → src/content/zh-TW/cat/{slug}.md (or None if absent)."""
    try:
        rel = knowledge_path.relative_to(KNOWLEDGE_ROOT)
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) != 2:
        return None
    cat_kn = parts[0]
    cat_sc = _CAT_MAP.get(cat_kn, cat_kn.lower())
    target = SRC_CONTENT_ROOT / cat_sc / parts[1]
    return target if target.exists() else None


# ────────────────── canonical sporeLink builder ──────────────────


def build_canonical_sporelinks(pub_rows):
    """Group by article slug → list of canonical identity entries.

    v2 entry shape (immutable identity pointer — metrics live in spores.json):
      - id / platform / date / url
    """
    by_slug = defaultdict(list)
    for pub in pub_rows:
        if not pub["url"] or not pub["slug"]:
            continue
        if pub.get("lang") and pub["lang"] != "zh":
            continue
        if pub["platform"] not in ("threads", "x"):
            continue

        entry = {
            "id": pub["n"],
            "platform": pub["platform"],
            "date": pub["date"],
            "url": pub["url"],
        }

        # Phase 6: Group by NORMALIZED slug so multi-version entries
        # ('李洋（v2）', '🌋 李洋（v3）', '李洋（⚠️ 已撤回）') all coalesce to one
        # 'knowledge/People/李洋.md' file with all spores listed.
        normalized = _normalize_slug(pub["slug"])
        by_slug[normalized].append(entry)

    # Dedupe by url within a slug (keep first; multi-versioned slugs write same URL)
    for slug in by_slug:
        seen_urls = set()
        deduped = []
        for e in by_slug[slug]:
            if e["url"] in seen_urls:
                continue
            seen_urls.add(e["url"])
            deduped.append(e)
        by_slug[slug] = sorted(deduped, key=lambda e: (e["date"], e["platform"], e["id"]))
    return by_slug


# ────────────────── frontmatter rewriter ──────────────────


SPORELINK_BLOCK_RE = re.compile(
    r"(?ms)^sporeLinks:\s*\n(?:(?:  - .*?\n(?:    .*?\n)*)+)?",
)


def render_sporelinks_block(entries):
    """Render canonical sporeLinks YAML block (v2 identity-only)."""
    if not entries:
        return ""
    out = ["sporeLinks:"]
    for e in entries:
        out.append(f"  - id: {e['id']}")
        out.append(f"    platform: '{e['platform']}'")
        out.append(f"    date: '{e['date']}'")
        out.append(f"    url: '{e['url']}'")
    return "\n".join(out) + "\n"


def update_article_sporelinks(article_path, new_block):
    """Replace sporeLinks frontmatter block. Returns (changed, before, after).

    If article has no sporeLinks block AND new_block is non-empty: insert before closing ---.
    If article has sporeLinks block AND new_block is empty: remove block.
    Otherwise: replace.
    """
    text = article_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False, text, text
    end = text.find("---", 3)
    if end == -1:
        return False, text, text

    fm = text[3:end]
    body = text[end:]

    has_existing = bool(SPORELINK_BLOCK_RE.search(fm))

    if has_existing:
        new_fm = SPORELINK_BLOCK_RE.sub(new_block, fm, count=1)
    elif new_block:
        # Insert before closing newline of frontmatter
        new_fm = fm.rstrip() + "\n" + new_block
    else:
        return False, text, text

    new_text = "---" + new_fm + body
    if new_text == text:
        return False, text, text
    return True, text, new_text


# ────────────────── diff helper ──────────────────


def show_diff(before, after, name):
    """Show unified diff snippet for sporeLinks section only."""
    import difflib
    b_lines = before.splitlines(keepends=True)
    a_lines = after.splitlines(keepends=True)
    diff = list(difflib.unified_diff(b_lines, a_lines, fromfile=f"a/{name}",
                                      tofile=f"b/{name}", n=2))
    return "".join(diff)


# ────────────────── main ──────────────────


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="Write changes (default: dry-run)")
    ap.add_argument("--diff", action="store_true",
                    help="Show full diff for each changed file")
    ap.add_argument("--article", default=None,
                    help="Only sync this article slug (for testing)")
    args = ap.parse_args()

    print("===== sync-spore-links =====")
    print(f"  mode: {'APPLY (write)' if args.apply else 'DRY-RUN (read-only)'}")
    if args.article:
        print(f"  filter: {args.article} only")
    print()

    pub_rows = parse_publication_table()
    print(f"  SPORE-LOG identity rows: {len(pub_rows)}")

    canonical = build_canonical_sporelinks(pub_rows)
    print(f"  Articles with canonical sporeLinks: {len(canonical)}")
    print()

    changes = []        # knowledge/ changes
    mirror_changes = [] # src/content/ changes (independent of knowledge/ status)
    missing = []
    for slug, entries in sorted(canonical.items()):
        if args.article and slug != args.article:
            continue
        path = find_article_path(slug)
        if not path:
            missing.append(slug)
            continue
        new_block = render_sporelinks_block(entries)
        changed, before, after = update_article_sporelinks(path, new_block)
        if changed:
            changes.append((slug, path, before, after))

        # src/content/ mirror — check independently
        mirror = src_content_mirror(path)
        if mirror:
            m_changed, m_before, m_after = update_article_sporelinks(mirror, new_block)
            if m_changed:
                mirror_changes.append((slug, mirror, m_before, m_after))

    if missing:
        print(f"⚠️  {len(missing)} articles in SPORE-LOG but no knowledge/*.md found:")
        for s in missing[:10]:
            print(f"     - {s}")
        if len(missing) > 10:
            print(f"     ... ({len(missing) - 10} more)")
        print()

    if not changes and not mirror_changes:
        print("✅ All sporeLinks already in canonical form — no changes needed.")
        return 0

    if changes:
        print(f"📋 {len(changes)} knowledge/ files would change:")
        for slug, path, before, after in changes:
            rel = path.relative_to(REPO)
            if args.diff:
                print(f"\n--- {rel} ---")
                print(show_diff(before, after, str(rel)))
            else:
                b_count = before.count("\n  - ")
                a_count = after.count("\n  - ")
                print(f"  {rel} (entries {b_count} → {a_count})")

    if mirror_changes:
        print(f"\n📋 {len(mirror_changes)} src/content/ mirror files would change:")
        for slug, path, before, after in mirror_changes:
            rel = path.relative_to(REPO)
            if args.diff:
                print(f"\n--- {rel} ---")
                print(show_diff(before, after, str(rel)))
            else:
                b_count = before.count("\n  - ")
                a_count = after.count("\n  - ")
                print(f"  {rel} (entries {b_count} → {a_count})")

    if args.apply:
        for slug, path, _, after in changes:
            path.write_text(after, encoding="utf-8")
        for slug, path, _, after in mirror_changes:
            path.write_text(after, encoding="utf-8")
        print(f"\n✅ Wrote {len(changes)} knowledge files + {len(mirror_changes)} src/content mirrors.")
    else:
        print(f"\n💡 Dry-run only. Run with --apply to write changes.")
        print(f"   Inspect first: python3 {Path(__file__).name} --diff [--article SLUG]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
