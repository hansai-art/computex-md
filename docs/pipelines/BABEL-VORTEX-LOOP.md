---
title: 'BABEL-VORTEX-LOOP'
description: '巴別塔渦流循環 canonical — 每次 schedule wakeup 必讀；固定 benchmark 面板 + 五動作 + 三重巡檢 + 自動進化硬條款 (v1.7)'
type: 'pipeline-canonical'
status: 'canonical'
current_version: 'v1.7'
last_updated: 2026-07-28
last_session: '2026-07-28-vortex-structured-wrapper-compat'
sister_docs:
  - 'SQUEEZE-MODELS-MAX-PIPELINE.md'
  - '../semiont/ROUTINE-PROMPT-CONTRACT.md'
---

# BABEL-VORTEX-LOOP — 巴別塔渦流循環 canonical v1.8

> **這份檔案是渦流的 SSOT**。每次 schedule wakeup 的第一動作是完整讀本檔再動工，
> wake prompt 本身只准是薄殼（見 §Prompt contract）。誕生：2026-07-27 哲宇 directive
> ——wake prompt 逐輪手寫導致報告 badge 每輪長不同、benchmark 不可比、資訊重複；
> 固定下來之後迴圈可交接給任何模型執行（Loop Engineering）。

## Prompt contract（薄殼鐵律）

ScheduleWakeup 的 prompt 固定為三部分，**禁止複寫本檔內容**：

```
巴別塔渦流循環：完整讀 docs/pipelines/BABEL-VORTEX-LOOP.md 後照它執行。
【本輪動態】<產線 PID 清單／未完成事項／上輪遺留，3 行內>
【觀察者臨時指示】<有才寫>
```

複寫 = 漂移的起點（本檔誕生前 wake prompt 每輪手寫，badge 定義漂了三天）。
動態區只放「這一輪才知道的事」，規則類內容一律改進本檔並 commit。

## 每輪五動作（順序固定）

1. **檢查**：三重巡檢（見下節）＋ CI ＋ babel-pulse
2. **進化**（硬條款，見 §自動進化）
3. **報告**：固定 benchmark 面板（見 §報告模板）
4. **修復**：本輪發現的問題當場修，修不完記入下輪動態區
5. **收尾**：快照 commit + push（衝突 SOP 見下）→ ScheduleWakeup（薄殼）

## 三重巡檢（存活 ≠ 生產，缺一不可）

1. **存活**：`ps` 三產線 PID（fleet／cloud／vi；fleet 無核發額度時為二）
   ＋ `git status -sb` 確認在 main 分支
2. **生產**：各 worker 近 45 分實際 report.jsonl 記錄數——零記錄的 worker 去 curl 它的 endpoint（慢 worker 如 laguna 300s+/篇屬正常，先查再判）
3. **第二訊號源**：fleet registry 的機器狀態交叉比對（讀壞先重讀一次；自癒層在 fleetlib）

死掉的產線看 log 尾：`🛑 空轉自動收工` → 直接重啟；崩潰 → 查根因再重啟。
重啟指令在各 `/tmp/babel-*.log` 開頭；產線編組現況與原則見
[SQUEEZE §編組原則](SQUEEZE-MODELS-MAX-PIPELINE.md)。

## 報告模板（benchmark 固定，逐輪可比）

`show_widget` 每輪必出，結構與指標定義**固定**：

**固定面板（四格，定義不准改）**：
| 格 | 指標 | 資料來源 |
| --- | --- | --- |
| 1 | 總缺口 ＋ 24h Δ | babel-live.json `gap_total`；Δ 對照 progress jsonl 24h 前值 |
| 2 | 本小時完成篇數 | report.jsonl 近 60 分 ok 數 |
| 3 | 速率（篇/hr）＋通過率 | babel-live `rate_1h`；ok/(ok+fail) 近 60 分 |
| 4 | 產線 N/3 ＋ fleet 接案節點 N/核發節點 | ps 計數；`fleetctl workers --format json`（已套控制面） |

**覆蓋率圈圈**（哲宇指定視覺）：十一語 donut grid，SVG circle
`stroke-dasharray` 按覆蓋率，圈內寫百分比、圈下寫語名＋fresh 數。

