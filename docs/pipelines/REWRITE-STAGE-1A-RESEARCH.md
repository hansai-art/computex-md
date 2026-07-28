---
title: 'REWRITE-STAGE-1A-RESEARCH'
description: 'REWRITE v9 stage contract — Stage 1 取材主幹：搜尋 ≥80 配額 / 矛盾鎖定 / 研究報告八段 SSOT / agent 收件 gate / 來源逐條可溯'
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

# Stage 1 contract — 取材 A（研究 fan-out 與研究報告 SSOT）

> **本檔是 REWRITE-PIPELINE v9.0 的 stage contract**：一個執行者（主 session、sub-agent、
> 或任何 context 有限的 model）只讀本檔＋本檔 INPUTS 宣告的檔案，就能執行本 stage。
> 派發路由與全 pipeline spine 在 [REWRITE-PIPELINE.md](REWRITE-PIPELINE.md)（薄索引）。
> 內文自 v8.0 主檔 verbatim 搬移（原行號 RP v8.0 L740-1123），歷史敘事與教訓保留在文內。

## 執行卡

|                  |                                                                                                                                                                                                  |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **職責**         | 帶 Stage 0 問題執行搜尋（≥80，中≥40/英≥20/一手≥15/反方≥5）、收斂矛盾或組織主軸、組裝八段研究報告 SSOT                                                                                            |
| **執行者**       | orchestrator（主 session）＋ N 個 parallel Sonnet 研究 agent（prompt 一律 [RESEARCH-AGENT-PROMPT.md](RESEARCH-AGENT-PROMPT.md) 填槽，禁即興）                                                    |
| **INPUTS**       | research report §觀點成型（Stage 0 產物）；RESEARCH.md；RESEARCH-AGENT-PROMPT.md                                                                                                                 |
| **OUTPUTS**      | `reports/research/{YYYY-MM}/{slug}.md`（八段合成單檔；sibling raw 收件後 consolidate 刪除）                                                                                                      |
| **GATES**        | 每份分部報告收件當下：`python3 scripts/tools/agent-report-health.py {file} --claimed {配額}`（FAIL 不准合成）；stage 終：`python3 scripts/tools/research-report-health.py {report} --tier=depth` |
| **context 預算** | orchestrator 本檔＋收件；各研究 agent 只吃 RESEARCH-AGENT-PROMPT 填槽 prompt                                                                                                                     |

## AGENT PROMPT

研究 sub-agent 唯一 prompt 載體：[RESEARCH-AGENT-PROMPT.md](RESEARCH-AGENT-PROMPT.md)（含輸出模板＋來源逐條可溯契約＋anti-example 庫）。填槽派發，禁即興——2026-07-12 茶文化即興 prompt 讓 84 條來源行只 35% 帶 URL。

## 交付條件（stage 完成的定義）

- [ ] 每份分部報告收件當下 `agent-report-health.py {file} --claimed {配額}` exit 0（FAIL 不准合成）
- [ ] 全部 raw verbatim 落 report §8（收到通知的第一個動作；禁 scratchpad／tmp）
- [ ] sibling raw 檔 consolidate 進主檔後刪除
- [ ] `research-report-health.py {report} --tier=depth` exit 0（distinct≥25／en≠0／一手≠0）
- [ ] frontmatter 核心矛盾（或組織主軸＋facet）已鎖

## HANDOFF（stage 完成時）

> stage 若委派 sub-agent，本五步由 orchestrator 於收件驗證後執行（agent 不碰共用看板——2026-07-16 高教 dogfood F6）。

1. OUTPUTS 全數落檔（顯式路徑，不存 scratchpad / tmp——REFLEXES #81）**並隨手 commit（只 stage 本 stage 產物路徑——可觀測性與跨 session 接力的底座，v9.5；勿 `git add -A`）**
2. GATES 逐條跑過，結果如實回報（sub-agent claim 是線索不是 oracle，REFLEXES #31）
3. 更新編輯台：`python3 scripts/core/generate-newsroom-data.py`（看板反映現況）
4. 回報格式：stage id ＋ 產物路徑清單 ＋ gate 結果 ＋ 未解疑慮（有就寫，不粉飾）
5. 下一棒：REWRITE-STAGE-1B-MEDIA.md（媒體＋persona 缺口）

---

## Stage 1: 取材（純搜尋執行，預算 25-30%）

**目標**：產出一份結構化研究筆記，讓 Stage 2「不需要再搜尋」就能寫。**帶 Stage 0.6 觀點成型的切入點 + 核心矛盾候選去搜尋驗證 / 反駁 / 深化**。

**必讀**（Stage 0.5 已讀完，這邊只是 reminder）：

- `docs/editorial/RESEARCH.md`（方法論：搜尋策略、來源判斷、避坑指南）
- `docs/editorial/RESEARCH-TEMPLATE.md`（填空模板）

### Step 1.1: 搜尋深度 ≥ 80 次（v6.4，含來源多樣性配額）

**搜尋至少 80 次**（v6.4 升級，自 v5.1 ≥ 40 提高；含 Stage 0 的 ≥ 20 = 全篇 ≥ 100 次）：

