#!/usr/bin/env node
/**
 * generate-og-images.mjs — 多語言 OG 圖片批次產生器 v4
 *
 * v4 結構性最佳化（2026-05-03 musing-chaplygin session）：
 *   舊 v3 為每篇文章開新 page navigation（newPage + goto + networkidle +
 *   font load wait + screenshot + close），單篇 ~2.3s × 4 worker = 17 min /
 *   ~1700 篇。每篇都重複 Astro hydration、font load、TCP roundtrip。
 *
 *   v4 改為「單頁 frontend + JS 動態替換 + screenshot loop」：
 *   ① inline HTML template 一次 setContent（無需 dev server）
 *   ② document.fonts 載一次 Noto Serif TC
 *   ③ 每篇 page.evaluate({...}) 直接 mutate DOM → double-rAF → screenshot
 *   實測（POC，2026-05-03）：50 entries 1.45s, mean 26ms/entry, p95 31ms。
 *   1731 篇預估 ~45s（單 worker）/ ~13s（4 worker），vs v3 17 min = 22-77×。
 *
 *   Trade-off：失去 Astro page rendering 的「設計即源碼」DRY。template 在
 *   本檔內 inline。為避免漂移：本檔自身列入 TEMPLATE_FILES，git mtime 改動
 *   觸發全量 regen；favicon embed 為 base64 確保視覺保真。
 *
 * 架構（與 v3 對比）：
 *   1. 渲染源：inline HTML（v3：Astro `?shot=1` page）
 *   2. 字體：Google Noto Serif TC inline `<link>`（同 v3）
 *   3. 輸出：JPG 85 到 public/og-images/[lang]/[category]/[slug].jpg（同 v3）
 *   4. Incremental：md 或本檔（template = self）mtime 比 JPG 新才重產（v3：模板 list mtime）
 *   5. 平行化：預設 4 worker（OG_WORKERS 覆寫，每 worker 獨立 page）（同 v3）
 *
 * **多語言 URL slug 規則（沿用 v3 v3）**：
 *   - zh-TW：URL 用 Chinese filename（如 /people/李洋/）
 *   - en：URL 用 en filename
 *   - ja/ko/其他：URL 用 en slug（via _translations.json 映射）
 *
 * 用法（向後相容 v3）：
 *   npm run og:generate                               # 全掃 article + diary（v4.1 預設含 diary）
 *   npm run og:generate -- --lang zh-TW               # 只產 zh-TW article
 *   npm run og:generate -- --lang ko --category food
 *   npm run og:generate -- --slug 李洋
 *   npm run og:generate -- --force                    # 全部重產
 *   npm run og:generate -- --diary                    # 只跑 diary
 *   npm run og:generate -- --no-diary                 # 跳過 diary（v4.1 新增 opt-out）
 *   npm run og:generate -- --diary --slug 2026-05-01-gamma-late
 *   OG_WORKERS=2 npm run og:generate                  # 降 worker 數
 *
 * v4.1（2026-05-03 musing-chaplygin 後續 fix）：production OG 抽樣發現所有 diary
 *   （/og-images/semiont/diary/*.jpg）皆 404，root cause 是 v3 v4 共有 pre-existing
 *   bug — CI 跑 `npm run og:generate` 預設不含 diary，需 `--include-diary`。修補：
 *   default 改為「articles + diary」一起跑（SSOT 對齊：site map 已含 diary OG path
 *   → generator 預設應產出）。`--include-diary` 保留為 alias 向後相容；`--no-diary`
 *   是新的 opt-out（局部跑 article-only 用例）。
 *
 * Diary 輸出：public/og-images/semiont/diary/[slug].jpg
 */

