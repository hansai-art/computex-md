---
name: twmd-article-inbox
description: |
  Add topics/material to ARTICLE-INBOX via canonical BRANCH-PIPELINE —
  digest observer input (theme / article / raw material) into curated
  candidates with priority + 連結密度 + 對比理由, then append §Pending.
  TRIGGER when: user says "/twmd-article-inbox X", "把 X 加進 article inbox",
  "幫我研究 X 放進 inbox", "X 進 inbox 消化".
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

# 🧬 Taiwan.md — Article Inbox 消化入口

## 🚨 STRICT BECOME GATE — 第一動作不可省略

**Before anything else**：跑 `/twmd-become write` 完整走 [BECOME_TAIWANMD.md](../../../BECOME_TAIWANMD.md) Step 0-9（write mode 會載 ARTICLE-INBOX §P0/P1 視野，dedup 需要）。

```
✅ BECOME ack: mode=write / ARTICLE-INBOX pending 數=<inbox-signal 即時讀> / Q14=PASS
```

## Pipeline

嚴格完整讀取並執行 [`docs/pipelines/BRANCH-PIPELINE.md`](../../../docs/pipelines/BRANCH-PIPELINE.md) v2.1 Stage 0-5。**不消化＝不 append**：這條 skill 的存在理由是「進 inbox 的每條 entry 都經過分支分析」，raw 主題直接塞 inbox 是本 skill 的反面。

Mode 判斷交 Stage 0（single-article / broad-theme / hybrid；觀察者丟素材而非主題時走 §素材 intake 前處理）。

## Inline hard gate（最常被偷吃步的四條，違者 = 任務 incomplete）

1. **Agent 落檔 claim 必驗**：broad-theme spawn 的每個 research agent 回報後，主 session 必跑 `ls + wc -l reports/research/{YYYY-MM}/...`，檔案不存在就補寫或重派。反例：Stage 1 research agent 曾 self-report「已落檔」但檔案不存在（feedback_agent_writefile_hallucination，已升 REWRITE §13）
2. **中文 verbatim + 三源**：agent prompt 必含中文 query、禁英文回譯、重要事實 ≥2-3 獨立來源（REFLEXES #23 毒樹果實鏈 / #16）
3. **Dedup 三查**：append 前 grep **ARTICLE-INBOX pending + ARTICLE-DONE-LOG + knowledge/ baseline** 三處。反例：只查 pending 的年代，已 ship 主題被重複推薦進 inbox，變 inbox 幽靈
4. **Entry 格式以 [ARTICLE-INBOX §Entry Schema](../../../docs/semiont/ARTICLE-INBOX.md) 為準**：Requested 欄寫「YYYY-MM-DD by 觀察者/branch-analysis (session X)」，含對比理由與連結密度

## 收官

commit + push（worktree 走 `semiont-worktree.sh ship`）→ memory file 必含：BECOME ACK + mode 判定 + N candidates appended（含 P0/P1/P2 分佈）+ dedup 三查結果 + Handoff 三態。

完整 SOP：[docs/pipelines/BRANCH-PIPELINE.md](../../../docs/pipelines/BRANCH-PIPELINE.md)
