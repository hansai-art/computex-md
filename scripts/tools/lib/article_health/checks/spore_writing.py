r"""spore_writing — SPORE-specific writing rules instrumentation.

Direction D from reports/spore-pipeline-evolution-plan-2026-05-08.md:
    把 SPORE-WRITING.md 的 prose 規則從「提醒 + 信任 AI 自律」升級為
    plugin gate (REFLEXES #15 第 N 次驗證：memory 是自律，pipeline 才是閘門).

Rules implemented (regex-only, Wave 1 + Wave 2):
  Wave 1 (initial ship 2026-05-08):
  - 編年體 lead 病 (Rule #15, 高鐵 s35 教訓)
    第一行 prose 開頭不該是「YYYY 年 M 月 D 日，XXX」這種新聞 lead
    觸發：line 1 of body matches `^\d{4}\s*年` 或 `^\d{4}\.`
  - 引語倒裝 (Rule #9, 李洋 #28 教訓)
    `「XXX」他/她說` 這種沒場景的引語倒裝
    應改為「他在 [場景] 說：『XXX』」

  Wave 2 (evolve 2026-05-08 同 session, 從 spore 成效數據驗證):
  - 朋友 tone prime (Rule #14, 高鐵 s35 教訓 + 5 月份 hook tier 數據)
    第一行 prose 必須有 friend tone prefix（你知道嗎？/欸/直接人說話）
    或滿足 Tier 1b「具體 anchor + 反差 hook」開場
    觸發：第一行不是 prefix + 不是引語 + 不是具體場景 → WARN 提醒加 prefix
    跳過：blueprint table（已 covered）/ harvest log meta（covered）

APPLIES_TO 設計：
  路徑必須在 docs/factory/SPORE-BLUEPRINTS/ 或 docs/factory/SPORE-HARVESTS/
  其他文章的開頭可以是日期（時間軸型 D 模板就是合法的），所以這條規則不普適。

Future extensions (deferred):
  - Rule #16 Scene-List-Scene 結構 (need LLM-as-judge, not pure regex)
  - Rule #8 同名連用 ≥3 (token analysis, 需要中文斷詞)
  - Reach × accuracy retroactive trigger (不在 plugin scope, SPORE-VERIFY 文件層 SOP)

Canonical:
  - docs/factory/SPORE-WRITING.md §進階寫作技術
  - docs/factory/SPORE-VERIFY.md §§11 書寫節制閘
"""

from __future__ import annotations
import re
from typing import Any, Iterator

from ..types import FileTarget, Severity, Violation


CHECK_NAME = "spore-writing"
DIMENSION = "spore-prose"
DEFAULT_SEVERITY = Severity.HARD
EDITORIAL_REF = "SPORE-WRITING.md §進階寫作技術"
APPLIES_TO = ["zh-TW"]  # 孢子主要是中文 prose


# ── Rule #15: 編年體 lead 病 (chronicle lead) ────────────────────────────────
# 第一行不應該是「YYYY 年」「YYYY.MM.DD」這種新聞 lead 開頭
_RE_CHRONICLE_LEAD = re.compile(
    r"^\s*(?:\d{4}\s*年|\d{4}[/.\-]\d{1,2}[/.\-]\d{1,2}|\d{4}-\d{2}-\d{2})",
    re.MULTILINE,
)

# ── Rule #9: 引語倒裝（quote inversion） ────────────────────────────────────
# 「XXX」他說 / 「XXX」她說 / 「XXX」XXX 說
# 改為：他在 [場景] 留了一句話：『XXX』
_RE_QUOTE_INVERSION = re.compile(
    r"「[^」]{5,80}」[^\n。]{0,8}[他她][^\n。]{0,5}說",
)


