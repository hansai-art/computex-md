#!/usr/bin/env node
/**
 * check-em-dash.mjs — 讀者看得到的字串裡不准有全形破折號（—）。
 *
 * 為什麼要有這支
 *   這是站台的寫作規則之一（改用冒號），但它是那種「每次都記得、然後某次不記得」
 *   的規則：em dash 在英文文案裡是預設反射，尤其是 `Title — subtitle` 這種標題
 *   句型。2026-07-29 一次盤點就在 i18n 找到 78 行，其中 5 行還是同一天新寫的。
 *
 *   人工 review 抓不住這種東西：它不會壞、不會醜、不會有人抱怨，只會慢慢滲回來。
 *
 * 掃什麼
 *   `src/i18n/**.ts` 的字串行。註解行不算 —— 註解是寫給維護者的，中文技術寫作
 *   用「——」當插入語是正常的，讀者也看不到。
 *
 * PENDING 清單
 *   `dashboard.ts` 的 69 行還是母體 Semiont 儀表板的內容，整頁在去母體化的待辦
 *   上，會跟著整份重寫一起消失。與其把整支 gate 擱著不接（擱著就等於沒有守門，
 *   新的破折號照樣進得來），不如接上並把當下的欠債列出來 —— 跟
 *   `verify-internal-links.mjs` 的 KNOWN_DEBT 同一個處置。
 *
 *   這份清單**只准變短**。NEVER 為了讓檢查過而往這裡加檔案。
 */

import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, resolve, relative } from 'node:path';

const ROOT = process.cwd();
const I18N = resolve(ROOT, 'src/i18n');

/** 尚未去母體化、暫時豁免的檔案。只准變短。 */
const PENDING = new Set(['src/i18n/dashboard.ts']);

function walk(dir, out = []) {
  for (const e of readdirSync(dir)) {
    const full = join(dir, e);
    if (statSync(full).isDirectory()) walk(full, out);
    else if (e.endsWith('.ts')) out.push(full);
  }
  return out;
}

const hits = [];
const pendingHits = new Map();

for (const file of walk(I18N)) {
  const rel = relative(ROOT, file);
  const lines = readFileSync(file, 'utf-8').split('\n');
  lines.forEach((line, i) => {
    const trimmed = line.trim();
    // 註解行不算：中文技術寫作在註解裡用「——」是正常的，讀者看不到。
    if (
      trimmed.startsWith('*') ||
      trimmed.startsWith('//') ||
      trimmed.startsWith('/*')
    )
      return;
    if (!line.includes('—')) return;
    const entry = { rel, line: i + 1, text: trimmed.slice(0, 100) };
    if (PENDING.has(rel)) {
      pendingHits.set(rel, (pendingHits.get(rel) ?? 0) + 1);
    } else {
      hits.push(entry);
    }
  });
}

// 陳舊豁免：清單裡列了但已經乾淨的檔案。留著會讓清單失去意義。
const stale = [...PENDING].filter((f) => !pendingHits.has(f));
if (stale.length) {
  console.log(
    `ℹ️  [em-dash] PENDING 清單有 ${stale.length} 個檔案已經乾淨，可以刪掉：${stale.join(', ')}`,
  );
}

if (hits.length) {
  console.error(
    `\n❌ [em-dash] ${hits.length} 處讀者可見的字串含全形破折號：\n`,
  );
  for (const h of hits) console.error(`  ${h.rel}:${h.line}\n    ${h.text}`);
  console.error('\n改用冒號。這是站台寫作規則，不是風格偏好。\n');
  process.exit(1);
}

const pendingTotal = [...pendingHits.values()].reduce((a, b) => a + b, 0);
console.log(
  `✅ [em-dash] i18n 字串沒有新的全形破折號` +
    (pendingTotal
      ? `（已知欠債 ${pendingTotal} 處，全部在待去母體化的 ${pendingHits.size} 個檔案裡）`
      : ''),
);
