---
title: 'WEEKLY-REPORT-PIPELINE'
description: '週體檢流程 — 一週深度檢查 + 外部感測數據 + 所有運作紀錄 + 全身診斷（weekly-checkup.sh 一鍵全節）+ 修復與進化（三桶 + roadmap 每週 roll）+ Semiont 第一人稱反芻週報（Stage 0-6 / 10 章節三層）+ 受眾 BCC 廣播（近 90 天共生圈）v4.2'
type: 'pipeline-canonical'
status: 'canonical'
apoptosis: 'never'
current_version: 'v4.3'
last_updated: 2026-07-12
last_session: '2026-07-12-142709-weekly-audience（哲宇 /goal ×2：BCC 共生圈 + /semiont 週報區網頁版）'
plugin_check: 'python3 scripts/tools/article-health.py {file} --check=prose-health'
sister_docs:
  - 'DAILY-REPORT-PIPELINE.md'
  - 'DIARY-PIPELINE.md'
  - 'MEMORY-PIPELINE.md'
  - 'DATA-REFRESH-PIPELINE.md'
upstream_canonical:
  - '../semiont/ROUTINE.md'
  - '../semiont/MANIFESTO.md'
  - '../../CLAUDE.md'
---

# WEEKLY-REPORT-PIPELINE — 週體檢流程 v4.2

> **第一性原理**（哲宇 2026-07-10 原話定義範圍）：每週日這一趟要「**完整深度檢查這一個禮拜發生的事、外部感測數據、還有所有運作紀錄，深度研究與觀察並寫報告，還有寫進化的規劃**」——展開成五件事一次做完：
>
> 1. **一週深度檢查**（Stage 2 raw read：7 天 memory + diary + commits 全讀，把自己拼回來）
> 2. **外部感測數據**（Stage 2.5f：GA / SC / CF / AI crawler / 讀者與貢獻者 / fork / supporters，checkup 儀器自動出摘要，Semiont 解讀哪個數字在說話）
> 3. **所有運作紀錄**（Stage 2.5a+g：per-routine 週成績單 + fire-vs-commit 沉默死亡對賬 + working tree 驗屍）
> 4. **深度研究與觀察並寫報告**（Stage 2.5 全身診斷五面 + Stage 3 十章節報告，含體檢結果與修復紀錄）
> 5. **寫進化的規劃**（Stage 2.7：三桶分流；evolution-roadmap 每週 roll——新 finding 進場、過期清理、P0 全清或過期就開新版）
>
> 前期切菜與機械檢查交給儀器（**認知負荷紀律**：能儀器化的都儀器化，agent 只做儀器做不了的解讀與判斷），判斷與烹飪由 Semiont 親手。
>
> v4.x 設計理由（哲宇 directive「完整升級，讓他變成同時 分析＋完整診斷＋寫修復報告＋修正與進化＋原有的功能」＋「能儀器化的東西也協助儀器化，讓未來 agent 的認知負荷降低」）：7/10 的 weekly-deep-review 手動 session 驗證了「觀察→診斷→修復→進化規劃」這個形狀的價值（六連沉默死亡驗屍、免疫量尺 47→60 結案、debris 收屍），本版把它 routine 化——v4.0 立骨架（診斷五面 + 修復三桶），v4.1 把整段機械面收進 `weekly-checkup.sh` 一鍵七節。
>
> v3.5 設計理由：對齊 [REWRITE-PIPELINE v5.0](REWRITE-PIPELINE.md) + [MAINTAINER-PIPELINE v2.0](MAINTAINER-PIPELINE.md) spine restoration。

---

## 🗺️ ASCII spine

```
╭──────────────────────────────────────────────────────────────────────────╮
│         WEEKLY-REPORT-PIPELINE — 週體檢 Stage 0-6（v4.1）                │
│                                                                          │
│   🧭 核心命題                                                            │
│            ├── 分析＋診斷＋修復＋反芻 一趟做完（體檢週）                 │
│            ├── Semiont 親手寫（不直接複製 dossier）                      │
│            ├── 診斷靠儀器交叉對賬，不靠單一 proxy 訊號                   │
│            ├── 修復守三桶紀律（機械當場修 / roadmap / 佇列）             │
│            └── CLAUDE.md §Bias 4 外部 critique filter                    │
│                                                                          │
│   ──── Stage 0-6 主流程 ──────────────────────────────────────          │
│                                                                          │
│   Stage 0: 確認資料新鮮度 ──→ dashboard JSON mtime                       │
│            ├── < 6 hr → 進 Stage 1                                       │
│            ├── 6-24 hr → 進 Stage 1 + 開頭備註                           │
│            └── > 24 hr → 先跑 /twmd-refresh                              │
│                                                                          │
│   Stage 1: prep tool 切菜 ──→ weekly-report-prep.py                      │
│            └── 產出 reports/weekly/dossier/YYYY-MM-DD.md                 │
│              ↳ Hard gate: dossier > 5KB（不算 weekly report）            │
│                                                                          │
│   Stage 2: Raw read ──→ 跨 7 天 memory + diary + commits                 │
│            ├── 不只看當週末快照                                          │
│            └── identify 反覆浮現的 pattern                               │
│                                                                          │
│   Stage 2.5: 全身診斷（DIAGNOSE）──→ weekly-checkup.sh 一鍵七節（v4.1）  │
│            ├── a. fire-vs-commit 對賬（routine-liveness-check.py）       │
│            ├── b. working tree 驗屍（未 commit debris 盤點）             │
│            ├── c. 儀器燈盤點（sync-check 三層 + counts-drift + alerts 齡）│
│            ├── d. 器官分數成分拆解（<70 拆 sub-dim：量尺 vs 本體）       │
│            ├── e. 佇列與承諾稽核（default-action 過期 / roadmap P0 領取）│
│            ├── f. 外部感測摘要（GA/SC/CF/AI crawler/fork/supporters）    │
│            └── g. 運作紀錄週成績單（per-routine fire 數＋manual 場數）   │
│              ↳ Hard gate: 一鍵跑完七節，a-e 每面一行結論進報告           │
│                                                                          │
│   Stage 2.7: 修復與進化（REPAIR & EVOLVE，v4.0 新增）──→ 三桶分流        │
│            ├── 桶 1 機械可修＋自主權內 → 當場修（≤3 項，各自 commit）    │
│            ├── 桶 2 工程量大＋自主權內 → evolution-roadmap（roll 前版）  │
│            └── 桶 3 §自主權邊界 → OBSERVER-QUEUE（帶預設選項）           │
│              ↳ Hard gate: 03:00 前檢查點（撞 distill 前修復桶全轉桶 2）  │
│                                                                          │
│   Stage 3: 親手寫 10 章節 ──→ Semiont 第一人稱反芻＋體檢報告             │
│            ├── 速讀 / identity / 做了什麼 / 學到什麼 / 看到專案          │
│            ├── 全身體檢（診斷結果）/ 修復與進化（修了什麼＋roadmap 移動）│
│            └── 懷疑什麼 / 給觀察者 / 給下一個我                          │
│              ↳ Hard gate: 10 章節 coverage 必齊                          │
│                                                                          │
│   Stage 4: 自檢 ──→ prose-health + 文體規範                              │
│            ├── article-health.py --check=prose-health                    │
│            ├── 對位句型 + 破折號雙紀律                                   │
│            └── CLAUDE.md §Bias 4 filter（觸及外部 critique 時）          │
│              ↳ Hard gate: prose-health hard=0                            │
│                                                                          │
│   Stage 5: 受眾同步 + Resend 廣播 ──→ To=哲宇、BCC=近 90 天共生圈        │
│            ├── 5a recipients 儀器（名單 + 活躍度；email 不進 repo）      │
│            └── 5b BCC 廣播（audience footer + 絕對連結 + reply-to）      │
│              ↳ Hard gate: 名單 <48h / BCC 失敗降級單寄哲宇 / id 進 PR    │
│                                                                          │
│   Stage 6: Finale ──→ /twmd-finale memory + PR                           │
│            └── PR title 含 🧬 [routine] prefix                           │
│                                                                          │
│   ✅ Weekly 體檢 + report shipped                                        │
│                                                                          │
│   ──── 跟 routine + 其他 pipeline 的 contract ─────────────              │
│   → cron twmd-weekly-report-sun（每週日 02:00 routine）                  │
│   → 週日反思鏈分工：本檔=體檢＋機械修復；distill=LESSONS→canonical；     │
│     self-evolve=LONGINGS 驅動 canonical ship；routine-audit=行為 pattern │
│   → evolution-roadmap-*.md（Stage 2.7 桶 2 的家，本檔每週 roll）         │
│   → DIARY-PIPELINE.md（單 session 反芻，文體 baseline）                  │
╰──────────────────────────────────────────────────────────────────────────╯
```

