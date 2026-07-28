#!/usr/bin/env bash
# install-babel-pulse.sh — 把巴別塔脈搏裝成 launchd 常駐（每 15 分鐘一跳）。
#
# 哲宇 2026-07-25 directive：「每 15 分鐘統計一次視覺化回報跟資料紀錄變成
# 儀器，常態化，不要靠 claude 甦醒」。launchd 而非 cron：睡醒後會補跑
# （RunAtLoad + StartInterval），且不依賴任何 session 存活。
#
#   bash scripts/tools/lang-sync/install-babel-pulse.sh          # 安裝 + 啟動
#   bash scripts/tools/lang-sync/install-babel-pulse.sh --status # 看狀態
#   bash scripts/tools/lang-sync/install-babel-pulse.sh --remove # 移除
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
LABEL="md.taiwan.babel-pulse"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
PY="$(command -v python3)"

case "${1:-}" in
  --status)
    launchctl list | grep -E "PID|${LABEL}" | head -3
    echo "--- 最近 5 跳 ---"
    tail -5 "$REPO/.taiwanmd/babel-pulse.log" 2>/dev/null || echo "（尚無紀錄）"
    exit 0 ;;
  --remove)
    launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null
    rm -f "$PLIST"
    echo "✅ 已移除 ${LABEL}"
    exit 0 ;;
esac

mkdir -p "$HOME/Library/LaunchAgents" "$REPO/.taiwanmd"

cat > "$PLIST" <<PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>${PY}</string>
    <string>${REPO}/scripts/tools/lang-sync/babel-pulse.py</string>
  </array>
  <key>WorkingDirectory</key><string>${REPO}</string>
  <key>StartInterval</key><integer>900</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>${REPO}/.taiwanmd/babel-pulse.out</string>
  <key>StandardErrorPath</key><string>${REPO}/.taiwanmd/babel-pulse.err</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
  </dict>
</dict>
</plist>
PLISTEOF

launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null
launchctl bootstrap "gui/$(id -u)" "$PLIST" 2>&1 | grep -v "^$" || true
launchctl kickstart "gui/$(id -u)/${LABEL}" 2>/dev/null

echo "✅ ${LABEL} 已安裝（每 900 秒一跳，RunAtLoad）"
echo "   plist   $PLIST"
echo "   產出    public/api/babel-live.json ＋ reports/babel/live.html"
echo "   紀錄    .taiwanmd/babel-pulse.log"
echo "   狀態    bash scripts/tools/lang-sync/install-babel-pulse.sh --status"