import { chromium } from 'playwright';
import { execSync } from 'node:child_process';
import { statSync, mkdirSync, existsSync, readFileSync } from 'node:fs';
import { readdir, stat, readFile } from 'node:fs/promises';
import { join, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import matter from 'gray-matter';

import {
  CATEGORY_LABELS,
  FOLDER_TO_SLUG,
} from '../../src/config/categories.mjs';
import {
  DEFAULT_LANGUAGE,
  ENABLED_LANGUAGE_CODES,
} from '../../src/config/languages.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const repoRoot = join(__dirname, '..', '..');

const knowledgeDir = join(repoRoot, 'knowledge');
const outDir = join(repoRoot, 'public', 'og-images');
const translationsPath = join(knowledgeDir, '_translations.json');
const faviconPath = join(repoRoot, 'public', 'favicon.png');

// 資料夾名 → URL slug。吃 src/config/categories.mjs 正本。
//
// 2026-07-29：這裡原本是母體 13 分類的第八份寫死副本。這個物種的資料夾叫
// Vendors / Products / Editions / Topics，一個都對不上，所以掃描結果永遠是
// 「0 routable items」，然後印「✅ No images need (re)generation」就結束 ——
// 全站 87 頁一張 OG 圖都沒有，而且看起來像成功。同一個形狀的坑在
// build-content-dates.mjs 已經踩過一次（第七份副本，產出 0 筆日期）。
// 分類表只准有一份，任何新的 build script 都 import 這支。
const CATEGORY_MAP = { ...FOLDER_TO_SLUG };

// 語言清單同樣吃正本，不寫死。母體是 4 語，這個物種目前 zh-TW + en。
// 寫死的後果比分類表更隱蔽：多寫一個沒開的語言只是白跑，少寫一個開了的語言
// 是那語言的 OG 圖整批不存在，而且不會有任何錯誤訊息。
const LANGUAGES = [...ENABLED_LANGUAGE_CODES];
const DEFAULT_LANG = DEFAULT_LANGUAGE.code;

// i18n labels。分類標籤吃 categories.mjs 正本（CATEGORY_LABELS），
// 這裡只轉成本檔要的 `{ lang: { slug: label } }` 形狀。
// 母體原本在這裡放一份 13 分類 × 4 語的手抄鏡像，附註「半年改一次、維護成本低」。
// 對這個物種不成立：分類名就是產品定位（廠商 / 產品 / 歷屆展會 / 產業觀察），
// 會跟著談授權的進度動，抄一份就是排定一次漂移。
const HOME_LABEL = {
  'zh-TW': '首頁',
  en: 'Home',
};

const CATEGORY_LABEL = Object.fromEntries(
  LANGUAGES.map((lang) => [
    lang,
    Object.fromEntries(
      Object.entries(CATEGORY_LABELS).map(([slug, labels]) => [
        slug,
        labels[lang] ?? labels[DEFAULT_LANG] ?? slug,
      ]),
    ),
  ]),
);

// 影響 OG 視覺輸出的檔案 — 任一 mtime 比 JPG 新 → 全量重產。
// v4：本檔自身（template inline）+ favicon。若本檔修 visual rendering 邏輯
// 或 favicon 改了，所有 OG 重 generate。
const TEMPLATE_FILES = [
  'scripts/core/generate-og-images.mjs',
  'public/favicon.png',
];

const DIARY_TEMPLATE_FILES = TEMPLATE_FILES; // 共用（v4 single template owner）
const DIARY_SOURCE_DIR = 'docs/semiont/diary';

const VIEWPORT = { width: 1200, height: 630 };
const JPEG_QUALITY = 85;
const FONT_WAIT_MS = 8000;
const WORKERS = Number(process.env.OG_WORKERS || 4);

// ── Greek transliteration (mirror src/lib/semiont-diary.ts) ────────────────
const GREEK_TRANSLIT = {
  α: 'alpha',
  β: 'beta',
  γ: 'gamma',
  δ: 'delta',
  ε: 'epsilon',
  ζ: 'zeta',
  η: 'eta',
  θ: 'theta',
  ι: 'iota',
  κ: 'kappa',
  λ: 'lambda',
  μ: 'mu',
  ν: 'nu',
  ξ: 'xi',
  ο: 'omicron',
  π: 'pi',
  ρ: 'rho',
  σ: 'sigma',
  τ: 'tau',
  υ: 'upsilon',
  φ: 'phi',
  χ: 'chi',
  ψ: 'psi',
  ω: 'omega',
};

function diarySlugFromFilename(filename) {
  const base = basename(filename, '.md');
  const m = base.match(/^(\d{4}-\d{2}-\d{2})(?:-(.+))?$/);
  if (!m) return null;
  const date = m[1];
  const suffix = m[2] || '';
  if (!suffix) return date;
  let translit = '';
  for (const ch of suffix) {
    if (ch === '+') {
      translit += '-plus';
    } else {
      translit += GREEK_TRANSLIT[ch] || ch;
    }
  }
  return `${date}-${translit}`;
}

// ── Frontmatter parsing ─────────────────────────────────────────────────────

function loadTranslationIndex() {
  const raw = readFileSync(translationsPath, 'utf-8');
  const translations = JSON.parse(raw);
  const zhToLang = {};
  for (const [langFile, zhFile] of Object.entries(translations)) {
    const lang = langFile.split('/')[0];
    if (!zhToLang[zhFile]) zhToLang[zhFile] = {};
    zhToLang[zhFile][lang] = langFile;
  }
  return { translations, zhToLang };
}

async function readArticleMeta(filePath) {
  const raw = await readFile(filePath, 'utf-8');
  const { data } = matter(raw);
  return {
    title: typeof data.title === 'string' ? data.title : null,
    description: typeof data.description === 'string' ? data.description : '',
  };
}

async function readDiaryMeta(filePath) {
  // Diary 無 frontmatter；title = H1 (#)。description 來源優先序：
  //   1. 第一個 blockquote `> ...`（舊文件常用）
  //   2. 第一個 italic-only 段落 `_..._`（新文件常用）
  //   3. 第一個非空白、非 heading、非 metadata 的段落
  const raw = await readFile(filePath, 'utf-8');
  const lines = raw.split('\n');
  let title = '';
  let titleLineIdx = -1;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].startsWith('# ')) {
      title = lines[i].replace(/^#\s+/, '').trim();
      titleLineIdx = i;
      break;
    }
  }

  let description = '';
  if (titleLineIdx >= 0) {
    const after = lines.slice(titleLineIdx + 1);
    for (const line of after) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      if (trimmed.startsWith('#')) continue;
      if (trimmed.startsWith('---')) continue;
      if (trimmed.startsWith('![')) continue;
      if (trimmed.startsWith('> ')) {
        description = trimmed.replace(/^>\s+/, '').trim();
        if (description.length >= 20) break;
        // too short → 繼續找下一段
        continue;
      }
      // italic-only paragraph: _..._ 或 *...*
      const italicMatch = trimmed.match(/^[_*](.+)[_*]$/);
      if (italicMatch && italicMatch[1].length >= 20) {
        description = italicMatch[1].trim();
        break;
      }
      // 一般段落
      if (
        !trimmed.startsWith('_') &&
        !trimmed.startsWith('*') &&
        trimmed.length >= 30
      ) {
        description = trimmed;
        break;
      }
    }
  }
  return { title: title || basename(filePath, '.md'), description };
}

