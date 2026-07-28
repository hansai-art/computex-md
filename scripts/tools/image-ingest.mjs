#!/usr/bin/env node
/**
 * image-ingest.mjs — COMPUTEX.md 影像後處理工具鏈 SSOT（檢驗 + 調整 一條龍）
 *
 * 把 REWRITE-PIPELINE Step 1.9.2 / Step 4.3 規定的影像後處理手工步驟全部儀器化。
 * 之前散在：cache-county-images.mjs（只 Wikimedia 22 縣市）+ check-aspect.sh（只 aspect）
 * + 一堆 sips/curl 手跑。本工具用 sharp（Astro 已帶，cross-platform）統一。
 *
 * 三個 mode：
 *
 *   ingest — 下載/讀檔 → 嗅探 magic bytes → 擋 GIF/HEIC/BMP/TIFF → auto-orient + 清 EXIF/GPS
 *            → 縮放上限 → 轉檔（預設 WebP）→ quality search 壓到 size budget
 *            → 命名規範 → cache public/article-images/{cat}/ → 印 md/frontmatter/§圖片來源/授權矩陣
 *
 *   check  — 純檢驗（不改檔），pre-commit / CI gate：格式白名單 / aspect / size budget / EXIF 殘留
 *
 *   audit  — 全站掃 public/article-images/：格式分佈 / 超標 / EXIF 洩漏 / aspect 違規
 *            + WebP 遷移估算（非 webp 張數 + 可省 bytes）
 *
 * Usage:
 *   node scripts/tools/image-ingest.mjs ingest --src <URL|path> --cat Food \
 *        --name dan-ta-portuguese-tart-2024 --role hero \
 *        [--format webp|jpg|png|keep] [--alt "葡式蛋撻"] \
 *        [--credit "作者 / Wikimedia"] [--license "CC BY-SA 4.0"] [--source-url "https://..."] [--dry-run]
 *
 *   node scripts/tools/image-ingest.mjs check public/article-images/food/*.webp [--role hero]
 *   node scripts/tools/image-ingest.mjs audit [--cat Food] [--json]
 *
 * Canonical: REWRITE-PIPELINE Step 1.9.2 + Step 4.3 / REFLEXES #15 #30
 */
import {
  readFile,
  writeFile,
  mkdir,
  access,
  readdir,
  stat,
} from 'node:fs/promises';
import { dirname, join, basename, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, '..', '..');
const IMG_ROOT = join(REPO_ROOT, 'public', 'article-images');

// ── 護欄常數（對齊 REWRITE-PIPELINE Step 1.9.2）────────────────────────────
const SIZE_BUDGET = { hero: 600 * 1024, inline: 400 * 1024 }; // hard ceiling
const SIZE_WARN = { hero: 500 * 1024, inline: 350 * 1024 };
const DIM_CAP = { hero: 2400, inline: 1600 }; // max width，只縮不放
const ASPECT = { hero: [0.9, 2.0], inline: [0.75, 2.5] }; // w/h
const SVG_MAX = 50 * 1024;
const OUTPUT_FORMATS = new Set(['webp', 'jpg', 'jpeg', 'png']);
const BANNED_STORE = new Set(['gif', 'heic', 'heif', 'bmp', 'tiff']); // 須轉檔才入庫
const QUALITY_START = 82;
const QUALITY_FLOOR = 58;

const UA =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 COMPUTEX.md ImageIngest/1.0';

const C = {
  red: '\x1b[0;31m',
  grn: '\x1b[0;32m',
  yel: '\x1b[0;33m',
  gry: '\x1b[0;90m',
  bold: '\x1b[1m',
  cyan: '\x1b[0;36m',
  nc: '\x1b[0m',
};
const kb = (b) => `${(b / 1024).toFixed(0)}KB`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ── arg parser ────────────────────────────────────────────────────────────
function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next === undefined || next.startsWith('--')) out[key] = true;
      else {
        out[key] = next;
        i++;
      }
    } else out._.push(a);
  }
  return out;
}

