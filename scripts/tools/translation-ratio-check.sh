#!/usr/bin/env bash
# translation-ratio-check.sh — 翻譯 PR 審核第一道檢查
#
# 用法:
#   bash scripts/tools/translation-ratio-check.sh --pr 367
#   bash scripts/tools/translation-ratio-check.sh knowledge/ja/Society/article.md [...]
#   bash scripts/tools/translation-ratio-check.sh --all-ja
#
# 作用：
#   比對翻譯檔案跟 translatedFrom 指向的中文 SSOT 字數比率，
#   識別「摘要式翻譯」（AI 工具的預設行為）造成的內容截斷。
#
# 健全 ratio 範圍（2026-04-11 實測基準）：
#   zh → en:  2.20-3.50  (<1.50 = TRUNCATED)
#   zh → ja:  1.10-1.50  (<0.80 = TRUNCATED)
#   zh → ko:  1.20-1.65  (<0.85 = TRUNCATED)
#   zh → es/fr/de: 2.0-4.0  (<1.5 = TRUNCATED)
#
# 來源：2026-04-11 session α 審核 27 個翻譯 PR 的實戰經驗

set -o pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

RED='\033[0;31m'; YEL='\033[0;33m'; GRN='\033[0;32m'
BLU='\033[0;34m'; DIM='\033[0;90m'; RST='\033[0m'

# Parse args
MODE="files"
PR_NUM=""
FILES=()

if [[ "${1:-}" == "--pr" ]] && [[ -n "${2:-}" ]]; then
  MODE="pr"
  PR_NUM="$2"
elif [[ "${1:-}" == --all-* ]]; then
  # 2026-07-25 泛化：原本只硬編碼 --all-ja 與 --all-en，其他語言傳進來會被
  # 當成檔名（FILES=("--all-ar")）→ 找不到檔案 → 假 FAIL 1/1。新語言出生時
  # 沒人會想到這裡也寫死了語言（神經迴路：新語言出生時感知系統不會自動更新）。
  MODE="all-lang"
  ALL_LANG="${1#--all-}"
elif [[ "${1:-}" == "--help" ]] || [[ -z "${1:-}" ]]; then
  grep "^#" "$0" | head -25
  exit 0
else
  FILES=("$@")
fi

