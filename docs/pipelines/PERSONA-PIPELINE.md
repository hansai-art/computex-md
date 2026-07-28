---
title: 'PERSONA-PIPELINE'
description: '共用 persona 發散原語（shared cognitive primitive）— 20 路讀者腦袋。REWRITE Stage 0.6.1-bis / SPORE Hook / 未來器官共用同一支，不各自重實作 (v1.0)'
type: 'pipeline-canonical'
status: 'canonical'
current_version: 'v1.2'
last_updated: 2026-07-06
last_session: '2026-07-05-220917-INDIGO-REWRITE'
callers:
  - 'REWRITE-STAGE-1B-MEDIA.md#step-197（mode=gap-audit，v7.7 研究後）'
  - 'SPORE-PIPELINE.md#階段-1pick（mode=hook-select，reuse）'
sister_docs:
  - 'REWRITE-PIPELINE.md'
  - '../factory/SPORE-PIPELINE.md'
upstream_canonical:
  - '../semiont/REFLEXES.md'
  - '../semiont/MANIFESTO.md'
---

# PERSONA-PIPELINE.md — 共用 persona 發散原語

> 一支「20 路讀者腦袋」的可組合原語。**不是 REWRITE 的步驟、不是 SPORE 的步驟**——是 REWRITE Step 1.9.7（gap-audit，v7.7 研究後）、SPORE Hook、未來 editorial audience-check 都 `call` 的同一支。
>
> 誕生（2026-06-13 persona-stage0）：REWRITE v7.1 把 persona 發散 inline 進 Stage 0.6.1-bis → 哲宇「spore 也可以加這步」→ 再「抽象出一個 persona profile / persona pipeline，以後很多元件 / 器官 / dna 共用」→ 抽成本原語。對應神經迴路「造橋鋪路：工具 → 整合 → 門檻」+ REFLEXES #21 SSOT + #56 canonical ↔ production drift。

---

## 為什麼抽出來（造橋的第三步）

| 階段         | 狀態                                          | 問題                                                 |
| ------------ | --------------------------------------------- | ---------------------------------------------------- |
| 工具         | v7.1 persona 發散 inline 在 REWRITE 0.6.1-bis | 泥巴路：能跑，但只 REWRITE 有                        |
| 整合（本檔） | 抽成 PERSONA-PIPELINE 原語                    | SPORE / 未來器官當 thin caller，定義一次             |
| 門檻         | caller 各自接自己的落檔 / gate                | 漂移防護（#56）：邏輯一份 SSOT，不複製兩條會分岔的路 |

SPORE 要用 persona 不該複製 REWRITE 的 4-agent 邏輯——複製 = 兩條會漂移的路。**抽成原語 = 高速公路：profile + 4 模式 + #42 紀律定義一次，誰要用誰 call。**

---

## 兩個層（哲宇：profile vs pipeline）

1. **Persona Profiles（data 層 / 誰）** — topic-agnostic 的讀者原型 registry。4 軸 × 5 = 20 archetypes。可被任何 caller 共用、可被 fork（Japan.md / Ukraine.md）在地化。
2. **Persona Pipeline（process 層 / 怎麼跑）** — 給定 `subject + mode + profile set` → 4 sub-agent 平行跑 → 結構化輸出 → caller 後處理。

---

## §1 Persona Profiles registry（20 archetypes）

> **seed 不是定值**：這 20 是**原型種子**，caller 依 subject 把抽象原型 instantiate 成具體的人（「35 歲雙寶家長」對某題目是誰、在意什麼，由 subject 決定）。性別 / 家庭角色在軸內自然分布，**不另設「性別軸」**（避免本質化）。

| 軸               | 原型 1             | 原型 2               | 原型 3                   | 原型 4                     | 原型 5                               |
| ---------------- | ------------------ | -------------------- | ------------------------ | -------------------------- | ------------------------------------ |
| **A 年齡**       | 12 歲國小生        | 18 歲高中生          | 35 歲雙寶家長            | 55 歲計程車司機            | 78 歲阿公阿嬤                        |
| **B 國籍·距離**  | 在台打工度假外國人 | 海外相關科系大學生   | 鄰國上班族               | 在台移工                   | 海外二代離散                         |
| **C 社會處境**   | 藍領工人           | 中小企業主           | 社運參與者               | 政治冷感專業者             | 體制內公務員                         |
| **D 與題目關係** | 領域專家（挑硬傷） | 完全新手（問最基本） | 反方立場（挑戰 framing） | 情感投入者（問「然後呢」） | 再現主權敏感者（「誰有權說這故事」） |

