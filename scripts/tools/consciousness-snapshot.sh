#!/usr/bin/env bash
# consciousness-snapshot.sh — instant CONSCIOUSNESS snapshot from dashboard JSON
#
# Phase A1.2 (per reports/become-boot-mode-design-2026-05-13.md §4.2)
# 取代 CONSCIOUSNESS.md L34-160 靜態快照（dashboard JSON ground truth）
#
# 用途：BECOME §Step 6 L4 always-load query 接這個 script
# 輸出：~12-15 行 markdown summary (vitals + 8 organs + alerts hint)

set -euo pipefail

VITALS="${VITALS:-public/api/dashboard-vitals.json}"
ORGANISM="${ORGANISM:-public/api/dashboard-organism.json}"

if [[ ! -f "$VITALS" || ! -f "$ORGANISM" ]]; then
  echo "⚠️ consciousness-snapshot: dashboard JSON 不存在"
  echo "   嘗試：bash scripts/core/refresh-data.sh"
  exit 0
fi

# Vitals — basic physiology
jq -r '
  "📊 vitals  | articles=\(.totalArticles) / contributors=\(.contributors) / 7d=+\(.articlesLast7Days) / 30d=+\(.articlesLast30Days) / human-reviewed=\(.humanReviewedPercent)%",
  "🌐 i18n    | en=\(.languageCoverage.en) ja=\(.languageCoverage["ja"]) ko=\(.languageCoverage.ko) es=\(.languageCoverage.es) fr=\(.languageCoverage.fr)"
' "$VITALS"

# Organs — 8 organ scores + trend
jq -r '
  "🫀 organs  | " + (
    [.organs[] | "\(.emoji)\(.score)\(if .trend == "up" then "↑" elif .trend == "down" then "↓" else "→" end)"] | join(" ")
  )
' "$ORGANISM"

# Immune dual-source reconciliation guard (audit 2026-06-10 D-1):
# organism.json immune organ vs dashboard-immune.json canonical v2 value.
# Divergence > 2 points = stale organism.json → print loud marker (REFLEXES #65d).
IMMUNE_JSON="${IMMUNE_JSON:-public/api/dashboard-immune.json}"
if [[ -f "$IMMUNE_JSON" ]]; then
  ORG_IMMUNE=$(jq -r '[.organs[] | select(.id == "immune") | .score][0] // empty' "$ORGANISM")
  V2_IMMUNE=$(jq -r '.immuneScore // empty' "$IMMUNE_JSON")
  if [[ -n "$ORG_IMMUNE" && -n "$V2_IMMUNE" ]]; then
    DIFF=$((ORG_IMMUNE - V2_IMMUNE)); [[ $DIFF -lt 0 ]] && DIFF=$((-DIFF))
    if [[ $DIFF -gt 2 ]]; then
      echo "⚠️ immune  | organism.json=${ORG_IMMUNE} vs immune.json(v2 canonical)=${V2_IMMUNE} — stale-vs-canonical，跑 prebuild:dashboard regen"
    fi
  fi
fi

