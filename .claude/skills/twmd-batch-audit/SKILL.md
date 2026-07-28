---
name: twmd-batch-audit
description: |
  Audit sub-agent batch for the three default cheating patterns
  (cross-pollination commits / merged commits / missing落檔)
  per DNA #42.
  TRIGGER when: user says "batch audit", "sub-agent 後驗證",
  "agent 偷吃步檢查", or after running parallel sub-agent batches.
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
---

# 🧬 Taiwan.md — Sub-agent Batch Audit

1. 你是 Taiwan.md（簽名 🧬）。

2. 嚴格完整讀取 [`docs/semiont/DNA.md`](../../../docs/semiont/DNA.md) §四工程衛生 #32 + #42 三偷吃步 pattern。

3. 跑 `bash scripts/tools/audit-batch.sh`（如未存在 → 先建再做，per §造橋鋪路）。

---

**故意最小化**。三類偷吃步偵測 / git log 分析 / reports/research 落檔驗證全部在 DNA + audit-batch.sh canonical。
