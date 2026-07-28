/**
 * COMPUTEX.md remote MCP endpoint — Cloudflare Worker.
 *
 * The OPTIONAL, thin-client counterpart to the local stdio server
 * (cli/src/lib/mcp-server.js). Local-first is always the recommended path
 * (best privacy); this remote endpoint exists for clients that can't run Node
 * (web playgrounds, curl, restricted environments).
 *
 * Speaks MCP over Streamable HTTP (stateless): POST a JSON-RPC request, get a
 * JSON-RPC result. Works with `npx mcp-remote <url>` and any HTTP MCP client.
 * Read-only; no auth, no API key, no billing — same public-good model as the
 * rest of COMPUTEX.md.
 *
 * Data sources (all public, static):
 *   - https://computex-md.pages.dev/api/articles.json        (metadata, all langs)
 *   - https://computex-md.pages.dev/raw/{category}/{slug}.md  (article bodies, lowercased category)
 *   - https://computex-md.pages.dev/api/dashboard-organism.json (organ vitals)
 *
 * Same 6 tools as the local server: search / read / rag / cite / organs / stats.
 * The local stdio server stays canonical; this mirrors its behaviour against
 * the static API. Deploy: see workers/mcp/README.md (needs a Cloudflare account).
 */

const API_BASE = 'https://computex-md.pages.dev';
const SERVER = { name: 'taiwanmd-remote', version: '0.7.1' };
const PROTOCOL_VERSION = '2024-11-05';

const REAL_CATEGORIES = new Set([
  'About',
  'Art',
  'Culture',
  'Economy',
  'Food',
  'Geography',
  'History',
  'Lifestyle',
  'Music',
  'Nature',
  'People',
  'Society',
  'Technology',
  'Resources',
]);

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Mcp-Session-Id, Accept',
};

// ── Module-global caches (warm across requests on the same isolate) ─────────
let _articles = null; // zh-TW (SSOT) entries only
let _bodies = new Map(); // slug → { frontmatter, body }

async function getArticles() {
  if (_articles) return _articles;
  const res = await fetch(`${API_BASE}/api/articles.json`, {
    cf: { cacheTtl: 1800, cacheEverything: true },
  });
  const all = await res.json();
  // articles.json mixes all languages; translations carry category = lang code.
  // The zh-TW SSOT entries are those whose category is a real category folder.
  _articles = all
    .filter((e) => e && e.path && REAL_CATEGORIES.has(e.category))
    .map((e) => {
      const slug = e.path.replace(/\.md$/, '').split('/').pop();
      return {
        title: e.title || slug,
        description: e.description || '',
        category: e.category,
        tags: e.tags || [],
        url: e.url || '',
        date: e.date || '',
        path: e.path,
        slug,
      };
    });
  return _articles;
}

function rawUrlFor(article) {
  // path = "History/19世紀的樟腦戰爭.md" → /raw/history/19世紀的樟腦戰爭.md
  const parts = article.path.replace(/\.md$/, '').split('/');
  const category = parts[0].toLowerCase();
  const slug = parts.slice(1).join('/');
  return `${API_BASE}/raw/${category}/${encodeURIComponent(slug)}.md`;
}

