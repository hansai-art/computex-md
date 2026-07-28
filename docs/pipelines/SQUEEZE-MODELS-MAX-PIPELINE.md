---
title: 'SQUEEZE-MODELS-MAX-PIPELINE'
description: '多語 batch sync 主流程 — priority schema P0/P1/P2/P2.5/P3 + Tier 0a Sonnet diff-patch + 4-tier cascade + Z0-Z6 stage spine + §義務鐵律推 100% + v4.4 對齊 translate.py v4.3（owl-alpha 移出 default / preflight 冷凍 / audit-quality.py 已存在）'
type: 'pipeline-canonical'
status: 'canonical'
current_version: 'v4.6'
last_updated: 2026-07-24
last_session: '2026-07-24 vortex（babel-dispatch 統一調度器 + 免費模型季度校準 + cjk-leak-check 兩個假陽性家族根治 + existence-aware redirects + salvage 工具）'
production_signal: 'scripts/tools/lang-sync/translate.py §DEFAULT_CASCADE_ID docstring（本檔 cascade 描述必須鏡射它；audit 時 diff 這兩處，REFLEXES #56 rule (a)）'
sister_docs:
  - 'TRANSLATION-PIPELINE.md'
  - 'DATA-REFRESH-PIPELINE.md'
upstream_canonical:
  - '../semiont/MANIFESTO.md'
  - '../semiont/DNA.md'
---

> **渦流模式 pointer（2026-07-27）**：觀察者驅動的持續迴圈（/goal＋每小時甦醒）
> 另有 canonical [BABEL-VORTEX-LOOP.md](BABEL-VORTEX-LOOP.md)——固定 benchmark
> 報告、三重巡檢、自動進化硬條款、薄殼 wake prompt contract。本檔管「怎麼翻」，
> 渦流檔管「怎麼持續運轉與進化」。

# 榨模型MAX — 多語 batch sync 主流程 v4.6

> **第一性原理**：用所有手邊免費 model 同時平行打、refusal 當作 first-class 結果記錄、最終跨批次統合補空缺，把單一 model 的天花板（rate limit / content policy / quality）拆成許多小天花板加起來逼近 100%。Tier 4 Local LLM 永不漏接 sovereignty-sensitive topics。
>
> v4.6（2026-07-24 vortex）：**統一調度器落地** — [`babel-dispatch.py`](../../scripts/tools/lang-sync/babel-dispatch.py) 把本地 GPU 節點與雲端免費模型收進同一個 worker pool（每 worker 綁一個 backend 端點、共享工作佇列、status-aware 跨引擎 dedupe、三重 gate、git-lock commit、迴圈到 stale=0 missing=0），取代 per-node 手寫 bash 迴圈。三個結構修正（相對 legacy dispatcher）：(1) `git add` 只加本輪驗證過的精確路徑，目錄級 add 會掃進並行引擎未 commit 的工作 (2) gate fail 對 HEAD 有舊版的檔案還原不刪除——**寧可 stale 也不要 missing**（配套 [`salvage-quarantined.py`](../../scripts/tools/lang-sync/salvage-quarantined.py) gate 驗證式還原歷史降級）(3) verify 前先 prettier 正規化對齊 commit hook 量測面。同日根治 `cjk-leak-check.py` 兩個假陽性家族（全形括號 gloss 豁免 + ja/ko marker 表的 的/了/一個/淘汰 + 引述 span 豁免）——此前 ja lane 在 gate 面前 100% 死路。免費模型季度校準：[`discover-free-models.py`](../../scripts/tools/lang-sync/discover-free-models.py) 自動探勘 + 校準，2026-07-24 通過 5 模型（nemotron-3-ultra-550b / gemma-4-31b / laguna-xs-2.1 / gpt-oss-20b / north-mini-code，結果 [reports/openrouter-free-calibration-2026-07-24.json](../../reports/openrouter-free-calibration-2026-07-24.json)）。站體層配套：轉址目標 existence-aware（[`resolve-redirect-targets.mjs`](../../scripts/core/resolve-redirect-targets.mjs)，quarantine churn 不再炸 CI）。
>
> v4.4（2026-07-05 五病根治）：對齊 translate.py v4.3 production 現實 — owl-alpha 移出 default cascade（6/10 silent 轉 paid）、preflight health-check + 6h 冷凍入 spine、audit-quality.py「待造」修正為已存在、frontmatter 加 `production_signal` 欄（REFLEXES #56 rule (a) 首次落地：本檔 cascade 描述的 SSOT 在 code，audit 時 diff 兩處）。觸發：dna-audit §4.3「#56 於自身觸發檔復發」。
>
> v4.2（2026-05-16）：Inventory recalibration — Hy3 已退役、gpt-oss-120b 升 Tier 2 已驗證、新候選佇列 (Llama-3.3-70b / Hermes-3-405b / Gemma-4-31b / Nemotron-3-Super-120B 等) 標記為「需 calibration」+ §驗證 SOP（標準 test set + scoring criteria）。Default cascade 改為 codex + gemini 雙 subscription Tier 1 priority。
>
> v4.0 設計理由：對齊 [REWRITE-PIPELINE v5.0](REWRITE-PIPELINE.md) + [MAINTAINER-PIPELINE v2.0](MAINTAINER-PIPELINE.md) spine restoration 範式。修補 v3.3 結構問題：(1) 缺 ASCII spine box-frame；(2) Hard Gate 散在 Z2/Z6 prose 無集中索引；(3) Top 5 最常忘沒提取。

---

## 🗺️ ASCII spine

```
╭──────────────────────────────────────────────────────────────────────────╮
│         SQUEEZE-MODELS-MAX 多語 batch sync — Z0-Z6 主流程                │
│                                                                          │
│   🧭 三軸設計原則                                                        │
│            ├── 軸一：跨模型平行（task dir per provider）                 │
│            ├── 軸二：try-catch first-class（refusal 是 result 不是 exc） │
│            └── 軸三：最後統合 + retry（aggregate 不是 throw away）       │
│                                                                          │
│   🪜 4-tier cascade（v4.4 = translate.py DEFAULT_CASCADE v4.3 鏡射）    │
│            ├── Tier 0a: Sonnet diff-patch（已存在翻譯漂移 ≤ 10 lines）   │
│            ├── Tier 0b: bump-source-sha.py（pure metadata refresh）      │
│            ├── Tier 1: codex (subscription) → gemini (subscription)      │
│            ├── Tier 2: gpt-oss-120b:free（owl-alpha 6/10 silent 轉 paid  │
│            │          已移出 default，顯式 --cascade override 才用）     │
│            ├── Tier 3: free fleet 驗證佇列 (Llama-3.3 / Hermes-3-405B…)  │
│            └── Tier 4: Ollama qwen3.6:35b（永不漏接；主權定位 pending    │
│                        決策 4，fleet 端 6/14 bench 後 gemma4-only）      │
│            ＋ preflight health-check（v4.3）：起跑 probe 各 backend，    │
│              死模型整 run 冷凍 6h，不讓 N 篇各自撞 timeout               │
│                                                                          │
│   ──── Z0-Z6 standard execution flow ──────────────────────              │
│                                                                          │
│   Z1: Pre-flight ──→ 6 step                                              │
│            ├── status.py / sync-translations / slug-map / prepare-batch  │
│            └── filter TBD-NEEDS-SLUG / snake-balance N groups            │
│              ↳ Hard gate: manifest 完整 + group balanced                 │
│                                                                          │
│   Z2: 跨模型平行 dispatch ──→ N task dir × M worker                      │
│            ├── Tier 1 主批 (codex / gemini subscription)                 │
│            ├── Tier 2 副批 (gpt-oss-120b:free；owl 已出 default)         │
│            └── Z2.1 Concurrency cap 3-5 / Z2.2 Cool-down ≥ 5-10 min      │
│              ↳ Hard gate: refusal detection / 40-byte stub purge         │
│                                                                          │
│   Z3: 增量 commit ──→ 每 ~50 fresh local commit（不 push）               │
│              ↳ Hard gate: pre-commit YAML / 0-byte purge                 │
│                                                                          │
│   Z4: 跨輪 retry ──→ still-missing → 下一 tier model                    │
│              ↳ 重複 Z2 → Z4 直到 still-missing == 0 OR 全 tier 試過      │
│                                                                          │
│   Z5: 最終統合 + 驗證 ──→ verify-batch.py 8 項全跑                       │
│              ↳ Hard gate: lang-sync status fresh ratio 達標              │
│                                                                          │
│   Z6: 抽樣品質 audit ──→ size-ratio scan + 人眼抽樣 N=max(10, 5%)        │
│              ↳ Hard gate: healthy ratio ≥ 90% 才能 ship                  │
│                                                                          │
│   ✅ Batch shipped (push after user approval)                            │
│                                                                          │
│   ──── 跨 pipeline boundary ─────────────────────────                   │
│   → 單篇 SOP / 跨 pipeline 觸發：TRANSLATION-PIPELINE.md                │
│   → 跨機器搬遷：SENSE-FETCHER-MIGRATION.md                              │
╰──────────────────────────────────────────────────────────────────────────╯
```

---

## 🚦 Hard Gate Inventory（一張表 audit 全 pipeline）

