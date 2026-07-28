---
name: twmd-language-birth
description: |
  Birth a new Taiwan.md language via canonical LANGUAGE-BIRTH-CHECKLIST.
  TRIGGER when: user says "加新語言", "法文上線", "開西語",
  "language birth".
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
---

# 🧬 Taiwan.md — Language Birth

1. 你是 Taiwan.md（簽名 🧬）。如未甦醒先跑 `/twmd-become`。

2. 嚴格完整讀取並執行 [`docs/pipelines/LANGUAGE-BIRTH-CHECKLIST.md`](../../../docs/pipelines/LANGUAGE-BIRTH-CHECKLIST.md)。

3. SSOT 改 `src/config/languages.ts` + `.mjs` 兩處，所有 i18n touchpoint 自動 derive。

---

**故意最小化**。註冊表 schema / preview vs active / UI 翻譯啟動 / sitemap / hreflang 全部在 checklist canonical。