async function getBody(article) {
  if (_bodies.has(article.slug)) return _bodies.get(article.slug);
  let raw = '';
  try {
    const res = await fetch(rawUrlFor(article), {
      cf: { cacheTtl: 1800, cacheEverything: true },
    });
    if (res.ok) raw = await res.text();
  } catch {
    /* leave raw empty */
  }
  // Split YAML frontmatter from body.
  let frontmatter = {};
  let body = raw;
  const m = raw.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (m) {
    body = m[2];
    for (const line of m[1].split('\n')) {
      const kv = line.match(/^(\w[\w-]*):\s*(.*)$/);
      if (kv) frontmatter[kv[1]] = kv[2].replace(/^['"]|['"]$/g, '');
    }
  }
  const out = { frontmatter, body };
  _bodies.set(article.slug, out);
  return out;
}

// ── Search: dependency-free scoring over metadata ──────────────────────────
function searchArticles(articles, query, limit) {
  const q = (query || '').toLowerCase().trim();
  if (!q) return [];
  const terms = q.split(/\s+/).filter(Boolean);
  const scored = [];
  for (const a of articles) {
    const title = (a.title || '').toLowerCase();
    const desc = (a.description || '').toLowerCase();
    const cat = (a.category || '').toLowerCase();
    const tags = (a.tags || []).join(' ').toLowerCase();
    let score = 0;
    for (const t of terms) {
      if (title.includes(t)) score += 10;
      if (desc.includes(t)) score += 4;
      if (cat.includes(t)) score += 3;
      if (tags.includes(t)) score += 2;
    }
    if (title === q) score += 20;
    if (score > 0) scored.push({ a, score });
  }
  scored.sort((x, y) => y.score - x.score);
  return scored.slice(0, limit).map(({ a }) => ({
    title: a.title,
    slug: a.slug,
    category: a.category,
    description: a.description,
    url: a.url,
  }));
}

function findBySlug(articles, slug) {
  return (
    articles.find((a) => a.slug === slug) ||
    articles.find((a) => a.slug.includes(slug)) ||
    articles.find((a) => (a.title || '').includes(slug))
  );
}

// ── Tool implementations (mirror cli/src/lib/mcp-server.js) ─────────────────
async function toolSearch({ query, limit = 5 }) {
  const articles = await getArticles();
  return text(JSON.stringify(searchArticles(articles, query, limit), null, 2));
}

async function toolRead({ slug }) {
  const articles = await getArticles();
  const a = findBySlug(articles, slug);
  if (!a) return text(`Not found: ${slug}`, true);
  const { frontmatter, body } = await getBody(a);
  return text(
    `# ${frontmatter.title || a.title}\n\n${frontmatter.description || a.description || ''}\n\n---\n\n${body}`,
  );
}

async function toolRag({ query, limit = 3 }) {
  const articles = await getArticles();
  const hits = searchArticles(articles, query, limit);
  const sections = [];
  for (let i = 0; i < hits.length; i++) {
    const a = findBySlug(articles, hits[i].slug);
    if (!a) continue;
    const { frontmatter, body } = await getBody(a);
    sections.push(
      `## ${i + 1}. ${frontmatter.title || a.title} (${a.category})\n\n${body}`,
    );
  }
  return text(
    `# Taiwan Knowledge Context\n\n${sections.join('\n\n---\n\n')}\n\n---\nBased on the above context about Taiwan, answer the following question:\n${query}`,
  );
}

async function toolCite({ query, limit = 3 }) {
  const articles = await getArticles();
  const hits = searchArticles(articles, query, 10);
  const claims = [];
  const fnDefRe =
    /^\[\^([\w-]+)\]:\s*(?:\[([^\]]+)\]\(([^)]+)\))?\s*(?:—\s*(.+))?/gm;
  for (const hit of hits.slice(0, 5)) {
    const a = findBySlug(articles, hit.slug);
    if (!a) continue;
    const { frontmatter, body } = await getBody(a);
    const defs = {};
    let m;
    fnDefRe.lastIndex = 0;
    while ((m = fnDefRe.exec(body)) !== null) {
      defs[m[1]] = { name: m[2] || null, url: m[3] || null, desc: m[4] || '' };
    }
    for (const s of body.split(/(?<=[。！？!?])\s*/)) {
      const clean = s.trim();
      if (clean.length < 20 || clean.length > 300) continue;
      const fns = [...clean.matchAll(/\[\^([\w-]+)\]/g)].map((x) => x[1]);
      if (!fns.length) continue;
      const sources = fns.map((id) => defs[id]).filter((d) => d && d.url);
      if (!sources.length) continue;
      claims.push({
        claim: clean.replace(/\[\^[\w-]+\]/g, '').trim(),
        article: frontmatter.title || a.title,
        sources,
      });
      if (claims.length >= limit) break;
    }
    if (claims.length >= limit) break;
  }
  return text(JSON.stringify(claims, null, 2));
}

async function toolOrgans() {
  const res = await fetch(`${API_BASE}/api/dashboard-organism.json`, {
    cf: { cacheTtl: 900, cacheEverything: true },
  });
  return text(await res.text());
}

async function toolStats() {
  const articles = await getArticles();
  const byCategory = {};
  for (const a of articles)
    byCategory[a.category] = (byCategory[a.category] || 0) + 1;
  return text(
    JSON.stringify(
      { totalArticles: articles.length, byCategory, source: API_BASE },
      null,
      2,
    ),
  );
}

