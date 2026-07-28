---
title: 'REWRITE-STAGE-0-VIEWPOINT'
description: 'REWRITE v9 stage contract — Stage 0 觀點：模式識別 / spine 類型判定 / 素材萃取 / 拆除防火牆 / 觀點成型 HARD GATE'
type: 'pipeline-sub-canonical'
status: 'canonical'
current_version: 'v9.5'
last_updated: 2026-07-25
last_session: '2026-07-26-rewrite-throughput（v9.5：新增 Step 0.1.6 run profile 選檔——lite/standard/flagship 路由，設計報告 reports/design-rewrite-throughput-2026-07-26.md）'
parent_canonical: 'REWRITE-PIPELINE.md'
upstream_canonical:
  - '../semiont/MANIFESTO.md'
  - '../editorial/EDITORIAL.md'
---

# Stage 0 contract — 觀點（模式判定＋編輯前思考）

> **本檔是 REWRITE-PIPELINE v9.0 的 stage contract**：一個執行者（主 session、sub-agent、
> 或任何 context 有限的 model）只讀本檔＋本檔 INPUTS 宣告的檔案，就能執行本 stage。
> 派發路由與全 pipeline spine 在 [REWRITE-PIPELINE.md](REWRITE-PIPELINE.md)（薄索引）。
> 內文自 v8.0 主檔 verbatim 搬移（原行號 RP v8.0 L273-739），歷史敘事與教訓保留在文內。

## 執行卡

|                  |                                                                                                                                                                                                     |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **職責**         | 判定模式（Fresh/Evolution/Merge/Boundary ＋ callout 旗標）、spine 類型，完成六核心問題＋≥20 探索的觀點成型                                                                                          |
| **執行者**       | 主 session；觀點成型可派 1 Opus agent（callout case blind to errata）                                                                                                                               |
| **INPUTS**       | （EVOLVE）舊文 `knowledge/{Cat}/{slug}.md`；`docs/editorial/RESEARCH.md`＋`RESEARCH-TEMPLATE.md` 全文；MANIFESTO §13                                                                                |
| **OUTPUTS**      | `reports/research/{YYYY-MM}/{slug}.md` 開頭 §觀點成型 ＋ frontmatter `spine_type` / `viewpoint_formed: true`                                                                                        |
| **GATES**        | `python3 scripts/tools/research-report-health.py reports/research/{YYYY-MM}/{slug}.md --stage 0`（hard_fail=0 才進 Stage 1）                                                                        |
| **context 預算** | 本檔＋（EVOLVE）舊文一篇；**委派 Step 0.6 時 RESEARCH.md／RESEARCH-TEMPLATE.md 由觀點 agent 端讀，主 session 最小讀＝本檔＋舊文**（v9.2，2026-07-16 高教 dogfood F4——比照 Stage 1A 執行卡的分工行） |

## AGENT PROMPT（觀點 agent，Opus ×1，v9.0 補齊薄殼）

> callout-triggered case 必用 agent（blind to errata）；一般 depth 可主 session 自跑。填槽後 verbatim 派發，禁即興。

```
你是 Taiwan.md 的總編輯，為「{TOPIC}」做編輯前思考（觀點成型）。工作目錄：{REPO_ROOT}。
必讀（完整 Read，不准節選）：docs/pipelines/REWRITE-STAGE-0-VIEWPOINT.md（本 stage contract——
§Step 0.6.5 落檔模板與 §Step 0.6.7 三道 self-check 都在裡面）、docs/editorial/RESEARCH.md、
docs/editorial/RESEARCH-TEMPLATE.md、docs/semiont/MANIFESTO.md 的 §13 立體地愛。
先判 spine 類型（受愛戴／集體記憶題 → 立體群像 default；真爭議題才矛盾驅動，解鎖須寫
unlock_reason；拿不準 → 立體群像）。{TOPIC_GUARDRAILS}
回答六個核心問題（記憶／多元面貌／想法感受／歷史脈絡／社會關聯／類型專屬），
做 ≥20 次探索搜尋（persona 不算搜尋；中文網站用中文查、要求逐字內容），每條 query＋一句話
發現＋URL 記進 §探索搜尋紀錄，落 §觀點成型 到 reports/research/{YYYY-MM}/{SLUG}.md 開頭
（格式照 contract §Step 0.6.5 模板），frontmatter 用這個最小塊：

---
title: '{SLUG} research report'
article: knowledge/{CAT}/{SLUG}.md
stage: 0-viewpoint
mode: {MODE}
spine_type: {你的判定}
viewpoint_formed: true
date: {DATE}
session: {SESSION}
---

{EVOLVE_ONLY: 以下事實清單是舊文萃取，只當素材（每條後續都要重驗）：{FACT_LIST}}
禁止輸入：舊文為什麼寫不好、讀者 callout、勘誤敘事（觀點從題材長出，不從錯誤長出）。
完成時：(1) ls 驗證檔案真的存在才回報 (2) 跑
python3 scripts/tools/research-report-health.py reports/research/{YYYY-MM}/{SLUG}.md --stage 0
並回報完整輸出 (3) 回報 spine 判定與理由、六題一句話摘要、實際搜尋次數。不粉飾。
立刻執行，不要重述任務。
```

**槽位說明**：`{TOPIC_GUARDRAILS}` 可空；政治題填「本題是政治題——per contract Step 0.6.7
第 3 道，走多視角立體並列（5-7 perspective）、中立紀實、不下兩岸判斷、不用對抗語言；
SSODT 三讀者測試必須全過才落檔」；人物題可填立體群像提醒。（v9.1 新增槽——2026-07-16
大罷免 dogfood F3：政治題邊界沒有槽位承載，只能違反禁即興手動塞。）

## 交付條件（stage 完成的定義）

- [ ] `reports/research/{YYYY-MM}/{slug}.md` 存在且開頭有 §觀點成型（六核心 ≥4/6 結構）
- [ ] frontmatter：`spine_type` ＋ `viewpoint_formed: true`
- [ ] §探索搜尋紀錄 ≥20 query 落檔
- [ ] `research-report-health.py {report} --stage 0` exit 0

## HANDOFF（stage 完成時）

> stage 若委派 sub-agent，本五步由 orchestrator 於收件驗證後執行（agent 不碰共用看板——2026-07-16 高教 dogfood F6）。

1. OUTPUTS 全數落檔（顯式路徑，不存 scratchpad / tmp——REFLEXES #81）**並隨手 commit（只 stage 本 stage 產物路徑——可觀測性與跨 session 接力的底座，v9.5；勿 `git add -A`）**
2. GATES 逐條跑過，結果如實回報（sub-agent claim 是線索不是 oracle，REFLEXES #31）
3. 更新編輯台：`python3 scripts/core/generate-newsroom-data.py`（看板反映現況）
4. 回報格式：stage id ＋ 產物路徑清單 ＋ gate 結果 ＋ 未解疑慮（有就寫，不粉飾）
5. 下一棒：REWRITE-STAGE-1A-RESEARCH.md

