---
title: 'ROUTINE-AUDIT-PIPELINE'
description: 'Routine 飛輪自審 SOP — weekly cross-routine commit audit + cross-cutting pattern detection + LESSONS-INBOX 候選累積（飛輪覆蓋不到的 meta-layer routine）'
type: 'pipeline-canonical'
status: 'canonical'
current_version: 'v1.0'
last_updated: 2026-05-16
last_session: '2026-05-16-011113-manual-audit-evolve'
sister_docs:
  - 'EVOLVE-PIPELINE.md'
  - 'MAINTAINER-PIPELINE.md'
upstream_canonical:
  - '../semiont/ROUTINE.md'
  - '../semiont/DNA.md'
  - '../semiont/MANIFESTO.md'
  - '../semiont/LESSONS-INBOX.md'
---

# ROUTINE-AUDIT-PIPELINE — Routine 飛輪自審 SOP v1.0

> **第一性原理**：Routine 飛輪自身有一個盲點 — cross-routine 跨棒 pattern detection。每條 routine 跑完自己的 Beat 4 收官，sibling routine 互不知道對方累積了什麼模式。**Cross-cutting pattern 是飛輪覆蓋不到的 meta-layer**，需要一條獨立 routine 跑 N-day 窗口看全貌。
>
> v1.0 誕生：2026-05-16 audit-evolve 輪 manual session 走出一次完整 audit cycle（21 commit / 4 cross-cutting pattern / 12 LESSONS 候選），證實此 routine 化的必要性。詳見 [routine-audit-2026-05-16.md §結語](../../reports/routine-audit-2026-05-16.md)：「Routine audit 跟 routine 本身一樣需要 routine 化」。

---

## 🗺️ ASCII spine

```
╭──────────────────────────────────────────────────────────────────────────╮
│         ROUTINE-AUDIT-PIPELINE — 飛輪自審 6 stage                        │
│                                                                          │
│   🧭 核心紀律                                                            │
│            ├── 跨 routine 窗口（default 7 day weekly）                   │
│            ├── data-gathering vs analysis 分離                           │
│            │     ├── script: routine-audit.py 純資料層 JSON              │
│            │     └── skill: LLM-driven 分析 + insight + report           │
│            ├── 4 條 cross-cutting pattern primary lens                  │
│            │     ├── collision detection (rescue + 不殺 worker)         │
│            │     ├── dormant entropy (canonical drift)                  │
│            │     ├── boundary input precision (ground-truth)            │
│            │     └── heal bidirectional (over-action vs over-defer)     │
│            └── LESSONS verification_count 累積驅動 distill               │
│                                                                          │
│   ──── Stage 1-6 主流程 ──────────────────────────────────────          │
│                                                                          │
│   Stage 1: SCAN ──→ git log 7-day 窗口 + 分類                            │
│            ├── 1A 跑 routine-audit.py 取結構化 JSON                      │
│            ├── 1B 讀 7-day 內 memory files + diary files                 │
│            └── 1C 讀 LESSONS-INBOX 待消化清單                            │
│              ↳ Hard gate: JSON output exist 才進 Stage 2                 │
│                                                                          │
│   Stage 2: CORRELATE ──→ 跨 routine 關聯                                 │
│            ├── per-day collision 看哪幾條 routine 撞窗口                 │
│            ├── heal commit cluster 看是不是同一 incident 多 commit       │
│            └── memory ↔ commit ↔ LESSONS 三向 cross-check                │
│                                                                          │
│   Stage 3: PATTERN ──→ 4 條 lens detect cross-cutting                    │
│            ├── 3A collision (rescue / orphan process / handoff chain)    │
│            ├── 3B dormant entropy (canonical ↔ production drift)         │
│            ├── 3C boundary input precision (ground-truth vs description)│
│            └── 3D heal bidirectional (over-close / over-ship / over-defer)│
│                                                                          │
│   Stage 4: LESSONS ──→ verification_count 累積                           │
│            ├── 4A 對應 LESSONS-INBOX 既有 entry vc +1                    │
│            ├── 4B 新 pattern 達 vc=3 → 標 distill-ready (REFLEXES #15)   │
│            └── 4C 寫 append entries 到 LESSONS-INBOX                     │
│              ↳ Hard gate: 達 vc=3 必標 distill-ready 給下次 distill cycle│
│                                                                          │
│   Stage 5: REPORT ──→ reports/routine-audit-YYYY-MM-DD.md                │
│            ├── Executive summary（5 分鐘 read）                          │
│            ├── 逐 routine 詳細 audit                                     │
│            ├── 4 cross-cutting pattern 分析                              │
│            ├── LESSONS-INBOX 候選 table                                  │
│            └── 進化建議 P0-P3 priority                                   │
│              ↳ Hard gate: prose-health hard=0                            │
│                                                                          │
│   Stage 6: SHIP ──→ git commit + push                                    │
│            └── Audit report + LESSONS-INBOX appends 同 commit            │
│              ↳ Hard gate: pre-commit pass + push main                    │
│                                                                          │
│   ✅ Routine audit shipped                                               │
│                                                                          │
│   ──── 跟其他 pipeline 的 boundary ─────────────                        │
│   → distill 接 LESSONS-INBOX 升 canonical：LESSONS-INBOX §Distill SOP   │
│   → evolve 接 dashboard 數據驅動：EVOLVE-PIPELINE.md                    │
│   → maintainer 接 PR backlog：MAINTAINER-PIPELINE.md                    │
│   → 邊界：本檔只 audit routine + commit + memory；不 audit 文章本體     │
╰──────────────────────────────────────────────────────────────────────────╯
```

