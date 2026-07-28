#!/usr/bin/env python3
"""spore-db.py — 孢子結構資料 SSOT 的唯一寫入工具。

SSOT files (reports/spore-json-ssot-2026-06-10.md):
  docs/factory/spore-log.json      identity registry — append at publish
  docs/factory/spore-metrics.json  metric event stream — append at harvest

Replaces hand-editing SPORE-LOG.md markdown tables (frozen ≤ historical ids,
2026-06-10). Narrative stays in SPORE-HARVESTS/*.md + SPORE-BLUEPRINTS/*.

Subcommands:
  add-spore    --date 2026-06-11 --platform threads --slug 文章slug --url URL
               [--lang zh] [--category music] [--template 'A2 ...']
               [--highlight 'ship 一句話'] [--id N]
               → assigns next id, prints it. Run once per platform post.
  add-metrics  --spore N --d-plus N --batch batch-2026-06-11-x [--at 'YYYY-MM-DD HH:MM']
               [--views 1.4K] [--likes 369] [--reposts 39] [--comments 21] [--shares 45]
               [--source harvest]
               → appends one harvest event. Numbers accept K/M suffix.
               Same (spore, batch, dPlus) replaces (idempotent re-harvest).
  last-spore   --article SLUG → JSON {lastDate, daysAgo, ids}; exit 3 if none.
               For PICK HG5 / PUBLISH ≥2週 查重.
  check        → schema + uniqueness + cross-ref validation. exit 2 on error.

  top          [--by views|likes|reposts|comments|shares|engagement] [--limit N]
               [--platform threads|x|...] [--since YYYY-MM-DD] [--article SLUG] [--json]
               → rank spores by peak metric (join log identity + metrics peak).
               engagement = (likes+reposts+comments+shares) / views. Read-only.
  show         --spore N → identity + full metric event history (read-only).

2026-06-10 | spore JSON SSOT flip
2026-06-19 | + read side (top / show) — query without hand-rolling joins
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LOG_PATH = REPO / "docs/factory/spore-log.json"
METRICS_PATH = REPO / "docs/factory/spore-metrics.json"

TPE = timezone(timedelta(hours=8))
METRIC_KEYS = ("views", "likes", "reposts", "comments", "shares")
PLATFORMS = {"threads", "x", "instagram", "facebook"}


def parse_count(v):
    """Tolerant count parser: '1.4K' → 1400, '2,357' → 2357, 'n/a' → None."""
    if v is None:
        return None
    s = str(v).strip().replace(",", "").replace("*", "").replace(" ", "")
    if not s or s.lower() in ("—", "-", "no-data", "n/a", "?", "null", "none"):
        return None
    m = re.match(r"^([\d.]+)([KkMm]?)$", s)
    if not m:
        raise ValueError(f"無法解析數字: {v!r}")
    n = float(m.group(1))
    suf = m.group(2).upper()
    if suf == "K":
        n *= 1_000
    elif suf == "M":
        n *= 1_000_000
    return int(n)


def _load(path, root_key):
    if not path.exists():
        return {"_meta": {"schemaVersion": 1}, root_key: []}
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _now():
    return datetime.now(TPE).strftime("%Y-%m-%d %H:%M")


# ────────────────── add-spore ──────────────────

def cmd_add_spore(args):
    data = _load(LOG_PATH, "spores")
    spores = data["spores"]

    if not re.match(r"^\d{4}-\d{2}-\d{2}$", args.date):
        print(f"❌ --date 格式需 YYYY-MM-DD: {args.date}", file=sys.stderr)
        return 2
    if args.platform not in PLATFORMS:
        print(f"❌ --platform 需為 {sorted(PLATFORMS)}: {args.platform}", file=sys.stderr)
        return 2
    if args.url:
        if "?" in args.url:
            print(f"❌ URL 帶 query string，先剝掉（SPORE-PIPELINE §URL 乾淨化）: {args.url}",
                  file=sys.stderr)
            return 2
        dup = next((s for s in spores if s.get("url") == args.url), None)
        if dup:
            print(f"❌ URL 已存在於 #{dup['id']}", file=sys.stderr)
            return 2

    sid = args.id if args.id else (max((s["id"] for s in spores), default=0) + 1)
    if any(s["id"] == sid for s in spores):
        print(f"❌ id #{sid} 已存在", file=sys.stderr)
        return 2

    # category auto-resolve from knowledge/ when omitted
    category = args.category
    if not category:
        for md in (REPO / "knowledge").rglob(f"{args.slug}.md"):
            rel = md.relative_to(REPO / "knowledge")
            if rel.parts[0] not in {"en", "ja", "ko", "es", "fr", "zh-TW"}:
                category = rel.parts[0].lower()
                break

    entry = {
        "id": sid,
        "date": args.date,
        "lang": args.lang,
        "platform": args.platform,
        "slug": args.slug,
        "category": category,
        "template": args.template,
        "url": args.url or None,
        "highlight": args.highlight,
    }
    spores.append(entry)
    spores.sort(key=lambda s: s["id"])
    _save(LOG_PATH, data)
    print(f"✓ spore #{sid} → spore-log.json ({args.platform} / {args.slug})")
    print(f"  下一步：sync-spore-links.py --apply 會把 identity pointer 長進文章 frontmatter")
    print(sid)
    return 0


# ────────────────── add-metrics ──────────────────

def cmd_add_metrics(args):
    log = _load(LOG_PATH, "spores")
    if not any(s["id"] == args.spore for s in log["spores"]):
        print(f"❌ spore #{args.spore} 不在 spore-log.json — 先 add-spore", file=sys.stderr)
        return 2

    data = _load(METRICS_PATH, "events")
    events = data["events"]
    try:
        nums = {k: parse_count(getattr(args, k)) for k in METRIC_KEYS}
    except ValueError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 2
    if all(v is None for v in nums.values()):
        print("❌ 至少給一個指標（--views/--likes/--reposts/--comments/--shares）",
              file=sys.stderr)
        return 2

    event = {
        "spore": args.spore,
        "dPlus": args.d_plus,
        "at": args.at or _now(),
        "batch": args.batch,
        **nums,
        "source": args.source,
    }
    # idempotent: same (spore, batch, dPlus) replaces
    replaced = False
    for i, e in enumerate(events):
        if (e["spore"], e.get("batch"), e.get("dPlus")) == (args.spore, args.batch, args.d_plus):
            events[i] = event
            replaced = True
            break
    if not replaced:
        events.append(event)
    events.sort(key=lambda e: (e["spore"],
                               e["dPlus"] if e.get("dPlus") is not None else -1,
                               e.get("at") or ""))
    _save(METRICS_PATH, data)
    shown = " ".join(f"{k}={v}" for k, v in nums.items() if v is not None)
    print(f"✓ #{args.spore} D+{args.d_plus} {shown} → spore-metrics.json"
          f"{' (replaced)' if replaced else ''}")
    print(f"  下一步：generate-spore-records.py 重生 spores.json（refresh Step 4 / prebuild 自動跑）")
    return 0


# ────────────────── last-spore ──────────────────

def cmd_last_spore(args):
    data = _load(LOG_PATH, "spores")
    hits = [s for s in data["spores"] if s.get("slug") == args.article and s.get("date")]
    if not hits:
        print(json.dumps({"slug": args.article, "lastDate": None, "ids": []},
                         ensure_ascii=False))
        return 3
    last = max(s["date"] for s in hits)
    days = (datetime.now(TPE).date() - datetime.strptime(last, "%Y-%m-%d").date()).days
    print(json.dumps({"slug": args.article, "lastDate": last, "daysAgo": days,
                      "ids": sorted(s["id"] for s in hits)}, ensure_ascii=False))
    return 0


# ────────────────── check ──────────────────

def cmd_check(_args):
    errors, warnings = [], []
    log = _load(LOG_PATH, "spores")
    metrics = _load(METRICS_PATH, "events")

    ids = [s.get("id") for s in log["spores"]]
    if len(ids) != len(set(ids)):
        errors.append("spore-log.json: id 重複")
    urls = [s["url"] for s in log["spores"] if s.get("url")]
    dupes = {u for u in urls if urls.count(u) > 1}
    if dupes:
        errors.append(f"spore-log.json: URL 重複 {sorted(dupes)[:3]}")
    for s in log["spores"]:
        for field in ("id", "date", "platform", "slug"):
            if s.get(field) in (None, ""):
                warnings.append(f"#{s.get('id', '?')} 缺 {field}")
                break
        if s.get("date") and not re.match(r"^\d{4}-\d{2}-\d{2}$", s["date"]):
            errors.append(f"#{s['id']} date 格式錯: {s['date']}")

    id_set = set(ids)
    for e in metrics["events"]:
        if e.get("spore") not in id_set:
            errors.append(f"spore-metrics.json: event 指向不存在的 #{e.get('spore')}")
        if all(e.get(k) is None for k in METRIC_KEYS):
            warnings.append(f"#{e.get('spore')} {e.get('batch')}: 全空 event")

    keys = [(e["spore"], e.get("batch"), e.get("dPlus")) for e in metrics["events"]]
    if len(keys) != len(set(keys)):
        errors.append("spore-metrics.json: (spore, batch, dPlus) 重複")

    for msg in errors:
        print(f"❌ {msg}")
    for msg in warnings[:8]:
        print(f"⚠️  {msg}")
    print(f"{'❌ FAIL' if errors else '✅ OK'} — "
          f"{len(log['spores'])} spores / {len(metrics['events'])} events / "
          f"{len(errors)} errors / {len(warnings)} warnings")
    return 2 if errors else 0


# ────────────────── read side: peak join ──────────────────

def _peak_by_spore(events):
    """Per-spore peak (max) of each metric across all its harvest events.

    Harvest is cumulative, so max == latest peak. Returns
    {spore_id: {views, likes, reposts, comments, shares, events, lastAt}}.
    """
    peak = {}
    for e in events:
        sid = e.get("spore")
        if sid is None:
            continue
        p = peak.setdefault(sid, {k: None for k in METRIC_KEYS})
        p["events"] = p.get("events", 0) + 1
        for k in METRIC_KEYS:
            v = e.get(k)
            if v is not None and (p[k] is None or v > p[k]):
                p[k] = v
        at = e.get("at")
        if at and at > (p.get("lastAt") or ""):
            p["lastAt"] = at
    return peak


def _engagement(p):
    """Sum of interaction metrics / peak views. None if views unknown/zero."""
    views = p.get("views")
    if not views:
        return None
    inter = sum(p.get(k) or 0 for k in ("likes", "reposts", "comments", "shares"))
    return inter / views


def cmd_top(args):
    log = _load(LOG_PATH, "spores")
    metrics = _load(METRICS_PATH, "events")
    identity = {s["id"]: s for s in log["spores"]}
    peak = _peak_by_spore(metrics["events"])

    rows = []
    for sid, p in peak.items():
        s = identity.get(sid, {})
        if args.platform and s.get("platform") != args.platform:
            continue
        if args.article and s.get("slug") != args.article:
            continue
        if args.since and (s.get("date") or "") < args.since:
            continue
        eng = _engagement(p)
        key = eng if args.by == "engagement" else p.get(args.by)
        if key is None:
            continue
        rows.append({
            "id": sid, "date": s.get("date"), "platform": s.get("platform"),
            "slug": s.get("slug"), "category": s.get("category"),
            "template": s.get("template"),
            "views": p.get("views"), "likes": p.get("likes"),
            "reposts": p.get("reposts"), "comments": p.get("comments"),
            "shares": p.get("shares"),
            "engagementPct": round(eng * 100, 2) if eng is not None else None,
            "url": s.get("url"), "sortKey": key,
        })
    rows.sort(key=lambda r: r["sortKey"], reverse=True)
    rows = rows[: args.limit]

    if args.json:
        for r in rows:
            r.pop("sortKey", None)
        print(json.dumps({"by": args.by, "count": len(rows), "rows": rows},
                         ensure_ascii=False, indent=2))
        return 0

    def fmt(n):
        return f"{n:,}" if isinstance(n, (int, float)) else "—"

    print(f"# top {len(rows)} by {args.by}"
          + (f" / platform={args.platform}" if args.platform else "")
          + (f" / since={args.since}" if args.since else "")
          + (f" / article={args.article}" if args.article else ""))
    print(f"{'rank':>4} {'id':>5} {'date':<11} {'plat':<8} "
          f"{'views':>9} {'likes':>7} {'eng%':>6}  slug")
    for i, r in enumerate(rows, 1):
        eng = f"{r['engagementPct']:.1f}" if r["engagementPct"] is not None else "—"
        print(f"{i:>4} #{r['id']:>4} {r['date'] or '?':<11} {r['platform'] or '?':<8} "
              f"{fmt(r['views']):>9} {fmt(r['likes']):>7} {eng:>6}  {r['slug'] or '?'}")
    return 0


def cmd_show(args):
    log = _load(LOG_PATH, "spores")
    metrics = _load(METRICS_PATH, "events")
    s = next((x for x in log["spores"] if x["id"] == args.spore), None)
    if not s:
        print(f"❌ spore #{args.spore} 不在 spore-log.json", file=sys.stderr)
        return 3
    events = [e for e in metrics["events"] if e.get("spore") == args.spore]
    events.sort(key=lambda e: (e.get("dPlus") if e.get("dPlus") is not None else -1,
                               e.get("at") or ""))
    if args.json:
        print(json.dumps({"identity": s, "events": events},
                         ensure_ascii=False, indent=2))
        return 0
    print(f"#{s['id']} {s.get('slug')} [{s.get('platform')}] {s.get('date')}"
          f"  {s.get('template') or ''}")
    if s.get("url"):
        print(f"  url: {s['url']}")
    if s.get("highlight"):
        print(f"  ship: {s['highlight']}")
    print(f"  {len(events)} harvest event(s):")
    for e in events:
        shown = " ".join(f"{k}={e[k]:,}" for k in METRIC_KEYS
                         if e.get(k) is not None)
        print(f"    D+{e.get('dPlus')} @ {e.get('at')} [{e.get('batch')}] {shown}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add-spore", help="發孢子後登錄 identity（每平台一筆）")
    a.add_argument("--id", type=int, default=None, help="顯式 id（預設 max+1）")
    a.add_argument("--date", required=True)
    a.add_argument("--lang", default="zh")
    a.add_argument("--platform", required=True)
    a.add_argument("--slug", required=True, help="文章 slug（knowledge 檔名）")
    a.add_argument("--category", default=None)
    a.add_argument("--template", default=None)
    a.add_argument("--url", default=None)
    a.add_argument("--highlight", default=None, help="ship 一句話備註")
    a.set_defaults(fn=cmd_add_spore)

    m = sub.add_parser("add-metrics", help="harvest 後 append 一筆 metric 事件")
    m.add_argument("--spore", type=int, required=True)
    m.add_argument("--d-plus", type=int, required=True)
    m.add_argument("--at", default=None, help="預設現在（TPE wall-clock）")
    m.add_argument("--batch", required=True, help="SPORE-HARVESTS batch 檔名（不含 .md）")
    for k in METRIC_KEYS:
        m.add_argument(f"--{k}", default=None)
    m.add_argument("--source", default="harvest")
    m.set_defaults(fn=cmd_add_metrics)

    l = sub.add_parser("last-spore", help="查文章最近一次發孢子（≥2週 gate 用）")
    l.add_argument("--article", required=True)
    l.set_defaults(fn=cmd_last_spore)

    c = sub.add_parser("check", help="schema + 一致性驗證")
    c.set_defaults(fn=cmd_check)

    t = sub.add_parser("top", help="排名孢子（peak metric，read-only）")
    t.add_argument("--by", default="views",
                   choices=["views", "likes", "reposts", "comments", "shares",
                            "engagement"])
    t.add_argument("--limit", type=int, default=15)
    t.add_argument("--platform", default=None)
    t.add_argument("--since", default=None, help="只看此日期(含)之後發的孢子 YYYY-MM-DD")
    t.add_argument("--article", default=None, help="只看某 slug")
    t.add_argument("--json", action="store_true")
    t.set_defaults(fn=cmd_top)

    sh = sub.add_parser("show", help="單一孢子 identity + metric 歷史（read-only）")
    sh.add_argument("--spore", type=int, required=True)
    sh.add_argument("--json", action="store_true")
    sh.set_defaults(fn=cmd_show)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
