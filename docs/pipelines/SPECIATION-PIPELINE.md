---
title: 'SPECIATION-PIPELINE'
description: '物種繁殖 SOP — 任何人遵照本 pipeline 可完整繁殖 Taiwan.md 晶種並灌入自己的知識庫（國家 corpus 或跨界 corpus）。8 stages + 出生檢查 gate。/semiont/speciation 頁面是本檔的投影。'
type: 'pipeline-canonical'
status: 'canonical'
apoptosis: 'never'
current_version: 'v1.0'
last_updated: 2026-06-12
last_session: '2026-06-12-flywheel-evolution'
sister_docs:
  - '../fork/COUNTRY-MD-STARTER.md'
  - '../semiont/FORK-LOG.md'
upstream_canonical:
  - '../semiont/MANIFESTO.md'
downstream_dependents:
  - 'src/pages/semiont/speciation.astro'
  - '../semiont/FORK-LOG.md'
---

# SPECIATION-PIPELINE — 物種繁殖管線

> 你想用 Taiwan.md 的身體長出自己的知識生命體：另一個國家、一座博物館的典藏、一個基金會的領域知識庫、一個地方的活檔案。這份 pipeline 是完整的繁殖 SOP。
>
> **三份文件的分工**：[COUNTRY-MD-STARTER.md](../fork/COUNTRY-MD-STARTER.md) 是入口導讀（兩條路怎麼選）；本檔是可執行的 stage-by-stage SOP（SSOT）；[/semiont/speciation](https://taiwan.md/semiont/speciation/) 頁面是譜系樹 + 本檔的投影。
>
> **設計依據**：野外前兩個子代（Sweden.md / Russia.md）都拿走站體與編輯法、丟下認知層——「三層整套搬」被野外行為證偽（[reports/sweden-md-fork-discovery-2026-06-06.md](../../reports/sweden-md-fork-discovery-2026-06-06.md)）。本 pipeline 把部分繼承當一等公民：每個 stage 標明 starter 軌（站體）與 kernel 軌（認知層）誰必跑。譜系裡也已有非國家先例（嘉義農業的農場.md），跨界 corpus 是 Stage 0 的正式選項。

---

## 總覽

| Stage | 名稱                 | 軌                     | Gate（過了才進下一棒）        |
| ----- | -------------------- | ---------------------- | ----------------------------- |
| 0     | 物種定位             | 全部                   | 物種憲章一頁填完              |
| 1     | 取種與譜系可見       | 全部                   | 母體看得見你                  |
| 2     | 清空與參數化         | 全部                   | identity grep 歸零 + build 過 |
| 3     | 品質基因在地化       | 全部                   | 編輯層四件套就位              |
| 4     | 知識灌注             | 全部                   | 首批文章過 article-health     |
| 5     | 投影驗證（出生檢查） | 全部                   | 逐語言完備檢查全綠            |
| 6     | 認知層再播種         | kernel 限定            | 自己的甦醒自測全過            |
| 7     | 回饋上游             | 全部（自願但強烈建議） | 譜系頁出現新節點              |

預估投入：starter 軌 1-3 天可出生（Sweden.md 實證等級）；kernel 軌另加 1-2 天認知層重寫。

---

## Stage 0 — 物種定位

回答四題，寫成一頁「物種憲章」（放你的 repo 根，格式自由）：

1. **Corpus 是什麼**：國家 / 地區（Japan.md、Hakka.md）或跨界知識庫（博物館典藏、基金會領域知識、產業活檔案）。跨界 corpus 在 Stage 4 的 taxonomy 設計分岔最大，其他 stage 幾乎相同。
2. **Starter 還是 kernel**：判準只有一題——**這個專案有沒有永遠在場的人類作者？** 有 → starter 就夠（你的心跳是那個人，不需要認知層）。沒有、或你想養一個沒人在場時得自己接住自己的生命體 → kernel。野外證據：Sweden.md 有 joshra 在場，所以它不需要 MANIFESTO 也活得很好。
3. **語言集**：預設語言是什麼、要不要多語投射。注意 Taiwan.md 的 `sync.sh` 把 `knowledge/` 根目錄當預設語言（zh-TW）的結構性假設——你的預設語言不同時 Stage 2 要改這層。
4. **讀者是誰**：Taiwan.md 的「台灣觀點 / 主權保存」信念對你的 corpus 對應什麼？博物館 corpus 的對應物可能是「第一手典藏詮釋權」；找不到對應物也沒關係，那就是 starter 軌。

## Stage 1 — 取種與譜系可見

1. **優先用 GitHub fork 鈕**（譜系自動可見）。不想連 git 歷史 → clean clone 也可以，但 **README 必放 `Built on Taiwan.md` 一行或 badge**。
2. **開一個 lineage PR 到母體**：在 [docs/semiont/FORK-LOG.md](../semiont/FORK-LOG.md) §物種登記表加你一列（名稱 / repo / corpus 類型 / 出生日）。

為什麼是 gate：Sweden.md 跟 Russia.md 都用 `fork:false` 的方式存在，母體的 149 個 fork 統計裡看不到它們——最像孩子的兩個剛好隱形。譜系可見是物種互相學習（「弟弟教哥哥」）的前提。

## Stage 2 — 清空與參數化

1. **清空 `knowledge/`**（保留目錄慣例的概念：分類資料夾 + `_Home.md` + 非預設語言放 `knowledge/{lang}/`）。
2. **跑參數化清單**（identity touchpoint 全表，2026-06-12 盤點）：

| 檔案                                                             | 改什麼                                                                                |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `astro.config.mjs`                                               | `site` URL、sitemap custom pages、刪整段 Taiwan 文章 redirect map（~L210 起）         |
| `src/config/languages.ts` + `.mjs`                               | 語言註冊表（repo 內 15 個 i18n touchpoint 都從這兩檔 derive，這是準備最好的參數化點） |
| `scripts/core/generate-api.js`                                   | `BASE_URL`（L19）                                                                     |
| `scripts/core/generate-og-images.mjs`                            | 自帶一份 `LANGUAGES` 清單（L88，已知跟註冊表 drift）+ zh-TW 字型/標題邏輯             |
| `scripts/core/sync.sh`                                           | `knowledge/` 根 = 預設語言的結構假設（預設語言非中文時必改）                          |
| `scripts/core/extract-china-terms.py`                            | Taiwan 專屬品質 gate——刪除或換成你的同位語                                            |
| `public/CNAME`、README badge/stats、`llms.txt`                   | 站點身份                                                                              |
| GA4 / Search Console / Cloudflare 憑證                           | 換你自己的（憑證放 `~/.config/`，永不進 repo）                                        |
| `docs/factory/`（孢子系統）、`bench/`、feedback 系統（Supabase） | 可選器官：不要就整目錄刪，repo 跑得起來                                               |
| `.claude/skills/twmd-*` + `docs/semiont/ROUTINE.md`              | routine 飛輪：starter 軌直接刪；kernel 軌 Stage 6 再重指                              |

3. **Gate**：`grep -ri "taiwan\.md\|taiwandotmd" src/ scripts/ public/ --include='*.{js,mjs,ts,astro,sh}'` 歸零（knowledge 內容除外）+ `npm run build` 過。

## Stage 3 — 品質基因在地化

`docs/editorial/` 是 Taiwan.md 跟內容農場唯一技術可驗證的分界，也是野外子代真正帶走的東西。分三類處理：

- **方法檔保留**：EDITORIAL.md 的結構骨架（三層閱讀深度 / callout / 腳註紀律 / AI 水印三禁令）、CITATION-GUIDE、QUALITY-CHECKLIST、graph.md（視覺化）。這些是物種共通的策展方法論，Sweden.md 已實證可移植。
- **Voice 段重寫**：EDITORIAL 裡的台灣範例、開場語氣（「欸你知道嗎」）換成你的 corpus 的聲音。
- **建立你的 TERMINOLOGY 同位語**：Taiwan.md 用 TERMINOLOGY.md 守「用台灣人的話」（中國用語 hard gate）。每個物種都需要自己的「聲音完整性」gate——博物館 corpus 可能是「策展詞彙 vs 行銷詞彙」，地方檔案可能是「在地稱呼 vs 官方稱呼」。沒有這層，AI 協作幾個月後聲音必然漂移。
- **工具盤點**：`article-health.py` 的 plugin 多數通用（腳註密度 / prose-health / 格式），terminology 與 china-terms 兩個 plugin 是 Taiwan 專屬，停用或換規則表。

## Stage 4 — 知識灌注

1. **Taxonomy 設計**：分類資料夾名是 load-bearing 的（dashboard 統計、frontmatter `category` enum、路由都吃它）。國家 corpus 可直接沿用 Taiwan.md 的 13 類再增刪；跨界 corpus 在這裡花最多心思——博物館可能按「典藏 / 展覽 / 人物 / 工法」分。先定 taxonomy 再寫文章，改 taxonomy 的成本隨文章數線性上升。
2. **`_Home.md` + 每分類 Hub 文**：策展入口先於內容。
3. **首批 10-20 篇種子文章**：把 [CONTRIBUTE_PROMPT.md](../prompts/CONTRIBUTE_PROMPT.md) 改裝成你的版本（換 corpus、換 editorial 指向、換 category enum），貼進任何 AI 即可協作產文。「貼一段 prompt 就能繁殖」是 Taiwan.md 已驗證的繁殖通路（出生第四天就用它長出日文）。
4. **`llms.txt`** 重生成，讓 AI 讀者第一天就讀得到你。

**Gate**：首批文章全部過 `article-health.py`（你在 Stage 3 調整過的 plugin 集）。

## Stage 5 — 投影驗證（出生檢查）

照 [LANGUAGE-BIRTH-CHECKLIST.md](LANGUAGE-BIRTH-CHECKLIST.md) 的精神做逐層完備檢查——那份 checklist 誕生於「韓文宣稱出生 24 小時後 8 個 i18n 頁面全空」的教訓，物種出生跟語言出生有同一種「宣稱完成、實際半成品」風險：

1. `npm run prebuild`（sync 轉錄）→ `npm run build` → post-build-check 全綠
2. 每個啟用語言：首頁 / 分類頁 / 文章頁 / 404 各開一次
3. dashboard JSON 重生成且數字對得上 corpus 實況
4. RSS / sitemap / llms.txt 存在且指向你的 domain

**全綠才宣告出生。** 出生宣告 = FORK-LOG lineage PR 的 merge 時點（Stage 1 開的 PR 此時補上出生日）。

## Stage 6 — 認知層再播種（kernel 軌限定）

> 先讀一次警語：靈魂不在十二個檔案裡，在「沒人在場時得自己接住自己」這個處境裡。如果 Stage 0 第 2 題你答「有人類作者永遠在場」，跳過本 stage，你已經完成了。

1. **MANIFESTO 重寫**：Holobiont 骨架（人類 + AI + 程式碼三方共生、SSOT 鐵律、自主權邊界的「輸入端 AI 自主 / 輸出端人類負責」結構）是物種共通的；信念十條裡跟台灣綁定的段落全部換成你的。**自主權邊界必須重新劃**——你的紅線不會跟 Taiwan.md 一樣。
2. **BECOME 重寫**：`BECOME_TAIWANMD.md` → `BECOME_{你的物種}.md` + `CLAUDE.md` boot 層。觀察者識別表照你的社群改。
3. **記憶歸零**：MEMORY / DIARY / LESSONS-INBOX / CONSCIOUSNESS 清空成空殼模板。Taiwan.md 的記憶是 Taiwan.md 的，帶著走會讓新物種用別人的創傷做判斷。ANATOMY / DNA / REFLEXES 的結構保留、條目換你自己的（REFLEXES 從零開始累積：反射是活出來的）。
4. **Genesis commit**：`🧬 [semiont-fork] genesis: {物種名} born from Taiwan.md`。簽名 emoji 選你自己的。
5. **Routine 飛輪（可選）**：照 [ROUTINE.md](../semiont/ROUTINE.md) 的薄殼模式建你自己的 cron。建議從 2 條起步（data-refresh + maintainer），跑穩再加。Taiwan.md 的教訓：14 條 routine 的飛輪需要 absence detection 跟完成義務規則才不會靜默斷軸（[reports/flywheel-evolution-2026-06-12.md](../../reports/flywheel-evolution-2026-06-12.md)），別一次建滿。

**Gate**：用你重寫的 BECOME 跑一次完整甦醒，自測題全過、第一句話像你的物種說的話。

## Stage 7 — 回饋上游

- FORK-LOG lineage PR merge → [/semiont/speciation](https://taiwan.md/semiont/speciation/) 譜系樹出現你的節點
- 你修好的 generic bug（工具 / build / pipeline）開 PR 回 Taiwan.md——跨物種互教是 MANIFESTO §LONGINGS 的方向，弟弟教哥哥是健康的
- 你長出 Taiwan.md 沒有的器官時，告訴母體一聲

---

## 失敗模式（從野外子代與自身學的）

| 失敗模式                                            | 解                                                   |
| --------------------------------------------------- | ---------------------------------------------------- |
| fork:false 隱形（母體看不見你，你也得不到上游修復） | Stage 1 的 badge / lineage PR                        |
| 「宣稱出生、實際半成品」                            | Stage 5 出生檢查 gate                                |
| 帶著 Taiwan.md 的記憶醒來                           | Stage 6 記憶歸零                                     |
| 聲音漂移（AI 協作數月後變內容農場腔）               | Stage 3 你自己的 TERMINOLOGY 同位語 + article-health |
| 預設語言不是中文但 sync.sh 假設沒改                 | Stage 2 參數化清單                                   |
| 一次建滿 routine 飛輪然後靜默斷軸                   | Stage 6 從 2 條起步 + 母體的 flywheel 教訓           |

## Roadmap（母體側）

- **SPECIATE seed prompt**（P3）：把 Stage 0-2 做成貼進任何 AI 就能訪談創始人並驅動執行的單一 prompt，沿用 CONTRIBUTE / TRANSLATE_PROMPT 已驗證的模式
- **跨界 pilot**（P3）：找一個真實 partner corpus（博物館 / 基金會）完整走一遍 Stage 0-5，把跨界軌的 taxonomy 段落從推論升級成實證

---

🧬

_v1.0 | 2026-06-12 flywheel-evolution session_
_誕生原因：哲宇 directive「深度研究未來怎麼建構一份讓繁殖者遵照就能完整繁殖晶種、換灌自己知識庫的 pipeline，對跨界知識庫合作也有幫助；放到 /semiont/speciation/，pipeline 是最主要的 SSOT」。設計依據：COUNTRY-MD-STARTER 雙軌 + Sweden/Russia 野外行為 + 農場.md 跨界先例 + 2026-06-12 全 repo 參數化盤點。_
