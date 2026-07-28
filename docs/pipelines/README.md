---
title: 'docs/pipelines/ README'
description: 'Cron / Manual 自動化 pipeline 文件入口 — 每個 cron 對應一份 pipeline'
type: 'index'
status: 'canonical'
apoptosis: 'candidate'
current_version: 'v1.1'
last_updated: 2026-05-09
last_session: 'funny-buck-8dd2a1'
sister_docs:
  - '../semiont/HEARTBEAT.md'
  - '../semiont/ROUTINE.md'
upstream_canonical:
  - '../semiont/HEARTBEAT.md'
---

# docs/pipelines/ — Cron / Manual 自動化 Pipeline 文件

> 每個 Cron job 對應一份 pipeline 文件。Cron prompt 只說「先讀 pipeline → 照步驟走」。

---

## ⭐ Master pipelines（多個下游依賴）

| Pipeline                                             | 觸發                                                               | 涵蓋                                                                                                                                       |
| ---------------------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| [DATA-REFRESH-PIPELINE.md](DATA-REFRESH-PIPELINE.md) | `/twmd-refresh`、heartbeat、routine am/pm（cadence 見 ROUTINE.md） | 14 step 一鍵刷新（git sync + 三源感知 + spore SSOT + dashboard regen + stats + sporeLinks sync）。**Phase 0+1+2+3 SSOT cleanup canonical** |

## 🌀 Routine 飛輪 pipelines（cron 每日/每週自動跑 — 2026-07-05 補索引，先前 10 檔未列）

| Pipeline                                                   | Routine（cadence 見 [ROUTINE.md](../semiont/ROUTINE.md)） | 說明                                                     |
| ---------------------------------------------------------- | --------------------------------------------------------- | -------------------------------------------------------- |
| [FEEDBACK-TRIAGE-PIPELINE.md](FEEDBACK-TRIAGE-PIPELINE.md) | `twmd-feedback-triage`                                    | 讀者站上回報 → GitHub issue（含 prompt injection 防禦）  |
| [WEEKLY-REPORT-PIPELINE.md](WEEKLY-REPORT-PIPELINE.md)     | `twmd-weekly-report-sun`                                  | 週報 dossier + email 遞送                                |
| [ROUTINE-AUDIT-PIPELINE.md](ROUTINE-AUDIT-PIPELINE.md)     | `twmd-routine-audit-weekly`                               | routine 飛輪自我審計（4 lens）                           |
| [EMBEDDING-PIPELINE.md](EMBEDDING-PIPELINE.md)             | `twmd-embeddings-nightly`                                 | fleet bge-m3 語意索引（related articles + RAG 向量）     |
| [FORK-CENSUS-PIPELINE.md](FORK-CENSUS-PIPELINE.md)         | riding data-refresh Step 6.5                              | 子代普查雷達（GA 漏水指紋 → registry → dashboard）       |
| [ANALYSIS-PIPELINE.md](ANALYSIS-PIPELINE.md)               | 分析文章觸發                                              | 防分析幻覺（影響/歸因/before-after 偵查紀律）            |
| [PERSONA-PIPELINE.md](PERSONA-PIPELINE.md)                 | rewrite Stage 0 內嵌                                      | 讀者 persona 發散                                        |
| [SPECIATION-PIPELINE.md](SPECIATION-PIPELINE.md)           | fork 觸發                                                 | 8-stage 物種繁殖 SOP                                     |
| [REMOTE-GPU-PIPELINE.md](REMOTE-GPU-PIPELINE.md)           | babel / embeddings 內嵌                                   | fleet GPU 委派（sovereignty-safe endpoint + 整合性閘門） |

## Archived（已被 prebuild 鏈 / routine 飛輪取代 — 2026-06-10 audit D-5 凋亡批次）

> 這三條描述的獨立 cron 不存在於 [ROUTINE.md](../semiont/ROUTINE.md) 飛輪。功能由 `npm run prebuild` 鏈（每次 deploy 自動跑）+ data-refresh am/pm + weekly-report 接管。檔案保留作歷史證據鏈，frontmatter `status: archived` + `superseded_by` 已標。