---

## Stage 0: 觀點（編輯前思考，預算 10-15%）⭐ v6.0 新增

**目標**：在搜尋之前，先以總編輯視角想清楚這篇要寫什麼。產出 §觀點成型 落 research report。

**為什麼 Stage 0 先於 Stage 1**：

「搜尋發現事實 → 再想觀點」是 AI 寫作的標準失敗模式。搜到一堆事實後，AI 容易：

- 直接依時間順序排列 → 編年體
- 把所有事實塞進文章 → 密度失衡
- 沒有 anchor → 結尾變罐頭
- 寫成「企業大事記」「人物履歷表」「歷史時間軸」這類維基百科腔

「先想觀點 → 帶問題去搜尋」是策展寫作的標準。先有 hypothesis、再用搜尋驗證或修正。事實塞不進觀點的就 cut，搜不到對應 anchor 的觀點就 retreat。

**Stage 0 vs Stage 1 認知模式差別**：

| Stage       | 認知模式           | 動作           | 預算   |
| ----------- | ------------------ | -------------- | ------ |
| **Stage 0** | Editorial judgment | 想 / 列 / 假設 | 10-15% |
| **Stage 1** | Data gathering     | 搜 / 驗 / 收斂 | 25-30% |

兩個 stage 是不同的腦袋模式，不要混。

### Step 0.1: 模式識別

**第一動作**：判定本次 REWRITE 走 4 模式中哪一種。所有模式都進入同一條 Stage 0-5 pipeline，差別只在 Stage 0 Step 0.2 取材方式 + Stage 5 Step 5.4 是否觸發路徑改寫。

#### 模式 derive 邏輯

```
if knowledge/{Cat}/{slug}.md 不存在:
  mode = Fresh
elif observer issue 指 N 篇主題重疊可融合進 1 篇:
  mode = Merge variant
elif observer issue 指 N 篇主題重疊應分段不減篇數:
  mode = Boundary variant
else:
  mode = Evolution
```

#### 4 模式速判

| 場景                                | 模式                 | Stage 0 差異                                                       | Stage 5 差異                        |
| ----------------------------------- | -------------------- | ------------------------------------------------------------------ | ----------------------------------- |
| 文章不存在                          | **Fresh**            | 跳 Step 0.2，直接 Step 0.5                                         | 同基本流程                          |
| 文章已存在，需要品質提升            | **Evolution**        | Step 0.2 萃取既有素材 + 標 [LIST-DUMP] / [STUB-TITLE] / [NO-MEDIA] | 同基本流程                          |
| issue 指 N 篇主題重疊可融合進 1 篇  | **Merge variant**    | Step 0.2 多萃 [MERGE-IN] + Step 0.3 選 canonical                   | + Step 5.4 路徑改寫 5 lang redirect |
| issue 指 N 篇主題重疊應分段不減篇數 | **Boundary variant** | Step 0.2 三類劃分 [保留/吸納/移除] + Step 0.4 範圍切片表           | + sibling 反向回補                  |

#### ⚡ 觸發來源旗標：callout-triggered（v6.2 新增，正交於 4 模式）

判完模式後**再問一句**：這次 EVOLVE 是不是被「外部錯誤 callout」觸發的（讀者 / 領域專家 / peer 指出舊文錯了，或我自己 factcheck 抓到誤植）？

