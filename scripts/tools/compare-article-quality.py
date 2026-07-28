#!/usr/bin/env python3
"""Compare one Rewrite Pipeline result with recent zh-TW article changes.

The comparison deliberately uses the same article-health dashboard profile for
every file, then adds transparent structural densities. It is evidence, not an
LLM vibe score.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def recent_articles(target: str, limit: int) -> list[str]:
    proc = subprocess.run(
        ["git", "log", "--since=30 days ago", "--diff-filter=AM", "--name-only", "--pretty=format:", "--", "knowledge"],
        cwd=ROOT, text=True, capture_output=True, check=True,
    )
    seen: set[str] = set()
    found: list[str] = []
    for raw in proc.stdout.splitlines():
        path = raw.strip()
        if not path or path in seen or path == target:
            continue
        if not re.match(r"^knowledge/[^/]+/[^/]+\.md$", path):
            continue
        if path.endswith(" Hub.md") or not (ROOT / path).exists():
            continue
        seen.add(path)
        found.append(path)
        if len(found) >= limit:
            break
    return found


def metrics(path: str) -> dict[str, object]:
    body = (ROOT / path).read_text(encoding="utf-8")
    health = subprocess.run(
        [sys.executable, "scripts/tools/article-health.py", path, "--profile=dashboard", "--output=json"],
        cwd=ROOT, text=True, capture_output=True, check=True,
    )
    report = json.loads(health.stdout)["reports"][0]
    summary = report["summary"]
    prose_warn = 0
    for result in report["results"]:
        if result["check"] == "prose-health":
            prose_warn = sum(v["severity"] == "warn" for v in result["violations"])
    prose = re.sub(r"^---[\s\S]*?---\s*", "", body, count=1)
    prose = re.split(r"\n## 參考資料\s*\n", prose, maxsplit=1)[0]
    prose = re.sub(r"(?m)^\[\^[^\]]+\]:.*$", "", prose)
    cjk = len(re.findall(r"[\u3400-\u9fff]", prose))
    footnotes = len(re.findall(r"(?m)^\[\^[^\]]+\]:", body))
    media = len(re.findall(r"!\[[^\]]*\]\(", body)) + len(re.findall(r"<iframe\b", body))
    if re.search(r"(?m)^image:\s*['\"]?\S+", body):
        media += 1
    scale = max(cjk / 1000, 1)
    return {
        "file": path,
        "cjk": cjk,
        "hard": summary["hard"],
        "warn": summary["warn"],
        "info": summary["info"],
        "prose_warn": prose_warn,
        "footnotes": footnotes,
        "media": media,
        "footnotes_per_1k": round(footnotes / scale, 2),
        "media_per_1k": round(media / scale, 2),
        "warn_per_1k": round(summary["warn"] / scale, 2),
    }


def median(rows: list[dict[str, object]], key: str) -> float:
    return round(statistics.median(float(row[key]) for row in rows), 2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    target = str(Path(args.target))
    comparators = recent_articles(target, args.limit)
    if len(comparators) < 3:
        raise SystemExit(f"need at least 3 recent comparator articles, found {len(comparators)}")
    target_row = metrics(target)
    recent_rows = [metrics(path) for path in comparators]
    keys = ["cjk", "hard", "warn", "prose_warn", "footnotes_per_1k", "media_per_1k", "warn_per_1k"]
    medians = {key: median(recent_rows, key) for key in keys}

    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"target": target_row, "recent": recent_rows, "recent_median": medians}
    output.with_suffix(".json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Rewrite Pipeline 品質比較",
        "",
        f"- 目標：`{target}`",
        f"- 對照：最近 {len(recent_rows)} 篇 zh-TW 文章變更",
        "- 方法：同一個 `article-health --profile=dashboard` 加上可重算的字數／腳註／媒體密度；不使用主觀 LLM 分數。",
        "",
        "| 指標 | 本次產出 | 近期中位數 |",
        "| --- | ---: | ---: |",
    ]
    labels = {
        "cjk": "CJK 字數",
        "hard": "HARD 違規",
        "warn": "WARN 總數",
        "prose_warn": "文體 WARN",
        "footnotes_per_1k": "每千字腳註",
        "media_per_1k": "每千字媒體",
        "warn_per_1k": "每千字 WARN",
    }
    for key in keys:
        lines.append(f"| {labels[key]} | {target_row[key]} | {medians[key]} |")
    lines.extend(["", "## 對照文章", ""])
    lines.extend(f"- `{row['file']}`" for row in recent_rows)
    lines.extend([
        "",
        "## 判讀",
        "",
        f"- 硬閘：{'通過' if target_row['hard'] == 0 else '未通過'}（HARD={target_row['hard']}）。",
        f"- 文體警訊：本次 {target_row['prose_warn']}，近期中位數 {medians['prose_warn']}。",
        f"- 溯源密度：本次每千字 {target_row['footnotes_per_1k']} 個腳註，近期中位數 {medians['footnotes_per_1k']}。",
        f"- 媒體密度：本次每千字 {target_row['media_per_1k']} 個媒體，近期中位數 {medians['media_per_1k']}。",
        "",
    ])
    output.write_text("\n".join(lines), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
