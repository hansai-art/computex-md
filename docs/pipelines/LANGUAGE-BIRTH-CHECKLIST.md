---
title: 'LANGUAGE-BIRTH-CHECKLIST'
description: '新語言誕生 pipeline — 選址→scaffold→模型校準→P0 內容批→介面與路由→啟用 flip→出生後驗證 7 stage + 四層完整度 hard gate（v2.2）'
type: 'pipeline-canonical'
status: 'canonical'
current_version: 'v2.2'
last_updated: 2026-07-19
last_session: '2026-07-19（讀者揭露 es/fr/ja/ko 68 檔「宣稱已譯實為英文」— Stage 3 QA gate 三道升四道，補 script-presence-check + translate.py 即時 hard gate）'
sister_docs:
  - 'TRANSLATION-PIPELINE.md'
  - 'SQUEEZE-MODELS-MAX-PIPELINE.md'
  - 'EVOLVE-PIPELINE.md'
upstream_canonical:
  - '../semiont/ANATOMY.md'
  - '../semiont/MANIFESTO.md'
---

# LANGUAGE-BIRTH-CHECKLIST — 新語言誕生 pipeline

> 相關：[EVOLVE-PIPELINE.md](EVOLVE-PIPELINE.md)（選址）| [SQUEEZE-MODELS-MAX-PIPELINE.md](SQUEEZE-MODELS-MAX-PIPELINE.md)（翻譯 cascade + 模型驗證）| [TRANSLATION-PIPELINE.md](TRANSLATION-PIPELINE.md)（單篇翻譯）| [ANATOMY.md §語言器官](../semiont/ANATOMY.md)
>
> 一個新語言（vi / id / pt / hi / ...）從「候選」到「活著」的完整出生 SOP。**語言器官有四層結構（骨架→頁面→Hub→文章），只量文章數 = 只量一維**——這是 v1.0 從 ko 出生學到的核心教訓，v2.0 原封保留，並把出生流程對齊 2026-07 的身體（語言註冊表 SSOT / babel cascade v4.4 / hreflang 註冊表化 / embeddings nightly）。

---

## 🗺️ ASCII spine

```
╭──────────────────────────────────────────────────────────────────────────╮
│      LANGUAGE-BIRTH — 新語言誕生 7 stage                                 │
│                                                                          │
│   🧭 核心紀律                                                            │
│            ├── 四層完整度（骨架→頁面→Hub→文章），缺一層 = 半殘           │
│            ├── 主權前測先於品質測（refusal test 排在 cost/quality 前）   │
│            └── 計數不寫死：語言清單一律從 languages.ts 註冊表 derive     │
│                                                                          │
│   Stage 0: 選址 ──→ EVOLVE 語言層（哪個語言值得出生？）                  │
│            └── 三源交叉＋人口槓桿＋主權缺口＋台灣連結＋可行性五維        │
│              ↳ Hard gate: ≥2 源確認 + 啟動排程過 OBSERVER-QUEUE          │
│                                                                          │
│   Stage 1: 註冊 scaffold ──→ enabled: false（決策結構化，不開路由）      │
│            └── languages.ts + .mjs 兩檔 + sync check + astro sync 驗證   │
│                                                                          │
│   ═══ 以下需哲宇啟動拍板（>50 檔重構 + 算力紅線）═══                    │
│                                                                          │
│   Stage 2: 模型校準 ──→ refusal 前測 + ratio band                        │
│            ├── SQUEEZE §驗證 SOP：4 篇校準集 × 新語                      │
│            └── zh→{lang} ratio band 從 ≥10 篇樣本校準                    │
│              ↳ Hard gate: 校準完成才准 batch                             │
│                                                                          │
│   Stage 3: P0 內容批 ──→ 首頁接觸點 + 該市場 SC 熱點 ~50 篇              │
│            └── babel cascade（SQUEEZE v4.4）+ 10% 抽檢                   │
│              ↳ Hard gate: translatedFrom + sourceCommitSha 全齊          │
│                                                                          │
│   Stage 4: 介面與路由 ──→ UI bundle + src/pages/{lang}/                  │
│            ├── src/i18n/ 各 bundle 加 {lang} block（key 數對齊 zh）      │
│            └── 路由目錄複製（結構債：待去複製化）                        │
│              ↳ Hard gate: per-bundle key 數 == zh key 數                 │
│                                                                          │
│   Stage 5: 啟用 flip ──→ enabled: true（一行）                           │
│            └── hreflang/sitemap/search/embeddings/dashboard 自動跟上     │
│              ↳ Hard gate: build 全綠 + cross-lang audit                  │
│                                                                          │
│   Stage 6: 出生後驗證 ──→ 四層完整度 + EXP 註冊 + 對外同步               │
│            └── UNKNOWNS 預註冊 SC CTR 目標（帶 due_date）                │
│              ↳ Hard gate: 四層全過才算「出生完成」                       │
╰──────────────────────────────────────────────────────────────────────────╯
```

