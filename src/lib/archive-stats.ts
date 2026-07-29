/**
 * archive-stats.ts — 首頁與導覽用的檔案庫統計，一律從事實層現算。
 *
 * 為什麼不寫死：首頁掛出來的每一個數字都是對讀者的宣稱。母體首頁掛的是
 * 「400+ 年歷史 / 59,000+ 物種」這種永遠不會被驗證的常識數字；我們掛的是
 * 「86 家廠商」這種一跑 harvester 就會變的數字。寫死＝下次抓完資料首頁就在
 * 說謊，而且沒有任何一支測試會叫。
 *
 * 資料源分工：
 *   data/exhibitors/*.json  官方名錄機械抽取的原始事實（廠商數 / 參展屆數）
 *   knowledge/<Cat>/*.md    實際產出的頁面數（跟路由一對一）
 *
 * 兩邊都讀，是因為它們回答不同問題：前者是「官方名錄說有幾家」，後者是
 * 「我們真的產出幾頁」。兩個數字不一致本身就是要看見的訊號，不是要抹平的誤差。
 */
import { readFileSync, readdirSync } from 'node:fs';
import { resolve, join } from 'node:path';
import matter from 'gray-matter';
import { CATEGORY_MAPPING } from '../config/categories';

export interface ExhibitingRecord {
  edition_year?: string;
  start_date?: string;
  end_date?: string;
  show?: string;
}

export interface ExhibitorRecord {
  exhibitor_id: string;
  name: string;
  venue?: string;
  show_area?: string;
  booth?: string;
  official_url?: string;
  brands?: string[];
  official_tags?: Array<{ code: string; label: string }>;
  exhibiting_record?: ExhibitingRecord[];
  source_url?: string;
  source_type?: string;
  last_checked_at?: string;
}

export interface ArchiveStats {
  /** 官方名錄抓到的參展廠商數 */
  vendors: number;
  /** 其中有 2 屆以上參展紀錄的家數 */
  returning: number;
  /** 參展紀錄涵蓋的最早年份 */
  earliestYear: number;
  /** 參展紀錄涵蓋的最晚年份 */
  latestYear: number;
  /** 參展紀錄涵蓋的不同屆數 */
  editionsCovered: number;
  /** 有攤位號的家數 */
  withBooth: number;
  /** 有官方網址的家數 */
  withOfficialUrl: number;
  /** 各分類實際產出的頁數（URL slug → 頁數） */
  pagesByCategory: Record<string, number>;
  /** 所有分類頁數總和 */
  totalPages: number;
}

const cache = new Map<string, ArchiveStats>();

/**
 * 該語言的 knowledge 根目錄。
 *
 * zh-TW 是 SSOT 根（`knowledge/<Cat>/`），其他語言在 `knowledge/<lang>/<Cat>/`。
 * 這個分岔必須貫穿到頁數統計裡：`knowledge/en/` 目前是空的，如果統計不分語言，
 * 英文首頁會宣稱有 86 頁廠商然後把讀者送到 `/en/vendors/<slug>`（不存在）。
 * 2026-07-29 首頁改寫時就是這樣一次做出 5 條死連結，被
 * `scripts/tools/verify-internal-links.mjs` 當場擋下來。
 */
function knowledgeRoot(lang: string): string[] {
  return lang === 'zh-TW' ? ['knowledge'] : ['knowledge', lang];
}

function readExhibitors(): ExhibitorRecord[] {
  const dir = resolve(process.cwd(), 'data/exhibitors');
  let files: string[] = [];
  try {
    files = readdirSync(dir).filter((f) => f.endsWith('.json'));
  } catch {
    return [];
  }
  const out: ExhibitorRecord[] = [];
  for (const f of files) {
    try {
      const raw = JSON.parse(readFileSync(join(dir, f), 'utf-8'));
      if (Array.isArray(raw.exhibitors)) out.push(...raw.exhibitors);
    } catch {
      // 壞掉的單一檔不該讓整個 build 掛掉，但也不該被無聲吞掉。
      console.warn(`[archive-stats] 讀不到 data/exhibitors/${f}，已跳過`);
    }
  }
  return out;
}

function countPages(lang: string, folder: string): number {
  try {
    return readdirSync(
      resolve(process.cwd(), ...knowledgeRoot(lang), folder),
    ).filter((f) => f.endsWith('.md') && !f.startsWith('_')).length;
  } catch {
    return 0;
  }
}

