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
  /** 其中有 2 屆以上 **COMPUTEX** 參展紀錄的家數 */
  returning: number;
  /** COMPUTEX 參展紀錄涵蓋的最早年份 */
  earliestYear: number;
  /** COMPUTEX 參展紀錄涵蓋的最晚年份 */
  latestYear: number;
  /** COMPUTEX 參展紀錄涵蓋的不同屆數 */
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

/**
 * 官方名錄的 `exhibiting_record` 收的是**這家公司參加過的所有外貿協會展會**，
 * 不是只有 COMPUTEX：86 家共 542 列紀錄裡，442 列是 COMPUTEX TAIPEI，其餘 100
 * 列是 TAITRONICS、TAIPEI AMPA、TIMTOS、台灣形象展（馬來西亞 / 印尼 / 美國 /
 * 越南 / 菲律賓 / 歐洲）、台北國際自行車展、醫療展、食品展⋯⋯
 *
 * 2026-07-29 抓到：本檔原本把整包 record 當成 COMPUTEX 屆數在算，於是
 *   - 首頁 / 探索頁的「N 家跨屆參展」多算了 6 家
 *   - 「在 COMPUTEX 待最久的廠商」榜前三名（Leadtek / Siemens / Voltronic）
 *     其實不是 COMPUTEX 的前三名（真正的是 Dynatron / Innodisk / Chenbro），
 *     其中 Siemens 的名次有一部分來自它參加過的其他展
 *
 * 這正是本站宣稱不會犯的那一類錯：一個掛著「純機械、買不到」的排行榜，算錯了
 * 對象。榜單標題寫 COMPUTEX，計數就只能數 COMPUTEX。
 *
 * 原始的 record 不刪也不藏 —— 廠商頁的「歷年參展紀錄」表照列全部，只是把
 * 「幾屆 COMPUTEX」跟「其他展會」分開講。
 */
function isComputex(show: unknown): boolean {
  return String(show ?? '')
    .trim()
    .toUpperCase()
    .startsWith('COMPUTEX');
}

/** 這家廠商的 COMPUTEX 屆別年份集合（不含其他外貿協會展會）。 */
function computexYears(r: ExhibitorRecord): Set<number> {
  const ys = new Set<number>();
  for (const e of r.exhibiting_record ?? []) {
    if (!isComputex(e.show)) continue;
    const y = Number.parseInt(String(e.edition_year ?? ''), 10);
    if (Number.isFinite(y)) ys.add(y);
  }
  return ys;
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
    const ys = computexYears(r);
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
 * 只數 COMPUTEX（見 `isComputex` 的說明）。名錄裡有 2 家的歷年紀錄完全不含
 * COMPUTEX（只參加過其他外貿協會展會，2027 是第一次來），它們屆數為 0，
 * 自然排在最後 — 這是對的，不是要修掉的邊界。
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
    const ys = computexYears(r);
    out.push({
      name: r.name,
      editions: ys.size,
      since: ys.size ? Math.min(...ys) : 0,
      slug,
    });
  }
  // 第三順位用名稱：目前有 4 家同為 16 屆、同為 2010 年起，前兩個鍵分不出來。
  // 沒有第三個鍵的話，誰上榜取決於檔案讀取順序 —— 那是排行榜最不該有的東西。
  out.sort(
    (a, b) =>
      b.editions - a.editions ||
      a.since - b.since ||
      a.name.localeCompare(b.name, 'en'),
  );
  return out.slice(0, limit);
}
