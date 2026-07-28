---
title: 'REWRITE-STAGE-2E-ROOM-PROSE'
description: 'REWRITE v9 stage contract — Step 2.5-R 正文結構編輯室：結構主編＋論點兌現二席對抗＋攻防輪'
type: 'pipeline-sub-canonical'
status: 'canonical'
current_version: 'v9.5'
last_updated: 2026-07-16
last_session: '2026-07-16-newsroom-orchestration（自 2-ROOM 合檔拆出，序列命名 2E）'
parent_canonical: 'REWRITE-PIPELINE.md'
upstream_canonical:
  - '../semiont/MANIFESTO.md'
  - '../editorial/EDITORIAL-ROOM.md'
---

# Stage 2E contract — 正文結構編輯室（Step 2.5-R）

> **本檔是 REWRITE-PIPELINE v9.0 的 stage contract**：執行者只讀本檔＋INPUTS 宣告的檔案。
> 派發路由在 [REWRITE-PIPELINE.md](REWRITE-PIPELINE.md)。內文自 v8.0 verbatim 搬移（原行號 L1474-1486）。

## 執行卡

|                  |                                                                                                                                                    |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **職責**         | 正文是否**執行**投影藍圖（全局功能兌現／論點中段被證明），非再發明結構                                                                             |
| **執行者**       | 2 parallel Sonnet seats（結構主編＋論點兌現，prompt 一律 [EDITORIAL-ROOM-PROMPTS.md](EDITORIAL-ROOM-PROMPTS.md) 填槽，禁即興）；主編永遠主 session |
| **INPUTS**       | 投影藍圖＋staging／canonical 正文。**禁止輸入**：research report 全份、寫作閒聊 context                                                            |
| **OUTPUTS**      | `reports/editorial-room/{slug}-prose-structure-review.md`（room: prose-structure＋`## 攻防` 段）                                                   |
| **GATES**        | `python3 scripts/tools/editorial-room-health.py {review}`；必改 ≤7；可與 Step 3.6 同 round 平行                                                    |
| **context 預算** | 各席只吃填槽 prompt＋藍圖＋正文                                                                                                                    |

## AGENT PROMPT

各席 prompt 唯一來源：[EDITORIAL-ROOM-PROMPTS.md](EDITORIAL-ROOM-PROMPTS.md) §正文結構室（結構主編／論點兌現）＋§攻防輪。禁即興增刪。

> **spawn 時機（v9.5）**：本站席位由大驗證輪一次平行派齊（與 3.6.1 verifier、3.7 探針同輪，
> 編排 canonical 在 [REWRITE-STAGE-3-VERIFY §Stage 3 收驗編排](REWRITE-STAGE-3-VERIFY.md)）。
> 席位讀什麼、審什麼不變——本 contract 對席位執行者仍然自足。

## 攻防輪（v1.1）

任一席 revise／block → 寫方答辯一輪（規則 canonical：[EDITORIAL-ROOM §攻防輪](../editorial/EDITORIAL-ROOM.md)），主編看攻防後裁決，review 檔記 `## 攻防` 段。

## 交付條件（stage 完成的定義）

- [ ] `reports/editorial-room/{slug}-prose-structure-review.md` 落檔（room: prose-structure，含各席 verdict＋必改 ≤7＋攻防段）
- [ ] `editorial-room-health.py {review}` exit 0
- [ ] overall=pass（revise → 修後可只重跑曾 raise 的席）

## HANDOFF（stage 完成時）

> stage 若委派 sub-agent，本五步由 orchestrator 於收件驗證後執行（agent 不碰共用看板——2026-07-16 高教 dogfood F6）。

1. OUTPUTS 全數落檔（顯式路徑，不存 scratchpad / tmp——REFLEXES #81）**並隨手 commit（只 stage 本 stage 產物路徑——可觀測性與跨 session 接力的底座，v9.5；勿 `git add -A`）**
2. GATES 逐條跑過，結果如實回報（sub-agent claim 是線索不是 oracle，REFLEXES #31）
3. 更新編輯台：`python3 scripts/core/generate-newsroom-data.py`
4. 回報格式：stage id ＋ 產物路徑清單 ＋ gate 結果 ＋ 未解疑慮
5. 下一棒：REWRITE-STAGE-3-VERIFY.md

---

### Step 2.5-R: 正文結構編輯室（v8.1）🏛️

> **canonical [EDITORIAL-ROOM.md](../editorial/EDITORIAL-ROOM.md)。** 與 [Step 3.6 成品總驗](REWRITE-STAGE-3-VERIFY.md#step-36-成品總驗三關assembled-product-verification--a-級大眾文-hard-) **分工**：本步查「有沒有執行藍圖／論點有沒有中段兌現」；3.6 查事實 atom／順稿／視覺。

**誰做**：2 parallel seats（正文結構主編 + 論點兌現）+ 主編合成。可與 3.6 fan-out **同 round 平行**。

**輸入**：投影藍圖 + staging／canonical 正文。  
**產物**：`reports/editorial-room/{slug}-prose-structure-review.md`  
**儀器**：`editorial-room-health.py`  
**Gate**：block/revise → 回修正文；pass → 進 Stage 3 其餘／與 3.6 合併主編清單後 ship。

**Dogfood**：[reports/editorial-room/Shopping-Design-prose-structure-review.md](../../reports/editorial-room/Shopping-Design-prose-structure-review.md)。
