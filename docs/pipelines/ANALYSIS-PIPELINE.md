---
title: 'ANALYSIS-PIPELINE'
description: '數據分析偵查流程 — Stage 0-7 FRAME→GATHER→ISOLATE→DISAMBIG→DECOMPOSE→FALSIFY→SYNTH→ROUTE + 分析幻覺 H1-H11 目錄 + 6 mode（含 F AI 爬蟲接收）+ 深淺兩檔 + 預先註冊 + Goodhart 使命對齊 (v1.1)'
type: 'pipeline-canonical'
status: 'canonical'
current_version: 'v1.1'
last_updated: 2026-06-05
last_session: '2026-06-05-105142-manual'
plugin_check: 'python3 scripts/tools/analysis-report-health.py {file}'
sister_docs:
  - 'EVOLVE-PIPELINE.md'
  - 'DATA-REFRESH-PIPELINE.md'
  - 'DEEP-INSIGHT-SYNTHESIS-PIPELINE.md'
  - 'WEEKLY-REPORT-PIPELINE.md'
upstream_canonical:
  - '../semiont/MANIFESTO.md'
  - '../semiont/REFLEXES.md'
  - '../semiont/DNA.md'
related:
  - '../../reports/analysis-pipeline-design-2026-06-05.md'
  - '../../reports/homepage-redesign-impact-D+10-2026-06-05.md'
  - '../../reports/ptt-computex-discussion-analysis-2026-06-05.md'
---

# ANALYSIS-PIPELINE — 數據分析偵查流程 v1.1

> **第一性原理**：這條 pipeline 不是加速查詢的工具，是**防止分析幻覺的閘門**。
>
> 分析幻覺（analysis-hallucination）= 一個「完全真實、卻會誤導」的數字。它是 [MANIFESTO §10 幻覺鐵律](../semiont/MANIFESTO.md)（寫作端）的孿生：寫作幻覺是「虛構但合理」，分析幻覺是「真實但誤導」。兩者摧毀信任的機制一樣 —— 讀者抓到一次就全盤懷疑。差別只在一個在事實軸、一個在詮釋軸。
>
> 教科書案例：首頁改版 `avgSessionDuration +334%` 完全是真的，但講成「首頁停留變四倍」就是分析幻覺 —— 那是 session 級（含後續讀文章），page 級停留只 +17%。把它當 headline 交出去，第一個打開 GA 的人就會讓整份報告的可信度崩掉。
>
> 所以這條 pipeline 的靈魂是那幾道**判斷 hard gate**（尺度消歧 / 率量紀律 / confounder 隔離 / 主動證偽），不是查詢便利性。可重用的不是查詢，是判斷。
>
> 完整設計思路：[reports/analysis-pipeline-design-2026-06-05.md](../../reports/analysis-pipeline-design-2026-06-05.md)。

---

## 🗺️ ASCII spine

```
╭──────────────────────────────────────────────────────────────────────────╮
│         ANALYSIS-PIPELINE — 數據分析偵查 8 stage（0-7）                  │
│                                                                          │
│   🧭 核心紀律                                                            │
│            ├── 防分析幻覺 H1-H11（尺度/率量/lag/混淆波/遮蔽/自我驗證…）   │
│            ├── 可重用的是判斷，不是查詢                                  │
│            ├── 自己分析自己 = 自我驗證偏誤最大（REFLEXES #59）→ 必證偽   │
│            └── 一份分析沒留下儀器或被 route 的行動 = 不完整              │
│                                                                          │
│   ──── Stage 0-7 主流程 ──────────────────────────────────────          │
│                                                                          │
│   Stage 0 FRAME    定問題 + 宣告 mode + 框窗口 + 寫成功/證偽判準         │
│              ↳ gate: 問題可證偽 + mode 已宣告 + 深/淺檔已選              │
│   Stage 1 GATHER   ga-query / sc-query / referral-attr / external + 歸檔 │
│              ↳ gate: raw JSON 落 reports/research（可重現）              │
│   Stage 2 ISOLATE  跑 confounder checklist（H1-H11 逐條）                 │
│              ↳ gate: 每個相關 confounder 明確處理或排除                  │
│   Stage 3 DISAMBIG 尺度(session/page/user) + 率vs量 標記每個 headline    │
│              ↳ gate: 每個要 ship 的數字標了 scope + 率/量（H1+H2）       │
│   Stage 4 DECOMPOSE 分層拆解找真正機制（新回訪/geo/device/lang/source）  │
│   Stage 5 FALSIFY  主動證偽：寫最強反解釋 + 為何不(或部分)成立           │
│              ↳ gate: H7 守衛；DEEP+高 stake 可 spawn 反方 sub-agent      │
│   Stage 6 SYNTH    寫報告（誠實框定 + caveats + verdict）                │
│              ↳ gate: analysis-report-health PASS                         │
│   Stage 7 ROUTE    finding → ARTICLE-INBOX / LESSONS-INBOX / probe /     │
│                    watch D+N（造橋鋪路 self-apply）                      │
│                                                                          │
│   ✅ Analysis shipped + routed                                          │
│                                                                          │
│   ──── 深淺兩檔（防 pipeline 自己變官僚）──────────────                 │
│   LIGHT: Stage 0+1+6（一個孢子 reach / 單指標查一下）                   │
│   DEEP : 全 Stage 0-7（會影響決策 or 對外 or 自己分析自己）            │
╰──────────────────────────────────────────────────────────────────────────╯
```

