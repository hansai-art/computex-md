#!/usr/bin/env node
/**
 * check-url-contract.mjs — build-output URL contract auditor
 *
 * 誕生背景（2026-07-17 hreflang 死鏈事件）：
 * 稽核發現全站 99.8% 頁面在 <head> 的 hreflang <link rel="alternate"> 對外公告
 * 死掉的 URL（累計 13,014 條），三個月沒人發現。根因不是某一次 code change 寫
 * 錯，而是**從來沒有一道閘門把「站體自我公告給機器的 URL」跟「build 出來真實
 * 存在的 route 表」對過帳**。hreflang / canonical / sitemap 這三種公告機制各自
 * 用不同邏輯算出目標 URL，只要任何一種算法跟實際檔案樹產生 drift（例如語言前
 * 綴規則改了、slug 正規化規則不一致、trailing slash 處理不一致），公告出去的
 * URL 就會指向不存在的頁面——Google/Bing 等爬蟲拿到 404，但人類 QA 用瀏覽器
 * 點頁面永遠看不到，因為 hreflang/canonical 不會出現在可見 UI 上。
 *
 * 這支工具就是那道閘門：對 `dist/`（Astro build 產物）做兩件事——
 *   1. 走訪檔案樹，重建「真實存在」的 URL 集合（ground truth）。
 *   2. 掃描每個 HTML 的 <head>（hreflang alternate + canonical）與
 *      sitemap-*.xml 的 <loc>，抽出「站體自我公告」的 URL 集合。
 * 兩個集合對帳：公告了但檔案樹裡找不到 = dead link 事件，回報。
 *
 * 刻意不驗「URL 格式合不合法」——那是替身訊號。只驗「檔案是否真的存在」。
 *
 * Usage:
 *   node scripts/tools/check-url-contract.mjs [distDir]        # report-only, exit 0
 *   node scripts/tools/check-url-contract.mjs --strict          # dead > 0 → exit 1
 *   node scripts/tools/check-url-contract.mjs --json            # machine-readable stdout
 *   node scripts/tools/check-url-contract.mjs dist --strict --json
 *
 * 預設模式是黃燈哲學（report-only, exit 0）：先跑起來收數據、觀察趨勢，
 * 等確認閘門本身沒有 false positive 再考慮在 CI 開 --strict 紅燈。
 */

import {
  readdirSync,
  statSync,
  openSync,
  readSync,
  closeSync,
  readFileSync,
} from 'node:fs';
import { LANGUAGES, DEFAULT_LANGUAGE } from '../../src/config/languages.mjs';
import { join, relative, extname, sep } from 'node:path';

const SITE_ORIGIN = 'https://computex.taiwanai.ngo';
const HEAD_READ_BYTES = 64 * 1024; // 64KB — head 段夠抽完所有 <link> tag
const MAX_EXAMPLES_PER_SOURCE = 20;

// ---------------------------------------------------------------------------
// CLI args
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const args = { distDir: 'dist', strict: false, json: false };
  for (const raw of argv) {
    if (raw === '--strict') args.strict = true;
    else if (raw === '--json') args.json = true;
    else if (!raw.startsWith('--')) args.distDir = raw;
  }
  return args;
}

// ---------------------------------------------------------------------------
// Step 1 — 走訪 dist/ 檔案樹，重建 ground-truth URL 集合
// ---------------------------------------------------------------------------

/**
 * dist/foo/index.html   → /foo/
 * dist/foo.html         → /foo
 * dist/index.html       → /
 * dist/assets/x.js      → /assets/x.js  (原路徑)
 *
 * 每個推導出來的路徑同時收「有無 trailing slash」+ decodeURIComponent
 * 變形進集合，比對時才不會被「site 內部各種公告機制對 trailing
 * slash / URL-encoding 處理不一致」誤判成 dead link。
 */
