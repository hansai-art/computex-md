import { defineCollection } from 'astro:content';
import { ALL_LANGUAGE_CODES } from '../config/languages';
import { z } from 'astro/zod';

// Shared schema for all language collections — they have identical shape.
const articleSchema = z.object({
  title: z.string(),
  description: z.string().optional(),
  tags: z.array(z.string()).optional(),
  date: z.date().optional(),
  // 2026-06-07 SEO freshness: explicit "last meaningful edit" override. Set by
  // EVOLVE-PIPELINE on a substantive rewrite. When absent, dateModified falls
  // back to git last-meaningful-commit (content-dates.json) → frontmatter.date.
  modified: z.date().optional(),
  draft: z.boolean().optional(),
  category: z.string().optional(),
  author: z.string().optional(),
  readingTime: z.number().optional(),
  featured: z.boolean().optional(),
});

// Generate one collection per registered language. Adding a language to
// languages.ts automatically gets a content collection here — no edits needed.
export const collections = Object.fromEntries(
  ALL_LANGUAGE_CODES.map((code) => [
    code,
    defineCollection({ type: 'content', schema: articleSchema }),
  ]),
);
