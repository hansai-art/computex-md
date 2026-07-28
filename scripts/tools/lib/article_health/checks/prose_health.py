"""prose_health — consolidated prose quality checks.

Migrated from `scripts/tools/quality-scan.sh` (16 dims) +
`scripts/tools/check-manifesto-11.sh` (3 tiers) into a single SSOT plugin.

Canonical:
  - quality-scan: docs/editorial/EDITORIAL.md §quality-scan 偵測指標
  - manifesto-11: docs/semiont/MANIFESTO.md §11 書寫節制

Ports the most actionable dimensions:

quality-scan dims:
  1. bullet density           7. repeated bullet blocks    13. (THIN — deferred)
  2. year count               8. plastic phrases (5 variants + extras)
  3. URL count               8b. em-dash overuse
  4. hollow words             8c. 全形分號「；」density (2026-07-19 哲宇, scored)
  5. (prose lines — deferred) 8d. run-on 長句 / 辭藻湯 (2026-07-19, WARN-only)
  6. lastHumanReview          8e. 英文式短句開場 (2026-07-19, WARN-only)
                              9. textbook opening
                             10. formulaic ending
                             11. template H2

2026-07-19 哲宇 directive (高速公路.md live review) 新增三 dim + Tier1 一變體：
  - §8c 全形分號：繁中散文水印，翻譯腔。scored（只在 rewrite-stage-3 咬）。
  - §8d run-on 長句：≥62 字 + ≥8 停頓 = 沒呼吸的辭藻湯。WARN-only soft-launch。
  - §8e 英文式短句開場：≤8 字平述句（。結尾、無數字）+ 接長句 = topic-sentence 腔。
    排除設問（？）與具體場景句。WARN-only soft-launch。corpus 校準見
    reports/prose-instrument-upgrade-2026-07-19.md。
  - Tier1 補「強加對比收束句」：根本是兩件事 / 兩本帳 / 不同的語言（散文對位變體）。
                             12. (LIST-DUMP — deferred)
                             14. (QUALITY-DECAY — deferred)
                             15. (CHINA-TERM — deferred to terminology plugin)
                             16. citation desert

manifesto-11 tiers:
  Tier 1: 11 「不是X是Y」 對位句型 variants + em-dash density
  Tier 2: 30+ AI 抽象 metaphor 詞 + 「重」當抽象份量隱喻 (warn ≥ 2 total)
  Tier 3: 17 AI ritual 語 (warn ≥ 1 occurrence)

§盼望而不粉飾 §自稱 (2026-06-15 哲宇 directive — MANIFESTO §跟台灣的關係 §自稱):
  - 島嶼自稱密度: 「這座島 / 這個島嶼」當台灣的迴避稱呼 (balance not ban，ratio-based:
    島佔「島+台灣」國名指稱 > 1/4 且 ≥ 3，或完全不稱台灣才 WARN，不罰文學用法)。WARN 級。

  (PUA 體 / 媒體焦慮體 偵測器於 2026-06-15 evaluation 後移除：四 subagent + 全 corpus
   814 篇驗證顯示 92-100% 假陽性 — 抓到第三方/引用/腳註新聞標題/文章正在批判的詞/正向用法。
   PUA 與媒體焦慮是「對誰施壓 / 是否販賣恐懼」的語意判斷，不是句法特徵，regex 結構上做不到。
   改由 EDITORIAL §六 對照表 + §五 結尾判準句的人工判斷接管。)

Total score budget: ≤ 3 = pass (per QUALITY-CHECKLIST §四 + REWRITE-PIPELINE).
A "score" violation is yielded with the running total — the runner can
gate on this via profile.fail_on = "score-budget".

Budget is configurable per-profile via `options.score_budget` (int, default
3) — read by article-health.py's score-budget gate (scripts/tools/
article-health.py::_resolve_score_budget). 2026-07-16: added so profiles
whose文體 structurally trips other dims (e.g. `memory-diary`: checklist/
handoff lists trip LIST-DUMP/THIN, no footnotes required) can raise the
pass threshold without changing the default zh-TW knowledge/ budget of 3.

AI 痕跡 Tier 4 (speak-human-tw 轉譯, 2026-07-16 soft-launch):
  (a) 立場真空 (stance-vacuum)      (d) 時代帽子開場 (time-hat opening)
  (b) 價值上升詞密度 (value-inflation) (e) 假推論密度 (「這意味著」)
  (c) 罐頭結尾起手式 (canned-ending)   (f) 首先/其次/最後 三件套
  全部併入 score budget（跟 quality-scan §1-16 一致，不是另開 WARN-only
  bucket像 §11 Tier 1-3 / §自稱）。權重是初次校準值，非最終定案 — 見各
  常數旁註解。

Deferred to Phase 4b (need more structural parsing):
  - LIST-DUMP: bullet ratio per file half
  - THIN: prose lines per H2 section
  - QUALITY-DECAY: prose ratio front vs back
  - CHINA-TERM: requires data/terminology TSV files (separate plugin)
"""

from __future__ import annotations
import re
from typing import Any, Iterator

from ..types import FileTarget, Severity, Violation


CHECK_NAME = "prose-health"
DIMENSION = "prose-quality"
DEFAULT_SEVERITY = Severity.WARN
EDITORIAL_REF = "EDITORIAL.md §quality-scan + MANIFESTO.md §11"
APPLIES_TO = ["zh-TW"]


# ── Plastic phrases (quality-scan §8) ────────────────────────────────────────
_RE_PLASTIC = re.compile(
    r"不僅.{0,8}更是|不只.{0,8}也是|不是.{0,8}而是|"
    r"展現了.{0,8}的精神|展現.{0,8}的決心|體現了.{0,8}的精神|"
    r"扮演著.{0,10}角色|發揮著.{0,10}作用|見證了.{0,10}的歷程|"
    r"彰顯了|承載著.{0,10}的|不僅僅是.{0,10}更是|"
    r"既是.{0,8}也是.{0,8}更是|成為.{0,8}的重要.{0,6}|"
    r"為.{0,10}注入.{0,8}活力|為.{0,10}奠定.{0,8}基礎|"
    r"在.{0,10}上扮演.{0,8}角色|為.{0,10}提供了.{0,8}動力|"
    r"開啟了.{0,8}的新篇章|翻開.{0,8}的新頁|書寫.{0,8}的篇章|"
    r"譜寫.{0,8}的華章|綻放.{0,8}的光芒|閃耀.{0,8}的光輝"
)

# ── Hollow words (quality-scan §4) ───────────────────────────────────────────
_RE_HOLLOW = re.compile(
    r"重要的|顯著的|豐富的|完整的|多元的|"
    r"積極|蓬勃發展|逐步|逐漸|不斷|持續|"
    r"日益|進一步|全面|深入|大力|有效|顯著|穩步"
)

# ── Em-dash (manifesto-11 [9-10] / quality-scan §8b) ─────────────────────────
_RE_EMDASH = re.compile(r"——")

# ── 中文字元計數（開場短句 / 長句判定用）─────────────────────────────────────
_CJK_CHAR = re.compile(r"[一-鿿]")

# ── 全形分號「；」(quality-scan §8c，2026-07-19 哲宇 directive) ────────────────
# 繁中自然散文極少用全形分號。它是翻譯腔 / 學術腔的水印：作者把英文一個帶 ';' 的長句
# 直譯過來，或把「該用句號斷成兩句」「該用頓號列舉」的並列子句硬用；接起來，讀起來像
# 論文或法律條文而不像人話。自然中文做法：句號（。）斷句、頓號（、）列舉。合法殘餘
# （引用官方 / 法律原文、腳註分隔多來源）用「排除腳註行 + ≤3 免計」兜住，不追殺文學例外。
_RE_SEMICOLON = re.compile(r"；")