function walkDist(distDir) {
  const urlSet = new Set();
  let fileCount = 0;

  function addVariants(pathname) {
    const variants = new Set();
    variants.add(pathname);
    if (pathname.endsWith('/') && pathname !== '/') {
      variants.add(pathname.slice(0, -1));
    } else if (!pathname.endsWith('/')) {
      variants.add(pathname + '/');
    }
    for (const v of [...variants]) {
      try {
        const decoded = decodeURIComponent(v);
        variants.add(decoded);
        if (decoded.endsWith('/') && decoded !== '/') {
          variants.add(decoded.slice(0, -1));
        } else if (!decoded.endsWith('/')) {
          variants.add(decoded + '/');
        }
      } catch {
        // malformed percent-encoding in a literal filename — ignore decode variant
      }
    }
    for (const v of variants) urlSet.add(v);
  }

  function walk(dir) {
    let entries;
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (entry.name === '.DS_Store') continue;
      const full = join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
        continue;
      }
      if (!entry.isFile()) continue;
      fileCount++;
      const rel = relative(distDir, full).split(sep).join('/');
      if (entry.name === 'index.html') {
        const dirPart = rel.slice(0, -'index.html'.length); // e.g. "foo/" or ""
        addVariants('/' + dirPart);
      } else if (extname(entry.name) === '.html') {
        const noExt = rel.slice(0, -'.html'.length);
        addVariants('/' + noExt);
      } else {
        addVariants('/' + rel);
      }
    }
  }

  walk(distDir);
  return { urlSet, fileCount };
}

function normalizeForLookup(pathname) {
  let p = pathname;
  try {
    p = decodeURIComponent(p);
  } catch {
    // leave as-is if not valid percent-encoding
  }
  return p;
}

function isDead(urlSet, pathname) {
  const normalized = normalizeForLookup(pathname);
  if (urlSet.has(pathname) || urlSet.has(normalized)) return false;
  const toggled =
    normalized.endsWith('/') && normalized !== '/'
      ? normalized.slice(0, -1)
      : normalized + '/';
  if (urlSet.has(toggled)) return false;
  const toggledRaw =
    pathname.endsWith('/') && pathname !== '/'
      ? pathname.slice(0, -1)
      : pathname + '/';
  if (urlSet.has(toggledRaw)) return false;
  return true;
}

// ---------------------------------------------------------------------------
// Step 2 — 抽取「站體自我公告」的 URL（hreflang/rss alternate + canonical + sitemap）
// ---------------------------------------------------------------------------

/** 只讀檔案前 64KB（head 段），避免整檔讀入拖慢效能。 */
function readHead(filePath, maxBytes) {
  let fd;
  try {
    fd = openSync(filePath, 'r');
    const buf = Buffer.alloc(maxBytes);
    const bytesRead = readSync(fd, buf, 0, maxBytes, 0);
    return buf.toString('utf8', 0, bytesRead);
  } catch {
    return '';
  } finally {
    if (fd !== undefined) {
      try {
        closeSync(fd);
      } catch {
        /* noop */
      }
    }
  }
}

// <link rel="alternate" ...href="...">  (含 hreflang 與 rss，順序不拘)
const LINK_TAG_RE = /<link\s+([^>]*\brel="(?:alternate|canonical)"[^>]*)>/g;
const HREF_RE = /\bhref="([^"]*)"/;
const REL_RE = /\brel="([^"]*)"/;

function extractHeadLinks(html) {
  const out = []; // { source: 'hreflang'|'canonical', href }
  let m;
  LINK_TAG_RE.lastIndex = 0;
  while ((m = LINK_TAG_RE.exec(html)) !== null) {
    const attrs = m[1];
    const hrefMatch = HREF_RE.exec(attrs);
    const relMatch = REL_RE.exec(attrs);
    if (!hrefMatch || !relMatch) continue;
    const rel = relMatch[1];
    const source = rel === 'canonical' ? 'canonical' : 'hreflang'; // alternate (hreflang or rss) → 'hreflang' bucket
    out.push({ source, href: hrefMatch[1] });
  }
  return out;
}

const LOC_RE = /<loc>([^<]*)<\/loc>/g;

