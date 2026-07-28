---
title: 'EDITORIAL-ROOM'
description: '編輯室對抗 canonical — 投影後／正文後乾淨 context 分席審稿；主編裁決；結構外部尺'
type: 'editorial-canonical'
status: 'canonical'
current_version: 'v1.2'
last_updated: 2026-07-25
last_session: '2026-07-25-外送專法（v1.2 總編室加開閱讀節奏席＝REWRITE Step 3.6.2 順稿移交）'
sister_docs:
  - 'PROJECTION.md'
  - 'EDITORIAL.md'
  - '../pipelines/REWRITE-PIPELINE.md'
  - '../pipelines/EDITORIAL-ROOM-PROMPTS.md'
upstream_canonical:
  - 'PROJECTION.md'
  - '../pipelines/REWRITE-PIPELINE.md'
---

# EDITORIAL-ROOM — 編輯室對抗

> 投影藍圖與正文成品，各過一間**乾淨 context 編輯室**：角色分席、任務互斥、主編裁決。  
> 同一顆腦不准又寫又審。subagent claim 是線索（[REFLEXES #31](../semiont/REFLEXES.md)）。  
> 設計背景：[reports/editorial-room-adversarial-design-2026-07-15.md](../../reports/editorial-room-adversarial-design-2026-07-15.md)

---

## 一句話

**把「總編輯看完整桌材料、質疑、要改寫」變成可重跑的 subagent 結構**——不是社群彈幕 UI，不是假留言牆。

---

## 兩道關

```text
研究 report 合成
    ↓
Step 2.0 投影藍圖（orchestrator 寫）
    ↓
⭐ Step 2.0-R 投影編輯室  ← 本檔 §投影室
    ↓ pass
fresh writer 寫正文
    ↓
⭐ Step 2.5-R 正文結構編輯室（包 A）+ Step 3.6 成品總驗（包 B）
    ↓
主編合併 → ship
```

| 關         | REWRITE 錨點 | 輸入                              | 產物                                                      |
| ---------- | ------------ | --------------------------------- | --------------------------------------------------------- |
| 投影室     | Step 2.0-R   | research report + projection 藍圖 | `reports/editorial-room/{slug}-projection-review.md`      |
| 正文結構室 | Step 2.5-R   | staging/正文 + 同一投影藍圖       | `reports/editorial-room/{slug}-prose-structure-review.md` |
| 正文事實室 | Step 3.6     | 成品 + footnotes + report         | research §audit + 既有 3.6 流程                           |

---

## 材料桌（足跡契約）

| 允許                                        | 禁止                             |
| ------------------------------------------- | -------------------------------- |
| 研究 report、一手 URL、投影藍圖、正文 draft | 憑記憶發明「讀者留言／社群情緒」 |
| 新聞／部落格／論文／podcast（經 research）  | FB／IG 主爬當預設材料            |
| 標 single-source hedge 的口述               | 腦補現場補洞                     |

足跡不夠 → 席位 **block**，指令「回 Stage 1 補研」或「砍該 beat」，不准寫手腦補。

---

## 席位（1 agent = 1 角色，平行）

### 投影室（depth HARD；Thin = 結構 + 炎上 + 主編）

| 席                       | 任務                                                                                                                         | verdict               |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| **結構主編**             | 論點非摘要、骨架 shuffle、全局功能、面向巡禮；**H2 小標**能否還原主–述–賓／外行目錄可讀（[EDITORIAL §小標題](EDITORIAL.md)） | pass / revise / block |
| **減法主編**（可併結構） | 減法誠實、密度、CV 感                                                                                                        | pass / revise / block |
| **炎上／倫理**           | spine × 立體地愛 × 政治中立；contrarian 炎上                                                                                 | pass / revise / block |
| **主編**                 | 永遠主 session：收件、≤7 必改、裁決歧見                                                                                      | 合成最終報告          |

### 正文結構室（包 A）

| 席           | 任務                                             |
| ------------ | ------------------------------------------------ |
| **結構主編** | 正文是否**執行**藍圖全局功能？有無退回面向巡禮？ |
| **論點兌現** | 論點是否在中段被證明／複雜化，而非頭尾各喊一次？ |

### 正文事實室（包 B = 既有 3.6）

原子重驗 / 視覺同步——不重寫規則，pointer 到 [REWRITE Step 3.6](../pipelines/REWRITE-PIPELINE.md)。
**順稿已於 v1.2 移出本室**，改由總編室閱讀節奏席執行（見下 §總編室）。

> **結構席參考彈藥（2026-07-16 補）**：regex 抓不到、只能人判的 AI 腔一族——說教深度腔（「說到底／本質上」開頭的儀式句）、金句公式（「X 是 Y 的 Z」硬鑄格言）、假坦白鉤子（「說真的／老實說」報備式停頓）、戲劇性短句轟炸、刻意換詞循環、句長過勻。判準與正反例見 [speak-human-tw patterns #13/#17-20/#29](https://github.com/Raymondhou0917/speak-human-tw)（MIT，Raymond Hou）；per OBSERVER-QUEUE #15 決策精神，這些維持人判不造 plugin。特別警惕：#17-20 常是「去 AI 味時被誤加上去的假人味」。

---

## 報告模板（HARD schema）

```markdown
---
slug: { slug }
room: projection | prose-structure | chief
date: YYYY-MM-DD
seats: [structure, ethics, ...]
overall: pass | revise | block
rounds: 1
---

# 編輯室報告 — {room} — {slug}

## 各席

### {席名}

- verdict: pass | revise | block
- findings: （子彈，可執行）
- evidence: （指向藍圖 § 或 正文段落）

## 必改清單（≤ 7）

1. ...

## 建議不擋 ship（≤ 5）

1. ...

## 歧見與主編裁決

...

## 回修指令（給 orchestrator）

- [ ] 改投影 §…
- [ ] 回 Stage 1 補…
- [ ] 正文改 section…
```

儀器：`python3 scripts/tools/editorial-room-health.py reports/editorial-room/{file}.md`

---

## Gate

| overall    | 動作                                           |
| ---------- | ---------------------------------------------- |
| **block**  | 必回修；投影室最多 2 輪全席，第 3 輪升級觀察者 |
| **revise** | 主編勾選採納；修後可只重跑曾 raise 的席        |
| **pass**   | 准下一 stage                                   |

**depth EVOLVE / Fresh / A 級**：投影室 HARD。  
**standard / 短修**：Thin 或 skip。  
**Micro**：skip。

---

## Context 隔離（每席 prompt 鐵律）

見 [EDITORIAL-ROOM-PROMPTS.md](../pipelines/EDITORIAL-ROOM-PROMPTS.md)。摘要：

1. 你沒有寫過這份藍圖／正文
2. 只讀附件清單內的檔
3. 不准讀 knowledge 舊文（除非 brief 明示 EVOLVE 對照）
4. 不准重寫全文；只列必改
5. 輸出嚴格用報告模板

---

---

## 攻防輪（記者答辯，v1.1）

> 睨（2026-07-16 對話）：「像 GAN 一樣——編輯挑戰選點，記者捍衛選點的選擇價值觀。」
> 原分席審是單向（席位出意見 → 主編裁決）；攻防輪讓寫方有一次答辯，主編看攻防後才裁。

**觸發**：任一席 verdict 為 revise / block 時，寫方（投影作者或 writer——用**原 context 的
那顆腦**，這是它唯一合法的出場：捍衛自己的選點）對每條必改回覆一次：

- `accept`：接受修改（默認）
- `defend`：捍衛選點，附理由（為什麼這個切點／減法／結構是刻意的，犧牲了什麼換到什麼）

**上限一輪**（防迴圈燒 token）。主編看完攻防才出最終裁決；defend 被駁回就照改。

**報告落檔**：review 檔加 `## 攻防` 段，結構化三欄——這一段就是公開視覺化的爭議過程素材：

```markdown
## 攻防

### 必改 #N

- challenge:（席位原文）
- defense: accept ｜ defend——（寫方理由）
- ruling:（主編裁決一句話）
```

---

## 總編室（成品層對抗總評，v1.1）

> 睨：「AI 是線性深度推論，總編很常是**平行的漣漪出去**，並且檢驗連結關係和脈絡
> 如果構成一個主軸。」哲宇：「需要總編輯獨立一個 agent，用對抗性的方式把標題的
> 觀點性、整篇文章的脈絡做總評。」

**REWRITE 錨點**：Step 3.7（[REWRITE-STAGE-3-VERIFY.md](../pipelines/REWRITE-STAGE-3-VERIFY.md)
§總編對抗總評）。**觸發面**：A 級／大眾文 HARD，standard WARN。與 3.6 同 round 可平行。

**與 2.5-R 的分工**：2.5-R 驗「正文有沒有執行藍圖」（對圖施工驗收）；總編室**不看藍圖**，
只拿成品＋標題，模擬一個冷讀的總編：這篇作為報導成不成立。

**平行探針**（Sonnet ×5-6，各自乾淨 context，falsification prompt，禁讀藍圖與研究報告）：

| 探針                 | 問題                                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------------------------ |
| 門面兌現             | 標題／description 承諾的觀點，正文中段有沒有真的賺到？（門面句是最弱面——Shopping Design 摘要尾句教訓） |
| 逐段主軸服務         | 每個 H2 段落對全篇主軸的扣回；抓「京都研究」式前後無脈絡的斷裂段（吸菸室教訓）                         |
| H2 載體還原          | 每個小標過主–述–賓還原＋可指載體（[EDITORIAL §小標題](EDITORIAL.md)）                                  |
| 連結成網             | footnote／cross-link／延伸閱讀是否構成支撐主軸的網，還是裝飾                                           |
| **閱讀節奏**（v1.2） | 哪一節讀起來窒息？哪一節資料密到散文承載不住卻沒有視覺？外科手術的縫線疤在哪？                         |
| 立體地愛（條件）     | 政治敏感／人物題加開：MANIFESTO §13 檢驗                                                               |

> **閱讀節奏席為什麼一定要在這裡，不能留在主 session**（v1.2，2026-07-25 外送專法）：
> REWRITE Step 3.6.2 順稿寫了「外科手術疊幾輪之後縫線會留疤——成品從頭到尾重讀一次」，
> 但把它指派給主 session ＝ 指派給全場**唯一讀不了新鮮的那個讀者**。主 session 剛決定過
> 每一句話該長什麼樣，理由跟句子是一起生的，重讀時理由會先替句子辯護一次。
> **順稿需要的不是深 context，是沒有 context**。誕生事件：外送專法 ship 時所有閘門
> hard=0 warn=0，哲宇讀完 callout「文段太長／順暢感掉了／後段沒圖表」，三句都對。
> 完整診斷與門檻校準：[reports/design-prose-flow-station-2026-07-25.md](../../reports/design-prose-flow-station-2026-07-25.md)。

**匯流**：主編（永遠主 session）收六路探針，落
`reports/editorial-room/{slug}-chief-review.md`（`room: chief`），≤7 必改，同 gate 三態。

---

## 與其他機制邊界

| 機制              | 編輯室關係                    |
| ----------------- | ----------------------------- |
| PROJECTION 5 題   | 作者自檢；編輯室 = **外部尺** |
| persona gap-audit | 讀者缺口；不取代結構主編      |
| 3.6 verifier      | 正文事實包 B                  |
| FACTCHECK         | 事後／高流量；不取代          |

---

_v1.2 | 2026-07-25 — 總編室加開第六探針「閱讀節奏」；REWRITE Step 3.6.2 順稿從主 session 移交本席。觸發：外送專法 ship 時閘門全綠但哲宇冷讀 callout 段落牆與後段圖表空白，追因發現順稿被指派給全場唯一讀不了新鮮的讀者。_
_v1.1 | 2026-07-16 — 攻防輪（記者答辯一輪）＋總編室（成品層平行探針對抗總評）；睨 GAN 提案與「總編是平行漣漪」洞察落地。_
_v1.0 | 2026-07-15 — dogfood Shopping Design 投影／正文結構室。_
