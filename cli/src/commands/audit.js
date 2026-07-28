/**
 * COMPUTEX.md Audit Command — Stage 3.5 Hallucination Audit
 *
 * Local runner for REWRITE-PIPELINE Stage 3.5 HALLUCINATION AUDIT.
 * Detection logic lives in lib/audit.js so tests can import it directly.
 *
 * Usage:
 *   taiwanmd audit 珍珠奶茶
 *   taiwanmd audit 王新仁 --json
 *   taiwanmd audit 台積電 --strict
 *   taiwanmd audit 吳哲宇 --fix-interactive
 */

import path from 'path';
import chalk from 'chalk';
import { getArticleFiles, readArticle } from '../lib/knowledge.js';
import { ensureData } from '../lib/ensure-data.js';
import { extractClaims, computeVerdict } from '../lib/audit.js';

function findArticleBySlug(slug) {
  try {
    const files = getArticleFiles();
    const exact = files.find((f) => path.basename(f, '.md') === slug);
    if (exact) return exact;
    const partial = files.find((f) => path.basename(f, '.md').includes(slug));
    return partial || null;
  } catch {
    return null;
  }
}

function printClaimSection(title, claims) {
  if (claims.length === 0) {
    console.log(`  ${chalk.gray(title)}: ${chalk.green('0 flags')}`);
    return;
  }
  const highCount = claims.filter((c) => c.severity === 'high').length;
  const warnCount = claims.filter((c) => c.severity === 'warn').length;
  const medCount = claims.filter((c) => c.severity === 'med').length;
  const infoCount = claims.filter((c) => c.severity === 'info').length;

  const flags = [];
  if (highCount) flags.push(chalk.red(`${highCount} high`));
  if (warnCount) flags.push(chalk.yellow(`${warnCount} warn`));
  if (medCount) flags.push(chalk.yellow(`${medCount} med`));
  if (infoCount) flags.push(chalk.gray(`${infoCount} info`));

  console.log(`  ${chalk.white(title)}: ${flags.join(', ')}`);
  for (const c of claims.slice(0, 5)) {
    const sev =
      c.severity === 'high'
        ? chalk.red('⚠ HIGH')
        : c.severity === 'warn'
          ? chalk.yellow('⚠ WARN')
          : c.severity === 'med'
            ? chalk.yellow('· MED')
            : chalk.gray('· info');
    const text = c.text.length > 70 ? c.text.slice(0, 70) + '...' : c.text;
    console.log(`    ${sev} L${c.line}: ${chalk.gray(text)}`);
  }
  if (claims.length > 5) {
    console.log(`    ${chalk.gray(`... +${claims.length - 5} more`)}`);
  }
}

export function auditCommand(program) {
  program
    .command('audit <slug>')
    .description(
      'Run Stage 3.5 Hallucination Audit locally (MANIFESTO §10 enforcer)',
    )
    .option('--json', 'Output as JSON')
    .option(
      '--strict',
      'Treat warnings as failures (exit 1 on any flag)',
      false,
    )
    .option(
      '--fix-interactive',
      'Interactive mode to mark flags as verified [not yet implemented]',
    )
    .action(async (slug, opts) => {
      try {
        await ensureData({ quiet: true });
        const filePath = findArticleBySlug(slug);
        if (!filePath) {
          const msg = `找不到文章: "${slug}". 請確認 slug 正確，或先執行 taiwanmd sync。`;
          if (opts.json) {
            console.log(JSON.stringify({ error: msg }, null, 2));
          } else {
            console.error(chalk.red(`\n❌ ${msg}\n`));
          }
          process.exit(1);
        }

        const { frontmatter, body } = readArticle(filePath);
        const claims = extractClaims(body);
        const verdict = computeVerdict(claims, opts.strict);

        const totalClaims =
          claims.award.length +
          claims.nameNumber.length +
          claims.location.length +
          claims.quote.length +
          claims.cocreator.length;

        if (opts.json) {
          console.log(
            JSON.stringify(
              {
                slug,
                title: frontmatter.title,
                filePath,
                verdict: verdict.status,
                label: verdict.label,
                totalClaims,
                highFlags: verdict.highFlags,
                warnFlags: verdict.warnFlags,
                patterns: {
                  award: claims.award,
                  nameNumber: claims.nameNumber,
                  location: claims.location,
                  quote: claims.quote,
                  cocreator: claims.cocreator,
                },
              },
              null,
              2,
            ),
          );
          process.exit(verdict.exitCode);
        }

        console.log('');
        console.log(
          chalk.bold(
            `🧬 Stage 3.5 Hallucination Audit — ${frontmatter.title || slug}`,
          ),
        );
        console.log(chalk.gray(`   ${filePath}`));
        console.log('');
        console.log(chalk.bold('Phase 1: Claim Table'));
        console.log(`  ${totalClaims} potential factual claims extracted`);
        console.log(
          `  ${claims.award.length} award · ${claims.nameNumber.length} name+number · ${claims.location.length} location · ${claims.quote.length} quote · ${claims.cocreator.length} co-creator`,
        );
        console.log('');
        console.log(chalk.bold('Phase 2: 5-Pattern Flags'));
        printClaimSection('[1] Award hallucination', claims.award);
        printClaimSection('[2] Names + precise numbers', claims.nameNumber);
        printClaimSection('[3] Location displacement', claims.location);
        printClaimSection('[4] Direct quotes', claims.quote);
        printClaimSection('[5] Co-creator omission', claims.cocreator);
        console.log('');
        console.log(chalk.bold('Phase 3: Verification Checklist'));
        if (verdict.status === 'pass') {
          console.log(chalk.green('  ✅ No action required'));
        } else {
          console.log(chalk.gray('  For each flag above:'));
          console.log(chalk.gray('  - Locate the source URL that backs it'));
          console.log(chalk.gray('  - If no source: downgrade or delete'));
          console.log(chalk.gray('  - If single source: mark single_source'));
          console.log(
            chalk.gray('  - If the subject is a person: confirm with them'),
          );
        }
        console.log('');
        console.log(chalk.bold(`Verdict: ${verdict.label}`));
        console.log(
          chalk.gray(
            '  Reference: MANIFESTO §10 幻覺鐵律 + REWRITE-PIPELINE Stage 3.5',
          ),
        );
        console.log('');
        process.exit(verdict.exitCode);
      } catch (err) {
        console.error(chalk.red(`\n❌ Audit failed: ${err.message}\n`));
        process.exit(1);
      }
    });
}
