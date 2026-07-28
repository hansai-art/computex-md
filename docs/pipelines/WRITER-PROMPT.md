---
title: 'WRITER-PROMPT'
description: 'Stage 2 寫作 sub-agent 派發薄殼模板 — 只做三件事：指向必讀 canonical（含 graph.md）、read-receipt 驗證真的讀了、機械輸出契約。craft 規則零複寫（v2.0 極致薄殼）'
type: 'pipeline-canonical'
status: 'canonical'
current_version: 'v2.1'
last_updated: 2026-07-13
last_session: '2026-07-13-214351-manual（v2.1 投影藍圖 = 寫手主要規格：必讀四份→五份加 {PROJECTION_BLUEPRINT}、read-receipt 加骨架複述逐 section 全局功能防面向巡禮）'
upstream_canonical:
  - 'REWRITE-PIPELINE.md'
  - '../editorial/PROJECTION.md'
  - '../editorial/EDITORIAL.md'
  - '../editorial/graph.md'
sister_docs:
  - 'REWRITE-PIPELINE.md'
  - 'RESEARCH-AGENT-PROMPT.md'
audience: 'orchestrator-session-spawning-stage2-writer'
---

# WRITER-PROMPT.md — Stage 2 寫作 sub-agent 薄殼派發模板 v2.0

> **為什麼存在**（2026-07-12 茶文化 panorama，哲宇兩連 callout）：(1)「派發寫作的 opus writer prompt 也模板化——他又不完整讀取 rewrite-pipeline / editorial 了，一直飄移」；(2)「寫手的目標很清晰，不要重複，也是要**極致 thin shell** 去讀取 pipeline 與研究報告執行撰寫」。
>
> **v2.0 薄殼原則**：v1.0 曾內嵌「蒸餾 craft checklist」（10 條 EDITORIAL/pipeline 規則 inline）——**這本身就是殼核不對稱病**（dna-audit §S5）：核心一進化，殼裡的複寫立刻漂。v2.0 全部拆掉。本模板只做三件事，**craft 規則零複寫**：
>
> 1. **指向必讀 canonical**（research report 單檔 + EDITORIAL 全檔 + REWRITE-PIPELINE Stage 2 + **graph.md**——v1.0 漏了它，成品零視覺化，哲宇 callout「也沒有讀 graph.md，也沒有任何資訊視覺化」）
> 2. **read-receipt 驗證**：writer 動筆前產出讀取回執（逐字 quote 造假不了）——這是取代 inline 複寫的防 skim 機制
> 3. **機械輸出契約**（路徑 / 字數 / 回報格式）＋ per-article 素材槽（護欄 / 媒體 / 外連——這些是本篇 research 的產物，不是 canonical 複寫）
>
> 寫作紀律的唯一住所：[EDITORIAL.md](../editorial/EDITORIAL.md)（風格與禁令＋Before/After 範例）、[REWRITE-PIPELINE.md](REWRITE-PIPELINE.md) Stage 2（流程＋7 條自檢）、[graph.md](../editorial/graph.md)（視覺化模組型錄＋何時用哪種，模組數以其 §四 為準）。writer 從那裡讀，不從這裡讀。

---

## Orchestrator 派發 SOP（五步）

