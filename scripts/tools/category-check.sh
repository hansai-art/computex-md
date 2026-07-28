#!/bin/bash
# category-check.sh — 分類路徑一致性檢查
# 驗證每篇 knowledge/ 文章的 frontmatter category 與實際檔案路徑是否一致
# 用途：HEARTBEAT Beat 1 骨骼器官診斷
#
# Usage:
#   bash scripts/tools/category-check.sh           # 掃描中文 SSOT
#   bash scripts/tools/category-check.sh --json    # JSON 輸出

set -uo pipefail

KNOWLEDGE_DIR="knowledge"
JSON_MODE=false
[[ "${1:-}" == "--json" ]] && JSON_MODE=true

total=0
mismatch=0
missing=0
mismatch_list=()
missing_list=()

# Scan all ZH SSOT .md files (top-level knowledge/<Category>/*.md)
for category_dir in "$KNOWLEDGE_DIR"/*/; do
  # Skip language dirs and hidden dirs
  dir_name=$(basename "$category_dir")
  case "$dir_name" in
    en|ja|ko|es|_*|.*) continue ;;
  esac

  for filepath in "$category_dir"*.md; do
    [[ ! -f "$filepath" ]] && continue
    filename=$(basename "$filepath")
    # Skip Hub files
    [[ "$filename" == _* ]] && continue

    total=$((total + 1))

    # Extract category from frontmatter
    fm_category=$(sed -n '/^---$/,/^---$/p' "$filepath" | grep -E "^category:" | head -1 | sed 's/category: *//; s/["\x27]//g; s/ *$//')

    if [[ -z "$fm_category" ]]; then
      missing=$((missing + 1))
      missing_list+=("$dir_name/$filename")
    elif [[ "$fm_category" != "$dir_name" ]]; then
      mismatch=$((mismatch + 1))
      mismatch_list+=("$dir_name/$filename — frontmatter: '$fm_category', path: '$dir_name'")
    fi
  done
done

if $JSON_MODE; then
  echo "{"
  echo "  \"total\": $total,"
  echo "  \"mismatch\": $mismatch,"
  echo "  \"missingCategory\": $missing,"
  echo "  \"mismatchList\": ["
  for i in "${!mismatch_list[@]}"; do
    comma=","; [[ $i -eq $((${#mismatch_list[@]} - 1)) ]] && comma=""
    echo "    \"${mismatch_list[$i]}\"$comma"
  done
  echo "  ]"
  echo "}"
else
  echo ""
  echo "📁 category-check v1.0 — 分類路徑一致性"
  echo "   掃描: knowledge/<Category>/*.md"
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📊 總計: $total 篇"
  echo "   ✅ 一致: $((total - mismatch - missing))"
  echo "   ⚠️  ���一致: $mismatch"
  echo "   📝 缺 category: $missing"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  if [[ $mismatch -gt 0 ]]; then
    echo ""
    echo "⚠️  frontmatter category ≠ 檔案路徑:"
    for item in "${mismatch_list[@]}"; do
      echo "   • $item"
    done
  fi

  if [[ $missing -gt 0 ]]; then
    echo ""
    echo "📝 缺少 category field（前 20 個）:"
    count=0
    for item in "${missing_list[@]}"; do
      echo "   • $item"
      count=$((count + 1))
      [[ $count -ge 20 ]] && echo "   ... 及更多 $((missing - 20)) 個" && break
    done
  fi

  if [[ $mismatch -eq 0 && $missing -eq 0 ]]; then
    echo ""
    echo "✅ 全部文章分類路徑一致！"
  fi
  echo ""
fi
