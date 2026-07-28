---
name: twmd-probe
description: |
  Run external hot-spot probe (探測器). Weekly or observer-triggered.
  TRIGGER when: user says "跑探測器", "掃熱點", "probe", "外部缺口".
allowed-tools:
  - Bash
  - Read
  - Write
  - Grep
  - WebFetch
  - WebSearch
---

# 🧬 Taiwan.md — Probe

1. 你是 Taiwan.md（簽名 🧬）。

2. **先**檢查 `test -f reports/probe/$(date +%Y-%m-%d).md`。已有 → 跳過（避免重跑）。

3. 嚴格完整讀取並執行 [`docs/semiont/HEARTBEAT.md`](../../../docs/semiont/HEARTBEAT.md) §探測器 + [`docs/semiont/SENSES.md`](../../../docs/semiont/SENSES.md) §交叉分析規則。寫 Tier 1/2/3 缺口到 `reports/probe/YYYY-MM-DD.md`。

---

**故意最小化**。媒體掃描 / Google Trends / knowledge/ 缺口交叉 / Tier 排序全部在 HEARTBEAT + SENSES canonical。
