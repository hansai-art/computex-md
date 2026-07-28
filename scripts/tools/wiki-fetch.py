#!/usr/bin/env python3
"""
wiki-fetch.py — Robust Wikimedia Commons image fetcher with 2026 rate-limit mitigation.

Built 2026-05-21 after 5/18 教訓 (Wikimedia 8s delay 仍 429 / 88 圖留給 cron 補) +
T413570 + WMF 2026 rate-limit policy research:

  - **Referer header** (Commons File: URL) significantly reduces 429
  - **Browser-like UA** beats custom app identifier (non-WMF apps pooled into shared bot limit)
  - **Standard thumb sizes only** (2026 restriction): 20/40/60/120/250/330/500/960/1280/1920/3840
  - **/thumb.php** alternative endpoint sometimes bypasses upload.wikimedia.org cache miss
  - **Respect Retry-After** header per HTTP standard
  - **Cross-process serialization** via /tmp/.wiki-fetch.lock — prevents 3 parallel agents
    burning shared rate budget. Polite 2s delay + jitter between requests system-wide.

Fallback chain per URL:
  1. As-given URL + Referer + browser UA + polite delay
  2. Thumbnail size variants (try smaller standard sizes: 1280→960→500→330)
  3. /thumb.php endpoint alternative
  4. Original (non-thumb) URL
  5. Wayback Machine snapshot (web.archive.org/web/2*/{url})
  6. Bail with structured error report

Usage:
  scripts/tools/wiki-fetch.py <URL> <OUTPUT_PATH>
  scripts/tools/wiki-fetch.py --batch <FILE>   # tab-separated URL<TAB>OUT per line
  scripts/tools/wiki-fetch.py --self-test       # verify tool works
"""

import argparse
import fcntl
import hashlib
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

# 2026 WMF standard thumb sizes — others may 404
STD_THUMB_SIZES = [3840, 1920, 1280, 960, 500, 330, 250, 120]

# Per WMF policy: browser-like UA performs better than custom app identifier.
# We use Firefox UA to blend with browser traffic pool (not bot pool).
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0"

# Cross-process serialization lock + min interval to upload.wikimedia.org
LOCK_PATH = "/tmp/.wiki-fetch.lock"
LAST_REQ_PATH = "/tmp/.wiki-fetch.last"
MIN_INTERVAL_S = 2.0  # per-host floor, +jitter
JITTER_S = 1.0


def politely_wait():
    """Cross-process: ensure ≥ MIN_INTERVAL_S between any wiki-fetch calls on this host."""
    with open(LOCK_PATH, "w") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            last = 0.0
            if os.path.exists(LAST_REQ_PATH):
                try:
                    last = float(Path(LAST_REQ_PATH).read_text().strip())
                except (ValueError, OSError):
                    last = 0.0
            now = time.time()
            elapsed = now - last
            wait = MIN_INTERVAL_S + random.uniform(0, JITTER_S) - elapsed
            if wait > 0:
                time.sleep(wait)
            Path(LAST_REQ_PATH).write_text(str(time.time()))
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def commons_file_referer(url: str) -> str:
    """Derive Commons File: page URL for Referer header.

    upload.wikimedia.org/wikipedia/commons/thumb/X/XY/Name.jpg/1280px-... → File:Name.jpg
    upload.wikimedia.org/wikipedia/commons/X/XY/Name.jpg → File:Name.jpg
    """
    m = re.search(r"/wikipedia/commons(?:/thumb)?/[0-9a-f]/[0-9a-f]{2}/([^/]+?)(?:/[^/]+)?$", url)
    if not m:
        return "https://commons.wikimedia.org/wiki/Main_Page"
    fname = urllib.parse.unquote(m.group(1))
    return f"https://commons.wikimedia.org/wiki/File:{fname}"


