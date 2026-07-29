#!/usr/bin/env node
/**
 * verify-internal-links.mjs — 掃 dist 每一頁的每一條站內 <a href>，確認它真的
 * 指向一個存在的檔案。
 *
 * 為什麼在 verify-nav-links 之外還要這一支
 *   `verify-nav-links` 只掃 header / nav / footer，因為那三塊在每頁都一樣，取
 *   兩個樣本就夠。它抓到過 28 條死連結，然後我們以為死連結問題結束了。
 *
 *   2026-07-29 首頁改寫時發現不是：首頁 hero 底下那四張最顯眼的「讀者入口」
 *   卡片，第四張從取種那天起就指向 `/semiont` —— 母體才有的路由，本站沒有。
 *   它不在外框裡，所以 nav-links 看不到；它不是 canonical / sitemap /
 *   hreflang，所以 `check-url-contract` 也看不到（那支驗的是「我們對外宣告的
 *   網址」，不是「使用者點得到的網址」）。同一頁的四個展廳裡還有 12 條
 *   `/geography` `/history` `/food` 這種母體分類連結，同樣全部落在兩支既有
 *   檢查的視線之外。
 *
 *   結論：外框以外的正文連結需要自己的守門，而且必須掃全站，不能取樣 ——
 *   正文每頁都不一樣，取樣等於沒掃。
 *
 * 範圍
 *   只管站內 href（`/` 開頭）。站外、mailto、tel、純 anchor、協定相對一律跳過。
 *   `#` 片段與 query 在比對前砍掉：檔案存不存在跟它們無關。
 *
 * 用法
 *   node scripts/tools/verify-internal-links.mjs [dist 路徑]
 *   有死連結時 exit 1，並列出「哪一條、被幾頁引用、前三頁是誰」。
 */

import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { join, dirname, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const distDir = process.argv[2] || join(repoRoot, 'dist');

/**
 * 2026-07-29：KNOWN_DEBT 已經清空並刪除。
 *
 * 它存在過的理由是：這支檢查第一次跑就抓到 33 條死連結，全部集中在 /about、
 * /explore、/mcp 三頁 —— 那三頁的內容本體還是母體的，清這些連結等於重寫那三頁。
 * 與其把整支 gate 擱著不接（擱著就等於沒有守門），不如接上並把當下的欠債逐條
 * 列出來，讓「今天之後新增的死連結」照樣被擋。
 *
 * 三頁在同一天全部重寫完，清單也就跟著歸零，整個常數與相關分支一起刪掉 ——
 * 那本來就是這種豁免清單唯一正確的結局。
 *
 * 從現在起這支沒有豁免機制：任何一條死連結都直接擋 build。要修連結，
 * NEVER 為了讓 build 過而把豁免加回來。
 */

function walk(dir, out = []) {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) walk(full, out);
    else if (entry.endsWith('.html')) out.push(full);
  }
  return out;
}

/** dist 裡這個路徑點得到嗎（目錄式網址、直接檔案、或補 .html 都算）。 */
const resolveCache = new Map();
function resolves(urlPath) {
  if (resolveCache.has(urlPath)) return resolveCache.get(urlPath);
  let ok;
  const clean = decodeURIComponent(urlPath.split(/[?#]/)[0]);
  if (clean === '/' || clean === '') {
    ok = existsSync(join(distDir, 'index.html'));
  } else {
    const rel = clean.replace(/^\/+/, '').replace(/\/+$/, '');
    ok =
      existsSync(join(distDir, rel, 'index.html')) ||
      existsSync(join(distDir, rel)) ||
      existsSync(join(distDir, `${rel}.html`));
  }
  resolveCache.set(urlPath, ok);
  return ok;
}

if (!existsSync(distDir)) {
  console.error(`❌ [internal-links] 找不到 ${distDir}。先跑 npm run build。`);
  process.exit(1);
}

const pages = walk(distDir);
if (pages.length === 0) {
  console.error(`❌ [internal-links] ${distDir} 裡一個 HTML 都沒有。`);
  process.exit(1);
}

const dead = new Map(); // href → 引用它的頁面清單
let checked = 0;

for (const file of pages) {
  const html = readFileSync(file, 'utf-8');
  for (const m of html.matchAll(/<a\b[^>]*?\bhref="([^"]+)"/g)) {
    const href = m[1];
    if (!href.startsWith('/') || href.startsWith('//')) continue;
    checked += 1;
    if (resolves(href)) continue;
    if (!dead.has(href)) dead.set(href, []);
    dead.get(href).push(relative(distDir, file).split(sep).join('/'));
  }
}

const fresh = [...dead];

if (fresh.length === 0) {
  console.log(
    `✅ [internal-links] ${pages.length} 頁共 ${checked} 條站內連結沒有死連結`,
  );
  process.exit(0);
}

const totalRefs = fresh.reduce((a, [, refs]) => a + refs.length, 0);
console.error(
  `❌ [internal-links] ${fresh.length} 條死連結，被引用 ${totalRefs} 次（掃了 ${pages.length} 頁 / ${checked} 條連結）：`,
);
for (const [href, refs] of fresh.sort((a, b) => b[1].length - a[1].length)) {
  const sample = refs.slice(0, 3).join(', ');
  const more = refs.length > 3 ? ` …+${refs.length - 3}` : '';
  console.error(`   ${href}   ← ${refs.length} 頁：${sample}${more}`);
}
console.error(
  '\n   站內連結只准指向 src/pages/ 真的產得出來的路由。\n' +
    '   要嘛把頁面補上，要嘛把連結拿掉 —— NEVER 留著等使用者點到 404，\n' +
    '   也 NEVER 為了讓 build 過而把豁免清單加回來（2026-07-29 已清空刪除）。',
);
process.exit(1);
