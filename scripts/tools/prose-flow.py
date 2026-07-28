#!/usr/bin/env python3
"""prose-flow.py — REWRITE-PIPELINE Step 3.6.2「順稿」量測儀器

誕生背景（2026-07-25 外送專法 ship 後）：觀察者讀完 callout「文段太長、閱讀順暢感
掉了、後段幾乎沒有資訊圖表」。事後量測證實：後半 16 段裡有 9 段 ≥200 字，且全篇
資料最密的那一節 viz 掛零。但當時所有儀器都是綠的——`paragraph-rhythm` 的牆門檻是
單段 >280 字，那 9 段落在 200-275 全部合格；`viz-health` 只數模組總數不看分布。

這支工具不是新造一套 prose 判定，是把 `article_health.checks.paragraph_rhythm`
既有的段落切分/分類邏輯（`_strip_for_prose_analysis` / `_is_prose_block` /
`_extract_h2_sections` / `_split_paragraphs`）接上「逐節」視角 + 兩個新門檻
（長段 ≥200 字 / viz 分布），抓 paragraph-rhythm（全篇單段門檻 280、不分節）
和 viz-health（只數總數、不看分布）中間那格空隙。

用法:
  python3 scripts/tools/prose-flow.py knowledge/Society/外送專法.md
  python3 scripts/tools/prose-flow.py knowledge/Society/外送專法.md --json
  python3 scripts/tools/prose-flow.py knowledge/Society/外送專法.md --strict

診斷工具，非 hard gate：預設一律 exit 0。--strict 時任一訊號亮才 exit 1。
stdlib-only（沿用 paragraph_rhythm 邏輯用 import，不重造一套判定）。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from statistics import median
from typing import Any

# ── 沿用既有 prose 判定邏輯，不另造一套（避免兩套尺漂移）──
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from article_health.checks import paragraph_rhythm as pr  # noqa: E402

LONG_PARA_CJK = 200  # 長段/牆門檻（本工具的存在理由——paragraph-rhythm 280 門檻漏掉
# 200-275 字這個窒息區間；2026-07-25 外送專法順稿前 9 段就落在這裡）
LONG_PARA_DENSITY_WARN = 0.4  # 任一節 ≥200 字段落 > 40% = 長段密度訊號
VIZ_GAP_STREAK_WARN = 3  # 連續 ≥3 節 0 viz = viz 空白帶訊號
BOILERPLATE_TITLE_RE = re.compile(
    r"^(參考資料|延伸閱讀|圖片來源|參考文獻|影片素材|影片來源)"
)


def _truncate_title(title: str, n: int = 24) -> str:
    return title if len(title) <= n else title[: n - 1] + "…"


def _analyze_section(raw_section_body: str) -> dict[str, Any]:
    """單一 H2 節（或前言）的 prose / viz / media 統計。

    raw_section_body 是「只去掉 frontmatter，保留 code fence / 圖片 / iframe」的
    原始節內文——先在這層數 viz / media，再對它跑 `_strip_for_prose_analysis`
    去拿乾淨的 prose 段落（跟 paragraph_rhythm.check() 同一套流程，只是切到
    節內而非全篇跑一次）。
    """
    viz_count = len(pr._RE_TW_MODULE.findall(raw_section_body))
    media_count = len(pr._RE_IMAGE_MD.findall(raw_section_body)) + len(
        pr._RE_IFRAME.findall(raw_section_body)
    )

    prose_body = pr._strip_for_prose_analysis(raw_section_body)
    paragraphs = pr._split_paragraphs(prose_body)
    prose_paragraphs = [p for p in paragraphs if pr._is_prose_block(p)]
    cjk_list = [pr._count_cjk(p) for p in prose_paragraphs]

    prose_count = len(cjk_list)
    longest = max(cjk_list) if cjk_list else 0
    median_cjk = int(median(cjk_list)) if cjk_list else 0
    long_count = sum(1 for c in cjk_list if c >= LONG_PARA_CJK)
    long_pct = (long_count / prose_count) if prose_count else 0.0

    return dict(
        prose_count=prose_count,
        longest_cjk=longest,
        median_cjk=median_cjk,
        long_count=long_count,
        long_pct=long_pct,
        viz_count=viz_count,
        media_count=media_count,
        cjk_list=cjk_list,
    )


def analyze(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    raw_body = pr._RE_FRONTMATTER.sub("", text)

    rows: list[dict[str, Any]] = []

    # 前言（第一個 H2 之前）— 跟 paragraph_rhythm 的 [lead] 對齊
    first_h2 = re.search(r"^##\s+(?!#)", raw_body, flags=re.MULTILINE)
    lead_raw = raw_body[: first_h2.start()] if first_h2 else raw_body
    lead_stats = _analyze_section(lead_raw)
    if lead_stats["prose_count"] or lead_stats["viz_count"] or lead_stats["media_count"]:
        rows.append(dict(title="[前言]", **lead_stats))

    for title, section_raw_body in pr._extract_h2_sections(raw_body):
        if BOILERPLATE_TITLE_RE.match(title):
            continue  # 延伸閱讀／參考資料／圖片來源 不是 prose 內容節，排除避免稀釋分布訊號
        stats = _analyze_section(section_raw_body)
        rows.append(dict(title=title, **stats))

    # ── 全篇 pooled 統計 ──
    all_cjk: list[int] = []
    for r in rows:
        all_cjk.extend(r["cjk_list"])
    total_prose = len(all_cjk)
    overall_median = int(median(all_cjk)) if all_cjk else 0
    overall_longest = max(all_cjk) if all_cjk else 0
    wall_count = sum(1 for c in all_cjk if c >= LONG_PARA_CJK)
    viz_total = sum(r["viz_count"] for r in rows)
    viz_empty_titles = [r["title"] for r in rows if r["viz_count"] == 0]

    # 連續 0 viz 最長串（依節序，含前言）
    longest_streak = 0
    cur_streak = 0
    for r in rows:
        if r["viz_count"] == 0:
            cur_streak += 1
            longest_streak = max(longest_streak, cur_streak)
        else:
            cur_streak = 0

    # ── 三個 WARN 訊號 ──
    long_density_hits = [
        (r["title"], r["long_count"], r["prose_count"], r["long_pct"])
        for r in rows
        if r["prose_count"] > 0 and r["long_pct"] > LONG_PARA_DENSITY_WARN
    ]
    signal_long_density = bool(long_density_hits)

    signal_viz_gap = longest_streak >= VIZ_GAP_STREAK_WARN

    n = len(rows)
    tail_n = max(1, n // 3) if n else 0
    tail_rows = rows[n - tail_n :] if n else []
    tail_viz_total = sum(r["viz_count"] for r in tail_rows)
    signal_back_desert = bool(tail_rows) and tail_viz_total == 0

    return dict(
        rows=rows,
        summary=dict(
            total_prose=total_prose,
            overall_median=overall_median,
            overall_longest=overall_longest,
            wall_count=wall_count,
            viz_total=viz_total,
            viz_empty_titles=viz_empty_titles,
            longest_viz_empty_streak=longest_streak,
        ),
        signals=dict(
            long_para_density=dict(
                fired=signal_long_density,
                sections=[
                    dict(title=t, long_count=lc, prose_count=pc, pct=round(pct, 2))
                    for t, lc, pc, pct in long_density_hits
                ],
            ),
            viz_gap=dict(fired=signal_viz_gap, max_streak=longest_streak),
            back_third_desert=dict(
                fired=signal_back_desert,
                tail_section_count=tail_n,
                tail_titles=[r["title"] for r in tail_rows],
                viz_in_tail=tail_viz_total,
            ),
        ),
    )


def _print_report(path: Path, result: dict[str, Any]) -> None:
    rows = result["rows"]
    summary = result["summary"]
    signals = result["signals"]

    print(f"📖 prose-flow  {path}")
    if not rows:
        print("   （沒有偵測到任何 H2 內容節，無法量測）")
    else:
        print(
            f"   {'節':<26}{'prose':>6}{'最長':>6}{'median':>7}{'長段(≥200)':>12}{'viz':>5}{'media':>7}"
        )
        for r in rows:
            title = _truncate_title(r["title"])
            long_ratio = (
                f"{r['long_count']}/{r['prose_count']}={r['long_pct']*100:.0f}%"
                if r["prose_count"]
                else "-"
            )
            print(
                f"   {title:<26}{r['prose_count']:>6}{r['longest_cjk']:>6}"
                f"{r['median_cjk']:>7}{long_ratio:>12}{r['viz_count']:>5}{r['media_count']:>7}"
            )

    print("\n   ── 全篇 summary ──")
    print(f"   總 prose 段數：{summary['total_prose']}")
    print(f"   全篇 median：{summary['overall_median']} 字")
    print(f"   全篇最長：{summary['overall_longest']} 字")
    print(f"   長段/牆 (≥{LONG_PARA_CJK} 字) 總數：{summary['wall_count']}")
    print(f"   viz 總數：{summary['viz_total']}")
    empty = "、".join(summary["viz_empty_titles"]) if summary["viz_empty_titles"] else "無"
    print(f"   viz 空白節：{empty}")
    print(f"   連續 0 viz 最長串：{summary['longest_viz_empty_streak']} 節")

    print("\n   ── 訊號（WARN 級，不 hard fail）──")
    ld = signals["long_para_density"]
    if ld["fired"]:
        names = "；".join(
            f"§{s['title']} {s['long_count']}/{s['prose_count']}={s['pct']*100:.0f}%"
            for s in ld["sections"]
        )
        print(f"   ⚠️  長段密度：{names}")
    else:
        print("   ✅ 長段密度：無節超過 40%")

    vg = signals["viz_gap"]
    if vg["fired"]:
        print(f"   ⚠️  viz 空白帶：連續 {vg['max_streak']} 節 0 viz（門檻 {VIZ_GAP_STREAK_WARN}）")
    else:
        print(f"   ✅ viz 空白帶：最長連續 {vg['max_streak']} 節，未達門檻 {VIZ_GAP_STREAK_WARN}")

    bd = signals["back_third_desert"]
    if bd["fired"]:
        tails = "、".join(bd["tail_titles"])
        print(f"   ⚠️  後段荒漠：後 1/3（{bd['tail_section_count']} 節：{tails}）viz 總數為 0")
    else:
        print(
            f"   ✅ 後段荒漠：後 1/3（{bd['tail_section_count']} 節）viz 總數 "
            f"{bd['viz_in_tail']}，未觸發"
        )

    fired = sum([ld["fired"], vg["fired"], bd["fired"]])
    print(f"\n   Summary: {fired}/3 訊號亮起")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true")
    ap.add_argument(
        "--strict", action="store_true", help="任一訊號亮起則 exit 1（預設一律 exit 0）"
    )
    args = ap.parse_args()

    p = Path(args.file)
    if not p.exists():
        print(f"❌ 找不到檔案：{p}", file=sys.stderr)
        sys.exit(0)

    if not pr._is_applicable_path(str(p)):
        msg = f"⏭️  {p} 不適用（非 zh-TW knowledge 正文 / hub 頁 / spore / report）"
        if args.json:
            print(json.dumps(dict(file=str(p), applicable=False, message=msg), ensure_ascii=False))
        else:
            print(msg)
        sys.exit(0)

    result = analyze(p)
    any_fired = any(s["fired"] for s in result["signals"].values())

    if args.json:
        # cjk_list 是內部中間值，JSON 輸出精簡掉，避免膨脹又跟 rows 其他欄位重複語意
        rows_out = [{k: v for k, v in r.items() if k != "cjk_list"} for r in result["rows"]]
        out = dict(
            file=str(p),
            applicable=True,
            sections=rows_out,
            summary=result["summary"],
            signals=result["signals"],
            any_signal_fired=any_fired,
        )
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        _print_report(p, result)

    if args.strict and any_fired:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
