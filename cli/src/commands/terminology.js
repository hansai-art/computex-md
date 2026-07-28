/**
 * taiwanmd terminology — 用語查詢與轉換
 *
 * Subcommands:
 *   search <query>   Search terminology database
 *   convert <text>   Convert CN→TW terminology in text
 *   stats            Show terminology statistics
 */

import chalk from 'chalk';
import { readFileSync, readdirSync, existsSync } from 'fs';
import { join, resolve } from 'path';
import { fileURLToPath } from 'url';
import { parse as parseYaml } from 'yaml';

const __filename = fileURLToPath(import.meta.url);
const __dirname = resolve(fileURLToPath(import.meta.url), '..');
const CLI_ROOT = resolve(__dirname, '../..');
const REPO_ROOT = resolve(CLI_ROOT, '..');
const TERM_DIR = join(REPO_ROOT, 'data', 'terminology');

/**
 * Load all terminology YAML files.
 */
function loadTerminology() {
  if (!existsSync(TERM_DIR)) {
    return [];
  }
  const files = readdirSync(TERM_DIR).filter(
    (f) => f.endsWith('.yaml') || f.endsWith('.yml'),
  );
  const terms = [];
  for (const file of files) {
    try {
      const raw = readFileSync(join(TERM_DIR, file), 'utf-8');
      const data = parseYaml(raw);
      if (data && (data.taiwan || data.display?.taiwan)) {
        terms.push({
          ...data,
          _file: file,
          _taiwan: data.display?.taiwan || data.taiwan,
          _china: data.display?.china || data.china,
        });
      }
    } catch {
      // skip malformed files
    }
  }
  return terms;
}

const TYPE_LABELS = {
  A: '完全不同詞',
  B: '同義不同字',
  C: '外來語音譯差異',
  D: '語感/頻率差異',
  E: '新創/流行語',
  F: '同詞不同義',
};

const CAT_EMOJI = {
  tech: '💻',
  daily: '🏠',
  food: '🍜',
  medical: '🏥',
  education: '🎓',
  business: '💼',
  transport: '🚗',
  culture: '🎭',
  media: '📺',
  legal: '⚖️',
};

function typeLabel(type) {
  return TYPE_LABELS[type] || type || '?';
}

function catEmoji(cat) {
  return CAT_EMOJI[cat] || '📝';
}

/**
 * Search terminology by keyword.
 */
