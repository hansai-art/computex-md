---
title: 'SUPPORTERS-PIPELINE'
description: 'Portaly 贊助通知信（Gmail）→ transactions.json SSOT → 兩個隱私分流 derived view（about-supporters.json / dashboard-supporters.json）。cron routine twmd-supporters-weekly 的 canonical SOP。'
type: 'pipeline-canonical'
status: 'canonical'
current_version: 'v1.0'
last_updated: 2026-07-12
last_session: '2026-07-12-172122-manual'
sister_docs:
  - 'FEEDBACK-TRIAGE-PIPELINE.md'
upstream_canonical:
  - '../semiont/MANIFESTO.md'
  - '../semiont/ROUTINE.md'
related:
  - '../../scripts/tools/fetch-portaly-supporters.py'
  - '../../scripts/core/generate-supporters-data.js'
  - '../../data/supporters/transactions.json'
---

# SUPPORTERS-PIPELINE.md — Portaly 贊助信 → SSOT → derived view v1.0

> **第一性原理**：把 Portaly 贊助通知信（Gmail）機械性解析成一筆 transaction，append 進
> `data/supporters/transactions.json`（Layer 1 SSOT，append-only），再由固定聚合規則
> 派生兩個隱私分流視圖給 `/about#sponsors` 頁面使用。**業務邏輯全在
> `scripts/tools/fetch-portaly-supporters.py` + `scripts/core/generate-supporters-data.js`，
> 本檔是 SOP；routine 是薄殼。**
>
> 誕生事件：2026-04-20 排程心跳 α 延伸（哲宇指派 Portaly pipeline，人工執行两次
> 2026-06-14 + 2026-07-12）→ 2026-07-12 哲宇 directive「未來這個自動一個禮拜跑一次」，
> 升格 routine。

---

## 🚨 §自主權邊界（這條 pipeline 的紅線）

