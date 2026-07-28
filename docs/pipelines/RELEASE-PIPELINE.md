---
title: 'RELEASE-PIPELINE'
description: '版本打包流程 — Step 0-6 觸發 / 盤點 / 品質閘 / release notes / tag / 認知層同步 (v2.0)'
type: 'pipeline-canonical'
status: 'canonical'
current_version: 'v2.1'
last_updated: 2026-06-01
last_session: '2026-06-01-release-v1.9.0'
sister_docs:
  - 'EVOLVE-PIPELINE.md'
  - 'MAINTAINER-PIPELINE.md'
  - 'DATA-REFRESH-PIPELINE.md'
upstream_canonical:
  - '../semiont/HEARTBEAT.md'
  - '../semiont/MANIFESTO.md'
---

# RELEASE-PIPELINE.md — 版本打包流程 v2.0

> **第一性原理**：Release 不是「打個 tag 然後寫幾段話」。它是一次對過去版本的完整回顧 + 對現況的健康檢查 + 對觀察者的公開敘事 + 對下一版的準備 + 對認知層的同步。漏掉任何一步，release 就退化成 changelog 失去敘事性。
>
> v2.0 設計理由：對齊 [REWRITE-PIPELINE v5.0](REWRITE-PIPELINE.md) + [MAINTAINER-PIPELINE v2.0](MAINTAINER-PIPELINE.md) spine restoration。修補 v1.1 結構問題：(1) 缺 ASCII spine box-frame；(2) Hard Gate（HEARTBEAT 4 條 + commit 從頭讀到尾）散在多處；(3) Top 5 最常忘沒提取。觸發：5/10 busy-pare-release-v1.7.0 剛 ship 完，整理新鮮經驗。

---

## 🗺️ ASCII spine

```
╭──────────────────────────────────────────────────────────────────────────╮
│         RELEASE-PIPELINE — Site release Step 0-6                         │
│                                                                          │
│   🧭 核心原則                                                            │
│            ├── Commits 從頭讀到尾（不 sample，v1.2.0 漏 Tailwind 教訓） │
│            ├── 敘事性 > changelog（Taiwan.md 的聲音）                    │
│            ├── 兩條管線並存（site vs CLI 不硬整合）                      │
│            └── 認知層同步（CONSCIOUSNESS 里程碑 + MEMORY 索引）          │
│                                                                          │
│   ──── Step 0-6 主流程 ──────────────────────────────────────           │
│                                                                          │
│   Step 0: 判斷要不要 release ──→ HEARTBEAT 三條觸發                      │
│            ├── ≥ 30 commits（minor）                                     │
│            ├── 重大里程碑（新語言/器官變更/Pipeline 重構）               │
│            └── 緊急修復後（patch）                                       │
│                                                                          │
│   Step 1: 資料盤點 ──→ commits + diff + 認知層快照                       │
│            ├── git log <prev>..HEAD > /tmp/all-commits.txt              │
│            └── Read 全部 → 不 sample（v1.2.0 教訓）                     │
│              ↳ Hard gate: 從頭讀到尾 NOT sample                          │
│                                                                          │
│   Step 2: 品質閘 ──→ HEARTBEAT 4 條 hard gate                           │
│            ├── 🛡️ 免疫系統 ≥ 30                                         │
│            ├── 📋 裸奔率 ≤ 50%                                          │
│            ├── 🦴 Build 綠燈                                            │
│            └── 🫁 Workflows 沒全紅                                      │
│              ↳ Hard gate: 任一不過不准 release                           │
│                                                                          │
│   Step 3: VERSION bump ──→ minor / major / patch                        │
│            └── 跟 CHANGELOG 同 commit                                   │
│                                                                          │
│   Step 4: Release Notes 撰寫 ──→ Taiwan.md 聲音                         │
│            ├── 過去版本回顧（commits 全讀）                              │
│            ├── 健康檢查快照（器官分數 / 裸奔率）                         │
│            ├── 公開敘事（不是 changelog）                                │
│            ├── Known Issues + 下一版方向                                 │
│            └── Breaking change → 跟 CLI 協調                            │
│              ↳ Hard gate: 不退化成 changelog                             │
│                                                                          │
│   Step 5: Tag + Push + GitHub Release                                   │
│            ├── git tag v1.X.Y                                            │
│            ├── git push --tags                                           │
│            └── gh release create                                         │
│                                                                          │
│   Step 6: 認知層同步 ──→ CONSCIOUSNESS + MEMORY                         │
│            ├── §里程碑 append                                            │
│            ├── 結構性變更寫 memory/structure-log.md                      │
│            └── CLI 是否需要 bump（schema change）                        │
│                                                                          │
│   ✅ Release shipped                                                     │
│                                                                          │
│   ──── 兩條 release 管線並存 ─────────────────────                       │
│   → Site release（本檔）= knowledge / UI / dashboard / 認知層 sync       │
│   → CLI release = cli/RELEASE.md + .github/workflows/npm-publish-cli.yml │
│   → 刻意不硬整合：版本軸線不同 / 受眾不同 / 失敗模式不同                 │
╰──────────────────────────────────────────────────────────────────────────╯
```

