/**
 * Build-time search index generator.
 *
 * Reads all markdown articles from knowledge/, tokenizes title/description/tags
 * with CJK bigrams + Latin words, builds serialized MiniSearch indexes.
 *
 * Output（2026-06-13 RAG Phase 0 — 六語系 per-lang shard）:
 *   public/api/search-minisearch-{lang}.json   ×6（每語言一份，client 按
 *     <html lang> 抓自己的 shard — 修復 ja/ko/es/fr 讀者搜尋零母語結果的洞，
 *     詳 reports/research/2026-06/rag-design-research-2026-06-13.md Phase 0）
 *   public/api/search-minisearch.json          legacy combined zh+en
 *     （back-compat：已部署/快取頁面的舊 client 仍指這個 URL，不能斷）
 *
 * 語言清單從 src/config/languages.mjs SSOT 讀（REFLEXES #20 architecture-as-data，
 * 新語言出生時本檔零改動）。
 */

import { readdir, readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve, join, basename } from 'node:path';
import matter from 'gray-matter';
import MiniSearch from 'minisearch';
import {
  ENABLED_LANGUAGE_CODES,
  DEFAULT_LANGUAGE,
} from '../../src/config/languages.mjs';

const CATEGORY_MAP = {
  history: 'History',
  geography: 'Geography',
  culture: 'Culture',
  food: 'Food',
  art: 'Art',
  music: 'Music',
  technology: 'Technology',
  nature: 'Nature',
  people: 'People',
  politics: 'Politics',
  society: 'Society',
  economy: 'Economy',
  lifestyle: 'Lifestyle',
};

// ── CJK bigram tokenizer ──

const isCJK = (cp) =>
  (cp >= 0x4e00 && cp <= 0x9fff) ||
  (cp >= 0x3400 && cp <= 0x4dbf) ||
  (cp >= 0xf900 && cp <= 0xfaff) ||
  (cp >= 0x3100 && cp <= 0x312f) ||
  // 2026-06-13 Phase 0：ja 假名 + ko 諺文也走 bigram（原本只有漢字，
  // ja/ko shard 的母語 query 打不中 — ko shard 421KB vs 他語 1.2MB+ 暴露的洞）
  (cp >= 0x3040 && cp <= 0x30ff) || // Hiragana + Katakana
  (cp >= 0x31f0 && cp <= 0x31ff) || // Katakana phonetic extensions
  (cp >= 0xac00 && cp <= 0xd7a3); // Hangul syllables

const LATIN_RE = /[a-z0-9][a-z0-9-]*[a-z0-9]|[a-z0-9]/g;

function bigramTokenize(text) {
  if (!text) return '';
  const normalized = text.toLowerCase().normalize('NFKC');
  const tokens = [];

  // Latin words (2+ chars)
  for (const m of normalized.matchAll(LATIN_RE)) {
    if (m[0].length >= 2) tokens.push(m[0]);
  }

  // CJK bigrams（ja 漢字/假名混排與 ko 諺文走 NFKC 後的 Latin/CJK 雙路；
  // 假名與諺文不在 isCJK 範圍時由 MiniSearch prefix match 接住 Latin 化查詢，
  // 母語標題的 CJK 漢字 bigram 仍為主要召回路徑）
  const chars = [...normalized];
  for (let i = 0; i < chars.length - 1; i++) {
    const cp1 = chars[i].codePointAt(0);
    const cp2 = chars[i + 1].codePointAt(0);
    if (isCJK(cp1) && isCJK(cp2)) {
      tokens.push(chars[i] + chars[i + 1]);
    }
  }

  return tokens.join(' ');
}

// ── Scan one language's articles ──

