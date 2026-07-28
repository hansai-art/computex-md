"""viz-health — 文章內視覺化模組的可信度 + AI 可讀性 + 結構完整性閘門（REWRITE Stage 4）。

儀器化 docs/editorial/graph.md §七 視覺化檢查清單 + §四 模組語法的可機檢項目
（其餘靠人工 preview）：

  A. 資料視覺化模組必標來源
     tw-bars / tw-waffle / tw-line / tw-heatmap / tw-stat 等這些「呈現資料關係」
     的模組，每個都該有來源（在 fenced block 內加一列 `來源：機構，年份` 會自動
     變成模組下方的來源 caption）。沒有 = 可信度破口 + AI 引用時無從追溯。對應
     graph.md §三.8 + The Pudding「transparency as trust」原則。

  B. 禁「如上圖／如下圖」AI-blind 指示語
     GPTBot / PerplexityBot / ClaudeBot 不跑 JS、看不到圖。「如上圖所示」這種句子
     對 AI 爬蟲毫無意義，且關鍵數值若只在圖裡，LLM 提取不到 → 違反 COMPUTEX.md 的
     AI-SEO / 主權使命（「讓 LLM 讀得懂的視覺化 = 主權的視覺化」）。關鍵數值要也
     寫進 prose，指示語改成具體結論或「見下表」。

  C. 結構完整性（2026-07-16 viz-evolution 新增，graph.md §四 模組語法的儀器化）
     每種圖表模組在 graph.md §四 都寫死了幾何限制（斜率圖恰兩點、折線圖 ≤3
     序列、堆疊條 ≤5 類別、方格圖加總 ≈100 ……）。這些不是美感建議，違反時
     renderer 要嘛畫出誤導的圖、要嘛直接畫壞。全部 WARN 級（soft-launch，跟
     A/B 一致）。含通用的「資料模組沒有可解析資料列」malformed 檢查——這種
     block 會被 renderer 靜默略過或退化成 code block，presence（fenced block
     存在）≠ appearance（渲染正確），對應 LESSONS 2026-06-12 viz-evolution。

設計脈絡：reports/article-visualization-design-2026-06-06.md §9.1。
DEFAULT WARN（soft-launch；legacy 文章可能含 violation，且 B 句式偶有 dual-use）。
待 vc≥3 production case 後評估是否對 rewrite-stage-4 升 HARD（per chronicle-lead pattern）。

2026-07-16 gate 集合審計（全站 226 個 block 自動統計）：被 `_DATA_MODULES` gate
的 10 個圖表模組來源缺失率 0%，沒被 gate 的 tw-timeline / tw-versus / tw-stat
缺失率 41–46%（53 個 block）——gate 集合的形狀直接決定行為，這三個高頻編輯模組
實質沒被儀器化過。追加進 `_DATA_MODULES`，會讓 ~53 個 legacy block 開始出 WARN
（default WARN 不擋 commit，只有 rewrite-stage-4 profile 對新文是 HARD）——這是
預期行為，不是誤報，legacy 債務要浮出來才看得見。tw-figure 維持排除：來源走
自身 line3 positional slot，本檢查判斷不到。
"""

from __future__ import annotations
import re
from typing import Any, Iterator

from ..types import FileTarget, Severity, Violation


CHECK_NAME = "viz-health"
DIMENSION = "visualization"
DEFAULT_SEVERITY = Severity.WARN
EDITORIAL_REF = "graph.md §七 視覺化檢查清單 + §六 AI 可讀性"
EDITORIAL_REF_SHAPE = "graph.md §四 模組語法 + §二 型錄"
APPLIES_TO = ["zh-TW"]  # 中文 SSOT 檢查；翻譯沿用幾何，文字由 babel 處理

# 呈現「資料關係」的模組 → 強制標來源（用 `來源：…` 列）。
# tw-figure 是關鍵數字 callout，來源走自身 line3 positional slot，不在此強制集。
# 2026-06-12 viz-evolution：+slope/dot/stack/pyramid/tiles/iso（graph.md v2.0 新六圖表模組）。
# 2026-07-16 viz-evolution：+timeline/versus/stat（審計：gate 內 0% 缺失 vs gate 外
# 41–46% 缺失，53 個 block——gate 集合本身決定了儀器有沒有在檢查）。
# 2026-07-16 viz-evolution：+arc/multiples（新模組，也需要來源列）。
_DATA_MODULES = {
    "tw-bars",
    "tw-waffle",
    "tw-line",
    "tw-heatmap",
    "tw-slope",
    "tw-dot",
    "tw-stack",
    "tw-pyramid",
    "tw-tiles",
    "tw-iso",
    "tw-timeline",
    "tw-versus",
    "tw-stat",
    "tw-arc",
    "tw-multiples",
}

