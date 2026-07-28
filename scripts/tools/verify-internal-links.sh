#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# verify-internal-links.sh — Post-build internal link verifier
# ─────────────────────────────────────────────────────────────────
#
# Validates every internal link (<a href="/...">) in the built Astro
# site under dist/. Catches dead language-switcher links, broken
# article cross-references, and any other orphaned internal hrefs.
#
# Run AFTER `npx astro build`:
#
#   bash scripts/tools/verify-internal-links.sh          # full scan
#   bash scripts/tools/verify-internal-links.sh --sample 50  # smoke test
#
# Exit codes:
#   0  gated broken ratio < threshold  (CI pass)
#   1  ratio >= threshold or dist/ missing
#
# Env: BROKEN_LINK_THRESHOLD=N  顯式覆寫 gate（必須在 routine memory 記一筆）
#
# 2026-06-10 build audit 熱點 #4：python 主體抽到
# scripts/tools/verify_internal_links.py 並 multiprocessing 平行化
# （單執行緒 64s → Pool；報表格式逐行不變）。本檔退為 thin wrapper。
#
# Requires: python3 (stdlib only, no pip installs)
# ─────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"

SAMPLE_SIZE=0  # 0 = all pages

while [[ $# -gt 0 ]]; do
  case "$1" in
    --sample)
      SAMPLE_SIZE="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: $0 [--sample N]"
      echo "  --sample N   randomly test N pages instead of all"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ ! -d "$DIST_DIR" ]]; then
  echo "ERROR: dist/ directory not found at $DIST_DIR" >&2
  echo "Run 'npx astro build' first." >&2
  exit 1
fi

exec python3 "$SCRIPT_DIR/verify_internal_links.py" "$DIST_DIR" "$SAMPLE_SIZE"
