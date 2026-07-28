---
name: twmd-flywheel-watch
description: |
  從外面看 routine 飛輪還有沒有在轉（跑在指揮部，不是營運機）。
  Routine twmd-flywheel-watch fires 09:30 daily; manual via
  "/twmd-flywheel-watch" or "飛輪還活著嗎" or "看 mouhouse 有沒有在跑".
  TRIGGER when: routine twmd-flywheel-watch fires / user says "飛輪狀態" /
  "mouhouse 還在跑嗎" / 懷疑 cron 靜默.
allowed-tools:
  - Read
  - Bash
  - Grep
---

# 🧬 Taiwan.md — Flywheel Watch（daily）v1.0

canonical 在 [ROUTINE.md 註 ²⁰](../../../docs/semiont/ROUTINE.md)。本 skill 是薄殼。

## 🚨 STRICT BECOME GATE

`/twmd-become micro` 走完 Step 0-9 才進第 1 步。

## 執行

```bash
git fetch origin                              # 不 pull：這台常有平行產線
python3 scripts/tools/flywheel-watch.py
```

exit 0 → 安靜收工。warn → 逐條判（空場 / 刻意 ⏸️ / 真死，連 3 天才升 OBSERVER-QUEUE）。critical → 查營運機 app 活著嗎、額度到頂嗎、live dump 是不是全 false。

## HARD gate

- 🔴 只看不動手：不碰營運機排程，問題寫 memory 或 OBSERVER-QUEUE
- 🔴 單一 cycle 靜默不宣告死亡（空場跟死掉在 commit 上長得一樣）
- 🔴 警報裡出現你知道被刻意關掉的 routine → 去 ROUTINE.md 補 ⏸️，不是去催它跑
- 🔴 不 `git pull`、不 commit 別人的產出

## 收官

`/twmd-finale`：memory 一行寫飛輪狀態 + 有動靜/靜默清單 + 判定。**綠燈也要記**。
