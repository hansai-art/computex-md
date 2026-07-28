---
title: 'BRANCH-PIPELINE'
description: '知識分支分析器 v2.2 — Mode 分流 (single-article / broad-theme) + spawn N parallel agents pattern + ARTICLE-INBOX 銜接 SOP + Hard Gate Inventory + /twmd-article-inbox skill 入口 + 素材 intake 前處理 + 台灣建築 dogfood 九摩擦回寫'
type: 'pipeline-canonical'
status: 'canonical'
current_version: 'v2.2'
last_updated: 2026-07-18
last_session: '2026-07-18-111730-inbox-skill'
sister_docs:
  - 'REWRITE-PIPELINE.md'
  - 'EVOLVE-PIPELINE.md'
  - 'PEER-INGESTION-PIPELINE.md'
upstream_canonical:
  - '../semiont/MANIFESTO.md'
  - '../editorial/RESEARCH.md'
---

# BRANCH-PIPELINE.md — 知識分支分析器 v2.2

> 觀察者給 theme / article → 拆解知識結構 → 找出缺口 → 寫 research report → 萃取 ARTICLE-INBOX candidates。
> 「Taiwan.md 的知識不該是孤島，每篇文章都是一棵樹，我們要看見整座森林的缺口。」
>
> v2.0 設計理由：對齊 [SOCIAL-POSTING v0.6](SOCIAL-POSTING-PIPELINE.md) + [MEMORY v2.1](MEMORY-PIPELINE.md) + [EVOLVE v3.5](EVOLVE-PIPELINE.md) spine restoration pattern。修補 v1.0 結構問題：(1) 只 handle single-article 拆解，不涵蓋 broad-theme 場景；(2) 缺 spawn N parallel agents pattern；(3) report 寫完後沒銜接 ARTICLE-INBOX；(4) Hard Gate 散落 / 無集中索引；(5) 缺 ASCII spine。

---

## 🗺️ ASCII spine

```
╭──────────────────────────────────────────────────────────────────────────╮
│         BRANCH-PIPELINE — 知識分支分析 6 stage                           │
│                                                                          │
│   🧭 核心紀律                                                            │
│            ├── 連結密度 = 最強 priority signal（能跟 5+ 文章互連 > 孤立）│
│            ├── 策展 ≠ 百科（不是所有缺口都填）                           │
│            ├── 人物嚴格知名度門檻（People 已 140+）                      │
│            └── Agent claim verify 鐵律（per feedback_agent_writefile）   │
│                                                                          │
│   ──── Mode 分流（單篇 vs 大主題）─────────────                          │
│            ├── Single-article mode: 觀察者「分析 X 文章」                │
│            │     → Stage 1 拆解 → Stage 2-5（單 session 跑完）           │
│            └── Broad-theme mode: 觀察者「研究台灣 X」（範圍大）          │
│                  → Stage 4 spawn N parallel agents 各跑一個 sub-theme    │
│                  → Stage 5 aggregate + ARTICLE-INBOX append             │
│                                                                          │
│   ──── Stage 0-5 主流程 ──────────────────────────────────────          │
│                                                                          │
│   Stage 0: Mode 判斷 ──→ scope assessment                                │
│            └── single-article / broad-theme / hybrid                    │
│                                                                          │
│   Stage 1: 主題拆解 ──→ Decomposition                                    │
│            ├── 核心主題 / 人物 / 地點 / 時間 / 機構 / wikilink           │
│            └── 既存 article baseline check（避免重複研究）               │
│                                                                          │
│   Stage 2: 知識庫交叉比對 ──→ Cross-Reference                            │
│            └── ✅ 已存在 / 🔗 部分涵蓋 / ❌ 完全缺失 三類                │
│                                                                          │
│   Stage 3: 知識缺口分析 ──→ Gap Analysis + priority                      │
│            └── 重要性 × 0.3 + 獨立性 × 0.2 + 可研究性 × 0.2              │
│                + 連結密度 × 0.3                                          │
│                                                                          │
│   Stage 4: Research（執行）──→ Mode 分流                                 │
│            ├── Single-article: 主 session 直接跑 web research            │
│            └── Broad-theme: spawn N parallel general-purpose agents     │
│                  ↳ Hard gate: agent claim verify (Write file existence) │
│                  ↳ Hard gate: 中文 prompt verbatim + 三源驗證            │
│                                                                          │
│   Stage 5: Aggregate + ARTICLE-INBOX append ──→ ship                     │
│            ├── Aggregate N sub-reports → master report                   │
│            ├── 萃取 candidates 按 P0/P1/P2 排序                          │
│            ├── 不重複既有 ARTICLE-INBOX pending entries                  │
│            └── git commit + push                                         │
│              ↳ Hard gate: candidate 含對比理由 + cross-link suggestion   │
│              ↳ Hard gate: 連結密度當主 priority signal                   │
│                                                                          │
│   ✅ Candidates appended to ARTICLE-INBOX                                │
│                                                                          │
│   ──── 跟其他 pipeline 的 boundary ──────────────────                   │
│   → EVOLVE-PIPELINE: GA4 + SC 數據驅動單 article candidate (本檔互補)    │
│   → PEER-INGESTION-PIPELINE: 外部 source 策展 (本檔內部知識缺口)         │
│   → REWRITE-PIPELINE: 從 ARTICLE-INBOX pick candidate 跑 5-stage         │
╰──────────────────────────────────────────────────────────────────────────╯
```

