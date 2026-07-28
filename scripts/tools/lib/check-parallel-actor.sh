#!/usr/bin/env bash
# check-parallel-actor.sh — 多核心 git 協調：偵測平行 actor（胼胝體鐵律 / REFLEXES #57）
#
# 平行 session / routine / 人類共用一個 working tree + 一個 origin/main。
# 動 git（commit / push / stash / pull）前先跑這支，知道現在有沒有別人在動，
# 避免 cross-session-git-index-pollution / multi-core-commit-collision / ref-lock race。
#
# 用法:
#   bash scripts/tools/lib/check-parallel-actor.sh            # 人類可讀
#   bash scripts/tools/lib/check-parallel-actor.sh --quiet    # 只回 exit code
#   STATUS=$(... --status)                                    # 只印 status 字
#
# 輸出 STATUS（第一個字）:
#   CLEAN        — 沒有偵測到平行 actor，可安全動 git
#   ACTOR_BUSY   — 有 active 翻譯/babel writer 或 index.lock（呼叫端應等或 abort）
#   REMOTE_AHEAD — origin 被別人推過（落地前先 git pull --rebase 避免 ref-lock reject）
#   DIRTY_BATCH  — working tree 留有大量未 commit .md（疑似 sibling 翻譯批次 leftover）
# exit: 0=CLEAN / 1=任一風險 / 2=error
#
# 被 .husky/pre-push、session 啟動、routine Step 1 共用。canonical: BECOME §行動鐵律 5。
set -uo pipefail

REPO="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "ERROR not-a-git-repo"; exit 2; }
cd "$REPO" || exit 2

MODE="${1:-}"
status="CLEAN"
reasons=""
add_reason() { reasons="${reasons}\n  - $1"; }
escalate() { # 不降級：ACTOR_BUSY > REMOTE_AHEAD > DIRTY_BATCH > CLEAN
  case "$1" in
    ACTOR_BUSY) status="ACTOR_BUSY";;
    REMOTE_AHEAD) [ "$status" != "ACTOR_BUSY" ] && status="REMOTE_AHEAD";;
    DIRTY_BATCH) [ "$status" = "CLEAN" ] && status="DIRTY_BATCH";;
  esac
}

# 1. index.lock — 別的程序正在 git 操作的最強訊號
if [ -f "$REPO/.git/index.lock" ]; then escalate ACTOR_BUSY; add_reason "index.lock present（另一個 git op 進行中）"; fi

# 2. File-system 層：active 翻譯/babel writer process
actor_pids="$(pgrep -f "lang-sync|babel-handoff|i18n-translate|fleet-endpoint|remote-ollama" 2>/dev/null | tr '\n' ' ' || true)"
if [ -n "${actor_pids// /}" ]; then escalate ACTOR_BUSY; add_reason "babel/lang-sync writer process: ${actor_pids}"; fi

# 3. Dirty-tree leftover：大量未 commit .md（疑似 sibling 翻譯批次，REFLEXES #57 v4）
dirty_md="$(git status --porcelain 2>/dev/null | grep -cE '\.md$' || true)"
dirty_md="${dirty_md:-0}"
if [ "$dirty_md" -gt 80 ]; then escalate DIRTY_BATCH; add_reason "dirty-tree leftover: ${dirty_md} 個未 commit .md（疑似 sibling 翻譯批次）"; fi

# 4. Git-ref 層：origin 被別人推過 → 落地會 ref-lock reject
git fetch origin -q 2>/dev/null || true
local_head="$(git rev-parse @ 2>/dev/null || true)"
remote_head="$(git rev-parse '@{u}' 2>/dev/null || git rev-parse origin/main 2>/dev/null || true)"
if [ -n "$remote_head" ] && [ -n "$local_head" ]; then
  base="$(git merge-base @ "$remote_head" 2>/dev/null || true)"
  if [ "$remote_head" != "$base" ] && [ "$remote_head" != "$local_head" ]; then
    escalate REMOTE_AHEAD; add_reason "origin 領先（$(git rev-parse --short "$remote_head")）— push 前先 git pull --rebase"
  fi
fi

# 輸出
case "$MODE" in
  --status) echo "$status"; ;;
  --quiet)  ;;
  *)
    if [ "$status" = "CLEAN" ]; then
      echo "PARALLEL_CHECK: CLEAN ✅  （dirty .md=${dirty_md}）"
    else
      printf "PARALLEL_CHECK: %s ⚠️%b\n" "$status" "$reasons"
    fi
    ;;
esac
[ "$status" = "CLEAN" ] && exit 0 || exit 1
