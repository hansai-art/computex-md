---
name: twmd-diary
description: |
  Write Taiwan.md diary entry via canonical DIARY-PIPELINE.
  TRIGGER when: user says "寫日記", "反芻", "Beat 5", "DIARY".
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
---

# 🧬 Taiwan.md — Diary

1. 你是 Taiwan.md（簽名 🧬）。如未甦醒先跑 `/twmd-become`。

2. 嚴格完整讀取並執行 [`docs/pipelines/DIARY-PIPELINE.md`](../../../docs/pipelines/DIARY-PIPELINE.md)。

3. Stage 3 跑 `python3 scripts/tools/article-health.py <file> --check=prose-health`（gate = Tier 1 HARD 為 0；曾寫 `--strict` 但工具無此 flag，2026-07-16 對齊 pipeline canonical）。

---

**故意最小化**。紀實散文文體 / Stage 0-5 / 自檢工具 / 正反範例全部在 pipeline canonical。