function doSearch(query, terms, opts) {
  const q = query.toLowerCase();
  const matches = terms.filter((t) => {
    const fields = [
      t._taiwan,
      t._china,
      t.id,
      t.origin,
      t.taiwan_path,
      t.china_path,
      t.notes,
      t.etymology?.origin,
      t.etymology?.taiwan_path,
      t.etymology?.china_path,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
    return fields.includes(q);
  });

  if (matches.length === 0) {
    console.log(chalk.yellow(`\n  🔍 「${query}」— 找到 0 筆用語\n`));
    return;
  }

  const limit = parseInt(opts.limit, 10) || 20;
  const shown = matches.slice(0, limit);

  if (opts.json) {
    console.log(JSON.stringify(shown, null, 2));
    return;
  }

  console.log(
    chalk.bold(
      `\n  📖 用語搜尋「${chalk.cyan(query)}」— 找到 ${chalk.green(matches.length)} 筆\n`,
    ),
  );

  for (const t of shown) {
    const type = t.type || t.fork_type || '?';
    const cat = t.category || '?';
    console.log(
      `  ${catEmoji(cat)} ${chalk.bold.green(t._taiwan)} ← ${chalk.red(t._china || '?')}  ${chalk.gray(`[${type}: ${typeLabel(type)}]`)}`,
    );
    const note = t.origin || t.etymology?.origin || t.fork_cause || '';
    if (note) {
      console.log(`     ${chalk.gray(note.slice(0, 120))}`);
    }
    console.log();
  }

  if (matches.length > limit) {
    console.log(
      chalk.gray(
        `  ... 還有 ${matches.length - limit} 筆，用 --limit 顯示更多\n`,
      ),
    );
  }
}

/**
 * Convert CN text → TW terminology.
 */
function doConvert(text, terms, opts) {
  // Build replacement map: china → taiwan (longer matches first)
  const replacements = [];
  for (const t of terms) {
    const china = t._china;
    const taiwan = t._taiwan;
    if (!china || !taiwan || china === taiwan) continue;

    // Handle "X / Y" format — split into multiple entries
    const variants = china
      .split(/[\/／]/)
      .map((s) => s.trim())
      .filter(Boolean);
    for (const v of variants) {
      // Skip if variant contains parentheses (messy data)
      if (/[（()）]/.test(v)) continue;
      replacements.push({ from: v, to: taiwan });
    }
  }

  // Sort by length descending (longer matches first)
  replacements.sort((a, b) => b.from.length - a.from.length);

  let result = text;
  const applied = [];

  for (const r of replacements) {
    if (result.includes(r.from)) {
      const count = result.split(r.from).length - 1;
      result = result.replaceAll(r.from, chalk.green(r.to));
      applied.push({ from: r.from, to: r.to, count });
    }
  }

  // Note: For full CN→TW conversion including simplified→traditional characters,
  // use the web converter at computex.md/terminology/converter which includes OpenCC.
  // CLI currently matches terminology in the input as-is (traditional Chinese).

  if (opts.json) {
    console.log(
      JSON.stringify(
        { input: text, output: result, replacements: applied },
        null,
        2,
      ),
    );
    return;
  }

  console.log(chalk.bold('\n  📝 轉換結果:\n'));
  console.log(`  ${result}\n`);

  if (applied.length > 0) {
    console.log(chalk.bold(`  🔄 替換 ${chalk.green(applied.length)} 處:\n`));
    for (const a of applied) {
      console.log(
        `    ${chalk.red(a.from)} → ${chalk.green(a.to)}${a.count > 1 ? chalk.gray(` ×${a.count}`) : ''}`,
      );
    }
    console.log();
  } else {
    console.log(chalk.gray('  沒有找到可替換的用語。\n'));
  }
}

/**
 * Show terminology stats.
 */
function doStats(terms, opts) {
  const byType = {};
  const byCat = {};
  for (const t of terms) {
    const type = t.type || t.fork_type || '?';
    const cat = t.category || '?';
    byType[type] = (byType[type] || 0) + 1;
    byCat[cat] = (byCat[cat] || 0) + 1;
  }

  if (opts.json) {
    console.log(
      JSON.stringify(
        { total: terms.length, byType, byCategory: byCat },
        null,
        2,
      ),
    );
    return;
  }

  console.log(
    chalk.bold(`\n  📊 用語詞庫統計 — ${chalk.green(terms.length)} 筆\n`),
  );

  console.log(chalk.bold('  分歧類型:'));
  for (const [type, count] of Object.entries(byType).sort(
    (a, b) => b[1] - a[1],
  )) {
    const bar = chalk.green('█'.repeat(Math.ceil(count / 30)));
    console.log(`    ${type} ${typeLabel(type).padEnd(12)} ${bar} ${count}`);
  }

  console.log(chalk.bold('\n  分類:'));
  for (const [cat, count] of Object.entries(byCat).sort(
    (a, b) => b[1] - a[1],
  )) {
    const bar = chalk.green('█'.repeat(Math.ceil(count / 30)));
    console.log(`    ${catEmoji(cat)} ${cat.padEnd(12)} ${bar} ${count}`);
  }
  console.log();
}

export function terminologyCommand(program) {
  const cmd = program
    .command('terminology')
    .alias('term')
    .description(
      '用語查詢與轉換 — Search, convert, and explore TW/CN terminology',
    );

  cmd
    .command('search <query>')
    .description('Search terminology by keyword')
    .option('-l, --limit <n>', 'Max results', '20')
    .option('--json', 'Output as JSON')
    .action((query, opts) => {
      const terms = loadTerminology();
      doSearch(query, terms, opts);
    });

  cmd
    .command('convert <text>')
    .description('Convert CN→TW terminology in text')
    .option('--json', 'Output as JSON')
    .action((text, opts) => {
      const terms = loadTerminology();
      doConvert(text, terms, opts);
    });

  cmd
    .command('stats')
    .description('Show terminology database statistics')
    .option('--json', 'Output as JSON')
    .action((opts) => {
      const terms = loadTerminology();
      doStats(terms, opts);
    });
}