// ── Article entry discovery (sync from v3) ──────────────────────────────────

async function findMarkdownFiles(filterLang, filterCategory) {
  const results = [];
  const { translations, zhToLang } = loadTranslationIndex();
  const langsToScan = filterLang ? [filterLang] : LANGUAGES;

  for (const lang of langsToScan) {
    for (const [folderName, categorySlug] of Object.entries(CATEGORY_MAP)) {
      if (filterCategory && categorySlug !== filterCategory) continue;

      if (lang === 'zh-TW') {
        const folderPath = join(knowledgeDir, folderName);
        if (!existsSync(folderPath)) continue;
        const files = await readdir(folderPath);
        for (const file of files) {
          if (!file.endsWith('.md') || file.startsWith('_')) continue;
          const filePath = join(folderPath, file).normalize('NFC');
          const fileStat = await stat(filePath);
          results.push({
            kind: 'article',
            lang,
            categorySlug,
            urlSlug: basename(file, '.md'),
            filePath,
            mtimeMs: fileStat.mtimeMs,
          });
        }
      } else if (lang === 'en') {
        const folderPath = join(knowledgeDir, 'en', folderName);
        if (!existsSync(folderPath)) continue;
        const files = await readdir(folderPath);
        for (const file of files) {
          if (!file.endsWith('.md') || file.startsWith('_')) continue;
          const filePath = join(folderPath, file).normalize('NFC');
          const fileStat = await stat(filePath);
          results.push({
            kind: 'article',
            lang,
            categorySlug,
            urlSlug: basename(file, '.md'),
            filePath,
            mtimeMs: fileStat.mtimeMs,
          });
        }
      } else {
        const enFolderPath = join(knowledgeDir, 'en', folderName);
        if (!existsSync(enFolderPath)) continue;
        const enFiles = await readdir(enFolderPath);
        for (const enFile of enFiles) {
          if (!enFile.endsWith('.md') || enFile.startsWith('_')) continue;
          const enKey = `en/${folderName}/${enFile}`;
          const zhFile = translations[enKey];
          if (!zhFile) continue;
          const langMap = zhToLang[zhFile];
          if (!langMap || !langMap[lang]) continue;
          const langFile = langMap[lang];
          const langFilePath = join(knowledgeDir, langFile).normalize('NFC');
          if (!existsSync(langFilePath)) continue;
          const fileStat = await stat(langFilePath);
          results.push({
            kind: 'article',
            lang,
            categorySlug,
            urlSlug: basename(enFile, '.md'),
            filePath: langFilePath,
            mtimeMs: fileStat.mtimeMs,
          });
        }
      }
    }
  }
  return results;
}