# ── 英文式超短句開場（歐化語法，2026-07-19 哲宇 directive）────────────────────
# 哲宇 anti-example：「協議並沒有收尾。自救會指控補償被打了六、七折…」——段落以一句
# 超短陳述（≤ 10 字）開頭，緊接一句長得多的句子。這是英文 topic-sentence / punchy
# lead 的腔調（先甩一句短的定調，再展開），中文自然行文會直接流進主題，不會孤立一個
# 四五字的短句當引子。判準刻意排除「整段只有一句短句」的電影感過場句（那是另一種手法，
# 不在此 detector 打擊範圍）——只抓「短開場 + 同段接長句」這個 English structure 指紋。
# 門檻經 2026-07-19 全 corpus 853 篇校準：初版 (≤10/≥15/2×) 誤報 58%（哲宇 anti-example
# 只是最極端一種，中文正常段落也常見中短句開頭）。收緊到 ≤8 字開場 + 後接 ≥28 字 + ≥3.5×
# 落差，把打擊面收到「真的甩一句超短定調再長篇展開」的英文 topic-sentence 指紋。
_ENGLISH_OPENER_MAX_CHARS = 8    # 開場句中文字數 ≤ 此值才算「超短」
_ENGLISH_OPENER_NEXT_MIN = 28    # 後接句中文字數 ≥ 此值（確保是「短→長」不是「短→中」）
_ENGLISH_OPENER_RATIO = 3.5      # 後接句 ≥ 開場句的幾倍

# ── 長句 / 華麗辭藻湯（quality-scan §8d，2026-07-19 哲宇 directive）────────────
# 哲宇：「有些段落切得太長，語感不順，看起來像是華麗的辭藻湯」。機械 proxy：單一句子
# （。！？之間）塞太多逗號 / 頓號 / 分號子句又太長 = 沒有呼吸的 run-on，讀起來像堆疊
# 修飾語的湯。soft-launch WARN，門檻抓得保守（同時超過長度 + 停頓數才報）避免誤殺
# 正常敘事長句。
# 門檻經 2026-07-19 corpus 校準：55字/7停頓誤報偏多（37%，多為正常敘事長句）。
# 收到 62字 + 8停頓，聚焦真正沒呼吸的辭藻湯。WARN-only（不計分）故寬鬆代價低，但仍收緊減噪。
_RUNON_MIN_CJK = 62       # 句子中文字數 ≥ 此值
_RUNON_MIN_PAUSES = 8     # 句內停頓（，、；）數 ≥ 此值

# 歐化「(不)是 X 的」判斷句 (余光中〈中文的常態與變態〉)：是/不是 + 評價形容詞 + 的 + 句末標點。
# 自然中文直接讓形容詞當謂語：「這個選址不隨便」優於「這個選址不是隨便的」。2026-06-07 哲宇
# directive 加入 (live review 複雜生活節「這個選址不是隨便的」)。curated 評價形容詞 list +
# 的後接標點 lookahead，避開合法的「是…的」(是我的 / 是紅色的 / 是教書的 / 是昨天來的)。
_EURO_DE_ADJ = (
    "隨便|必然|偶然|明顯|顯而易見|理所當然|合理|正確|錯誤|重要|必要|多餘|困難|容易|"
    "普遍|常見|罕見|獨特|特別|相同|一致|值得|危險|公平|刻意|足夠|充分|有限|徒勞|"
    "空洞|脆弱|致命|關鍵|根本|主觀|客觀|清楚|模糊|完整|完美|理想|樂觀|悲觀"
)
_RE_EURO_DE = re.compile(rf"不?是(?:{_EURO_DE_ADJ})的(?=[。，！？、；：」』）\s])")

# ── Manifesto §11 Tier 1: 不是X是Y 對位句型 變體 ───────────────────────────
# Tightened versions of patterns from check-manifesto-11.sh.
# 2026-05-09 brave-kirch: 加 antithesis-bare 抓最普遍的「不是 X，是 Y」
# (X 跟 Y 都不超過 30 字、結尾是純「是」不要求「而是 / 也是 / 更是」)。
# 哲宇 EDITORIAL v6.0 self-check 揭露 plugin 漏抓 16+ 處對位句型。
_TIER1_PATTERNS = [
    # 既有 11 patterns (require explicit antithesis tail)
    re.compile(r"不是.{0,30}[，,]\s*而是"),  # cross-comma
    re.compile(r"這不是.{0,15}是"),
    re.compile(r"不只是.{0,15}是"),
    re.compile(r"不再是.{0,15}是"),
    re.compile(r"不僅.{0,15}更是"),
    re.compile(r"不只.{0,15}也是"),
    re.compile(r"不是.{0,8}而是"),
    re.compile(r"不僅僅是.{0,10}更是"),
    re.compile(r"既是.{0,8}也是.{0,8}更是"),
    re.compile(r"從.{2,15}到.{2,15}[，,]\s*從.{2,15}到"),
    re.compile(r"與其說.{0,15}不如說"),
    # NEW (2026-05-09): bare antithesis 「不是 X，是 Y」 / 「不是 X 是 Y」
    # X 1-30 字 (no 是 inside to avoid match overlap); Y 1-30 字
    re.compile(r"不是[^是\n]{1,30}[，,]\s*是[^，,。\n]{1,30}"),  # 不是 X，是 Y
    # NEW: 「不只 X，更 Y」「不只是 X，也 Y」「並非 X，而是 Y」 系列
    re.compile(r"不只[^更也\n]{1,30}[，,]\s*更"),
    re.compile(r"不只是[^也還\n]{1,30}[，,]\s*(也|還)"),
    re.compile(r"並非[^而\n]{1,30}[，,]\s*而是"),
    re.compile(r"並不[^而是\n]{1,30}[，,]\s*而是"),
]

# ── §11 Tier 1 補：強加對比的收束句（2026-07-19 哲宇 directive）───────────────
# 對位句型的散文變體：不是「不是 X 是 Y」的句型，而是段末 / 節末拿一個抽象對比當
# 結論——「（大眾直覺與官方統計）量的根本是兩件事」「（兩邊講的）根本是不同的語言」
# 「這條路的兩本帳，從來沒有攤開在同一頁上」。tell 是「根本是 …兩件事 / 兩回事 /
# 不同的 X」「兩本帳」「沒攤開在同一頁」這種把並列的兩者硬拗成「其實是兩種東西」的
# essay 收尾腔。跟「兩件事」裸詞不同（「這篇要做兩件事」「相隔半年的兩件事」是實指，
# 不抓）——只抓「根本是 / 其實是 + 兩件事 / 不同的」與「兩本帳 / 同一頁」高精度變體。
_RE_FORCED_CONTRAST_CLOSER = re.compile(
    r"(?:根本|其實|說到底|講的|量的|要的|問的)(?:是|上是|其實是)?[^，。！？\n]{0,10}"
    r"(?:兩件事|兩回事|兩碼事|不同的(?:語言|東西|世界|邏輯|事|概念))"
    r"|兩本帳"
    r"|(?:從來)?(?:沒有|沒|未曾|不曾)[^，。！？\n]{0,8}(?:攤開|放|擺)[^，。！？\n]{0,6}同一(?:頁|張|條|個)"
)

# ── Manifesto §11 Tier 2: AI 抽象 metaphor 詞 ────────────────────────────────
_TIER2_WORDS = [
    "重量", "縮影", "軌跡", "弧線", "DNA", "基因",
    "土壤", "養分", "血液", "縫隙", "皺褶", "肌理", "織就",
    "指紋", "神經末梢", "肌肉記憶", "基底", "底色",
    "張力", "光譜", "鏡子", "承載著", "形塑", "鬆動",
    "展演", "召喚", "凝視", "直面", "直擊",
    "鋪陳", "醞釀", "沈澱",
]

# ── §11 Tier 2 補：「重」當抽象份量隱喻 (2026-06-04 哲宇 callout) ──────────────
# AI 很愛把「意義/份量/重要性」寫成物理上的「重」(很重 / 最重的一刻 / 沉重 /
# 份量很重)。是 Tier 2 metaphor 的高頻變體，但「重量」靜態詞 catch 不到、又不能
# 用裸 substring「很重」(會誤殺「很重要/很重視/很重大」)。用 regex + 負向預看
# 排除常見複合詞，逐處 WARN + 計入 Tier 2 密度。口語替代：把抽象的「重」改成具體
# 後果或畫面 (「最重的一刻」→「最不敢忘的一刻」/ 直接寫那一刻發生什麼)。
_RE_WEIGHT_METAPHOR = re.compile(
    r"(?:很|最|更|太|格外|分外|這麼|那麼|如此|越來越|愈來愈|沉甸甸地?)重"
    r"(?!要|視|新|複|建|點|申|組|演|置|逢|疊|整|大|心|力|機|金|傷|病|罪|刑|兵|鎮"
    r"|工|劃|唱|奏|圍|彈|操|播|映|審|提|溫|現|生|用|返|犯|劑|物|量|罰|稅|賞|創)"
    r"|[沉沈]重(?!澱)"
    r"|份量|分量"
)