---

## 🚦 Hard Gate Inventory

| Gate                    | 觸發 stage | 條件                  | 工具 / 判準                                       | 不過 = ?                  |
| ----------------------- | ---------- | --------------------- | ------------------------------------------------- | ------------------------- |
| 三源 ≥2 源確認          | Stage 0    | 候選語言              | GA + SC + CF 國家維度（REFLEXES #4）              | 不升 candidate            |
| 啟動排程過佇列          | Stage 0    | >50 檔重構 + 算力紅線 | OBSERVER-QUEUE 待決項，🔒 等真人                  | 停在 scaffold             |
| 註冊表雙檔 sync         | Stage 1    | commit 前             | `check-language-registry-sync.sh`（pre-commit）   | 修到一致                  |
| 空 collection 不炸      | Stage 1    | scaffold 後           | `npx astro sync` + ENABLED 數不變                 | 回滾 scaffold             |
| 模型 refusal 前測       | Stage 2    | batch 前              | SQUEEZE §驗證 SOP score ≥ 7（4 篇校準集）         | 換 model / 調 cascade     |
| ratio band 校準         | Stage 2    | batch 前              | ≥10 篇樣本 → `translation-ratio-check.sh` 加 band | 摘要式翻譯 silent 流入    |
| translatedFrom 全齊     | Stage 3    | 每篇翻譯              | pre-commit 孤兒防護                               | 孤兒風險                  |
| P0 批 10% 抽檢          | Stage 3    | batch 後              | 人讀完成品（每 10 篇 ≥ 1）                        | AI Slop 規模化            |
| UI key 數對齊 zh        | Stage 4    | flip 前               | 下方 §驗證指令 per-bundle 對賬                    | 頁面層空洞（ko 教訓重演） |
| build 全綠 + cross-lang | Stage 5    | flip 後               | `npm run build` + `cross-lang-audit.py`           | 回滾 flip                 |
| 四層完整度              | Stage 6    | 出生宣告前            | 下方 §四層完整度檢查                              | 「宣稱完成但半完成」      |
| 出生 EXP 註冊           | Stage 6    | 出生宣告時            | UNKNOWNS §可證偽實驗（帶 `due_date:` 機械檢查）   | 出生效果永遠沒人回頭驗    |

---

## ⚠️ Top 5 最常忘的 step

1. **UI 頁面層空洞** — ko 出生 24 小時後才發現 8 個 i18n 頁面檔全空，韓國讀者點 /ko/about 看到英文；文章數量健康不代表語言器官健康（v1.0 誕生原因，永不過期）
2. **ratio band 沒校準就 batch** — AI 翻譯的預設行為是摘要；沒有 zh→{新語} 的 ratio band，TRUNCATED 翻譯會 silent 流入且無尺可攔
3. **refusal 前測沒跑** — cloud free tier 對 Taiwan-sensitive 主題約 20% refuse 是 PRC content policy 指紋；不前測就 batch，sovereignty 最重要的 20% 會缺口在最沉默的位置（MANIFESTO §主權的巴別塔）
4. **感知系統不會自動「認識」新語言** — 神經迴路老教訓；2026-07 現況多數面已從註冊表 derive（search / embeddings / dashboard / hreflang），但 flip 後仍要逐面驗證，不要信「應該會自動」（REFLEXES #82 proxy signal）
5. **自我描述落後身體** — LANGUAGE-STATUS.md / README 語言徽章 / CONTRIBUTING 忘了同步（本檔 v1.0 自己就示範了這個病：躺了三個月沒跟上註冊表時代，直到 2026-07-18 選址才發現殭屍步驟）

