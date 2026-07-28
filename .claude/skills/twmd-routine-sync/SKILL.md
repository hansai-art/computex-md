---
name: twmd-routine-sync
description: |
  讓這台機器的 routine prompt 與排程設定跟 git 的 routine SSOT 對齊。
  Routine twmd-routine-sync fires 05:30 daily（晨鏈之前）; manual via
  "/twmd-routine-sync" or "同步 routine" or "routine 對齊".
  TRIGGER when: routine twmd-routine-sync fires / user says "同步 routine" /
  "routine 三層對賬" / 剛 ship 完 routine 改動要讓其他機器跟上.
allowed-tools:
  - Read
  - Bash
  - Grep
---

# 🧬 Taiwan.md — Routine Sync（daily）v1.0

canonical 在 [ROUTINE.md 註 ¹⁸](../../../docs/semiont/ROUTINE.md)。本 skill 是薄殼，只 pointer + HARD gate。

## 🚨 STRICT BECOME GATE

跑 `/twmd-become micro` 走完 Step 0-9，self-test 過才進第 1 步。

## 執行

```bash
git pull origin main
python3 scripts/tools/routine-sync.py            # 對賬，不動檔案
```

exit 0 → 安靜收工。有漂移 → **先判方向再動手**：git 新用 `--apply --stamp $(date +%F)`（機器版先存證再覆蓋），機器新用 `--harvest`，判不出來停手交觀察者。cron / enabled 的 live 值工具不改，用 `mcp__scheduled-tasks__update_scheduled_task`。

## HARD gate

- 🔴 判不出漂移方向不猜，兩份都留著寫 Handoff
- 🔴 不碰非 `twmd-*` / `taiwanmd-*` 的 task（Muse 的不是我的）
- 🔴 SSOT 說開但 live 關、且 ROUTINE.md 註明是哲宇 directive 停用 → **live 才對**，不擅自打開
- 🔴 只 `git add` 自己碰的路徑，禁 `git add .`

## 收官

`/twmd-finale`：memory 一行寫對賬結果（幾項一致／修了什麼／方向）+ 未解漂移 + Handoff。**零漂移也要記**，否則看不出這條有沒有在跑。