---

## 🚦 Hard Gate Inventory（一張表 audit 全 pipeline）

| Gate                                        | 觸發 stage | 條件                    | 工具                                                                                                                                                               | 不過 = ?                               |
| ------------------------------------------- | ---------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------- |
| Mode 判斷對                                 | Stage 0    | broad-theme 別當 single | manual scope 估算（單 session 跑得完 vs 拆 N agents）                                                                                                              | wrong mode = 跑不完 / 不必要 parallel  |
| 既存 article baseline check（雙層）         | Stage 1    | 拆解前                  | **檔名層 `find -name "*{kw}*"` 優先** + 內文層 grep 補充；禁 `\| head -N` 截斷判讀（v2.2：內文 grep 曾漏掉大稻埕專篇）                                             | 重複研究浪費 token / 誤提 P0           |
| Agent claim verify (Write)                  | Stage 4    | broad-theme N agents    | `ls + wc -l` 每個 agent 回報的 path，**一律絕對路徑**（v2.2：Bash cwd 會靜默跳回主 repo，相對路徑撲空會誤判 agent 幻覺，cross-ref LESSONS shell-cwd-silent-reset） | agent hallucination silent ship / 誤判 |
| 中文 prompt verbatim                        | Stage 4    | agent prompt 寫法       | manual（中文 query + 不英文回譯）                                                                                                                                  | 觸犯 EDITORIAL §挖引語制度紅線         |
| 三源驗證                                    | Stage 4    | 重要事實                | per agent 寫進 prompt（≥ 2-3 獨立 source）                                                                                                                         | REFLEXES #16 違反                      |
| Dedup 三查（pending + DONE-LOG + baseline） | Stage 5    | append 前               | grep ARTICLE-INBOX + ARTICLE-DONE-LOG + knowledge/；**命中必讀 context 判「專篇 vs 順帶提及」**，count 單獨會誤判（v2.2）                                          | duplicate / 幽靈 candidate             |
| Candidate 含對比理由                        | Stage 5    | append 前               | manual（「為什麼這篇 vs 其他」reasoning trace）                                                                                                                    | maintainer 看不出優先序                |
| 連結密度當主 priority signal                | Stage 3    | candidate scoring       | 計算能跟幾篇 cross-link                                                                                                                                            | 孤立缺口優先序虛高                     |
| 策展 ≠ 百科                                 | Stage 3    | candidate 篩選          | manual（不是所有缺口都填）                                                                                                                                         | 庫膨脹 + 維護成本 explode              |
| 人物知名度門檻                              | Stage 3    | People 類別 candidate   | grep `knowledge/People/_PEOPLE-ROADMAP.md`（200 人計畫 SSOT）+ manual 裁決（≥ 國民級知名度 / 真實重要性；v2.2 接上現成 SSOT）                                      | People 已超載                          |
| git commit + push                           | Stage 5    | 收官                    | git                                                                                                                                                                | 沒記錄 = 沒做                          |

---

## ⚠️ Top 5 最常忘的 step

> 從 2026-05-23 台灣詩人研究 session + REFLEXES #4 #16 + feedback_agent_writefile_hallucination 抽 friction 最高的 5 條。