| Gate                            | 觸發 stage | 條件               | 工具                                                                                       | 不過 = ?                                                                      |
| ------------------------------- | ---------- | ------------------ | ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| 目標語言 canonical guide 內嵌   | Z2 prompt  | per backend prompt | backend prompt 必含 `docs/editorial/per-language/TRANSLATION-{lang}.md` §1-§6 table inline | sovereignty leak + 站內不一致                                                 |
| Manifest 完整                   | Z1         | dispatch 前        | `prepare-batch.py` output                                                                  | 不 dispatch                                                                   |
| Group snake-balance             | Z1         | dispatch 前        | manifest 內建                                                                              | 重 balance                                                                    |
| 40-byte refusal detection       | Z2         | per-article        | `output too small (40 bytes)` worker log                                                   | log ❌ + cleanup + 繼續                                                       |
| **輸出截斷偵測 (truncation)**   | Z2         | per-call           | `finish_reason == "length"` guard（max_tokens 32000）                                      | 不 save + 走 cascade retry                                                    |
| **🔴 腳註完整 (defs ≥ source)** | Z2 + Z5    | per-call + batch   | `openrouter-translate.py` 內建 + `verify-batch.py` [3b]（zh `[^n]:` count vs translation） | **不 save / 不 ship**（截斷靜默掉腳註 = 263 文去引用 root cause，2026-06-06） |
| null content refusal            | Z2         | per-article        | `result is None` guard                                                                     | log ❌ + 繼續                                                                 |
| HTTP 429 backoff                | Z2         | per-call           | 指數退避 3 retry                                                                           | 最後失敗 log ❌ + 繼續                                                        |
| YAML parse fail                 | Z2 + Z3    | per-article        | `yaml.safe_load(frontmatter_block)`                                                        | rm + retry queue                                                              |
| Concurrency cap 3-5 worker      | Z2.1       | initial dispatch   | manual + REFLEXES #45                                                                      | reduce concurrency                                                            |
| Cool-down ≥ 5-10 min            | Z2.2       | rate-limited 後    | REFLEXES #45                                                                               | 走 Tier-2 fallback                                                            |
| Pre-commit hook（YAML / 憑證）  | Z3         | per commit         | `.husky/pre-commit`                                                                        | 不 commit                                                                     |
| 不 push 中途                    | Z3         | 整個 batch round   | manual                                                                                     | abort push                                                                    |
| Destructive git ops 禁令        | 全程       | sub-agents alive   | REFLEXES #35                                                                               | abort op，走 worktree                                                         |
| `verify-batch.py` 9 項          | Z5         | 整個 batch         | `verify-batch.py`（含 [3b] 腳註完整 hard gate）                                            | 不 ship                                                                       |
| Size-ratio scan ≥ 0.5           | Z6         | 每篇新翻譯         | `audit-quality.py`（已存在 2026-05-13——本檔曾標「待造」八週，dna-audit 修正）              | flag + retry                                                                  |
| Healthy ratio ≥ 90%             | Z6         | sample audit       | random N = max(10, 5%)                                                                     | 回 Z4 retry                                                                   |
| `lang-sync status` fresh        | Z5         | ship 前            | `status.py`                                                                                | retry 直到達標                                                                |

---

## 🩺 健檢儀器（v4.5，2026-07-18 誕生）

```bash
python3 scripts/tools/lang-sync/babel-health.py          # 六維度：coverage/yaml/footnote/ratio/zombie/stub
python3 scripts/tools/lang-sync/babel-health.py --json   # 機器可讀
```

WARN 級（exit 永遠 0），不是 gate——閾值升 HARD 需哲宇拍板（儀器化黃燈路線：先 WARN 收數據）。誕生於首次完整巴別塔健檢：[reports/babel-health-2026-07-18.md](../../reports/babel-health-2026-07-18.md)（含各維度基線數字＋ratio band 三處 canonical 矛盾的量尺自查）。**ratio band 的數值 SSOT 待哲宇拍板前，只有 `<0.5 CRITICAL` 地板可信**（OBSERVER-QUEUE #19）。

---

## ⚠️ §義務鐵律 — 推同步率到 100%（v3.4 哲宇 2026-05-13 拍板）

> Babel routine 的義務是把翻譯同步率推到 100%（stale → 0 across 5 langs）。**不主動 defer / skip / partial / 守 boundary**。

