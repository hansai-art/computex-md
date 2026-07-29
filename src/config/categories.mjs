/**
 * CATEGORY_REGISTRY（.mjs 資料正本）
 *
 * 分類對照表**只有這一份**。TypeScript 端由 `categories.ts` import 後補型別再
 * re-export；Node 直跑的 build script（`scripts/core/*.mjs`）直接 import 這支。
 *
 * 為什麼是 .mjs 當正本而不是 .ts：build script 是 Node 直接執行的，吃不了 .ts。
 * 母體對語言清單的處理是「維護 languages.ts 與 languages.mjs 兩份 + 一支
 * check-language-registry-sync.sh 保證同步」，也就是承認會漂移然後加一道檢查。
 * 分類表這裡不重複那個結構：資料只有一份，TS 那份是薄包裝，沒有東西可以漂移。
 *
 * 加分類的成本隨檔案數線性上升（資料夾名是 load-bearing 的：dashboard 統計、
 * frontmatter category、路由都吃它），所以請在灌內容之前把 taxonomy 定死。
 *
 * URL slug 一律小寫；資料夾名維持首字母大寫，對齊 knowledge/ 目錄結構。
 */

/** URL slug → knowledge/ 資料夾名 */
export const CATEGORY_MAPPING = {
  vendors: 'Vendors',
  products: 'Products',
  editions: 'Editions',
  topics: 'Topics',
};

/** 所有 URL slug，順序即導覽列順序 */
export const CATEGORY_LIST = Object.keys(CATEGORY_MAPPING);

/** 所有資料夾名 */
export const CATEGORY_FOLDERS = Object.values(CATEGORY_MAPPING);

/** 資料夾名 → URL slug（反查） */
export const FOLDER_TO_SLUG = Object.fromEntries(
  Object.entries(CATEGORY_MAPPING).map(([slug, folder]) => [folder, slug]),
);

/** 顯示名稱（zh-TW / en） */
export const CATEGORY_LABELS = {
  vendors: { 'zh-TW': '廠商', en: 'Vendors' },
  products: { 'zh-TW': '產品與技術', en: 'Products' },
  editions: { 'zh-TW': '歷屆展會', en: 'Editions' },
  topics: { 'zh-TW': '產業觀察', en: 'Topics' },
};
