/**
 * CATEGORY_REGISTRY（TypeScript 端的型別包裝）
 *
 * ⚠️ 資料正本在 `categories.mjs`，這支只補型別再 re-export，**不要在這裡改資料**。
 * 分成兩支的唯一理由：`scripts/core/*.mjs` 是 Node 直接執行的，吃不了 .ts。
 *
 * 為什麼要有這個 registry：母體把同一張 13 分類對照表複製在 6 個地方
 * （category-static-paths / articles-index / rawArticle / TopicsMasonry /
 * CategoryGrid / article.template），而且自己的註解已經承認兩張表會漂移
 * （article.template.astro：「CATEGORY_MAPPING 一直有 politics，兩張表應同步」）。
 * 2026-07-29 又在 `scripts/core/build-content-dates.mjs` 找到第七份（還停在母體的
 * 14 分類，導致 content-dates 產出 0 筆、/latest 與 sitemap lastmod 全空）。
 * 複製第八份只會讓漂移更難察覺。
 */

import {
  CATEGORY_MAPPING as _MAPPING,
  CATEGORY_LIST as _LIST,
  CATEGORY_FOLDERS as _FOLDERS,
  FOLDER_TO_SLUG as _FOLDER_TO_SLUG,
  CATEGORY_LABELS as _LABELS,
} from './categories.mjs';

/** URL slug → knowledge/ 資料夾名 */
export const CATEGORY_MAPPING: Record<string, string> = _MAPPING;

/** 所有 URL slug，順序即導覽列順序 */
export const CATEGORY_LIST: string[] = _LIST;

/** 所有資料夾名 */
export const CATEGORY_FOLDERS: string[] = _FOLDERS;

/** 資料夾名 → URL slug（反查） */
export const FOLDER_TO_SLUG: Record<string, string> = _FOLDER_TO_SLUG;

/** 顯示名稱。zh-TW 與 en 各一份，其餘語言 fallback 到 en。 */
export const CATEGORY_LABELS: Record<string, { 'zh-TW': string; en: string }> =
  _LABELS;
