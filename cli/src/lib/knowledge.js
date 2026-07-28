/**
 * COMPUTEX.md Knowledge Base Access
 *
 * Detects whether the CLI is running inside the repo or standalone,
 * and provides unified access to knowledge base articles and API data.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import os from 'os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// CLI package root: cli/src/lib -> cli/
const CLI_ROOT = path.resolve(__dirname, '../..');
// Repo root (one level above cli/)
const REPO_ROOT = path.resolve(CLI_ROOT, '..');

const STANDALONE_DATA_DIR = path.join(os.homedir(), '.taiwanmd');
const STANDALONE_KNOWLEDGE_DIR = path.join(STANDALONE_DATA_DIR, 'knowledge');
const STANDALONE_CACHE_DIR = path.join(STANDALONE_DATA_DIR, 'cache');

// Non-article top-level dirs that are never zh-TW content, whatever the language
// registry says.
const NON_ARTICLE_DIRS = new Set(['resources']);

// The 14 real zh-TW category folders. Used as a whitelist when the language
// registry is unreachable (standalone install), and as the reconciliation target
// for the registry-derived path. A whitelist can only miss a NEW category (loud,
// caught by the first article that lands in it); a blacklist misses every NEW
// LANGUAGE silently — which is exactly what happened between 2026-04 and 07-26,
// when fr/vi/id/pt/hi/ar/ru were born and 2900 of 3766 "zh-TW" files the CLI
// reported were actually translations. Same whitelist the remote Worker uses
// (workers/mcp/src/index.js REAL_CATEGORIES) so both rulers agree — REFLEXES #83.
const REAL_CATEGORIES = new Set([
  'About',
  'Art',
  'Culture',
  'Economy',
  'Food',
  'Geography',
  'History',
  'Lifestyle',
  'Music',
  'Nature',
  'People',
  'Politics',
  'Society',
  'Technology',
]);

/**
 * Language directory names to skip, derived from the repo's language registry
 * (src/config/languages.mjs — the SSOT per ANATOMY §資源地圖) so a newly born
 * language never needs anyone to remember to update a list here.
 *
 * Falls back to null when the registry is unreachable (standalone install,
 * where ~/.taiwanmd/knowledge has no src/). Callers then use REAL_CATEGORIES.
 *
 * @returns {Set<string>|null}
 */
