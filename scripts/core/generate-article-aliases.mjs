#!/usr/bin/env node
/**
 * generate-article-aliases.mjs — 中文文章的英文別名 registry 維護器
 *
 * ── 為什麼有這支工具 ────────────────────────────────────────────────────────
 * 中文文章的網址用中文檔名（`/culture/中元節`），其他語言用英文 slug
 * （`/en/culture/ghost-festival-zhongyuan`）。站上其他每一種頁面，中文版都等於
 * 英文版把 `/en/` 拿掉：`/en/about` ↔ `/about`、`/en/dashboard` ↔ `/dashboard`。
 * 只有文章頁打破這條規則，因為 slug 本身也換了。
 *
 * 結果是讀者跟機器照著我們自己教的規則推網址，然後撞牆。2026-07-23 單日
 * `monitor-404.py` 的 cross-lang-slug 家族 538 次（303 機器 / 235 真人瀏覽器），
 * 抽查前 10 條猜測 slug 對照 en 檔名 10/10 完全命中——沒有人在自創英文寫法，
 * 大家就是把 `/en/` 拿掉而已。
 *
 * 這支工具產出那扇本來就該存在的側門：每篇中文文章一個英文別名網址。
 *
 * ── 三條設計鐵律 ──────────────────────────────────────────────────────────
 * 1. **只增不改（append-only）**。別名一旦進 registry 就凍住，即使來源的 en
 *    檔名之後改名也不動。理由：近 90 天 en 改過 6 次檔名，如果別名每次 build
 *    現算，改一次名就殺掉一批已經分享出去的連結。凍住 = 分享出去的網址永不死。
 *    要改某條別名是人的決定，手改這個檔，不是工具的權限。
 * 2. **registry 是 SSOT，不是 cache**。`config/article-aliases.json` 進 git，
 *    工具只負責「補新的」跟「檢查衝突」。刪掉重跑不會得到同一份檔案（改過名的
 *    文章會跟著漂），所以它不可重生——別把它加進 .gitignore。
 * 3. **永不對外公告**。別名不進 sitemap、不進 hreflang、不做站內連結、canonical
 *    永遠指回中文網址。2026-07-17 那次 15% 404 率的根因就是站體對外公告了
 *    13,014 條自己沒有的 URL；別名是反向風險（它們存在），但紀律一樣：
 *    公告面一條都不給。sitemap 過濾在 astro.config.mjs 的 serialize()，
 *    機械斷言在 check-url-contract.mjs。
 *
 * ── 輸入 / 輸出 ──────────────────────────────────────────────────────────
 * 輸入：knowledge/_translations.json（en 那半邊 = zh 檔 → en 檔的對照）
 *       knowledge/{Category}/*.md（真實存在的中文文章，ground truth）
 *       config/article-aliases.json（既有 registry，可能不存在）
 * 輸出：config/article-aliases.json
 *       { "<category-slug>/<alias-slug>": "<Category>/<中文檔名>" }
 *       key 是別名網址的 path 尾段，value 是它指向的中文文章（相對 knowledge/）
 *
 * Usage:
 *   node scripts/core/generate-article-aliases.mjs            # 補新條目並寫檔
 *   node scripts/core/generate-article-aliases.mjs --check    # 唯讀，有缺漏/衝突則 exit 1
 *   node scripts/core/generate-article-aliases.mjs --json     # 機器可讀 summary
 */

