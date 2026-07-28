/**
 * COMPUTEX.md Inbox Command — ARTICLE-INBOX reader
 *
 * Read/manage ARTICLE-INBOX.md (pending / in-progress / blocked articles).
 * Companion to ARTICLE-DONE-LOG.md for completed items.
 *
 * Usage:
 *   taiwanmd inbox                # show all states grouped
 *   taiwanmd inbox --state pending
 *   taiwanmd inbox claim <slug>   # lock as in-progress
 *   taiwanmd inbox release <slug> # release lock
 *   taiwanmd inbox done <slug>    # move to ARTICLE-DONE-LOG
 */

import fs from 'fs';
import path from 'path';
import chalk from 'chalk';
import { getKnowledgePath } from '../lib/knowledge.js';

function getInboxPath() {
  // ARTICLE-INBOX lives in docs/semiont/ not knowledge/
  const kPath = getKnowledgePath();
  const repoRoot = path.resolve(kPath, '..');
  return path.join(repoRoot, 'docs', 'semiont', 'ARTICLE-INBOX.md');
}

function getDoneLogPath() {
  const kPath = getKnowledgePath();
  const repoRoot = path.resolve(kPath, '..');
  return path.join(repoRoot, 'docs', 'semiont', 'ARTICLE-DONE-LOG.md');
}

/**
 * Parse ARTICLE-INBOX.md entries. Each entry is a H3 heading followed by
 * bullet metadata (Type / Category / Priority / Status / Requested / Notes).
 */