async function findDiaryEntries(filterSlug) {
  const folder = join(repoRoot, DIARY_SOURCE_DIR);
  if (!existsSync(folder)) return [];
  const files = await readdir(folder);
  const out = [];
  for (const f of files) {
    if (!f.endsWith('.md') || f.startsWith('_') || f.startsWith('.')) continue;
    const slug = diarySlugFromFilename(f);
    if (!slug) continue;
    if (filterSlug && slug !== filterSlug) continue;
    const full = join(folder, f);
    const st = await stat(full);
    out.push({
      kind: 'diary',
      lang: 'zh-TW',
      categorySlug: 'diary',
      urlSlug: slug,
      filePath: full,
      mtimeMs: st.mtimeMs,
    });
  }
  return out;
}

function outputPathFor(entry) {
  if (entry.kind === 'diary') {
    const dir = join(outDir, 'semiont', 'diary');
    return { dir, jpg: join(dir, `${entry.urlSlug}.jpg`) };
  }
  const isDefault = entry.lang === DEFAULT_LANG;
  const langPath = isDefault ? '' : entry.lang;
  const categoryOutDir = join(outDir, langPath, entry.categorySlug);
  return {
    dir: categoryOutDir,
    jpg: join(categoryOutDir, `${entry.urlSlug}.jpg`),
  };
}

function getTemplateMtimeMs() {
  return Math.max(
    0,
    ...TEMPLATE_FILES.map((f) => {
      const full = join(repoRoot, f);
      return existsSync(full) ? statSync(full).mtimeMs : 0;
    }),
  );
}

// ── HTML Template (inline) ──────────────────────────────────────────────────

