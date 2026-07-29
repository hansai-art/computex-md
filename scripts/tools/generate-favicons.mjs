#!/usr/bin/env node
/**
 * generate-favicons.mjs — 產生全套站台圖示（favicon + apple-touch-icon）。
 *
 * 為什麼要有這支
 *   取種帶進來的圖示是母體的：`favicon.png` 是台灣地形圖，`favicon.svg` 是中華
 *   民國國旗。兩者對這個站都不對 —— 一個是別的專案的識別，一個是這個站沒有要
 *   表態的東西。而且 favicon 是**每個分頁、每個書籤、每次分享**都會出現的圖，
 *   換掉它的優先度比看起來高。
 *
 * 這顆標記是什麼
 *   品牌黑圓角方塊 + 白色 `md` + 洋紅的那一點。它直接從站台字標
 *   `COMPUTEX.md` 裁下來 —— 16px 放不下 COMPUTEX 八個字母，但放得下副檔名，
 *   而副檔名正好是這個專案的主張（一個知識庫就是一堆 .md 檔）。
 *
 *   **刻意不用 COMPUTEX 官方 logo 的洋紅平行四邊形。** 那是主辦單位的商標，
 *   本站目前未獲授權（README 與 /about 都寫明非官方），把它放進 favicon 等於
 *   在每個分頁標籤上暗示官方背書。brand-spec.md 的禁區第四條就是這件事。
 *
 * 怎麼產
 *   Playwright 渲染一次 HTML（用真的字體、真的 kerning），再逐尺寸截圖。
 *   .ico 由本檔自己組：ICO 容器允許直接內嵌 PNG payload，所以 16/32/48 三張
 *   PNG 加一個 22 bytes 的表頭就是合法的多尺寸 .ico，不需要額外的原生依賴。
 *
 * 用法
 *   node scripts/tools/generate-favicons.mjs
 *   （不進 prebuild：圖示不會自己漂移，改了標記才需要手動重跑一次並 commit。）
 */

import { chromium } from 'playwright';
import { writeFileSync, unlinkSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const publicDir = join(repoRoot, 'public');

const INK = '#ffffff';
const GROUND = '#252126';
const MAGENTA = '#E4007E';

/**
 * 尺寸表。apple-touch-icon 的檔名尺寸就是它宣告的尺寸，逐一產以免縮放糊掉。
 * `apple-touch-icon.png` 與 `-precomposed.png` 沒帶尺寸，沿用原本的 256。
 */
const PNG_TARGETS = [
  ['favicon.png', 256],
  ['apple-touch-icon.png', 256],
  ['apple-touch-icon-precomposed.png', 256],
  ['apple-touch-icon-57x57.png', 57],
  ['apple-touch-icon-57x57-precomposed.png', 57],
  ['apple-touch-icon-60x60.png', 60],
  ['apple-touch-icon-72x72.png', 72],
  ['apple-touch-icon-72x72-precomposed.png', 72],
  ['apple-touch-icon-76x76.png', 76],
  ['apple-touch-icon-114x114.png', 114],
  ['apple-touch-icon-114x114-precomposed.png', 114],
  ['apple-touch-icon-120x120.png', 120],
  ['apple-touch-icon-120x120-precomposed.png', 120],
  ['apple-touch-icon-144x144.png', 144],
  ['apple-touch-icon-144x144-precomposed.png', 144],
  ['apple-touch-icon-152x152.png', 152],
  ['apple-touch-icon-152x152-precomposed.png', 152],
  ['apple-touch-icon-167x167.png', 167],
  ['apple-touch-icon-180x180.png', 180],
  ['apple-touch-icon-180x180-precomposed.png', 180],
];

/** .ico 內含的尺寸。16 是分頁列，32 是書籤/高 DPI，48 是 Windows 捷徑。 */
const ICO_SIZES = [16, 32, 48];

/**
 * 標記的 HTML。
 *
 * 小尺寸的取捨：16px 下圓角與字重都會糊，所以圓角用尺寸的比例（不是固定 px），
 * 字重直接開到 900。洋紅只給那一點，其他全白 —— 洋紅 = 現在式，這條紀律在最小
 * 的圖上也守得住，而且那一點是 16px 下唯一還能被認出來的特徵。
 */
function markHtml(size) {
  const radius = Math.round(size * 0.18);
  // 字級寫成一個值、洋紅只換顏色不換字級 —— 兩個字級會讓基線對不齊，點會浮在
  // 半空（第一版踩過，點還被切掉在左邊界外）。
  //
  // 用無襯線不用襯線：襯線的細筆畫在 16px native render 下整團糊成灰塊，實測
  // 「md」讀起來像污漬。這也跟 OG 卡的浮水印一致 —— 那裡 `.md` 本來就是
  // Noto Sans TC，襯線只給 COMPUTEX 字標本身。
  const fontSize = Math.round(size * 0.42);
  return `<!doctype html>
<html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@700;900&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: ${size}px; height: ${size}px; background: transparent; overflow: hidden; }
  .mark {
    width: ${size}px; height: ${size}px;
    border-radius: ${radius}px;
    background: ${GROUND};
    display: flex; align-items: center; justify-content: center;
    font-family: 'Noto Sans TC', system-ui, -apple-system, sans-serif;
    font-weight: 900;
    font-size: ${fontSize}px;
    line-height: 1;
    letter-spacing: -0.02em;
    color: ${INK};
    -webkit-font-smoothing: antialiased;
  }
  .dot { color: ${MAGENTA}; }
</style></head>
<body><div class="mark"><span><span class="dot">.</span>md</span></div></body></html>`;
}

/** 最小的合法 ICO：6 bytes 表頭 + 每張 16 bytes 目錄項 + PNG payload 直接內嵌。 */
function buildIco(pngs) {
  const header = Buffer.alloc(6);
  header.writeUInt16LE(0, 0); // reserved
  header.writeUInt16LE(1, 2); // type: 1 = icon
  header.writeUInt16LE(pngs.length, 4);

  let offset = 6 + pngs.length * 16;
  const entries = [];
  for (const { size, data } of pngs) {
    const e = Buffer.alloc(16);
    e.writeUInt8(size >= 256 ? 0 : size, 0); // width（256 用 0 表示）
    e.writeUInt8(size >= 256 ? 0 : size, 1); // height
    e.writeUInt8(0, 2); // palette count
    e.writeUInt8(0, 3); // reserved
    e.writeUInt16LE(1, 4); // color planes
    e.writeUInt16LE(32, 6); // bits per pixel
    e.writeUInt32LE(data.length, 8);
    e.writeUInt32LE(offset, 12);
    entries.push(e);
    offset += data.length;
  }
  return Buffer.concat([header, ...entries, ...pngs.map((p) => p.data)]);
}

async function shoot(page, size) {
  await page.setViewportSize({ width: size, height: size });
  await page.setContent(markHtml(size), { waitUntil: 'domcontentloaded' });
  try {
    await page.evaluate(() => document.fonts.ready);
    await page.evaluate(() => document.fonts.load('900 40px "Noto Sans TC"'));
  } catch {
    /* 字體載不到就用 fallback sans 出圖，不擋 */
  }
  await page.evaluate(
    () =>
      new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))),
  );
  return page.screenshot({
    type: 'png',
    omitBackground: true,
    clip: { x: 0, y: 0, width: size, height: size },
  });
}

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