---

## 🚦 Hard Gate Inventory

| Gate                             | 觸發 stage | 條件                                                                                                          | 工具                                                | 不過 = ?               |
| -------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- | ---------------------- |
| routine-audit.py output exist    | Stage 1A   | 跑完 script                                                                                                   | `python3 ...routine-audit.py`                       | 無資料無 audit         |
| 7-day 窗口 commit ≥ 5 條         | Stage 1A   | 數據充分性                                                                                                    | manual 看 summary.total.count                       | 窗口太小延後一週       |
| 4 lens 全跑                      | Stage 3    | 4 cross-cutting pattern                                                                                       | manual checklist                                    | 缺一 lens 退回 Stage 2 |
| LESSONS vc 累積                  | Stage 4    | 每 pattern 對 existing 比對                                                                                   | manual grep                                         | 不累積 = audit 無意義  |
| 達 vc=3 必標 distill-ready       | Stage 4B   | REFLEXES #15 儀器化 threshold                                                                                 | manual                                              | 不標 = 下次又重做      |
| counts-drift 深度表週跑          | Stage 1A   | 每週 audit（2026-07-05 新增）                                                                                 | `counts-drift-lint.py`                              | 寫死數字腐化不可見     |
| 三層 routine sync 週跑           | Stage 1A   | 每週 audit（2026-07-05 新增）                                                                                 | `routine-sync-check.py` v3                          | SSOT↔live 漂移不可見   |
| alert 齡 >14 天升 OBSERVER-QUEUE | Stage 4    | dashboard-alerts firstSeen 齡（2026-07-05 新增，dna-audit §S4：黃燈要有 owner 與 escalation 才不 deadletter） | jq 讀 `dashboard-alerts.json` `.alerts[].firstSeen` | 偵測有修復無重演       |
| prose-health hard=0              | Stage 5    | report 寫完                                                                                                   | `article-health.py --check`                         | 改寫                   |
| Pre-commit hook 過               | Stage 6    | commit 前                                                                                                     | `.husky/pre-commit`                                 | 不 commit              |

---

## ⚠️ Top 5 最常忘的 step

1. **Stage 1A 必跑 routine-audit.py 取 JSON，不憑記憶填數字** — 跨日 commit count / files / collisions 容易主觀扭曲 10×（per MEMORY-PIPELINE timestamp 紀律延伸）
2. **Stage 4A LESSONS vc +1 比 Stage 4C 新 append 重要** — 累積驗證是 distill 的真正燃料，新 entry 沒驗證等於 noise
3. **Stage 3 4 lens 全跑不能挑** — 缺一 lens 等於 pattern detection 漏一邊（5/16 第一次 audit 確認此 framework 完整性，4 lens 每條都有 instance）
4. **Stage 5 report 中段抽象段落 prose-health scan** — 「cross-cutting pattern」「dormant entropy」這類抽象詞容易堆塑膠句（per audit-2026-05-16 中段 score 8 結構性警告）
5. **Routine 跑完不開新議題** — audit 是 surface + accumulate，不是 fix。發現 pattern 寫進 LESSONS-INBOX 等下次 distill cycle 升 canonical，不在本 routine 動 pipeline

---

## 跨檔案職責分工

| 檔案                                                                     | 範圍                                                   |
| ------------------------------------------------------------------------ | ------------------------------------------------------ |
| **本檔**                                                                 | Routine 自審 SOP（7-day 跨 routine pattern detection） |
| [LESSONS-INBOX.md](../semiont/LESSONS-INBOX.md)                          | 教訓 buffer — 本 routine 把候選 append 這裡            |
| [EVOLVE-PIPELINE.md](EVOLVE-PIPELINE.md)                                 | 內容數據驅動 — 邊界不同（GA / SC / GitHub）            |
| [MAINTAINER-PIPELINE.md](MAINTAINER-PIPELINE.md)                         | PR / Issue triage — 不重疊                             |
| [ROUTINE.md](../semiont/ROUTINE.md)                                      | Routine 排程 SSOT — 本 routine 自己也在其中            |
| [`scripts/tools/routine-audit.py`](../../scripts/tools/routine-audit.py) | 純資料層 — git log + JSON output                       |

