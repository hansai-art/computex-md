#!/usr/bin/env node
/**
 * 字體缺字守門員。
 *
 * 站上的思源黑體是自己託管的**子集**，只切了「產生子集當下內容用到的字」。
 * 內容會長：多一家廠商、多一篇觀察，就可能多出幾個字。那些字不在子集裡的話，
 * 瀏覽器會安靜地掉回系統字 —— 畫面不會壞，只會有一兩個字長得不太一樣，
 * 沒有人會發現，然後這件事就永遠這樣了。
 *
 * 所以這道檢查存在的意義是：讓「缺字」變成 build 紅燈，而不是一個沒人看見的
 * 視覺瑕疵。
 *
 * 為什麼讀 manifest 不讀 woff2：解析 woff2 的 cmap 需要 fonttools（Python，
 * 裝在 venv 裡）。build 是 Node，不該依賴一個要手動建的 Python 環境，那種
 * 相依性遲早會在某台機器上壞掉，然後守門員就會被當成「壞掉的檢查」拿掉。
 * manifest 帶著 woff2 的 sha256，本腳本會重算比對，所以兩者不可能悄悄失聯。
 */

import { createHash } from 'node:crypto';
import { readFileSync, existsSync } from 'node:fs';
import { readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  '../..',
);
const DIST = path.join(ROOT, 'dist');
const MANIFEST = path.join(ROOT, 'scripts/tools/font-coverage.json');

const fail = (msg) => {
  console.error(`\n✗ [font-coverage] ${msg}\n`);
  process.exit(1);
};

if (!existsSync(MANIFEST)) {
  fail(
    `找不到 ${path.relative(ROOT, MANIFEST)}。\n` +
      `  產生方式見 scripts/tools/subset-font.py 檔頭。`,
  );
}

const manifest = JSON.parse(readFileSync(MANIFEST, 'utf8'));
const fontPath = path.join(ROOT, manifest.font);

if (!existsSync(fontPath))
  fail(`manifest 指向的字體檔不存在：${manifest.font}`);

// 字體檔與 manifest 必須是同一次產生的，否則涵蓋範圍是假的
const actual = createHash('sha256')
  .update(readFileSync(fontPath))
  .digest('hex');
if (actual !== manifest.sha256) {
  fail(
    `字體檔與 manifest 對不起來（字體 ${actual.slice(0, 12)}… / ` +
      `manifest ${manifest.sha256.slice(0, 12)}…）。\n` +
      `  代表有人換了字體檔卻沒重跑子集腳本，manifest 記的涵蓋範圍已經不可信。\n` +
      `  修法：重跑 scripts/tools/subset-font.py --build`,
  );
}

const covered = new Set(manifest.codepoints);

// 只看使用者看得到的文字：把 script / style / 標籤剝掉
const STRIP =
  /<script[^>]*>[\s\S]*?<\/script>|<style[^>]*>[\s\S]*?<\/style>|<[^>]+>/g;

async function* htmlFiles(dir) {
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) yield* htmlFiles(p);
    else if (e.name.endsWith('.html')) yield p;
  }
}

if (!existsSync(DIST)) fail('找不到 dist/，請先 npm run build');

const missing = new Map(); // 字 → 第一次出現的頁面
let pages = 0;

for await (const file of htmlFiles(DIST)) {
  pages++;
  const text = readFileSync(file, 'utf8').replace(STRIP, ' ');
  for (const ch of text) {
    const cp = ch.codePointAt(0);
    // 空白與控制字元不需要字形
    if (cp < 0x21) continue;
    if (covered.has(cp)) continue;
    if (!missing.has(ch)) missing.set(ch, path.relative(DIST, file));
  }
}

if (missing.size > 0) {
  const sample = [...missing.entries()]
    .slice(0, 25)
    .map(
      ([ch, page]) =>
        `    ${ch}  U+${ch.codePointAt(0).toString(16).toUpperCase().padStart(4, '0')}  ${page}`,
    )
    .join('\n');
  fail(
    `${pages} 頁裡有 ${missing.size} 個字不在字體子集中，這些字會靜默掉回系統字：\n${sample}` +
      (missing.size > 25 ? `\n    …還有 ${missing.size - 25} 個` : '') +
      `\n\n  修法：重跑 scripts/tools/subset-font.py --build，然後 commit 新的 woff2 與 manifest`,
  );
}

console.log(
  `✅ [font-coverage] ${pages} 頁用到的字全部在子集裡（${covered.size} 個字碼，` +
    `${(manifest.bytes / 1024).toFixed(0)} KB），無 fallback 破口`,
);