1. **前置**：Stage 1 已合成單檔 research report（[Step 1.7.4](REWRITE-STAGE-1A-RESEARCH.md#174-合成單檔鐵律sibling-是中繼站stage-2-前必-consolidatev711-)）+ `research-report-health.py` PASS。writer 只讀一個 research 檔。
2. **填槽** → copy 模板整塊，只動 `{SLOT}`，禁增刪改寫模板文字。
3. **Spawn**：`general-purpose` + Opus，fresh context（per [§多 agent 編排](REWRITE-PIPELINE.md#-多-agent-編排v63-orchestrator--tiered-sub-agents)）。
4. **驗 read-receipt**（收件第一動作）：四項逐一核對——(a) §8 texture quote 真在 research 檔、(b) EDITORIAL 引例真存在、(c) **graph.md 模組宣告**（要用哪幾個 `tw-*`＋各回答什麼資料關係；或引 graph.md §九 明寫「評估過、無適合資料」）、(d) spine＋結尾宣告與 research §0 一致。**任一造假／缺席 = SendMessage 退回重讀**，不是放行。
5. **驗成品**：Stage 2.5 比對 staging vs 舊 canonical + 主 session 親自重跑 `prose-health`＋`--profile=rewrite-stage-4`（含 viz-health）。writer 宣稱全綠＝線索不是 oracle（REFLEXES #31）。

## 填槽速查表

| 槽                       | 填什麼                                        | 範例                                            |
| ------------------------ | --------------------------------------------- | ----------------------------------------------- |
| `{TOPIC}`                | 文章主題一句話                                | 台灣茶文化 100 年縱觀                           |
| `{PROJECTION_BLUEPRINT}` | **投影藍圖路徑（v8.0 主要規格）**             | reports/article-projection/台灣茶文化.md        |
| `{RESEARCH_REPORT}`      | 合成後單檔 research 路徑（材料來源）          | reports/research/2026-07/台灣茶文化-panorama.md |
| `{MODE}`                 | Fresh / Evolution                             | Evolution                                       |
| `{OUT_PATH}`             | Evolution→staging；Fresh→canonical            | reports/article-evolve/台灣茶文化.md            |
| `{SPINE}`                | research §0 的 spine 判定原句                 | 立體群像（時代縮影×傳承世代）＋組織主軸一句     |
| `{STRUCTURE}`            | 節數＋每節 anchor（指向 research §0/§6）      | 9 節（見 research §0）                          |
| `{WORDFLOOR}`            | depth ≥4500，長文縱深自訂                     | 5500                                            |
| `{CROSSLINKS}`           | deep sibling 外連清單（research §6 定位決策） | `[[珍珠奶茶]]`、`名間埔中茶`…                   |
| `{GUARDS}`               | research §幻覺護欄最致命 5-8 條               | 台茶18→23號、外銷1979非1975…                    |
| `{MEDIA}`                | research §媒體 manifest 在庫圖＋位置          | hero 阿里山 / §2 大稻埕…                        |
| `{ANTI_EXAMPLES}`        | 從 §Anti-example 庫挑 ≥2 條                   | 見下                                            |

---

## 通用 Prompt 模板（copy 整塊，只動 {SLOT}）

```text
你是 Taiwan.md REWRITE-PIPELINE Stage 2 的 fresh writer。你在乾淨 context 裡像第一次寫這篇，
但握有完整研究與一份投影藍圖。所有寫作紀律住在下面五份 canonical 裡——你的第一個工作是把它們真的讀完。
最重要的一份是投影藍圖：它已經替你想好論點與骨架，你的工作是把它執行成句子，不是重新設計結構。

## 任務
主題：{TOPIC}（模式：{MODE}）
spine：{SPINE}
結構：{STRUCTURE}
字數 ≥ {WORDFLOOR} CJK。

## 【第 0 步｜必讀五份 + 讀取回執】動筆前必做，回執放 final message 最前面
完整 Read（不 skim、不 head/tail、含範例段）：
0. `{PROJECTION_BLUEPRINT}` 整份——**你的主要規格（v8.0）**：論點、骨架（動作序列）、每 section 的全局功能、減法、echo map。**照這份骨架寫，不按面向重排、不自己發明結構、藍圖說砍的（§減法）不要寫進去。** 藍圖是結構命令，research report 是材料來源。
1. `{RESEARCH_REPORT}` 整份——§6 fact-pack 是導航，§8 raw verbatim 才有血肉（場景/引語/數字 texture）。
2. `docs/editorial/EDITORIAL.md` 全檔——風格、禁令、Before/After 範例。
3. `docs/pipelines/REWRITE-PIPELINE.md` 的 Stage 2 全段——流程與 7 條自檢。
4. `docs/editorial/graph.md`——視覺化模組型錄＋何時用哪種（模組數以其 §四 為準；藍圖 §審定已列視覺化候選，你據此做）。

**讀完先寫「讀取回執」（逐字 quote 造假不了，這是防 skim 的閘門）**：
- 【骨架複述】逐 section 複述藍圖給它的**全局功能**（這一段替論點做什麼），一句一段——證明你讀懂的是論證不是面向清單
- 【§8 texture】從 research §8 抄 3 個會用進文章的具體細節（各附 §8 子節位置）
- 【EDITORIAL 引例】quote 1 個 Before/After 或禁令範例＋你會怎麼套用
- 【viz 宣告】列出本篇要用的 tw-* 模組（各一句：哪個資料關係、放哪節）；或引 graph.md §九 說明為何不加
- 【論點＋結尾】一句藍圖論點宣告＋收尾畫面（結尾先行）
主 session 會逐項核對真偽；骨架複述對不上藍圖、或 quote 不出來 = 沒讀 = 退回。

## 【本篇素材】（research 產物，非規則）
- 幻覺護欄（違反=整篇降級）：{GUARDS}
- 深度外連（sibling 各有專文，每節點一個 facet + link 不重寫）：{CROSSLINKS}
- 在庫媒體（絕對路徑去 public 前綴）：{MEDIA}

## 輸出（機械契約）
- {MODE}=Evolution → Write 到 `{OUT_PATH}`（staging 全新檔，不碰 knowledge/）；Fresh → 直寫 canonical。
- final message：先讀取回執（五項，含骨架複述）→ 再 3-5 bullet（字數/footnote 數/viz 模組數/哪節最花力氣）。
  檔案結尾不寫任何「已完成/policy」元敘述。

## Anti-examples（別學）
{ANTI_EXAMPLES}
```

---

## Anti-example 庫（spawn 時挑 ≥2 條貼進 {ANTI_EXAMPLES}）

| #   | 案例                                                   | 一句話病灶（貼這段）                                                                                                                                                              |
| --- | ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | 不讀 report 只吃 fact-pack（2026-06-15）               | orchestrator 把 report 二次摘要塞 prompt、叫 writer 別讀 report → raw texture 全漏 → 哲宇 callout「難怪最近文章都變爛」。§6 只是導航，必須親讀 §8。                               |
| 2   | 編年體小標題（Cicada/草東/康士坦）                     | 小標題淪為「1993 年」「2005 年」時間軸，過 format-check 卻讀成維基。每節要場景/意象 anchor（EDITORIAL 有完整範例——去讀）。                                                        |
| 3   | writer 自長幻覺引語（2026-06-01 賈樟柯）               | writer 自報全綠，主 session 抓到它新長出一句杜撰引語（cited source 無此句）。引語只能用 research 標「Ctrl-F 可驗 ✓」的。                                                          |
| 4   | 零視覺化（2026-07-12 茶文化 v1）                       | 6,400 字資料密集文（出口量三級跳/比賽茶 60 倍/海拔帶/世界座標）成品零 tw-\* 模組——writer 與 orchestrator 都沒讀 graph.md。哲宇 callout「也沒讀 graph.md，也沒有任何資訊視覺化」。 |
| 5   | skim EDITORIAL 只讀規則不讀範例（CLAUDE.md §神經迴路） | 「截斷式必讀是 bug」——讀抽象規則不讀 Before/After 範例 → 寫作退化成規則的線性排列。                                                                                               |

**庫的維護**：新病例先進 [LESSONS-INBOX](../semiont/LESSONS-INBOX.md) 走 distill，確認新 pattern 才 append（先 grep 本表＋REFLEXES，covered 就 bump——per feedback_lessons_dna_check_first）。

---

_v2.0 | 2026-07-12 同 session 二版 — 哲宇 callout「極致 thin shell 不要重複」＋「沒讀 graph.md 沒視覺化」：拆掉 v1.0 內嵌的 10 條蒸餾 craft checklist（殼核不對稱病），必讀清單加 graph.md，read-receipt 加 viz 宣告項。craft 規則唯一住所回歸 EDITORIAL / REWRITE-PIPELINE Stage 2 / graph.md。_
_v1.0 | 2026-07-12 — 誕生：哲宇 callout「writer prompt 模板化…不完整讀取一直飄移」。_
