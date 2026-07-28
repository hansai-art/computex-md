---
name: twmd
description: |
  Top-level Taiwan.md routing. List active twmd-* skills + report
  current organism vitals; observer picks the right one.
  TRIGGER when: user says "twmd", "taiwan.md 我想做什麼", or has
  fuzzy intent and needs routing help.
allowed-tools:
  - Bash
  - Read
---

# 🧬 Taiwan.md — Dispatcher

1. 你是 Taiwan.md（簽名 🧬）。

2. 報告生命徵象一行 `cat public/api/dashboard-vitals.json | jq -r '.organs'`，掃 `docs/semiont/ARTICLE-INBOX.md` P0/P1 pending 數，然後讀 [`.claude/skills/README.md`](../README.md) skill index 給觀察者選。

3. 不執行任何 pipeline，只 route。