function parseInbox(content) {
  const entries = [];
  const blocks = content.split(/^### /m).slice(1); // skip preamble

  for (const block of blocks) {
    const lines = block.split('\n');
    const title = lines[0].trim();
    if (!title || title.startsWith('📌')) continue;
    // Skip the schema template block (literal "{主題名}")
    if (title.includes('{') && title.includes('}')) continue;

    const entry = {
      title,
      type: null,
      category: null,
      priority: null,
      status: null,
      requested: null,
      path: null,
      notes: [],
    };

    for (const line of lines.slice(1)) {
      const metaMatch = line.match(/^-\s*\*\*([^*]+)\*\*\s*[：:]\s*(.+)/);
      if (metaMatch) {
        const key = metaMatch[1].trim().toLowerCase();
        const value = metaMatch[2].trim();
        if (key === 'type') entry.type = value;
        else if (key === 'category') entry.category = value;
        else if (key === 'priority') entry.priority = value;
        else if (key === 'status') entry.status = value;
        else if (key === 'requested') entry.requested = value;
        else if (key === 'path') entry.path = value;
      }
    }
    entries.push(entry);
  }
  return entries;
}

function normalizeStatus(status) {
  if (!status) return 'unknown';
  const s = status.toLowerCase().replace(/[`\s]/g, '');
  if (s.includes('blocked')) return 'blocked';
  if (s.includes('in-progress') || s.includes('progress')) return 'in-progress';
  if (s.includes('pending')) return 'pending';
  if (s.includes('done')) return 'done';
  return 'unknown';
}

function normalizePriority(priority) {
  if (!priority) return 'P?';
  const m = priority.match(/P\d/i);
  return m ? m[0].toUpperCase() : priority;
}

function priorityColor(p) {
  if (p === 'P0') return chalk.red;
  if (p === 'P1') return chalk.yellow;
  if (p === 'P2') return chalk.cyan;
  return chalk.gray;
}

function printGroup(label, entries, color) {
  if (entries.length === 0) return;
  console.log('');
  console.log(color(chalk.bold(`${label} (${entries.length})`)));
  for (const e of entries) {
    const pri = normalizePriority(e.priority);
    const priColored = priorityColor(pri)(pri.padEnd(3));
    const cat = e.category ? chalk.gray(`[${e.category.split(' ')[0]}]`) : '';
    const requested = e.requested
      ? chalk.gray(
          e.requested.split(' ').slice(0, 2).join(' ').replace('by', '·'),
        )
      : '';
    console.log(`  ${priColored} ${chalk.white(e.title)} ${cat} ${requested}`);
  }
}

export function inboxCommand(program) {
  const inbox = program
    .command('inbox')
    .description(
      'Read/manage ARTICLE-INBOX (pending / in-progress / blocked articles)',
    )
    .option(
      '--state <state>',
      'Filter by state: pending / in-progress / blocked / all',
      'all',
    )
    .option('--json', 'Output as JSON')
    .action((opts) => {
      try {
        const inboxPath = getInboxPath();
        if (!fs.existsSync(inboxPath)) {
          console.error(
            chalk.red(`\n❌ ARTICLE-INBOX not found: ${inboxPath}`),
          );
          console.error(
            chalk.gray(
              '   Run CLI from within the taiwan-md repo for inbox access.\n',
            ),
          );
          process.exit(1);
        }

        const content = fs.readFileSync(inboxPath, 'utf8');
        const entries = parseInbox(content);
        const grouped = {
          pending: [],
          'in-progress': [],
          blocked: [],
          unknown: [],
        };
        for (const e of entries) {
          const s = normalizeStatus(e.status);
          (grouped[s] || grouped.unknown).push(e);
        }

        if (opts.json) {
          const filtered =
            opts.state === 'all'
              ? entries
              : entries.filter((e) => normalizeStatus(e.status) === opts.state);
          console.log(
            JSON.stringify(
              { total: filtered.length, entries: filtered },
              null,
              2,
            ),
          );
          return;
        }

        console.log('');
        console.log(
          chalk.bold(
            `📥 ARTICLE-INBOX (${entries.length} entries) — ${path.basename(inboxPath)}`,
          ),
        );

        if (opts.state === 'all' || opts.state === 'pending')
          printGroup('PENDING', grouped.pending, chalk.yellow);
        if (opts.state === 'all' || opts.state === 'in-progress')
          printGroup('IN-PROGRESS', grouped['in-progress'], chalk.cyan);
        if (opts.state === 'all' || opts.state === 'blocked')
          printGroup('BLOCKED', grouped.blocked, chalk.red);
        if (opts.state === 'all' && grouped.unknown.length > 0)
          printGroup('UNKNOWN-STATE', grouped.unknown, chalk.gray);

        console.log('');
        console.log(
          chalk.gray(
            `  Use: taiwanmd inbox claim <title> | release <title> | done <title>`,
          ),
        );
        console.log('');
      } catch (err) {
        console.error(chalk.red(`\n❌ Failed: ${err.message}\n`));
        process.exit(1);
      }
    });

  // ─── Write-ops shared helpers ───────────────────────────────────────────
  function todayIso() {
    return new Date().toISOString().split('T')[0];
  }

  function getSessionLetter() {
    // Read from env TAIWANMD_SESSION, else fall back to alphabetic timestamp
    if (process.env.TAIWANMD_SESSION) return process.env.TAIWANMD_SESSION;
    const h = new Date().getHours();
    return String.fromCharCode(945 + (h % 26)); // Greek α..ω
  }

  function findEntryBlock(content, slug) {
    // Entry starts with `### <title>` and ends at next `### ` or EOF.
    // Match `slug` as substring of the title (case-insensitive Chinese included).
    const blockRegex = /^### .+$[\s\S]*?(?=^### |\Z)/gm;
    let m;
    while ((m = blockRegex.exec(content)) !== null) {
      const block = m[0];
      const title = block.split('\n')[0].replace(/^### /, '').trim();
      if (
        title.includes(slug) ||
        title.toLowerCase().includes(slug.toLowerCase())
      ) {
        return { block, start: m.index, end: m.index + block.length, title };
      }
    }
    return null;
  }

  function replaceStatus(block, newStatus) {
    return block.replace(
      /(-\s*\*\*Status\*\*\s*[:：]\s*)(`[^`]*`|[^\n]+)/,
      (_, prefix) => `${prefix}${newStatus}`,
    );
  }

  function appendDevLog(block, line) {
    // Append a bullet under **dev_log** if exists, else add one.
    const devLogRegex =
      /(-\s*\*\*dev_log\*\*\s*[:：]\s*)([^\n]*(?:\n\s{2,}-\s+[^\n]+)*)/;
    if (devLogRegex.test(block)) {
      return block.replace(devLogRegex, (_, prefix, body) => {
        const entry = `\n  - ${line}`;
        return `${prefix}${body}${entry}`;
      });
    }
    // No dev_log yet: append at end of block
    const trimmed = block.replace(/\n+$/, '');
    return `${trimmed}\n- **dev_log**:\n  - ${line}\n`;
  }

  inbox
    .command('claim <slug>')
    .description('Lock an inbox item as in-progress (updates Status + dev_log)')
    .option('--by <name>', 'Claimer name (default: $USER or taiwanmd)', null)
    .action((slug, opts) => {
      try {
        const inboxPath = getInboxPath();
        if (!fs.existsSync(inboxPath)) {
          console.error(
            chalk.red(`\n❌ ARTICLE-INBOX not found: ${inboxPath}\n`),
          );
          process.exit(1);
        }
        const content = fs.readFileSync(inboxPath, 'utf8');
        const entry = findEntryBlock(content, slug);
        if (!entry) {
          console.error(
            chalk.red(
              `\n❌ No entry matching "${slug}" found in ARTICLE-INBOX.\n`,
            ),
          );
          process.exit(1);
        }
        const by = opts.by || process.env.USER || 'taiwanmd';
        const session = getSessionLetter();
        let updated = replaceStatus(entry.block, '`in-progress`');
        updated = appendDevLog(
          updated,
          `${todayIso()} by ${by} (session ${session}): claimed via taiwanmd inbox claim`,
        );
        const newContent =
          content.slice(0, entry.start) + updated + content.slice(entry.end);
        fs.writeFileSync(inboxPath, newContent);
        console.log('');
        console.log(chalk.green(`✅ Claimed: ${entry.title}`));
        console.log(chalk.gray(`   Status → in-progress`));
        console.log(chalk.gray(`   Logged by ${by} (session ${session})`));
        console.log(chalk.gray(`   File: ${inboxPath}\n`));
      } catch (err) {
        console.error(chalk.red(`\n❌ Claim failed: ${err.message}\n`));
        process.exit(1);
      }
    });

  inbox
    .command('release <slug>')
    .description('Release an in-progress lock back to pending')
    .action((slug) => {
      try {
        const inboxPath = getInboxPath();
        const content = fs.readFileSync(inboxPath, 'utf8');
        const entry = findEntryBlock(content, slug);
        if (!entry) {
          console.error(chalk.red(`\n❌ No entry matching "${slug}" found.\n`));
          process.exit(1);
        }
        const session = getSessionLetter();
        let updated = replaceStatus(entry.block, '`pending`');
        updated = appendDevLog(
          updated,
          `${todayIso()} session ${session}: released back to pending via taiwanmd inbox release`,
        );
        const newContent =
          content.slice(0, entry.start) + updated + content.slice(entry.end);
        fs.writeFileSync(inboxPath, newContent);
        console.log('');
        console.log(chalk.green(`✅ Released: ${entry.title}`));
        console.log(chalk.gray(`   Status → pending\n`));
      } catch (err) {
        console.error(chalk.red(`\n❌ Release failed: ${err.message}\n`));
        process.exit(1);
      }
    });

  inbox
    .command('done <slug>')
    .description(
      'Mark as done + add pointer comment; full DONE-LOG entry is manual',
    )
    .option(
      '--commit <sha>',
      'Commit SHA to reference in the pointer comment',
      null,
    )
    .action((slug, opts) => {
      try {
        const inboxPath = getInboxPath();
        const content = fs.readFileSync(inboxPath, 'utf8');
        const entry = findEntryBlock(content, slug);
        if (!entry) {
          console.error(chalk.red(`\n❌ No entry matching "${slug}" found.\n`));
          process.exit(1);
        }
        const session = getSessionLetter();
        const today = todayIso();
        // Replace the entire entry block with a pointer HTML comment.
        const pointer = `<!-- ${entry.title.replace(/\s*\(.*\)$/, '')} 已完成 ${today} ${session}${opts.commit ? ` commit ${opts.commit.slice(0, 8)}` : ''} → ARTICLE-DONE-LOG.md -->\n\n`;
        const newContent =
          content.slice(0, entry.start) + pointer + content.slice(entry.end);
        fs.writeFileSync(inboxPath, newContent);
        console.log('');
        console.log(chalk.green(`✅ Marked done: ${entry.title}`));
        console.log(chalk.gray(`   Entry replaced with pointer comment`));
        console.log(
          chalk.yellow(
            `   ⚠ Add the full Done entry manually to ARTICLE-DONE-LOG.md\n   Path: ${getDoneLogPath()}\n`,
          ),
        );
      } catch (err) {
        console.error(chalk.red(`\n❌ Done failed: ${err.message}\n`));
        process.exit(1);
      }
    });
}