async function scanLang(lang, startId) {
  const docs = [];
  let id = startId;
  const isDefault = lang === DEFAULT_LANGUAGE.code;

  for (const [slug, folder] of Object.entries(CATEGORY_MAP)) {
    const dirPath = isDefault
      ? resolve(process.cwd(), 'knowledge', folder)
      : resolve(process.cwd(), 'knowledge', lang, folder);
    try {
      const files = (await readdir(dirPath)).filter(
        (f) => f.endsWith('.md') && !f.startsWith('_'),
      );
      for (const file of files) {
        try {
          const { data } = matter(await readFile(join(dirPath, file), 'utf-8'));
          const name = basename(file, '.md');
          const title = data.title || name;
          const description = data.description || '';
          const tags = Array.isArray(data.tags)
            ? data.tags
            : data.tags
              ? [data.tags]
              : [];
          docs.push({
            id: id++,
            t: title,
            d: description,
            u: isDefault ? `/${slug}/${name}` : `/${lang}/${slug}/${name}`,
            tags,
            lang,
            title_bigram: bigramTokenize(title),
            desc_bigram: bigramTokenize(description),
            tags_bigram: bigramTokenize(tags.join(' ')),
          });
        } catch {
          console.warn(`[search] skipped ${lang}/${file}: YAML parse error`);
        }
      }
    } catch (err) {
      if (err.code !== 'ENOENT')
        console.warn(`[search] error reading ${dirPath}:`, err.message);
    }
  }

  return docs;
}

// ── Build one serialized MiniSearch index from docs ──

function buildIndex(docs) {
  const miniSearch = new MiniSearch({
    idField: 'id',
    fields: ['title_bigram', 'desc_bigram', 'tags_bigram'],
    storeFields: ['t', 'd', 'u', 'tags', 'lang'],
    tokenize: (text) => text.split(/\s+/).filter(Boolean),
    searchOptions: {
      boost: { title_bigram: 6, tags_bigram: 4, desc_bigram: 2 },
      prefix: true,
    },
  });
  miniSearch.addAll(docs);
  return JSON.stringify(miniSearch);
}

// ── Main ──

const apiDir = resolve(process.cwd(), 'public', 'api');
await mkdir(apiDir, { recursive: true });

const docsByLang = new Map();
let nextId = 0;
for (const lang of ENABLED_LANGUAGE_CODES) {
  const docs = await scanLang(lang, nextId);
  nextId += docs.length;
  docsByLang.set(lang, docs);
}

// Per-lang shards ×6
for (const [lang, docs] of docsByLang) {
  const serialized = buildIndex(docs);
  await writeFile(
    join(apiDir, `search-minisearch-${lang}.json`),
    serialized,
    'utf-8',
  );
  console.log(
    `[search] shard ${lang}: ${docs.length} docs, ${(serialized.length / 1024).toFixed(0)} KB → search-minisearch-${lang}.json`,
  );
}

// Legacy combined zh+en（back-compat：舊 client / 快取 HTML 仍 fetch 這個 URL）
const legacyDocs = [
  ...(docsByLang.get(DEFAULT_LANGUAGE.code) || []),
  ...(docsByLang.get('en') || []),
];
const legacySerialized = buildIndex(legacyDocs);
await writeFile(
  join(apiDir, 'search-minisearch.json'),
  legacySerialized,
  'utf-8',
);
console.log(
  `[search] legacy combined zh+en: ${legacyDocs.length} docs, ${(legacySerialized.length / 1024).toFixed(0)} KB → search-minisearch.json`,
);

// Plain-array fallback for Layout.astro's indexOf path (used only when
// MiniSearch fails to load). 2026-06-13 EVO-A2: this REPLACES the duplicate
// runtime route src/pages/api/search-index.json.ts, which re-scanned knowledge/
// with its OWN category map that had drifted (missing politics, zh+en only).
// Derived from legacyDocs = the same single scan → zh+en, all categories, no
// drift. Strip the bigram fields; keep the {t,d,u,tags,lang} shape the old
// route emitted so Layout's fallback is unchanged.
const fallbackDocs = legacyDocs.map((d) => ({
  t: d.t,
  d: d.d,
  u: d.u,
  tags: d.tags,
  lang: d.lang,
}));
await writeFile(
  join(apiDir, 'search-index.json'),
  JSON.stringify(fallbackDocs),
  'utf-8',
);
console.log(
  `[search] fallback plain index: ${fallbackDocs.length} docs (zh+en) → search-index.json`,
);
