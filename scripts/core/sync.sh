#!/usr/bin/env bash
# COMPUTEX.md 統一同步腳本：knowledge/ SSOT → src/content/ 投影層
#
# 設計：
#   - SSOT: enabled lang codes from src/config/languages.mjs
#   - zh-TW (default): knowledge/{Category}/ → src/content/zh-TW/{category}/
#   - 其他 lang:       knowledge/{lang}/{Category}/ → src/content/{lang}/{category}/
#   - Resources:       knowledge/resources/ (zh-TW) + knowledge/{lang}/resources/ → src/content/{lang}/resources/
#   - Root files:      knowledge/{lang}/*.md (root level) → src/content/{lang}/*.md
#   - 冪等：先 rm -rf 所有 enabled lang dirs 再重建
#
# 用法：bash scripts/core/sync.sh
#
# 2026-05-12 admiring-montalcini-post-finale refactor:
#   - 從 217 行 5x repeat → 模組化 sync_lang() function
#   - 修補既有 bug:
#     (a) fr/es 加進 rm list（清 336 zombie articles）
#     (b) 各 lang 都跑 resources/ 同步（原本只跑 zh-TW + en）
#     (c) 各 lang 的 root-level .md 也搬（原本只搬 zh-TW _Home.md，
#         knowledge/en/{root.md} 等被略過 → 8 silent missing 根因）
#   - SSOT 驅動：active lang list 從 src/config/languages.mjs 讀取
#
# 對應：reports/sync-architecture-evolution-2026-05-12.md v2.0 Ship 1

set -euo pipefail

# ────────────────── 設定 ──────────────────
readonly REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

# Categories（跟 knowledge/ 目錄結構對齊；新增分類時這裡 + knowledge/ 一起加）
readonly CATEGORIES=(
  About Art Culture Economy Food Geography History
  Lifestyle Music Nature People Politics Society Technology
)

# Enabled lang codes 從 SSOT 讀取
ENABLED_LANGS=$(node -e "
  import('./src/config/languages.mjs')
    .then(m => console.log(m.ENABLED_LANGUAGE_CODES.join(' ')))
    .catch(e => { console.error(e.message); process.exit(1); });
" 2>&1) || {
  echo "❌ 無法從 src/config/languages.mjs 讀取 ENABLED_LANGUAGE_CODES" >&2
  echo "   錯誤：$ENABLED_LANGS" >&2
  exit 2
}

if [ -z "$ENABLED_LANGS" ]; then
  echo "❌ ENABLED_LANGUAGE_CODES 為空" >&2
  exit 2
fi

# ────────────────── Header ──────────────────
echo "🚀 COMPUTEX.md sync — knowledge/ SSOT → src/content/ 投影層"
echo "═══════════════════════════════════════════════════════"
echo "  Enabled langs: $ENABLED_LANGS"
echo ""

# ────────────────── Phase 1: 清空 ──────────────────
echo "🧹 Phase 1: 清空 src/content/{lang}/ (冪等重建)..."
for lang in $ENABLED_LANGS; do
  if [ -d "src/content/$lang" ]; then
    rm -rf "src/content/$lang"
  fi
done
echo "  ✅ Cleaned: $ENABLED_LANGS"
echo ""

# ────────────────── Phase 2: 同步 sync_lang() ──────────────────
KNOWLEDGE_COUNT=$(find knowledge/ -name "*.md" | wc -l | tr -d ' ')
SYNCED_TOTAL=0

# sync_lang LANG_CODE — 把 knowledge/{lang}/ (或 zh-TW 的 knowledge/ root) 同步到 src/content/{lang}/
sync_lang() {
  local lang="$1"
  local src_root dst_root count=0

  # zh-TW 特例：source 在 knowledge/ root（不在 knowledge/zh-TW/）
  if [ "$lang" = "zh-TW" ]; then
    src_root="knowledge"
  else
    src_root="knowledge/$lang"
  fi
  dst_root="src/content/$lang"

  if [ ! -d "$src_root" ]; then
    echo "  ⚠️  $lang: SKIP (no $src_root/)"
    return
  fi

  # 2a. Category subdirs (knowledge/{Cat}/*.md → src/content/{lang}/{cat}/*.md)
  for category in "${CATEGORIES[@]}"; do
    local src_dir="$src_root/$category"
    [ ! -d "$src_dir" ] && continue

    local cat_lower
    cat_lower=$(echo "$category" | tr '[:upper:]' '[:lower:]')
    local dst_dir="$dst_root/$cat_lower"
    mkdir -p "$dst_dir"

    for file in "$src_dir"/*.md; do
      [ ! -f "$file" ] && continue
      cp "$file" "$dst_dir/$(basename "$file")"
      count=$((count + 1))
    done
  done

  # 2b. resources/ subdir (各 lang 都有，原本 bug：只跑 zh-TW + en)
  if [ -d "$src_root/resources" ]; then
    mkdir -p "$dst_root/resources"
    for file in "$src_root/resources"/*.md; do
      [ ! -f "$file" ] && continue
      cp "$file" "$dst_root/resources/$(basename "$file")"
      count=$((count + 1))
    done
  fi

  # 2c. Root-level .md files (knowledge/{lang}/*.md → src/content/{lang}/*.md)
  # 原本 bug：只搬 knowledge/_Home.md，其他 lang root 的 .md 被略過 → silent missing
  for file in "$src_root"/*.md; do
    [ ! -f "$file" ] && continue
    cp "$file" "$dst_root/$(basename "$file")"
    count=$((count + 1))
  done

  SYNCED_TOTAL=$((SYNCED_TOTAL + count))
  printf "  ✅ %-6s %4d files\n" "$lang" "$count"
}

echo "📁 Phase 2: 同步 (per lang)..."
for lang in $ENABLED_LANGS; do
  sync_lang "$lang"
done
echo ""

# ────────────────── Phase 3: Frontmatter 修復 (legacy) ──────────────────
# 注意：fix-all-frontmatter.py 只在缺 `title:` 時重建 frontmatter (99% 檔案 no-op)
# 留著是 legacy migration safeguard，未來 contributor 直丟到 src/content/ 不再可能（gitignore 後）
echo "🔧 Phase 3: Frontmatter 修復 (legacy fallback)..."
if [ -f "scripts/utils/fix-all-frontmatter.py" ]; then
  python3 scripts/utils/fix-all-frontmatter.py 2>&1 | tail -2
else
  echo "  ⚠️  scripts/utils/fix-all-frontmatter.py 不存在，跳過"
fi
echo ""

# ────────────────── Phase 4: 圖片健康檢查 ──────────────────
echo "🖼️  Phase 4: 圖片健康檢查..."
if [ -f "scripts/utils/check-images.mjs" ]; then
  node scripts/utils/check-images.mjs 2>&1 | tail -5 || echo "  ⚠️  圖片檢查回報警告（非致命）"
else
  echo "  ⚠️  scripts/utils/check-images.mjs 不存在，跳過"
fi
echo ""

# ────────────────── Footer ──────────────────
CONTENT_FINAL=$(find src/content/ -name "*.md" | wc -l | tr -d ' ')

echo "═══════════════════════════════════════════════════════"
echo "✨ Sync 完成"
echo "   📊 knowledge/ source: $KNOWLEDGE_COUNT files"
echo "   📊 src/content/ final: $CONTENT_FINAL files"
echo "   📊 synced: $SYNCED_TOTAL files"
echo ""
echo "▶️  下一步：npm run build"