function extractSitemapLocs(xml) {
  const out = [];
  let m;
  LOC_RE.lastIndex = 0;
  while ((m = LOC_RE.exec(xml)) !== null) {
    out.push(m[1]);
  }
  return out;
}

/** 只驗 https://computex.taiwanai.ngo 開頭或相對路徑；外部域跳過。回傳 pathname 或 null。 */
function toPathnameOrNull(href) {
  if (!href) return null;
  let s = href.trim();
  if (s.startsWith(SITE_ORIGIN)) {
    s = s.slice(SITE_ORIGIN.length);
    if (s === '') s = '/';
  } else if (s.startsWith('/') && !s.startsWith('//')) {
    // relative path — keep as-is
  } else {
    return null; // external domain / protocol-relative / mailto: / etc.
  }
  // strip query + hash
  const qIdx = s.indexOf('?');
  if (qIdx !== -1) s = s.slice(0, qIdx);
  const hIdx = s.indexOf('#');
  if (hIdx !== -1) s = s.slice(0, hIdx);
  if (s === '') s = '/';
  return s;
}

// ---------------------------------------------------------------------------
// Step 3 — 走訪 dist/ 找所有 html 檔（給抽取公告用）與 sitemap-*.xml
// ---------------------------------------------------------------------------

function findFiles(distDir) {
  const htmlFiles = [];
  const sitemapFiles = [];

  function walk(dir) {
    let entries;
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (entry.name === '.DS_Store') continue;
      const full = join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
        continue;
      }
      if (!entry.isFile()) continue;
      if (extname(entry.name) === '.html') {
        htmlFiles.push(full);
      } else if (/^sitemap.*\.xml$/i.test(entry.name)) {
        sitemapFiles.push(full);
      }
    }
  }

  walk(distDir);
  return { htmlFiles, sitemapFiles };
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main() {
  const args = parseArgs(process.argv.slice(2));
  const distDir = args.distDir;

  try {
    statSync(distDir);
  } catch {
    console.error(`[check-url-contract] dist directory not found: ${distDir}`);
    console.error(
      'Run a build first, or pass the dist path as the first argument.',
    );
    process.exit(2);
  }

  const startedAt = Date.now();

  // --- ground truth ---
  const { urlSet, fileCount } = walkDist(distDir);

  // --- announced URLs ---
  const { htmlFiles, sitemapFiles } = findFiles(distDir);

  // source -> Map(rawHref -> announcingFile)  (dedupe by exact raw href string
  // for perf: most hreflang/rss link tags repeat verbatim across many pages)
  const announced = {
    hreflang: new Map(),
    canonical: new Map(),
    sitemap: new Map(),
  };

  for (const file of htmlFiles) {
    const head = readHead(file, HEAD_READ_BYTES);
    if (!head) continue;
    const links = extractHeadLinks(head);
    for (const { source, href } of links) {
      const bucket = announced[source];
      if (!bucket.has(href)) bucket.set(href, file);
    }
  }

  for (const file of sitemapFiles) {
    // sitemap files can be a few MB but are single-purpose; read whole file.
    const xml = readHead(file, 16 * 1024 * 1024); // 16MB cap, generous
    const locs = extractSitemapLocs(xml);
    for (const loc of locs) {
      if (!announced.sitemap.has(loc)) announced.sitemap.set(loc, file);
    }
  }

  // --- reconcile ---
  const result = {
    distDir,
    fileCount,
    urlSetSize: urlSet.size,
    htmlScanned: htmlFiles.length,
    sitemapScanned: sitemapFiles.length,
    elapsedMs: 0,
    totalAnnouncedUnique: 0,
    totalDead: 0,
    bySource: {},
  };

  for (const sourceName of ['hreflang', 'canonical', 'sitemap']) {
    const bucket = announced[sourceName];
    const deadExamples = [];
    let deadCount = 0;

    for (const [href, file] of bucket) {
      const pathname = toPathnameOrNull(href);
      if (pathname === null) continue; // external domain — skip
      if (isDead(urlSet, pathname)) {
        deadCount++;
        if (deadExamples.length < MAX_EXAMPLES_PER_SOURCE) {
          deadExamples.push({ file: relative(process.cwd(), file), url: href });
        }
      }
    }

    result.bySource[sourceName] = {
      totalAnnounced: bucket.size,
      dead: deadCount,
      examples: deadExamples,
    };
    result.totalAnnouncedUnique += bucket.size;
    result.totalDead += deadCount;
  }

  // --- 反向覆蓋：dist 裡的文章頁必須全部出現在 sitemap ---
  // 正向對賬抓「公告了不存在的」，這裡抓「存在了卻沒公告的」——對爬蟲與
  // SC 隱形的頁面。黃燈起步：報告但不計入 totalDead（strict 不擋），
  // 收數據確認無 false positive 後再升。
  const CATS = new Set([
    'history',
    'geography',
    'culture',
    'food',
    'art',
    'music',
    'technology',
    'nature',
    'people',
    'society',
    'economy',
    'lifestyle',
  ]);
  const LANG_PREFIXES = new Set(
    LANGUAGES.filter((l) => l.enabled && !l.isDefault).map((l) => l.code),
  );
  const sitemapSet = new Set();
  for (const href of announced.sitemap.keys()) {
    const p = toPathnameOrNull(href);
    if (!p) continue;
    const n = normalizeForLookup(p);
    for (const v of [p, n]) {
      sitemapSet.add(v);
      sitemapSet.add(v.endsWith('/') && v !== '/' ? v.slice(0, -1) : v + '/');
    }
  }
  const missingFromSitemap = [];
  for (const file of htmlFiles) {
    const rel = relative(distDir, file).replace(/\\/g, '/');
    if (!rel.endsWith('/index.html')) continue;
    const urlPath = '/' + rel.slice(0, -'/index.html'.length) + '/';
    const segs = urlPath.split('/').filter(Boolean);
    const catIdx = LANG_PREFIXES.has(segs[0]) ? 1 : 0;
    if (segs.length !== catIdx + 2 || !CATS.has(segs[catIdx])) continue;
    if (!sitemapSet.has(urlPath) && !sitemapSet.has(urlPath.slice(0, -1))) {
      // redirect stub（astro.config redirects 渲染的 meta-refresh 頁）本來
      // 就不該進 sitemap——只有真文章頁的缺席才是訊號
      const head = readHead(file, 4096) || '';
      if (/http-equiv=["']?refresh/i.test(head)) continue;
      missingFromSitemap.push(urlPath);
    }
  }
  result.sitemapCoverage = {
    articlePagesChecked: htmlFiles.length,
    missing: missingFromSitemap.length,
    examples: missingFromSitemap.slice(0, MAX_EXAMPLES_PER_SOURCE),
  };

  // --- 別名洩漏：英文別名側門一條都不准出現在對外公告面 ---
  // 2026-07-25 article-alias。別名是給「照我們自己的 URL 文法推網址」的人與
  // 機器走的側門，canonical 永遠是中文網址。它們不會變成死連結（頁面真的
  // 存在），要防的是反向風險：把側門公告成正門，讓 Google 把同一篇文章當兩個
  // URL 收。「永不公告」寫在產生器註解裡是自律，寫在這裡才是閘門
  // （REFLEXES #15：memory 是自律，canonical gate 才是閘門）。
  const aliasSet = new Set();
  try {
    const raw = readFileSync(
      join(process.cwd(), 'config/article-aliases.json'),
      'utf-8',
    );
    for (const key of Object.keys(JSON.parse(raw))) {
      aliasSet.add(normalizeForLookup(`/${key}/`));
    }
  } catch {
    /* registry 不存在（fork / 還沒跑產生器）→ 這節無事可做 */
  }
  const aliasLeaks = [];
  if (aliasSet.size) {
    for (const sourceName of ['hreflang', 'canonical', 'sitemap']) {
      for (const [href, file] of announced[sourceName]) {
        const pathname = toPathnameOrNull(href);
        if (pathname === null) continue;
        if (!aliasSet.has(normalizeForLookup(pathname))) continue;
        aliasLeaks.push({
          source: sourceName,
          url: href,
          file: relative(process.cwd(), file),
        });
      }
    }
  }
  result.aliasLeak = {
    aliasesTracked: aliasSet.size,
    leaks: aliasLeaks.length,
    examples: aliasLeaks.slice(0, MAX_EXAMPLES_PER_SOURCE),
  };
  // 別名洩漏計進 totalDead 讓 --strict 直接擋 deploy：這條紅燈起步，不走
  // 黃燈觀察期。反向覆蓋那條黃燈是因為可能誤報；這條的判準是集合包含關係，
  // 沒有模糊空間，命中就是真的漏了。
  result.totalDead += aliasLeaks.length;

  result.elapsedMs = Date.now() - startedAt;

  // --- output ---
  if (args.json) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    printHumanReport(result, args.strict);
  }

  // URL_CONTRACT_MODE=warn 讓 CI 在誤報搶修時能不擋 deploy（緊急逃生口，
  // 用了要在 commit message 說明）；預設不設 = strict 生效。
  const downgraded = process.env.URL_CONTRACT_MODE === 'warn';
  if (args.strict && result.totalDead > 0 && !downgraded) {
    process.exit(1);
  }
  if (downgraded && result.totalDead > 0) {
    console.error(
      `[check-url-contract] URL_CONTRACT_MODE=warn — ${result.totalDead} dead 未擋 deploy`,
    );
  }
  process.exit(0);
}

function printHumanReport(result, strict) {
  console.log('=== URL 契約對賬 (check-url-contract) ===');
  console.log(`dist: ${result.distDir}`);
  console.log(
    `檔案總數: ${result.fileCount}  (HTML: ${result.htmlScanned}, sitemap 檔: ${result.sitemapScanned})`,
  );
  console.log(`ground-truth URL 集合大小（含變形）: ${result.urlSetSize}`);
  console.log(
    `公告 URL 總數（去重後，跨三來源加總）: ${result.totalAnnouncedUnique}`,
  );
  console.log(`耗時: ${result.elapsedMs}ms`);
  console.log('');
  console.log(`>>> DEAD 總數: ${result.totalDead} <<<`);
  console.log('');

  const labels = {
    hreflang: 'hreflang/rss alternate',
    canonical: 'canonical',
    sitemap: 'sitemap <loc>',
  };
  for (const sourceName of ['hreflang', 'canonical', 'sitemap']) {
    const s = result.bySource[sourceName];
    console.log(`--- ${labels[sourceName]} ---`);
    console.log(`  公告數: ${s.totalAnnounced}  dead: ${s.dead}`);
    if (s.examples.length > 0) {
      console.log(`  範例（前 ${s.examples.length} 條）:`);
      for (const ex of s.examples) {
        console.log(`    [${ex.file}] → ${ex.url}`);
      }
    }
    console.log('');
  }

  if (result.sitemapCoverage) {
    const c = result.sitemapCoverage;
    console.log('--- sitemap 反向覆蓋（文章頁必須全在 sitemap）---');
    console.log(`  缺席: ${c.missing}（黃燈：報告不擋）`);
    for (const ex of c.examples) console.log(`    ✗ ${ex}`);
    console.log('');
  }

  if (result.aliasLeak) {
    const a = result.aliasLeak;
    console.log('--- 英文別名洩漏（側門不准出現在公告面）---');
    console.log(`  追蹤別名: ${a.aliasesTracked}`);
    console.log(`  洩漏: ${a.leaks}${a.leaks ? '（紅燈：計入 dead）' : ''}`);
    for (const ex of a.examples)
      console.log(`    ✗ [${ex.source}] ${ex.url}  ← ${ex.file}`);
    console.log('');
  }

  if (result.totalDead > 0) {
    console.log(
      strict
        ? '模式: --strict → dead > 0，exit 1。'
        : '模式: report-only（黃燈）→ exit 0。加 --strict 讓 dead > 0 變 exit 1。',
    );
  } else {
    console.log('沒有偵測到 dead 公告 URL。');
  }
}

main();
