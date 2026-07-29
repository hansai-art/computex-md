/**
 * build-embeddings.mjs — semantic index bootstrap (RAG Phase 1).
 *
 * Article-level bge-m3 embeddings → two durable artifacts the whole system reuses
 * (the "keystone" of reports/research/2026-06/fleet-compute-all-pipelines-2026-06-14.md):
 *   public/api/related/{lang}.json        top-6 cosine neighbours per article
 *     (reader "you might also like" — zero client cost, no browser model)
 *   public/api/rag/{lang}/meta.json       [{id, slug, title, url, category}]
 *   public/api/rag/{lang}/vectors-i8.bin  Int8 unit vectors (×127), N×DIM flat
 *   public/api/rag/manifest.json          schema/model/dim/quant — versioned, swappable
 *
 * Embeddings run on the GPU fleet's `embed` service (bge-m3 on the 4090, always-on).
 * Schema is model-versioned: a later switch to CI e5-small = full rebuild, consumers
 * verify via manifest.model. Per RAG doc §2.1: local bge-m3 = bootstrap; steady-state
 * increment can move to CI e5-small (or always-on fleet) — manifest records which.
 *
 *   EMBED_HOST   Ollama endpoint (default localhost; set to fleet node for bge-m3)
 *   EMBED_MODEL  default bge-m3:latest
 *
 * Usage:
 *   EMBED_HOST=http://<fleet 節點位址>:11434 node scripts/core/build-embeddings.mjs --langs zh-TW,en
 *   node scripts/core/build-embeddings.mjs --langs all --limit 20   # test
 */
import { readdir, readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve, join, basename } from 'node:path';
import matter from 'gray-matter';
import {
  ENABLED_LANGUAGE_CODES,
  DEFAULT_LANGUAGE,
} from '../../src/config/languages.mjs';
import { CATEGORY_MAPPING } from '../../src/config/categories.mjs';

/**
 * 分類表只准有一份：src/config/categories.mjs。
 *
 * 2026-07-29：這裡原本寫死母體的 13 個分類（history / geography / culture /
 * food / …），一個都對不上本站的 Vendors / Products / Editions / Topics。
 * 效果跟前面十二支一樣：掃出 0 篇，然後安靜地產出一份空的 related index，
 * 沒有 exit code、沒有警告 —— `src/data/related/{lang}.json` 至今是 `{}`。
 */
const CATEGORY_MAP = CATEGORY_MAPPING;

const EMBED_HOST = (process.env.EMBED_HOST || 'http://localhost:11434').replace(
  /\/$/,
  '',
);
const EMBED_MODEL = process.env.EMBED_MODEL || 'bge-m3:latest';
const DIM = 1024; // bge-m3
const TOP_K = 8; // pre-fetch 8 neighbours as backup; frontend shows 4/3/3 (desktop/tablet/mobile)

const args = process.argv.slice(2);
const langArg = args[args.indexOf('--langs') + 1] || 'all';
const LANGS =
  langArg === 'all' || !args.includes('--langs')
    ? ENABLED_LANGUAGE_CODES
    : langArg.split(',');
const LIMIT = args.includes('--limit')
  ? parseInt(args[args.indexOf('--limit') + 1], 10)
  : Infinity;

