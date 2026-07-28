#!/bin/bash
# dead-cross-ref-scan.sh — 掃 knowledge/ 所有 cross-ref 目標存在性
#
# 用途：偵測 `[label](/category/slug)` 形式 cross-ref 中目標不存在的條目，
# 避免 polish 加 placeholder cross-ref 推升 EXP-A 404 rate（LESSONS-INBOX 2026-04-21 γ）
#
# 使用方式：
#   bash scripts/tools/dead-cross-ref-scan.sh                    # 人類可讀輸出
#   bash scripts/tools/dead-cross-ref-scan.sh --json             # JSON 輸出
#   bash scripts/tools/dead-cross-ref-scan.sh --inbox-format     # 產生 ARTICLE-INBOX P3 backlog 條目
#
# 邏輯：
#   1. grep 所有 knowledge/**/*.md 找 `[label](/category/slug)` 形式
#   2. URL-decode slug，對應到 knowledge/Category/slug.md（首字大寫）
#   3. 不存在 → dead，產報告
#   4. 排除：anchor (#)、外部 URL、非 knowledge category（about/images/resources）

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

MODE="human"
case "$1" in
    --json) MODE="json" ;;
    --inbox-format) MODE="inbox" ;;
esac

TMP=$(mktemp)
trap "rm -f $TMP" EXIT

total_files=0
total_refs=0
dead_refs=0

# Category mapping (lowercase URL → first-letter-uppercase folder)
to_category() {
    case "$1" in
        people) echo "People" ;;
        society) echo "Society" ;;
        history) echo "History" ;;
        culture) echo "Culture" ;;
        music) echo "Music" ;;
        nature) echo "Nature" ;;
        technology) echo "Technology" ;;
        food) echo "Food" ;;
        art) echo "Art" ;;
        lifestyle) echo "Lifestyle" ;;
        geography) echo "Geography" ;;
        economy) echo "Economy" ;;
        *) echo "" ;;  # Skip non-knowledge categories
    esac
}

# URL decode (%XX → byte) using printf
url_decode() {
    printf '%b' "${1//%/\\x}"
}

while IFS= read -r article; do
    total_files=$((total_files + 1))
    while IFS= read -r url_raw; do
        [ -z "$url_raw" ] && continue
        total_refs=$((total_refs + 1))

        # Strip trailing slash and #anchor
        url=$(echo "$url_raw" | sed 's/\/$//' | sed 's/#.*//')
        category=$(echo "$url" | awk -F/ '{print $2}')
        slug_encoded=$(echo "$url" | awk -F/ '{print $3}')
        [ -z "$category" ] || [ -z "$slug_encoded" ] && continue

        cat_proper=$(to_category "$category")
        [ -z "$cat_proper" ] && continue  # Skip non-knowledge category

        # URL decode slug
        slug=$(url_decode "$slug_encoded")
        target="knowledge/${cat_proper}/${slug}.md"

        if [ ! -f "$target" ]; then
            dead_refs=$((dead_refs + 1))
            printf '%s\t%s\t%s\n' "$article" "$url" "$target" >> "$TMP"
        fi
    done < <(grep -oE '\]\(/[a-zA-Z]+/[^)#]+\)' "$article" 2>/dev/null | sed -E 's/^\]\(//;s/\)$//')
done < <(find knowledge -maxdepth 2 -name "*.md" -type f ! -name "_*")

# Compute percentage with awk (POSIX-safe)
if [ "$total_refs" -gt 0 ]; then
    pct=$(awk -v d="$dead_refs" -v t="$total_refs" 'BEGIN { printf "%.1f", d * 100 / t }')
else
    pct="0.0"
fi

unique_targets=$(awk -F'\t' '{print $3}' "$TMP" | sort -u | wc -l | tr -d ' ')

case "$MODE" in
    json)
        echo "{"
        echo "  \"total_files\": $total_files,"
        echo "  \"total_refs\": $total_refs,"
        echo "  \"dead_refs\": $dead_refs,"
        echo "  \"dead_rate_pct\": $pct,"
        echo "  \"unique_missing_targets\": $unique_targets,"
        echo "  \"dead\": ["
        first=1
        while IFS=$'\t' read -r src url target; do
            [ -z "$src" ] && continue
            if [ $first -eq 1 ]; then first=0; else echo ","; fi
            printf '    {"source": "%s", "url": "%s", "missing_target": "%s"}' "$src" "$url" "$target"
        done < "$TMP"
        echo ""
        echo "  ]"
        echo "}"
        ;;

    inbox)
        if [ ! -s "$TMP" ]; then
            echo "✅ 無 dead cross-ref，不需 P3 backlog 條目"
            exit 0
        fi
        echo "# Dead cross-ref P3 backlog 候選（${dead_refs} 條失效，${unique_targets} 個獨立目標）"
        echo ""
        echo "_由 \`scripts/tools/dead-cross-ref-scan.sh --inbox-format\` 產生 — $(date +%Y-%m-%d)_"
        echo ""
        # group by target，列引用來源
        awk -F'\t' '{print $3 "\t" $1}' "$TMP" | sort | awk -F'\t' '
            {
                if ($1 != prev) {
                    if (prev != "") print ""
                    n = split($1, parts, "/")
                    cat = parts[2]
                    file = parts[3]
                    sub(/\.md$/, "", file)
                    print "### " file
                    print ""
                    print "- **Type**: `NEW`"
                    print "- **Category**: " cat
                    print "- **Priority**: `P3` (dead cross-ref backlog)"
                    print "- **Status**: `pending`"
                    print "- **Requested**: 2026-04-23 by dead-cross-ref-scan.sh"
                    print "- **Notes**: 已被引用但無條目（產生 404 tail 風險）。引用來源："
                    prev = $1
                }
                src = $2
                sub(/^knowledge\//, "", src)
                print "  - " src
            }
        '
        ;;

    human|*)
        if [ "$dead_refs" -eq 0 ]; then
            echo -e "${GREEN}✅ 掃描 $total_files 篇文章 / $total_refs 個 cross-ref，全部目標存在${NC}"
            exit 0
        fi
        echo -e "${RED}❌ 發現 $dead_refs 個 dead cross-ref（$total_refs 個 cross-ref 中，$pct%）${NC}"
        echo -e "${YELLOW}🎯 涵蓋 $unique_targets 個獨立缺失目標${NC}"
        echo ""
        echo "（dead cross-ref → CF 7d 404 tail 來源；建議造 P3 backlog，見 --inbox-format）"
        echo ""
        # group by target, sorted by reference count desc (top 20)
        awk -F'\t' '{print $3}' "$TMP" | sort | uniq -c | sort -rn | head -20 | while read -r cnt target; do
            echo -e "${YELLOW}🎯 缺：${target}${NC}  (被 ${cnt} 處引用)"
            grep -F "$(printf '\t')${target}" "$TMP" | head -5 | awk -F'\t' '{
                src = $1; sub(/^knowledge\//, "", src)
                print "   ← " src
            }'
            extra=$((cnt - 5))
            if [ "$extra" -gt 0 ]; then
                echo "   ... 還有 $extra 處"
            fi
            echo ""
        done
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo "📊 $total_files 篇 | $total_refs cross-ref | $dead_refs dead ($pct%) | $unique_targets 獨立缺失"
        echo "💡 P3 backlog 條目: bash scripts/tools/dead-cross-ref-scan.sh --inbox-format"
        echo "💡 完整 JSON: bash scripts/tools/dead-cross-ref-scan.sh --json"
        ;;
esac

if [ "$dead_refs" -gt 0 ]; then
    exit 1
fi
exit 0