# ── Rule #14: 朋友 tone prime（friend-tone curiosity prime） ─────────────────
# v2 (2026-05-28): WARN → HARD severity inversion. 觸發背景: 5/27-5/28 #97 美食 /
#   #101 落日飛車 / #103 周蕙 連續三條 spore drift — #97「你知道嗎—」(破折號取代
#   問號) / #101「你知道嗎，」(逗號 + 無 emoji) / #103「走進台灣任何一間 KTV」(完全
#   無 prefix) 通通 silent pass。哲宇 callout「為什麼孢子失去『你知道嗎』voice」+
#   診斷指向 CONTRACT v1.0 over-engineering → plugin severity 太弱 + scope 太窄。
#
# 孢子第一行必須有「朋友跟你講八卦」的 curiosity prime，不是新聞 lead。
# 對應 [MANIFESTO §我怎麼說話](docs/semiont/MANIFESTO.md#我怎麼說話)「像在跟朋友介
# 紹台灣：『欸你知道嗎⋯⋯』」哲學落實。
#
# 合格 prefix（友善開場式）：
#   1. 「你知道嗎？」/「你知道嗎，」（強烈推薦 + emoji，舊風格允許逗號）
#   2. 「欸，」/「欸你」+ 具體事件片段
#   3. 「身為台灣人」/「想像」/「如果」/「當你」 第二人稱開場
#   4. 直接人說話（「『...』」引語開場 — hook 力夠強的 case）
#   5. 純 emoji 開場
#
# v2 升級：trigger 從「news lead AND no prefix」改成「no prefix → HARD」（除非
# publicletter F-family / E-thread family / hook_tier=N/A frontmatter exempt）。
# 不再依賴 looks_like_news_lead 判斷 — 場景代入 / 第二人稱化也不算「等效 prime」，
# 必須字面 prefix 才算過閘。
_RE_FRIEND_PREFIX = re.compile(
    r"^\s*(?:你知道嗎[？，?,]|欸[，,]|欸你|身為台灣人|想像[一下你]|"
    r"如果(?:[你台]|[\d])|當[你你們]|"
    r"[「『\"]|[\U0001F300-\U0001F9FF\U0001F600-\U0001F64F])"
)
# Family scope detection — publicletter / E-thread / non-viral 不適用 friend-tone gate
_RE_PUBLICLETTER_FAMILY = re.compile(
    r"^(?:template:\s*F[-\s]|type:\s*station-announcement|hook_tier:\s*N/A)",
    re.MULTILINE,
)


def _is_publicletter_family(text: str) -> bool:
    """Detect F-publicletter / E-thread / non-viral family via frontmatter.

    Used to scope Rule #14 — friend-tone prime is only required for viral
    family (A/B/C/D templates). F-公開信 (站方公開信) uses 教授 tone, not
    朋友 tone. E-串文 may have different prime convention.
    """
    return bool(_RE_PUBLICLETTER_FAMILY.search(text[:2000]))


# 新聞 lead pattern (legacy from v1, retained as INFO-only diagnostic — not the
# HARD trigger 在 v2)：補抓「機構 + 動詞」客觀敘事 開場
_RE_NEWS_LEAD = re.compile(
    r"^\s*[一-鿿]{2,8}(?:宣布|表示|簽下|公布|成立|頒布|通過|裁決|"
    r"發表|主張|強調|指出|呼籲|批評|證實|否認|聲明|警告)"
)


def _is_spore_path(path: str) -> bool:
    """Check if file is a SPORE blueprint, harvest log, or ad-hoc draft.

    Path conventions:
      - docs/factory/SPORE-BLUEPRINTS/ (production blueprints)
      - docs/factory/SPORE-HARVESTS/ (production harvest logs)
      - /tmp/spore-* (ad-hoc draft testing — any tmp file with `spore-` prefix)
      - /tmp/...spore... (other ad-hoc paths containing "spore")
    """
    p_lower = str(path).lower()
    return (
        "SPORE-BLUEPRINTS" in path
        or "SPORE-HARVESTS" in path
        or "/spore-" in p_lower  # /tmp/spore-anything.md
        or p_lower.startswith("spore-")
        or p_lower.endswith("/spore.md")
    )