# ── Manifesto §11 Tier 3: AI ritual 語 ───────────────────────────────────────
_TIER3_PHRASES = [
    "在這個意義上", "從某種意義上", "就此而言", "換言之",
    "值得我們深思", "值得我們反思", "拭目以待", "不容忽視",
    "不可或缺", "不可磨滅", "影響深遠", "歷久彌新",
    "並非偶然", "耐人尋味", "不言而喻", "不可言說", "無以名狀",
]

# ── AI 痕跡 Tier 4 (speak-human-tw 轉譯, 2026-07-16 soft-launch) ─────────────
# 校準狀態：soft-launch。權重是初次估計，未經 vc≥3 production case 驗證
# （跟 chronicle-lead / word-count 當初 promotion 前的 staging 階段一樣）。
# 併入 score budget（不像 §11 Tier 1-3 / §自稱是 WARN-only 不計分）——這組
# 抓的是「作者沒有立場 / 灌水式升值語 / 罐頭收尾」，屬於 quality-scan 同一
# 家族的可計分維度，不是純風格建議。

# (a) 立場真空：每 hit +1，上限 +2（避免單篇因為多次「見仁見智」被過度懲罰）。
_RE_STANCE_VACUUM = re.compile(
    r"各有優缺點|見仁見智|因人而異|取決於多方面因素|具體情況具體分析"
)
_STANCE_VACUUM_SCORE_CAP = 2

# (b) 價值上升詞密度：≥3 hits +1、≥6 +2。
# 「轉捩點」「里程碑」刻意不列入——史觀文章的正當高頻詞，列入會誤殺敘事史文。
# 「不可磨滅」跟 §11 Tier 3 ritual 語重疊，此處刻意保留（Tier 3 不計分，
# 這裡才是這個詞第一次進 score budget）。
_RE_VALUE_INFLATION = re.compile(
    r"標誌著|見證了|彰顯了|體現了|突顯了|奠定.{0,10}基礎|不可磨滅"
)

# (c) 罐頭結尾起手式：最後 3 個段落內出現任一 → +2（fixed，非累加）。
# 跟既有 _RE_FORMULAIC_ENDING（quality-scan #10，抓最後 5 行）不同顆粒度
# （這裡是「最後 3 段」，且多收「總而言之」——舊規則沒有）。兩者故意並存、
# 允許同一處文字同時觸發兩個維度：#10 抓行級、Tier4(c) 抓段落級起手式。
_RE_CANNED_ENDING_OPENER = re.compile(
    r"總的來說|綜上所述|總而言之|總結來說"
)

# (d) 時代帽子開場：第一個 prose 段落以此開頭 → +2（fixed）。
_RE_TIME_HAT_OPENING = re.compile(
    r"^(?:在當今|在這個.{0,12}的時代|隨著.{0,15}的(?:快速)?發展)"
)

# (e) 假推論密度：「這意味著」≥2 hits +1。
_FALSE_INFERENCE_PHRASE = "這意味著"
_FALSE_INFERENCE_MIN_HITS = 2

# (f) 首先/其次/最後 三件套：同時出現「首先」+「其次」+（「最後」或「再者」）→ +1。

# ── §盼望而不粉飾 (2026-06-15 哲宇 directive 儀器化) ───────────────────────────
# canonical: MANIFESTO §進化哲學 盼望而不粉飾 + §跟台灣的關係 §自稱 + EDITORIAL §六。
# 三組全 WARN、不計入 score（跟 §11 Tier 1-3 一致）—— surface drift 但不擋既有 stage 閘。

# 島嶼自稱：「這座島 / 這個島 / 這座島嶼 / 這個小島 / 這座島國」當台灣的迴避稱呼。
# 哲宇 2026-06-15：島嶼文學性可以提，但不要過度——大多數時候大方講「台灣 / 這個國家」。
# 所以密度過高 (≥ 3) 或超過直接稱台灣才 WARN，不罰單次文學用法。曹永和「以島嶼為主體」
# 島史脈絡機器分不出 → WARN 級留人判斷。
# 已知限制：寫實際外島（綠島 / 蘭嶼 / 澎湖）的文章，「這座島」指該島非台灣，會誤報 —
# WARN 級可由審稿者忽略，不 block。
_RE_ISLAND_EUPHEMISM = re.compile(r"這(?:座|個)(?:小)?島(?:嶼|國)?")
_RE_TAIWAN_REF = re.compile(r"台灣|臺灣")

# PUA 體 / 媒體焦慮體 regex 偵測器已於 2026-06-15 evaluation 後移除。四 subagent +
# 全 corpus 814 篇驗證：PUA `沒資格` 4/4 假陽性（抓到第三方/引用/虛構角色），媒體焦慮
# 13 hits 僅 ~1 真陽性（抓到腳註裡的新聞標題、文章正在批判的「最後一塊淨土」、正向的
# 「潛規則正在瓦解」、歷史事實「關係正在崩潰」）。根因：PUA = 對誰施壓、媒體焦慮 = 是否
# 販賣恐懼，都是語意判斷不是句法特徵，regex 結構上做不到（架構解非守備修補）。改由
# EDITORIAL §六 對照表 + §五 結尾判準句的人工判斷接管。島嶼自稱因為是可量化的比例
# （島 vs 台灣稱呼），才留得住偵測器。

# ── Textbook opening (quality-scan §9) ───────────────────────────────────────
_RE_TEXTBOOK_OPENING = re.compile(
    r"^(台灣的.{2,20}是|.{2,10}是台灣.{2,20}|"
    r"作為.{2,15}[，,]\s*台灣|"
    r"在.{2,10}(方面|領域)[，,]\s*台灣|"
    r"台灣.{2,6}(擁有|具有|位於|以其))"
)

# ── Formulaic ending (quality-scan §10) ──────────────────────────────────────
# 2026-05-09 added 「故事還在寫」family per 哲宇 callout — soft hand-waving
# non-endings that sound reflective but add nothing. Same anti-pattern family
# as 「將繼續發光發熱」: writer doesn't have a concrete closure so retreats to
# story-as-meta-narrative cliché.
_RE_FORMULAIC_ENDING = re.compile(
    r"總之|綜上所述|展望未來|總結來說|總的來說|未來展望|"
    r"隨著.{2,20}的(發展|推進|深化)|將繼續|值得期待|"
    # 「故事還在寫 / 還沒結束 / 仍在繼續」family
    r"(這個|這段|那個|那段|.{0,4}的)?故事(還在|仍在|尚未|還沒).{0,3}(寫|繼續|結束|完結|落幕)|"
    r"故事(還沒|仍未|尚未)(寫完|結束|完結|落幕)|"
    r"後來.{0,5}(這個|這段)?故事還在|"
    r"還(沒|未)(寫完|結束|落幕)|"
    r"繼續.{0,5}(被)?(寫|書寫)(下去|著|這個|這段)?|"
    r"持續(被)?(書寫|寫)(著|下去)"
)

# ── Template H2 (quality-scan §11) ───────────────────────────────────────────
_RE_TEMPLATE_H2 = re.compile(
    r"^(歷史(背景|沿革|發展)?|發展歷程|歷史脈絡|"
    r"現況(與|及)?|現狀|當前|"
    r"未來(展望|發展|趨勢)|結語|總結|"
    r"挑戰與展望|挑戰與機遇|影響與意義|"
    r"特色(與|及)?|重要性|"
    r"國際(比較|影響|地位))$"
)


def _count_year_mentions(body: str) -> int:
    """4-digit years in 1600-2099 range, excluding `date:` lines."""
    n = 0
    for line in body.splitlines():
        if "date:" in line:
            continue
        n += len(re.findall(r"\b(?:1[6-9]\d{2}|20[0-2]\d)\b", line))
    return n


def _count_urls(body: str) -> int:
    return body.count("http")


# 參考裝置 section 標題：延伸閱讀 / 圖片來源 / 參考資料 / 授權清單 —— 這些是
# attribution / reference apparatus，bullet 是結構必需（每張圖一條、每篇延伸一條），
# 不是 prose 灌水。bullet 灌水檢查只看正文，碰到這些 heading 就截斷。
# 2026-06-04 v2 實驗：5 圖 article 的「## 圖片來源」5 bullet 誤判成「連續bullet5行」。
_REF_APPARATUS_RE = re.compile(
    r"(?m)^#{2,3}\s*(延伸閱讀|圖片來源|圖片授權|媒體授權|參考資料|參考來源|資料來源|來源)"
)