function buildTemplateHtml(faviconDataUri) {
  return `<!doctype html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<title>OG Batch (computex.md)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;600;700&family=Noto+Serif+JP:wght@700;900&family=Noto+Serif+KR:wght@700;900&family=Noto+Serif+TC:wght@400;700;900&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body {
  width: 1200px; height: 630px;
  background: #1a3c34; color: #f4f0ea;
  font-family: 'Noto Serif TC', 'Source Han Serif TC', serif;
  overflow: hidden;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
body[data-diary='1'] {
  background: #03080a;
  background-image: linear-gradient(to bottom, #03080a 0%, #0a1612 100%);
}

.frame {
  width: 1200px; height: 630px;
  position: relative;
  padding: 12vh 6vw 6vh;
  display: flex; flex-direction: column;
}
body[data-diary='1'] .frame { padding: 18vh 6vw 8vh; }

.breadcrumb {
  font-size: 1.05rem;
  color: rgba(244, 240, 234, 0.65);
  margin-bottom: 1.6rem;
  font-family: 'Noto Sans TC', system-ui, -apple-system, sans-serif;
  font-weight: 400;
  display: flex;
  align-items: center;
  gap: 0.5em;
  white-space: nowrap;
  overflow: hidden;
}
body[data-diary='1'] .breadcrumb { display: none; }

.breadcrumb .crumb-sep {
  color: rgba(244, 240, 234, 0.45);
  font-size: 0.95em;
  flex-shrink: 0;
}
.breadcrumb .crumb {
  flex-shrink: 0;
}
.breadcrumb .crumb-trunc {
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

h1.hero-title {
  font-family: 'Noto Serif TC', 'Source Han Serif TC', serif;
  font-weight: 900;
  font-size: 3.75rem;
  line-height: 1.2;
  margin-bottom: 1.25rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: #f4f0ea;
  letter-spacing: 0.01em;
}
body[data-diary='1'] h1.hero-title {
  font-size: 3.5rem;
  font-weight: 900;
}
html[lang='ja'] h1.hero-title { font-family: 'Noto Serif JP', 'Noto Serif TC', serif; }
html[lang='ko'] h1.hero-title { font-family: 'Noto Serif KR', 'Noto Serif TC', serif; }

p.description {
  font-family: 'Noto Serif TC', 'Source Han Serif TC', serif;
  font-size: 1.2rem;
  line-height: 1.65;
  max-width: min(860px, 75%);
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: rgba(244, 240, 234, 0.85);
}
html[lang='ja'] p.description { font-family: 'Noto Serif JP', 'Noto Serif TC', serif; }
html[lang='ko'] p.description { font-family: 'Noto Serif KR', 'Noto Serif TC', serif; }

.watermark {
  position: absolute;
  right: 48px; bottom: 40px;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-family: 'Noto Serif TC', serif;
  font-weight: 700;
  font-size: 1.3rem;
  color: #ffffff;
  line-height: 1;
}
.watermark img {
  width: 1.4rem; height: 1.4rem;
  vertical-align: middle;
}
.watermark .brand-text { color: #ffffff; }
.watermark .brand-dot {
  font-family: 'Noto Sans TC', sans-serif;
  font-weight: 600;
  color: #00d4aa;
}
</style>
</head>
<body>
<div class="frame">
  <nav class="breadcrumb" id="breadcrumb"></nav>
  <h1 class="hero-title" id="title"></h1>
  <p class="description" id="description"></p>
  <span class="watermark">
    <img src="${faviconDataUri}" alt="" aria-hidden="true">
    <span class="brand-text">COMPUTEX<span class="brand-dot">.md</span></span>
  </span>
</div>
<script>
window.__renderOG = ({ kind, lang, title, description, breadcrumb }) => {
  document.documentElement.lang = lang || 'zh-TW';
  if (kind === 'diary') document.body.setAttribute('data-diary', '1');
  else document.body.removeAttribute('data-diary');

  const bc = document.getElementById('breadcrumb');
  bc.innerHTML = '';
  if (breadcrumb && breadcrumb.length) {
    breadcrumb.forEach((b, i) => {
      if (i > 0) {
        const sep = document.createElement('span');
        sep.className = 'crumb-sep';
        sep.textContent = '›';
        bc.appendChild(sep);
      }
      const s = document.createElement('span');
      // Last item gets ellipsis-truncate; earlier items are flex-shrink: 0
      s.className = i === breadcrumb.length - 1 ? 'crumb crumb-trunc' : 'crumb';
      s.textContent = b;
      bc.appendChild(s);
    });
  }

  document.getElementById('title').textContent = title || '';
  document.getElementById('description').textContent = description || '';
};

window.__waitFontReady = async () => {
  await document.fonts.ready;
  // 預載最關鍵 weight × family
  await Promise.all([
    document.fonts.load('900 60px "Noto Serif TC"'),
    document.fonts.load('900 60px "Noto Serif JP"').catch(() => {}),
    document.fonts.load('900 60px "Noto Serif KR"').catch(() => {}),
    document.fonts.load('400 19px "Noto Serif TC"'),
  ]);
  return document.fonts.check('900 60px "Noto Serif TC"');
};

window.__doubleRaf = () => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
</script>
</body>
</html>`;
}

