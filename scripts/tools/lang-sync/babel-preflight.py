#!/usr/bin/env python3
"""babel-preflight.py — 宿主機算力自檢（任何機器跑 babel 前先照鏡子）。

為什麼存在（2026-07-25）：routine 飛輪遷到專用宿主機之後，
twmd-babel-nightly 在一台跟開發機不同的宿主機上跑。babel 的算力來自四個
互相獨立的來源（OpenRouter key 池／本機 ollama／Tailscale fleet 節點／
codex 訂閱），每一個缺席時 cascade 都會「優雅降級」——也就是**靜默**降級：
沒 key 就只用本機模型，產能剩一半，log 上看起來一切正常。

這正是 2026-07-24 一整天反覆現形的病：靜默失敗比大聲失敗貴得多
（gate 假陽性屠殺好譯文而自報正常、KEYS.md 被當 key 送出、dispatcher 的
`|| true` 吞掉 pre-commit 拒絕）。所以 babel 的入口要有一面鏡子：這台
機器現在有哪些算力、缺哪些、缺的那些會讓產能掉多少，全部說出來。

用法：
  python3 scripts/tools/lang-sync/babel-preflight.py           # 人讀報告
  python3 scripts/tools/lang-sync/babel-preflight.py --json    # 機器可讀
  python3 scripts/tools/lang-sync/babel-preflight.py --strict  # 算力歸零才 exit 1

exit code：0 = 有可用算力（即使部分缺席）；1 = --strict 下算力歸零。
永遠不因「部分缺席」擋下 babel——半條產線好過沒有產線，但缺席必須可見。
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CREDS = Path.home() / ".config" / "taiwan-md" / "credentials"

sys.path.insert(0, str(Path(__file__).resolve().parent))


def check_openrouter_keys() -> dict:
    """key 池：載入數 + 逐把 auth 探測（值不外洩，只回遮罩與狀態）。"""
    try:
        from backends import openrouter as orb
        keys = list(orb._load_all_keys())
    except Exception as e:
        return {"available": False, "count": 0, "error": f"loader 失敗：{e}"}
    if not keys:
        return {"available": False, "count": 0,
                "hint": f"key 池空。放 sk-or-v1-* 單行檔到 {CREDS}/openrouter-keys/*.key"}
    live, dead, credited = [], [], 0
    for name, v in keys:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {v}"})
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                d = json.loads(r.read())["data"]
                live.append(name)
                if not d.get("is_free_tier"):
                    credited += 1
        except Exception:
            dead.append(name)
    return {"available": bool(live), "count": len(keys), "live": len(live),
            "dead": dead, "credited": credited,
            "note": "credited = 已儲值帳戶（日配額約 20×free tier）"}


def check_ollama() -> dict:
    host = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
    try:
        with urllib.request.urlopen(f"{host}/api/tags", timeout=5) as r:
            models = [m["name"] for m in json.loads(r.read()).get("models", [])]
    except Exception as e:
        return {"available": False, "host": host, "error": str(e)[:80],
                "hint": "ollama serve 沒起來，或本機沒裝 ollama"}
    # 翻譯用得上的模型（bge-m3 是 embedding 不算）
    usable = [m for m in models if not m.startswith("bge-")
              and "embed" not in m.lower()]
    return {"available": bool(usable), "host": host,
            "models": usable[:8], "count": len(usable)}


def check_fleet() -> dict:
    """Tailscale fleet 節點可達性（registry 由 muse-bot fleet 維護，跨 repo 只讀）。"""
    reg = Path.home() / "Projects" / "muse-bot" / "fleet" / "registry.json"
    if not reg.exists():
        return {"available": False, "reason": "fleet registry 不在本機（非指揮部機器，正常）"}
    try:
        machines = json.loads(reg.read_text()).get("machines", [])
    except Exception as e:
        return {"available": False, "error": str(e)[:80]}
    reachable = []
    for m in machines:
        hostip = m.get("tailscale_ip") or m.get("host")
        if not hostip or m.get("retired"):
            continue
        url = f"http://{hostip}:11434"
        try:
            with urllib.request.urlopen(f"{url}/api/tags", timeout=4):
                reachable.append(m.get("id", hostip))
        except Exception:
            pass
    return {"available": bool(reachable), "reachable": reachable,
            "total_registered": len(machines)}


def check_track_record(days: int = 2) -> dict:
    """歷史產出品質——端點活著不等於產得出可用的東西。

    2026-07-26 新增。此前 preflight 的 healthy 只證明「端點回得了訊息」：
    l4090 那台機器活著、ollama 有回應、preflight 全綠，而它翻葡萄牙語
    0/28、印尼語 1/20——每一次呼叫都花完整的 GPU 時間翻出必被擋下的成品。
    存活訊號與生產訊號是兩件事（今日同型第五例），算力自檢必須看實績。

    來源：各 run dir 的 report.jsonl（worker × lang 通過率）。
    """
    import glob
    from collections import defaultdict
    from datetime import datetime, timedelta
    cut = (datetime.now().astimezone() - timedelta(days=days)).isoformat()
    grid = defaultdict(lambda: [0, 0])
    for rp in glob.glob("/tmp/babel-unified-2*/report.jsonl"):
        try:
            for line in open(rp, encoding="utf-8"):
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if r.get("ts", "") < cut:
                    continue
                grid[(r.get("worker", "?"), r.get("lang", "?"))][0 if r.get("ok") else 1] += 1
        except Exception:
            continue
    weak = []
    for (w, lang), (ok, fail) in sorted(grid.items()):
        n = ok + fail
        if n >= 8 and ok / n < 0.15:
            weak.append({"worker": w, "lang": lang, "pass_pct": round(ok / n * 100), "n": n})
    return {"samples": sum(ok + fail for ok, fail in grid.values()),
            "weak_pairs": weak,
            "note": "通過率 <15%（n≥8）的 worker×語言組合——切軌或換模型，"
                    "不要靠加大重試（同一個弱適配再燒一次算力）" if weak else "無明顯弱適配"}


def check_codex() -> dict:
    path = shutil.which("codex")
    if not path:
        return {"available": False, "hint": "codex CLI 不在 PATH（訂閱層算力缺席）"}
    r = subprocess.run(["codex", "--version"], capture_output=True, text=True, timeout=20)
    return {"available": r.returncode == 0, "path": path,
            "version": (r.stdout or r.stderr).strip()[:60]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    report = {
        "host": socket.gethostname(),
        "repo": str(REPO),
        "openrouter": check_openrouter_keys(),
        "ollama": check_ollama(),
        "fleet": check_fleet(),
        "codex": check_codex(),
        "track_record": check_track_record(),
    }
    tiers_up = sum(1 for k in ("openrouter", "ollama", "fleet", "codex")
                   if report[k].get("available"))
    report["tiers_available"] = tiers_up
    report["verdict"] = ("no-compute" if tiers_up == 0
                         else ("degraded" if tiers_up < 2 else "healthy"))

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        o, ol, fl, cx = (report["openrouter"], report["ollama"],
                         report["fleet"], report["codex"])
        print(f"🗼 babel 宿主機算力自檢 — {report['host']}")
        print(f"   判定：{report['verdict']}（{tiers_up}/4 層可用）\n")
        if o.get("available"):
            print(f"   ✅ OpenRouter  {o['live']}/{o['count']} 把 key 通過，"
                  f"其中 {o['credited']} 把已儲值")
            if o.get("dead"):
                print(f"      ⚠️ 失效：{', '.join(o['dead'])}")
        else:
            print(f"   ❌ OpenRouter  {o.get('hint') or o.get('error')}")
        if ol.get("available"):
            print(f"   ✅ 本機 ollama {ol['count']} 個可翻譯模型 @ {ol['host']}")
            print(f"      {', '.join(ol['models'])}")
        else:
            print(f"   ❌ 本機 ollama {ol.get('hint') or ol.get('error')}")
        if fl.get("available"):
            print(f"   ✅ fleet 節點  {len(fl['reachable'])} 台可達："
                  f"{', '.join(fl['reachable'])}")
        else:
            print(f"   ➖ fleet 節點  {fl.get('reason') or '全部不可達'}")
        tr = report["track_record"]
        if tr.get("weak_pairs"):
            print(f"   ⚠️ 實績檢查  {len(tr['weak_pairs'])} 個弱適配組合"
                  f"（近兩日 {tr['samples']} 筆）：")
            for wp in tr["weak_pairs"][:6]:
                print(f"      {wp['worker']} × {wp['lang']} = {wp['pass_pct']}%（n={wp['n']}）")
            print(f"      → {tr['note']}")
        elif tr.get("samples"):
            print(f"   ✅ 實績檢查  近兩日 {tr['samples']} 筆，無明顯弱適配")
        print(f"   {'✅' if cx.get('available') else '➖'} codex      "
              f"{cx.get('version') or cx.get('hint')}")
        if report["verdict"] != "healthy":
            print("\n   ⚠️ 算力層缺席會讓 babel 靜默降級（產能掉但 log 看起來正常）。"
                  "\n      缺 key → 只跑本機模型；缺 ollama → 只跑雲端且無主權捕手。")

    if args.strict and tiers_up == 0:
        print("\n🔴 --strict：這台機器沒有任何可用算力，babel 不該起跑。", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