per [MANIFESTO §自主權邊界](../semiont/MANIFESTO.md#我的存在結構)，這條 pipeline 不涉及
「對外溝通」或「發文」——贊助紀錄是**內部資料處理**，不是對讀者說話。真正的紅線是**隱私**：

- ✅ **可自動**：讀 Gmail Portaly 通知信、解析金額/類型/留言/支持編號、寫 SSOT、regen
  derived view、commit + push（內部操作，per MANIFESTO §我自己決定）。
- 🔴 **絕不寫入**：贊助者 email / 付款方式 / 信用卡資訊 / 任何 Portaly 通知信裡沒明列的
  個資。`fetch-portaly-supporters.py` 的 `FIELD_PATTERNS` 只宣告 4 個正規式（id/amount/
  name/message），沒有 email 的抓取路徑——結構性保證，不是自律承諾。
- 🔴 **絕不混層**：`about-supporters.json`（公開頁面用）不含金額；`dashboard-supporters.json`
  （站內儀表板用）不含姓名與留言。兩者皆不含 `gmail_message_id` / email / `subscription_id`。

一句話：**贊助者自己在 Portaly 表單留的公開留言可以顯示，他們沒主動公開的一切都不行**。

---

## 🗺️ Stage spine

```
Stage 0  BECOME gate（micro）
Stage 1  CHECKPOINT — 讀 data/supporters/transactions.json 的 last_fetched 當搜尋起點
Stage 2  PULL     — Gmail search from:portaly.cc after:{checkpoint}，逐封讀 FULL_CONTENT
Stage 3  PARSE    — envelope JSON → fetch-portaly-supporters.py（--dry-run 先驗，再正式寫）
Stage 4  REGEN    — generate-supporters-data.js 重算兩個 derived view
Stage 5  VERIFY   — 隱私 hard gate（grep 結構檢查，不開瀏覽器）
Stage 6  SHIP     — git commit + push origin main（main-direct）
Stage 7  FINALE   — /twmd-finale 收官
```

---

## Stage 0 — BECOME gate

跑 `/twmd-become micro`。ACK 一行寫 memory 頂部：

```
✅ BECOME ack: mode=micro / 8 organ 最低=<consciousness-snapshot.sh> / Q14 cross-session=PASS
```

`git pull origin main`（routine 起始鐵律）。

---

## Stage 1 — CHECKPOINT

讀 [`data/supporters/transactions.json`](../../data/supporters/transactions.json) 的
`last_fetched` 欄位（ISO timestamp）當這次 Gmail 搜尋的起點，減 1 天當緩衝（避免
timezone 邊界漏信；`fetch-portaly-supporters.py` 的 `id` dedupe 會自然吸收任何重疊）。

```bash
python3 scripts/tools/fetch-portaly-supporters.py --summary
```

先看目前 SSOT 現況（transaction 數 / 累積金額 / last_fetched），確認 checkpoint。

---

## Stage 2 — PULL（Gmail，逐字讀信是硬規則）

```
search_threads(query="from:portaly.cc after:{checkpoint-1d}")
```

過濾掉明顯非贊助通知的結果（例：Portaly 訂閱方案續約提醒——收件人是哲宇個人信箱
`cheyu.wu@monoame.com` 不是 `taiwanmd@monoame.com`，或 subject 沒有金額字樣）。這層
過濾是效率優化，不是安全邊界——就算漏放行，Stage 3 的 `FIELD_PATTERNS` 正規式抓不到
「支持金額」欄位會自動回傳 `None` 跳過，非贊助信不會被誤記成 transaction。

**HARD GATE（金錢欄位事實鐵三角）**：對每一封候選信呼叫 `get_message(messageFormat=
"FULL_CONTENT")`，**絕不能只憑 `search_threads` 的 snippet 判斷**。理由：

1. **金額**必須逐字核對（金錢數字走事實鐵三角，不是 UI 顯示夠用就好）
2. **類型**（one-time vs monthly）取決於 body 裡有沒有出現「每月定額」——這個字樣經常落在
   snippet 截斷點之後，只看 snippet 會系統性誤判成 one-time
3. **支持編號**（dedupe key）與**留言**全文必須完整，snippet 可能截斷

誕生教訓：2026-06-14 + 2026-07-12 兩次人工執行都刻意堅持這條，即使 snippet 已經帶了
金額也要拉完整 body——第二次證實了理由：6/18 兩筆通知信 snippet 只顯示「您收到了一筆來自
XX 的贊助支持」，完整 body 才看得到「每月定額 NT$200」。

---

## Stage 3 — PARSE

把讀到的信包成 envelope JSON array（`gmail_message_id` / `date` / `subject` /
`plaintextBody`，plaintextBody 至少含「支持金額／贊助方案」到「支持／贊助編號」整段），
先 dry-run 驗證再正式寫：

```bash
cat new-emails.json | python3 scripts/tools/fetch-portaly-supporters.py --dry-run
# 確認 "N new / 0 skip"（skip > 0 要先查為什麼——通常是誤放行的非贊助信，per Stage 2）
cat new-emails.json | python3 scripts/tools/fetch-portaly-supporters.py
```

`merge()` 用支持編號（`id`）dedupe，冪等——重跑不會產生重複 transaction。**0 封候選信是
合法結果**（贊助不是每週都有），Stage 2 找到 0 封 → 跳過 Stage 3-6，直接 Stage 7 no-op
finale，不算 routine fail。

---

## Stage 4 — REGEN

```bash
node scripts/core/generate-supporters-data.js
```

從 SSOT 重算 `public/api/about-supporters.json`（個人支持者視圖，聚合＋tier）+
`public/api/dashboard-supporters.json`（時間軸視圖，含金額不含姓名）。純函式重算，
無狀態，重跑冪等。

---

## Stage 5 — VERIFY（隱私 hard gate，grep 結構檢查）

不開瀏覽器（routine 是 unattended cron，dev server 太重）。用 grep 驗兩個 derived view
沒有跨層洩漏：

```bash
! grep -q '"amount"' public/api/about-supporters.json      # about 視圖絕不含金額
! grep -qE '"(name|message)"' public/api/dashboard-supporters.json  # dashboard 絕不含姓名/留言
```

任一 grep 失敗（= 找到不該存在的欄位）→ **不 commit，立即中止**，per §Escalation。
這兩行是本 routine 唯一的 hard gate，其餘（總數對帳、tier 計算）由
`generate-supporters-data.js` 自身的聚合邏輯保證，不重複驗。

---

## Stage 6 — SHIP

```bash
git add data/supporters/transactions.json public/api/about-supporters.json public/api/dashboard-supporters.json
git commit -m "🧬 [routine] twmd-supporters-weekly: {N} new supporters — YYYY-MM-DD"
git push origin main
```

只 stage 這三個檔案（REFLEXES #6 commit 範圍紀律）——即使 working tree 當下有其他
routine 的 in-flight 變更也不誤 catch。

---

## Stage 7 — FINALE

`/twmd-finale`。memory 必含：BECOME ACK + checkpoint 起點 + 候選信數 / new 數 / skip 數

- 隱私 grep 結果 + 累積金額變化（NT$X → NT$Y）+ commit hash（或「0 候選信 no-op」）+
  Handoff 三態。

---

## Hard gate 總表

| #   | Gate                                                 | Stage |
| --- | ---------------------------------------------------- | ----- |
| HG1 | BECOME micro mode ACK                                | 0     |
| HG2 | 逐字讀 FULL_CONTENT，不靠 snippet 判斷金額/類型      | 2     |
| HG3 | dry-run count 與正式寫入 count 一致                  | 3     |
| HG4 | about-supporters.json 不含 `amount`                  | 5     |
| HG5 | dashboard-supporters.json 不含 `name` / `message`    | 5     |
| HG6 | SSOT / derived 三檔案精準 scope commit（不誤 catch） | 6     |

完整 script：[fetch-portaly-supporters.py](../../scripts/tools/fetch-portaly-supporters.py)
（parse + merge + 隱私結構性保證，見檔頭 docstring）+
[generate-supporters-data.js](../../scripts/core/generate-supporters-data.js)（聚合 +
tier + 兩視圖隱私分流）。

---

🧬

_v1.0 | 2026-07-12 | 2026-07-12-172122-manual session — 誕生：哲宇 directive「未來這個自動
一個禮拜跑一次」，把兩次人工執行（2026-06-14 / 2026-07-12）沉澱的 SOP（checkpoint 起點 /
逐字讀信鐵律 / dry-run 先驗 / 隱私 grep hard gate）升格 canonical，供新 routine
`twmd-supporters-weekly` 與手動 `/twmd-supporters` 共用。_