let _langDirsCache;
export function getLanguageDirs() {
  if (_langDirsCache !== undefined) return _langDirsCache;

  const registry = path.join(REPO_ROOT, 'src', 'config', 'languages.mjs');
  if (!fs.existsSync(registry)) {
    _langDirsCache = null;
    return _langDirsCache;
  }

  try {
    // Parsed rather than imported: this module is loaded by the MCP server on
    // stdio, where a bad dynamic import would corrupt the protocol stream.
    const src = fs.readFileSync(registry, 'utf-8');
    const codes = [...src.matchAll(/code:\s*['"]([\w-]+)['"]/g)].map(
      (m) => m[1],
    );
    if (codes.length === 0) {
      _langDirsCache = null;
      return _langDirsCache;
    }
    // zh-TW is the SSOT and lives at knowledge/{Category}/, not in a lang dir.
    _langDirsCache = new Set(codes.filter((c) => c !== 'zh-TW'));
  } catch {
    _langDirsCache = null;
  }
  return _langDirsCache;
}

/**
 * Is this top-level dir under knowledge/ a zh-TW article category?
 * @param {string} name - top-level directory name
 */
export function isZhCategoryDir(name) {
  // Dot-directories are tooling, never content: knowledge/.obsidian holds an
  // Obsidian vault config, and Obsidian will happily create .md files inside
  // it. Caught 2026-07-26 by this module's own reconciliation test, which is
  // the point of having one.
  if (name.startsWith('.')) return false;
  if (NON_ARTICLE_DIRS.has(name)) return false;

  const langDirs = getLanguageDirs();
  if (langDirs) return !langDirs.has(name);

  // No registry (standalone): fall back to the whitelist.
  return REAL_CATEGORIES.has(name);
}

export { REAL_CATEGORIES };

/**
 * Determine if we are running inside the repo (i.e. ../knowledge/ exists).
 */
function isInRepo() {
  const repoKnowledge = path.join(REPO_ROOT, 'knowledge');
  return (
    fs.existsSync(repoKnowledge) && fs.statSync(repoKnowledge).isDirectory()
  );
}

/**
 * Get the knowledge base root path.
 * In-repo: <repo>/knowledge/
 * Standalone: ~/.taiwanmd/knowledge/
 */
export function getKnowledgePath() {
  if (isInRepo()) {
    return path.join(REPO_ROOT, 'knowledge');
  }
  return STANDALONE_KNOWLEDGE_DIR;
}

/**
 * Get the API data path.
 * In-repo: <repo>/public/api/
 * Standalone: ~/.taiwanmd/cache/
 */
export function getApiPath() {
  if (isInRepo()) {
    return path.join(REPO_ROOT, 'public', 'api');
  }
  return STANDALONE_CACHE_DIR;
}

/**
 * Check if the knowledge base is available (directory exists and contains files).
 */
export function isKnowledgeAvailable() {
  const kPath = getKnowledgePath();
  if (!fs.existsSync(kPath)) return false;
  try {
    const entries = fs.readdirSync(kPath);
    return entries.length > 0;
  } catch {
    return false;
  }
}

/**
 * Recursively collect all zh-TW article markdown file paths.
 * Excludes: files starting with _, language dirs (en/es/ja), resources dir.
 */
export function getArticleFiles() {
  const knowledgeDir = getKnowledgePath();
  if (!fs.existsSync(knowledgeDir)) return [];

  const results = [];
  collectArticleFiles(knowledgeDir, knowledgeDir, results);
  return results;
}

/**
 * Collect all article markdown files for a given language.
 * For lang 'zh' (default), delegates to getArticleFiles().
 * For other langs (en, ja, es), scans knowledge/{lang}/ directory.
 *
 * @param {string} lang - Language code: 'zh', 'en', 'ja', 'es'
 * @returns {string[]} Array of absolute file paths
 */
export function getArticleFilesForLang(lang) {
  if (!lang || lang === 'zh' || lang === 'zh-TW') {
    return getArticleFiles();
  }

  const knowledgeDir = getKnowledgePath();
  const langDir = path.join(knowledgeDir, lang);

  if (!fs.existsSync(langDir)) return [];

  const results = [];
  function collect(dir) {
    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        collect(fullPath);
      } else if (
        entry.isFile() &&
        entry.name.endsWith('.md') &&
        !entry.name.startsWith('_')
      ) {
        results.push(fullPath);
      }
    }
  }

  collect(langDir);
  return results;
}

function collectArticleFiles(dir, rootDir, results) {
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      // At the top level, keep only real zh-TW category dirs (skips every
      // language dir and resources/, present and future).
      const relativeToRoot = path.relative(rootDir, fullPath);
      const topLevelDir = relativeToRoot.split(path.sep)[0];
      if (relativeToRoot === topLevelDir && !isZhCategoryDir(topLevelDir)) {
        continue;
      }
      collectArticleFiles(fullPath, rootDir, results);
    } else if (
      entry.isFile() &&
      entry.name.endsWith('.md') &&
      !entry.name.startsWith('_')
    ) {
      results.push(fullPath);
    }
  }
}

/**
 * Parse simple YAML frontmatter from markdown content.
 * Mirrors the parsing approach used in scripts/core/generate-api.js.
 */
