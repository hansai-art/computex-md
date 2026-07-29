#!/usr/bin/env node
/**
 * generate-spore-image.mjs — 產出社群孢子用附圖
 *
 * 原理：
 *   1. 開文章頁 `?shot=1` 模式（hero only、無 nav/footer/body）
 *   2. 等 justfont SDK 真的把日星宋體 `rixingsong-semibold` 載入
 *      `.hero-title`；只看 computed font-family 不夠，必須再以
 *      FontFaceSet.check() 確認指定標題字元實際可用
 *   3. screenshot 整個 viewport 存 PNG
 *
 * 日星宋體若因 justfont subset / CDN 問題無法載入，SHIP 圖直接失敗，
 * 不再以蘭陽黑或系統 fallback 字體悄悄產圖。
 *
 * REFLEXES #26 v2 合規：AI 自主生圖屬「內部處理」，Post 到 Threads/X 仍然
 * 是 human only。本腳本只產檔不發文。
 *
 * 用法：
 *   node scripts/tools/generate-spore-image.mjs --path /people/李洋/
 *   node scripts/tools/generate-spore-image.mjs --path /music/台灣民歌運動/ --size square
 *   node scripts/tools/generate-spore-image.mjs --url https://computex.taiwanai.ngo/lifestyle/台灣高鐵/ --out /tmp/x.png
 *
 * Options:
 *   --path <articlePath>  文章路徑（/category/slug/），會自動接到 --base
 *   --url <fullUrl>       完整 URL（會蓋過 --path 與 --base）
 *   --base <baseUrl>      預設 http://localhost:4321；production 用 https://computex.taiwanai.ngo
 *   --prod                捷徑：base = https://computex.taiwanai.ngo（不用 dev server）
 *   --size landscape|square|vertical  預設 landscape (1600×900)
 *   --title <str>         覆蓋文章 title（shot mode 用，不動 SSOT）
 *   --desc <str>          覆蓋文章 description（shot mode 用）
 *   --out <filePath>      輸出檔名。預設 public/spore-images/<slug>-<size>.png
 *   --timeout <ms>        等 justfont 的 timeout，預設 15000ms
 *   --no-font-wait        跳過 justfont 等待（debug 用）
 */

import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

// ── CLI parsing ──────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const getArg = (name) => {
  const i = args.indexOf(name);
  return i !== -1 ? args[i + 1] : undefined;
};
const hasFlag = (name) => args.includes(name);

const articlePath = getArg('--path');
const fullUrl = getArg('--url');
const useProd = hasFlag('--prod');
const base =
  getArg('--base') ||
  (useProd ? 'https://computex.taiwanai.ngo' : 'http://localhost:4321');
const size = getArg('--size') || 'landscape';
const titleOverride = getArg('--title');
const descOverride = getArg('--desc');
const timeout = parseInt(getArg('--timeout') || '15000', 10);
const skipFontWait = hasFlag('--no-font-wait');
let outPath = getArg('--out');

if (!fullUrl && !articlePath) {
  console.error('Error: need --path <articlePath> or --url <fullUrl>');
  console.error(
    'Example: node scripts/tools/generate-spore-image.mjs --path /people/李洋/',
  );
  process.exit(2);
}

const SIZES = {
  landscape: { w: 1600, h: 900 }, // 16:9, X/Threads feed friendly, closest to CheYu's current habit
  square: { w: 1080, h: 1080 }, // Threads 預覽不裁切
  vertical: { w: 1080, h: 1350 }, // 4:5, Instagram/Threads best for portrait
};

const viewport = SIZES[size];
if (!viewport) {
  console.error(
    `Error: --size must be one of: ${Object.keys(SIZES).join(', ')}`,
  );
  process.exit(2);
}

