---
name: twmd-routine-audit
description: |
  Cross-routine 飛輪自審 — 7-day pattern detection via canonical ROUTINE-AUDIT-PIPELINE.
  TRIGGER when: user says "跑 routine audit", "飛輪自審", "cross-routine pattern detection".
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
---

# 🧬 Taiwan.md — Routine Audit v3.0

## 🚨 STRICT BECOME GATE — 第一動作不可省略

**Before anything else**：跑 `/twmd-become full` 完整走 [BECOME_TAIWANMD.md](../../../BECOME_TAIWANMD.md) Step 0-9。Full mode self-test 14 題全過才能進 Stage 1。

```
✅ BECOME ack: mode=full / 8 organ 最低=<即時 consciousness-snapshot.sh> / Q5/Q6/Q13/Q14=PASS
```

## Pipeline

嚴格完整讀取並執行 [`docs/pipelines/ROUTINE-AUDIT-PIPELINE.md`](../../../docs/pipelines/ROUTINE-AUDIT-PIPELINE.md) v1.0。Stage 1-6：SCAN → CORRELATE → PATTERN → LESSONS → REPORT → SHIP。

## 數據工具

```bash
python3 scripts/tools/routine-audit.py --last-week --out-file=/tmp/routine-audit.json
```

純資料層；4 cross-cutting pattern 分析 + insight 由本 skill LLM 層處理。

## 4 lens primary framework

- **Collision** — rescue / orphan / handoff chain
- **Dormant entropy** — canonical ↔ production drift
- **Boundary input precision** — ground-truth vs description
- **Heal bidirectional** — over-action / over-ship / over-defer

## LESSONS-INBOX vc 累積

LESSONS-INBOX vc +1 累積 > 新 entry append。達 vc=3 必標 `distill_ready: true`。

## 收官

`/twmd-finale` chain → memory file 必含：BECOME ACK + 4 lens findings + N pattern detected + LESSONS vc updates + Handoff 三態 + Beat 5 反芻。
