---
name: twmd-feedback-triage
description: |
  讀者站上回報（Supabase）→ 分類/反 spam/去重 → GitHub issue（對齊既有 template）→
  接 MAINTAINER 飛輪。Routine twmd-feedback-triage fires 07:00 daily（maintainer-am 之前）;
  manual via "/twmd-feedback-triage" or "跑 feedback triage" or "把回報轉成 issue".
  TRIGGER when: routine twmd-feedback-triage fires / user says "跑 feedback triage" /
  "處理讀者回報" / "把站上回報開成 issue".
allowed-tools:
  - Read
  - Bash
  - Grep
---

# 🧬 Taiwan.md — Feedback Triage (daily) v1.0

業務邏輯 canonical 在 [FEEDBACK-TRIAGE-PIPELINE.md](../../../docs/pipelines/FEEDBACK-TRIAGE-PIPELINE.md)。
本 skill 是薄殼,只 pointer + HARD gate,不複寫 threshold / SOP / step。

## 🚨 STRICT BECOME GATE — 第一動作不可省略

跑 `/twmd-become review` 完整走 [BECOME_TAIWANMD.md](../../../BECOME_TAIWANMD.md) Step 0-9。Review mode self-test（含 Q13 anti-bias + Q14 cross-session）全過才進 Stage 1。

ACK 一行（寫 memory 頂部）：

```
✅ BECOME ack: mode=review / 8 organ 最低=<consciousness-snapshot.sh> / Q13=PASS / Q14=PASS
```

## 🔴 §自主權邊界（讀 pipeline §自主權邊界 全文後才動）

開 issue = 機械轉錄讀者原話（可自動）。**以維護者身份回覆 / close / merge 永遠留人類** —— 那是 MAINTAINER-PIPELINE 的事,不在本 routine。

## 執行

完整 5 stage（BECOME → PULL → TRIAGE → FILE → WRITE-BACK → FINALE）讀 [FEEDBACK-TRIAGE-PIPELINE.md](../../../docs/pipelines/FEEDBACK-TRIAGE-PIPELINE.md) §每 stage。核心動作：

```bash
git pull origin main

# 機器身份：開 issue 走 GitHub App，不用宿主機的哲宇帳號（HG10）
export GH_TOKEN="$(bash scripts/tools/gh-app-token.sh)"
bash scripts/tools/gh-app-token.sh --whoami    # 應為 {"issues": "write", "metadata": "read"}

# 先 dry-run 看分類（HG2 無 email / HG5 spam / HG6 dedupe 自己核一遍）
node scripts/feedback/triage.mjs

# 確認 OK 才 --commit（真開 issue + 回寫 status）
node scripts/feedback/triage.mjs --commit
```

未配置 Supabase（`SUPABASE_URL`/`SUPABASE_SERVICE_KEY` 缺）→ emit「feedback backend 未配置,skip」,**不算 fail**（escalation 只看 quality gate）。

## HARD gate（cite pipeline §Hard gate 總表,逐條核）

- HG2 🔴 issue body **無 email**（`triage.test.mjs` regex 守,CI 必綠）
- HG3 🔴 讀者文字 verbatim 不改寫
- HG5/HG6 spam reject + dedupe 正確
- HG8 🔴 不以維護者身份開口（留人類）
- HG9 🔴 **git archive 主權層**：每筆 filed 寫 `docs/feedback/archive/`（無 email），
  issue 留言 sync 進 §溝通紀錄。**收官前 `git add docs/feedback/archive/`**（不進 git = 主權層失效）。
- HG10 🔴 **機器身份**：`GH_TOKEN` 必須是 App installation token（`ghs_` 開頭）。
  空值或缺失 = 停手，不要讓 `gh` 退回哲宇帳號把 issue 掛成維護者親開。

## 收官

`/twmd-finale` → memory 必含 BECOME ACK + file/reject/skip count + 開的 issue #N + archive 檔數 + Handoff。
**commit 前**：`git add docs/feedback/archive/`（per HG9，讓回報+溝通紀錄落進 git）。

ARGUMENTS: (none — script 自己讀 Supabase status='new')
