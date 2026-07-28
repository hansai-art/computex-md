#!/usr/bin/env python3
"""fetch-pansci-data.py — PanSci 泛科學 peer content ingester

PanSci 是 COMPUTEX.md 第一個正式簽 MOU 的 Content Curation Partner（2026-05-05）。

授權範圍：166 篇 explicit authorize list (data/PanSci/_authorization/authorize-list.json)
其他 14,061 篇 follow 一般 footnote 引用規範（不在本 crawler scope）

Idempotent crawler — 可重跑、保留 provenance:
- 每篇 post 一個 .md（frontmatter + 全文）
- raw JSON 存 data/PanSci/raw/ provenance
- manifest.json 記錄爬取時間 / 總量
- 嚴格 rate limit（≥1s 避免被 block）+ retry

Usage:
    python3 scripts/tools/fetch-pansci-data.py
    python3 scripts/tools/fetch-pansci-data.py --dry-run
    python3 scripts/tools/fetch-pansci-data.py --refresh-meta-only

References:
    - MOU: data/PanSci/_authorization/ (gitignored PDF)
    - 授權清單: data/PanSci/_authorization/authorize-list.json
    - PEER-INGESTION-PIPELINE.md Stage 2
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
import urllib.request
import urllib.error

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PANSCI_DIR = REPO_ROOT / 'data' / 'PanSci'
AUTH_LIST = PANSCI_DIR / '_authorization' / 'authorize-list.json'
ARTICLES_DIR = PANSCI_DIR / 'authorized'
RAW_DIR = PANSCI_DIR / 'raw'
MANIFEST_PATH = RAW_DIR / 'manifest.json'

UA = 'COMPUTEX.md PanSci-ingester/1.0 (Content Curation Partner per MOU 2026-05-05; contact@computex.md)'
BASE = 'https://pansci.asia/wp-json/wp/v2'
RATE_LIMIT_SEC = 1.2  # WordPress.com / Cloudflare-fronted blogs 通常 60+/min OK，但保守起見
MAX_RETRIES = 4


def http_get(url, timeout=30):
    """GET with UA + retries + exponential backoff."""
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Accept': 'application/json',
    })
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503) and attempt < MAX_RETRIES:
                backoff = 3 * attempt
                print(f'   ⏸ HTTP {e.code} retry in {backoff}s (attempt {attempt + 1})', file=sys.stderr)
                time.sleep(backoff)
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < MAX_RETRIES:
                time.sleep(2 * attempt)
                continue
            raise
    raise RuntimeError(f'Failed after {MAX_RETRIES} retries: {url}')


def html_to_markdown(html):
    """Lightweight HTML → markdown converter (no external deps).

    Handles: headings / paragraphs / links / lists / images / bold/em / blockquotes.
    Preserves enough fidelity for Stage 4 analysis reading; not pixel-perfect.
    """
    if not html:
        return ''
    s = html
    # Block-level
    s = re.sub(r'<h1[^>]*>(.*?)</h1>', r'\n# \1\n', s, flags=re.S | re.I)
    s = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n## \1\n', s, flags=re.S | re.I)
    s = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n### \1\n', s, flags=re.S | re.I)
    s = re.sub(r'<h4[^>]*>(.*?)</h4>', r'\n#### \1\n', s, flags=re.S | re.I)
    s = re.sub(r'<h5[^>]*>(.*?)</h5>', r'\n##### \1\n', s, flags=re.S | re.I)
    s = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', lambda m: '\n' + '\n'.join('> ' + ln for ln in m.group(1).strip().split('\n')) + '\n', s, flags=re.S | re.I)
    s = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', s, flags=re.S | re.I)
    s = re.sub(r'</?[uo]l[^>]*>', '\n', s, flags=re.I)
    s = re.sub(r'<p[^>]*>(.*?)</p>', r'\n\1\n', s, flags=re.S | re.I)
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.I)
    # Inline
    s = re.sub(r'<(strong|b)[^>]*>(.*?)</\1>', r'**\2**', s, flags=re.S | re.I)
    s = re.sub(r'<(em|i)[^>]*>(.*?)</\1>', r'*\2*', s, flags=re.S | re.I)
    s = re.sub(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', s, flags=re.S | re.I)
    s = re.sub(r'<img[^>]*alt="([^"]*)"[^>]*src="([^"]+)"[^>]*/?>', r'\n![\1](\2)\n', s, flags=re.I)
    s = re.sub(r'<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"[^>]*/?>', r'\n![\2](\1)\n', s, flags=re.I)
    s = re.sub(r'<img[^>]*src="([^"]+)"[^>]*/?>', r'\n![](\1)\n', s, flags=re.I)
    # Strip remaining tags
    s = re.sub(r'<script[^>]*>.*?</script>', '', s, flags=re.S | re.I)
    s = re.sub(r'<style[^>]*>.*?</style>', '', s, flags=re.S | re.I)
    s = re.sub(r'<[^>]+>', '', s)
    # Entity decode (basic)
    s = (s.replace('&nbsp;', ' ').replace('&amp;', '&')
         .replace('&lt;', '<').replace('&gt;', '>')
         .replace('&quot;', '"').replace('&#8217;', "'").replace('&#8220;', '"')
         .replace('&#8221;', '"').replace('&#8211;', '–').replace('&#8212;', '—'))
    # Collapse blank lines
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()


def extract_links(html):
    """Extract all external/internal URLs from HTML for provenance."""
    if not html:
        return [], []
    urls = re.findall(r'href="([^"]+)"', html, flags=re.I)
    ext, int_ = [], []
    for u in urls:
        if u.startswith('http://pansci.asia') or u.startswith('https://pansci.asia') or u.startswith('/'):
            int_.append(u)
        elif u.startswith('http'):
            ext.append(u)
    # Dedupe while preserving order
    seen_e, seen_i = set(), set()
    ext = [u for u in ext if not (u in seen_e or seen_e.add(u))]
    int_ = [u for u in int_ if not (u in seen_i or seen_i.add(u))]
    return ext, int_


def fetch_post(wp_id):
    """Fetch single WP post by ID, return parsed JSON."""
    url = f'{BASE}/posts/{wp_id}?_embed=true'
    return http_get(url)


def safe_slug(s, fallback):
    """Make filesystem-safe filename slug; fallback if title has special chars."""
    s = re.sub(r'[\\/:*?"<>|]', '_', s or '')
    s = s.strip().rstrip('.')[:80]  # truncate
    return s or fallback


def write_post_md(post, auth_entry, out_path):
    """Convert WordPress post + authorization entry to COMPUTEX.md-style markdown."""
    title = post.get('title', {}).get('rendered', '') or auth_entry.get('title', '')
    excerpt_html = post.get('excerpt', {}).get('rendered', '') or ''
    content_html = post.get('content', {}).get('rendered', '') or ''
    excerpt_md = html_to_markdown(excerpt_html)
    content_md = html_to_markdown(content_html)
    ext_links, int_links = extract_links(content_html)

    # Embedded author / featured media
    author_name = auth_entry.get('author', '')
    if not author_name:
        emb_authors = (post.get('_embedded', {}) or {}).get('author', []) or []
        if emb_authors:
            author_name = emb_authors[0].get('name', '')
    featured_url = ''
    media = (post.get('_embedded', {}) or {}).get('wp:featuredmedia', []) or []
    if media:
        featured_url = media[0].get('source_url', '')

    cats = ', '.join(auth_entry.get('categories', []))
    tags = ', '.join(auth_entry.get('tags', []))
    published = post.get('date_gmt') or auth_entry.get('published', '')
    modified = post.get('modified_gmt', '')

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8') as f:
        f.write(f'# {title}\n\n')
        f.write(f'- Source: {auth_entry.get("url", "")}\n')
        f.write(f'- API: {BASE}/posts/{auth_entry["wp_id"]}\n')
        f.write(f'- Type: post\n')
        f.write(f'- WordPress ID: {auth_entry["wp_id"]}\n')
        f.write(f'- Slug: {post.get("slug", "")}\n')
        f.write(f'- Published: {published}\n')
        f.write(f'- Modified: {modified}\n')
        f.write(f'- Author: {author_name}\n')
        f.write(f'- Categories: {cats}\n')
        f.write(f'- Tags: {tags}\n')
        f.write(f'- Featured Image: {featured_url or "none"}\n')
        f.write(f'- Word Count (Excel): {auth_entry.get("word_count", "")}\n')
        f.write(f'- Science Student Article: {"Y" if auth_entry.get("science_student") else "N"}\n')
        f.write(f'- Authorization: ✅ MOU 2026-05-05 / 完整授權/轉寫\n')
        f.write(f'\n## Excerpt\n\n{excerpt_md}\n')
        f.write(f'\n## Content\n\n{content_md}\n')
        f.write(f'\n## External Links\n\n')
        for u in ext_links:
            f.write(f'- {u}\n')
        f.write(f'\n## Internal Links\n\n')
        for u in int_links:
            f.write(f'- {u}\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='print plan, do not fetch')
    ap.add_argument('--limit', type=int, default=0, help='only fetch first N (testing)')
    ap.add_argument('--skip-existing', action='store_true', default=True, help='skip if markdown exists')
    args = ap.parse_args()

    if not AUTH_LIST.exists():
        print(f'❌ 授權清單不存在: {AUTH_LIST}', file=sys.stderr)
        sys.exit(1)

    with AUTH_LIST.open(encoding='utf-8') as f:
        auth_data = json.load(f)

    articles = auth_data['articles']
    if args.limit:
        articles = articles[:args.limit]
    print(f'📋 授權清單載入：{len(articles)} 篇')
    print(f'   MOU: {auth_data["mou_signed"]} → {auth_data["mou_expires"]}')
    print(f'   License: {auth_data["license"]}')

    if args.dry_run:
        for a in articles[:5]:
            print(f'  - [{a["wp_id"]}] {a["title"][:50]}')
        print(f'   ... ({len(articles)} total)')
        return

    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    fetched, skipped, failed = 0, 0, 0
    raw_posts = []

    for i, a in enumerate(articles):
        wp_id = a['wp_id']
        slug = safe_slug(a.get('title', ''), f'pansci-{wp_id}')
        md_path = ARTICLES_DIR / f'{wp_id}-{slug}.md'

        if args.skip_existing and md_path.exists():
            skipped += 1
            continue

        print(f'[{i+1}/{len(articles)}] {wp_id} — {a["title"][:50]}')
        try:
            post = fetch_post(wp_id)
            write_post_md(post, a, md_path)
            raw_posts.append(post)
            fetched += 1
        except urllib.error.HTTPError as e:
            print(f'   ❌ HTTP {e.code} — {a["url"]}', file=sys.stderr)
            failed += 1
        except Exception as e:
            print(f'   ❌ {type(e).__name__}: {e}', file=sys.stderr)
            failed += 1
        time.sleep(RATE_LIMIT_SEC)

    # Save raw provenance batch
    if raw_posts:
        with (RAW_DIR / 'posts.json').open('w', encoding='utf-8') as f:
            json.dump(raw_posts, f, ensure_ascii=False, indent=2)

    # Fetch categories & tags (one-shot, paginated)
    print('\n📦 抓 categories / tags / users metadata...')
    for endpoint, fname in [('categories', 'categories.json'), ('tags', 'tags.json')]:
        try:
            all_items = []
            page = 1
            while True:
                items = http_get(f'{BASE}/{endpoint}?per_page=100&page={page}')
                if not items:
                    break
                all_items.extend(items)
                if len(items) < 100:
                    break
                page += 1
                time.sleep(0.6)
            with (RAW_DIR / fname).open('w', encoding='utf-8') as f:
                json.dump(all_items, f, ensure_ascii=False, indent=2)
            print(f'   ✅ {fname}: {len(all_items)} items')
        except Exception as e:
            print(f'   ⚠️  {fname} failed: {e}')

    # Manifest
    manifest = {
        'peer': 'PanSci',
        'fetched_at': datetime.now(timezone.utc).isoformat(),
        'mou_signed': auth_data['mou_signed'],
        'mou_expires': auth_data['mou_expires'],
        'partnership_label': auth_data['partnership_label'],
        'authorized_total': len(auth_data['articles']),
        'this_run': {
            'fetched': fetched,
            'skipped_existing': skipped,
            'failed': failed,
        },
    }
    with MANIFEST_PATH.open('w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f'\n=== Summary ===')
    print(f'  📥 Fetched this run: {fetched}')
    print(f'  ⏭️  Skipped existing: {skipped}')
    print(f'  ❌ Failed: {failed}')
    print(f'  📁 Articles: {ARTICLES_DIR}')
    print(f'  📋 Manifest: {MANIFEST_PATH}')


if __name__ == '__main__':
    main()