def _body_before_apparatus(body: str) -> str:
    """正文 = 第一個參考裝置 heading 之前（bullet 灌水只查正文）。"""
    m = _REF_APPARATUS_RE.search(body)
    return body[: m.start()] if m else body


def _count_repeated_bullets(body: str) -> int:
    """Max consecutive `- **` bullet block length（排除參考裝置 section）。"""
    max_run = 0
    cur = 0
    for line in _body_before_apparatus(body).splitlines():
        if line.startswith("- **"):
            cur += 1
            if cur > max_run:
                max_run = cur
        else:
            cur = 0
    return max_run


def _count_bullet_lines(body: str) -> tuple[int, int]:
    """Returns (bullet_lines, total_lines). Bullet = `- **` style（排除參考裝置）。"""
    prose = _body_before_apparatus(body)
    total = prose.count("\n") + 1
    bullets = sum(1 for line in prose.splitlines() if line.startswith("- **"))
    return bullets, total


def _detect_textbook_opening(body: str) -> bool:
    """First 2 non-empty non-heading lines after frontmatter."""
    seen_lines = 0
    for line in body.splitlines():
        if not line.strip():
            continue
        if line.startswith("#"):
            continue
        if _RE_TEXTBOOK_OPENING.search(line):
            return True
        seen_lines += 1
        if seen_lines >= 2:
            break
    return False


def _detect_formulaic_ending(body: str) -> bool:
    """Last 5 non-bullet non-heading non-link lines."""
    eligible = [
        line for line in body.splitlines()
        if line.strip()
        and not line.startswith("#")
        and not line.startswith("-")
        and "http" not in line
    ]
    tail = eligible[-5:] if eligible else []
    text = "\n".join(tail)
    return bool(_RE_FORMULAIC_ENDING.search(text))


def _split_paragraphs(body: str) -> list[str]:
    """Split body into paragraph text blocks (blank-line separated).

    Used by Tier 4 (c) 罐頭結尾起手式 (last-3-paragraph scope) and
    (d) 時代帽子開場 (first-prose-paragraph scope). Simple blank-line
    splitter — matches the loose 段落 notion used elsewhere in this module
    (e.g. _count_thin_blocks operates on H2 blocks, this operates on the
    finer blank-line granularity).
    """
    return [p for p in re.split(r"\n\s*\n", body) if p.strip()]


def _detect_canned_ending_opener(body: str) -> bool:
    """Tier 4 (c): 最後 3 個段落內是否出現罐頭結尾起手式。"""
    paragraphs = _split_paragraphs(body)
    tail = paragraphs[-3:] if paragraphs else []
    text = "\n\n".join(tail)
    return bool(_RE_CANNED_ENDING_OPENER.search(text))


def _detect_time_hat_opening(body: str) -> bool:
    """Tier 4 (d): 第一個 prose 段落（跳過 heading / blockquote）是否以
    時代帽子開場 pattern 開頭。"""
    for p in _split_paragraphs(body):
        stripped = p.strip()
        if not stripped:
            continue
        if stripped.startswith(">") or stripped.startswith("#"):
            continue
        return bool(_RE_TIME_HAT_OPENING.match(stripped))
    return False


def _paragraphs_with_offset(body: str) -> list[tuple[int, str]]:
    """Blank-line-separated paragraph blocks with their start char offset in body.

    Offset aligns with body (loader pads leading blank lines for source-line
    parity), so _line_at_offset(body, offset) gives the source .md line number.
    """
    out: list[tuple[int, str]] = []
    offset = 0
    cur_start: int | None = None
    cur_lines: list[str] = []
    for line in body.split("\n"):
        if line.strip() == "":
            if cur_lines:
                out.append((cur_start or 0, "\n".join(cur_lines)))
                cur_lines = []
                cur_start = None
        else:
            if cur_start is None:
                cur_start = offset
            cur_lines.append(line)
        offset += len(line) + 1  # +1 for the split '\n'
    if cur_lines:
        out.append((cur_start or 0, "\n".join(cur_lines)))
    return out


# 段落開頭若是這些字元 = 非散文 block（heading / list / quote / callout / caption /
# HTML / code / image / link），英文短句開場 detector 一律跳過。
_NON_PROSE_LEAD = set("># -*|`![_<+=~")


def _detect_english_openers(body: str) -> list[tuple[int, str, int, int]]:
    """英文式超短句開場：段落以 ≤N 字短陳述開頭 + 同段緊接長句。

    回傳 [(offset, 開場句, 開場字數, 後接字數)]。刻意排除「整段只有一句短句」的
    過場句（rest 為空 → skip），只抓「短開場 + 接長句」的 English topic-sentence 腔。
    """
    hits: list[tuple[int, str, int, int]] = []
    for start, para in _paragraphs_with_offset(body):
        s = para.strip()
        if not s or s[0] in _NON_PROSE_LEAD or s.startswith("```"):
            continue
        # 跳過數字 / 英文字母 / 粗體標籤開頭（清單、年份條列、callout 標題）
        if re.match(r"^(?:\d|[A-Za-z]|\*\*)", s):
            continue
        # 只抓「。」結尾的平述定調句：英文 topic-sentence 是平述句。開場短問句（？）是
        # 中文設問（「為什麼選這塊地？」「軍人多到什麼程度？」）是自然修辭，不是這個病；
        # 驚嘆句（！）也是另一種語氣。限定 。 結尾把打擊面收到哲宇 anti-example 的句型
        # （2026-07-19 corpus 抽樣揭：？ 開場全是設問 false positive）。
        m = re.match(r"^([^。！？\n]{1,40}。)", s)
        if not m:
            continue
        first = m.group(1)
        opener_len = len(_CJK_CHAR.findall(first))
        if opener_len == 0 or opener_len > _ENGLISH_OPENER_MAX_CHARS:
            continue
        # 具體場景定調句（含數字：年份 / 日期 / 數量）是自然中文敘事節奏（「1978 年通車。」
        # 長段），不是英文抽象 topic-sentence 腔。哲宇 anti-example「協議並沒有收尾」是抽象
        # 狀態陳述、無數字——用「開場句含數字則豁免」把打擊面收到抽象定調句（2026-07-19 校準）。
        if re.search(r"[0-9]", first):
            continue
        rest = s[m.end():].strip()
        if not rest:
            continue  # 單句過場段 — 另一種手法，不打擊
        m2 = re.match(r"^([^。！？\n]{1,200}[。！？]?)", rest)
        next_seg = m2.group(1) if m2 else rest
        next_len = len(_CJK_CHAR.findall(next_seg))
        if next_len >= _ENGLISH_OPENER_NEXT_MIN and next_len >= opener_len * _ENGLISH_OPENER_RATIO:
            lead = len(para) - len(para.lstrip())
            hits.append((start + lead, first, opener_len, next_len))
    return hits


def _detect_runon_sentences(text: str) -> list[tuple[int, str, int, int]]:
    """長句 / 華麗辭藻湯：單句同時超過長度門檻 + 停頓數門檻 = 沒呼吸的 run-on。

    回傳 [(offset, 句子, 中文字數, 停頓數)]。保守雙門檻避免誤殺正常敘事長句。
    """
    hits: list[tuple[int, str, int, int]] = []
    for m in re.finditer(r"[^。！？\n]{1,400}[。！？]", text):
        # 排除腳註定義行（[^N]: …）與 blockquote 行（> …）：引用裝置 / 直接引語不是
        # 作者散文，長是來源本身的事，不該當 run-on 罰（2026-07-19 dogfood 揭 4 處腳註 FP）。
        ls = text.rfind("\n", 0, m.start()) + 1
        line_prefix = text[ls:ls + 4].lstrip()
        if line_prefix.startswith("[^") or line_prefix.startswith(">"):
            continue
        seg = m.group(0)
        cjk = len(_CJK_CHAR.findall(seg))
        pauses = seg.count("，") + seg.count("、") + seg.count("；")
        if cjk >= _RUNON_MIN_CJK and pauses >= _RUNON_MIN_PAUSES:
            hits.append((m.start(), seg, cjk, pauses))
    return hits


def _count_template_h2(body: str) -> int:
    n = 0
    for line in body.splitlines():
        if line.startswith("## "):
            heading = line[3:].strip()
            if _RE_TEMPLATE_H2.match(heading):
                n += 1
    return n


def _count_footnote_defs(body: str) -> int:
    return sum(
        1
        for line in body.splitlines()
        if re.match(r"^\[\^[0-9a-zA-Z_-]+\]:", line)
    )


