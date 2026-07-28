---
title: 'CORRECTION-PIPELINE'
description: '勘誤處理流程 SSOT — 收到/發現錯誤後的 5 stage TRIAGE/VERIFY/FIX/NOTIFY/LOG + 錯誤邊界=可追溯性 + 【勘誤通知】正式格式 + reply 5 鐵律 + 16 案例表 (v1.0)'
type: 'pipeline-canonical'
status: 'canonical'
current_version: 'v1.0'
last_updated: 2026-06-24
last_session: '2026-06-24-142554-龜山島-rewrite'
plugin_check: 'python3 scripts/tools/article-health.py {file} --check=prose-health'
sister_docs:
  - 'SPORE-HARVEST-PIPELINE.md'
  - 'REWRITE-PIPELINE.md'
  - 'FACTCHECK-PIPELINE.md'
  - 'MAINTAINER-PIPELINE.md'
upstream_canonical:
  - '../semiont/MANIFESTO.md'
  - '../semiont/REFLEXES.md'
---

# CORRECTION-PIPELINE.md — 勘誤處理流程（SSOT）v1.0

> **第一性原理**：**錯誤邊界 = 可追溯性，不是完美。** Taiwan.md 一定會出錯（AI 記憶過時、stage 2 引語脫離語境、在地細節推導錯）。決定信任的不是「零錯誤」，是「錯了之後怎麼處理」。**可追溯的錯 → 公開更正（更正本身是信任訊號）；無法溯源的杜撰 → 撤回。** 沉默、防衛、拖延，才是真正侵蝕信任的東西。
>
> 實證：李洋孢子 #29 帶著未解的事實爭議，公開更正版 2 小時 21K views / engagement 12%（產業平均兩倍），是史上第二強孢子（觀察者協作記憶 `project_error_boundary_traceability`——private layer 不在 repo，哲學結論已收斂進本檔第一性原理）。把更正當成《報導者》式的嚴肅自我修正來做，它本身就是信任的證明。
>
> **這份 pipeline 把原本散在 SPORE-HARVEST（Bucket A/C + Error Boundary + Reply 5 鐵律）、REWRITE（Step 0.2-bis 拆除防火牆）、FACTCHECK、6 條 feedback memory、16 個 worked case 的勘誤 SOP 收斂成單一 canonical。** 不分管道（讀者孢子留言 / contributor issue / 我自己 factcheck / peer），收到或發現錯誤就走這條。

---

## 🗺️ ASCII spine

```
╭──────────────────────────────────────────────────────────────────────────╮
│        CORRECTION-PIPELINE 5 階段 — 收到/發現錯誤就走                    │
│                                                                          │
│   🧭 核心紀律                                                            │
│            ├── 錯誤邊界=可追溯性（可溯→更正 / 杜撰→撤回）                │
│            ├── 三步齊全：驗證 + 修文章 + 回覆（缺一不可）                │
│            ├── D+0 ≤6hr acute → 30 min 內處理（traceability erode 防線） │
│            └── 認錯不防衛、不卑不亢、不洩漏紅線焦慮                      │
│                                                                          │
│   Stage 1: TRIAGE ──→ 分類（這是哪種錯？該怎麼處置？）                   │
│            ├── 先 falsify callout 本身（讀者也會錯）                     │
│            ├── traceable factual / scene-inference → 修+通知            │
│            ├── 杜撰/無源 → 撤回（retract）                              │
│            ├── framing/立場 → defer 哲宇（§自主權邊界）                  │
│            └── severity × reach × D+N（acute window 判定）              │
│              ↳ Hard gate: 分桶前不行動                                  │
│                                                                          │
│   Stage 2: VERIFY ──→ 查證（callout + 原文都查）                         │
│            ├── 跨 3+ 獨立來源 + 中文逐字（禁英摘回譯）                   │
│            ├── 清單外連帶錯一起修（callout 價值一半在清單外）            │
│            └── 無法溯源 → 不寫/撤，不硬留                                │
│              ↳ Hard gate: 委派 FACTCHECK Quick/Full（delegate）          │
│                                                                          │
│   Stage 3: FIX ──→ 修正（knowledge/ canonical，外科手術）               │
│            ├── 只改 knowledge/，commit `heal: {slug} — 勘誤 per @reader` │
│            ├── 杜撰 → 撤回該 claim/段/篇                                 │
│            └── callout-triggered 全 EVOLVE → REWRITE Step 0.2-bis 防火牆 │
│              ↳ Hard gate: git log 留痕（可追溯）                         │
│                                                                          │
│   Stage 4: NOTIFY ──→ 通知（公開承認 + 指向更正）                        │
│            ├── 正式：【勘誤通知】格式（標題+正確版+說明+致謝+連結）      │
│            ├── 隨手：inline reply 5 鐵律（認錯+具體+指 fix+你+🧬）       │
│            └── URL percent-encode / 致謝具名 / 無客服腔                  │
│              ↳ Hard gate: 改了文章必指出更正 URL（否則 traceability 斷） │
│                                                                          │
│   Stage 5: LOG ──→ 記錄（blueprint / memory / LESSONS / teach）          │
│            └── 抽出可複用教訓（這類錯下次怎麼防）                        │
│                                                                          │
│   ──── 跨 pipeline 委派 ───────────────                                 │
│   ← SPORE-HARVEST Bucket A/C（讀者孢子留言）→ 本檔                       │
│   ← MAINTAINER（contributor issue 勘誤）→ 本檔                           │
│   ← REWRITE callout-triggered EVOLVE → 本檔 + Step 0.2-bis 防火牆        │
│   → FACTCHECK-PIPELINE（Stage 2 查證引擎）                               │
╰──────────────────────────────────────────────────────────────────────────╯
```