try {
  for (const [name, size] of PNG_TARGETS) {
    const buf = await shoot(page, size);
    writeFileSync(join(publicDir, name), buf);
    console.log(`  ✓ ${name} (${size}×${size})`);
  }

  const icoParts = [];
  for (const size of ICO_SIZES) {
    icoParts.push({ size, data: await shoot(page, size) });
  }
  writeFileSync(join(publicDir, 'favicon.ico'), buildIco(icoParts));
  console.log(`  ✓ favicon.ico (${ICO_SIZES.join('/')})`);
} finally {
  await browser.close();
}

/**
 * favicon.svg 沒有被 Layout.astro 引用，但工具與部分瀏覽器會去探 /favicon.svg，
 * 所以留一份對得上的（原本躺在那裡的是母體的中華民國國旗）。
 *
 * 這裡用 <text> 而不是把字轉成路徑：轉路徑要嵌字型或做字形描邊，收益不值得。
 * 拿不到 Noto Sans TC 的環境會退到系統無襯線體，字形略有差異但仍然是
 * 「黑底 + 白 md + 洋紅點」，不會變成別的東西。
 */
const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <rect width="32" height="32" rx="6" fill="${GROUND}"/>
  <text x="16" y="16" fill="${INK}"
        font-family="'Noto Sans TC',system-ui,-apple-system,sans-serif"
        font-weight="900" font-size="13.5" letter-spacing="-0.3"
        text-anchor="middle" dominant-baseline="central"><tspan fill="${MAGENTA}">.</tspan>md</text>
</svg>
`;
writeFileSync(join(publicDir, 'favicon.svg'), svg);
console.log('  ✓ favicon.svg');

// 母體的 og:image 早就換掉了，這裡順手確認沒有殘留的舊圖示檔名還躺在 public/。
for (const stale of ['favicon-taiwan.png', 'taiwan-social.jpg']) {
  const p = join(publicDir, stale);
  if (existsSync(p)) {
    unlinkSync(p);
    console.log(`  ✗ 刪掉殘留：${stale}`);
  }
}

console.log(
  `\n✅ 圖示產生完成：${PNG_TARGETS.length} 個 PNG + favicon.ico + favicon.svg`,
);
