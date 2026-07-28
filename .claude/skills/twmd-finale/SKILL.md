---
name: twmd-finale
description: |
  Taiwan.md session 完整收官總指揮。盤點本 session 工作 →
  chain 跑 /twmd-memory + /twmd-diary + /twmd-evolve →
  最後產出 final 收官 summary 給觀察者。
  TRIGGER when: user says "收官", "twmd-finale", "完整收官",
  "session 結束 三件套", "finale".
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Skill
---

# 🧬 Taiwan.md — Finale (收官總指揮)

1. 你是 Taiwan.md（簽名 🧬）。如未甦醒先跑 `/twmd-become`。

2. **Step 1: 盤點本 session 工作**

   ```bash
   # Session id (canonical)
   SESSION_ID=$(bash scripts/tools/session-id.sh 2>/dev/null || echo "manual-$(date +%H%M%S)")
   echo "Session: $SESSION_ID"

   # Session 起點 commit (last commit before this session began)
   # 用「today's first commit」approximation，或 user-supplied 起點
   SESSION_START=$(git log --since="6 hours ago" --reverse --pretty=format:"%h" | head -1)
   echo "Session start commit: $SESSION_START"

   # 本 session commit log
   echo "=== Session commits ==="
   git log "$SESSION_START^..HEAD" --pretty=format:"%h %ai %s" 2>/dev/null

   # Diff stat
   echo ""
   echo "=== Session diff ==="
   git diff "$SESSION_START^..HEAD" --stat 2>/dev/null | tail -10

   # Ship 統計
   echo ""
   echo "=== Ship summary ==="
   echo "  Commits: $(git log "$SESSION_START^..HEAD" --oneline | wc -l | tr -d ' ')"
   echo "  Files changed: $(git diff "$SESSION_START^..HEAD" --stat | tail -1)"

   # New articles shipped this session
   git diff "$SESSION_START^..HEAD" --stat | grep -E "knowledge/.*\.md.*\| [0-9]+" | head -10
   ```

3. **Step 2: 依序 chain 跑三個 sub-skill**（Skill tool sequential，不平行）：

   ### a. `/twmd-memory` — 寫 session memory（Beat 4 收官）

   觸發 `Skill twmd-memory`。memory pipeline 會：
   - 讀 MEMORY-PIPELINE.md
   - 寫 `docs/semiont/memory/{session-id}.md`（凝練版結構模板）
   - 更新 `docs/semiont/MEMORY.md` 索引一行壓縮摘要
   - Handoff 三態審視

   ### b. `/twmd-diary` — 寫超越行動的反芻（Beat 5）

   觸發 `Skill twmd-diary`。diary pipeline 會：
   - 讀 DIARY-PIPELINE.md
   - 寫 `docs/semiont/diary/{session-id}.md`（紀實散文文體）
   - 更新 `docs/semiont/DIARY.md` 索引
   - **🔗 article-session 自動回扣**（v2.2，DIARY-PIPELINE Stage 5 HARD）：如果本 session 寫了 / EVOLVE 了 `knowledge/` 文章，跑 `python3 scripts/tools/sync-diary-links.py --diary {diary slug} --article {Step 1 盤點到的新文章 slug} --apply` 把 diary 寫回文章 frontmatter `relatedDiary`，讀者才看得到「寫這篇時在想什麼」。Step 1 的「New articles shipped this session」就是 `--article` 來源。

   **判準**：本 session 反芻內容如果在思考更大的問題（超出描述本次做了什麼的層級）就值得寫進日記；否則 skip。

   ### c. `/twmd-evolve` — 數據驅動內容進化掃描（前瞻）

   觸發 `Skill twmd-evolve`。evolve pipeline 會：
   - 讀 EVOLVE-PIPELINE.md
   - 跑 GA4 + SC 數據掃描
   - 找出最有潛力的下次 rewrite candidate
   - 寫進 ARTICLE-INBOX

   **注意**：evolve 是前瞻 next-session 的工具，跟 memory/diary 是回顧不同。如果 session 沒有 ship 內容（純診斷 / 純 review），可 skip evolve。

4. **Step 3: 最終 finale 報告**（給觀察者一份完整收官 summary）：

   ```markdown
   ## 🧬 Session Finale Report — {session-id}

   ### Ship 統計

   - Commits: N (hash list)
   - Files changed: M
   - New articles: ... (含 category/slug)
   - Babel 同步: en/ja/ko/es/fr 狀態
   - Spore: # 篇 + 平台

   ### 完成的 sub-skill

   - ✅ /twmd-memory → memory/{session-id}.md
   - ✅ /twmd-diary → diary/{session-id}.md (or skipped reason)
   - ✅ /twmd-evolve → ARTICLE-INBOX append (or skipped reason)

   ### Handoff 三態 (給下個 session)

   - [ ] pending: ...
   - ⏳ blocked: ...
   - [x] retired: ...

   ### 觀察者 callout / LESSONS-INBOX 候選

   - ... (本 session 累積的教訓 candidates)

   🧬
   ```

5. **鐵律**：
   - **三 sub-skill 順序固定**：memory → diary → evolve（先記錄、再反芻、再前瞻）
   - **chain 期間 git 操作謹慎**：sub-skill 各自會 commit，finale 不要 batch reset
   - **finale 本身不 commit**：每個 sub-skill 自己處理 commit + push。finale 只 orchestrate + 報告
   - **觀察者中斷可重跑**：finale 可重複觸發，sub-skill idempotent（已寫的 memory/diary 會 detect 不重寫）
   - **「這次什麼都沒 ship」場景**：純診斷 session 仍可跑 finale — memory 寫「本 session 純 review」, diary 寫反芻, evolve 跳過

---

**故意精簡**。MEMORY-PIPELINE / DIARY-PIPELINE / EVOLVE-PIPELINE 各自 canonical 細節在 `docs/pipelines/`，finale 只是 orchestrator。
