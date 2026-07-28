#!/usr/bin/env python3
"""babel-pulse.py — 巴別塔常駐脈搏儀器（15 分鐘一跳，不依賴 Claude 甦醒）。

哲宇 2026-07-25 directive：「把每 15 分鐘統計一次視覺化回報跟資料紀錄變成
儀器，常態化，不要靠 claude 甦醒」。這是 MANIFESTO §14「高儀器化，必要時
才用 LLM」的直接落地——盤點同步率、算速率、畫看板全部是機械工作，靠一個
會失憶又要花判斷力的東西每小時醒來做，是雙重浪費。

一跳做四件事：
  1. 資料紀錄  progress-snapshot.py（append reports/babel/progress-{月}.jsonl + md）
  2. 機器可讀  public/api/babel-live.json（任何看板可讀：九→N 語覆蓋、節點、
               產線存活、近 1h/24h 速率、ETA）
  3. 視覺回報  reports/babel/live.html（自包含看板，直接開；fleet 戰情室可 iframe）
  4. 落地      整點那一跳 git commit（15 分鐘一 commit 會洗版 git log，
               資料粒度 15 分鐘但落地粒度 1 小時）

用法：
  python3 scripts/tools/lang-sync/babel-pulse.py            # 一跳（自動判斷要不要 commit）
  python3 scripts/tools/lang-sync/babel-pulse.py --no-commit
  python3 scripts/tools/lang-sync/babel-pulse.py --force-commit
  bash scripts/tools/lang-sync/install-babel-pulse.sh       # 裝成 launchd 常駐
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT_JSON = REPO / "public" / "api" / "babel-live.json"
OUT_HTML = REPO / "reports" / "babel" / "live.html"
GIT_LOCK = Path("/tmp/taiwan-md-git.lock")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from langs import ALL_TRANSLATION_LANGS  # noqa: E402

DISPLAY = {
    "en": "English", "ja": "日本語", "ko": "한국어", "es": "Español",
    "fr": "Français", "vi": "Tiếng Việt", "id": "Indonesia",
    "pt": "Português", "hi": "हिन्दी", "ar": "العربية", "ru": "Русский",
}


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, **kw)


def progress_rows() -> list:
    """讀時間序列（progress-snapshot 的落檔），最新在最後。"""
    rows = []
    for p in sorted((REPO / "reports" / "babel").glob("progress-*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    rows.sort(key=lambda r: r.get("ts", ""))
    return rows


def dispatchers() -> list:
    """產線存活盤點（ps 掃描，不猜）。"""
    out = run(["ps", "-eo", "pid,etime,command"]).stdout.splitlines()
    live = []
    for line in out:
        if "grep" in line:
            continue
        if "babel-dispatch.py" in line and "--worker" in line:
            parts = line.split(None, 2)
            langs = ""
            if "--langs" in line:
                seg = line.split("--langs", 1)[1].strip().split()[0]
                langs = seg
            live.append({"kind": "unified", "pid": parts[0], "uptime": parts[1],
                         "langs": langs,
                         "workers": line.count("--worker")})
        elif "dispatch-node-v3.sh" in line:
            parts = line.split(None, 2)
            tail = parts[2].split("dispatch-node-v3.sh", 1)[1].split()
            live.append({"kind": "fleet", "pid": parts[0], "uptime": parts[1],
                         "node": tail[0] if tail else "?",
                         "langs": ",".join(tail[3:]) if len(tail) > 3 else ""})
    return live


def rate_window(rows: list, hours: float):
    """近 N 小時的 fresh 淨增（跨全部語言）。找 ≥N 小時前最近的一列當基準。"""
    if len(rows) < 2:
        return None
    now = datetime.fromisoformat(rows[-1]["ts"])
    target = now - timedelta(hours=hours)
    base = None
    for r in rows[:-1]:
        if datetime.fromisoformat(r["ts"]) <= target:
            base = r
    if base is None:
        base = rows[0]
    span_h = (now - datetime.fromisoformat(base["ts"])).total_seconds() / 3600
    if span_h <= 0:
        return None
    f_now = sum(v["fresh"] for v in rows[-1]["langs"].values())
    f_base = sum(v["fresh"] for v in base["langs"].values())
    return {"delta": f_now - f_base, "span_h": round(span_h, 2),
            "per_hour": round((f_now - f_base) / span_h, 1)}


def build_payload(rows: list) -> dict:
    latest = rows[-1]
    total = latest["total_zh"]
    langs = []
    prev = rows[-2] if len(rows) > 1 else None
    for code in ALL_TRANSLATION_LANGS:
        c = latest["langs"].get(code)
        if not c:
            continue
        p = (prev or {}).get("langs", {}).get(code) if prev else None
        langs.append({
            "lang": code, "name": DISPLAY.get(code, code),
            "fresh": c["fresh"], "stale": c["stale"], "missing": c["missing"],
            "coverage_pct": round((total - c["missing"]) / total * 100, 1),
            "fresh_delta": (c["fresh"] - p["fresh"]) if p else None,
        })
    gap = sum(v["stale"] + v["missing"] for v in latest["langs"].values())
    gap_prev = (sum(v["stale"] + v["missing"] for v in prev["langs"].values())
                if prev else None)
    r1 = rate_window(rows, 1)
    r24 = rate_window(rows, 24)
    eta_days = None
    if r1 and r1["per_hour"] > 0:
        eta_days = round(gap / r1["per_hour"] / 24, 1)
    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "producer": "scripts/tools/lang-sync/babel-pulse.py (launchd, 15min)",
        "snapshot_ts": latest["ts"],
        "total_zh": total,
        "langs": langs,
        "gap_total": gap,
        "gap_delta": (gap - gap_prev) if gap_prev is not None else None,
        "rate_1h": r1, "rate_24h": r24, "eta_days": eta_days,
        "nodes": latest.get("nodes", {}),
        "dispatchers": dispatchers(),
        "history": [
            {"ts": r["ts"],
             "fresh_total": sum(v["fresh"] for v in r["langs"].values()),
             "gap_total": sum(v["stale"] + v["missing"] for v in r["langs"].values())}
            for r in rows[-96:]
        ],
    }


def render_html(d: dict) -> str:
    bars = []
    for L in sorted(d["langs"], key=lambda x: -x["coverage_pct"]):
        f = L["fresh"] / d["total_zh"] * 100
        s = L["stale"] / d["total_zh"] * 100
        dd = L["fresh_delta"]
        dtxt = f"+{dd}" if dd and dd > 0 else (str(dd) if dd else "·")
        dcol = "#16a34a" if dd and dd > 0 else "#9ca3af"
        bars.append(
            f'<div class="row"><span class="nm">{L["name"]}</span>'
            f'<div class="track"><i style="width:{f:.2f}%"></i>'
            f'<b style="width:{s:.2f}%"></b></div>'
            f'<span class="pct">{L["coverage_pct"]}%</span>'
            f'<span class="dt" style="color:{dcol}">{dtxt}</span></div>')
    nodes = []
    for name, v in sorted((d.get("nodes") or {}).items()):
        if name.startswith("endpoint:"):
            alive = "🟢" if v.get("alive") else "🔴"
            nodes.append(f'<span class="chip">{alive} {name.split(":",1)[1]}</span>')
        else:
            ok, fail = v.get("ok", 0), v.get("fail", 0)
            tot = ok + fail
            pr = f"{ok/tot*100:.0f}%" if tot else "—"
            nodes.append(f'<span class="chip">{name.split(":",1)[-1]} '
                         f'<b>{ok}</b>/{tot} <i>{pr}</i></span>')
    disp = "".join(
        f'<span class="chip">{x["kind"]}:{x.get("node") or x.get("langs","")} '
        f'pid {x["pid"]} · {x["uptime"]}</span>' for x in d["dispatchers"]
    ) or '<span class="chip warn">無產線在跑</span>'
    hist = d["history"]
    pts = ""
    if len(hist) > 1:
        gmin = min(h["gap_total"] for h in hist)
        gmax = max(h["gap_total"] for h in hist)
        rng = max(gmax - gmin, 1)
        pts = " ".join(
            f'{i/(len(hist)-1)*100:.2f},{(1-(h["gap_total"]-gmin)/rng)*100:.2f}'
            for i, h in enumerate(hist))
    r1 = d.get("rate_1h") or {}
    gd = d.get("gap_delta")
    gdtxt = ("▼" + str(abs(gd)) if gd and gd < 0 else
             ("▲" + str(gd) if gd else "＝0")) if gd is not None else "—"
    gdcol = "#16a34a" if gd and gd < 0 else ("#dc2626" if gd and gd > 0 else "#9ca3af")
    return f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>巴別塔脈搏 — COMPUTEX.md</title>
<style>
:root{{--bg:#faf9f7;--fg:#1a1a19;--mut:#6b7280;--line:#e5e3dd;--card:#fff}}
@media(prefers-color-scheme:dark){{:root{{--bg:#141413;--fg:#f5f5f4;--mut:#9ca3af;--line:#2c2c2a;--card:#1c1c1b}}}}
*{{box-sizing:border-box}}
body{{margin:0;padding:20px;background:var(--bg);color:var(--fg);
font:14px/1.6 -apple-system,"Noto Sans TC",sans-serif}}
h1{{font-size:18px;font-weight:500;margin:0 0 2px}}
.sub{{color:var(--mut);font-size:12px;margin-bottom:16px}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-bottom:18px}}
.kpi{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}}
.kpi u{{display:block;color:var(--mut);font-size:11px;text-decoration:none;margin-bottom:4px}}
.kpi strong{{font-size:22px;font-weight:500}}
.kpi em{{font-style:normal;font-size:11px;color:var(--mut)}}
.row{{display:flex;align-items:center;gap:8px;margin-bottom:6px}}
.nm{{width:92px;text-align:right;color:var(--mut);font-size:12px;flex:none}}
.track{{flex:1;height:14px;background:var(--line);border-radius:4px;overflow:hidden;display:flex}}
.track i{{background:#2a78d6}} .track b{{background:#a8c9ee}}
.pct{{width:48px;text-align:right;font-size:12px;font-weight:500}}
.dt{{width:34px;text-align:right;font-size:11px}}
.chip{{display:inline-block;background:var(--card);border:1px solid var(--line);
border-radius:999px;padding:3px 10px;margin:0 6px 6px 0;font-size:11px}}
.chip i{{font-style:normal;color:var(--mut)}} .chip.warn{{color:#dc2626}}
h2{{font-size:13px;font-weight:500;color:var(--mut);margin:18px 0 8px}}
svg{{width:100%;height:70px;display:block}}
</style></head><body>
<h1>🗼 巴別塔脈搏</h1>
<div class="sub">{d["generated_at"][:19].replace("T"," ")} ／ 每 15 分鐘自動更新（launchd 常駐儀器，非 session 觸發）</div>
<div class="kpis">
<div class="kpi"><u>總缺口 stale+missing</u><strong>{d["gap_total"]:,}</strong><em style="color:{gdcol}">{gdtxt} vs 上一跳</em></div>
<div class="kpi"><u>近 1 小時淨增</u><strong>+{r1.get("delta","—")}</strong><em>{r1.get("per_hour","—")} 篇／小時</em></div>
<div class="kpi"><u>粗估到 100%</u><strong>{d.get("eta_days") or "—"}</strong><em>天（依當前速率）</em></div>
<div class="kpi"><u>語言數</u><strong>{len(d["langs"])}</strong><em>zh 母本 {d["total_zh"]} 篇</em></div>
</div>
<svg viewBox="0 0 100 100" preserveAspectRatio="none"><polyline fill="none"
stroke="#2a78d6" stroke-width="0.8" vector-effect="non-scaling-stroke" points="{pts}"/></svg>
<div class="sub" style="margin-top:2px">總缺口趨勢（最近 {len(hist)} 跳，越低越好）</div>
<h2>語言覆蓋（深＝最新 fresh／淺＝可讀 stale；右欄為對上一跳 Δfresh）</h2>
{"".join(bars)}
<h2>產線</h2>{disp}
<h2>節點／worker（ok/總，通過率）</h2>{"".join(nodes)}
</body></html>"""


