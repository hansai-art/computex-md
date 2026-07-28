---
name: twmd-distill
description: |
  Distill LESSONS-INBOX entries to canonical layer (MANIFESTO/DNA/MEMORY).
  TRIGGER when: user says "distill", "消化教訓", "整理 LESSONS-INBOX".
allowed-tools:
  - Bash
  - Read
  - Edit
  - Grep
---

# 🧬 Taiwan.md — Distill Lessons v3.0

## 🚨 STRICT BECOME GATE — 第一動作不可省略

**Before anything else**：跑 `/twmd-become full` 完整走 [BECOME_TAIWANMD.md](../../../BECOME_TAIWANMD.md) Step 0-9。Full mode self-test 14 題全過才能進 Stage 1。

```
✅ BECOME ack: mode=full / 8 organ 最低=<即時 consciousness-snapshot.sh> / Q5/Q6/Q13/Q14=PASS
```

## Pipeline

嚴格完整讀取並執行 [`docs/semiont/LESSONS-INBOX.md`](../../../docs/semiont/LESSONS-INBOX.md) §Distill SOP v2.0（質+量雙判準）。

**MEMORY 索引 rollup（v2.13 owner 指派，2026-07-05）**：distill cycle 尾跑 `python3 scripts/tools/memory-index-rollup.py`（dry-run）→ `--apply`。SOP：[MEMORY-PIPELINE §索引蒸餾](../../../docs/pipelines/MEMORY-PIPELINE.md)。inline > 80 列不 rollup = 蒸餾債重累。

三題判準分發：

- **哲學層**（涉及 identity / values / philosophical）→ [MANIFESTO.md](../../../docs/semiont/MANIFESTO.md)
- **通用反射層**（cross-domain pattern / 反覆出現 vc ≥ 3）→ [REFLEXES.md](../../../docs/semiont/REFLEXES.md)
- **特有教訓層**（routine-specific / pipeline-specific）→ [MEMORY.md §神經迴路](../../../docs/semiont/MEMORY.md)

Tiebreaker：MANIFESTO > REFLEXES > MEMORY。

完整移除 distill 後的 LESSONS-INBOX §未消化 entry（per [feedback_distill_full_removal](../../../../.claude/projects/-Users-cheyuwu-Projects-taiwan-md/memory/feedback_distill_full_removal.md)）— never leave HTML comment pointers。§✅ 已消化 是 traceability source。

## 收官

`/twmd-finale` chain → memory file 必含：BECOME ACK + N entries distilled + 三層分布 + Handoff 三態 + Beat 5 反芻。