// ── magic-bytes 格式嗅探（不信副檔名）──────────────────────────────────────
function sniffFormat(buf) {
  if (buf.length < 12) return 'unknown';
  const b = buf;
  if (b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff) return 'jpeg';
  if (b[0] === 0x89 && b[1] === 0x50 && b[2] === 0x4e && b[3] === 0x47)
    return 'png';
  if (
    b.slice(0, 4).toString('ascii') === 'RIFF' &&
    b.slice(8, 12).toString('ascii') === 'WEBP'
  )
    return 'webp';
  if (b[0] === 0x47 && b[1] === 0x49 && b[2] === 0x46) return 'gif';
  if (b[0] === 0x42 && b[1] === 0x4d) return 'bmp';
  if (
    (b[0] === 0x49 && b[1] === 0x49 && b[2] === 0x2a) ||
    (b[0] === 0x4d && b[1] === 0x4d && b[2] === 0x00)
  )
    return 'tiff';
  // HEIC/HEIF: ftyp box with heic/heix/mif1 brand
  if (b.slice(4, 8).toString('ascii') === 'ftyp') {
    const brand = b.slice(8, 12).toString('ascii');
    if (/heic|heix|hevc|mif1|heif/i.test(brand)) return 'heic';
  }
  const head = b.slice(0, 256).toString('utf-8');
  if (head.includes('<svg') || head.includes('<?xml')) return 'svg';
  return 'unknown';
}

// ── 下載（generalize cache-county：UA / 30s / 429,5xx retry / thumb→original）──
function thumbToOriginal(url) {
  const m = url.match(
    /^(https:\/\/upload\.wikimedia\.org\/wikipedia\/[a-z]+)\/thumb\/([0-9a-f])\/([0-9a-f]{2})\/([^/]+)\/[^/]+$/,
  );
  return m ? `${m[1]}/${m[2]}/${m[3]}/${m[4]}` : null;
}
async function fetchOnce(url) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 30000);
  try {
    return await fetch(url, {
      redirect: 'follow',
      headers: { 'User-Agent': UA, Accept: 'image/*' },
      signal: ctrl.signal,
    });
  } finally {
    clearTimeout(timer);
  }
}
async function download(url, attempt = 1) {
  try {
    let resp = await fetchOnce(url);
    if (resp.status === 404 && attempt === 1) {
      const orig = thumbToOriginal(url);
      if (orig) {
        console.log(`     ${C.gry}↻ thumb 404 → original${C.nc}`);
        resp = await fetchOnce(orig);
      }
    }
    if (!resp.ok) {
      if ((resp.status === 429 || resp.status >= 500) && attempt < 6) {
        await sleep(8000 * attempt); // Wikimedia 429 兇，需 8s+ 漸進退避
        return download(url, attempt + 1);
      }
      throw new Error(`HTTP ${resp.status}`);
    }
    return Buffer.from(await resp.arrayBuffer());
  } catch (e) {
    if (attempt < 4) {
      await sleep(3000);
      return download(url, attempt + 1);
    }
    throw e;
  }
}

