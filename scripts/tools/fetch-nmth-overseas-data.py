#!/usr/bin/env python3
"""
fetch-nmth-overseas-data.py — 爬取臺史博「海外史料看臺灣」資料集

用法:
    python3 scripts/tools/fetch-nmth-overseas-data.py

輸出:
    data/NMTH-overseas/
    ├── README.md
    ├── manifest.json
    ├── plans/
    │   ├── INDEX.md
    │   └── {plan-number}.md
    ├── collections/
    │   ├── INDEX.md
    │   └── {uuid}.md
    └── raw/
        ├── plans/
        └── collections/

API endpoints (reverse-engineered 2026-04-12):
    GET /api/Plan/GetPlan/{planUUID}  → plan detail + all collection UUIDs
    GET /api/collection/{UUID}        → individual collection item detail

來源: PEER-INGESTION-PIPELINE Stage 2 for NMTH-overseas
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://taiwanoverseas.nmth.gov.tw"
API_PLAN = f"{BASE_URL}/api/Plan/GetPlan"
API_COLLECTION = f"{BASE_URL}/api/collection"
FILE_API = f"{BASE_URL}/files"

OUTPUT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / "data" / "NMTH-overseas"

# Known plan UUIDs (scraped from SSR page 2026-04-12).
# The site uses Nuxt SSR with no plan-list API, so we seed with known UUIDs
# and discover more via cross-references in plan responses.
SEED_PLAN_UUIDS = [
    "78acece6-2e0a-4459-acb7-51c290850829",
    "ca32c735-14c4-4ec5-acf0-ca99f0442ab3",
    "784a8fe1-2eda-4a2a-884e-03fac0904b5a",
    "0e501608-203e-468c-a2cd-86855e53afdb",
    "3145b874-860e-488e-8d2e-f2aef9e57f31",
    "043ad591-881c-4e40-bd0d-73568fca0673",
    "a84fd3a9-88ec-48f3-b3d4-2c9f7089b597",
    "c234c455-0fa7-4fd7-86ad-0b6d4e30d992",
    "e640fb93-bbd1-4053-8347-38c9ebb295dc",
    "7a5f55e3-dcfa-4bce-8b27-7da8d61a9bd2",
    "69a054a3-fda6-42dc-9ff6-6c929ea59721",
    "56c6b0e6-55f3-48cf-bd58-f7a2a9f12f64",
]

USER_AGENT = "COMPUTEX.md-Semiont/1.0 (https://computex.taiwanai.ngo; peer-ingestion-pipeline)"


def fetch_json(url, retries=3, delay=1.0):
    """Fetch JSON from URL with retries and polite delay."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, Exception) as e:
            if attempt < retries - 1:
                print(f"  ⚠️  Retry {attempt+1}/{retries} for {url}: {e}")
                time.sleep(delay * (attempt + 1))
            else:
                print(f"  ❌ Failed after {retries} attempts: {url}: {e}")
                return None
    return None


def fetch_plan(plan_uuid):
    """Fetch a plan's detail including all collection UUIDs."""
    url = f"{API_PLAN}/{plan_uuid}"
    data = fetch_json(url)
    if not data or not data.get("isSuccess"):
        return None
    time.sleep(0.5)  # Polite crawling
    return data.get("result")


def fetch_collection(collection_uuid):
    """Fetch a single collection item's full detail."""
    url = f"{API_COLLECTION}/{collection_uuid}"
    data = fetch_json(url)
    if not data or not data.get("isSuccess"):
        return None
    time.sleep(0.3)
    return data.get("result")


def sanitize_filename(name, max_len=80):
    """Create a safe filename from a string."""
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    name = name.strip()[:max_len]
    return name or "untitled"


def plan_to_markdown(plan):
    """Convert plan JSON to markdown."""
    lines = [f"# {plan.get('name', 'Untitled Plan')}"]
    lines.append("")
    lines.append(f"- Plan ID: `{plan.get('planId', '')}`")
    lines.append(f"- Plan Number: {plan.get('planNumber', '')}")
    lines.append(f"- Source Type: {plan.get('sourceType', '')}")
    lines.append(f"- Status: {plan.get('status', '')}")
    lines.append(f"- Source: {BASE_URL}/archives/plan/{plan.get('planId', '')}")

    # Continents
    continents = plan.get("continent", plan.get("continents", []))
    if continents:
        lines.append(f"- Continents: {', '.join(c.get('name', '') for c in continents)}")

    lines.append("")

    desc = plan.get("description", "")
    if desc:
        # Strip HTML tags
        desc = re.sub(r"<[^>]+>", "", desc).strip()
        lines.append("## Description")
        lines.append("")
        lines.append(desc)
        lines.append("")

    # Collection list
    collections = plan.get("collection", plan.get("collections", []))
    if collections:
        lines.append(f"## Collections ({len(collections)} items)")
        lines.append("")
        for i, c in enumerate(collections, 1):
            title = c.get("title", "Untitled")
            uuid = c.get("collectionId", "")
            lines.append(f"{i}. [{title}](../collections/{uuid}.md)")
        lines.append("")

    return "\n".join(lines)


