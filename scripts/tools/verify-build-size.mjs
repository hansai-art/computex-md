#!/usr/bin/env node
/**
 * verify-build-size.mjs — dist 有多大，以及那個大小離額度天花板還有多遠。
 *
 * 為什麼要有這支（CLAUDE.md rule 57，此類第四次重踩的預防）
 *   `deploy.yml` 每次 push 都把整個 dist 當 artifact 上傳。GitHub 免費帳號的
 *   Actions storage 是 500MB，而 pages artifact 預設保留 1 天，所以真正的算式是
 *
 *     同時存在量 = 單份壓縮後大小 × 保留期（天）× 每日觸發次數
 *
 *   這個算式沒有人會在寫 PR 時想起來。它的特性是**長期無感、然後某一天整個爆掉**：
 *   aiterms-tw 2026-07-05 為了省 Actions 分鐘改成上傳 53MB dist，天花板瞬間掉到
 *   「每天推 10 次」，07-25 推了 11 次就爆。爆的那天看起來跟內容完全無關。
 *
 *   所以這支不是為了「讓 dist 變小」，是為了**讓那個乘法在每次 build 都被算一次
 *   並印出來**。數字自己會說話：離天花板還有幾次 push。
 *
 * 為什麼量 apparent size 而不是實際壓縮
 *   壓縮一次要兩秒多，而且結果依 tar 實作而異（runner 是 GNU tar、開發機是
 *   bsdtar）。改成量「檔案位元組總和」：快、精確、跨平台一致，再乘一個實測的
 *   壓縮比。壓縮比會隨內容組成漂移（圖片多就接近 1，HTML 多就更小），所以它
 *   標了實測日期與重測指令，不是憑感覺填的常數。
 *
 *     2026-07-29 實測：dist 51.8 MB（614 檔）→ tar.gz 21.5 MB，比值 0.415
 *     重測：tar -czf - dist | wc -c
 *
 * 天花板怎麼定
 *   500MB ÷ 20 次/天 ÷ 1 天保留 = 每份 25MB 壓縮後。
 *   25MB ÷ 0.415 ≈ 60MB apparent。取 60MB 當硬天花板。
 *
 *   「每天 20 次」是這個專案現在的節奏上限（實際遠低於此）。要放寬天花板，
 *   MUST 重跑這個算式並把新的假設寫進來，NEVER 只是把數字調大 —— 調大數字
 *   而不重算，就是把天花板從「算出來的」變成「感覺夠用的」。
 *
 * 用法
 *   node scripts/tools/verify-build-size.mjs   （掛在 postbuild）
 */

import { readdirSync, statSync } from 'node:fs';
import { join, resolve, extname } from 'node:path';

const DIST = resolve(process.cwd(), 'dist');

/** 實測壓縮比（見檔頭）。重測指令：tar -czf - dist | wc -c */
const COMPRESSION_RATIO = 0.415;
const COMPRESSION_MEASURED_ON = '2026-07-29';

/** Actions storage 免費額度與這個專案假設的推送節奏 */
const FREE_STORAGE_MB = 500;
const ASSUMED_PUSHES_PER_DAY = 20;
const RETENTION_DAYS = 1; // upload-pages-artifact 的預設

/** 硬天花板（apparent MB）。改這個數字前先重跑檔頭的算式。 */
const BUDGET_MB = 60;

function walk(dir, out = { bytes: 0, files: 0, byExt: new Map() }) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full, out);
      continue;
    }
    const size = statSync(full).size;
    out.bytes += size;
    out.files += 1;
    const ext = extname(entry.name).toLowerCase() || '(no ext)';
    const prev = out.byExt.get(ext) ?? { bytes: 0, files: 0 };
    out.byExt.set(ext, { bytes: prev.bytes + size, files: prev.files + 1 });
  }
  return out;
}

const mb = (bytes) => bytes / 1_000_000;
const fmt = (bytes) => `${mb(bytes).toFixed(1)} MB`;

let stats;
try {
  stats = walk(DIST);
} catch {
  console.error('❌ [build-size] dist 不存在，先 build');
  process.exit(1);
}

const apparentMb = mb(stats.bytes);
const compressedMb = apparentMb * COMPRESSION_RATIO;
const pushesToCeiling = Math.floor(
  FREE_STORAGE_MB / (compressedMb * RETENTION_DAYS),
);

const html = stats.byExt.get('.html') ?? { bytes: 0, files: 0 };
const perPageKb = html.files ? html.bytes / html.files / 1000 : 0;

const top = [...stats.byExt.entries()]
  .sort((a, b) => b[1].bytes - a[1].bytes)
  .slice(0, 4)
  .map(([ext, v]) => `${ext} ${fmt(v.bytes)}（${v.files} 檔）`)
  .join(' · ');

console.log(
  `[build-size] dist ${fmt(stats.bytes)}，${stats.files} 檔：${top}\n` +
    `             HTML 平均每頁 ${perPageKb.toFixed(0)} KB（${html.files} 頁）\n` +
    `             壓縮後約 ${compressedMb.toFixed(1)} MB` +
    `（比值 ${COMPRESSION_RATIO}，${COMPRESSION_MEASURED_ON} 實測）\n` +
    `             同時存在量 = ${compressedMb.toFixed(1)} MB × ${RETENTION_DAYS} 天 × 每日推送次數` +
    `　→　${FREE_STORAGE_MB}MB 額度在**每天 ${pushesToCeiling} 次**推送時用盡`,
);

if (apparentMb > BUDGET_MB) {
  console.error(
    `\n❌ [build-size] dist ${apparentMb.toFixed(1)} MB 超過預算 ${BUDGET_MB} MB。\n\n` +
      `  這不是「檔案有點大」的提醒，是額度天花板：每天推 ${pushesToCeiling} 次就會把\n` +
      `  帳號的 ${FREE_STORAGE_MB}MB Actions storage 用完，而用完那天的症狀跟內容無關，\n` +
      `  沒有人會聯想到是某個 PR 讓 dist 變大。\n\n` +
      `  先看上面哪一類副檔名長最多。要放寬預算，MUST 重跑這支檔頭的算式並把新的\n` +
      `  假設寫進去，NEVER 只是把 BUDGET_MB 調大。\n`,
  );
  process.exit(1);
}

console.log(
  `✅ [build-size] ${apparentMb.toFixed(1)} / ${BUDGET_MB} MB 預算內` +
    `（還有 ${(BUDGET_MB - apparentMb).toFixed(1)} MB 餘裕）`,
);