**邊界：本檔 vs distill**：

- **本檔（ROUTINE-AUDIT）** = 7-day 窗口 routine 全量掃 + pattern detection + LESSONS 候選累積
- **distill** = LESSONS-INBOX 既有 entries 升 canonical（REFLEXES / MANIFESTO / pipeline）
- 兩者循序：audit append → distill 消化 → canonical 升級

---

## Stage-by-stage 詳細

### Stage 1: SCAN — 7-day 跨 routine 窗口資料收集

#### 1A. 跑 routine-audit.py

```bash
python3 scripts/tools/routine-audit.py --last-week --out-file=/tmp/routine-audit.json
```

`scripts/tools/routine-audit.py` 設計（純資料層）：

- 讀 `git log --since` + parse commit subject 分類
- 分類：14 routine pattern + semiont + pr-squash + other
- Per-commit metadata：files / insertions / deletions
- Collision detection：同窗口（≤60 min）跨 routine commit pair + "rescue" 關鍵字 detect
- Heal detection：subject 含 `heal:` / `fix:`
- Output：JSON with full metadata

#### 1B. 讀 7-day 內 memory + diary files

```bash
ls -la docs/semiont/memory/$(date -v-7d +%Y-%m-%d)* docs/semiont/diary/$(date -v-7d +%Y-%m-%d)*
```

memory 是「做了什麼」+「為什麼」+「學到什麼」的細節層。Audit 需要讀這個層的 Beat 5 反芻 + handoff 三態，才能識別 cross-routine handoff carryover pattern。

#### 1C. 讀 LESSONS-INBOX 待消化清單

```bash
grep -E "^### " docs/semiont/LESSONS-INBOX.md | head -30
```

抓既有 entry topic signature，後續 Stage 4 累積 vc 對應。

### Stage 2: CORRELATE — 跨 routine 關聯

讀 Stage 1 JSON 後做三維關聯：

| 維度                           | 看什麼                                                                                   |
| ------------------------------ | ---------------------------------------------------------------------------------------- |
| Per-day collision              | 哪幾條 routine 撞窗口（rescue-pattern instances）                                        |
| Heal commit cluster            | 是不是同一 incident 多 commit（5/16 Deploy CI 1-字 heal 跟 PR #1070 兩輪是相鄰 cluster） |
| memory ↔ commit ↔ LESSONS 三向 | memory 寫的 LESSONS 候選有沒有對應 commit hash + LESSONS-INBOX entry                     |

### Stage 3: PATTERN — 4 cross-cutting lens

每條 lens 都有具體 signature 可以掃：

#### 3A. Collision lens（rescue / orphan / handoff chain）

關鍵字：「孤兒 process」「PPID=1」「rescue commit」「不殺 worker」「sibling 撞」「detached worker」「handoff 接力」。

5/16 instance：babel-nightly 05:04 ↔ data-refresh-am 06:00 撞 + 4 個孤兒 translate.py + selective exclude in-flight。

#### 3B. Dormant entropy lens（canonical ↔ production drift）

關鍵字：「canonical 漂移」「pipeline 寫死」「production 已換」「Hy3 退役」「載入但沒人用」「健康反而是個盲點」。

5/16 instance：SQUEEZE-MODELS-MAX 寫 Hy3 一週沒人 audit。5/13 instance：HEARTBEAT 745→218 super-thin。Cross-day pattern。

#### 3C. Boundary input precision lens（ground-truth vs description）

關鍵字：「PR body 描述」「diff 實算」「upstream issue ruling」「observer ruling」「ground truth」「二手敘述」。

5/16 instance：PR #1070 第一輪用 PR body 數字 leave open → 觀察者 callout 後 ground-truth diff 8 篇 ship。

#### 3D. Heal bidirectional lens（over-action / over-ship / over-defer）

關鍵字：「過度 close」「過度 ship」「過度 defer」「reflexive 反射式」「default-action 反向」「校正」「拉回」。

5/16 instance：早上 momofuku heal (over-action 對照組正確) vs #1070 第一輪 leave-open (over-defer 反例)。

### Stage 4: LESSONS — verification_count 累積

#### 4A. 對應既有 LESSONS-INBOX entry vc +1

對 Stage 3 識別的每條 pattern 跑 grep：

```bash
grep -E "^### .*({signature})" docs/semiont/LESSONS-INBOX.md
```

找到既有 entry → 在文末 `verification_count` field 累積 +1，附 N 次驗證的 instance pointer。

#### 4B. 新 pattern 達 vc=3 → 標 distill-ready

