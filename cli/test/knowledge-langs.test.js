/**
 * Reconciliation tests for lib/knowledge.js — zh-TW article listing must never
 * include translations.
 *
 * Why this file exists: from 2026-04 to 2026-07-26 the language list here was a
 * hardcoded blacklist (`['en','es','ja','ko','resources']`). Seven languages
 * were born after it was written (fr/vi/id/pt/hi/ar/ru) and nobody came back to
 * update it, so 2900 of the 3766 files the CLI called "zh-TW" were actually
 * translations — 77%, served silently through `search`, `list`, `random`,
 * `stats` and the MCP tools. Nothing failed; it just answered wrong.
 *
 * These tests are the ground-truth reconciliation that was missing
 * (REFLEXES #84): the listing is checked against the language registry and the
 * filesystem rather than against its own logic.
 *
 * Run with: cd cli && npx vitest run
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';
import {
  getArticleFiles,
  getKnowledgePath,
  getLanguageDirs,
  isZhCategoryDir,
  REAL_CATEGORIES,
} from '../src/lib/knowledge.js';

const knowledgeDir = getKnowledgePath();
const inRepo = fs.existsSync(path.join(knowledgeDir, '..', 'src', 'config'));

describe('zh-TW article listing', () => {
  const files = getArticleFiles();

  it('returns a non-empty list', () => {
    expect(files.length).toBeGreaterThan(0);
  });

  it('contains no files from any language directory', () => {
    const langDirs = getLanguageDirs() ?? new Set();
    const leaked = files.filter((f) => {
      const rel = path.relative(knowledgeDir, f);
      return langDirs.has(rel.split(path.sep)[0]);
    });
    // Name the offenders — a bare count tells you nothing about which language
    // regressed.
    expect(leaked.slice(0, 10)).toEqual([]);
  });

  it('every top-level dir it walks is a real category', () => {
    const tops = new Set(
      files.map((f) => path.relative(knowledgeDir, f).split(path.sep)[0]),
    );
    for (const t of tops) {
      expect(REAL_CATEGORIES.has(t), `unexpected category dir: ${t}`).toBe(
        true,
      );
    }
  });
});

describe('language registry derivation', () => {
  it.runIf(inRepo)(
    'derives language dirs from the registry, not a literal',
    () => {
      const langs = getLanguageDirs();
      expect(langs).toBeInstanceOf(Set);
      // zh-TW is the SSOT at knowledge/{Category}/ and is never a lang dir.
      expect(langs.has('zh-TW')).toBe(false);
      // Every language dir that physically exists must be known to the registry.
      // This is the assertion that would have caught the 2026-04→07 drift: a new
      // language landing on disk without the registry knowing fails here.
      const onDisk = fs
        .readdirSync(knowledgeDir, { withFileTypes: true })
        .filter((e) => e.isDirectory())
        .map((e) => e.name)
        // Dot-dirs are tooling (.obsidian), not languages.
        .filter(
          (n) =>
            !n.startsWith('.') && !REAL_CATEGORIES.has(n) && n !== 'resources',
        );
      for (const dir of onDisk) {
        expect(langs.has(dir), `language dir not in registry: ${dir}`).toBe(
          true,
        );
      }
    },
  );

  it('classifies resources/ as non-article', () => {
    expect(isZhCategoryDir('resources')).toBe(false);
  });

  it('classifies dot-directories as non-article', () => {
    // knowledge/.obsidian exists and Obsidian creates .md files in it.
    expect(isZhCategoryDir('.obsidian')).toBe(false);
    expect(isZhCategoryDir('.git')).toBe(false);
  });

  it('classifies a known category as an article dir', () => {
    expect(isZhCategoryDir('History')).toBe(true);
  });

  it.runIf(inRepo)('classifies every registry language as non-article', () => {
    for (const lang of getLanguageDirs()) {
      expect(isZhCategoryDir(lang), `${lang} leaked into zh listing`).toBe(
        false,
      );
    }
  });
});