1. **Mode 判斷對 vs 別當 single-article** — broad-theme（「研究台灣詩人」「研究台灣歷史人物」）scope 大時必須拆 N agents，硬塞單 session 跑不完 / 出來薄
2. **Agent claim verify 鐵律** — sub-agent 報「Write 完成檔案路徑 X」後主 session **必 grep verify 檔案存在 + 字數對得起來**，agent hallucination 是結構性風險（per feedback_agent_writefile_hallucination）
3. **既存 article baseline check** — 拆解 / 派 agent 前先 `grep -l "$topic" knowledge/` scan baseline，agent prompt 寫「已 ship 不需研究只 mention」避免重複工作
4. **中文 prompt verbatim 跟三源驗證** — agent prompt 必含「中文 query + 不要英文回譯 + 三源 cross-check」三鐵律，否則出來的 research 是 AI 摘要 hallucination（per RESEARCH.md + REFLEXES #23 毒樹果實鏈）
5. **ARTICLE-INBOX candidate 含對比理由** — 「為什麼這個 candidate 比其他優先 / 跟既有 X 文章的差別」reasoning trace 必寫，maintainer 看才知道優先序

---

## 跨檔案職責分工

| 檔案                                                     | 範圍                                                                        |
| -------------------------------------------------------- | --------------------------------------------------------------------------- |
| **本檔**                                                 | 知識分支分析 — 拆解 theme / article → 找缺口 → spawn agents → ARTICLE-INBOX |
| [EVOLVE-PIPELINE.md](EVOLVE-PIPELINE.md)                 | 數據驅動 candidate (GA4 + SC + GitHub feedback) → ARTICLE-INBOX (本檔互補)  |
| [PEER-INGESTION-PIPELINE.md](PEER-INGESTION-PIPELINE.md) | 策展外部 peer source (TFT / NMTH) → ARTICLE-INBOX                           |
| [REWRITE-PIPELINE.md](REWRITE-PIPELINE.md)               | 寫實際文章（從 ARTICLE-INBOX pick candidate 跑 5-stage）                    |
| [ARTICLE-INBOX.md](../semiont/ARTICLE-INBOX.md)          | candidate 輸出位置                                                          |
| [RESEARCH.md](../editorial/RESEARCH.md)                  | 中文 prompt verbatim + 三源驗證 baseline                                    |

**邊界**：

- **EVOLVE** 是「數據先行」（GA / SC 告訴你哪些缺口已有需求）
- **本檔（BRANCH）** 是「結構先行」（拆解一個 theme / article 找延伸主題）
- 兩者都產 ARTICLE-INBOX candidate，source 不同。一個 theme 大到要拆 N agents 是本檔 broad-theme mode 場景，single article 拆解是 v1.0 single-article mode 場景

---

## 觸發方式

### Skill 入口（v2.1 新增）

**[`/twmd-article-inbox`](../../.claude/skills/twmd-article-inbox/SKILL.md) 是本 pipeline 的正式 skill 觸發層**（2026-07-18 誕生，設計報告：[reports/design-article-inbox-evolve-mode4-2026-07-18.md](../../reports/design-article-inbox-evolve-mode4-2026-07-18.md)）。觀察者說「把 X 加進 article inbox」「/twmd-article-inbox X」時走這條。核心語意：**進 inbox 的每條 entry 都要經過本 pipeline 消化**（baseline check + 缺口分析 + 連結密度 + 對比理由），raw 主題直接塞 inbox 是反面。mode 判斷照 Stage 0，skill 殼不複寫判準。

### 素材 intake 前處理（v2.1 新增）

觀察者丟的不是明確主題而是**素材**（URL / 一段文字 / 半成形想法 / Issue 內文）時，Stage 0 前先做一步消化：讀素材 → 萃取 1-3 個候選 theme + 初步 candidate 雛形 → 回到 Stage 0 判 mode。這是輸入軸的前處理，不是新 mode（mode 軸留給 scope，混在一起是 REFLEXES #38 混維度）。

### Single-article mode（v1.0 既有）

觀察者說「分析 X」、「branch analysis X」：

```
分析「文章名」
```

例：`分析「二二八事件」`、`分析「夜市文化」`、`分析「曾雅妮」`

### Broad-theme mode（v2.0 新增）

觀察者說「研究 X」、「針對 X 做大資訊化研究」、「找 X 領域所有可開發 candidates」：

```
針對台灣從以前到現在的詩人，做完整大資訊化研究...
研究台灣戰後歌曲 1949-2026 所有重要 cluster...
針對台灣科技史人物全 sweep 出來放 ARTICLE-INBOX...
```

判準：scope 大到 1 session 直接 web search 跑不完（30+ 候選 / 跨多個時代 / 跨多個語言路線）→ broad-theme，必拆 N agents。

---

## Stage 0 — Mode 判斷（v2.0 新增）

寫 prompt / spawn agent 前先判斷 mode，避免 wrong mode 浪費 token。