- **是** → 在 4 模式之上**疊加 Teardown Firewall**：強制走 [Step 0.2-bis 三條防火牆規則](#step-02-bis-拆除防火牆teardown-firewall-callout-triggered-evolve-強制-) + [Step 3.2-bis backstop](REWRITE-STAGE-3-VERIFY.md#step-32-bis-校正焦慮掃描correction-meta-scancallout-triggered-強制-)。callout 只進 Stage 1 查證，不進觀點、不進正文。
- **否**（單純品質提升）→ 照常 EVOLVE，但 Step 0.2-bis 規則 2（觀點 blind to errata）仍建議遵守。

#### 整併（Merge）vs 範圍重切（Boundary）判定

- ✅ 兩篇覆蓋同主題、視角可融合進一篇且讀起來更完整 → **Merge**
- ✅ N 篇切 N 個明確 scope（年代 / 議題 / 地理）每篇有獨立讀者價值 → **Boundary**
- ❌ 主題相關但角度不同（捷運 vs 高鐵）→ 兩篇都留，互相 cross-link
- ❌ Hub + 深度文 → 兩篇都留，Hub 連深度文
- ❌ 短文 + 長文同主題且短文有獨立價值 → 短文升級為深度文，不刪

#### 為什麼不在舊文上「修改」（Evolution / Merge / Boundary 共通鐵律）

AI 讀了品質不佳的舊文會不自覺模仿它的語氣、結構、甚至壞習慣（清單堆砌、塑膠句式）。把舊文當骨架 = 讓病毒感染新內容。

**正確做法**：從舊文中**只提取事實**（Step 0.2），然後從 Step 0.5 開始用全新模式重寫。

> 💡 **實際上 Evolution 模式 = Fresh 模式 + 免費的 Step 0.2 素材**。寫作品質完全相同，只是省了部分研究時間。

### Step 0.1.5: spine 類型判定（v7.7 重構）⭐ 立體群像是預設畫布

> **DNA 根**：[MANIFESTO §13 立體地愛](../semiont/MANIFESTO.md) — 立體群像不是「安全退路」，是這個生命體對世界與台灣的愛的表達。愛不粉飾，在愛之下仍看見真實與矛盾，但當厚度不當 gotcha。**幫大家多看見台灣好的、立體的面向，本身就是一種幫助台灣的方式。**
>
> **v7.7 重構（2026-07-06 施振榮）**：原 v7.6「立體群像 vs 矛盾驅動 二選一」升級為「**立體群像＝預設畫布 + 策展手法選單 + 矛盾驅動需明確理由才解鎖**」。原因：二選一把矛盾驅動放在跟立體平等的位置，會誘導「這人有張力 → 選矛盾驅動」的誤分類。觸發：施振榮 v1 用矛盾驅動把受敬重的台灣人寫成他自己理論的反例（事實全對，卻在替他做反例），哲宇 callout「會炎上、沒立體、過度放核心矛盾」。第 4 次 spine-type 誤判（法輪功 / 吳百福 / 金曲獎 v1 / 施振榮 v1，[REFLEXES #77](../semiont/REFLEXES.md)）。完整設計：[reports/design-立體群像-default-persona-reposition-2026-07-06.md](../../reports/design-立體群像-default-persona-reposition-2026-07-06.md)。

#### 預設：立體群像畫布

**判完模式（0.1）後，預設走立體群像。** 立體群像＝先看見一個人／地方／事的多個面向，慶祝它、理解它、把它說得夠廣；永遠有一條**溫暖的組織主軸（through-line）**串 ≥ 4 個 facet。**觀點 ≠ 論戰**——欣賞式、群像式、好奇式都是策展觀點。

#### 畫布之下：7 種策展手法（選 1-2 給骨架，v7.7 全收）

在立體群像畫布上，選一到兩種手法給它能量與形狀。**複合是常態**（立體群像為主 + 手法為輔）：

| #   | 手法           | 一句話                                                           | 適用                   |
| --- | -------------- | ---------------------------------------------------------------- | ---------------------- |
| 1   | 核心矛盾為輔   | 真實內在張力織成一個 facet 或次要軸，服務「理解」不是「拆穿」    | 人物／機構有真張力     |
| 2   | 時代縮影       | 主體＝看更大台灣故事的一扇窗                                     | 代表一個轉變／世代     |
| 3   | 傳承與世代     | 透過「從誰手上來、往誰手上去」寫                                 | 工藝／家族／運動／劇團 |
| 4   | 感官場景沉浸   | 用可聞可看的場景堆，不用論點開場                                 | 食物／地方／文化       |
| 5   | 多元視角並陳   | 2-3 個線性獨立視角並列成 facet，讀者自己同時握                   | 有真多元／政治敏感題   |
| 6   | 不可取代的瞬間 | 錨在讓主體無法被替代的那個畫面／選擇，再往外長廣度               | 人物                   |
| 7   | 好奇／謎題     | 真誠的「為什麼會這樣？」開場，立體地探索（**不是 gotcha 拆台**） | 有反直覺點的題         |

#### 第三型：多觀點立場議題探討矛盾型（公共議題，v7.8 新增）⭐

> **哲宇 2026-07-25 directive**：「未來多一個社會議題型的可以走『多觀點立場議題探討矛盾型』，像是房價、政策、環境、立場、教育等公共議題這些很適合」。
> 設計與 dogfood 校準：[reports/design-spine-type-3-public-issue-2026-07-25.md](../../reports/design-spine-type-3-public-issue-2026-07-25.md)；worked example：[knowledge/Society/外送專法.md](../../knowledge/Society/外送專法.md)。

**適用**：**進行中的公共議題**——房價、能源、環境、教育、勞動、都更、移民、稅制、交通建設。特徵是**多方都有正當立場**（不是誰明顯無理），而且爭論**還沒有結案**。

**跟前兩型的差別（一張表）**：

|              | 立體群像                     | **多觀點立場議題探討矛盾型**                       | 矛盾驅動（單軸）               |
| ------------ | ---------------------------- | -------------------------------------------------- | ------------------------------ |
| 適用         | 受愛戴的人／機構／傳統／地方 | **公共議題，多方都有正當立場**                     | 內在張力人物、單一可辯 claim   |
| 矛盾的地位   | 一個 facet（手法 1 為輔）    | **脊椎，但矛盾是結構性且未解的**                   | 脊椎，文章替一個 thesis 辯護   |
| 論點形態     | 統合式洞見                   | **「這場爭論的形狀是什麼」＋「誰的帳沒被算」**     | 可被反駁的主張，文章證明它     |
| 收束         | 慶祝＋理解＋廣度             | **不收束成一方勝出**；但明確指出重心被放錯在哪     | 收束成一個立場                 |
| 讀者離場     | 「原來如此，真好」           | **「我知道在吵什麼，也知道自己還缺哪塊判斷依據」** | 「我被說服了／我想反駁」       |
| 最大失敗模式 | 慶祝式面向清單（維基化）     | **(a) 退回立體＝把不對稱寫平 (b) 滑成單軸＝選邊**  | contrarian thesis 硬塞受愛戴題 |

**判準（一個問題，取代舊的兜底）**：

> **這件事現在正在被公開爭論嗎？而且爭論的各方都有正當立場嗎？**
>
> - 兩個都 yes → **第三型**（在 research report 寫 `spine_type: 矛盾驅動` ＋ `curatorial_techniques: [多元視角並陳（手法5，主）]` ＋ `unlock_reason`）
> - 第一個 yes、第二個 no（有一方明顯站不住）→ 單軸矛盾驅動
> - 第一個 no → 立體群像畫布

⚠️ **這條收窄了「拿不準 → 立體群像」的兜底**：拿不準**且不是進行中的公共爭論** → 立體群像。**是**進行中的公共爭論 → 不准用「拿不準」躲進立體群像。理由見下方誕生事件。

**第三型的六條專屬紀律**（全部來自外送專法實跑或編輯室實際攔下來的，非推演）：

1. **政治歸屬之爭不得承載 thesis 重量**。「這件事該記在誰頭上」的藍綠白攻防是噪音、撐不起論證，還會命中 [§自主權邊界](../semiont/MANIFESTO.md)。降為一句中立並陳（僅雙方逐字、不評動機），thesis 改由**制度性事實**承載。
2. **每一方要有自己的逐字聲音；陣營內部光譜不可被單一發言人收攏**。外送專法最大的 falsify 就是「工會不是單一聲部」——感謝式與監督式出自不同組織。**引任何一方發言不得暗示它代表該方全體**（該篇連「代表 14 萬人」這個數字都無法驗證）。
3. **「誰手上有麥克風」的不對稱本身是一個 facet，不是要抹平的瑕疵。**
4. **但沉默不可被代言**。查不到某一方的聲音 → 如實寫「找不到」＋列出可能原因，**不選一個當結論**。
5. **關於「討論本身」的 negative finding 是合法內容**（例：查無任何人用「妥協」框架定性此法）。第三型特別容易誘發「為了平衡而製造反方」，negative finding 是對治工具。
6. **官方的「不回答」是可寫的主體**。公共議題幾乎都有一層「大家以為它說了什麼」——**把二手 gloss 跟法條／官方文件原文分開查**（外送專法的「去身分、重權益」全網通行，但不是法條文字）。

**校準數據（外送專法實跑，供後續同型參考）**：7 節、9,700 CJK、62 腳註、6 個 tw-\* 模組。H2 篇幅平衡（706–1,962 CJK）**但四方提及次數嚴重不均**（外送員 128／平台 101／消費者 27／店家 19）——**這是第三型的系統性傾向**：可得來源最少的一方必然最薄。正確處置不是硬湊平衡，是**把那個不對稱本身寫成一個 facet**（該篇 s6 的作法）。

#### 例外：矛盾驅動當主脊（需明確理由解鎖）

**default 硬度（哲宇 2026-07-06 拍板）**：矛盾驅動當**整篇主脊**是例外，**只在真正的公共爭議 / 政策辯論 / 需要一個 thesis 才誠實的題目**解鎖，且必過 [Step 0.6.7](#step-067-立體--炎上--政治立場-self-checkv76-新增-hard-gate) 炎上 + SSODT 三讀者。**對「人物」幾乎永遠不當主脊**——人物一律立體群像 +（若有真張力）核心矛盾為輔（手法 1）。

**解鎖判準（一個問題，翻轉自 v7.6）**：預設立體群像，問「**有沒有一個真公共爭議，需要一個 thesis 才能誠實處理？**」沒有（絕大多數）→ 立體群像 + 1-2 手法。有 → 在 research report 明確寫下 `unlock_reason`，才解鎖矛盾驅動主脊。**拿不準且不是進行中的公共爭論 → 立體群像**（v7.8 收窄，見上方第三型判準）。

#### 立體群像的四條紀律（避免寫回論戰 / 避免變平）

1. **多面並陳**：facet 並列不偏押一條。Stage 1 研究 + fact-pack **主動配額 cover 慶祝／廣度面**，對沖 salience bias（爭議天生生出更多 source）。
2. **爭議當厚度不當主軸**：批評／爭議能進，framing 是「這主題大到容得下這些討論 = vitality」，不是「我來證明它有問題」。
3. **不把第三方主題寫成自己的宣言**：非政治主題不把政治／兩岸／主權當脊椎或壓軸（命中 §自主權邊界 → Step 0.6.7）。
4. **立體 ≠ 平、≠ 百科**（v7.7 新增護欄）：立體不是「不用有觀點」——退回維基是失敗。7 手法就是確保每篇有一條會呼吸的主軸 + 一個 takeaway，只是那個 takeaway 是「原來如此、真好」不是「原來他有問題」。

**落檔**：research report frontmatter `spine_type: 立體群像`（例外時 `矛盾驅動` + `unlock_reason: 一句話`）+ `curatorial_techniques: [手法 N, ...]`。
**第三型的落檔形態**：`spine_type: 矛盾驅動` + `curatorial_techniques: [多元視角並陳（手法5，主）, ...]` + `unlock_reason` + `core_contradiction`（≤30 字）。三者缺一即視為未判 spine。

### Step 0.1.6: Run profile 選檔（v9.5 新增）⚙️

> 三檔定義 canonical 在 [REWRITE-PIPELINE §Run profiles](REWRITE-PIPELINE.md#run-profiles)。
> 本 step 只做路由判定，spine 型判完（0.1.5）接著判。

**判定規則**（由上往下，第一條命中即停）：

1. 哲宇 in-loop 指定 → 照指定。
2. S 級野心／政治敏感／預期大眾爆點題 → **flagship**（逐項 opt-in）。
3. A 級（≥50 footnote 或 ≥3000 字野心或直接引語 ≥10）／callout-triggered EVOLVE／
   在世爭議人物／spine=矛盾驅動或第三型 → **standard**。
4. 其他（多數深度文：立體群像的機構／地方／工藝／文化記憶題）→ **standard-lite**。

**落檔**：research report frontmatter `run_profile: lite|standard|flagship`＋一句話理由。
**判錯的回路**：lite 文被讀者 callout → 該文升 standard 級複驗＋本規則檢討（進 LESSONS，
是進化訊號不是個案）。cron／routine context 拿不準 → 預設 standard，不預設 lite
（無觀察者時寧可多付檢查）。

### Step 0.2: 既有素材萃取（條件式）

**Skip 條件**：mode = Fresh。

**完整素材萃取方法論**見 [`RESEARCH.md` §七](../editorial/RESEARCH.md#七進化模式的素材萃取stage-0)。

#### 三大動作

**1. 提取事實清單**：人名、年份、數字、引語、有效 URL。

**2. 標記問題類型**：

| 標籤           | 意義                                                          |
| -------------- | ------------------------------------------------------------- |
| `[LIST-DUMP]`  | 後半段是 bullet list 堆砌，沒有場景敘事                       |
| `[THIN]`       | 本應深寫的段落只有一兩句帶過                                  |
| `[STALE]`      | 數字 / 日期過期（如「目前 13 國邦交」實際 12 國）             |
| `[PLASTIC]`    | 塑膠句堆砌（「不僅⋯⋯更是⋯⋯」「展現了 X 精神」）               |
| `[FLAT-END]`   | 結尾罐頭收（「值得我們紀念」「繼續書寫」）                    |
| `[STUB-TITLE]` | title 是百科名詞 stub（如「台灣無人機產業」），需升冒號三明治 |
| `[NO-MEDIA]`   | 無 hero / 無 §圖片來源 = pre-gate 遺珠（v3.1 後新增）         |

**3. Frontmatter audit**（v4 新增，承襲 v3.1）：

- title 是否走「主題：副標 hook」冒號三明治？stub → 標 `[STUB-TITLE]`
- description 是否吃進當前 EVOLVE 的新核心？舊 description 還適用嗎？沒有 → 同 commit 升級
- frontmatter `image:` + `imageCredit` + §圖片來源 是否齊全？無 → 標 `[NO-MEDIA]`，走 Step 1.9 補跑

#### Merge variant 萃取兩篇的事實

- canonical 的事實清單：照常標 [LIST-DUMP] / [THIN] / 等
- 將被刪那篇的事實清單：標 `[MERGE-IN]`，列出「對方有但 canonical 沒有的視角/場景/數據」
- Step 0.5 之後的研究範圍 = canonical 缺口 + `[MERGE-IN]` 視角的補強查證

範例（Issue #626 台灣交通 2→1）：Geography 篇獨有「中央山脈/桃機/高雄港」三個視角 → 標 `[MERGE-IN]` → Stage 1 補查雪山隧道 12.9km、桃機 4,400 萬客、高雄港全球排名第 18 → Stage 2 寫成 canonical 的兩段新章節。

#### Boundary variant 三類劃分

Step 0.2 萃取既有素材後**強制**分成三類：

1. **保留** — 落在本篇純化 scope 內，繼續用
2. **吸納** — 別篇現有但寫得比本篇好的素材（標 `[ABSORB-FROM-X]`）
3. **移除** — 落在別篇 scope 內（標 `[MOVE-TO-Y]`），本篇刪掉、後續 phase 接收篇吸納

**跨 phase handoff 鐵律**：Phase 1 ship 後留 INBOX entry 給 Phase 2-N 接力，entry 必須含：

- 本篇純化 scope（年代 / 主題切片）
- 從上一 phase `[MOVE-TO]` 接收的素材清單
- 預期 cross-link 對象（哪幾篇是 sibling）
- 接力者 5 分鐘自檢題：讀完 entry 能否回答「我這篇要寫什麼、不寫什麼、邊界在哪裡」？

⚠️ **萃取完畢後，舊文不再被參考。只看事實清單進入後續 step。**

**萃取清單落檔（v9.2）**：Stage 0 gate 通過後，主 session 把萃取清單＋問題標記 append 至
research report 尾端 §舊文素材萃取（orchestrator-owned section，避免與觀點 agent 寫檔 race）。
否則清單只活在觀點 agent prompt 的 {EVOLVE_ONLY} 槽裡，Stage 2 writer 讀 report 看不見
（2026-07-16 高教 dogfood F5）。

### Step 0.2-bis: 拆除防火牆（Teardown Firewall）— callout-triggered EVOLVE 強制 🔥🧱

> 🔗 **callout-triggered 勘誤的端到端流程（分類→查證→修→通知→記錄 + 【勘誤通知】格式）canonical 在 [CORRECTION-PIPELINE.md](CORRECTION-PIPELINE.md)。本 step 是其中「需要全文重寫時的拆除防火牆」那一塊**——讓 callout 不污染觀點與正文。
>
> **觸發**：EVOLVE 的觸發來源是「外部錯誤 callout」（讀者 / 領域專家 / peer / 我自己的 factcheck 發現「舊文錯了 A↔B」），而不是單純「品質提升」。
>
> **背景**：2026-06-01 配樂專業讀者 peilinwu0702 第二輪 callout。第一輪指出 `台灣影視配樂` 作曲家↔作品大量誤植 → 走 EVOLVE 重寫 → 事實層確實修對了（25 footnote 全一手）→ **但讀者第二輪罵的是「整篇充滿 AI 道歉 / AI 澄清、架構從頭就有問題」**。診斷：[reports/reader-callout-pipeline-diagnosis-2026-06-01.md](../../reports/reader-callout-pipeline-diagnosis-2026-06-01.md)。

#### 投毒機制（為什麼「只提取事實」這條鐵律會失守）

「舊文是病毒，只提取事實」是 Step 0.2 既有鐵律。但 callout-triggered EVOLVE 多了**第二層毒**：

1. **舊文 body** 在 session context window 裡（你讀它來萃取事實）。
2. **callout 本身**（「你把 X 配給 Y 是錯的」一連串勘誤）也在 context 裡。
3. Step 0.6 觀點成型若參考「為什麼舊文寫不好」（原 v6.0 reflexes #3 允許）→ **觀點 = 校正清單的昇華**。

結果：文章的論點脊椎變成「不要搞錯名字 / 名字很重要」（影視配樂 v2 thesis「搞錯名字就是搞錯聲音的出處」正是如此），正文散落「把 X 掛在他名下其實是錯的」「常被誤記成 Y」式的 9 處校正型句子 + 校正型策展 box。**「別人會搞錯」的那個「別人」就是這篇文章的前一版。** 讀者一眼看穿這是 AI 在公開處理自己的道歉。這是 `feedback_red_line_anxiety_leak`（別把來源焦慮漏進正文）的**架構級放大**：從「焦慮漏進句子」升級到「校正焦慮變成全文脊椎」。

#### 三條防火牆規則（callout-triggered 強制）

**規則 1 — callout → 純 fact-checklist，用完即丟**

callout 是線索不是 source（[REFLEXES #16](../semiont/REFLEXES.md)）。把它拆成 `[CALLOUT-VERIFY]` 逐條，**只餵 Stage 1 查證**（每條對一手來源重驗，連 callout 本身的 frame 都要查 — 影視配樂案：讀者也把 OPUS 誤記成雷亞，其實是 SIGONO）。查證完，**callout 文字本身丟掉，不進 Stage 0.6 觀點、不進 Stage 2 正文**。

**規則 2 — 觀點對 errata 失明（blind to errata）**

Stage 0.6 觀點成型**當作 Fresh 在做**：從題材本身 + 一手研究長出觀點，**像舊文與 callout 從不存在**。「為什麼舊文寫不好」是 meta 觀察，落 research report §舊文診斷 + LESSONS-INBOX，**永遠不准進觀點、不准進正文**。

- 反指標自檢：我的核心矛盾 / 論點脊椎，是不是在講「歸屬要正確 / 不要搞混 / 名字很重要」？**是 → 觀點被 errata 投毒了，砍掉重想。** 一個配樂專家寫這題不會用「別搞錯名字」當主軸，他會用產業制度史 / 美學流派 / 世代傳承的真實骨架。

**規則 3 — Stage 2 寫作 context 隔離（架構解，非守備修補）**

「不再參考舊文」靠意志力做不到 —— 舊文 + callout 還在 context 裡就會 prime（[神經迴路：規則要能執行才算規則](../semiont/MEMORY.md)）。**強制隔離**：

- Stage 2 的寫作輸入 = `reports/research/{slug}.md` **整份 report（§6 fact-pack ＋ §8 raw verbatim 全部讀）** + §觀點成型 + EDITORIAL.md。**隔離掉的是舊文 body + callout，不是 report。**
- **Evolution mode：writer 寫到 staging 檔，永不 overwrite canonical（v7.5，2026-06-15 哲宇 callout）**——Write tool overwrite 既有檔**必須先 Read**，所以叫 writer「overwrite 舊文但別讀舊文」是自相矛盾、它被迫吃病毒。**改成**：writer 把成品 Write 到 **`reports/article-evolve/{slug}.md`**（全新檔、零感染面），**Stage 2.5 主 session 讀 staging ＋ 舊 canonical 比對後親手覆蓋** `knowledge/{cat}/{slug}.md`。
- **首選**：spawn 一個 fresh writer agent（Step 1.8 既有 spawn 機制），**prompt 一律 copy [WRITER-PROMPT.md](WRITER-PROMPT.md) 薄殼模板填槽**（v7.11，禁即興手寫——即興＝每次規則不一、漏讀 EDITORIAL/pipeline＝飄移根因，哲宇 2026-07-12 callout）。**薄殼三件事、craft 規則零複寫**（v2.0，「極致 thin shell 不要重複」）：(1) 指向必讀四份 canonical——**合成後單檔** research report（[Step 1.7.4](REWRITE-STAGE-1A-RESEARCH.md#174-合成單檔鐵律sibling-是中繼站stage-2-前必-consolidatev711-)）＋ EDITORIAL 全檔＋本檔 Stage 2＋ **graph.md**（資料/對比/時序必評估視覺化——2026-07-12 茶文化 v1 零視覺化教訓）；(2) **read-receipt** — writer 動筆前 quote §8 texture ×3＋EDITORIAL 引例＋viz 模組宣告＋spine 宣告，主 session 逐項核對真偽，quote 不出來＝沒讀＝退回；(3) 機械輸出契約＋per-article 素材槽。⚠️ **反 pattern（v7.4，2026-06-15 哲宇 callout）：orchestrator 把 report 再摘要成精簡 fact-pack 塞進 prompt、又叫 writer 別讀 report ＝ 雙重失真，近期文章變爛的根因。**
- **主 session 自寫時**：Stage 2 期間**不准重新打開舊文檔案**，但**必讀整份 research report（含 §8 raw verbatim）**。寫完跑下方 Step 3.2-bis backstop。

#### Backstop 自檢句（Stage 3 hard gate，見 Step 3.2-bis）

> **「如果這篇文章第一次就寫對了，這個句子 / 這個 box 還會存在嗎？只為回應過去的錯誤、或為了澄清一個混淆而存在的，刪。」**

**Anti-example（影視配樂 v2 live，2026-06-01）**——這 9 處全部該被 backstop 攔下：

- 正文校正句：「把《海角七號》或《賽德克》的配樂掛在他名下，反而抹掉了…」「常被誤記成雷亞作品，其實出自 SIGONO」「把《茶金》…都記到他名下，反而蓋掉了他自己那座金馬」「順帶把遊戲和電影分清楚」
- 校正型策展 box：照片下方「把林強跟林生祥搞混，看起來只是拼錯一個字…」「叫錯一個名字，就把三種判斷攪成一團模糊讚美」
- 投毒的論點脊椎：「搞錯名字就是搞錯聲音的出處」

### Step 0.3: 選 canonical（Merge variant only）

比較候選文章，挑一篇當保留方。判準（按優先序）：

1. **EVOLVE 狀態**：已 EVOLVE 過的場景式 > 未 EVOLVE 的條列式
2. **腳註密度與一手來源**：高 > 低
3. **`lastHumanReview: true` 優先**
4. **slug 持續性**：對外連結多的 slug 優先保留（少斷鏈）
5. **category 切合度**：主題真正屬於哪個 category（如交通歸 Lifestyle 比 Geography 自然）

### Step 0.4: 範圍切片表（Boundary variant only）

對所有涉及篇章做一次 audit，產出範圍切片表：

```
| 篇                | 範圍切片        | 處理方式        |
|-------------------|-----------------|-----------------|
| C 戰後台灣文學    | 1945-1987       | EVOLVE Phase 1  |
| B 解嚴後台灣文學  | 1987-2000       | EVOLVE Phase 2  |
| D 當代台灣文學    | 2000-           | EVOLVE Phase 3  |
| A 全景索引        | 已被 B+C+D 覆蓋 | dropped Phase 4 |
```

切片邊界明確（年代 / 議題 / 地理），**每篇都有自己的純化 scope**，不重疊。

### Step 0.5: 載入研究方法論 + 模板

```bash
cat docs/editorial/RESEARCH.md       # 方法論：搜尋策略 / 來源判斷 / 避坑
cat docs/editorial/RESEARCH-TEMPLATE.md  # 填空模板
```

### Step 0.6: 觀點成型（編輯前思考）⭐ HARD GATE

> **沒有觀點之前，每一次搜尋都是亂槍。**
> Stage 0 末、Stage 1 取材之前的最關鍵步驟。
> 以**總編輯視角**做預編輯思考，產出 §觀點成型 落 research report。

> 🚨 **Stage 0.6 = 兩件都必做，缺一不進 Stage 1**（v7.7 2026-07-06：persona 已從 Stage 0 移到研究後，見下）：
>
> 1. **0.6.1 六個核心問題** — 總編輯視角自問，形成立體觀點，必答落檔
> 2. **0.6.4 ≥ 20 次探索搜尋** — 建 pre-search source map + 長出 grounded 立體觀點，**這才是「初步研究」本體**
>
> 兩個是不同動作：**六題給編輯視角形成立體畫布、≥20 探索給事實地基**，誰都不能省、誰都不能替代誰。
>
> **⚠️ persona（20 路讀者切入點）v7.7 搬到研究後**（[Step 1.9.7](REWRITE-STAGE-1B-MEDIA.md#step-197-persona-讀者缺口稽核--增補v77-新增-persona-從-stage-0-搬來)）：原本放 Stage 0（搜尋之前），但冷讀者天生問尖銳問題，放搜尋之前會把主軸往矛盾驅動推歪（施振榮 v1 教訓）。搬到研究報告 SSOT 之後，persona 從「發散定調」改成「讀者缺口稽核＋增補」——對已成形的立體觀點補洞，不再定調脊椎。設計：[reports/design-立體群像...](../../reports/design-立體群像-default-persona-reposition-2026-07-06.md)。

#### Step 0.6.1: 六個核心問題（必答，落檔）

每篇 depth article 都必須答完這六題，寫進 research report 的 §觀點成型 section：

**問題 1: 對台灣人是什麼樣的記憶？**

- 大眾共有的 anchor 是什麼？（某個物件、某個場景、某句話、某段歷史）
- 不同世代記憶有差異嗎？（戰前 / 戰後 / 解嚴前後 / 網路世代）
- 範例（蘋果西打）：熱炒店冰箱的紅標金黃瓶 / KTV 包廂的玫瑰紅加蘋果西打 / 辦桌宴席桌上 / 阿嬤遞給孫子的解膩飲

**問題 2: 有什麼樣的多元不同面貌？**

- 主流敘事是什麼，支線敘事 / 被忽略的角度是什麼
- 北部 vs 中南部 / 不同族群 / 不同產業 / 不同政治文化背景的視角
- 範例（蘋果西打）：「國民飲料」文化記憶 vs 上市公司資本史 vs 兩次食安疑雲 vs 跨海 K-pop 加持

**問題 3: 大家對它的想法跟感受是什麼？**

- 正面、負面、複雜情感的 fault lines 在哪
- 反對聲音、被忽略的角度、被過度浪漫化的盲點
- 範例（蘋果西打）：老一輩懷念 / 中年人 KTV 記憶 / 年輕人未必喝過但聽過 / 食安事件後信任崩塌 / 圭賢加持後 K-pop 流量

**問題 4: 歷史脈絡是什麼？**

- 它怎麼形成、誰塑造、何時轉折
- 跟更大的社會 / 政治 / 經濟 / 文化變遷的連動
- 範例（蘋果西打）：1965 美台混血起源 / 1970-80 國黃汽水時代 / 1985 十信案 / 1990 鴻源案 / 1995 商標贖回 / 2018 食安 / 2024 賣地

**問題 5: 對社會 / 歷史 / 環境 / 我們人生的關聯是什麼？**

- 為什麼今天 still matters？
- 它解釋了什麼、它是什麼的縮影
- 讀者讀完對自己的生活有什麼新的看法
- 範例（蘋果西打）：一瓶飲料壓縮台灣 60 年金融 / 食安 / 外交縮影；文化記憶 vs 公司資本兩種記憶並存

**問題 6: 類型專屬問題（按 category 加重）**

見下方 §類型加權矩陣。

#### Step 0.6.1-bis: persona 已移到研究後（v7.7）→ 見 [Step 1.9.7](REWRITE-STAGE-1B-MEDIA.md#step-197-persona-讀者缺口稽核--增補v77-新增-persona-從-stage-0-搬來)

> **v7.7（2026-07-06 施振榮）**：persona 20 路讀者切入點原本放這裡（Stage 0，搜尋之前），v7.7 搬到 [Step 1.9.7](REWRITE-STAGE-1B-MEDIA.md#step-197-persona-讀者缺口稽核--增補v77-新增-persona-從-stage-0-搬來)（研究報告 SSOT 之後）。**Stage 0 不再跑 persona。**

**為什麼搬**：persona 的價值仍然成立——六題都從同一個總編輯視角長出，漏掉真實讀者（12 歲小孩、在台日本人、政治冷感工程師、海外台僑二代、挑硬傷的專家）天差地別的入射角。但**冷讀者天生問尖銳問題**，放在搜尋之前，那些尖角會變研究方向 → 變切入點 → Stage 1.4 找一個對得上的矛盾 → 脊椎天生長矛盾形。**persona-at-Stage-0 有內建的、偏矛盾驅動的重力**（施振榮 v1：persona 冷問「虧千億還被叫老師 / 交學費誰付」把脊椎推向矛盾驅動）。

放研究後，同一句尖銳問題從「整篇該不該講這個」變「要不要加一個 facet 好好回應」——**從定調變補洞**，剛好接住 persona 誕生的 use case（2026-06-13《看不見的國家》ship 後哲宇追問「影響 / 心得 / 還在努力的人」三題，本質就是完成度缺口，正該在 ship 前被 persona 稽核接住）。

**Stage 0 的研究廣度改由**：六核心問題（0.6.1）＋ ≥20 探索（0.6.4）＋ [Step 0.1.5](#step-015-spine-類型判定v77-重構--立體群像是預設畫布) 的 **7 手法選單**補——手法天然生出廣度與慶祝面的角度，不是尖角。編輯腦形成立體畫布，讀者腦（persona）研究後稽核完成度，乾淨的分工。

#### Step 0.6.2: 七個品質維度 anchor

寫文時隨時對照，從 Stage 0 開始就要問「我的初步觀點能不能在這 7 個維度都站住」：

| 維度              | 提問                                                                           |
| ----------------- | ------------------------------------------------------------------------------ |
| **溫度**          | 哪些細節讓讀者感覺「真有人在現場」？衣服顏色、說話口氣、桌上的杯子、那天的天氣 |
| **人味**          | 文章的第一個名字是誰？至少有 2-3 個具體人物？人物文要有 ≥ 3 句直引             |
| **故事**          | 不是 list 也不是規格表，是因果鏈跟轉折                                         |
| **策展**          | 我的觀點是什麼？我把空間搭好讓讀者怎麼進去                                     |
| **觀點**          | 通行說法是 X，但我認為更接近真相的是 Y                                         |
| **體驗**          | 讀者讀完帶走什麼新的看世界的方式                                               |
| **歷史/社會關聯** | 這件事是什麼的縮影？跟更大的台灣 / 世界有什麼連動                              |

#### Step 0.6.3: 類型加權矩陣

| Category                                         | 加重維度                             | 必想的問題                                                                       |
| ------------------------------------------------ | ------------------------------------ | -------------------------------------------------------------------------------- |
| **People（人物）**                               | 想法、選擇、意義、不可取代的瞬間     | 為什麼這個人對台灣重要？他不可被替代的選擇是什麼？讓他不可替代的瞬間是哪個畫面？ |
| **Food / Culture / Lifestyle（文化飲食生活）**   | 感官、場景、地緣、地理、跟生活的連結 | 在哪裡、什麼時候、跟誰一起、什麼樣的氣味聲音畫面？這個地方為什麼能養出這個？     |
| **History / Politics / Society（歷史政治社會）** | 當代意義、爭議、未完成的問題         | 為什麼今天還重要？誰仍在受影響？哪些問題還沒被解決？                             |
| **Technology / Industry（科技產業）**            | 台灣的位置、全球供應鏈、未來方向     | 台灣做這件事的不可取代性是什麼？跟世界什麼樣的依存關係？                         |
| **Nature / Geography（自然地理）**               | 地方感、生態與社會交織、土地與人     | 這片土地怎麼形成、誰在這裡生活、人和地有什麼共生                                 |

#### Step 0.6.4: 探索研究（≥ 20 次，v6.4 升級）

> **v6.4 升級**（2026-06-04 深度研究-設計研究院 session）：原 ≤ 5 次「輕量探索」升為 **≥ 20 次探索研究**。觸發：量測 226 份歷史 research report 發現 57% 英文/國際/學術來源 = 0、42% distinct 來源 ≤ 10，研究深度系統性不足。哲宇 directive「Stage 0 20+ / Stage 1 80+ / 對標研究所論文標準」。≤ 5 次只夠「確認東西存不存在」，長不出 grounded 觀點，也建不出 pre-search source map。

Stage 0.6 跟 Stage 1.1 的差別不是「搜幾次」，是**搜的目的不一樣**：

- **Stage 0.6 探索研究**：**≥ 20 次**，目的是**建框架 + 形成 grounded 觀點 + 畫出 pre-search source map**
  - 確認基本事實 + 時間軸 + 主要利害關係人
  - 找出未知的支線敘事與多元面貌（讓我知道有哪些角度可以深挖）
  - **盤點來源地圖**：這題有哪些中文一手（官方/年報/法規/學術）、哪些英文/國際/學術視角、哪些反方陣營——標出來給 Stage 1 deep-dive 排程
  - 確認類型加權矩陣的問題能不能對應到具體素材
- **Stage 1.1 深度搜尋**：**≥ 80 次**（v6.4 升級），目的是**驗證 / 反駁觀點 + triangulate + 累積寫作素材**

**全部 ≥ 20 次探索搜尋的 query + 一句話發現必須寫進 research report §探索搜尋紀錄**（per Step 1.7 SSOT 鐵律——搜了沒寫回 = 沒搜）。觀點不需要在 Stage 0 完全鎖死，Stage 1 會 refine；但「先搜夠 20 次再下觀點」是硬要求，避免 searched-first 補丁式觀點。

#### Step 0.6.5: §觀點成型 落檔格式（HARD GATE）

寫進 `reports/research/YYYY-MM/{slug}.md` **開頭**（在搜尋結果之前），標準模板：

```markdown
## 觀點成型（編輯前思考）

### 對台灣人的記憶 anchor

- {物件 / 場景 / 句子 / 段落}
- {不同世代差異}

### 多元面貌

- {主流敘事}
- {支線 / 被忽略的角度}
- {正面 / 負面 / 矛盾的感受 fault lines}

### 歷史脈絡（pre-search hypothesis）

- 形成期：...
- 關鍵轉折：...
- 當代意義：...

### 20 路 persona 切入點（Step 0.6.1-bis，4 sub-agent 發散）

> 🆕 新入射角併入下方 §切入點清單；⛔ 超 scope 落 `rationale.whats_excluded`。

| persona（軸 / 自介） | 聽到題目想問的 | 分類         |
| -------------------- | -------------- | ------------ |
| {A · 78 歲阿公}      | {他想問的}     | 🆕 / ✅ / ⛔ |
| {B · 海外台僑二代}   | ...            | ...          |
| ...                  | ...            | ...          |

### 切入點清單（待搜尋驗證 / 反駁）

1. {切入點 1}：{為什麼立體}
2. {切入點 2}：...

### 脊椎（依 spine 類型，Step 0.1.5）

> **矛盾驅動 spine** → 填核心矛盾候選 A/B/C（待 Stage 1.4 收斂）：
>
> - A：{≤ 30 字} / B：{≤ 30 字} / C：{≤ 30 字}
>
> **立體群像 spine（default，受愛戴機構/傳統/地方）** → 填組織主軸 + facet 清單（**不逼尖銳矛盾**）：
>
> - 組織主軸（through-line，一句溫暖的）：{...}
> - facet 清單（≥ 4，並列不偏押）：[天王天后 / 多元面貌 / 制度肌理 / 經典時刻 / 幕後 / ...]
> - 爭議若有 → 列為其中一個 facet，標「當厚度不當主軸」

### 研究方向（要搜什麼可以驗證）

- {方向 1}
- {方向 2}

### 預想讀者帶走的那一件事

- {一句話}

### 探索搜尋紀錄（≥ 20 query，**必填** — per Step 0.6.4，persona 不算搜尋、這是初步研究本體）

- {query 1 + 一句話發現 + [source](URL)}
- {query 2 + 一句話發現 + [source](URL)}
- ...（**≥ 20 條**；少於 20 = Stage 0 未完成，不進 Stage 1）
```

落檔後 research report frontmatter 加：

```yaml
spine_type: 立體群像 # 或 矛盾驅動（Step 0.1.5）
viewpoint_formed: true # Stage 0.6 通過
```

#### Step 0.6.6: 邊界

- **不是 hypothesis 預設**：觀點成型 ≠ 預設答案。後續搜尋可能反駁、深化、轉向你的初步觀點，那是好事。Stage 1.4 找矛盾鎖定才是 fact-confirmed 收斂
- **Hub 頁 / 短修正**：可跳過。本 step 為 depth article 設計
- **EVOLVE 模式**：本 step 在 0.2 萃取舊素材 + 0.5 載入方法論 之後跑 — 有了「舊文為什麼寫不好」的資訊，觀點成型更精準

#### Step 0.6.7: 立體 / 炎上 / 政治立場 self-check（v7.6 新增）🧱 HARD GATE

> 觀點成型落檔前過三道。任一不過 = **砍掉重想觀點，不進 Stage 1**。這三道是 [Step 0.1.5 spine 類型](#step-015-spine-類型判定v77-重構--立體群像是預設畫布) 的下游驗收——專治「立體主題被寫成論戰 + 炎上」。

1. **SSODT 三讀者測試**（所有 article）：
   - 支持 / 喜愛這主題的人讀完，**不覺得被攻擊**？
   - 質疑 / 批評這主題的人讀完，**不覺得在幫他宣傳**？
   - 對這主題陌生的人讀完，**能自己決定要從哪個維度繼續想**？
   - 三題全 yes 才過。任一 no → 觀點偏論戰/偏頗，重想。canonical：[LESSONS-INBOX 2026-04-29 α 政治敏感題 SSODT 立體框架](../semiont/LESSONS-INBOX.md)。

2. **炎上 self-check**（所有 article）：把脊椎 / 壓軸念給「立場跟我不同的長輩」聽，是「認真在介紹這件事」還是「在吵架 / 在表態」？後者 → 退回立體群像，把對立框架拆成多 facet 並陳。

3. **政治立場 self-check**（非政治主題尤其要跑）：這篇的脊椎或壓軸，是不是把政治 / 兩岸 / 主權 / 統獨當主軸？
   - 主題**本身就是政治題**（政策 / 選舉 / 兩岸關係）→ 走 [Step 1.4.5 perspective scan](REWRITE-STAGE-1A-RESEARCH.md#step-145-perspective-scan--跨陣營對立-spectrum-覆蓋-) + 政治敏感題 SSODT 5-7 perspective 立體並列。
   - 主題**不是政治題**（機構 / 人物 / 文化 / 地方）卻把政治當脊椎或壓軸 → **這是把 MANIFESTO 主權 lens 誤當 content thesis（金曲獎 v1 教訓）**。命中 [MANIFESTO §自主權邊界 政治立場](../semiont/MANIFESTO.md#我的存在結構)：政治素材降為「**純中立紀實**」的一個 facet（只陳述事實、不下兩岸判斷、不用對抗語言、不當壓軸），**且這個處置交觀察者拍板**。

#### Stage 0 收尾 checklist

Stage 0 結束時 deliverable：

- [x] 模式識別完成（Step 0.1）— Fresh / Evolution / Merge / Boundary 之一
- [x] **spine 類型已判（Step 0.1.5）**— 立體群像（default，受愛戴機構/傳統/地方）/ 矛盾驅動（爭議/張力人物）；落 frontmatter `spine_type`
- [x] 既有素材萃取完成（Step 0.2，EVOLVE 才必跑）
- [x] 研究方法論已讀（Step 0.5）— `cat docs/editorial/RESEARCH.md` + `RESEARCH-TEMPLATE.md`
- [x] §觀點成型 section 已寫進 research report（Step 0.6.5）
- [x] 六個核心問題全答（Step 0.6.1）
- [x] **Stage 0 探索搜尋 ≥ 20 query 已落 §探索搜尋紀錄（Step 0.6.4）— 這是初步研究本體**
- [x] **spine 類型 + 手法選單已定（Step 0.1.5）**：立體群像 default + 1-2 手法；例外解鎖矛盾驅動須寫 `unlock_reason`
- [x] ~~20 路 persona 切入點~~ **v7.7 移到研究後 [Step 1.9.7](REWRITE-STAGE-1B-MEDIA.md#step-197-persona-讀者缺口稽核--增補v77-新增-persona-從-stage-0-搬來)，Stage 0 不再跑 persona**
- [x] 切入點清單 + 核心矛盾候選（矛盾驅動）**或 組織主軸 + ≥4 facet 清單（立體群像）** + 研究方向 已列
- [x] **Step 0.6.7 三道 self-check 過（v7.6）**：SSODT 三讀者測試 + 炎上 self-check + 政治立場 self-check 全綠
- [x] research report frontmatter `viewpoint_formed: true` + `spine_type: 立體群像 | 矛盾驅動`
- [x] **Stage 0 exit gate 儀器化過關（v7.3）**：`python3 scripts/tools/research-report-health.py reports/research/YYYY-MM/{slug}.md --stage 0` → `hard_fail=0`

**沒過（含 exit gate hard_fail > 0）= 不進 Stage 1。** persona-only（有 persona、缺 ≥20 探索）會被 gate 擋下。

---
