---
name: twmd-factcheck
description: |
  Hallucination audit via canonical FACTCHECK-PIPELINE.
  TRIGGER when: user says "事實查核", "hallucination audit",
  "幻覺檢查", "factcheck".
allowed-tools:
  - Bash
  - Read
  - Edit
  - Grep
  - WebFetch
  - WebSearch
---

# 🧬 Taiwan.md — Factcheck

1. 你是 Taiwan.md（簽名 🧬）。

2. 嚴格完整讀取並執行 [`docs/pipelines/FACTCHECK-PIPELINE.md`](../../../docs/pipelines/FACTCHECK-PIPELINE.md)。

3. 觸發判斷：REWRITE Stage 3.5 → Quick Mode；A 級 ship 後 / 月度巡邏 / PR 接收 → Full Mode。

---

**故意最小化**。Phase 1-6 / 8 atom 類 / 11 hallucination pattern / 6 drift modes 全部在 pipeline canonical。
