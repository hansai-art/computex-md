/**
 * ensure-data.js
 *
 * Checks whether the local knowledge base is present.
 * If not, automatically runs a sync before continuing.
 * Used by all data-reading commands (search, read, list, random, stats).
 */

import fs from 'fs';
import path from 'path';
import os from 'os';
import chalk from 'chalk';
import { execFileSync } from 'child_process';
import { runSync } from '../commands/sync.js';

const STANDALONE_KNOWLEDGE_DIR = path.join(
  os.homedir(),
  '.taiwanmd',
  'knowledge',
);
const STANDALONE_CACHE_DIR = path.join(os.homedir(), '.taiwanmd', 'cache');

// CLI package root: cli/src/lib -> cli/
import { fileURLToPath } from 'url';
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const CLI_ROOT = path.resolve(__dirname, '../..');
const REPO_ROOT = path.resolve(CLI_ROOT, '..');

/**
 * Returns true if we're running inside the monorepo (so knowledge/ is local).
 */
function isInRepo() {
  const repoKnowledge = path.join(REPO_ROOT, 'knowledge');
  try {
    return (
      fs.existsSync(repoKnowledge) && fs.statSync(repoKnowledge).isDirectory()
    );
  } catch {
    return false;
  }
}

/**
 * Returns true if the standalone knowledge base has been populated.
 */
function hasLocalData() {
  if (isInRepo()) return true;

  if (!fs.existsSync(STANDALONE_KNOWLEDGE_DIR)) return false;
  try {
    const entries = fs.readdirSync(STANDALONE_KNOWLEDGE_DIR);
    // Must have at least one subdirectory (a category folder)
    return entries.some((e) => {
      try {
        return fs
          .statSync(path.join(STANDALONE_KNOWLEDGE_DIR, e))
          .isDirectory();
      } catch {
        return false;
      }
    });
  } catch {
    return false;
  }
}

let _synced = false; // avoid running sync more than once per process

// How old the standalone knowledge base may get before we say something.
// COMPUTEX.md ships roughly 20-30 articles a week, so a fortnight is already a
// visibly different Taiwan.
const STALE_WARN_DAYS = 14;
// Past this we stop asking and just refresh: at this range the answers are no
// longer about the same knowledge base.
const STALE_AUTO_SYNC_DAYS = 60;

/**
 * Age of the standalone knowledge base, in days, from the last commit it holds.
 * Returns null in-repo (git handles freshness there) or when it can't be read.
 *
 * @returns {number|null}
 */
export function getDataAgeDays() {
  if (isInRepo()) return null;
  const gitDir = path.join(STANDALONE_KNOWLEDGE_DIR, '.git');
  if (!fs.existsSync(gitDir)) return null;
  try {
    const iso = execFileSync(
      'git',
      ['-C', STANDALONE_KNOWLEDGE_DIR, 'log', '-1', '--format=%cI'],
      { encoding: 'utf-8', stdio: ['ignore', 'pipe', 'ignore'] },
    ).trim();
    if (!iso) return null;
    const ms = Date.now() - new Date(iso).getTime();
    if (!Number.isFinite(ms)) return null;
    return Math.floor(ms / 86_400_000);
  } catch {
    return null;
  }
}

/**
 * Ensure the knowledge base is available *and not silently ancient*.
 *
 * The freshness half was missing until 2026-07-26: this function only ever
 * asked "is there data", so a copy synced in April kept answering questions
 * about Taiwan with April's Taiwan, indefinitely, with nothing on screen to
 * suggest otherwise. Measured on the author's own machine: 97 days old,
 * reporting 2255 articles when the real count was 863. A knowledge base that
 * quietly serves stale answers is worse than one that admits it is empty.
 *
 * @param {object} [options]
 * @param {boolean} [options.quiet] - Suppress banners
 */
export async function ensureData(options = {}) {
  if (_synced) return;

  if (hasLocalData()) {
    const age = getDataAgeDays();
    if (age === null) return;

    if (age >= STALE_AUTO_SYNC_DAYS) {
      if (!options.quiet) {
        console.log(
          chalk.yellow(
            `\n  🕐 本機知識庫已經 ${age} 天沒更新，正在自動同步...\n`,
          ),
        );
      }
      try {
        await runSync({ silent: !!options.quiet });
        _synced = true;
      } catch {
        if (!options.quiet) {
          console.log(
            chalk.gray(
              '  自動同步沒成功，先用舊資料。手動更新：taiwanmd sync\n',
            ),
          );
        }
      }
      return;
    }

    if (age >= STALE_WARN_DAYS && !options.quiet) {
      console.log(
        chalk.yellow(
          `  🕐 本機知識庫是 ${age} 天前的版本，跑 taiwanmd sync 更新\n`,
        ),
      );
    }
    return;
  }

  if (!options.quiet) {
    console.log(
      chalk.bold('\n  🌐 COMPUTEX.md 知識庫尚未下載，正在自動同步...\n'),
    );
    console.log(chalk.gray('  (首次使用需要一點時間，之後會很快)\n'));
  }

  try {
    await runSync({ silent: false });
    _synced = true;
  } catch (err) {
    console.error(chalk.red(`\n  ❌ 自動同步失敗: ${err.message}\n`));
    console.log(chalk.gray('  請手動執行: taiwanmd sync\n'));
    // Don't exit — let the calling command handle missing data gracefully
  }
}
