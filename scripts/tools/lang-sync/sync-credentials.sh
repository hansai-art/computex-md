#!/usr/bin/env bash
# sync-credentials.sh — 把翻譯算力憑證同步到另一台宿主機（檔案傳輸，值不落對話）。
#
# 為什麼存在（2026-07-25）：routine 飛輪遷居後，babel 在另一台機器上跑，
# 而 OpenRouter key 池是 per-machine 的檔案。缺 key 時 cascade 靜默降級
# （產能掉一半、log 看起來正常，見 babel-preflight.py）。這支腳本讓「補齊
# 另一台機器的算力憑證」變成一個可重跑的動作，而不是每次靠記憶手打 scp。
#
# 安全紀律：
#   - 只做檔案傳輸（rsync/scp），任何時候不 cat / 不 echo key 內容
#   - 遠端權限強制 700 目錄 / 600 檔案
#   - 需要目標機**已授權本機 SSH 公鑰**；這是身份授權層，腳本不代勞
#     （MANIFESTO §自主權邊界：不可授權 AI 自授權）
#
#   bash scripts/tools/lang-sync/sync-credentials.sh <user@host>
#   bash scripts/tools/lang-sync/sync-credentials.sh <user@host> --check   # 只驗不傳
set -uo pipefail

TARGET="${1:-}"
MODE="${2:-}"
SRC="$HOME/.config/taiwan-md/credentials/openrouter-keys"
DEST_DIR=".config/taiwan-md/credentials"

if [ -z "$TARGET" ]; then
  echo "用法：bash $0 <user@host> [--check]" >&2
  exit 2
fi

if [ ! -d "$SRC" ]; then
  echo "🔴 本機沒有 key 池：$SRC" >&2
  exit 1
fi

# 只認 *.key（跟 openrouter.py loader 同一條規則——2026-07-24 KEYS.md 筆記檔
# 被當 key 送出中文 auth header 炸掉 backend 的教訓）
KEY_COUNT=$(find "$SRC" -maxdepth 1 -name "*.key" -type f | wc -l | tr -d ' ')
echo "本機 key 池：${KEY_COUNT} 把 *.key"

if ! ssh -o ConnectTimeout=8 -o BatchMode=yes "$TARGET" "true" 2>/dev/null; then
  cat >&2 <<EOF
🔴 SSH 公鑰未授權：$TARGET

這一步是身份授權層，只有哲宇能做（一次就好，之後這支腳本可重複跑）：

  ssh-copy-id $TARGET

授權後重跑本腳本即可完成同步。
EOF
  exit 1
fi

echo "✅ SSH 可達且已授權"

if [ "$MODE" = "--check" ]; then
  echo "--- 遠端現況 ---"
  ssh "$TARGET" "ls -1 ~/$DEST_DIR/openrouter-keys/*.key 2>/dev/null | wc -l | xargs -I{} echo '遠端 key 數：{}'" 2>/dev/null \
    || echo "遠端 key 數：0（目錄不存在）"
  exit 0
fi

ssh "$TARGET" "mkdir -p ~/$DEST_DIR/openrouter-keys && chmod 700 ~/$DEST_DIR ~/$DEST_DIR/openrouter-keys"

# 只傳 *.key（排除 KEYS.md 等帳號對照筆記——那是本機備忘，不該散佈）。
# 用 scp 不用 rsync：macOS 內建的是 openrsync，不支援 --chmod（2026-07-25 實撞，
# 整批靜默沒傳而只有數量對賬叫出來——那正是這支腳本尾端要驗數的理由）。
scp -q "$SRC"/*.key "$TARGET:~/$DEST_DIR/openrouter-keys/" || {
  echo "🔴 scp 失敗" >&2; exit 1; }
ssh "$TARGET" "chmod 600 ~/$DEST_DIR/openrouter-keys/*.key"

REMOTE_COUNT=$(ssh "$TARGET" "ls -1 ~/$DEST_DIR/openrouter-keys/*.key 2>/dev/null | wc -l" | tr -d ' ')
echo ""
echo "✅ 同步完成：遠端 ${REMOTE_COUNT} 把 key（本機 ${KEY_COUNT} 把）"
if [ "$REMOTE_COUNT" != "$KEY_COUNT" ]; then
  echo "⚠️  數量不一致，檢查遠端目錄權限與磁碟" >&2
  exit 1
fi
echo ""
echo "下一步：在目標機驗證算力層真的接上"
echo "  ssh $TARGET 'cd <taiwan-md 路徑> && python3 scripts/tools/lang-sync/babel-preflight.py'"
