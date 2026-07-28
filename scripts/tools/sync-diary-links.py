#!/usr/bin/env python3
"""sync-diary-links.py — write a diary slug into article(s) `relatedDiary` frontmatter.

## Why

When a Semiont session writes a knowledge/ article AND a reflection diary
(REWRITE-PIPELINE → DIARY-PIPELINE), the diary should be linked back into the
article frontmatter as `relatedDiary`, so readers see "what Semiont was thinking
while writing this" (rendered by src/components/RelatedDiaries.astro).

Before 2026-06-24 this back-link was a manual step that got silently skipped
(龜山島 NEW article shipped with a diary but no relatedDiary). This tool +
DIARY-PIPELINE Stage 4.5 instrument it so the link is written every time
(REFLEXES #15「反覆浮現要儀器化」).

## What it does (≠ sync-spore-links)

sync-spore-links REGENERATES sporeLinks from an SSOT (spore-log.json).
This tool APPENDS/MERGES: it adds the given diary slug to each target article's
relatedDiary, PRESERVING existing entries + excerpts, deduped by slug, idempotent.
(The diary↔article relationship is established at write time, not stored in a
separate log — the diary file is its own SSOT.)

Layer map:
  - docs/semiont/diary/{slug}.md            = diary SSOT (slug = filename stem)
  - knowledge/{Cat}/{slug}.md relatedDiary  = pointer (THIS script)
  - src/content/zh-TW/{cat}/{slug}.md       = mirror (gitignored projection)

Entry shape (matches src/content.config.ts relatedDiary + RelatedDiaries.astro):
  - 2026-06-24-142554-龜山島-rewrite                 # slug-only → title/excerpt auto-resolve
  - { slug: 2026-04-13-alpha2, excerpt: '自訂摘要…' }  # object form overrides excerpt

## Usage

  # explicit article (the rewrite session knows its slug):
  python3 scripts/tools/sync-diary-links.py --diary 2026-06-24-142554-龜山島-rewrite --article 龜山島 --apply

  # multiple articles (e.g. a Merge/Boundary session):
  ... --diary SLUG --article 龜山島 --article 宜蘭縣 --apply

  # curated excerpt override (else slug-only, auto-resolve from the diary file):
  ... --diary SLUG --article 龜山島 --excerpt '今天寫龜山島，寫到一半發現我在寫自己。' --apply

  # auto-detect newly-ADDED zh knowledge articles since a git ref (finale / cron):
  python3 scripts/tools/sync-diary-links.py --diary SLUG --auto HEAD~3 --apply

## Safety

- Default mode is dry-run — no writes without --apply.
- Idempotent: re-running with the same (diary, article) is a no-op.
- Verifies the diary file exists (typo guard — RelatedDiaries graceful-skips a
  bad slug, so a typo would silently render nothing).
- --auto only auto-includes ADDED articles (unambiguous new). MODIFIED articles
  are printed as candidates but NOT auto-linked (avoids tagging trivial edits
  like reverse cross-links); pass them via --article to confirm.

2026-06-24 龜山島-rewrite | born from 哲宇 callout「文章沒標注相關的記錄」
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DIARY_DIR = REPO / "docs/semiont/diary"
KNOWLEDGE_ROOT = REPO / "knowledge"
SRC_CONTENT_ROOT = REPO / "src/content/zh-TW"  # mirror target

# Map knowledge/ category dir → src/content/zh-TW/ slug dir (Capitalized → lower)
_CAT_MAP = {
    "Art": "art", "Culture": "culture", "Economics": "economics",
    "History": "history", "Music": "music", "Nature": "nature",
    "People": "people", "Society": "society", "Technology": "technology",
    "Geography": "geography",
}
_MIRROR_LANG_DIRS = {"en", "ja", "ko", "es", "fr", "zh-TW"}


# ────────────────── helpers ──────────────────


def _normalize_slug(slug: str) -> str:
    """Strip emoji prefix + parenthetical version markers (mirror sync-spore-links)."""
    s = re.sub(r"^[\U0001F300-\U0001FAFF☀-➿\s]+", "", slug)
    s = re.sub(r"[（(].*?[）)]\s*$", "", s)
    return s.strip()


# Greek session letters → latin, MUST mirror src/lib/semiont-diary.ts transliterateGreek
# exactly: the diary /semiont/diary/{slug} route + RelatedDiaries.astro resolve by the
# transliterated slug, so a raw-Greek slug in relatedDiary silently renders nothing.
_GREEK_MAP = {
    "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "epsilon", "ζ": "zeta",
    "η": "eta", "θ": "theta", "ι": "iota", "κ": "kappa", "λ": "lambda", "μ": "mu",
}


def _translit_greek(greek: str) -> str:
    if not greek:
        return ""
    base, suffix = greek[0], greek[1:]
    if base not in _GREEK_MAP:
        return greek.lower()  # non-Greek handle: route lowercases ASCII, CJK unaffected
    return _GREEK_MAP[base] + suffix.replace("+", "-plus").replace(" ", "")


def route_slug(filename_stem: str) -> str:
    """diary filename stem → the slug the site routes/resolves it under.

    Ports semiont-diary.ts: slug = date + ('-' + transliterateGreek(rest)). For a
    Greek session (2026-04-21-β) this differs from the filename (→ 2026-04-21-beta);
    for timestamp/CJK/descriptive handles it equals the lowercased stem.
    """
    m = re.match(r"^(\d{4}-\d{2}-\d{2})(?:-(.+))?$", filename_stem)
    if not m:
        return filename_stem
    date, rest = m.group(1), m.group(2) or ""
    return date + ("-" + _translit_greek(rest) if rest else "")


def find_article_path(slug_or_path: str) -> Path | None:
    """Find knowledge/{Cat}/{slug}.md (zh canonical). Accepts slug or knowledge/ path."""
    # If a path was passed, use it directly when it exists.
    p = Path(slug_or_path)
    if p.suffix == ".md":
        cand_abs = p if p.is_absolute() else (REPO / p)
        if cand_abs.exists():
            return cand_abs
    candidates = [slug_or_path, _normalize_slug(slug_or_path)]
    seen = set()
    for cand in candidates:
        if not cand or cand in seen:
            continue
        seen.add(cand)
        for md in KNOWLEDGE_ROOT.rglob(f"{cand}.md"):
            rel = md.relative_to(KNOWLEDGE_ROOT)
            if rel.parts and rel.parts[0] in _MIRROR_LANG_DIRS:
                continue  # skip multilingual mirrors — zh canonical only
            return md
    return None


def src_content_mirror(knowledge_path: Path) -> Path | None:
    """knowledge/Cat/{slug}.md → src/content/zh-TW/cat/{slug}.md (or None if absent)."""
    try:
        rel = knowledge_path.relative_to(KNOWLEDGE_ROOT)
    except ValueError:
        return None
    if len(rel.parts) != 2:
        return None
    cat_sc = _CAT_MAP.get(rel.parts[0], rel.parts[0].lower())
    target = SRC_CONTENT_ROOT / cat_sc / rel.parts[1]
    return target if target.exists() else None


# ────────────────── relatedDiary frontmatter parse/render ──────────────────

RELATEDDIARY_BLOCK_RE = re.compile(
    r"(?ms)^relatedDiary:[ \t]*\n(?:(?:  - .*?\n(?:    .*?\n)*)+)?",
)


def _yaml_squote(s: str) -> str:
    """Single-quote a YAML scalar, escaping internal apostrophes by doubling.

    project_babel_frontmatter_apostrophe: unescaped ' in single-quoted YAML
    breaks js-yaml → silent frontmatter loss.
    """
    return s.replace("'", "''")


def parse_existing(block_text: str) -> list[tuple[str, str | None]]:
    """Parse an existing relatedDiary block → [(slug, excerpt|None), ...].

    Handles both string items (`  - slug`) and object items (`  - slug: x` +
    optional `    excerpt: 'y'`).
    """
    entries: list[tuple[str, str | None]] = []
    lines = block_text.splitlines()
    i = 1  # skip the "relatedDiary:" header line
    while i < len(lines):
        m = re.match(r"  - (.*)", lines[i])
        if not m:
            i += 1
            continue
        item = m.group(1).strip()
        obj = re.match(r"slug:\s*(.+)", item)
        if obj:
            slug = obj.group(1).strip().strip("'\"")
            excerpt = None
            j = i + 1
            while j < len(lines) and re.match(r"    \S", lines[j]):
                em = re.match(r"    excerpt:\s*(.+)", lines[j])
                if em:
                    raw = em.group(1).strip()
                    if len(raw) >= 2 and raw[0] in "'\"" and raw[-1] == raw[0]:
                        raw = raw[1:-1].replace("''", "'")
                    excerpt = raw
                j += 1
            entries.append((slug, excerpt))
            i = j
        else:
            entries.append((item.strip("'\""), None))
            i += 1
    return entries


def render_block(entries: list[tuple[str, str | None]]) -> str:
    if not entries:
        return ""
    out = ["relatedDiary:"]
    for slug, excerpt in entries:
        if excerpt:
            out.append(f"  - slug: {slug}")
            out.append(f"    excerpt: '{_yaml_squote(excerpt)}'")
        else:
            out.append(f"  - {slug}")
    return "\n".join(out) + "\n"


def update_article(article_path: Path, diary_slug: str, excerpt: str | None):
    """Add diary_slug to article relatedDiary. Returns (changed, before, after)."""
    text = article_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False, text, text
    end = text.find("---", 3)
    if end == -1:
        return False, text, text
    fm, body = text[3:end], text[end:]

    existing_match = RELATEDDIARY_BLOCK_RE.search(fm)
    entries = parse_existing(existing_match.group(0)) if existing_match else []

    slugs = {s for s, _ in entries}
    if diary_slug in slugs:
        # already linked — but allow excerpt upgrade if a new excerpt is given
        if excerpt:
            entries = [(s, excerpt if s == diary_slug else e) for s, e in entries]
        else:
            return False, text, text
    else:
        entries.append((diary_slug, excerpt))

    new_block = render_block(entries)
    if existing_match:
        new_fm = RELATEDDIARY_BLOCK_RE.sub(new_block, fm, count=1)
    else:
        new_fm = fm.rstrip() + "\n" + new_block
    new_text = "---" + new_fm + body
    return (new_text != text), text, new_text


def _git_added_articles(since_ref: str) -> tuple[list[str], list[str]]:
    """Return (added, modified) zh knowledge article slugs since git ref."""
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-status", f"{since_ref}..HEAD"],
            cwd=REPO, text=True,
        )
    except subprocess.CalledProcessError:
        return [], []
    added, modified = [], []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, path = parts[0], parts[-1]
        m = re.match(r"knowledge/([^/]+)/(.+)\.md$", path)
        if not m or m.group(1) in _MIRROR_LANG_DIRS:
            continue
        slug = m.group(2)
        if status.startswith("A"):
            added.append(slug)
        elif status.startswith("M"):
            modified.append(slug)
    return added, modified


# ────────────────── main ──────────────────


def main() -> int:
    ap = argparse.ArgumentParser(description="Write diary slug into article relatedDiary frontmatter.")
    ap.add_argument("--diary", required=True, help="Diary slug (filename stem, e.g. 2026-06-24-142554-龜山島-rewrite)")
    ap.add_argument("--article", action="append", default=[], help="Target article slug or knowledge/ path (repeatable)")
    ap.add_argument("--auto", default=None, metavar="GIT_REF", help="Auto-include ADDED zh knowledge articles since this git ref")
    ap.add_argument("--excerpt", default=None, help="Curated excerpt override (else slug-only, auto-resolve from diary)")
    ap.add_argument("--apply", action="store_true", help="Write changes (default: dry-run)")
    args = ap.parse_args()

    print("===== sync-diary-links =====")
    print(f"  mode:  {'APPLY (write)' if args.apply else 'DRY-RUN (read-only)'}")
    print(f"  diary: {args.diary}")

    # Typo guard: diary file must exist (RelatedDiaries graceful-skips bad slugs silently).
    if not (DIARY_DIR / f"{args.diary}.md").exists():
        print(f"  ⚠️  diary file not found: docs/semiont/diary/{args.diary}.md — aborting (typo?)")
        return 2

    # The STORED slug must match the site route (Greek transliterated); the file check
    # above uses the raw filename. They differ only for Greek-session diaries.
    diary_slug = route_slug(args.diary)
    if diary_slug != args.diary:
        print(f"  slug:  {diary_slug}  (transliterated from {args.diary})")

    targets = list(args.article)
    if args.auto:
        added, modified = _git_added_articles(args.auto)
        if added:
            print(f"  auto (ADDED, linked): {', '.join(added)}")
            targets.extend(added)
        if modified:
            print(f"  auto (MODIFIED, NOT auto-linked — pass --article to confirm): {', '.join(modified)}")
    # dedup targets preserving order
    targets = list(dict.fromkeys(targets))

    if not targets:
        print("  no target articles (use --article or --auto). nothing to do.")
        return 0

    changed_any = False
    for slug in targets:
        path = find_article_path(slug)
        if not path:
            print(f"  ✗ {slug}: article not found in knowledge/")
            continue
        rel = path.relative_to(REPO)
        changed, _, after = update_article(path, diary_slug, args.excerpt)
        mirror = src_content_mirror(path)
        if not changed:
            print(f"  ＝ {rel}: already linked (no-op)")
        else:
            print(f"  ✓ {rel}: + relatedDiary[{diary_slug}]")
            if args.apply:
                path.write_text(after, encoding="utf-8")
            changed_any = True
        # mirror (independent — may already match or be absent)
        if mirror:
            m_changed, _, m_after = update_article(mirror, diary_slug, args.excerpt)
            if m_changed:
                print(f"     ↳ mirror {mirror.relative_to(REPO)}")
                if args.apply:
                    mirror.write_text(m_after, encoding="utf-8")

    if not args.apply and changed_any:
        print("\n  (dry-run) re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