### Single-article mode 判準

- 觀察者明說「分析 X 文章」/「branch X」/「分析「Y」」
- Scope 是 1 篇既存 article 的延伸主題拆解
- 預計拆出 5-15 個延伸 candidate
- 主 session 1-2 hr 可跑完所有 web check + report 撰寫

→ 走 v1.0 既有 Pipeline 四階段，主 session 直接執行。

### Broad-theme mode 判準

- 觀察者說「研究台灣 X」/「對 X 領域所有 case 做研究」/「完整大資訊化研究」
- Scope 跨多個時代 / 多個 sub-cluster / 30+ 候選
- 預計拆出 N (3-6) 個 sub-theme，每個 sub-theme 又包含 5-15 個候選人物 / movement
- 單 session 跑會 token explode / coverage 不全

→ 走 v2.0 新增 spawn N parallel agents pattern（見 Stage 4）。

### Hybrid mode（罕見）

- 觀察者「分析 X 文章 + 拆出 series」（如「分析二二八事件 + 拆出相關歷史事件 series」）
- single-article 拆解 + broad-theme series 萃取並行

→ Stage 1-3 走 single-article；Stage 4 視 series 規模決定 spawn agents 或主 session 跑。

---

## Pipeline 四階段（v1.0 既有，Stage 1-3 跨 mode 共用）

### Stage 1：主題拆解（Decomposition）

讀取目標文章，拆解成結構化主題樹：

```
📄 目標文章
├── 🏷️ 核心主題（1-3 個）
├── 👤 提及人物（所有人名）
├── 📍 提及地點（所有地名）
├── 📅 提及時間（關鍵年份/時期）
├── 🏛️ 提及機構/組織
├── 🔗 現有 wikilink（文章內已連結的頁面）
└── 🌿 延伸主題（從內容推導，每個核心主題 3-5 個分支）
```

**執行方式：**

```bash
# 1. 讀目標文章
cat ~/taiwan-md/knowledge/{category}/{article}.md

# 2. 提取 wikilink
grep -oP '\[\[([^\]]+)\]\]' article.md | sort -u

# 3. 提取 tags
grep "tags:" article.md
```

### Stage 2：知識庫交叉比對（Cross-Reference）

將拆解出的主題，與現有 422 篇文章比對：

```bash
# 取得現有文章清單
find ~/taiwan-md/knowledge/ -name "*.md" \
  -not -path "*/en/*" -not -path "*/es/*" -not -path "*/ja/*" \
  -not -path "*/resources/*" -not -name "_*" \
  | sed 's|.*/||;s|\.md$||' | sort > /tmp/existing-articles.txt

# 搜尋相關文章（用 grep 或語意匹配）
for topic in "${extracted_topics[@]}"; do
  grep -ril "$topic" ~/taiwan-md/knowledge/ --include="*.md" | head -5
done
```

**比對分類：**

| 狀態        | 意義                             | 動作                 |
| ----------- | -------------------------------- | -------------------- |
| ✅ 已存在   | 知識庫有這篇文章                 | 建議加 wikilink 連結 |
| 🔗 部分涵蓋 | 在其他文章中被提及但沒有獨立頁面 | 評估是否值得獨立成篇 |
| ❌ 完全缺失 | 知識庫完全沒有                   | 標記為知識缺口       |

### Stage 3：知識缺口分析（Gap Analysis）

對每個「❌ 完全缺失」的主題，進行深度評估：

```
🕳️ 知識缺口評估
├── 重要性（1-5）：對理解台灣有多重要？
├── 獨立性（1-5）：能獨立成篇還是只適合作為段落？
├── 可研究性（1-5）：有足夠公開資料可以寫嗎？
├── 連結密度：能跟幾篇現有文章互連？
└── 建議分類：放在哪個 category 最合適？
```

**優先級公式：**

```
priority = 重要性 × 0.3 + 獨立性 × 0.2 + 可研究性 × 0.2 + 連結密度 × 0.3
```

連結密度權重最高 — 能跟越多現有文章互連的主題，對整個知識庫的價值越大。

> **v2.2 誠實化**：這條公式是**思考框架，不是計算義務**——v1.0 至今沒有一次被逐項計分過，強制填表只會變 performative compliance。唯一必附數字的是**連結密度**（列出具體可互連的 article path）；其餘三維用判斷，但判斷要寫成對比理由。人物類 candidate 另過 `_PEOPLE-ROADMAP.md`（200 人計畫）門檻對照。

### Stage 4：Research 執行（v2.0 mode 分流）