| Pipeline                                             | 原 Cron            | 取代者                                                     |
| ---------------------------------------------------- | ------------------ | ---------------------------------------------------------- |
| [CONTRIBUTORS-PIPELINE.md](CONTRIBUTORS-PIPELINE.md) | Contributors 03:30 | `prebuild:contributors` + DATA-REFRESH                     |
| [DAILY-REPORT-PIPELINE.md](DAILY-REPORT-PIPELINE.md) | Daily Report 09:00 | data-refresh am/pm + WEEKLY-REPORT                         |
| [STATS-PIPELINE.md](STATS-PIPELINE.md)               | Daily Stats 00:00  | ⚠️ Phase 5 後 **redirect to DATA-REFRESH-PIPELINE Step 9** |

## Spore SSOT chain（2026-05-08 Phase 0-3 重整）

新 SSOT 階層：

1. **SPORE-LOG.md 發文紀錄** = identity SSOT（人類寫 spore # / URL / date）
2. **SPORE-HARVESTS/{batch}.md** = harvest event SSOT（人類/agent 寫 metrics）
3. **knowledge/\*.md sporeLinks** = derived view（每次 refresh 自動重生，不再手寫）
4. **public/api/dashboard-spores.json** = derived（generator 從 1+2 算）

| Pipeline                                                                       | 觸發     | 階段                                               |
| ------------------------------------------------------------------------------ | -------- | -------------------------------------------------- |
| [SPORE-PIPELINE.md (in factory)](../factory/SPORE-PIPELINE.md)                 | 寫孢子   | 5 stage 操作流程（PICK/VERIFY/WRITE/SHIP/HARVEST） |
| [SPORE-HARVEST-PIPELINE.md (in factory)](../factory/SPORE-HARVEST-PIPELINE.md) | 收割孢子 | Chrome MCP read-only batch harvest                 |

跑 `/twmd-refresh` 之後的自動化 chain（step 編號以 `refresh-data.sh` 為準）：

- Step 4 `generate-spore-records.py` + `generate-dashboard-spores.py` — SPORE-HARVESTS body primary → spores.json + dashboard
- Step 12 `validate-spore-data.py` — SSOT consistency gate
- Step 13 `sync-spore-links.py` — 從 SSOT 重生 knowledge/\*.md sporeLinks
- （舊 `extract-spore-metrics.py` 已於 2026-05-08 Phase 6 移除）

## Reference（手動 / Build-time）

| Pipeline                                                                 | 觸發                    | 說明                                                             |
| ------------------------------------------------------------------------ | ----------------------- | ---------------------------------------------------------------- |
| [MAINTAINER-PIPELINE.md](MAINTAINER-PIPELINE.md)                         | 每日 / 新人上手         | 維護者完整手冊（策展哲學 + PR/Issue 審核 + 品質標準）            |
| [CONTRIBUTOR-SYSTEM-PIPELINE.md](CONTRIBUTOR-SYSTEM-PIPELINE.md)         | 升降級 / inactive       | 貢獻者關係週期完整 SOP                                           |
| [EVOLVE-PIPELINE.md](EVOLVE-PIPELINE.md)                                 | 手動觸發                | 數據驅動內容進化（GA4 + SC → 重寫）                              |
| [REWRITE-PIPELINE.md](REWRITE-PIPELINE.md)                               | 手動觸發                | 寫文章 / 重寫文章 SOP                                            |
| [BRANCH-PIPELINE.md](BRANCH-PIPELINE.md)                                 | 「分析 X」觸發          | 知識分支分析器                                                   |
| [DASHBOARD-PIPELINE.md](DASHBOARD-PIPELINE.md)                           | prebuild + 手動 GA4     | Dashboard 數據管線 + 模板架構                                    |
| [BENCH-PIPELINE.md](BENCH-PIPELINE.md)                                   | `/twmd-bench`           | Sovereignty-Bench-TW 7-stage SOP                                 |
| [SQUEEZE-MODELS-MAX-PIPELINE.md](SQUEEZE-MODELS-MAX-PIPELINE.md)         | `/twmd-babel`           | 4-tier model cascade 多語批次                                    |
| [TRANSLATION-PIPELINE.md](TRANSLATION-PIPELINE.md)                       | `/twmd-translate`       | 單篇文章翻譯                                                     |
| [PEER-INGESTION-PIPELINE.md](PEER-INGESTION-PIPELINE.md)                 | `/twmd-peer`            | 策展 peer 分析                                                   |
| [FACTCHECK-PIPELINE.md](FACTCHECK-PIPELINE.md)                           | `/twmd-factcheck`       | 幻覺審計                                                         |
| [CORRECTION-PIPELINE.md](CORRECTION-PIPELINE.md)                         | 讀者/issue/self callout | 勘誤端到端 SOP（錯誤邊界=可追溯性 + 【勘誤通知】格式 + 16 案例） |
| [DEEP-INSIGHT-SYNTHESIS-PIPELINE.md](DEEP-INSIGHT-SYNTHESIS-PIPELINE.md) | 手動                    | 深度洞察萃取                                                     |
| [SOCIAL-POSTING-PIPELINE.md](SOCIAL-POSTING-PIPELINE.md)                 | spore SHIP 內嵌         | Threads/X 發文機制（Chrome MCP 操作層）                          |