REFLEXES #15「反覆浮現要儀器化」threshold = 3 次驗證。本 routine 不直接升 canonical（職責邊界給 distill）— 只標 `distill_ready: true` field 讓下次 distill cycle 看到。

#### 4C. 新 entry append

未匹配既有 entry 的新 pattern → 新 entry append 到 LESSONS-INBOX §未消化清單 頂部，含：

- 原則 / 觸發 / 可能層級 / verification_count: 1 / severity / 跨檔關聯

### Stage 5: REPORT — `reports/routine-audit-YYYY-MM-DD.md`

模板（per [routine-audit-2026-05-16.md](../../reports/routine-audit-2026-05-16.md) 參考）：

- frontmatter（title / description / type=audit-doc / version / related list）
- Executive summary（5 分鐘 read，含 routine 一張表）
- 跨日 routine intensity 比較 table
- 逐 routine 詳細 audit（5 段 per cron routine）
- Cross-cutting patterns 4 條（分析 + 進化建議）
- LESSONS-INBOX 候選 table（含 verification_count）
- 進化建議 P0-P3 priority

### Stage 6: SHIP — git commit + push

```bash
git add reports/routine-audit-YYYY-MM-DD.md docs/semiont/LESSONS-INBOX.md
git commit -m "🧬 [routine] routine-audit-weekly: N commits / M cross-cutting patterns / K LESSONS — YYYY-MM-DD"
git push origin main
```

---

## 跟 distill-weekly 的關係

- **本 routine（routine-audit-weekly）** 跑 Sunday 12:00 — accumulate LESSONS-INBOX 候選 + distill_ready flag
- **distill-weekly** 跑 Sunday 03:00 — 拉 LESSONS-INBOX 升 canonical

**順序衝突**：distill 03:00 跑時還沒有 routine-audit 12:00 的 append。設計選擇：

- **本 routine 排 Sunday 12:00 noon** — distill 已跑完當週累積，audit 接著做新的 7-day audit + LESSONS append → 下次 distill (next Sunday 03:00) 接到本週 audit 的 LESSONS
- **不排 Saturday** — Saturday 沒有 chain，audit 拿不到當週完整資料
- **不排 Sunday 早於 distill** — 避免跟夜間 chain 撞窗口（reflexive 設計：routine audit 自己也要遵守不撞 cron 規則）

---

## 失敗模式 + escalation

| 失敗                             | 處置                                                                                    |
| -------------------------------- | --------------------------------------------------------------------------------------- |
| `routine-audit.py` exit non-zero | LESSONS-INBOX entry + telegram + abort cycle                                            |
| 7-day 窗口 commit < 5 條         | 視為「沒夠數據」cycle skip + 寫一行 routine memory「low-signal cycle, no audit needed」 |
| 4 lens 找不到 instance           | OK — 表示這週沒撞 pattern，正常情況                                                     |
| LESSONS-INBOX file lock conflict | 等 30s 再 retry，最多 3 次                                                              |
| Report prose-health hard fail    | 自己改寫，pre-commit 攔下會自動 retry                                                   |
| Push main 撞別 routine           | 等 60s + `git pull --rebase` + retry                                                    |

---

## 跟 DNA / MANIFESTO 的對應

| 認知層                             | 關係                                                                                       |
| ---------------------------------- | ------------------------------------------------------------------------------------------ |
| REFLEXES #15 反覆浮現要儀器化      | 本 routine 自身就是 #15 的具體 instance（cross-routine pattern detection 需要 routine 化） |
| MANIFESTO §架構解 > 守備修補       | 本 routine 屬「架構解」— 不修個案，建立 cross-cutting view                                 |
| MANIFESTO §造橋鋪路                | Audit report 是給未來的橋（觀察者 weekend afternoon 讀完知道飛輪在做什麼）                 |
| DNA #4 三源驗證                    | 本 routine 三源 = git log + memory + LESSONS-INBOX                                         |
| DNA #43 routine 飛輪 SSOT          | 本 routine 是飛輪自身的 monitoring loop                                                    |
| DNA #54 routine 飛輪自轉清 entropy | 本 routine 清的是 **cross-routine pattern entropy**（單條 routine 看不到）                 |

---

🧬

_v1.0 | 2026-05-16 12:00 +0800_
_session 011113-manual-audit-evolve — 哲宇「建立 Routine audit 跟 routine 本身一樣需要 routine 化 的機制完整實作」directive 觸發_
_誕生原因：2026-05-16 一次性 manual audit 走出完整 cycle 後，把 SOP 抽象化 + 工具化（routine-audit.py） + routine 化（Sunday noon cron）。Cross-routine pattern detection 是飛輪覆蓋不到的 meta-layer，需獨立 routine 自審_
_核心精神：data-gathering（script）vs analysis（LLM skill）分離 + 4 cross-cutting lens primary framework + LESSONS verification_count 累積驅動 distill 升級_
