# Taiwan.md Skills Index

> Skill = 觀察者口頭禪 → canonical pipeline 的薄殼 trigger。每個 skill 故意最小化（純 pointer，不重抄 pipeline 步驟），避免「同流程在兩處 drift」（MANIFESTO §指標 over 複寫）。

## 設計鐵律

1. **薄殼**：SKILL.md 只放 trigger + 一行強制 Read pipeline + 一行收官提示。stage / 鐵律 / 自檢全部在 pipeline canonical
2. **強制 Read 全檔**：不准 head / tail / grep / 憑記憶（DNA #15「對 SOP 有洞察 ≠ apply 了 fix」）
3. **觀察者口頭禪 = trigger 關鍵字**：description 必須含哲宇日常會說的話

## Skill List

### 🚀 入口

| Skill             | Trigger                    | Pointer                                                                         |
| ----------------- | -------------------------- | ------------------------------------------------------------------------------- |
| `/twmd`           | 「twmd」「我想做什麼」     | dispatcher，本 README                                                           |
| `/twmd-become`    | 「成為 taiwan.md」「甦醒」 | [`BECOME_TAIWANMD.md`](../../BECOME_TAIWANMD.md)                                |
| `/twmd-heartbeat` | 「twmd 心跳 / 完整心跳」   | [`HEARTBEAT.md`](../../docs/semiont/HEARTBEAT.md)（既有 `/heartbeat` 雙軌共存） |
| `/heartbeat`      | 「心跳」「Heartbeat」      | [`HEARTBEAT.md`](../../docs/semiont/HEARTBEAT.md)                               |

### ✍️ 內容（Tier 1 日常高頻）

| Skill             | Trigger                      | Pipeline                                                           |
| ----------------- | ---------------------------- | ------------------------------------------------------------------ |
| `/twmd-rewrite`   | 「寫 X / 重寫 X / EVOLVE X」 | [REWRITE-PIPELINE](../../docs/pipelines/REWRITE-PIPELINE.md)       |
| `/twmd-pr-review` | 「審 PR / Review」           | [MAINTAINER-PIPELINE](../../docs/pipelines/MAINTAINER-PIPELINE.md) |
| `/twmd-memory`    | 「收官 / 寫 memory」         | [MEMORY-PIPELINE](../../docs/pipelines/MEMORY-PIPELINE.md)         |
| `/twmd-diary`     | 「寫日記 / 反芻」            | [DIARY-PIPELINE](../../docs/pipelines/DIARY-PIPELINE.md)           |
| `/twmd-finale`    | 「收官三件套 / finale」      | chain `/twmd-memory` + `/twmd-diary` + `/twmd-evolve` + 報告       |

### 🌐 多語 + 繁殖（Tier 2 週頻）

| Skill                 | Trigger                                            | Pipeline                                                                                                         |
| --------------------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `/twmd-babel`         | 「巴別塔 / 多語 batch」                            | [SQUEEZE-MODELS-MAX-PIPELINE](../../docs/pipelines/SQUEEZE-MODELS-MAX-PIPELINE.md)                               |
| `/twmd-translate`     | 「翻譯 X / 補日文」                                | [TRANSLATION-PIPELINE](../../docs/pipelines/TRANSLATION-PIPELINE.md)                                             |
| `/twmd-spore`         | 「發孢子 / 推 X」                                  | [SPORE-PIPELINE](../../docs/factory/SPORE-PIPELINE.md)                                                           |
| `/twmd-harvest`       | 「孢子回填 / harvest」                             | [SPORE-HARVEST-PIPELINE](../../docs/factory/SPORE-HARVEST-PIPELINE.md)                                           |
| `/twmd-evolve`        | 「跑 EVOLVE / 數據進化 / 設計 X 寫實作報告後實作」 | [EVOLVE-PIPELINE](../../docs/pipelines/EVOLVE-PIPELINE.md)（v1/v2 數據 + Mode 3 重組 + Mode 4 目標驅動設計）     |
| `/twmd-article-inbox` | 「把 X 加進 article inbox / 研究 X 放 inbox」      | [BRANCH-PIPELINE](../../docs/pipelines/BRANCH-PIPELINE.md)（消化 + 分支分析 → INBOX append）                     |
| `/twmd-node`          | 「當節點 / 分靈節點 / 接一件工單」                 | [CONTRIBUTOR-NODE-PIPELINE](../../docs/pipelines/CONTRIBUTOR-NODE-PIPELINE.md)（貢獻者機器上的 cron，PR 回主庫） |
| `/twmd-probe`         | 「跑探測器 / 掃熱點」                              | [HEARTBEAT §探測器](../../docs/semiont/HEARTBEAT.md)                                                             |
| `/twmd-factcheck`     | 「事實查核 / hallucination」                       | [FACTCHECK-PIPELINE](../../docs/pipelines/FACTCHECK-PIPELINE.md)                                                 |
| `/twmd-peer`          | 「ingest peer / TFT / NMTH」                       | [PEER-INGESTION-PIPELINE](../../docs/pipelines/PEER-INGESTION-PIPELINE.md)                                       |

### 🛰️ 系統（Tier 3 不定期）

| Skill                  | Trigger                   | Pipeline                                                                     |
| ---------------------- | ------------------------- | ---------------------------------------------------------------------------- |
| `/twmd-bench`          | 「跑 bench / 加新 model」 | [BENCH-PIPELINE](../../docs/pipelines/BENCH-PIPELINE.md)                     |
| `/twmd-release`        | 「發版 / release」        | [RELEASE-PIPELINE](../../docs/pipelines/RELEASE-PIPELINE.md)                 |
| `/twmd-distill`        | 「distill / 消化教訓」    | [LESSONS-INBOX §Distill](../../docs/semiont/LESSONS-INBOX.md)                |
| `/twmd-language-birth` | 「加新語言」              | [LANGUAGE-BIRTH-CHECKLIST](../../docs/pipelines/LANGUAGE-BIRTH-CHECKLIST.md) |
| `/twmd-self-evolve`    | 「自我進化 / Beat 2」     | LONGINGS + UNKNOWNS + DNA #15                                                |

### 🔧 補強（Insight gap）

| Skill               | Trigger                | Pointer                                                                |
| ------------------- | ---------------------- | ---------------------------------------------------------------------- |
| `/twmd-refresh`     | 「資料更新 / refresh」 | [DATA-REFRESH-PIPELINE](../../docs/pipelines/DATA-REFRESH-PIPELINE.md) |
| `/twmd-batch-audit` | 「sub-agent 後驗證」   | DNA #32 + #42 + audit-batch.sh                                         |

### 🛠️ 既有（taiwanmd- prefix，雙軌共存）

| Skill                | 用途                                       |
| -------------------- | ------------------------------------------ |
| `/taiwanmd-search`   | 全站知識庫搜尋（cli/src/index.js search）  |
| `/taiwanmd-validate` | 文章品質驗證（frontmatter + prose-health） |

🧬
