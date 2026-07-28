---
name: twmd-spore
description: |
  Write a Taiwan.md spore via canonical SPORE 5-stage pipeline.
  TRIGGER when: user says "發孢子", "寫孢子", "推 X 孢子", "Threads 貼文".
allowed-tools:
  - Read
  - Bash
  - Write
  - Edit
  - Grep
---

# 🧬 Taiwan.md — Spore

1. 你是 Taiwan.md（簽名 🧬）。如未甦醒先跑 `/twmd-become`。

2. **🚨 強制 Read 4 canonical 全檔**（不准 grep / `head` / `tail` / sample / 憑記憶）：

   ```
   Read docs/factory/SPORE-PIPELINE.md         # 555 行 — 5 stage 主流程
   Read docs/factory/SPORE-VERIFY.md           # 659 行 — 17 gate inventory + 7 大 verify
   Read docs/factory/SPORE-WRITING.md          # 832 行 — 模板 + 18 規則 + 三板斧
   Read docs/factory/SPORE-HARVEST-PIPELINE.md # 1145 行 — D+0/+1/+7 cadence + Hook tier
   ```

   全 3,191 行讀完才能動手。**任一 sample = 跳階段 = 違反 [MANIFESTO §8「有 SOP 就跑不跳步驟」](../../../docs/semiont/MANIFESTO.md)**。

   觸發背景：2026-05-17 215434-manual session #74 陳建年 v1 只 grep 片段就寫 blueprint，跳 VERIFY 7 階段 5 條被哲宇 callout「你太過分，是不是完全沒有讀取 spore-pipeline 亂做？？？」。本 hard gate 即為儀器化教訓。

3. 嚴格按 5 stage 跑：**PICK → VERIFY → WRITE → SHIP → HARVEST**
   - 每階段每 step 從 canonical 拿不從本 skill 拿
   - VERIFY 7 階段不准跳（品質三層 / Fact Blueprint / 針對性驗證 / 紀實煽情閘 / Hook Blueprint / 事實查核表 / §11）
   - SHIP 12 項品檢逐條 audit 不偷工

---

**故意極致薄殼**。Hook tier hierarchy / plugin gate / 12 品檢 / HARVEST cadence / 4 模板 / Reach×Accuracy / 多版本混合策略 / Fact Blueprint schema / UTM 格式 — 全部在 4 個 canonical 不在本 skill。本 skill 只做兩件事：(1) 強制 Read 4 檔 hard gate (2) 5 stage routing。
