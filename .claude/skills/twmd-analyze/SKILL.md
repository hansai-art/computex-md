---
name: twmd-analyze
description: |
  Rigorous data-analysis investigation via canonical ANALYSIS-PIPELINE —
  defends against 分析幻覺 (true-but-misleading numbers). Impact / attribution /
  funnel / reception / cohort analysis with confounder isolation + honest gates.
  TRIGGER when: user says "分析 X 有沒有改善", "這流量哪來", "before/after",
  "改版影響", "研究這批數據", "這個 finding 可不可信", "跑 analysis".
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - Agent
---

# 🧬 Taiwan.md — Analyze（極簡薄殼）

> **故意極簡**。所有 SOP（Stage 0-7 / Hard Gate Inventory / 分析幻覺 H1-H9 目錄 / 5 mode / 深淺兩檔 / 工具盤 / §跨檔分工）100% 在 pipeline canonical。本 skill **只做三件事，不複寫 pipeline 內容**（複寫 = drift = 退化）。

## 1. STRICT BECOME GATE（不可省）

跑 `/twmd-become` 完整 [BECOME_TAIWANMD.md](../../../BECOME_TAIWANMD.md) Step 0-9。分析會影響決策 / 對外 / 自己分析自己 → high-stake 強制升 Full mode，self-test 全過才動工。

## 2. 完整讀 ANALYSIS-PIPELINE（不可 head / tail / 取樣）

用 **Read tool 一次讀完** `docs/pipelines/ANALYSIS-PIPELINE.md`（無 `limit` / `offset`）。照 Stage 0-7 跑，每道 hard gate 都過。

## 3. 執行 + 過誠實 gate 才交報告

工具盤在 `scripts/tools/`：`ga-query.py` / `sc-query.py` / `ga-window-compare.py` / `referral-attribution.py` / `analysis-report-health.py`（地基 `lib/sense_client.py`）。報告 ship 前 `python3 scripts/tools/analysis-report-health.py {report} --tier=deep` 必 PASS。Stage 7 把 finding route 到 INBOX / probe / watch，不讓報告腐爛。

**鐵律**：可重用的是判斷不是查詢；pipeline 防的是「真實但誤導」的分析幻覺（H1 尺度 / H2 率量 / H3 lag / H7 自我驗證）。不要用 ga4-analytics skill 的 runReport 下 filter（靜默吞 filter，REFLEXES #24）—— 一律用 `ga-query.py`。