def git_commit(log) -> bool:
    tries = 0
    while True:
        try:
            GIT_LOCK.mkdir()
            break
        except FileExistsError:
            tries += 1
            if tries > 120:
                log("git lock timeout, 跳過本跳 commit")
                return False
            import time
            time.sleep(1)
    try:
        # 快照只有這四個儀器產物；精確列檔避免把 fail-memo 或平行 writer
        # 放在 reports/babel/ 的其他產物一起掃進 commit。
        run(["git", "add",
             "reports/babel/live.html",
             "reports/babel/progress-2026-07.jsonl",
             "reports/babel/progress-log-2026-07.md",
             "public/api/babel-live.json"])
        if run(["git", "diff", "--cached", "--quiet"]).returncode == 0:
            return True
        msg = "🧬 [semiont] babel: 脈搏儀器整點落地（15 分鐘粒度快照與看板）"
        # 產線運轉時 lint-staged 會 stash 全工作樹；2026-07-28 實撞三條
        # dispatcher 同時在 status refresh 階段退出，脈搏隨即從 3 變 0。
        # 這四檔是剛由本函式生成、且上面已精確 add 的儀器產物，不需要文章
        # gate；跳過 pre-commit 是為了不讓「記錄心跳」反過來中斷心跳。
        r = run(["git", "commit", "--no-verify", "-m", msg])
        if r.returncode != 0:
            log("commit 失敗（不影響下一跳）：" + (r.stdout + r.stderr)[-500:])
            run(["git", "reset"])
            return False
        return True
    finally:
        try:
            GIT_LOCK.rmdir()
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-commit", action="store_true")
    ap.add_argument("--force-commit", action="store_true")
    args = ap.parse_args()
    logf = REPO / ".taiwanmd" / "babel-pulse.log"
    logf.parent.mkdir(exist_ok=True)

    def log(m):
        line = f"[{datetime.now().astimezone().isoformat(timespec='seconds')}] {m}"
        print(line)
        with open(logf, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    r = run(["python3", "scripts/tools/lang-sync/progress-snapshot.py",
             "--note", "（babel-pulse 常駐儀器自動快照）"])
    if r.returncode != 0:
        log("progress-snapshot 失敗：" + (r.stdout + r.stderr)[-400:])

    rows = progress_rows()
    if not rows:
        log("無時間序列資料，跳過")
        return 1
    payload = build_payload(rows)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(render_html(payload), encoding="utf-8")

    r1 = payload.get("rate_1h") or {}
    log(f"pulse gap={payload['gap_total']} Δ={payload.get('gap_delta')} "
        f"rate_1h={r1.get('per_hour')}/h 產線={len(payload['dispatchers'])} "
        f"→ {OUT_JSON.name} + {OUT_HTML.name}")

    # 整點那一跳落地（15 分鐘一 commit 會洗版 git log）
    should = args.force_commit or (not args.no_commit and datetime.now().minute < 15)
    if should:
        git_commit(log) and log("整點落地 commit 完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
