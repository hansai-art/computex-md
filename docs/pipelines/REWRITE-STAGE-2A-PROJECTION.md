---
title: 'REWRITE-STAGE-2A-PROJECTION'
description: 'REWRITE v9 stage contract — Step 2.0 投影藍圖＋2.0.5 視覺化思考：論點/骨架/減法/echo map，craft canonical 在 PROJECTION.md'
type: 'pipeline-sub-canonical'
status: 'canonical'
current_version: 'v9.0'
last_updated: 2026-07-16
last_session: '2026-07-16-newsroom-orchestration（v9.0 拆檔：自 REWRITE-PIPELINE v8.0 verbatim 搬移，行數守恆）'
parent_canonical: 'REWRITE-PIPELINE.md'
upstream_canonical:
  - '../semiont/MANIFESTO.md'
  - '../editorial/EDITORIAL.md'
---

# Stage 2.0 contract — 投影藍圖（研究 → 論點＋骨架）

> **本檔是 REWRITE-PIPELINE v9.0 的 stage contract**：一個執行者（主 session、sub-agent、
> 或任何 context 有限的 model）只讀本檔＋本檔 INPUTS 宣告的檔案，就能執行本 stage。
> 派發路由與全 pipeline spine 在 [REWRITE-PIPELINE.md](REWRITE-PIPELINE.md)（薄索引）。
> 內文自 v8.0 主檔 verbatim 搬移（原行號 RP v8.0 L1370-1388 + L1414-1426），歷史敘事與教訓保留在文內。

## 執行卡

|                  |                                                                                                                          |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **職責**         | 讀整份研究報告，產投影藍圖（論點＋骨架＋每 section 雙重職責＋減法＋echo map＋視覺化候選）                                |
| **執行者**       | 主 session（Opus orchestrator）親自做，**不派給寫手**                                                                    |
| **INPUTS**       | 合成後 research report 全份；[PROJECTION.md](../editorial/PROJECTION.md) 全文（craft canonical）；graph.md（視覺化型錄） |
| **OUTPUTS**      | `reports/article-projection/{slug}.md`（frontmatter `projection_done: true`）                                            |
| **GATES**        | PROJECTION §gate 5 題（論點非摘要/骨架 shuffle/全局功能/減法非空/echo 覆蓋）；depth 題續走 2.0-R 編輯室外部尺            |
| **context 預算** | 本檔＋PROJECTION.md＋research report                                                                                     |

## AGENT PROMPT

**不派 agent**——投影是最高判斷，主 session（Opus orchestrator）讀整份 research report 親自做。craft canonical：[PROJECTION.md](../editorial/PROJECTION.md)（寫前完整讀）。

## 交付條件（stage 完成的定義）

- [ ] `reports/article-projection/{slug}.md` 存在，frontmatter：`article`＋`researchReport`＋`spine_type`＋`projection_done: true`
- [ ] 六節齊：論點／骨架／每 section 雙重職責／減法／echo map／審定
- [ ] PROJECTION §gate 5 題自檢過（作者自檢；外部尺在 2B）

## HANDOFF（stage 完成時）

> stage 若委派 sub-agent，本五步由 orchestrator 於收件驗證後執行（agent 不碰共用看板——2026-07-16 高教 dogfood F6）。

1. OUTPUTS 全數落檔（顯式路徑，不存 scratchpad / tmp——REFLEXES #81）**並隨手 commit（只 stage 本 stage 產物路徑——可觀測性與跨 session 接力的底座，v9.5；勿 `git add -A`）**
2. GATES 逐條跑過，結果如實回報（sub-agent claim 是線索不是 oracle，REFLEXES #31）
3. 更新編輯台：`python3 scripts/core/generate-newsroom-data.py`（看板反映現況）
4. 回報格式：stage id ＋ 產物路徑清單 ＋ gate 結果 ＋ 未解疑慮（有就寫，不粉飾）
5. 下一棒：REWRITE-STAGE-2B-ROOM-PROJECTION.md（投影編輯室，depth HARD）

---

### Step 2.0: 投影藍圖（v8.0 新增）📐 —— 研究 → 投影邏輯 → 文章 (HARD GATE)

> **canonical [PROJECTION.md](../editorial/PROJECTION.md)（寫本步前完整讀）。** 誕生：2026-07-13 哲宇跟陳睨聊後 callout「每個 section 單獨看都完整、接起來卻沒有一個更大的敘事 / 論點 / 意圖」。Stage 0 給**角度**、投影給**建築**、Stage 2 prose 給**句子**——以前從角度直接跳句子，中間沒人設計「這篇到底怎麼長成一個論證」，寫手拿面向清單一段寫一個面向 → 面向巡禮、加法不是乘法、整篇空泛。

