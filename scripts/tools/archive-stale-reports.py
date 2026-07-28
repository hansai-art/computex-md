#!/usr/bin/env python3
"""
archive-stale-reports.py — quarterly archive stale top-level reports/*.md

掃 reports/*.md 頂層，把 N+ 天無 reference 的舊檔 git mv 到
reports/archive/{YYYY-Q}/ ，per reports-archival-audit-2026-05-27.md Layer 4。

「無 reference」= grep 全 repo（不含 .git / node_modules / dist / .claude/worktrees /
reports/archive 自身）找不到指向該檔的 markdown link / wikilink / raw filename。

Default: dry-run。需要實際移動加 --apply。

Usage:
    # 預覽 90+ 天的 stale 候選（預設 threshold）
    python3 scripts/tools/archive-stale-reports.py

    # 改 threshold + 預覽
    python3 scripts/tools/archive-stale-reports.py --threshold-days=120

    # 實際執行（git mv）
    python3 scripts/tools/archive-stale-reports.py --apply

    # 指定 archive target quarter
    python3 scripts/tools/archive-stale-reports.py --apply --target=reports/archive/2026-Q2

設計原則:
- 保留 git history (用 git mv 不是 rm)
- 不刪內容 (per REFLEXES #22 raw 永遠不刪)
- Dry-run 為 default，避免 cron 誤觸大批 archive
- INDEX 標題 / 圖片標題 不算 reference (因為 INDEX.md 自身被 regen)

SSOT: reports/reports-archival-audit-2026-05-27.md §4 Layer 4
觸發: docs/semiont/ROUTINE.md twmd-quarterly-archive (待加 cron)
"""

from __future__ import annotations

import argparse
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# 不掃 reference 的位置 (避免循環:
#   - reports/archive/* 已歸檔不算 active reference
#   - .claude/worktrees/* worktree clone 不算
#   - INDEX.md 是 derived，不算 reference)
EXCLUDE_REF_PATHS = (
    ".git", "node_modules", "dist", ".astro",
    ".claude/worktrees",
    "reports/archive",
    "reports/INDEX.md",
)


def find_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    )
    return Path(result.stdout.strip())


def get_quarter(date: datetime) -> str:
    """Convert datetime → YYYY-QN string."""
    quarter = (date.month - 1) // 3 + 1
    return f"{date.year}-Q{quarter}"


def file_age_days(filepath: Path) -> int:
    """Use git log to get last commit mtime; fallback to filesystem mtime."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%at", "--", str(filepath)],
            capture_output=True, text=True, check=True,
        )
        timestamp_str = result.stdout.strip()
        if timestamp_str:
            mtime = datetime.fromtimestamp(int(timestamp_str))
            return (datetime.now() - mtime).days
    except (subprocess.CalledProcessError, ValueError):
        pass
    # Fallback: filesystem mtime
    mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
    return (datetime.now() - mtime).days


def count_references(filename_stem: str, repo_root: Path) -> int:
    """Count places in repo that reference this filename (excluding self + archive)."""
    # grep for filename (stem with .md, OR bare stem in markdown link / wikilink)
    patterns = [
        f"{filename_stem}.md",
        f"[[{filename_stem}]]",
    ]
    total_count = 0
    for pattern in patterns:
        try:
            # Use `grep -rln --exclude-dir=` (BSD grep on macOS supports this)
            cmd = ["grep", "-rln", "--include=*.md", "--include=*.sh", "--include=*.py"]
            for path in EXCLUDE_REF_PATHS:
                cmd.append(f"--exclude-dir={Path(path).name}")
            cmd.append(pattern)
            cmd.append(str(repo_root))
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.stdout.strip():
                # Filter out self-reference (the file itself) + excluded paths
                lines = []
                for line in result.stdout.strip().split("\n"):
                    if any(excl in line for excl in EXCLUDE_REF_PATHS):
                        continue
                    if line.endswith(f"/{filename_stem}.md"):
                        continue  # self-reference
                    lines.append(line)
                total_count += len(lines)
        except subprocess.CalledProcessError:
            continue
    return total_count


def scan_stale(reports_dir: Path, threshold_days: int, repo_root: Path) -> list[dict]:
    """Return list of stale candidate dicts: {filepath, age_days, ref_count}."""
    candidates = []
    for filepath in sorted(reports_dir.glob("*.md")):
        if filepath.name == "INDEX.md":
            continue
        age = file_age_days(filepath)
        if age < threshold_days:
            continue
        refs = count_references(filepath.stem, repo_root)
        if refs > 0:
            continue  # 有活的 reference 不歸檔
        candidates.append({
            "filepath": filepath,
            "age_days": age,
            "ref_count": refs,
        })
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--threshold-days", type=int, default=90,
        help="Archive files older than N days with 0 active references (default: 90)",
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Actually git mv files (default is dry-run)",
    )
    parser.add_argument(
        "--target", type=str, default=None,
        help="Target archive dir (default: reports/archive/{current-quarter})",
    )
    args = parser.parse_args()

    repo_root = find_repo_root()
    reports_dir = repo_root / "reports"
    target_dir = (
        Path(args.target) if args.target
        else reports_dir / "archive" / get_quarter(datetime.now())
    )
    if not target_dir.is_absolute():
        target_dir = repo_root / target_dir

    print(f"🔍 Scanning {reports_dir.relative_to(repo_root)}/*.md ...")
    print(f"   Threshold: {args.threshold_days}+ days old AND 0 references")
    print(f"   Target archive: {target_dir.relative_to(repo_root)}")
    print(f"   Mode: {'APPLY (git mv)' if args.apply else 'DRY-RUN (no changes)'}")
    print()

    candidates = scan_stale(reports_dir, args.threshold_days, repo_root)

    if not candidates:
        print("✅ No stale candidates found.")
        return 0

    print(f"📋 {len(candidates)} stale candidate(s):")
    print()
    for cand in candidates:
        rel = cand["filepath"].relative_to(repo_root)
        print(f"   {cand['age_days']:4d}d / {cand['ref_count']} refs   {rel}")
    print()

    if not args.apply:
        print(f"💡 Dry-run only. Re-run with --apply to git mv {len(candidates)} files.")
        return 0

    # Apply
    target_dir.mkdir(parents=True, exist_ok=True)
    for cand in candidates:
        src = cand["filepath"]
        dst = target_dir / src.name
        try:
            subprocess.run(["git", "mv", str(src), str(dst)], check=True)
            print(f"   ✓ {src.relative_to(repo_root)} → {dst.relative_to(repo_root)}")
        except subprocess.CalledProcessError as exc:
            print(f"   ✗ Failed to mv {src.name}: {exc}")
    print()
    print(f"✅ Archived {len(candidates)} files to {target_dir.relative_to(repo_root)}/")
    print(f"💡 Next: git commit + git push origin main (per ROUTINE main-direct)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
