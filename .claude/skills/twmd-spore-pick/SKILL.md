---
name: twmd-spore-pick
description: |
  Daily spore candidate picking via canonical SPORE-PICK-PIPELINE — propose 3 candidates
  to SPORE-INBOX §Pending. Routine fires 08:00 daily; manual via "/twmd-spore-pick" or
  "跑 spore pick" or "補 SPORE-INBOX".
  TRIGGER when: routine twmd-spore-pick-daily fires / user says "跑 spore pick" /
  "幫我選幾篇可以發孢子的文章" / "補 SPORE-INBOX".
allowed-tools:
  - Read
  - Bash
  - Write
  - Edit
  - Grep
---

# 🧬 Taiwan.md — Spore Pick (daily) v3.0

## 🚨 STRICT BECOME GATE — 第一動作不可省略

**Before anything else**：跑 `/twmd-become write` 完整走 [BECOME_TAIWANMD.md](../../../BECOME_TAIWANMD.md) Step 0-9。Write mode self-test 8-9 題全過才能進 Stage 1。

**驗證 ACK 一行**（必寫 memory file 頂部）：

```
✅ BECOME ack: mode=write / 8 organ 最低=<即時 consciousness-snapshot.sh> / Q14 cross-session continuity=PASS
```

---

## Stage 0: Routine context

```bash
git pull origin main
```

---

## Stage 1: READ — 6 source（cheap layer 不 web）

| Source                                                 | 用途                                      |
| ------------------------------------------------------ | ----------------------------------------- |
| `public/api/dashboard-articles.json`                   | article pool (~500-700 non-about wc>2000) |
| `public/api/dashboard-analytics.json` §searchConsole7d | SC opportunities (pos>10 imp>100)         |
| `public/api/dashboard-spores.json`                     | 最近 14d 排除 list                        |
| `docs/factory/SPORE-INBOX.md` §Pending                 | 現有 pending 排除 list                    |
| `docs/semiont/ARTICLE-DONE-LOG.md` 最近 14d            | 趁熱 candidate pool                       |
| `docs/semiont/ARTICLE-INBOX.md` §P0/P1                 | EVERGREEN-TOPIC candidate                 |

每 source 在 memory file 標 line count cite（HG2）。

---

## Stage 2: SCORE — 7-dim weighted（v2 HG10 multi-dim gate）

對 article pool 每篇算 7 dim：

| Dim                   | 範圍  | 觸發條件                                                                        |
| --------------------- | ----- | ------------------------------------------------------------------------------- |
| **D1 趁熱**           | 0-30  | ≤7d=30, ≤14d=15, ≤30d=5                                                         |
| **D2 SC opportunity** | 0-25  | imp ≥ 500 + pos > 10 → +25, imp ≥ 100 → +15                                     |
| **D3 News sense**     | 0-20  | article.slug ∈ this-week news-lens topics → +20                                 |
| **D4 多語 fanout**    | 0-15  | category ∈ {People/Food/Music/Sports/History} + < 3 translations → +15, else +8 |
| **D5 冷門高品質**     | 0-10  | v2 widen: 80/80/30d=+10, 70/70/60d=+7, 70/-/90d=+5                              |
| **D6 Hook variety**   | -10-0 | recent 3 spore hook 同類 → -10                                                  |
| **D7 敏感度**         | -20-0 | high-sensitivity keyword 命中非 REACTIVE → -20                                  |

```python
score = d1 + d2 + d3 + d4 + d5 + d6 + d7
non_zero_dims = sum(1 for d in [d1, d2, d3, d4, d5] if d > 0)
```

---

## Stage 3: DRAFT — full SPORE-INBOX schema

每 candidate 4 hook anchor + ≥ 2 hook types + 必驗事實 ≥ 10 條 + Source-Mode 標記 + Notes 欄位 score 拆解 transparency。

完整 schema：[SPORE-PICK-PIPELINE.md §Stage 3](../../../docs/factory/SPORE-PICK-PIPELINE.md)。

---

## Stage 4: VERIFY — 10 hard gate（HG1-HG10，v2 升級）

| #             | Gate                                                                  | Stage |
| ------------- | --------------------------------------------------------------------- | ----- |
| HG1           | BECOME write mode 完成                                                | 0     |
| HG2           | 6 source 全讀完（line count cite）                                    | 1     |
| HG3           | 每 candidate 7 dim 都算分（Notes transparency）                       | 2     |
| HG4           | 每 candidate ≥ 2 hook anchor + ≥ 2 hook types                         | 3     |
| HG5           | 0 candidate 在 14d 內發過孢子（`spore-db.py last-spore --article`）   | 4     |
| HG6           | 0 candidate 跟 SPORE-INBOX 現有 pending 重複                          | 4     |
| HG7           | 至少 2 個不同 Source-Mode                                             | 4     |
| HG8           | 至少 1 個來自 ARTICLE-DONE-LOG 最近 7d                                | 4     |
| HG9           | 不碰高敏感（兩岸/228/政治）除非 REACTIVE                              | 4     |
| **HG10 (v2)** | **每 candidate 至少 2 個非零 dim 或 score ≥ 35**（D1 單軸不算 valid） | 2     |

**HG10 fail handling（鐵律 2026-05-28 v2）**：candidate 不能 propose，**寧可 < 3 candidates** 也不用單軸湊數。Pool 太稀 → 寫 LESSONS-INBOX entry + 明確 emit「< 3 viable, observer review」（不假裝 routine 健康）。

觸發背景：5/28 spore-pick audit 揭露三 candidate 全 D1 單軸（艋舺 30/0/0/0/0/0/0 / 台灣 BIM 30/0/0/0/0/0/0 / 媒體總史 0/0/0/8/0/0/0）→ 7-dim 框架實質退化成「最舊 FIFO」proxy。

---

## Stage 5-6: APPEND + COMMIT

Append 3 entries 到 [SPORE-INBOX.md](../../../docs/factory/SPORE-INBOX.md) §Pending（保留 §已發歷史 不動，append-only 鐵律遵守）。

routine source default `P2`。score ≥ 60 / news-lens 標 / REACTIVE 才升 P0/P1。

commit + push origin main（v2.0 main-direct）。

---

## Stage 7: 收官

`/twmd-finale` chain → memory file 必含：BECOME ACK + Stage 1-4 outcome + 10 HG 狀態表 + Handoff 三態 + Beat 5 反芻。

完整 SOP：[SPORE-PICK-PIPELINE.md](../../../docs/factory/SPORE-PICK-PIPELINE.md)

ARGUMENTS: (none — pipeline 自己讀 dashboard + INBOX state)