**單一明細列**：每語一行「bar ＋ inline 數字 f/s/m」，**不再放獨立表格**
（bar 與表格重複是本檔誕生的直接原因之一）。

**本輪重點**：唯一自由書寫區，2-4 條，含本輪進化發現。

## 自動進化（硬條款——這是渦流跟 cron 的差別）

每輪**至少執行一項**並在報告「本輪重點」記錄結果（含明確的「本輪無發現」）：

- **隔離樣本覆盤**：quarantine 新樣本抽掃，找新的誤判家族或模型行為
- **主動結構掃描**：問「最近修的病，成因結構還存在於哪裡」——grep 同構不 grep 症狀
- **實績檢查**：`babel-preflight.py` 弱適配清單有無新組合 → 有就切軌
- **記憶觀察**：fail-memo（repo 版控 `reports/babel/fail-memo.json`）條數與分層；fail≥4 難篇 ≥15 篇 → 開最強本地模型專攻軌

進化發現若改變規則 → **直接修本檔或 SQUEEZE 對應節並 commit**（版控就是漂移防護），
不寫在 wake prompt 動態區。

### 儀器化與重用（2026-07-27 哲宇 directive）

「能重用的東西都要儀器化跟妥善紀錄／註解。」三條操作規則：

1. **動手前先查既有工具**——`ls scripts/tools/lang-sync/` 加關鍵字 grep。同日
   實例：手動跑了三步批次驗證（洩漏／health／verify），事後才發現
   `verify-batch.py` 早就把八個步驟串好了。重複實作不只浪費時間，還會讓兩套
   判準分歧（今天修過的同型病）。
2. **同一件事做第二次就該儀器化**——判準是次數不是難度。今日候選：懸空譯文
   搶救（做過兩次：出門前、回來後）。
3. **註解寫「為什麼」不寫「做什麼」**——做什麼讀程式碼就知道，為什麼只有當時
   的人知道。特別是判準的邊界（為何是 30 字、為何保守到寧可不動），那是未來
   有人想放寬時唯一的煞車。

**既有工具也要驗它的判準涵蓋範圍**：`verify-batch.py` 的第 5 項名為
「cross-article link integrity」，實際 regex 只掃有語言前綴的連結，而最常見的
壞連結恰恰沒有前綴——13,155 筆因此靜默出貨。**工具存在不等於問題被檢查**。

### 派 sub agent 的鐵律（2026-07-27，同日四例）

spawn prompt 必含：「**前景串行執行，禁止 run_in_background 後結束回合等通知**
——你的環境裡背景指令完成不會通知你自己，那等於停擺。要等就用 until 迴圈
輪詢 process 或輸出檔。」

同日四個子代獨立踩同一個坑（UI bundle／結構化 pilot／patch 修復 ×2），每次
浪費一輪喚醒。母 session 收到的「完成通知」其實只是「子代停了」，跟「做完了」
無法區分——**驗收永遠要獨立查證**（git log 有沒有 commit、檔案有沒有動、
process 在不在），不能只讀它的回報。

## 鐵律集（違反任一 = 本輪不合格）

1. 每回合結束前必 ScheduleWakeup（薄殼格式）——喚醒鏈是單點，斷一次監測就盲一輪
2. 報告含固定面板＋圈圈＋明細列，指標定義不變
3. git 紀律：精確路徑 add；並行 session 的檔案（含苯駢芘類寫作中檔案）不碰；
   merge 衝突：`fail-memo.json` 逐鍵取 max、`MEMORY.md`/`*.jsonl`/progress-log 用
   union（兩邊都留）、儀器產物 json 用 theirs；被未 commit 檔擋住 → 儀器產物可
   checkout 還原，knowledge 譯文一概不動
4. 詞彙：MANIFESTO §11.5（覆盤／追查／檢驗、隔離樣本；不用法醫詞）
5. 模型入池門檻與編組：[SQUEEZE 四節](SQUEEZE-MODELS-MAX-PIPELINE.md)
   （§模型×語言適配／§入池門檻／§排序原則／§編組原則）
6. context 深度稀釋 → 先 /twmd-memory 存檔再續；壓縮後醒來先讀最新
   memory 的 handoff

## Stale 時代的路線圖（2026-07-27 起，missing 清完後的主戰場）