| 來源類別                                 | 最低配額 | 為什麼                                                             |
| ---------------------------------------- | -------- | ------------------------------------------------------------------ |
| **中文**                                 | ≥ 40     | 在地視角、當地報導、社群記憶                                       |
| **英文 / 國際 / 學術**                   | **≥ 20** | 國際視角 + triangulation；攻擊「57% 報告英文來源 = 0」的系統性缺口 |
| **一手**（官方/政府/年報/法規/學術論文） | ≥ 15     | 對標論文：claim 要追到原始來源，不是二手新聞的二手                 |
| **反方 / 批評**（perspective scan）      | ≥ 5      | 跨陣營對立 spectrum，落 `rationale.whats_excluded`                 |

> **v6.4 升級理由**（2026-06-04）：量測 226 份歷史 report — **57% 英文/國際/學術來源 = 0、42% distinct 來源 ≤ 10**。對標 gold standard [毒馬鈴薯認知作戰.md](../../reports/research/2026-04/毒馬鈴薯認知作戰.md)（85 來源 / 1,699 行 / §1-§N 分章 / 每 claim 標信度）vs 退化後的 synthesized fact-pack（~200 行）差近 9 倍。哲宇 directive「搜尋總數 80+、對標研究所論文標準」。**這 4 條配額由 `research-report-health.py` 儀器化驗收**（en==0 / primary==0 = HARD），不是 aspirational。

- 研究深度直接決定文章品質——40 次仍會留單源依賴風險，80 次才有 triangulation 餘裕、找到反方、挖到非 Wikipedia 層級的具體錨點（引語、場景、日期）
- **多語系不是 nice-to-have**：英文/國際來源是 default 不是例外。真正只有中文來源的題目（極在地的兩岸/戒嚴細節）→ 在 §搜尋日誌 明寫「本題英文來源稀少，因為 X」，不要靜默跳過（對應 research-report-health en==0 HARD）