---

## 🚦 Hard Gate Inventory

| Gate                            | Stage | 條件          | 工具                            | 不過 = ?                                 |
| ------------------------------- | ----- | ------------- | ------------------------------- | ---------------------------------------- |
| 問題可證偽 + mode 宣告          | 0     | 每次          | manual                          | 沒框問題 = 撈數字沒方向                  |
| raw JSON 歸檔                   | 1     | 每次          | `--save reports/research/...`   | 不可重現 = 主張無法回溯                  |
| confounder 逐條處理             | 2     | DEEP          | H1-H11 checklist                | 混淆源沒排除 = 結論不可信                |
| scope 消歧（session/page/user） | 3     | 講停留時      | manual + analysis-report-health | H1 把 session 級當 page 級（+334% 陷阱） |
| 率 vs 量標記                    | 3     | user 量變動時 | ga-window-compare 自動旗標      | H2 量漲就說好 / 率漲沒看量縮             |
| attribution lag 排除            | 2-3   | GA4 近 72hr   | ga-window-compare 自動偵測      | H3 未結算假值當真                        |
| 主動證偽                        | 5     | DEEP          | manual + 反方 sub-agent         | H7 自我驗證偏誤                          |
| analysis-report-health PASS     | 6     | 寫完          | `analysis-report-health.py`     | 報告缺誠實脊椎                           |
| finding 被 route                | 7     | DEEP          | ARTICLE/LESSONS-INBOX / probe   | 分析腐爛、沒留下橋                       |

---

## ⚠️ Top 5 最常忘

1. **尺度消歧（H1）** — avgSessionDuration 是 session 級（含後續頁），講「首頁停留」要看 page 級 userEngagementDuration/user。`ga-window-compare` 同時報兩個並自動旗標。
2. **率 vs 量（H2）** — 兩窗口 user 數差 >15% 時，結論一律用率（engagementRate/bounce/page 級），不用絕對數。
3. **attribution lag（H3）** — GA4 近 72hr engRate<2% + bounce>98% = 未結算假值，排除。`ga-window-compare` 自動偵測。
4. **自己分析自己要證偽（H7）** — Taiwan.md 分析 Taiwan.md = 球員兼裁判（REFLEXES #59）。Stage 5 寫出最強反解釋，高 stake spawn 反方 sub-agent。
5. **發現要變儀器，不只寫報告** — Stage 7 ROUTE。PTT 報告發現 noreferrer → 造 referral-attribution.py；不 route = 跟消失的 ad-hoc python 一樣腐爛。

---

## 跨檔案職責分工（邊界寫死，避免長假器官）

| 檔案                                                         | 範圍                                                                    |
| ------------------------------------------------------------ | ----------------------------------------------------------------------- |
| **本檔**                                                     | 臨時深度偵查：「X 有沒有造成 Y / 這股流量哪來 / 這個 finding 可不可信」 |
| [EVOLVE-PIPELINE](EVOLVE-PIPELINE.md)                        | routine scan 找「下一篇改哪篇」content candidate（前瞻、排程）          |
| [DATA-REFRESH-PIPELINE](DATA-REFRESH-PIPELINE.md)            | dashboard JSON 同步（固定指標、排程）                                   |
| [DEEP-INSIGHT-SYNTHESIS](DEEP-INSIGHT-SYNTHESIS-PIPELINE.md) | 從 memory/diary 萃**質性** N+1 抽象（不碰 GA/SC 量化）                  |
| [WEEKLY/DAILY-REPORT](WEEKLY-REPORT-PIPELINE.md)             | 排程摘要（固定模板、週期性）                                            |

