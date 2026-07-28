/**
 * COMPUTEX.md Cite Command — Anti-hallucination claim lookup
 *
 * Returns verified claims + source URLs instead of generated sentences.
 * Complements `rag` (which returns full article body) with surgical per-claim
 * attribution — the anti-hallucination primitive that MANIFESTO §10 demands.
 *
 * Strategy:
 *   1. Search articles for topic
 *   2. Extract sentences that have [^N] footnote markers (citation-backed)
 *   3. Resolve footnote definition to (source name, URL)
 *   4. Return structured claim list
 *
 * Usage:
 *   taiwanmd cite "珍珠奶茶發明年份"
 *   taiwanmd cite "台積電 3nm" --limit 5
 *   taiwanmd cite "原住民族" --json
 */

import path from 'path';
import chalk from 'chalk';
import { getArticleFiles, readArticle } from '../lib/knowledge.js';
import { searchArticles } from '../lib/search.js';
import { ensureData } from '../lib/ensure-data.js';

/**
 * Extract citation-backed claims from an article body.
 * A claim = a sentence that contains a [^N] footnote reference.
 */
function extractCitedClaims(body, maxClaims = 50) {
  const claims = [];
  // Split into sentences using Chinese + Latin delimiters
  const sentences = body.split(/(?<=[。！？!?])\s*/);
  for (const sentence of sentences) {
    const clean = sentence.trim();
    if (clean.length < 20 || clean.length > 300) continue;
    const footnoteMatches = [...clean.matchAll(/\[\^([\w-]+)\]/g)];
    if (footnoteMatches.length === 0) continue;
    claims.push({
      text: clean.replace(/\[\^[\w-]+\]/g, '').trim(),
      footnotes: footnoteMatches.map((m) => m[1]),
    });
    if (claims.length >= maxClaims) break;
  }
  return claims;
}

/**
 * Extract footnote definitions from article body.
 * Returns map of footnoteId -> { name, url, desc }
 */
function extractFootnoteDefs(body) {
  const defs = {};
  // Match lines like: [^1]: [Name](URL) — description
  const regex =
    /^\[\^([\w-]+)\]:\s*(?:\[([^\]]+)\]\(([^)]+)\))?\s*(?:—\s*(.+))?/gm;
  let m;
  while ((m = regex.exec(body)) !== null) {
    const id = m[1];
    defs[id] = {
      name: m[2] || null,
      url: m[3] || null,
      desc: (m[4] || '').trim(),
    };
  }
  return defs;
}

/**
 * Score relevance of a claim to a query using token overlap.
 */
function scoreClaim(claim, query) {
  const queryTokens = query
    .toLowerCase()
    .split(/\s+/)
    .filter((t) => t.length > 0);
  const claimLower = claim.text.toLowerCase();
  let score = 0;
  for (const token of queryTokens) {
    if (claimLower.includes(token)) score += token.length;
  }
  return score;
}

export function citeCommand(program) {
  program
    .command('cite <query>')
    .description(
      'Look up verified claims + source URLs (anti-hallucination primitive)',
    )
    .option('-l, --limit <n>', 'Max claims to return', '3')
    .option('--json', 'Output as JSON')
    .action(async (query, opts) => {
      try {
        await ensureData({ quiet: true });
        const files = getArticleFiles();
        const limit = parseInt(opts.limit, 10) || 3;

        // Stage 1: search returns top articles
        const hits = await searchArticles(query, { limit: 10 });
        if (!hits || hits.length === 0) {
          const msg = `找不到相關文章: "${query}"`;
          if (opts.json)
            console.log(
              JSON.stringify({ error: msg, query, claims: [] }, null, 2),
            );
          else console.log(chalk.yellow(`\n⚠ ${msg}\n`));
          return;
        }

        // Stage 2-3: for each top hit, extract cited claims + resolve footnotes
        const allClaims = [];
        for (const hit of hits.slice(0, 5)) {
          const filePath = files.find(
            (f) => path.basename(f, '.md') === hit.slug || f.includes(hit.slug),
          );
          if (!filePath) continue;
          const { frontmatter, body } = readArticle(filePath);
          const defs = extractFootnoteDefs(body);
          const claims = extractCitedClaims(body);
          for (const c of claims) {
            const sources = c.footnotes
              .map((id) => defs[id])
              .filter((d) => d && d.url);
            if (sources.length === 0) continue;
            allClaims.push({
              claim: c.text,
              article: frontmatter.title,
              slug: path.basename(filePath, '.md'),
              sources,
              score: scoreClaim(c, query),
            });
          }
        }

        // Rank by score descending
        allClaims.sort((a, b) => b.score - a.score);
        const top = allClaims.slice(0, limit);

        if (opts.json) {
          console.log(JSON.stringify({ query, claims: top }, null, 2));
          return;
        }

        console.log('');
        console.log(chalk.bold(`📎 Cite — "${query}"`));
        console.log(
          chalk.gray(
            `  ${top.length} verified claim${top.length === 1 ? '' : 's'}`,
          ),
        );
        console.log('');
        if (top.length === 0) {
          console.log(
            chalk.yellow('  ⚠ No citation-backed claims found for this query.'),
          );
          console.log(
            chalk.gray(
              '  (CLI only returns claims that have [^N] footnote attached.)',
            ),
          );
          console.log('');
          return;
        }
        top.forEach((c, i) => {
          console.log(chalk.bold.cyan(`${i + 1}. ${c.claim}`));
          console.log(chalk.gray(`   From: ${c.article} (${c.slug})`));
          for (const src of c.sources) {
            console.log(
              chalk.gray(
                `   ▸ ${src.name || 'source'}: ${chalk.underline(src.url)}`,
              ),
            );
            if (src.desc)
              console.log(chalk.gray(`     ${src.desc.slice(0, 120)}`));
          }
          console.log('');
        });
      } catch (err) {
        console.error(chalk.red(`\n❌ Cite failed: ${err.message}\n`));
        process.exit(1);
      }
    });
}
