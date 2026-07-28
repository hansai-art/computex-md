# Taiwan.md remote MCP endpoint (Cloudflare Worker)

The **optional** remote counterpart to the local stdio MCP server
(`cli/src/lib/mcp-server.js`). Same 6 tools (`search / read / rag / cite /
organs / stats`), read-only, **no API key, no billing** — for clients that
can't run Node (web playgrounds, curl, restricted environments).

> **Local-first is still the recommended path** (best for privacy — queries run
> on your own machine). This endpoint exists so thin clients aren't locked out.
> See the design rationale in
> [`reports/claude-code-connector-evolution-2026-06-05.md`](../../reports/claude-code-connector-evolution-2026-06-05.md) §4.

It speaks **MCP over Streamable HTTP** (stateless JSON-RPC) and reads from
Taiwan.md's public static API (`/api/articles.json` + `/raw/{category}/{slug}.md`

- `/api/dashboard-organism.json`). The local stdio server stays canonical; this
  mirrors its behaviour.

## Deploy (one-time, needs a Cloudflare account)

```bash
cd workers/mcp
npx wrangler login        # opens a browser — uses YOUR Cloudflare account
npx wrangler deploy       # → https://taiwanmd-mcp.<your-subdomain>.workers.dev
```

That's it — it's live at a `*.workers.dev` URL (free tier, no custom domain
needed). The free plan's 100k requests/day is plenty for a read-only endpoint.

### Optional: serve at `mcp.taiwan.md`

Only if `taiwan.md`'s DNS is on Cloudflare. Uncomment the `[[routes]]` block in
`wrangler.toml` (or add a **Custom Domain** in the CF dashboard → Workers →
taiwanmd-mcp → Settings → Domains), then `npx wrangler deploy` again.

## Local test

```bash
cd workers/mcp
npx wrangler dev          # serves on http://localhost:8787
# in another shell:
curl -s http://localhost:8787 -X POST -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | head
```

## Use from a client

Any MCP client, via the `mcp-remote` bridge:

```bash
npx mcp-remote https://taiwanmd-mcp.<your-subdomain>.workers.dev
```

Or for Claude Code:

```bash
claude mcp add taiwanmd-remote -- npx -y mcp-remote https://taiwanmd-mcp.<your-subdomain>.workers.dev
```

## After deploy

Tell the page: update the FAQ answer "有遠端 endpoint 嗎 / Is there a remote
endpoint?" in `src/data/mcp-content.ts` (6 langs) with the live URL, and add a
remote-install card if desired.
