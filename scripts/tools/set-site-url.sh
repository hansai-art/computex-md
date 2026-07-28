#!/usr/bin/env bash
# 換站點網址：單一入口。母體把網址散在 astro.config / generate-api / CNAME / llms.txt，
# 這支把它收斂成一個指令，避免換網域時漏改造成 canonical 錯亂。
set -euo pipefail
NEW="${1:-}"
[ -z "$NEW" ] && { echo "用法: $0 https://your.domain"; exit 1; }
NEW="${NEW%/}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OLD=$(python3 -c "import json;print(json.load(open('$ROOT/config/site.json'))['url'].rstrip('/'))")
[ "$OLD" = "$NEW" ] && { echo "已經是 $NEW"; exit 0; }
cd "$ROOT"
grep -rl "$OLD" src scripts public cli workers i18n config tools tests astro.config.mjs 2>/dev/null \
  | xargs -I{} sed -i '' "s|$OLD|$NEW|g" {}
python3 - "$NEW" <<'PY'
import json,sys
p='config/site.json'; d=json.load(open(p)); d['url']=sys.argv[1]
json.dump(d,open(p,'w'),ensure_ascii=False,indent=2); open(p,'a').write('\n')
PY
echo "${NEW#https://}" > public/CNAME
echo "✅ $OLD → $NEW（含 public/CNAME）"