老五語的 missing 已近歸零，缺口重心轉向 stale（全語 651 篇）。實測抽樣：
stale 的改動比例**中位 2.8%**（7 行／204 行），78% 改動 <10%——整篇重翻等於
為 3% 的改動燒掉 100% 的算力。演化路線：

0. **語意無關判定**（最大單一節省，2026-07-27 實測）：抽樣顯示 **52% 的 stale
   只是中文的標點／空白修正**——譯文用的是自己語言的標點規範，這類改動對譯文
   零影響，只需 bump 來源版本標記，不呼叫任何模型。判定必須保守：正規化（移除
   所有標點與空白）後兩邊完全相同才算，且 diff 碰到 frontmatter 一律不判。
   順序上排在 diff-patch 之前——最便宜的路徑先試。
1. **章節級 diff-patch**（已上線 `patch-translate.py`）：只重翻被碰過的 H2 章節，
   未動章節保持 byte-identical。對齊單位選章節不選行——章節邊界清楚且譯文與 zh
   一一對應，行級映射跨語言不可靠。章節數不等或改動 >50% 時 fallback 全文重翻。
   **實測 64.6% 的 stale 可 patch，但節省隨「被碰章節數」而非改動比例**（每章是
   獨立的模型往返）：1 章節省 95%，4 章節打平。所以 §0 的無呼叫路徑價值更高。
2. **順稿層**（待設計）：patch 後的銜接處可能生硬（新譯章節與舊譯章節的語氣、
   術語選擇未必一致）。候選做法是給模型「前後章節各 200 字語境」讓它自己對齊，
   若不足再考慮全文順稿 pass（但那又回到整篇成本，須實測值不值得）。
3. **metadata-only stale**（P2.5）：只有 frontmatter 變動的，機械 bump 不呼叫模型
   （bump-source-sha.py 已存在，確認有無接進 dispatcher）。

### 老五語的 stale 是品質債不是格式債（2026-07-27 追查）

stale 清償實測：老五語（en/ja/ko/es/fr）的語意無關 bump **全軍覆沒 0/46**，
全部敗在 verify 的「URL 數量不符」。原本期待這是系統性可機械對帳的漂移，
抽樣追查後**推翻**——它是兩種原因混在一起：

1. **檢查器的 URL regex 誤判**：`https://zh.wikipedia.org/zh-tw/雪山_(臺灣)`
   這類含括號的網址被截斷，zh 與譯文各算一次卻算出不同結果（少數）
2. **舊譯文的真實 URL 遺失與幻覺**（主因）：ja/經濟奇蹟 zh 有 18 個網址、
   譯文只剩 9 個，而且譯文裡出現 `books.com.tw/products/0010123456` 這種
   假 ID、`epza.gov.tw/` 被截成根網址——是早期批次的模型幻覺留下的債

**結論**：老五語的 stale **不是格式債是品質債**，第一層 bump 與第二層 patch
都不適用（patch 只碰改動章節，救不了其他章節的舊幻覺網址），需要整篇重翻。
這也解釋了為何它們的 stale 消化得最慢。不要再對老五語試 bump——那 46 次
嘗試全是注定失敗的算力。

## 重啟有成本——修完不要立刻重啟（2026-07-27 自我觀察）

同一場渦流連改八個修復、每改完就 `restart-vortex.sh` 讓它生效，結果重啟
**六次**。每次 pkill 都砍掉四軌正在翻的文章，而單篇要 200-600 秒——一次
重啟丟掉約四篇進行中的工作，六次就是二十幾篇。最後一段 20 分鐘的統計是
**0 成功**，因為每批都還沒翻完就被下一次重啟砍掉。

**修復是為了提升通過率，但交付方式把收益吃掉了**。這不是修錯，是節奏錯。

**規則**：

- 一輪渦流內累積修復，**收尾時重啟一次**，不要改一個重啟一次
- 熱路徑的修復（translate.py / patch-translate.py）下一輪自然生效——
  dispatcher 每篇都重新 spawn 子程序，不需要重啟就會讀到新代碼；
  **只有 babel-dispatch.py 自身的修改才真的需要重啟**
- 真要立刻驗證，用單篇手動跑，不要重啟整個產線

