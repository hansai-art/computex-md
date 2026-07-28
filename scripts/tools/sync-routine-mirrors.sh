#!/usr/bin/env bash
# sync-routine-mirrors.sh — 把 repo 裡的 routine mirror 正本推到本機宿主機。
#
# 為什麼存在（2026-07-25）：cron 讀的 SKILL.md 住 ~/.claude/scheduled-tasks/，
# 不在 git 裡。飛輪遷到專用宿主機之後，每台宿主機的 mirror 各自停在搬過去那天，
# 而 SSOT（ROUTINE.md）持續演化——中間的落差沒有任何儀器看得到（sync-check 只
# 比對 name/description，內文寫死的語言清單它看不見）。實例：babel mirror 寫死
# 五語，語言長到 11 個之後新六語整批漏掉。
#
#   bash scripts/tools/sync-routine-mirrors.sh          # 只比對，印差異
#   bash scripts/tools/sync-routine-mirrors.sh --apply  # 覆寫本機 mirror
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC="$REPO/docs/semiont/routine-mirrors"
DEST="$HOME/.claude/scheduled-tasks"
APPLY="${1:-}"

[ -d "$SRC" ] || { echo "🔴 找不到 mirror 正本目錄：$SRC" >&2; exit 1; }
[ -d "$DEST" ] || { echo "➖ 本機沒有 scheduled-tasks（非 cron 宿主機，正常）"; exit 0; }

diffs=0 same=0 missing=0
for f in "$SRC"/*.md; do
  base="$(basename "$f" .md)"
  [ "$base" = "README" ] && continue
  target="$DEST/$base/SKILL.md"
  if [ ! -f "$target" ]; then
    echo "➖ $base：本機無此 routine（未註冊，跳過）"
    missing=$((missing+1))
    continue
  fi
  if diff -q "$f" "$target" >/dev/null 2>&1; then
    echo "✅ $base：已對齊"
    same=$((same+1))
  else
    diffs=$((diffs+1))
    if [ "$APPLY" = "--apply" ]; then
      # 正本用 $TWMD_REPO 佔位（repo 不寫死任何機器的路徑，資安 + fork 友好），
      # 落地時展成這台機器的真實路徑，cron session 讀到的才是可直接執行的指令
      sed "s|\$TWMD_REPO|$REPO|g" "$f" > "$target"
      echo "🔄 $base：已覆寫本機 mirror"
    else
      echo "⚠️  $base：與正本不同（$(diff "$f" "$target" | grep -c '^[<>]') 行差異）"
    fi
  fi
done

echo ""
echo "對齊 $same／差異 $diffs／未註冊 $missing"
if [ "$diffs" -gt 0 ] && [ "$APPLY" != "--apply" ]; then
  echo "→ 覆寫本機：bash scripts/tools/sync-routine-mirrors.sh --apply"
  exit 1
fi
