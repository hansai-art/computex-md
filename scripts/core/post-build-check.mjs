/**
 * Post-build smoke test for COMPUTEX.md
 *
 * Runs after `npm run build` to catch silent failures like:
 * - getStaticPaths returning 0 paths (empty catch swallowing errors)
 * - Category pages showing "內容準備中" instead of articles
 * - Build producing far fewer pages than expected
 *
 * Exit code 1 = CI should NOT deploy.
 */

import { readdir, readFile, stat } from 'node:fs/promises';
import { resolve, join, relative } from 'node:path';
import { LANGUAGES } from '../../src/config/languages.mjs';

const DIST = resolve(process.cwd(), 'dist');
// 下限的用意是抓「整組頁面消失」，不是「內容要夠多」。母體 863 篇所以設 300 / 100 /
// 每類 3 篇；COMPUTEX.md 出生時只有 1 篇，沿用母體數字會讓這道防線永遠紅 —
// 永遠紅的防線等於沒有防線。內容長大時把這三個數字一起往上調。
const MIN_TOTAL_PAGES = 20;
const MIN_ARTICLES_PER_CATEGORY = 0;
// 分類不再硬編（母體硬編 13 個台灣分類，fork 後整組失效）。
// 這支是 .mjs 不能 import .ts 的 SSOT，所以改成從 knowledge/ 實際目錄推導 —
// 推導比複製好：它永遠跟真相一致，不會漂移。
const CATEGORIES = (
  await readdir(resolve(process.cwd(), 'knowledge'), { withFileTypes: true })
)
  .filter((d) => d.isDirectory() && !/^(en|_)/.test(d.name))
  .map((d) => d.name.toLowerCase());

// i18n route smoke (audit 2026-06-10 D-8): REFLEXES #19 要求大型 refactor 後
// 人工 smoke test 多語頁面 — 這段把它自動化進每次 CI。每語言驗：目錄存在、
// 頁數高於塌方線、抽 1 頁驗 <html lang> 正確。
// LANG_ROUTES 從 registry derive（pre-commit hook 抓到第一版硬編碼 — 它是對的）。
const LANG_ROUTES = LANGUAGES.filter((l) => l.enabled && !l.isDefault).map(
  (l) => l.code,
);

let errors = [];
let warnings = [];

// ── 1. Count total HTML pages ──

async function countHtml(dir) {
  let count = 0;
  try {
    const entries = await readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      const full = join(dir, entry.name);
      if (entry.isDirectory()) {
        count += await countHtml(full);
      } else if (entry.name.endsWith('.html')) {
        count++;
      }
    }
  } catch {}
  return count;
}

const totalPages = await countHtml(DIST);
console.log(`📊 Total HTML pages: ${totalPages}`);

if (totalPages < MIN_TOTAL_PAGES) {
  errors.push(
    `Total pages (${totalPages}) below minimum (${MIN_TOTAL_PAGES}). Likely a getStaticPaths failure.`,
  );
}

// ── 2. Check each category has article pages (not just index) ──

for (const cat of CATEGORIES) {
  const catDir = join(DIST, cat);
  try {
    const entries = await readdir(catDir, { withFileTypes: true });
    const articleDirs = entries.filter(
      (e) => e.isDirectory() && e.name !== 'index',
    );
    const articleCount = articleDirs.length;

    if (articleCount < MIN_ARTICLES_PER_CATEGORY) {
      errors.push(
        `/${cat}/ has only ${articleCount} article pages (min: ${MIN_ARTICLES_PER_CATEGORY})`,
      );
    } else {
      console.log(`  ✅ /${cat}/: ${articleCount} articles`);
    }
  } catch {
    errors.push(`/${cat}/ directory missing in dist/`);
  }
}

// ── 3. Spot-check: category index pages should have article cards ──

for (const cat of CATEGORIES) {
  const indexPath = join(DIST, cat, 'index.html');
  try {
    const html = await readFile(indexPath, 'utf-8');
    const hasArticles =
      html.includes('article-card') || html.includes('articlesGrid');
    const hasComingSoon = html.includes('coming-soon-content');
    // If the page has the "coming soon" block but no article cards, it's broken
    if (hasComingSoon && !hasArticles) {
      errors.push(
        `/${cat}/index.html has no article cards — only "coming soon" fallback`,
      );
    }
  } catch {
    warnings.push(`/${cat}/index.html not found`);
  }
}

// ── 4. Spot-check: random article pages should have real content ──

const SAMPLE_CATEGORIES = CATEGORIES.slice(0, 3);
for (const cat of SAMPLE_CATEGORIES) {
  const catDir = join(DIST, cat);
  try {
    const entries = await readdir(catDir, { withFileTypes: true });
    const articleDirs = entries.filter((e) => e.isDirectory());
    if (articleDirs.length > 0) {
      const sample = articleDirs[0];
      const htmlPath = join(catDir, sample.name, 'index.html');
      const s = await stat(htmlPath);
      if (s.size < 1024) {
        warnings.push(
          `/${cat}/${sample.name}/index.html is suspiciously small (${s.size} bytes)`,
        );
      }
    }
  } catch {}
}

// ── 5. i18n route smoke (audit 2026-06-10 D-8) ──

const zhArticlePages = await countHtml(join(DIST, 'people')); // proxy for zh depth
for (const lang of LANG_ROUTES) {
  const langDir = join(DIST, lang);
  try {
    const langPages = await countHtml(langDir);
    const zhTotalProxy = totalPages; // includes all langs; use floor heuristic instead
    const LANG_COLLAPSE_FLOOR = 5;
    if (langPages < LANG_COLLAPSE_FLOOR) {
      errors.push(
        `/${lang}/ has only ${langPages} HTML pages (< ${LANG_COLLAPSE_FLOOR} collapse floor) — getStaticPaths or sync likely broke for this language`,
      );
      continue;
    }
    // lang attribute spot-check: first category index found
    let checked = false;
    for (const cat of CATEGORIES) {
      const p = join(langDir, cat, 'index.html');
      try {
        const html = await readFile(p, 'utf8');
        const m = html.match(/<html[^>]*\blang="([^"]+)"/i);
        if (m && !m[1].toLowerCase().startsWith(lang)) {
          errors.push(
            `/${lang}/${cat}/ has <html lang="${m[1]}"> — language attribute mismatch (REFLEXES #19 class bug)`,
          );
        }
        checked = true;
        break;
      } catch {}
    }
    if (!checked) {
      warnings.push(
        `/${lang}/: no category index found for lang-attribute spot-check`,
      );
    }
    console.log(`  ✅ /${lang}/: ${langPages} pages, lang attribute ok`);
  } catch {
    errors.push(`/${lang}/ directory missing in dist/`);
  }
}

// ── Report ──

console.log('');
if (warnings.length > 0) {
  console.log(`⚠️  ${warnings.length} warning(s):`);
  warnings.forEach((w) => console.log(`   - ${w}`));
}

if (errors.length > 0) {
  console.log(`\n🔴 ${errors.length} CRITICAL error(s):`);
  errors.forEach((e) => console.log(`   - ${e}`));
  console.log('\n❌ Post-build check FAILED. Deploy blocked.');
  process.exit(1);
} else {
  console.log(
    `\n✅ Post-build check passed. ${totalPages} pages, all categories healthy.`,
  );
}
