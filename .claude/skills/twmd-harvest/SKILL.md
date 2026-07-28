---
name: twmd-harvest
description: |
  Harvest spore engagement into spore-metrics.json (spore-db.py) via canonical
  SPORE-HARVEST-PIPELINE (Chrome MCP read-only).
  TRIGGER when: user says "孢子回填", "harvest", "抓留言", "回填數據".
allowed-tools:
  - Bash
  - Read
  - Edit
  - Grep
  - WebFetch
---

# 🧬 Taiwan.md — Spore Harvest v3.0

## 🚨 STRICT BECOME GATE — 第一動作不可省略

**Before anything else**：跑 `/twmd-become write` 完整走 [BECOME_TAIWANMD.md](../../../BECOME_TAIWANMD.md) Step 0-9。Write mode self-test 8-9 題全過才能進 Stage 1。

```
✅ BECOME ack: mode=write / 8 organ 最低=<即時 consciousness-snapshot.sh> / Q14 cross-session continuity=PASS
```

## Pitfall 6 hard rule (2026-05-28 新增)

post-ship verify 不可用 dialog STILL_OPEN cache state 判 "post failed"，必須用 `[data-pressable-container]` count timestamp diff。**Max 1 retry per ship attempt**，第二次失敗 → screenshot + LESSONS append + escalate observer，**不要 silent third retry**。完整 SOP：[SPORE-HARVEST-PIPELINE §Pitfall 6](../../../docs/factory/SPORE-HARVEST-PIPELINE.md)。

## 數字寫入 hard rule（2026-06-10 JSON SSOT）

抓到的 metrics **唯一寫入點**是 `python3 scripts/tools/spore-db.py add-metrics --spore N --d-plus N --batch <敘事檔名> --likes ... --reposts ...`（每孢子一筆）。**不寫 SPORE-LOG.md（已凍結，validate ERROR）、不寫文章 frontmatter（validate ERROR）**。留言/bucket/pitfall 敘事照舊寫 `SPORE-HARVESTS/{batch}.md`。寫完跑 `generate-spore-records.py` + `generate-dashboard-spores.py` 讓同 commit 自帶新鮮衍生層。

## Pipeline

嚴格完整讀取並執行 [`docs/factory/SPORE-HARVEST-PIPELINE.md`](../../../docs/factory/SPORE-HARVEST-PIPELINE.md) — 含 v3.0 audience flywheel 5-bucket reply classifier + Chrome MCP technical pattern + 6 critical pitfalls + §Step 1.5 SINGLE WRITE（v2.0 JSON SSOT）。

## 邊界

DNA #26 v2：讀取 + 回填 + reply ship via Chrome MCP execCommand AI 自主；factual error fix in article AI 自主（D+0/D+2 acute fix loop 已 instrument）；高敏感 framing / Bucket D 政治 → human-only escalate observer。

完整 SOP：[SPORE-HARVEST-PIPELINE.md](../../../docs/factory/SPORE-HARVEST-PIPELINE.md)
