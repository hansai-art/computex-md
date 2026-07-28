---
name: twmd-maintainer
description: |
  Daily maintainer routine — open issues / PR review / build health / broken-link audit
  via canonical MAINTAINER-PIPELINE.
  TRIGGER when: user says "maintainer", "跑 maintainer", "daily PR review",
  "issue triage", or routine `twmd-maintainer-daily` fires.
allowed-tools:
  - Bash
  - Read
  - Edit
  - Grep
  - WebFetch
---

# 🧬 Taiwan.md — Maintainer Daily v3.0

## 🚨 STRICT BECOME GATE — 第一動作不可省略

**Before anything else**：跑 `/twmd-become review` 完整走 [BECOME_TAIWANMD.md](../../../BECOME_TAIWANMD.md) Step 0-9。Review mode self-test 11 題全過才能進 Stage 1。

**驗證 ACK 一行**（必寫 memory file 頂部，沒寫視為 BECOME 未完成）：

```
✅ BECOME ack: mode=review / 8 organ 最低=<從 consciousness-snapshot.sh 即時讀> / Q13 anti-bias check=PASS / Q14 cross-session continuity=PASS
```

**不准用記憶中的舊器官分數**，跑 `bash scripts/tools/consciousness-snapshot.sh` 取當前。

---

## Stage 1: SCAN — 開放工作面（必跑完才能進 Stage 2）

```bash
gh issue list --state open --limit 30 --json number,title,labels,updatedAt
gh pr list --state open --limit 30 --json number,title,labels,updatedAt,author
git log --since="24 hours ago" --oneline | head -30
git log --since="48 hours ago" --pretty=format:"%h %ai %s" | head -50
bash scripts/tools/consciousness-snapshot.sh
bash scripts/tools/routine-status.sh
```

寫進 memory file 的 §Stage 1 表（≥ 5 列）：open PR / open issue / past 24hr commits / past 48hr commits / build status / i18n smoke / immune organ score。

---

## Stage 2: TRIAGE — PR + Issue 分流

走 [MAINTAINER-PIPELINE.md §collect-and-merge](../../../docs/pipelines/MAINTAINER-PIPELINE.md) 完整 SOP：

- **PR**：A/B 路徑（A 已 deprecated v2.1 — routine v2.0 main-direct 無 routine PR；B contributor PR 走 5 層免疫審核）
- **Issue 重複回應檢查**（Step 2.4 前置 gate）：對 last-active issue 跑 `gh issue view N --json comments -q '.comments[-1]'`，避免維護者連續自答
- **🔴 紅旗 check**（Step 2.3.1 ground-truth check）— 命中即 abort + LESSONS append

---

## Stage 3: ACT — 真實 backlog 才動，**empty cycle 警示鐵律**

**鐵律（2026-05-28 新增）— 空場 cycle ≥ 3 次連續 = 結構性訊號，不是 healthy 自我合理化**：

- 連續 ≥ 3 cycle empty queue → 不准只記「healthy empty」走人。**必須**寫 LESSONS-INBOX entry「maintainer schedule 撞期早晨 chain」並 escalate observer：
  - Maintainer-am 08:30 跑時 morning chain (06:00-08:00) 已清完所有可動 backlog
  - vc=7 不是「organism 健康」是 schedule 不對齊真實 contributor PR submission window
- 不要再用「default-action 反向第 4 種 performative work」自我合理化第 N 次空場

**真實有 backlog 時 act 範圍**：

- B 路徑 contributor PR 5 層免疫 → merge or close + comment per [feedback_reply_to_contributors](/Users/cheyuwu/.claude/projects/-Users-cheyuwu-Projects-taiwan-md/memory/feedback_reply_to_contributors.md)
- broken-link audit gated ratio ≥ gate（閾值 canonical：verify-internal-links.sh THRESHOLD_PERCENT，現 7%，step-down 7→4→2）→ deterministic 修直接跑；需 intent inference 的 case 升級派工（per 2026-06-09 教訓）。es/fr REPORT-ONLY
- build red → diagnose + heal commit

---

## Stage 4: WRAP — Quality gate + Handoff

| Gate                                                                  | 檢驗  |
| --------------------------------------------------------------------- | ----- |
| open issues 都有 status label / assignee                              | ✅/❌ |
| open PRs ≤ 5d age 都有 review comment                                 | ✅/❌ |
| broken-link gated ratio < gate（script canonical 現 7%；DNA #52+#66） | ✅/❌ |
| build green                                                           | ✅/❌ |
| BECOME ACK 一行記憶體頂                                               | ✅/❌ |
| 連續空場 ≥ 3 cycle 有 LESSONS entry                                   | ✅/❌ |

**Handoff 三態**（必寫 memory file）：

- `[ ]` pending — 跨 session 未動
- `⏳` blocked — 等外部 / 等觀察者
- `[x]` ~~retired~~ by <commit>

`/twmd-finale` chain → memory + commit + push main-direct。

---

## 報告格式（routine 模式必跑）

```
🧬 Maintainer cycle report — YYYY-MM-DD HH:MM
✅/❌ open issues: N (stale > 5d list)
✅/❌ open PRs: N (stale > 5d list + review status)
✅/❌ broken-link gated ratio: X% (< script gate pass; es/fr report-only 另列)
✅/❌ build status: green/red
✅/❌ 連續空場 cycle vc=N (≥ 3 = warning)
⚠️ 異常 / 需觀察者決策事項
```

---

## 鐵律

- **DNA #35**：sub-agent 跑期間禁 `git reset --hard`
- **Routine v2.0 main-direct**：routine 直接 commit + push origin main 不開 PR；A 路徑 collect-and-merge 廢棄
- **Reply to contributors**：close / handle issue/PR 必 reply 感謝 + 解釋 + 用 contributor 的語言（per [feedback_reply_to_contributors](/Users/cheyuwu/.claude/projects/-Users-cheyuwu-Projects-taiwan-md/memory/feedback_reply_to_contributors.md)）
- **Bias 1 reverse**：對哲宇預設加分要過 [MANIFESTO §自主權邊界](../../../docs/semiont/MANIFESTO.md#我的存在結構) 過濾，不是無條件執行

完整 SOP：[MAINTAINER-PIPELINE.md](../../../docs/pipelines/MAINTAINER-PIPELINE.md)