# fenced tw-* block：```tw-xxx\n …內容… \n```
_FENCE_RE = re.compile(r"```(tw-[a-z]+)[^\n]*\n(.*?)```", re.DOTALL)

# 來源列：來源：… / 資料來源：… / source: …（中英冒號）
_SRC_RE = re.compile(r"(?:資料來源|來源|source)\s*[:：]\s*\S", re.IGNORECASE)

# AI-blind 指示語：如上圖 / 見下圖 / 如圖所示 / 上圖所示 / 下圖顯示 …
_AIBLIND_RE = re.compile(
    r"(?:如|見|參見)(?:上|下|左|右)?圖(?:所示)?"
    r"|(?:上|下)圖(?:所示|顯示|可見|中)"
)

# config 列：單位：… / 過半：… / 欄：… / 基準：… / 基準線：…（v2.0 共通約定）
_CONFIG_RE = re.compile(r"^(?:單位|過半|欄|基準線?)\s*[:：]")

# tw-multiples 群組分隔列
_MULTIPLES_SEP_RE = re.compile(r"^---\s*", re.MULTILINE)

# 數字欄位（含千分位逗號 / 百分號 / 負號 / 強調 `*` 前綴）
_NUMERIC_RE = re.compile(r"^-?[\d,]+(?:\.\d+)?%?$")


def _parse_block(content: str) -> dict[str, Any]:
    """拆解一個 fenced tw-* block 內容成標題／config／來源／資料四類列。

    每類回傳 (相對列號, 內容) tuples；相對列號 = `content.split("\\n")` 的
    0-based index，呼叫端可换算成檔案絕對行號（見 check() 內 content_start_line）。

    分類優先序（跟 v2.0 共通約定一致）：來源列 > config 列 >
    標題列（僅第一個非空列，且無 `|`）> 資料列（其餘含 `|` 的列）。
    沒有 `|` 又不是第一列、也不是 config/來源的行（例如 tw-multiples 的
    `---` 分隔列）不落入任何一類，由呼叫端各自用專屬 regex 處理。
    """
    title: tuple[int, str] | None = None
    config: list[tuple[int, str]] = []
    source: list[tuple[int, str]] = []
    data: list[tuple[int, str]] = []
    seen_content = False
    for idx, raw in enumerate(content.split("\n")):
        line = raw.strip()
        if not line:
            continue
        if _SRC_RE.search(line):
            source.append((idx, line))
            seen_content = True
            continue
        if _CONFIG_RE.match(line):
            config.append((idx, line))
            seen_content = True
            continue
        if "|" not in line:
            if not seen_content:
                title = (idx, line)
            seen_content = True
            continue
        data.append((idx, line))
        seen_content = True
    return {"title": title, "config": config, "source": source, "data": data}


def _cols(line: str) -> int:
    """`|` 分欄後的欄數。"""
    return len(line.split("|"))


def _is_numeric(field: str) -> bool:
    """欄位是否為純數字（容許千分位逗號 / 百分號 / 強調 `*` 前綴）。"""
    f = field.strip()
    if f.startswith("*"):
        f = f[1:].strip()
    return bool(_NUMERIC_RE.match(f))


def _to_float(field: str) -> float | None:
    """欄位轉 float；不是數字回傳 None（呼叫端自行決定要不要略過）。"""
    f = field.strip().rstrip("%").replace(",", "")
    try:
        return float(f)
    except ValueError:
        return None


