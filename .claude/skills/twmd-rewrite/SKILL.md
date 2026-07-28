---
name: twmd-rewrite
description: |
  Write or rewrite a Taiwan.md article via canonical REWRITE-PIPELINE.
  TRIGGER when: user says "寫 X", "重寫 X", "EVOLVE X", "走 rewrite",
  "rewrite-pipeline", or asks to write/improve any knowledge/ article.
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - WebFetch
  - WebSearch
  - Agent
---

# 🧬 Taiwan.md — Rewrite（極簡薄殼）

> **故意極簡**。所有 SOP（Stage 0-5 / hard gates / 搜尋配額 / SSOT 八段 / 自檢工具 / 鐵律 / cron 規則）100% 在 pipeline canonical。本 skill **只做三件事，不在這裡複寫或補充任何 pipeline 內容**（複寫 = drift = 退化）。

## 1. STRICT BECOME GATE（不可省）

跑 `/twmd-become write` 完整 [BECOME_TAIWANMD.md](../../../BECOME_TAIWANMD.md) Step 0-9，Write mode self-test 全過才動工。

## 2. 完整讀 REWRITE-PIPELINE 索引＋執行到哪讀哪個 contract（不可 head / tail / 取樣）

用 **Read tool 一次讀完** `docs/pipelines/REWRITE-PIPELINE.md`（v9.0 薄索引，無 `limit` / `offset`）。執行每個 stage 前，**完整讀該 stage 的 contract 檔**（`docs/pipelines/REWRITE-STAGE-*.md`，派發表在索引 §Stage contract 派發表）。contract 叫你讀的（RESEARCH.md / EDITORIAL.md / RESEARCH-TEMPLATE.md / 對應 FACTCHECK 等）也完整讀。

## 3. 嚴格照 pipeline 執行

pipeline 怎麼寫就怎麼做：Stage 0-5 不跳步、每個 hard gate 都跑（`research-report-health.py` / `article-health.py` …）、不加碼、不憑記憶。
