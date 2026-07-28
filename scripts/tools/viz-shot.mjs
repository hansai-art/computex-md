#!/usr/bin/env node
/**
 * viz-shot.mjs — tw-* 視覺模組逐元件截圖（像素層驗證儀器）
 *
 * 為什麼存在：2026-06-12 viz-evolution 視覺體檢發現 v1.0 模組（tw-quote 雙重框 /
 * tw-heatmap 字色）在 production 壞了六天，而 6/06 的驗證紀錄全綠——當時用 curl
 * 驗 markup 存在，沒有看像素。「存在了」跟「長對了」是兩種驗證；本工具把後者
 * 做成一條命令。對應 graph.md §七 視覺化檢查清單「人工 preview」的具體儀器 +
 * LESSONS 2026-06-12 viz-evolution（presence vs appearance）。
 *
 * 用法（dev server 先跑起來，預設 port 4322）：
 *   node scripts/tools/viz-shot.mjs                          # 型錄頁全模組 × light/dark/mobile
 *   node scripts/tools/viz-shot.mjs --page /society/國宅與居住正義/
 *   node scripts/tools/viz-shot.mjs --variants light,dark    # 只跑桌機雙主題
 *   node scripts/tools/viz-shot.mjs --out /tmp/my-shots
 *
 * 模組清單從頁面自動偵測（class 恰為 tw-xxx 一段者），renderer 長新模組不用改這裡。
 * 產出 PNG 後逐張人眼看過才算驗證完成——工具只負責把眼睛要看的東西排出來。
 */
import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';

const args = process.argv.slice(2);
const getArg = (name, dflt) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 && args[i + 1] ? args[i + 1] : dflt;
};

const PORT = getArg('port', '4322');
// 型錄頁住 knowledge/About/，recat 時本預設值要跟著搬——2026-07-16 曾 404 一個月沒人發現
const PAGE = getArg(
  'page',
  '/about/%E8%A6%96%E8%A6%BA%E5%8C%96%E6%A8%A1%E7%B5%84%E5%9E%8B%E9%8C%84/',
);
const OUT = getArg('out', '/tmp/viz-shots');
const VARIANTS = getArg('variants', 'light,dark,mobile').split(',');
const URL = `http://localhost:${PORT}${PAGE}`;

const VARIANT_DEFS = {
  light: { width: 1280, theme: 'light' },
  dark: { width: 1280, theme: 'dark' },
  mobile: { width: 390, theme: 'light' },
  'mobile-dark': { width: 390, theme: 'dark' },
};

await mkdir(OUT, { recursive: true });
const browser = await chromium.launch();
let total = 0;
let failed = 0;

for (const vName of VARIANTS) {
  const v = VARIANT_DEFS[vName];
  if (!v) {
    console.error(`SKIP unknown variant: ${vName}`);
    continue;
  }
  const page = await browser.newPage({
    viewport: { width: v.width, height: 900 },
  });
  await page.goto(URL, { waitUntil: 'networkidle' });
  await page.evaluate((t) => {
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem('theme', t);
  }, v.theme);
  await page.waitForTimeout(400);

  // 自動偵測頁上的模組容器：class 恰為一段 tw-xxx（排除 tw-mod-title / tw-sr-only 等子元素）
  const mods = await page.evaluate(() => {
    const found = new Set();
    document.querySelectorAll('[class*="tw-"]').forEach((el) => {
      el.classList.forEach((c) => {
        if (/^tw-[a-z]+$/.test(c)) found.add(c);
      });
    });
    return [...found].sort();
  });
  if (mods.length === 0) {
    // 空頁 = 儀器對著 404 或壞掉的 render 截圖，靜默 WARN 會讓這種故障放一個月
    // 沒人發現（2026-07-16 型錄頁 recat 後預設路徑 404 案例）。fail loud。
    failed++;
    console.error(`FAIL ${vName}: 頁面上沒偵測到任何 tw-* 模組`);
  }

  for (const m of mods) {
    const el = page.locator(`.${m}`).first();
    try {
      await el.scrollIntoViewIfNeeded();
      await page.waitForTimeout(120);
      await el.screenshot({ path: `${OUT}/${m}-${vName}.png` });
      total++;
    } catch (e) {
      failed++;
      console.error(`FAIL ${m}-${vName}: ${e.message.split('\n')[0]}`);
    }
  }
  await page.close();
  console.log(`done ${vName}: ${mods.length} modules`);
}
await browser.close();
console.log(`${total} shots → ${OUT}${failed ? ` (${failed} FAILED)` : ''}`);
process.exit(failed ? 1 : 0);
