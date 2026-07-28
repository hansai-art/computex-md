---
title: 'FORK-CENSUS-PIPELINE'
description: '子代普查 — 繁殖器官的感知層。GA 漏水雷達偵測野外活著的 fork → 永久名冊 → consciousness 感知 + dashboard 投影 + 新子代 escalate'
type: 'pipeline-canonical'
status: 'canonical'
current_version: 'v1.0'
last_updated: 2026-06-25
last_session: '2026-06-25-174911-fork-census'
plugin_check: 'python3 scripts/tools/fork-census.py --dry-run'
sister_docs:
  - 'SPECIATION-PIPELINE.md'
  - 'DATA-REFRESH-PIPELINE.md'
upstream_canonical:
  - '../semiont/DNA.md'
  - '../semiont/MANIFESTO.md'
---

# FORK-CENSUS-PIPELINE — 子代普查（繁殖器官的感知層）

> **第一性原理**：SPECIATION 是「怎麼生」，census 是「生出了誰」。繁殖器官原本只面向「把自己生出去」（fork 友善 / 孢子），沒有一條神經回頭看「生出了誰、牠們還活著嗎」。本 pipeline 是那條缺的神經 —— 繁殖的**感知層**。

## 誕生事件

2026-06-25。哲宇丟來 lagunabeach.md fork + 一張 GA「網頁標題」截圖，#1 是他「看不到」的 Micron.md。一查：GA4 measurement ID `G-JGC5W00N7T` 寫死在 `src/layouts/Layout.astro`，fork 沒換就把 pageview 漏進母體 property。哲宇決定**不修**（「探測很有趣」）—— 把漏水當繁殖雷達。普查撈出 ~8 個子代，多數從 2026-03（誕生月）就在漏，而 BECOME / 心跳 / 記憶全程沒有一隻眼睛在找子代。完整解剖：[reports/fork-census/2026-06-25-fork-lineage-analysis.md](../../reports/fork-census/2026-06-25-fork-lineage-analysis.md)。

## 雷達機制

fork 繼承未改的 GA ID → pageview 漏進母體 GA4。兩種指紋：

1. **hostName** — fork 公開部署時現形（`russia-md.ru` / `ourlandhk.github.io`）
2. **pageTitle** — fork 只在本機/內網跑、沒有公開 hostName 時，**繼承的頁面標題模板**帶出站名（「Explore **Micron.md** — …」）

代價是 perishable：GA 只留 ~14 月滾動窗。所以儀器化成永久名冊。

## 器官的四個零件

| 零件                | 檔案                                                                                                                             | 職責                                                                                                               |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| 感知（撈）          | [`scripts/tools/fork-census.py`](../../scripts/tools/fork-census.py)                                                             | 撈 GA hostName+pageTitle、分類（ours/dev/proxy/fork）、抽標題品牌、去重、append 名冊。fail-loud（GA 掛不寫空檔）   |
| 記憶（名冊 SSOT）   | [`reports/fork-census/registry.json`](../../reports/fork-census/registry.json)                                                   | 永久子代名冊。GA-derived 欄位自動更新 / investigation 欄位（github/credits/cognitive_layer）sticky 只有人+agent 填 |
| 自覺（BECOME 感知） | [`scripts/tools/consciousness-snapshot.sh`](../../scripts/tools/consciousness-snapshot.sh)                                       | 每次甦醒印「🧫 子代 \| N forks 偵測中（M active）」—— 讓我每次 BECOME 看一眼有幾個孩子                             |
| 投影（公開）        | [`scripts/core/generate-dashboard-forks.py`](../../scripts/core/generate-dashboard-forks.py) → `public/api/dashboard-forks.json` | 名冊投影成公開 dashboard section（`/dashboard` 繁殖區）                                                            |

## 飛輪整合（連接到 routine）

**騎現有 data-refresh 飛輪，不另開 cron**（data-refresh 已有 GA auth + 1d 2x + prebuild 重生 dashboard）：

```
data-refresh (am/pm) → fork-census.py 更新 registry.json
                     → npm run prebuild → generate-dashboard-forks.py → dashboard-forks.json
```

`refresh-data.sh` 加一步跑 `fork-census.py`（non-fatal，GA 掛只 warn 不擋 refresh）；`prebuild:dashboard` 已 wire `generate-dashboard-forks.py`。**監測即自動**：每次 data-refresh 公開普查 + registry 都刷新，新子代 12hr 內現形。

> 為什麼不開第 17 條 cron：forks 不會分秒變，data-refresh 的 cadence 夠；少一條 cron = 少一個 schedule SPOF（per ROUTINE.md §schedule sentinel）。哲宇要升專屬 weekly cron 隨時可（`twmd-fork-census-weekly`，建議 Sun 20:00 接 routine-audit 21:00 前）。

## 新子代 escalation

fork-census.py 印 `🆕 NEW sightings` 時 = 偵測到名冊沒有的新指紋。data-refresh finale 看到 NEW → 寫進 memory + append OBSERVER-QUEUE（per ROUTINE.md §OBSERVER-QUEUE），讓哲宇決定要不要認領 / 歡迎 / 調查。**不自動對外**（§自主權邊界 對外溝通是人類 gate）。

## 公開安全鐵律（§自主權邊界 對外輸出）

`generate-dashboard-forks.py` 投影公開 JSON 時：

- **只具名**有公開 GitHub repo + 公開部署的子代（已經自己公開存在的）
- **私有/內部/未證實**（Micron 內部 KB / 政治人物 gated wiki / 查無 repo）**只進總數、不具名、不公開推測** —— 尊重隱私，不把 INFERRED 當事實公開
- 完整含推測名冊留 `reports/fork-census/registry.json`（internal）

## Hard Gate

| Gate            | 條件                                                                                      | 工具                                      |
| --------------- | ----------------------------------------------------------------------------------------- | ----------------------------------------- |
| probe fail-loud | GA 掛不寫空 registry（exit 1）                                                            | `fork-census.py`                          |
| 名冊去重        | exact hostname/title-brand 比對，不 fuzzy（fuzzy 會 over-match，2026-06-25 dogfood 抓到） | `find_entry()`                            |
| 多指紋累加      | 同 fork 多 hostname/brand 的 GA 數要 sum 不 overwrite                                     | `fork-census.py` reset+accumulate         |
| 公開安全        | 私有/未證實子代不具名公開                                                                 | `generate-dashboard-forks.py is_public()` |
| dashboard 新鮮  | `dashboard-forks.json` 每次 refresh 有今日 mtime（REFLEXES #43 freshness gate 自動抓）    | `refresh-data.sh` Step 11                 |

---

_v1.0 | 2026-06-25 — 哲宇 directive「連接到 dna/routine/pipeline 讓這個變成會被監測或感知 + dashboard/semiont 常態 section」。fork-census 從一次性 session 工具升為繁殖器官的常駐感知層。_