function parseFrontmatter(content) {
  const fmRegex = /^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/;
  const match = content.match(fmRegex);

  if (!match) {
    return { frontmatter: {}, body: content };
  }

  const fmText = match[1];
  const body = match[2];
  const frontmatter = {};

  const lines = fmText.split('\n');
  let currentKey = null;
  let currentArrayValues = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Skip empty lines and comments
    if (!trimmed || trimmed.startsWith('#')) continue;

    // Check if this is a multiline array item (  - value)
    if (currentKey && /^\s+-\s+/.test(line)) {
      const itemValue = line
        .replace(/^\s+-\s+/, '')
        .trim()
        .replace(/^['"]|['"]$/g, '');
      if (currentArrayValues) {
        currentArrayValues.push(itemValue);
      }
      continue;
    }

    // Flush any pending multiline array
    if (currentKey && currentArrayValues) {
      frontmatter[currentKey] = currentArrayValues;
      currentKey = null;
      currentArrayValues = null;
    }

    // Parse key: value
    const colonIndex = trimmed.indexOf(':');
    if (colonIndex === -1) continue;

    const key = trimmed.slice(0, colonIndex).trim();
    let value = trimmed.slice(colonIndex + 1).trim();

    // Remove quotes
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }

    // Inline array: [a, b, c]
    if (value.startsWith('[') && value.endsWith(']')) {
      value = value
        .slice(1, -1)
        .split(',')
        .map((v) => v.trim().replace(/^['"]|['"]$/g, ''))
        .filter((v) => v.length > 0);
      frontmatter[key] = value;
      continue;
    }

    // Empty value might indicate a multiline array follows
    if (value === '') {
      currentKey = key;
      currentArrayValues = [];
      continue;
    }

    // Boolean coercion
    if (value === 'true') {
      frontmatter[key] = true;
      continue;
    }
    if (value === 'false') {
      frontmatter[key] = false;
      continue;
    }

    // Number coercion (for revision, etc.)
    if (/^\d+$/.test(value)) {
      frontmatter[key] = parseInt(value, 10);
      continue;
    }

    frontmatter[key] = value;
  }

  // Flush final pending multiline array
  if (currentKey && currentArrayValues) {
    frontmatter[currentKey] = currentArrayValues;
  }

  return { frontmatter, body };
}

/**
 * Calculate word count.
 * CJK characters count as 1 word each; latin words are whitespace-separated.
 */
function calculateWordCount(text) {
  if (!text) return 0;

  // Match CJK characters (CJK Unified Ideographs + common ranges)
  const cjkRegex =
    /[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3000-\u303f\uff00-\uffef]/g;
  const cjkMatches = text.match(cjkRegex);
  const cjkCount = cjkMatches ? cjkMatches.length : 0;

  // Remove CJK chars and count remaining latin words
  const withoutCjk = text.replace(cjkRegex, ' ');
  const latinWords = withoutCjk
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter((w) => w.length > 0);

  return cjkCount + latinWords.length;
}

/**
 * Read a single article file and return parsed data.
 * @param {string} filePath - Absolute path to the markdown file
 * @returns {{ frontmatter: object, body: string, filePath: string }}
 */
export function readArticle(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const { frontmatter, body } = parseFrontmatter(content);

  // Ensure tags is always an array
  if (frontmatter.tags && !Array.isArray(frontmatter.tags)) {
    frontmatter.tags = [frontmatter.tags];
  }
  if (!frontmatter.tags) {
    frontmatter.tags = [];
  }

  // Derive slug from filename
  const slug = path.basename(filePath, '.md');

  // Derive category from directory path
  const knowledgeDir = getKnowledgePath();
  const relativePath = path.relative(knowledgeDir, filePath);
  const category = relativePath.split(path.sep)[0] || 'Misc';

  // Calculate word count from body
  const wordCount = calculateWordCount(body);

  return {
    frontmatter: {
      title: frontmatter.title || slug,
      description: frontmatter.description || '',
      date: frontmatter.date || null,
      tags: frontmatter.tags,
      featured: frontmatter.featured === true,
      lastHumanReview: frontmatter.lastHumanReview ?? null,
      lastVerified: frontmatter.lastVerified || null,
      revision: frontmatter.revision ?? null,
      commitHash: frontmatter.commitHash || null,
      category: category.toLowerCase(),
      slug,
      wordCount,
    },
    body,
    filePath,
  };
}
