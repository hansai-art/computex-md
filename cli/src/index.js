#!/usr/bin/env node
import { Command } from 'commander';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { searchCommand } from './commands/search.js';
import { readCommand } from './commands/read.js';
import { listCommand } from './commands/list.js';
import { randomCommand } from './commands/random.js';
import { syncCommand } from './commands/sync.js';
import { statsCommand } from './commands/stats.js';
import { todayCommand } from './commands/today.js';
import { quizCommand } from './commands/quiz.js';
import { exploreCommand } from './commands/explore.js';
import { diffCommand } from './commands/diff.js';
import { graphCommand } from './commands/graph.js';
import { ragCommand } from './commands/rag.js';
import { contributeCommand } from './commands/contribute.js';
import { validateCommand } from './commands/validate.js';
import { terminologyCommand } from './commands/terminology.js';
// v0.6 — canonical sync (MANIFESTO #10 + Stage 3.5 + ARTICLE-INBOX + SPORE-LOG)
import { auditCommand } from './commands/audit.js';
import { inboxCommand } from './commands/inbox.js';
import { sporeCommand } from './commands/spore.js';
// v0.8 — organism introspection
import { organsCommand } from './commands/organs.js';
import { supportersCommand } from './commands/supporters.js';
import { senseCommand } from './commands/sense.js';
import { citeCommand } from './commands/cite.js';
// v0.7 preview
import { mcpCommand } from './commands/mcp.js';
// v0.7 — identity sync release (exposes v1.5.0 site infrastructure to CLI)
import { profileCommand } from './commands/profile.js';
import { mailmapCommand } from './commands/mailmap.js';
// v0.8 — the front door: one line you can hand to someone else
import { printWelcome } from './commands/welcome.js';

const program = new Command();

/** Version from package.json, so it can't drift the way the literal '0.7.0'
 *  did while package.json said 0.7.1. */
function cliVersion() {
  try {
    const pkg = path.resolve(
      path.dirname(fileURLToPath(import.meta.url)),
      '../package.json',
    );
    return JSON.parse(fs.readFileSync(pkg, 'utf8')).version || '0.0.0';
  } catch {
    return '0.0.0';
  }
}

program
  .name('taiwanmd')
  .description(
    'COMPUTEX.md — 台灣知識庫 CLI\nSearch, read, and explore 900+ curated articles about Taiwan.',
  )
  .version(cliVersion());

// v0.5 — existing commands
searchCommand(program);
readCommand(program);
listCommand(program);
randomCommand(program);
syncCommand(program);
statsCommand(program);
todayCommand(program);
quizCommand(program);
exploreCommand(program);
diffCommand(program);
graphCommand(program);
ragCommand(program);
contributeCommand(program);
validateCommand(program);
terminologyCommand(program);

// v0.6 — canonical sync release
auditCommand(program);
inboxCommand(program);
sporeCommand(program);

// v0.8 — organism introspection (shipped early with v0.6 since data is ready)
organsCommand(program);
supportersCommand(program);
senseCommand(program);
citeCommand(program);

// v0.7 — MCP server preview
mcpCommand(program);

// v0.7 — identity sync release
profileCommand(program);
mailmapCommand(program);

// Bare `npx taiwanmd` shows the ladder rather than a wall of flags — that
// screen is the unit you can pass to another person.
if (process.argv.length <= 2) {
  printWelcome();
} else {
  program.parse();
}