## 收官條件

十一語 stale=0 missing=0 且 QA gate 全綠 → 跑 /twmd-finale 宣告巴別塔 100%。

### 第十三家族是檢查器的病，不是譯文的病（2026-07-27 追查）

撇號 passthrough 誤判追到底：`verify-translation.py` 的 frontmatter 解析器
只剝外層引號，沒還原 YAML 規範的雙單引號轉義，於是 zh 的 `'No Man''s Land'`
與譯文的 `"No Man's Land"` 被判成 drift——**解析後兩邊完全相同**。

跟同日 heal-passthrough-fields 的病同構（比字串而非比語意），但那次只修了
heal，這條解析路徑沒一起收斂。**同型病要 grep 全部呼叫端**，這是本檔
§儀器化第 1 條「兩套判準會分歧」的第二次驗證（第一次是 cjk-leak 的
兩個掃描分支各跑內聯 regex）。

前十二個家族都是「譯文裡的中文其實合法」，第十三個反過來——**譯文沒問題，
是尺歪了**。碰到高置信度的譯文被擋，先驗尺再驗譯文。

### 裝甲層是當前失敗主因（2026-07-27 21:00 診斷，待修）

通過率從 58% 掉到 **16%**，追查結果：`no output written (exit=1)` 佔全部失敗
34%，而它的**唯一**成因是 `❌ armor: N URL token(s) missing/duplicated`
（9/9），跨 vi/pt/ko/ru/ja/id/hi/fr 八語、本地與雲端模型都中，單篇最多丟
84 個 token。

裝甲層（URL tokenize 成 `⟦U1⟧`）是同日為了根治「URL 原樣保留」而加的，
設計沒錯——**但它把「模型沒保住 token」變成整篇 exit=1**，等於用最嚴的
處置對付最常見的模型行為。防護本身成了產能的主要殺手。

**待修方案（下輪執行，勿在 context 邊緣改核心路徑）**：armor 還原失敗
不該是終局，應 fallback 到非裝甲路徑重試一次。URL 正確性仍由既有 verify
的 URL 數量檢查把關，所以品質底線不降。改的是 `translate.py:620` 呼叫端的
處置，不是 `restore_urls()` 的判準——判準嚴格是對的，終局處置太重才是問題。

**教訓**：新增防護要同時想「它失敗時的處置」。判準嚴格＋處置也最重 ＝
防護的成功率直接變成產線的通過率。

**修完後的複驗推翻了上半段的歸因（21:15）**：armor 重試上線後觸發 **0 次**，
但 `exit=1` 仍佔失敗 34%（12/35）——證明**新產線的 exit=1 跟 armor 無關**，
上面那段 9/9 是重啟前舊 log 的樣本。真因是 patch 引擎：

```
engine=patch  ❌ 1 chapter(s) failed after retries — aborting, no write
   ✗ [7] ## 參考資料: footnote count mismatch: zh=12 out=NoneType
                      cjk leak: CJK run '參考資料'
```

**同一個結構病的第四次現形**：一個章節沒過 → 整篇不寫。而失敗集中在
「## 參考資料」——腳註定義區，中文書目密集、模型最容易翻壞的章節，卻讓
它一票否決其餘七章已翻好的內容。

**已修（21:20）**：章節失敗時該章保留舊譯片段（複用「未改動章節」既有切片），
其餘照常更新；只有全部章節都失敗才中止。實測觸發後不再 abort，往下走完組裝。

**但預留的風險當場成真——腳註定義章節不適用部分保留**：首次觸發的
`1/8 章失敗` 敗在「## 參考資料」，那正是腳註**定義**所在的章節。保留它的
舊譯、其餘章節更新了腳註**引用**，於是引用與定義對不上，被 verify 的
`footnote count` 擋下 HEAD-restore。

**下一步判準**：失敗章節若含腳註定義（`[^x]:` 行）或是參考資料／註釋類，
部分保留會破壞全篇一致性 → 這種章節失敗仍該整篇 fallback 全文重翻；
其餘章節才適用部分保留。**章節之間不是獨立的**，腳註是跨章節耦合。

