#!/bin/bash
# sitemap-prune-hreflang.sh — 後備驗證：掃 dist/sitemap-0.xml + dist/ 結構
# 移除指向不存在 .html 的 hreflang alternate（雙保險，Astro serialize hook 為主解）
#
# 用法：
#   bash scripts/tools/sitemap-prune-hreflang.sh                 # 跑驗證 + 修補
#   bash scripts/tools/sitemap-prune-hreflang.sh --check         # 只報告，不修
#   bash scripts/tools/sitemap-prune-hreflang.sh --json          # JSON 輸出
#
# 觸發位置：
#   1. npm run build 之後（手動或 CI）
#   2. 心跳 Beat 1 sync.sh 之後（如果有 dist/）
#
# 邏輯：
#   1. 解析 dist/sitemap-0.xml 抽出所有 <xhtml:link rel="alternate" hreflang="X" href="URL"/>
#   2. 對每個 URL 推 dist/{path}/index.html 是否存在
#   3. 不存在 → 標記為 fake hreflang
#   4. 若非 --check：重寫 sitemap-0.xml 移除 fake alternate

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

MODE="fix"
case "$1" in
    --check) MODE="check" ;;
    --json) MODE="json" ;;
esac

SITEMAP="dist/sitemap-0.xml"
DIST="dist"

if [ ! -f "$SITEMAP" ]; then
    echo -e "${RED}❌ $SITEMAP 不存在。請先跑 npm run build${NC}"
    exit 1
fi

# 抽出所有 hreflang URLs
TMP=$(mktemp)
trap "rm -f $TMP $TMP.fix $TMP.fakes" EXIT

grep -oE '<xhtml:link rel="alternate" hreflang="[^"]+" href="https://taiwan\.md[^"]+"' "$SITEMAP" \
  | sed -E 's|.*hreflang="([^"]+)".*href="https://taiwan\.md([^"]+)".*|\1\t\2|' \
  > "$TMP"

total=$(wc -l < "$TMP" | tr -d ' ')
fake_count=0
> "$TMP.fakes"

while IFS=$'\t' read -r lang path; do
    [ -z "$path" ] && continue
    # path 範例：/en/people/吳哲宇/
    # dist 對應：dist/en/people/吳哲宇/index.html
    # URL decode 不需要—dist/ 已是 UTF-8 檔名
    target="${DIST}${path}index.html"
    # 處理結尾無 / 的情況
    if [ "${path: -1}" != "/" ]; then
        target="${DIST}${path}/index.html"
    fi
    if [ ! -f "$target" ]; then
        fake_count=$((fake_count + 1))
        echo -e "${lang}\t${path}" >> "$TMP.fakes"
    fi
done < "$TMP"

# 統計
real=$((total - fake_count))
if [ "$total" -gt 0 ]; then
    fake_pct=$(awk -v f="$fake_count" -v t="$total" 'BEGIN { printf "%.1f", f * 100 / t }')
else
    fake_pct="0.0"
fi

case "$MODE" in
    json)
        echo "{"
        echo "  \"total_hreflang\": $total,"
        echo "  \"real\": $real,"
        echo "  \"fake\": $fake_count,"
        echo "  \"fake_pct\": $fake_pct,"
        echo "  \"fakes_by_lang\": {"
        awk -F'\t' '{print $1}' "$TMP.fakes" | sort | uniq -c | sort -rn | \
            awk 'BEGIN{first=1} {if(!first)print ","; printf "    \"%s\": %d", $2, $1; first=0} END{print ""}'
        echo "  }"
        echo "}"
        ;;

    check)
        echo "📋 sitemap hreflang 驗證報告"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  Total hreflang: $total"
        echo -e "  ${GREEN}✅ Real: $real${NC}"
        if [ "$fake_count" -eq 0 ]; then
            echo -e "  ${GREEN}🎉 無 fake hreflang，sitemap 健康${NC}"
        else
            echo -e "  ${RED}❌ Fake: $fake_count ($fake_pct%)${NC}"
            echo ""
            echo "  各語言 fake count:"
            awk -F'\t' '{print "    " $1}' "$TMP.fakes" | sort | uniq -c | sort -rn | head -10
            echo ""
            echo "  抽樣 fake URL（前 10 個）："
            head -10 "$TMP.fakes" | awk -F'\t' '{print "    https://computex-md.pages.dev" $2 "  (lang=" $1 ")"}'
            echo ""
            echo -e "  ${YELLOW}修補：bash scripts/tools/sitemap-prune-hreflang.sh${NC}"
        fi
        ;;

    fix|*)
        echo "📋 sitemap hreflang 修補"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  Total hreflang: $total"
        echo -e "  ${GREEN}✅ Real: $real${NC}"
        if [ "$fake_count" -eq 0 ]; then
            echo -e "  ${GREEN}🎉 無 fake hreflang，無需修補${NC}"
            exit 0
        fi
        echo -e "  ${RED}❌ Fake: $fake_count ($fake_pct%) — 移除中...${NC}"

        # 重寫 sitemap：對每個 fake (lang, path) pair，移除整個 <xhtml:link .../>
        cp "$SITEMAP" "$SITEMAP.bak"
        cp "$SITEMAP" "$TMP.fix"
        while IFS=$'\t' read -r lang path; do
            [ -z "$path" ] && continue
            # 構造 fake link tag pattern
            # <xhtml:link rel="alternate" hreflang="LANG" href="https://computex-md.pages.dev/PATH"/>
            tag_pattern="<xhtml:link rel=\"alternate\" hreflang=\"${lang}\" href=\"https://computex-md.pages.dev${path}\"/>"
            # 用 python 處理 (sed 不適合處理 UTF-8 + 特殊字元)
            python3 -c "
import sys
p = '$TMP.fix'
content = open(p).read()
tag = '''$tag_pattern'''
content = content.replace(tag, '')
open(p, 'w').write(content)
"
        done < "$TMP.fakes"

        # 比對前後 hreflang 數量
        before_count=$(grep -o "hreflang=" "$SITEMAP.bak" | wc -l | tr -d ' ')
        after_count=$(grep -o "hreflang=" "$TMP.fix" | wc -l | tr -d ' ')
        removed=$((before_count - after_count))

        # Atomic rename
        mv "$TMP.fix" "$SITEMAP"

        echo -e "  ${GREEN}✅ 修補完成${NC}"
        echo "    Before: $before_count hreflang"
        echo "    After:  $after_count hreflang"
        echo "    Removed: $removed fake hreflang"
        echo "    Backup: $SITEMAP.bak"
        ;;
esac

if [ "$fake_count" -gt 0 ] && [ "$MODE" = "check" ]; then
    exit 1
fi
exit 0
