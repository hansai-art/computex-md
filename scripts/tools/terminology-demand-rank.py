#!/usr/bin/env python3
"""terminology-demand-rank.py — 用語 per-term 頁的需求驅動 enrich 排序器

把 Search Console 的「{中國詞}台灣用語 / 支語 / 台灣怎麼說 / 是支語嗎」長尾需求，
join 到 data/terminology 詞條的存在性 + 內容豐富度，產出「該先 enrich 哪些詞」的排序清單。

回答的問題：讀者在搜哪些中國詞想知道台灣怎麼說？這些詞我們有沒有詞條？有的話是只有對照
還是有肉？→ 把 enrich 精力放在「高需求 + 缺料」的交集（reports/terminology-page-evolution-2026-06-22.md §3 Layer 2）。

state 分類：
  MISSING     有人搜但詞條不存在 → 該建新詞條
  MAPPING     詞條只有對照、零內文 → 該加肉（origin/usage/example）
  RICH        已有詞源或 usage → 維持

用法:
  terminology-demand-rank.py                 # 近 35 天，表格輸出
  terminology-demand-rank.py --days 28       # 自訂窗口
  terminology-demand-rank.py --json          # 機器可讀（cron / 下游工具）
  terminology-demand-rank.py --top 40        # 只看前 N（預設 60）
  terminology-demand-rank.py --state MISSING # 只看缺詞條的

來源: 2026-06-22 terminology-evolve session 造橋（把一次性 inline 分析儀器化）。
SC lag ~2-3 天，end 預設 today-2。candidate cron: twmd-terminology-demand-weekly。
"""
import argparse
import json
import os
import sys
import pathlib
import glob
from datetime import date, timedelta

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib.sense_client import reexec_in_venv  # noqa: E402

reexec_in_venv()
from lib.sense_client import sc_query  # noqa: E402

# NB: the sense_client venv has no pyyaml, so we parse the (machine-generated,
# consistent block-style) terminology YAML with a minimal 2-level reader rather
# than mutating the shared venv. Only the fields used for ranking are extracted.

ROOT = pathlib.Path(__file__).resolve().parents[2]
TERM_DIR = ROOT / "data" / "terminology"

# Query patterns that signal「我想知道這個中國詞台灣怎麼說 / 算不算支語」intent.
PATTERNS = ["台灣用語", "支語", "台灣怎麼說", "台灣 用語"]
# Wrapper tokens stripped to recover the bare china term from a query.
STRIP = [
    "台灣用語", "是支語嗎", "支語", "台灣怎麼說", "怎麼說",
    "台灣 用語", "的", "台灣", "是", "嗎", " ",
]
PLACEHOLDERS = {"台灣用法", "台灣用語", "中國用法", "中國用語", "用法", "無", ""}


def china_term(q):
    s = q
    for w in STRIP:
        s = s.replace(w, "")
    return s.strip()


def parse_entry(path):
    """Minimal 2-level block-YAML reader for the fields the ranker needs."""
    d, cur = {}, None
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#") or line.lstrip().startswith("- "):
            continue
        if ":" not in line:
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, _, val = line.strip().partition(":")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if indent == 0:
            d[key] = val
            cur = key
        elif cur:
            if not isinstance(d.get(cur), dict):
                d[cur] = {}
            d[cur][key] = val
    return d


def load_index():
    """china-term / id -> parsed entry dict."""
    idx = {}
    for f in glob.glob(str(TERM_DIR / "*.yaml")):
        if os.path.basename(f).startswith("_"):
            continue
        try:
            d = parse_entry(f)
        except Exception:
            continue
        if not d:
            continue
        disp = d.get("display") if isinstance(d.get("display"), dict) else {}
        cn = (disp.get("china") or d.get("china") or "").split("/")[0].strip()
        if cn:
            idx.setdefault(cn, d)
        fid = d.get("id") or os.path.basename(f)[:-5]
        idx.setdefault(fid, d)
    return idx


