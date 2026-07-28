# Taiwan.md Connector

> Free, open-source, **local-first** Taiwan knowledge for your AI.
> No API key. No account. No billing. Your queries never leave your machine.

Taiwan.md is an open-source, AI-native knowledge base about Taiwan — 900+
curated, citation-backed articles across 13 categories. This connector exposes
it over the **Model Context Protocol (MCP)** so Claude Code, Claude Desktop,
Cursor, Copilot CLI, Codex CLI, and any other MCP client can search, read, and
**cite** verified articles about Taiwan instead of guessing.

---

## Why this exists

When you ask an AI about Taiwan, you get whatever the base model happened to
absorb — often vague, sometimes wrong, sometimes silently reframed. This
connector puts **Taiwan's own first-person, source-backed voice** one tool call
away. The `taiwanmd_cite` tool returns _only_ claims that carry a real footnote
and source URL, so anything you write about Taiwan can be traced back to a
source.

It is deliberately the opposite of a commercial data gateway:

|                   | Taiwan.md Connector               | Typical commercial MCP gateway |
| ----------------- | --------------------------------- | ------------------------------ |
| Price             | Free                              | Paid / metered                 |
| API key           | None                              | Required                       |
| Where queries run | Your machine (stdio)              | Their servers                  |
| Source            | Open (MIT code, CC BY-SA content) | Closed                         |

---

## Install

### Claude Code (one line)

```bash
claude mcp add taiwanmd -- npx -y taiwanmd mcp serve
```

That's it. Ask Claude anything about Taiwan and it will use the tools below.

### Claude Desktop (one-click bundle)

1. Download `taiwanmd.mcpb`.
2. Double-click it. Claude Desktop installs it.
3. Done — no API key prompt, because there is no API key.

> Or add it manually to
> `~/Library/Application Support/Claude/claude_desktop_config.json`:
>
> ```json
> {
>   "mcpServers": {
>     "taiwanmd": {
>       "command": "npx",
>       "args": ["-y", "taiwanmd", "mcp", "serve"]
>     }
>   }
> }
> ```

### Cursor

Settings → MCP → add a server:

```
command: npx
args: ["-y", "taiwanmd", "mcp", "serve"]
```

### Copilot CLI / Codex CLI / Cline / Continue / any MCP client

Point the client at the stdio command:

```
npx -y taiwanmd mcp serve
```

You can always print the right snippet with:

```bash
npx -y taiwanmd mcp install --client claude-code   # or claude-desktop, cursor
```

---

## Tools

| Tool              | What it does                                                     |
| ----------------- | ---------------------------------------------------------------- |
| `taiwanmd_search` | Full-text search across 900+ articles (Chinese or English)       |
| `taiwanmd_read`   | Read the full body of an article by slug                         |
| `taiwanmd_rag`    | Top-N articles as a prompt-ready RAG context block               |
| `taiwanmd_cite`   | **Anti-hallucination**: only claims with a footnote + source URL |
| `taiwanmd_organs` | Taiwan.md Semiont 8-organ health scores                          |
| `taiwanmd_stats`  | Article count, categories, timestamps                            |

---

## How it works (and your privacy)

- The server runs **locally over stdio** — it is a process on your machine, not
  a remote service. Your questions are not sent to any Taiwan.md server.
- On first use, the knowledge base auto-syncs to `~/.taiwanmd/` (a one-time
  download). After that it's local and fast. The server pre-warms this on
  startup so your first query isn't slow.
- Inside the Taiwan.md repo, it reads `knowledge/` directly.
- Content is CC BY-SA 4.0; the CLI/connector code is MIT.

A remote endpoint is live at `https://mcp.taiwan.md` for thin clients that
can't run Node (web playgrounds, curl, restricted environments). It is an
**optional** convenience; local-first stays the recommended path because your
queries never leave your machine.

```bash
claude mcp add taiwanmd-remote -- npx -y mcp-remote https://mcp.taiwan.md
```

It serves the same six tools, read-only, no API key, reading from Taiwan.md's
public static API.

---

## Troubleshooting

- **First query is slow** — the one-time knowledge sync is running. Subsequent
  queries are fast.
- **`npx` not found** — install Node.js ≥ 18 (which ships `npx`).
- **Want to pin a version** — use `npx -y taiwanmd@0.7 mcp serve`.

---

## For maintainers: build the one-click bundle

```bash
cli/scripts/build-mcpb.sh        # → cli/dist/taiwanmd.mcpb
```

The bundle (`cli/mcpb/`) is a thin wrapper that runs `npx -y taiwanmd@latest
mcp serve`, so it stays tiny and always pulls the latest published server.
Before a public release, validate the manifest with the official packer:

```bash
npx @anthropic-ai/mcpb pack cli/mcpb cli/dist/taiwanmd.mcpb
```

---

🧬 Part of [Taiwan.md](https://taiwan.md) — the open-source knowledge organism about Taiwan.
