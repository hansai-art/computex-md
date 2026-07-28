#!/usr/bin/env node
/**
 * twmd — COMPUTEX.md 統一 CLI 入口（thin router）
 *
 * 為什麼：scripts/ 下 98+ 個散裝工具，靠記憶找路徑（「擁有工具 ≠ 使用工具」
 * 神經迴路的結構性根因之一）。本 CLI 是純路由層：每個子命令指向 canonical
 * 工具，不複寫任何邏輯（同 article-health.py SSOT 整併哲學 + skill thin-shell
 * 範式）。新工具誕生時在 COMMANDS 表加一行即可被發現。
 *
 * 用法：
 *   node scripts/twmd.mjs <command> [args...]
 *   npm run twmd -- <command> [args...]
 *   npx twmd <command>（package.json bin 已註冊，npm install 後可用）
 *
 * 2026-06-13 refactor session 誕生。
 */
import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

// ── Command registry（architecture-as-data：加工具 = 加一行）─────────────────
// run: argv 陣列（{args} 佔位 = 使用者附加參數插入點；沒有則 append 到尾）
const COMMANDS = {
  // ── 日常 ──
  status: {
    desc: '生命徵象三件套：器官分數 + routine 跑況 + inbox backlog（BECOME ground truth）',
    cat: '日常',
    run: [
      'bash',
      '-c',
      'bash scripts/tools/consciousness-snapshot.sh; echo; bash scripts/tools/routine-status.sh; echo; bash scripts/tools/inbox-signal.sh',
    ],
  },
  sync: {
    desc: 'knowledge/ SSOT → src/content/ 投影層轉錄',
    cat: '日常',
    run: ['bash', 'scripts/core/sync.sh'],
  },
  build: {
    desc: 'astro build（不含 prebuild/postbuild；完整鏈用 npm run build）',
    cat: '日常',
    run: ['npx', 'astro', 'build'],
  },
  dev: {
    desc: 'sync + astro dev',
    cat: '日常',
    run: ['npm', 'run', 'dev'],
  },
  'session-id': {
    desc: '取 canonical session ID（YYYY-MM-DD-HHMMSS-{handle}）',
    cat: '日常',
    run: ['bash', 'scripts/tools/session-id.sh'],
  },

  // ── 品質 ──
  health: {
    desc: '文章健康 SSOT（25 plugin）：twmd health <file> 或 twmd health --all',
    cat: '品質',
    run: ['python3', 'scripts/tools/article-health.py'],
  },
  links: {
    desc: 'dist/ 內鏈驗證（multiprocessing；需先 build）',
    cat: '品質',
    run: ['bash', 'scripts/tools/verify-internal-links.sh'],
  },
  parity: {
    desc: 'refactor HTML parity 閘門：twmd parity <dist-baseline> <dist-after>',
    cat: '品質',
    run: ['bash', 'scripts/tools/build-parity-diff.sh'],
  },
  viz: {
    desc: 'tw-* 視覺模組像素閘門（light/dark/mobile 截圖）',
    cat: '品質',
    run: ['node', 'scripts/tools/viz-shot.mjs'],
  },
  frontmatter: {
    desc: 'frontmatter 驗證（CI 同款）',
    cat: '品質',
    run: ['node', 'scripts/core/test-frontmatter.mjs'],
  },

  // ── 感知 / 數據 ──
  perf: {
    desc: 'CI build 效能 trend 抓取（GitHub Actions API → dashboard-build-perf.json）',
    cat: '感知',
    run: ['node', 'scripts/core/extract-build-perf.mjs'],
  },
  'i18n-status': {
    desc: '六語言翻譯覆蓋狀態',
    cat: '感知',
    run: ['python3', 'scripts/utils/i18n-status.py'],
  },

  // ── 翻譯 ──
  translate: {
    desc: 'lang-sync 翻譯 pipeline（OpenRouter cascade）：twmd translate --help 看參數',
    cat: '翻譯',
    run: ['python3', 'scripts/tools/lang-sync/openrouter-translate.py'],
  },
};

// ── Router ───────────────────────────────────────────────────────────────────
const [cmd, ...args] = process.argv.slice(2);

function printHelp() {
  console.log(
    '🧬 twmd — COMPUTEX.md 統一 CLI（thin router，邏輯都在 canonical 工具）\n',
  );
  const cats = [...new Set(Object.values(COMMANDS).map((c) => c.cat))];
  for (const cat of cats) {
    console.log(`  ${cat}`);
    for (const [name, c] of Object.entries(COMMANDS).filter(
      ([, c]) => c.cat === cat,
    )) {
      console.log(`    twmd ${name.padEnd(14)} ${c.desc}`);
    }
    console.log('');
  }
  console.log(
    '  其他散裝工具：ls scripts/tools/（98+ 支，本表只收高頻 + 閘門類）',
  );
}

if (
  !cmd ||
  cmd === 'help' ||
  cmd === '--help' ||
  cmd === '-h' ||
  cmd === 'list'
) {
  printHelp();
  process.exit(0);
}

const entry = COMMANDS[cmd];
if (!entry) {
  // 模糊建議：前綴 / 包含
  const candidates = Object.keys(COMMANDS).filter(
    (k) => k.startsWith(cmd) || k.includes(cmd),
  );
  console.error(`❌ 未知命令：${cmd}`);
  if (candidates.length)
    console.error(`   你是不是要：${candidates.join(' / ')}`);
  console.error('   twmd help 看完整清單');
  process.exit(1);
}

const [bin, ...binArgs] = entry.run;
// sanity：被路由的工具必須存在（防 canonical 搬家後 CLI 變殭屍指標）
const target = binArgs.find((a) => a.startsWith('scripts/'));
if (target && !existsSync(resolve(ROOT, target))) {
  console.error(
    `❌ 路由目標不存在：${target}（工具搬家了？更新 scripts/twmd.mjs COMMANDS 表）`,
  );
  process.exit(1);
}

const r = spawnSync(bin, [...binArgs, ...args], {
  stdio: 'inherit',
  cwd: ROOT,
});
process.exit(r.status ?? 1);
