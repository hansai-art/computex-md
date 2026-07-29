#!/usr/bin/env node
/**
 * verify-og-images.mjs — 掃 dist 每一頁對外宣告的社交圖，確認那個檔案真的存在。
 *
 * 為什麼需要這一支
 *   2026-07-29 手動抽查 `dist/about/index.html` 才發現：`SEO.astro` 的預設
 *   og:image 一直是母體的 `/images/taiwan-social.jpg`，而這個 repo 連
 *   `public/images/` 這個資料夾都沒有。也就是說 86 篇廠商頁以外的**每一頁**
 *   （首頁、/about、/explore、所有分類索引），對 Facebook / LINE / X /
 *   Slack / Discord 宣告的預覽圖都是 404。
 *
 *   為什麼三支既有守門全都看不到它：
 *     - `check-url-contract`  驗 canonical / sitemap / hreflang，不驗 meta 圖
 *     - `verify-nav-links`    只驗外框的 <a href>
 *     - `verify-internal-links` 驗全站 <a href>，但 og:image 不是 <a>
 *   共同的形狀：**沒有人點得到的 URL，沒有人在驗**。而社交圖恰恰是這種 URL
 *   ——使用者永遠不會點它，只有爬蟲會抓，所以壞掉可以壞很久沒人知道。
 *   對一個「被引用」就是全部價值的專案，這是最不能壞的一類連結。
 *
 * 範圍
 *   `og:image` / `twitter:image` / JSON-LD 裡任何 http(s) 圖片 URL。
 *   只驗指向本站的（絕對 URL 比對 siteUrl，或 `/` 開頭的相對路徑）；
 *   外部主機不碰（那要打網路，不是 build gate 該做的事）。
 *
 * 用法
 *   node scripts/tools/verify-og-images.mjs [dist 路徑]
 *   任一宣告的圖片在 dist 裡不存在 → exit 1，列出「哪張圖、被幾頁宣告」。
 */

import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { join, dirname, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const distDir = process.argv[2] || join(repoRoot, 'dist');

/** SEO.astro 裡宣告的站台網址。改那邊要改這邊（只有兩處，先不抽 SSOT）。 */
const SITE_URL = 'https://computex.taiwanai.ngo';

function walk(dir, out = []) {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) walk(full, out);
    else if (entry.endsWith('.html')) out.push(full);
  }
  return out;
}

/** 絕對 URL → 站內路徑；外部主機回 null（不驗）。 */
function toLocalPath(raw) {
  const url = raw.trim();
  if (url.startsWith(SITE_URL)) return url.slice(SITE_URL.length) || '/';
  if (url.startsWith('/') && !url.startsWith('//')) return url;
  return null;
}

const resolveCache = new Map();
function fileExists(urlPath) {
  if (resolveCache.has(urlPath)) return resolveCache.get(urlPath);
  const clean = decodeURIComponent(urlPath.split(/[?#]/)[0]).replace(
    /^\/+/,
    '',
  );
  const ok = clean !== '' && existsSync(join(distDir, clean));
  resolveCache.set(urlPath, ok);
  return ok;
}

if (!existsSync(distDir)) {
  console.error(`❌ [og-images] 找不到 ${distDir}。先跑 npm run build。`);
  process.exit(1);
}

const pages = walk(distDir);
if (pages.length === 0) {
  console.error(`❌ [og-images] ${distDir} 裡一個 HTML 都沒有。`);
  process.exit(1);
}

// og:image / twitter:image（property 與 name 兩種寫法、兩種屬性順序都吃）
const META_PATTERNS = [
  /<meta[^>]+(?:property|name)="(?:og:image|twitter:image)"[^>]+content="([^"]+)"/g,
  /<meta[^>]+content="([^"]+)"[^>]+(?:property|name)="(?:og:image|twitter:image)"/g,
];
// JSON-LD 裡的圖片 URL（ImageObject.url / image / logo.url 都會長成 "url":"..."）
const JSONLD_BLOCK =
  /<script type="application\/ld\+json">([\s\S]*?)<\/script>/g;
const JSONLD_IMAGE = /"url"\s*:\s*"([^"]+\.(?:jpg|jpeg|png|webp|svg|gif))"/g;

const missing = new Map(); // 圖片路徑 → 宣告它的頁面
let declared = 0;
let pagesWithNoImage = 0;

for (const file of pages) {
  const html = readFileSync(file, 'utf-8');
  const rel = relative(distDir, file).split(sep).join('/');
  const found = new Set();

  for (const pattern of META_PATTERNS) {
    pattern.lastIndex = 0;
    for (const m of html.matchAll(pattern)) found.add(m[1]);
  }
  JSONLD_BLOCK.lastIndex = 0;
  for (const block of html.matchAll(JSONLD_BLOCK)) {
    for (const m of block[1].matchAll(JSONLD_IMAGE)) found.add(m[1]);
  }

  if (found.size === 0) pagesWithNoImage += 1;

  for (const raw of found) {
    const local = toLocalPath(raw);
    if (local === null) continue; // 外部主機
    declared += 1;
    if (fileExists(local)) continue;
    if (!missing.has(local)) missing.set(local, []);
    missing.get(local).push(rel);
  }
}

if (missing.size === 0) {
  console.log(
    `✅ [og-images] ${pages.length} 頁共 ${declared} 條社交圖宣告全部指向存在的檔案` +
      (pagesWithNoImage ? `（${pagesWithNoImage} 頁沒宣告任何圖）` : ''),
  );
  process.exit(0);
}

const totalRefs = [...missing.values()].reduce((a, r) => a + r.length, 0);
console.error(
  `❌ [og-images] ${missing.size} 張社交圖不存在，被 ${totalRefs} 頁宣告（掃了 ${pages.length} 頁）：`,
);
for (const [path, refs] of [...missing].sort(
  (a, b) => b[1].length - a[1].length,
)) {
  const sample = refs.slice(0, 3).join(', ');
  const more = refs.length > 3 ? ` …+${refs.length - 3}` : '';
  console.error(`   ${path}   ← ${refs.length} 頁：${sample}${more}`);
}
console.error(
  '\n   社交圖是使用者永遠不會點、只有爬蟲會抓的 URL，壞掉可以壞很久沒人發現。\n' +
    '   要嘛把圖產出來（`npm run og:generate`），要嘛改掉宣告 —— NEVER 讓它 404。',
);
process.exit(1);