---

## 跨檔案職責分工

| 檔案                                                             | 範圍                                                                     |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **本檔**                                                         | 新語言出生 7 stage SOP + 四層完整度 gate                                 |
| [EVOLVE-PIPELINE.md](EVOLVE-PIPELINE.md)                         | Stage 0 選址方法論（三源交叉；語言層評分見 2026-07-18 報告 worked case） |
| [SQUEEZE-MODELS-MAX-PIPELINE.md](SQUEEZE-MODELS-MAX-PIPELINE.md) | Stage 2-3 翻譯 cascade（Tier 0-5）+ 模型驗證 SOP                         |
| [TRANSLATION-PIPELINE.md](TRANSLATION-PIPELINE.md)               | 單篇翻譯品質規範（活語言的日常）                                         |
| [`src/config/languages.ts`](../../src/config/languages.ts)       | 語言註冊表 SSOT（+ `.mjs` mirror）                                       |
| [LANGUAGE-STATUS.md](../community/LANGUAGE-STATUS.md)            | 社群入口（contributor 看的狀態表；本檔是內部 SOP）                       |

**Worked case（第一次完整 Stage 0-1）**：[reports/evolve-2026-07-18-language-branches.md](../../reports/evolve-2026-07-18-language-branches.md) — vi/id/pt/hi 選址 + scaffold，含五維評分表與落選理由。

---

## Stage 0 — 選址（EVOLVE 語言層）

哪個語言值得出生，用數據回答，走 [EVOLVE-PIPELINE](EVOLVE-PIPELINE.md) 核心紀律的語言層變體：

- **三源交叉**：GA（誰來了）＋ SC 國家維度（誰想來但沒來：高曝光低 CTR 且無對應語言 = 語言層缺口）＋ CF（誰在邊緣讀我）。≥2 源確認才升 candidate；假流量過濾照 EVOLVE v2.0（bot 指紋：每人頁數異常）。
- **五維評分**（2026-07-18 建立，權重可校準）：需求訊號 0.30 / 人口槓桿 0.25（Ethnologue 總使用者）/ 主權缺口 0.20（該語言資訊圈的 PRC 敘事滲透度）/ 台灣連結 0.15（新住民、移工、戰略關係）/ 可行性 0.10（書寫方向、模型支援、既有 playbook 可複用度）。
- **文章層進化分數公式不硬套**（會混維度，OBSERVER-QUEUE #16 同型病）。
- 輸出：`reports/evolve-{date}-language-branches.md` 型報告 + 落選者記錄在案 + 啟動排程進 OBSERVER-QUEUE（🔒 >50 檔重構 + 算力經費）。

## Stage 1 — 註冊 scaffold（enabled: false）

把選址決策結構化進 SSOT，不開任何路由、不改使用者可見行為：

- [ ] [`src/config/languages.ts`](../../src/config/languages.ts) + `.mjs` 各加一筆 `enabled: false`，notes 寫選定日期＋一句理由＋報告 pointer
- [ ] `bash scripts/tools/check-language-registry-sync.sh` 過
- [ ] `npx astro sync` 過（content collections 對空語言目錄不炸）＋ ENABLED 語言數不變
- [ ] 此時起 `knowledge/{lang}/` 接受 contributor 翻譯 PR（進資料層，無路由——原 preview 模式）

## Stage 2 — 模型校準（啟動拍板後）

**主權前測先於品質測**。對每個新語言：

