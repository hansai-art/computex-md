#!/usr/bin/env python3
"""music-media-audit.py — 找 Music / 音樂類 People 條目缺 iframe 的 backlog.

Per EDITORIAL §媒體編織 類型 × 媒體比重 baseline (2026-05-17):
  - 音樂人:        2-3 圖 + 2-3+ 影片
  - 樂團/音樂史:   2-3 圖 + 3-5 影片
  - 運動員/演員:   2-3 圖 + 1-3 影片
  - YouTuber:      2-3 圖 + 2-4 影片
  - Hub 頁:        0 + 0

Output:
  reports/music-media-audit/YYYY-MM-DD.md (human-readable summary)
  reports/music-media-audit/YYYY-MM-DD.json (machine-readable)
  ARTICLE-INBOX append candidate (per --append-inbox flag, observer-gated)

Usage:
  python3 scripts/tools/music-media-audit.py            # scan + write report
  python3 scripts/tools/music-media-audit.py --json     # stdout JSON
  python3 scripts/tools/music-media-audit.py --top 10   # only top 10 gaps
"""

from __future__ import annotations
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = REPO_ROOT / "knowledge"
REPORTS_DIR = REPO_ROOT / "reports" / "music-media-audit"

# Baseline per EDITORIAL §媒體編織 (CJK section anchor:
# 媒體編織圖片與影片穿插的敘事流2026-05-17-新增)
BASELINE = {
    "music_person": {"min": 2, "max": 5, "rationale": "音樂人代表作 / 早期 / 最新三層"},
    "music_topic":  {"min": 3, "max": 5, "rationale": "樂團 / 音樂類型史各時期 anchored 時間軸"},
    "performer":    {"min": 1, "max": 3, "rationale": "運動員 / 演員 / YouTuber 表演關鍵時刻"},
    "youtuber":     {"min": 2, "max": 4, "rationale": "YouTuber / Podcaster 代表節目"},
}

# Subcategory → tier classifier
MUSIC_PERSON_SUBCATS = {
    "音樂", "音樂人", "音樂與表演", "流行音樂", "獨立音樂", "原住民音樂",
    "古典音樂", "搖滾", "民歌", "嘻哈",
}
PERFORMER_SUBCATS = {
    "演員", "演員與表演", "表演", "戲劇", "影視",
    "運動", "運動員", "棒球", "羽球", "舉重", "桌球", "拳擊", "電競",
    "綜藝", "主持",
}
YOUTUBER_SUBCATS = {"YouTuber", "創作者", "網紅", "Podcaster"}

# Hub pages (don't audit)
EXCLUDE_FILE_PREFIXES = ("_",)


def parse_frontmatter(text: str) -> dict:
    """Lightweight frontmatter parser (no yaml dep)."""
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end < 0:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
            val = val[1:-1]
        fm[key] = val
    return fm


def count_video_embeds(text: str) -> int:
    """Count <div class="video-embed"> blocks."""
    return len(re.findall(r'class="video-embed"', text))


def count_inline_youtube_links(text: str) -> int:
    """Count markdown links to YouTube (legacy convention before iframe upgrade)."""
    return len(re.findall(r'\]\(https?://(?:www\.)?(?:youtube\.com/watch|youtu\.be/)', text))


def count_images(text: str) -> int:
    """Count markdown image references (rough — includes hero + inline)."""
    return len(re.findall(r'!\[[^\]]*\]\([^)]+\)', text))


def classify_tier(file_path: Path, fm: dict) -> str | None:
    """Decide which baseline tier applies. None = skip (not music-related)."""
    rel = str(file_path.relative_to(REPO_ROOT))
    subcat = fm.get("subcategory", "")

    # Music/ directory → music topic articles
    if rel.startswith("knowledge/Music/"):
        return "music_topic"

    # People/ directory → classify by subcategory
    if rel.startswith("knowledge/People/"):
        for s in MUSIC_PERSON_SUBCATS:
            if s in subcat:
                return "music_person"
        for s in YOUTUBER_SUBCATS:
            if s in subcat:
                return "youtuber"
        for s in PERFORMER_SUBCATS:
            if s in subcat:
                return "performer"

    return None  # not audited


