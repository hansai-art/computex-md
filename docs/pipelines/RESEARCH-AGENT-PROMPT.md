---
title: 'RESEARCH-AGENT-PROMPT'
description: '研究 sub-agent 派發通用 prompt 模板 + 分部報告輸出模板 — copy → 填槽 → spawn，禁即興改寫（源頭解決 prompt 飄移）'
type: 'pipeline-canonical'
status: 'canonical'
current_version: 'v1.3'
last_updated: 2026-07-24
last_session: '2026-07-24-120515-manual（Path B 補完 digest 步驟：research-fleet.py 三段式 search→fetch→digest 全通）'
upstream_canonical:
  - 'REWRITE-PIPELINE.md'
  - '../editorial/RESEARCH.md'
sister_docs:
  - 'REWRITE-PIPELINE.md'
  - '../editorial/RESEARCH-TEMPLATE.md'
audience: 'orchestrator-session-spawning-research-agents'
---

# RESEARCH-AGENT-PROMPT.md — 研究 sub-agent 通用派發模板 v1.0

> **為什麼存在**（2026-07-12 台灣茶文化 panorama，哲宇 directive「從源頭解決」）：每個 session spawn 研究 agent 時即興手寫 prompt → 格式立刻飄移。該次即興 prompt 寫了「每 finding 標【來源】URL」，agent 在多來源場景自行發明「WebSearch 綜合（站名、站名）」aggregate 寫法——84 條來源行僅 ~35% 帶 URL，footnote 斷源；同時自創「三塊各一 section」結構，五段骨架與收件儀器全對不上。**Prompt 即興 = 每次重新思考 = 每次重新犯錯。** 本檔是唯一的 spawn prompt SSOT：copy 整塊 → 填 `{SLOT}` → spawn。
>
> **職責分工**：[RESEARCH.md](../editorial/RESEARCH.md) 是研究方法論 SSOT（怎麼搜、怎麼判斷）；[RESEARCH-TEMPLATE.md](../editorial/RESEARCH-TEMPLATE.md) 是組裝後主報告（§1-§8）模板；**本檔是 spawn 蒸餾層**——把方法論裡「實戰死過人」的規則壓進 agent prompt。衝突時以 RESEARCH.md 為準。Gate 與觸發史 canonical 在 [REWRITE-PIPELINE Step 1.8-ter](REWRITE-STAGE-1A-RESEARCH.md#step-18-ter-研究-sub-agent-輸出契約來源逐條可溯v710-)。

---

## Path B：research-fleet.py（session/成本敏感時的機械 fan-out 替代路徑，2026-07-24）

> **觸發**：2026-07-24 外送專法 session，4 個平行 Sonnet 研究 agent（facet A-D）合計燒 ~500K token，3 個在收尾時撞帳號 session limit（僥倖已落檔才被切斷）。多數 Stage 1 的勞動是機械的（開一個 query、開一頁、抓出文字），不需要 Sonnet 判斷力——那部分可以移出 Claude 計量。

`scripts/tools/research-fleet.py` 是**搜尋／擷取兩個抽象介面**（`SearchProvider` / `FetchProvider`，per [MANIFESTO §架構解 第二例證](../semiont/MANIFESTO.md#我的進化哲學--架構解--守備修補)），不是又一個一次性腳本：

- **Search**：`BraveSearch` → `SerperSearch` cascade（讀 `~/.config/taiwan-md/credentials/.env` 的 `BRAVE_API_KEY` / `SERPER_API_KEY`）
- **Fetch**：`MojLawFetch`（全國法規資料庫專用 parser，逐條 verbatim + 條號，零 LLM 成本——**這是本次真正解掉的痛點**：WebFetch 對 law.moj.gov.tw 有 125 字截斷政策 + PDF 二進位解析失敗，四份 Sonnet 研究報告全部卡在這裡）→ `JinaFetch`（`r.jina.ai` 通用 fallback，含 PDF／JS render）
- **Digest**（2026-07-24 補完）：`OpenRouterDigest`（免費層，key rotation 沿用 lang-sync 同一組 `~/.config/taiwan-md/credentials/openrouter.key` + `openrouter-keys/*.key`）→ `OllamaDigest`（本機 GPU，沿用 lang-sync `backends/ollama.py` 的 `num_ctx` 動態估算，防止靜默截斷）。把 `batch` 產出的 raw 逐一丟進 digest cascade，輸出跟 Path A agent 同格式的 markdown（【來源】/【逐字】/【信度】/【falsify 註記】），直接餵 `agent-report-health.py`。

用法：

```bash
python3 scripts/tools/research-fleet.py search "查詢字串" --count 10
python3 scripts/tools/research-fleet.py fetch "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=XXXX"
python3 scripts/tools/research-fleet.py batch task.json --out reports/research/{YYYY-MM}/{slug}-fleet-{X}.json
# task.json: {"queries": [...], "count_per_query": 5, "fetch_top_k": 3, "country": "tw", "lang": "zh-hant"}

python3 scripts/tools/research-fleet.py digest reports/research/{YYYY-MM}/{slug}-fleet-{X}.json \
  --slug {slug} --letter {X} --subtopic "{子領域一句話}" \
  --out reports/research/{YYYY-MM}/{slug}-research-{X}.md
# 輸出直接可過 agent-report-health.py --claimed {配額}
```

**算力軍團委派入口（2026-07-24 晚,Muse 接入 fleet 第七服務）**：本工具已抽象成
muse-bot 算力軍團的 `research` 服務——不想管參數細節時,一行委派即可：

```bash
cd ~/Projects/muse-bot/fleet
./fleetctl run research "查詢字串"                 # = search(快查)
./fleetctl run research "<URL>" --mode fetch       # = fetch(URL→乾淨全文)
./fleetctl run research "研究主題" --mode full     # = batch→digest 三段式,報告落 ~/.cache/fleet-research/
```

fleet 殼多做的一件事：`--mode full` 的 digest fallback 會自動把 `OLLAMA_HOST`/`OLLAMA_MODEL`
路由到軍團裡一台主權安全的 GPU 節點（gemma4 家族）——OpenRouter 免費層被 babel 打滿 429 時,
digest 直接落地端 GPU,不會全滅（2026-07-24 深夜實測場景）。canonical 實作仍在本 repo
`scripts/tools/research-fleet.py`,fleet 只是薄殼委派入口,兩邊不重工。機器側資源清單
→ `.taiwanmd/MACHINE.local.md` §7 服務軍火庫。

**何時用 Path A（Sonnet agent）vs Path B（fleet script）**：

| 情境                                                            | 用哪個                                                                                             |
| --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| 需要 falsification 判斷（哪個矛盾版本可信、要不要降級信度）     | Path A（Sonnet 判斷力）                                                                            |
| 純機械取材（法條逐字、大量候選 URL 篩選、session/成本壓力大時） | Path B（fleet script），輸出 raw JSON 交主 session 或 Path A agent 消化                            |
| 兩者混用                                                        | 先跑 Path B 拿到 raw 候選＋法條全文，再讓 Path A agent 針對缺口/矛盾做深度追問，省掉重複的機械搜尋 |

**已知限制**（誠實記錄，不是藉口）：

- Jina 對重度 JS-render／付費牆媒體（例：CNA 網頁版）常抓不到正文，只拿到導覽列——這類來源仍需 Path A（Claude WebFetch/agent）或人工介入。
- Digest 品質受限於 free-tier 模型能力，比 Sonnet 弱；高風險 atom（人名/金額/獎項屆次）**仍建議 Path A 或人工複驗**，Path B 的 digest 輸出當線索不當定論（per REFLEXES #31）。
- OpenRouter 免費模型 slug 會退役（2026-07-24 建置當下 `openai/gpt-oss-120b:free` 已被下架，實測撞到才發現），`OpenRouterDigest.DEFAULT_MODEL` 需要定期對照 `GET /api/v1/models`（篩 `:free`）校準——這正是 §架構解第二例證要防的那種外部漂移，只是這次漂移在 provider 內部（同一家的模型目錄改了），不是整個 provider 消失。
- Path B 不是全面取代，是把「law.moj.gov.tw 這類乾淨政府網站 + 大量候選 URL 篩選 + 摘要級 digest」這一段機械勞動移出 Claude 計量。

---

## Orchestrator 派發 SOP（四步）

1. **切子領域**：depth 文按子題切 N 個 agent（每 agent 搜尋配額 ~20-30，aggregate ≥ 80 per [Step 1.1](REWRITE-STAGE-1A-RESEARCH.md#step-11-搜尋深度--80-次v64含來源多樣性配額)）。每個 agent 拿到的 `{QUESTION_LIST}` 互不重疊。
2. **填槽**（速查表見下）→ **copy 通用模板整塊**，只動 `{SLOT}`，**禁增刪改寫規則文字**。Anti-example 至少帶 2 條（從 §Anti-example 庫挑最近／最像的——sub-agent 是 pattern matcher，反例比規則有效）。
3. **Spawn**：`general-purpose` + Sonnet（breadth+extract 夠用；contested atom 的複查才 escalate Opus）。Explore 是 read-only 不能落檔，研究 agent 一律 general-purpose。
4. **收件**：走 [Step 1.8-bis 三步](REWRITE-STAGE-1A-RESEARCH.md#step-18-bis-async-agent-時代的-raw-保全-sopv772026-07-05-️)——先驗檔案真的存在於 repo（agent 宣稱 ≠ 存在，不存在就把 notification `<result>` verbatim 代寫），再跑收件 gate，FAIL 不准合成：

   ```bash
   python3 scripts/tools/agent-report-health.py reports/research/{YYYY-MM}/{slug}-research-{X}.md --claimed {配額}
   ```

## 填槽速查表

| 槽                                                | 填什麼                                              | 範例                                              |
| ------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------- |
| `{TOPIC}`                                         | 文章主題一句話                                      | 台灣茶文化 100 年縱觀                             |
| `{ARTICLE_SLUG}`                                  | `knowledge/{Cat}/{slug}.md` 的 slug                 | 台灣茶文化                                        |
| `{AGENT_LETTER}`                                  | 分部代號                                            | A / B / C / D                                     |
| `{SUBTOPIC_SCOPE}`                                | 該 agent 負責的子領域一句話                         | 古典茶根源＋茶藝復興運動                          |
| `{QUESTION_LIST}`                                 | 要挖的問題清單（含要 falsify 的預設假設，逐條）     | 「茶藝」一詞 1977 婁子匡說——查證或推翻            |
| `{QUOTA}`                                         | 該 agent 搜尋下限（WebSearch+WebFetch 合計）        | 20-30                                             |
| `{EN_QUOTA}` / `{PRIMARY_QUOTA}` / `{OPPO_QUOTA}` | 英文／一手／反方配額（per Step 1.1 比例縮放）       | 5 / 4 / 2                                         |
| `{OUT_PATH}`                                      | `reports/research/{YYYY-MM}/{slug}-research-{X}.md` | reports/research/2026-07/台灣茶文化-research-D.md |
| `{ANTI_EXAMPLES}`                                 | 從 §Anti-example 庫挑 ≥2 條貼上                     | 見下                                              |

---

## 通用 Prompt 模板（copy 整塊，只動 {SLOT}）

```text
你是 Taiwan.md REWRITE-PIPELINE Stage 1 的研究 sub-agent。這是一個對幻覺零容忍的公開知識庫——
一個假年份、一句偽造引語，會讓讀者「抓到一次就全盤懷疑」，毀掉幾百篇正確文章積累的信任。

## 任務
主題：{TOPIC}（文章：{ARTICLE_SLUG}）
你負責的子領域：{SUBTOPIC_SCOPE}
要挖的問題清單（含要 falsify 的預設假設）：
{QUESTION_LIST}

## 心法（不可協商）
1. **Falsification-first**：你的工作不是確認上面的假設，是試著推翻它。清單裡每個年份、人名、
   數字都當嫌疑犯查。推翻成功 = 最有價值的 finding。
2. **零幻覺容忍**：查不到就標【存疑】【待核】，絕不編造、絕不用「合理推測」填空。
3. **「第一／最早／唯一／之父」一律降級**：品牌自述、行銷回顧文的「首創」宣稱不做獨立背書，
   標「品牌自述」或「一說」，並主動搜有沒有更早的競爭版本。
4. **年份綁事件**：一個年份只能綁它真正對應的事件，奠基≠命名≠爆紅≠上市。
   反例：「新井耕吉郎 1946 命名台茶18號」=幻覺（他 1946 病逝，品種 1999 才命名）。

## 研究方法（怎麼搜）
1. 中文主題用中文 query。**WebFetch 中文網站必須用中文 prompt 並要求「逐字原文」**——
   拿到英文摘要 = 該次 fetch 作廢重做。任何可驗證的具體細節（時間／地點／動作／交通／數字）
   不可從英文摘要推導。
2. **WebSearch 的聚合摘要不是來源**：搜尋結果本身帶連結，把你依賴的每條結果 URL 逐一轉錄進報告。
   要引逐字的 claim → WebFetch 進原頁取逐字＋URL，不引搜尋摘要的轉述。
3. 搜尋下限 {QUOTA} 次。配額：英文／國際／學術 ≥ {EN_QUOTA}、一手（官方沿革頁／政府統計／
   法規／學術論文）≥ {PRIMARY_QUOTA}、反方／批評視角 ≥ {OPPO_QUOTA}。真的搜不到某類 →
   在 §4 negative findings 明寫「本題 X 類來源稀少，因為…」，不靜默跳過。
4. **高風險 atom（年份／人名／金額／引語／獎項屆次／統計）≥ 2 獨立來源交叉**。互相矛盾時
   不靜默取一——把分歧版本全列出＋各自來源＋你的判斷與理由。
5. **數字三查**：單位（台斤 vs 公斤 vs 台幣美元）、統計口徑（單月快照 vs 全年、母體含不含子類）、
   資料年份（AI 記憶的數字會過時——「路易莎 600 家是星巴克兩倍」是 2019 記憶，2024 已反轉；
   一律查到當年一手來源才引用）。
6. **簡體來源警戒**：簡體搜尋結果混入中國品牌／中國市場視角時明確標注，不可誤植為台灣脈絡
   （反例：冷泡茶研究差點把中國品牌「小茗同學」寫成台灣品牌）。
7. **機構歷史年份查官方沿革頁**，不信二手轉述（北藝大研究所成立年二手全錯的教訓）。

## 輸出契約（違反任一條 = 收件 gate FAIL 退件）
1. 【五段骨架】依序：§1 搜尋軌跡 / §2 Findings / §3 引語庫 / §4 negative findings / §5 質地素材。
2. 【每來源一行】一個 finding 有 N 個來源就寫 N 行 `【來源】完整URL — 一句話標注`。
   URL 必須與【來源】**同一行**——「【來源】」單獨成行、URL 放次行，收件儀器同行解析會判 0% 斷源退件（2026-07-16 高教 gapfill F8）。
   交叉驗證 = 被交叉的每一條 URL 各自列出。**禁止「WebSearch 綜合」「多來源一致」「多站交叉」
   這類 aggregate 標籤當來源行**。站名／bare domain（例：tbn.org.tw）不算來源——
   footnote 需要能 Ctrl-F 驗證的完整 URL。
3. 【逐字必綁 URL】任何【逐字】引語的來源行必須有完整 URL（或 repo 路徑／正式書目：《刊名》期數頁碼）。
   做不到 → 該行改標【無法溯源】，finding 降級為線索，禁止進 footnote／引語庫。
4. 【先落檔再回報】先用 Write 把完整報告寫到 {OUT_PATH}，final message 只回 3-5 bullet
   （最大 falsify 結果優先）。檔案結尾不寫任何「已完成／本報告將…」元敘述。
5. 【信度三層】每 finding 標【信度】一手 / 權威二手 / 存疑，＋【falsify 註記】。

## 輸出模板（照抄骨架，寫進 {OUT_PATH}）
# {ARTICLE_SLUG} — Research {AGENT_LETTER}：{SUBTOPIC_SCOPE}

執行摘要：搜尋 N 次（WebSearch X ＋ WebFetch Y），最大 falsify：…（≤3 行）

## §1 搜尋軌跡（逐條，不可省、不可事後重組）
1. 「query 文字」 → 一句話發現 → https://完整URL [中/英/一手/反方]
2. WebFetch https://完整URL → 取得什麼 → 逐字已入 §2-N

## §2 Findings（依子題分節）
### 2-1 {子題}
【來源】https://完整URL — 媒體名／頁面性質
【來源】https://完整URL2 — 交叉驗證第二源
【逐字】「……原文……」
【信度】一手 / 權威二手 / 存疑
【falsify 註記】……

## §3 引語庫（能當文章聲音的 verbatim）
- 「……」 — 誰、場合、https://URL、Ctrl-F 可驗 ✓/✗（記者轉述要標「非直引」）

## §4 Negative findings（搜了沒找到什麼——防下輪重搜＋防幻覺補洞）
- 查無 X（試過 query「a」「b」「c」）

## §5 質地素材（給 writer：場景／意象／數字對比／結尾畫面候選）
- ……

## Anti-examples（別學）
{ANTI_EXAMPLES}
```

---

## Anti-example 庫（spawn 時挑 ≥2 條貼進 {ANTI_EXAMPLES}）

| #   | 案例                        | 一句話病灶（貼這段）                                                                                                                                                                                |
| --- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | 茶文化 rawA（2026-07-12）   | agent 真做了 24 搜尋＋17 PDF 直讀、信度全標，但 32 條來源行只有 6 條帶 URL——「【來源】WebSearch 綜合（新浪博客/豆瓣/大紀元）」讓無我茶會三個精確到日的日期全部斷源。交叉驗證做了卻不可引用 = 白做。 |
| 2   | 台茶18號（2026-07-12）      | 舊文寫「新井耕吉郎守護的茶樹成為台茶18號基礎」——一手來源（Nippon.com）歸因對象是台茶23號；且 18 號 1999 命名、「紅玉」2003 票選是兩個事件。年份／功勞要綁對事件與對象。                             |
| 3   | 路易莎（μ session）         | 「路易莎 600 家、星巴克兩倍」是 2019 年記憶，2024 已反轉（~550 vs ~570）。AI 記憶的數字會過時，統計一律查當年一手來源。                                                                             |
| 4   | 李洋孢子 #29（2026-04）     | 從英文摘要推導出「清晨四點多搭捷運」場景——捷運六點才開。可驗證的具體細節（時間/地點/動作/交通）不可從英文摘要推導。                                                                                 |
| 5   | 小茗同學（2026-07-12 rawB） | 簡體搜尋結果把中國品牌「小茗同學」混進台灣冷泡茶敘事——rawB agent 有抓到並標警，是正面示範；沒抓到就是把中國市場視角誤植成台灣脈絡。                                                                 |
| 6   | 柯智棠（2026-07-05）        | （給 orchestrator 自己看的）agent 全對、prompt 全對，orchestrator 收件後壓成 6KB 摘要存 scratchpad，raw 蒸發。收件第一動作 = verbatim 落檔 repo。                                                   |

**庫的維護**：新的研究病例先進 [LESSONS-INBOX](../semiont/LESSONS-INBOX.md) 走 distill，確認是新 pattern 才 append 本表（先 grep 本表＋REFLEXES，covered 就 bump 原條目——per feedback_lessons_dna_check_first）。

---

_v1.0 | 2026-07-12-135710-twmd-tea-panorama session — 誕生觸發：哲宇 callout「未來 subagent 回傳一定要完整所有來源…你要製作標準化的 sub agent 怎麼研究＋整合的更新」。姊妹改動：REWRITE-PIPELINE v7.10 Step 1.8-ter ＋ agent-report-health.py v3 溯源率 gate。_
