/**
 * articles-index.ts — Module-level shared frontmatter cache for all [slug].astro
 *
 * 為什麼：6 個 [slug].astro（zh + en + ja + ko + es + fr）每個 page render 都
 * 重做「relatedArticles 同 category 掃 + allArticles 全 category 掃」= readdir
 * + readFile + matter() loop。每篇文章 × N 篇同 cat + N×14 篇跨 cat = O(N²)
 * 重複工作。Article page 6950 × 這個 loop = build time 主要 hot path 之一。
 *
 * 本模組把整個 lang 的 article index 在 module 第一次呼叫時 build 完整次，
 * 後續所有 [slug].astro page render 共享同一個 in-memory Map。Build 整 process
 * 只 readdir 一次 + readFile 一次 + matter 一次 per file。
 *
 * 2026-05-03 sleepy-colden Tier 1.4 build-perf optimization。
 */

import { readdir, readFile } from 'node:fs/promises';
import { resolve, join, basename } from 'node:path';
import matter from 'gray-matter';

export interface ArticleSummary {
  title: string;
  slug: string;
  description: string;
  image: string;
  category: string; // category slug (lowercase)
  readingTime?: number; // frontmatter readingTime (分鐘)
  tags?: string[]; // frontmatter tags
  footnotes?: number; // count of [^n]: footnote definitions (引用深度訊號)
}

const CATEGORY_MAPPING: Record<string, string> = {
  about: 'About',
  history: 'History',
  geography: 'Geography',
  culture: 'Culture',
  food: 'Food',
  art: 'Art',
  music: 'Music',
  technology: 'Technology',
  nature: 'Nature',
  people: 'People',
  society: 'Society',
  economy: 'Economy',
  lifestyle: 'Lifestyle',
  politics: 'Politics',
};

function safeMatter(fileContent: string): {
  data: Record<string, any>;
  content: string;
} {
  try {
    return matter(fileContent) as any;
  } catch {
    const stripped = fileContent.replace(/^---\s*\n[\s\S]*?\n---\s*\n/, '');
    return { data: {}, content: stripped };
  }
}

// Per-lang cache. 'zh-TW' reads knowledge/{Cat}/, others read knowledge/{lang}/{Cat}/
const _cache = new Map<string, Promise<Map<string, ArticleSummary[]>>>();

async function buildIndex(
  lang: string,
): Promise<Map<string, ArticleSummary[]>> {
  const result = new Map<string, ArticleSummary[]>();
  for (const [catSlug, folderName] of Object.entries(CATEGORY_MAPPING)) {
    const folderPath =
      lang === 'zh-TW'
        ? resolve(process.cwd(), 'knowledge', folderName)
        : resolve(process.cwd(), 'knowledge', lang, folderName);
    try {
      const files = await readdir(folderPath);
      const articles: ArticleSummary[] = [];
      for (const file of files) {
        if (!file.endsWith('.md') || file.startsWith('_')) continue;
        const articleSlug = basename(file, '.md');
        const filePath = join(folderPath, file);
        try {
          const fileContent = await readFile(filePath, 'utf-8');
          const { data: fm } = safeMatter(fileContent);
          // Footnote definitions ([^n]:) — citation-depth signal, same count
          // explore.template uses for its featured deep-dive cards.
          const footnotes = (fileContent.match(/^\[\^\d+\]:/gm) || []).length;
          articles.push({
            title: fm.title || articleSlug,
            slug: articleSlug,
            description: fm.description || '',
            image: fm.image || '',
            category: catSlug,
            readingTime:
              typeof fm.readingTime === 'number' ? fm.readingTime : undefined,
            tags: Array.isArray(fm.tags) ? fm.tags : undefined,
            footnotes,
          });
        } catch {
          // unreadable file — skip silently
        }
      }
      result.set(catSlug, articles);
    } catch {
      // missing category folder for this lang — skip
    }
  }
  return result;
}

/**
 * Get articles index for a language (zh-TW / en / ja / ko / es / fr).
 * First call: builds the index by reading all knowledge files; subsequent
 * calls within the same process return the cached Map.
 */
export function getArticlesIndex(
  lang: string,
): Promise<Map<string, ArticleSummary[]>> {
  let entry = _cache.get(lang);
  if (!entry) {
    entry = buildIndex(lang);
    _cache.set(lang, entry);
  }
  return entry;
}

/* ───────────────────────────────────────────────────────────────────────────
 * Semantic related articles (RAG Phase 1, 2026-06-14)
 *
 * src/data/related/{lang}.json maps `${cat}/${slug}` → up to 5 nearest-neighbour
 * `${cat}/${slug}` strings, pre-computed offline from bge-m3 embeddings on the
 * GPU fleet (scripts/core/build-embeddings.mjs → slimmed to slug-only). The
 * reader gets cross-topic semantic neighbours (e.g. a 戒嚴 article surfaces a
 * 白色恐怖 piece in a different category) instead of same-category proximity —
 * with ZERO browser model: the links are baked into the article HTML at build.
 *
 * Graceful degrade: if the file is absent (CI build without a fleet rebuild) or
 * the article isn't in the map, getRelatedArticles falls back to the original
 * same-category behaviour. Architecture: reports/research/2026-06/
 * p0-compute-experiments-2026-06-14.md + rag-design-research-2026-06-13.md.
 * ──────────────────────────────────────────────────────────────────────────*/