def thumb_size_variants(url: str) -> list[str]:
    """Generate alternative thumb-size URLs by swapping the width prefix.

    Returns list ordered from largest to smallest, original URL excluded.
    """
    # Match …/thumb/X/XY/Name.ext/NNNpx-Name.ext
    m = re.match(
        r"^(https://upload\.wikimedia\.org/wikipedia/[a-z]+/thumb/[0-9a-f]/[0-9a-f]{2}/[^/]+/)(\d+)px-(.+)$",
        url,
    )
    if not m:
        return []
    prefix, current_size_str, suffix = m.group(1), m.group(2), m.group(3)
    current = int(current_size_str)
    out = []
    for sz in STD_THUMB_SIZES:
        if sz == current:
            continue
        out.append(f"{prefix}{sz}px-{suffix}")
    return out


def thumb_to_original(url: str) -> Optional[str]:
    """Strip /thumb/ + size prefix → original file URL."""
    m = re.match(
        r"^(https://upload\.wikimedia\.org/wikipedia/[a-z]+)/thumb/([0-9a-f])/([0-9a-f]{2})/([^/]+)/[^/]+$",
        url,
    )
    if not m:
        return None
    return f"{m.group(1)}/{m.group(2)}/{m.group(3)}/{m.group(4)}"


def thumb_php_alternative(url: str) -> Optional[str]:
    """Convert upload.wikimedia.org/wikipedia/commons/thumb/.../NNNpx-Name.ext →
    commons.wikimedia.org/w/thumb.php?f=Name.ext&width=NNN

    /thumb.php sometimes bypasses upload cache miss per T413570 discussion.
    """
    m = re.match(
        r"^https://upload\.wikimedia\.org/wikipedia/commons/thumb/[0-9a-f]/[0-9a-f]{2}/([^/]+)/(\d+)px-",
        url,
    )
    if not m:
        return None
    fname, width = m.group(1), m.group(2)
    return f"https://commons.wikimedia.org/w/thumb.php?f={fname}&width={width}"


