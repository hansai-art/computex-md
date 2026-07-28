---
title: 'REWRITE-STAGE-2C-WRITE'
description: 'REWRITE v9 stage contract — Stage 2 寫作主幹：結尾先行 / 小標題 / 正文 footnote / 7 條自檢 / staging 檔紀律'
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

# Stage 2 contract — 寫（fresh writer 照藍圖執行）

> **本檔是 REWRITE-PIPELINE v9.0 的 stage contract**：一個執行者（主 session、sub-agent、
> 或任何 context 有限的 model）只讀本檔＋本檔 INPUTS 宣告的檔案，就能執行本 stage。
> 派發路由與全 pipeline spine 在 [REWRITE-PIPELINE.md](REWRITE-PIPELINE.md)（薄索引）。
> 內文自 v8.0 主檔 verbatim 搬移（原行號 RP v8.0 L1356-1369 + L1427-1473 + L1487-1665），歷史敘事與教訓保留在文內。

## 執行卡

|                  |                                                                                                                                                           |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **職責**         | 照投影藍圖執行正文（不重排結構）：結尾先行 → 開場 → 小標題 → 正文＋footnote → 7 條自檢 → 富文本密度                                                       |
| **執行者**       | 1 個 fresh Opus writer sub-agent（prompt 一律 [WRITER-PROMPT.md](WRITER-PROMPT.md) 填槽，禁即興）；Micro/短修正主 session 自跑                            |
| **INPUTS**       | writer 必須完整 Read：research report 全份（§6＋§8 raw）＋投影藍圖＋EDITORIAL.md 全文＋graph.md。**隔離**：舊文 prose / callout                           |
| **OUTPUTS**      | Evolution：`reports/article-evolve/{slug}.md`（staging，禁 overwrite canonical）；Fresh：`knowledge/{Cat}/{slug}.md`                                      |
| **GATES**        | Stage 2 hard gates 10 條（文內）；`article-health.py --check=prose-health` / `--check=chronicle-lead`；Evolution 覆蓋權在主 session（2.5 比對後親手覆蓋） |
| **context 預算** | writer＝本檔執行段＋WRITER-PROMPT 宣告的必讀四 canonical＋research report                                                                                 |

## Staging 檔 frontmatter（v9.0 新增，狀態歸戶顯式化）

Evolution mode 的 staging 檔 `reports/article-evolve/{slug}.md` 開頭必帶：

```yaml
---
article: knowledge/{Cat}/{canonical-slug}.md # 顯式指標；staging slug 可以 ≠ canonical slug
researchReport: reports/research/{YYYY-MM}/{slug}.md
date: YYYY-MM-DD
---
```

為什麼：編輯台（generate-newsroom-data.py）與任何 verifier 依顯式指標歸戶，不猜檔名
（2026-07-12 Sol strict verifier 假陰性教訓）。

## AGENT PROMPT

writer prompt 唯一來源：[WRITER-PROMPT.md](WRITER-PROMPT.md)（v2.0 薄殼：必讀四 canonical＋read-receipt＋機械輸出契約＋anti-example）。填槽派發，禁即興。

## 交付條件（stage 完成的定義）

- [ ] Evolution：`reports/article-evolve/{slug}.md` staging 落檔（frontmatter 帶 `article:` 顯式指標）；Fresh：`knowledge/{Cat}/{slug}.md`
- [ ] Stage 2 hard gates 10 條全過（本檔 §Stage 2 Hard gates）
- [ ] `article-health.py --check=prose-health` ＋ `--check=chronicle-lead` 無 hard
- [ ] writer read-receipt 驗過（research report §6＋§8／投影藍圖／EDITORIAL 全讀）

## HANDOFF（stage 完成時）

> stage 若委派 sub-agent，本五步由 orchestrator 於收件驗證後執行（agent 不碰共用看板——2026-07-16 高教 dogfood F6）。