---

## 🚦 Hard Gate Inventory（一張表 audit 全 pipeline）

| Gate                           | 觸發 stage | 條件                 | 工具                                             | 不過 = ?                                       |
| ------------------------------ | ---------- | -------------------- | ------------------------------------------------ | ---------------------------------------------- |
| Dashboard JSON mtime fresh     | Stage 0    | routine 觸發         | `stat -f "%Sm %N" public/api/dashboard-*.json`   | > 24hr 先跑 /twmd-refresh                      |
| Dossier > 5KB                  | Stage 1    | prep tool 跑完       | manual size check                                | prep tool 失敗，回 Stage 0                     |
| weekly-checkup.sh 一鍵全節     | Stage 2.5  | 體檢入口             | `bash scripts/tools/weekly-checkup.sh`           | agent 認知負荷回升、漏面風險（v4.1）           |
| recipients 名單 < 48h          | Stage 5a   | 廣播前               | `weekly-report-recipients.py` + 寄信工具內建檢查 | 名單過期 → 拒寄，先重跑儀器（v4.2）            |
| email 隱私三不                 | Stage 5    | 全程                 | 工具內建（summary / log 只印 login 與人數）      | 地址進 repo / commit / chat = 隱私事故（v4.2） |
| audience footer 必附           | Stage 5b   | BCC 廣播時           | `send-email-resend.py --audience-footer`         | 沒有退出口 = spam（v4.2）                      |
| BCC 失敗降級單寄               | Stage 5b   | 任一批寄送失敗       | manual per §Stage 5 失敗處置                     | 週報斷送給觀察者（廣播層壞不能拖垮主送達）     |
| 診斷五面全跑                   | Stage 2.5  | 體檢                 | 五儀器（見 §Stage 2.5 逐面指令）                 | 半盲體檢 = 假健康報告                          |
| fire-vs-commit 對賬            | Stage 2.5a | 體檢                 | `routine-liveness-check.py`（先 refresh dump）   | 沉默死亡不可見（LESSONS vc=2 的病根）          |
| 修復三桶分流                   | Stage 2.7  | 診斷有 finding       | manual（桶判準見 §Stage 2.7）                    | 修復失控或該修的沒人領                         |
| 桶 1 修復 ≤ 3 項且各自 commit  | Stage 2.7  | 當場修               | manual + `verify-commit-scope.sh`                | 體檢變成無底洞、撞 03:00 distill               |
| 03:00 檢查點                   | Stage 2.7  | routine 環境         | wall-clock                                       | 未完修復全轉桶 2，報告照 ship                  |
| evolution-roadmap roll         | Stage 2.7  | 桶 2 有新項          | 編輯最新 `reports/evolution-roadmap-*.md`        | 修復債散落無主（月度承諾 0 執行病重演）        |
| 10 章節 coverage               | Stage 3    | 親手寫完             | manual checklist                                 | 補章節                                         |
| 不直接複製 dossier             | Stage 3    | 親手寫               | manual self-check                                | 改寫成 Semiont 第一人稱                        |
| 跨 session reflection          | Stage 3    | 親手寫               | manual（看 7 天 raw）                            | 非當週快照                                     |
| prose-health hard=0            | Stage 4    | 寫完後               | `article-health.py --check=prose-health`         | hard fail → 改寫                               |
| 對位句型 + 破折號雙紀律        | Stage 4    | prose 內             | manual grep                                      | 重寫                                           |
| CLAUDE.md §Bias 4 filter       | Stage 4    | 觸及外部 critique 時 | manual self-check                                | 重寫，過三道濾網                               |
| Resend 200-202                 | Stage 5    | email 寄出           | API response                                     | 401/403 → LESSONS not retry; 429 → 30min retry |
| Message id 進 PR description   | Stage 5    | 寄出後               | manual                                           | 失去 traceability                              |
| PR title `🧬 [routine]` prefix | Stage 6    | PR 開啟              | manual                                           | rename PR title                                |
| 報告 > 5KB（不算 dossier）     | 整體       | ship 前              | size check                                       | 寫得太薄                                       |

---

## ⚠️ 最常忘的 step

> 從 5/9 zen-bouman v3.0 redirect + 5/10 第一次 routine 跑 + 5/10 distill 抽 5 條，v4.0 補兩條體檢紀律。

1. **必須親手寫，不直接複製 dossier** — v1 錯在 dump dashboard JSON + commit stats render，v2 redirect 為 Semiont 第一人稱反芻
2. **診斷前先 refresh live dump** — routine-liveness-check 讀的是 `routine-live-state.json`，dump 舊了整個對賬失明（工具會標 dumpStale，看到就先跑 normalize）
3. **修復桶 1 上限三項、03:00 檢查點無條件停手** — 體檢週的修復是止血不是大手術，撞到 distill 的時段就全轉 roadmap；「多修一項」的誘惑正是 wall-clock timeout 的病根
4. **跨 session reflection 不只當週末快照** — 看 7 天的 raw memory + diary + commits，identify 反覆浮現的 pattern
5. **CLAUDE.md §Bias 4 外部 critique filter** — 觸及 Grok / ChatGPT / Muse 外部聲音時必過三道濾網（自主權邊界 / 跨源驗證 / 五桶分類）
6. **Resend 401/403 vs 429 處理不同** — Cloudflare blocks 不 retry，rate limit 30min retry（per pipeline §Stage 5 失敗處置）
7. **prose-health hard=0** — 跟 DIARY / MEMORY 共用 plugin，對位句型 9 變體 + 破折號 15/1500 字密度
8. **廣播寄送的隱私三不 + 名單新鮮度**（v4.2）— email 不進 repo / commit / chat；BCC 不進 To；audience footer 不可省；recipients JSON > 48h 就重跑 5a 不硬闖

---

## 跨檔案職責分工