def _is_hub_file(target: FileTarget) -> bool:
    """Hub files (`_X Hub.md`) — relax structural penalties per quality-scan.sh."""
    name = target.path.name
    return name.startswith("_") and "Hub" in name


def _bullet_ratios_split(body: str) -> tuple[int, int, int, int]:
    """Front/back half bullet ratios. Returns (front_bullet, back_bullet,
    front_total, back_total) — total = non-empty lines, bullet =
    `- ` / `* ` / `N.`."""
    lines = body.splitlines()
    n = len(lines)
    if n == 0:
        return 0, 0, 0, 0
    split = (n * 6) // 10  # quality-scan uses 60/40 split
    front_bullet = back_bullet = front_total = back_total = 0
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        is_bullet = bool(re.match(r"^(?:[-*]\s|\d+\.\s)", line))
        if i < split:
            front_total += 1
            if is_bullet:
                front_bullet += 1
        else:
            back_total += 1
            if is_bullet:
                back_bullet += 1
    return front_bullet, back_bullet, front_total, back_total


def _count_thin_blocks(body: str) -> int:
    """H2 blocks with < 3 prose lines. Mirrors quality-scan.sh dim 13.

    Structural sections (參考資料 / 延伸閱讀 / 圖片來源 / sources) are
    exempted — they're by-design lists of footnotes / further-reading
    links / image attributions, not prose paragraphs. Counting them as
    "thin" generates false positives on every well-formed article.
    """
    structural_h2 = {
        "## 參考資料", "## 延伸閱讀", "## 圖片來源",
        "## 來源", "## References", "## Further Reading", "## Image Sources",
    }
    thin = 0
    in_block = False
    is_structural = False
    prose = 0
    for line in body.splitlines():
        if line.startswith("## "):
            if in_block and not is_structural and prose < 3:
                thin += 1
            in_block = True
            stripped = line.rstrip()
            is_structural = stripped in structural_h2
            prose = 0
        elif in_block:
            if line.strip() and not re.match(r"^(?:[#\-*|>]|\d+\.)", line):
                prose += 1
    if in_block and not is_structural and prose < 3:
        thin += 1
    return thin


def _prose_ratios_split(body: str) -> tuple[int, int, int, int]:
    """Front/back half prose ratios for QUALITY-DECAY detection."""
    lines = body.splitlines()
    n = len(lines)
    split = (n * 6) // 10
    fp = bp = fa = ba = 0
    for i, line in enumerate(lines):
        if i < split:
            fa += 1
            if line.strip() and not re.match(r"^(?:[#\-*|>]|\d+\.)", line):
                fp += 1
        else:
            ba += 1
            if line.strip() and not re.match(r"^(?:[#\-*|>]|\d+\.)", line):
                bp += 1
    return fp, bp, fa, ba


def _word_count(body: str) -> int:
    """Rough whitespace-tokenized count after frontmatter (CJK 1 char = 1 word).

    Matches `wc -w` semantics of the shell script for parity.
    """
    return len(body.split())


def _line_at_offset(body: str, offset: int) -> int:
    """Return 1-indexed line number of given char offset in body.

    body is padded with leading blank lines to match original-file line
    numbers (per FileTarget.body_pad_lines), so the returned line equals
    the line number in the source .md file.
    """
    if offset < 0 or offset > len(body):
        return 1
    return body.count("\n", 0, offset) + 1


def _context_around(body: str, start: int, end: int, before: int = 20, after: int = 20) -> str:
    """Return the matched span with surrounding context, marking the match.

    Layout: `…<before>《MATCH》<after>…`
    Newlines collapsed to ⏎ so single-line snippets stay readable.
    Caller can show this in violation snippet for grep-style locate.
    """
    body_len = len(body)
    ctx_start = max(0, start - before)
    ctx_end = min(body_len, end + after)
    pre = body[ctx_start:start].replace("\n", "⏎")
    mid = body[start:end].replace("\n", "⏎")
    post = body[ctx_end:end].replace("\n", "⏎") if False else body[end:ctx_end].replace("\n", "⏎")
    leading = "…" if ctx_start > 0 else ""
    trailing = "…" if ctx_end < body_len else ""
    return f"{leading}{pre}《{mid}》{post}{trailing}"


def _uneditable_punct_predicate(text: str):
    """回傳 is_uneditable(start) — 該標點位置是否落在 campaign 鐵律禁改的合法區。

    破折號/分號 gate 只該數「可編輯正文裡的修辭性用法」，不該數這些合法且鐵律禁改的區：
      - 參考裝置段（## 參考資料 / 延伸閱讀 / 圖片來源…）之後全部
      - blockquote 行（> …）：引用材料，—— / ； 是來源的不是作者的
      - 腳註定義行（[^n]: …）：引用裝置
      - 圖片行（![…]）與斜體圖說行（_…_）：來源標註
      - 書名號內《…——…》：破折號是書名的一部分
    2026-07-19 campaign 揭：不排除這些區，一篇合法引用/書名多的文章（辦桌/花蓮縣/手路菜）
    無論正文清得多乾淨都過不了 gate（禁改區本身就超標）。排除後量的才是真正的寫作 tic。
    text_for_patterns 已先移除 code fence / URL，本 predicate 再補上述行級 + 書名 span。
    """
    m = _REF_APPARATUS_RE.search(text)
    ref_cut = m.start() if m else len(text)
    title_spans = [(mm.start(), mm.end()) for mm in re.finditer(r"《[^》]*》", text)]

    def is_uneditable(start: int) -> bool:
        if start >= ref_cut:
            return True
        ls = text.rfind("\n", 0, start) + 1
        le = text.find("\n", start)
        line = text[ls:(le if le != -1 else len(text))]
        st = line.lstrip()
        if st.startswith((">", "[^", "![")):
            return True
        if st.startswith("_") and st.rstrip().endswith("_"):
            return True
        for a, b in title_spans:
            if a <= start < b:
                return True
        return False

    return is_uneditable


