/**
 * CATEGORY_REGISTRY — 分類的單一事實來源（SSOT）。
 *
 * 為什麼有這支：母體把同一張 13 分類對照表複製在 6 個地方
 * （category-static-paths / articles-index / rawArticle / TopicsMasonry /
 * CategoryGrid / article.template），而且自己的註解已經承認兩張表會漂移
 * （article.template.astro：「CATEGORY_MAPPING 一直有 politics，兩張表應同步」）。
 * 複製第七份只會讓漂移更難察覺，所以 COMPUTEX.md 在出生時就把它收斂成一支。
 *
 * 加分類的成本隨檔案數線性上升（分類資料夾名是 load-bearing 的：dashboard 統計、
 * frontmatter category、路由都吃它），所以請在 Stage 4 灌內容之前把 taxonomy 定死。
 *
 * URL slug 一律小寫；資料夾名維持首字母大寫，對齊 knowledge/ 目錄結構。
 */

/** URL slug → knowledge/ 資料夾名 */
export const CATEGORY_MAPPING: Record<string, string> = {
  vendors: 'Vendors',
  products: 'Products',
  editions: 'Editions',
  topics: 'Topics',
};

/** 所有 URL slug，順序即導覽列順序 */
export const CATEGORY_LIST: string[] = Object.keys(CATEGORY_MAPPING);

/** 所有資料夾名 */
export const CATEGORY_FOLDERS: string[] = Object.values(CATEGORY_MAPPING);

/** 資料夾名 → URL slug（反查） */
export const FOLDER_TO_SLUG: Record<string, string> = Object.fromEntries(
  Object.entries(CATEGORY_MAPPING).map(([slug, folder]) => [folder, slug]),
);

/** 顯示名稱。zh-TW 與 en 各一份，其餘語言 fallback 到 en。 */
export const CATEGORY_LABELS: Record<string, { 'zh-TW': string; en: string }> =
  {
    vendors: { 'zh-TW': '廠商', en: 'Vendors' },
    products: { 'zh-TW': '產品與技術', en: 'Products' },
    editions: { 'zh-TW': '歷屆展會', en: 'Editions' },
    topics: { 'zh-TW': '產業觀察', en: 'Topics' },
  };
