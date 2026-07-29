#!/usr/bin/env node
/**
 * verify-no-inherited-accounts.mjs — 母體的第三方帳號不准出現在產出裡。
 *
 * 為什麼要有這支
 *   2026-07-29 盤點時發現，取種帶進來的 `src/layouts/Layout.astro` 把 taiwan.md
 *   的兩個第三方帳號寫死在**每一頁都會載入的位置**：
 *
 *     G-JGC5W00N7T   Google Analytics 資源 ID
 *     _jf.push(['p', '65854'])   justfont webfont 專案
 *
 *   兩行都跟母體 repo 裡的那一行一字不差。效果是：本站每一次瀏覽都把訪客資料
 *   回報進別人的 GA 資源（我們自己一筆也看不到），每一次載入都消耗別人的
 *   webfont 額度。
 *
 *   這一類錯的特徵是**它不會壞**。頁面照常渲染、CI 全綠、Lighthouse 不扣分，
 *   沒有任何症狀會指向它；要嘛有人去讀那 200 行 vendor blob，要嘛永遠不會發現。
 *   所以它只能靠機器守。
 *
 * 掃什麼
 *   dist 的所有 .html 與 .js，逐條比對已知的母體帳號指紋。命中就擋 build。
 *
 * 這支不是「安全掃描」
 *   它不通用、也不打算通用。它只認**這一份**繼承清單，因為那正是它要防的東西：
 *   繁殖出來的站帶著母體的帳號跑。新增第三方服務時，把新的 ID 用環境變數接進來
 *   （NEVER 寫死），並把母體對應的 ID 加進下面的清單。
 */

import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, resolve, relative } from 'node:path';

const DIST = resolve(process.cwd(), 'dist');

/**
 * 母體（frank890417/taiwan-md）的第三方帳號指紋。
 * 每一條都是實際出現在母體 src/layouts/Layout.astro 裡的字串。
 */
const INHERITED = [
  {
    id: 'G-JGC5W00N7T',
    what: 'taiwan.md 的 Google Analytics 資源',
    fix: '本站的 GA 從 PUBLIC_GA_MEASUREMENT_ID 讀；沒設定就整段不輸出。',
  },
  {
    id: "_jf.push(['p', '65854']",
    what: 'taiwan.md 的 justfont webfont 專案 65854',
    fix: 'justfont SDK 已整段移除。要重新接上，先自己買專案，ID 從環境變數讀。',
  },
  {
    id: 'taiwanmd.mcpb',
    what: '母體作者打包的 MCP connector',
    fix: '已從 public/ 移除；/mcp 頁只列本站真的有的東西。',
  },
];

const EXT = new Set(['.html', '.js', '.mjs', '.json', '.txt', '.xml']);

function walk(dir, out = []) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full, out);
      continue;
    }
    const dot = entry.name.lastIndexOf('.');
    if (dot > -1 && EXT.has(entry.name.slice(dot))) out.push(full);
  }
  return out;
}

let files;
try {
  files = walk(DIST);
} catch {
  console.error('❌ [inherited-accounts] dist 不存在，先 build');
  process.exit(1);
}

/** fingerprint id → 命中的檔案清單 */
const hits = new Map();

for (const file of files) {
  let text;
  try {
    text = readFileSync(file, 'utf-8');
  } catch {
    continue; // 二進位檔，跳過
  }
  for (const { id } of INHERITED) {
    if (text.includes(id)) {
      if (!hits.has(id)) hits.set(id, []);
      hits.get(id).push(relative(DIST, file));
    }
  }
}

if (hits.size) {
  console.error(
    `\n❌ [inherited-accounts] 產出裡有 ${hits.size} 個母體帳號：\n`,
  );
  for (const { id, what, fix } of INHERITED) {
    const where = hits.get(id);
    if (!where) continue;
    console.error(`  ${id}`);
    console.error(`    是什麼：${what}`);
    console.error(
      `    出現在：${where.length} 個檔案，例如 ${where.slice(0, 3).join(', ')}`,
    );
    console.error(`    怎麼修：${fix}\n`);
  }
  console.error(
    '這不是設定沒改到，是把別人的帳號當成自己的在用。第三方 ID 一律從環境變數讀，\n' +
      'NEVER 給預設值 —— 有預設值的那一天，就是它又靜靜指回別人帳號的那一天。\n',
  );
  process.exit(1);
}

console.log(
  `✅ [inherited-accounts] ${files.length} 個產出檔裡沒有母體的第三方帳號` +
    `（比對 ${INHERITED.length} 條指紋）`,
);
