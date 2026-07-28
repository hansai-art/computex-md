import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';

// 定義通用的 content collection schema
const baseContentSchema = z.object({
  title: z.string(),
  description: z.string(),
  date: z.coerce.date(),
  tags: z.array(z.string()).default([]),
  author: z.string().optional().default('COMPUTEX.md Contributors'),
  difficulty: z
    .enum(['beginner', 'intermediate', 'advanced'])
    .optional()
    .default('beginner'),
  readingTime: z.number().optional().default(5),
  featured: z.boolean().optional().default(false),
  status: z
    .enum(['draft', 'published', 'archived'])
    .optional()
    .default('published'),
  lastUpdated: z.coerce.date().optional(),
  relatedTopics: z.array(z.string()).optional().default([]),
  sources: z.array(z.string()).optional().default([]),
  subcategory: z.string().optional().default(''),
  // 相關日記：寫這篇文章時 Semiont 的反芻日記（讓讀者看見「寫的時候在想什麼」）。
  // 每筆給日記 slug（檔名去 .md，希臘字母 transliterate，對應 /semiont/diary/{slug}），
  // title / 摘要 / 日期由 RelatedDiaries.astro build-time 從日記檔自動 resolve。
  // 物件形式 { slug, excerpt } 可覆寫摘要。array 版，取代舊的單篇 diaryLink / diaryExcerpt。
  relatedDiary: z
    .array(
      z.union([
        z.string(),
        z.object({ slug: z.string(), excerpt: z.string().optional() }),
      ]),
    )
    .optional()
    .default([]),
  // 舊：單篇日記 teaser（DiaryTeaser）。relatedDiary 為其後繼，新文章用 relatedDiary。
  diaryLink: z.string().optional(),
  diaryExcerpt: z.string().optional(),
});

// 中文內容 collection
const zhTWCollection = defineCollection({
  type: 'content',
  schema: baseContentSchema.extend({
    // 中文特有欄位
    originalTitle: z.string().optional(), // 原始中文標題
    alternativeNames: z.array(z.string()).optional().default([]), // 別名
  }),
});

// 英文內容 collection
const enCollection = defineCollection({
  type: 'content',
  schema: baseContentSchema.extend({
    // 英文特有欄位
    chineseTitle: z.string().optional(), // 對應中文標題
    translationStatus: z
      .enum(['complete', 'partial', 'planned'])
      .optional()
      .default('complete'),
  }),
});

// 導出 collections
export const collections = {
  'zh-TW': zhTWCollection,
  en: enCollection,
};

// Type exports for TypeScript support
export type ZhTWContent = z.infer<typeof baseContentSchema> & {
  originalTitle?: string;
  alternativeNames?: string[];
};

export type EnContent = z.infer<typeof baseContentSchema> & {
  chineseTitle?: string;
  translationStatus?: 'complete' | 'partial' | 'planned';
};
