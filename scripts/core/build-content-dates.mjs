#!/usr/bin/env node
/**
 * Prebuild: src/data/content-dates.json
 * Accurate per-URL "last meaningful modification" date for SEO freshness.
 *
 * WHY (2026-06-07 SEO 完整修復 — reports/seo-optimization-plan-2026-06-07.md §1.1):
 *   The sitemap used a global `lastmod: new Date()` → every page claimed
 *   "modified today" on every build. Google's docs name this exact anti-pattern
 *   ("Don't set the last modification time to the current time whenever the
 *   sitemap is served") and respond by distrusting the site's lastmod entirely,
 *   killing the crawl-scheduling benefit. Separately, Article JSON-LD
 *   dateModified always equalled datePublished, so EVOLVE'd articles never
 *   signalled freshness.
 *
 * WHAT:
 *   One git pass over knowledge/ (the SSOT). For each article file, take the
 *   newest commit date that is NOT cosmetic/automated — so a nightly babel run
 *   or a lint sweep never fakes freshness (Google's "artificially refreshing"
 *   red flag). Author-date (%aI) is used = wall-clock ISO-8601 with timezone,
 *   exactly the format Google wants (and consistent with the repo's wall-clock
 *   timestamp discipline). Output is keyed by site URL path.
 *
 * CONSUMED BY:
 *   - astro.config.mjs  → per-URL sitemap <lastmod>
 *   - src/templates/article.template.astro → Article JSON-LD dateModified
 *   Both reading one source keeps visible/structured dates consistent (another
 *   Google requirement).
 *
 * SAFETY: a file whose every commit is cosmetic (e.g. a translation only ever
 *   touched by babel) is omitted → consumers fall back to frontmatter.date,
 *   which is conservative (a stale-but-true date, never a fake-fresh one).
 */