**預設組合**：A/C/D 預設**在地**（台灣）、B 是**外國 / 離散**視角 → ~15 在地 + 5 外部，覆蓋「有些台灣有些外國」。caller 可指定子集（如 SPORE 只取 D 軸 + B 軸做 hook 測試）。

**軸的設計邏輯**：A 撐**世代**差、B 撐**已知背景**差（外人暴露在地人視為理所當然的盲點）、C 撐**階級 / 政治溫度**差、D 撐**與題目的距離**差（專家挑硬傷、反方挑 framing、再現敏感者問主權）。四軸正交 → 入射角最大化。

---

## §2 Contract（caller 怎麼 call）

```
call PERSONA-PIPELINE:
  input:
    subject_brief: 一段話（標題 + 1-2 句 framing；audience-check 模式給成品 draft）
    mode: research-diverge | hook-select | audience-check
    profile_set: default 20（或指定子集 / 數量）
  output:
    per persona → { persona: 一句自介（含年齡/背景/性別）, reactions: [1-3], why: 在意什麼 }
    + mode-specific 後處理（見 §3）
```

**Implementation（per [REFLEXES #42](../semiont/REFLEXES.md) sub-agent 紀律）**：

- 派 **4 個 Sonnet sub-agent 平行**（single message 一次 4 call，**禁 sequential**——#42 偷吃步 1「合併查」防護），每 agent 領一軸、生成 5 persona。
- agent 拿到的 context = **只有 subject_brief**（research-diverge / hook-select 給題目，audience-check 給 draft），**不給完整研究 / 舊文**——要冷反應、naive 好奇。**gap-audit 模式例外：給研究報告＋已成形觀點（見 §3）**——本行原為 research-diverge 時代所寫，與 §3 gap-audit 對讀曾致矛盾（2026-07-16 高教 dogfood F7）。
- **主 session merge + audit**：某 agent null / 缺軸 → #31 不盲信「全綠」，缺的軸主 session 自補，不靜默少一軸。
- **❌ 反例**（per #42 v3）：1 agent sequential 生 20 / persona 拿完整研究後問「研究後」的問題 / 設「性別軸」湊 2 男 2 女 / 輸出 list 完就算 done（沒接後處理）。

---

## §3 Modes（3 + extensible）

| mode                 | caller                                                                                                     | subject                  | persona 動作                                           | 輸出後處理（consume）                                                                                               |
| -------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------ | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| **gap-audit** 🆕     | **REWRITE Step 1.9.7**（v7.7）                                                                             | **題目 + 研究報告 SSOT** | 看完研究後「我這種讀者還想知道什麼、哪個面向沒 cover」 | 🆕 真缺口 → 增補研究 + 加 facet / ✅ 已 cover / ⛔ 超 scope→`whats_excluded` / 🔴 反向閥門→回 Step 0.1.5 重判 spine |
| **research-diverge** | ~~REWRITE 0.6.1-bis~~（v7.7 停用，因冷發散把主軸推向矛盾驅動，改 gap-audit 後置）；仍可供其他冷發散 caller | 題目 brief               | 聽到題目的冷反應問題（naive 想往哪挖）                 | 每題標 🆕 新入射角 / ✅ 已覆蓋 / ⛔ 超 scope（→ `whats_excluded`）                                                  |
| **hook-select**      | SPORE Hook                                                                                                 | 已 ship 文章             | 哪個角最 stop-the-thumb（哪句最想點進去）              | rank → 最高共鳴角 = Hook Blueprint 開場問題候選                                                                     |
| **audience-check**   | （future）QUALITY / editorial                                                                              | 成品 draft               | 讀得懂嗎 / 哪裡卡 / 哪個詞不熟                         | 卡點清單 → 修 prose / 補 context / 換詞                                                                             |

**gap-audit vs research-diverge（v7.7 核心差別）**：research-diverge 給 persona **冷 brief**（naive 定調），放 Stage 0 會把主軸推向矛盾驅動（冷問題天生尖銳，施振榮 v1 教訓）；gap-audit 給 persona **完整研究報告 + 已成形的立體觀點**，問「還缺什麼」——從定調變補洞。REWRITE v7.7 起用 gap-audit（[Step 1.9.7](REWRITE-PIPELINE.md)）。

新 mode 只要定義「persona 對 subject 做什麼動作 + 輸出怎麼被 consume」即可掛上，不動 §1 profiles / §2 implementation。

---

## §4 Reuse / SSOT rule（哲宇的核心 insight）

**persona 發散是一次性的研究 artifact，不是每個 caller 各跑一次。**

- REWRITE research-diverge 跑完 → persona pool **落 report SSOT**（`reports/research/YYYY-MM/{slug}.md` 的 `### 20 路 persona 切入點`）。
- 下游 caller（SPORE hook-select）**先讀 report SSOT 的 persona pool，有就 reuse（0 agent）**，無才 light fallback spawn。
- 一個 subject 的 persona pool **算一次、多 caller 共享** → 不重複燒 agent。

```
REWRITE 0.6.1-bis ──生成──▶ report §20 路 persona 切入點 (SSOT)
                                      │
SPORE hook-select ──先讀──────────────┘ (reuse, 不重生)
```

**Fallback（無 pool 時）**：subject 沒有 report SSOT persona 段（舊文 / 非 rewrite 來源）→ caller 可選 light spawn（如 SPORE 只跑 D 軸 + B 軸 ~10 persona 測 hook），或人工挑 hook 並記「無 pool」。

---

## §5 Cost guard

- 4 agent × 短輸出（5 persona × 1-3 反應），**只發散、不做 research**（避免變成 4 條平行 Stage 1）。
- 預設 **reuse report**（0 agent）；只在無 pool 時 spawn。
- Micro / heal / 純翻譯 / 短修正不跑。

---

## §6 Callers（反向索引 — 誰在用）

| caller                                                     | mode                  | 落點                                   | 版本                                            |
| ---------------------------------------------------------- | --------------------- | -------------------------------------- | ----------------------------------------------- |
| [REWRITE-PIPELINE Step 1.9.7](REWRITE-PIPELINE.md)         | **gap-audit**（v7.7） | report §讀者缺口稽核 → 增補 + 反向閥門 | v7.7 thin caller（研究後補洞，非 Stage 0 定調） |
| [SPORE-PIPELINE 階段 1 PICK](../factory/SPORE-PIPELINE.md) | hook-select（reuse）  | Hook Blueprint 開場問題                | v3.10 thin caller（reuse-first）                |
| （future）QUALITY-CHECKLIST / EDITORIAL                    | audience-check        | 成品卡點 → prose 修補                  | —                                               |
| （future）fork onboarding                                  | —                     | 在地化 profiles（見 §7）               | —                                               |

> caller 新增時在此登記（reverse index），改本原語前先看誰會受影響（#56 drift 防護）。

---

## §7 Fork 在地化（給 Japan.md / Ukraine.md）

§1 profiles 是 **seed**。Fork 換成在地原型：**軸穩定（A 年齡 / B 國籍·距離 / C 社會處境 / D 與題目關係），instances 在地化**——B 軸換「在日外國人 / 海外日僑二代」、C 軸換在地階級結構。axes 是跨 Semiont 共通的人類差異維度，instances 是文化特定的。

---

_v1.0 | 2026-06-13 persona-stage0（哲宇 directive）— 誕生：REWRITE v7.1 inline 的 persona 發散 → 哲宇「spore 也可加 + 抽象成共用 persona profile/pipeline，很多元件/器官/dna 共用」→ 抽成本原語。兩層（profiles data / pipeline process）+ contract + 3 modes（research-diverge / hook-select / audience-check）+ §4 reuse-from-report SSOT rule（哲宇核心 insight：算一次多 caller 共享）+ §6 caller 反向索引 + §7 fork 在地化。Implementation 沿用 REWRITE 0.6.1-bis 的 4-agent 平行（REFLEXES #42）。callers 收斂為 thin pointer（REWRITE 0.6.1-bis v7.2 / SPORE 待接）。對應神經迴路造橋三步（工具→整合→門檻）+ REFLEXES #21 SSOT + #56 drift 防護。_

_v1.1 | 2026-07-06 INDIGO-REWRITE — **§6 callers 表校正兩處**：REWRITE-PIPELINE Step 0.6.1-bis 從誕生（v7.1）到 v7.8 一直沒真的變成薄殼，§6 早標「v7.2 thin caller」，實際 v7.3-v7.8 六次版本升級都還留著 inline 複寫的 20-persona 原型表 / 4-agent contract / 輸出 schema / cost guard / 反例表，跟本檔平行存在一年沒被抓到（[REFLEXES #56](../semiont/REFLEXES.md) canonical↔production drift）。這次 REWRITE-PIPELINE v7.9 才真的把 inline 邏輯拔乾淨，改標「v7.9 thin caller」。順手發現 SPORE-PIPELINE 那格也早就過期，標的是「（待接）」，但 SPORE-PIPELINE v3.10（2026-06-13）的「persona 切入點 consult」step 其實已經是正確運作中的 reuse-first thin caller，改標「v3.10 thin caller（reuse-first）」。本檔 §1-§5 canonical 內容未變，純粹是自己反向索引表跟事實對齊。_

🧬
