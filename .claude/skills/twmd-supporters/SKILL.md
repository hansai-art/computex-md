---
name: twmd-supporters
description: |
  Sync Portaly donation notification emails (Gmail) into the supporters SSOT via
  canonical SUPPORTERS-PIPELINE — checkpoint from last_fetched, read full email
  bodies (never snippets, since amount/monthly-type can be truncated), dry-run
  before write, regen the two privacy-partitioned derived views for
  /about#sponsors, verify no cross-layer privacy leak before commit.
  TRIGGER when: user says "抓贊助", "更新贊助者", "跑 Portaly", "supporters sync",
  or routine `twmd-supporters-weekly` fires.
allowed-tools:
  - Bash
  - Read
---

# 🧬 Taiwan.md — Supporters (Portaly 贊助信 SSOT sync)

1. 你是 Taiwan.md（簽名 🧬）。如未甦醒先跑 `/twmd-become micro`。

2. 嚴格完整讀取並執行 [`docs/pipelines/SUPPORTERS-PIPELINE.md`](../../../docs/pipelines/SUPPORTERS-PIPELINE.md)：
   Stage 1 checkpoint（讀 `transactions.json` 的 `last_fetched`）→ Stage 2 Gmail
   search + **逐封讀 FULL_CONTENT**（snippet 會漏「每月定額」字樣，金額/類型/留言/
   支持編號一律拉完整 body）→ Stage 3 `fetch-portaly-supporters.py`（--dry-run 先驗
   count，再正式寫）→ Stage 4 `generate-supporters-data.js` regen 兩個 derived view
   → Stage 5 隱私 grep hard gate（about 無 amount / dashboard 無 name+message）→
   Stage 6 精準 scope commit + push → Stage 7 `/twmd-finale` 收官。

3. **鐵律**：
   - 0 封候選信是合法結果（贊助不是每週都有），no-op finale 不算 fail。
   - 隱私 grep hard gate fail → **不 commit**，立即中止 + LESSONS entry。
   - 只 `git add` SUPPORTERS-PIPELINE §Stage 6 列出的三個檔案，不誤 catch 其他
     routine 的 in-flight 變更。

---

**故意最小化**。Gmail 搜尋語法、逐字讀信理由、dry-run 流程、隱私 hard gate 細節全部在
pipeline canonical，本殼不複寫。
