#!/usr/bin/env python3
"""editorial-room-health.py — schema gate for editorial room review reports.

Usage:
  python3 scripts/tools/editorial-room-health.py reports/editorial-room/foo-projection-review.md
  python3 scripts/tools/editorial-room-health.py reports/editorial-room/ --all

Exit 0 = pass, 2 = fail.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

VALID_OVERALL = {"pass", "revise", "block"}
VALID_VERDICT = {"pass", "revise", "block"}


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    block = text[3:end]
    out: dict[str, str] = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip().strip("\"'")
    return out


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    if len(text.encode("utf-8")) < 400:
        errors.append("file too small (<400 bytes) — likely empty stub")

    fm = parse_frontmatter(text)
    for key in ("slug", "room", "date", "overall"):
        if key not in fm:
            errors.append(f"frontmatter missing: {key}")
    if fm.get("overall") and fm["overall"] not in VALID_OVERALL:
        errors.append(f"overall must be pass|revise|block, got {fm.get('overall')!r}")
    room = fm.get("room", "")
    if room and room not in ("projection", "prose-structure", "chief"):
        errors.append(f"room must be projection|prose-structure|chief, got {room!r}")

    # seat verdicts
    seat_blocks = re.findall(
        r"^### .+\n- verdict:\s*(\w+)",
        text,
        flags=re.MULTILINE,
    )
    if len(seat_blocks) < 1:
        # also allow ## 各席 / nested
        seat_blocks = re.findall(r"verdict:\s*(pass|revise|block)", text, flags=re.I)
    if len(seat_blocks) < 1:
        errors.append("no seat verdict: lines found (expect `- verdict: pass|revise|block`)")
    for v in seat_blocks:
        if v.lower() not in VALID_VERDICT:
            errors.append(f"invalid verdict: {v!r}")

    # required sections
    for heading in ("必改清單", "主編"):
        if heading not in text:
            # 主編裁决 variants
            if heading == "主編" and ("裁決" in text or "主編裁決" in text or "overall" in fm):
                continue
            if heading == "必改清單" and "必改" not in text:
                errors.append(f"missing section containing: {heading}")

    # must-fix count heuristic
    must = re.search(r"## 必改清單.*?\n((?:.*\n)*?)(?:## |\Z)", text)
    if must:
        items = re.findall(r"^\s*\d+\.|^-\s+", must.group(1), flags=re.M)
        if len(items) > 7:
            errors.append(f"必改清單 has {len(items)} items (>7 hard max)")

    # overall consistency: any block seat → overall should be block
    if fm.get("overall") == "pass":
        for v in seat_blocks:
            if v.lower() == "block":
                errors.append("overall=pass but a seat verdict is block")
                break

    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: editorial-room-health.py <file.md>|--all <dir>", file=sys.stderr)
        return 2
    paths: list[Path] = []
    if sys.argv[1] == "--all":
        root = Path(sys.argv[2] if len(sys.argv) > 2 else "reports/editorial-room")
        paths = sorted(root.glob("*-review.md"))
    else:
        paths = [Path(sys.argv[1])]

    failed = 0
    for p in paths:
        if not p.is_file():
            print(f"❌ {p}: not a file")
            failed += 1
            continue
        errs = check_file(p)
        if errs:
            print(f"❌ {p}")
            for e in errs:
                print(f"   - {e}")
            failed += 1
        else:
            print(f"✅ {p}")
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
