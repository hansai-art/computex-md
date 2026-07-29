#!/usr/bin/env node
/**
 * verify-generated-data.mjs — 產出物必須對得上來源。
 *
 * 為什麼要有這支
 *   這個站從母體取種以來，同一種錯誤已經抓到十二次：**某支 build script 裡有一份
 *   寫死的分類表（或語言表），內容是母體的**。資料夾名一個都對不上，掃出來是零筆，
 *   然後它印一行綠色的成功訊息就結束了：
 *
 *     [search] shard zh-TW: 0 docs, 0 KB → search-minisearch-zh-TW.json
 *     ✓ latest.json: 0 entries across 6 langs
 *
 *   有勾、有箭頭、沒有 exit code。CI 全綠，站上全站搜尋打什麼都是「找不到結果」，
 *   而且是從第一天就這樣。這一類錯的共同形狀是「**產出 0 筆，但印成功**」——
 *   人不會去讀每一行成功訊息裡的數字，所以只能讓機器讀。
 *
 *   這支就是那個機器。它不檢查內容對不對（那是別的 gate 的事），只檢查一件事：
 *   **來源有東西的時候，產出物不准是空的、也不准少一大截。**
 *
 * 判準
 *   來源真相 = `knowledge/` 底下的 .md 檔數（依語言、依分類數）。這是唯一不會
 *   說謊的數字：檔案在磁碟上，數得出來。每一項產出物宣告自己該有多少筆，比不上
 *   就 exit 1。
 *
 *   `atLeast` 用在「本來就會過濾掉一些」的產出物（例如 latest.json 只收有 git
 *   日期的），`exact` 用在「一篇都不該掉」的（搜尋索引、articles.json）。
 *   來源本身是空的（例如 Products 資料夾還沒有內容）不算失敗 —— 空資料夾產出空
 *   陣列是誠實的，那不是這支要抓的東西。
 *
 * 用法
 *   node scripts/tools/verify-generated-data.mjs
 *   （掛在 prebuild 尾巴：產出物剛做完就驗，不必等 build 完。）
 */

