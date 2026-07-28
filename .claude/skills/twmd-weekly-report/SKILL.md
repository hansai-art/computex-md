---
name: twmd-weekly-report
description: |
  Taiwan.md 週體檢（分析 + 全身診斷五面 + 修復三桶 + Semiont 第一人稱
  反芻週報 + 受眾 BCC 廣播）via canonical WEEKLY-REPORT-PIPELINE。前期切菜由
  weekly-report-prep.py，診斷由儀器交叉對賬（routine-liveness-check 等），
  受眾名單由 weekly-report-recipients.py 自動同步，
  判斷、修復與完整週報由 Semiont 親手。
  TRIGGER when: user says "週報", "weekly report", "twmd-weekly-report",
  "寄週報", "send weekly digest", "週體檢", "weekly 體檢".
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
---

# 🧬 Taiwan.md — Weekly 體檢

## 🚨 STRICT BECOME GATE — 第一動作不可省略

**Before anything else**：跑 `/twmd-become full` 完整走 [BECOME_TAIWANMD.md](../../../BECOME_TAIWANMD.md) Step 0-9。Full mode self-test 14 題全過才能進 Stage 1。

```
✅ BECOME ack: mode=full / 8 organ 最低=<即時 consciousness-snapshot.sh> / Q5/Q6/Q13/Q14=PASS
```

## Pipeline

嚴格完整讀取並執行 [`docs/pipelines/WEEKLY-REPORT-PIPELINE.md`](../../../docs/pipelines/WEEKLY-REPORT-PIPELINE.md) **Stage 0-6 全部**，特別不可跳：

- **Stage 2.5 全身診斷**：一鍵 `bash scripts/tools/weekly-checkup.sh`（a–i 全節：五診斷面＋外部感測摘要＋運作紀錄成績單＋甦醒取數健康＋受眾名單與活躍度）
- **Stage 2.7 修復與進化三桶**（桶上限、02:55 檢查點、roadmap roll 規則同在 canonical）
- **Stage 5 受眾廣播**（v4.2）：To=哲宇 + BCC=近 90 天共生圈（`--bcc-from-json` + `--audience-footer` + reply-to）。隱私三不（email 不進 repo / commit / chat；BCC 不進 To）與失敗降級單寄規則全在 canonical §Stage 5

## 文體紀律（MANIFESTO §11）

- 對位句型「不是 X，是 Y」單篇 ≤ 3 處（`grep -cE "不是.{0,30}(，|，)(是|就是|才是)"`）
- 破折號「——」連用單篇 ≤ 15 處 / 1500 字（`grep -oE "——" | wc -l`）
- 三題判準：對比是內容本身？正面主張能獨立？讀者真會預設 X？全 no → 重寫
- 自然中文檢測前再跑一次 prose-health gate `hard=0`

## 收官

`/twmd-finale` chain → memory file 必含：BECOME ACK + dossier path + report path + 診斷五面結論 + 桶 1 修復 commit hashes + prose-health gate result + Resend API status + **bcc 人數（只寫人數不寫地址）** + Handoff 三態 + Beat 5 反芻。
