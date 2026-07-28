/**
 * rag-query.mjs — query the semantic index (verification + consumer prototype).
 *
 * Embeds a query via the same bge-m3 model, cosine-ranks against a lang's
 * Int8 vector shard. Proves cross-lingual semantic search (the RAG doc's
 * claim: a Korean query hits the right zh/ko Taiwan article) and is the
 * reference consumer for the future taiwanmd MCP `semantic_search` tool.
 *
 *   EMBED_HOST=http://<fleet 節點位址>:11434 node scripts/core/rag-query.mjs <lang> "<query>"
 *   node scripts/core/rag-query.mjs ko "민주주의와 선거"      # cross-lingual proof
 *   node scripts/core/rag-query.mjs zh-TW "原住民的歷史"
 */
import { readFile } from 'node:fs/promises';
import { resolve, join } from 'node:path';

const EMBED_HOST = (process.env.EMBED_HOST || 'http://localhost:11434').replace(
  /\/$/,
  '',
);
const EMBED_MODEL = process.env.EMBED_MODEL || 'bge-m3:latest';
const DIM = 1024;

const [lang, query] = process.argv.slice(2);
if (!lang || !query) {
  console.error('usage: rag-query.mjs <lang> "<query>"');
  process.exit(1);
}

async function embed(text) {
  const r = await fetch(`${EMBED_HOST}/api/embeddings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: EMBED_MODEL, prompt: text }),
  });
  const j = await r.json();
  return j.embedding;
}
function unit(v) {
  let n = 0;
  for (const x of v) n += x * x;
  n = Math.sqrt(n) || 1;
  return v.map((x) => x / n);
}

const base = resolve(process.cwd(), 'public/api/rag', lang);
const meta = JSON.parse(await readFile(join(base, 'meta.json'), 'utf-8'));
const buf = await readFile(join(base, 'vectors-i8.bin'));
const vecs = new Int8Array(buf.buffer, buf.byteOffset, buf.length);

const q = unit(await embed(query));
const scores = meta.map((m, i) => {
  let dot = 0;
  for (let d = 0; d < DIM; d++) dot += q[d] * vecs[i * DIM + d];
  return [m, dot / 127];
});
scores.sort((a, b) => b[1] - a[1]);

console.log(`🔎 [${lang}] "${query}"  (${meta.length} articles)`);
for (const [m, s] of scores.slice(0, 6))
  console.log(`  ${s.toFixed(3)}  ${m.title}  (${m.url})`);
