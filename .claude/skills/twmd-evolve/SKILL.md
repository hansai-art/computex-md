---
name: twmd-evolve
description: |
  Evolution via canonical EVOLVE-PIPELINE — data-driven content evolution
  (v1/v2), pipeline self-refactor (Mode 3), goal-driven design evolution
  (Mode 4: 思考→發散→報告→實作).
  TRIGGER when: user says "跑 EVOLVE", "數據驅動進化", "evolve-pipeline",
  "進化 X pipeline 本身", "設計 X（技能/器官）", "深度思考自我進化",
  "寫實作報告後實作".
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - Agent
  - WebFetch
  - WebSearch
---

# 🧬 Taiwan.md — Evolve v4.0

## 🚨 STRICT BECOME GATE — 第一動作不可省略

**Before anything else**：跑 `/twmd-become full` 完整走 [BECOME_TAIWANMD.md](../../../BECOME_TAIWANMD.md) Step 0-9。Full mode self-test 14 題全過才能進 Stage 1。

```
✅ BECOME ack: mode=full / 8 organ 最低=<即時 consciousness-snapshot.sh> / Q5/Q6/Q13/Q14=PASS
```

## Mode 分流（判定寫進 ACK，判準 canonical 在 pipeline）

| 觸發語                                                             | Mode                                        |
| ------------------------------------------------------------------ | ------------------------------------------- |
| 「跑 EVOLVE」「數據驅動進化」/ twmd-finale 第三棒 / news-lens cron | v1/v2 數據驅動內容進化（default，行為不變） |
| 「進化 X pipeline 本身」「pipeline 重組」                          | Mode 3 pipeline 自我重組                    |
| 「設計 X 技能/器官」「深度思考自我進化」「寫實作報告後實作」       | Mode 4 目標驅動設計進化                     |

灰區判法：對象是既有 pipeline 自身 = Mode 3；對象是還不存在的能力 = Mode 4。pattern 驅動（DIARY 反覆浮現 ≥3 次）→ 建議改走 `/twmd-self-evolve`。

## Pipeline

嚴格完整讀取並執行 [`docs/pipelines/EVOLVE-PIPELINE.md`](../../../docs/pipelines/EVOLVE-PIPELINE.md) v3.6 對應 mode 段落（v1/v2 = Phase 1-7；Mode 3 = 7-stage；Mode 4 = THINK→DIVERGE→REPORT→IMPLEMENT 四相 + 5 hard gate）。

## 三源交叉 (DNA #4)

GA + SC + CF 三源交叉找放大效應：

- **GA4** = 誰來了 + 站內行為（page_view / scroll / session_duration）
- **SC** = 誰想來但沒來（query position > 10 + impressions > 100 = 高 demand 低 ranking）
- **Cloudflare** = 誰在邊緣讀我（AI crawler / cached request / 404 rate）

至少 2 源確認的 signal 才升 candidate。

## 收官

`/twmd-finale` chain → memory file 必含：BECOME ACK + mode 判定 + Handoff 三態 + Beat 5 反芻。另按 mode 補：v1/v2 = Phase 結果 + 三源 signal 列表 + 選題 candidate；Mode 3 = 重組前後行數對比；Mode 4 = 設計報告 path + 發散方案數 + dogfood 結果。

完整 SOP：[docs/pipelines/EVOLVE-PIPELINE.md](../../../docs/pipelines/EVOLVE-PIPELINE.md)