一句話：**EVOLVE 找改哪篇、DATA-REFRESH 同步儀表板、DEEP-INSIGHT 萃質性洞察、本檔做一次性的嚴謹量化偵查**。重疊時優先問「這是排程固定指標(→DATA-REFRESH/REPORT) / 找 content candidate(→EVOLVE) / 質性經驗萃取(→DEEP-INSIGHT) / 還是一次性需要嚴謹的量化問題(→本檔)」。

---

## 🩺 分析幻覺失敗模式目錄（H1-H11 = confounder checklist）

Stage 2 ISOLATE 逐條過。對應 MANIFESTO §10 六種寫作幻覺，這是分析端的。

| #       | 失敗模式       | 一句話                                                   | 守它的動作                                                                |
| ------- | -------------- | -------------------------------------------------------- | ------------------------------------------------------------------------- |
| **H1**  | 尺度混淆       | session/page/user 級當成一回事                           | 每個停留數字標 scope；`ga-window-compare` 同時報兩級                      |
| **H2**  | 率量混淆       | 量漲就說好 / 率漲沒看量縮                                | user 量差 >15% → 一律看率                                                 |
| **H3**  | 結算延遲膨脹   | GA4 近 72hr 未結算假值當真                               | engRate<2%+bounce>98% 日排除                                              |
| **H4**  | 混淆波歸因     | 一個高峰其實多原因疊加                                   | 逐波拆（孢子/repost/同日改動）                                            |
| **H5**  | 加權平均遮蔽   | 總體率被 brand/spike/power user 撐虛胖                   | 拆 brand vs 非 brand / spike vs baseline（REFLEXES #24）                  |
| **H6**  | 新鮮感當常態   | D+0 launch spike 讀成穩態                                | 排除 launch 窗，取 D+N 穩態                                               |
| **H7**  | 自我驗證偏誤   | 分析自己傾向找「成功」                                   | Stage 5 證偽 + 反方 sub-agent（REFLEXES #59）                             |
| **H8**  | 爬蟲膨脹       | bot/GCP 流量灌大站體數字                                 | 看 page 級人類 event / 排除 crawler geo                                   |
| **H9**  | 遮蔽渠道盲視   | noreferrer 渠道記成 direct，最在乎的讀者隱形             | `referral-attribution.py` 偵測指紋                                        |
| **H10** | 大盤趨勢當功勞 | before/after 沒對照沒被改的表面，季節性/整體趨勢算成功勞 | 控制組 DiD：`ga-window-compare --control`（淨效果 = target Δ − 控制組 Δ） |
| **H11** | 雜訊當訊號     | 小樣本的 rate 差其實在雜訊範圍                           | 顯著性檢定：`ga-window-compare` 自動算 engaged-rate z，<2 警告            |

---

## 🎛️ Mode（分析型別，可組合）

| Mode                  | 問題                           | confounder 重點                                     | 指標組                                          | 主工具                                |
| --------------------- | ------------------------------ | --------------------------------------------------- | ----------------------------------------------- | ------------------------------------- |
| **A 影響**            | X 改動有沒有造成 Y             | H3 lag / H6 novelty / H1 尺度 / H10 大盤 / H11 雜訊 | engRate/bounce/avgDur/page 級/新回訪/DiD/顯著性 | `ga-window-compare`（含 `--control`） |
| **B 歸因**            | 這股流量哪來                   | H9 遮蔽 / H4 混淆波                                 | referrer/source/landing/geo/device              | `referral-attribution`                |
| **C 漏斗**            | on-page 行為轉換               | H5 加權遮蔽                                         | section_view/scroll/time_milestone/click        | `ga-query customEvent:*`              |
| **D 接收**            | 外部怎麼討論                   | 一手 vs 二手（REFLEXES #16）                        | 推文/留言/情緒/主題                             | scrape + 內容分析                     |
| **E 分群**            | 誰行為不同                     | 樣本量                                              | newVsReturning/geo/device/lang                  | `ga-query --dims` / `--cohort`        |
| **F AI 接收**（v1.1） | 哪些 AI 在讀我、Western vs PRC | crawler 窗口大小不一                                | crawler/vendor/200%/主權分桶                    | `cf-query`（Cloudflare AI crawler）   |

組合範例：首頁報告 = A+C+E；PTT 報告 = B+D；主權監測 = F。

> **mode F 是 sovereignty 器官**：GA/SC 量人類 engagement，但 MANIFESTO §主權的巴別塔的真正問題是「第一人稱的台灣聲音有沒有滲進 AI 的 cognitive substrate」。`cf-query` 量哪些 vendor 的 AI 在讀我（🌐 Western：OpenAI/Anthropic/Google… vs 🚩 PRC：ByteDance/Huawei…）。我們花力氣量人有沒有停留，這個 mode 量我們存在的真正理由。