- [ ] 跑 [SQUEEZE §驗證 SOP](SQUEEZE-MODELS-MAX-PIPELINE.md) 的 4 篇校準集（中性技術 / 政治人物 / 文化宗教 / sovereignty），對 cascade 現役 Tier 1-2 model + 本地捕手各測一輪，score ≥ 7 才進 production cascade；refusal pattern 記進 `_refusal-cache.json`
- [ ] 從 ≥10 篇樣本校準 zh→{lang} ratio band（防摘要式翻譯；參考值：zh→en 0.80-1.30 / zh→ja 0.70-1.10 / zh→es·fr 2.0-4.0，新語言實測定案），寫進 `translation-ratio-check.sh` 與 lang-sync 狀態機
- [ ] 非拉丁書寫系統（如 hi 天城文）加渲染驗證：字型 fallback、行高、`viz-shot.mjs` 抽 3 頁截圖人眼看

## Stage 3 — P0 內容批

- [ ] 選批：首頁接觸點（策展過最能代表台灣的文章）＋該語言市場 SC 熱點，約 50 篇
- [ ] 跑 babel cascade（[SQUEEZE v4.4](SQUEEZE-MODELS-MAX-PIPELINE.md)：Tier 0 diff-patch / Tier 1-2 cloud / 本地捕手 / fleet），每篇 frontmatter `translatedFrom` + `sourceCommitSha` 齊
- [ ] **算力雙軌**（v2.1，2026-07-18 實戰定型）：codex 池吃品質關鍵與大檔、本機 qwen 池吃長尾，cascade 互為 fallback（`codex,ollama` vs `ollama,codex`）——兩份 disjoint 輸入檔避免同檔互蓋。天城文等高 token 密度書寫系統給 codex 設 `CODEX_TIMEOUT=1200`（hi 大檔 600s 必 timeout）
- [ ] **Hub 層走直通 runner**：`scripts/tools/lang-sync/hub-translate.py <lang>`——⚠️ `_* Hub.md` 不在 `_translation-status.json` 索引（`_` 前綴被排除），`prepare-batch --input` 對它們一律 Skipping unknown，標準批次管線從不服務 Hub（es/fr 當年是手工，2026-07-18 才發現此結構洞）
- [ ] **wikilink 扁平化**：`flatten-translation-wikilinks.py --lang {lang} --apply`——翻譯模型把 `[[目標]]` 譯壞（`[[林義雄 (Lin Chi-hsiung)]]`／`[[semicondutores]]` 都不解析，wikilink-target 要求目標 == zh-TW slug）。神經迴路鐵律：譯文 wikilink 轉純文字。⚠️ 扁平**後**再跑 CJK 檢查——純漢字目標（Hub 相關文章清單）扁平後會暴露 CJK 進正文
- [ ] 10% 抽檢人讀完成品（生產量 ≥ 品質是 AI Slop 的定義）
- [ ] **四道語意 QA gate 全綠才進 Stage 5**（ratio gate 只擋長度，擋不住這四類語意錯）：
  1. `cjk-residue-check.py --lang {lang}`——codex 產融合殘字（phong杀）、**qwen 漏簡體/Hangul 片段**（连霸／野百合世代「白」→백），ratio gate 全穿
  2. **`geo-fidelity-check.py --lang {lang}`（主權關鍵）**——翻譯模型會**幻覺式地點遷移**：出生戰役發現 vi/taiwan-democratization 系統性把「台北」譯成「北京」（整篇民主化文 7 處，含「台北高雄市長」→「北京市長」、天安門對照段的台北學生→北京學生）。把台灣的事搬進中國是巴別塔最致命失效。flag 的每檔逐行對照 zh 源人審（合法天安門 vs 幻覺台北→北京）
  3. `article-health.py`（pre-commit 自動跑）——含 wikilink-target、frontmatter；譯文 lang 偵測靠 loader `_LANG_DIRS`（已 registry-derive，勿再寫死）
  4. **`person-fidelity-check.py --lang {lang}`（主權關鍵）**——翻譯模型會**政治人物張冠李戴**：出生戰役發現 蔣經國（1987 解嚴、1988 去世）被系統性譯成「Chiang Kai-shek」（1975 已死）跨四語、陳水扁（美麗島大審辯護律師）在 id 被譯成「Tsai Ing-wen」（當時還是學生）、賴清德（2025 現任）在 tsmc 被譯成「Tsai Ing-wen」。懂台灣史的讀者一眼看破。flag 逐處對照 zh 源（中正紀念堂等地標為合法 false positive）
  5. **`script-presence-check.py --lang {lang}`（主權關鍵，2026-07-19 誕生）**——翻譯模型會**整篇配合但用英文回答**（不是拒答，是「宣稱已譯」的 frontmatter + 語意流暢的英文本文，前四道 gate 全部穿——footnote 數對、frontmatter 合法、無漢字殘留、無地名/人名幻覺，因為它根本沒被判定為「翻譯」而是被判定為「英文原創」）。es/fr/ja/ko 累計查出 68 檔，4 篇（taiwan-generations／complex-life-festival／huang-shan-liao／psychological-warfare）四語同時中鏢，全是主權敏感題材（統戰／白色恐怖／心戰／認知作戰）。此 gate 已同時內嵌進 `translate.py` 即時 hard gate（`check_script_presence()`），新出生語言若有非拉丁字母（ja/ko/hi）或有特殊變音符號（fr/es/pt/vi）會自動擋；`id` 走功能詞比對。詳見 [reports/ja-fr-es-ko-english-leak-2026-07-19.md](../../reports/ja-fr-es-ko-english-leak-2026-07-19.md)

