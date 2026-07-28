#!/usr/bin/env node
/**
 * land-media-batch.mjs — 把一份 media manifest（軍團 research 產出）批次落地。
 *
 * 讀 manifest JSON（army-raw.json 等）→ 對某 slug 的每張圖呼叫 image-ingest ingest
 * （下載/清EXIF/縮放/WebP/壓縮/cache）→ 印出整篇文章的「貼進文章」編輯計畫
 * （frontmatter image: / 每張 inline markdown + caption / §圖片來源 list / 影片 + viz 提示）。
 *
 * image-ingest.mjs 仍是單張處理 SSOT；本檔只是 batch orchestrator（不重複處理邏輯）。
 *
 * Usage:
 *   node scripts/tools/land-media-batch.mjs --manifest reports/research/2026-06/media-manifests/army-raw.json \
 *        --slug 蛋撻 --prefix dan-ta [--dry-run] [--include-fair]
 *
 * 規則：
 *   - hero 取第一張 role=hero 且 landscape 的乾淨圖；portrait 的 hero 自動降 inline
 *   - 預設跳過 fair-use（除非 --include-fair），抽象/肖像需人工 source
 *   - direct_url 是真 http 就用；否則用 source_page（image-ingest 會 Special:FilePath 解析）
 *   - name = {prefix}-{hero|NN}[-{year}]，year 從 caption 取首個 4 位數
 *
 * Canonical: REWRITE Step 1.9.2 / 搭配 image-ingest.mjs
 */
import { readFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, '..', '..');
const INGEST = join(__dirname, 'image-ingest.mjs');

const C = {
  red: '\x1b[0;31m',
  grn: '\x1b[0;32m',
  yel: '\x1b[0;33m',
  gry: '\x1b[0;90m',
  bold: '\x1b[1m',
  cyan: '\x1b[0;36m',
  nc: '\x1b[0m',
};

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const k = a.slice(2),
        n = argv[i + 1];
      if (n === undefined || n.startsWith('--')) out[k] = true;
      else {
        out[k] = n;
        i++;
      }
    } else out._.push(a);
  }
  return out;
}
const aspect = (d) => {
  const m = /(\d+)\s*[x×]\s*(\d+)/.exec(d || '');
  return m ? +m[1] / +m[2] : null;
};
const yearOf = (s) => {
  const m = /\b(19|20)\d{2}\b/.exec(s || '');
  return m ? m[0] : null;
};
const isFair = (l) => /fair[\s-]?use/i.test(l || '');
const cleanLic = (l) =>
  !isFair(l) && /(cc0|cc\s?by|public domain|pd-|政府|open data)/i.test(l || '');

const args = parseArgs(process.argv.slice(2));
const { manifest, slug, prefix } = args;
if (!manifest || !slug || !prefix) {
  console.error(`${C.red}缺 --manifest --slug --prefix${C.nc}`);
  process.exit(2);
}
const dry = !!args['dry-run'];
const includeFair = !!args['include-fair'];

const all = JSON.parse(
  await readFile(
    manifest.startsWith('/') ? manifest : join(REPO_ROOT, manifest),
    'utf-8',
  ),
);
const m = all.find((x) => x.slug === slug);
if (!m) {
  console.error(`${C.red}manifest 無 slug=${slug}${C.nc}`);
  process.exit(1);
}
const cat = m.cat;
const catDir = cat.toLowerCase();

// 排序：hero 候選優先（role=hero & landscape & 乾淨），其餘依序
let imgs = (m.images || []).filter((im) => {
  if (isFair(im.license) && !includeFair) {
    console.log(
      `${C.yel}⏭ 跳過 fair-use：${im.subject?.slice(0, 40)}（需 --include-fair + 人工確認）${C.nc}`,
    );
    return false;
  }
  return true;
});

// 決定 hero：role=hero 且 aspect 合格的第一張；否則第一張 landscape 乾淨圖
let heroIdx = imgs.findIndex(
  (im) =>
    im.role === 'hero' &&
    (aspect(im.dims) === null ||
      (aspect(im.dims) >= 0.9 && aspect(im.dims) <= 2.0)),
);
if (heroIdx < 0)
  heroIdx = imgs.findIndex((im) => {
    const a = aspect(im.dims);
    return a !== null && a >= 0.9 && a <= 2.0;
  });

