#!/usr/bin/env node
/**
 * Normalize terminology YAML files:
 * Convert top-level {taiwan, china, type} → {display: {taiwan, china}, fork_type}
 * and move top-level origin/taiwan_path/china_path/fork_cause into etymology block.
 *
 * Usage: node tools/normalize-terminology.js [--dry-run]
 */

import { readFileSync, writeFileSync, readdirSync } from 'fs';
import { join } from 'path';
import { parse as parseYaml, stringify as stringifyYaml } from 'yaml';

const TERM_DIR = join(import.meta.dirname, '..', 'data', 'terminology');
const dryRun = process.argv.includes('--dry-run');

const files = readdirSync(TERM_DIR).filter(
  (f) => f.endsWith('.yaml') || f.endsWith('.yml'),
);

let converted = 0;
let skipped = 0;
let errors = 0;

for (const file of files) {
  const filePath = join(TERM_DIR, file);
  let raw;
  try {
    raw = readFileSync(filePath, 'utf-8');
  } catch {
    continue;
  }

  let d;
  try {
    d = parseYaml(raw);
  } catch {
    console.error(`  ❌ YAML parse error: ${file}`);
    errors++;
    continue;
  }

  if (!d || typeof d !== 'object') continue;

  // Skip if already in display format
  if (d.display && d.display.taiwan) {
    skipped++;
    continue;
  }

  // Only convert if has top-level taiwan or china
  if (!d.taiwan && !d.china) {
    skipped++;
    continue;
  }

  // Build new structure
  const newData = {};

  // id
  if (d.id) newData.id = d.id;

  // category + subcategory
  if (d.category) newData.category = d.category;
  if (d.subcategory) newData.subcategory = d.subcategory;

  // fork_type (convert from "type")
  newData.fork_type = d.type || d.fork_type || '';

  // display block
  newData.display = {};
  if (d.taiwan) newData.display.taiwan = d.taiwan;
  if (d.china) newData.display.china = d.china;

  // english (if any)
  if (d.english) newData.english = d.english;

  // etymology block (merge from top-level fields)
  const ety = {};
  if (d.origin) ety.origin = d.origin;
  if (d.taiwan_path) ety.taiwan_path = d.taiwan_path;
  if (d.china_path) ety.china_path = d.china_path;
  if (d.fork_cause) ety.fork_cause = d.fork_cause;
  if (Object.keys(ety).length > 0) {
    newData.etymology = ety;
  }

  // usage (if any)
  if (d.usage) newData.usage = d.usage;

  // status
  if (d.status) newData.status = d.status;

  // notes
  if (d.notes)
    newData.notes = typeof d.notes === 'string' ? d.notes.trim() : d.notes;

  // sources
  if (d.sources) newData.sources = d.sources;

  // added/updated
  const today = new Date().toISOString().split('T')[0];
  if (d.added) newData.added = d.added;
  if (d.updated) newData.updated = d.updated;
  else newData.updated = today;

  // Generate YAML
  const yamlOut = stringifyYaml(newData, { lineWidth: 120 });

  if (dryRun) {
    console.log(`\n--- ${file} (DRY RUN) ---`);
    console.log(yamlOut.slice(0, 500));
  } else {
    writeFileSync(filePath, yamlOut, 'utf-8');
  }

  converted++;
  console.log(`  ✅ ${file}: top-level → display format`);
}

console.log(
  `\n📊 結果: ${converted} converted, ${skipped} skipped, ${errors} errors (total: ${files.length})`,
);
if (dryRun) console.log('  (dry run — no files changed)');
