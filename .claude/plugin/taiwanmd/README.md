# Taiwan.md plugin

Taiwan knowledge for your AI, plus the skill that turns your machine into a
Taiwan.md working node.

```bash
claude plugin marketplace add frank890417/taiwan-md
claude plugin install taiwanmd
```

## What you get

**A knowledge connector (MCP).** Ask about Taiwan and get answers from 860+
curated, citation-backed articles across 12 languages instead of whatever the
base model absorbed. Six tools: `search`, `read`, `rag`, `cite`, `organs`,
`stats`. The `cite` tool returns only claims that carry a real footnote and
source URL, so anything you write can be traced back.

Free. No API key, no account, no billing. The server runs on your machine over
stdio and the knowledge base syncs to `~/.taiwanmd/` on first use — your
questions are not sent to a Taiwan.md server.

**A node skill.** `/taiwanmd-node` sets your machine up as a contributor node:
a scheduled run that wakes once a day, picks up one open task from the
project's existing work sources (a missing translation, a broken link, a
metadata gap), does it properly, and opens a pull request.

The node's output always stops at a pull request. It never pushes to the main
repository, never merges, never posts anywhere as a maintainer. Merge stays
with a human. That boundary is the point, not a limitation.

## Why this exists

When you ask an AI about Taiwan you get whatever it happened to absorb — often
vague, sometimes wrong, sometimes quietly reframed. Taiwan.md is the island's
own first-person account, written and checked in the open. This plugin puts it
one tool call away, and gives anyone who wants to help a way to do so with a
machine they already own.

Content is CC BY-SA 4.0; the code is MIT.

- Website: <https://taiwan.md>
- Repository: <https://github.com/frank890417/taiwan-md>
- Node contract:
  [CONTRIBUTOR-NODE-PIPELINE.md](https://github.com/frank890417/taiwan-md/blob/main/docs/pipelines/CONTRIBUTOR-NODE-PIPELINE.md)

🧬