const plan = { hero: null, inline: [], sources: [] };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let inlineN = 0;
for (let i = 0; i < imgs.length; i++) {
  if (i > 0) await sleep(5000); // throttle Wikimedia（避免 429 burst）
  const im = imgs[i];
  const role = i === heroIdx ? 'hero' : 'inline';
  const yr = yearOf(im.caption) || yearOf(im.subject) || '';
  const name =
    role === 'hero'
      ? `${prefix}-hero${yr ? '-' + yr : ''}`
      : `${prefix}-${String(++inlineN).padStart(2, '0')}${yr ? '-' + yr : ''}`;
  const src =
    im.direct_url &&
    /^https?:\/\//.test(im.direct_url) &&
    !/derive-from-file-page/i.test(im.direct_url)
      ? im.direct_url
      : im.source_page;
  if (!src) {
    console.log(`${C.red}✗ 無可用 src：${im.subject?.slice(0, 40)}${C.nc}`);
    continue;
  }
  const credit = `${im.author || '?'} / Wikimedia Commons`;
  const ingestArgs = [
    'ingest',
    '--src',
    src,
    '--cat',
    cat,
    '--name',
    name,
    '--role',
    role,
    '--format',
    'webp',
    '--alt',
    im.alt || im.subject || '',
    '--credit',
    credit,
    '--license',
    im.license || '',
    '--source-url',
    im.source_page || '',
  ];
  if (dry) ingestArgs.push('--dry-run');
  console.log(
    `${C.bold}── ${role} ${name} ──${C.nc} ${C.gry}${im.tier} ${im.license}${C.nc}`,
  );
  let okIngest = true;
  try {
    execFileSync('node', [INGEST, ...ingestArgs], {
      stdio: 'inherit',
      cwd: REPO_ROOT,
    });
  } catch (e) {
    okIngest = false;
    console.log(
      `${C.red}  ✗ ingest 失敗（exit）— 可能超 budget / aspect，見上${C.nc}`,
    );
  }
  const webPath = `/article-images/${catDir}/${name}.webp`;
  const lic = im.license || '';
  const licShort = cleanLic(lic) ? lic.replace(/\s*via.*$/i, '') : lic;
  if (role === 'hero') plan.hero = { webPath, name, im };
  else plan.inline.push({ webPath, im });
  plan.sources.push(
    `- [${im.subject?.slice(0, 50) || name}](${im.source_page}) — Photo: ${im.author || '?'}, ${yr || 'n.d.'}, ${licShort}`,
  );
}

// ── 印編輯計畫 ──
console.log(
  `\n${C.bold}══════ ${slug} 編輯計畫（${plan.inline.length + (plan.hero ? 1 : 0)} 張）══════${C.nc}`,
);
if (plan.hero) {
  const im = plan.hero.im;
  console.log(`\n${C.cyan}# frontmatter（加在 readingTime 後）${C.nc}`);
  console.log(`image: '${plan.hero.webPath}'`);
  console.log(`imageCredit: '${im.author || '?'} / Wikimedia Commons'`);
  console.log(
    `imageLicense: '${(im.license || '').replace(/\s*via.*$/i, '')}'`,
  );
  console.log(`imageSource: '${im.source_page}'`);
}
console.log(
  `\n${C.cyan}# inline（放進對應段落，markdown + 斜體 caption）${C.nc}`,
);
for (const x of plan.inline) {
  const im = x.im;
  const licVia = /commons\.wikimedia/i.test(im.source_page || '')
    ? `[${(im.license || '').replace(/\s*via.*$/i, '')} via Wikimedia Commons](${im.source_page})`
    : `[${im.license}](${im.source_page})`;
  console.log(`\n![${im.alt || im.subject}](${x.webPath})`);
  console.log(
    `_${im.caption || im.subject}. Photo: ${im.author || '?'}. ${licVia}._`,
  );
}
console.log(`\n${C.cyan}# §圖片來源（放在 ## 參考資料 前）${C.nc}`);
console.log(
  `## 圖片來源\n\n本文使用 ${plan.sources.length} 張公有領域 / CC 授權圖片，全部 cache 於 \`public/article-images/${catDir}/\` 避免熱連結來源伺服器：\n`,
);
plan.sources.forEach((s) => console.log(s));
if ((m.videos || []).length) {
  console.log(`\n${C.cyan}# 官方影片（可選 iframe embed，Step 4.3.6）${C.nc}`);
  m.videos.forEach((v) =>
    console.log(
      `  - ${v.work?.slice(0, 50)} → youtube ${v.youtube_id} (${v.channel}, official=${v.verified_official})`,
    ),
  );
}
if ((m.viz_recommendation || '').trim())
  console.log(
    `\n${C.yel}# viz 建議（抽象題補圖表）：${C.nc}${m.viz_recommendation.slice(0, 200)}`,
  );
console.log(
  `\n${C.gry}negative: ${(m.negative_findings || '').slice(0, 160)}${C.nc}`,
);