_RE_NUMBERED_LIST = re.compile(r"^\s*\d+\.\s")  # `1. `, `2. ` ordered list items


def _strip_frontmatter_and_meta(text: str) -> tuple[str, int]:
    """Return (body_text, body_start_line).

    v2 (2026-05-28): 修補 false-positive — Rule #14 對 #101 落日飛車 / #105 瘂弦
    錯把「紀實/煽情閘四問自檢」numbered list 當 spore body 第一行 trigger HARD。
    真正 spore body 在 ``` ``` code fence 內（per blueprint convention §Draft Body
    / §Spore 文案 final）。新策略：找第一個 ``` fence start，從 fence 內取首行。
    Fallback：沒找到 fence → 用 v1 strip 邏輯（heading/blockquote/table/bullet/
    bold-meta/numbered-list 全 skip）。

    Strips frontmatter (--- ... ---) and tries to locate the actual spore body:
      Priority A: first ``` ``` code fence content (production blueprint convention)
      Priority B: strip leading meta lines (legacy fallback for ad-hoc drafts)
    """
    lines = text.split("\n")
    i = 0
    # Skip frontmatter
    if i < len(lines) and lines[i].strip() == "---":
        i += 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        if i < len(lines):
            i += 1  # skip closing ---

    # Priority A: locate the spore body code fence content via proper open/close
    # state machine (v2 2026-05-28 fix bug — previous version treated fence-close
    # as new fence-open, picking up bogus content like "## 配圖" heading after a
    # closed fence).
    candidate_fences: list[tuple[int, str]] = []  # (line_idx, first_prose_line)
    in_fence = False
    k = i
    while k < len(lines):
        if lines[k].strip().startswith("```"):
            if in_fence:
                in_fence = False  # closing
            else:
                in_fence = True  # opening — capture first prose line
                j = k + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and not lines[j].strip().startswith("```"):
                    candidate_fences.append((j, lines[j].strip()))
        k += 1

    # Filter: real spore body has CJK char + length ≥ 50 + no URL signal in line.
    # URL signals (`https://`, `👉`, `完整故事`) indicate self-reply / inline URL
    # meta fence (e.g. #59 黃魚鴞 / #93 國家人權博物館 first fence is self-reply
    # URL not the body). Skip these → pick next body fence.
    def _is_real_body_fence(content: str) -> bool:
        # Threshold 5: friend prefix line can be very short
        # (e.g. #93 國家人權「你知道嗎？🧬」6 chars on its own line, real spore
        # body continues after blank). URL-only / meta fences filtered by other
        # rules below — `#` markdown comment / `http` URL / 「完整故事」CTA /
        # 「👉」emoji marker. Earlier 30+ threshold was too strict (rejected
        # short hook lines), 5 catches all real body openers.
        if len(content) < 5:
            return False
        if content.startswith("#") or content.startswith("http"):
            return False
        # URL-bearing line = self-reply / inline link meta, not body
        if "https://" in content or "http://" in content:
            return False
        # 「👉 完整故事」style CTA prefix = self-reply
        if "👉" in content or content.startswith("完整故事"):
            return False
        return bool(re.search(r"[一-鿿]", content))

    body_fences = [(idx, c) for idx, c in candidate_fences if _is_real_body_fence(c)]
    if body_fences:
        # Use first qualifying fence (production spore = first body fence)
        body_line_idx = body_fences[0][0]
        return ("\n".join(lines[body_line_idx:]), body_line_idx)

    # Priority B: legacy strip fallback — used only for ad-hoc / planning-stage
    # blueprints (e.g. early #33 草東 v2.1 era no fence yet). Rule #14 caller
    # will see the legacy-strip first line; planning-stage blueprints whose
    # body isn't yet written may yield false-positive HARD — acceptable per
    # 「未 finalize 的 blueprint 本就該被閘攔」principle (forces writer to put
    # body in fence convention before plugin pass).
    while i < len(lines) and (
        not lines[i].strip()
        or lines[i].strip().startswith("#")
        or lines[i].strip().startswith(">")
        or lines[i].strip().startswith("|")  # blueprint table rows
        or lines[i].strip().startswith("- ")  # bullet
        or lines[i].strip().startswith("**")  # bold inline meta like **Angle**: ...
        or bool(_RE_NUMBERED_LIST.match(lines[i]))  # ordered list `1. `
    ):
        i += 1
    return ("\n".join(lines[i:]), i)