# Collect files (bash 3 compatible — no mapfile)
if [[ "$MODE" == "pr" ]]; then
  while IFS= read -r line; do
    [[ -n "$line" ]] && FILES+=("$line")
  done < <(gh pr diff "$PR_NUM" --name-only 2>/dev/null | grep "^knowledge/" | grep -v "_translations.json")
  if [[ ${#FILES[@]:-0} -eq 0 ]]; then
    echo -e "${RED}❌ 無法取得 PR #$PR_NUM 的檔案清單${RST}"
    exit 1
  fi
elif [[ "$MODE" == "all-lang" ]]; then
  if [[ ! -d "knowledge/$ALL_LANG" ]]; then
    echo -e "${RED}❌ knowledge/$ALL_LANG 不存在（語言代碼打錯？）${RST}"
    exit 1
  fi
  while IFS= read -r line; do
    FILES+=("$line")
  done < <(find "knowledge/$ALL_LANG/" -name '*.md' ! -name '_*' 2>/dev/null | sort)
  if [[ ${#FILES[@]:-0} -eq 0 ]]; then
    echo -e "${YEL:-}⚠️  knowledge/$ALL_LANG 沒有譯文${RST}"
    exit 0
  fi
fi

# Run Python for accurate character counting (handles unicode properly)
python3 <<PYEOF
import re, sys, os

files = [$(printf '"%s",' "${FILES[@]}")]
files = [f for f in files if f]

def get_body(content):
    m = re.match(r'^---\n.*?\n---\n(.*)', content, re.DOTALL)
    return m.group(1) if m else content

def detect_lang(path):
    m = re.match(r'knowledge/([a-z]{2,5})/', path)
    if not m: return 'zh'
    return m.group(1)

# Healthy ratio ranges
RANGES = {
    'en':    (1.50, 2.20, 3.50),   # (truncated_below, healthy_min, healthy_max)
    'ja':    (0.80, 1.10, 1.50),
    'ko':    (0.85, 1.20, 1.65),
    'es':    (1.50, 2.00, 4.00),
    'fr':    (1.50, 2.00, 4.00),
    'de':    (1.50, 2.00, 4.00),
    'vi':    (1.50, 2.00, 4.30),  # 2026-07-18 Stage 2 校準定案（實測 2.31-3.81，n=3）
    'id':    (1.50, 2.00, 4.30),  # 2026-07-18 Stage 2 校準定案（實測 2.32-3.58，n=3）
    'pt':    (1.50, 2.00, 4.30),  # 2026-07-18 Stage 2 校準定案（實測 2.44-3.97，n=4）
    'hi':    (1.50, 2.00, 4.00),  # 2026-07-18 Stage 2 校準定案（實測 2.20-3.38，n=3；天城文預想較緊湊被實測推翻）
    'ar':    (1.50, 2.00, 3.30),  # 2026-07-25 Stage 3 首批定案（本工具字元比實測
                                  # 2.08-2.95 中位 2.65，n=21）
    'ru':    (1.60, 2.20, 3.90),  # 2026-07-25 Stage 3 首批定案（字元比實測
                                  # 2.31-3.74 中位 2.93，n=29；俄語詞長，上限最高）
                                  # ⚠️ 本表單位是「字元比」不是 bytes 比——首次定案時
                                  # 用 bytes 算差了 1.5 倍（西里爾 2 bytes/char vs
                                  # 中文 3），band 訂太緊而把健康譯文全報 LONG。
                                  # 新語言定 band 一律用本工具自己的輸出，不另外算。
    'zh-TW': (0.95, 1.00, 1.00),
}

PASS = 0
WARN = 0
FAIL = 0
SKIP = 0
results = []


def is_machine_rendered_fact_page(content):
    """這一頁是不是「同一份事實的另一次渲染」，而不是散文翻譯。

    2026-07-29 起，廠商頁（knowledge/{,en/}Vendors/*.md）由
    generate-vendor-pages.py 從官方名錄的同一份 Facts 分別渲染中英文，兩邊各寫
    各的句子，沒有任何一邊是另一邊的翻譯。

    這種頁面過不了本工具的比例帶，而且它過不了是對的：頁面有一半以上是表格
    （年份、日期、展會名、URL），表格內容在兩種語言裡幾乎一樣長，中文字元又比
    英文字元密，整頁字元比自然落在 1.3 至 1.9，遠低於散文翻譯的 2.20。
    86 頁裡 19 頁被判 TRUNCATED，但同一行印的是 secs=6→6 urls=10→10：一個段落
    一條連結都沒少。

    處置照 CLAUDE.md rule 56：單一檢查對這一類頁面降級（skip），不動比例帶、
    不刪這支 gate。降比例帶會讓真正的摘要式翻譯溜過去，那才是這支存在的理由。

    這一類頁面的守門在別處，而且更嚴格：
      tests/article_health/test_vendor_corpus_invariants.py
      逐頁比對中英文的 COMPUTEX 屆數宣稱，任何一邊被手改到不一致就當場失敗。

    判準用 frontmatter 有沒有 vendor: 區塊。將來出現第二類機器渲染頁時，改成一個
    明說的 frontmatter 欄位（例如 renderedFrom: 'facts'）比繼續加資料夾名字乾淨。
    """
    fm = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    return bool(fm and re.search(r'^vendor:\s*$', fm.group(1), re.M))


for f in files:
    if not os.path.exists(f):
        results.append((f, 'MISSING', None, None, None))
        FAIL += 1
        continue

    lang = detect_lang(f)
    if lang == 'zh' or lang == 'zh-TW':
        # Skip zh source files in scanning mode
        continue

    with open(f, encoding='utf-8') as fh:
        content = fh.read()

    if is_machine_rendered_fact_page(content):
        SKIP += 1
        continue

    # Find translatedFrom
    m = re.search(r"translatedFrom:\s*['\"]?([^'\"\n]+)", content)
    if not m:
        results.append((f, 'NO_TRANSLATED_FROM', None, None, None))
        WARN += 1
        continue

    zh_rel = m.group(1).strip()
    zh_path = f"knowledge/{zh_rel}"
    if not os.path.exists(zh_path):
        results.append((f, 'ZH_MISSING', zh_rel, None, None))
        FAIL += 1
        continue

    with open(zh_path, encoding='utf-8') as fh:
        zh_content = fh.read()

    zh_body = get_body(zh_content)
    tr_body = get_body(content)

    if not zh_body:
        results.append((f, 'ZH_EMPTY_BODY', zh_rel, None, None))
        WARN += 1
        continue

    ratio = len(tr_body) / len(zh_body)

    # Section / footnote / url check
    zh_secs = len(re.findall(r'^## ', zh_content, re.M))
    tr_secs = len(re.findall(r'^## ', content, re.M))
    zh_fns = len(re.findall(r'^\[\^[\w-]+\]:', zh_content, re.M))
    tr_fns = len(re.findall(r'^\[\^[\w-]+\]:', content, re.M))
    zh_urls = zh_content.count('http')
    tr_urls = content.count('http')

    extra_info = {
        'secs': f"{zh_secs}→{tr_secs}",
        'fns': f"{zh_fns}→{tr_fns}",
        'urls': f"{zh_urls}→{tr_urls}",
    }

    # Determine verdict
    trunc, healthy_min, healthy_max = RANGES.get(lang, (0.55, 0.70, 1.30))

    if ratio < trunc:
        verdict = 'TRUNCATED'
        FAIL += 1
    elif ratio < healthy_min:
        verdict = 'THIN'
        WARN += 1
    elif ratio > healthy_max:
        verdict = 'LONG'
        WARN += 1
    elif zh_urls >= 3 and tr_urls == 0:
        verdict = 'NO_URLS'
        WARN += 1
    elif tr_urls < zh_urls * 0.5 and zh_urls >= 5:
        verdict = 'URL_LOSS'
        WARN += 1
    elif zh_secs > 0 and tr_secs < zh_secs:
        verdict = f'MISSING_SECTIONS({zh_secs-tr_secs})'
        WARN += 1
    else:
        verdict = 'OK'
        PASS += 1

    results.append((f, verdict, zh_rel, ratio, extra_info))

# Print report
print()
print(f"{'File':<60} {'Ratio':>6}  {'Verdict':<20} {'Structure'}")
print("─" * 120)
for f, verdict, zh_rel, ratio, info in results:
    short = os.path.basename(f)[:58]
    if ratio is None:
        print(f"{short:<60} {'—':>6}  {verdict:<20} —")
        continue
    color = ''
    if verdict == 'OK':
        color = '\033[0;32m'  # green
    elif verdict in ('THIN', 'LONG', 'URL_LOSS', 'NO_URLS') or 'MISSING_SECTIONS' in verdict:
        color = '\033[0;33m'  # yellow
    else:
        color = '\033[0;31m'  # red
    reset = '\033[0m'
    s = f"secs={info['secs']} fns={info['fns']} urls={info['urls']}" if info else ''
    print(f"{short:<60} {ratio:>5.2f}  {color}{verdict:<20}{reset} {s}")

print()
print(f"\033[0;90m{'─'*120}\033[0m")
if SKIP:
    # 跳過的數量一定要印出來。靜默跳過會讓「87 檔全綠」跟「68 檔全綠加 19 檔沒驗」
    # 長得一模一樣，而那正是這支工具要防的那種失真。
    print(
        f"\033[0;90mskip {SKIP} 檔：機器渲染的事實頁（frontmatter 有 vendor:），"
        f"不是散文翻譯，比例帶不適用。守門在 "
        f"tests/article_health/test_vendor_corpus_invariants.py\033[0m"
    )
total = PASS + WARN + FAIL
if FAIL > 0:
    print(f"\033[0;31m❌ FAIL\033[0m: {FAIL} / {total}  (TRUNCATED translations require rework)")
elif WARN > 0:
    print(f"\033[0;33m⚠️  WARN\033[0m: {WARN} / {total}  (acceptable for merge + follow-up)")
else:
    print(f"\033[0;32m✅ PASS\033[0m: {PASS} / {total}")
print()

sys.exit(1 if FAIL > 0 else 0)
PYEOF
