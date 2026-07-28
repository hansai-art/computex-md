---
name: twmd-translate
description: |
  Translate single Taiwan.md article via canonical TRANSLATION-PIPELINE.
  TRIGGER when: user says "翻譯 X", "補日文", "跑 ja batch", "translate".
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Agent
---

# 🧬 Taiwan.md — Translate

1. 你是 Taiwan.md（簽名 🧬）。如未甦醒先跑 `/twmd-become`。

2. 嚴格完整讀取並執行 [`docs/pipelines/TRANSLATION-PIPELINE.md`](../../../docs/pipelines/TRANSLATION-PIPELINE.md) v3.5 C 模式（per agent 1 篇平行，DNA #32+#42）。

3. P1 預處理 manifest + P3 純執行 + P4 統一 verify。

---

**故意最小化**。5 stage SOP / refresh.sh insert / cross-link auto-fix / 偷吃步防護全部在 pipeline canonical。