import { readdir, readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { CATEGORY_MAPPING } from '../../src/config/categories.mjs';
import {
  ENABLED_LANGUAGE_CODES,
  DEFAULT_LANGUAGE,
} from '../../src/config/languages.mjs';

const ROOT = process.cwd();
const API = resolve(ROOT, 'public/api');

// ── 來源真相：knowledge/ 底下數得出來的 .md ──────────────────────────────

/** lang → { total, byCategory: {slug: n} } */
async function scanKnowledge() {
  const out = {};
  for (const lang of ENABLED_LANGUAGE_CODES) {
    const isDefault = lang === DEFAULT_LANGUAGE.code;
    const byCategory = {};
    let total = 0;
    for (const [slug, folder] of Object.entries(CATEGORY_MAPPING)) {
      const dir = isDefault
        ? resolve(ROOT, 'knowledge', folder)
        : resolve(ROOT, 'knowledge', lang, folder);
      let files = [];
      try {
        files = (await readdir(dir)).filter(
          (f) => f.endsWith('.md') && !f.startsWith('_'),
        );
      } catch {
        // 分類資料夾對這個語言不存在 —— 0 筆，不是錯
      }
      byCategory[slug] = files.length;
      total += files.length;
    }
    out[lang] = { total, byCategory };
  }
  return out;
}

// ── 檢查表 ────────────────────────────────────────────────────────────

const failures = [];
const notes = [];

function check({ file, label, actual, expected, mode = 'exact' }) {
  if (expected === 0) {
    notes.push(
      `· ${label}：來源 0 筆，產出 ${actual} 筆（來源本來就空，跳過）`,
    );
    return;
  }
  const ok = mode === 'exact' ? actual === expected : actual >= expected;
  if (ok) {
    notes.push(`✓ ${label}：${actual} 筆（來源 ${expected}）`);
  } else {
    failures.push(
      `${file}\n    ${label}：產出 ${actual} 筆，來源有 ${expected} 筆` +
        (actual === 0
          ? '\n    → 產出是空的。先看產這支檔案的 script 裡有沒有寫死的分類表 / 語言表。'
          : `\n    → 少了 ${expected - actual} 筆。`),
    );
  }
}

async function readJson(rel) {
  const p = join(API, rel);
  if (!existsSync(p)) return null;
  try {
    return JSON.parse(await readFile(p, 'utf-8'));
  } catch (e) {
    failures.push(`public/api/${rel}\n    JSON 解析失敗：${e.message}`);
    return null;
  }
}

const knowledge = await scanKnowledge();
const totalAll = Object.values(knowledge).reduce((s, k) => s + k.total, 0);

// 1. articles.json / stats.json —— 全語言全分類，一篇都不該掉
const articles = await readJson('articles.json');
if (articles) {
  check({
    file: 'public/api/articles.json',
    label: '全站文章 metadata',
    actual: Array.isArray(articles.articles)
      ? articles.articles.length
      : Array.isArray(articles)
        ? articles.length
        : 0,
    expected: totalAll,
  });
}

const stats = await readJson('stats.json');
if (stats) {
  check({
    file: 'public/api/stats.json',
    label: 'totalArticles',
    actual: stats.totalArticles ?? 0,
    expected: totalAll,
  });
  // 分類名必須全部出自正本分類表。母體的分類名、或路徑被誤讀成分類（`en`）都會在這裡現形。
  const known = new Set(Object.values(CATEGORY_MAPPING));
  const bogus = (stats.categories ?? [])
    .map((c) => c.name)
    .filter((n) => !known.has(n));
  if (bogus.length) {
    failures.push(
      `public/api/stats.json\n    出現不在正本分類表上的分類：${bogus.join(', ')}` +
        '\n    → 通常是路徑解析取錯段（把語言碼當分類），或殘留母體分類名。',
    );
  } else {
    notes.push(`✓ stats.json 分類名：全部出自正本分類表`);
  }
}

// 2. 搜尋索引 —— 這是踩最痛的一支，逐語言檢查
for (const lang of ENABLED_LANGUAGE_CODES) {
  const shard = await readJson(`search-minisearch-${lang}.json`);
  if (shard) {
    // MiniSearch 序列化格式：documentCount 在頂層或 index 內，兩種都撈
    const actual =
      shard.documentCount ??
      shard.documentIds?.length ??
      Object.keys(shard.storedFields ?? {}).length ??
      0;
    check({
      file: `public/api/search-minisearch-${lang}.json`,
      label: `搜尋索引 ${lang}`,
      actual,
      expected: knowledge[lang].total,
    });
  }
}

const fallback = await readJson('search-index.json');
if (fallback) {
  const expected =
    (knowledge[DEFAULT_LANGUAGE.code]?.total ?? 0) +
    (knowledge.en?.total ?? 0) * (DEFAULT_LANGUAGE.code === 'en' ? 0 : 1);
  check({
    file: 'public/api/search-index.json',
    label: '搜尋 fallback 索引（zh+en）',
    actual: Array.isArray(fallback) ? fallback.length : 0,
    expected,
  });
}

// 3. latest.json —— 語言桶必須剛好是本站開的語言（母體六語殘留會在這裡現形）
const latest = await readJson('latest.json');
if (latest) {
  const langs = Object.keys(latest.byLang ?? {});
  const extra = langs.filter((l) => !ENABLED_LANGUAGE_CODES.includes(l));
  const missing = ENABLED_LANGUAGE_CODES.filter((l) => !langs.includes(l));
  if (extra.length || missing.length) {
    failures.push(
      `public/api/latest.json\n    語言桶對不上：多了 [${extra.join(', ') || '無'}]，少了 [${missing.join(', ') || '無'}]` +
        '\n    → 語言清單只准從 src/config/languages.mjs 讀。',
    );
  } else {
    notes.push(`✓ latest.json 語言桶：${langs.join(', ')}`);
  }
  // 有 git 日期的才會進榜，所以只驗「不是全空」
  const total = Object.values(latest.byLang ?? {}).reduce(
    (s, a) => s + (a?.length ?? 0),
    0,
  );
  check({
    file: 'public/api/latest.json',
    label: '最新文章總筆數',
    actual: total,
    expected: totalAll ? 1 : 0,
    mode: 'atLeast',
  });
}

// 4. random-index-<lang>.json —— 逐語言，且不准有本站沒開的語言檔殘留
for (const lang of ENABLED_LANGUAGE_CODES) {
  const pool = await readJson(`random-index-${lang}.json`);
  if (pool) {
    const actual = Object.values(pool.byCat ?? {}).reduce(
      (s, a) => s + (a?.length ?? 0),
      0,
    );
    check({
      file: `public/api/random-index-${lang}.json`,
      label: `隨機探索池 ${lang}`,
      actual,
      expected: knowledge[lang].total,
    });
  }
}
try {
  const stale = (await readdir(API))
    .filter((f) => /^random-index-(.+)\.json$/.test(f))
    .map((f) => f.match(/^random-index-(.+)\.json$/)[1])
    .filter((l) => !ENABLED_LANGUAGE_CODES.includes(l));
  if (stale.length) {
    failures.push(
      `public/api/\n    殘留了本站沒開的語言檔：${stale.map((l) => `random-index-${l}.json`).join(', ')}` +
        '\n    → 語言關掉時舊產出不會自己消失，手動刪掉。',
    );
  }
} catch {
  /* API 目錄不存在，前面已經報過 */
}

// ── 收尾 ──────────────────────────────────────────────────────────────

console.log('[generated-data] 來源真相（knowledge/ 實際 .md 檔數）：');
for (const [lang, k] of Object.entries(knowledge)) {
  const detail = Object.entries(k.byCategory)
    .map(([c, n]) => `${c}=${n}`)
    .join(' ');
  console.log(`  ${lang}: ${k.total} 篇（${detail}）`);
}
console.log('');
for (const n of notes) console.log(`  ${n}`);

if (failures.length) {
  console.error(
    `\n❌ [generated-data] ${failures.length} 項產出物對不上來源：\n`,
  );
  for (const f of failures) console.error(`  ${f}\n`);
  console.error(
    '這一類錯的形狀是「產出 0 筆但印成功訊息」。修法通常是把 script 裡寫死的\n' +
      '分類表 / 語言表換成 src/config/categories.mjs 與 src/config/languages.mjs。\n',
  );
  process.exit(1);
}

console.log(`\n✅ [generated-data] ${notes.length} 項產出物與來源一致`);