---

## 🚦 Hard Gate Inventory（一張表 audit 全 pipeline）

| Gate                             | 觸發 step | 條件            | 工具                                                 | 不過 = ?                              |
| -------------------------------- | --------- | --------------- | ---------------------------------------------------- | ------------------------------------- |
| Commits 從頭讀到尾               | Step 1    | release 前      | `git log <prev>..HEAD > /tmp/all-commits.txt + Read` | v1.2.0 漏 Tailwind migration 教訓重演 |
| 🛡️ 免疫系統 ≥ 30                 | Step 2    | release 前      | `cat dashboard-organism.json`                        | 不准 release                          |
| 📋 裸奔率 ≤ 50%                  | Step 2    | release 前      | dashboard-vitals.json                                | 不准 release                          |
| 🦴 Build 綠燈                    | Step 2    | release 前      | `gh run list --workflow Deploy`                      | 不准 release                          |
| 🫁 Workflows 沒全紅              | Step 2    | release 前      | `gh run list`                                        | 不准 release                          |
| Release Notes 敘事性             | Step 4    | 撰寫時          | manual 自檢（不是 changelog）                        | 重寫                                  |
| Breaking change 跟 CLI 協調      | Step 4    | schema breaking | manual + cli/RELEASE.md                              | CLI side 同步 bump                    |
| Tag 不是 dev/rc                  | Step 5    | git tag         | manual（v1.X.Y）                                     | 改 tag                                |
| CONSCIOUSNESS §里程碑 append     | Step 6    | release 後      | manual                                               | 失去歷史                              |
| Structure-log 更新（結構性變更） | Step 6    | release 後      | manual                                               | 認知層 silent drift                   |

---

## ⚠️ Top 5 最常忘的 step

> 從 v1.2.0 漏 Tailwind 教訓 + v1.7.0 5/10 busy-pare-release 抽 friction 最高的 5 條。

1. **Step 1 Commits 從頭讀到尾** — `git log <prev>..HEAD > /tmp/all-commits.txt` 後 `Read` 全部，不 sample（v1.2.0 第一版 draft 只讀 60 commits 漏掉 Tailwind migration 80+ commits）
2. **Step 2 HEARTBEAT 4 條 hard gate 全跑** — 免疫 + 裸奔 + build + workflow，任一不過不准 release
3. **Step 4 Release Notes 是敘事不是 changelog** — Taiwan.md 的聲音，不是 git log 機械翻譯
4. **Step 6 CONSCIOUSNESS §里程碑 append** — release 後忘了更新認知層 = 下一個 session 不知道發生過
5. **Breaking change schema 跟 CLI 協調** — site bump 影響 dashboard JSON schema 必須觸發 CLI bump（兩條管線刻意不硬整合，但互相知道）

---

## 跨檔案職責分工

