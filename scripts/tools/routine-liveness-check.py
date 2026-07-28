#!/usr/bin/env python3
"""
routine-liveness-check.py — fire-vs-commit 對賬：抓 routine 的沉默死亡

per weekly-deep-review 2026-07-10 §五 + evolution-roadmap P0-1：
scheduler 的 lastRunAt 只證明扳機被按下；routine 真正的完成證明是 git 痕跡。
機器睡眠或 cron 環境層病可以讓 session 在 fire 後無聲死亡——routine-status.sh
靠 memory 檔偵測 fire，所以「該來沒來的班」完全不可見；scheduler 又只記扳機。
兩個資料源各自誠實，交叉才見屍體（2026-07-10 morning chain 六連沉默死亡 vc=2，
前例 2026-07-04 rewrite-daily，LESSONS `routine-fire-vs-git-trace-silent-death`）。

資料源：
  - docs/semiont/routine-live-state.json（scheduler dump，data-refresh rider 每日更新）
  - git log（fire 之後 TRACE_WINDOW 小時內找該 routine 的 commit 痕跡）

判定（對最近一次 lastRunAt）：
  ✅ traced        fire 後 TRACE_WINDOW 內有對應 tag 的 commit
  🕐 in-grace      fire 距今 < GRACE_HOURS，session 可能還在跑，不判
  🔴 silent-death  fire 距今 ≥ GRACE_HOURS 且窗口內零 git 痕跡
  ⏸️ disabled      live enabled=false，跳過
  ⚪ stale-dump    dump 本身超過 DUMP_STALE_HOURS，先跑 routine-live-normalize.py

用法：
  python3 scripts/tools/routine-liveness-check.py            # 人讀表
  python3 scripts/tools/routine-liveness-check.py --json     # 給 generate-dashboard-alerts.mjs
  python3 scripts/tools/routine-liveness-check.py --grace 2  # 覆寫 grace（小時）

下游消費者：
  - WEEKLY-REPORT-PIPELINE v4.0 Stage 2.5a（週體檢診斷面 a）
  - generate-dashboard-alerts.mjs（silent-death → yellow alert，owner=該 routine）
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LIVE_STATE = REPO_ROOT / "docs" / "semiont" / "routine-live-state.json"

GRACE_HOURS = 3        # fire 後多久內不判（session 可能還在跑）
TRACE_WINDOW_HOURS = 6  # fire 後多久內找 git 痕跡
DUMP_STALE_HOURS = 48   # dump 超齡警告（sync-check 同一條線）

# taskId → git log subject 的 grep pattern（跟 memory 檔 handle / commit 標記一致）
# 新 routine 誕生時必須同 commit 補這張表（REFLEXES #43 家族：新器官必須進 sensor 視野）
TAG_PATTERNS: dict[str, list[str]] = {
    "twmd-data-refresh-am": ["data-refresh-am", "twmd-data-refresh-am"],
    "twmd-data-refresh-pm": ["data-refresh-pm", "twmd-data-refresh-pm"],
    "twmd-babel-nightly": ["twmd-babel"],
    "twmd-embeddings-nightly": ["embeddings"],
    "twmd-maintainer-daily": [
        "twmd-maintainer-daily", "maintainer-daily",
        "twmd-maintainer-am", "maintainer-am", "twmd-maintainer:",
    ],
    "twmd-maintainer-pm": ["twmd-maintainer-pm", "maintainer-pm"],
    "twmd-spore-harvest-am": ["twmd-spore-harvest", "spore-harvest"],
    "taiwanmd-routine-twmd-feedback-triage": ["twmd-feedback-triage", "feedback-triage"],
    "twmd-rewrite-daily": ["twmd-rewrite-daily", "rewrite-daily", "[semiont] rewrite:", "[routine] rewrite:"],
    "twmd-news-lens-weekly": ["news-lens"],
    "twmd-weekly-report-sun": ["weekly-report", "twmd-weekly-report", "report: weekly"],
    "twmd-distill-weekly": ["distill"],
    "twmd-self-evolve-weekly": ["self-evolve"],
    "twmd-routine-audit-weekly": ["routine-audit"],
    "twmd-spore-pick-daily": ["spore-pick"],
    "twmd-spore-publish-daily": ["spore-publish"],
    "twmd-routine-sync": ["twmd-routine-sync"],
    "twmd-supporters-weekly": ["twmd-supporters-weekly", "supporters"],
    "twmd-music-media-audit-weekly": ["music-media-audit"],
}


def _git_subjects(since: datetime, until: datetime) -> list[str]:
    out = subprocess.run(
        [
            "git", "log",
            f"--since={since.isoformat()}",
            f"--until={until.isoformat()}",
            "--pretty=format:%h %s",
        ],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    return [l for l in out.stdout.splitlines() if l.strip()]


def check(grace_hours: float, window_hours: float) -> dict:
    if not LIVE_STATE.exists():
        return {"error": f"{LIVE_STATE} 不存在 — 先跑 routine-live-normalize.py"}

    state = json.loads(LIVE_STATE.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    fetched = datetime.fromisoformat(state.get("fetched_at", "1970-01-01T00:00:00+00:00"))
    dump_age_h = (now - fetched).total_seconds() / 3600

    results = []
    for t in state.get("tasks", []):
        task_id = t.get("taskId", "?")
        if not t.get("enabled", False):
            results.append({"taskId": task_id, "status": "disabled"})
            continue
        last_run = t.get("lastRunAt")
        if not last_run:
            results.append({"taskId": task_id, "status": "never-ran"})
            continue

        fire = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
        age_h = (now - fire).total_seconds() / 3600

        if age_h < grace_hours:
            results.append({"taskId": task_id, "status": "in-grace",
                            "firedAt": last_run, "ageHours": round(age_h, 1)})
            continue

        patterns = TAG_PATTERNS.get(task_id, [task_id])
        subjects = _git_subjects(fire, fire + timedelta(hours=window_hours))
        hits = [s for s in subjects
                if any(p.lower() in s.lower() for p in patterns)]

        results.append({
            "taskId": task_id,
            "status": "traced" if hits else "silent-death",
            "firedAt": last_run,
            "ageHours": round(age_h, 1),
            "evidence": hits[0] if hits else None,
        })

    return {
        "checkedAt": now.isoformat(),
        "dumpFetchedAt": state.get("fetched_at"),
        "dumpAgeHours": round(dump_age_h, 1),
        "dumpStale": dump_age_h > DUMP_STALE_HOURS,
        "graceHours": grace_hours,
        "traceWindowHours": window_hours,
        "silentDeaths": sum(1 for r in results if r["status"] == "silent-death"),
        "results": results,
    }


ICONS = {"traced": "✅", "in-grace": "🕐", "silent-death": "🔴",
         "disabled": "⏸️", "never-ran": "❓"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--grace", type=float, default=GRACE_HOURS)
    ap.add_argument("--window", type=float, default=TRACE_WINDOW_HOURS)
    args = ap.parse_args()

    report = check(args.grace, args.window)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if "error" in report:
        print(f"⚠️  {report['error']}")
        return 1

    print("🧬 routine-liveness-check — fire-vs-commit 對賬"
          f"（dump 齡 {report['dumpAgeHours']}h"
          f"{'，⚪ STALE 建議先 refresh dump' if report['dumpStale'] else ''}）\n")
    for r in report["results"]:
        icon = ICONS.get(r["status"], "?")
        line = f"  {icon} {r['taskId']:42s} {r['status']}"
        if r.get("firedAt"):
            line += f"  fire={r['firedAt'][:16]}"
        if r.get("evidence"):
            line += f"  → {r['evidence'][:60]}"
        print(line)
    print(f"\nSummary: silent-death={report['silentDeaths']} "
          f"(grace={report['graceHours']}h / window={report['traceWindowHours']}h)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