import { execSync } from 'node:child_process';
import { writeFileSync, mkdirSync, readdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import {
  ENABLED_LANGUAGE_CODES,
  DEFAULT_LANGUAGE,
} from '../../src/config/languages.mjs';
import { FOLDER_TO_SLUG } from '../../src/config/categories.mjs';

const ROOT = process.cwd();
const OUT = resolve(ROOT, 'src/data/content-dates.json');

// knowledge/ category folder (capitalised) → URL slug (lowercase)
// 2026-07-29：這裡原本是母體 14 分類的硬編副本。這個物種的分類不同，於是每個
// 檔案路徑都比對不到分類，dates 產出 0 筆，`/latest` 與 sitemap lastmod 全空，
// 而 build 只印一行 warning 就過去了。改吃 SSOT（src/config/categories.mjs）。
const CAT_TO_SLUG = FOLDER_TO_SLUG;
// Derive from the language registry (SSOT) — no hardcoded array (REFLEXES #20).
const NON_DEFAULT_LANGS = new Set(
  ENABLED_LANGUAGE_CODES.filter((c) => c !== DEFAULT_LANGUAGE.code),
);

// Commit subjects that do NOT represent a meaningful content change.
// Excluding them stops nightly babel / lint / routine sweeps from faking
// freshness. Tuned to COMPUTEX.md's commit conventions (git log inspected).
const COSMETIC =
  /(\[routine\]|babel|prettier|\blint\b|^🧬 \[semiont\] chore|format-only|translate\(|apostrophe|simplified-char|繁簡)/i;

// Spore lifecycle commits (ship / harvest backfill / sporeLinks pointer sync)
// touch article frontmatter only — publishing or measuring a spore is NOT an
// article content change. Without this, 34/57 spore-carrying articles had
// their /latest position + sitemap lastmod set by spore ops (2026-06-10
// audit, reports/spore-data-architecture-2026-06-10.md §2.3). Type-position
// anchors keep real fixes like「heal: … 孢子 #132 查證抓出文章 date error」
// counting as content. Belt-and-suspenders: since the same report's refactor,
// harvest no longer writes article files at all.
const SPORE_POINTER =
  /(^🧬 \[semiont\] (spore|harvest)\b|^🧬 \[harvest|fix\(spore\)|evolve\+harvest|feat: spore SSOT cleanup|衍生資料同步|sporeLinks)/i;

// Image / media-only operations (supplement hero+inline images, optimize, WebP
// migrate, cache, fix image refs) touch article bodies but do NOT change prose —
// they should not reset SEO-freshness / /latest position. Without this, the
// 2026-06-13 WebP migration (570 articles, mechanical .jpg→.webp) + media-
// supplement batches set 580 articles' /latest date to one single day. Adding
// media is an enrichment, not a content-freshness event (user directive
// 2026-06-13: 補圖不該把文章擠到「最新文章」今天). Errs toward conservative
// (stale-but-true) per this file's stated principle, never fake-fresh.
const MEDIA_ONLY =
  /(WebP 全站遷移|媒體增補|媒體落地|影像後處理|image-ingest|land-media|migrate-images|圖片以 ?WebP|babel year-mangle)/i;

// relatedDiary back-link commits touch article frontmatter only — pointing an
// article at the reflection-diary written alongside it is NOT a content change
// (exactly like sporeLinks above). Without this, the 2026-06-24 retroactive
// back-fill of historical diary↔article links (sync-diary-links.py /
// analyze-diary-article-links.py) would set every back-filled article's /latest
// position + sitemap lastmod to the back-fill day — the same anti-pattern the
// SPORE_POINTER + MEDIA_ONLY guards exist to prevent (user directive 2026-06-24:
// 集體回補 relatedDiary 不要動到文章編輯日期 / 不影響「最新文章」頁面). Errs
// conservative (stale-but-true), never fake-fresh.
const RELATED_DIARY =
  /(relatedDiary|relatedDiary 回扣|relatedDiary 集體回補|sync-diary-links)/i;

// 2026-06-28: dedicated cross-link commits touch only a sibling's 延伸閱讀 list — NOT a
// content edit. A reverse-cross-link (Step 5.2 commit "cross-link: 為「X」建立雙向延伸閱讀")
// adds one line to each sibling; without this, every article ship floats its 2-5
// cross-linked siblings to「最新文章」(user callout 2026-06-28: 不是今天寫的文章也因為連結
// 被浮上來). Siblings always have an older substantive commit to fall back to, so this
// never orphans a date. Complements BATCH_THRESHOLD below (the >50-file slug-rename sweep).
// NOT included: recat/重新分類 (a path move leaves the new-path file with NO older history
// here — making it cosmetic would drop it from /latest entirely, worse than the move date);
// and a cross-link BUNDLED inside a substantive ship commit (subject "rewrite:…" that also
// reverse-cross-links siblings) — fully covering that needs per-file diff-size (-z
// --numstat), deferred as a riskier change to this previously-/latest-breaking parser.
// Mitigation: keep reverse-cross-links in their own "cross-link:" commit. Errs stale-but-true.
const CROSS_LINK_RECAT =
  /(cross-link|雙向延伸閱讀|反向延伸閱讀|reverse cross-link)/i;

function knowledgePathToUrl(p) {
  const parts = p.split('/');
  if (parts[0] !== 'knowledge') return null;
  let i = 1;
  let lang = 'zh-TW';
  if (NON_DEFAULT_LANGS.has(parts[1])) {
    lang = parts[1];
    i = 2;
  }
  const cat = parts[i];
  const file = parts[i + 1];
  // must be exactly knowledge/[lang/]Cat/file.md (no deeper nesting)
  if (parts.length !== i + 2) return null;
  if (!cat || !file || !file.endsWith('.md') || file.startsWith('_'))
    return null;
  const catSlug = CAT_TO_SLUG[cat];
  if (!catSlug) return null;
  const slug = file.replace(/\.md$/, '').normalize('NFC');
  const prefix = lang === 'zh-TW' ? '' : `/${lang}`;
  return `${prefix}/${catSlug}/${slug}/`;
}

/**
 * 磁碟上實際有幾篇 zh-TW 文章（不含 hub 頁）。
 * 用來把 anomaly 門檻從絕對值改成相對比例，見下方 MIN_EXPECTED。
 */
function countZhArticles() {
  let n = 0;
  for (const folder of Object.keys(CAT_TO_SLUG)) {
    const dir = resolve(ROOT, 'knowledge', folder);
    let entries;
    try {
      entries = readdirSync(dir);
    } catch {
      continue; // 分類資料夾還沒建，不算異常
    }
    n += entries.filter((f) => f.endsWith('.md') && !f.startsWith('_')).length;
  }
  return n;
}

function main() {
  let log = '';
  try {
    // `-z` = NUL-separated raw paths (immune to git's core.quotepath octal-escaping
    // of non-ASCII filenames). `-c core.quotepath=false` is belt-and-suspenders.
    // ROOT CAUSE of the 2026-06-14 /latest collapse: a `--numstat` rewrite (without
    // -z) was parsed with a `knowledge/.+\.md` regex; it worked locally only because
    // this dev's git config had core.quotepath=false, but CI's default is TRUE →
    // every CJK-named article path came back octal-escaped ("knowledge/People/\\350…")
    // → regex missed them → CJK articles got no date → /latest showed only ASCII-slug
    // articles. Build scripts MUST be invariant to local git config: use -z and/or
    // pin core.quotepath. Never trust a git-text parser that "works on my machine".
    log = execSync(
      'git -c core.quotepath=false log --full-history -z --name-only --format="COMMIT|%H|%aI|%s" -- knowledge/',
      { encoding: 'utf-8', maxBuffer: 256 * 1024 * 1024 },
    );
  } catch (e) {
    console.error('[content-dates] git log failed:', e.message);
    mkdirSync(dirname(OUT), { recursive: true });
    writeFileSync(
      OUT,
      JSON.stringify({ _generated: null, count: 0, dates: {} }),
    );
    return;
  }

  const dates = {}; // url -> ISO (newest substantive wins; log is newest-first)
  let skipped = 0;

  // 2026-06-28: BATCH_THRESHOLD — a single commit touching > 50 knowledge .md files
  // is a bulk op (cross-link rename sweep, slug rename, mass re-categorize) even when
  // its subject reads substantive (e.g. "rewrite: X NEW + rename" that ALSO sed'd 99
  // 延伸閱讀 links). Subject-based COSMETIC can't catch a MIXED commit (1 real article
  // edit + 99 link-only touches), so a slug-rename sweep flooded「最新文章」with
  // articles that only had one link changed (user callout 2026-06-28: 不是今天寫的
  // 文章也因為連結被浮上來). Fix = two-pass dating: substantive (non-batch) commits
  // set the real date first; batch commits then fill ONLY articles still undated — so
  // a genuinely-new article shipped inside the batch commit keeps today's date, while
  // articles with an older real edit keep that older date. Mirrors
  // generate-dashboard-data.js BATCH_THRESHOLD. Errs stale-but-true, never fake-fresh.
  const BATCH_THRESHOLD = 50;

  // Parse the newest-first log into commits with their knowledge URLs.
  const commits = []; // { date, cosmetic, urls: [] }
  let cur = null;
  for (let token of log.split('\0')) {
    token = token.replace(/^\n+/, '').trim();
    if (!token) continue;
    if (token.startsWith('COMMIT|')) {
      const parts = token.split('|');
      const subject = parts.slice(3).join('|');
      cur = {
        date: parts[2] || '',
        cosmetic:
          COSMETIC.test(subject) ||
          SPORE_POINTER.test(subject) ||
          MEDIA_ONLY.test(subject) ||
          RELATED_DIARY.test(subject) ||
          CROSS_LINK_RECAT.test(subject),
        urls: [],
      };
      commits.push(cur);
    } else if (cur && token.startsWith('knowledge/') && token.endsWith('.md')) {
      const url = knowledgePathToUrl(token);
      if (url) cur.urls.push(url);
    }
  }
  for (const c of commits) if (c.cosmetic) skipped += c.urls.length;

  // Pass 1 = substantive non-batch commits (set real date); Pass 2 = batch commits
  // fill only still-undated articles (new-in-batch). Both iterate newest-first, so
  // `if (!dates[url])` keeps the newest qualifying date per article.
  for (const batchPass of [false, true]) {
    for (const c of commits) {
      if (c.cosmetic) continue;
      if (c.urls.length > BATCH_THRESHOLD !== batchPass) continue;
      for (const url of c.urls) if (!dates[url]) dates[url] = c.date;
    }
  }

  // 2026-06-14: a translated article's freshness IS its zh source's content
  // freshness — a pure re-translation (lang-sync / 平行翻譯 / 榨模型 batch) is not a
  // content event. We DERIVE rather than FILTER: filtering translation commits
  // would leave a translated file (whose every commit is a translation) with NO
  // date → foreign /latest collapse. Inheriting the zh date instead dissolves the
  // historical 1329-on-2026-05-01 + 805-on-05-02 sitemap floods (translated files
  // were all dated on their sync day) while keeping every translation dated and
  // making foreign /latest mirror real zh content recency.
  let derived = 0;
  for (const url of Object.keys(dates)) {
    const m = url.match(/^\/([a-z]{2})\/(.+)$/);
    if (m && NON_DEFAULT_LANGS.has(m[1])) {
      const zhUrl = '/' + m[2];
      if (dates[zhUrl] && dates[url] !== dates[zhUrl]) {
        dates[url] = dates[zhUrl];
        derived++;
      }
    }
  }

  // 2026-06-14: proactive anomaly guard (report §Part3.4). A single day with an
  // implausible article count = a batch op leaked through the cosmetic filters
  // (the media flood + the 1329-on-05-01 translation flood both looked like this).
  // A near-empty result = a parser/env regression (the core.quotepath /latest
  // collapse). Warn LOUDLY in the build log so the next pollution source or
  // regression announces itself, instead of waiting for a human to spot /latest.
  const FLOOD = 120;
  // 2026-07-29：母體的 3000 是它 3,977 篇語料的尺度。這個物種還在出生階段，
  // 寫死絕對值會讓「永遠低於門檻」變成背景噪音，真的壞掉時反而沒人聽見
  // （這次就是這樣：0 筆的 warning 混在一堆 warning 裡跟著 build 過去）。
  // 改成相對比例：實際掃到幾個 zh-TW 檔，就該產出多少筆日期。
  const zhFileCount = countZhArticles();
  const MIN_EXPECTED = Math.max(1, Math.floor(zhFileCount * 0.9));
  const byDay = {};
  for (const v of Object.values(dates)) {
    const d = (v || '').slice(0, 10);
    if (d) byDay[d] = (byDay[d] || 0) + 1;
  }
  const floods = Object.entries(byDay)
    .filter(([, n]) => n >= FLOOD)
    .sort((a, b) => b[1] - a[1]);
  if (floods.length) {
    console.warn(
      `[content-dates] ⚠️  ANOMALY: ${floods.length} day(s) ≥${FLOOD} articles (batch-op leak? add to COSMETIC/derive): ` +
        floods
          .slice(0, 5)
          .map(([d, n]) => `${d}=${n}`)
          .join(' '),
    );
  }
  if (Object.keys(dates).length < MIN_EXPECTED) {
    console.warn(
      `[content-dates] ⚠️  ANOMALY: only ${Object.keys(dates).length} dated URLs (expected >${MIN_EXPECTED}) — parser/env regression? (e.g. core.quotepath octal-escaping CJK paths)`,
    );
  }

  mkdirSync(dirname(OUT), { recursive: true });
  writeFileSync(
    OUT,
    JSON.stringify({
      _generated: new Date().toISOString(),
      count: Object.keys(dates).length,
      dates,
    }),
  );
  console.log(
    `[content-dates] ${Object.keys(dates).length} URL dates (skipped ${skipped} cosmetic; ${derived} translated inherited zh date) → src/data/content-dates.json`,
  );
}

main();
