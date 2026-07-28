#!/usr/bin/env bash
# i18n-coverage-audit.sh
# 掃描 src/i18n/ 12 個 module，統計每個語言的 key 覆蓋率
#
# 輸出：
#   - human-readable 表格（default）
#   - --json：JSON 輸出（給 dashboard / CI 用）
#   - --report：寫 reports/i18n-coverage-YYYY-MM-DD.md
#   - --json-out FILE：寫 JSON 到指定檔案
#
# 對應 reports/i18n-evolution-roadmap-2026-04-25.md Phase 3 任務 #8
# bash 3.2 兼容（macOS default）— 不用 associative array

set -euo pipefail

MODE="${1:-table}"
JSON_OUT="${2:-}"

I18N_DIR="src/i18n"
MODULES=(home about contribute changelog dashboard data resources map assets notfound taiwanShape semiont)

# 2026-07-25 哲宇 directive: 語言清單改從 src/config/languages.mjs（SSOT）動態 derive，
# 不再寫死 6 語。新語言出生時（vi/id/pt/hi 2026-07-19 那批）dashboard 曾整批漏掉，
# 因為這裡的 LANGS 陣列沒跟著長 — 這個 audit script 是唯一資料來源，寫死就等於
# 讓後生語言在 dashboard 上「不存在」。改用 ALL_LANGUAGE_CODES（含 enabled:false
# 的 ar/ru，讓它們的 UI 覆蓋率能從 0 開始被看見、逐步爬升到開站那天）。
# zh-TW 永遠放第一個，因為它是覆蓋率計算的 100% 基準（MAX_TOTAL 用它的 key 數）。
# bash 3.2 相容：不用 mapfile/readarray（bash 4+ only），改 while-read 組陣列。
LANGS=()
while IFS= read -r _lang_code; do
  [[ -n "$_lang_code" ]] && LANGS+=("$_lang_code")