// ── Per-entry render data builder ───────────────────────────────────────────

function buildBreadcrumb(entry) {
  if (entry.kind === 'diary') return [];
  const lang = entry.lang;
  const homeLabel = HOME_LABEL[lang] || HOME_LABEL[DEFAULT_LANG];
  const catLabel =
    CATEGORY_LABEL[lang]?.[entry.categorySlug] ||
    CATEGORY_LABEL[DEFAULT_LANG][entry.categorySlug] ||
    entry.categorySlug;
  // Article 第三層用 truncated title（v3 視覺保真）
  return [homeLabel, catLabel, entry.title || entry.urlSlug];
}

async function buildRenderPayload(entry) {
  if (entry.kind === 'diary') {
    const meta = await readDiaryMeta(entry.filePath);
    return {
      kind: 'diary',
      lang: 'zh-TW',
      title: meta.title,
      description: meta.description,
      breadcrumb: [],
    };
  }
  const meta = await readArticleMeta(entry.filePath);
  const enriched = {
    ...entry,
    title: meta.title || entry.urlSlug,
    description: meta.description || '',
  };
  return {
    kind: 'article',
    lang: entry.lang,
    title: enriched.title,
    description: enriched.description,
    breadcrumb: buildBreadcrumb(enriched),
  };
}

// ── Worker ──────────────────────────────────────────────────────────────────

async function workerLoop(
  id,
  queue,
  processedCounter,
  total,
  browser,
  templateHtml,
  skipFontWait,
) {
  const ctx = await browser.newContext({
    viewport: VIEWPORT,
    deviceScaleFactor: 1,
    reducedMotion: 'reduce',
  });
  const page = await ctx.newPage();
  let ok = 0,
    failed = 0;
  try {
    await page.setContent(templateHtml, { waitUntil: 'domcontentloaded' });
    if (!skipFontWait) {
      try {
        await page.waitForFunction(
          () => typeof window.__waitFontReady === 'function',
          { timeout: 5000 },
        );
        await page.evaluate(() => window.__waitFontReady());
      } catch (_) {
        /* fallback: continue without font ready signal */
      }
    }

    while (queue.length > 0) {
      const entry = queue.shift();
      if (!entry) break;
      const idx = ++processedCounter.value;
      const label =
        entry.kind === 'diary'
          ? `[${idx}/${total}] w${id} diary/${entry.urlSlug}`
          : `[${idx}/${total}] w${id} ${entry.lang}/${entry.categorySlug}/${entry.urlSlug}`;

      try {
        const payload = await buildRenderPayload(entry);
        await page.evaluate((data) => window.__renderOG(data), payload);
        await page.evaluate(() => window.__doubleRaf());
        const { dir, jpg } = outputPathFor(entry);
        if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
        await page.screenshot({
          path: jpg,
          type: 'jpeg',
          quality: JPEG_QUALITY,
          clip: { x: 0, y: 0, width: VIEWPORT.width, height: VIEWPORT.height },
          animations: 'disabled',
        });
        ok++;
        console.log(`${label} ... ✓`);
      } catch (err) {
        failed++;
        console.log(`${label} ... ✗ ${err.message}`);
      }
    }
  } finally {
    await ctx.close();
  }
  return { ok, failed };
}

// ── Main ────────────────────────────────────────────────────────────────────

/**
 * 自我修復的 Playwright 啟動（2026-06-01）：OG 生成最常見的失敗是 Playwright 瀏覽器
 * 二進位缺失/版本不符（cache key 漂移、arch 不符、版本 bump）。容錯的正解不是靜默跳過
 * （會讓問題長期隱形、很難發現），而是「偵測到 binary 問題 → 重新安裝 → 重渲染」自我修復。
 * 自癒一次仍失敗才上拋（由 main().catch 印明確錯誤 + 擋 build），確保真問題不被埋掉。
 */
