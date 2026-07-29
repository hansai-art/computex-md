#!/usr/bin/env node
/**
 * verify-nav-links.mjs — 掃 dist，確認站台外框（header / nav / footer）的每一條
 * 站內連結都指向真的存在的檔案。
 *
 * 為什麼需要這支
 *   2026-07-29 實測：站台外框有 44 條站內連結，其中 **28 條是 404**，而且出現在
 *   全部 127 頁上。既有的 `verify-announced-urls` 一路報 0 dead，因為它只驗
 *   canonical / sitemap / hreflang —— 那三個是「我們對外宣告的網址」，不是
 *   「使用者點得到的網址」。兩者的交集比想像中小。
 *
 *   壞掉的原因也很單純：站體是從 taiwan-md 取種的，導覽列整份指向母體的路由
 *   （/map、/soundscape、/bench、/elections/2026、/history…）。取種當下不會爆，
 *   因為 Astro 不驗 href；要等到有人點下去才知道。
 *
 * 做法
 *   拿首頁 + 一篇文章頁當樣本（外框在每頁都一樣，不必掃 127 份），抽出
 *   header/nav/footer 裡的站內 href，逐條在 dist 找對應檔案。
 *   外部連結、mailto、tel、純 anchor 一律跳過 —— 這支只管站內。
 *
 * 用法
 *   node scripts/tools/verify-nav-links.mjs [dist 路徑]
 *   有死連結時 exit 1。
 */

import { existsSync, readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const distDir = process.argv[2] || join(repoRoot, 'dist');

/** 外框在每頁都一樣，取兩個樣本就夠：首頁 + 任一文章頁。 */
const SAMPLES = ['index.html', 'vendors/wiwynn/index.html', 'about/index.html'];

const CHROME_TAGS = ['header', 'nav', 'footer'];

function chromeHtml(html) {
  let out = '';
  for (const tag of CHROME_TAGS) {
    const re = new RegExp(`<${tag}[\\s>][\\s\\S]*?</${tag}>`, 'g');
    for (const m of html.matchAll(re)) out += m[0];
  }
  return out;
}

/** dist 裡這個路徑點得到嗎（目錄式網址或直接檔案都算）。 */
function resolves(urlPath) {
  const clean = decodeURIComponent(urlPath.split(/[?#]/)[0]);
  if (clean === '/' || clean === '')
    return existsSync(join(distDir, 'index.html'));
  const rel = clean.replace(/^\/+/, '').replace(/\/+$/, '');
  return (
    existsSync(join(distDir, rel, 'index.html')) ||
    existsSync(join(distDir, rel)) ||
    existsSync(join(distDir, `${rel}.html`))
  );
}

const dead = new Map(); // path → 出現在哪些樣本
let checked = 0;
let scanned = 0;

for (const sample of SAMPLES) {
  const file = join(distDir, sample);
  if (!existsSync(file)) continue;
  scanned += 1;
  const chrome = chromeHtml(readFileSync(file, 'utf-8'));
  for (const m of chrome.matchAll(/href="([^"]+)"/g)) {
    const href = m[1];
    // 站外 / mailto / tel / 純 anchor / 協定相對：不歸這支管
    if (!href.startsWith('/') || href.startsWith('//')) continue;
    checked += 1;
    if (resolves(href)) continue;
    if (!dead.has(href)) dead.set(href, new Set());
    dead.get(href).add(sample);
  }
}

if (scanned === 0) {
  console.error(
    `❌ [nav-links] 在 ${distDir} 找不到任何樣本頁。先跑 npm run build。`,
  );
  process.exit(1);
}

if (dead.size === 0) {
  console.log(
    `✅ [nav-links] 站台外框 ${checked} 條站內連結全部指向存在的頁面（掃了 ${scanned} 個樣本）`,
  );
  process.exit(0);
}

console.error(
  `❌ [nav-links] 站台外框有 ${dead.size} 條死連結（共檢查 ${checked} 條）：`,
);
for (const [href, samples] of [...dead].sort()) {
  console.error(`   ${href}   ← ${[...samples].join(', ')}`);
}
console.error(
  '\n   導覽列與頁尾只准指向 src/pages/ 真的產得出來的路由。\n' +
    '   要嘛把頁面補上，要嘛把連結拿掉 —— NEVER 留著等使用者點到 404。',
);
process.exit(1);