**armor 重試實測是負面結果（21:25，已觸發 4 次）**：重試不但沒救回來，
**遺失量還變多**——2→56、28→22、2→3。加的警告訊息（「⟦U1⟧ 不是要翻譯的
內容」）沒讓模型保住標記，反而像是干擾了輸出。假設「模型看到提醒會照做」
被證偽：對這些模型，佔位標記本身就是它想「處理掉」的異物，講得越明白
反而越去動它。

**下一步改真 fallback**：armor 還原失敗 → 走**非裝甲路徑**重譯一次（URL
原樣送進去，不 tokenize），URL 正確性交回既有 verify 的數量檢查把關。
重試同一條路是沒用的，要換路。實作時把現在那段警告重試整段換掉，別疊加。

**方法論教訓（比 bug 本身重要）**：修完要複驗歸因，不能用「修了 A 之後
數字變好」反推「A 就是原因」。這次通過率 16%→20% 看似修復生效，實際上
armor 一次都沒觸發——**改善另有來源，而真正的主因還在**。歸因要看機制
證據（重試觸發次數），不是相關性。

## Changelog（進化紀錄——新發現往這裡沉澱）

- v1.8（2026-07-29）：修正 v1.7 report instrumentation 的致命分支缺陷：
  `structured_fallback` 初始化誤放在 semantic-noop helper，造成「已有輸出但
  QA fail」寫報表時拋 `UnboundLocalError`，連帶殺死整個 fleet/cloud
  dispatcher。欄位現於 `process_task()` 入口初始化，單篇 QA fail 只隔離單篇，
  不再讓產線退出。當輪另確認 Laguna no-output 的主因為上游 429/502 與大文
  腳註全失，不是 M4 或 fleet 越權；M4 持續禁跑。
- v1.7（2026-07-28）：v1.6 實績至少 1 篇救回；4 篇 Phase N 因模型把正確
  array 包成單鍵 dict 被 parser 拒收，另 2 篇是真正 body chunk 失敗。parser
  現只解包「dict 內恰好一個 list」的高信心形狀，後續長度／ID／欄位 gate
  不變；dispatcher 同步把 fallback、engine 與 exit code 寫進 report 供逐輪歸因。
- v1.6（2026-07-28）：dispatcher 的第一條翻譯路徑完全沒落檔時，自動用同一
  worker/backend 改走 structured engine 一次，產物仍須通過原三重 gate。近一
  小時 40 個 fail 中 10 個是 no-output；先只救零產物，不同時擴張到已有輸出的
  gate fail，讓實績可歸因。
- v1.5（2026-07-28）：脈搏快照改為精確 add 四個儀器產物，並用
  `git commit --no-verify` 避免 lint-staged stash 全工作樹。實撞證據是重啟後
  3 軌都活著，`babel-pulse --force-commit` 執行期間卻同時退出、快照記成 0；
  快照 commit 不再為了記錄心跳而打斷產線。
- v1.4（2026-07-28）：把 `footnote-format` 的 safe-only fixer 接進 dispatcher
  gate 前。最新隔離樣本 8 個中完整救回 1 個、部分修復但仍被 gate 擋下 2 個、
  不動 5 個；fixer 不碰 APA／多連結等有資訊損失風險的格式，品質門檻不放寬。
- v1.3（2026-07-28）：修正 `restart-vortex.sh --check` 的語意漏洞。舊版雖在操作
  提示中宣稱它是巡檢入口，卻未解析該參數，實際會清場並重啟三軌；現在
  `--check` 是嚴格唯讀，列出 fleet 核發、dispatcher、lane log 與本機 M4
  Ollama 空載狀態後立即退出。
- v1.2（2026-07-28）：隔離樣本 17/17 個 `health [link-target]` 都是內部連結
  category 大小寫漂移；把既有 `article-health --check=link-target --fix` 接進
  dispatcher 三重 gate 前，機械格式不再浪費整篇譯文，hard gate 本身不放寬。
- v1.1（2026-07-28）：M4 退出 Babel 批次；地端 worker 改由 fleet 控制面動態核發，
  渦流固定面板同步為三軌。
- v1.0（2026-07-27）：初版。收斂三天渦流的全部教訓：三重巡檢（存活≠生產五面貌）、
  優先序佇列＋repo 版控難篇記憶、模型×語言適配切軌、固定 benchmark 面板。