done < <(node -e "
import('./src/config/languages.mjs').then(({ ALL_LANGUAGE_CODES }) => {
  const rest = ALL_LANGUAGE_CODES.filter((c) => c !== 'zh-TW');
  console.log(['zh-TW', ...rest].join('\n'));
});
")

# bash 3.2 compat: 用 temp dir 存 key=value 而不是 associative array
TMP=$(mktemp -d)
trap "rm -rf $TMP" EXIT

count_keys() {
  local module=$1 lang=$2 f="$I18N_DIR/${module}.ts"
  [[ ! -f "$f" ]] && { echo 0; return; }
  local n
  n=$(awk "/^  '$lang': \{|^  $lang: \{/,/^  \},/" "$f" \
        | grep -E "^    [a-z']" 2>/dev/null \
        | wc -l \
        | tr -d ' ')
  echo "${n:-0}"
}

# Pre-compute 所有 (module, lang) → count
for module in "${MODULES[@]}"; do
  for lang in "${LANGS[@]}"; do
    c=$(count_keys "$module" "$lang")
    echo "$c" > "$TMP/${module}__${lang}"
  done
done

get_count() {
  cat "$TMP/${1}__${2}" 2>/dev/null || echo 0
}

# 各 lang 加總
for lang in "${LANGS[@]}"; do
  total=0
  for module in "${MODULES[@]}"; do
    c=$(get_count "$module" "$lang")
    total=$((total + c))
  done
  echo "$total" > "$TMP/total__${lang}"
done

get_total() {
  cat "$TMP/total__${1}" 2>/dev/null || echo 0
}

MAX_TOTAL=$(get_total "zh-TW")

# JSON output（給 dashboard / CI）
emit_json() {
  echo "{"
  echo "  \"generated\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
  echo "  \"max_total\": $MAX_TOTAL,"
  echo "  \"modules\": ["
  local i=0
  for module in "${MODULES[@]}"; do
    echo "    {"
    echo "      \"name\": \"$module\","
    echo "      \"langs\": {"
    local j=0
    for lang in "${LANGS[@]}"; do
      c=$(get_count "$module" "$lang")
      sep=$([[ $j -lt $((${#LANGS[@]} - 1)) ]] && echo "," || echo "")
      echo "        \"$lang\": $c$sep"
      j=$((j + 1))
    done
    echo "      }"
    sep=$([[ $i -lt $((${#MODULES[@]} - 1)) ]] && echo "," || echo "")
    echo "    }$sep"
    i=$((i + 1))
  done
  echo "  ],"
  echo "  \"lang_totals\": {"
  local j=0
  for lang in "${LANGS[@]}"; do
    total=$(get_total "$lang")
    pct=$(awk "BEGIN { printf \"%.2f\", ($total / $MAX_TOTAL) * 100 }")
    sep=$([[ $j -lt $((${#LANGS[@]} - 1)) ]] && echo "," || echo "")
    echo "    \"$lang\": { \"keys\": $total, \"coverage_pct\": $pct }$sep"
    j=$((j + 1))
  done
  echo "  }"
  echo "}"
}

if [[ "$MODE" == "--json" ]]; then
  emit_json
  exit 0
fi

if [[ "$MODE" == "--json-out" ]] && [[ -n "$JSON_OUT" ]]; then
  emit_json > "$JSON_OUT"
  echo "✅ JSON written: $JSON_OUT"
  exit 0
fi

if [[ "$MODE" == "--report" ]]; then
  TODAY=$(date +%Y-%m-%d)
  OUT="reports/i18n-coverage-${TODAY}.md"
  mkdir -p reports

  {
    echo "---"
    echo "title: i18n 翻譯覆蓋率 Audit"
    echo "date: $TODAY"
    echo "session: i18n-coverage-audit"
    echo "trigger: 'scripts/tools/i18n-coverage-audit.sh --report'"
    echo "---"
    echo
    echo "# i18n 翻譯覆蓋率 Audit ($TODAY)"
    echo
    echo "對應 [reports/i18n-evolution-roadmap-2026-04-25.md](i18n-evolution-roadmap-2026-04-25.md) Phase 3 任務 #8。"
    echo "由 \`scripts/tools/i18n-coverage-audit.sh --report\` 自動產出。"
    echo
    echo "## 各語言總覽"
    echo
    echo "| 語言 | 已翻譯 keys | 缺失 | 覆蓋率 | FALLBACK_CHAIN |"
    echo "| ---- | ----------: | ---: | -----: | -------------- |"
    for lang in "${LANGS[@]}"; do
      total=$(get_total "$lang")
      missing=$((MAX_TOTAL - total))
      pct=$(awk "BEGIN { printf \"%.1f\", ($total / $MAX_TOTAL) * 100 }")
      # 對照 src/i18n/utils.ts FALLBACK_CHAIN（2026-07-25 補 vi/id/pt/hi；
      # ar/ru 尚未加入該 map，語言出生時要記得同步這裡）
      case "$lang" in
        zh-TW) chain="—（default）" ;;
        en) chain="en → zh-TW" ;;
        ja) chain="ja → zh-TW" ;;
        ko) chain="ko → zh-TW" ;;
        fr) chain="**fr → en → zh-TW**" ;;
        es) chain="**es → en → zh-TW**" ;;
        vi) chain="vi → en → zh-TW" ;;
        id) chain="id → en → zh-TW" ;;
        pt) chain="**pt → es → en → zh-TW**" ;;
        hi) chain="hi → en → zh-TW" ;;
        *) chain="$lang → zh-TW（尚未加入 utils.ts FALLBACK_CHAIN）" ;;
      esac
      printf "| **%s** | %d | %d | %s%% | %s |\n" "$lang" "$total" "$missing" "$pct" "$chain"
    done
    echo
    echo "**MAX_TOTAL** = $MAX_TOTAL keys（zh-TW canonical）"
    echo
    echo "## 各 module × 語言矩陣"
    echo
    printf "| Module |"
    for lang in "${LANGS[@]}"; do printf " %s |" "$lang"; done
    echo
    printf "| ------ |"
    for lang in "${LANGS[@]}"; do printf " ----: |"; done
    echo
    for module in "${MODULES[@]}"; do
      printf "| **%s** |" "$module"
      zh_count=$(get_count "$module" "zh-TW")
      for lang in "${LANGS[@]}"; do
        c=$(get_count "$module" "$lang")
        if [[ $c -eq 0 && $zh_count -gt 0 ]]; then
          printf " 🔴 0 |"
        elif [[ $c -lt $zh_count ]]; then
          printf " 🟡 %d/%d |" "$c" "$zh_count"
        elif [[ $c -gt 0 ]]; then
          printf " ✅ %d |" "$c"
        else
          printf " — |"
        fi
      done
      echo
    done
    echo
    echo "**圖例**：✅ = 完整覆蓋 / 🟡 = 部分覆蓋 / 🔴 = 完全缺失（依賴 FALLBACK_CHAIN）/ — = 該 module 未存在"
    echo
    echo "## 觀察"
    echo
    for lang in "${LANGS[@]}"; do
      total=$(get_total "$lang")
      pct_int=$(awk "BEGIN { printf \"%d\", ($total / $MAX_TOTAL) * 100 }")
      missing_modules=""
      partial_modules=""
      for module in "${MODULES[@]}"; do
        c=$(get_count "$module" "$lang")
        zh_count=$(get_count "$module" "zh-TW")
        if [[ $c -eq 0 && $zh_count -gt 0 ]]; then
          missing_modules+="${module}, "
        elif [[ $c -lt $zh_count && $c -gt 0 ]]; then
          partial_modules+="${module}, "
        fi
      done
      missing_modules="${missing_modules%, }"
      partial_modules="${partial_modules%, }"
      printf -- "- **%s** (%s%%)" "$lang" "$pct_int"
      [[ -n "$missing_modules" ]] && printf " — 完全缺失：\`%s\`" "$missing_modules"
      [[ -n "$partial_modules" ]] && printf " — 部分缺失：\`%s\`" "$partial_modules"
      [[ -z "$missing_modules" && -z "$partial_modules" ]] && printf " — 完全覆蓋 ✅"
      printf "\n"
    done
    echo
    echo "## 怎麼補翻譯"
    echo
    echo "1. 找到 \`src/i18n/{module}.ts\` 的目標 module"
    echo "2. 在缺失的 \`{lang}: { ... }\` block 裡加 keys（複製 en block 為起點）"
    echo "3. 跑 \`npm run build\` 確認 build pass"
    echo "4. 開 PR，標題 \`[i18n] add {lang} translations for {module}\`"
    echo
    echo "## 自動化規劃"
    echo
    echo "- ✅ #8 audit script（已 ship 2026-04-25）"
    echo "- ✅ #9 dashboard 露出此覆蓋率（同 session ship）"
    echo "- ✅ #10 visual diff CI 抓結構漂移（同 session ship）"
    echo "- ✅ #11 visual smoke test SOP 寫進 REWRITE-PIPELINE Stage 4（同 session ship）"
    echo
    echo "## Re-run"
    echo
    echo '```bash'
    echo "bash scripts/tools/i18n-coverage-audit.sh --report"
    echo '```'
    echo
    echo "🧬"
  } > "$OUT"

  echo "✅ Report written: $OUT"
  exit 0
fi

# Default: human-readable table
echo "📋 i18n Coverage Audit"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
printf "%-15s" "Module"
for lang in "${LANGS[@]}"; do printf "%6s" "$lang"; done
echo
echo "─────────────────────────────────────────────────────────────"
for module in "${MODULES[@]}"; do
  printf "%-15s" "$module"
  for lang in "${LANGS[@]}"; do
    printf "%6d" "$(get_count "$module" "$lang")"
  done
  echo
done
echo "─────────────────────────────────────────────────────────────"
printf "%-15s" "TOTAL"
for lang in "${LANGS[@]}"; do printf "%6d" "$(get_total "$lang")"; done
echo
printf "%-15s" "Coverage %"
for lang in "${LANGS[@]}"; do
  total=$(get_total "$lang")
  pct=$(awk "BEGIN { printf \"%.0f\", ($total / $MAX_TOTAL) * 100 }")
  printf "%5s%%" "$pct"
done
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "💡 模式："
echo "  --json              JSON 輸出"
echo "  --json-out FILE     寫 JSON 到指定檔案"
echo "  --report            寫 reports/i18n-coverage-YYYY-MM-DD.md"