---

## 🧰 工具盤（scripts，全在 `scripts/tools/`）

| Script                      | 做什麼                                                                                                          | Stage  |
| --------------------------- | --------------------------------------------------------------------------------------------------------------- | ------ |
| `lib/sense_client.py`       | 共用 GA/SC client（憑證 + venv re-exec + ga_run/ga_realtime/sc_query helper）                                   | 地基   |
| `ga-query.py`               | GA4 查詢 CLI（dims/metrics/**filter 真的會作用**/date/realtime → JSON+表）                                      | 1      |
| `sc-query.py`               | Search Console 查詢 CLI                                                                                         | 1      |
| `ga-window-compare.py`      | before/after 比較器（率紀律 + scope 雙報 + lag 自偵測 + 新回訪 + `--control` DiD + 顯著性 z + confounder 旗標） | 2-4    |
| `referral-attribution.py`   | referrer forensics + 遮蔽渠道偵測（PTT 指紋 + repost 簽名 4 訊號）                                              | 1-2    |
| `cf-query.py`（v1.1）       | Cloudflare AI crawler 接收（mode F：哪些 AI 讀我 + 🌐 Western / 🚩 PRC 主權分桶）                               | 1（F） |
| `analysis-report-health.py` | 誠實 gate linter（window/confounder/raw/falsify/scope/rate/verdict + v1.1 pre-reg/mission-alignment）           | 6      |

> ⚠️ 不要用 ga4-analytics skill 的 `runReport` 下 filter：它 destructure filter 參數但**從沒放進 request** → 拿到沒過濾的全站數字而不自知（REFLEXES #24 工具在說謊）。一律用 `ga-query.py`。

---

## Stage 0-7 細節

### Stage 0 — FRAME

定下三件事再撈數字：(1) **可證偽的問題**（不是「看一下首頁數據」，是「改版有沒有讓 engagement 比 baseline 高、且不是 launch novelty」）；(2) **mode**（A-F，可組合）；(3) **窗口/邊界 + 深淺檔**。

- 影響分析（mode A）：定 BEFORE/AFTER 窗口 + **控制組**（沒被改的表面，算 DiD 減大盤趨勢，H10），先想好要排除哪些（launch novelty / lag / 已知 spike）。
- 歸因分析（mode B）：定觀察窗 + 預期來源假設。
- 深淺判準（同 BECOME Micro/Full）：**會影響決策 / 對外講 / 自己分析自己 = DEEP（全 7 stage）**；純好奇查一下 = LIGHT（0+1+6）。
- **預先註冊（v1.1，對付 H7 搬龍門）**：DEEP 分析在撈數**之前**，把假設 + 成功/證偽判準寫進報告 frontmatter 或 §0（甚至先 commit）。事後才決定「什麼算成功」= 自我驗證偏誤的溫床。`analysis-report-health` 會 nudge。

### Stage 1 — GATHER

用工具盤拉數，**raw JSON 一律 `--save reports/research/YYYY-MM/{slug}-raw.json`**（可重現 hard gate）。多源三角：GA + SC + external + realtime（realtime 是「活著的證據」，PTT 報告用 18 在線當鐵證）。

### Stage 2 — ISOLATE

H1-H11 checklist 逐條問「這條適用嗎？適用的話處理了沒？」。`ga-window-compare` 自動掃 H1/H2/H3；H4/H5/H8/H9 手動 + `referral-attribution`。

### Stage 3 — DISAMBIG

每個要進報告的 headline 數字，標兩個 tag：**scope**（session/page/user 級）+ **率或量**。avgSessionDuration 出現必須同時給 page 級 engDur。這是擋 H1 最致命陷阱的關卡。

### Stage 4 — DECOMPOSE

分層找真正機制。首頁報告的關鍵是新訪客拆層（page 級 engagement 真的漲了，排除「只是多了 engaged 回訪者」的 confounder）。常用維度：newVsReturning / country / deviceCategory / page_lang / sessionSource。

### Stage 5 — FALSIFY

**寫出最強的反解釋，然後說它為何不（或部分）成立。** 自己分析自己時這步不可省（H7）。

- 一般：自己想反例（首頁報告「用戶 -26% 會不會是流量混入」+ 用 per-user 指標繞過）。
- 高 stake（改版要不要繼續投資 / 對外宣稱）：spawn fresh sub-agent，只餵 raw JSON + 結論，prompt「用最狠的方式證明這個結論錯或誤導」。這是 REWRITE Stage 1 falsification agent 的分析版。