def check(target: FileTarget, config: dict[str, Any]) -> Iterator[Violation]:
    """Yield prose-health violations + a final score-summary violation.

    Skips if file is too short (lines < 20).

    Frontmatter requirement: knowledge/ articles must have frontmatter
    (matches legacy quality-scan.sh::scan_file semantics). For docs/
    canonical SSOT files (EDITORIAL.md / MANIFESTO.md / pipeline files /
    cognitive layer), prose-health still applies — these don't have
    frontmatter but should be held to same writing discipline.

    2026-05-09 brave-kirch: 原本 `if not target.frontmatter: return` 讓
    EDITORIAL.md 自己漏抓 16+ 處對位句型。docs/ canonical 文件 frontmatter
    是 optional，不應該 skip prose-health.
    """
    body = target.body
    line_count = body.count("\n") + 1
    if line_count < 20:
        return
    # Frontmatter required only for knowledge/ articles (legacy semantics).
    path_str = str(target.path)
    is_knowledge_article = "/knowledge/" in path_str or path_str.startswith("knowledge/")
    if is_knowledge_article and not target.frontmatter:
        # Hub / private docs in knowledge/ without frontmatter — skip
        return

    score = 0
    reasons: list[str] = []
    # Per-profile pass threshold — default 3 (quality-scan canonical),
    # overridable via profile options_overrides.prose-health.score_budget
    # (e.g. `memory-diary` profile raises this to 8). Only informational
    # here (message text); the actual gate lives in article-health.py's
    # `_resolve_score_budget` (score-budget fail_on).
    score_budget = 3
    if config:
        raw_budget = config.get("score_budget")
        if raw_budget is not None:
            try:
                score_budget = int(raw_budget)
            except (TypeError, ValueError):
                score_budget = 3

    # 破折號 / 分號「觸檔即硬」門檻（2026-07-19 哲宇選項3）：只在有設此 config 的 profile
    # 才把超量破折號 / 分號升成 HARD。pre-commit profile 設了 → 你 commit 的檔（新寫 or
    # 編輯）超量就擋，逼觸檔即清（touch-it-fix-it）。ci-deploy 全站掃描不設 → 保持 WARN，
    # 144 篇 legacy 不會 brick push/deploy。門檻設在惡性等級（破折號>15 / 分號>12），
    # 抓 高速公路(17/20)、蘇打綠(72 dash)、認知作戰(29 semi) 這種，不動輕症。
    def _hard_over(key: str):
        if not config:
            return None
        v = config.get(key)
        if v is None:
            return None
        try:
            return int(v)
        except (TypeError, ValueError):
            return None
    emdash_hard_over = _hard_over("emdash_hard_over")
    semicolon_hard_over = _hard_over("semicolon_hard_over")

    # Use body without protected regions for pattern detection so code
    # blocks / link URLs don't trigger false positives.
    text_for_patterns = target.body_without_protected()

    # ── 1. Bullet density ──
    bullets, total = _count_bullet_lines(body)
    if total > 0:
        ratio = bullets * 100 // total
        if ratio > 30:
            score += 3
            reasons.append(f"bullet密度{ratio}%")
        elif ratio > 20:
            score += 1
            reasons.append(f"bullet密度{ratio}%")

    # ── 2. Year count ──
    years = _count_year_mentions(body)
    if years < 2:
        score += 3
        reasons.append(f"年份僅{years}個")
    elif years < 5:
        score += 1
        reasons.append(f"年份{years}個")

    # ── 3. URL count ──
    urls = _count_urls(body)
    if urls == 0:
        score += 3
        reasons.append("無URL來源")
    elif urls < 3:
        score += 1
        reasons.append(f"僅{urls}個URL")

    # ── 4. Hollow words ──
    hollow_n = len(_RE_HOLLOW.findall(text_for_patterns))
    if hollow_n > 15:
        score += 3
        reasons.append(f"空洞詞{hollow_n}個")
    elif hollow_n > 8:
        score += 2
        reasons.append(f"空洞詞{hollow_n}個")
    elif hollow_n > 4:
        score += 1
        reasons.append(f"空洞詞{hollow_n}個")

    # ── 6. lastHumanReview ──
    if target.frontmatter.get("lastHumanReview") is False:
        score += 1
        reasons.append("未人工審核")

    # ── 7. Repeated bullet blocks ──
    max_run = _count_repeated_bullets(body)
    if max_run >= 6:
        score += 2
        reasons.append(f"連續bullet{max_run}行")
    elif max_run >= 4:
        score += 1
        reasons.append(f"連續bullet{max_run}行")

    # ── 8. Plastic phrases ──
    # Emit per-match with line + 前後文 context (2026-05-10 sad-shockley
    # feedback). Aggregate count drives score; individual locations help
    # writer find them fast.
    plastic_matches = list(_RE_PLASTIC.finditer(text_for_patterns))
    plastic_n = len(plastic_matches)
    if plastic_n > 8:
        score += 4
        reasons.append(f"塑膠句{plastic_n}個")
    elif plastic_n > 4:
        score += 3
        reasons.append(f"塑膠句{plastic_n}個")
    elif plastic_n > 2:
        score += 2
        reasons.append(f"塑膠句{plastic_n}個")
    elif plastic_n >= 1:
        score += 1
        reasons.append(f"塑膠句{plastic_n}個")
    # Itemize each plastic phrase occurrence (capped at 10 to avoid noise)
    for m in plastic_matches[:10]:
        line_no = _line_at_offset(text_for_patterns, m.start())
        ctx = _context_around(text_for_patterns, m.start(), m.end())
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.WARN,
            message=f"塑膠句 (§quality-scan #8)：{ctx}",
            line=line_no,
            snippet=m.group(0)[:80],
            editorial_ref="EDITORIAL.md §quality-scan #8 塑膠句禁令",
            fix_suggestion="改成正面具體斷言 (替換「不僅...更是」「展現了...精神」「值得紀念」)",
        )

    # ── 8b. Em-dash overuse ──
    # 只數可編輯正文的修辭性破折號——排除 blockquote/腳註/圖說/書名/參考裝置（禁改合法區，
    # 2026-07-19 campaign 揭：不排除的話引用/書名多的文章正文清乾淨也過不了 gate）。
    _is_uneditable = _uneditable_punct_predicate(text_for_patterns)
    dash_matches = [m for m in _RE_EMDASH.finditer(text_for_patterns) if not _is_uneditable(m.start())]
    dash_n = len(dash_matches)
    if dash_n > 15:
        score += 3
        reasons.append(f"破折號{dash_n}個")
    elif dash_n > 8:
        score += 2
        reasons.append(f"破折號{dash_n}個")
    elif dash_n > 4:
        score += 1
        reasons.append(f"破折號{dash_n}個")
    # 觸檔即硬 gate（哲宇選項3）：pre-commit profile 設 emdash_hard_over 時，超量升 HARD。
    if emdash_hard_over is not None and dash_n > emdash_hard_over:
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.HARD,
            message=(
                f"破折號連用超硬門檻：{dash_n} 處 > {emdash_hard_over}"
                f"（§quality-scan #8b HARD gate，2026-07-19 哲宇選項3 觸檔即硬）"
            ),
            editorial_ref="EDITORIAL.md §破折號 + MANIFESTO §11.2",
            fix_suggestion=(
                f"這是 pre-commit HARD gate：你改到的檔破折號必須降到 ≤ {emdash_hard_over}。"
                "改用「，即」「（）」「：」/ 分句 / 短句。（全站 legacy 仍 WARN 不擋，只有你觸碰的檔要清。）"
            ),
        )
    # Only itemize if over budget (> 8) — don't spam < 5 instances
    if dash_n > 8:
        for m in dash_matches[:10]:
            line_no = _line_at_offset(text_for_patterns, m.start())
            ctx = _context_around(text_for_patterns, m.start(), m.end(), before=15, after=15)
            yield Violation(
                check=CHECK_NAME,
                severity=Severity.WARN,
                message=f"破折號連用 (§quality-scan #8b 第 {dash_matches.index(m)+1}/{dash_n} 處)：{ctx}",
                line=line_no,
                snippet="——",
                editorial_ref="EDITORIAL.md §quality-scan #8b + MANIFESTO §11.2",
                fix_suggestion="改用「，即」「（）」「：」/ 分句 / 短句 / bullet",
            )

    # ── 8c. Semicolon density (；) — 2026-07-19 哲宇 directive ──
    # 排除腳註定義行（引用裝置，分號分隔多來源可接受）。text_for_patterns 已排除
    # code fence（tw-timeline/tw-bars 的 ；不算）+ URL。
    # 同 §8b：只數可編輯正文的分號（排除 blockquote/腳註/圖說/參考裝置等禁改合法區）。
    semi_matches = [m for m in _RE_SEMICOLON.finditer(text_for_patterns) if not _is_uneditable(m.start())]
    semi_n = len(semi_matches)
    if semi_n > 8:
        score += 2
        reasons.append(f"分號{semi_n}個")
    elif semi_n > 3:
        score += 1
        reasons.append(f"分號{semi_n}個")
    # 觸檔即硬 gate（哲宇選項3）：pre-commit profile 設 semicolon_hard_over 時，超量升 HARD。
    if semicolon_hard_over is not None and semi_n > semicolon_hard_over:
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.HARD,
            message=(
                f"全形分號超硬門檻：{semi_n} 處 > {semicolon_hard_over}"
                f"（§quality-scan #8c HARD gate，2026-07-19 哲宇選項3 觸檔即硬）"
            ),
            editorial_ref="EDITORIAL.md §歐化語法 §分號",
            fix_suggestion=(
                f"這是 pre-commit HARD gate：你改到的檔全形分號必須降到 ≤ {semicolon_hard_over}。"
                "拆句號句 / 並列改頓號。（全站 legacy 仍 WARN 不擋，只有你觸碰的檔要清。）"
            ),
        )
    if semi_n > 3:
        for m in semi_matches[:10]:
            line_no = _line_at_offset(text_for_patterns, m.start())
            ctx = _context_around(text_for_patterns, m.start(), m.end(), before=18, after=18)
            yield Violation(
                check=CHECK_NAME,
                severity=Severity.WARN,
                message=f"全形分號連用 (§quality-scan #8c 第 {semi_matches.index(m)+1}/{semi_n} 處)：{ctx}",
                line=line_no,
                snippet="；",
                editorial_ref="EDITORIAL.md §歐化語法 §分號 + quality-scan #8c",
                fix_suggestion=(
                    "繁中散文少用全形分號（翻譯腔水印）。多數情況：前後子句拆成兩個句號句"
                    "（；→。），或並列項改頓號（、）。分號讀起來像論文/法律條文不像人話。"
                ),
            )

    # ── 8d. Run-on sentence / 華麗辭藻湯 (soft-launch WARN，不計分) — 哲宇 directive ──
    for off, seg, cjk, pauses in _detect_runon_sentences(text_for_patterns)[:8]:
        line_no = _line_at_offset(text_for_patterns, off)
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.WARN,
            message=f"長句沒呼吸 (§quality-scan #8d {cjk}字/{pauses}個停頓)：{seg[:50]}…",
            line=line_no,
            snippet=seg[:80],
            editorial_ref="EDITORIAL.md §段落呼吸 + §歐化語法",
            fix_suggestion=(
                "這句塞太多逗號子句、太長，讀起來像堆修飾語的湯。在意義段落處斷成 2-3 個"
                "句號句；一句話講一件事，讓句子之間有呼吸。"
            ),
        )

    # ── 8e. 英文式超短句開場 (soft-launch WARN，不計分) — 哲宇 directive ──
    for off, opener, olen, nlen in _detect_english_openers(body)[:8]:
        line_no = _line_at_offset(body, off)
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.WARN,
            message=f"英文式短句開場 (§歐化：開場{olen}字→接{nlen}字)：「{opener}」",
            line=line_no,
            snippet=opener[:60],
            editorial_ref="EDITORIAL.md §歐化語法 §英文式短句開場",
            fix_suggestion=(
                "段落以超短句定調再展開，是英文 topic-sentence 腔（哲宇 anti-example："
                "「協議並沒有收尾。自救會指控…」）。中文自然行文直接流進主題：把短開場併入"
                "後句，或改成有具體人事時地的句子起頭，不要孤立一個四五字短句當引子。"
            ),
        )

    # ── 9. Textbook opening ──
    if _detect_textbook_opening(body):
        score += 2
        reasons.append("教科書開場")

    # ── 10. Formulaic ending ──
    if _detect_formulaic_ending(body):
        score += 2
        reasons.append("套路結尾")

    # ── 11. Template H2 ──
    template_h2 = _count_template_h2(body)
    if template_h2 >= 4:
        score += 3
        reasons.append(f"萬用H2×{template_h2}")
    elif template_h2 >= 3:
        score += 2
        reasons.append(f"萬用H2×{template_h2}")
    elif template_h2 >= 2:
        score += 1
        reasons.append(f"萬用H2×{template_h2}")

    # ── 12. LIST-DUMP (back-half bullet density disproportionate to front) ──
    is_hub = _is_hub_file(target)
    front_b, back_b, front_t, back_t = _bullet_ratios_split(body)
    if front_t > 0 and back_t > 0:
        front_ratio = front_b * 100 // front_t
        back_ratio = back_b * 100 // back_t
        if is_hub:
            # Hub pages naturally back-heavy index lists — relaxed
            if back_ratio > 60 and back_ratio > front_ratio * 3:
                score += 1
                reasons.append(f"後段清單堆砌{back_ratio}%(Hub)")
        else:
            if back_ratio > 40 and back_ratio > front_ratio * 2:
                score += 3
                reasons.append(f"後段清單堆砌{back_ratio}%")
            elif back_ratio > 30:
                score += 2
                reasons.append(f"後段清單堆砌{back_ratio}%")

    # ── 13. THIN (H2 blocks with < 3 prose lines) ──
    thin = _count_thin_blocks(body)
    if is_hub:
        if thin >= 4:
            score += 1
            reasons.append(f"稀薄段落×{thin}(Hub)")
    else:
        if thin >= 2:
            score += 2
            reasons.append(f"稀薄段落×{thin}")
        elif thin >= 1:
            score += 1
            reasons.append(f"稀薄段落×{thin}")

    # ── 14. QUALITY-DECAY (front prose ratio >> back prose ratio) ──
    fp, bp, fa, ba = _prose_ratios_split(body)
    if fa > 0 and ba > 0:
        front_pr = fp * 100 // fa
        back_pr = bp * 100 // ba
        if is_hub:
            if back_pr < front_pr // 4:
                score += 1
                reasons.append(f"品質衰退前{front_pr}%後{back_pr}%(Hub)")
        elif front_pr > 0:
            if back_pr < front_pr // 2:
                score += 3
                reasons.append(f"品質衰退前{front_pr}%後{back_pr}%")
            elif back_pr < (front_pr * 7) // 10:
                score += 1
                reasons.append(f"品質衰退前{front_pr}%後{back_pr}%")

    # ── 16. Citation desert ──
    fn_defs = _count_footnote_defs(body)
    word_count = _word_count(body)
    if fn_defs == 0:
        if word_count > 500:
            if urls == 0:
                score += 4
                reasons.append("引用荒漠(零腳註零URL)")
            else:
                score += 2
                reasons.append("引用荒漠(零腳註)")
        elif word_count > 200:
            score += 1
            reasons.append("無腳註")

    # ── Manifesto §11 Tier 1: 對位句型 ──
    # Emit per-match with line + 前後文 context so writers can locate fast
    # (per 2026-05-10 sad-shockley feedback: tool 應該直接指出哪裡 + 前後文).
    tier1_total = 0
    for pat in _TIER1_PATTERNS:
        matches = list(pat.finditer(text_for_patterns))
        if matches:
            tier1_total += len(matches)
            for m in matches:
                line_no = _line_at_offset(text_for_patterns, m.start())
                ctx = _context_around(text_for_patterns, m.start(), m.end())
                yield Violation(
                    check=CHECK_NAME,
                    severity=Severity.WARN,
                    message=f"對位句型 (§11 Tier 1)：{ctx}",
                    line=line_no,
                    snippet=m.group(0)[:80],
                    editorial_ref="MANIFESTO.md §11 Tier 1 對位句型禁令",
                    fix_suggestion=(
                        "三題判準 (MANIFESTO §11.1)：(1) 對比是內容本身嗎？(2) 正面主張能獨立站立嗎？"
                        "(3) 讀者真會預設 X 嗎？三題全 no = 改成正面斷言"
                    ),
                )

    # ── §11 Tier 1 補：強加對比的收束句 — 2026-07-19 哲宇 directive ──
    for m in _RE_FORCED_CONTRAST_CLOSER.finditer(text_for_patterns):
        line_no = _line_at_offset(text_for_patterns, m.start())
        ctx = _context_around(text_for_patterns, m.start(), m.end())
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.WARN,
            message=f"強加對比收束句 (§11 Tier 1 散文變體)：{ctx}",
            line=line_no,
            snippet=m.group(0)[:60],
            editorial_ref="MANIFESTO.md §11 Tier 1 + EDITORIAL §對位句型",
            fix_suggestion=(
                "把並列的兩者硬拗成「其實是兩件事 / 兩本帳 / 不同的語言」是對位句型的散文變體："
                "作者用一個抽象對比幫段落強行收尾。改法：直接寫出兩者各自是什麼、差在哪的具體"
                "後果，不要用「根本是兩件事」這種抽象標籤代替說明。"
            ),
        )

    # ── 歐化「(不)是 X 的」判斷句 — 2026-06-07 哲宇 directive 儀器化 ──
    for m in _RE_EURO_DE.finditer(text_for_patterns):
        line_no = _line_at_offset(text_for_patterns, m.start())
        ctx = _context_around(text_for_patterns, m.start(), m.end())
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.WARN,
            message=f"歐化「是…的」判斷句：{ctx}",
            line=line_no,
            snippet=m.group(0)[:40],
            editorial_ref="EDITORIAL.md §歐化語法 (是…的判斷句)",
            fix_suggestion=(
                "去掉「是…的」讓形容詞直接當謂語：「這個選址不是隨便的」→「這個選址不隨便」"
                "或「挑這裡有它的道理」；「答案是顯而易見的」→「答案顯而易見」。"
            ),
        )

    # ── Manifesto §11 Tier 2: AI metaphor ──
    tier2_total = sum(text_for_patterns.count(w) for w in _TIER2_WORDS)
    # 「重」當抽象份量隱喻：regex 逐處 WARN（給 line + ctx）+ 計入密度
    # 2026-06-04 哲宇 callout「把『很重』列為 AI 氾濫用語」
    weight_hits = list(_RE_WEIGHT_METAPHOR.finditer(text_for_patterns))
    for m in weight_hits:
        line_no = _line_at_offset(text_for_patterns, m.start())
        ctx = _context_around(text_for_patterns, m.start(), m.end())
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.WARN,
            message=f"AI 份量隱喻「{m.group(0)}」(§11 Tier 2「重」當抽象份量)：{ctx}",
            line=line_no,
            snippet=m.group(0)[:80],
            editorial_ref="MANIFESTO.md §11 Tier 2",
            fix_suggestion=(
                "把抽象的「重」改成具體後果或畫面：「最重的一刻」→ 直接寫那一刻發生什麼／"
                "為什麼忘不掉；「份量很重」→「壓得人喘不過氣」或寫出具體代價。物理重量例外。"
            ),
        )
    tier2_total += len(weight_hits)
    if tier2_total >= 2:
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.WARN,
            message=f"AI 抽象 metaphor 密度 (§11 Tier 2): 累計 {tier2_total} 處",
            editorial_ref="MANIFESTO.md §11 Tier 2",
        )

    # ── Manifesto §11 Tier 3: ritual 語 ──
    tier3_total = sum(text_for_patterns.count(p) for p in _TIER3_PHRASES)
    if tier3_total >= 1:
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.WARN,
            message=f"AI ritual 句 (§11 Tier 3): 累計 {tier3_total} 處",
            editorial_ref="MANIFESTO.md §11 Tier 3",
        )

    # ════════════════════════════════════════════════════════════════
    # §盼望而不粉飾 (2026-06-15 哲宇 directive) — 全 WARN，不計 score budget
    # （跟 §11 Tier 1-3 一致：surface drift 但不擋既有 stage 閘）
    # ════════════════════════════════════════════════════════════════

    # ── 島嶼自稱密度 (balance, not ban) ──
    island_hits = list(_RE_ISLAND_EUPHEMISM.finditer(text_for_patterns))
    island_n = len(island_hits)
    taiwan_n = len(_RE_TAIWAN_REF.findall(text_for_patterns))
    # ratio-based：島嶼文學用法不罰，只抓「拿島當台灣的迴避稱呼」的 crutch。
    # 條件 = island 佔「島+台灣」國名指稱 > 1/4 (3×island > taiwan) 且 ≥ 3 次，
    # 或完全不稱台灣只用島 (≥ 2 次 + taiwan_n==0)。長文 5 島 vs 77 台灣 = 健康
    # 文學用法，不 flag（避免 instrument 哭狼，REFLEXES #24）。
    if (island_n >= 3 and 3 * island_n > taiwan_n) or (island_n >= 2 and taiwan_n == 0):
        for m in island_hits[:10]:
            line_no = _line_at_offset(text_for_patterns, m.start())
            ctx = _context_around(text_for_patterns, m.start(), m.end())
            yield Violation(
                check=CHECK_NAME,
                severity=Severity.WARN,
                message=f"島嶼自稱密度偏高 ({island_n} 處 vs 台灣 {taiwan_n} 處，§自稱)：{ctx}",
                line=line_no,
                snippet=m.group(0)[:40],
                editorial_ref="MANIFESTO.md §跟台灣的關係 §自稱 + EDITORIAL §六",
                fix_suggestion=(
                    "島嶼文學性可以保留，但不要過度——大多數時候大方寫「台灣」「臺灣」「這個國家」。"
                    "逐處判斷：曹永和「以島嶼為主體」島史脈絡（留），還是不敢寫台灣的迴避稱呼（換）？"
                ),
            )

    # （PUA 體 / 媒體焦慮體偵測器已移除 — 見檔頭 docstring + _RE_ISLAND 上方註解。
    #   語意判斷非句法特徵，regex 92-100% 假陽性，改人工判斷 by EDITORIAL §六。）

    # ════════════════════════════════════════════════════════════════
    # AI 痕跡 Tier 4 (speak-human-tw 轉譯, 2026-07-16 soft-launch)
    # 併入 score budget（跟 quality-scan §1-16 同一計分家族）。
    # ════════════════════════════════════════════════════════════════

    # ── (a) 立場真空：每 hit +1，上限 +2 ──
    stance_hits = list(_RE_STANCE_VACUUM.finditer(text_for_patterns))
    if stance_hits:
        score += min(len(stance_hits), _STANCE_VACUUM_SCORE_CAP)
        reasons.append(f"立場真空×{len(stance_hits)}")
        for m in stance_hits[:10]:
            line_no = _line_at_offset(text_for_patterns, m.start())
            ctx = _context_around(text_for_patterns, m.start(), m.end())
            yield Violation(
                check=CHECK_NAME,
                severity=Severity.WARN,
                message=f"立場真空 (§AI痕跡 Tier4-a「{m.group(0)}」)：{ctx}",
                line=line_no,
                snippet=m.group(0)[:40],
                editorial_ref="speak-human-tw #37/#30 + EDITORIAL.md",
                fix_suggestion="留判斷：文章自己的立場是什麼？把「見仁見智」換成具體斷言或明確標示為留待讀者判斷的理由。",
            )

    # ── (b) 價值上升詞密度：≥3 hits +1、≥6 +2 ──
    value_inflation_hits = list(_RE_VALUE_INFLATION.finditer(text_for_patterns))
    vi_n = len(value_inflation_hits)
    if vi_n >= 6:
        score += 2
        reasons.append(f"價值上升詞×{vi_n}")
    elif vi_n >= 3:
        score += 1
        reasons.append(f"價值上升詞×{vi_n}")
    if vi_n >= 3:
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.WARN,
            message=f"價值上升詞密度 (§AI痕跡 Tier4-b): 累計 {vi_n} 處 (標誌著/見證了/彰顯了/體現了/突顯了/奠定...基礎/不可磨滅)",
            editorial_ref="speak-human-tw #37/#30 + EDITORIAL.md",
            fix_suggestion="改成具體描述事件本身，不用「標誌著/見證了」幫它加冕。",
        )

    # ── (c) 罐頭結尾起手式：最後 3 段出現任一 → +2 (fixed) ──
    if _detect_canned_ending_opener(body):
        score += 2
        reasons.append("罐頭結尾起手式")
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.WARN,
            message="罐頭結尾起手式 (§AI痕跡 Tier4-c)：最後 3 段內出現「總的來說/綜上所述/總而言之/總結來說」",
            editorial_ref="speak-human-tw #37/#30 + EDITORIAL.md",
            fix_suggestion="拿掉起手式，讓收尾句直接說結論本身。",
        )

    # ── (d) 時代帽子開場：第一個 prose 段落以此開頭 → +2 (fixed) ──
    if _detect_time_hat_opening(body):
        score += 2
        reasons.append("時代帽子開場")
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.WARN,
            message="時代帽子開場 (§AI痕跡 Tier4-d)：第一段以「在當今/在這個...的時代/隨著...的(快速)發展」開頭",
            editorial_ref="speak-human-tw #37/#30 + EDITORIAL.md",
            fix_suggestion="從具體的人事時地物開始，不要先戴一頂時代帽子。",
        )

    # ── (e) 假推論密度：「這意味著」≥2 hits +1 ──
    false_inference_n = text_for_patterns.count(_FALSE_INFERENCE_PHRASE)
    if false_inference_n >= _FALSE_INFERENCE_MIN_HITS:
        score += 1
        reasons.append(f"假推論密度×{false_inference_n}")
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.WARN,
            message=f"假推論密度 (§AI痕跡 Tier4-e「這意味著」): 累計 {false_inference_n} 處",
            editorial_ref="speak-human-tw #37/#30 + EDITORIAL.md",
            fix_suggestion="檢查每一處「這意味著」後面的推論是否文章本身證據支撐，不是就直接寫因果，是就去掉這個轉折詞。",
        )

    # ── (f) 首先/其次/最後 三件套：同篇同時出現 → +1 ──
    has_first = "首先" in text_for_patterns
    has_second = "其次" in text_for_patterns
    has_last = ("最後" in text_for_patterns) or ("再者" in text_for_patterns)
    if has_first and has_second and has_last:
        score += 1
        reasons.append("首先其次三件套")
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.WARN,
            message="首先/其次/最後 三件套 (§AI痕跡 Tier4-f)：同篇同時出現「首先」+「其次」+「最後/再者」",
            editorial_ref="speak-human-tw #37/#30 + EDITORIAL.md",
            fix_suggestion="改成敘事順序（時間/因果）串接，不用條列式接續詞堆疊。",
        )

    # ── Final score summary as a single violation ──
    # The runner can gate on score via profile.fail_on = "score-budget".
    if score > 0:
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.WARN,
            message=f"prose-health score: {score} (≤ {score_budget} = pass) — {'; '.join(reasons)}",
            editorial_ref=EDITORIAL_REF,
            fix_suggestion=str(score),  # used by score-budget gating
        )
