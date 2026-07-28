/**
 * COMPUTEX.md Sense Command — GA4 / Search Console / Cloudflare sense data
 *
 * Reads public/api/dashboard-analytics.json. The name "sense" reflects
 * Semiont 的 §感知器官 (perception organs) in ANATOMY.md.
 *
 * Usage:
 *   taiwanmd sense                   # today's snapshot
 *   taiwanmd sense --range 7d        # 7-day window
 *   taiwanmd sense --source ga       # filter to GA / sc / cf
 *   taiwanmd sense --json
 */

import fs from 'fs';
import path from 'path';
import chalk from 'chalk';
import { getApiPath } from '../lib/knowledge.js';
import { ensureData } from '../lib/ensure-data.js';

export function senseCommand(program) {
  program
    .command('sense')
    .description(
      'Show sense data: GA4 pageviews / Search Console queries / Cloudflare traffic',
    )
    .option('--range <range>', 'Window: 24h | 7d', '7d')
    .option('--source <source>', 'Filter: ga | sc | cf | all', 'all')
    .option('--limit <n>', 'Top N items per section', '8')
    .option('--json', 'Output as JSON')
    .action(async (opts) => {
      try {
        await ensureData({ quiet: true });
        const jsonPath = path.join(getApiPath(), 'dashboard-analytics.json');
        if (!fs.existsSync(jsonPath)) {
          console.error(
            chalk.red(`\n❌ dashboard-analytics.json not found: ${jsonPath}`),
          );
          process.exit(1);
        }
        const raw = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));

        if (opts.json) {
          console.log(JSON.stringify(raw, null, 2));
          return;
        }

        const limit = parseInt(opts.limit, 10) || 8;
        const source = opts.source;
        const ga = raw.ga || {};
        const sc =
          opts.range === '24h'
            ? raw.searchConsole24h || {}
            : raw.searchConsole7d || {};
        const cf =
          opts.range === '24h'
            ? raw.cloudflare24h || {}
            : raw.cloudflare7d || {};

        console.log('');
        console.log(
          chalk.bold(
            `👁️  Sense — updated ${raw.lastUpdated?.split('T')[0] || 'unknown'} · window ${opts.range}`,
          ),
        );
        console.log(
          chalk.gray(`  sources used: ${(raw.sourcesUsed || []).join(', ')}`),
        );

        if (source === 'all' || source === 'ga') {
          console.log('');
          console.log(chalk.bold.magenta('📊 GA4'));
          const gaTotals = ga.totals || {};
          console.log(
            `  window: ${ga.startDate} → ${ga.endDate} (${ga.days}d)`,
          );
          console.log(
            `  users: ${chalk.white((gaTotals.activeUsers || 0).toLocaleString())}  pageviews: ${chalk.white((gaTotals.pageViews || 0).toLocaleString())}  engagement: ${chalk.white(gaTotals.engagementTimeAvgSec || '?')}s`,
          );
          const pages = (
            ga.topArticles7d ||
            ga.topPages ||
            raw.topPages ||
            []
          ).slice(0, limit);
          if (pages.length > 0) {
            console.log(chalk.bold('  Top articles:'));
            for (const p of pages) {
              const title = (p.title || p.path || '?')
                .split(' | ')[0]
                .slice(0, 48);
              console.log(
                `    ${chalk.white(title.padEnd(50))} ${chalk.cyan(String(p.views || 0).padStart(6))}`,
              );
            }
          }
        }

        if (source === 'all' || source === 'sc') {
          console.log('');
          console.log(chalk.bold.blue('🔍 Search Console'));
          const scTotals = sc.totals || {};
          console.log(
            `  window: ${sc.startDate} → ${sc.endDate} (${sc.days}d)`,
          );
          console.log(
            `  clicks: ${chalk.white(scTotals.clicks || 0)}  imp: ${chalk.white((scTotals.impressions || 0).toLocaleString())}  CTR: ${chalk.white(scTotals.ctr || 0)}%  pos: ${chalk.white(scTotals.position || '?')}`,
          );
          if (scTotals.query_dim_coverage_pct !== undefined) {
            console.log(
              chalk.gray(
                `  (query-dim coverage: ${scTotals.query_dim_coverage_pct}% — rest is anonymized queries)`,
              ),
            );
          }
          const queries = (sc.topQueries || []).slice(0, limit);
          if (queries.length > 0) {
            console.log(chalk.bold('  Top queries:'));
            for (const q of queries) {
              const query = (q.query || '?').slice(0, 30);
              console.log(
                `    ${chalk.white(query.padEnd(32))} clicks ${chalk.cyan(String(q.clicks || 0).padStart(4))}  imp ${chalk.gray(String(q.impressions || 0).padStart(6))}`,
              );
            }
          }
        }

        if (source === 'all' || source === 'cf') {
          console.log('');
          console.log(chalk.bold.yellow('☁️  Cloudflare'));
          const cfTotals = cf.totals || {};
          console.log(
            `  requests: ${chalk.white((cfTotals.requests || 0).toLocaleString())}  uniques: ${chalk.white((cfTotals.uniqueVisitors || 0).toLocaleString())}`,
          );
          if (cfTotals.notFoundRatePct !== undefined)
            console.log(
              `  404 rate: ${chalk.white(cfTotals.notFoundRatePct + '%')}`,
            );
          const countries = (raw.countries || cf.countries || []).slice(
            0,
            limit,
          );
          if (countries.length > 0) {
            console.log(chalk.bold('  Top countries:'));
            for (const c of countries) {
              const name = (c.country || c.name || '?').slice(0, 25);
              console.log(
                `    ${chalk.white(name.padEnd(26))} ${chalk.cyan(String(c.requests || c.users || 0).padStart(7))}`,
              );
            }
          }
          if (cf.aiCrawlers) {
            console.log(
              chalk.gray(
                `  AI crawlers: ${cf.aiCrawlers.total || 0} requests across ${Object.keys(cf.aiCrawlers.byBot || {}).length} bots`,
              ),
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
