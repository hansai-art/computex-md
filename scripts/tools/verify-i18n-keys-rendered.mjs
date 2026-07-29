#!/usr/bin/env node
/**
 * i18n 裸 key 守門員。
 *
 * ## 這道檢查在防什麼
 *
 * `useTranslations()` 的最後一行是 `?? String(key)`：找不到翻譯就把 key 本身
 * 當成內容回傳。這個 fallback 本身沒錯（總比整頁炸掉好），但它的失敗形態是
 * **靜默且長得像內容**：2026-07-30 全站每一頁的搜尋 modal 上都掛著六顆寫著
 * `explore.hotSearches.term1` 的按鈕，做成 chip、可以點、點下去搜出 0 筆，
 * 從取種那天起就在線上，沒有任何測試或 lint 叫過一聲。
 *
 * 靜態掃 `t('...')` 擋不住它，因為那行是 `t(\`...\${n}\` as any)` —— 動態字串
 * 組出來的 key，再加一個 `as any` 把型別防線關掉。**能擋的只有看輸出。**
 *
 * ## 判準
 *
 * 掃 dist 的文字節點，整段（trim 後）長得像 `namespace.a.b` 而且第一段是真的
 * i18n namespace 才算違規。namespace 清單從 src/i18n/*.ts 現讀，不寫死：新增
 * 一組 key 就自動納入守備範圍，沒有人需要記得回來更新這支。
 */

import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  '../..',
);
const DIST = path.join(ROOT, 'dist');
const I18N = path.join(ROOT, 'src/i18n');

const fail = (msg) => {
  console.error(`\n✗ [i18n-keys] ${msg}\n`);
  process.exit(1);
};

if (!existsSync(DIST)) fail('找不到 dist/，請先 npm run build');

// ── 從字典現讀 namespace 與完整 key 集合 ──
const allKeys = new Set();
const namespaces = new Set();
for (const f of readdirSync(I18N)) {
  if (!f.endsWith('.ts')) continue;
  const src = readFileSync(path.join(I18N, f), 'utf8');
  for (const m of src.matchAll(/^\s*'([a-zA-Z][a-zA-Z0-9_.-]*)':/gm)) {
    const key = m[1];
    if (!key.includes('.')) continue;
    allKeys.add(key);
    namespaces.add(key.split('.')[0]);
  }
}
if (namespaces.size === 0)
  fail('從 src/i18n/*.ts 讀不到任何 key，這支檢查等於沒在跑');

// 整段文字就是一個 key 的形狀：namespace.something(.something…)
const KEY_SHAPE = /^[a-zA-Z][a-zA-Z0-9]*(?:\.[a-zA-Z0-9_-]+){1,4}$/;
// script / style 內容是程式碼，本來就會出現 key 字面（例如 i18n bundle 本身）
const STRIP = /<script[^>]*>[\s\S]*?<\/script>|<style[^>]*>[\s\S]*?<\/style>/g;
const TEXT_NODES = />([^<>]+)</g;

async function* htmlFiles(dir) {
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) yield* htmlFiles(p);
    else if (e.name.endsWith('.html')) yield p;
  }
}

const offenders = new Map(); // key → { pages:Set, known:boolean }
let pages = 0;

for await (const file of htmlFiles(DIST)) {
  pages++;
  const html = readFileSync(file, 'utf8').replace(STRIP, ' ');
  for (const m of html.matchAll(TEXT_NODES)) {
    const text = m[1].trim();
    if (!text || text.length > 80) continue;
    if (!KEY_SHAPE.test(text)) continue;
    if (!namespaces.has(text.split('.')[0])) continue;
    if (!offenders.has(text))
      offenders.set(text, { pages: new Set(), known: allKeys.has(text) });
    const rec = offenders.get(text);
    if (rec.pages.size < 3) rec.pages.add(path.relative(DIST, file));
  }
}

if (offenders.size > 0) {
  const lines = [...offenders.entries()].map(([key, rec]) => {
    // 字典裡有這個 key 卻仍印出字面 → 多半是 render 端漏了 t()；
    // 字典裡沒有 → 就是打錯 / 指著別的專案的 key。兩種都要修，訊息分開講。
    const why = rec.known
      ? '字典裡有這個 key，但頁面印的是 key 本身（漏了 t()？）'
      : '字典裡沒有這個 key，t() 於是回傳 key 字面';
    return `    ${key}\n      ${why}\n      出現在：${[...rec.pages].join(', ')}`;
  });
  fail(
    `${pages} 頁裡有 ${offenders.size} 個 i18n key 直接印在畫面上：\n` +
      lines.join('\n') +
      `\n\n  這種洞不會讓頁面壞掉，只會讓讀者看到一段沒人看得懂的字串。` +
      `\n  修法：把 key 補進 src/i18n/ 對應字典，或改成真的有值的資料來源。`,
  );
}

console.log(
  `✅ [i18n-keys] ${pages} 頁沒有裸露的 i18n key（守備 ${namespaces.size} 個 namespace / ${allKeys.size} 個 key）`,
);
