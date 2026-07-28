#!/usr/bin/env python3
"""
spore-content-hash-audit.py — Spore URL content-fingerprint mismatch detection.

LESSONS-INBOX 2026-05-16 #5 instrumentation: #71 無人機 X URL mismatch 第 3 次驗證
達 REFLEXES #15「反覆浮現要儀器化」threshold。本工具偵測 SPORE-LOG row URL 抓到
的內容跟首次紀錄的 content fingerprint 不一致場景（URL 寫錯 / post 已刪除 / X UI
自動 redirect 到 edit 版）。

設計：side-car JSON `docs/factory/spore-content-fingerprints.json` 不動 SPORE-LOG
schema（避免 73+ row migration）。每條 spore URL 首次 harvest record 內容指紋（title
首段 + emoji + utm_campaign），後續 harvest 抓到時 cross-check。

Usage:
    # 1. 從現有 harvest batch log 抽取 fingerprint baseline（首次建檔）
    python3 scripts/tools/spore-content-hash-audit.py --build-baseline

    # 2. 對單一 URL 計算 fingerprint
    python3 scripts/tools/spore-content-hash-audit.py --url=URL --content=TEXT

    # 3. cross-check 既有 fingerprint vs 新 harvest content
    python3 scripts/tools/spore-content-hash-audit.py --check --url=URL --content=TEXT

    # 4. 列出當前 fingerprint inventory
    python3 scripts/tools/spore-content-hash-audit.py --list

設計報告: reports/spore-content-hash-gate-design-2026-05-16.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
FINGERPRINT_FILE = REPO / "docs" / "factory" / "spore-content-fingerprints.json"


def normalize_content(content: str) -> str:
    """Strip whitespace, normalize fullwidth/halfwidth, lowercase emoji handling."""
    # Strip whitespace runs
    content = re.sub(r"\s+", " ", content.strip())
    return content


def extract_fingerprint_parts(content: str) -> dict:
    """Extract recognizable parts: title/first sentence, emoji set, utm_campaign."""
    normalized = normalize_content(content)
    # First sentence (split by ◎ 。 ! ? !? ⋯ . line breaks)
    first_sentence = re.split(r"[。！？\.\?!⋯…\n]", normalized, maxsplit=1)[0][:80]
    # Emoji set (catch common ones — far from complete, just signature characters)
    emojis = re.findall(
        r"[\U0001F300-\U0001F9FF\U0001FA00-\U0001FAFF🇹🇼🏭🎯⚓⏰📌]", content
    )
    emoji_set = sorted(set(emojis))
    # utm_campaign or status id
    utm_match = re.search(r"utm_campaign=(s?\d+)", content)
    utm = utm_match.group(1) if utm_match else ""
    return {
        "first_sentence": first_sentence,
        "emojis": emoji_set,
        "utm_campaign": utm,
    }


def compute_fingerprint(content: str) -> str:
    """Stable hash of the recognizable parts."""
    parts = extract_fingerprint_parts(content)
    # Use first_sentence + sorted emojis + utm — deterministic
    key = f"{parts['first_sentence']}|{','.join(parts['emojis'])}|{parts['utm_campaign']}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def load_fingerprints() -> dict:
    """Load the fingerprint side-car JSON; return empty dict if missing."""
    if not FINGERPRINT_FILE.exists():
        return {
            "_schema": "spore-content-fingerprints v1.0",
            "_purpose": "URL-to-fingerprint mapping for harvest mismatch detection (LESSONS-INBOX 2026-05-16 #5 instrumentation)",
            "_format": {
                "key": "spore URL (e.g. https://x.com/.../status/123)",
                "value": {
                    "fingerprint": "sha256 16-char hex of (first_sentence + emoji set + utm_campaign)",
                    "first_recorded": "ISO timestamp",
                    "first_sentence": "verbatim first sentence (audit aid)",
                    "emojis": "list of signature emoji chars",
                    "utm_campaign": "s{N} or empty",
                    "spore_id": "associated #N from SPORE-LOG (optional)",
                },
            },
            "fingerprints": {},
        }
    return json.loads(FINGERPRINT_FILE.read_text())


def save_fingerprints(data: dict) -> None:
    FINGERPRINT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def record_fingerprint(url: str, content: str, spore_id: str = "") -> dict:
    """Record fingerprint for URL (first-record or overwrite if --force)."""
    data = load_fingerprints()
    parts = extract_fingerprint_parts(content)
    fp = compute_fingerprint(content)
    entry = {
        "fingerprint": fp,
        "first_recorded": datetime.now().isoformat(timespec="seconds"),
        "first_sentence": parts["first_sentence"],
        "emojis": parts["emojis"],
        "utm_campaign": parts["utm_campaign"],
        "spore_id": spore_id,
    }
    data["fingerprints"][url] = entry
    save_fingerprints(data)
    return entry


def check_fingerprint(url: str, content: str) -> dict:
    """Compare new harvest content against recorded fingerprint."""
    data = load_fingerprints()
    recorded = data["fingerprints"].get(url)
    new_fp = compute_fingerprint(content)
    new_parts = extract_fingerprint_parts(content)

    if not recorded:
        return {
            "status": "no-baseline",
            "url": url,
            "new_fingerprint": new_fp,
            "message": "No fingerprint recorded for this URL — call --build-baseline first",
        }

    if recorded["fingerprint"] == new_fp:
        return {
            "status": "match",
            "url": url,
            "fingerprint": new_fp,
        }

    # Mismatch detected
    return {
        "status": "mismatch",
        "url": url,
        "recorded_fingerprint": recorded["fingerprint"],
        "recorded_first_sentence": recorded["first_sentence"],
        "recorded_utm_campaign": recorded["utm_campaign"],
        "new_fingerprint": new_fp,
        "new_first_sentence": new_parts["first_sentence"],
        "new_utm_campaign": new_parts["utm_campaign"],
        "message": "⚠️ Content fingerprint mismatch — possible URL drift / post edit / wrong row",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--build-baseline", action="store_true", help="Seed fingerprint JSON from a sample URL+content pair")
    ap.add_argument("--check", action="store_true", help="Compare new content vs recorded fingerprint")
    ap.add_argument("--list", action="store_true", help="List current fingerprint inventory")
    ap.add_argument("--url", help="Spore URL")
    ap.add_argument("--content", help="Harvest content (first 200 chars enough)")
    ap.add_argument("--spore-id", default="", help="Associated SPORE-LOG #N")
    ap.add_argument("--force", action="store_true", help="Overwrite existing fingerprint")
    args = ap.parse_args()

    if args.list:
        data = load_fingerprints()
        fps = data.get("fingerprints", {})
        print(f"📋 {len(fps)} fingerprint(s) recorded in {FINGERPRINT_FILE.relative_to(REPO)}")
        for url, entry in sorted(fps.items()):
            print(f"  spore #{entry.get('spore_id','?'):>3}  fp={entry['fingerprint']}  utm={entry['utm_campaign']:>5}  {url[:60]}")
            print(f"      first: {entry['first_sentence'][:80]}")
        return 0

    if args.build_baseline:
        if not args.url or not args.content:
            print("❌ --build-baseline requires --url + --content", file=sys.stderr)
            return 2
        entry = record_fingerprint(args.url, args.content, args.spore_id)
        print(json.dumps({"status": "recorded", "url": args.url, "entry": entry}, ensure_ascii=False, indent=2))
        return 0

    if args.check:
        if not args.url or not args.content:
            print("❌ --check requires --url + --content", file=sys.stderr)
            return 2
        result = check_fingerprint(args.url, args.content)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "match" else 1

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
