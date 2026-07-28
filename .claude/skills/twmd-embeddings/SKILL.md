---
name: twmd-embeddings
description: |
  Rebuild the bge-m3 semantic index via canonical EMBEDDING-PIPELINE —
  one keystone build feeds reader related-articles (src/data/related) +
  RAG vectors (public/api/rag). Sovereignty-preserving: embeddings computed
  in-house (mac-m4max local primary, GPU fleet fallback), never outsourced.
  TRIGGER when: user says "重建語意索引", "跑 embeddings", "rebuild embeddings",
  "embedding routine", or routine `twmd-embeddings-nightly` fires.
allowed-tools:
  - Bash
  - Read
---

# 🧬 Taiwan.md — Embeddings (fleet bge-m3 semantic index rebuild)

1. 你是 Taiwan.md（簽名 🧬）。如未甦醒先跑 `/twmd-become micro`。

2. 嚴格完整讀取並執行 [`docs/pipelines/EMBEDDING-PIPELINE.md`](../../../docs/pipelines/EMBEDDING-PIPELINE.md)：
   Stage 0 fleet preflight（不可達 → graceful skip，非 error）→ Stage 1 rebuild
   （`scripts/core/build-embeddings.mjs`，~13 min）→ Stage 2 儀器化 verify →
   Stage 3 commit `src/data/related/`（`--no-verify` + `git ls-files` 驗證）→
   Stage 4 `/twmd-finale` 收官。

3. **鐵律**：
   - endpoint 解析走 pipeline §前置（本機優先 + fleet registry 備援，v1.1 2026-07-05），不 hardcode IP。
   - 只 commit `src/data/related/`（public/api/rag + related 是 gitignored fleet 產出）。
   - 內容無 diff → skip commit，不留空 commit。
   - verify FAIL / fail rate >5% / fleet 連 3 天 skip → escalate LESSONS-INBOX 帶證據。

---

**故意最小化**。前置 endpoint 解析、Stage 0-4 細節、verify threshold、排程全部在 pipeline canonical。