#### Single-article mode（v1.0 既有）

主 session 直接跑 4-8 次 WebSearch + 必要 WebFetch，撰寫研究計畫報告。

#### Broad-theme mode（v2.0 新增 — spawn N parallel agents）

**判準成立後**（scope 大 + 30+ candidates + 跨多 sub-cluster）→ spawn 3-6 個 parallel `general-purpose` sub-agents 各跑一個 sub-theme。

**Spawn pattern**：

```
# 1. 主 session 先 baseline scan
echo "=== Existing coverage ==="
for p in $candidate_list; do
  if [ -f "knowledge/People/$p.md" ]; then echo "✅ $p"; else echo "❌ $p"; fi
done

# 2. Aggregate 結果 — 哪些已有不需研究 + 哪些是缺口

# 3. Spawn N agents（一個 message 發 N 個 Agent tool call parallel）
# 每個 agent 負責一個 sub-theme，獨立 web search + 寫獨立 report file
```

**Agent prompt 鐵律**（每個 sub-agent 都要明寫）：

```markdown
1. **中文 prompt verbatim** — 跟中文 source 查時用中文 query，不要英文回譯（per MEMORY「WebFetch Chinese Verbatim」rule + REFLEXES #23 毒樹果實鏈）
2. **三源驗證** — 重要事實（生卒、首部代表作、verbatim 引語）至少 2-3 個獨立來源 cross-check（per REFLEXES #16）
3. **不要憑記憶** — 每個事實都從 web search 結果取
4. **Verbatim 引語必須 100% 正確** — 名句要 cross-check 原文
5. **Write 一定要實際執行** — 寫完後再讀一次自己 Write 的檔案確認存在
6. **回報時附完整檔案路徑 + 字數 + 涵蓋人物/movement 數**
7. **已存在 article 只 mention 不研究**（避免浪費 agent token）
8. **主 session 必須把 baseline 已存在清單逐條附進 prompt**（v2.2——只寫「已存在只 mention」agent 不知道哪些已存在；清單來自 Stage 1 雙層 baseline scan）
9. **人物類 sub-theme 必要求誠實門檻評估**（v2.2——prompt 明寫「誠實評估每位是否過 People 門檻，過不了就建議群像/合併形式」；台灣建築 dogfood 中這條產出了全場品質最高的策展判斷）
```

**Output schema**（每個 agent 獨立寫到 `reports/research/{YYYY-MM}/{theme}-{N-slug}.md`）：

```markdown
# {Theme} 研究 — 第 N 部：{sub-theme name}

> 研究範圍：{covered topics}
> 資料來源：[列 web source]

## 一、{sub-section heading}

（每個人物 / movement ~200-400 字 brief）

## 二、{sub-section heading}

...

## 研究觀察 + ARTICLE candidates 提示

- 哪些 candidate 最值得 Taiwan.md article 開發（priority hint P0/P1/P2）
- 哪些 sub-cluster 可做 series 而非單篇
- 跟既有 knowledge/ 的 cross-link 建議
```

**Agent claim verify 鐵律**（per feedback_agent_writefile_hallucination 升 hard gate）：

```bash
# 每個 agent 完成後主 session 必跑
ls -la reports/research/{YYYY-MM}/{theme}-{N}-*.md
wc -l reports/research/{YYYY-MM}/{theme}-{N}-*.md
```

- 檔案不存在 → agent hallucinate write 了。主 session 必須補寫 / 重派 agent
- 字數 < 預估 / 涵蓋 candidate 數 < 預估 → 品質不夠，補派 follow-up agent

**併行 vs 序列**：

- **併行**：sub-theme 之間沒順序依賴（每個 era 獨立研究）→ N agents 同 message spawn parallel
- **序列**：sub-theme 有依賴（後者要參考前者結果）→ wait + chain

### Stage 5：Aggregate + ARTICLE-INBOX append（v2.0 新增）

#### Single-article mode

Stage 4 主 session 寫完 report 後直接萃取 candidate 進 ARTICLE-INBOX（per Stage 4 既有 Research Plan 輸出格式）。

#### Broad-theme mode

##### 5.1 Aggregate N sub-reports → master report

```bash
# 主 session 讀每個 sub-report file
cat reports/research/{YYYY-MM}/{theme}-1-*.md
cat reports/research/{YYYY-MM}/{theme}-2-*.md
...
```

寫 master report 到 `reports/research/{YYYY-MM}/{theme}-comprehensive.md`，結構：