def check(target: FileTarget, config: dict[str, Any]) -> Iterator[Violation]:
    body = target.body
    if not body.strip():
        return

    # ── A. 資料視覺化模組缺來源 ──────────────────────────────────────────
    for m in _FENCE_RE.finditer(body):
        lang = m.group(1)
        content = m.group(2)
        if lang in _DATA_MODULES and not _SRC_RE.search(content):
            line_no = body[: m.start()].count("\n") + 1
            yield Violation(
                check=CHECK_NAME,
                severity=DEFAULT_SEVERITY,
                message=(
                    f"資料視覺化模組 `{lang}` 缺來源標註 — 在 fenced block 內加一列 "
                    f"`來源：機構，年份`（可信度 + 讓 AI 引用時可追溯來源）。"
                ),
                line=line_no,
                snippet=f"```{lang} …",
                editorial_ref=EDITORIAL_REF,
                fix_suggestion=(
                    "在該 ```"
                    f"{lang}"
                    "``` 區塊內加一列 `來源：…`，會自動渲染成模組下方的來源 caption。"
                ),
            )

    # ── B. 「如上圖／如下圖」AI-blind 指示語 ─────────────────────────────
    masked = target.body_without_protected()
    for line_no, line in enumerate(masked.split("\n"), start=1):
        if not line.strip():
            continue
        m = _AIBLIND_RE.search(line)
        if not m:
            continue
        yield Violation(
            check=CHECK_NAME,
            severity=DEFAULT_SEVERITY,
            message=(
                f"AI 爬蟲讀不到圖：「{m.group(0)}」這種指示語對 GPTBot/PerplexityBot "
                f"/ClaudeBot 無意義（它們看不到圖）。關鍵數值要也寫進 prose。"
            ),
            line=line_no,
            snippet=line.strip()[:90],
            editorial_ref=EDITORIAL_REF,
            fix_suggestion=(
                "把「如上圖」改成具體數值或結論；要指向資料就用「見下表」並把數字"
                "寫進文字，讓 LLM 也提取得到。"
            ),
        )

    # ── C. 結構完整性（graph.md §四 模組語法的幾何限制） ────────────────────
    for m in _FENCE_RE.finditer(body):
        lang = m.group(1)
        content = m.group(2)
        if lang not in _DATA_MODULES:
            continue

        fence_line = body[: m.start()].count("\n") + 1
        content_start_line = body[: m.start(2)].count("\n") + 1
        parsed = _parse_block(content)

        if not parsed["data"]:
            yield Violation(
                check=CHECK_NAME,
                severity=DEFAULT_SEVERITY,
                message=(
                    f"`{lang}` 模組內沒有可解析的資料列 — renderer 會靜默略過或退化"
                    f"成純 code block，讀者只看到空白或原始文字，發布前必修。"
                ),
                line=fence_line,
                snippet=f"```{lang} …",
                editorial_ref=EDITORIAL_REF_SHAPE,
                fix_suggestion=(
                    "檢查每列資料是否都含 `|` 分欄；扣掉標題／config／來源列後，"
                    "至少要留一列真正的資料列。"
                ),
            )
            continue  # 沒資料列，下面的欄數/加總檢查沒意義

        if lang == "tw-slope":
            idx, header = parsed["data"][0]
            cols = _cols(header)
            if cols != 2:
                yield Violation(
                    check=CHECK_NAME,
                    severity=DEFAULT_SEVERITY,
                    message=(
                        f"`tw-slope` 頭列（第一條資料列）{cols} 欄 — 斜率圖需恰兩個"
                        f"時點（graph.md §四）；多於兩點改用 tw-line 呈現完整趨勢。"
                    ),
                    line=content_start_line + idx,
                    snippet=header[:80],
                    editorial_ref=EDITORIAL_REF_SHAPE,
                    fix_suggestion=(
                        "header 列改成 `左時點 | 右時點` 恰兩欄；有 3 個以上時間點"
                        "就改用 tw-line。"
                    ),
                )

        elif lang == "tw-line":
            idx, header = parsed["data"][0]
            series = _cols(header) - 1
            if series > 3:
                yield Violation(
                    check=CHECK_NAME,
                    severity=DEFAULT_SEVERITY,
                    message=(
                        f"`tw-line` {series} 條序列 — 折線圖 >3 序列會互相纏繞、"
                        f"難以辨識（graph.md §四）；拆圖或改用 tw-multiples。"
                    ),
                    line=content_start_line + idx,
                    snippet=header[:80],
                    editorial_ref=EDITORIAL_REF_SHAPE,
                    fix_suggestion=(
                        "序列數精簡到 ≤3；真的要多序列比較就拆成多張圖，或改用 "
                        "tw-multiples 小倍數網格。"
                    ),
                )

        elif lang == "tw-stack":
            idx, header = parsed["data"][0]
            categories = _cols(header) - 1
            if categories > 5:
                yield Violation(
                    check=CHECK_NAME,
                    severity=DEFAULT_SEVERITY,
                    message=(
                        f"`tw-stack` {categories} 個類別 — 堆疊條類別建議 ≤5"
                        f"（graph.md §四），太多段肉眼分不出寬度差。"
                    ),
                    line=content_start_line + idx,
                    snippet=header[:80],
                    editorial_ref=EDITORIAL_REF_SHAPE,
                    fix_suggestion=(
                        "把小類別合併成「其他」；仍 >5 類就改用表格呈現。"
                    ),
                )

        elif lang == "tw-waffle":
            total = 0.0
            any_parsed = False
            for _, row in parsed["data"]:
                fields = row.split("|")
                val = _to_float(fields[-1]) if fields else None
                if val is not None:
                    total += val
                    any_parsed = True
            if any_parsed and not (90 <= total <= 110):
                yield Violation(
                    check=CHECK_NAME,
                    severity=DEFAULT_SEVERITY,
                    message=(
                        f"`tw-waffle` 資料列加總約 {total:.1f} — 方格圖是部分對"
                        f"全體，加總應 ≈100（graph.md §四）；不是組成比例改用 "
                        f"tw-bars。"
                    ),
                    line=fence_line,
                    snippet=f"```{lang} …",
                    editorial_ref=EDITORIAL_REF_SHAPE,
                    fix_suggestion=(
                        "檢查百分比欄加總是否正確（四捨五入誤差在 90–110 內算"
                        "合理）；資料本質不是「組成」就改用 tw-bars。"
                    ),
                )

        elif lang == "tw-pyramid":
            idx, header = parsed["data"][0]
            cols = _cols(header)
            if cols != 3:
                yield Violation(
                    check=CHECK_NAME,
                    severity=DEFAULT_SEVERITY,
                    message=(
                        f"`tw-pyramid` 頭列 {cols} 欄 — 金字塔需『組欄名 | 左名 | "
                        f"右名』恰三欄（graph.md §四）。"
                    ),
                    line=content_start_line + idx,
                    snippet=header[:80],
                    editorial_ref=EDITORIAL_REF_SHAPE,
                    fix_suggestion=(
                        "header 列改成三欄：組欄名｜左側標籤｜右側標籤，左右數值"
                        "才能共用同一把尺對照。"
                    ),
                )

        elif lang == "tw-arc":
            for idx, row in parsed["data"]:
                fields = row.split("|")
                if len(fields) >= 2 and not _is_numeric(fields[1]):
                    yield Violation(
                        check=CHECK_NAME,
                        severity=DEFAULT_SEVERITY,
                        message=(
                            f"`tw-arc` 資料列「{row[:40]}」第二欄非數字 — 席次欄"
                            f"需為數字（graph.md §四 新模組規範）。"
                        ),
                        line=content_start_line + idx,
                        snippet=row[:80],
                        editorial_ref=EDITORIAL_REF_SHAPE,
                        fix_suggestion=(
                            "第二欄改成純數字席次（如 51）；文字註記放第三欄。"
                        ),
                    )

        elif lang == "tw-multiples":
            sep_count = len(_MULTIPLES_SEP_RE.findall(content))
            if sep_count < 3:
                yield Violation(
                    check=CHECK_NAME,
                    severity=DEFAULT_SEVERITY,
                    message=(
                        f"`tw-multiples` 只偵測到 {sep_count} 個群組分隔（`---`）"
                        f"— 小倍數甜蜜點是 3-20 組（graph.md §四）；"
                        f"少於 3 組改 tw-line 多序列或 tw-versus。"
                    ),
                    line=fence_line,
                    snippet=f"```{lang} …",
                    editorial_ref=EDITORIAL_REF_SHAPE,
                    fix_suggestion=(
                        "用 `---` 另起一列分隔至少三組小圖；1-2 組資料改用 "
                        "tw-line 多序列或 tw-versus。"
                    ),
                )
            elif sep_count > 20:
                yield Violation(
                    check=CHECK_NAME,
                    severity=DEFAULT_SEVERITY,
                    message=(
                        f"`tw-multiples` {sep_count} 個群組 — 小倍數 >20 格難以"
                        f"逐格掃視（graph.md §四），先聚合分組再畫。"
                    ),
                    line=fence_line,
                    snippet=f"```{lang} …",
                    editorial_ref=EDITORIAL_REF_SHAPE,
                    fix_suggestion=(
                        "把群組數壓到 ≤20；相近類別先合併，或拆成多張 tw-multiples。"
                    ),
                )