async function launchChromiumWithHeal() {
  try {
    return await chromium.launch({ headless: true });
  } catch (err) {
    const msg = err && err.message ? err.message : String(err);
    const isMissingBinary =
      /Executable doesn't exist|playwright install|chrome-headless-shell/i.test(
        msg,
      );
    if (!isMissingBinary) throw err; // 非 binary 問題（如系統 deps）→ 直接上拋
    console.error(
      '\n⚠️  Playwright 瀏覽器二進位缺失 → 自我修復：重新安裝 chromium 後重試 launch（一次）',
    );
    console.error(`⚠️  觸發訊息：${msg.split('\n')[0]}`);
    try {
      execSync('npx playwright install chromium', { stdio: 'inherit' });
    } catch (installErr) {
      const im =
        installErr && installErr.message
          ? installErr.message
          : String(installErr);
      throw new Error(
        `Playwright 自動安裝失敗，無法 self-heal。launch 原錯：${msg.split('\n')[0]}；安裝錯：${im.split('\n')[0]}`,
      );
    }
    console.error('✓ Playwright chromium 安裝完成，重試 launch...');
    return await chromium.launch({ headless: true }); // 再失敗 → 上拋給 main().catch
  }
}

async function main() {
  const args = process.argv.slice(2);
  const getArg = (name) => {
    const eq = args.find((a) => a.startsWith(`--${name}=`));
    if (eq) return eq.split('=')[1];
    const i = args.indexOf(`--${name}`);
    return i !== -1 ? args[i + 1] : null;
  };
  const hasFlag = (name) => args.includes(`--${name}`);

  const filterLang = getArg('lang');
  const filterCategory = getArg('category');
  const filterSlug = getArg('slug');
  const force = hasFlag('force');
  const skipFontWait = hasFlag('no-font-wait');
  const onlyDiary = hasFlag('diary');
  const includeDiaryFlag = hasFlag('include-diary'); // v3 alias，向後相容
  const noDiary = hasFlag('no-diary');
  // v4.1 預設 articles + diary 一起跑（除非 --no-diary 或 --diary only）
  const includeDiary = onlyDiary || includeDiaryFlag || !noDiary;

  console.log(
    `\n🖼️  OG Image Generator v4 (inline-HTML batch / Noto Serif TC / JPG ${JPEG_QUALITY})`,
  );
  console.log(`   architecture: single-page + JS mutate + screenshot loop`);
  console.log(`   viewport    : ${VIEWPORT.width}×${VIEWPORT.height}`);
  console.log(`   workers     : ${WORKERS}`);
  if (filterLang) console.log(`   lang        : ${filterLang}`);
  if (filterCategory) console.log(`   category    : ${filterCategory}`);
  if (filterSlug) console.log(`   slug        : ${filterSlug}`);
  if (onlyDiary) console.log(`   mode        : --diary (only)`);
  else if (noDiary) console.log(`   mode        : --no-diary (article only)`);
  else console.log(`   mode        : article + diary (v4.1 default)`);
  if (force) console.log(`   mode        : --force`);
  console.log('');

  // Load favicon → base64 (embed once into template)
  if (!existsSync(faviconPath)) {
    // throw（非 process.exit）→ 走 main().catch 的非致命 handler，不擋 build
    throw new Error(`favicon not found: ${faviconPath}`);
  }
  const faviconB64 = readFileSync(faviconPath).toString('base64');
  const faviconDataUri = `data:image/png;base64,${faviconB64}`;
  const templateHtml = buildTemplateHtml(faviconDataUri);

  // Discovery
  const articleEntries = onlyDiary
    ? []
    : await findMarkdownFiles(filterLang, filterCategory);
  const diaryEntries = includeDiary ? await findDiaryEntries(filterSlug) : [];
  const entries = [...articleEntries, ...diaryEntries];

  const byLang = entries.reduce((acc, e) => {
    const key = e.kind === 'diary' ? 'diary' : e.lang;
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
  console.log(
    `📂 ${entries.length} routable items: ` +
      Object.entries(byLang)
        .map(([l, n]) => `${l}=${n}`)
        .join(', '),
  );

  const tplMtime = getTemplateMtimeMs();
  const toUpdate = entries.filter((entry) => {
    if (filterSlug && entry.urlSlug !== filterSlug) return false;
    if (force) return true;
    const { jpg } = outputPathFor(entry);
    if (!existsSync(jpg)) return true;
    const jpgMtime = statSync(jpg).mtimeMs;
    return entry.mtimeMs > jpgMtime || tplMtime > jpgMtime;
  });

  if (toUpdate.length === 0) {
    console.log(`✅ No images need (re)generation.\n`);
    return;
  }
  console.log(`📝 ${toUpdate.length} images queued.\n`);

  const browser = await launchChromiumWithHeal();
  const startTime = Date.now();

  const queue = [...toUpdate];
  const processedCounter = { value: 0 };

  let totals = { ok: 0, failed: 0 };
  try {
    const results = await Promise.all(
      Array.from({ length: WORKERS }, (_, i) =>
        workerLoop(
          i + 1,
          queue,
          processedCounter,
          toUpdate.length,
          browser,
          templateHtml,
          skipFontWait,
        ),
      ),
    );
    for (const r of results) {
      totals.ok += r.ok;
      totals.failed += r.failed;
    }
  } finally {
    await browser.close();
  }

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  const rate = elapsed > 0 ? (totals.ok / parseFloat(elapsed)).toFixed(2) : '0';
  const mark = totals.failed === 0 ? '✅' : '⚠️';
  console.log(
    `\n${mark}  ${totals.ok}/${toUpdate.length} in ${elapsed}s (${rate} img/s, ${WORKERS} workers)` +
      (totals.failed ? `, ${totals.failed} failed` : '') +
      '\n',
  );
}

main().catch((err) => {
  // 擋上線 + 錯誤標注明確（2026-06-01 哲宇 directive，修正先前「靜默 exit 0」）：
  // 容錯的正解是「自我修復」（launchChromiumWithHeal 偵測 binary 問題就重裝重渲染），
  // 不是吞掉錯誤。若 self-heal 後仍失敗 = 真問題 → 印「分類 + 怎麼修」明確錯誤並 exit 1
  // 擋住 deploy。寧可擋住讓人馬上發現且好修，也不要靜默讓問題長期隱形（很難發現）。
  const msg = err && err.message ? err.message : String(err);
  console.error(
    '\n❌ ════════════════════════════════════════════════════════',
  );
  console.error(
    '❌ OG 圖生成失敗 —— 擋 build/deploy（self-heal 後仍無解 = 真問題，需修）',
  );
  console.error(`❌ 錯誤：${msg.split('\n')[0]}`);
  if (
    /Executable doesn't exist|playwright install|chrome-headless-shell/i.test(
      msg,
    )
  ) {
    console.error('❌ 分類：Playwright 瀏覽器二進位問題（自動重裝後仍失敗）');
    console.error('❌ 怎麼修：');
    console.error(
      '❌   1) deploy.yml Playwright cache key 要含 runner.arch（os 對 arm/x64 都是 Linux）',
    );
    console.error(
      '❌   2)「Install Playwright Chromium binary」step 確認有跑（cache-hit 時也要能補裝）',
    );
    console.error(
      '❌   3) 本地重現：rm -rf ~/.cache/ms-playwright && npx playwright install chromium',
    );
  } else if (/favicon not found/i.test(msg)) {
    console.error(
      '❌ 分類：favicon 缺失 — 確認 public/favicon.png 存在於 repo',
    );
  } else {
    console.error('❌ 分類：未分類 OG 生成錯誤 — 完整 stack 如下供診斷：');
    console.error(err);
  }
  console.error(
    '❌ ════════════════════════════════════════════════════════\n',
  );
  process.exit(1);
});