```markdown
# {Theme} 完整研究 — 大資訊化 master report

> 4 sub-agents 平行研究 + aggregate
> Total coverage: N 個人物 / M 個 movement / O 個 sub-cluster

## 一、{Sub-theme 1 title}

（從 sub-report 1 摘要 + cross-link）

## 二、{Sub-theme 2 title}

...

## N+1、研究總觀察

- 跨 sub-theme 的 pattern observation
- 哪些 cluster 最值得優先 ship
- Series 萃取建議
- **多 agent 獨立收斂的題目**（≥2 個互不知情的 agent 提同一題 = 最硬的缺口訊號，priority 升權）
- **agent 間判斷衝突與主 session 裁決**（v2.2——衝突不能靜默擇一，裁決理由留痕）

## N+2、候選處置總表（v2.2 必含）

全部 candidate 提示分三類，**被拒的也要留痕跡**——否則下次同 theme branch 會原樣再推薦一遍（重複推薦病，跟 inbox 幽靈同型）：

| 類                  | 內容                                          |
| ------------------- | --------------------------------------------- |
| ✅ 進 ARTICLE-INBOX | 本輪 append 的 entries                        |
| 🕰️ 次波 pool        | 值得做但本輪不進 INBOX（策展 ≠ 百科，不灌水） |
| ✗ 不做              | 附理由（dedup 命中 / 清單性質 / 併入既有文）  |

## 附錄：sub-reports 完整檔案

- [{theme}-1-{slug}.md]({theme}-1-{slug}.md)
- [{theme}-2-{slug}.md]({theme}-2-{slug}.md)
  ...
```

##### 5.2 ARTICLE-INBOX candidates 萃取