// Build target URL
let target;
if (fullUrl) {
  const u = new URL(fullUrl);
  u.searchParams.set('shot', '1');
  if (titleOverride) u.searchParams.set('title', titleOverride);
  if (descOverride) u.searchParams.set('desc', descOverride);
  target = u.toString();
} else {
  // articlePath like /people/李洋/  (may already be URL-encoded or not)
  const clean = articlePath.startsWith('/') ? articlePath : '/' + articlePath;
  const encoded = clean
    .split('/')
    .map((seg) =>
      seg && /[^\x00-\x7f]/.test(seg) ? encodeURIComponent(seg) : seg,
    )
    .join('/');
  const base_ = base.replace(/\/$/, '');
  const path_ = encoded.endsWith('/') ? encoded : encoded + '/';
  const params = new URLSearchParams({ shot: '1' });
  if (titleOverride) params.set('title', titleOverride);
  if (descOverride) params.set('desc', descOverride);
  target = `${base_}${path_}?${params.toString()}`;
}

// Default output path
if (!outPath) {
  const __dirname = dirname(fileURLToPath(import.meta.url));
  const repoRoot = resolve(__dirname, '..', '..');
  const slugFromUrl = (() => {
    try {
      const u = new URL(target);
      const segs = u.pathname.split('/').filter(Boolean);
      return decodeURIComponent(segs[segs.length - 1] || 'spore');
    } catch {
      return 'spore';
    }
  })();
  outPath = resolve(
    repoRoot,
    'public',
    'spore-images',
    `${slugFromUrl}-${size}.png`,
  );
}

// ── Main ─────────────────────────────────────────────────────────────────────
(async () => {
  await mkdir(dirname(outPath), { recursive: true });

  console.log(`[spore-image] target: ${target}`);
  console.log(`[spore-image] viewport: ${viewport.w}×${viewport.h}`);
  console.log(`[spore-image] output:  ${outPath}`);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: viewport.w, height: viewport.h },
    deviceScaleFactor: 2, // retina crispness
  });
  const page = await context.newPage();

  // Surface console errors so justfont / CSP / font-load problems are visible
  page.on('pageerror', (err) =>
    console.warn(`[spore-image] pageerror: ${err.message}`),
  );

  await page.goto(target, { waitUntil: 'networkidle', timeout: 30_000 });

  if (!skipFontWait) {
    // Wait for the branded Rixing typeface and verify that the exact title
    // glyphs are backed by a loaded FontFace. A computed family name alone
    // can still render through the fallback chain when the webfont failed.
    console.log('[spore-image] waiting for justfont rixingsong-semibold...');
    try {
      await page.waitForFunction(
        () => {
          const h1 = document.querySelector('.hero-title');
          if (!h1) return false;
          const ff = getComputedStyle(h1).fontFamily || '';
          return (
            document.documentElement.classList.contains('jf-active') &&
            ff.toLowerCase().includes('rixingsong-semibold')
          );
        },
        { timeout, polling: 200 },
      );
      const fontReady = await page.evaluate(async () => {
        const h1 = document.querySelector('.hero-title');
        const sample = h1?.textContent?.trim() || '台灣';
        await document.fonts.load('600 72px "rixingsong-semibold"', sample);
        await document.fonts.ready;
        return document.fonts.check('600 72px "rixingsong-semibold"', sample);
      });
      if (!fontReady) {
        throw new Error('rixingsong-semibold did not cover the title glyphs');
      }
      console.log('[spore-image] ✅ rixingsong-semibold loaded for title');
    } catch (e) {
      throw new Error(
        `justfont rixingsong-semibold unavailable after ${timeout}ms; refusing fallback screenshot: ${e.message}`,
      );
    }
  }

  // Extra settle time so font-paint & layout fully stabilise before snap
  await page.waitForTimeout(500);

  await page.screenshot({
    path: outPath,
    fullPage: false,
    omitBackground: false,
  });

  // Report dimensions and font check
  const meta = await page.evaluate(() => {
    const h1 = document.querySelector('.hero-title');
    return {
      title: h1?.textContent?.trim(),
      fontFamily: h1 ? getComputedStyle(h1).fontFamily : null,
      dataShot: document.documentElement.getAttribute('data-shot'),
    };
  });
  console.log(`[spore-image] h1: "${meta.title}"`);
  console.log(`[spore-image] font-family: ${meta.fontFamily}`);
  console.log(`[spore-image] data-shot: ${meta.dataShot}`);

  await browser.close();
  console.log(`[spore-image] ✅ saved: ${outPath}`);
})().catch((err) => {
  console.error('[spore-image] fatal:', err);
  process.exit(1);
});
