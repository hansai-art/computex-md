---
name: twmd-refresh
description: |
  Refresh Taiwan.md dashboard data — full ground truth抓取與更新
  via canonical DATA-REFRESH-PIPELINE (git pull + 三源感知 +
  prebuild dashboard JSON 全套 regen + GitHub stats).
  TRIGGER when: user says "資料更新", "refresh", "跑 refresh-data",
  "三源感知", "dashboard 更新", "dashboard 資料抓取", "dashboard 怪怪的".
allowed-tools:
  - Bash
  - Read
---

# 🧬 Taiwan.md — Refresh Dashboard Data v3.0

## 🚨 STRICT BECOME GATE — 第一動作不可省略

**Before anything else**：跑 `/twmd-become micro` 完整走 [BECOME_TAIWANMD.md](../../../BECOME_TAIWANMD.md) Step 0-9。Micro mode self-test 7 題全過才能進 Stage 1。

```
✅ BECOME ack: mode=micro / 8 organ 最低=<即時 consciousness-snapshot.sh> / Q14 cross-session continuity=PASS
```

---

## Stage 1: 跑 pipeline

```bash
bash scripts/tools/refresh-data.sh
```

**步驟表不在本 skill 複寫** — canonical：[DATA-REFRESH-PIPELINE.md §一鍵執行](../../../docs/pipelines/DATA-REFRESH-PIPELINE.md)（步數與編號以 `refresh-data.sh` 頭註為準）。

**Rider：scheduler live-state dump**（session 層步驟，bash 進不了 MCP store——2026-07-05 S1 根治）：

1. 呼叫 `mcp__scheduled-tasks__list_scheduled_tasks`，raw JSON 存暫存檔
2. `python3 scripts/tools/routine-live-normalize.py <raw.json> --session <session-id>`（自動過濾私人 routine，只留 twmd-/taiwanmd-）
3. `docs/semiont/routine-live-state.json` 跟著 refresh commit 進 git — `routine-sync-check.py` v3 第三層比對靠它

> 2026-07-05 前本 skill 曾複寫 14 步全表——違反 ROUTINE-PROMPT-CONTRACT「殼層禁複寫 SOP」，且複寫版一度比 canonical 還新（SSOT 失守症狀，dna-audit §S5 反向案例）。改 pointer 後：修 pipeline = 改一處。

---

## Stage 2: 報告 + Step 11 freshness gate handling

Step 11 抓到 stale dashboard JSON → 走 [DATA-REFRESH-PIPELINE §catch ≠ fix 鐵律](../../../docs/pipelines/DATA-REFRESH-PIPELINE.md)（**第 2 次連續 catch 同一 stale 必須當 cycle wire fix，不 spawn chip**——鐵律全文與誕生背景在 canonical，本殼只留觸發指令）。

---

## Stage 3: 收官

`/twmd-finale` chain → memory file 必含：

- BECOME ACK 一行
- 14-step pipeline outcome（每 step PASS / FAIL）
- 三源 status (200 / refused / partial)
- Step 11 freshness 結果（stale list + handling）
- Handoff 三態
- Beat 5 反芻

完整 SOP：[DATA-REFRESH-PIPELINE.md](../../../docs/pipelines/DATA-REFRESH-PIPELINE.md)