1. OUTPUTS 全數落檔（顯式路徑，不存 scratchpad / tmp——REFLEXES #81）**並隨手 commit（只 stage 本 stage 產物路徑——可觀測性與跨 session 接力的底座，v9.5；勿 `git add -A`）**
2. GATES 逐條跑過，結果如實回報（sub-agent claim 是線索不是 oracle，REFLEXES #31）
3. 更新編輯台：`python3 scripts/core/generate-newsroom-data.py`（看板反映現況）
4. 回報格式：stage id ＋ 產物路徑清單 ＋ gate 結果 ＋ 未解疑慮（有就寫，不粉飾）
5. 下一棒：REWRITE-STAGE-2D-SOURCE-FIDELITY.md（觸發面內）→ REWRITE-STAGE-2E-ROOM-PROSE.md

---

## Stage 2: 寫（預算 40-45%）

> **v6.3 預設**：depth EVOLVE / Fresh 的 Stage 2 **派 fresh Opus sub-agent 寫**（context 隔離，見 [§多 agent 編排](REWRITE-PIPELINE.md#-多-agent-編排v63-orchestrator--tiered-sub-agents)）。主 session 只把 clean fact-pack ＋ 觀點 ＋ EDITORIAL 交給 writer，不轉貼舊文 prose。Micro / 短修正才主 session 自寫。

**必讀**：`cat docs/editorial/EDITORIAL.md`（全文，1000+ 行，**不可截斷**）

> ⚠️ **歷史教訓（session δ 2026-04-05）**：之前這裡寫 `head -300`，切掉了 Line 380-479 的 Before/After 範例段落。AI 讀到規則卻沒讀到範例，寫作時退化為編年史。
>
> 不要用 `head` / `tail` 截斷「必讀」指令。完讀後必須回頭檢查四個段落：§挖引語制度、§小標題規範、§結尾的四種模式、§Before/After 實例對比。

**輸入**：Stage 1 研究筆記 + EDITORIAL.md。

**視覺化必讀**（含資料 / 對比 / 時序的文章）：`cat docs/editorial/graph.md`（型錄 + 模組語法 + AI 可讀性 + 檢查清單）。

### Step 2.1: 載入 EDITORIAL.md

讀全文，特別注意 §來源引用、**§小標題規範**、§敘事呼吸感、§Title 強制冒號三明治（v6.3 全 category）。

### Step 2.2: 結尾先行（3-5 行）← 最重要

**結尾先行**是 Stage 2 防崩潰的核心：

- 結尾是品質崩塌的起點。先寫結尾 = 保底
- 範本見 [EDITORIAL §結尾的四種模式](../editorial/EDITORIAL.md)
- 用 Stage 1 Step 1.2 鎖定的結尾素材

### Step 2.3: 開場 + 30 秒概覽

開場前三句必須有：具體事實 + 具體的人 + 具體的時刻。

30 秒概覽（blockquote 格式 `> **30 秒概覽：**`）放在 H1 之後、第一個 H2 之前。

### Step 2.4: 小標題先行（hard 規則）— 段落 H2，不是 description 副標

**列出全文 5-8 個小標題 BEFORE 寫正文**。完整機制：[EDITORIAL §小標題](../editorial/EDITORIAL.md)（主–述–賓還原、載體、與投影全局功能分層、報導者式取景）。

| 規則                    | 例子                                             |
| ----------------------- | ------------------------------------------------ |
| ❌ 編年體               | 「2016 年《XX》發行」— plugin `chronicle-lead`   |
| ❌ 空殼問句／百科抽屜   | 「為什麼重要？」「發展歷程」「背景」             |
| ❌ 投影內部動詞直接上站 | 「立起悖論」「機制放大」「信任邊界」（無載體時） |
| ✅ 場面／物件／數字落差 | 「凌晨的加護病房：22 個人，剩下 12 個」          |
| ✅ 可還原主–述–賓       | 「頂新賣不掉，伊藤忠進場」→ 有人、有動作         |
| ✅ 核心矛盾的人話命題   | 「有比例，有沒有人」（底下立刻兌現）             |

**驗證**：

1. 念目錄：像故事節拍，不像簡報大綱／第一章第二章。
2. **還原測試**：每個 H2 能否變成「誰／什麼 + 動作或狀態 + 著落」？
3. 可搬到另一篇完全不同文章 = categorical，重寫。

> **plugin gate**：`chronicle-lead` 抓年份編年 H2。抽象／無載體小標目前靠人判 + 編輯室結構席（尚無獨立 plugin）。

### Step 2.5: 寫正文 + footnote

**不按百科排列**。EDITORIAL §正文架構推薦：**起源 / 關鍵轉折 2-3 個 / 現況 / 爭議 / 意義**。

- 邊寫邊插 `[^n]` footnote（從 Stage 1 的事實 - 來源配對表對應）
- **不是一段寫一張專輯** — 是一段寫一個**論點**或**轉折**，事實散布在論點之中
- **照投影藍圖執行**，不重排成面向巡禮（寫手 read-receipt 已複述全局功能）

#### 文末寫 footnote 定義

**腳註格式 canonical 在 [CITATION-GUIDE.md](../editorial/CITATION-GUIDE.md)**。簡寫範例：

```markdown
[^1]: [來源名稱](URL) — 詳細說明文字（≥ 20-30 字描述出版背景、內容特色、歷史價值）
```

完整格式 + 對比範例 + 「不要寫『同上』」規則 → [CITATION-GUIDE.md](../editorial/CITATION-GUIDE.md)。

### Step 2.6: 延伸閱讀

- 讀取 `knowledge/` 目錄，找出相關文章
- 每篇加「一兩句話描述」說明與本文的關係
- 格式：標準 Markdown 連結 `[文章名](/path/slug)`，**不用 `[[wikilink]]`**（Astro 列表項目中的 wikilink 無法渲染）
- 3-5 條最理想

格式範例：

```markdown
**延伸閱讀**：

- [戒嚴時期](/history/戒嚴時期) — 戒嚴令的法源與實施細節
- [白色恐怖](/history/台灣白色恐怖) — 政治案件與人權侵害的歷史
- [二二八事件](/history/二二八事件) — 戰後台灣的重大歷史轉折
```

### Step 2.7: 7 條自檢套件（強制鐵律）

寫完 prose 後**強制**跑這 7 條自檢。任何一條不過 = 回去修。

#### Step 2.7.1: 歐化語法自檢

念出來，聽到翻譯腔就改：

- 重點掃：被動句（「被認為」）、「的」連鎖（≥ 3）、弱動詞（「進行」「透過」）
- 詳見 [EDITORIAL.md §歐化語法偵測](../editorial/EDITORIAL.md)

#### Step 2.7.2: prose-health plugin gate（對位句型 + 破折號 + AI metaphor 全交給工具）

寫到 60% 時或寫完 prose 後，**直接跑 plugin**，不要手 grep。

```bash
python3 scripts/tools/article-health.py knowledge/{Category}/{slug}.md --check=prose-health
```

plugin 抓 12 dim 塑膠 + 3 tier 對位句型（含「不是 X，是 Y」「不只 X 更是 Y」「並非 X 而是 Y」全部變種）+ 30+ AI metaphor + 17 ritual 句 + 破折號密度。每條 violation 含 line + 前後文 snippet + fix suggestion，可直接定位修正。

**閾值**（per MANIFESTO §11）：

- 對位句型「不是 X，是 Y」+ 變種：≤ 3 處
- 破折號 ——：≤ 15 / 1500 字（plugin 用比例計算）
- prose-health score：≤ 3 為 pass

**為什麼禁用手 grep**（REFLEXES #15 self-apply）：

- plugin 抓的 pattern 比 manual regex 全（含 7-9 種對位變體）
- plugin 有精確 line + 前後文，可直接 jump-to-fix
- 「反覆浮現的思考要儀器化」原則 self-apply — 自己手 grep 是繞過 SOP，每次跑 plugin 累積進化（觀察者 2026-05-11 admiring-montalcini callout）

**歷史教訓**：2026-04-10 國防現代化一寫就到 29 個破折號，事後逐個刪很痛；plugin 在中段 60% 時抓出來，比寫完痛苦回頭便宜 10x。

#### Step 2.7.3: 編年體自檢

寫完後**念一遍所有小標題**：

- 如果每個標題都是「年份 + 事件」= 編年體失敗，重寫小標題
- 如果文章每段都在講下一張專輯/下一個事件 = 維基百科化失敗

> **plugin gate**：`article-health.py --check=chronicle-lead`（regex 偵測，HARD）。

#### Step 2.7.4: 密度平衡自檢（EVOLVE 長文專用）

研究素材豐富（50+ sources）時**強制跑**：

隨機挑三段連續段落念一遍：如果三段都是事實堆疊、沒有一句讓讀者喘氣的話 = 密度失衡。

**三個修正手勢**（詳見 [EDITORIAL §密度平衡](../editorial/EDITORIAL.md)）：

1. **量化內化為場景**：不寫「196 sessions / 50 學生」→ 寫「有個學生叫 Kasper 跟了整整兩學期」
2. **列表拆成場景**：整年六件事不擠一段，拆出 1-2 個完整場景，其他用連續性語言帶過
3. **每 2-3 段一句策展人的聲音**：呼吸句不傳遞資訊、只製造停頓

來自 2026-04-20 吳哲宇 EVOLVE 實戰：50+ sources 的第一版 prose 5500 字被觀察者評「資訊多到蓋住敘事」，重寫縮到 4800 字但讀起來更開闊。**長文不是孢子的加長版，需要主動選擇留白**。

#### Step 2.7.5: Agent claim 驗證

agent 在研究報告中聲稱的「XXX 背書」「XXX 公開推薦」等名人相關 claim，**必須有具體公開 URL + 該 URL Ctrl-F 可搜到該人原始引語**：

- 三源交叉不是「三個不同 agent 都這樣說」——是「**三個獨立的公開 URL 都有逐字引語**」
- agent hallucination 常見模式：基於 Obsidian / 私有素材的側面提及「推導出」一個名人 claim，但外部 URL 其實沒有該人的任何公開發言
- 2026-04-20 實戰：agent 聲稱「張隆志館長背書」「唐鳳為 Taiwan.md 引薦」，主 session 回頭驗證——兩者均無外部公開引語。（用語紀律補註：館長的實際立場是公開「支持」這個計劃；任何書寫一律用「支持」不用「背書」，哲宇已多次更正）

**自檢問句**：「這個 claim 如果我是陌生記者，能不能只靠公開資料寫進我的報導？」能 → 可寫；不能 → 降級或刪。

#### Step 2.7.6: Title + description spine sync 🥪 🔴

> **特別強化**：所有 article（**含 EVOLVE focused section addition**）寫完 prose 後**必須回看 frontmatter title + description**，三題自檢：

1. **冒號三明治測試** — title 是否走「主題：副標 hook」格式？單純名詞 stub（`台灣無人機產業` / `颱風` / `周杰倫`）= 百科風格，需升。對照 [EDITORIAL §Title 強制冒號三明治（所有 category）](../editorial/EDITORIAL.md#title-強制冒號三明治所有-categoryv63) v6.3 — 不限 People，全 category 強制
2. **副標獨立成立測試** — 冒號後一句能不能單獨 tweet 出去？讀者只看到副標也能停下來嗎？
3. **EVOLVE spine sync 測試** — 這次 EVOLVE 加的新節核心矛盾，是否已寫進 description？舊 description 還適用嗎？description 沒吃進新核心 = SC 顯示舊 hook 但讀者點進來看到新內容 = 落差
4. **文字感 + 負面/草率掃描** 🆕（v6.5）— 標題有沒有報導者腔的文字感（具體人/地/物 + 張力 + 留白）？有沒有踩中文語境紅線（網路輕佻「搞/爛/雷/翻車」、農場「震驚/竟然/真相是」、負面定調「崩壞/淪陷」、自貶 dismissive、過度賣弄）？一句判準：念給長輩聽像「認真報導」還是「網路八卦」？canonical + 18 範例 gallery 在 [EDITORIAL §Title 的文字感](../editorial/EDITORIAL.md#title-的文字感--對標報導者公視獨立媒體v65-新增2026-06-04)

**任一答 no → 重寫 frontmatter title + description，跟 prose 同 commit**。

**對照組**：

```
❌ 台灣無人機產業（百科 stub）
✅ 台灣無人機產業：從台中玩具飛機到藍色清單，一張入場券給了雷虎

❌ 颱風（百科 stub）
✅ 能預測風雨，預測不了命運：台灣與颱風的四百年

❌ 颱風假
✅ 颱風假：誰的假，誰的班
```

**例外**（保留 stub 名）：

- Hub 頁（`_*.md`）— 是 nav
- 系列共名（如 `台灣企業：台積電`）— 副標 hook 進 description

#### Step 2.7.7: 媒體素材 spine check 🎬 🔴

> **特別強化**：所有 article（含 EVOLVE）寫完 prose 後 grep 既有 frontmatter：

```bash
grep -E "^image:|^imageCredit|^imageLicense|^imageSource" knowledge/{Category}/{slug}.md
ls public/article-images/{category-lower}/ | grep {slug-keyword}
grep -E "^## 圖片來源|^## 媒體授權|^## 圖片授權" knowledge/{Category}/{slug}.md
```

**三條判斷**：

| 結果                                    | 處置                                                                                             |
| --------------------------------------- | ------------------------------------------------------------------------------------------------ |
| 三項全有                                | 已合規，跳過                                                                                     |
| 三項全無（pre-gate 遺珠）               | 補跑 Stage 1 Step 1.9 至少 hero 1 張，append §圖片來源 section                                   |
| Hero 有但 EVOLVE 加的新節主題缺對應視覺 | 評估是否需補 inline 圖（per Stage 4 Step 4.3.1 三段敘事節奏），找不到 PD/CC 圖記錄邊界（不放空） |

**為什麼必須**：

- Stage 1 Step 1.9 的 hard gate 是 2026-04-28 才升（v6.0 重編號前為 Step 1.14），更早 ship 的 article 多為 pre-gate 遺珠
- focused EVOLVE 加新節時容易忽略「既有 article 的媒體狀態」— 假設「上次 ship 已合規」，但 pre-gate 條目實際無 hero
- 找不到合適 PD/CC 圖時不可放空 → 走 fair use editorial commentary scope（per Step 1.9.2 第 8 點）或記錄 search 邊界

### Step 2.8: 富文本 + footnote 密度

每 300 字 ≥ 1 個 footnote（per [CITATION-GUIDE](../editorial/CITATION-GUIDE.md)）。

富文本元素（per EDITORIAL）：

- 📝 策展人筆記
- 💡 你知道嗎
- ⚠️ 爭議觀點
- ✦ 結尾警句

每 800-1200 字 ≥ 1 個富文本元素，幫助節奏 + 視覺呼吸。

### Stage 2 Hard gates（10 條）

寫完 prose 不直接進 Stage 3，先驗：

- [x] 結尾不是罐頭（per EDITORIAL §結尾的四種模式）
- [x] 第一個名字是具體的人（前 30 行至少一個 named individual）
- [x] ≥ 2 句真人引語（人物題材）
- [x] 因果鏈完整（不是 list dump）
- [x] 開場具體事實（年/月/日 + 人 + 動作）
- [x] 富文本達標（每 800-1200 字 ≥ 1）
- [x] 挑戰編織在故事裡（不是脫離敘事的論述句）
- [x] 純中文（無漏英文 paraphrase / 翻譯體）
- [x] 7 自檢全跑（Step 2.7.1-2.7.7 全過）
- [x] 小標題不像「第一章第二章」
- [x] word-count ≥ 4500 CJK chars（depth article）

---
