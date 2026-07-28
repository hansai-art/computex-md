#!/usr/bin/env bash
# restart-vortex.sh — 一鍵重啟巴別塔三軌（含 fleet 受管接案與編組原則）
#
# 為什麼有這支：渦流的產線編組是三天實測演化出來的（模型×語言適配、
# 擅長語種共軌、專軌避單點），每次重啟手打長指令既慢又容易漏參數。
# 2026-07-27 哲宇帶機器出門前建立，回來一個指令續戰。
#
# 編組依據見 SQUEEZE-MODELS-MAX-PIPELINE.md §模型×語言適配／§編組原則。
# 地端硬體一律由 muse-bot/fleet 控制面核發 worker；本檔不持有節點 IP、
# model 或並行數。M4 是否接批次也只由 fleet control.json 決定。
# 用法：
#   bash scripts/tools/lang-sync/restart-vortex.sh [--stale-only]
#   bash scripts/tools/lang-sync/restart-vortex.sh --check

set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 1
REPO=$(pwd)

FLEETCTL="${FLEETCTL:-${HOME}/Projects/muse-bot/fleet/fleetctl}"
FLEET_ARGS=()

echo "🗼 巴別塔渦流重啟 — $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ── 前置：向 fleet 抽象層領 worker（控制面已套接案開關／並行／天花板）──
echo "▸ fleet 受管接案"
if [ -x "$FLEETCTL" ]; then
  fleet_spec=$("$FLEETCTL" workers --service llm --format babel)
  if [ -n "$fleet_spec" ]; then
    read -r -a FLEET_ARGS <<< "$fleet_spec"
    "$FLEETCTL" workers --service llm --format table
  else
    echo "   ⚠️  fleet 目前沒有核發 worker；地端軌本輪不啟動"
  fi
else
  echo "   ⚠️  找不到 fleetctl：$FLEETCTL；地端軌本輪不啟動"
fi
echo ""

# ── 唯讀巡檢：不能清程序、不能起新軌 ──────────────────────────────
# 2026-07-28 修：文件早已把 --check 列為巡檢入口，但舊版沒有解析，
# 傳入後反而照常 pkill + restart。巡檢語意必須真的唯讀，避免觀察者
# 為了看狀態意外打斷正在翻譯的 worker。
if [ "${1:-}" = "--check" ]; then
  echo "▸ 受管產線（唯讀）"
  lane_rows=$(ps ax -o pid=,etime=,command= |
    awk '/[Pp]ython .*scripts\/tools\/lang-sync\/babel-dispatch\.py/{print}')
  if [ -n "$lane_rows" ]; then
    printf '%s\n' "$lane_rows"
    lane_count=$(printf '%s\n' "$lane_rows" | wc -l | tr -d ' ')
  else
    echo "   ⚠️  目前沒有 babel-dispatch.py"
    lane_count=0
  fi
  echo "   lanes=${lane_count}（有 fleet 額度時預期 3，否則 2）"
  echo ""
  echo "▸ lane logs"
  for log in /tmp/babel-fleet.log /tmp/babel-cloud.log /tmp/babel-vi-rescue.log; do
    if [ -f "$log" ]; then
      stat -f "   %N  modified=%Sm  bytes=%z" -t "%Y-%m-%d %H:%M:%S" "$log"
    else
      echo "   $log  missing"
    fi
  done
  echo ""
  echo "▸ 本機 M4 Ollama 實際負載（是否接 Babel 以 fleet control 為準）"
  if command -v ollama >/dev/null 2>&1; then
    ollama ps
  else
    echo "   ollama command unavailable"
  fi
  exit 0
fi

# ── 殘留清理（重啟前必做，避免雙份產線互撞）──
if pgrep -f "babel-dispatch" >/dev/null 2>&1; then
  echo "▸ 清理殘留產線"
  pkill -f "babel-dispatch" 2>/dev/null
  pkill -f "translate.py --group" 2>/dev/null
  sleep 3
fi

start() {   # start <logname> <描述> <args...>
  local log="$1"; shift
  local desc="$1"; shift
  nohup python3 -u scripts/tools/lang-sync/babel-dispatch.py "$@" \
    --order forward --rounds 300 --commit-every 50 > "/tmp/$log" 2>&1 &
  echo "   PID $! — $desc"
  disown
}

echo "▸ 起跑（全軍 forward 由新到舊；排序鍵：失敗沉底→新鮮窗→缺頁先於過期→編輯時間）"

# 地端軌只認 fleet 核發的 worker；M4 是否接 Babel 由 control.json 的
# accept_batch 決定，可依觀察者逐輪授權，不在本腳本硬編碼。
# 韓語從退役的 mac 軌併入地端軌；其餘新語仍由品質較穩的 nemotron 軌處理。
if [ "${#FLEET_ARGS[@]}" -gt 0 ]; then
  if [ "${1:-}" = "--stale-only" ]; then
    start babel-stale-fleet.log "受管 fleet 四語 stale 專軌" \
      --langs en,es,fr,ko --priority p1 "${FLEET_ARGS[@]}"
  else
    start babel-fleet.log "受管 fleet 四語軌" \
      --langs en,es,fr,ko "${FLEET_ARGS[@]}"
  fi
fi

# nemotron 在葡俄阿印尼印地 42-60%，但翻越南語只有 2-6%——所以 vi 不進這軌。
# ja 暫移入此軌做實績驗收；若 n≥8 仍低於 15%，下一輪再切換模型。
start babel-cloud.log "雲端 nemotron×4（六語）" --langs ja,id,pt,hi,ar,ru \
  --worker "nemo=openrouter:nvidia/nemotron-3-ultra-550b-a55b:free" \
  --worker "nemo2=openrouter:nvidia/nemotron-3-ultra-550b-a55b:free" \
  --worker "nemo3=openrouter:nvidia/nemotron-3-ultra-550b-a55b:free" \
  --worker "nemo4=openrouter:nvidia/nemotron-3-ultra-550b-a55b:free"

# laguna 翻越南語 43-71% 是全場最佳（nemotron 只有 2-6%）——專軌用三併發避單點
start babel-vi-rescue.log "越南語專軌 laguna×3" --langs vi \
  --worker "laguna=openrouter:poolside/laguna-xs-2.1:free" \
  --worker "laguna2=openrouter:poolside/laguna-xs-2.1:free" \
  --worker "laguna3=openrouter:poolside/laguna-xs-2.1:free"

sleep 3
echo ""
echo "▸ 確認：$(pgrep -f babel-dispatch | wc -l | tr -d ' ') 條產線在跑（fleet／cloud／vi，fleet 無額度時為 2）"
echo ""
echo "接下來："
echo "  巡檢   bash scripts/tools/lang-sync/restart-vortex.sh --check  （或見 BABEL-VORTEX-LOOP.md §三重巡檢）"
echo "  進度   python3 scripts/tools/lang-sync/babel-pulse.py --no-commit"
echo "  渦流   讀 docs/pipelines/BABEL-VORTEX-LOOP.md 照它執行"
