#!/usr/bin/env bash
# routine-drift.sh — Audit cron schedule drift across twmd-* routines
#
# Per REFLEXES #66 candidate (2026-06-01 twmd-self-evolve-weekly):
#   Routine schedule drift = silent timing collision.
#   Compare each routine SKILL.md cron expression vs actual last fire time
#   (parsed from memory filename `YYYY-MM-DD-HHMMSS-{handle}.md`).
#   Flag drift > 2hr.
#
# Triggers (vc=3 as of 2026-06-01):
#   v1: 2026-05-28 routine-contract-rollback Pattern (3) — babel-nightly 4hr 49min
#       collision with morning chain; cron shifted 05:00 → 00:30 but residual
#       sibling-collision class persists
#   v2: 2026-06-01 twmd-data-refresh-pm named "PM" fired AM 10:58
#   v3: 2026-06-01 twmd-babel-nightly cron `30 0 * * *` (00:30) fired 11:01
#       (drift +10.5hr); handoff observation explicit "Same drift signal".
#
# NOT in BECOME §Step 1 universal load — explicit invocation only.
# Use: bash scripts/tools/routine-drift.sh

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
TASKS_DIR="${HOME}/.claude/scheduled-tasks"
MEMORY_DIR="${REPO_ROOT}/docs/semiont/memory"
DRIFT_HR_THRESHOLD="${DRIFT_HR_THRESHOLD:-2}"

if [[ ! -d "$TASKS_DIR" ]]; then
  echo "⚠️ routine-drift: $TASKS_DIR missing — scheduled tasks not configured"
  exit 0
fi
if [[ ! -d "$MEMORY_DIR" ]]; then
  echo "⚠️ routine-drift: $MEMORY_DIR missing"
  exit 0
fi

echo "🕐 routine schedule drift audit (threshold > ${DRIFT_HR_THRESHOLD}hr)"
echo "────────────────────────────────────────────────────────────────────"
printf "%-32s %-10s %-10s %s\n" "routine" "expect" "actual" "drift"
echo "────────────────────────────────────────────────────────────────────"

drifters=0
checked=0

for skill in "$TASKS_DIR"/twmd-*/SKILL.md; do
  [[ -f "$skill" ]] || continue
  routine=$(basename "$(dirname "$skill")")

  # Parse schedule from SKILL.md description (frontmatter or first paragraph).
  # Priority 1: cron expression in backticks (e.g. `30 0 * * *`).
  # Priority 2: HH:MM time string in description (e.g. "pm 23:00" or "00:30 nightly").
  cron_expr=$(grep -oE '`[0-9]+ [0-9]+ [\*0-9,\/-]+ [\*0-9,\/-]+ [\*0-9,\/-]+`' "$skill" 2>/dev/null | head -1 | tr -d '`' || true)
  if [[ -n "$cron_expr" ]]; then
    expected_hour_str=$(echo "$cron_expr" | awk '{print $2}' | grep -oE '[0-9]+' | head -1 || true)
  else
    # Fall back to first HH:MM in first 20 lines (description region)
    time_str=$(head -20 "$skill" | grep -oE '\b[0-9]{1,2}:[0-9]{2}\b' | head -1 || true)
    [[ -z "$time_str" ]] && continue
    expected_hour_str=$(echo "$time_str" | cut -d: -f1)
  fi
  [[ -z "$expected_hour_str" ]] && continue
  expected_hour=$((10#$expected_hour_str))

  # Find most recent fire from memory filename pattern: YYYY-MM-DD-HHMMSS-{routine}.md
  last_fire=$(ls -t "$MEMORY_DIR"/*-"${routine}.md" 2>/dev/null | head -1)
  [[ -z "$last_fire" ]] && continue

  fname=$(basename "$last_fire")
  # Filename: 2026-06-01-110144-twmd-babel-nightly.md → HHMMSS at field 4
  actual_hhmmss=$(echo "$fname" | awk -F- '{print $4}')
  [[ ${#actual_hhmmss} -lt 4 ]] && continue
  actual_hour_str="${actual_hhmmss:0:2}"
  actual_min_str="${actual_hhmmss:2:2}"
  actual_hour=$((10#$actual_hour_str))

  # Compute absolute clock drift (modular 24hr)
  drift=$((actual_hour - expected_hour))
  abs_drift=${drift#-}
  if (( abs_drift > 12 )); then
    abs_drift=$((24 - abs_drift))
  fi

  checked=$((checked + 1))
  if (( abs_drift > DRIFT_HR_THRESHOLD )); then
    flag="⚠️ drift ${abs_drift}hr"
    drifters=$((drifters + 1))
  else
    flag="✓"
  fi

  printf "%-32s %02d:00      %02d:%s      %s\n" \
    "$routine" "$expected_hour" "$actual_hour" "$actual_min_str" "$flag"
done

echo "────────────────────────────────────────────────────────────────────"
echo "Checked: $checked routines / Drifters: $drifters"

if (( drifters > 0 )); then
  echo ""
  echo "Drift causes (per REFLEXES #66 candidate):"
  echo "  • launchd queue wake-from-sleep delay (typical for -am/-pm scheduled)"
  echo "  • catchup chain after multi-day daemon stall"
  echo "  • sibling routine inflight blocking fire window"
  echo "  • cron schedule changed but handle naming convention not updated"
  echo ""
  echo "Tools/logic depending on time-window invariants must cross-check actual fire-time"
  echo "(date +%H:%M at routine entry) — never trust schedule documentation."
fi