**誰做**：主 session（Opus orchestrator），研究合成單檔（[Step 1.7.4](REWRITE-STAGE-1A-RESEARCH.md#174-合成單檔鐵律sibling-是中繼站stage-2-前必-consolidatev711-)）之後、派寫手之前。**不派給寫手**——寫手拿到的是已經想清楚的藍圖，執行結構不發明結構。

**產物**：`reports/article-projection/{slug}.md`（模板見 [PROJECTION.md §四](../editorial/PROJECTION.md)），六件事：

1. **論點**：一句話，有張力、要被賺到，非摘要（判準：讀者能不同意，或文章非證明不可）。論點型別跟 spine 綁定——矛盾驅動用辯論式主張，立體群像用有推進的統合洞見（**立體 ≠ 沒論點**，per [Step 0.1.5](REWRITE-STAGE-0-VIEWPOINT.md#step-015-spine-類型判定v77-重構--立體群像是預設畫布) + [REFLEXES #77](../semiont/REFLEXES.md)；投影對所有題要求推進，只對爭議題要求對立）。
2. **骨架**：動作序列（動詞不是名詞），過 **shuffle test**（section 順序打亂會讀不通，第 N 步預設第 N-1 步）。
3. **每 section 雙重職責**：局部承載 + **全局功能（替論點做什麼）** + 扣回主軸 + 進出連結。全局功能只有「介紹某面向」= 目錄條目 → 給功能或砍。
4. **減法**：明列砍掉什麼材料、為什麼（投影是選擇 + 連結，不是鋪滿；根治密度失衡）。
5. **echo map**：每個 section 一個回到主軸錨的 beat（不只頭尾）——錨反覆變奏 = 那個「宏大抽象的敘事」。
6. **審定**：spine 類型 / title 冒號三明治雛形 / 結尾畫面（先行）/ **視覺化候選（見 Step 2.0.5）** / 媒體分鏡。

**HARD GATE（5 題全過才派寫手）**：論點非摘要 / 骨架過 shuffle test / 每 section 有全局功能 / 減法非空 / echo map 覆蓋全篇。任一不過 → 回去重投影，不派寫手。寫手 read-receipt 加一項：**逐 section 複述全局功能**（證明它讀懂骨架不是照面向抄）。

> worked example：[reports/article-projection/Shopping-Design.md](../../reports/article-projection/Shopping-Design.md)（before＝可 shuffle 的面向巡禮，after＝五步論證，中間三面向壓成「機制放大」一步）。**Evolution 模式照樣先投影**——EVOLVE 最容易踩面向巡禮（研究更多、更想鋪滿）。

### Step 2.0.5: 視覺化思考（v6.8 新增，v8.0 併入投影審定動作 6）💭📊

借 The Pudding「問題先於資料」：寫之前掃過 fact-pack，問三題（**不是強制加圖**——沒有適合的資料就誠實不加，記 research report）：

1. 這篇有哪些「**資料關係**」（比較 / 排名 / 比例 / 分布 / 趨勢 / 流向 / 單一大數字 / 質性對比）密集到讓 prose 變數字堆疊？
2. 每個密集點，[graph.md §型錄](../editorial/graph.md) 哪個 `tw-*` 模組最適合？（**一圖一重點**：一個關係一張圖）
3. 這張圖的 **annotation** 要寫什麼「為什麼重要」？（不是裝飾，是策展觀點）

產出：在 research report §觀點成型 或 fact-pack 標「視覺化候選清單」（哪段 → 哪個 `tw-*` → 想講的重點 → 來源）。Writer agent 吃這份清單，把密集數字段升級成模組（語法見 graph.md §四）。

> **指標**（viz 不是越多越好，避免 chartjunk）：depth 文至少**評估過** 1 個候選（可記「評估後不加 + 理由」）；資料圖表模組 100% 標來源（`viz-health` gate）；viz 密度跟 media band 共管（`paragraph-rhythm`）。**「讓 LLM 讀得懂的視覺化 = 主權的視覺化」**——禁圖片型/D3/Canvas viz、禁「如上圖」AI-blind 指示語。
> **設計脈絡**：[reports/article-visualization-design-2026-06-06.md](../../reports/article-visualization-design-2026-06-06.md)。
