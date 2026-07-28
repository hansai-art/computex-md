---
title: 'REWRITE-STAGE-2B-ROOM-PROJECTION'
description: 'REWRITE v9 stage contract — Step 2.0-R 投影編輯室：三席分席對抗（結構/減法/炎上）＋攻防輪＋主編裁決'
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

# Stage 2B contract — 投影編輯室（Step 2.0-R，乾淨 context 分席對抗）

> **本檔是 REWRITE-PIPELINE v9.0 的 stage contract**：一個執行者（主 session、sub-agent、
> 或任何 context 有限的 model）只讀本檔＋本檔 INPUTS 宣告的檔案，就能執行本 stage。
> 派發路由與全 pipeline spine 在 [REWRITE-PIPELINE.md](REWRITE-PIPELINE.md)（薄索引）。
> 內文自 v8.0 主檔 verbatim 搬移（原行號 RP v8.0 L1389-1413 + L1474-1486），歷史敘事與教訓保留在文內。

## 執行卡

|                  |                                                                                                                                               |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **職責**         | 投影後（2.0-R：結構/減法/炎上三席）與正文後（2.5-R：結構主編/論點兌現二席）乾淨 context 分席審，主編合成裁決                                  |
| **執行者**       | seats ＝ parallel Sonnet sub-agent（prompt 一律 [EDITORIAL-ROOM-PROMPTS.md](EDITORIAL-ROOM-PROMPTS.md) 填槽，禁即興）；**主編永遠主 session** |
| **INPUTS**       | 2.0-R：投影藍圖＋research report（唯讀）；2.5-R：投影藍圖＋staging 正文。**禁止輸入**：舊文全文/寫作閒聊 context                              |
| **OUTPUTS**      | `reports/editorial-room/{slug}-projection-review.md` / `{slug}-prose-structure-review.md`（frontmatter room/seats/overall/rounds）            |
| **GATES**        | `python3 scripts/tools/editorial-room-health.py {review}`；overall=block → 回修（最多 2 輪全席，第 3 輪升級觀察者）；必改 ≤7                  |
| **context 預算** | 各席只吃填槽 prompt＋審查對象；主編收件合成                                                                                                   |

## 攻防輪（v1.1）

任一席 revise／block → 寫方答辯一輪（accept／defend，prompt 見
[EDITORIAL-ROOM-PROMPTS §攻防輪](EDITORIAL-ROOM-PROMPTS.md)），主編看攻防後才最終裁決；
review 檔加 `## 攻防` 段（challenge／defense／ruling 三欄——公開視覺化的爭議過程素材）。
規則 canonical：[EDITORIAL-ROOM §攻防輪](../editorial/EDITORIAL-ROOM.md)。

## AGENT PROMPT

三席 prompt 唯一來源：[EDITORIAL-ROOM-PROMPTS.md](EDITORIAL-ROOM-PROMPTS.md) §投影室（結構主編／減法主編／炎上倫理）＋§攻防輪。填槽派發，禁即興。

## 交付條件（stage 完成的定義）

- [ ] `reports/editorial-room/{slug}-projection-review.md` 落檔（room: projection，含各席 verdict＋必改 ≤7＋攻防段）
- [ ] `editorial-room-health.py {review}` exit 0
- [ ] overall=pass（block → 回修投影最多 2 輪，第 3 輪升級觀察者）

## HANDOFF（stage 完成時）

> stage 若委派 sub-agent，本五步由 orchestrator 於收件驗證後執行（agent 不碰共用看板——2026-07-16 高教 dogfood F6）。

1. OUTPUTS 全數落檔（顯式路徑，不存 scratchpad / tmp——REFLEXES #81）**並隨手 commit（只 stage 本 stage 產物路徑——可觀測性與跨 session 接力的底座，v9.5；勿 `git add -A`）**
2. GATES 逐條跑過，結果如實回報（sub-agent claim 是線索不是 oracle，REFLEXES #31）
3. 更新編輯台：`python3 scripts/core/generate-newsroom-data.py`（看板反映現況）
4. 回報格式：stage id ＋ 產物路徑清單 ＋ gate 結果 ＋ 未解疑慮（有就寫，不粉飾）
5. 下一棒：pass → REWRITE-STAGE-2C-WRITE.md；block → 回修投影（最多 2 輪）

---

### Step 2.0-R: 投影編輯室（v8.1）🏛️ — 編輯室對抗 (HARD depth)

> **canonical [EDITORIAL-ROOM.md](../editorial/EDITORIAL-ROOM.md) + [EDITORIAL-ROOM-PROMPTS.md](EDITORIAL-ROOM-PROMPTS.md)。**  
> 誕生：2026-07-15 哲宇「用 subagent 做編輯室對抗是結構」+ 陳睨「編輯台蓋回來／主編這隻手」；投影 5 題是作者自檢，編輯室是**乾淨 context 外部尺**。

**誰做**：3 個 parallel seat subagent（結構主編／減法主編／炎上倫理；Thin 可併減法→結構）+ **主 session 當主編**合成。**各席不准寫過藍圖的同一 context。**

**輸入（唯讀）**：`reports/article-projection/{slug}.md` + research report + PROJECTION §gate。  
**禁止輸入**：舊文全文、orchestrator 寫藍圖時的閒聊、writer draft。

**產物**：`reports/editorial-room/{slug}-projection-review.md`  
**儀器**：`python3 scripts/tools/editorial-room-health.py reports/editorial-room/{slug}-projection-review.md`

**Gate**：

| overall    | 動作                                           |
| ---------- | ---------------------------------------------- |
| **block**  | 回修投影藍圖；最多 2 輪全席；第 3 輪升級觀察者 |
| **revise** | 主編勾選 ≤7 必改；修後可只重跑 raise 席        |
| **pass**   | 才准派寫手                                     |

**depth EVOLVE / Fresh / A 級 = HARD。** standard 可 Thin（結構+炎上+主編）。Micro skip。

**Dogfood**：[reports/editorial-room/Shopping-Design-projection-review.md](../../reports/editorial-room/Shopping-Design-projection-review.md)（2026-07-15）。
