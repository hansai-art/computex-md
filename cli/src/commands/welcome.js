/**
 * commands/welcome.js — what `npx taiwanmd` says when you give it nothing.
 *
 * COMPUTEX.md had five distribution surfaces and no install path: a website, an
 * npm CLI, a local MCP server, a remote MCP endpoint, a desktop bundle, plus a
 * cognitive layer and node contract reachable only by cloning 849 MB. Each one
 * answered a different question, none of them told you the others existed.
 *
 * So there was nothing to hand a friend. This screen is that thing. One line
 * you can pass along (`npx taiwanmd`), and the person who runs it can see the
 * whole ladder: read it, ask it, write with it, become one of its nodes.
 *
 * Design report: reports/design-taiwanmd-node-app-distribution-2026-07-26.md §七
 */

import chalk from 'chalk';
import { getArticleFiles, getLanguageDirs } from '../lib/knowledge.js';
import { getDataAgeDays } from '../lib/ensure-data.js';

const UPSTREAM = 'hansai-art/computex-md';

/** Article count + language count, counted rather than claimed. */
function vitals() {
  let articles = null;
  let languages = null;
  try {
    articles = getArticleFiles().length;
  } catch {
    /* no local data yet — fall through to the generic line */
  }
  try {
    const langs = getLanguageDirs();
    // +1 for zh-TW, which is the SSOT and has no language directory of its own.
    if (langs) languages = langs.size + 1;
  } catch {
    /* same */
  }
  return { articles, languages };
}

/** One line about how current the local copy is. Silence here is what let a
 *  97-day-old snapshot answer questions as though it were today's. */
function freshnessLine() {
  const age = getDataAgeDays();
  if (age === null) return chalk.gray('  知識庫：直接讀 repo（隨 git 更新）');
  if (age >= 60)
    return chalk.yellow(`  知識庫：${age} 天前的版本 — 跑 taiwanmd sync 更新`);
  if (age >= 14)
    return chalk.yellow(`  知識庫：${age} 天前同步 — 建議跑 taiwanmd sync`);
  return chalk.gray(`  知識庫：${age} 天前同步（新鮮）`);
}

export function printWelcome() {
  const { articles, languages } = vitals();
  const scale =
    articles && languages
      ? `${articles} 篇文章，${languages} 種語言`
      : '關於台灣的開源知識庫';

  const rungs = [
    {
      n: '1',
      label: '讀',
      en: 'read',
      cmd: 'https://computex-md.pages.dev',
      note: '網站，十二種語言',
    },
    {
      n: '2',
      label: '問我',
      en: 'ask',
      cmd: 'claude mcp add taiwanmd -- npx -y taiwanmd mcp serve',
      note: '接上你的 AI，回答帶得出處（免金鑰，查詢不離開你的機器）',
    },
    {
      n: '3',
      label: '一起寫',
      en: 'write',
      cmd: 'npx taiwanmd contribute "你想寫的主題"',
      note: '產生草稿骨架，改完開 PR',
    },
    {
      n: '4',
      label: '當節點',
      en: 'run a node',
      cmd: `claude plugin marketplace add ${UPSTREAM}`,
      note: '你的機器每天醒來一次，接一件工單，成果用 PR 回來',
    },
  ];

  const out = [];
  out.push('');
  out.push(`  🧬 ${chalk.bold('COMPUTEX.md')} — ${scale}`);
  out.push(freshnessLine());
  out.push('');
  for (const r of rungs) {
    out.push(
      `  ${chalk.bold(r.n)}  ${chalk.bold(r.label)}  ${chalk.gray(`(${r.en})`)}`,
    );
    out.push(`     ${chalk.cyan(r.cmd)}`);
    out.push(`     ${chalk.gray(r.note)}`);
    out.push('');
  }
  out.push(chalk.gray('  taiwanmd --help  看全部指令'));
  out.push(
    chalk.gray('  知識 CC BY-SA 4.0 · 程式 MIT · 沒有金鑰、沒有帳號、沒有帳單'),
  );
  out.push('');
  console.log(out.join('\n'));
}