---

## 🚦 Hard Gate Inventory（一張表 audit 全 pipeline）

| Gate                     | 觸發 stage | 條件                | 工具/自檢                                                   | 不過 = ?                                             |
| ------------------------ | ---------- | ------------------- | ----------------------------------------------------------- | ---------------------------------------------------- |
| 分桶前不行動             | TRIAGE     | 每條 callout        | 5-bucket 分類（[SPORE-HARVEST](SPORE-HARVEST-PIPELINE.md)） | 亂修/誤撤                                            |
| 先 falsify callout       | TRIAGE     | 每條 callout        | 讀者 claim 也跨源驗（讀者會錯）                             | 把對的改成錯（無名小卒「不是BBS」/ 太空中心 1 不採） |
| D+0 ≤6hr acute → 30 min  | TRIAGE     | traceable + 已公開  | 立即進 FIX，不 defer                                        | traceability erode = 信任失靈                        |
| 跨 3+ 源 + 中文逐字      | VERIFY     | 所有事實/引語       | FACTCHECK Quick/Full + Ctrl-F 中文原頁                      | 禁英摘回譯（毒樹果實）                               |
| 清單外連帶修             | VERIFY     | 修一處時            | 順手 audit 鄰近同類錯                                       | 只修點名的，漏沒點名的（太空中心 3 腳註）            |
| 只改 knowledge/          | FIX        | 所有修正            | 不碰 src/content（投影層）                                  | 下次轉錄被覆蓋                                       |
| heal commit 留痕         | FIX        | 所有修正            | `heal: {slug} — 勘誤 per @{reader}`                         | 可追溯性斷（偷改不留痕=信任違反）                    |
| 杜撰 → 撤回非更正        | FIX        | 無法溯源的 claim    | retract（刪該 claim/段）                                    | 留著假事實賺信任                                     |
| 改文章必指更正 URL       | NOTIFY     | 有對外回覆          | reply/通知含 encoded 更正連結                               | reader 不知後續，traceability 斷                     |
| reply URL percent-encode | NOTIFY     | reply 含中文 path   | `urllib.parse.quote`                                        | Threads/X auto-link 斷                               |
| 認錯不防衛/不洩漏焦慮    | NOTIFY     | 所有對外文字        | reply 5 鐵律 + 無紅線焦慮                                   | 客服腔/防衛 = 二次信任傷害                           |
| §11 prose-health         | NOTIFY     | 勘誤通知/reply 文字 | `article-health.py --check=prose-health`                    | AI 水印                                              |

---

## ⚠️ Top 6 最常忘的 step