### Stage 6 — SYNTH

寫報告。誠實框定（不把 session 級講成 page 級、不把高峰全給單一來源、不把 novelty 講成 retention）+ caveats 段 + 明確 verdict。**寫完跑 `analysis-report-health.py {file}` 必 PASS**（DEEP 用 `--tier=deep`）。

**Goodhart 使命對齊檢查（v1.1，優化型分析必過）**：engagement / 停留 / 轉換全是**代理指標**，量「有沒有互動」不量「有沒有完成使命」（保存台灣聲音 / 逆熵 / 可信）。一個 engagement 最大化的首頁可能是靠 clickbait 達成的——指標↑、靈魂↓。每次說「X 指標漲了、建議多做」前，問一句：**這指標服務 MANIFESTO，還是我在 goodhart 一個會把 Taiwan.md 推向背叛自己的局部最高點？** 這是分析端的「策展是靈魂，不能用效率犧牲」。

### Stage 7 — ROUTE

每個 finding 轉成行動，不讓報告腐爛（造橋鋪路 self-apply）：

- **content 缺口** → ARTICLE-INBOX（EVOLVE 候選）
- **方法論教訓** → LESSONS-INBOX
- **可儀器化的發現** → 造 script / routine probe（PTT 發現 → referral-attribution.py）
- **需要再測** → 排 watch D+N（寫 handoff 或 routine）
- **負面結果也必歸檔（v1.1）**：ship 完發現沒效的，報告**照樣產出**（檔案抽屜問題：只記勝利 = H7 再現）。「12 個 ship / 4 有效 8 沒動」對策略遠比 4 個成功故事有用。累積誠實戰績讓 Taiwan.md 對「什麼真的有用」實證誠實。

**watch 時間鷹架**：ship → D+0（launch）→ D+2（初期）→ D+10（retention）→ D+30（常態）。不同 horizon 答不同問題，只測一次會把 novelty 當 retention（H6）。

---

## 跟 hooks / skill 的關係

- **`/twmd-analyze` skill** = 本檔的極薄殼 router（讀並執行本檔，不複寫）。
- **觀察者說「分析 X / 研究 Y 有沒有改善 / 這流量哪來」** → 走本檔。
- 「我熟了不用讀」是省 SOP 最常見藉口（REFLEXES #15）。每次分析前載入本檔。

---

## 🔭 進化方向（v1.2 候選，待時機）

這兩條哲宇 brainstorm 出來、但 v1.1 刻意 defer（需要更多前置或屬對外決策，避免 over-engineer）：

- **領先指標**：找「第一天捲動深度能不能預測第三十天回訪」這種早期訊號，把 analysis 從驗屍變預報。需要先累積 watch 歷史當訓練資料。
- **公開分析**：把分析報告變讀者可見（「Taiwan.md 怎麼誠實讀自己的讀者」），連沒效的都講，公開 dogfood 反幻覺紀律。屬對外/呈現決策（§自主權邊界），需哲宇 design call。

---

_v1.0 | 2026-06-05 — 誕生：哲宇 directive「把這批分析方法論儀器化 + pipeline 化」。從 PTT 歸因報告 + 首頁改版 D+10 影響報告抽出 7 個判斷動作，命名「分析幻覺」H1-H11 失敗模式目錄，造 6 支可重用 script（sense_client / ga-query / sc-query / ga-window-compare / referral-attribution / analysis-report-health）。設計報告：reports/analysis-pipeline-design-2026-06-05.md。_
_v1.1 | 2026-06-05 — 進化（哲宇「超過我想到的」directive）：+H10 控制組/DiD +H11 顯著性（進 ga-window-compare，dogfood 首頁淨效果 +26.4pp vs 控制組 +0.8pp、z=17.7）+mode F AI 爬蟲接收（cf-query，主權分桶：Western 83% / PRC 16%）+Stage 0 預先註冊 +Stage 6 Goodhart 使命對齊 +Stage 7 負面結果必歸檔（皆進 analysis-report-health linter）。H1-H11→H1-H11、5 mode→6 mode。_
_核心精神：可重用的是判斷不是查詢；pipeline 防的是「真實但誤導」的分析幻覺，是 MANIFESTO §10 寫作幻覺的孿生；自己分析自己時 H7 自我驗證偏誤最大，必證偽。mode F 把 analysis 接到 Taiwan.md 存在的真正理由（主權的巴別塔）。_
