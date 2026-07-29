#!/usr/bin/env node
/**
 * verify-machine-doors.mjs — /mcp 列出的每一道門都必須真的打得開。
 *
 * 為什麼單獨一支
 *   `/mcp` 這一頁的內容就是一份「機器可以從這裡讀」的清單。它比別的頁面更不能
 *   有死連結：讀它的多半不是人，是照著清單去抓的程式，抓到 404 不會回報，
 *   只會少讀一份。這一頁如果列出不存在的路徑，就變成它自己要解決的那個問題。
 *
 *   `verify-internal-links.mjs` 掃的是 HTML 之間的連結，`/llms.txt`、
 *   `/api/*.json`、`/sitemap-index.xml`、`/feed.xml`、`/robots.txt` 這些非 HTML
 *   的產出物不在它的守備範圍。這支補那一段。
 *
 * 檢查什麼
 *   1. `/mcp` 與 `/en/mcp` 頁面上每一個 `<a href>` 指向的站內路徑在 dist 裡存在
 *   2. 而且不是空檔（0 bytes 的 llms.txt 一樣算壞掉）
 *   3. 這幾道門是這個專案的核心承諾，所以另外硬性要求它們一定要在清單上：
 *      /llms.txt /robots.txt /sitemap-index.xml /api/articles.json
 *      —— 有人把某一條從頁面上刪掉時要當場知道
 *
 * 用法
 *   node scripts/tools/verify-machine-doors.mjs   （掛在 postbuild）
 */

import { readFileSync, existsSync, statSync } from 'node:fs';
import { resolve, join } from 'node:path';

const DIST = resolve(process.cwd(), 'dist');

/** 一定要出現在 /mcp 上的門。少一條就是承諾縮水，要當場知道。 */
const REQUIRED = [
  '/llms.txt',
  '/robots.txt',
  '/sitemap-index.xml',
  '/api/articles.json',
];

const PAGES = ['mcp/index.html', 'en/mcp/index.html'];

/** dist 裡這個路徑打得開嗎（目錄式網址、直接檔案、或補 .html 都算）。 */
function resolveInDist(urlPath) {
  const clean = urlPath.split('#')[0].split('?')[0];
  const rel = clean.replace(/^\/+/, '');
  if (!rel) return join(DIST, 'index.html');
  for (const cand of [
    join(DIST, rel),
    join(DIST, rel, 'index.html'),
    join(DIST, `${rel}.html`),
  ]) {
    if (existsSync(cand) && statSync(cand).isFile()) return cand;
  }
  return null;
}

const failures = [];
let checked = 0;

for (const page of PAGES) {
  const file = join(DIST, page);
  if (!existsSync(file)) {
    failures.push(`dist/${page} 不存在 —— /mcp 沒有被 build 出來`);
    continue;
  }
  const html = readFileSync(file, 'utf-8');

  // 只取 <main> 之後的內容：頁首導覽與頁尾的連結由 verify-nav-links 負責，
  // 這支只管這一頁自己列出來的那份清單。
  const body = html.slice(html.indexOf('<main'));
  const hrefs = [...body.matchAll(/href="([^"]+)"/g)]
    .map((m) => m[1])
    .filter((h) => h.startsWith('/'));

  const seen = new Set();
  for (const href of hrefs) {
    if (seen.has(href)) continue;
    seen.add(href);
    checked += 1;
    const target = resolveInDist(href);
    if (!target) {
      failures.push(`${page} 列出的 ${href} 在 dist 裡不存在`);
    } else if (statSync(target).size === 0) {
      failures.push(`${page} 列出的 ${href} 是 0 bytes`);
    }
  }

  for (const must of REQUIRED) {
    if (!seen.has(must)) {
      failures.push(
        `${page} 沒有列出 ${must} —— 這是本站對機器的核心承諾之一，` +
          `不該從這一頁消失（真的要拿掉，先改這支 gate 的 REQUIRED 並寫清楚為什麼）`,
      );
    }
  }
}

if (failures.length) {
  console.error(`\n❌ [machine-doors] ${failures.length} 項問題：\n`);
  for (const f of failures) console.error(`  ${f}`);
  console.error('');
  process.exit(1);
}

console.log(
  `✅ [machine-doors] /mcp 列出的 ${checked} 條機器入口全部打得開，` +
    `必要的 ${REQUIRED.length} 條都在`,
);