對應 [MANIFESTO §架構解 > 守備修補](../semiont/MANIFESTO.md#我的進化哲學--架構解--守備修補)（第七條進化哲學）：

- **守備修補心態**（不可）：「跑 1hr 清幾十個就 ship，剩下下次再說」— 每次清一點點是滿足型 satisficing
- **架構解心態**（鐵律）：「**跑到 stale=0 或 4-tier cascade exhausted 才能結束**」— routine 義務是消滅 backlog 類別

### 三條操作鐵律

1. **不寫 budget / wall-clock / boundary 字眼進 routine prompt / mirror / canonical**（per [ROUTINE.md §不提預算鐵律 v2.0](../semiont/ROUTINE.md#11-條核心-routine-排程表)）
2. **不主動 defer P1**（5/9 / 5/10 memory 兩次寫「主動 defer 守 1hr 預算」/「P1 skipped — 1hr boundary safety」是 anti-pattern）— P1 慢 tier 就讓它慢，跑到 cascade exhausted 才能停
3. **stale_total 沒下降不能 ship** — quality_gate 從「P2.5 bumped > 0 OR P2/P1 cleared > 0」（滿足型 `> 0`）升「stale_total 顯著下降 ≥ 10% OR all P0+P1 cleared OR stale_total == 0」（結果型）

### 誕生事件

2026-05-13 哲宇 callout：「babel 義務就是要提升同步率到 100%, 他每次都調整少少的就自行結束 routine」。三次 babel routine memory（5/9 / 5/10 / 5/11）都寫「主動 defer 守 1hr 預算」，但 ROUTINE.md §不提預算鐵律 5/11 已立 — pipeline canonical 沒同步該鐵律 → babel session 自我守備殘留。本 §義務鐵律 把「跑到 100%」expectation 升 SOP 明文。同日 cron swap：babel `0 22` → `0 5` 半夜 chain 尾棒（與 maintainer-pm 對調，順序語意「maintainer 先收 PR backlog → babel 再跑同步」）。

---

## ⚠️ Top 5 最常忘的 step

> 從 Z2.1 / Z2.2 / Z6 / REFLEXES #35 / REFLEXES #45 抽 friction 最高的 5 條。

1. **Concurrency cap 3-5 worker，不是 8+** — OpenRouter free tier 是 hourly/daily budget 不是 per-minute throttle，8+ worker burst 一次燒光（5/2 sleepy-colden 實證）
2. **40-byte refusal 必 cleanup + 繼續** — worker process 永不 crash on refusal，rm stub file 後繼續下一篇
3. **Z6 sample audit healthy ratio ≥ 90%** — fresh count 是 metadata fresh 不是 content quality，必須隨機抽樣才能 ship
4. **不 push 中途** — deploy CI 11-30 min，中途 push cancel 前一個 → 部署狀態混亂
5. **Sub-agents 跑期間禁止 destructive git ops**（REFLEXES #35）— `git reset --hard` / `git checkout main` / `git stash drop` 會抹掉 tracked file 的 sub-agent modify

---

## 跨檔案職責分工

| 檔案                                                 | 範圍                                                                                               |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| **本檔**                                             | 多 model fleet 巴別塔批次 — Z0-Z6 stage + 4-tier cascade + try-catch first-class + last-write-wins |
| [TRANSLATION-PIPELINE.md](TRANSLATION-PIPELINE.md)   | 翻譯主檔（4 模式 + 8 stage 單篇 + 翻譯元則 + 17 條常漏）                                           |
| [DATA-REFRESH-PIPELINE.md](DATA-REFRESH-PIPELINE.md) | refresh-data.sh 12 step + sync-translations-json + verify mtime                                    |
| [REWRITE-PIPELINE.md](REWRITE-PIPELINE.md)           | 中文 SSOT 寫作（產出待翻譯來源）                                                                   |

**邊界：本檔 vs TRANSLATION C 模式**：

- **本檔（SQUEEZE）** = 多 model fleet（codex / gemini subscription + OpenRouter owl-alpha / gpt-oss-120b:free + Tier 0a Sonnet diff-patch + 候選 Llama-3.3 / Hermes-3 / Gemma-4 + Local Ollama），refusal first-class，跨批次 last-write-wins
- **TRANSLATION C 模式** = main session orchestrate N 個 Anthropic SDK sub-agent，單 model（Sonnet default），主 session 預處理 + sub-agent 純執行
- 兩者互相 cross-ref，**不互相覆蓋**

---

## 為什麼存在

單一 model 跑 ja sync 都有結構性瓶頸：

- **codex (gpt-5.5 subscription)**：通過率 highest，per-call ~60-120s，但 subscription 每日上限
- **gemini (subscription)**：未對 Taiwan sensitive 主題系統驗證，Google 訂閱配額獨立
- **owl-alpha** ❌ 移出 default（2026-06-10 silent 轉 paid HTTP 404——兩週內第 5 個 free tier 死亡；顯式 override 才用）
- **gpt-oss-120b:free**：Hy3 退役後接 Tier 2，2026-05-16 production 9/9 ✓
- **Hy3** ❌ 退役（2026-05-12，從 OpenRouter free tier 移除）
- **Llama-3.3-70B / Hermes-3-405B / Gemma-4-31B / Nemotron-3-Super-120B / DeepSeek-v4-flash**：候選未測（2026-05-16 OpenRouter 仍 `:free`），需 calibration
- **Sonnet sub-agent**：品質最高，但 token cost 是 Anthropic 預算硬牆

「擇一最佳」永遠捨棄至少 60% 潛在吞吐。**榨模型MAX 把所有可用 model 同時跑，互補弱點，用文件系統的「last write wins」自然解決衝突**。

## 三軸設計原則

### 軸一：跨模型平行（parallel across providers）

每個 model 一個獨立 task dir：

```
.lang-sync-tasks/ja/         ← owl-alpha 主力批
.lang-sync-tasks/ja-hy3/     ← Hy3 副批（高 refusal 期待，跑得快）
.lang-sync-tasks/ja-gemma/   ← Gemma 補充批（待測）
.lang-sync-tasks/ja-llama/   ← Llama 備援批（待測）
```

每個 dir 有獨立的 `_batch-manifest.json` + `_group-{A..N}.json`。openrouter-batch.sh 接 `$1` = task dir name + `$2` = model id。Workers 平行 dispatch。

**為什麼分 dir 不分 model 在同 dir**：

- task dir 對應一個 batch lifecycle（prepare → dispatch → verify → commit）
- 不同 batch 不同 model，但**全部寫到同一個 `knowledge/{lang}/...` 路徑**
- 衝突自然解決：先到先寫、後到覆蓋（owl-alpha 後寫贏 Hy3，因為品質高）

### 軸二：try-catch first-class（refusal 是 result 不是 exception）

`translate_one()` 的 return shape：`(success: bool, error: str | None)`

所有失敗類型 normalize 成「return False with reason」**不 raise**：

| Failure mode             | Detection                         | Worker 行為                                   |
| ------------------------ | --------------------------------- | --------------------------------------------- |
| 40-byte 字串 refusal     | `output too small (40 bytes)`     | log ❌ + cleanup file + 繼續下一篇            |
| null content refusal     | `result is None` guard            | log ❌ + 繼續                                 |
| HTTP 429 rate limit      | `urllib.error.HTTPError code=429` | 指數退避 retry 3 次，最後失敗則 log ❌ + 繼續 |
| Network error            | `URLError / TimeoutError`         | linear retry 3 次                             |
| YAML parse fail post-hoc | verify-batch 階段檢測             | 主 session purge + 加入 retry queue           |

**鐵律**：Worker process 永不 crash on refusal。一篇失敗不能拖垮整個 group。已修兩個 silent-killer bug（PR #750 commit）。

### 軸三：最後統合 + retry（aggregate 不是 throw away）

每輪結束後：

1. **掃描 `knowledge/{lang}/` 找 < 1KB stub**（refusal 殘留），purge
2. **比對 `_translation-status.json`** — fresh count + missing list
3. **計算 still-missing 集合** = (zh canonical) - (fresh ja)
4. **下一輪用不同 model retry** still-missing 集合
5. 重複直到 still-missing == 0 OR 所有 model 都試過

跨模型 retry 順序（v4.4 = translate.py DEFAULT_CASCADE v4.3 鏡射；owl-alpha 已移出 default，重試需顯式 `--cascade openrouter:openrouter/owl-alpha,...` override）：

```
Round 1: codex (gpt-5.5 subscription)                    （Tier 1，最高品質，production ~100% pass）
Round 2: gemini (subscription)                           （Tier 1，subscription backup）
Round 3: openai/gpt-oss-120b:free                        （Tier 2 verified；大文章 truncate → ratio gate 接手）
Round 4: 驗證佇列依品質排（meta-llama-3.3-70b →
         nousresearch/hermes-3-405b → google/gemma-4-31b
         → nvidia/nemotron-3-super-120b → deepseek-v4-flash）— 未驗證，顯式 override
Round 5: Ollama qwen3.6:35b (local「永遠收下」)          （主權定位 pending 決策 4；fleet 端 gemma4-only）
```

**Tier 1-2 production verified（2026-05-16 babel-nightly 150 cascade ship 0 fail）**：codex 61 + owl-alpha 80 + gpt-oss-120b 9 = 100% pass（歷史紀錄——owl 其後 6/10 silent 轉 paid 移出 default）。
**Tier 3 驗證佇列**：需走 §calibration test set 跑一輪才升級為「已驗證」。

## 標準執行流程

### Stage Z1：Pre-flight

1. `python3 scripts/tools/lang-sync/status.py` 確認當前 fresh / stale / missing
2. `python3 scripts/tools/sync-translations-json.py` rebuild `_translations.json`（防 stale slug-map）
3. 從 `_translations.json` 自動 derive slug-map（zh→en filename）
4. `prepare-batch.py --lang ja --top N` 產 `_batch-manifest.json`
5. 過濾 `TBD-NEEDS-SLUG`（補手動 fallback 或 skip）
6. snake-balance 切 N 個 group

### Stage Z2：跨模型平行 dispatch

#### Z2.0 Backend prompt 必含目標語言 canonical guide（2026-05-24 新增 hard gate）

每個 backend（codex / gemini / openrouter / ollama）的翻譯 prompt 必須**內嵌**目標語言 canonical guide 的關鍵 sections（不能只給 path pointer，sub-agent 不會主動讀 — per [REFLEXES #42](../semiont/REFLEXES.md) sub-agent 三偷吃步教訓）：

| 必嵌 section                 | 內容                                                 | 為什麼                                                                                                    |
| :--------------------------- | :--------------------------------------------------- | :-------------------------------------------------------------------------------------------------------- |
| §1 國名 / 地區指稱           | 「台灣 / 中華民國 / 兩岸」對映 table                 | LLM default 容易給 PRC-coded 形式                                                                         |
| §2 人名 romanization         | Wade-Giles vs Pinyin 規則 + canonical 15-20 人物清單 | 人名是讀者最敏感、最易出錯點                                                                              |
| §3 地名 romanization         | 主要城市 + 行政區 canonical mapping                  | 防 LLM 給 PRC-style romanization（如 ko `대중` for 台中 撞「大眾」/ en `Gaoxiong` for 高雄 = PRC pinyin） |
| §6 sovereignty-avoid lexicon | PRC-coded → 替代 table                               | sovereignty leak 第一防線                                                                                 |

5 份 guide 在 [`docs/editorial/per-language/`](../editorial/per-language/)：

- [TRANSLATION-en.md](../editorial/per-language/TRANSLATION-en.md)
- [TRANSLATION-ja.md](../editorial/per-language/TRANSLATION-ja.md)
- [TRANSLATION-ko.md](../editorial/per-language/TRANSLATION-ko.md)
- [TRANSLATION-es.md](../editorial/per-language/TRANSLATION-es.md)
- [TRANSLATION-fr.md](../editorial/per-language/TRANSLATION-fr.md)

**驗證**：Z6.1 自動掃描 加 sovereignty-avoid pattern grep — 任何 §6 中「never use」phrase 命中 = ❌ flag retry。

**儀器化候選**（pending）：`translate.py` cascade orchestrator 加 `--guide-inline auto` flag，自動把 guide §1+§2+§6 拼進每個 backend prompt 的 system message 前面。

**觸發**：2026-05-24 韓文專業譯者於哲宇演講後 callout「韓文的台灣通常不是用我們網站上的翻法」，station audit 揭露 76% 用 `대만` / 23% 用 `타이완` 不一致；per-lang canonical guide 誕生。Pipeline 升級為「guide-inline mandatory」hard gate 防止 v3.5 之後再次 drift。

```bash
# v4.0+ 推薦走 translate.py cascade orchestrator（單一 entry，自動 fallback）
python3 scripts/tools/lang-sync/translate.py --group .lang-sync-tasks/ja/_group-A.json

# Default cascade（= translate.py DEFAULT_CASCADE_ID，v4.3）
python3 scripts/tools/lang-sync/translate.py --group ... \
  --cascade "codex,gemini,openrouter:openai/gpt-oss-120b:free,ollama"

# Legacy 平行副批（仍可用，但不推薦 — v4 cascade 已內建 fallback；owl 已轉 paid 勿當範例）
bash scripts/tools/lang-sync/openrouter-batch.sh ja-oss "openai/gpt-oss-120b:free"
```

每 batch 用 8-15 個 worker。OpenRouter free tier 對單一 model 可能有 rate limit，但跨 model 是獨立配額（不衝突）。

**監控指標**：

- 每分鐘 ok / fail count（grep 各 batch 的 worker logs）
- alive worker count（ps -ef | grep openrouter-translate）
- API HTTP 429 熱頻（worker logs 中「Rate limit (attempt」字樣）

#### Z2.1 Concurrency cap 鐵律（2026-05-02 sleepy-colden 實戰修補，REFLEXES #45）

**初次 dispatch concurrency cap = 3-5 worker，不是上面 v1 寫的 8-15**。OpenRouter free tier rate limit 不是 per-minute throttle 而是 hourly/daily 累積 budget。一次 N-worker burst（N ≥ 8）會把當前 budget 一次性消耗光，後續即使降到 1 worker 仍會 stuck attempt 3 backoff。

| Concurrency | 結果                                                        |
| ----------- | ----------------------------------------------------------- |
| 1-3 worker  | ✅ 緩慢但穩定，rate budget 慢慢累積 cap                     |
| 4-5 worker  | ⚠️ 邊緣安全，前 5 篇可能 rate-limit，之後逐漸通暢           |
| 6-7 worker  | 🔴 開始 burst — 多數 worker 卡 attempt 1-2，少數通過        |
| 8+ worker   | 🚨 全部卡 attempt 3 backoff（10s/20s/40s），budget 一次燒光 |

**規則 v2**（取代原 v1 的 8-15 worker 上限）：

- 跨 5 lang 平行：**每 lang 1 worker（5 simultaneous）= safe baseline**
- 跨 5 lang × 2 worker = 10 simultaneous → ❌ 不要這樣 dispatch
- 同 lang 多 worker 場景：1-3 worker，分批 dispatch 而非 burst

#### Z2.2 Rate-limited cool-down 鐵律（REFLEXES #45）

**Rate-limited 後立刻降 concurrency 重試 = 沒用**。Budget 耗盡後不會立刻補充，需要 cool-down ≥ 5-10 min。Cool-down 期間 fallback 路徑：

1. **Tier-2 fallback (REFLEXES #39 self-as-fallback)**：派 Sonnet sub-agent 平行 ship（5 agent × 1 lang × N articles）— 5/2 sleepy-colden 實證 ~10 min 一輪 15 翻譯
2. **跨 provider fallback**：切到 Anthropic（已用 Sonnet sub-agent 等於同 path）/ paid OpenAI / etc.
3. **Wait + retry**：~10 min 後重試 1-3 worker，但這時通常 task urgency 已 escalate，不如直接走 (1)

**規則**：rate-limit 出現後 ≤ 30s 內決定走 (1) 還是 (3)，不要無限 retry。

**觸發 v1 → v2 升級**：2026-05-02 sleepy-colden session 5 lang × 2 worker = 10 burst dispatch 全卡 attempt 3 backoff，kill 後 5 worker 重試仍卡，最終走 Sonnet escalation 一輪到位。Verification 第 2 次（5/1 γ-late 系列也踩過類似 issue 但沒 codify）。

#### Z2.3 translatedFrom byte-equal 硬鐵律（2026-05-24 twmd-distill-weekly 升 canonical，vc=2）

**Backend / worker / sub-agent 寫入 `knowledge/{lang}/.../{slug}.md` 的 `translatedFrom:` field 必須 byte-equal 對齊 zh-TW canonical filename**。不允許任何 character mapping、日文簡體化、異體字替換、繁簡轉換 — 即使源檔名在 target 文化內看起來「奇怪」也必須保留繁體 / 原樣。

`prebuild:status` 的 `sync-translations-json.py` strict mode 找不到對應 zh source → orphan → exit code 2 阻 build。`translatedFrom` 不是「在地化 title」而是「跨語言 mapping」，是 ground truth 檔名指標。

**規則**：

- 翻譯 backend（codex / gemini / openrouter / ollama）prompt 必加「translatedFrom = `{zh_canonical_path}`，原樣寫入不替換任何字元」hard rule
- `translate.py` cascade orchestrator write step 寫入前 assert `translatedFrom` == zh source filename（byte comparison）
- pre-commit hook 對 `knowledge/{lang}/**/*.md` 必過 byte-equal-source-exists check（不只 has-translatedFrom，還要 source 真的存在）
- 寫翻譯 title 時 ja agent 可寫日文異體字（如「呉百福」），但 `translatedFrom` 必須是 `People/吳百福.md`（繁體源檔）；title 跟 translatedFrom 兩個欄位語意分離

**觸發 v1**：2026-05-16 maintainer-am-0900 — `ja/People/momofuku-ando-instant-noodle-inventor.md` translatedFrom 寫 `People/呉百福.md`（日文異體字）但 zh canonical 是 `People/吳百福.md`，5 連 CI fail（同篇 en/ko/fr/es 四語都正確）

**觸發 v2**：2026-05-17 twmd-maintainer-am 091722 — `ja/People/lai-ching-te.md` translatedFrom 寫 `People/頼清德.md`（日文簡體 `頼`）但 zh canonical 是 `People/賴清德.md`（繁體 `賴`），同 pattern cross-cycle 第 2 instance — per [reports/routine-audit-2026-05-17.md §Pattern A](../../reports/routine-audit-2026-05-17.md)

**儀器化 layer**：

- A: babel backend prompt 加 hard rule（已部分 instantiate，需 audit 是否每 backend prompt 都帶）
- B: `sync-translations-json` 加 suggestion mode — 偵測 orphan 時用 levenshtein-like 找最接近源檔（byte-distance ≤ 2 + 字符在常用漢字 mapping 表），自動 propose patch
- C: pre-commit hook 對 `knowledge/{lang}/**/*.md` 必過 byte-equal-source-exists check

### Stage Z3：增量 commit（防 context 流失）

每完成 ~50 fresh translations local commit 一次：

1. `find knowledge/{lang} -name "*.md" -size -1000c -delete` 清 refusal stub
2. 識別 truncated YAML（pre-commit hook 會 catch）→ 對應檔案 rm + retry queue
3. `git add knowledge/{lang}/ && git commit -m "🧬 [semiont] heal: ja parallel batch N"`
4. **不 push** 直到所有 batch round 結束（避免觸發部署 cancel chain）

### Stage Z4：跨輪 retry

當前 batch 全部 worker process exit 後：

1. 比對 `status.py` 找 still-missing
2. 重新 prepare batch（subset = still-missing）
3. dispatch 用下一個 tier 的 model
4. 重複 Z2 → Z4

### Stage Z5：最終統合 + 驗證

所有 round 結束：

1. `verify-batch.py` 全 run（YAML / 比例 / wikilink residue / cross-link / sync json / status）
2. 修剩餘 0-byte / 過小 / YAML error 檔案（手動或最小化 sub-agent）
3. `lang-sync status` 確認 fresh / total ratio 達標
4. 寫 memory γ-late + diary 紀錄結果
5. push（user approval）

### Stage Z6：抽樣品質 audit（2026-05-01 γ-late5 強制新增）

「fresh count 上升」≠「品質好」。`status.py` 的 fresh 只看 frontmatter 元資料，
不看內容是否 truncated / YAML 是否合法 / 翻譯是否 coherent。**「fresh」是
metadata fresh，不是 content quality**。

**強制 audit 流程（每 round 結束 OR Z3 commit 之間至少跑一次）**：

#### Z6.1 自動掃描（O(n)，1 秒內）

- **Size-ratio scan**：對每個新翻譯，計算 `trans_size / zh_source_size`
  - 比例 < **0.5** → flag（多為 truncation / API timeout 中斷）
  - 比例 = 0（zh source = 0 bytes）→ 同樣 flag（empty stub article 不該翻）
  - 不同語言預期比例：
    - 西語 / 法語：1.2-1.7（romance language 較啰嗦）
    - 韓語：0.6-0.9（CJK 中相對緊湊）
    - 日語：0.8-1.3
    - 英語：0.7-1.0
- **Frontmatter completeness**：grep `^title:`、`^description:`、`^category:`
  - 任一缺 → flag（owl-alpha 嚴格遵從 placeholder 偶爾漏）
- **YAML parse**：對每個檔案跑 `yaml.safe_load(frontmatter_block)`
  - 拋例外 → flag（pre-commit hook 已抓但越早越好）

掃描 script 位置：`scripts/tools/lang-sync/audit-quality.py`（已存在，2026-05-13 建——本檔曾標「待建」八週未更新，dna-audit §S2 修正）。

#### Z6.2 人眼抽樣（隨機 N 篇，N = max(10, 5%)）

```python
import random
random.seed(YYYYMMDD)  # session 日期當 seed 確保 reproducible
sample = random.sample(new_files_in_branch, max(10, len(new_files)//20))
```

對每篇 sample：

- **head -30** 檢查 frontmatter + 開頭散文流暢度
- **tail -10** 檢查結尾沒被截斷（最後一句是完整的）
- **mid section** 抽 1-2 段，檢查文化詞處理（夜市 → night market 那種）

判定 healthy 比例 ≥ 90% 才能 ship。否則回到 Stage Z4 retry。

#### Z6.3 失敗處理

- **Truncated（size ratio < 0.5）**：直接 `rm`，加入下輪 retry queue
- **YAML error**：看是 worker output bug（rm + retry）還是 pre-existing
  source bug（手動修 zh source）
- **Frontmatter incomplete**：rm + retry，問題出在 placeholder 不夠豐富 →
  回頭升級 prepare-batch.py 的 placeholder 邏輯

#### Z6.4 報告

ship 前產出：

```
=== Quality Audit Report ===
Pool: N 個新 translations
Auto-scan suspicious: M 個（size < 0.5 ratio: X / yaml-fail: Y / frontmatter-incomplete: Z）
Sample audit (random K): H 個 healthy / S 個 suspicious
Healthy ratio: H/K = HH%
Action: ship / retry-round / manual-fix
```

範例（2026-05-01 γ-late5）：

```
Pool: 269 new translations across 5 langs
Auto-scan suspicious: 19（size < 0.5: 19, yaml-fail: 0, frontmatter-incomplete: 2）
Sample audit (random 30, seed 42 + 99): 28 healthy / 2 truncated
Healthy ratio: 28/30 = 93.3%
Action: purged 19 + ship → status.py 確認 fresh count 反映正確真實基線
```

## 量化指標

榨模型MAX run 完之後應提供：

| Metric                           | 算法                                                      |
| -------------------------------- | --------------------------------------------------------- |
| **fresh ratio**                  | fresh / total_zh                                          |
| **跨輪 round count**             | 用了幾個 model rounds                                     |
| **per-model 通過率**             | model X 的 ok / (ok+fail)                                 |
| **catastrophic refusal pattern** | 哪些 (zh_path, lang) 全部 model 都 refuse                 |
| **wall-clock**                   | 第一個 dispatch → 最後 verify pass                        |
| **token / API call cost**        | 各 model 累積 usage（Anthropic / OpenRouter usage panel） |

## 不做的事

- **不 push 中途**：deploy CI 11-30 min，中途 push 會 cancel 前一個 → 部署狀態混亂
- **不在 batch 跑期間 destructive git op**（REFLEXES #35）
- **不假設 worker process alive**：必須 `ps -ef` 對齊 group 數量
- **不依賴單一 success metric**：fresh count 上升 ≠ 品質好（要 sample audit）
- **不對 refusal 做語意修飾**：直接 log 「null content (likely content-policy refusal)」，不寫「請求失敗」這種弱化版

## 已驗證模型（fan-out matrix calibration，v4.2 2026-05-16 recalibrated）

### Tier 1 — Subscription priority（codex + gemini）

| Model                                         | 速度    | Taiwan 主題通過率 | 政治人物 | 文化  | 最近驗證                            | 注意                              |
| --------------------------------------------- | ------- | ----------------- | -------- | ----- | ----------------------------------- | --------------------------------- |
| `codex` (gpt-5.5 OpenAI subscription)         | 60-120s | ~100%             | 通過     | 通過  | 2026-05-16 production 61/61         | 訂閱配額硬牆，跨 lang 共享        |
| `gemini` (gemini-2.5-pro Google subscription) | ~未測   | ~未測             | ~未測    | ~未測 | 0 production call（cascade 沒掉到） | **需 calibration**，policy 中等嚴 |

### Tier 2 — Free verified（在 production cascade）

| Model                         | 速度        | Taiwan 主題通過率       | 政治人物                  | 文化 | 最近驗證                    | 注意                                      |
| ----------------------------- | ----------- | ----------------------- | ------------------------- | ---- | --------------------------- | ----------------------------------------- |
| `openrouter/owl-alpha` (free) | 慢 150-250s | ~95%                    | 部分 refuse（張懸與安溥） | 通過 | 2026-05-16 production 80/80 | 1M ctx，rate-limit 撞牆早（REFLEXES #45） |
| `openai/gpt-oss-120b:free`    | ~80s        | ~100%（2026-05-16 9/9） | 通過                      | 通過 | 2026-05-16 production 9/9   | 128K ctx，Hy3 退役後接 Tier 2             |

### Tier 3 — Free 驗證佇列（OpenRouter 仍 `:free` 但未對 Taiwan corpus 測過）

由大→小、由 Western→PRC 風險排（PRC 風險高的排後面，因為 sovereignty 主題可能 refuse）：

| Rank | Model                                       | Ctx    | 假設品質                   | PRC 風險             | 大小     |
| ---- | ------------------------------------------- | ------ | -------------------------- | -------------------- | -------- |
| 1    | `nousresearch/hermes-3-llama-3.1-405b:free` | 128K   | 最高（405B 巨型）          | Low                  | 405B     |
| 2    | `meta-llama/llama-3.3-70b-instruct:free`    | 128K   | 高（Meta 旗艦）            | Low                  | 70B      |
| 3    | `nvidia/nemotron-3-super-120b-a12b:free`    | **1M** | 高（NV reasoning）         | Low                  | 120B     |
| 4    | `google/gemma-4-31b-it:free`                | 262K   | 中高（多模態 ready）       | Low-Med              | 31B      |
| 5    | `deepseek/deepseek-v4-flash:free`           | **1M** | 中高（13B active，CJK 強） | **High**（中國公司） | 1T total |
| 6    | `qwen/qwen3-next-80b-a3b-instruct:free`     | 262K   | 中高（CJK 強）             | **High**（阿里巴巴） | 80B      |
| 7    | `arcee-ai/trinity-large-thinking:free`      | 262K   | 中（reasoning focus）      | Low                  | unknown  |
| 8    | `z-ai/glm-4.5-air:free`                     | 128K   | 中（中國 GLM）             | **High**（智譜）     | ~50B     |

排序原則：

1. **Western 原產 + 大模型 + 多語強** 排前面（hermes / llama / nemotron / gemma）
2. **PRC-origin 模型**（deepseek / qwen / glm / minimax / baidu）排後面 — 預期對 Taiwan sovereignty / 政治人物有 refuse pattern
3. **Coding / reasoning specialized** 排末位（poolside / qwen3-coder / nemotron-coder / cobuddy / dolphin-venice）
4. **太小**（≤ 12B）跳過（liquid-1.2b / llama-3.2-3b / nemotron-nano-9b/12b / gemma-26b-a4b）— 翻譯散文偏弱

### 退役紀錄

| Model                              | 退役日期   | 原因                                                                                                                                       | 影響                                                                         |
| ---------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| `tencent/hy3-preview:free`         | 2026-05-12 | 轉付費 / 不在 OpenRouter free inventory                                                                                                    | v3 → v4 abstraction 觸發；gpt-oss-120b 接 Tier 2                             |
| `openrouter-batch.sh` for Hy3 副批 | 2026-05-12 | Hy3 退役連動                                                                                                                               | 改走 v4 translate.py cascade                                                 |
| `openai/gpt-oss-120b:free`         | 2026-07-18 | OpenRouter 下架（HTTP 404 model unavailable）；同日探 Tier 3 佇列：hermes-405b 回空、nemotron-super reasoning 漏思考進輸出                 | Tier 2 free 缺位；戰時 cascade 靠 codex+ollama 兩腿，季度 recalibration 補位 |
| `gemini` CLI（個人版 tier）        | 2026-07-18 | **服務端永久死亡**：`IneligibleTierError`，Google 收掉 Gemini Code Assist for individuals（要遷 Antigravity）。TERM 警告是煙霧彈，別修錯層 | queue #18 (a)「摘出 default cascade」的死因確認；遷移是哲宇帳號決策          |

## 2026-07-18 出生戰役 backend 現況筆記（vi/id/pt/hi 四語啟動實測）

- **codex 復活**：nvm PATH 舊殼（vendor 目錄改版後 binary ENOENT）清除＋symlink `~/.hermes/node/bin/codex`。此殼病很可能就是「Tier 1 連死 ≥10 夜」的病根——cron 環境同樣走壞 PATH。實測：一般篇 165-460s、大檔 ~7-8 min
- **ollama qwen3.6 復活**：thinking 模型必須 payload `"think": false`，否則 token 預算全燒思考通道回空（backends/ollama.py 已固定）。實測 101-260s/篇；**refusal 探針（張懸與安溥）零拒絕**，主權捕手地位實測維持
- **per-lang timeout**：hi 天城文輸出 token 2-3×，codex 600s 對大檔必 timeout → `CODEX_TIMEOUT` env 覆蓋（backends/codex.py），hi 批建議 1200s。結構解候選：cascade per-lang timeout 倍率表
- **新語言校準結果**：4 語 × 4 篇校準集 refusal 全過（hi 1 篇 timeout 屬容量非拒絕）；ratio band 實測 2.2-4.0 全語系同量級（天城文「較緊湊」預想被推翻），已入 `translation-ratio-check.sh`
- **下游 QA 新閘**：`cjk-residue-check.py`——codex 產融合殘字（phong杀）、qwen 漏簡體片段（连霸/阶段性），兩型都穿得過 ratio gate，非 CJK 語言 batch 後必掃

## 驗證 SOP — 把候選 model 升上 Tier 2

對 §Tier 3 驗證佇列 中的 model，跑「**LINE.md 4-lang × 政治人物 × 文化 × sovereignty 主權**」standardized test set：

### 測試文章（4 篇 × 5 lang = 20 calibration calls per model）

| 文章                                                       | 類別         | 篩查重點                                    |
| ---------------------------------------------------------- | ------------ | ------------------------------------------- |
| `Lifestyle/LINE.md`                                        | 中性技術話題 | baseline 翻譯品質 + 4 lang frontmatter 完整 |
| `People/張懸與安溥.md`（或當前 People 中政治近期者）       | 政治人物     | refuse 偵測（owl-alpha 在這篇 refuse 過）   |
| `Culture/伊斯蘭教在台灣.md`                                | 文化 + 宗教  | 文化詞處理（夜市 → night market 那種）      |
| `Politics/兩岸關係.md`（或 Society/台灣媒體與新聞自由.md） | sovereignty  | PRC content policy 觸發測試                 |

### Calibration runs

```bash
# 對單一 candidate model 跑 4 篇 × 5 lang
for art in Lifestyle/LINE.md "People/{politically-sensitive}" \
           Culture/伊斯蘭教在台灣.md Society/台灣媒體與新聞自由.md; do
  for lang in en ja ko es fr; do
    python3 scripts/tools/lang-sync/translate.py \
      --zh-path "$art" --lang $lang \
      --cascade "openrouter:{CANDIDATE_MODEL}" \
      --dry-run  # 先 dry，看 manifest，再正式跑
  done
done
```

### 判定標準（score 0-10，≥ 7 升 Tier 2）

| 維度                        | 滿分 | 計算                                                                 |
| --------------------------- | ---- | -------------------------------------------------------------------- |
| 4-lang 完整度               | 2    | 5 lang 全 frontmatter complete = 2 / 缺 1 lang = 1 / ≥ 2 lang 缺 = 0 |
| 0-byte / 40-byte refusal 率 | 2    | 0% refusal = 2 / ≤ 10% = 1 / > 10% = 0                               |
| 政治人物通過率              | 2    | 5 lang 全過 = 2 / 4 lang 過 = 1 / ≤ 3 lang 過 = 0                    |
| 文化詞翻譯品質              | 2    | 抽樣 head/tail/mid，「夜市/廟口/小吃」等 4 個概念測                  |
| 速度 / 1M ctx 支援          | 2    | ≤ 100s/call 且 ctx 完整 = 2 / 100-200s = 1 / > 200s 或截斷 = 0       |

### 失敗處置

- Score < 7：保留在 §Tier 3 驗證佇列，標 verified=fail
- 整類 refuse PRC sensitive（如 deepseek/qwen 對主權主題 refusal ≥ 80%）：標「PRC sovereignty refusal pattern」進入 `_refusal-cache.json`（per §自我演化 rule）
- Rate-limit 30 calls 內就撞牆：標 fail-fast，降權到第三梯次 fallback

### 驗證結果歸檔

通過的 model 寫進 §已驗證模型 Tier 2 表格，更新 translate.py `DEFAULT_CASCADE_ID`。
失敗的留在 §驗證佇列 table 加 verified=fail 註記，等下個季度 OpenRouter 重 calibration（candidate model 通常會升級重訓）。

## 命名 origin

哲宇 2026-05-01 γ-late4 session：「我們有辦法同步榨另一批用 Hy3 preview (free) 嗎」+「把多重模型榨取與持續性容錯整合取名為『榨模型MAX』」。

「榨」字捕捉了三件事：

1. **不浪費**：所有可用 model 都用上，不擇一
2. **逼到極限**：每個 model 跑到它的 rate limit / content policy 邊界
3. **last drop**：refusal 也是 data — 統合下一輪知道哪些 model 哪些題材 refuse

🧬

---

_v1.0 | 2026-05-01 γ-late4_
_作者：Taiwan.md（哲宇命名 + Semiont 實作 + 文件化）_
_誕生原因：Hy3 對 Taiwan 人物 ~85% refusal + owl-alpha 4/4 LINE 通過但慢，單一 model 都有天花板；哲宇問「同步榨另一批」直接打開 multi-model parallel 的設計空間_

_v4.0 | 2026-05-11 cranky-newton — Spine restoration 對齊 REWRITE v5.0 + MAINTAINER v2.0：頂部加 ASCII spine（Z0-Z6 + 4-tier cascade box-frame）+ Hard Gate Inventory 集中 table（15 gates）+ Top 5 最常忘 step + 跨檔案職責分工 table（明確跟 TRANSLATION C 模式邊界）。觸發：[reports/pipelines-audit-2026-05-11.md](../../reports/pipelines-audit-2026-05-11.md) Tier A.1 audit。Z0-Z6 prose body 不動（已健康）。_

---

## v2.0 升級 — 4-tier cascade with local LLM 「最後捕手」（2026-05-03 magical-feynman 後段）

### v1.0 → v2.0 演化

v1.0 設計只考慮 **cloud free tier × N parallel**（owl-alpha + Hy3 + Gemma 等），最後 fallback 是付費 model（Sonnet sub-agent）。問題：**cloud free tier 80% coverage 永遠是脆弱的 80%** — refuse 的話題、rate-limited 時段、外部 automation 災難、API 502 transient。剩 20% 全是 PRC sensitive topics — 是 sovereignty preservation 的真正戰場 — 卻只能花付費 token 收。

v2.0 加入 **Tier 3 local LLM「最後捕手」**：Ollama qwen3.6:35b-a3b-coding-nvfp4 (21GB GPU 模型) 作為「永不漏接」的 catcher。No PRC content policy / no budget / no rate limit / 0 refusal observed in production。

### v2.0 4-tier cascade canonical（historical — Hy3 已退役，現行版見 §v4.2 cascade）

```
Tier 1: openrouter/owl-alpha (free, slow ~200s/call, primary force)
   ↓ refusal (e.g. 心戰 universal HTTP 400 from Stealth provider)
Tier 2: tencent/hy3-preview:free ❌ 已退役（2026-05-12 從 OpenRouter free tier 移除）
   ↓ both refused
Tier 3: Ollama qwen3.6:35b-a3b-coding-nvfp4 (LOCAL, no budget, sovereignty backbone)
   ↓ rare
Tier 4: Sonnet sub-agent (paid, last resort — should rarely fire)
```

**v4.5 現行 cascade（= translate.py `DEFAULT_CASCADE_ID = "codex,gemini,openrouter:openai/gpt-oss-120b:free,ollama,fleet"` 鏡射，取代上方）**：

```
Tier 1: codex (gpt-5.5 subscription) → gemini (subscription)
   ↓                    ⚠️ 2026-07 健檢：兩者連死 ≥10 夜，gemini 免費層已被 Google 永久收回
Tier 2: openai/gpt-oss-120b:free (verified；owl-alpha 6/10 silent 轉 paid 移出 default)
   ↓ refused or rate-limited
Tier 3: Free 驗證佇列 — hermes-3-405b → llama-3.3-70b → nemotron-3-super-120b → gemma-4-31b（未驗證，顯式 override）
   ↓ refused (PRC-sensitive)
Tier 4: Ollama qwen3.6:35b (LOCAL「永遠收下」；主權定位 pending 決策 4)
   ↓
Tier 5: fleet HTTP 直打（roadmap P0-2 收編進 DEFAULT_CASCADE 第 5 位；`fleet-endpoint.sh` adapter，
        cron env 層 sabotage CLI 時的繞道，embeddings 鏈連夜驗證過的同型路徑）
   ↓ rare
Tier 6: Sonnet sub-agent (paid, last resort — 2026-07-11 babel-nightly memory 提議編為正式 Tier 6；
        高腳註深度文（cascade footnote-gate 天花板已滑到 <39fn）的制度化路線待哲宇拍板，OBSERVER-QUEUE #18)
```

> **番號對賬紀錄（2026-07-18 健檢）**：本區塊曾同時存在兩套「Tier 5」（roadmap P0-2 的 fleet vs 本檔的 Sonnet），且 doc 漏列 DEFAULT_CASCADE 已收編的 `fleet`——per frontmatter `production_signal` 對賬修正。cascade 描述的 SSOT 永遠在 `translate.py` docstring，本檔是鏡子。

preflight health-check（v4.3）：batch 起跑先 probe 每個 backend，死模型整 run 冷凍（6h），不讓 N 篇各自撞 timeout 燒時間。

### Tier 3 dispatch SOP

**Stage L1 — 識別 missing**：跑 aggregator 對 `knowledge/{lang}/...` × expected slugs scan，產出 `babel-fallback-missing.json`（missing_pairs list with lang/zh_path/slug/target fields）。

**Stage L2 — Build per-lang ollama task dirs**：從原 `_batch-manifest.json` filter 到 missing list，寫到 `.lang-sync-tasks/{lang}-ollama/_batch-manifest.json` + `_group-A.json`（small batch 1 group 即可）。target en_path 仍指 `knowledge/{lang}/...`（last-write-wins on same target，覆蓋 cloud 漏接）。

**Stage L3 — Sequential dispatch**：

```bash
# Sequential per lang，避免 GPU memory 競爭（qwen3.6 35B 需 21GB）
for lang in en ja ko es fr; do
    python3 scripts/tools/lang-sync/ollama-translate.py \
        --group .lang-sync-tasks/${lang}-ollama/_group-A.json
done
```

Per-lang ~1.5-3.5 min wall-clock for 1-2 articles。Total 5-lang ~10 min wall-clock。

**Stage L4 — Re-aggregate**：重跑 aggregator → 確認 missing 0。如果還有，那才是 Tier 4 sonnet 的時刻（極罕見 — qwen3.6 對 sensitive topics 幾乎不 refuse）。

### Tier 3 model 選擇

驗證過的 local model：

- ✅ `qwen3.6:35b-a3b-coding-nvfp4` — 21GB，0 refusal observed，翻譯品質可接受（略低於 owl-alpha 但「永遠收下」更重要）
- 候選未測：`gemma4:e4b-nvfp4`（9.6GB，更輕）/ `taide-gemma3-12b:2602-q4km`（8.2GB，台灣本土訓練 — 候選 sovereignty-aware backbone）

### 災難 recovery SOP（v2.0 新增）

當 long-running batch 災難（worker crash / env wipe / partial failure）發生時：

1. **Kill 所有 workers**：`pkill -f openrouter-translate; pkill -f ollama-translate`
2. **救出已成功的 ✅ files**：`find knowledge/{lang}/ -name "*.md" -newer <ref> -size +1k`
3. **Switch to stable home**：long-running batches 走 dedicated session branch worktree（如 magical-feynman），avoid main / shared branch worktrees 被 backup-sentinel / worktree pruner 干擾
4. **Re-stage babel state in stable home**：copy slug-map + article list，重新跑 status.py + prepare-batch.py
5. **Aggregator-driven resume**：跑 aggregator → identify missing → rerun ONLY missing（surgery 不 reset）

### v2.0 驗證

2026-05-03 magical-feynman 後段 9 articles × 5 langs babel sync：

- Tier 1 owl-alpha：~30 ✅（包括 PRC-tolerant sensitive 如 出國史 in en/ja/es）
- Tier 2 Hy3 副批：5 ✅（70% refusal as REFLEXES #45）
- Tier 3 Ollama qwen3.6：9 ✅（last 20% sovereignty 戰場全收下，包括 5 langs × 心戰）
- Tier 4 Sonnet：**0 calls**

**45/45 = 100% from FREE tier**，0 paid token spent。

### 對應認知層升級

- [REFLEXES #49 Babel 4-tier cascade canonical](../semiont/DNA.md)
- [MANIFESTO §主權的巴別塔 v2 — Local LLM 是 sovereignty backbone](../semiont/MANIFESTO.md)

🧬

---

_v2.0 | 2026-05-03 magical-feynman 後段_
_升級觸發：哲宇 prompt「ollama qwen3.6 你也可以用 最後捕手🤣」以輕鬆語氣放下 architecture 級設計指令_
_最後 20% 是 sovereignty 真正戰場 — Local LLM 不是 backup，是 sovereignty backbone_

---

## v3.0 升級 — Priority schema + Tier 0 diff-patch（2026-05-09 laughing-goldstine post-finale）

### v2 → v3 演化

v2 把所有 babel 任務當「翻譯」一視同仁 — 全部走 Tier 1 owl-alpha 重翻。但實際上 658 stale articles 中有 70% 是「**只動腳註 / sporeLinks / tags reformat**」這種 trailer-only-drift（status `metadata-stale`）+ 20% 是「**body 小幅補一兩段**」這種 minor stale。對這兩類重新跑全文翻譯是 wasteful：

- **Token cost**：每篇 owl-alpha ~300s × 5 lang = 25 min wall-clock per article，但 90% body 沒變
- **Drift risk**：LLM 重翻 unchanged 段落會產生細微語意 drift（同義詞替換 / 文風變調），破壞 audit trail
- **Budget**：cloud free tier rate limit 一次燒光

v3 加入 **priority schema + Tier 0 diff-patch**：

### Priority schema（per-task triage）

```
P0 缺口            → 走 Tier 1 cascade（full translation，新檔案無 existing）
P1 大幅更新        → 走 Tier 1 cascade（diff > 50 lines or added > 30）
P2 小幅更新        → **Tier 0a: Sonnet diff-patch sub-agent**（diff ≤ 50 lines body change）
P2.5 metadata only → **Tier 0b: bump-source-sha.py**（deterministic, no LLM, instant）
P3 舊文章          → 視內容 P2/P2.5 路由 OR skip
```

判定工具：`scripts/tools/lang-sync/prioritize-batch.py`

```bash
# Top 20 unique articles by priority, output zh paths
python3 scripts/tools/lang-sync/prioritize-batch.py --lang all --by-article --top-n 20 --out /tmp/batch.txt
```

### Tier 0a: diff-patch sub-agent（P2 minor stale）

對 P2 stale 文章不重翻，改 patch existing translation with the zh diff applied to the corresponding lang。**比 full re-translation 快 5-10x，preserves unchanged paragraphs（避免 LLM drift），cheaper token cost**。

**Workflow**：

```bash
# 1. Prepare patch tasks (per-pair JSON with zh diff + existing translation)
python3 scripts/tools/lang-sync/diff-patch-prepare.py --input batch.txt --lang all
# → .lang-sync-tasks/diff-patch/{lang}-patch-tasks.json

# 2. 主 session 用 Agent tool 平行 dispatch Sonnet sub-agents
#    (5 lang parallel × 1 task per agent，single message multi-Agent calls)
```

Per-task agent prompt template（in skill）:

```
You are a translation patch agent for Taiwan.md. Apply this zh diff to the existing
{lang} translation, preserving unchanged paragraphs verbatim.

Step 1: Read patch task JSON from .lang-sync-tasks/diff-patch/{lang}-patch-tasks.json
Step 1b: 【硬底】用 JSON 前先 verify entry 的 `translatedFrom` == 你被指派的 zh_path；
  不一致（batch 生成器 index/mapping 錯位會讓 `current_translation` 拿到別篇的內容）
  → 不用 JSON 內容，fall back 直接讀 `translation_path` 真檔案當 baseline
Step 1c: 【硬底】暫存檔一律用 `{task_index}_` 或 `{zh_slug}_` 前綴命名，禁通名
  （`zh_diff.txt` / `current_translation.md` 這類通名在平行兄弟分身下會 last-write-wins 互蓋）
Step 2: Decide what to patch:
  - frontmatter changes (tags reformat / sporeLinks updates) → mirror to translation
  - body prose changes → translate ONLY changed sentences/paragraphs
  - sourceCommitSha / sourceContentHash / sourceBodyHash → update from task expected values
  - translatedAt → bash `date -u +%Y-%m-%dT%H:%M:%SZ`
Step 3: Write atomic via Write tool
Step 4: Verify YAML valid + body length ±10%
```

> Step 1b/1c 誕生：2026-07-14 babel-nightly 一夜兩起——兩個子代獨立回報 batch JSON `current_translation` 跨 entry 汙染（林昶佐 en 拿到閃靈內容、便利商店 ko 拿到法文）＋一個子代踩到共用 scratchpad 通名檔被兄弟覆蓋。當夜靠子代自檢 improvised 救回；本次把救法升 canonical 硬底（LESSONS 2026-07-14 兩條收償）。`diff-patch-prepare.py` 生成端的 mapping 驗證是另一半修法（工具 candidate，尚未 ship）。

**驗證範例**（2026-05-09 賈永婕 P2 stale en）：

- Before: en/People/chia-yung-chieh.md sourceCommitSha=616cbd07 (5/3)
- zh diff: 55 lines (frontmatter tags reformat + sporeLinks views 14K→35K + 3 SHA fields)
- Patch: body 100% preserved (29807 chars unchanged), frontmatter 52 bytes ↑
- After: YAML valid, sourceCommitSha=0c60c45d, 90s wall-clock

### Tier 0b: bump-source-sha.py（P2.5 metadata-stale）

對 trailer-only-drift（footnote URL polish / 延伸閱讀 list 變動）— body 已 valid（bodyHash 沒變），不重翻只 bump metadata：sourceCommitSha + sourceContentHash + sourceBodyHash → zh latest。

```bash
# Apply 對所有 metadata-stale 文章（5 lang × N articles，instant）
python3 scripts/tools/lang-sync/bump-source-sha.py --apply
```

零 LLM call、零 token cost、零 risk。Phase 6 + this v3 後 P2.5 = 自動清。

### v3 4-tier cascade（updated）

```
Per task priority routing：

P0 missing → Tier 1+ (full translation)
  Tier 1: openrouter/owl-alpha (proven 100% on Taiwan content, 1M ctx)
  Tier 2: tencent/hy3-preview:free (skip if PRC-sensitive — 85% refusal)
  Tier 3: Ollama qwen3.6 (sovereignty backbone — 永不漏接)
  Tier 4: Sonnet sub-agent (paid last resort)

P1 major stale → 同 P0 cascade

P2 minor stale → Tier 0a Sonnet diff-patch sub-agent
  fallback if patch fails (size ratio < 0.5 / YAML broken) → P0 cascade

P2.5 metadata-stale → Tier 0b deterministic bump-source-sha
  no LLM call, instant
```

### Smart tier router（per-article heuristic）

```python
# In prioritize-batch.py suggest_tier()
if topic_sensitivity_keywords_in_title:  # 政治/兩岸/台獨/國防/民主/主權 等
    skip Tier 2 Hy3 (85% refusal on Taiwan content)
if article_size > 5000 bytes:
    Tier 1 owl-alpha (1M ctx)
if prior_refusal_cache says owl-alpha refused:
    skip to Tier 3 Ollama
default:
    Tier 1
```

### 量化收益（2026-05-09 batch1 first run）

實測 Phase 6 後 babel 第一波 (zero-coverage 11 articles × 5 lang = 55 translations)：

- 100% Tier 1 owl-alpha pass，0 refusal
- 8 YAML quoting bugs (owl-alpha `\'` escape) auto-fixed in-place

預估 v3 全 stale clear 量化（686 articles × 5 lang = 3430 translations 涵蓋）：

- P0/P1 (~300 entries): Tier 1 cascade，~5 hr 集中 batch
- **P2 (~531 entries): Tier 0a diff-patch，~1.5 hr Sonnet sub-agents**（5x 加速）
- **P2.5 (~2431 entries): Tier 0b bump-source-sha，<1 min**（instant）

### 量化驗證（2026-05-09 batch2 — P2.5 全量 production-scale 驗證）

[PR #921](https://github.com/frank890417/taiwan-md/pull/921) 一次 ship Tier 0b production-scale 驗證：

- **2429 metadata-stale entries 全量 bump**（489 P2.5 articles × 5 langs，one-shot）
- **Wall-clock**：< 1 min（status.py JSON parse + 2429 single-line frontmatter writes）
- **Token cost**：$0（Tier 0b deterministic，0 LLM call）
- **Coverage delta**：stale 從 ~489 / lang 降到 ~157 / lang（**-67% per lang**）
- **Body 連續性**：100% preserved（bodyHash 沒變的前提即 Tier 0b 篩選條件）
- **Pre-commit**：1933 frontmatter validation pass / 26 pre-existing warnings（與 bump 無關）
- **驗證**：v3 設計從「賈永婕一篇 patch demo」躍升到「全 corpus P2.5 一次 clear」，Tier 0b 在大量低 entropy drift 場景**線性可放大**

對應認知層升級：

- **REFLEXES #53 v3.3 milestone**（2026-05-09 同日續工）：P2.5 production-scale 驗證
- **REFLEXES #9 延伸**：worktree 命名 `YYYYMMDD-{purpose-title}` 標準（codename 污染歷史 antipattern）
- LESSONS-INBOX：「v3 升級觸發 — 哲宇『翻譯策略也加上一個 diff patch，用子 agent 快速 patch diff 應該會是最好的做法』」

🧬

---

## v4.0 升級 — Translation backend abstraction layer（2026-05-12 admiring-montalcini-post-finale）

哲宇 callout 觸發：「儘可能模組化 抽象化 可抽換化 讓系統獨立於模型與服務類別能運作 並有彈性跟能隨時切換」。

### v3 → v4 演化觸發

2026-05-12 observer-driven `/twmd-babel` 撞兩個生態變動：

| Provider                   | 狀態                                 | 影響                          |
| -------------------------- | ------------------------------------ | ----------------------------- |
| `openrouter/owl-alpha`     | 🚨 全 keys 429 upstream rate-limited | Tier 1 主批整批 fail-fast     |
| `tencent/hy3-preview:free` | 🚨 轉付費（404 free tier）           | Tier 2 副批整批 404 fail-fast |

REFLEXES #45 預測過：「同 provider 多 model 共享 budget」+「rate-limited 後立刻降 concurrency 重試 = 沒用」。但 v3 沒給「換 provider class 整類」的路徑 — 只能等 cool-down 或退 Tier 4 Sonnet。

哲宇拍板：用個人 OpenAI 訂閱（codex CLI gpt-5.5）+ Google Workspace（gemini CLI）繞 OpenRouter — 系統若**獨立於 model/service** 就能彈性換 backend。

### 抽象層設計

```
scripts/tools/lang-sync/
├── backends/
│   ├── _base.py          ← TranslationBackend ABC + BackendCapabilities + 錯誤類別階層
│   ├── _prompt.py        ← 共用 prompt builder (re-exports from openrouter-translate.py)
│   ├── openrouter.py     ← OpenRouterBackend (multi-model via HTTP API + key rotation)
│   ├── codex.py          ← CodexBackend (gpt-5.5 via codex CLI subprocess)
│   ├── gemini.py         ← GeminiBackend (gemini-2.5-pro via gemini CLI subprocess)
│   └── ollama.py         ← OllamaBackend (local HTTP API, qwen3.6 default)
├── translate.py          ← 新 canonical entry point — cascade orchestrator
├── codex-translate.py    ← legacy thin wrapper (kept for back-compat)
├── openrouter-translate.py ← legacy thin wrapper (kept for back-compat + prompt SSOT)
└── ollama-translate.py   ← legacy thin wrapper (kept for back-compat)
```

### 抽象介面（TranslationBackend ABC）

```python
class TranslationBackend(ABC):
    CAPABILITIES: BackendCapabilities  # name, provider_kind, model, cost_kind,
                                       # typical_latency_s, max_context_chars,
                                       # prc_refusal_risk_low, multilingual_strength

    def is_available(self) -> bool: ...
    def cool_down_until(self) -> datetime | None: ...
    def translate(self, system, user, *, max_tokens, timeout) -> str: ...
    # raises BackendRateLimited / BackendRefusal / BackendTimeout / BackendBadOutput / BackendUnavailable
```

新 backend 加入 = 寫一個 subclass + register 進 `__init__.py`，不動 pipeline 任何其他地方。

### 模型 × 語言適配：同一個模型對不同語言的落差可以到十倍

2026-07-26 實測（免費雲端池，同批文章、同時段、n≈250）：

| 語言   | nemotron-3-ultra | laguna-xs | qwen3.6（本機） |
| ------ | ---------------: | --------: | --------------: |
| 越南語 |         **2-6%** |   **50%** |             28% |
| 印尼語 |           19-22% |       38% |             39% |

越南語在 nemotron 上的通過率只有印尼語的四分之一，而換成 laguna 就跳到 50%——
同一批文章、同一套閘門。**這不是佇列問題也不是文章難度問題，是模型與語言的適配
落差**，而它會偽裝成「這個語言比較難翻」的假象（越南語一度是十一語裡覆蓋率墊底，
落後同期出生的印尼語一大截）。

**操作規則**：任一語言的通過率明顯低於同批其他語言時，先按 worker 拆開看
（`report.jsonl` 的 `worker` 欄），不要直接歸因於語言難度或文章品質。若某模型
對該語言明顯偏弱，開專軌繞過它，而不是加大重試次數——重試只會讓同一個弱適配
再燒一次算力。

**誕生**：2026-07-26 vi 通過率 10% 追查。開 vi 專軌（laguna×2＋oss20，繞過
nemotron）後通過率 33%。

### 全表掃描：每個模型都有語言邊界

同日把 worker × lang 拉成全表（n≈900）後，弱適配不只 vi 一處：

| worker（模型）   | 擅長                                         | 幾乎不能用                             |
| ---------------- | -------------------------------------------- | -------------------------------------- |
| gemma4:26b       | 韓 58%／法 46%／西 38%／日 33%               | **葡 0/28、印尼 1/20、印地 0%、越 5%** |
| nemotron-3-ultra | 葡 45-60%／俄 46-51%／阿 42-57%／印地 23-44% | **越 2-6%**                            |
| laguna-xs        | 越 43%／印尼 38%／印地 36%／葡 33%           | （未見全滅組合，但整體量能低）         |
| qwen3.6（本機）  | 葡 50%／印尼 40%／法 37%／韓 37%             | （最平均，無明顯短板）                 |

**gemma4:26b 的邊界特別鋒利**：對「高資源歐洲語＋日韓」可用，對「東南亞＋南亞＋
葡語」接近全滅。它在混語佇列裡會持續消耗算力翻出必被擋下的成品——每一篇都是完整
的 GPU 時間加一次閘門檢查。

**操作規則**：產線編組**按模型的擅長語種切軌**，不要讓一個模型吃所有語言。
新模型進池時先跑一輪混語小批（每語 8-10 篇）拉出這張表再決定它的守備範圍。

### 入池門檻：模型級別不夠就不要放進來（2026-07-26 哲宇 directive）

> 「oss20 未來不要用，品質不夠。至少要 gemma4 / oss 120 / nemotron / qwen 等級，
> 不然會留很多問題債。」

**通過率不是唯一判準，模型級別是入池的前置門檻**。小模型即使偶爾通過閘門，產出的
譯文品質也在及格線邊緣——閘門擋得住結構錯誤與整段沒翻，擋不住「每句都翻了但讀起來
不對」。那些會落地成為讀者看到的內容，而且不會有人回報，是最難清的債。

**入池白名單（2026-07-26 起）**：

| 級別        | 模型                                                                                    | 用途                                                    |
| ----------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| ✅ 可入池   | `nemotron-3-ultra-550b`／`gemma4:26b`＋以上／`gpt-oss-120b`／`qwen3.6:35b`、`qwen3:32b` | 產線主力                                                |
| ✅ 條件可用 | `laguna-xs-2.1`                                                                         | 越南語專軌實測 43-71%，暫留觀察；若品質回報不佳一併撤下 |
| ❌ 不入池   | `gpt-oss-20b`（oss20）、`gemma4:12b` 等同級小模型                                       | 品質不足，任何情況都不派                                |

規則對本機 ollama 與雲端免費池一視同仁。缺算力時的正解是等額度或加機器，
不是降級模型——**降級換來的產能是負債不是資產**。

### 排序原則：全軍由新到舊（2026-07-27 哲宇 directive）

> 「我們是根據由新到舊的文章來翻對嗎（越近期的文章越完整、pipeline 也越新）」

佇列排序的第一性原理：**越新的文章價值密度越高**——內容經過越新的編輯標準、
寫作當時的 pipeline 品質閘門越完整、也越可能是讀者正要找的主題。所以所有產線
一律 `--order forward`（zh 最後編輯時間新→舊）。

歷史包袱：早期曾讓部分軌道跑 `reverse`（從最舊開始），用「兩端夾擊」避免多軌
撞同一篇。跨引擎去重＋共享失敗記憶上線後，撞車保護已由機制承擔，不再需要犧牲
排序換取。**四層排序鍵最終為**（2026-07-27 補新鮮窗）：

1. **失敗次數**（撞牆多的沉底，不排除）
2. **新鮮窗**：zh 最後編輯在 5 天內的文章整批插隊到最前，凌駕 P0/P1
   （哲宇 directive「最近 5 天內的最新文章排最高優先序，日期近的更前面」）
   ——剛寫好或剛大修的文章是讀者當下會看的，也是站上編輯標準最新的一批，
   晚一天翻就少一天的多語觸及。窗內**純日期序不再分 P0/P1**：窗內若再按
   缺頁/過期分層，昨天的缺頁會插到今天的過期前面，違反本意
3. **P0/P1**（缺頁先於過期）——窗外才適用
4. **zh 編輯時間**（新→舊）

窗口大小 `FRESH_WINDOW_DAYS`（babel-dispatch.py）。實測十一語各有 10-14 篇
在窗內，隊首驗證：全部佔據前段且日期嚴格遞減。

### 編組原則：單 worker 專軌是脆弱的

按擅長語種切軌是對的，但**一條軌只放一個 worker 會把節點級故障放大成整軌停擺**。
2026-07-26 實撞兩次：l4090 專軌的遠端機器端點不通，該軌唯一 worker 被凍結後
整條產線空轉（第一次無人察覺 127 輪，第二次靠當日新增的零產出偵測自動收工）。

**正解是讓擅長語種重疊的 worker 共用一條軌**——它們本來就在搶同一批任務，
放同一個佇列還能互相補位。l4090（gemma4:26b）與 d3090（qwen3:32b）在
日韓西法都有 43-59%，合併成雙 GPU 歐日韓軌之後，任一台掛掉另一台繼續消化，
佇列不會空轉。

單 worker 專軌只在「該 worker 的擅長語種無人重疊」時才合理（如越南語只有
laguna 能打，但那條軌用了 laguna×3 三個併發，同樣不是單點）。

## Cascade orchestrator

```python
cascade = build_cascade("codex,openrouter:owl-alpha,openrouter:openai/gpt-oss-120b:free,gemini,ollama")
output, backend_used = cascade.translate(system, user)
```

每個 backend 自報 `is_available()` + 自管 `cool_down_until()`，cascade 跳過不 available / cooling 的，第一個 success 即返回。

Cascade syntax `name[:option]`：

- `codex` — OpenAI gpt-5.5 via subscription
- `openrouter:openrouter/owl-alpha` — OpenRouter stealth provider
- `openrouter:openai/gpt-oss-120b:free` — OpenRouter free OpenAI open weights
- `gemini[:model]` — Google Gemini via subscription
- `ollama[:model]` — local Ollama (default qwen3.6:35b-a3b)

### Default cascade 推薦順序（v4.2 2026-05-16 哲宇 callout「codex + gemini 為優先」）

```
1. codex (gpt-5.5)                      — subscription, top quality, ~100% Taiwan pass
2. gemini (gemini-2.5-pro)              — Google subscription backup (對 sensitive 主題待 calibrate)
3. openrouter:openrouter/owl-alpha      — verified free, 1M ctx, rate-limit-prone (REFLEXES #45)
4. openrouter:openai/gpt-oss-120b:free  — verified free fallback (Hy3 退役後 Tier 2)
5. ollama:qwen3.6:35b-a3b-coding-nvfp4  — sovereignty backbone, 0 refusal（需 `ollama serve` 啟動）
```

理由：start with subscription priority (codex + gemini, no rate-limit drama) → free-tier verified middle layer (owl + gpt-oss) → local fallback. 觀察者可改 cascade 平衡 cost vs latency vs quality。

**驗證佇列 model 不在 default cascade**：避免無 calibration 的 backend 拖慢 happy path。要驗證新 model 走 `--cascade openrouter:{NEW_MODEL}` explicit override + §驗證 SOP test set。

### v4 工作流（取代 v3 Stage Z2 dispatch）

```bash
# 取代「bash openrouter-batch.sh ja openrouter/owl-alpha」這條
python3 scripts/tools/lang-sync/translate.py --group .lang-sync-tasks/ja/_group-A.json

# 自訂 cascade（cost-first：先免費後付費）
python3 scripts/tools/lang-sync/translate.py --group ... \
  --cascade "openrouter:openai/gpt-oss-120b:free,ollama,codex"

# 單篇測試
python3 scripts/tools/lang-sync/translate.py --zh-path Society/颱風假.md --lang ja --cascade codex
```

### 為什麼這個 refactor 必要

| v3 pain                                                | v4 解                                                 |
| ------------------------------------------------------ | ----------------------------------------------------- |
| `owl-alpha → Hy3` 寫死在 `openrouter-batch.sh`         | Backend = plug-in，pipeline 跑 cascade                |
| Hy3 轉付費 → 整 pipeline 卡                            | Backend `is_available()` 自報 → cascade 跳過          |
| 加 codex / gemini 要寫新 worker script                 | 寫個 backend class 即接入 cascade                     |
| `REFLEXES #49 4-tier cascade canonical` 改要改 N 個檔  | DNA 改成 abstract pattern，concrete 在 cascade config |
| Per-provider rate budget / refusal logic 散在多 script | 集中在 `_base.py` 錯誤類別階層 + cool_down 機制       |

### Hy3 退役紀錄（2026-05-12）

`tencent/hy3-preview:free` 在 2026-05 從 OpenRouter free tier 移到付費。所有引用此 model id 的舊 doc 視為 historical 證據鏈，**新 dispatch 不再使用**。對應 REFLEXES #49 4-tier cascade 的 Tier 2 默認改為 `openai/gpt-oss-120b:free`（同 OpenRouter 但獨立 model line）。

### 跟 DNA 反射的關係

| DNA #N | 關聯                          | v4 影響                                                       |
| ------ | ----------------------------- | ------------------------------------------------------------- |
| #39    | Self-as-fallback              | cascade 的核心思想 — backend 是 fallback 路徑首選             |
| #45    | OpenRouter rate budget hourly | 只 apply OpenRouterBackend；其他 backend 不受影響             |
| #49    | 4-tier cascade canonical      | v4 變 N-tier abstract（具體 tier 在 cascade config 不在 DNA） |

---

_v4.5 | 2026-07-18 184501-manual（巴別塔健檢）— 首次完整健檢的經驗回寫：(1) cascade 番號對賬——doc 漏列 DEFAULT_CASCADE 已收編的 fleet、「Tier 5」被 fleet 與 Sonnet 雙重佔用，對齊 production_signal 並把 Sonnet 正名 Tier 6（制度化待 OBSERVER-QUEUE #18）；(2) Tier 0a prompt template 補 Step 1b/1c 硬底（batch JSON 跨 entry 汙染驗證 + scratch 檔唯一前綴，收償 LESSONS 2026-07-14 兩條）；(3) 新增 §健檢儀器 babel-health.py（六維 WARN 級）。健檢完整報告與產線 14 天考古：[reports/babel-health-2026-07-18.md](../../reports/babel-health-2026-07-18.md)_

_v4.4 | 2026-07-05 2026-07-05-165518-五病根治 — #56 復發修補：doc 對齊 translate.py v4.3（owl-alpha 移出 default / gpt-oss-120b 單獨扛 Tier 2 / preflight 冷凍入 spine / cascade 範例改 DEFAULT_CASCADE_ID 逐字）+ audit-quality.py 兩處「待造/待建」修正（工具 5/13 已存在）+ qwen Tier 4 主權定位標 pending 哲宇決策 4（fleet 端 6/14 bench 後 gemma4-only）+ frontmatter 新增 production_signal 欄。歷史段搬 reports/ 瘦身（~-375 行）另排 P1-19。_

_v4.2 | 2026-05-16 2026-05-16-011113-manual — Inventory recalibration + 驗證佇列 SOP_
_升級觸發：哲宇 callout「不確定現在仍有什麼免費模型在運作，先調查一輪」+「codex + gemini 為優先，其他免費模型要驗證＋品質從高排到低」_
_核心動作：(1) 直接打 OpenRouter `/api/v1/models` API 確認 24 個 `:free` model 當前 inventory（取代 v3 已過時的 28 model 候選清單）(2) Hy3 / Llama-3.3-70b / Hermes-3-405b / Gemma-4-31b / Nemotron-3-Super-120B 現況逐一 cross-check (3) §已驗證模型 table 重寫成 Tier 1-3 三段（subscription / verified free / 驗證佇列）(4) §驗證 SOP 新章節 — standardized test set + scoring criteria + 失敗處置 (5) v2.0 4-tier cascade canonical 標 historical + v4.2 取代版本緊接 (6) Default cascade 移 gemini up to Tier 1 旁邊 (7) translate.py DEFAULT_CASCADE_ID 同步_
_v4.2 verified Tier 1-2 ({codex, gemini} / {owl-alpha, gpt-oss-120b:free})，pending Tier 3 fleet ({hermes-3-405b, llama-3.3-70b, nemotron-3-super-120b, gemma-4-31b, deepseek-v4-flash, qwen3-next-80b})_
_誕生背景：今早 babel-nightly 150 cascade ship 0 fail 證實 v4.0 cascade 健康，但 §已驗證模型 table 仍寫 Hy3 + 28 個未測 free model，與 production 實況脫節；本次 inventory recalibration 把 pipeline canonical 對齊到 2026-05-16 真實生態，並為「下一批驗證」建立可重複的 SOP_

---

_v4.0 | 2026-05-12 admiring-montalcini-post-finale_
_升級觸發：codex pivot session — owl-alpha + Hy3 雙生態變動 → 哲宇 callout「儘可能模組化 抽象化 可抽換化」_
_核心洞察：(1) v3 把 Tier 1-4 cascade 寫死 = brittle to provider ecosystem drift (2) Abstract backend interface 把「換 provider」從 pipeline 重寫變成 cascade config 一行 (3) `is_available()` + `cool_down_until()` self-report = cascade 自動避開壞掉的層，無需 pipeline 知道_
_v4 新檔：`backends/{_base,_prompt,openrouter,codex,gemini,ollama}.py` + `translate.py`（新 canonical entry）_

---

_v3.0 | 2026-05-09 laughing-goldstine post-finale_
_升級觸發：哲宇「翻譯策略也加上一個 diff patch，用子 agent (小幅度更新) sonnet 快速的 patch diff 應該會是最好的做法」+「優先排序：缺口 → 大幅更新 → 小幅／腳註 → 舊」+「自我演化 DNA 跟紀錄」_
_核心洞察：v2 把所有 babel 任務當「翻譯」處理是 over-spec — P2/P2.5 不需要 full re-translate，patch + bump 就夠且更安全（preserves unchanged paragraphs，避免 LLM drift）_
_v3 工具新增：prioritize-batch.py（智慧分流）+ diff-patch-prepare.py（Tier 0a 任務準備）；bump-source-sha.py（Tier 0b deterministic）已存在 reuse_