/**
 * @param lang 頁數要用哪個語言的 corpus 算。廠商 / 屆數這類展會事實跟語言無關，
 *             兩邊共用。
 */
export function getArchiveStats(lang = 'zh-TW'): ArchiveStats {
  const hit = cache.get(lang);
  if (hit) return hit;

  const exhibitors = readExhibitors();
  const years: number[] = [];
  let returning = 0;

  for (const r of exhibitors) {
    const ys = new Set<number>();
    for (const e of r.exhibiting_record ?? []) {
      const y = Number.parseInt(String(e.edition_year ?? ''), 10);
      if (Number.isFinite(y)) ys.add(y);
    }
    years.push(...ys);
    if (ys.size >= 2) returning += 1;
  }

  const pagesByCategory: Record<string, number> = {};
  for (const [slug, folder] of Object.entries(CATEGORY_MAPPING)) {
    pagesByCategory[slug] = countPages(lang, folder);
  }

  const stats: ArchiveStats = {
    vendors: exhibitors.length,
    returning,
    earliestYear: years.length ? Math.min(...years) : 0,
    latestYear: years.length ? Math.max(...years) : 0,
    editionsCovered: new Set(years).size,
    withBooth: exhibitors.filter((r) => r.booth).length,
    withOfficialUrl: exhibitors.filter((r) => r.official_url).length,
    pagesByCategory,
    totalPages: Object.values(pagesByCategory).reduce((a, b) => a + b, 0),
  };
  cache.set(lang, stats);
  return stats;
}

/**
 * exhibitor_id → 實際檔名 slug。
 *
 * 為什麼不在這裡重寫一份 slugify：`generate-vendor-pages.py` 的
 * `slugify()` 有砍公司後綴、NFKD 正規化、非 ASCII 丟棄三段行為，用 TypeScript
 * 重刻一份等於埋一個「兩邊哪天不一致，首頁就靜靜連到 404」的地雷。
 * 檔名本身就是唯一正解，直接讀它。
 */
function slugByExhibitorId(lang: string): Map<string, string> {
  const map = new Map<string, string>();
  const dir = resolve(
    process.cwd(),
    ...knowledgeRoot(lang),
    CATEGORY_MAPPING.vendors,
  );
  let files: string[] = [];
  try {
    files = readdirSync(dir).filter(
      (f) => f.endsWith('.md') && !f.startsWith('_'),
    );
  } catch {
    return map;
  }
  for (const f of files) {
    try {
      const { data } = matter(readFileSync(join(dir, f), 'utf-8'));
      const id = data?.vendor?.exhibitor_id;
      if (typeof id === 'string') map.set(id, f.replace(/\.md$/, ''));
    } catch {
      console.warn(`[archive-stats] 讀不到 ${dir}/${f}，已跳過`);
    }
  }
  return map;
}

/**
 * 連續參展最久的幾家，給首頁當「這個檔案庫有什麼」的實際樣本。
 *
 * 排序純機械：屆數多的在前，同屆數比誰更早開始。這條排序刻意跟未來的
 * Booth Score 同一個性質 — 文案吹捧不加分，只有可查證的紀錄算數。
 *
 * 沒有對應頁面的廠商直接不列入：首頁只放點得到的東西。
 */
export function longestExhibitors(
  lang = 'zh-TW',
  limit = 5,
): Array<{ name: string; editions: number; since: number; slug: string }> {
  const slugs = slugByExhibitorId(lang);
  const out: Array<{
    name: string;
    editions: number;
    since: number;
    slug: string;
  }> = [];
  for (const r of readExhibitors()) {
    const slug = slugs.get(r.exhibitor_id);
    if (!slug) continue;
    const ys = new Set<number>();
    for (const e of r.exhibiting_record ?? []) {
      const y = Number.parseInt(String(e.edition_year ?? ''), 10);
      if (Number.isFinite(y)) ys.add(y);
    }
    out.push({
      name: r.name,
      editions: ys.size,
      since: ys.size ? Math.min(...ys) : 0,
      slug,
    });
  }
  out.sort((a, b) => b.editions - a.editions || a.since - b.since);
  return out.slice(0, limit);
}