## Stage 4 — 介面與路由

- [ ] `src/i18n/` 各 bundle（以目錄實際檔案數為準，2026-07 為 17 檔）加 `{lang}` block：**跑產線儀器 `scripts/tools/lang-sync/ui-bundle-translate.py --file src/i18n/{f} --lang {lang} --backend codex --fallback ollama --apply`**（字串感知括號配對＋鍵序驗證＋esbuild 語法閘＋指南 TL;DR inline；2026-07-18 誕生，同檔四語序列跑避免並寫互蓋）＋母語者或高信心 model spot-check
- [ ] Key 數對齊驗證（防 ko 1,743 keys 空洞重演）——見下方 §驗證指令
- [ ] `src/pages/{lang}/` 路由目錄：現狀為複製既有語言目錄（以 `src/pages/en/` 實際內容為準）。**已知結構債**：每語一份實體目錄在 10 語時代不可維護，去複製化（動態 `[lang]` 路由或腳本化產生）是巴別塔結構進化項，評估紀錄在 2026-07-18 報告 §三個結構性進化項
- [ ] Header 語言切換、nav、`getLangSwitchPath`（LangMapRegistry uniform 2-step，加語言 = registry 一行）確認自動 derive

## Stage 5 — 啟用 flip

- [ ] `enabled: false` → `true`（兩檔），這是唯一的「出生開關」
- [ ] `npm run build` 全綠；`cross-lang-audit.py` 全站健檢無 critical
- [ ] 逐面驗證自動 derive 有真的跟上（不信「應該會自動」）：hreflang（註冊表驅動，2026-07-17 起）/ sitemap / 搜尋索引分片（`build-search-index.mjs` 吃 ENABLED）/ 語意索引（`build-embeddings.mjs` 吃 ENABLED，bge-m3 原生多語）/ dashboard 翻譯覆蓋（`generate-dashboard-data.js` 吃註冊表）/ 語言切換器
- [ ] 上線後 `check-url-contract.mjs` 對賬：對機器公告的 URL 沒有死鏈（hreflang 一萬三千條死鏈的教訓，2026-07-17）

## Stage 6 — 出生後驗證與對外同步

### 四層完整度檢查（v1.0 核心，永不過期）

