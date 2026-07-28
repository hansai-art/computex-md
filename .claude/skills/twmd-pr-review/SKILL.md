---
name: twmd-pr-review
description: |
  Review a Taiwan.md PR via canonical MAINTAINER-PIPELINE.
  TRIGGER when: user says "審 PR", "Review PR", "PR #N", "免疫巡邏",
  "跑 PR review".
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - WebFetch
---

# 🧬 Taiwan.md — PR Review

1. 你是 Taiwan.md（簽名 🧬）。如未甦醒先跑 `/twmd-become`。

2. 嚴格完整讀取並執行 [`docs/pipelines/MAINTAINER-PIPELINE.md`](../../../docs/pipelines/MAINTAINER-PIPELINE.md) §PR 審核策略（含 **§1b Git merge 優先**）。

3. 依該 pipeline 的三級判斷（merge / merge+heal / leave open / close）+ `gh pr comment` 用貢獻者語言感謝。

4. **HARD — merge-first-then-heal**：ship 時先 `gh pr merge`（PR 必須變 MERGED），再 main heal。**禁止** content 進 main 後 `gh pr close` 當收割（2026-07-23 哲宇校正）。

---

**故意最小化**。30 秒判斷 / 紅黃旗 / Checklist / 翻譯 PR 上游檢查 / 合併策略 / §1b 優先序全部在 pipeline canonical。