按 priority 排序寫進 [ARTICLE-INBOX.md](../semiont/ARTICLE-INBOX.md)。**Entry 格式以 [ARTICLE-INBOX §Entry Schema](../semiont/ARTICLE-INBOX.md#entry-schema) 為唯一 canonical**（v2.1 收斂：本檔原自帶一份 format 已與 schema 漂移——`Source`/`預估時間` 欄位 vs schema 的 `Requested`/`Notes`/`Reference`——per 指標 over 複寫，計數與格式只住一處）。branch analysis 產出的 candidate 額外要求：

- **Requested** 欄寫 `{YYYY-MM-DD} by branch-analysis — {theme} (session {id})`
- **Notes** 欄必含**對比理由**（為什麼這個 candidate 比其他優先）：連結密度（能跟 N 篇現有文章互連，列具體 path）+ SC opportunity（如有）+ 跟既有 article 的 cross-link 建議
- **Reference** 欄指向 `reports/research/{YYYY-MM}/{theme}-{N}-{slug}.md §{section}`

##### 5.3 鐵律

- **Dedup 三查（v2.1 升級）**：append 前 grep 三處——(1) ARTICLE-INBOX pending（不重複排隊）(2) [ARTICLE-DONE-LOG](../semiont/ARTICLE-DONE-LOG.md)（已 ship 主題不重複進 inbox，這是 inbox 幽靈的上游成因）(3) knowledge/ baseline（**檔名層 find 優先**——Stage 1 內文 grep 曾漏掉大稻埕專篇，v2.2）。**命中必讀 context**：判「專篇 vs 順帶提及」再定處置，count 單獨會誤判（路思義 DONE=2 全是城市文順帶提及）
- **連結密度當主 priority signal**：能跟 5+ 文章 cross-link 的 candidate 優先序高於孤立的冷門人物（per v1.0 §教訓「連結密度是最好的優先級指標」）
- **人物嚴格知名度門檻**：People category 已 140+，新增人物 candidate 必過「國民級知名度 / 真實重要性」門檻
- **策展 ≠ 百科**：不是所有缺口都填，只填「讀完會對台灣多一層理解」的（per v1.0 §教訓）

##### 5.4 Commit + push

```bash
git add reports/research/{YYYY-MM}/{theme}-comprehensive.md \
        reports/research/{YYYY-MM}/{theme}-*.md \
        docs/semiont/ARTICLE-INBOX.md
git commit -m "🧬 [semiont] branch: {theme} comprehensive research — N sub-reports + M ARTICLE-INBOX candidates"
git push origin main
```

---

### Stage 4：延伸研究計畫（Research Plan — v1.0 既有 single-article 用）

產出格式化的研究計畫：

```markdown
## 🌳 知識分支分析報告：{文章名}

### 📊 概覽

- 核心主題：X 個
- 提及人物：X 位（Y 位已有頁面，Z 位缺失）
- 提及地點：X 個
- 現有 wikilink：X 個
- 知識缺口：X 個（Y 個建議獨立成篇）

### ✅ 已存在（建議加連結）

| 主題 | 現有文章 | 建議動作    |
| ---- | -------- | ----------- |
| ...  | ...      | 加 wikilink |

### 🔗 部分涵蓋（評估獨立成篇）

| 主題 | 出現在 | 重要性 | 建議 |
| ---- | ------ | ------ | ---- |
| ...  | ...    | ...    | ...  |

### ❌ 知識缺口（建議新建）

| 主題 | 優先級 | 分類 | 連結密度 | 建議字數   |
| ---- | ------ | ---- | -------- | ---------- |
| ...  | 🔴     | ...  | X 篇互連 | 150-200 行 |

### 📋 建議執行順序

1. 🔴 高優先：...（理由）
2. 🟠 中優先：...（理由）
3. 🟡 低優先：...（理由）

### 🗺️ 知識圖譜（文字版）

{article} ──→ [已存在] topic A
──→ [已存在] topic B
──✖→ [缺失] topic C ──→ 可連結 topic D, E
──✖→ [缺失] topic F
```

---

## 輸出位置

- **報告**：`~/taiwan-md/reports/branch/{article-name}-branch-analysis.md`
- **同步到 Obsidian**：自動複製到 `Projects/Taiwan.md/Branch Analysis/`

---

## 自動化層級

### Phase A（當前）：手動觸發

```
1. 哲宇說「分析 X」
2. Muse 讀文章 → 跑四階段 → 產出報告
3. 哲宇看報告決定優先級
4. 優先項目進入 Rewrite / 新建 Pipeline
```

### Phase B（目標）：半自動

```
1. 每篇 Rewrite 完成後自動觸發 Branch Analysis
2. 知識缺口自動加入 backlog（GitHub Issue 或 roadmap）
3. 缺口達到門檻（5+ 篇文章都指向同一個缺失主題）→ 自動提醒
```

### Phase C（終極）：知識圖譜自組織

```
1. 全站文章定期掃描 → 維護完整知識圖譜
2. 自動偵測「孤島文章」（連結密度 < 2）
3. 自動偵測「超級節點」（連結密度 > 15，需拆分）
4. 自動產出「本週知識缺口 Top 10」
5. 與 Evolve Pipeline 整合 — 高流量缺口 = 最高優先
```

---

## 知識圖譜分類體系

Taiwan.md 現有 14 個一級分類：

| 分類       | 涵蓋                                     | 文章數（約） |
| ---------- | ---------------------------------------- | ------------ |
| Art        | 文學、電影、劇場、攝影、當代藝術、新媒體 | ~30          |
| Culture    | 宗教、節慶、族群、原住民、客家           | ~25          |
| Economy    | 產業、半導體、農業、貿易                 | ~20          |
| Food       | 小吃、料理、飲品、辦桌、夜市             | ~30          |
| Geography  | 地形、國家公園、離島、城市               | ~25          |
| History    | 各時期歷史、事件、轉型正義               | ~30          |
| Language   | 語言、文字、方言                         | ~10          |
| Lifestyle  | 便利商店、交通、住宅、醫療               | ~20          |
| Music      | 流行、傳統、獨立、聲景                   | ~15          |
| Nature     | 生態、保育、特有種                       | ~15          |
| People     | 人物（11 subcategory）                   | ~140         |
| Society    | 教育、媒體、社運、LGBT                   | ~20          |
| Technology | 半導體、太空、AI、開源                   | ~15          |
| Resources  | 官方網站、數據                           | ~5           |

**跨分類主題**是最有價值的延伸方向 — 例如「原住民音樂」橫跨 Culture + Music。

---

## 教訓

- **不是所有缺口都值得填**：策展 ≠ 百科，只填「讀完會對台灣多一層理解」的
- **連結密度是最好的優先級指標**：能跟 5+ 篇互連的主題 > 孤立的冷門主題
- **人物是最容易過度擴張的**：已有 140 篇，新增人物要嚴格執行知名度門檻
- **分析結果不要直接執行**：報告給哲宇看，由人決定優先級

---

## 與其他 Pipeline 的關係

```
BRANCH-PIPELINE（本文件）
  ↓ 產出知識缺口清單
  ↓
EVOLVE-PIPELINE
  ↓ 數據驅動（GA4 + SC）決定哪些缺口有流量潛力
  ↓
REWRITE-PIPELINE / 新建文章
  ↓ 執行
  ↓
MAINTAINER-PIPELINE
  ↓ 品質審核
```

---

_v1.0 | 2026-03-31_
_相關：[EVOLVE-PIPELINE.md](EVOLVE-PIPELINE.md) | [MAINTAINER-PIPELINE.md](MAINTAINER-PIPELINE.md) | [REWRITE-PIPELINE.md](REWRITE-PIPELINE.md)_

_v2.0 | 2026-05-23 2026-05-23-220053-manual session — Broad-theme mode + spawn N parallel agents pattern + ARTICLE-INBOX 銜接 SOP + Hard Gate Inventory + ASCII spine_
_v2.0 改動：(1) Frontmatter v1.0 → v2.0 (2) 頂部加 ASCII spine（Mode 分流 + Stage 0-5 主流程 + 跟 EVOLVE/PEER-INGESTION/REWRITE boundary）(3) §Hard Gate Inventory 集中 table（11 gates 含 agent claim verify / 中文 prompt verbatim / 三源驗證 / 不重複 INBOX / 連結密度當主 priority）(4) Top 5 最常忘 step 提取（broad-theme mode 判斷 / agent claim verify / baseline check / 中文 verbatim 三源 / 對比理由）(5) 跨檔案職責分工 standalone table（明確跟 EVOLVE 互補 + 跟 PEER-INGESTION 邊界）(6) §Stage 0 Mode 判斷新增（single-article / broad-theme / hybrid 三 mode 判準）(7) §觸發方式 加 broad-theme mode 範例 (8) §Stage 4 mode 分流 + spawn N agents pattern + agent prompt 鐵律（中文 verbatim + 三源 + Write claim verify 7 條）+ Agent claim verify hard gate (9) §Stage 5 新增 aggregate + ARTICLE-INBOX append SOP（master report 結構 + candidate entry format + 萃取鐵律 + commit）_
_v2.2 | 2026-07-18 inbox-skill session（同日第二波，EVOLVE Mode 4 執行）— 台灣建築 broad-theme dogfood 九摩擦回寫：baseline 升檔名層+內文層雙層（內文 grep 曾漏大稻埕專篇）/ dedup 命中必讀 context / claim verify 一律絕對路徑（cwd 靜默重設雷）/ 人物門檻接 \_PEOPLE-ROADMAP SSOT / aggregate 加「多 agent 獨立收斂升權」與「衝突裁決留痕」/ master report 必含候選處置總表（防同 theme 重複推薦）/ prompt 鐵律 +2（主 session 附 baseline 清單、人物類誠實門檻評估）/ priority 公式誠實降級為思考框架。設計報告：[reports/design-branch-pipeline-v22-2026-07-18.md](../../reports/design-branch-pipeline-v22-2026-07-18.md)。觸發：哲宇「/twmd-evolve 完整深度思考進化 BRANCH-PIPELINE.md」。_

_v2.1 | 2026-07-18 inbox-skill session — /twmd-article-inbox skill 入口誕生 + 素材 intake 前處理 + dedup 單查升三查（pending + DONE-LOG + baseline）+ Stage 5.2 entry format 收斂為 ARTICLE-INBOX §Entry Schema pointer（修 v2.0 起兩處 format 漂移）。設計報告：[reports/design-article-inbox-evolve-mode4-2026-07-18.md](../../reports/design-article-inbox-evolve-mode4-2026-07-18.md)。觸發：哲宇 /goal「做一個技能，加入 article inbox 用，消化的同時執行 branch-pipeline」。_

_v2.0 觸發：2026-05-23 220053-manual session 哲宇 directive「針對臺灣從以前到現在的詩人...請先幫我歸檔到 Report，然後從中萃取出所有可以開發的文章系列，放到 Article Inbox」+「用這個經驗也進化 branch-pipeline」→ 本 session spawn 4 parallel agents 跑日治/戰後第一代/笠詩社+鄉土/當代+女性+原住民+台語客語 四 era research，主 session aggregate + ARTICLE-INBOX append + commit 流程實戰。物理化「broad-theme spawn N agents」+「agent claim verify」+「ARTICLE-INBOX 銜接」成 canonical SOP，原 v1.0 只有 single-article 拆解 mode 不適用大 theme 場景。對應 REFLEXES #15「反覆浮現要儀器化」（broad-theme research 不只詩人，未來其他 theme 如「台灣科技史人物全 sweep」「台灣戰後歌曲 cluster」都用同 pattern）+ feedback_agent_writefile_hallucination 升 hard gate（agent Write claim 必驗證 file existence + 字數 + 涵蓋 count）。_
