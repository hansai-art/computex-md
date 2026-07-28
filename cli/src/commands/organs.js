/**
 * COMPUTEX.md Organs Command — Semiont vital signs
 *
 * Reads public/api/dashboard-organism.json and surfaces the 8 organ
 * health scores that currently live inside `stats`.
 *
 * Usage:
 *   taiwanmd organs              # colored bar chart
 *   taiwanmd organs --json
 *   taiwanmd organs --lang en    # English labels
 */

import fs from 'fs';
import path from 'path';
import chalk from 'chalk';
import { getApiPath } from '../lib/knowledge.js';
import { ensureData } from '../lib/ensure-data.js';

function bar(score, max = 100, width = 10) {
  const filled = Math.round((score / max) * width);
  const empty = width - filled;
  return '█'.repeat(filled) + '░'.repeat(empty);
}

function colorByScore(score) {
  if (score >= 80) return chalk.green;
  if (score >= 60) return chalk.yellow;
  if (score >= 40) return chalk.hex('#FFA500'); // orange
  return chalk.red;
}

function trendIcon(trend) {
  if (trend === 'up') return chalk.green('↑');
  if (trend === 'down') return chalk.red('↓');
  if (trend === 'flat' || trend === 'stable') return chalk.gray('→');
  return chalk.gray('?');
}

export function organsCommand(program) {
  program
    .command('organs')
    .description('Show Semiont vital signs (8 organ health scores)')
    .option('--json', 'Output as JSON')
    .option('--lang <lang>', 'Label language: zh | en', 'zh')
    .action(async (opts) => {
      try {
        await ensureData({ quiet: true });
        const jsonPath = path.join(getApiPath(), 'dashboard-organism.json');
        if (!fs.existsSync(jsonPath)) {
          console.error(
            chalk.red(`\n❌ dashboard-organism.json not found: ${jsonPath}`),
          );
          console.error(chalk.gray('   Run: taiwanmd sync --force\n'));
          process.exit(1);
        }

        const raw = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
        const organs = raw.organs || [];

        if (opts.json) {
          console.log(JSON.stringify(raw, null, 2));
          return;
        }

        const overall =
          organs.length > 0
            ? Math.round(
                organs.reduce((s, o) => s + (o.score || 0), 0) / organs.length,
              )
            : 0;

        console.log('');
        console.log(
          chalk.bold(
            `🧬 Organism vitals — ${raw.lastUpdated?.split('T')[0] || 'unknown'}`,
          ),
        );
        console.log('');

        for (const o of organs) {
          const label =
            opts.lang === 'en'
              ? `${o.emoji} ${o.name.padEnd(14)}`
              : `${o.emoji} ${(o.nameZh || o.name).padEnd(6)}`;
          const barStr = colorByScore(o.score)(bar(o.score));
          const scoreStr = String(o.score).padStart(3);
          const trend = trendIcon(o.trend);
          const meta = o.metaphor ? chalk.gray(` · ${o.metaphor}`) : '';
          console.log(`  ${label} ${barStr} ${scoreStr} ${trend}${meta}`);
        }

        console.log('');
        console.log(
          chalk.bold(
            `Overall: ${colorByScore(overall)(overall + '/100')} · ${organs.length} organs tracked`,
          ),
        );
        console.log('');
      } catch (err) {
        console.error(chalk.red(`\n❌ Failed: ${err.message}\n`));
        process.exit(1);
      }
    });
}
