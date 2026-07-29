/**
 * hot-terms.ts — 搜尋框的「試試」熱門詞，唯一正本。
 *
 * ## 為什麼要有這支
 *
 * 熱門詞出現在兩個地方：/explore 的搜尋區，以及全站 Header 的搜尋 modal。
 * 兩邊本來各寫各的：
 *
 *   - /explore 從實際資料現算（展區 + 館別），這條路是對的。
 *   - Header 讀 `explore.hotSearches.term1` ～ `term6` 六個 i18n key，而這六個
 *     key 從來沒有存在過。母體有，我們沒有。`t()` 找不到 key 時回傳 key 本身，
 *     所以 modal 上直接印出 `explore.hotSearches.term1` 這串字，還做成可點的
 *     chip：點下去搜 `explore.hotSearches.term1`，結果是 0 筆。
 *     TypeScript 沒擋，因為那行是 `t(\`...\${n}\` as any)` —— 動態 key 加 as any，
 *     兩道型別防線同時被繞過。
 *
 * ## 這支的契約
 *
 * **印出來的每一個詞，都保證在使用者真的按下去的那個索引裡搜得到東西。**
 *
 * 光「從真實資料算」不夠：搜尋索引只吃 title / description / tags 三個欄位，
 * frontmatter 裡有的欄位不一定進得了索引。所以候選詞算完之後，會再拿
 * `public/api/search-minisearch-<lang>.json` —— 也就是 client 端等一下真的會
 * fetch 的那一份 —— 跑一次查詢，0 筆的直接丟掉。查詢管線（bigram 切詞 +
 * prefix）與 Layout.astro 的 `_queryBigrams` / `_doSearch` 對齊，不然這裡驗過
 * 的詞到瀏覽器上還是可能落空。
 *
 * 於是「點了搜不到」這個狀態變成結構上不可能，而不是靠人記得去點點看。
 */
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { resolve, join } from 'node:path';
import matter from 'gray-matter';
import MiniSearch from 'minisearch';
import { CATEGORY_MAPPING } from '../config/categories';

export interface HotTerm {
  /** chip 上顯示的字（展區名去掉英文括號那段） */
  label: string;
  /** 真正送進搜尋框的字串 */
  term: string;
}

const cache = new Map<string, HotTerm[]>();

/** 與 build-search-index.mjs / Layout.astro 的 isCJK 同一份範圍。 */
const isCJK = (cp: number) =>
  (cp >= 0x4e00 && cp <= 0x9fff) ||
  (cp >= 0x3400 && cp <= 0x4dbf) ||
  (cp >= 0x3040 && cp <= 0x30ff) ||
  (cp >= 0x31f0 && cp <= 0x31ff) ||
  (cp >= 0xac00 && cp <= 0xd7a3);

/** Layout.astro `_queryBigrams` 的 build 端分身（stop-bigram 過濾略去，
 *  它只會讓命中更少不會更多，這裡寧可嚴一點）。 */
function queryBigrams(text: string): string {
  const tokens: string[] = [];
  for (const seg of text.toLowerCase().normalize('NFKC').trim().split(/\s+/)) {
    if (!seg) continue;
    const chars = [...seg];
    if (!chars.some((c) => isCJK(c.codePointAt(0)!))) {
      tokens.push(seg);
      continue;
    }
    if (chars.length === 1) tokens.push(chars[0]);
    else
      for (let i = 0; i < chars.length - 1; i++)
        tokens.push(chars[i] + chars[i + 1]);
  }
  return tokens.join(' ');
}

/** 載入 client 端等一下會抓的那一份索引。抓不到就回 null（→ 不出 chip）。 */
function loadIndex(lang: string): MiniSearch | null {
  const shard = resolve(
    process.cwd(),
    'public/api',
    `search-minisearch-${lang}.json`,
  );
  if (!existsSync(shard)) return null;
  try {
    return MiniSearch.loadJSON(readFileSync(shard, 'utf-8'), {
      idField: 'id',
      fields: ['title_bigram', 'desc_bigram', 'tags_bigram'],
      storeFields: ['t', 'u'],
      tokenize: (text: string) => text.split(/\s+/).filter(Boolean),
      searchOptions: {
        boost: { title_bigram: 6, tags_bigram: 4, desc_bigram: 2 },
        prefix: true,
      },
    });
  } catch {
    return null;
  }
}

/**
 * 候選詞 = 廠商頁裡出現最多次的展區與館別。
 *
 * 展區取 `subcategory`（中文在前、英文在括號裡）而不是 `vendor.show_area`
 * （純英文）：chip 是給中文讀者看的，「AI 運算與技術」比 `AI Computing & Tech`
 * 更像一個會被打進搜尋框的詞。英文版頁面 subcategory 本身就是英文，同一段
 * 程式兩邊都對。
 */
function candidates(lang: string, isZh: boolean): HotTerm[] {
  const dir = resolve(
    process.cwd(),
    ...(isZh ? ['knowledge'] : ['knowledge', lang]),
    CATEGORY_MAPPING.vendors,
  );
  const zoneCount = new Map<string, number>();
  const hallCount = new Map<string, number>();
  try {
    for (const f of readdirSync(dir)) {
      if (!f.endsWith('.md') || f.startsWith('_')) continue;
      const raw = readFileSync(join(dir, f), 'utf-8');
      const { data } = matter(raw);
      const zone =
        typeof data?.subcategory === 'string' && data.subcategory.trim()
          ? data.subcategory
          : data?.vendor?.show_area;
      if (typeof zone === 'string' && zone.trim())
        zoneCount.set(zone, (zoneCount.get(zone) || 0) + 1);
      const hall = raw.match(
        /台北南港展覽館 \d 館|台北世貿[一二三]館|TaiNEX \d|TWTC Hall \d/,
      )?.[0];
      if (hall) hallCount.set(hall, (hallCount.get(hall) || 0) + 1);
    }
  } catch {
    // 資料夾不在（某語言還沒有內容）→ 沒有候選詞，區塊自己收掉
  }
  const top = (m: Map<string, number>, n: number) =>
    [...m.entries()].sort((a, b) => b[1] - a[1]).slice(0, n);
  return [
    ...top(zoneCount, 4).map(([term]) => ({
      // 展區名很長，chip 只放括號前那段，搜尋時仍送完整字串
      label: term.replace(/\s*[（(].*$/, ''),
      term,
    })),
    ...top(hallCount, 2).map(([term]) => ({ label: term, term })),
  ];
}

/**
 * 熱門搜尋詞。已對真實索引驗證過，每個詞至少搜得到 1 筆。
 *
 * @param limit chip 上限（Header modal 空間比 /explore 小）
 */
export function getHotSearchTerms(lang: string, limit = 4): HotTerm[] {
  const key = `${lang}:${limit}`;
  const hit = cache.get(key);
  if (hit) return hit;

  const engine = loadIndex(lang);
  const pool = candidates(lang, lang === 'zh-TW');
  const kept: HotTerm[] = [];
  for (const c of pool) {
    if (kept.length >= limit) break;
    // 索引還沒生出來（純 dev、還沒跑 prebuild:search）→ 不冒險出 chip
    if (!engine) break;
    const hits = engine.search(queryBigrams(c.term), {
      prefix: true,
      limit: 1,
    });
    if (hits.length > 0) kept.push(c);
  }
  cache.set(key, kept);
  return kept;
}