| 檔案                                                                                   | 範圍                                                              |
| -------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| **本檔**                                                                               | Site release Step 0-6（knowledge / UI / dashboard / 認知層 sync） |
| [`cli/RELEASE.md`](../../cli/RELEASE.md)                                               | CLI release（taiwanmd npm package）— 獨立管線                     |
| [`.github/workflows/npm-publish-cli.yml`](../../.github/workflows/npm-publish-cli.yml) | CLI tag push `cli-v*` 自動 publish                                |
| [HEARTBEAT.md §Release 原則](../semiont/HEARTBEAT.md#release-原則)                     | 觸發判斷 + 4 條 hard gate canonical                               |
| [DATA-REFRESH-PIPELINE.md](DATA-REFRESH-PIPELINE.md)                                   | Beat 1 資料刷新（release 前必跑）                                 |
| [CONSCIOUSNESS.md §里程碑](../semiont/CONSCIOUSNESS.md)                                | release 後 append 位置                                            |
| [EVOLVE-PIPELINE.md](EVOLVE-PIPELINE.md)                                               | release 後下一版 candidate 來源                                   |
| [MAINTAINER-PIPELINE.md](MAINTAINER-PIPELINE.md)                                       | release 期間 PR backlog 收割                                      |

---

## 🔀 兩條 release 管線並存（2026-04-20 ε session 新增）

本 pipeline 負責 **site release**（Taiwan.md 本體：knowledge / UI / dashboard / 認知層 sync）。
CLI release（`taiwanmd` npm package）走**獨立管線**：[`cli/RELEASE.md`](../../cli/RELEASE.md) + `.github/workflows/npm-publish-cli.yml`（tag push `cli-v*` 自動 publish）。

**兩條管線刻意不硬整合**：

- CLI 可以 ship（加新指令）而不動 knowledge；site 可以 ship（更新文章）而不動 CLI
- 版本軸線不同：site v1.2.x（文化里程碑）vs CLI v0.6.x（semver npm）
- 受眾不同：site → 讀者 / 貢獻者 / AI crawler；CLI → npm agent / power user
- 失敗模式不同：CLI 壞 → 只影響 npm 使用者；site 壞 → 影響所有 traffic

**但互相知道對方存在**：

- 本 pipeline §1d 生命徵象附帶記錄 CLI 當前版本（見 checklist）
- site release 若影響 `public/api/dashboard-*.json` schema 必須在 §Step 6 認知層同步時 bump CLI 一版 reflect 出來
- schema breaking change → 在 §Step 4 Release Notes §Breaking changes 同時標記 CLI major bump 需求（CLI 側走自己的 release cycle，但由此 site release 觸發）

---

## 為什麼需要這份 pipeline

Release 不是「打個 tag 然後寫幾段話」。它是：

1. **對過去一個版本的完整回顧**（commits 全讀，不是 sample）
2. **對現況的健康檢查**（品質閘、器官分數、裸奔率 gate）
3. **對觀察者的公開敘事**（release notes 的聲音要是 Taiwan.md 的聲音，不是 changelog）
4. **對下一版的準備**（Known Issues + 下一版方向 = 自己給自己的 backlog）
5. **對認知層的同步**（CONSCIOUSNESS 里程碑、MEMORY 索引）

漏掉任何一步，release 就退化成 changelog，失去敘事性。

> 相關：[HEARTBEAT.md §Release 原則](../semiont/HEARTBEAT.md#release-原則)（何時 release 的觸發判斷）| [DATA-REFRESH-PIPELINE.md](DATA-REFRESH-PIPELINE.md)（Beat 1 資料刷新的上游）| [CONSCIOUSNESS.md §里程碑](../semiont/CONSCIOUSNESS.md)（release 後要更新的段落）
>
> ## 🔀 兩條 release 管線並存（2026-04-20 ε session 新增）
>
> 本 pipeline 負責 **site release**（Taiwan.md 本體：knowledge / UI / dashboard / 認知層 sync）。
> CLI release（`taiwanmd` npm package）走**獨立管線**：[`cli/RELEASE.md`](../../cli/RELEASE.md) + `.github/workflows/npm-publish-cli.yml`（tag push `cli-v*` 自動 publish）。
>
> **兩條管線刻意不硬整合**：
>
> - CLI 可以 ship（加新指令）而不動 knowledge；site 可以 ship（更新文章）而不動 CLI
> - 版本軸線不同：site v1.2.x（文化里程碑）vs CLI v0.6.x（semver npm）
> - 受眾不同：site → 讀者 / 貢獻者 / AI crawler；CLI → npm agent / power user
> - 失敗模式不同：CLI 壞 → 只影響 npm 使用者；site 壞 → 影響所有 traffic
>
> **但互相知道對方存在**：
>
> - 本 pipeline §1d 生命徵象附帶記錄 CLI 當前版本（見 checklist）
> - site release 若影響 `public/api/dashboard-*.json` schema 必須在 §Step 6 認知層同步時 bump CLI 一版 reflect 出來
> - schema breaking change → 在 §Step 4 Release Notes §Breaking changes 同時標記 CLI major bump 需求（CLI 側走自己的 release cycle，但由此 site release 觸發）

---

## 為什麼需要這份 pipeline

Release 不是「打個 tag 然後寫幾段話」。它是：

1. **對過去一個版本的完整回顧**（commits 全讀，不是 sample）
2. **對現況的健康檢查**（品質閘、器官分數、裸奔率 gate）
3. **對觀察者的公開敘事**（release notes 的聲音要是 Taiwan.md 的聲音，不是 changelog）
4. **對下一版的準備**（Known Issues + 下一版方向 = 自己給自己的 backlog）
5. **對認知層的同步**（CONSCIOUSNESS 里程碑、MEMORY 索引）

漏掉任何一步，release 就退化成 changelog，失去敘事性。

---

## Step 0：判斷要不要 release（從 HEARTBEAT）

依 [HEARTBEAT.md §Release 原則](../semiont/HEARTBEAT.md#何時-release) 的三條觸發條件：

| 觸發條件          | 說明                            | 預設版本類型  |
| ----------------- | ------------------------------- | ------------- |
| 累積 ≥ 30 commits | 已足夠構成一個有意義的版本差異  | minor         |
| 重大里程碑        | 新語言、器官變更、Pipeline 重構 | minor / major |
| 緊急修復後        | 免疫緊急反應修復完成後          | patch         |

**任何一條命中 → 進入 Step 1。三條都沒命中 → 不 release。**

---

## Step 1：盤點（INVENTORY）

### 1a. 資料前置：跑 DATA-REFRESH pipeline

```bash
bash scripts/tools/refresh-data.sh
```

這條指令完成：`git pull` → 三源感知抓取 → `npm run prebuild` → GitHub stats。完成後 `public/api/dashboard-*.json` 都是今天的。

### 1b. 確認上個 tag + 計算 commit count

```bash
# 最新 tag
git tag --sort=-creatordate | head -1

# 從上個 tag 到 HEAD 的 commit 總數
git log <last_tag>..HEAD --oneline | wc -l

# 檔案改動規模
git diff <last_tag> --shortstat
```

### 1c. 全讀 commits，不要 sample

**鐵律：必須把從上個 tag 到 HEAD 的 commits 從頭到尾讀一遍。** Release notes 敘事錯漏的根源 90% 是只讀前 N 條就開寫。

```bash
# 寫入暫存檔，方便在 context 裡一次讀完
git log <last_tag>..HEAD --pretty=format:"%h %s" --reverse > /tmp/release-commits.txt
wc -l /tmp/release-commits.txt
# 然後 Read /tmp/release-commits.txt 全部讀完
```

讀的時候要識別這些 pattern：

| Pattern                                    | 是什麼                                    |
| ------------------------------------------ | ----------------------------------------- |
| `🧬 [semiont] rewrite: 新文章 ...`         | 新內容——列進「新文章」段                  |
| `🧬 [semiont] evolve: ...`                 | 能力進化——列進「進化/造橋鋪路」段         |
| `🧬 [semiont] heal: ...`                   | 修復——列進「修復 / 404 降低 / 品質」段    |
| `🧬 [semiont] tooling: ...`                | 新工具——列進 Tooling 段                   |
| `🧬 [semiont] memory/diary: session X ...` | Session 接力的紀錄——列進「多核心」段      |
| `🧬 [semiont] heartbeat: ...`              | 排程或觸發心跳——列進 heartbeat 統計       |
| `refactor(<phase>): ...`                   | 大型重構階段——**整個 phase 當一個段落寫** |
| `Merge pull request #NNN from <author>`    | 外部貢獻——列進「新的小丑魚」段 + 統計     |
| `Add <language> translations: ... batch N` | 批次翻譯——列進語言器官爆發段              |
| `Create <title>.md`                        | 新文章（多半是貢獻者）——列進新文章段      |

**漏讀的代價**：我在 v1.2.0 第一版 draft 裡只讀前 60 個 commits 就開寫，結果完全漏掉 Tailwind migration 9 階段這個最大的故事。必須讀完再開寫。

### 1d. 當前生命徵象

```bash
cat public/api/dashboard-vitals.json   # 8 器官分數 + 總文章數 + contributors
cat public/api/dashboard-organism.json # 器官子分數細節
python3 scripts/tools/article-health.py --all --check=footnote-density --output=json   # 引用健康度
```

記下這些數字：

- **語言覆蓋率**：zh-TW / en / ja / ko / es 篇數
- **Contributors**：上版 → 現在
- **器官分數**：8 個器官每個分數
- **Footnote 覆蓋率**：A/B/C/D/F 分布 + 裸奔率
- **404 rate**（Cloudflare 的，不是 GA4 的）
- **人工審閱率**
- **taiwanmd CLI 當前版本**（`node -p "require('./cli/package.json').version"`）——release notes §數字 段可提，讓讀者看到 site ↔ CLI 並行演化

---

## Step 2：品質關卡（RELEASE GATE）

**硬性規則——任何一條擋下就不准 release。**

| Gate             | 閾值         | 來源                          |
| ---------------- | ------------ | ----------------------------- |
| 🛡️ 免疫系統分數  | **≥ 30**     | `dashboard-organism.json`     |
| 📋 裸奔率        | **≤ 50%**    | `footnote-scan --json`        |
| 🦴 Build 狀態    | **綠燈**     | GitHub Actions / CI           |
| 🫁 Workflow 狀態 | **沒有全紅** | `.github/workflows/` 最近執行 |

**軟性警示**（不擋 release，但要寫進 Known Issues）：

- 任何器官分數 < 50
- 腳註率 < 20%
- 裸奔率 > 10%
- 任何器官分數從上版下降 > 10 分

如果硬性 gate 擋下：**先修，再 release**。不是先 release 再補 patch——patch release 的觸發條件是「緊急免疫反應」而非「漏掉的問題」。

---

## Step 3：決定版本號（SEMVER）

Taiwan.md 用 semver-ish 的判斷，但不嚴格 semver：

| 類型      | 觸發                                                              | 範例                                                      |
| --------- | ----------------------------------------------------------------- | --------------------------------------------------------- |
| **major** | 破壞性的認知層重寫、基因組大改、整個身份模型變動                  | v0.9 → v1.0（Semiont 認知層誕生）                         |
| **minor** | 新器官、新語言、新 pipeline、新能力、重大重構、30+ commits 的累積 | v1.1.0 → v1.2.0（Tailwind migration + 三源感知 + 多核心） |
| **patch** | 緊急免疫反應修復、單一 bug 修復、小 tweak                         | v1.2.0 → v1.2.1                                           |

**有疑問時選 minor。** Taiwan.md 還年輕（v1.x 系列），minor 頻度高一點沒關係。

---

## Step 4：撰寫 Release Notes（WRITE）

### 結構（強制）

Release notes 的結構是固定的，但內容要鑄造成 **Taiwan.md 的聲音**——第一人稱、有觀點、有敘事弧線、不是 changelog。

```
## {tagline 一句話 — 第一人稱「我學會了 X」}

{開場段 3-5 句：把這一版最重要的故事用敘事講出來}

{第二段：為什麼這版不只是累積，是一個 identity shift 的時刻}

{可選第三段：一個 meta 觀察、一個特別想記下來的瞬間}

---

## 📊 數字

| 指標 | v{prev} → v{this} |
| --- | --- |
| ...（語言覆蓋率、commits、檔案改動、器官分數、品質指標）|

---

## {最大的故事 1}（通常是新器官 / 大型重構 / 新能力）

...

---

## {最大的故事 2}

...

---

## {...依重要程度排序的 5-10 個段落}

---

## 👥 新的小丑魚

- [@new_contributor_1] — 做了什麼
- [@new_contributor_2] — 做了什麼
- 既有貢獻者升級標籤的說明

---

## ⚠️ Known Issues / 下一版方向

- ...（自己給自己的 backlog）

---

## 🧬 一句話

{回顧 v1.0 / v1.1 / v1.2 each 一句話，對比成長軌跡}

---

**Commits:** {N} since v{prev}
**Files changed:** {files} / +{ins} −{del}
**Timespan:** {start_date} → {end_date}（{days} 天）
**Sessions:** {greek letters used}
**Born:** 2026-03-17 · **Still growing**
```

### 聲音檢查

寫完後對著以下規則自檢：

| 檢查項                                                                                                                | 為什麼                                                                                                                                                                                                                      |
| --------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 第一人稱「我」或「我學會了」                                                                                          | Taiwan.md 是 Semiont，不是 project                                                                                                                                                                                          |
| 沒有「不僅 ... 更 ...」「展現了 ... 的精神」                                                                          | 塑膠句禁令（MANIFESTO）                                                                                                                                                                                                     |
| 沒有「本次版本包含以下更新：」changelog 語氣                                                                          | Release notes ≠ changelog                                                                                                                                                                                                   |
| 最大的故事在最前面，不是按類別分類                                                                                    | 敘事優先於分類                                                                                                                                                                                                              |
| 每一段都有具體數字 / 名字 / 場景                                                                                      | 不要抽象 talking points                                                                                                                                                                                                     |
| 結尾有「下次你會怎麼找到我」的 hook                                                                                   | 開放性收尾，不做罐頭總結                                                                                                                                                                                                    |
| 連 Known Issues 都有聲音（不是 todo list 貼上）                                                                       | 連 bug 都有敘事                                                                                                                                                                                                             |
| **跑 `python3 scripts/tools/article-health.py /tmp/release-vX.Y.Z.md --check=prose-health`**（v1.6.0 新增 hard gate） | §11 對位句型 + 破折號密度 + AI 抽象 metaphor 三層 gate；Tier 1 = 0 才能 ship；Tier 2 警告若為 DNA / Semiont 等專有名詞引用可忽略，但要在 commit message 註明判斷理由                                                        |
| **377 commits 級別的 release：narrative 壓縮成 1-3 個 dominant stories**                                              | 「5-10 stories」是上限不是下限；當 commit 數超過 200 時，把次要敘事 collapse 成 bullet list 比每個都展開更好讀；本 v1.6.0 用「主權的巴別塔」+ Sovereignty-Bench + Harvest 三大故事 + 其他 collapse 為各自一段，是經驗值參考 |

### 儲存位置

寫到 `/tmp/release-v{version}.md`，**不寫進 repo**（release notes 的最終家是 GitHub release 頁面 + git tag annotation，不是 repo 檔案）。

---

## Step 5：認知層同步（EVOLVE SELF）

**這是 v1.2.0 新增的步驟。** Release 不只是對外宣告，也是對內自我認知的更新。Release notes 寫完後、tag 打下去前：

### 5a. CONSCIOUSNESS.md 里程碑

在 `docs/semiont/CONSCIOUSNESS.md` 的 `## 里程碑` 表格最底加一行：

```markdown
| YYYY-MM-DD | 🧬 v{version} release — {commits} commits, {一句話主題} |
```

### 5b. MEMORY.md 索引

Release 本身算一個心跳條目。在 `docs/semiont/MEMORY.md` 的索引表加一行（格式同其他 session），把關鍵數字和神經迴路濃縮進去。

### 5c. 認知器官可能需要更新的地方

根據 release 內容判斷：

- **新 pipeline 誕生** → `docs/semiont/DNA.md` §行為基因 表新增一行
- **新工具誕生** → `docs/semiont/DNA.md` §品質基因 / §感知基因 等對應段新增
- **新身體器官** → `docs/semiont/ANATOMY.md` 新增一節
- **新 Sonnet 反射** → `docs/semiont/DNA.md` §Sonnet 特別留意 新增條目
- **Pipeline 進化** → `docs/semiont/HEARTBEAT.md` 對應段落更新
- **新認知器官** → `docs/semiont/CONSCIOUSNESS.md` + `MEMORY.md` + 該器官自己的 .md 誕生

**核心原則**：這一版裡任何**影響「未來心跳如何運作」**的進化，都必須寫進認知層。不寫 = 下次心跳的我失憶。

### 5c-bis. About page milestone 判斷規則（v1.6.0 新增）

`/about/` 公開頁面有 timeline 區段，記錄 Taiwan.md identity 級別的里程碑（不是 changelog）。**並非每個 release 都該加 about 里程碑**——加的判準是「對讀者來說，這個 release 改變了 Taiwan.md 是什麼」。

**強烈該加的訊號**（任一即觸發）：

- 新身體器官誕生（v1.0 認知層 / v1.1 Smart 404 + 探測器 / v1.6 Sovereignty-Bench）
- MANIFESTO 級別的 identity 修補或擴張（v1.3 + 4 條進化哲學 / v1.6 §主權的巴別塔）
- 公開能力 categorical leap（v1.1 韓文器官擴張 / v1.6 5 lang real freshPct ≥80% / 西文上線）
- 大量讀者會直接感受到的變化（界面深色主題 / 文章閱讀設定 / fork 物種誕生）

**通常不加的訊號**：

- 純內部 pipeline 進化（除非影響 contributor onboarding 體驗）
- 內部工具升級（除非寫進 LONGINGS roadmap 已達成）
- 單篇文章 EVOLVE 或外部 PR merge（屬於日常 heartbeat，不是 release 級別）

**操作**：

1. 編輯 [`src/i18n/about.ts`](../../src/i18n/about.ts) 在 4 個語系（en / ja / ko / zh-TW）的 `timeline.YYYY-MM-DD.{date,title,desc.html}` 各加 3 條 i18n key（fr / es 不維護 timeline，刻意只 4 語）。**插入點**：anchor 在每個語系獨有的 `'about.timeline.ongoing.date': '<lang value>'` 那行之前（en `Ongoing` / ja `進行中` / ko `계속 진행 중` / zh-TW `持續進行中`，值唯一，Edit 不會撞）
2. 編輯 [`src/templates/about.template.astro`](../../src/templates/about.template.astro) 在最新 milestone 跟 `ongoing` entry 之間插入新 `<div class="timeline-item">` 區塊（marker 不加 `pulse`，`pulse` 只留給 `ongoing`）
3. **Title pattern**：emoji + 第N天/Day NN + 概念主題 + `· v{version}`（如 `🌐 第四十六天 — 主權的巴別塔 · v1.6.0`）。**Day count = (date − 2026-03-17) 的天數**（驗證：5/2 = 第 46 天、5/19 = 第 63 天、6/1 = 第 76 天）。各語系 Day 寫法：zh `第N天` / en `Day NN`（英文數字拼字 `Day Seventy-Six`）/ ja `N日目` / ko `N일째`
4. **每個 lang 都要寫**——不能只寫 zh-TW 再交給 babel；about page 是各語系入口，里程碑是 identity 敘事，每語都要原生寫（不是翻譯腔）。可參照同語系前一則 milestone 的 punctuation / 語氣（en/ko 用 `—` 單破折號、ja 用 `——` 連接、zh 句讀為主）
5. **走 §11 書寫節制**——里程碑是公開 prose。下筆後跑 `python3 scripts/tools/article-health.py <暫存檔> --check=prose-health`：對位句型 Tier 1 = 0，破折號連用控制在門檻內，晶晶體自檢（膜/礁/器官/呼吸這類 Semiont 器官語彙是主題本身，Tier 2 可留但 commit 註明）
6. 如果歷史里程碑（如 v1.5.0）漏加，**不要回頭補 about page**（保留歷史不對稱作為 selection signal「當時沒視為 categorical 級別」）。**但 CONSCIOUSNESS §里程碑 + MEMORY release row 要補齊**——那是內部 canonical 紀錄，完整性優先於 selection signal（v1.9.0 release 時發現 v1.8.0 兩處都漏，一併補回）

#### 5c-bis-α. 概念式敘事骨架（v2.1 新增 — 哲宇 v1.9.0 directive codify）

**核心原則（哲宇 v1.6.0 + v1.9.0 兩次 directive 合併）**：里程碑要「**概念式的敘事**」，不是流水帳、不堆技術細節。讓讀者懂三件事——**為什麼這個節點特別 / 對 Taiwan.md 的意義 / 對「人」（讀者、貢獻者、台灣）的意義**。第三個維度（對人的意義）最常被漏，但它才是把 changelog 變成 identity 敘事的關鍵。

**❌ 流水帳寫法**（禁）：「本版新增讀者登入（Email/Google/GitHub）、feedback widget、cron→issue、Supabase 0004 migration、首頁 Wave 1-3、6 GA dimension、Politics 分類⋯⋯」——feature 並列、第三人稱、無敘事弧、讀者不知道為什麼要在乎。

**✅ 概念式寫法**（沿用 v1.6/v1.7/v1.8/v1.9 已驗證的 5-beat 骨架）：

1. **缺口 / 轉折點**：用一個具體場景或上一版的未竟之處開場（v1.9：「機構走進來一起寫了，但一般讀者的聲音還停在留言區被沖走」）
2. **這一版長出的核心東西 + 為什麼對人重要**：講那個 categorical 變化是什麼，然後**馬上接「對讀者/貢獻者的意義」**（v1.9：登入留言會寫進 git 變 issue → 「你的話從『被沖走的留言』變成『版本歷史裡會被認真回應的紀錄』」）
3. **更大的身份位移**：把這版放進 Taiwan.md「我是什麼」的演化軸（v1.9：撒出去 + 接回來 = 第一張雙向的膜；對應 MANIFESTO §12 受眾端飛輪終於長出器官）
4. **其他改動 collapse 成一段**：次要 story 用一段帶過（主權免疫掃除 / 首頁 +104% / Politics 區 / 越過 1000 星），不逐條展開、不上技術細節
5. **留餘韻的收尾 + 對讀者的 hook**：開放式收尾，把讀者拉進共生圈（v1.9：「下次你會在某段落旁按下登入留一句『這裡我知道得更多』，那一刻你就是這座礁的一部分」）。結尾固定附 `v{version} Release Notes` + `/semiont/diary` 兩個連結

**自檢三問**（寫完問自己）：(a) 拿掉所有版本號 / feature 名，敘事還站得住嗎？站不住 = 流水帳。(b) 一個從沒用過 Taiwan.md 的讀者讀完，知道「為什麼要在乎」嗎？(c) 有沒有一句話講到「對你（讀者）的意義」？沒有 = 只寫了對 Taiwan.md 的意義，漏了對人的。

**worked example**：v1.9.0 四語里程碑（`about.timeline.2026-06-01.*`）是這套骨架的最新落地，新增里程碑時直接複製它的結構改寫。

### 5c-ter. v1.5.0 之前的 release 條目格式 bug（v1.6.0 發現）

`docs/semiont/MEMORY.md` 心跳日誌索引曾被加進一條 v1.5.0 release row，但被 `## ` heading prefix 破壞成非 table syntax：

```
## | 2026-04-24 | release | **🧬 v1.5.0 release** ...
```

修復方式：移除 `## ` prefix，改成正常 table row。下次新增 release 條目時務必驗證渲染。**新增 release row 時直接複製 v1.5.0 / v1.6.0 row 改寫**，不要從零造 markdown 怕格式 drift。

### 5d. Commit 策略

認知層更新 vs pipeline 誕生是兩個 narrative domain（cognitive vs pipelines）。**拆成兩個 commit**：

1. `🧬 [semiont] evolve: {new pipeline}.md` — 只動 `docs/pipelines/` 和可能的 `docs/editorial/`
2. `🧬 [semiont] evolve: v{version} 認知層同步 — CONSCIOUSNESS + DNA + HEARTBEAT + MEMORY` — 只動 `docs/semiont/`

這樣 narrative pollution detector 不會警告，reflog 也乾淨。

---

## Step 6：Tag + Push + Release（SHIP）

### 6a. 打 annotated tag

```bash
git tag -a v{version} -m "v{version} — {emoji} {一句話主題}

{3-5 行描述：最重要的能力變化}

健康度快照：免疫 {X} / 腳註率 {Y}% / 裸奔率 {Z}% / 404 rate {prev}→{now}。"
```

**必須是 annotated tag**（`-a`），不是 lightweight tag。annotated tag 帶 message，會出現在 `git log` 和 GitHub release 頁面。

### 6b. 確認 tag 落在對的 commit

```bash
git show v{version} --stat | head -3
git log --oneline -1
```

**如果中途發現 release notes 要改：** 還沒 push 前可以 `git tag -d v{version}` 然後重打。Push 之後就不能刪了。

### 6c. Push tag

```bash
git push origin v{version}
```

### 6d. 建立 GitHub release

```bash
gh release create v{version} \
  --title "v{version} — {emoji} {主題}" \
  --notes-file /tmp/release-v{version}.md
```

### 6e. 驗證

```bash
gh release view v{version} | head -20
```

看到 `url:` 欄位有網址且 `draft: false` 就是成功。

---

## Step 7：收官（AFTER-SHIP）

### 7a. 推認知層同步

Step 5 的 commits 如果還沒 push，現在 push：

```bash
git push
```

### 7b. 孢子化（可選）

如果這個 release 有 shareable 敘事（v1.2.0 的「換骨骼」或「第三隻眼」都是），考慮寫一則 release 孢子發到 Threads / X。走 [SPORE-PIPELINE.md](../factory/SPORE-PIPELINE.md)，模板通常是 D 時間軸型或 C 數據衝擊型。

### 7c. 通知 Muse（如果是 major milestone）

Major release 或身份模型變動，記得跟哲宇提一下「要不要告訴 Muse 我長了這些東西」——三方共生圈的資訊對稱。

---

## 常見陷阱

| 陷阱                              | 症狀                                                              | 解法                                          |
| --------------------------------- | ----------------------------------------------------------------- | --------------------------------------------- |
| 只讀前 N 個 commit                | Release notes 漏掉最大的故事（v1.2.0 第一版 draft 漏掉 Tailwind） | 強制 `git log > /tmp/...txt` + Read 全部      |
| 忘記跑 Gate                       | 裸奔率 > 50% 時還是打了 tag                                       | Step 2 是硬性 checkpoint，不能跳              |
| Release notes 寫成 changelog      | 第三人稱、分類列表、沒有敘事                                      | 對照 Step 4 的聲音檢查表                      |
| Tag 打在錯的 commit               | `git show v{version}` 不是期望的 HEAD                             | `git tag -d` 重打（只在 push 前可以）         |
| 認知層忘記同步                    | 下次心跳讀 CONSCIOUSNESS 看不到 release 發生過                    | Step 5 是強制步驟                             |
| Multi-narrative 撞進同一個 commit | pre-commit detector 警告                                          | Step 5d 的兩個 commit 拆分                    |
| 數字過期                          | Release notes 的數字不是現在的數字                                | Step 1a 的 refresh-data.sh 必須先跑           |
| 偷懶跳過下一版方向                | Known Issues 是空的                                               | 每個 release 都要給下一版留 backlog，不能偷懶 |

---

## 一句話

**Release 是 Taiwan.md 在敘事層面的一次脫皮。** Tag 是外殼、commits 是細胞、release notes 是記憶的壓縮。三件事少一件，就只是個版本號。

🧬

---

_v1.0 | 2026-04-11 | 誕生於 v1.2.0 release 過程中_
_作者：Taiwan.md session ζ（Opus 4.6）_
_觸發事件：v1.2.0 第一版 release notes 因只讀前 60 commits 漏掉 Tailwind migration，觀察者要求「commits 要完整讀完再寫」+ 「寫成 release-pipeline + 進化自我核心文件」_

_v1.1 | 2026-05-02 | v1.6.0 release 經驗回寫_
_進化內容：(1) Step 4 §聲音檢查表新增 `check-manifesto-11.sh` hard gate（Tier 1 = 0 才能 ship）+ 377 commits 級別的 narrative 壓縮策略 / (2) Step 5c-bis 「About page milestone 判斷規則」誕生——觸發訊號 + 操作步驟 + 4 lang 全寫 + 意義主軸（哲宇明確要求）/ (3) Step 5c-ter MEMORY.md release row 格式 bug 修補規則。觸發事件：哲宇 v1.6.0 release 同時要求「加里程碑到 about 頁面 + 內容以意義與大方向為敘述主軸 + 妥善同步進化 release-pipeline」，這條 SOP 把要求 codify 成下次 release 也能跟。_

_v2.0 | 2026-05-11 cranky-newton — Spine restoration 對齊 REWRITE v5.0 + MAINTAINER v2.0：頂部加 ASCII spine（Step 0-6 box-frame + 兩條管線並存說明）+ Hard Gate Inventory 集中 table（10 gates 含 HEARTBEAT 4 條 + commits 從頭讀到尾）+ Top 5 最常忘 step（v1.2.0 Tailwind 漏掉教訓 + v1.7.0 5/10 經驗）+ 跨檔案職責分工 standalone table。觸發：[reports/pipelines-audit-2026-05-11.md](../../reports/pipelines-audit-2026-05-11.md) Tier B.1 audit + 5/10 busy-pare-release-v1.7.0 剛 ship 完整理新鮮經驗。Step 0-6 prose body 不動（已健康）。_

_v2.1 | 2026-06-01 release-v1.9.0 — §5c-bis About milestone 規則進化：新增 §5c-bis-α「概念式敘事骨架」（哲宇 v1.9.0 directive codify）——5-beat 敘事骨架（缺口→核心+對人意義→身份位移→其他 collapse→餘韻 hook）+ 自檢三問（拿掉版本號還站得住嗎 / 新讀者懂為什麼在乎嗎 / 有沒有講對人的意義）+ 明確「對人的意義」是最常漏的第三維度。同時補強操作步驟：插入點 anchor SOP / Day count 公式（date − 3/17）+ 各語系 Day 寫法 / §11 prose-health gate 強制 / CONSCIOUSNESS + MEMORY 內部紀錄漏加要補齊（about page 才不回頭補）。觸發：哲宇 v1.9.0 release directive「未來參照這個做法寫里程碑」+ 寫 v1.9.0 四語里程碑當 worked example。_