// Commons File: page / Special:FilePath → canonical Special:FilePath download URL
// （讓 manifest 給 File: 頁 URL 或 "derive-from-file-page" 時也能直接下載原圖）
function commonsFilePath(src) {
  let m = src.match(/commons\.wikimedia\.org\/wiki\/(?:File|Image):(.+)$/i);
  if (m) {
    const fname = m[1].replace(/^.*\//, '').split('#')[0];
    return `https://commons.wikimedia.org/wiki/Special:FilePath/${fname}`;
  }
  if (/commons\.wikimedia\.org\/wiki\/Special:FilePath\//i.test(src))
    return src;
  return null;
}

async function resolveSource(src) {
  if (/^https?:\/\//.test(src)) {
    const cf = commonsFilePath(src);
    const url = cf || src;
    console.log(
      `  ${C.gry}↓ downloading ${cf ? '[Commons FilePath] ' : ''}${url.slice(0, 80)}…${C.nc}`,
    );
    return download(url);
  }
  const p = src.startsWith('/') ? src : join(REPO_ROOT, src);
  return readFile(p);
}

function validateName(name) {
  const bare = name.replace(/\.[a-z0-9]+$/i, '');
  const warn = [];
  if (!/^[a-z0-9-]+$/.test(bare))
    return {
      ok: false,
      bare,
      err: '命名須全小寫 kebab-case（無空格 / 無 CJK / 無底線）',
    };
  if (!/\d{4}/.test(bare))
    warn.push('建議含 4 位年份（{subject}-{topic}-{year}）');
  if (bare.split('-').length < 2) warn.push('建議 subject-topic 至少兩段');
  return { ok: true, bare, warn };
}

// ── ingest（調整 主路徑）────────────────────────────────────────────────────
async function modeIngest(args) {
  const { src, cat, name, role = 'inline' } = args;
  const fmt = (args.format || 'webp').toLowerCase();
  if (!src || !cat || !name) {
    console.error(`${C.red}缺參數：--src --cat --name 必填${C.nc}`);
    process.exit(2);
  }
  if (!['hero', 'inline'].includes(role)) {
    console.error(`${C.red}--role 只能 hero|inline${C.nc}`);
    process.exit(2);
  }
  const nameCheck = validateName(name);
  if (!nameCheck.ok) {
    console.error(`${C.red}✗ ${nameCheck.err}${C.nc}`);
    process.exit(2);
  }
  nameCheck.warn?.forEach((w) => console.log(`  ${C.yel}⚠ ${w}${C.nc}`));

  const catDir = cat.toLowerCase();
  let buf;
  try {
    buf = await resolveSource(src);
  } catch (e) {
    console.error(`${C.red}✗ 取源失敗：${e.message}${C.nc}`);
    process.exit(1);
  }

  const inFmt = sniffFormat(buf);
  console.log(
    `  ${C.gry}源格式（magic bytes）：${inFmt}　原始 ${kb(buf.length)}${C.nc}`,
  );
  if (inFmt === 'unknown') {
    console.error(`${C.red}✗ 無法辨識影像格式（magic bytes 不符）${C.nc}`);
    process.exit(1);
  }

  // SVG：向量，不 raster 處理，只檢查體積
  if (inFmt === 'svg') {
    if (buf.length > SVG_MAX)
      console.log(
        `  ${C.yel}⚠ SVG ${kb(buf.length)} > ${kb(SVG_MAX)} 上限${C.nc}`,
      );
    const dest = join(IMG_ROOT, catDir, `${nameCheck.bare}.svg`);
    if (!args['dry-run']) {
      await mkdir(dirname(dest), { recursive: true });
      await writeFile(dest, buf);
    }
    emitSnippets({ catDir, file: `${nameCheck.bare}.svg`, role, args });
    console.log(
      `  ${C.grn}✓ SVG 入庫 ${dest.replace(REPO_ROOT + '/', '')}${C.nc}`,
    );
    return;
  }

  if (BANNED_STORE.has(inFmt))
    console.log(
      `  ${C.cyan}↻ ${inFmt} 禁止入庫 → 轉檔為 ${fmt === 'keep' ? 'webp' : fmt}${C.nc}`,
    );

  // 出檔格式
  let outFmt =
    fmt === 'keep'
      ? inFmt === 'png'
        ? 'png'
        : inFmt === 'webp'
          ? 'webp'
          : 'jpeg'
      : fmt === 'jpg'
        ? 'jpeg'
        : fmt;
  if (BANNED_STORE.has(inFmt) && fmt === 'keep') outFmt = 'webp';
  if (!OUTPUT_FORMATS.has(outFmt)) {
    console.error(`${C.red}✗ 出檔格式不允許：${outFmt}${C.nc}`);
    process.exit(2);
  }
  const extFinal = outFmt === 'jpeg' ? 'jpg' : outFmt; // jpeg→jpg 副檔名

  let meta;
  try {
    meta = await sharp(buf).metadata();
  } catch (e) {
    console.error(`${C.red}✗ sharp 讀取失敗：${e.message}${C.nc}`);
    process.exit(1);
  }
  const hadExif = !!meta.exif || !!meta.iptc || !!meta.xmp;
  console.log(
    `  ${C.gry}原始尺寸 ${meta.width}×${meta.height}　EXIF/metadata：${hadExif ? '有（將清除）' : '無'}${C.nc}`,
  );

  const cap = DIM_CAP[role];
  // quality search 壓到 budget
  const budget = SIZE_BUDGET[role];
  const warnBudget = SIZE_WARN[role];
  let out,
    qUsed = QUALITY_START,
    finalMeta;
  for (let q = QUALITY_START; q >= QUALITY_FLOOR; q -= 6) {
    let pipe = sharp(buf, { failOn: 'error' }).rotate(); // auto-orient from EXIF then drop it
    if (meta.width > cap)
      pipe = pipe.resize({ width: cap, withoutEnlargement: true });
    if (outFmt === 'webp') pipe = pipe.webp({ quality: q, effort: 5 });
    else if (outFmt === 'jpeg') pipe = pipe.jpeg({ quality: q, mozjpeg: true });
    else if (outFmt === 'png')
      pipe = pipe.png({ compressionLevel: 9, palette: true });
    out = await pipe.toBuffer();
    qUsed = q;
    if (outFmt === 'png') break; // png 不做 quality search
    if (out.length <= budget) break;
  }
  finalMeta = await sharp(out).metadata();
  const ar = +(finalMeta.width / finalMeta.height).toFixed(3);
  const [amin, amax] = ASPECT[role];

  // 報告
  const sizeMark =
    out.length > budget
      ? `${C.red}✗ ${kb(out.length)} > ${kb(budget)} 超 budget${C.nc}`
      : out.length > warnBudget
        ? `${C.yel}⚠ ${kb(out.length)}${C.nc}`
        : `${C.grn}${kb(out.length)}${C.nc}`;
  const arMark =
    ar >= amin && ar <= amax
      ? `${C.grn}${ar}${C.nc}`
      : `${C.red}✗ ${ar}（${role} 須 ${amin}–${amax}，建議換圖不強塞）${C.nc}`;
  console.log(
    `  處理後：${finalMeta.width}×${finalMeta.height}　${outFmt} q${qUsed}　${sizeMark}　aspect ${arMark}　EXIF 已清`,
  );
  console.log(
    `  ${C.gry}壓縮率 ${((1 - out.length / buf.length) * 100).toFixed(0)}%（${kb(buf.length)} → ${kb(out.length)}）${C.nc}`,
  );

  const fileName = `${nameCheck.bare}.${extFinal}`;
  const dest = join(IMG_ROOT, catDir, fileName);
  if (args['dry-run']) {
    console.log(
      `  ${C.cyan}[dry-run] 不寫檔 → ${dest.replace(REPO_ROOT + '/', '')}${C.nc}`,
    );
  } else {
    await mkdir(dirname(dest), { recursive: true });
    await writeFile(dest, out);
    console.log(`  ${C.grn}✓ 入庫 ${dest.replace(REPO_ROOT + '/', '')}${C.nc}`);
  }
  emitSnippets({ catDir, file: fileName, role, args });
  // 硬性失敗 → 非零 exit（讓批次/CI 看得到）
  if (out.length > budget) process.exitCode = 1;
}

function emitSnippets({ catDir, file, role, args }) {
  const webPath = `/article-images/${catDir}/${file}`;
  const alt = args.alt || '（待填 alt：具體描述畫面，勿用「圖片」）';
  console.log(`\n  ${C.bold}── 貼進文章 ──${C.nc}`);
  if (role === 'hero')
    console.log(`  frontmatter:  ${C.cyan}image: ${webPath}${C.nc}`);
  console.log(`  markdown:     ${C.cyan}![${alt}](${webPath})${C.nc}`);
  if (args.credit || args.license || args['source-url']) {
    const credit = args.credit || '（作者）';
    const lic = args.license || '（授權）';
    const url = args['source-url'] || '';
    console.log(
      `  §圖片來源:    ${C.cyan}- [${credit}](${url}) — ${lic}${C.nc}`,
    );
    console.log(
      `  授權矩陣 row: ${C.gry}| ${file} | ${credit} | ${lic} | ${url} | ${role} |${C.nc}`,
    );
  } else {
    console.log(
      `  ${C.yel}⚠ 未給 --credit/--license/--source-url，§圖片來源 需手補（CC/fair-use 必標）${C.nc}`,
    );
  }
}

// ── check（檢驗 gate，不改檔）────────────────────────────────────────────────
async function inspectFile(path, roleHint) {
  const abs =
    path.startsWith('/') && !path.startsWith(REPO_ROOT)
      ? join(REPO_ROOT, path.replace(/^\//, 'public/'))
      : path.startsWith('/')
        ? path
        : join(REPO_ROOT, path);
  // 接受 repo-relative 或 web-path /article-images/...
  let real = abs;
  try {
    await access(real);
  } catch {
    real = join(REPO_ROOT, 'public', path.replace(/^\//, ''));
  }
  const buf = await readFile(real);
  const fmt = sniffFormat(buf);
  const role =
    roleHint || (basename(real).includes('hero') ? 'hero' : 'inline');
  const v = [];
  // 格式白名單
  if (BANNED_STORE.has(fmt))
    v.push({ sev: 'hard', msg: `格式 ${fmt} 禁止入庫（須轉 webp/jpg/png）` });
  else if (fmt === 'unknown')
    v.push({ sev: 'hard', msg: '無法辨識格式（magic bytes）' });
  let dims = '';
  if (fmt !== 'svg' && fmt !== 'unknown') {
    try {
      const m = await sharp(buf).metadata();
      dims = `${m.width}×${m.height}`;
      const ar = +(m.width / m.height).toFixed(3);
      const [amin, amax] = ASPECT[role];
      if (ar < amin || ar > amax)
        v.push({
          sev: 'hard',
          msg: `aspect ${ar}（${role} 須 ${amin}–${amax}）`,
        });
      if (m.exif || m.iptc || m.xmp)
        v.push({
          sev: 'warn',
          msg: 'EXIF/metadata 殘留（建議重新 ingest 清除）',
        });
      const budget = SIZE_BUDGET[role];
      if (buf.length > budget)
        v.push({
          sev: 'hard',
          msg: `${kb(buf.length)} > ${kb(budget)} (${role} budget)`,
        });
    } catch (e) {
      v.push({ sev: 'hard', msg: `sharp 讀取失敗：${e.message}` });
    }
  }
  if (fmt === 'svg' && buf.length > SVG_MAX)
    v.push({ sev: 'warn', msg: `SVG ${kb(buf.length)} > ${kb(SVG_MAX)}` });
  return {
    path: real.replace(REPO_ROOT + '/', ''),
    fmt,
    role,
    dims,
    size: buf.length,
    v,
  };
}

async function modeCheck(args) {
  const files = args._.slice(1);
  if (!files.length) {
    console.error(`${C.red}check 需要至少一個檔案路徑${C.nc}`);
    process.exit(2);
  }
  let hard = 0,
    warn = 0;
  for (const f of files) {
    let r;
    try {
      r = await inspectFile(f, args.role);
    } catch (e) {
      console.log(`${C.red}✗ ${f} — ${e.message}${C.nc}`);
      hard++;
      continue;
    }
    const mark = r.v.some((x) => x.sev === 'hard')
      ? C.red + '✗'
      : r.v.length
        ? C.yel + '⚠'
        : C.grn + '✓';
    console.log(
      `${mark} ${r.path}${C.nc}  ${C.gry}${r.fmt} ${r.dims} ${kb(r.size)} [${r.role}]${C.nc}`,
    );
    for (const x of r.v) {
      console.log(
        `    ${x.sev === 'hard' ? C.red : C.yel}${x.sev}: ${x.msg}${C.nc}`,
      );
      x.sev === 'hard' ? hard++ : warn++;
    }
  }
  console.log(
    `\n${hard ? C.red : C.grn}檢驗：${hard} hard / ${warn} warn${C.nc}`,
  );
  if (hard) process.exitCode = 1;
}

// ── audit（全站掃描 + WebP 遷移估算）─────────────────────────────────────────
async function walk(dir) {
  const out = [];
  let entries;
  try {
    entries = await readdir(dir, { withFileTypes: true });
  } catch {
    return out;
  }
  for (const e of entries) {
    const p = join(dir, e.name);
    if (e.isDirectory()) out.push(...(await walk(p)));
    else if (/\.(jpe?g|png|webp|svg|gif|bmp|tiff?|hei[cf])$/i.test(e.name))
      out.push(p);
  }
  return out;
}

async function modeAudit(args) {
  const base = args.cat ? join(IMG_ROOT, args.cat.toLowerCase()) : IMG_ROOT;
  const files = await walk(base);
  const byExt = {};
  let totalBytes = 0,
    nonWebpBytes = 0,
    nonWebpCount = 0,
    banned = 0,
    exifLeak = 0,
    oversize = 0,
    aspectBad = 0;
  const issues = [];
  for (const f of files) {
    const st = await stat(f);
    const ext = extname(f).slice(1).toLowerCase();
    byExt[ext] = (byExt[ext] || 0) + 1;
    totalBytes += st.size;
    const rel = f.replace(REPO_ROOT + '/', '');
    const role = basename(f).includes('hero') ? 'hero' : 'inline';
    if (
      ext === 'gif' ||
      ext === 'bmp' ||
      ext === 'tiff' ||
      ext === 'tif' ||
      ext === 'heic' ||
      ext === 'heif'
    ) {
      banned++;
      issues.push(`${C.red}banned${C.nc} ${rel}`);
    }
    if (!['webp', 'svg'].includes(ext)) {
      nonWebpCount++;
      nonWebpBytes += st.size;
    }
    if (ext !== 'svg') {
      try {
        const buf = await readFile(f);
        const m = await sharp(buf).metadata();
        if (m.exif || m.iptc || m.xmp) {
          exifLeak++;
        }
        const ar = m.width / m.height;
        const [amin, amax] = ASPECT[role];
        if (ar < amin || ar > amax) {
          aspectBad++;
        }
        if (st.size > SIZE_BUDGET[role]) {
          oversize++;
        }
      } catch {
        /* skip unreadable */
      }
    }
  }
  if (args.json) {
    console.log(
      JSON.stringify(
        {
          root: base.replace(REPO_ROOT + '/', ''),
          count: files.length,
          byExt,
          totalKB: Math.round(totalBytes / 1024),
          nonWebpCount,
          oversize,
          exifLeak,
          aspectBad,
          banned,
        },
        null,
        2,
      ),
    );
    return;
  }
  console.log(
    `${C.bold}📊 image audit — ${base.replace(REPO_ROOT + '/', '')}${C.nc}`,
  );
  console.log(
    `  檔案數：${files.length}　總體積：${(totalBytes / 1024 / 1024).toFixed(1)}MB`,
  );
  console.log(
    `  格式分佈：${Object.entries(byExt)
      .sort((a, b) => b[1] - a[1])
      .map(([k, v]) => `${k}=${v}`)
      .join(' ')}`,
  );
  console.log(
    `  ${banned ? C.red : C.grn}禁用格式（GIF/BMP/TIFF/HEIC）：${banned}${C.nc}`,
  );
  console.log(
    `  ${oversize ? C.yel : C.grn}超 size budget：${oversize}${C.nc}　${aspectBad ? C.yel : C.grn}aspect 違規：${aspectBad}${C.nc}　${exifLeak ? C.yel : C.grn}EXIF 殘留：${exifLeak}${C.nc}`,
  );
  console.log(
    `  ${C.cyan}WebP 遷移面：非 webp ${nonWebpCount} 張 / ${(nonWebpBytes / 1024 / 1024).toFixed(1)}MB（轉 webp 估省 25–35%）${C.nc}`,
  );
  if (issues.length) {
    console.log(`  ${C.gry}— banned 清單 —${C.nc}`);
    issues.slice(0, 20).forEach((i) => console.log(`    ${i}`));
  }
}

// ── dispatch ────────────────────────────────────────────────────────────────
const args = parseArgs(process.argv.slice(2));
const mode = args._[0];
const dispatch = { ingest: modeIngest, check: modeCheck, audit: modeAudit };
if (!dispatch[mode]) {
  console.error(
    `${C.bold}image-ingest.mjs${C.nc} — 影像後處理 SSOT\n` +
      `  modes: ${C.cyan}ingest${C.nc} (下載+調整+入庫) / ${C.cyan}check${C.nc} (檢驗 gate) / ${C.cyan}audit${C.nc} (全站掃描)\n` +
      `  see header for usage.`,
  );
  process.exit(mode ? 2 : 0);
}
dispatch[mode](args).catch((e) => {
  console.error(`${C.red}${e.stack || e.message}${C.nc}`);
  process.exit(1);
});
