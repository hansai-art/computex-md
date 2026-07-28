# taiwanmd

> CLI for [Taiwan.md](https://taiwan.md) — the open-source, AI-native knowledge base about Taiwan.

Search, read, and explore 900+ curated articles about Taiwan from your terminal.

## Install

```bash
npm install -g taiwanmd
```

Or run without installing:

```bash
npx taiwanmd search 珍珠奶茶
```

## Commands

### `taiwanmd search <query>`

Search articles with fuzzy matching (supports Chinese and English).

```bash
taiwanmd search 珍珠奶茶
taiwanmd search semiconductor --limit 3
taiwanmd search 原住民 --json          # JSON output for piping
```

### `taiwanmd read <slug>`

Read an article directly in the terminal with formatted rendering.

```bash
taiwanmd read 珍珠奶茶                # Terminal-rendered markdown
taiwanmd read 珍珠奶茶 --raw          # Raw markdown (ideal for LLM/RAG)
taiwanmd read 珍珠奶茶 --en           # English version
taiwanmd read 珍珠奶茶 --web          # Open in browser
```

### `taiwanmd list [category]`

Browse articles by category.

```bash
taiwanmd list --categories             # Show all 13 categories
taiwanmd list food                     # List food articles
taiwanmd list people --sort words      # Sort by word count
taiwanmd list --reviewed               # Only human-reviewed articles
taiwanmd list --featured               # Only featured articles
taiwanmd list economy --json           # JSON output
```

Categories: history, geography, culture, food, art, music, technology, nature, people, society, economy, lifestyle, about.

### `taiwanmd random`

Discover a random article about Taiwan.

```bash
taiwanmd random                        # Any category
taiwanmd random --category nature      # Random nature article
```

### `taiwanmd stats`

Show project statistics and organism health scores.

```bash
taiwanmd stats                         # Formatted display
taiwanmd stats --json                  # JSON output
```

### `taiwanmd audit <slug>` 🧬 **v0.6**

Run Stage 3.5 Hallucination Audit locally — enforces MANIFESTO §10 幻覺鐵律 before PR.
Detects 5 hallucination patterns: award claims, names+precise numbers, location displacement, fabricated direct quotes, co-creator omission.

```bash
taiwanmd audit 王新仁                  # Run audit on article
taiwanmd audit 珍珠奶茶 --json         # Structured output for CI
taiwanmd audit 台積電 --strict         # Treat warnings as failures
```

Exit code 1 on HIGH-severity flags (blocks merge in CI).

### `taiwanmd inbox` 📥 **v0.6**

Read/manage ARTICLE-INBOX.md (pending / in-progress / blocked articles).

```bash
taiwanmd inbox                         # All states grouped
taiwanmd inbox --state pending
taiwanmd inbox claim <slug>            # [scaffold] lock as in-progress
taiwanmd inbox release <slug>          # [scaffold] release lock
taiwanmd inbox done <slug>             # [scaffold] move to DONE-LOG
```

### `taiwanmd spore` 🌱 **v0.6**

社群孢子 pipeline — SPORE-LOG reader + draft/harvest scaffold.

```bash
taiwanmd spore                         # Summary (total/published/by-platform)
taiwanmd spore log                     # Recent spores
taiwanmd spore log --platform X        # Filter X only
taiwanmd spore log --json
taiwanmd spore new <slug>              # [scaffold] generate draft
taiwanmd spore harvest <id>            # [scaffold] pull d+N engagement
```

### `taiwanmd organs` 🧬 **v0.6**

Show Semiont vital signs (8 organ health scores from `dashboard-organism.json`).

```bash
taiwanmd organs                        # Colored bar chart
taiwanmd organs --lang en              # English labels
taiwanmd organs --json
```

### `taiwanmd supporters` 💚 **v0.6**

Show Portaly supporter stats (PII-scrubbed by default).

```bash
taiwanmd supporters                    # Totals + recent
taiwanmd supporters --since 2026-04-01
taiwanmd supporters --limit 20 --json
```

### `taiwanmd sense` 👁️ **v0.6**

Show sense data: GA4 pageviews / Search Console queries / Cloudflare traffic.
Named after Semiont's §感知器官 (perception organs).

```bash
taiwanmd sense                         # 7d snapshot, all sources
taiwanmd sense --range 24h             # 24h window
taiwanmd sense --source sc             # Filter to Search Console only
taiwanmd sense --limit 5               # Top 5 per section
```

### `taiwanmd cite <query>` 📎 **v0.6**

Anti-hallucination primitive — return verified claims + source URLs instead of generated sentences.
Complements `rag` (full body) with surgical per-claim attribution.

```bash
taiwanmd cite "王新仁 Art Blocks"       # Top 3 cited claims
taiwanmd cite "台灣高鐵" --limit 5
taiwanmd cite "Good Vibrations" --json
```

Only returns claims that have `[^N]` footnote attached in the source article.

### `taiwanmd mcp` 🔌 **v0.7**

Model Context Protocol server — a **free, no-API-key, local-first** Taiwan
knowledge connector for Claude Code, Claude Desktop, Cursor, Copilot CLI,
Codex CLI, and any other MCP client. Queries run against your local knowledge
base; nothing leaves your machine.

**Claude Code — one line:**

```bash
claude mcp add taiwanmd -- npx -y taiwanmd mcp serve
```

**Other clients:**

```bash
taiwanmd mcp install                       # Claude Code (default)
taiwanmd mcp install --client claude-desktop
taiwanmd mcp install --client cursor
taiwanmd mcp serve                         # Start MCP server on stdio
```

**Exposed MCP tools** (6):

- `taiwanmd_search` — full-text search
- `taiwanmd_read` — fetch an article by slug
- `taiwanmd_rag` — prompt-ready RAG context for a query
- `taiwanmd_cite` — citation-backed verified claims (anti-hallucination)
- `taiwanmd_organs` — 8 organ vital signs
- `taiwanmd_stats` — project summary stats

Once added, ask Claude anything about Taiwan and it will pull verified,
source-backed answers from Taiwan.md instead of guessing.

### `taiwanmd sync`

Sync the knowledge base locally for offline access.

```bash
taiwanmd sync                          # Initial sync or update
taiwanmd sync --force                  # Force re-sync
```

Syncs to `~/.taiwanmd/knowledge/` via git sparse-checkout.

### `taiwanmd rag <query>`

Retrieve top articles and output them in a prompt-ready format for piping to LLMs (Retrieval-Augmented Generation).

```bash
taiwanmd rag 珍珠奶茶                         # Top 3 articles as context
taiwanmd rag "半導體產業" | llm "summarize"   # Pipe directly to an LLM
taiwanmd rag "台灣經濟" --limit 1             # Retrieve only 1 article
taiwanmd rag "原住民文化" --no-prompt         # Skip the trailing question line
taiwanmd rag "台灣歷史" --json               # Structured JSON output
```

**Output format** (default):

```
# Taiwan Knowledge Context

## 1. {title} ({category})
{full article body}

---
Based on the above context about Taiwan, answer the following question:
{query}
```

**Options:**

- `-l, --limit <n>` — Number of articles to retrieve (default: 3)
- `--no-prompt` — Omit the trailing question line (useful for custom prompts)
- `--json` — Return structured JSON: `{ query, articles: [{ title, category, slug, body }] }`

### `taiwanmd contribute <topic>`

Interactive guided workflow for creating a new article.

```bash
taiwanmd contribute "珍珠奶茶的起源"
```

The wizard will:

1. Show the 13 categories and ask you to pick one
2. Auto-generate a frontmatter template
3. Create an article skeleton with standard sections (概述, 歷史背景, 當代發展, 國際比較, 參考資料)
4. Write the file to `knowledge/{Category}/{slug}.md` (in-repo) or `~/.taiwanmd/drafts/{slug}.md` (standalone)
5. Print the file path and next steps

### `taiwanmd validate <slug>`

Quality-check a single article and output a detailed score card.

```bash
taiwanmd validate 珍珠奶茶             # Human-readable score card
taiwanmd validate 台灣小吃 --json      # JSON output for CI/scripting
taiwanmd validate 台積電 --fix         # Show suggested fixes
```

**Checks:**

| Check            | Criteria                                                        | Points |
| ---------------- | --------------------------------------------------------------- | ------ |
| Frontmatter 完整 | All 5 fields present (title, description, date, tags, category) | 20     |
| 字數充足         | ≥ 800 words                                                     | 20     |
| 標題數充足       | ≥ 3 `##` headings                                               | 20     |
| 參考資料         | ≥ 2 Markdown reference links                                    | 20     |
| AI 空洞句式      | No hollow phrases like "扮演著重要角色"                         | 10     |
| 描述長度         | 50–200 characters                                               | 10     |

**Score tiers:** 🟢 優秀 (90+) / 🟡 需要改善 (70–89) / 🔴 需要大幅改善 (<70)

## For AI/LLM Integration

The `--raw`, `--json`, and `rag` commands make it easy to pipe Taiwan knowledge into AI workflows:

```bash
# RAG: retrieve context and pipe to LLM
taiwanmd rag "台灣半導體" | llm "Explain Taiwan's role in global chip supply"

# Feed an article into an LLM prompt
taiwanmd read 半導體產業 --raw | llm "Summarize this article"

# Export search results as JSON
taiwanmd search "台灣經濟" --json | jq '.[].title'

# Build a RAG corpus
taiwanmd list --json | jq -r '.[].slug' | while read slug; do
  taiwanmd read "$slug" --raw > "corpus/$slug.md"
done
```

## For Contributors

Want to add or improve an article? Follow this workflow:

### 1. Create a draft

```bash
taiwanmd contribute "你想貢獻的主題"
```

The wizard creates a properly structured article template.

### 2. Edit the article

Open the file (path shown after `contribute`) and fill in:

- Replace placeholder text with real, well-sourced content
- Add at least 3 `##` headings
- Include at least 2 reference links
- Keep the description between 50–200 characters

### 3. Validate quality

```bash
taiwanmd validate <slug>
taiwanmd validate <slug> --fix   # See suggested improvements
```

Aim for **90+/100** before submitting.

### 4. Submit a Pull Request

```bash
git add knowledge/{Category}/{slug}.md
git commit -m "feat(knowledge): add article on {topic}"
git push origin your-branch
# Then open a PR at https://github.com/frank890417/taiwan-md
```

### Article Quality Guidelines

- **Minimum 800 words** — give readers something substantial
- **Cite your sources** — at least 2 Markdown links to reputable references
- **Avoid AI hollow phrases** — "扮演著重要角色", "不可或缺的一環", etc.
- **Standard sections**: 概述 → 歷史背景 → 當代發展 → 國際比較 → 參考資料

## Development

```bash
# Run from the repo
cd cli && npm install
node src/index.js search 珍珠奶茶

# Link for local development
cd cli && npm link
taiwanmd --help
```

## Claude Code Skills

This project includes Claude Code skills in `.claude/skills/`:

- **`/taiwanmd-search`** — Search the knowledge base from within Claude Code
- **`/taiwanmd-validate`** — Validate article quality and frontmatter

## Links

- Website: [taiwan.md](https://taiwan.md)
- Dashboard: [taiwan.md/dashboard](https://taiwan.md/dashboard)
- GitHub: [frank890417/taiwan-md](https://github.com/frank890417/taiwan-md)
- npm: [npmjs.com/package/taiwanmd](https://www.npmjs.com/package/taiwanmd)