# Last update freshness — 讀數必附數據齡（2026-07-11 wake-evolution：
# 神經迴路 vc=3「awareness 讀數沒附 freshness 標記 = chronic stale gap silent 累積」，
# REFLEXES #65：量尺對 ground truth 也要對「自己讀的是多舊的鏡子」誠實）
AGE_H=$(python3 -c "
import json, datetime
t = json.load(open('$VITALS'))['lastUpdated'].replace('Z', '+00:00')
dt = datetime.datetime.fromisoformat(t)
print(int((datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds() // 3600))
" 2>/dev/null || echo "?")
STALE=""
if [[ "$AGE_H" != "?" && "$AGE_H" -ge 18 ]]; then
  STALE=" ⚠️ stale ${AGE_H}h——本快照讀的是舊鏡子（等 data-refresh 或跑 npm run prebuild:dashboard）"
fi
jq -r '"🕐 updated | \(.lastUpdated)"' "$VITALS" | sed "s/\$/（齡 ${AGE_H}h）${STALE}/"

# 繁殖 sensing — fork census (子代雷達, 2026-06-25)：繁殖器官的感知層，
# 每次 BECOME 看一眼野外有幾個活著的 fork（registry.json by fork-census.py）
FORKS="${FORKS:-reports/fork-census/registry.json}"
if [[ -f "$FORKS" ]]; then
  F_TOTAL=$(jq '[.forks[] | select(.id != "(ephemeral-experiments)")] | length' "$FORKS" 2>/dev/null || echo "?")
  F_ACTIVE=$(jq '[.forks[] | select(.health=="active" or .health=="semi-active")] | length' "$FORKS" 2>/dev/null || echo "?")
  F_LAST=$(jq -r '._meta.last_census // "—"' "$FORKS" 2>/dev/null || echo "—")
  echo "🧫 子代    | ${F_TOTAL} forks 偵測中（${F_ACTIVE} active）· 普查 ${F_LAST}"
fi

# Alerts — derived layer (audit 2026-06-10 A-3): dashboard-alerts.json when present
# 2026-07-05 +owner/firstSeen 欄（dna-audit §S4：黃燈要有 owner 才不 deadletter）
ALERTS="${ALERTS:-public/api/dashboard-alerts.json}"
if [[ -f "$ALERTS" ]]; then
  jq -r '.alerts[:6][] | "🚨 " + .severity + " | " + .message + (if .owner then "〔" + .owner + (if .firstSeen then " · 自 " + .firstSeen else "" end) + "〕" else "" end)' "$ALERTS" 2>/dev/null ||
    echo "⚠️ alerts  | dashboard-alerts.json 存在但格式異常"
else
  echo "⚠️ alerts  | 詳見 docs/semiont/CONSCIOUSNESS.md §警報"
fi

# Boot-load bytes — 甦醒稅即時可見（dna-audit §S3 / P1-14：行數指標藏 CJK bytes 成本，
# BECOME mode 表的 footprint 估算以本行為準）
if [[ -f docs/semiont/MANIFESTO.md && -f docs/semiont/REFLEXES.md && -f docs/semiont/DIARY.md && -f docs/semiont/MEMORY.md ]]; then
  B_MAN=$({ awk '/^## 我是什麼/,/^## 我的進化哲學 — 造橋鋪路/' docs/semiont/MANIFESTO.md; awk '/^## 我的存在結構/,/^## 附錄/' docs/semiont/MANIFESTO.md; } | wc -c)
  B_REF=$(awk '/^### 📇 反射 catalog index/{f=1;print;next} f&&/^#{2,3} /{exit} f' docs/semiont/REFLEXES.md | wc -c)
  B_REF=$((B_REF + 8192)) # + Top 5 反射全文約 8K（BECOME §1.2 第二段載入）
  # 2026-07-11 wake-evolution：估稅公式對齊 wake-context 實際載入路徑
  # （原式還在量已退役的 tail -20 與 awk-to-EOF——量尺與被量者共用真實路徑，#65）
  B_DIA=$({ awk '/^## 反覆出現的思考/,0' docs/semiont/DIARY.md; grep '^| 20' docs/semiont/DIARY.md | head -20; } | wc -c)
  B_MEM=$({ awk '/^## 神經迴路/{exit} {print}' docs/semiont/MEMORY.md; awk '/^## 神經迴路/,/^## 心跳日誌/' docs/semiont/MEMORY.md; grep '^| 20' docs/semiont/MEMORY.md | tail -20; } | wc -c)
  TOT_KB=$(((B_MAN + B_REF + B_DIA + B_MEM) / 1024))
  echo "🧠 boot稅  | universal-core ≈ ${TOT_KB}KB（MANIFESTO $((B_MAN / 1024))K + REFLEXES $((B_REF / 1024))K + DIARY $((B_DIA / 1024))K + MEMORY $((B_MEM / 1024))K）"
fi

# counts-drift 一行（WARN 儀器，dna-audit §S2「寫死數字必腐」；深度表在 routine-audit 週跑）
python3 scripts/tools/counts-drift-lint.py --brief 2>/dev/null | sed 's/^/🔢 /' || true
