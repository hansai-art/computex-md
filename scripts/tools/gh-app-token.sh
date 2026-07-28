#!/usr/bin/env bash
# gh-app-token.sh — 換一把一小時就過期的 GitHub App installation token，印到 stdout。
#
# 為什麼存在：twmd-feedback-triage 這條 routine 對 GitHub 只做「開 issue」一件事，
# 卻一直借用哲宇帳號帶 repo + workflow 全權的憑證。改用 App token 之後它手上
# 只剩 taiwan-md 這個庫的 Issues 讀寫，而且一小時自動失效。
# 設計背景：reports/design-bot-identity-feedback-triage-2026-07-25.md
#
# 用法：
#   GH_TOKEN="$(bash scripts/tools/gh-app-token.sh)" gh issue create ...
#   bash scripts/tools/gh-app-token.sh --whoami     # 印身份與權限，不印 token（診斷用）
#
# 環境變數（都有預設，平常不用設）：
#   TAIWANMD_APP_KEY        私鑰路徑，預設 ~/.taiwanmd-app.pem
#   TAIWANMD_APP_CLIENT_ID  App 的 Client ID（非機密）
#   TAIWANMD_APP_INSTALL_ID 指定 installation；省略則自動問 GitHub
#
# 🔴 fail-loud 鐵律：這支腳本永遠不准在失敗時印出空字串。空的 GH_TOKEN 會讓 gh
# 安靜退回 keyring 裡的哲宇身份，變成「以為換了身份、其實沒換」的假綠燈——正是
# REFLEXES #52 與 2026-07-24〜25 連續抓到的靜默吞錯家族。任何一步失敗一律 exit 1。

set -euo pipefail

KEY_PATH="${TAIWANMD_APP_KEY:-$HOME/.taiwanmd-app.pem}"
CLIENT_ID="${TAIWANMD_APP_CLIENT_ID:-Iv23lifwtZnJYK6YU0ea}"
API="https://api.github.com"

die() {
  echo "gh-app-token: $*" >&2
  exit 1
}

b64url() { openssl base64 -A | tr '+/' '-_' | tr -d '='; }

[[ -f $KEY_PATH ]] || die "找不到私鑰 $KEY_PATH（設 TAIWANMD_APP_KEY 指到正確位置）"

# 私鑰權限太鬆就擋下來，不要邊漏邊跑
perm="$(stat -f '%OLp' "$KEY_PATH" 2>/dev/null || stat -c '%a' "$KEY_PATH")"
[[ $perm == 600 || $perm == 400 ]] || die "私鑰權限是 $perm，請 chmod 600 $KEY_PATH"

# ── 1. 用私鑰簽一個 JWT（10 分鐘，只用來換 installation token）─────────────────
now="$(date +%s)"
header="$(printf '{"alg":"RS256","typ":"JWT"}' | b64url)"
# iat 往前退 60 秒，避開本機與 GitHub 的時鐘差
payload="$(printf '{"iat":%d,"exp":%d,"iss":"%s"}' "$((now - 60))" "$((now + 540))" "$CLIENT_ID" | b64url)"
signature="$(printf '%s' "$header.$payload" \
  | openssl dgst -sha256 -sign "$KEY_PATH" -binary \
  | b64url)" || die "JWT 簽章失敗（私鑰格式不對？）"
jwt="$header.$payload.$signature"

api_get() {
  curl -sS --fail-with-body -H "Authorization: Bearer $jwt" \
    -H 'Accept: application/vnd.github+json' \
    -H 'X-GitHub-Api-Version: 2022-11-28' "$API$1"
}

# ── 2. 找 installation id（沒指定就問 GitHub，不要人手抄）────────────────────────
install_id="${TAIWANMD_APP_INSTALL_ID:-}"
if [[ -z $install_id ]]; then
  installs="$(api_get /app/installations)" \
    || die "拿不到 installation 清單（JWT 被拒：App ID／Client ID 或私鑰對不上？）"
  install_id="$(printf '%s' "$installs" | /usr/bin/python3 -c '
import json,sys
rows = json.load(sys.stdin)
if not rows:
    sys.exit("EMPTY")
print(rows[0]["id"])
' 2>/dev/null)" || die "這個 App 還沒安裝到任何帳號。到 App 頁面按 Install App → Only select repositories → taiwan-md"
fi

# ── 3. 換 installation token ───────────────────────────────────────────────────
resp="$(curl -sS --fail-with-body -X POST \
  -H "Authorization: Bearer $jwt" \
  -H 'Accept: application/vnd.github+json' \
  -H 'X-GitHub-Api-Version: 2022-11-28' \
  "$API/app/installations/$install_id/access_tokens")" \
  || die "換 token 失敗（installation $install_id）：$resp"

token="$(printf '%s' "$resp" | /usr/bin/python3 -c '
import json,sys
print(json.load(sys.stdin).get("token",""))
' 2>/dev/null)"

[[ -n $token && $token == ghs_* ]] \
  || die "回應裡沒有合法 token（不印空字串給 gh 用，見檔頭 fail-loud 鐵律）"

if [[ ${1:-} == --whoami ]]; then
  printf '%s' "$resp" | /usr/bin/python3 -c '
import json,sys
d = json.load(sys.stdin)
print("installation :", d.get("repository_selection"))
print("expires_at   :", d.get("expires_at"))
print("permissions  :", json.dumps(d.get("permissions"), ensure_ascii=False))
print("repositories :", ", ".join(r["full_name"] for r in d.get("repositories", [])) or "(all)")
'
  exit 0
fi

printf '%s' "$token"
