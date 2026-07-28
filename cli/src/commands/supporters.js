/**
 * COMPUTEX.md Supporters Command — Portaly 贊助資料 reader
 *
 * Reads public/api/dashboard-supporters.json (derived from Gmail 透過
 * fetch-portaly-supporters.py). PII-safe by default: no names / emails
 * exposed in output.
 *
 * Usage:
 *   taiwanmd supporters                    # totals + recent
 *   taiwanmd supporters --since 2026-04-01
 *   taiwanmd supporters --json
 */

import fs from 'fs';
import path from 'path';
import chalk from 'chalk';
import { getApiPath } from '../lib/knowledge.js';
import { ensureData } from '../lib/ensure-data.js';

function formatTwd(amount) {
  return `NT$ ${amount.toLocaleString()}`;
}

export function supportersCommand(program) {
  program
    .command('supporters')
    .description('Show Portaly supporter stats (PII-scrubbed by default)')
    .option('--since <date>', 'Filter timeline since YYYY-MM-DD')
    .option('--limit <n>', 'Max timeline entries to show', '10')
    .option('--json', 'Output as JSON')
    .action(async (opts) => {
      try {
        await ensureData({ quiet: true });
        const jsonPath = path.join(getApiPath(), 'dashboard-supporters.json');
        if (!fs.existsSync(jsonPath)) {
          console.error(
            chalk.red(`\n❌ dashboard-supporters.json not found: ${jsonPath}`),
          );
          process.exit(1);
        }

        const raw = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
        const totals = raw.totals || {};
        let timeline = raw.timeline || [];

        if (opts.since) {
          timeline = timeline.filter((t) => t.date >= opts.since);
        }

        if (opts.json) {
          console.log(
            JSON.stringify(
              { totals, timeline, by_month: raw.by_month },
              null,
              2,
            ),
          );
          return;
        }

        console.log('');
        console.log(
          chalk.bold(
            `💚 Portaly Supporters — updated ${raw.last_updated?.split('T')[0] || 'unknown'}`,
          ),
        );
        console.log('');
        console.log(
          `  Total received:   ${chalk.green(formatTwd(totals.total_received_twd || 0))}`,
        );
        console.log(
          `  Transactions:     ${chalk.white(totals.transaction_count || 0)}`,
        );
        console.log(
          `  Unique supporters: ${chalk.white(totals.supporter_count || 0)}`,
        );
        console.log(
          `  Monthly subs:     ${chalk.cyan(totals.monthly_subscriptions || 0)}`,
        );
        console.log(
          `  One-time:         ${chalk.yellow(totals.one_time || 0)}`,
        );
        if (typeof totals.anonymous_ratio === 'number') {
          console.log(
            `  Anonymous:        ${chalk.gray(`${Math.round(totals.anonymous_ratio * 100)}%`)}`,
          );
        }

        if (raw.by_month) {
          console.log('');
          console.log(chalk.bold('  By month:'));
          for (const [month, amount] of Object.entries(raw.by_month)) {
            console.log(`    ${month}  ${chalk.green(formatTwd(amount))}`);
          }
        }

        const limit = parseInt(opts.limit, 10) || 10;
        const shown = timeline.slice(-limit).reverse();
        if (shown.length > 0) {
          console.log('');
          console.log(chalk.bold(`  Recent (${shown.length}):`));
          for (const t of shown) {
            const type =
              t.type === 'monthly'
                ? chalk.cyan('月訂閱')
                : chalk.yellow('一次性');
            const anon = t.anonymous ? chalk.gray('anon') : chalk.gray('named');
            console.log(
              `    ${t.date}  ${formatTwd(t.amount).padEnd(10)}  ${type}  ${anon}`,
            );
          }
        }
        console.log('');
      } catch (err) {
        console.error(chalk.red(`\n❌ Failed: ${err.message}\n`));
        process.exit(1);
      }
    });
}