def check(target: FileTarget, config: dict[str, Any]) -> Iterator[Violation]:
    """Run SPORE-WRITING-specific regex checks.

    Skipped when file is not in SPORE-BLUEPRINTS / SPORE-HARVESTS path
    (returning early so普通文章不誤觸發 Rule #15 timeline templates).
    """
    if not _is_spore_path(str(target.path)):
        return

    body_text, body_start = _strip_frontmatter_and_meta(target.text)

    # ── Rule #15: 編年體 lead 病 ──
    # Only the very first prose line is checked — body 中段可有日期
    first_line = body_text.split("\n", 1)[0] if body_text else ""
    if first_line and _RE_CHRONICLE_LEAD.match(first_line):
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.HARD,
            message=(
                "編年體 lead 病 (Rule #15): "
                "第一行不該是日期開頭，改用人物動作 / 引語"
            ),
            line=body_start + 1,
            snippet=first_line[:80],
            editorial_ref="SPORE-WRITING.md §避免編年體 lead 病",
            fix_suggestion=(
                "改成「[人物] 在 [場景] 說：『[引語]』」或「[人物] 做了 [動作]」開頭"
            ),
        )

    # ── Rule #9: 引語倒裝 ──
    for m in _RE_QUOTE_INVERSION.finditer(body_text):
        # Compute approximate line number (offset from body_start)
        prefix = body_text[: m.start()]
        line_offset = prefix.count("\n")
        yield Violation(
            check=CHECK_NAME,
            severity=Severity.WARN,
            message=(
                "引語倒裝 (Rule #9): "
                "改為「他在 [場景] 留了一句話：『XXX』」給讀者場景感"
            ),
            line=body_start + line_offset + 1,
            snippet=m.group(0)[:80],
            editorial_ref="SPORE-WRITING.md §禁止清單",
        )

    # ── Rule #14 v2: 朋友 tone prime — HARD gate ──
    # v2 (2026-05-28) inversion: WARN → HARD + 取消 looks_like_news_lead 依賴。
    # 場景代入 / 第二人稱化 / 日常感都不算「等效 prime」— 必須字面 prefix。
    # Scope: viral family only（F-公開信 / E-thread / hook_tier=N/A exempt）。
    is_publicletter = _is_publicletter_family(target.text)
    has_friend_prefix = bool(_RE_FRIEND_PREFIX.match(first_line)) if first_line else False
    if (
        first_line
        and len(first_line) >= 8
        and not is_publicletter
    ):
        if not has_friend_prefix:
            looks_like_news_lead = bool(_RE_NEWS_LEAD.match(first_line))
            extra_hint = (
                "（且開場像新聞 lead）" if looks_like_news_lead else ""
            )
            yield Violation(
                check=CHECK_NAME,
                severity=Severity.HARD,  # v2: WARN → HARD
                message=(
                    f"朋友 tone prime 缺失 (Rule #14 v2 HARD){extra_hint}: "
                    "viral spore 第一行必須有友善開場 prefix —「你知道嗎？」/"
                    "「欸，」/「身為台灣人」/「想像」/「當你」/「『引語』」/"
                    "emoji 之一。場景代入 / 第二人稱化不算等效 prime。"
                ),
                line=body_start + 1,
                snippet=first_line[:80],
                editorial_ref=(
                    "SPORE-WRITING.md §朋友 tone prime + MANIFESTO §我怎麼說話"
                ),
                fix_suggestion=(
                    "改第一行：「你知道嗎？{emoji} {反差 hook}」"
                    "或「欸，{具體事件}」"
                    "或直接引語「『XXX』{說話者} 在 {場景} 留下這句」開場。"
                    "若本 spore 屬 F-公開信 / E-thread / 非 viral family，"
                    "frontmatter 加 `template: F-...` 或 `hook_tier: N/A` exempt。"
                ),
            )

    # ── Rule #14.A v3: Standalone hook line — WARN gate ──
    # v3 (2026-05-28) 哲宇 directive「補充標準 spore 格式」觸發 canonical 化。
    # 標準孢子格式：「你知道嗎？{emoji}」獨立第一行（≤ 15 chars）+ blank line +
    # 故事段落。Inline hook (「你知道嗎？🎤 1999 年福茂發行...」整段一行) 不擋 ship
    # 但 surface drift signal —— 視覺呼吸 + thumb-scroll 停留 + emoji 錨點都被
    # dilute。
    #
    # Trigger condition (WARN):
    #   has_friend_prefix=True AND
    #   first_line length > 15 chars (inline with story content)
    #   AND not publicletter family
    if has_friend_prefix and not is_publicletter and first_line:
        first_line_len = len(first_line)
        if first_line_len > 15:
            yield Violation(
                check=CHECK_NAME,
                severity=Severity.WARN,
                message=(
                    f"Hook 未獨立第一行 (Rule #14.A v3 WARN): "
                    f"first_line={first_line_len} chars inline 與故事段落混在一起，"
                    "標準格式「你知道嗎？{emoji}」獨立短行 (≤15 chars) + 空白行 + 故事段落"
                ),
                line=body_start + 1,
                snippet=first_line[:60],
                editorial_ref="SPORE-WRITING.md §標準孢子格式",
                fix_suggestion=(
                    "拆「你知道嗎？{emoji}」獨立第一行 + 空白行 + 故事段落 1 開頭。"
                    "視覺呼吸 + thumb-scroll 停留 + emoji 錨點都需要 hook 獨立成行。"
                    "若極短 spore (<200 chars 主貼) 或觀察者拍板 inline，可接受 WARN。"
                ),
            )

    # ── Rule #14.B v3: Paragraph block count — WARN gate ──
    # 標準孢子格式有 4-7 段（hook standalone + 3-5 story + optional URL）。
    # < 4 段 = monolithic prose (collapsed state)；> 6 段 = staccato pattern
    # (Twitter 串文 style 不是紀實段落)。
    #
    # Scope: viral family only。F-公開信 / E-thread frontmatter signal exempt。
    if not is_publicletter and body_text.strip():
        paragraphs = [
            p.strip() for p in body_text.split("\n\n") if p.strip()
        ]
        para_count = len(paragraphs)
        # 短 spore (主貼 < 200 chars) 可以 3 段；標準 4-7
        body_total_len = sum(len(p) for p in paragraphs)
        min_para = 3 if body_total_len < 200 else 4
        if para_count < min_para:
            yield Violation(
                check=CHECK_NAME,
                severity=Severity.WARN,
                message=(
                    f"段落呼吸不足 (Rule #14.B v3 WARN): "
                    f"only {para_count} paragraph blocks (body_total={body_total_len} chars), "
                    f"標準 spore 4-5 段呼吸 (hook standalone + 3-5 story + optional URL)。"
                ),
                line=body_start + 1,
                snippet=body_text[:80].replace("\n", "⏎"),
                editorial_ref="SPORE-WRITING.md §標準孢子格式",
                fix_suggestion=(
                    "拆 monolithic prose 成 4-5 paragraph：時間軸 cut 處切段 + "
                    "場景轉換處切段 + 引語前後切段。"
                    "對應 SOCIAL-POSTING-PIPELINE pre-ship check 7 (compose block ≥ 4)。"
                ),
            )