def entry_state(term, idx):
    d = idx.get(term)
    if not d:
        return ("MISSING", "", "")
    disp = d.get("display") or {}
    tw = disp.get("taiwan") or d.get("taiwan") or ""
    ety = d.get("etymology") or {}

    def real(k):
        v = (ety.get(k) or "").strip()
        return v if v not in PLACEHOLDERS else ""

    usage = d.get("usage") or {}
    has_example = bool((usage.get("example") or "").strip())
    notes = (d.get("notes") or "").strip()
    real_notes = notes and not (notes.startswith("來源") or "CC0" in notes)
    rich = bool(
        real("origin") or real("fork_point") or real("fork_cause")
        or real("taiwan_path") or real("china_path") or has_example or real_notes
    )
    return ("RICH" if rich else "MAPPING", tw, d.get("fork_type") or d.get("type") or "")


def main():
    ap = argparse.ArgumentParser(description="用語頁需求驅動 enrich 排序器")
    ap.add_argument("--days", type=int, default=35)
    ap.add_argument("--top", type=int, default=60)
    ap.add_argument("--state", choices=["MISSING", "MAPPING", "RICH"], default=None)
    ap.add_argument("--min-impr", type=int, default=3)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    end = (date.today() - timedelta(days=2)).isoformat()
    start = (date.today() - timedelta(days=args.days + 2)).isoformat()

    # Pull + merge all pattern queries (dedupe by query string).
    seen_q = {}
    for pat in PATTERNS:
        rows = sc_query(
            ["query"], start, end,
            [{"dimension": "query", "operator": "contains", "expression": pat}],
            row_limit=2000,
        )
        for r in rows:
            q = (r.get("keys") or [""])[0]
            seen_q[q] = r  # same query under multiple patterns → one row

    idx = load_index()
    agg = {}
    for q, r in seen_q.items():
        ct = china_term(q)
        if not ct or len(ct) > 8:
            continue
        a = agg.setdefault(ct, {"impr": 0, "clk": 0, "pos": []})
        a["impr"] += r.get("impressions", 0)
        a["clk"] += r.get("clicks", 0)
        a["pos"].append(r.get("position", 0))

    out = []
    for ct, a in agg.items():
        st, tw, fork = entry_state(ct, idx)
        out.append({
            "china": ct, "impr": a["impr"], "clk": a["clk"],
            "best_pos": round(min(a["pos"]), 1) if a["pos"] else 0,
            "taiwan": tw, "state": st, "fork": fork,
        })
    out.sort(key=lambda x: (-x["impr"], x["best_pos"]))
    out = [r for r in out if r["impr"] >= args.min_impr]
    if args.state:
        out = [r for r in out if r["state"] == args.state]

    tot_impr = sum(r["impr"] for r in out)
    tot_clk = sum(r["clk"] for r in out)
    summary = {
        "window": f"{start}→{end}",
        "distinct_terms": len(out),
        "total_impr": tot_impr,
        "total_clk": tot_clk,
        "ctr_pct": round(100 * tot_clk / tot_impr, 1) if tot_impr else 0,
        "missing": sum(1 for r in out if r["state"] == "MISSING"),
        "mapping_only": sum(1 for r in out if r["state"] == "MAPPING"),
    }

    if args.json:
        print(json.dumps({"summary": summary, "rows": out[: args.top]}, ensure_ascii=False, indent=2))
        return

    print(f"📊 用語需求 enrich 排序  窗口 {summary['window']}")
    print(f"   {summary['distinct_terms']} 中國詞 / {tot_impr} impr / {tot_clk} clk "
          f"/ {summary['ctr_pct']}% CTR | MISSING={summary['missing']} MAPPING={summary['mapping_only']}")
    print(f"\n{'impr':>5}{'clk':>4}{'pos':>6}  {'中國詞':<8}{'→台灣詞':<13}{'state':<9}fork")
    print("-" * 64)
    for r in out[: args.top]:
        flag = "🔴" if r["state"] == "MISSING" else ("🟡" if r["state"] == "MAPPING" else "  ")
        print(f"{r['impr']:>5}{r['clk']:>4}{r['best_pos']:>6}  "
              f"{r['china']:<8}{r['taiwan'][:12]:<13}{r['state']:<9}{r['fork']} {flag}")
    print("\n🔴 MISSING = 建新詞條   🟡 MAPPING = 加肉（origin/usage.example）")


if __name__ == "__main__":
    main()