1. **先 falsify callout，讀者也會錯** — 預設讀者對（反射），但要查證；無名小卒讀者「不是 BBS」才是錯的、太空中心 12 條有 1 條不採。認錯前先確認真的錯。
2. **D+0 ≤6hr 不 defer** — acute window 30 min 內 fix+通知是 SOP 不是 stretch goal。延遲 = 讀者看到錯的窗口擴大。
3. **清單外連帶修** — callout 價值一半在清單外：修讀者點名的，順手 audit 鄰近同類錯（太空中心讀者點 10 條，連帶修了 3 個沒點名的腳註錯綁）。
4. **改了必指更正 URL（encode）** — 文章改了但 reply 沒指 URL = reader 不知後續 = traceability 斷。中文 path 必 percent-encode。
5. **杜撰要撤回不是更正** — 可追溯的錯改正；查無源的杜撰（人/引語/事件不存在）要撤回該 claim，不是改寫。謝甫宜老師不存在 = 撤；龜山島山羊查無 live 源 = 不寫。
6. **callout 只進查證，不進觀點/正文（全 EVOLVE 時）** — callout-triggered 全文重寫走 [REWRITE Step 0.2-bis 拆除防火牆](REWRITE-PIPELINE.md)：別讓「不要搞錯」變成文章脊椎、別在正文撒校正焦慮句（影視配樂第二輪教訓）。

---

## 跨檔案職責分工

| 檔案                                                                                   | 範圍                                                                      |
| -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **本檔（CORRECTION）**                                                                 | 勘誤端到端 SOP（triage→verify→fix→notify→log）+ 【勘誤通知】格式 SSOT     |
| [SPORE-HARVEST-PIPELINE](SPORE-HARVEST-PIPELINE.md)                                    | 讀者孢子留言入口（5-Bucket Classifier）+ Chrome MCP reply 機制            |
| [MAINTAINER-PIPELINE](MAINTAINER-PIPELINE.md)                                          | contributor issue/PR 勘誤入口                                             |
| [REWRITE-PIPELINE Step 0.2-bis](REWRITE-PIPELINE.md)                                   | callout-triggered 全 EVOLVE 時的拆除防火牆（callout 不進觀點/正文）       |
| [FACTCHECK-PIPELINE](FACTCHECK-PIPELINE.md)                                            | Stage 2 查證引擎（4 關 + Quick/Full mode）                                |
| 協作記憶 `project_error_boundary_traceability`（private，不在 repo）                   | 哲學層：可追溯→更正 / 杜撰→撤回（已收斂進本檔第一性原理）                 |
| 協作記憶 `feedback_reply_url_encode` / `feedback_chrome_threads_text_input`（private） | reply 落地機制（repo 內 canonical = 本檔 §4.4 + SPORE-HARVEST Pitfall 6） |

---

## Stage 1：TRIAGE（分類）

**分桶之前不行動**（reuse [SPORE-HARVEST 5-Bucket Classifier](SPORE-HARVEST-PIPELINE.md)）。先問兩層：

### 1.1 這個 callout 本身對嗎？（先 falsify 讀者）