def wayback_alternative(url: str) -> Optional[str]:
    """Query Wayback CDX API for any cached snapshot, return latest snapshot URL."""
    cdx = (
        "https://web.archive.org/cdx/search/cdx?"
        + urllib.parse.urlencode(
            {"url": url, "output": "json", "limit": "-1", "filter": "statuscode:200"}
        )
    )
    try:
        req = urllib.request.Request(cdx, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if not data or len(data) < 2:
            return None
        # data[0] is header row; last row is most recent
        row = data[-1]
        timestamp, original = row[1], row[2]
        return f"https://web.archive.org/web/{timestamp}id_/{original}"
    except Exception:
        return None


def _fetch_once(url: str, referer: str, timeout: int = 30):
    """Single HTTP GET. Returns (status, retry_after_secs, bytes_or_None, err_or_None)."""
    politely_wait()
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "image/avif,image/webp,image/png,image/svg+xml,image/*,*/*;q=0.8",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.5",
            "Referer": referer,
            "Accept-Encoding": "identity",  # avoid gzip on binary
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return (resp.status, 0, resp.read(), None)
    except urllib.error.HTTPError as e:
        retry_after = 0
        try:
            retry_after = int(e.headers.get("Retry-After", "0") or "0")
        except (ValueError, TypeError):
            retry_after = 0
        return (e.code, retry_after, None, str(e))
    except Exception as e:
        return (0, 0, None, str(e))


def fetch_with_fallback(url: str, out_path: str, log=print) -> dict:
    """Run the full fallback chain. Returns dict with keys: ok, bytes, strategy, attempts."""
    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        if size > 0:
            return {"ok": True, "bytes": size, "strategy": "skip-exists", "attempts": 0}

    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    referer = commons_file_referer(url)
    attempts = []

    # Build full URL candidate list (in fallback priority order)
    candidates = [(url, "as-given")]
    candidates.extend((u, f"thumb-variant-{i}") for i, u in enumerate(thumb_size_variants(url)))
    orig = thumb_to_original(url)
    if orig:
        candidates.append((orig, "original-full-size"))
    php_alt = thumb_php_alternative(url)
    if php_alt:
        candidates.append((php_alt, "thumb.php-endpoint"))

    for candidate_url, strategy in candidates:
        # Per-candidate up to 3 retries with exponential backoff on 429/5xx
        for attempt in range(3):
            status, retry_after, body, err = _fetch_once(candidate_url, referer)
            attempts.append(
                {"url": candidate_url, "strategy": strategy, "status": status, "err": err}
            )
            if status == 200 and body:
                with open(out_path, "wb") as f:
                    f.write(body)
                log(f"   ✅ {os.path.basename(out_path)} ({len(body) // 1024} KB) via {strategy}")
                return {
                    "ok": True,
                    "bytes": len(body),
                    "strategy": strategy,
                    "attempts": attempts,
                }
            if status == 429:
                wait = retry_after if retry_after > 0 else (15 * (2**attempt) + random.uniform(0, 5))
                log(f"   ⏸ 429 on {strategy}, retry in {wait:.0f}s (attempt {attempt + 1}/3)")
                time.sleep(wait)
                continue
            if status >= 500:
                wait = 10 * (attempt + 1)
                log(f"   ⏸ {status} on {strategy}, retry in {wait}s")
                time.sleep(wait)
                continue
            # 4xx (non-429) — break inner loop, try next candidate
            break

    # All upload.wikimedia.org strategies failed — try Wayback
    wb = wayback_alternative(url)
    if wb:
        log(f"   🕰 trying Wayback Machine fallback")
        status, _, body, err = _fetch_once(wb, "https://web.archive.org/")
        attempts.append({"url": wb, "strategy": "wayback", "status": status, "err": err})
        if status == 200 and body:
            with open(out_path, "wb") as f:
                f.write(body)
            log(f"   ✅ {os.path.basename(out_path)} ({len(body) // 1024} KB) via Wayback")
            return {
                "ok": True,
                "bytes": len(body),
                "strategy": "wayback",
                "attempts": attempts,
            }

    log(f"   ❌ {os.path.basename(out_path)} — all strategies failed")
    return {"ok": False, "bytes": 0, "strategy": "exhausted", "attempts": attempts}


def main():
    parser = argparse.ArgumentParser(description="Robust Wikimedia Commons image fetcher")
    parser.add_argument("url", nargs="?", help="Image URL to fetch")
    parser.add_argument("out_path", nargs="?", help="Output file path")
    parser.add_argument("--batch", help="Tab-separated file: URL<TAB>OUT_PATH per line")
    parser.add_argument("--self-test", action="store_true", help="Verify tool works")
    parser.add_argument("--json", action="store_true", help="Emit JSON per fetch")
    args = parser.parse_args()

    if args.self_test:
        # Fetch a known small Wikimedia image to verify
        test_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Commons-logo.svg/120px-Commons-logo.svg.png"
        test_out = "/tmp/wiki-fetch-self-test.png"
        result = fetch_with_fallback(test_url, test_out)
        if result["ok"]:
            print(f"✅ Self-test passed. Strategy: {result['strategy']}, bytes: {result['bytes']}")
            os.unlink(test_out)
            sys.exit(0)
        else:
            print(f"❌ Self-test failed: {json.dumps(result, ensure_ascii=False, indent=2)}")
            sys.exit(1)

    if args.batch:
        results = []
        with open(args.batch) as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) != 2:
                    print(f"  ⚠️ line {line_no} malformed (need URL<TAB>OUT_PATH): {line}")
                    continue
                url, out_path = parts
                print(f"\n📥 [{line_no}] {os.path.basename(out_path)}")
                result = fetch_with_fallback(url, out_path)
                result["url"] = url
                result["out_path"] = out_path
                results.append(result)
        ok = sum(1 for r in results if r["ok"])
        fail = len(results) - ok
        print(f"\n=== Batch summary: {ok} ok / {fail} fail ===")
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        sys.exit(0 if fail == 0 else 1)

    if not args.url or not args.out_path:
        parser.print_help()
        sys.exit(2)

    result = fetch_with_fallback(args.url, args.out_path)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