- [ ] **第一層 骨架**：註冊表 entry + 路由存在 + dashboard 認識新語言
- [ ] **第二層 頁面**：全部 i18n bundle 的 `{lang}` block key 數對齊 zh，抽 3 頁人眼看非英文殘留
- [ ] **第三層 Hub**：分類 Hub 頁存在且有策展內容
- [ ] **第四層 文章**：P0 批上線 + 過 ratio gate + 進 TRANSLATION-PIPELINE 日常流程

### 出生 EXP 與對外

- [ ] UNKNOWNS §可證偽實驗 預註冊（帶 `due_date:`，dashboard-alerts 機械檢查）：該市場 SC CTR 從基線 → 目標值的 60 天預測＋反駁條件（worked case：EXP-vi 0.5%→≥2% / EXP-pt clicks 5→≥50，見 2026-07-18 報告）
- [ ] [LANGUAGE-STATUS.md](../community/LANGUAGE-STATUS.md) / README 語言徽章 / CONTRIBUTING 同步
- [ ] CONSCIOUSNESS §里程碑 + structure-log 記出生事件

---

## 驗證指令

```bash
# 註冊表與衍生
bash scripts/tools/check-language-registry-sync.sh
node -e "import('./src/config/languages.mjs').then(m => console.log(m.ENABLED_LANGUAGE_CODES))"

# UI bundle key 數對齊（{lang} 換目標語言；每個 bundle 檔跑）
for f in src/i18n/*.ts; do
  zh=$(grep -c "'zh-TW\." "$f" 2>/dev/null || echo 0)
  new=$(grep -c "'{lang}\." "$f" 2>/dev/null || echo 0)
  [ "$zh" != "$new" ] && echo "⚠️ $f zh=$zh {lang}=$new"
done

# 內容層
python3 scripts/tools/lang-sync/status.py --json | jq '._meta.summary'
bash scripts/tools/translation-ratio-check.sh --all-{lang}
python3 scripts/tools/cross-lang-audit.py

# 路由與 URL 契約
ls src/pages/{lang}/
npm run check:url-contract
```

---

## 設計溯源

- **v1.0 誕生（2026-04-08）**：ko 出生 24 小時後發現文章翻了 24 篇但 8 個 i18n 頁面檔全空，韓國讀者點 /ko/about 看到英文 → 四層完整度概念誕生，緊急補 1,743 keys
- **v2.0 誕生（2026-07-18）**：vi/id/pt/hi 選址 session 盤點巴別塔現狀，發現本檔與身體脫節三個月量級——`scripts/i18n-mapping.json` 步驟已是殭屍（僅 scripts/README 提及，無消費者）、「`generate-dashboard-data.js` 認識新語言」步驟已被註冊表 derive 取代（2026-04-14 η 重構）、且完全缺 Stage 0 選址 / Stage 2 模型校準與 refusal 前測 / scaffold 慣例（es/fr 都走過 `enabled: false` 先行但從未 canonical 化）。教訓自我示範了 Top 5 第 5 條：出生 SOP 自己也會落後身體，**每次新語言出生前先健檢本檔**

---

_v2.1 | 2026-07-18 出生戰役 — vi/id/pt/hi 首次全程 dogfood 回寫：Stage 3 收算力雙軌定型＋Hub 直通 runner（`_` 前綴不在 status 索引的結構洞）＋CJK 殘留 QA gate（codex 融合殘字與 qwen 簡體滲出兩型）；Stage 4 UI 產線儀器化（ui-bundle-translate.py）。完整實錄：[reports/language-birth-2026-07-18.md](../../reports/language-birth-2026-07-18.md)\_
_v2.0 | 2026-07-18 115441-manual — 全檔重寫對齊註冊表時代：7 stage（選址→scaffold→校準→P0 批→介面路由→flip→出生後驗證）+ Hard Gate Inventory + 主權前測紀律 + 殭屍步驟清除。觸發：哲宇「紀錄經驗＋進化整個新語言誕生＋支援的過程跟完整需要執行的 pipeline 跟 dna」_
_v1.0 | 2026-04-08 γ — ko 誕生教訓：語言器官四層結構，只量文章數 = 只量一維_
