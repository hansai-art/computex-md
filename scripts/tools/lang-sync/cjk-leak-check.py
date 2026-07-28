#!/usr/bin/env python3
"""
cjk-leak-check.py — detect partial zh leakage into any target-language body.

verify-translation.py's CJK checks only catch a whole field being byte-
identical to the zh source (the "whole tags array left in Chinese" class of
bug). They can't see a PARTIAL leak — a few zh words or even a whole sentence
left untranslated in the middle of an otherwise-genuine translation.

Two strategies depending on target script:
- ja/ko (CJK-script targets): raw CJK-presence isn't a signal — these
  languages legitimately contain Han characters (kanji/hanja) throughout.
  Instead: zh-only grammatical particles / function words with no legitimate
  standalone ja/ko usage (你/我們/因為/所以/一個/掐死/etc — deliberately
  excludes 的/了, false positives from legitimate ja suffix (先天的) and
  compound-word usage (終了)).
- en/es/fr/vi/id/pt/hi (non-CJK-script targets): the bar is much lower — ANY
  run of 4+ consecutive CJK Han characters in body prose (outside a
  parenthetical proper-noun gloss like "(李安)") is almost certainly a leak,
  since these languages have zero legitimate standalone Han vocabulary.

Found 2026-07-24 in the ko P1 batch: knowledge/ko/Art/taiwanese-cinema.md had
掐死/淘汰/烂死/这一次/悄悄 scattered through the body (Chinese-only figurative
verbs the model apparently gave up translating) plus one entire closing
paragraph left 100% in zh. None of that shows up as "field identical to
source" — it's word-level and sentence-level leakage inside otherwise-real
prose.

Usage:
  python3 cjk-leak-check.py knowledge/ko/Art/taiwanese-cinema.md [more files...]
  python3 cjk-leak-check.py --glob 'knowledge/ko/**/*.md'
  python3 cjk-leak-check.py --since-git <ref>  # files changed since a git ref
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

# Only markers that are unambiguous: zh function words / zh-only figurative
# verbs, never legitimate ja/ko vocabulary on their own. Content nouns
# (e.g. 電影, 政治, 歷史) are deliberately excluded — those DO legitimately
# appear in ja/ko (shared kanji/hanja), so they're not leak signals.
#
# 2026-07-24 修正：表曾含 的/了/一個/淘汰，跟本 docstring 直接矛盾——
# 日文 〜的 是最常見形容詞後綴（言語的/構造的）、了 在 完了/終了、
# 一個（いっこ）是量詞、淘汰（自然淘汰）是常用語。抽測 3/3 健康 ja 檔
# 被誤判（的 ×63/×42/×9），ja lane 在 gate 面前 100% 死路，是 2026-07-24
# ja/ko 大量好譯文被 quarantine 降級的主因之一（另一半是全形括號豁免）。
ZH_ONLY_MARKERS = [
    "這個", "这个", "那個", "那个", "你", "我們", "我们",
    "沒有", "没有", "就是", "都是", "還是", "还是", "因為", "因为",
    "所以", "如果", "這樣", "这样", "這裡", "这里", "這次", "这次",
    "而且", "但是", "可是", "掐死", "烂死",
    "爛死", "淹死", "悄悄", "這一次", "这一次", "被宣告",
]


# Non-CJK-script targets (en/es/fr/vi/id/pt/hi): unlike ja/ko, these languages
# have ZERO legitimate standalone Han-character vocabulary, so the bar is much
# lower — any run of 4+ consecutive CJK Han characters in the body (outside a
# parenthetical, where a short proper-noun citation like "(李安)" is normal)
# is almost certainly a leak, not a false positive.
CJK_RUN_RE = re.compile(r"[一-鿿]{4,}")
NON_CJK_SCRIPT_LANGS = {"en", "es", "fr", "vi", "id", "pt", "hi", "ar", "ru"}

# ─────────────── 合法保留原文的區域：一份清單，兩個分支共用 ───────────────
# 2026-07-25 抽出。此前 ja/ko 與非 CJK 兩個分支各自維護一套豁免，一天之內
# 冒出七個假陽性家族，每個都是「另一邊有、這邊漏了」——括號 gloss 只認半形、
# ja/ko marker 表含合法日文詞、書名號沒進豁免、ja/ko 漏括號、非 CJK 漏引述。
# 單看每次都像新的 edge case，看七次才知道病在「清單沒共用」。新增豁免現在
# 只改這一處（LESSONS 2026-07-25 vc=5）。
#
# 共同判準：上限 30 字。命名 gloss、作品名、短引語在界內；整句整段的洩漏
# 不會剛好躲在括號、書名號或引號裡。
LEGIT_ZH_SPANS = [
    re.compile(r"[(（][^()（）]{0,30}[)）]"),        # 命名 gloss：（李安）、(張懸 Deserts Chang)
    re.compile(r"《[^《》]{0,30}》|〈[^〈〉]{0,30}〉"),  # 作品名：《笠》詩刊、〈小情歌〉
    re.compile(r"「[^「」]{0,30}」|『[^『』]{0,30}』"),  # 短引語：古文引句、受訪者原話
]
PAREN_GLOSS_RE = LEGIT_ZH_SPANS[0]      # 舊名保留，避免外部引用斷掉
TITLE_BRACKET_RE = LEGIT_ZH_SPANS[1]


def legit_spans(text: str) -> list:
    """所有「這裡的中文是編輯選擇不是洩漏」的區間。"""
    return [m.span() for rx in LEGIT_ZH_SPANS for m in rx.finditer(text)]


# 連結類：target 必須保留原文才能解析，不是洩漏
LINK_LIKE_RES = [
    # HTML 標籤（第十一家族 2026-07-27）：標籤內的屬性值是結構不是正文——
    # YouTube 嵌入的 title="大象體操 Elephant Gym -〈水底〉" 是原始影片標題、
    # <a href="/people/草東沒有派對"> 的中文 slug 是站內連結能解析的前提。
    # 兩者都跟 wikilink 同理：保留原文是正確的編輯選擇。救回 en 歷史刪除檔時
    # 現形——10 篇「只有 CJK 洩漏」的譯文全卡在這裡。
    re.compile(r"<[a-zA-Z/][^>]*>"),
    # 行內腳註引用（第十二家族 2026-07-27）：`[^台灣醬油]` 是 markdown 錨點
    # 不是正文——標籤中英文都合法，但必須與定義行一致，譯文保留原標籤才對。
    # 既有規則只剝了腳註「定義行」，行內引用漏網。
    re.compile(r"\[\^[^\]]+\]"),
    re.compile(r"\[\[[^\]]*\]\]"),                                    # [[wikilink]]
    re.compile(r"\[[^\[\]]*(?:\[[^\]]*\][^\[\]]*)*\]\([^)]*\)"),      # [text](url)（容一層巢狀）
    re.compile(r"https?://\S+"),                                      # 裸 URL
    re.compile(r"^\[\^[^\]]+\]:.*$", re.M),                           # [^n]: 腳註定義
]


def strip_legit_zones(text: str, drop_frontmatter: bool = False) -> str:
    """把所有「中文出現在這裡是合法的」區域剝掉，回傳只剩正文的字串。

    2026-07-26 抽出成公開 API。此前每個需要判斷「這段中文算不算洩漏」的工具
    各自維護一份剝除邏輯：cjk-leak-check 兩個分支、verify-translation 的
    description 檢查（同日早上我自己複製的第三份）、cross-lang-audit 的中文
    佔比統計（只剝腳註，其餘全漏）。一天內十個假陽性家族全部源於這種分歧，
    修好一處另一處照樣誤判——所以判準只能有一份，其他工具 import 這個函式。
    """
    body = text
    if drop_frontmatter and body.startswith("---"):
        end_fm = body.find("---", 3)
        if end_fm != -1:
            body = body[end_fm + 3:]
    for rx in LINK_LIKE_RES:
        body = rx.sub("", body)
    for rx in LEGIT_ZH_SPANS:
        body = rx.sub("", body)
    return body


def detect_lang(path: Path) -> str:
    parts = path.parts
    if "knowledge" in parts:
        idx = parts.index("knowledge")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return "unknown"


def scan_file(path: Path, lang: str = None):
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"READ_ERROR: {e}"]
    lang = lang or detect_lang(path)
    hits = []

    if lang in NON_CJK_SCRIPT_LANGS:
        # Strip legitimate zh-bearing zones before scanning:
        #   frontmatter block (translatedFrom etc always references the zh filename)
        #   markdown links [text](url) — internal wikilinks use zh slugs, external
        #     citations legitimately keep the source's actual (Chinese) title
        #   footnote definitions `[^n]: ...` — same citation-title reasoning
        # 2026-07-27 收斂：本分支原本各自內聯一套剝除 regex，於是 strip_legit_zones
        # 加的新豁免（HTML 標籤＝第十一家族）在這裡不生效——抽了共用 API 卻沒改
        # 呼叫端，跟今天修的其他分歧同型。改為單一來源。
        body = strip_legit_zones(text, drop_frontmatter=True)
        for m in CJK_RUN_RE.finditer(body):
            start, end = m.span()
            ctx = body[max(0, start - 20):end + 20].replace("\n", " ")
            hits.append(f"CJK run {m.group(0)!r} (e.g. …{ctx}…)")
        return hits

    # ja/ko marker 掃描前的合法區剝除（2026-07-24）：
    #   「…」『…』引述 span — 引用原文 zh 是編輯選擇（陳建仁原話等），非洩漏
    #   《…》〈…〉作品名 — 專輯／書／單曲／詩名保留原文合法
    #   markdown 連結（容忍一層巢狀中括號）— 引用的 zh 標題合法
    scan = strip_legit_zones(text)   # 同一把尺（2026-07-27 收斂）
    scan = re.sub(r"https?://\S+", "", scan)   # 裸 URL 同豁免（第八家族）
    for marker in ZH_ONLY_MARKERS:
        c = scan.count(marker)
        if c:
            # show one example context for the first occurrence
            idx = scan.find(marker)
            ctx = scan[max(0, idx - 20):idx + 20].replace("\n", " ")
            hits.append(f"{marker!r} x{c} (e.g. …{ctx}…)")
    return hits


def files_from_git_range(rng):
    out = subprocess.run(
        ["git", "diff", "--name-only", rng],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout
    return [REPO / p for p in out.splitlines() if p.startswith("knowledge/") and p.endswith(".md")
            and detect_lang(Path(p)) in (NON_CJK_SCRIPT_LANGS | {"ja", "ko"})]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--glob")
    ap.add_argument("--since-git")
    args = ap.parse_args()

    if args.since_git:
        paths = files_from_git_range(args.since_git)
    elif args.glob:
        paths = list(REPO.glob(args.glob))
    elif args.files:
        paths = [(REPO / f) if not Path(f).is_absolute() else Path(f) for f in args.files]
    else:
        print("need files, --glob, or --since-git", file=sys.stderr)
        sys.exit(1)

    flagged = 0
    for p in paths:
        if not p.exists():
            continue
        hits = scan_file(p)
        if hits:
            flagged += 1
            print(f"\n❌ {p.relative_to(REPO)}")
            for h in hits:
                print(f"   - {h}")

    print(f"\n{flagged}/{len(paths)} files flagged for zh leakage")
    sys.exit(1 if flagged else 0)


if __name__ == "__main__":
    main()