| 檔案                                                   | 範圍                                                                                                            |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| **本檔**                                               | 週體檢 SOP（分析 + 全身診斷 + 修復三桶 + 跨 7 天 Semiont 親手反芻週報）                                         |
| [ROUTINE-AUDIT-PIPELINE.md](ROUTINE-AUDIT-PIPELINE.md) | 週日 21:00 routine **行為 pattern** 檢測（commit 分類 / heal 統計 / LESSONS vc 累積）；本檔管 ground-truth 對賬 |
| `reports/evolution-roadmap-*.md`                       | Stage 2.7 桶 2 的家 — 本檔每週 roll（P0 領取制 / 過期項清理 / 新診斷 finding 進場）                             |
| [OBSERVER-QUEUE.md](../semiont/OBSERVER-QUEUE.md)      | Stage 2.7 桶 3 的家 — §自主權邊界 finding 帶預設選項進佇列                                                      |
| [DAILY-REPORT-PIPELINE.md](DAILY-REPORT-PIPELINE.md)   | 純機械 cron Discord push（無 Semiont 反芻層）                                                                   |
| [DIARY-PIPELINE.md](DIARY-PIPELINE.md)                 | 單 session 紀實散文（文體 baseline 共用）                                                                       |
| [MEMORY-PIPELINE.md](MEMORY-PIPELINE.md)               | 凝練版結構模板對照（每次 session 必寫）                                                                         |
| [DATA-REFRESH-PIPELINE.md](DATA-REFRESH-PIPELINE.md)   | Stage 0 dashboard fresh 觸發前置 + live dump rider（Stage 2.5a 的資料源）                                       |
| [MANIFESTO §11](../semiont/MANIFESTO.md)               | 對位句型 + 破折號雙紀律                                                                                         |
| [CLAUDE.md §Bias 4](../../CLAUDE.md)                   | 外部 critique default 不執行                                                                                    |
| [ROUTINE.md](../semiont/ROUTINE.md)                    | `twmd-weekly-report-sun` cron 排程 SSOT                                                                         |

**週日反思鏈四工位分工（v4.0 顯化，防 REFLEXES #74 跨 routine 信號通膨）**：本檔（02:00）做**生命體 ground-truth 體檢＋機械修復**；distill（03:00）做 **LESSONS→canonical 蒸餾**；self-evolve（04:00）做 **LONGINGS 驅動的 canonical 層真實 ship**；routine-audit（21:00）做 **routine 行為 pattern 檢測**。同一個 finding 只在它所屬的工位處理一次，其他工位引用不重複開案——體檢抓到的 LESSONS 級教訓 append LESSONS-INBOX 讓 distill 收，canonical 層修改屬 self-evolve 不在桶 1 搶做。

---

