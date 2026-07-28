#!/usr/bin/env python3
"""progress-snapshot.py — 巴別塔同步率時間序列快照（repo 常駐紀錄）。

把 status.py 的九語 fresh/stale/missing 讀數 append 到
reports/babel/progress-{YYYY-MM}.jsonl（repo 追蹤，每次更新增補 commit），
並同步 append 一段人讀 markdown 到 progress-log-{YYYY-MM}.md
（九語表＋對上一筆的 delta＋可選 note）。哲宇 directive 2026-07-24
「把這些進度也完整記錄留在 repo 裡面，每一次更新都增補」。

用法：
  python3 scripts/tools/lang-sync/progress-snapshot.py                # 快照 + JSONL + MD
  python3 scripts/tools/lang-sync/progress-snapshot.py --note "..."  # MD 段加產線備註
  python3 scripts/tools/lang-sync/progress-snapshot.py --last 5      # 印最近 N 列
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT_DIR = REPO / "reports" / "babel"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from langs import ALL_TRANSLATION_LANGS  # noqa: E402


def out_paths(now: datetime) -> tuple[Path, Path]:
    ym = now.strftime("%Y-%m")
    return (OUT_DIR / f"progress-{ym}.jsonl", OUT_DIR / f"progress-log-{ym}.md")


def snapshot() -> dict:
    subprocess.run(
        ["python3", "scripts/tools/lang-sync/status.py"],
        cwd=REPO, capture_output=True, text=True,
    )
    data = json.loads((REPO / "knowledge" / "_translation-status.json").read_text())
    summary = data["_meta"]["summary"]
    row = {"ts": datetime.now().astimezone().isoformat(timespec="seconds"),
           "total_zh": data["_meta"]["totalZh"], "langs": {}}
    for lang in ALL_TRANSLATION_LANGS:
        s = summary.get(lang, {})
        row["langs"][lang] = {
            "fresh": s.get("fresh", 0),
            "stale": s.get("stale", 0) + s.get("metadata_stale", s.get("metadataStale", 0)),
            "missing": s.get("missing", 0),
        }
    return row


def _node_endpoints() -> dict:
    """節點端點從 fleet registry derive，不寫死在 repo。

    2026-07-25 哲宇 callout：機器位址與帳號屬本機環境細節，寫進公開 repo
    等於把內網拓撲送出去；要記就記在 local machine config／local profile。
    registry 由 muse-bot fleet 維護（gitignored 的本機檔），這裡只讀。
    """
    out = {"local": "http://127.0.0.1:11434"}
    reg = Path.home() / "Projects" / "muse-bot" / "fleet" / "registry.json"
    try:
        for m in json.loads(reg.read_text()).get("machines", []):
            addr = m.get("tailscale_ip") or m.get("host")
            if addr and not m.get("retired") and m.get("id"):
                out[m["id"]] = f"http://{addr}:11434"
    except Exception:
        pass  # 非指揮部機器沒有 registry — 只探本機，正常
    return out


def _probe(url: str) -> bool:
    import urllib.request
    try:
        urllib.request.urlopen(f"{url}/api/version", timeout=3)
        return True
    except Exception:
        return False


def collect_node_stats() -> dict:
    """每節點／worker 的累計 ok/fail/平均秒數＋存活探測。

    來源：babel-dispatch run dirs 的 report.jsonl（worker 級，含秒數與
    fail_reason）＋ legacy fleet dispatcher 的 batch-report-*.jsonl
    （node 級，無時間戳，取累計）＋ ollama endpoint 探活。delta 由
    讀者對照上一筆 nodes 自算（本工具存絕對累計，不存差分）。
    """
    import glob
    from collections import Counter, defaultdict
    nodes: dict = {}

    agg = defaultdict(lambda: {"ok": 0, "fail": 0, "secs": 0.0,
                               "reasons": Counter(), "last_ts": ""})
    for rp in glob.glob("/tmp/babel-unified-2*/report.jsonl"):
        for line in open(rp, encoding="utf-8"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            a = agg[f"worker:{r.get('worker', '?')}"]
            if r.get("ok"):
                a["ok"] += 1
                a["secs"] += r.get("seconds", 0)
            else:
                a["fail"] += 1
                a["reasons"][(r.get("fail_reason") or "?")[:24]] += 1
            a["last_ts"] = max(a["last_ts"], r.get("ts", ""))
    for name, a in agg.items():
        nodes[name] = {
            "ok": a["ok"], "fail": a["fail"],
            "avg_s": round(a["secs"] / a["ok"], 1) if a["ok"] else None,
            "top_fail": a["reasons"].most_common(2),
            "last_activity": a["last_ts"] or None,
        }

    for rp in glob.glob("/tmp/babel-fleet-*/batch-report-*.jsonl"):
        node = Path(rp).stem.replace("batch-report-", "")
        ok = fail = 0
        reasons: Counter = Counter()
        for line in open(rp, encoding="utf-8"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("ok"):
                ok += 1
            else:
                fail += 1
                reason = ("health" if r.get("health_fail")
                          else ("leak" if r.get("leak_fail")
                                else f"verify={r.get('verify_fails')}"))
                reasons[reason] += 1
        nodes[f"fleet:{node}"] = {"ok": ok, "fail": fail, "avg_s": None,
                                  "top_fail": reasons.most_common(2),
                                  "last_activity": None}

    for name, url in _node_endpoints().items():
        nodes.setdefault(f"endpoint:{name}", {})["alive"] = _probe(url)
    return nodes


def append_md(md_path: Path, row: dict, prev: dict | None, note: str) -> None:
    ts = row["ts"]
    total = row["total_zh"]
    lines = []
    if not md_path.exists():
        lines.append("# 巴別塔同步進度日誌\n")
        lines.append("> 每次更新增補一段（producer: `progress-snapshot.py`，"
                     "資料源同目錄 `progress-*.jsonl`）。fresh=最新 / "
                     "stale=可讀待刷新 / missing=無頁面。\n")
    lines.append(f"\n## {ts}（zh 總數 {total}）\n")
    lines.append("| 語言 | fresh | stale | missing | 覆蓋率 | Δfresh | Δmissing |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    gap = gap_prev = 0
    for lang in ALL_TRANSLATION_LANGS:
        c = row["langs"][lang]
        gap += c["stale"] + c["missing"]
        cov = (total - c["missing"]) / total * 100
        if prev and lang in prev.get("langs", {}):
            p = prev["langs"][lang]
            gap_prev += p["stale"] + p["missing"]
            df, dm = c["fresh"] - p["fresh"], c["missing"] - p["missing"]
            dfs = f"+{df}" if df > 0 else (str(df) if df else "·")
            dms = f"+{dm}" if dm > 0 else (str(dm) if dm else "·")
        else:
            dfs = dms = "—"
        lines.append(f"| {lang} | {c['fresh']} | {c['stale']} | {c['missing']}"
                     f" | {cov:.1f}% | {dfs} | {dms} |")
    if prev:
        d = gap - gap_prev
        arrow = "▼" if d < 0 else ("▲" if d > 0 else "＝")
        lines.append(f"\n總缺口（stale+missing）：**{gap}**（{arrow}{abs(d)} vs 上一筆）")
    else:
        lines.append(f"\n總缺口（stale+missing）：**{gap}**")

    nodes = row.get("nodes") or {}
    workers = {k: v for k, v in nodes.items() if not k.startswith("endpoint:")}
    if workers:
        prev_nodes = (prev or {}).get("nodes") or {}
        lines.append("\n**節點／worker**（ok/fail 為累計；Δ為對上一筆）\n")
        lines.append("| 節點 | ok | fail | Δok | 平均秒 | 主要 fail |")
        lines.append("| --- | ---: | ---: | ---: | ---: | --- |")
        for name in sorted(workers):
            v = workers[name]
            pv = prev_nodes.get(name, {})
            dok = v.get("ok", 0) - pv.get("ok", 0) if pv else None
            doks = (f"+{dok}" if dok and dok > 0 else (str(dok) if dok else "·")) if pv else "—"
            top = "；".join(f"{r}×{c}" for r, c in (v.get("top_fail") or [])) or "—"
            avg = v.get("avg_s")
            lines.append(f"| {name} | {v.get('ok', 0)} | {v.get('fail', 0)}"
                         f" | {doks} | {avg if avg is not None else '—'} | {top} |")
        probes = {k.split(':', 1)[1]: v.get("alive")
                  for k, v in nodes.items() if k.startswith("endpoint:")}
        if probes:
            alive = "、".join(f"{n} {'🟢' if a else '🔴'}" for n, a in probes.items())
            lines.append(f"\nendpoint 探活：{alive}")
    if note:
        lines.append(f"\n{note}")
    with open(md_path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--last", type=int, default=0)
    ap.add_argument("--note", default="", help="附在本次 MD 段的產線備註")
    args = ap.parse_args()
    now = datetime.now().astimezone()
    jsonl_path, md_path = out_paths(now)
    if args.last:
        lines = jsonl_path.read_text().splitlines() if jsonl_path.exists() else []
        for ln in lines[-args.last:]:
            print(ln)
        return
    prev = None
    if jsonl_path.exists():
        tail = jsonl_path.read_text().splitlines()
        if tail:
            prev = json.loads(tail[-1])
    row = snapshot()
    row["nodes"] = collect_node_stats()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(jsonl_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    append_md(md_path, row, prev, args.note)
    print(json.dumps(row, ensure_ascii=False))
    print(f"→ {jsonl_path.relative_to(REPO)} + {md_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
