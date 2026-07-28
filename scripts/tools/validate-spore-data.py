#!/usr/bin/env python3
"""validate-spore-data.py — 孢子資料跨層一致性檢查（v3, 2026-06-10 JSON SSOT）。

層級（reports/spore-json-ssot-2026-06-10.md）：
  docs/factory/spore-log.json       identity SSOT（spore-db.py add-spore 寫）
  docs/factory/spore-metrics.json   metric 事件 SSOT（spore-db.py add-metrics 寫）
  docs/factory/SPORE-HARVESTS/*.md  敘事層（留言/bucket，不載 canonical 數字）
  docs/factory/SPORE-LOG.md         凍結歷史（≤ bootstrap 當下，不再寫入）
  src/data/spores.json              衍生記錄層（generate-spore-records.py）
  knowledge/*.md sporeLinks         identity pointer（id/platform/date/url，無數字）
  public/api/dashboard-spores.json  衍生分析聚合

6 checks:
  1. spore-db check（schema / unique id / unique url / event refs）
  2. 數字 parser regression（K/M suffix，spore-db.parse_count）
  3. SPORE-LOG.md 凍結守衛（發文紀錄 row 數不得增加 — 新孢子走 spore-db.py）
  4. SPORE-HARVESTS 敘事 frontmatter key drift（spores plural canonical）
  5. knowledge sporeLinks identity-only（帶 metrics = ERROR）+ URL ↔ spore-log 對照
  6. 衍生層 freshness + coverage（spores.json / dashboard-spores.json vs SSOT mtime）

Exit code: 0 = 綠 / 1 = warnings / 2 = errors（block CI / pre-commit）
Usage: python3 scripts/tools/validate-spore-data.py [--strict]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_JSON = REPO_ROOT / "docs/factory/spore-log.json"
METRICS_JSON = REPO_ROOT / "docs/factory/spore-metrics.json"
FROZEN_LOG_MD = REPO_ROOT / "docs/factory/SPORE-LOG.md"
HARVESTS_DIR = REPO_ROOT / "docs/factory/SPORE-HARVESTS"
RECORDS_JSON = REPO_ROOT / "src/data/spores.json"
DASHBOARD_JSON = REPO_ROOT / "public/api/dashboard-spores.json"
KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"

# 凍結基線（2026-06-10 bootstrap 當下的發文紀錄 row 數）。
# 之後新孢子只進 spore-log.json — markdown row 數變多 = 有人寫回凍結檔。
FROZEN_PUB_ROWS = 125

METRIC_KEYS = ("views", "likes", "reposts", "comments", "shares")
LANG_DIRS = {"en", "ja", "ko", "es", "fr", "zh-TW"}


def green(s):
    return f"\033[32m{s}\033[0m"


def yellow(s):
    return f"\033[33m{s}\033[0m"


def red(s):
    return f"\033[31m{s}\033[0m"


def _load_spore_db():
    spec = importlib.util.spec_from_file_location(
        "spore_db", REPO_ROOT / "scripts/tools/spore-db.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── check 1: spore-db schema ──

def check_spore_db():
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts/tools/spore-db.py"), "check"],
        capture_output=True, text=True)
    errors = [] if r.returncode == 0 else [f"❌ spore-db check failed:\n{r.stdout.strip()}"]
    return errors, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""


# ── check 2: parser regression ──

def check_parser_regression(spore_db):
    cases = [
        ("65.4K", 65400), ("1.8K", 1800), ("180K", 180000),
        ("65,400", 65400), ("1,800", 1800), ("65000", 65000),
        ("300,000", 300000), ("2.5M", 2500000),
    ]
    failures = []
    for inp, expected in cases:
        got = spore_db.parse_count(inp)
        if got != expected:
            failures.append((inp, got, expected))
    return failures


# ── check 3: frozen markdown guard ──

def check_frozen_log():
    if not FROZEN_LOG_MD.exists():
        return []
    text = FROZEN_LOG_MD.read_text(encoding="utf-8")
    in_pub, count = False, 0
    for line in text.splitlines():
        if line.startswith("## "):
            in_pub = line[3:].strip() == "發文紀錄"
            continue
        if in_pub and re.match(r"^\|\s*\d+\s*\|", line):
            count += 1
    if count > FROZEN_PUB_ROWS:
        return [f"❌ SPORE-LOG.md 發文紀錄 有 {count} rows（凍結基線 {FROZEN_PUB_ROWS}）— "
                f"新孢子要走 spore-db.py add-spore，不寫凍結 markdown"]
    return []


# ── check 4: harvest narrative frontmatter drift ──

def check_harvests_frontmatter():
    warnings = []
    canonical = legacy = 0
    if not HARVESTS_DIR.exists():
        return warnings, 0, 0
    for md in HARVESTS_DIR.glob("*.md"):
        head = md.read_text(encoding="utf-8")[:600]
        if re.search(r"^spores:", head, re.M):
            canonical += 1
        elif re.search(r"^spore:", head, re.M):
            legacy += 1
            warnings.append(f"⚠️  {md.name}: legacy 'spore' singular frontmatter key")
    return warnings, legacy, canonical


# ── check 5: knowledge sporeLinks identity-only ──

def parse_sporelinks_from_md(md_path):
    try:
        text = md_path.read_text(encoding="utf-8")
    except OSError:
        return []
    if not text.startswith("---") or "sporeLinks:" not in text:
        return []
    end = text.find("---", 3)
    if end == -1:
        return []
    lines = text[3:end].split("\n")
    start = next((i for i, l in enumerate(lines)
                  if l.strip().startswith("sporeLinks:")), None)
    if start is None:
        return []
    items, cur = [], None
    for line in lines[start + 1:]:
        if line.startswith("  - "):
            if cur:
                items.append(cur)
            cur = {}
            kv = line[4:].split(":", 1)
            if len(kv) == 2:
                cur[kv[0].strip()] = kv[1].strip().strip("'\"")
        elif line.startswith("    ") and cur is not None:
            kv = line.strip().split(":", 1)
            if len(kv) == 2:
                cur[kv[0].strip()] = kv[1].strip().strip("'\"")
        else:
            if cur:
                items.append(cur)
            break
    if cur:
        items.append(cur)
    return items


def check_sporelinks_identity_only():
    errors, warnings = [], []
    log_urls = set()
    if LOG_JSON.exists():
        log_urls = {s["url"] for s in
                    json.loads(LOG_JSON.read_text(encoding="utf-8"))["spores"]
                    if s.get("url")}
    checked = 0
    for md in KNOWLEDGE_ROOT.rglob("*.md"):
        sl = parse_sporelinks_from_md(md)
        if not sl:
            continue
        rel = md.relative_to(REPO_ROOT)
        is_zh = md.relative_to(KNOWLEDGE_ROOT).parts[0] not in LANG_DIRS
        for link in sl:
            checked += 1
            leaked = [k for k in METRIC_KEYS if k in link]
            if leaked:
                errors.append(
                    f"❌ {rel}: sporeLinks carries metrics {leaked} — identity-only "
                    f"(id/platform/date/url)，數字住 spore-metrics.json")
            url = (link.get("url") or "").strip()
            if is_zh and url and url not in log_urls:
                warnings.append(f"⚠️  {rel} sporeLinks URL 不在 spore-log.json: {url}")
    return errors, warnings, checked


# ── check 6: derived freshness + coverage ──

def check_derived():
    errors, warnings = [], []
    if not RECORDS_JSON.exists():
        errors.append("❌ src/data/spores.json missing — run generate-spore-records.py")
        return errors, warnings
    try:
        records = json.loads(RECORDS_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"❌ spores.json unparseable: {e}"], warnings

    n_log = len([s for s in json.loads(LOG_JSON.read_text(encoding="utf-8"))["spores"]
                 if not s.get("deleted")]) if LOG_JSON.exists() else 0
    n_rec = len(records.get("spores", []))
    if n_log and n_rec != n_log:
        warnings.append(f"⚠️  spores.json {n_rec} records vs spore-log {n_log} — regen")

    for target, name, fix in (
        (RECORDS_JSON, "spores.json", "generate-spore-records.py"),
        (DASHBOARD_JSON, "dashboard-spores.json", "generate-dashboard-spores.py"),
    ):
        if not target.exists():
            errors.append(f"❌ {name} missing — run {fix}")
            continue
        t_m = target.stat().st_mtime
        for src in (LOG_JSON, METRICS_JSON):
            if src.exists() and src.stat().st_mtime > t_m:
                warnings.append(f"⚠️  {name} 比 {src.name} 舊 — run {fix}")
                break
    return errors, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="warnings → errors")
    args = ap.parse_args()

    print("===== Spore data SSOT validation (v3 JSON) =====\n")
    all_errors, all_warnings = [], []
    spore_db = _load_spore_db()

    print("[1/6] spore-db schema check...")
    errs, summary = check_spore_db()
    all_errors.extend(errs)
    print(red(f"    {errs[0]}") if errs else green(f"    ✅ {summary}"))

    print("\n[2/6] count parser regression (K/M)...")
    failures = check_parser_regression(spore_db)
    if failures:
        for inp, got, expected in failures:
            all_errors.append(f"❌ parse_count('{inp}') = {got}, expected {expected}")
        print(red(f"    ❌ {len(failures)} failures"))
    else:
        print(green("    ✅ 8/8 cases pass"))

    print("\n[3/6] SPORE-LOG.md 凍結守衛...")
    errs = check_frozen_log()
    all_errors.extend(errs)
    print(red(f"    {errs[0]}") if errs else
          green(f"    ✅ frozen at {FROZEN_PUB_ROWS} rows"))

    print("\n[4/6] SPORE-HARVESTS 敘事 frontmatter key drift...")
    warns, legacy, canonical = check_harvests_frontmatter()
    all_warnings.extend(warns)
    print((yellow(f"    ⚠️  canonical {canonical} / legacy {legacy}") if warns
           else green(f"    ✅ canonical {canonical} / legacy {legacy}")))

    print("\n[5/6] knowledge sporeLinks identity-only...")
    errs, warns, checked = check_sporelinks_identity_only()
    all_errors.extend(errs)
    all_warnings.extend(warns)
    print(f"    {checked} entries checked")
    for it in (errs + warns)[:5]:
        print(yellow(f"    {it}"))
    if not errs and not warns:
        print(green("    ✅ all identity-only (id/platform/date/url)"))

    print("\n[6/6] 衍生層 freshness + coverage...")
    errs, warns = check_derived()
    all_errors.extend(errs)
    all_warnings.extend(warns)
    for it in (errs + warns)[:5]:
        print(yellow(f"    {it}"))
    if not errs and not warns:
        print(green("    ✅ spores.json + dashboard-spores.json fresh"))

    print(f"\n===== Summary =====")
    print(f"  Errors:   {len(all_errors)}")
    print(f"  Warnings: {len(all_warnings)}")
    if all_errors:
        print(red("\n❌ FAIL"))
        return 2
    if all_warnings and args.strict:
        print(red("\n❌ FAIL (strict mode)"))
        return 2
    if all_warnings:
        print(yellow("\n⚠️  PASS with warnings"))
        return 1
    print(green("\n✅ ALL GREEN"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