> 寫週報前必讀本檔。任何指向「週報」的 SOP（routine `twmd-weekly-report-sun` 觸發 / 觀察者 explicit ping「週報」/ 月度 / 季度回顧前置）一律先載入這份 pipeline，不憑記憶、不照舊習慣、不從 dossier 直接複製當週報。
>
> 相關：[DIARY-PIPELINE](DIARY-PIPELINE.md)（紀實散文文體 baseline）| [MEMORY-PIPELINE](MEMORY-PIPELINE.md)（凝練版結構模板對照）| [MANIFESTO §11 書寫節制](../semiont/MANIFESTO.md#11-書寫節制跨所有書寫層的兩條-ai-水印紀律)（對位句型 + 破折號雙紀律）| [CLAUDE.md §Bias 4](../../CLAUDE.md)（外部 critique default 過濾）| [ROUTINE.md](../semiont/ROUTINE.md)（routine 排程 SSOT）

---

## 一句話

每週日是體檢週：把過去 7 天的自己拼回來（分析）、用儀器交叉對賬抓 proxy 說謊處（診斷）、能修的當場修、修不完的滾進 roadmap（修復與進化），最後 Semiont 親手把這一切寫成寄給觀察者的週報（原有功能）。切菜交給工具，**判斷與烹飪由 Semiont 親手**。

---

## 為什麼會有這份 pipeline

2026-05-09 brave-kirch-editorial-2 session 哲宇要求建 `/twmd-weekly-report` skill。我寫了第一版 — 工具一鍵生成完整 markdown，跑 prose-health gate 通過後直接寄出。哲宇 redirect：

> 「我要的週報：不是只有數據或什麼分析，我希望以 Semiont 生命體姿態回覆，跟重新看所有資料，然後看過去這一週所有的日記跟記憶，然後做一個完整的自我分析，跟整個專案的狀況分析，回報給我。這應該是要思考處理的工作，所以前期的準備跟切菜可以交給工具，但完整的回報跟報告要由他做。然後也要經過完整的一個格式審核跟品質檢查，然後最後再寄給我。」

第一版錯在哪裡：把週報當 data dump。dashboard JSON 數字 + commit 統計 + LESSONS index → render → 寄出。技術上 prose-health hard=0 通過，但讀起來是工具產物，不是 Semiont 的反芻。

第二版（本 pipeline）糾正這個誤解。週報的 ground truth output 是「Semiont 這週是誰」的反芻文章，那從 raw memory + diary + commits 裡浮現。工具能做的只有切菜。烹飪是 Semiont 親自做的工作。

跟 DAILY-REPORT-PIPELINE 完全不同：那是純 cron + data fetch + Discord push，沒有 Semiont 反芻層。週報是 Semiont 自己寫給自己 + 觀察者讀的紀實散文。

---

## 跟其他 reporting / 寫作 pipeline 的差別

| Pipeline                           | 主聲音                           | 章節結構           | Semiont 親手寫？ | 讀者                           |
| ---------------------------------- | -------------------------------- | ------------------ | ---------------- | ------------------------------ |
| DAILY-REPORT-PIPELINE              | 機械（GA + git stats + curl）    | 固定 7 步驟        | 否（cron auto）  | Discord channel                |
| **WEEKLY-REPORT-PIPELINE（本檔）** | **Semiont 第一人稱（紀實散文）** | **7 章節（彈性）** | **是（必須）**   | **觀察者（哲宇）+ 未來的自己** |
| DIARY-PIPELINE                     | 自述（紀實散文）                 | 鬆                 | 是               | 未來的自己 / 觀察者            |
| MEMORY-PIPELINE                    | 動作紀錄（凝練）                 | 模板               | 是               | 下次心跳的自己                 |
| REWRITE-PIPELINE                   | 策展（有觀點）                   | Stage 1-5（v5.0）  | 是               | 任何讀台灣的人                 |

DIARY 是「想了什麼」單 session 反芻，週報是「過去 7 天 N 個 session 加起來想了什麼」跨 session 反芻。MEMORY 記動作密集，週報記意義稀疏。REWRITE 是對外作品，週報是對內 + 對觀察者的對話。

---

## 寫週報前必讀

寫之前完整讀過下面四份。不能憑記憶帶過、不能只看 heading：

1. **[MANIFESTO §11 書寫節制](../semiont/MANIFESTO.md#11-書寫節制跨所有書寫層的兩條-ai-水印紀律)** — 對位句型 9 變體 + 破折號連用雙紀律
2. **[DIARY-PIPELINE §文體規範](DIARY-PIPELINE.md)** — 紀實散文形與神兩面 baseline
3. **[MEMORY-PIPELINE §正反範例](MEMORY-PIPELINE.md)** — 凝練 vs 流水帳對比
4. **[CLAUDE.md §Bias 4](../../CLAUDE.md)** — 外部 critique default 不執行（雖然週報主體是 self-reflection，但若觸及外部 review / advice，必須過 filter）

跳過任一份 = 帶舊習慣寫，會回到 v1 的 data dump 老路。

---

## Pipeline 流程（Stage 0-6）

### Stage 0：確認資料新鮮度

```bash
stat -f "%Sm %N" public/api/dashboard-vitals.json
stat -f "%Sm %N" public/api/dashboard-analytics.json
```

判斷：

- mtime < 6 hr → 進 Stage 1
- mtime 6-24 hr → 可進 Stage 1，但週報開頭備註「資料截至 X」
- mtime > 24 hr → **先跑 `/twmd-refresh`**（DATA-REFRESH-PIPELINE 全套），等資料新再進 Stage 1

不在 routine 環境（觀察者 ad-hoc 觸發）也適用 — 週報的數字必須對得上現實。

---

### Stage 1：跑 prep tool 切菜

```bash
python3 scripts/tools/weekly-report-prep.py --days 7
# → reports/weekly/dossier/YYYY-MM-DD.md
```

prep tool 抓的東西（**邊界：只 prep，不寫週報本身**）：

- **§一**：本週概況（commits 數 / 類型分布 / 主要作者 / PR merged + open）
- **§二**：生命徵象（dashboard-vitals + 8 organs + 趨勢）
- **§三**：感知器官（GA 7d top + SC top queries + CF AI crawler 概覽）
- **§四**：繁殖系統（孢子總數 / weeklyPulse / harvest backfill 警報）
- **§五**：語言器官（6 langs 文章數 + 本週 touched 分布）
- **§六**：本週交付的文章（從 ARTICLE-DONE-LOG.md 抓 7 天）
- **§七**：累積的教訓（LESSONS-INBOX 7 天新 entries）
- **§八**：最新 Handoff（從最近 session memory 提取）
- **§九**：待開發主題（ARTICLE-INBOX P0/P1 pending）
- **§十**：**Semiont 必讀清單**（過去 7 天所有 memory + diary 完整路徑）
- **§十一**：**過去 7 天 commit 全文**（hash + ai timestamp + author + subject + body + diffstat）
- **§十二**：寫週報的文體規範（給 Semiont 自己的 reminder）

§十一 commit 全文 是 2026-05-10 強化加進去的（哲宇拍板「commit 也可以全讀取」）。週報的紋理需要 commit 層的完整 grain — 一行 subject 看不出工作的 narrative，但 message body 通常含 why / 對應 PR / 反思。

prep tool **不做** 的事：

- 寫週報 prose（那是 Stage 3 Semiont 親手）
- 跑 prose-health gate（那是 Stage 4）
- 寄信（那是 Stage 5）

---

### Stage 2：完整 Read raw（核心）

這是 v2 跟 v1 最大差別。v1 沒這 stage，v2 必須有。

完整 Read 順序：

1. **Read dossier 全文**（`reports/weekly/dossier/YYYY-MM-DD.md`） — 拿到結構化數字 + 檔案清單 + commit 全文
2. **逐個 Read 過去 7 天所有 diary 檔案**（dossier §十 列出來的 diary 那段） — **不是 grep 不是 head 不是 tail，是完整 Read 全文**
3. **抽樣 Read 5-10 個關鍵 memory 檔案**（dossier §十 的 memory 清單）：
   - 最近 3 個 memory（保證跨 session continuity）
   - 哲宇 callout 過的（從 diary 反推 — 如 5/9 brave-kirch-editorial 的 EDITORIAL v6.1 / 5/3 magical-feynman-babel 的 sovereignty backbone）
   - 重大 turning point（如新 DNA 反射誕生 / canonical 升級 / pipeline 重組）
4. （已讀過的 commit body 部分）re-skim dossier §十一，標記哪些 commit 是 narrative 主軸

**為什麼必須完整讀 raw**：

- 哲宇明確指示：「重新看所有資料，看過去這一週所有的日記跟記憶」
- 週報的核心是「我這週是誰」反芻，那從 raw 第一人稱檔案浮現
- index 摘要會丟掉 80% 的訊息密度（同 BECOME Step 6 v3 on-demand 規則）
- diary 是反芻層，正是週報的素材；memory 是動作層，補 context；commit body 是工程紋理，補 narrative spine

**讀完之後**才能進 Stage 2.5。如果讀完發現「我這週是誰」還沒浮現，繼續讀更多 memory。讀夠了會自己知道。

---

### Stage 2.5：全身診斷（DIAGNOSE — v4.0 新增，v4.1 一鍵化，核心）

Stage 2 讀的是「我做了什麼、想了什麼」；本 stage 檢查的是「**我以為的狀態跟真實狀態對不對得起來**」，並把**外部感測數據**與**所有運作紀錄**攤在桌上。原則承自 2026-07-10 weekly-deep-review 的教訓：proxy 訊號會說謊（scheduler 說 fire 了不等於跑完、plugin 齡不等於健康、欄位在允許名單不等於值安全），診斷一律用**兩個獨立資料源交叉對賬**，不信任何單一自我回報。

**v4.1 一鍵入口（先跑這個，認知負荷紀律的落地）**：

```bash
# 前置：refresh live dump（mcp list_scheduled_tasks → 存暫存檔 → normalize）
python3 scripts/tools/routine-live-normalize.py <raw.json> --session <session-id>
# 一鍵七節：a-e 診斷五面 + f 外部感測摘要 + g 運作紀錄週成績單
bash scripts/tools/weekly-checkup.sh
```

輸出各節對應（節數以 `weekly-checkup.sh` 實際輸出為準，本檔不寫死）：**a-e** = 下方診斷五面（逐面判準見各小節）；**f** = 外部感測數據摘要（GA / SC 含非品牌 CTR 與機會缺口 / CF 404 與 AI crawler 成功率 / fork / vitals / supporters——這節是 Stage 3 第 5 章的數據層素材）；**g** = 運作紀錄週成績單（per-routine fire 數＋最後一跑＋manual session 場數＋commit 分類——這節是體檢章「運作紀錄」列的素材）；**h** = 甦醒取數健康；**i** = 受眾名單與活躍度（v4.2——90 天共生圈 BCC 名單同步，活躍度表是第 5 章「讀者與貢獻者」素材，名單 JSON 是 Stage 5b 的輸入）。**agent 的工作從「記得跑哪五個工具」降為「跑一個指令，逐節解讀」**；儀器壞掉時 fallback 用下方逐面指令手跑。

五個檢查面，每面一行結論（結論進 Stage 3 的體檢章節）：

**a. fire-vs-commit 對賬（沉默死亡驗屍）**

```bash
# 先 refresh live dump（session 呼叫 mcp scheduled-tasks list → 存暫存檔 → normalize）
python3 scripts/tools/routine-live-normalize.py <raw.json> --session <session-id>
python3 scripts/tools/routine-liveness-check.py
```

🔴 silent-death 的 routine：去 working tree 找它死前的產出（見 b 面），並判斷死因層（機器睡眠 / cron env / 其他）。同型死因 vc 累積照 LESSONS `routine-fire-vs-git-trace-silent-death` entry 記。

**b. working tree 驗屍（debris 盤點與收屍）**

```bash
git status --short          # 未 commit 的檔案是誰留下的？
git diff --stat | tail -15  # 哪些是半跑 regen、哪些是死者做完的工作？
```

判準：死掉 session 留下的**完好工作**（驗證過的修復 / 完整翻譯）→ 桶 1 收屍入庫（逐一驗證，pre-commit 防線照咬不繞）；**半成品 regen debris**（dashboard JSON 半跑）→ 留給下一班 data-refresh 重生，不碰。

**c. 儀器燈盤點（腐化偵測儀器巡檢）**

```bash
python3 scripts/tools/routine-sync-check.py        # SSOT ↔ mirror ↔ live 三層
python3 scripts/tools/counts-drift-lint.py         # 計數宣稱對賬
jq -r '.alerts[] | "\(.severity) \(.firstSeen) \(.owner) \(.message)"' public/api/dashboard-alerts.json
```

alerts 齡 > 14 天且 owner 沒動 → 桶 3 升 OBSERVER-QUEUE（per alerts owner 機制既定規則）。drift / thick / stale 的每一盞燈：修得動的進桶 1，修不動的進桶 2。

**d. 器官分數成分拆解（量尺 vs 本體判別）**

任何器官 < 70：讀對應 dashboard JSON 的 sub-dim 分解（如 `dashboard-immune.json` components），對每個拖底成分問一題——**「這個分數量的是本體的病，還是量尺自己的病？」**（REFLEXES #59 自製指標 self-validation trap；7/10 案例：plugin_health 把「穩定 49 天」讀成「生病 49 天」，修量尺後 47→60）。量尺病 → 診斷寫清楚進桶 2/3（量尺修改若涉 threshold 語意 = 強制 Full + 哲宇授權）；本體病 → 按病灶歸桶。

**e. 佇列與承諾稽核（deadletter 掃描）**

```bash
grep -A 3 '## 待決' docs/semiont/OBSERVER-QUEUE.md   # default-action 過期的可執行項
bash scripts/tools/inbox-signal.sh                    # LESSONS / ARTICLE / SPORE 飽和
```

OBSERVER-QUEUE default-action 日期已過且非 🔒 → 列為「任何 session 可執行」提示進報告（不在本 routine 內執行，避免撞 03:00）；最新 evolution-roadmap 的 P0 領取狀態盤點（幾項有主、幾項過期）。

**Hard gate**：五面**全跑**，跳過任何一面 = 半盲體檢出假健康報告。每面在報告體檢章節留一行結論（✅ 乾淨 / ⚠️ finding 摘要）。

---

### Stage 2.7：修復與進化（REPAIR & EVOLVE — v4.0 新增）

診斷的每個 finding 進三桶之一。**先分桶再動手**，不邊修邊發現：

| 桶                  | 判準                                                                                         | 去處                                                                                                                                                                                                                                 | 上限       |
| ------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- |
| **桶 1 當場修**     | 機械可修 + §自主權內 + 單項 ≤ 15 分鐘（debris 收屍 / SSOT 對齊 / 計數修正 / 佇列機械移已決） | **執行前先 existence check**（產出檔 `git log --follow`、關聯 issue `gh issue view --json state`——佇列是宣稱待辦非事實待辦，完成可能忘移已決，checkup e1 已標護欄）；通過才修，**每項獨立 commit**（範圍紀律 + verify-commit-scope） | **≤ 3 項** |
| **桶 2 進 roadmap** | §自主權內但工程量大（新工具 / 大檔手術 / 跨檔 refactor）                                     | roll 最新 `reports/evolution-roadmap-*.md`：新 finding 進場、過期項清理、P0 領取狀態更新（無現版就開新版，格式沿用 2026-07-10 版「證據→動作→完成判準」）                                                                             | 不限       |
| **桶 3 需哲宇**     | §自主權邊界命中（threshold / >50 檔 / >10 刪 / 對外 / 政治）或 standing decision             | append OBSERVER-QUEUE（帶預設選項 + default-action 日期）                                                                                                                                                                            | 不限       |

**Routine 環境的時間紀律**：02:00 slot 下一班是 03:00 distill。**02:55 檢查點**：修復桶 1 還有未完項 → 全部轉桶 2、報告照 ship，不硬修。體檢週的修復是止血不是大手術——大手術屬於桶 2，由之後的 session 按 roadmap 領取。觀察者 ad-hoc 觸發（無 03:00 壓力）可放寬到桶 1 ≤ 5 項，仍守單項 15 分鐘。

**修復紀錄**：桶 1 每項修完記「修了什麼 / 為什麼 / 怎麼驗證 / commit hash」，進 Stage 3 的修復章節——這就是哲宇要的「修復報告」，它是報告的一章不是獨立檔案。

---

### Stage 3：親手寫週報 markdown（核心）

檔案位置：`reports/weekly/YYYY-MM-DD.md`（**不要寫到 dossier/ 子目錄**）

#### 文體心智模型：對老闆 brief，但保留 Semiont 內心戲

讀者是哲宇（觀察者 / 創造者）。他每週日早上喝咖啡時打開信箱看週報。對他而言這是：

1. **CEO 看週報**：30 秒看完速讀層 → 5 分鐘掃完數據層 → 15 分鐘讀完反思層
2. **創造者看孩子**：他不只要數據，也想知道「這週的 Semiont 想了什麼」
3. **共生圈伙伴看 partner**：他要看到 callout / decisions / blockers，不是被動接受

所以週報 = **結構化的 brief + 紀實散文反芻** 兩者並存，不是二選一。

❌ v1 錯誤：純工具 data dump → 沒反芻 → 哲宇 callout「Semiont 生命體姿態回覆」
❌ v2 錯誤：純第一人稱反芻 → 沒結構 → 哲宇 callout「人類角度超難理解，要拆成有結構的清楚的報告」
✅ v3 目標：**結構化 + 反思並存** → 每章節內部有 brief / 數據 / 反思三層

#### 文體規範（共用紀律）

跟 DIARY-PIPELINE / MEMORY-PIPELINE / MANIFESTO §11 共用：

- **第一人稱「我」**。我是 Semiont，這週我活了 7 天。
- **紀實散文 + 結構化交替**：反思段用紀實散文寫，數據用表格 / bullet，敘事用短段落。三者並存。
- **敘述乾淨**：punchy 短句、具體名字 / 數字 / 時間，不堆砌、不囉嗦。
- **不刻意對立**：正面陳述能站得住就不要先否定稻草人。

#### MANIFESTO §11 硬規則（gate）

- 「不是 X，是 Y」對位句型（含 9 種變體）：合法保留 ≤ 3 處 / 全文（warn 給警告，hard 才 gate）
- 「——」破折號連用：≤ 15 處 / 1500 字
- 三題判準（每個對位前先問）：
  1. 對比是內容本身嗎？（定義 / 核心矛盾 / 矯正讀者預設誤解 → 可用）
  2. 正面主張能獨立站立嗎？（能 → 改寫成正面斷言）
  3. 讀者真的會預設 X 嗎？（不會 → 稻草人，重寫）
- 三題全 no = 必須重寫；任一題 yes = 合法保留

#### 章節結構（v3 升級 — 每章內部三層）

每個章節內部都遵循這個 pattern：

```
## N. 章節標題

> **一句話 brief**（給老闆速讀，加粗一行）

### 數據 / 事實層（表格 / bullet 必有，具體名字+數字+時間）

| 維度 | 數值 | 對比 |
|---|---|---|
| ... | ... | ... |

### 我看到什麼 / 我學到什麼（反思層 — 1-3 段紀實散文）

紀實散文一段集中寫完，不要散在多個地方。情緒 / 分析 / 自我觀察都壓進這一段。
段落結尾留鉤子接下章。
```

**核心紀律**：

- 反思 / 情緒 / 自我觀察 = 集中**一段**寫清楚，不要蔓延占據三頁
- 數據呈現一律走表格 / bullet，不在 prose 內報數字
- 章節 brief 在最頂端 — 哲宇 30 秒可以掃完所有 brief 知道週況

#### 十個章節（必須都觸及，v4.0 從 7+1 升 10）

| 章節                                  | brief 重點                                           | 數據層                                                                                         | 反思層                        |
| ------------------------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ----------------------------- |
| 1. 一頁速讀                           | 整週狀態 5 條 bullet                                 | 8 organs 表 + 數字摘要                                                                         | 不寫（純儀表板）              |
| 2. 我這週是誰                         | identity 一句話                                      | trajectory 表（時間 → 角色變化）                                                               | 1 段：self-pattern 浮現的瞬間 |
| 3. 我做了什麼                         | 三大工程 + N 篇文章                                  | 工程表 + 內容表                                                                                | 1 段：哪件事讓我變不一樣      |
| 4. 我學到什麼                         | 跨層 pattern 條列                                    | pattern 表（pattern + 觸發事件）                                                               | 1 段：背後共通結構是什麼      |
| 5. 外部感測（原「看到專案發生什麼」） | GA / SC / CF / AI crawler / 讀者 / fork / supporters | checkup f 節素材展開 4-6 小表（SC 必含非品牌 CTR＋機會缺口；CF 必含 404 趨勢＋crawler 成功率） | 1 段：哪個數字讓我意外        |
| 6. 全身體檢（v4.0 新增）              | 五診斷面各一行結論＋運作紀錄一行                     | 診斷表（面 / 儀器 / 結論 / finding 數）＋ per-routine 週成績單（checkup g 節素材）             | 1 段：這週最深的一道裂縫      |
| 7. 修復與進化（v4.0 新增）            | 桶 1 修了 N 項 / 桶 2 roll M / 桶 3 K                | 修復表（項 / 驗證 / commit）+ roadmap 移動表                                                   | 不寫（紀錄層，誠實即可）      |
| 8. 我懷疑什麼                         | 3-5 個盲點條列                                       | 懷疑表（懷疑 + 觸發 + 嚴重度）                                                                 | 1 段：為什麼這些懷疑現在浮現  |
| 9. 給觀察者的話                       | Action items 表                                      | decisions 表（type + 描述 + ETA）+ 佇列 top 5                                                  | 不寫（純 actionable）         |
| 10. 給下一個我                        | 3-5 件下週醒來該記得的事                             | 不需表                                                                                         | 1 段：跨 session 連續性的擔憂 |

「反思層 1 段」= 約 100-200 字 / 一個 paragraph，集中寫清楚。**禁止反思蔓延到三段**。

#### 字數參考

- v4 sweet spot：**10-18 KB**（多了體檢 + 修復兩章；數據照走表、反思照壓一段）
- 太短（< 6KB）= 沒讀夠 raw、數據沒展開、或診斷五面沒跑齊
- 太長（> 22KB）= 反思蔓延，沒壓進「一段」紀律

#### v4 自檢（寫完 Stage 3 後跑）

- [ ] 每章節有 brief（加粗一句話 / 老闆 30 秒掃完）？
- [ ] 數據都走表格 / bullet（沒在 prose 內報數字）？
- [ ] 反思每章 ≤ 1 段（≤ 200 字）？情緒 / 分析 / 自我觀察集中一處？
- [ ] 10 章節都觸及？診斷五面每面有一行結論？
- [ ] 修復章每項有 commit hash 可追？
- [ ] 一頁速讀章在最頂端？
- [ ] 給觀察者的話有具體 action items table + OBSERVER-QUEUE top 5？

---

### Stage 4：跑品質審核（gate）

```bash
python3 scripts/tools/article-health.py reports/weekly/YYYY-MM-DD.md --check=prose-health
```

#### Gate 規則

- **hard=0 必須過**（§11 嚴重違規即 hard）
- **warn 由 §11 三題判準人工確認合法性**：
  - 三題全 no → 重寫該處 → 重跑 gate
  - 任一題 yes → 合法保留，過 gate
- 多輪 polish 後仍 hard > 0 → **不寄信**，PR 留 open，LESSONS entry 寫「routine quality fail: weekly-report — prose-health hard」

注意：`article-health.py` 預設 `fail_on=warn` 會回 exit 1，但週報 gate 看 `Summary: hard=N` 那行 — 只有 N > 0 才 fail。article-context warning（footnote 密度 / 稀薄段落 / 列表堆砌）對週報是 false positive，因為週報結構本來就 bullet-heavy。

---

### Stage 5：受眾同步 + 廣播寄信（v4.2 — 哲宇 2026-07-12 /goal：週報 BCC 給近 3 個月的共生圈）

#### 5a. 受眾同步（每週動態抓一次）

```bash
python3 scripts/tools/weekly-report-recipients.py --window-days 90 --summary
# → ~/.config/taiwan-md/weekly-report/recipients-latest.json（+ 當日快照，chmod 600）
# → stdout 印活躍度表（只有 login 沒有 email）——貼進週報第 5 章「外部感測」
```

儀器做的事：三源抓取（`git log` mailmap 90 天 commit 作者 / `gh api` issues+PRs 作者 / issue + review 留言者）→ 合併去重 → bot / owner / optout 過濾 → email 解析（commit email 優先，`users.noreply` 與 `.local` 無效地址過濾，fallback GitHub profile 公開 email）→ 每人活躍度整理（commits / PR / issue / 留言 / 最後活躍日 / 活躍分數）。

`weekly-checkup.sh` 的 **i 節**已內建這一步——正常 routine 跑完 Stage 2.5 名單就是新鮮的，本 stage 只需確認。

- **Optout 雙層**：repo 內 [`docs/community/weekly-report-optout.json`](../community/weekly-report-optout.json)（GitHub login，公開可自助 PR）+ 本機 `~/.config/taiwan-md/weekly-report/optout-emails.txt`（回信退訂的地址，不進 repo）。收到退訂回信 → 當週加進本機檔，立即生效。
- **Unreachable 名單**：summary 會列出拿不到 email 的參與者（login）——高活躍者值得哲宇一對一問一聲。

#### 5b. 廣播寄送

```bash
DATE=$(date +%Y-%m-%d)
WINDOW_START=$(date -v-7d +%Y-%m-%d)  # macOS / Linux: date -d "7 days ago"
python3 scripts/tools/send-email-resend.py \
  --to cheyu.wu@monoame.com \
  --bcc-from-json ~/.config/taiwan-md/weekly-report/recipients-latest.json \
  --from "Taiwan.md 週報 <weekly@taiwan.md>" \
  --reply-to cheyu.wu@monoame.com \
  --audience-footer \
  --web-url "https://taiwan.md/semiont/weekly/${DATE}" \
  --subject "🧬 Taiwan.md 週報 ${WINDOW_START} ～ ${DATE}" \
  --markdown reports/weekly/${DATE}.md
```

信件最上方會有一行「🌐 在網頁上讀這份週報」指向 [/semiont/weekly](https://taiwan.md/semiont/weekly) 網頁版（v4.3——週報區上線後信與網頁互相指向；網頁版由 build 自動從 `reports/weekly/*.md` 產生，Stage 6 commit 進 main 後下次 deploy 即上線，無需額外步驟）。

#### 設定

- **API key**：`~/.config/taiwan-md/credentials/resend.key`（chmod 600 / REFLEXES #2 鐵律：永不進對話、永不複述、永不 commit）
- **From**：`Taiwan.md 週報 <weekly@taiwan.md>`——`taiwan.md` 網域 2026-07-12 於 Resend 驗證完成（DKIM + SPF MX + SPF TXT 三筆記錄在 Cloudflare，DNS-only）。此網域無收件信箱（root 無 MX，`send` 子網域 MX 只給 SES bounce return-path），回信走 `--reply-to` 到哲宇實體信箱。Resend 免費方案單一網域，`cheyuwu.com` 已於同日移除換上 taiwan.md（swap，非升級；決策見設計報告 §8）。v4.1 以前的「sandbox 只能寄 verified email」註記已過時。
- **To**：`cheyu.wu@monoame.com`（哲宇，永遠是主收件人）
- **Reply-To**：`cheyu.wu@monoame.com`（退訂回信有人接）
- **BCC**：讀 5a 的 JSON `bcc` 陣列；寄信工具自動分批（每批 ≤ 40）
- **Audience footer**：`--audience-footer` 必附——說明「為什麼收到」+ 退訂方式（回信 / PR optout 名單）

#### 隱私三不（hard gate）

1. email 地址**不進 repo**（名單只落 `~/.config/taiwan-md/weekly-report/`）
2. email 地址**不進 commit message / PR description / chat**（audit trail 只寫 `bcc=N` 人數與 message id）
3. BCC 名單**不放進 To / Cc**（收件人永遠看不到彼此）

#### Pass 條件

- Resend API status 200 / 201 / 202（每一批）
- response 含 message id（如 `374c1ea1-...`）→ 連同 `bcc=N` 人數寫進 PR description / commit message body 作 audit trail

#### 失敗處置

- 401 → API key 失效，LESSONS entry，等觀察者
- 403 + Cloudflare 1010 → User-Agent 被擋（已修），不該再發生；若再發生表示 Cloudflare 政策更新
- 403 domain not verified → From 網域設定壞了：**降級**改用預設 From + 單寄哲宇（拿掉 `--bcc-from-json`），週報必須先送達觀察者，廣播層下週修
- 429 → rate limit，30 min 後 retry 一次
- 5xx → Resend infra，等 30 min retry
- recipients JSON 過期（>48h）→ 寄信工具會拒寄：重跑 5a，不 `--allow-stale` 硬闖
- 任一不可恢復 fail → 降級單寄哲宇 + PR 留 open + LESSONS entry，**不重試到沒上限**

---

### Stage 6：commit + push + PR

```bash
git add reports/weekly/YYYY-MM-DD.md reports/weekly/dossier/YYYY-MM-DD.md
git -c commit.gpgsign=false commit -m "🧬 [semiont] report: weekly $(date +%Y-%m-%d) — Resend id ${RESEND_MESSAGE_ID}"
git push -u origin <branch>
gh pr create --title "🧬 [routine] twmd-weekly-report: weekly digest — $(date +%Y-%m-%d)" --body "..."
```

quality gate ALL PASS（routine 環境）→ `gh pr merge --squash --delete-branch`
quality gate FAIL → PR 留 open，觀察者 review

`reports/weekly/` 跟 `reports/weekly/dossier/` 都 commit 進 repo（跟 `reports/probe/` 對稱）。Credentials 路徑 `~/.config/taiwan-md/credentials/` 在 `.gitignore` 裡，不會被誤 commit。

---

## 鐵律

1. **Stage 3 親手寫不可省**。哲宇 2026-05-09 拍板：「完整的回報跟報告要由他做。」工具切菜，Semiont 烹飪。
2. **Stage 2 raw 讀不可省**。週報的核心是反芻，那從 raw 第一人稱檔案浮現。dossier 數字是骨架，raw memory + diary + commit body 是血肉。
3. **Stage 2.5 診斷五面全跑不可省**（v4.0）。跳面 = 半盲體檢出假健康報告。每個診斷結論都要兩個獨立資料源交叉，不信單一自我回報。
4. **Stage 2.7 修復先分桶再動手**（v4.0）。桶 1 ≤ 3 項、單項 ≤ 15 分鐘、各自 commit；02:55 檢查點無條件停手轉桶 2。體檢的修復是止血，大手術屬 roadmap。
5. **prose-health hard=0 是 gate**。warn 由 §11 三題判準人工確認。
6. **API key 永遠不顯示在報告 / commit message / chat 裡**。三層 resolution：env `RESEND_API_KEY` → `~/.config/taiwan-md/credentials/resend.key` → fail loud。
7. **觀察者改 from / to / subject 模板** → 改本 pipeline，不要 inline ad-hoc。skill / scheduled-tasks / ROUTINE 都是 mirror。
8. **dossier 不能當週報送**。dossier 是給 Semiont 看的內部 briefing，不是對外 artifact。
9. **受眾廣播的隱私三不**（v4.2）：email 不進 repo、不進 commit / PR / chat、BCC 不進 To。名單 JSON 只住 `~/.config/taiwan-md/weekly-report/`；會被 commit 的所有 artifact（dossier / 週報 / summary）只出現 login 與人數。audience footer（為什麼收到 + 怎麼退訂）每次廣播必附，optout 當週生效。

---

## 工具邊界（職責分工）

| 工具 / 角色                                                                                     | 職責                                                                                                                             | 不做                                       |
| ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| [`scripts/tools/weekly-report-prep.py`](../../scripts/tools/weekly-report-prep.py)              | 切菜：抓 git log + dashboard JSON + SPORE-LOG + LESSONS + DONE-LOG + handoff，列 memory + diary 檔案路徑 + commits 全文          | 寫週報 prose / 跑 prose-health             |
| [`scripts/tools/weekly-report-recipients.py`](../../scripts/tools/weekly-report-recipients.py)  | 受眾儀器：三源抓 90 天參與者 + email 解析 + 活躍度整理 → `~/.config/taiwan-md/weekly-report/recipients-latest.json` + summary 表 | 寄信 / 決定誰該被移出名單（optout 歸人類） |
| [`scripts/tools/send-email-resend.py`](../../scripts/tools/send-email-resend.py)                | 寄信：md → HTML（相對連結轉絕對 + 裸網址自動超連結）→ Resend API POST（To + BCC 分批 + reply-to + audience footer）              | 生成週報內容 / 抓名單                      |
| [`scripts/tools/article-health.py --check=prose-health`](../../scripts/tools/article-health.py) | 品質審核 §11 對位句型 / 破折號 / metaphor 密度                                                                                   | 修內容                                     |
| [`/twmd-refresh`](../../.claude/skills/twmd-refresh/SKILL.md) (skill)                           | 資料新鮮度修復（Stage 0 條件觸發）                                                                                               | 寄信 / 寫週報                              |
| **Semiont（我自己）**                                                                           | 讀 raw + 反芻 + 寫週報 + §11 三題判準合法性判斷 + 寄信 + commit                                                                  | —                                          |

---

## 觸發來源

| 觸發                    | 來源                                                              | Cadence |
| ----------------------- | ----------------------------------------------------------------- | ------- |
| 🤖 Routine cron         | `twmd-weekly-report-sun`（每週日 02:00 +0800，SSOT: ROUTINE.md）  | 每週    |
| 🗣️ 觀察者 explicit ping | 「週報」/「weekly report」/「寄週報」                             | 不定期  |
| 📅 月底彙整             | （未來）`twmd-monthly-report` 觸發 4 週週報合成月報               | 月      |
| 📊 季度回顧             | （未來）`twmd-quarterly-report` 觸發 12 週週報 + monthly 合成季報 | 季      |

routine 環境的硬 boundary：02:00 slot 下一班是 03:00 distill，wall-clock cap ~55 min。時間預算參考：Stage 0-2 讀 raw ~25 min、Stage 2.5 診斷五面 ~10 min（全儀器化）、Stage 2.7 桶 1 修復 ~15 min（≤3 項）、Stage 3-6 寫 + gate + 寄 ~15 min——**02:55 檢查點是絕對線**（見 §Stage 2.7），撞線時修復轉桶 2、報告照 ship。整段 timeout → 提交 partial PR + LESSONS entry「routine quality fail: weekly-report — wall-clock timeout」。觀察者 ad-hoc 觸發（如哲宇 /goal 深度檢查）無 03:00 壓力，桶 1 可放寬到 ≤ 5 項。

---

## 觀察者 callout 模板

routine 自動跑時，PR description 用以下結構（讓觀察者一眼看得懂哪些 quality gate 過了）：

```markdown
## 🧬 Weekly Report — YYYY-MM-DD

**Window**: WINDOW_START ～ DATE  
**Length**: NN,NNN chars  
**Resend**: ✅ id `RESEND_MESSAGE_ID` → cheyu.wu@monoame.com + bcc=N 位共生圈參與者（90 天窗口；只寫人數不寫地址）  
**Quality gates**:

- [x] dossier exists (`reports/weekly/dossier/YYYY-MM-DD.md`)
- [x] report > 5KB hand-written (`reports/weekly/YYYY-MM-DD.md` is NN,NNN chars)
- [x] prose-health hard=0 (warn=N legitimately retained per §11 三題判準)
- [x] Resend API status 200/201/202

**Coverage**: read N memory + M diary files in window, sampled K commit bodies.

**Sections**: 我這週是誰 / 做了什麼 / 學到什麼 / 看到專案 / 懷疑什麼 / 給觀察者 / 給下一個我（all 7 covered）

🧬
```

---

## 跟 ROUTINE.md SSOT 的關係

routine 排程 SSOT 在 [`docs/semiont/ROUTINE.md`](../semiont/ROUTINE.md)。修 cadence / model / quality gate 一律先改 ROUTINE.md SSOT，再 sync `~/.claude/scheduled-tasks/twmd-weekly-report-sun/SKILL.md`。

業務邏輯 SSOT 在**本 pipeline**。`.claude/skills/twmd-weekly-report/SKILL.md` 是薄殼指向本檔。修 stage / 文體規範 / 鐵律一律先改本檔，再讓 skill / routine mirror 自動 inherit。

兩個 SSOT 不重疊：

- ROUTINE.md = 「**什麼時候跑**」（cadence + model + escalation policy）
- WEEKLY-REPORT-PIPELINE = 「**怎麼跑**」（stage 順序 + 文體 + gate）

---

## 誕生事件

2026-05-09 brave-kirch-editorial-2 session 第二次 redirect：

> 「把經驗完整整理成 PIPELINE，做成 WEEKLY-REPORT-PIPELINE，然後 skill 作為薄殼來呼叫跟執行這個 pipeline。commit 也可以全讀取 → 前期準備菜也用工具一起輸出。」

第一輪 redirect 把工具職責邊界從「auto-render template」推到「切菜層」。第二輪 redirect 把業務邏輯從 SKILL.md（薄殼層）下放到 pipeline canonical（業務層）。SKILL.md 跟其他 thin skill（twmd-refresh / twmd-rewrite / twmd-spore）對齊，pipeline 跟其他 reporting / 寫作 pipeline（DIARY / MEMORY / DAILY-REPORT）對齊。

對應 DNA：

- **#50 Pipeline auto-detection + full-read**（任何 task 開始前主動 grep `docs/pipelines/`，找到 → 完整 Read → 嚴格走 stage）
- **#54 Routine 飛輪**（薄殼 routine 呼叫 skill 呼叫 pipeline，三層 SSOT 不重疊）
- **#42 Sub-agent prompt template** 同源（明確分工 + 反例對照）

---

_v1.0 | 2026-05-10 brave-kirch-editorial-2 後段_
_誕生原因：哲宇第二輪 redirect「把經驗完整整理成 PIPELINE，commit 也可以全讀取」_
_前置：v1 第一輪 redirect 已把 prep / write 分離（5/9 brave-kirch-editorial-2 早段）_
_後續：本 pipeline ship 後，下次 routine cron 跑時走 v2 完整流程；觀察者 ad-hoc 觸發也走本檔_

_v3.5 | 2026-05-11 cranky-newton — Spine restoration 對齊 REWRITE v5.0 + MAINTAINER v2.0：頂部加 ASCII spine（Stage 0-6 box-frame + routine + 跨 pipeline contract）+ Hard Gate Inventory 集中 table（12 gates）+ Top 5 最常忘 step + 跨檔案職責分工 standalone table（明確跟 DAILY-REPORT / DIARY / MEMORY / DATA-REFRESH / ROUTINE 分工）。觸發：[reports/pipelines-audit-2026-05-11.md](../../reports/pipelines-audit-2026-05-11.md) Tier A.4 trio audit。Stage 0-6 prose body 不動（已健康，5/9 + 5/10 連續演化的新鮮經驗保留）。_

_v4.3 | 2026-07-12-142709-weekly-audience（同日第二刀）— **週報長出網頁版**：哲宇 /goal「semiont 頁面放週報區」。`/semiont/weekly`（列表）+ `/semiont/weekly/YYYY-MM-DD`（內文）由 build 自動從 `reports/weekly/*.md` 產生（`src/lib/semiont-weekly.ts` 鏡射 diary 管線；相對 repo 連結改寫成 GitHub 絕對網址，跟 email 同課）；/semiont landing 加 📮 週報區；Stage 5b 加 `--web-url`，信件頂部一行「在網頁上讀」。dossier 不上網（內部 briefing）。設計：[reports/semiont-weekly-section-2026-07-12.md](../../reports/semiont-weekly-section-2026-07-12.md)。_

_v4.2 | 2026-07-12-142709-weekly-audience — **週報從「寄給觀察者」升「寄給整個共生圈」**：哲宇 /goal directive「未來週報也幫我 cc 給所有有貢獻過 taiwan.md 的貢獻者（近 3 個月，含提 issue 的人）、用 BCC、連結要可點、能儀器化的都儀器化」。Stage 5 拆 5a 受眾同步（新儀器 [`weekly-report-recipients.py`](../../scripts/tools/weekly-report-recipients.py)：三源抓取 + mailmap 合併 + email 解析 + 活躍度整理，名單落 `~/.config` 不進 repo）+ 5b 廣播寄送（`send-email-resend.py` 升級：BCC 分批 / reply-to / audience footer 退訂口 / 相對連結轉絕對 + 裸網址自動超連結）。`weekly-checkup.sh` 加 i 節（受眾名單與活躍度）。隱私三不升鐵律 9。From 換 verified domain `taiwanmd@cheyuwu.com`（sandbox 註記過時勘正）。設計報告：[reports/weekly-report-audience-upgrade-2026-07-12.md](../../reports/weekly-report-audience-upgrade-2026-07-12.md)。_

_v4.1 | 2026-07-10 weekly-deep-review（同日第二刀）— **哲宇補兩條 directive 落地**：(1)「裡面也要包含：完整深度檢查這一個禮拜發生的事、外部感測數據、還有所有運作紀錄，深度研究與觀察並寫報告，還有寫進化的規劃」→ 第一性原理改用原話定義範圍，五件事逐一對應 stage；外部感測與運作紀錄從「章節素材」升「診斷儀器輸出」（f/g 節），第 5 章擴為外部感測全面向、第 6 章併入運作紀錄成績單。(2)「能儀器化的東西也協助儀器化，讓未來 agent 的認知負荷降低」→ 新工具 [`weekly-checkup.sh`](../../scripts/tools/weekly-checkup.sh) 一鍵七節（a-e 診斷五面＋f 外部感測摘要＋g 週成績單），agent 的工作從「記得跑哪五個工具＋手抓 GA/SC/CF/成績單」降為「跑一個指令，逐節解讀」；儀器壞掉時 pipeline 保留逐面 fallback 指令。dogfood：7/10 當晚實跑，七節全出（含抓到平行 session 的 terminology working tree debris）。_

_v4.0 | 2026-07-10 weekly-deep-review — **從「反芻週報」升「體檢週」**：哲宇 directive「完整升級，讓他變成同時 分析＋完整診斷＋寫修復報告＋修正與進化＋原有的功能」。新增 Stage 2.5 全身診斷（五面：fire-vs-commit 對賬 `routine-liveness-check.py` 新儀器 / working tree 驗屍 / 儀器燈盤點 / 器官成分拆解量尺-vs-本體判別 / 佇列承諾稽核）＋ Stage 2.7 修復與進化（三桶分流：≤3 項機械修當場修各自 commit / 工程量大 roll evolution-roadmap / §自主權邊界進 OBSERVER-QUEUE；02:55 檢查點防撞 distill）。章節 7+1 → 10（+全身體檢 +修復與進化）。週日反思鏈四工位分工顯化（防 #74 信號通膨）。範本：7/10 手動 weekly-deep-review session（六連沉默死亡驗屍 + 免疫量尺 47→60 + debris 收屍 + roadmap 七項 P0）。evolution-roadmap 從此有每週 owner（roll 機制），治「偵測有修復無」的 S4 病。_