def collection_to_markdown(item):
    """Convert collection item JSON to markdown."""
    lines = [f"# {item.get('title', 'Untitled')}"]
    lines.append("")
    lines.append(f"- Source: {BASE_URL}/archives/{item.get('collectionId', '')}")
    lines.append(f"- API: /api/collection/{item.get('collectionId', '')}")
    lines.append(f"- Rights: {item.get('rights', '')}")
    lines.append(f"- Pages: {item.get('pages', '')}")
    lines.append(f"- View Count: {item.get('viewTimes', 0)}")

    # Categories
    for cat in item.get("categories", []):
        cat_name = cat.get("name", "")
        sub_names = [s.get("name", "") for s in cat.get("subCategories", [])]
        if sub_names:
            lines.append(f"- {cat_name}: {', '.join(sub_names)}")

    # Plans
    for plan in item.get("plans", []):
        lines.append(f"- Plan: {plan.get('name', '')} (`{plan.get('planId', '')}`)")

    # Dates
    dates = item.get("collectionDate", {})
    for key, val in dates.items():
        if val:
            lines.append(f"- {key}: {val}")

    # Supplementary info (often contains author)
    supp = item.get("supplementaryExplanation", "")
    if supp:
        lines.append(f"- Note: {supp}")

    lines.append("")

    # Description
    desc = item.get("description", "")
    if desc:
        lines.append("## Description")
        lines.append("")
        lines.append(desc)
        lines.append("")

    # Language documents (bilingual text)
    lang_docs = item.get("languageDocuments", [])
    for doc in lang_docs:
        lang_obj = doc.get("language") or {}
        lang_name = lang_obj.get("name", "Unknown") if isinstance(lang_obj, dict) else "Unknown"
        lang_type = doc.get("languageType", "")
        text = doc.get("text", "").strip()
        if text:
            label = f"{lang_name} ({lang_type})" if lang_type else lang_name
            lines.append(f"## {label}")
            lines.append("")
            # Clean HTML from text
            clean_text = re.sub(r"<[^>]+>", "", text)
            # Limit very long texts
            if len(clean_text) > 50000:
                lines.append(clean_text[:50000])
                lines.append(f"\n... [truncated, original {len(clean_text)} chars]")
            else:
                lines.append(clean_text)
            lines.append("")

    # Attachments
    attachments = item.get("attachments", [])
    if attachments:
        lines.append("## Attachments")
        lines.append("")
        seen = set()
        for att in attachments:
            src = att.get("src", "")
            if src and src not in seen:
                seen.add(src)
                att_type = att.get("type", "")
                lines.append(f"- [{att_type}] {BASE_URL}{src}")
        lines.append("")

    return "\n".join(lines)