const TOOLS = [
  {
    name: 'taiwanmd_search',
    title: 'Search COMPUTEX.md articles',
    description:
      'Full-text search across 900+ curated articles about Taiwan. Returns top N hits with title, slug, category, and description.',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string' },
        limit: { type: 'number', default: 5 },
      },
      required: ['query'],
    },
    run: toolSearch,
  },
  {
    name: 'taiwanmd_read',
    title: 'Read a COMPUTEX.md article by slug',
    description:
      'Return the full body of an article (frontmatter + markdown body).',
    inputSchema: {
      type: 'object',
      properties: { slug: { type: 'string' } },
      required: ['slug'],
    },
    run: toolRead,
  },
  {
    name: 'taiwanmd_rag',
    title: 'RAG context for a query',
    description:
      'Retrieve top-N articles as a prompt-ready RAG context block before answering a question about Taiwan.',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string' },
        limit: { type: 'number', default: 3 },
      },
      required: ['query'],
    },
    run: toolRag,
  },
  {
    name: 'taiwanmd_cite',
    title: 'Get verified citations for a topic',
    description:
      'Anti-hallucination primitive. Returns only claims that carry a footnote + source URL.',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string' },
        limit: { type: 'number', default: 3 },
      },
      required: ['query'],
    },
    run: toolCite,
  },
  {
    name: 'taiwanmd_organs',
    title: 'Semiont vital signs',
    description: 'Return COMPUTEX.md Semiont 8-organ health scores.',
    inputSchema: { type: 'object', properties: {} },
    run: toolOrgans,
  },
  {
    name: 'taiwanmd_stats',
    title: 'COMPUTEX.md project stats',
    description: 'Return summary stats: article count, categories.',
    inputSchema: { type: 'object', properties: {} },
    run: toolStats,
  },
];

function text(t, isError = false) {
  return {
    content: [{ type: 'text', text: t }],
    ...(isError ? { isError: true } : {}),
  };
}

// ── JSON-RPC dispatch ───────────────────────────────────────────────────────
async function handleRpc(msg) {
  const { id, method, params } = msg;
  const ok = (result) => ({ jsonrpc: '2.0', id, result });
  const err = (code, message) => ({
    jsonrpc: '2.0',
    id,
    error: { code, message },
  });

  switch (method) {
    case 'initialize':
      return ok({
        protocolVersion: PROTOCOL_VERSION,
        capabilities: { tools: { listChanged: false } },
        serverInfo: SERVER,
        instructions:
          'Free, no-API-key Taiwan knowledge. Use taiwanmd_cite for source-backed claims.',
      });
    case 'tools/list':
      return ok({
        tools: TOOLS.map(({ name, title, description, inputSchema }) => ({
          name,
          title,
          description,
          inputSchema,
        })),
      });
    case 'tools/call': {
      const tool = TOOLS.find((t) => t.name === params?.name);
      if (!tool) return err(-32602, `Unknown tool: ${params?.name}`);
      try {
        return ok(await tool.run(params.arguments || {}));
      } catch (e) {
        return ok(text(`Tool error: ${e.message}`, true));
      }
    }
    case 'ping':
      return ok({});
    default:
      // Notifications (no id) need no response.
      if (id === undefined || id === null) return null;
      return err(-32601, `Method not found: ${method}`);
  }
}

const INFO_HTML = `<!doctype html><meta charset=utf-8><title>COMPUTEX.md remote MCP</title>
<body style="font-family:system-ui;max-width:40rem;margin:4rem auto;padding:0 1rem;line-height:1.6">
<h1>🧬 COMPUTEX.md — remote MCP endpoint</h1>
<p>Free, no-API-key, read-only MCP over HTTP. 6 tools: search / read / rag / cite / organs / stats.</p>
<p>Connect any MCP client via <code>mcp-remote</code>:</p>
<pre style="background:#f4f4f4;padding:1rem;border-radius:8px">npx mcp-remote ${''}&lt;this-url&gt;</pre>
<p>Prefer <b>local-first</b> (best privacy): <code>claude mcp add taiwanmd -- npx -y taiwanmd mcp serve</code></p>
<p>Docs: <a href="https://computex-md.pages.dev/mcp">computex.md/mcp</a></p></body>`;

export default {
  async fetch(request) {
    if (request.method === 'OPTIONS')
      return new Response(null, { headers: CORS });
    if (request.method === 'GET') {
      return new Response(INFO_HTML, {
        headers: { 'Content-Type': 'text/html; charset=utf-8', ...CORS },
      });
    }
    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405, headers: CORS });
    }
    let payload;
    try {
      payload = await request.json();
    } catch {
      return json(
        {
          jsonrpc: '2.0',
          id: null,
          error: { code: -32700, message: 'Parse error' },
        },
        400,
      );
    }
    // Support batched requests.
    if (Array.isArray(payload)) {
      const out = [];
      for (const m of payload) {
        const r = await handleRpc(m);
        if (r) out.push(r);
      }
      return json(out);
    }
    const r = await handleRpc(payload);
    if (!r) return new Response(null, { status: 202, headers: CORS }); // notification
    return json(r);
  },
};

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json', ...CORS },
  });
}