import { readFile, writeFile, readdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO = join(__dirname, '../..');

const TRANSLATIONS_PATH = join(REPO, 'knowledge/_translations.json');
const REGISTRY_PATH = join(REPO, 'config/article-aliases.json');
const KNOWLEDGE_DIR = join(REPO, 'knowledge');

// 抄自 generate-redirects.mjs 的同名表（category 資料夾 → URL slug）。
// 不在表內的資料夾 fallback 用 lowercase，跟既有 route 產生邏輯一致。
const CATEGORY_FOLDER_TO_SLUG = {
  History: 'history',
  Geography: 'geography',
  Culture: 'culture',
  Food: 'food',
  Art: 'art',
  Music: 'music',
  Technology: 'technology',
  Nature: 'nature',
  People: 'people',
  Society: 'society',
  Economy: 'economy',
  Lifestyle: 'lifestyle',
  Politics: 'politics',
  About: 'about',
  Resources: 'resources',
};

const args = process.argv.slice(2);
const CHECK_ONLY = args.includes('--check');
const AS_JSON = args.includes('--json');

const log = (...a) => {
  if (!AS_JSON) console.log(...a);
};

const catSlug = (folder) =>
  CATEGORY_FOLDER_TO_SLUG[folder] || folder.toLowerCase();

/** 掃出真實存在的中文文章（ground truth，不信任 _translations.json 單邊）。 */
async function scanZhArticles() {
  const out = new Set();
  const entries = await readdir(KNOWLEDGE_DIR, { withFileTypes: true });
  for (const e of entries) {
    // 語言資料夾是小寫二到三碼（en/ja/ko/ar/...）；中文分類資料夾首字母大寫。
    if (!e.isDirectory()) continue;
    if (!/^[A-Z]/.test(e.name)) continue;
    if (!(e.name in CATEGORY_FOLDER_TO_SLUG)) continue;
    const files = await readdir(join(KNOWLEDGE_DIR, e.name));
    for (const f of files) {
      if (!f.endsWith('.md') || f.startsWith('_')) continue;
      out.add(`${e.name}/${f.slice(0, -3)}`);
    }
  }
  return out;
}

/** 從 _translations.json 取 zh 文章 → en slug 的對照。 */
async function readEnSlugMap() {
  const raw = JSON.parse(await readFile(TRANSLATIONS_PATH, 'utf-8'));
  const map = new Map(); // "Category/中文檔名" → "en-slug"
  for (const [translated, source] of Object.entries(raw)) {
    if (!translated.startsWith('en/')) continue;
    const rest = translated.slice(3); // Category/slug.md
    const slashAt = rest.indexOf('/');
    if (slashAt < 0) continue; // en/xxx.md 沒有分類，跳過
    const enSlug = rest.slice(slashAt + 1).replace(/\.md$/, '');
    const zhKey = source.replace(/\.md$/, '');
    map.set(zhKey, enSlug);
  }
  return map;
}

async function main() {
  const [zhArticles, enSlugs] = await Promise.all([
    scanZhArticles(),
    readEnSlugMap(),
  ]);

  /** @type {Record<string,string>} */
  let registry = {};
  if (existsSync(REGISTRY_PATH)) {
    registry = JSON.parse(await readFile(REGISTRY_PATH, 'utf-8'));
  }

  // ── 既有條目：只驗不動（append-only 鐵律） ────────────────────────────────
  const stale = []; // 別名指向的中文文章已經不存在（改名/合併/刪除）
  for (const [alias, target] of Object.entries(registry)) {
    if (!zhArticles.has(target)) stale.push({ alias, target });
  }

  // ── 佔用表：別名不能撞到任何真實中文文章網址，也不能互撞 ──────────────────
  const zhUrlKeys = new Set(
    [...zhArticles].map((a) => {
      const [folder, slug] = a.split('/');
      return `${catSlug(folder)}/${slug}`;
    }),
  );
  const taken = new Set(Object.keys(registry));

  // ── 補新條目 ──────────────────────────────────────────────────────────────
  const added = [];
  const skippedNoEn = [];
  const skippedCollision = [];
  const alreadyAliased = new Set(Object.values(registry));

  for (const zhKey of [...zhArticles].sort()) {
    if (alreadyAliased.has(zhKey)) continue; // 已經有別名，不重發
    const enSlug = enSlugs.get(zhKey);
    if (!enSlug) {
      skippedNoEn.push(zhKey);
      continue;
    }
    const [folder, zhSlug] = zhKey.split('/');
    const aliasKey = `${catSlug(folder)}/${enSlug}`;

    // 中文 slug 本來就是 ASCII 且跟 en slug 相同（如 About/taiwan-md）→ 別名
    // 等於本尊，不需要側門。
    if (aliasKey === `${catSlug(folder)}/${zhSlug}`) continue;

    if (zhUrlKeys.has(aliasKey)) {
      skippedCollision.push({ zhKey, aliasKey, reason: 'zh-article-url' });
      continue;
    }
    if (taken.has(aliasKey)) {
      skippedCollision.push({ zhKey, aliasKey, reason: 'alias-duplicate' });
      continue;
    }
    taken.add(aliasKey);
    alreadyAliased.add(zhKey);
    added.push({ aliasKey, zhKey });
  }

  const next = { ...registry };
  for (const { aliasKey, zhKey } of added) next[aliasKey] = zhKey;

  // key 排序讓 diff 穩定（append-only 但檔案順序不該隨掃描順序漂）
  const sorted = Object.fromEntries(
    Object.entries(next).sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0)),
  );

  // ── fail-loud selftest ────────────────────────────────────────────────────
  const problems = [];
  for (const [alias, target] of Object.entries(sorted)) {
    if (zhUrlKeys.has(alias))
      problems.push(`別名撞到真實中文文章網址: /${alias}`);
    if (!zhArticles.has(target))
      problems.push(`別名指向不存在的中文文章: /${alias} → ${target}`);
  }

  const summary = {
    zh_articles: zhArticles.size,
    registry_before: Object.keys(registry).length,
    registry_after: Object.keys(sorted).length,
    added: added.length,
    skipped_no_en_translation: skippedNoEn.length,
    skipped_collision: skippedCollision.length,
    stale_targets: stale.length,
    problems: problems.length,
  };

  if (AS_JSON) {
    console.log(
      JSON.stringify({ ...summary, stale, skippedCollision }, null, 2),
    );
  } else {
    log('🔗 article-aliases');
    log(`   中文文章          ${summary.zh_articles}`);
    log(
      `   registry          ${summary.registry_before} → ${summary.registry_after}（新增 ${summary.added}）`,
    );
    log(`   跳過（無 en 譯本）  ${summary.skipped_no_en_translation}`);
    if (skippedCollision.length) {
      log(`   ⚠️  跳過（衝突）     ${summary.skipped_collision}`);
      for (const c of skippedCollision.slice(0, 10))
        log(`        ${c.zhKey} → /${c.aliasKey} (${c.reason})`);
    }
    if (stale.length) {
      // 不自動刪：別名指向的文章可能只是被 quarantine 暫時移走，砍掉等於
      // 讓已分享的連結永久死掉。人來判。
      log(`   ⚠️  別名指向已不存在的文章 ${stale.length} 條（保留，待人判）`);
      for (const s of stale.slice(0, 10))
        log(`        /${s.alias} → ${s.target}`);
    }
  }

  if (problems.length) {
    console.error('❌ article-aliases selftest 失敗：');
    for (const p of problems.slice(0, 20)) console.error('   ' + p);
    process.exit(1);
  }

  if (CHECK_ONLY) {
    if (added.length) {
      console.error(
        `❌ registry 缺 ${added.length} 條別名（跑 node scripts/core/generate-article-aliases.mjs 補上並 commit）`,
      );
      process.exit(1);
    }
    log('✅ registry 是最新的');
    return;
  }

  await writeFile(REGISTRY_PATH, JSON.stringify(sorted, null, 2) + '\n');
  log(`✅ 寫入 ${REGISTRY_PATH.replace(REPO + '/', '')}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