def main():
    print("🏛️  NMTH Overseas Historical Materials Crawler")
    print(f"   Target: {BASE_URL}/archives")
    print(f"   Output: {OUTPUT_DIR}")
    print()

    # Create directories
    for subdir in ["plans", "collections", "raw/plans", "raw/collections"]:
        (OUTPUT_DIR / subdir).mkdir(parents=True, exist_ok=True)

    # ── Phase A: Fetch all plans ─────────────────────────────────────────────
    print("📋 Phase A: Fetching plans...")
    all_plans = {}
    all_plan_uuids = set(SEED_PLAN_UUIDS)
    discovered_uuids = set()

    for plan_uuid in list(all_plan_uuids):
        if plan_uuid in all_plans:
            continue
        print(f"  📄 Fetching plan {plan_uuid[:8]}...")
        plan = fetch_plan(plan_uuid)
        if plan:
            all_plans[plan_uuid] = plan
            # Save raw JSON
            raw_path = OUTPUT_DIR / "raw" / "plans" / f"{plan_uuid}.json"
            with open(raw_path, "w", encoding="utf-8") as f:
                json.dump(plan, f, ensure_ascii=False, indent=2)
            # Discover new plan UUIDs from collections' plan references
            for col in plan.get("collection", plan.get("collections", [])):
                # Each collection might reference other plans
                pass  # We'll discover more from collection detail later
            print(f"    ✅ {plan.get('name', '?')}: {len(plan.get('collections', []))} collections")
        else:
            print(f"    ❌ Failed to fetch plan {plan_uuid}")

    print(f"\n📋 Total plans fetched: {len(all_plans)}")

    # ── Phase B: Fetch all collections ───────────────────────────────────────
    print("\n📦 Phase B: Fetching collections...")
    all_collection_uuids = set()
    for plan in all_plans.values():
        for col in plan.get("collection", plan.get("collections", [])):
            uuid = col.get("collectionId")
            if uuid:
                all_collection_uuids.add(uuid)

    print(f"   Total unique collection UUIDs: {len(all_collection_uuids)}")

    all_collections = {}
    for i, uuid in enumerate(sorted(all_collection_uuids), 1):
        print(f"  📄 [{i}/{len(all_collection_uuids)}] Fetching {uuid[:8]}...")
        item = fetch_collection(uuid)
        if item:
            all_collections[uuid] = item
            # Save raw JSON
            raw_path = OUTPUT_DIR / "raw" / "collections" / f"{uuid}.json"
            with open(raw_path, "w", encoding="utf-8") as f:
                json.dump(item, f, ensure_ascii=False, indent=2)
            # Discover new plans from collection's plan references
            for plan_ref in item.get("plans", []):
                pid = plan_ref.get("planId")
                if pid and pid not in all_plans:
                    discovered_uuids.add(pid)
            title = item.get("title", "?")
            print(f"    ✅ {title[:50]}")
        else:
            print(f"    ❌ Failed")

    # ── Phase B2: Fetch newly discovered plans ───────────────────────────────
    if discovered_uuids:
        print(f"\n🔍 Discovered {len(discovered_uuids)} new plans from collections...")
        for plan_uuid in discovered_uuids:
            if plan_uuid in all_plans:
                continue
            print(f"  📄 Fetching plan {plan_uuid[:8]}...")
            plan = fetch_plan(plan_uuid)
            if plan:
                all_plans[plan_uuid] = plan
                raw_path = OUTPUT_DIR / "raw" / "plans" / f"{plan_uuid}.json"
                with open(raw_path, "w", encoding="utf-8") as f:
                    json.dump(plan, f, ensure_ascii=False, indent=2)
                # Fetch new collections from this plan
                for col in plan.get("collection", plan.get("collections", [])):
                    cuuid = col.get("collectionId")
                    if cuuid and cuuid not in all_collections:
                        all_collection_uuids.add(cuuid)
                        print(f"    📄 Fetching collection {cuuid[:8]}...")
                        citem = fetch_collection(cuuid)
                        if citem:
                            all_collections[cuuid] = citem
                            raw_path = OUTPUT_DIR / "raw" / "collections" / f"{cuuid}.json"
                            with open(raw_path, "w", encoding="utf-8") as f:
                                json.dump(citem, f, ensure_ascii=False, indent=2)

    # ── Phase C: Generate markdown files ─────────────────────────────────────
    print("\n📝 Phase C: Generating markdown...")

    # Plans
    plan_index_lines = ["# NMTH 海外史料看臺灣 — Plans Index", "",
                        f"Total plans: {len(all_plans)}", ""]
    for pid, plan in sorted(all_plans.items(), key=lambda x: x[1].get("planNumber", "")):
        plan_num = plan.get("planNumber", pid[:8])
        plan_name = plan.get("name", "Untitled")
        col_count = len(plan.get("collection", plan.get("collections", [])))

        md = plan_to_markdown(plan)
        safe_name = sanitize_filename(plan_num)
        plan_path = OUTPUT_DIR / "plans" / f"{safe_name}.md"
        with open(plan_path, "w", encoding="utf-8") as f:
            f.write(md)

        plan_index_lines.append(f"- [{plan_num} — {plan_name}]({safe_name}.md) ({col_count} collections)")

    with open(OUTPUT_DIR / "plans" / "INDEX.md", "w", encoding="utf-8") as f:
        f.write("\n".join(plan_index_lines))

    # Collections
    col_index_lines = ["# NMTH 海外史料看臺灣 — Collections Index", "",
                       f"Total collections: {len(all_collections)}", ""]
    for uuid, item in sorted(all_collections.items(), key=lambda x: x[1].get("title", "")):
        title = item.get("title", "Untitled")
        md = collection_to_markdown(item)
        col_path = OUTPUT_DIR / "collections" / f"{uuid}.md"
        with open(col_path, "w", encoding="utf-8") as f:
            f.write(md)

        # Get categories for index
        cats = []
        for cat in item.get("categories", []):
            for sub in cat.get("subCategories", []):
                cats.append(sub.get("name", ""))
        cat_str = f" [{', '.join(cats)}]" if cats else ""
        col_index_lines.append(f"- [{title}]({uuid}.md){cat_str}")

    with open(OUTPUT_DIR / "collections" / "INDEX.md", "w", encoding="utf-8") as f:
        f.write("\n".join(col_index_lines))

    # ── Phase D: Generate manifest + README ──────────────────────────────────
    print("\n📊 Phase D: Generating manifest + README...")

    # Collect stats
    time_periods = {}
    resource_types = {}
    languages = {}
    locations = {}
    for item in all_collections.values():
        for cat in item.get("categories", []):
            cat_name = cat.get("name", "")
            for sub in cat.get("subCategories", []):
                sub_name = sub.get("name", "")
                if cat_name == "時代":
                    time_periods[sub_name] = time_periods.get(sub_name, 0) + 1
                elif cat_name == "資源類型":
                    resource_types[sub_name] = resource_types.get(sub_name, 0) + 1
                elif cat_name == "檔案格式":
                    pass  # skip file format
                elif cat_name == "文物描述地點":
                    locations[sub_name] = locations.get(sub_name, 0) + 1
        for doc in item.get("languageDocuments", []):
            lang_obj = doc.get("language") or {}
            lang_name = lang_obj.get("name", "") if isinstance(lang_obj, dict) else ""
            lang_type = doc.get("languageType", "")
            key = f"{lang_name} ({lang_type})" if lang_type else lang_name
            languages[key] = languages.get(key, 0) + 1

    manifest = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": BASE_URL,
        "peerName": "國立臺灣歷史博物館 — 海外史料看臺灣",
        "peerId": "nmth-overseas",
        "counts": {
            "plans": len(all_plans),
            "collections": len(all_collections),
            "seedPlanUuids": len(SEED_PLAN_UUIDS),
            "discoveredPlanUuids": len(discovered_uuids),
        },
        "distributions": {
            "timePeriods": dict(sorted(time_periods.items())),
            "resourceTypes": dict(sorted(resource_types.items(), key=lambda x: -x[1])),
            "languages": dict(sorted(languages.items(), key=lambda x: -x[1])),
            "locations": dict(sorted(locations.items(), key=lambda x: -x[1])),
        },
        "planIndex": {
            pid: {
                "number": p.get("planNumber", ""),
                "name": p.get("name", ""),
                "collectionCount": len(p.get("collections", [])),
            }
            for pid, p in all_plans.items()
        },
    }

    with open(OUTPUT_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # README
    readme_lines = [
        "# 臺史博「海外史料看臺灣」資料集",
        "",
        f"> Crawled: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        f"> Source: {BASE_URL}/archives",
        f"> Crawler: `scripts/tools/fetch-nmth-overseas-data.py`",
        f"> © 國立臺灣歷史博物館 National Museum of Taiwan History",
        "",
        "## Summary",
        "",
        f"- **Plans**: {len(all_plans)}",
        f"- **Collections**: {len(all_collections)}",
        "",
        "## Time Period Distribution",
        "",
    ]
    for period, count in sorted(time_periods.items()):
        readme_lines.append(f"- {period}: {count}")
    readme_lines.extend(["", "## Resource Types", ""])
    for rtype, count in sorted(resource_types.items(), key=lambda x: -x[1]):
        readme_lines.append(f"- {rtype}: {count}")
    readme_lines.extend(["", "## Languages", ""])
    for lang, count in sorted(languages.items(), key=lambda x: -x[1]):
        readme_lines.append(f"- {lang}: {count}")
    readme_lines.extend(["", "## How to re-run", "",
                         "```bash",
                         "python3 scripts/tools/fetch-nmth-overseas-data.py",
                         "```", ""])

    with open(OUTPUT_DIR / "README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(readme_lines))

    # ── Summary ──────────────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print(f"✅ NMTH Overseas Historical Materials — Crawl Complete")
    print(f"   Plans: {len(all_plans)}")
    print(f"   Collections: {len(all_collections)}")
    print(f"   Output: {OUTPUT_DIR}")
    print(f"   Raw JSON: {OUTPUT_DIR / 'raw'}")
    size_mb = sum(f.stat().st_size for f in OUTPUT_DIR.rglob("*") if f.is_file()) / 1024 / 1024
    print(f"   Total size: {size_mb:.1f} MB")
    print("=" * 60)


if __name__ == "__main__":
    main()