// ── extract a rich embed text from an article: title + desc + headings + first para ──
function embedText(data, body) {
  const parts = [data.title || '', data.description || ''];
  const lines = body.split('\n');
  const headings = lines
    .filter((l) => /^#{1,3}\s/.test(l))
    .slice(0, 4)
    .map((l) => l.replace(/^#+\s*/, ''));
  parts.push(...headings);
  // first non-heading, non-blank, non-frontmatter-artifact paragraph
  const firstPara = lines.find((l) => {
    const t = l.trim();
    return (
      t &&
      !t.startsWith('#') &&
      !t.startsWith('>') &&
      !t.startsWith('|') &&
      !t.startsWith('_') &&
      !t.startsWith('![') &&
      !t.startsWith('---')
    );
  });
  if (firstPara) parts.push(firstPara.trim().slice(0, 500));
  return parts.filter(Boolean).join('\n').slice(0, 2000);
}

async function scanLang(lang) {
  const isDefault = lang === DEFAULT_LANGUAGE.code;
  const docs = [];
  for (const [slug, folder] of Object.entries(CATEGORY_MAP)) {
    const dir = isDefault
      ? resolve(process.cwd(), 'knowledge', folder)
      : resolve(process.cwd(), 'knowledge', lang, folder);
    let files;
    try {
      files = (await readdir(dir)).filter(
        (f) => f.endsWith('.md') && !f.startsWith('_'),
      );
    } catch {
      continue;
    }
    for (const file of files) {
      try {
        const { data, content } = matter(
          await readFile(join(dir, file), 'utf-8'),
        );
        const name = basename(file, '.md');
        docs.push({
          slug: `${slug}/${name}`,
          title: data.title || name,
          category: CATEGORY_MAP[slug],
          url: isDefault ? `/${slug}/${name}` : `/${lang}/${slug}/${name}`,
          text: embedText(data, content),
        });
      } catch {
        /* skip YAML errors */
      }
    }
  }
  return docs.slice(0, LIMIT);
}

async function embed(text) {
  const res = await fetch(`${EMBED_HOST}/api/embeddings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: EMBED_MODEL, prompt: text }),
  });
  if (!res.ok) throw new Error(`embed HTTP ${res.status}`);
  const j = await res.json();
  return j.embedding;
}

function l2normInt8(vec) {
  let n = 0;
  for (const x of vec) n += x * x;
  n = Math.sqrt(n) || 1;
  const out = new Int8Array(vec.length);
  for (let i = 0; i < vec.length; i++)
    out[i] = Math.max(-127, Math.min(127, Math.round((vec[i] / n) * 127)));
  return out;
}

function cosineI8(a, b) {
  let dot = 0;
  for (let i = 0; i < a.length; i++) dot += a[i] * b[i];
  return dot / (127 * 127); // unit vectors → ≈ cosine
}

async function run() {
  console.log(
    `🧬 build-embeddings — model=${EMBED_MODEL} host=${EMBED_HOST} langs=${LANGS.join(',')}`,
  );
  const outRag = resolve(process.cwd(), 'public/api/rag');
  const outRel = resolve(process.cwd(), 'public/api/related');
  // Slim related (slug-only neighbours) — committed build-input read by
  // src/utils/articles-index.ts getRelatedArticles. ~0.9MB across langs vs the
  // ~5MB full public/api/related (gitignored fleet output kept for debug/AI).
  const outRelSlim = resolve(process.cwd(), 'src/data/related');
  await mkdir(outRag, { recursive: true });
  await mkdir(outRel, { recursive: true });
  await mkdir(outRelSlim, { recursive: true });
  const manifest = {
    schema: 'rag-v1',
    model: EMBED_MODEL,
    dim: DIM,
    quant: 'i8-unit',
    builtAt: new Date().toISOString().replace(/\.\d+Z$/, 'Z'),
    langs: {},
    source: 'fleet-bge-m3-bootstrap',
  };

  for (const lang of LANGS) {
    const t0 = Date.now();
    const docs = await scanLang(lang);
    if (!docs.length) {
      console.log(`  ${lang}: 0 docs, skip`);
      continue;
    }
    const vecs = [];
    let ok = 0,
      fail = 0;
    for (const d of docs) {
      try {
        d.vec = l2normInt8(await embed(d.text));
        vecs.push(d);
        ok++;
      } catch (e) {
        fail++;
        if (fail <= 3) console.warn(`    ✗ ${lang}/${d.slug}: ${e.message}`);
      }
      if (ok % 100 === 0 && ok)
        process.stdout.write(`\r  ${lang}: ${ok}/${docs.length} embedded`);
    }
    process.stdout.write('\n');

    // 找得到文章、卻一個向量都沒產出 = 嵌入端點掛了（或位址沒設），不是內容問題。
    //
    // 這裡以前的行為是照樣往下寫一份空的 related index，印
    //   ✅ zh-TW: 0 vecs (3 fail), related+shard written, 0s
    // 然後 exit 0。有綠勾、有「written」、沒有 exit code —— 而且它會**覆蓋掉**
    // 上一次成功產出的索引。這正是這個 repo 追了十三次的那個形狀：產出 0 筆，
    // 但印成功訊息。所以在這裡硬擋，寧可整支失敗也不要留下一份空索引。
    if (!vecs.length) {
      console.error(
        `\n❌ ${lang}: 掃到 ${docs.length} 篇文章，但 0 篇嵌入成功（${fail} 篇失敗）。\n` +
          `   嵌入端點是 ${EMBED_HOST}（模型 ${EMBED_MODEL}）。先確認它活著：\n` +
          `     curl -s ${EMBED_HOST}/api/tags\n` +
          `   要指到別台：EMBED_HOST=http://<主機>:11434 node ${'scripts/core/build-embeddings.mjs'}\n` +
          `   已存在的索引保持不動，沒有被這次失敗覆蓋。\n`,
      );
      // continue 而不是 return：多語言時要把每一種語言的狀況都報完，
      // 不要因為第一種語言失敗就讓後面幾種看起來「沒跑到」。
      process.exitCode = 1;
      continue;
    }

    // related-articles: top-K cosine per article (same-lang)
    const related = {};
    for (let i = 0; i < vecs.length; i++) {
      const scores = [];
      for (let j = 0; j < vecs.length; j++) {
        if (i === j) continue;
        scores.push([j, cosineI8(vecs[i].vec, vecs[j].vec)]);
      }
      scores.sort((a, b) => b[1] - a[1]);
      related[vecs[i].slug] = scores.slice(0, TOP_K).map(([j, s]) => ({
        slug: vecs[j].slug,
        title: vecs[j].title,
        url: vecs[j].url,
        score: Math.round(s * 1000) / 1000,
      }));
    }
    // write artifacts
    const langDir = join(outRag, lang);
    await mkdir(langDir, { recursive: true });
    const meta = vecs.map((d, id) => ({
      id,
      slug: d.slug,
      title: d.title,
      url: d.url,
      category: d.category,
    }));
    const flat = new Int8Array(vecs.length * DIM);
    vecs.forEach((d, i) => flat.set(d.vec, i * DIM));
    await writeFile(join(langDir, 'meta.json'), JSON.stringify(meta));
    await writeFile(join(langDir, 'vectors-i8.bin'), Buffer.from(flat.buffer));
    await writeFile(join(outRel, `${lang}.json`), JSON.stringify(related));
    // slim: neighbour slugs only (page resolves summaries from the index).
    // Keep all TOP_K (8) — frontend renders 4/3/3, extras are backup if some
    // neighbour was deleted / is the current slug and gets filtered at render.
    const slim = {};
    for (const [k, arr] of Object.entries(related))
      slim[k] = arr.map((r) => r.slug);
    await writeFile(join(outRelSlim, `${lang}.json`), JSON.stringify(slim));
    manifest.langs[lang] = {
      count: vecs.length,
      failed: fail,
      bytes: flat.byteLength,
    };
    console.log(
      `  ✅ ${lang}: ${vecs.length} vecs (${fail} fail), related+shard written, ${((Date.now() - t0) / 1000).toFixed(0)}s`,
    );
  }
  await writeFile(
    join(outRag, 'manifest.json'),
    JSON.stringify(manifest, null, 2),
  );
  const total = Object.values(manifest.langs).reduce((s, l) => s + l.count, 0);
  console.log(
    `\n🧬 done — ${total} article vectors across ${Object.keys(manifest.langs).length} langs → public/api/rag/ + public/api/related/`,
  );
}

run().catch((e) => {
  console.error(e);
  process.exit(1);
});