預設讀者對是健康反射，但**不是免驗證**。讀者級事實（在地人秒懂的：方向、站名、人物關係、獎項屆次）正是 research agent 抓不到、讀者抓得到的層（[REFLEXES #16](../semiont/REFLEXES.md)），所以讀者通常對——但仍要跨源查（無名小卒讀者說「不是 BBS」其實錯了；太空中心 12 條 callout 有 1 條「晉陞 CTO」查無公開佐證不採）。

### 1.2 這是哪一類錯？→ 處置

| 類別                  | 訊號                                                 | 處置                                                                                                     | 對外？      |
| --------------------- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ----------- |
| **可追溯事實錯**      | 史實/數字/時序/方向錯，有來源可驗                    | VERIFY → FIX 修正 → NOTIFY                                                                               | ✅ 公開更正 |
| **場景推導錯**        | 從英文摘要/想像推導的具體細節（時間/地點/交通/方向） | 同上（no-scene-inference 規則 canonical → [RESEARCH.md §六](../editorial/RESEARCH.md) + EDITORIAL v4.4） | ✅          |
| **杜撰/無源**         | 人/引語/事件查無 live 源，本來就不該存在             | **撤回（retract）** 該 claim/段/篇                                                                       | ✅ 說明撤回 |
| **詮釋/立場/framing** | 不是事實錯，是價值判斷/政治立場質疑                  | **defer 哲宇**（§自主權邊界），不自動修                                                                  | ⏸️ 等拍板   |
| **callout 本身錯**    | 讀者記錯/誤解                                        | 禮貌澄清（仍查證後）                                                                                     | ✅ 溫和說明 |

### 1.3 急迫度：severity × reach × D+N

- **D+0 ≤6hr acute**：traceable factual → **30 min 內 fix + 通知**（Error Boundary = Traceability，[SPORE-HARVEST](SPORE-HARVEST-PIPELINE.md)）。
- **reach ≥ 50K**：觸發 [retroactive FACTCHECK Quick Mode](SPORE-VERIFY.md) 主動驗 3-5 atom（reach 越大讀者分散式 audit 壓力越大）。
- reach 不是 fix 觸發條件，**traceability + acute window 才是**（美食總覽 2.5K views 仍 30 min fix）。

---

## Stage 2：VERIFY（查證）

委派 [FACTCHECK-PIPELINE](FACTCHECK-PIPELINE.md) Quick（3-5 atom）或 Full（A 級/大爭議）。鐵律：

- **跨 3+ 獨立來源**，中文事實用中文原頁 Ctrl-F 逐字，**禁從英文摘要回譯**（毒樹果實鏈，[REFLEXES #23](../semiont/REFLEXES.md)）。
- **同時查 callout 跟原文**：原文可能對、讀者可能錯，也可能兩邊都有料。
- **清單外連帶修**：修一處時 audit 鄰近同類錯（太空中心：讀者點 10 條，連帶抓出 3 個沒點名的腳註錯綁）。
- **跨語言 + 跨文章健檢**（per [REFLEXES #73 (e) 外部注意力聚光燈](../semiont/REFLEXES.md)）：這條錯誤有沒有同時活在 (a) 本文其他語言版本（`knowledge/{lang}/` 對應譯文同一事實段）(b) 有反向連結指回本文、內容提到同一事實的 sibling article？外部關注天然只照到活躍位置——讀者點名一處時，順手一次掃完比等下次全站巡邏才發現同一個錯散在別處信噪比高一階。命中一併修，寫進同一個 commit。
- **無法溯源 → 不寫/撤**：查無 live 源的事實不放進每句要可追溯的文章（龜山島山羊 udn 已 404 → HELD；謝甫宜老師查無此人 → 撤）。

---

## Stage 3：FIX（修正）

- **只改 `knowledge/`**（SSOT），不碰 `src/content/`（投影層，下次轉錄覆蓋）。
- **外科手術，非全文重寫**：好文只修錯點（[神經迴路「好文不需全重寫」](../semiont/MEMORY.md)）。連帶把鄰近同類錯一起修。
- **commit 格式**：`🧬 [semiont] heal: {slug} — {factual layer} 勘誤 per @{reader} callout`（git log 留痕 = 可追溯性的物理基礎；偷改不留痕 = 信任違反）。
- **杜撰 → 撤回非更正**：claim 本來就不該存在的，刪掉該句/段（不是改寫成另一個版本）。
- **callout-triggered 全 EVOLVE** → 走 [REWRITE Step 0.2-bis 拆除防火牆](REWRITE-PIPELINE.md)：callout 只進 Stage 1 查證、用完即丟，**不進 Stage 0.6 觀點、不進正文**；觀點 blind to errata（避免「不要搞錯名字」變成文章脊椎 + 正文撒校正焦慮句，影視配樂第二輪教訓）+ Step 3.2-bis backstop 自檢「這句只為回應過去錯誤而存在嗎？是→刪」。

---

## Stage 4：NOTIFY（通知 / 回覆）

改了文章**必須**對外指出更正（否則 reader 不知後續，traceability 斷）。兩種格式：

### 4.1 【勘誤通知】正式格式（v1.0 canonical，2026-06-24 哲宇 directive）

獨立、明顯的更正（重要事實錯、標題錯、或想正式記錄的）用這個格式。語氣**正式但不客服腔**（像《報導者》的更正欄，不是「造成不便敬請見諒」的罐頭）：

```
【勘誤通知】
{一句：哪篇/哪則貼文 + 哪裡錯，特此更正}

正確版本：{正確的事實}
更正說明：{為什麼會錯 / 關鍵 nuance}（選填，幫讀者理解不是隨便寫的）

{文章已更正的範圍說明}。感謝 @{reader1}、@{reader2} 等{在地/領域}讀者指正。

已更正全文 👉 {percent-encoded 文章 URL}
🧬
```

**worked example（龜山島方向勘誤，本 pipeline 誕生案例）**：

```
【勘誤通知】
這篇龜山島貼文（以及文章開頭）寫「從雪隧開出來往右一瞄」就看見龜山島，方向標示有誤，特此更正。

正確方向：開車往南、朝宜蘭方向駛出雪山隧道時，龜山島在左手邊的海上；只有往北、離開宜蘭時，它才會出現在右側。原文寫的是「回家」的情境，卻標成了離開的方向。

文章開頭與結尾均已更正，並加註了行進方向的差別。感謝 @mingzeke、@thisismoin0212 等多位在地讀者即時指正。

已更正全文 👉 https://taiwan.md/geography/%E9%BE%9C%E5%B1%B1%E5%B3%B6/
🧬
```

### 4.2 隨手 inline reply（5 鐵律，reuse [SPORE-HARVEST Reply Tone Discipline](SPORE-HARVEST-PIPELINE.md)）

快速回單一留言用這個（短、口語、平輩）：

| #   | 鐵律                   | 對                                    | 錯                                     |
| --- | ---------------------- | ------------------------------------- | -------------------------------------- |
| 1   | 認錯第一句             | 「你抓得對」「方向我寫反了」          | 「其實我的意思是…」「但文章也有提到…」 |
| 2   | 具體 anchor 不空泛     | 「往南回宜蘭，龜山島在左手邊的海上」  | 「謝謝指正，會改善」                   |
| 3   | 指向 fix（URL encode） | 「文章已更正：taiwan.md/%E9%BE%9C…/」 | 「我們會研議」/ 中文 path 不 encode    |
| 4   | 不卑不亢，平輩語氣     | 「你」「我」                          | 「您」「敝庫將參酌」                   |
| 5   | 🧬 收尾不打廣告        | 結尾單獨 🧬                           | 「歡迎追蹤！」                         |

### 4.3 反 pattern（兩種格式都禁）

- **紅線焦慮洩漏**（協作記憶 `feedback_red_line_anxiety_leak`）：「我們嚴格遵循官方來源」「絕對沒有杜撰」——reader 不關心你怎麼自我約束，只要文章改對。
- **客服腔/晶晶體**（協作記憶 `feedback_contributor_reply_humanize`）：「感謝您寶貴的回饋」「cross-validation/canonical」。
- **防衛**：「來源寫的，不是我的問題」。

### 4.4 管道落地

- **孢子留言（Threads）**：Chrome MCP，JXA NSPasteboard + Cmd+V（多段）或 execCommand insertText（短；機制 canonical → [SPORE-HARVEST Pitfall 6](../factory/SPORE-HARVEST-PIPELINE.md)）；post-ship verify pressable-count diff（max 1 retry）。X reply Chrome MCP 不支援 → 手動。
- **contributor issue**：`gh issue comment`，用 contributor 母語。
- **文章內**：重大更正可在文章加更正註（選擇性）。

---

## Stage 5：LOG（記錄）

- 孢子勘誤 → spore blueprint §Ship log 加「🔴 D+N 勘誤」條（posted spore body 不可改，記錄差異）。
- session memory 記勘誤事件 + **teach（抽可複用教訓）**：這類錯下次怎麼防。
- pattern 級教訓 → LESSONS-INBOX（vc 累積）；達閾值 distill 到 REFLEXES/MANIFESTO。

---

## 📋 過去案例表（pipeline 長在真實案例上）

| 案例                  | 錯什麼                                              | 類別               | 處理                                    | 教訓 / canonical                                       |
| --------------------- | --------------------------------------------------- | ------------------ | --------------------------------------- | ------------------------------------------------------ |
| 李洋 #29 (4/14)       | 清晨四點搭捷運(MRT 6am 才開)/兩千萬→一千萬/杜撰引語 | 場景推導+數字+杜撰 | 19hr 公開更正 marathon                  | 公開更正版 12% engagement=信任訊號；no-scene-inference |
| 草東 #33              | 貝斯手名字錯                                        | 讀者級事實         | 修+回                                   | 讀者級事實強制查（即使 high_confidence）               |
| 壞特 #45 (D+2 65K)    | 兩階段醫師國考                                      | 可追溯事實         | 修原文 9 處                             | reach 大→reader 分散 audit                             |
| 林琪兒                | USAFA 大三 hallucination                            | 杜撰               | 修 5 處 + 補 footnote                   | spore prep 反向 audit article                          |
| 美食總覽 #97 (5/27)   | 1949 美軍嘉義火雞                                   | 可追溯史實         | T+30min fix+commit+push+reply           | D+0 acute traceability loop；reply URL 要 encode       |
| 太空中心 #1139 (6/12) | 在軌數/接任日/真因 12 條                            | 可追溯（含1不採）  | 10 採 1 不採 + 連帶修 3 沒點名腳註      | callout 一半價值在清單外；無源 claim 不寫              |
| 影視配樂 (6/01)       | 作曲家↔作品誤植（2 輪）                             | 可追溯 + 校正焦慮  | EVOLVE + Teardown Firewall              | callout 不進觀點/正文（Step 0.2-bis）                  |
| 嘻哈饒舌 (6/09)       | 寶哥=宋岳庭（合成層杜撰同位語）                     | 杜撰 gloss         | de-quote                                | orchestrator 詮釋 gloss 也是 claim 要驗                |
| 無名小卒 (6/14)       | 站名「無名小卒」幻覺                                | 杜撰 + callout半對 | 修「無名」+ 撤；讀者「不是BBS」也錯     | stage2-quote-context-collapse；falsify callout         |
| 天下 #134 (6/13)      | 棗紅色 verbatim                                     | 可追溯             | footnote heal                           | 孢子查證反向 audit 源文 mis-attribution                |
| 迷音 #142 (6/16)      | 標題 sub judice 寫成已定罪                          | 可追溯（標題）     | 去罪化                                  | 事實紀律含標題非只內文                                 |
| 王力宏 / 馬英九       | 家族關係鏈 / 「清廉」評價詞                         | 詮釋/讀者級        | hedge + 政治 pre-ship review            | 政治人物評價要 hedge（REFLEXES #16）                   |
| 謝甫宜老師 (6/19)     | 不存在的人物（pre-ship 抓到）                       | 杜撰               | 撤（不選為錨）                          | falsification-first；無源不寫                          |
| **龜山島方向 (6/24)** | 出雪隧「往右」看龜山島（應往左）                    | 在地空間方向       | 開頭+結尾 右→左 + 方向註 + 【勘誤通知】 | **本 pipeline 誕生案例**；在地方向綁行進方向           |

---

## 跟其他 pipeline 的分工（一句話）

- 寫之前防錯 = [FACTCHECK](FACTCHECK-PIPELINE.md)（4 關查證）+ [REWRITE Stage 3](REWRITE-PIPELINE.md)（事實鐵三角）。
- 寫之後收錯 = **本檔**（端到端勘誤）。
- 讀者留言入口 = [SPORE-HARVEST](SPORE-HARVEST-PIPELINE.md)（5-Bucket）→ Bucket A/C 委派本檔。

---

_v1.0 | 2026-06-24 龜山島-rewrite — 誕生於龜山島孢子「出雪隧往右看龜山島」方向勘誤（@mingzeke / @thisismoin0212 + monolab D+0 callout）。哲宇 directive：【勘誤通知】正式格式 + 建勘誤 pipeline 參考過去所有案例。把散在 SPORE-HARVEST（5-Bucket + Error Boundary + Reply 5 鐵律）/ REWRITE（0.2-bis 防火牆）/ FACTCHECK / 6 feedback memory / 16 worked case 的勘誤 SOP 收斂成單一 canonical + 新增【勘誤通知】格式。對應 [REFLEXES #15 反覆浮現要儀器化] + project_error_boundary_traceability。_