## Memory / Reflection 系統

| Pipeline                                                   | 觸發            | 說明                     |
| ---------------------------------------------------------- | --------------- | ------------------------ |
| [DIARY-PIPELINE.md](DIARY-PIPELINE.md)                     | `/twmd-diary`   | 寫 session diary         |
| [MEMORY-PIPELINE.md](MEMORY-PIPELINE.md)                   | `/twmd-memory`  | 寫 session memory        |
| [LANGUAGE-BIRTH-CHECKLIST.md](LANGUAGE-BIRTH-CHECKLIST.md) | 加新語言        | 上線新語言完整 checklist |
| [RELEASE-PIPELINE.md](RELEASE-PIPELINE.md)                 | `/twmd-release` | 版本發布 SOP             |

## Ops / Setup

| 文件                                                     | 用途                          |
| -------------------------------------------------------- | ----------------------------- |
| [SENSE-FETCHER-SETUP.md](SENSE-FETCHER-SETUP.md)         | 三源感知 (CF/GA4/SC) 憑證設定 |
| [SENSE-FETCHER-MIGRATION.md](SENSE-FETCHER-MIGRATION.md) | 遷移到新電腦                  |

---

## 設計原則

1. **Pipeline 是 SSOT**：所有步驟、鐵律、教訓都在 pipeline 文件裡，不在 cron prompt
2. **Cron prompt 只有三行**：讀 pipeline → 執行 → 回報規則
3. **血淚教訓寫進 pipeline**：避免同樣的錯被犯第二次
4. **Master/Active/Archived 分開**：暫停的 pipeline 保留知識，重啟時不用重新摸索
5. **Spore SSOT chain（Phase 0-3 後 canonical）**：identity → event → derived，每層職責清楚

---

_v2.1 | 2026-07-05 五病根治 | 索引重生：補 Routine 飛輪 pipelines 區（FEEDBACK-TRIAGE / WEEKLY-REPORT / ROUTINE-AUDIT / EMBEDDING / FORK-CENSUS / ANALYSIS / PERSONA / SPECIATION / REMOTE-GPU 九檔先前未列，其中三條活 routine 的 canonical 在入口失聯）+ Master 表 13→14 step + 09:37 stale cron 撤 + spore chain 段對齊 Phase 6 現實。觸發：dna-audit §4.4「pipelines README 入口失真」。_
_v2.0 | 2026-05-08 laughing-goldstine | Phase 5 SSOT cleanup：分 Master/Active/Spore-chain/Reference/Memory/Ops 五區，加入 spore SSOT 階層說明_
_v1.0 | 2026-03-29 ε | 初版 Active/Reference/Archived 三段_