const _semanticRelated = new Map<string, Promise<Record<string, string[]>>>();
function loadSemanticRelated(lang: string): Promise<Record<string, string[]>> {
  let entry = _semanticRelated.get(lang);
  if (!entry) {
    entry = readFile(
      resolve(process.cwd(), 'src/data/related', `${lang}.json`),
      'utf-8',
    )
      .then((raw) => {
        try {
          return JSON.parse(raw) as Record<string, string[]>;
        } catch {
          return {};
        }
      })
      .catch(() => ({})); // no semantic index → category fallback
    _semanticRelated.set(lang, entry);
  }
  return entry;
}

// Flat `${cat}/${slug}` → ArticleSummary lookup, memoised per lang. Lets the
// semantic neighbour slugs resolve back to full summaries for the card render.
const _bySlug = new Map<string, Promise<Map<string, ArticleSummary>>>();
function getBySlugIndex(lang: string): Promise<Map<string, ArticleSummary>> {
  let entry = _bySlug.get(lang);
  if (!entry) {
    entry = getArticlesIndex(lang).then((index) => {
      const flat = new Map<string, ArticleSummary>();
      for (const [cat, articles] of index) {
        for (const a of articles) flat.set(`${cat}/${a.slug}`, a);
      }
      return flat;
    });
    _bySlug.set(lang, entry);
  }
  return entry;
}

/**
 * Related articles for the article-page footer. Prefers semantic neighbours
 * (cross-category, meaning-based) from the pre-computed index; falls back to
 * same-category proximity when the semantic index is absent or the article is
 * not indexed. Return shape is unchanged (ArticleSummary[]) so callers and the
 * shared ArticleCard (premium) need no changes.
 */
export async function getRelatedArticles(
  lang: string,
  category: string,
  excludeSlug: string,
  limit = 3,
): Promise<ArticleSummary[]> {
  const index = await getArticlesIndex(lang);

  // Semantic first.
  const semantic = await loadSemanticRelated(lang);
  const neighbours = semantic[`${category}/${excludeSlug}`];
  if (neighbours && neighbours.length) {
    const bySlug = await getBySlugIndex(lang);
    const out: ArticleSummary[] = [];
    for (const key of neighbours) {
      const art = bySlug.get(key);
      if (art && art.slug !== excludeSlug) out.push(art);
      if (out.length >= limit) break;
    }
    if (out.length) return out;
  }

  // Fallback: same-category proximity (original behaviour).
  const inCategory = index.get(category) ?? [];
  return inCategory.filter((a) => a.slug !== excludeSlug).slice(0, limit);
}

/**
 * Convenience: all articles across all categories (for "explore more" widgets).
 */
export async function getAllArticles(
  lang: string,
  excludeCategory?: string,
): Promise<ArticleSummary[]> {
  const index = await getArticlesIndex(lang);
  const out: ArticleSummary[] = [];
  for (const [cat, articles] of index) {
    if (cat === excludeCategory) continue;
    for (const a of articles) out.push(a);
  }
  return out;
}

/* ───────────────────────────────────────────────────────────────────────────
 * Latest articles (時序主軸) — joins the article index with content-dates.json
 * (git last-content-change times) so "latest" reflects when an article was
 * actually shipped, not a hand-set frontmatter date. Used by the /latest page,
 * the /explore section, the homepage strip, and (via /api/latest.json) the
 * client-side article-page rail. Design: reports/latest-articles-discoverability
 * -design-2026-06-09.md §4.
 * ──────────────────────────────────────────────────────────────────────────*/

export interface DatedArticle extends ArticleSummary {
  date: string; // ISO 8601 git-ship timestamp
}

let _contentDates: Promise<Record<string, string>> | null = null;
function loadContentDates(): Promise<Record<string, string>> {
  if (!_contentDates) {
    _contentDates = readFile(
      resolve(process.cwd(), 'src/data/content-dates.json'),
      'utf-8',
    )
      .then((raw) => {
        try {
          return (JSON.parse(raw).dates as Record<string, string>) ?? {};
        } catch {
          return {};
        }
      })
      .catch(() => ({}));
  }
  return _contentDates;
}

// URL key aligned with content-dates.json: zh-TW → `/${cat}/${slug}/`,
// other langs → `/${lang}/${cat}/${slug}/` (raw, not percent-encoded).
function latestUrlKey(lang: string, cat: string, slug: string): string {
  return lang === 'zh-TW' ? `/${cat}/${slug}/` : `/${lang}/${cat}/${slug}/`;
}

/**
 * Latest articles across all categories for a language, newest-first by git
 * ship time. Articles without a content-dates entry, plus the `about` meta
 * folder, are excluded. `excludeSlug` drops the current article (for the rail).
 */
export async function getLatestArticles(
  lang: string,
  limit = 12,
  excludeSlug?: string,
): Promise<DatedArticle[]> {
  const [all, dates] = await Promise.all([
    getAllArticles(lang),
    loadContentDates(),
  ]);
  const out: DatedArticle[] = [];
  for (const a of all) {
    if (a.category === 'about') continue;
    if (excludeSlug && a.slug === excludeSlug) continue;
    const date = dates[latestUrlKey(lang, a.category, a.slug)] ?? '';
    if (!date) continue;
    out.push({ ...a, date });
  }
  // Newest first by epoch — robust even if content-dates mixes timezone
  // formats (lexicographic compare breaks on Z vs +08:00). Stable sort keeps
  // same-second batch entries in index order.
  out.sort((x, y) => Date.parse(y.date) - Date.parse(x.date));
  return out.slice(0, limit);
}
