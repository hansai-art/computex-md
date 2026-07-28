/**
 * rawArticle.ts — shared helpers for the /raw/ plain-text endpoints.
 *
 * Plain-text routes expose `knowledge/**.md` (the SSOT) directly over HTTP,
 * so readers on poor networks, old devices, screen readers, lynx, or anything
 * future-proof can read articles with zero JS, zero CSS, no images, no fonts.
 *
 * Mirrors the category mapping used in src/pages/[category]/[slug].astro.
 */

import { readdir, readFile } from 'fs/promises';
import { resolve, join, basename } from 'path';

import { CATEGORY_MAPPING } from '../config/categories';

/** 分類 slug → knowledge/ 資料夾名。SSOT 在 src/config/categories.ts。 */
export const CATEGORY_TO_FOLDER = CATEGORY_MAPPING;

/** Root-relative dir for a given language: '' = zh-TW, 'en' / 'ja' / etc. */
function langDir(lang: string): string {
  return lang === 'zh-TW' ? '' : lang;
}

export async function getRawPaths(lang: string) {
  const langSegment = langDir(lang);
  const knowledgeRoot = langSegment
    ? resolve(process.cwd(), 'knowledge', langSegment)
    : resolve(process.cwd(), 'knowledge');

  const paths: Array<{
    params: { category: string; slug: string };
    props: { lang: string; absPath: string };
  }> = [];

  for (const [categorySlug, folderName] of Object.entries(CATEGORY_TO_FOLDER)) {
    const folderPath = join(knowledgeRoot, folderName);
    let files: string[] = [];
    try {
      files = await readdir(folderPath);
    } catch {
      continue;
    }
    for (const file of files.filter(
      (f) => f.endsWith('.md') && !f.startsWith('_'),
    )) {
      const slug = basename(file, '.md');
      paths.push({
        params: { category: categorySlug, slug },
        props: {
          lang,
          absPath: join(folderPath, file).normalize('NFC'),
        },
      });
    }
  }
  return paths;
}

/**
 * Render a raw markdown response. Includes a 4-line provenance header so the
 * reader knows what they're looking at without rendering frontmatter UI.
 */
export async function renderRawMarkdown(absPath: string, lang: string) {
  const content = await readFile(absPath, 'utf-8');
  const relFromKnowledge = absPath.split('/knowledge/')[1] ?? '';
  const sourceUrl = relFromKnowledge
    ? `https://github.com/hansai-art/computex-md/blob/main/knowledge/${relFromKnowledge}`
    : '';

  const header = [
    `# Source: knowledge/${relFromKnowledge}`,
    `# Language: ${lang}`,
    `# License: CC BY-SA 4.0  ·  Editable on GitHub: ${sourceUrl}`,
    `# Plain-text view of COMPUTEX.md — no JS, no CSS, no images. The source markdown is the SSOT.`,
    '',
    '',
  ].join('\n');

  return header + content;
}

export const RAW_HEADERS = {
  'Content-Type': 'text/plain; charset=utf-8',
  'Cache-Control': 'public, max-age=3600',
  'X-Content-Type-Options': 'nosniff',
};