> ⚠️ **≥80 是 fan-out aggregate，不是單 agent 串行能達到的**（2026-06-04 v2 實驗實證）：minimal-guidance 單一 Opus research agent 串行只跑到 ~36 次就接近 token 上限。**要達 80+ 必須照 [§多 agent 編排](REWRITE-PIPELINE.md#-多-agent-編排v63-orchestrator--tiered-sub-agents) 派 N 個 parallel research sub-agent**（按 §A/§B/§C/§D 子領域切，每 agent ~20-30 次，aggregate ≥80），orchestrator 合 §8 raw + §6 fact-pack。單 agent 自跑只適合 standard tier（≥40）；硬要 depth ≥80 而不 fan-out → 在 §未達標誠實說明 記缺口，不灌水硬湊。**研究廣度（4 子題 + 反方 + 一手 + 英文）優先於搜尋次數的硬達標**。

**v5.1 升級理由**（2026-05-11 cranky-newton）：v2.17 訂 ≥ 20 是相對 12 次淺研究的下限。實戰累積後（NMTH Fresh / 政治人物 batch / 認知作戰深度文）顯示 20 次仍會留下「單源依賴」風險（同一篇 ltn 報導被 5 atom 綁住 = over-citing 紅旗），40 次才開始有 triangulation 空間。

**v2.17 原版觸發**：2026-04-18 當日 11 篇音樂人批次中，12-15 次搜尋的 Cicada / 草東 / 康士坦 / 魏如萱 雖然 pass format-check，但小標題淪為編年史，缺乏場景/意象級的敘事錨點，研究深度是根本原因。

**Stage 0.6 → Stage 1.1 銜接**：帶著 Stage 0.6 §觀點成型 列出的「研究方向（要搜什麼可以驗證）」+「核心矛盾候選 A/B/C」+「pre-search source map」進來。80 次搜尋的分配建議：40% 驗證 Stage 0.6 hypothesis、25% 反駁/深化 hypothesis、20% 補英文/國際/學術視角（配額）、15% 探索預期之外的支線。如果搜完發現 Stage 0.6 觀點完全錯了，那是好結果 — Stage 1.4 找矛盾鎖定會自動修正。

### Step 1.2: 結尾素材鎖定

⚠️ **不要等寫到最後才想結尾**。結尾素材在研究階段就要鎖定。

每篇文章結尾應該是：

- 一個具體場景（不是論述句）
- 一個首尾呼應的 anchor（呼應開場 icon）
- 一句留白的引語或畫面（讓讀者「停一下」）

研究時就標出 2-3 個候選結尾畫面，Stage 2 Step 2.2（結尾先行）直接挑用。

### Step 1.3: 重複偵測

完整方法論見 [RESEARCH.md §六](../editorial/RESEARCH.md)。**不要寫完才發現重疊**。

```bash
ls knowledge/{Category}/ | grep {keyword}
grep -r "主題關鍵詞" knowledge/{Category}/
```

如果發現高度重疊的既有文章 → 改走 Evolution / Merge / Boundary 模式（回 Step 1.1 重判）。

### Step 1.4: 找矛盾鎖定 / 組織主軸（依 spine 類型分叉，v7.6）🔥

> ⚠️ **先看 [Step 0.1.5](REWRITE-STAGE-0-VIEWPOINT.md#step-015-spine-類型判定v77-重構--立體群像是預設畫布) 判的 spine 類型**：
>
> - **矛盾驅動 spine**（爭議/張力人物）→ 走下方原 SOP，收斂單一核心矛盾。
> - **立體群像 spine**（受愛戴的機構/傳統/集體記憶/地方，default）→ **不逼尖銳矛盾**。改鎖一句**組織主軸（through-line）+ ≥ 4 facet 清單**；張力若有，當其中一個 facet，不當全文脊椎。寫進研究筆記：`組織主軸 = ?` + `facet = [a, b, c, d]`。**硬找一個矛盾 = 把立體主題壓成論戰 = 炎上**（金曲獎 v1 教訓）。

**以下為矛盾驅動 spine 的 SOP**：在結束 Stage 1 之前，必須能回答這個問題：**「這篇文章的核心矛盾是什麼？」**

- 好的重寫不是修辭層的工作，是矛盾層的工作。舊文不是寫得不好，是它拒絕承認內部矛盾
- 找到矛盾 = 找到重寫的理由。**找不到矛盾**（爭議題）= 這篇不該被重寫；但**受愛戴的機構題找不到尖銳矛盾是正常的**，那就走立體群像，不是不該寫
- 寫進研究筆記：`核心矛盾 = ?`（一句話，不超過 30 字）

**範例**：

- 「台灣說要走豪豬戰略，但 76% 預算拿去買美國傳統武器」
- 「TFT 說要解決偏鄉教育，但孩子的問題不在教室裡是在整個生態系」
- 「美國要排除中國，但只給台灣一張入場券」（無人機產業 EVOLVE）

**v2.14 觸發背景**：2026-04-10 session α 國防現代化重寫的教訓——沒有李喜明那句苦笑，整篇會變回豪豬戰略勝利敘事。

### Step 1.4.5: Perspective scan — 跨陣營對立 spectrum 覆蓋 🧭

Step 1.4 收斂的是文章內部 thesis 矛盾。Step 1.4.5 找的是**跨陣營對立 spectrum** — 哪些陣營對本文 framing 會質疑、是否該引述對立論述、排除哪些理由。perspective scan 結果**必須**落地到 frontmatter `rationale.whats_excluded` (per [RATIONALE-SPEC.md](../editorial/RATIONALE-SPEC.md))。

**兩種做法擇一**：

| 做法                      | 適用                                                      | 觸發                       |
| ------------------------- | --------------------------------------------------------- | -------------------------- |
| **A. spawn 反方 agent**   | 爭議題目 (政治 / 史觀 / 政策 / identity)                  | sub-agent WebSearch 可用時 |
| **B. 作者自問 checklist** | 非爭議題目 OR sub-agent WebSearch 不可用 OR retrofit 場景 | 永遠可用作 fallback        |

#### 做法 A — sub-agent prompt (含防呆三條)

```
你是 [topic] 議題的反方代表 / 質疑者 / 批評者。
從反對立場找 5-10 個有實質論述的 sources。

防呆三條:
1. 每條對立論述必附 source URL — 拿不出 URL 就不算數
2. 列 5-10 條;論述不夠就明確標「對立陣營論述薄弱」+ 為什麼,不要硬湊
3. 顯式排除「情緒攻擊類 / 無實質論點」(範例: 人身攻擊 / 沒事實依據的 ad hominem / 純口號 chants)

回覆格式: { url, position summary, strongest argument, source quality grade (A/B/C) }
```

**設計目的**：寧可 agent 回「對立論述不夠」也不要 hallucinated 假反方觀點。前者作者還能判斷，後者會誤導作者把假論述當真論述處理。

#### 做法 B — 作者 self-checklist 5 題

寫文章前作者自問：

1. 這個主題的主要爭議陣營是誰？
2. 我引用的 sources 涵蓋了哪些陣營？
3. 我沒引的陣營有沒有實質論述存在於網路上？
4. 如果有，我為什麼沒引？
5. **對立論述如果存在但作者選擇不引 — 是因為 (a) 論述薄弱 (b) 篇幅限制 (c) 不在範疇？三選一寫進 `whats_excluded`**

**為什麼第 5 題強制三選一**：含糊帶過會變成「我有想過」的偷吃步 — 只有逼作者選一個具體原因，這個思考才真的留下來給後人。

#### 處理策略 3 選 1

對 sub-agent 結果或 self-checklist 結論，作者決定每個對立論述的處理：

| 策略                | 動作                          | 落地位置                   |
| ------------------- | ----------------------------- | -------------------------- |
| **引用**            | 把論述帶進文章作 counterpoint | 文章內 + 補新 `[^N]`       |
| **排除 + 理由**     | 不帶進文章，理由寫進 metadata | `rationale.whats_excluded` |
| **不在範圍 + 理由** | 對立論述跟本文焦點不同        | `rationale.whats_excluded` |

→ 跟 RATIONALE-SPEC.md hard coupled — perspective scan 結果**必須**落到 metadata。

#### 不做的事

- ❌ 不強制平衡 (總有平衡不完)
- ❌ 不取代 Step 1.4 找矛盾 (perspective scan 是 1.4 的延伸)
- ❌ 不 retroactive 200 篇 (per #851 Build 3 「retrofit 太重」)

**觸發背景**：2026-04-30 issue #851 哲宇提 No2「20 個 source 是數量檢查，沒有觀點檢查」。5/22-23 Phase 3 統獨光譜 + Phase 4 蔡英文 retrofit 兩篇 dogfood 後 ship canonical。完整脈絡見 [RATIONALE-SPEC.md](../editorial/RATIONALE-SPEC.md)。

### Step 1.5: 問觀察者要一手素材 🫧

Stage 1 結束前，**主動問觀察者一句**：

> 「你手上有沒有我搜不到但你知道的素材？（付費牆文章、私人筆記、實體書、個人經驗）」

這不是偷懶，是承認感知有邊界。爬蟲給事實骨架，觀察者給血肉。

**v2.15 觸發背景**：安溥重寫——Agent 49 次搜尋抓不到康健雜誌 403 付費牆文章，觀察者直接貼全文。女巫店兩桌客人、時薪八十塊、林黛玉比喻——文章最有人味的段落全部來自這個管道。

### Step 1.6: 私有 SSOT 觀察者拍板（條件式）

**Skip 條件**：Stage 1 沒整合任何當事人提供的私有素材（Obsidian 筆記、個人編年史、家族內情）。

#### 流程（v2.18 新增）

1. **Stage 1 末尾**：列出「從私有素材看到但不確定能否公開」的項目，依 [EDITORIAL §私有素材顆粒度](../editorial/EDITORIAL.md) 分成 Tier 1-4
2. **觀察者拍板**：清單交給當事人，一題一題回答（拒寫 / 寫但不提名 / 寫但改措辭 / 完整寫）
3. **研究報告 §維護者校準備忘錄**：記錄所有 tier 3-4 項目的拍板結果，**不記錄拒寫項目的具體內容**
4. **Stage 2 寫作護欄**：agent 若基於私有素材自動推導進來的 tier 3-4 claim 必須刪
5. **Stage 3 VERIFY 追加項**：文章公開前再檢查一次是否有漏網的 tier 3-4 內容

**對應**：

- [EDITORIAL §私有素材 × 公開文章的顆粒度](../editorial/EDITORIAL.md)
- [MEMORY §feedback 隱私協商是動態連續決策](../semiont/MEMORY.md)

**預警**：私有 SSOT 也會有誤記（當事人 2026 寫 2008 的事情）。當事人的 SSOT 需要與公開 source 三源交叉，**不是免驗證的 oracle**。

### Step 1.7: 研究報告 = SSOT（對標研究所論文標準）📁 🔬

> **v6.4 大改**（2026-06-04）：research report 從「agent 輸出 + header」升格成 **SSOT（single source of truth）**——對標研究所論文：有方法論（搜尋日誌）、有完整參考文獻、每個 claim 都標來源 + 信度、原始搜尋軌跡全留。**搜了沒寫回 report = 沒搜**。觸發：v6.3 多 agent 編排「合成 clean fact-pack」把 agent 原始搜尋軌跡丟掉（違反「不摘要」），report 退化成摘要；量測 226 份報告 57% 英文來源 = 0。

**Scope gate**（不是所有文章都存）：

- ✅ 要存：People/ 深度文、Society/ 深度文、History/ 深度文、Tech/ 深度文（預計 ≥ 10 腳註 或 ≥ 2,000 字）
- ❌ 不存：Hub 頁面、短修正、翻譯、單事件補登

**檔案路徑**：`reports/research/YYYY-MM/{article-slug}.md`

#### 1.7.1 SSOT 八段結構（depth article 強制，v6.5 從 12 份範本萃取）

> 方法論 canonical + 信心程度系統 + 10 骨架在 [RESEARCH.md §二之二](../editorial/RESEARCH.md) + [methodology synthesis](../../reports/research-methodology-synthesis-2026-06-04.md)。

```markdown
---
article: knowledge/{Category}/{slug}.md
stage: 1-research
date: YYYY-MM-DD
session: { handle }
agents: [Explore×N / general-purpose]
search_count: { stage0: N, stage1: M, total: N+M } # Stage0 ≥20 / Stage1 ≥80
source_count: { distinct: X, zh: A, en: B, primary: C, opposition: D } # en/primary ≠ 0
core_contradiction: 一句話（≤ 30 字）
viewpoint_formed: true
verification: # 信心程度系統 — 每條附「憑什麼是這層」的基礎
  high_confidence: [...] # ≥2-3 獨立來源 verbatim 一致
  single_source: [...] # 單源，標 need cross-check
  unverified: [...] # 搜尋後仍無 / 有反證 → 不寫進文章
---

# Research Report: {Title}

## 1. 觀點成型（Stage 0，含 §探索搜尋紀錄 ≥20 query）

記憶 anchor / 多元面貌 / 核心矛盾候選 2-3（多選一 + 為什麼）。

## 2. 搜尋日誌 / 方法論（Search Log）

全部 query（Stage 0 + Stage 1）逐條：`query → 一句話發現 → [source](URL)`，每條標 [中]/[英]/[一手]/[學術]/[反方]。
**negative finding 必記**（「搜尋 N 次未找到 X」「Y 機構未發布」）——搜了沒找到也是 finding。

## 3. Findings by sub-topic（§A / §B / §C …）

每個子題分章，每個 claim 後標**信度 + 基礎**（高信度〔A+B+C 多源〕/ 單一來源〔X 提及〕/ 必驗 / 未驗證）。
**數字分歧揭露**：多源不一致時寫出差異 + 怎麼處理（不靜默取一）；多口徑數字分開（交易額 vs 利益 vs 淨利）。
對標 gold standard 毒馬鈴薯 §1-§N。

## 4. 引語庫（verbatim quotes）

每條：逐字原文 + URL + 場合 + `Ctrl-F 可驗證 ✓/✗`。記者轉述分開標（「此為記者敘述，非直引」）。
找不到原文 → 標「改轉述不加引號」。
**「場合」欄禁止夾詮釋 gloss**（「寶哥=宋岳庭」這種同位語等號）——代稱指涉、身分推斷是獨立 atom，要寫進 §3 Findings 自帶信度標記，不准搭引語滑進庫（2026-06-09 嘻哈饒舌：orchestrator 在場合欄注入的 gloss 被 writer 忠實寫出、verifier 驗了引語沒驗 gloss → 讀者抓到）。

## 5. 反例 / 護欄（不能說的話 / 必驗反例 / 不採信清單）

出 fact 之前先列「這些推論錯誤要主動防範」+「雖然誘人但不能說的話」+「找到但不採信的線索 + 為什麼」。
（thesis-grade 跟一般報告最大分野。`政府/來源自身矛盾 > 正反並陳`。）

## 6. Clean Fact-Pack + Stage 2 操作規範（給 writer 的合成層，額外、不取代 raw）

去重乾淨事實 + 幻覺護欄 + 媒體 manifest + hook scene 候選（附時間軸）+ 5-8 小標題候選 +
不可忽略校正點 + **幻覺候選 Ctrl-F 清單**。Stage 2 writer 只吃這層。

## 7. 參考文獻 + Verification Table

全部 distinct 來源（標 [中]/[英]/[一手]/[學術]）+ 高風險 atom 表 `| claim | sources | Ctrl-F | 信度 | verdict |`。

## 8. Agent 原始輸出（raw，不摘要，append 全部）

每個研究 agent 的完整回報原文 verbatim 貼上（REFLEXES #22 raw 永不刪）。
```

#### 1.7.2 不摘要鐵律 × v6.3 編排的和解（v6.4 核心修補）

v6.3 多 agent 編排叫主 session「合成去重成 clean fact-pack」，但這跟 Step 1.7「agent 完整輸出，不摘要」**衝突** —— 這次 TDRI session 就是只留 fact-pack、丟掉 3 個 agent 的原始搜尋軌跡，report 退化成 192 行摘要。

**和解規則**：synthesis 是**疊加層**，不是替換。

1. 每個研究 agent 回報**完整搜尋軌跡 + 原始 findings**（不准自己摘要）。
2. 主 session 把**所有 agent 原始輸出 verbatim append 到 §8**（SSOT raw）。
3. 主 session **額外**合成 §6 Clean Fact-Pack 給 writer。
4. §6 是 §8 的蒸餾，不是 §8 的替代。**§8 缺席 = Stage 1 未完成**。
5. **落檔時機 = 收到回報的第一個動作**（v7.7）：async agent 的 task-notification `<result>` 一到，先 verbatim 落檔，才准做任何合成／蒸餾。「先摘要待會再補」＝柯智棠病（見 §鐵律 8）。**落檔的兩種形態**：(a) 直接 append 主報告 §8 inline；(b) 先寫 repo 內 sibling raw 檔 `{slug}-research-{X}.md`（async 場景較快、較不會撞主檔）。**但 sibling 是「中繼站」不是終點**——見下方 1.7.4。
6. **禁 ephemeral 存放**（v7.7）：session scratchpad、`/private/tmp`、tasks/\*.output pointer 都不是落檔——tmp 是倒數計時的刪除佇列（醫療 report 5 份 raw 就是這樣永久蒸發的）。raw 唯一合法的家在 git 內。

#### 1.7.4 合成單檔鐵律：sibling 是中繼站，Stage 2 前必 consolidate（v7.11）📦

> **觸發**：2026-07-12 台灣茶文化 panorama（哲宇 directive「research 階段分批做完之後，一定要合成同一篇歸檔同一篇大 research 歸 repo，現在都是散落的」）。該次 4 個研究 agent 各寫一個 sibling raw 檔（-rawA/-rawB/-rawC/-research-D），主報告 §8 只放 pointer 表——**5 個檔散落**，findability 差、跨文 re-use 難、審計要開 5 個檔。v7.10 以前 gate 明說「分檔金曲獎型也認」，等於祝福散落。

**鐵律**：**一篇文章的 research = 一個 repo 內的大檔**（`reports/research/{YYYY-MM}/{slug}.md`），§1-§8 全在裡面。sibling raw 檔只是 async 落檔的中繼站，**Stage 2 spawn writer 之前，orchestrator 必須**：

1. **Consolidate**：把每個 sibling raw 的**完整內容** verbatim inline 進主報告 §8（建議 `### §8.A / §8.B / …` 分節，標原 agent 子領域），不是留 pointer。
2. **Delete siblings**：合成後刪掉 `{slug}-research-*.md` / `{slug}-raw*.md`（git rm 或 unlink）——避免同內容兩份、避免下游不知道讀哪個。
3. **驗**：跑 `research-report-health.py`，§8 inline 密度自然 ≥ 120；`ls reports/research/{YYYY-MM}/{slug}-*.md` 應只剩主檔一個。

**為什麼是單檔不是分檔**：(a) findability——一個 slug 一個 research SSOT，grep / re-use / reader-callout 追源只開一個檔；(b) writer 只需 Read 一個檔就有全部 raw texture（分檔要 Read N 個，容易漏讀 = 飄移根因之一）；(c) 歸檔完整性——散落的 sibling 容易在 cleanup / worktree gc 時漏掉一兩個（呼應本 session 的圖檔差點變孤兒）。**中繼站的存在只為 async 落檔安全（鐵律 8），一旦合成完成它的任務就結束了。**

#### 1.7.3 HARD GATE：`research-report-health.py` 🔬

```bash
python3 scripts/tools/research-report-health.py reports/research/YYYY-MM/{slug}.md --tier=depth
```

驗收（depth tier）：distinct 來源 ≥ 25 / **英文來源 ≠ 0**（理想 ≥ 5）/ **一手來源 ≠ 0**（理想 ≥ 5）/ 有搜尋日誌 section / 信度標記 ≥ 8 / 行數 ≥ 300 / **§8 raw 有效密度 ≥ 120 行**（v2 HARD — inline 行數＋指向存在的 repo 內 raw 檔行數合計）/ **ephemeral pointer = 0**（v2 HARD — §8 指 /tmp 或 scratchpad 直接 FAIL）/ **合成單檔**（v3 WARN — 主報告旁還躺著 `{slug}-research-*` / `{slug}-raw*` sibling = 未 consolidate，per [Step 1.7.4](#174-合成單檔鐵律sibling-是中繼站stage-2-前必-consolidatev711-)）。**final 形態＝單檔楊德昌型**；分檔金曲獎型只是 async 中繼，Stage 2 前必合成 + 刪 sibling。**hard_fail > 0 = 不進 Stage 2**（回去補搜尋 + 把原始軌跡寫回 SSOT）。儀器化背景：把 §Step 1.1 的 4 條來源配額從 aspirational 變可量測（REFLEXES #15）；v2 兩條把 §鐵律 8「orchestrator aggregate-on-receive」從紀律變閘門——柯智棠病例（§8 = 9 行 pointer 指 scratchpad）在 gate v1 是 PASS，v2 是雙 hard fail。**v2.1 疑慮通知層**：每條 fail/warn 附「為什麼＋思考方向」給呼叫 session 決策（`--json` 含 `concerns[]`）；上游每份分部報告另有收件 gate `agent-report-health.py`（Step 1.8-bis 步 2，收到就跑、FAIL 不准合成）。

**好處**（[REFLEXES #22 raw 永遠不刪](../semiont/DNA.md) + [MANIFESTO §造橋鋪路](../semiont/MANIFESTO.md)）：

- Audit trail / 跨文 re-use / agent prompt tuning 樣本 / 時間切片對照（同舊版）
- **+ SSOT**：reader callout 質疑某 claim → 直接在 §7 Verification Table + §8 raw 追到當時逐字來源，不用重搜

**存檔責任**：Stage 1 主 session 在 agent 回傳後**同一個 response** 內寫 §1-§8 完整檔 + 跑 research-report-health gate，不 defer。raw §8 缺席或 gate hard_fail = Stage 1 未完成。

**讀取責任**：Stage 2 Write 開始前，grep `reports/research/` 看有無相關主題報告可 cross-reference。**Writer agent 讀整份 research report（§6 fact-pack ＋ §8 raw verbatim 全部）**——§6 只是 navigation aid，不是 writer 的唯一食物（v7.4 修正，per §多 agent 編排鐵律 2；本行原寫「只吃 §6」是 v6.3 殘留，2026-07-05 對齊）。

#### Step 1.7 附：reports/ 頂層 ad-hoc report 命名 convention（2026-05-27 新增）

> ⚠️ 本附則約束 **Stage 1 research report 以外** 寫到 `reports/*.md` 頂層的 ad-hoc 報告（design / plan / analysis / audit / evaluation / evolution / proposal / ops / semiont-analysis 等）。Stage 1 research report 維持 `reports/research/{YYYY-MM}/{article-slug}.md` 格式不變。
>
> 觸發：[reports/reports-archival-audit-2026-05-27.md](../../reports/reports-archival-audit-2026-05-27.md) §4 Layer 2 — 113 個頂層 ad-hoc report 命名整齊但 prefix 自由式，9 type bucket 規律僅 corpus 萃取存在，未升 canonical 規範。

**命名格式（推薦）**：

```
{type}-{topic}-{YYYY-MM-DD}.md
```

**9 type bucket**（從 corpus 萃取 + audit §2.3 規範 + `scripts/tools/generate-reports-index.py` plugin gate）：

| Type            | 用途                                                                                                    | 範例                                               |
| --------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| `design`        | 設計提案 / 系統設計                                                                                     | `become-boot-mode-design-2026-05-13.md`            |
| `plan`          | 執行計畫 / orchestration / planning                                                                     | `historic-districts-series-planning-2026-05-21.md` |
| `evolution`     | 進化計畫 / roadmap / spec                                                                               | `homepage-evolution-2026-05-26.md`                 |
| `analysis`      | 數據分析 / investigation / deep-research / discussion                                                   | `ai-crawler-404-analysis-2026-04-18.md`            |
| `audit`         | 體檢 / snapshot / hygiene 盤點                                                                          | `reports-archival-audit-2026-05-27.md`             |
| `audit-routine` | Routine 自動產出的 audit（routine-audit / sense / heartbeat / homepage-evolution / self-evolve-weekly） | `routine-audit-2026-05-27.md`                      |
| `evaluation`    | A/B test / fit-check / POC / 模型評估                                                                   | `editorial-v6-ab-test-2026-05-09.md`               |
| `proposal`      | 提案 / strategy（要哲宇拍板的）                                                                         | `2026-election-evolution-proposal-2026-05-27.md`   |
| `ops`           | 操作報告 / triage / handoff / fix（unmatched fallback）                                                 | `issue-1059-triage-2026-05-21.md`                  |
| `semiont`       | 其他組織 semiont-analysis（NMTH / TFT / PanSci / NML / ThinkingTaiwan）                                 | `PanSci-semiont-analysis-2026-05-18.md`            |

**規則**：

- **新加報告先過命名 check**：寫到 `reports/*.md` 頂層之前先想「這屬於哪個 type bucket」。命中 → 用對應 prefix；命不中 → 用 `ops` fallback
- **不搬既有檔**：113 個既有頂層 \*.md 維持原命名（per audit §3「不搬家成本太高 / 239 references」）。本規範只約束新加 report
- **subdir 不受規範約束**：`reports/research/{YYYY-MM}/{slug}.md` 用 article-slug；`reports/probe/YYYY-MM-DD.md`、`reports/weekly/YYYY-MM-DD.md` 用 date；`reports/ab-tests/`、`reports/music-media-audit/`、`reports/translation-research/`、`reports/harvest/` 各有自己 convention，皆健康
- **type 增加 SOP**：若實際寫作出現第 10+ type，先 append [audit report §4 Layer 2](../../reports/reports-archival-audit-2026-05-27.md) 規範 → 同步加入 `scripts/tools/generate-reports-index.py` TYPE_BUCKETS regex
- **歸檔自動分桶**：每日 06:00 + 23:00 `bash scripts/tools/refresh-data.sh` Step 13 跑 `generate-reports-index.py` 自動 regen `reports/INDEX.md`，按 9 type × 月份 雙軸索引

**為什麼這條 convention**：

- 9 type bucket 不是 top-down 設計，是 113 file corpus 真實規律的命名（per audit §2.3 regex distribution）
- 對未來自己最大幫助：grep `reports/*-design-*` 找 design / `reports/*-audit-*` 找 audit，~90% noise reduction
- 對 fork Taiwan.md 的人最大幫助：copy `reports/INDEX.md` + `scripts/tools/generate-reports-index.py` 立刻有同樣的 observability

**反例**（避免）：

```
❌ 2026-election-evolution-proposal-2026-05-27.md  # double-date prefix 冗餘
✅ election-evolution-proposal-2026-05-27.md       # 單 date suffix

❌ P1-batch-repair-2026-05-13.md                   # tier-letter prefix 是 internal label 不對外
✅ ops-p1-batch-repair-2026-05-13.md               # ops 是 routine ops report

❌ daily-heartbeat-2026-04-11.md                   # heartbeat 是 routine 名稱不是 type
✅ audit-routine-heartbeat-2026-04-11.md           # audit-routine 更明確
```

### Step 1.8: Spawn agent 選型 🤖

Stage 1 spawn 研究 agent 時，**必須先判斷需不需要直接落檔**：

| Agent 類型        | Write 權限               | 適用情境                                        |
| ----------------- | ------------------------ | ----------------------------------------------- |
| `Explore`         | ❌ read-only（系統強制） | 純 research、結果回主 session 由主 session 落檔 |
| `general-purpose` | ✅ 有 Write              | 需要 agent 直接寫入 `reports/research/YYYY-MM/` |

**判斷流程**：

- 研究量大（50+ URLs、需要長篇結構化輸出）→ 用 `general-purpose`，prompt 明確要求「直接寫入 `reports/research/YYYY-MM/{slug}.md`」
- 研究會回到主 session 處理 → 用 `Explore`（較專精、較便宜）

**歷史教訓**：

- `feedback_agent_writefile_hallucination` memory：「agent 說自己不能寫檔是幻覺」對 general-purpose 成立，**對 Explore 不成立**——Explore 真的 read-only
- 2026-04-20 吳哲宇 EVOLVE 第一次 spawn Explore 要求寫檔、被退回、改 spawn general-purpose 成功
- spawn 之前先確認 agent type，省一輪來回

#### Step 1.8-bis: Async agent 時代的 raw 保全 SOP（v7.7，2026-07-05）⚠️

Claude Code 改版後 agent 預設 async 啟動：spawn 的 tool result 只回「launched successfully + output_file 路徑」，真正的回報以 **task-notification `<result>`** 送達，output_file 指向 tasks/\*.output（→ subagent transcript symlink，隨 session 清理蒸發）。這改變了 raw 的存亡結構——**訊息通道與 tmp 都不可信任，唯一可信的是 repo 內的檔案**。

**強制三步**（每個研究 agent、每次）：

1. **Prompt 要求 agent 自己落檔**（雙保險上半）：general-purpose agent 的 prompt 加一句「先用 Write 把完整回報寫到 `reports/research/{YYYY-MM}/{slug}-research-{X}.md`，再把同樣內容當 final message 回傳」。agent 寫檔成功 → raw 已在 repo，訊息通道只是副本。
2. **收件 gate：notification 到手先落檔、跑儀器、再合成**（雙保險下半，v7.8 儀器化）：主 session 收到 task-notification 的**第一個動作**是確保分部報告在 repo 路徑（agent 沒落檔 → 把 `<result>` **verbatim** 寫進該路徑，一字不改），然後跑：

   ```bash
   python3 scripts/tools/agent-report-health.py reports/research/{YYYY-MM}/{slug}-research-{X}.md --claimed {該 agent 的搜尋配額}
   ```

   儀器驗七件事（存放位置 / 體積 8KB 分界 / 軌跡 section / 軌跡 ≥10 行 / 宣稱 vs 記錄比 / 五段結構 / **來源溯源率 v3**——見 [Step 1.8-ter 輸出契約](#step-18-ter-研究-sub-agent-輸出契約來源逐條可溯v710-)），每條疑慮附「為什麼＋思考方向」。**FAIL = 不准開始合成 §6**（先照思考方向救 raw：notification 原文 → subagent transcript → SendMessage 要求補報）；CONCERN = 可續行但 orchestrator 回報必須明示每條處置。閾值由 2026-07-05 真實 corpus 校準（壓縮版 5-6KB/軌跡 2-9 行 vs 真 final 14-38KB/13-62 行，兩側 ≥2x margin）；非搜尋型 agent（persona / verifier）用 `--min-kb` `--min-trail` 調整或免跑。

3. **Gate 收口**：組完 report 跑 `research-report-health.py`——§8 有效密度 ＋ ephemeral pointer 兩條 v2 hard gate 會攔住任何漏網，v2.1 起每條 fail/warn 同樣附疑慮通知（見 Step 1.7.3）。

**反例（附給 sub-agent prompt 用，anti-example beats rule）**：2026-07-05 柯智棠 EVOLVE——prompt 寫對了（「絕對不要自己摘要濃縮，raw 全留」）、4 隻 agent 全照做（各回 ~20KB 逐條軌跡，實測 224 次 web 操作），orchestrator 收到通知後卻把每份壓成 ~6KB 主題摘要存 scratchpad，report §8 剩 9 行。**斷點不在 agent、不在 prompt，在 orchestrator 收到之後的 30 秒**。

#### Step 1.8-ter: 研究 sub-agent 輸出契約——來源逐條可溯（v7.10）📎

> **觸發**：2026-07-12 台灣茶文化 panorama（哲宇 callout「footnote 會寫不精準」）——3 隻研究 agent 交叉驗證都真做了（24 搜尋＋17 PDF 直讀那種等級），但 84 條【來源】行只有 ~35% 帶 URL，其餘轉錄成「WebSearch 綜合（新浪博客／豆瓣／大紀元）」aggregate 標籤：**逐字引語活著、URL 蒸發**。無我茶會三個精確到「日」的日期全部斷源——寫進文章就是 unfootnotable claim。病根兩層：(1) Claude 改版後 WebSearch 回傳聚合摘要，agent 預設把「摘要」當「來源」；(2) 每個 session 即興寫 spawn prompt（該次用「三塊各一 section」自創格式），agent 輸出跟著漂移，五段骨架與儀器全對不上。**鐵律 9 是哲學，本 step 是可 copy-paste 的操作契約。**

**契約全文＋通用派發 prompt＋分部報告輸出模板＋anti-example 庫 → [RESEARCH-AGENT-PROMPT.md](RESEARCH-AGENT-PROMPT.md)（唯一 copy-paste 載體，禁即興改寫；本 step 不複寫契約條文——殼核不對稱教訓，dna-audit §S5）**。五條契約的骨架：五段骨架 / 每來源一行（禁 aggregate 標籤）/ 逐字必綁 URL / 先落檔再回報 / 信度三層。

**收件驗收（Step 1.8-bis 步 2 的 gate 自動涵蓋）**：`agent-report-health.py` v3 溯源率檢查——來源行 ≥ 5 時，可溯率 < 60% = **hard FAIL（不准合成）**、< 85% = warn。可溯 = 完整 URL / repo 路徑 / 正式書目（《刊名》＋期／頁）/ 同上前引。校準 corpus：該攔 rawA 38% / rawB 36%，該過（帶警）rawC 67%。

**為什麼 prompt 禁即興**：per [feedback_routine_prompt_contract]（prompt 禁複寫 SOP、pointer 到 canonical）＋本次實證——即興 prompt 寫了「每 finding 標【來源】URL」十個字，agent 在多來源場景自行發明了 aggregate 寫法；契約塊把「多來源怎麼寫」顯式化，儀器把它變可退件。
