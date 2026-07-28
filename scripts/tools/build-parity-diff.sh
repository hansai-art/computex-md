#!/bin/bash
# ─────────────────────────────────────────────────────────────────
# build-parity-diff.sh — 兩個 dist 樹的 HTML parity 比對
# ─────────────────────────────────────────────────────────────────
#
# Refactor 驗證閘門：normalize 掉 Astro 每次 build 合法變動的雜訊
# （asset hash 檔名 / scope id），其餘必須 byte-identical。
#
# 用法（典型 refactor A/B 流程）：
#   npx astro build && mv dist /tmp/dist-baseline     # refactor 前
#   <做 refactor>
#   npx astro build                                    # refactor 後
#   bash scripts/tools/build-parity-diff.sh /tmp/dist-baseline dist
#
# 輸出：每個 content-diff 檔案列前 3 個 + 總結 PARITY: PASS/FAIL。
# 完整 diff 檔案清單寫到 /tmp/parity-diff-files.txt。
#
# ⚠️ 比對前提：兩輪 build 的「輸入」必須凍結（knowledge/ + src/content/ +
# public/api/*.json 不變、git HEAD 不動）。並行 routine（babel 等）會寫
# knowledge/ — 處置 SOP 見 reports/article-template-refactor-2026-06-13.md §7.2
# （備份未 commit 變更 → checkout 還原 → build → 逐檔還原）。
#
# 誕生：2026-06-13 refactor-article session。第一版 sed 用 `|` 同時當
# delimiter 跟 alternation → 錯誤時輸出空檔 → 5,268 檔 empty-vs-empty
# 假 PASS。教訓「驗證器也會說謊」→ normalizer 自帶 self-test（樣本檔
# 輸出 < 100 bytes 即 exit 2），這個 guard 是本工具的可信度來源，不可移除。
# ─────────────────────────────────────────────────────────────────
set -uo pipefail
if [ $# -ne 2 ]; then
  echo "Usage: $0 <dist-baseline> <dist-after>" >&2
  exit 1
fi
A="$1"; B="$2"
[ -d "$A" ] && [ -d "$B" ] || { echo "ERROR: 兩個 dist 目錄都要存在" >&2; exit 1; }

norm() {
  sed -E \
    -e 's#/_astro/[A-Za-z0-9._-]+\.[A-Za-z0-9_-]{8,12}\.(css|js)#/_astro/ASSET.\1#g' \
    -e 's#astro-[a-zA-Z0-9]{6,10}#astro-SCOPE#g' \
    -e 's#data-astro-cid-[a-z0-9]{8,12}#data-astro-cid-X#g'
}

# Self-test：normalizer 在真實檔案上必須產出非空輸出（防 sed 靜默失敗 → 假 PASS）
sample=$(find "$A" -name "index.html" | head -1)
if [ -z "$sample" ] || [ "$(norm < "$sample" | wc -c)" -lt 100 ]; then
  echo "NORMALIZER SELF-TEST FAILED on ${sample:-<no html found>}" >&2
  exit 2
fi
echo "normalizer self-test ok ($(norm < "$sample" | wc -c | tr -d ' ') bytes from sample)"

fail=0
( cd "$A" && find . -name "*.html" | sort ) > /tmp/parity-files-a.txt
( cd "$B" && find . -name "*.html" | sort ) > /tmp/parity-files-b.txt
if ! diff -q /tmp/parity-files-a.txt /tmp/parity-files-b.txt > /dev/null; then
  echo "FILE SET DIFFERS:"
  diff /tmp/parity-files-a.txt /tmp/parity-files-b.txt | head -20 || true
  fail=1
fi

count=0; diffs=0
: > /tmp/parity-diff-files.txt
while IFS= read -r f; do
  count=$((count+1))
  if ! cmp -s <(norm < "$A/$f") <(norm < "$B/$f"); then
    diffs=$((diffs+1))
    echo "$f" >> /tmp/parity-diff-files.txt
    if [ "$diffs" -le 3 ]; then
      echo "DIFF: $f"
      { diff <(norm < "$A/$f") <(norm < "$B/$f") || true; } | head -10
    fi
  fi
done < /tmp/parity-files-a.txt

echo "---"
echo "checked=$count htmlfiles, content-diff=$diffs, fileset-fail=$fail"
if [ "$diffs" -eq 0 ] && [ "$fail" -eq 0 ]; then
  echo "PARITY: PASS"
else
  echo "PARITY: FAIL（diff 清單在 /tmp/parity-diff-files.txt）"
  exit 1
fi