def audit_file(file_path: Path) -> dict | None:
    """Audit a single file. Returns dict or None if not audited."""
    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception:
        return None

    fm = parse_frontmatter(text)
    tier = classify_tier(file_path, fm)
    if tier is None:
        return None

    iframe_count = count_video_embeds(text)
    yt_link_count = count_inline_youtube_links(text)
    image_count = count_images(text)

    baseline = BASELINE[tier]
    gap = max(0, baseline["min"] - iframe_count)

    return {
        "path": str(file_path.relative_to(REPO_ROOT)),
        "slug": file_path.stem,
        "category": file_path.parent.name,
        "subcategory": fm.get("subcategory", ""),
        "title": fm.get("title", "")[:80],
        "tier": tier,
        "iframe_count": iframe_count,
        "yt_link_count": yt_link_count,
        "image_count": image_count,
        "baseline_min": baseline["min"],
        "baseline_max": baseline["max"],
        "gap": gap,
        "rationale": baseline["rationale"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="emit JSON only to stdout")
    ap.add_argument("--top", type=int, default=0, help="cap output to top N gaps")
    ap.add_argument("--no-write", action="store_true", help="don't write report files")
    args = ap.parse_args()

    candidates = []
    for cat_dir in ("Music", "People"):
        d = KNOWLEDGE_DIR / cat_dir
        if not d.exists():
            continue
        for md in d.glob("*.md"):
            if md.name.startswith(EXCLUDE_FILE_PREFIXES):
                continue
            result = audit_file(md)
            if result:
                candidates.append(result)

    # Sort by gap descending, then by alphabetical
    candidates.sort(key=lambda r: (-r["gap"], r["path"]))

    # Stats
    total = len(candidates)
    gap_files = [c for c in candidates if c["gap"] > 0]
    at_baseline = [c for c in candidates if c["gap"] == 0 and c["iframe_count"] >= c["baseline_min"]]
    over_baseline = [c for c in candidates if c["iframe_count"] > c["baseline_max"]]

    summary = {
        "generated": datetime.now().isoformat(),
        "baseline_canonical": "docs/editorial/EDITORIAL.md#媒體編織",
        "total_audited": total,
        "needs_heal": len(gap_files),
        "at_baseline": len(at_baseline),
        "over_baseline": len(over_baseline),
        "by_tier": {
            tier: sum(1 for c in candidates if c["tier"] == tier and c["gap"] > 0)
            for tier in BASELINE
        },
    }

    if args.top:
        candidates = candidates[:args.top]

    output = {"summary": summary, "candidates": candidates}

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    # Print human-readable + optionally write
    print(f"🎵 music-media-audit @ {summary['generated'][:19]}", file=sys.stderr)
    print(f"   total: {total} / needs heal: {summary['needs_heal']} / at baseline: {summary['at_baseline']}", file=sys.stderr)
    print(f"   by tier: {summary['by_tier']}", file=sys.stderr)
    print(file=sys.stderr)
    print(f"{'gap':>4} {'iframe':>6} {'links':>5} {'imgs':>4} {'tier':<14} path", file=sys.stderr)
    for c in candidates[:30]:
        print(f"{c['gap']:>4} {c['iframe_count']:>6} {c['yt_link_count']:>5} {c['image_count']:>4} {c['tier']:<14} {c['path']}", file=sys.stderr)

    if not args.no_write:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")

        # JSON
        json_path = REPORTS_DIR / f"{date_str}.json"
        json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")

        # Markdown
        md_path = REPORTS_DIR / f"{date_str}.md"
        lines = [
            f"# Music Media Audit — {date_str}",
            "",
            f"Per EDITORIAL §媒體編織 baseline (2026-05-17). 自動 cron: twmd-music-media-audit-weekly.",
            "",
            "## Summary",
            "",
            f"- **Total audited**: {summary['total_audited']}",
            f"- **Needs heal** (iframe < baseline_min): {summary['needs_heal']}",
            f"- **At baseline**: {summary['at_baseline']}",
            f"- **Over baseline** (iframe > baseline_max): {summary['over_baseline']}",
            "",
            "### By tier",
            "",
        ]
        for tier, count in summary['by_tier'].items():
            lines.append(f"- `{tier}`: {count} need heal")
        lines.extend(["", "## Heal Candidates (sorted by gap desc)", "", "| Gap | iframe | YT-link | Imgs | Tier | Path | Title |", "|---|---|---|---|---|---|---|"])
        for c in candidates:
            lines.append(
                f"| {c['gap']} | {c['iframe_count']} | {c['yt_link_count']} | {c['image_count']} "
                f"| `{c['tier']}` | `{c['path']}` | {c['title']} |"
            )
        lines.extend([
            "",
            "## Suggested heal batch (next session manual pick)",
            "",
            "1. Pick top 3-5 high-traffic articles from `gap >= 2` rows",
            "2. For each: WebSearch + WebFetch verify Official MV URLs (per REWRITE Step 4.3.6)",
            "3. Insert iframe + italic caption sample sentence",
            "4. Run preview_eval to verify rendering",
            "5. Commit as batch heal `🧬 [semiont] heal: N 條 Music 條目補 iframe`",
            "",
            "Notes:",
            "",
            "- `yt-link` column shows existing inline YouTube markdown links (legacy convention). High link count + 0 iframe = candidate for upgrade rather than greenfield.",
            "- `Imgs` count includes hero + inline. Articles with 0 images AND 0 iframe are deeper heal candidates (missing both layers).",
            "- Tier `music_person`: 音樂人 (流行音樂 / 獨立音樂 / 原住民音樂 / 古典音樂 subcategory)",
            "- Tier `music_topic`: knowledge/Music/ 全部 (樂團 / 音樂類型史 / 文化現象)",
            "- Tier `performer`: 演員 / 運動員 / 戲劇 subcategory under People/",
            "- Tier `youtuber`: YouTuber / Podcaster / 創作者 subcategory under People/",
            "",
        ])
        md_path.write_text("\n".join(lines))
        print(f"   ✅ wrote {json_path.relative_to(REPO_ROOT)}", file=sys.stderr)
        print(f"   ✅ wrote {md_path.relative_to(REPO_ROOT)}", file=sys.stderr)


if __name__ == "__main__":
    main()
