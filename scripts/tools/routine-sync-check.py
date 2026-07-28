#!/usr/bin/env python3
"""
routine-sync-check.py — Routine 飛輪 SSOT vs mirror drift detector

per MANIFESTO §指標 over 複寫 §薄殼鐵律
per REFLEXES #38 status drift = silent killer
per REFLEXES #52 immune system fail-loud
per ROUTINE.md §同步來源 — promised tool, finally written 2026-05-11

Compares docs/semiont/ROUTINE.md SSOT vs
~/.claude/scheduled-tasks/twmd-*/SKILL.md mirrors. Detects:

  ✗ missing mirror   (SSOT lists task but no mirror dir)
  ✗ orphan mirror    (mirror exists but not in SSOT)
  ✗ skill drift      (mirror's name field != SSOT's task title)
  ✗ cron drift       (mirror SKILL.md cron expression != SSOT cron column)
                     ← v2 加入 2026-05-12 routine-v2-resync session
                     ← 觸發：3-layer drift 揭露 SSOT 卡 v1.3 而 mirror 已 v2.0
                     ← cron 全 mismatch，tool 跑出 ok=10 / drift=0 silent pass
  ✗ thick mirror     (mirror > 30 lines = warn, > 50 = hard)
                     per 薄殼鐵律 1: mirrors must be thin pointers

Mirrors should pointer back to ROUTINE.md + canonical pipeline, not
inline Stage steps / quality gates / escalation logic.

v3 live layer（2026-07-05 五病根治，dna-audit §S1 根治）:
    第三層比對來源 = docs/semiont/routine-live-state.json（由 data-refresh session
    呼叫 `mcp__scheduled-tasks__list_scheduled_tasks` → routine-live-normalize.py
    落檔進 git；MCP live state 在 server 內部 store 無 file access，dump 是唯一
    git 可見化路徑）。v3 新增檢查:

      ✗ live_enabled_drift  (SSOT 標 active 但 live disabled，或反過來
                             — 2026-06/07 spore-pick/publish disabled 21 天
                             SSOT 還列實驗中的 v2.9 重演就是這型)
      ✗ live_cron_drift     (SSOT cron 欄 vs live cronExpression)
      ✗ live_orphan         (live 有 twmd task 但 SSOT 沒列)
      ⚠ live_desc_time_drift (live description 內寫的 HH:MM ≠ cron 時間
                             — rewrite-daily description「18:00」vs cron 19:00)
      ⚠ live dump stale > 48h / missing (dump 沒在跟著 data-refresh 更新)

    alias 修補: SSOT `twmd-feedback-triage` 的 mirror/live taskId 是
    `taiwanmd-routine-twmd-feedback-triage`（歷史命名），v2 glob twmd-* 永遠
    找不到它 → chronic false MISSING。v3 以 ALIASES 表對映。

Usage:
    python3 scripts/tools/routine-sync-check.py
    python3 scripts/tools/routine-sync-check.py --format=json
    python3 scripts/tools/routine-sync-check.py --warn-lines=30 --hard-lines=50

Exit code: 0 = pass, 1 = drift / thick mirror / live drift found
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ROUTINE_SSOT = REPO_ROOT / "docs" / "semiont" / "ROUTINE.md"
MIRROR_ROOT = Path(os.path.expanduser("~/.claude/scheduled-tasks"))
LIVE_STATE = REPO_ROOT / "docs" / "semiont" / "routine-live-state.json"

DEFAULT_WARN_LINES = 30
DEFAULT_HARD_LINES = 50
LIVE_DUMP_STALE_HOURS = 48

# SSOT taskId → 實際 mirror dir / live taskId（歷史命名差異）
ALIASES = {
    "twmd-feedback-triage": "taiwanmd-routine-twmd-feedback-triage",
}


def load_live_state():
    """讀 routine-live-state.json dump；回 (tasks_by_id, fetched_at, err)。"""
    if not LIVE_STATE.exists():
        return None, None, "missing"
    try:
        data = json.loads(LIVE_STATE.read_text(encoding="utf-8"))
        tasks = {t["taskId"]: t for t in data.get("tasks", [])}
        return tasks, data.get("fetched_at"), None
    except (json.JSONDecodeError, KeyError) as e:
        return None, None, f"unparsable: {e}"


def dump_age_hours(fetched_at):
    from datetime import datetime, timezone

    try:
        dt = datetime.fromisoformat(fetched_at)
        now = datetime.now(dt.tzinfo or timezone.utc)
        return (now - dt).total_seconds() / 3600
    except (ValueError, TypeError):
        return None


def desc_time_mismatch(description, cron):
    """live description 內出現的 HH:MM 全部 ≠ cron 時間 → 回傳 (desc_times, cron_time)。"""
    if not description or not cron:
        return None
    parts = cron.split()
    if len(parts) != 5 or not parts[0].isdigit() or not parts[1].isdigit():
        return None  # 非單純 m h 型 cron（*/N 等）不比
    cron_time = f"{int(parts[1]):02d}:{int(parts[0]):02d}"
    times = re.findall(r"\b(\d{1,2}):(\d{2})\b", description)
    if not times:
        return None
    norm = {f"{int(h):02d}:{mm}" for h, mm in times}
    if cron_time in norm:
        return None
    return sorted(norm), cron_time


def parse_routine_table(ssot_path):
    """Extract routine task rows from §10 條核心 routine 排程表 markdown table."""
    text = ssot_path.read_text(encoding="utf-8")
    tasks = {}
    in_table = False
    for line in text.splitlines():
        if line.startswith("| TaskId"):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|") or line.startswith("| ---"):
                if line.strip() == "" and tasks:
                    break
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) < 6:
                continue
            task_id_raw = cells[0].strip("`")
            if not task_id_raw.startswith("twmd-"):
                continue
            tasks[task_id_raw] = {
                "title": re.sub(r"\s+¹.*$", "", cells[1]),
                "cron": cells[2].strip("`"),
                "skill": cells[3].strip("`"),
                "model": cells[4],
                "cadence": cells[5],
            }

    # ⏸️ PAUSED 副表（欄位不同：TaskId | 原 slot | 暫停日 | 原因）— 這些任務
    # 在 SSOT 是「已知暫停」，live disabled 是預期，不算 orphan / enabled drift
    m = re.search(r"\*\*⏸️ PAUSED\*\*.*?(?=\n## |\Z)", text, re.DOTALL)
    if m:
        for tid in re.findall(r"`(twmd-[a-z0-9-]+)`", m.group(0)):
            tasks.setdefault(
                tid,
                {
                    "title": tid,
                    "cron": None,
                    "skill": None,
                    "model": None,
                    "cadence": "⏸️ paused（PAUSED 副表）",
                },
            )
    return tasks


def parse_mirror_frontmatter(skill_path):
    """Extract frontmatter name + description from SKILL.md."""
    text = skill_path.read_text(encoding="utf-8")
    fm = {}
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return fm, len(text.splitlines())
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, len(text.splitlines())


def parse_mirror_cron(skill_path):
    """Extract cron expression from SKILL.md prompt body.

    Pattern: cron `0 22 * * *` (backtick-wrapped, 5 fields)
    Returns normalized cron string or None if not found.
    """
    text = skill_path.read_text(encoding="utf-8")
    m = re.search(r"cron\s+`([0-9*/,\-\s]+)`", text)
    if m:
        return " ".join(m.group(1).split())
    return None


def normalize_cron(cron_str):
    """Normalize cron expression for comparison (strip quotes, collapse whitespace)."""
    if not cron_str:
        return None
    return " ".join(cron_str.strip().strip("'\"`").split())


def audit(warn_lines, hard_lines):
    results = {
        "missing": [],
        "orphan": [],
        "drift": [],
        "cron_drift": [],
        "thick": [],
        "ok": [],
    }

    if not ROUTINE_SSOT.exists():
        print(f"❌ ROUTINE SSOT not found: {ROUTINE_SSOT}", file=sys.stderr)
        return results, 2

    ssot_tasks = parse_routine_table(ROUTINE_SSOT)

    mirror_dirs = (
        {
            p.name: p
            for pat in ("twmd-*", "taiwanmd-*")
            for p in MIRROR_ROOT.glob(pat)
            if p.is_dir()
        }
        if MIRROR_ROOT.exists()
        else {}
    )

    for task_id, meta in ssot_tasks.items():
        mirror_dir = mirror_dirs.get(task_id) or mirror_dirs.get(ALIASES.get(task_id, ""))
        if mirror_dir is None:
            results["missing"].append({"task_id": task_id, "meta": meta})
            continue

        skill_md = mirror_dir / "SKILL.md"
        if not skill_md.exists():
            results["missing"].append(
                {"task_id": task_id, "meta": meta, "reason": "no SKILL.md"}
            )
            continue

        fm, line_count = parse_mirror_frontmatter(skill_md)

        if fm.get("name") not in (task_id, ALIASES.get(task_id)):
            results["drift"].append(
                {
                    "task_id": task_id,
                    "field": "name",
                    "ssot": task_id,
                    "mirror": fm.get("name", "<missing>"),
                }
            )

        ssot_cron = normalize_cron(meta.get("cron"))
        mirror_cron = normalize_cron(parse_mirror_cron(skill_md))
        if ssot_cron and mirror_cron and ssot_cron != mirror_cron:
            results["cron_drift"].append(
                {
                    "task_id": task_id,
                    "ssot": ssot_cron,
                    "mirror": mirror_cron,
                }
            )
        # mirror 無可解析 cron 欄位 → 不再列 CRON_DRIFT（v3：mirror prompt 世代已
        # 不含 cron 字樣，SSOT ↔ live 層接手 cron 真相；15 條 <not found> 假陽性
        # 洪水 = alarm fatigue，per REFLEXES #74）

        thick_severity = None
        if line_count > hard_lines:
            thick_severity = "hard"
        elif line_count > warn_lines:
            thick_severity = "warn"

        if thick_severity:
            results["thick"].append(
                {
                    "task_id": task_id,
                    "lines": line_count,
                    "threshold_warn": warn_lines,
                    "threshold_hard": hard_lines,
                    "severity": thick_severity,
                }
            )
        else:
            results["ok"].append({"task_id": task_id, "lines": line_count})

    ssot_ids = set(ssot_tasks.keys())
    aliased_ids = ssot_ids | {ALIASES.get(t, t) for t in ssot_ids}
    for mirror_id in mirror_dirs.keys():
        if mirror_id not in aliased_ids:
            results["orphan"].append({"task_id": mirror_id})

    # ── v3 第三層：SSOT ↔ live scheduler dump ──────────────────────────
    results["live_enabled_drift"] = []
    results["live_cron_drift"] = []
    results["live_orphan"] = []
    results["live_desc_time_drift"] = []
    results["live_dump"] = {"status": "ok", "fetched_at": None, "age_hours": None}

    live_tasks, fetched_at, live_err = load_live_state()
    if live_err:
        results["live_dump"]["status"] = live_err
    else:
        results["live_dump"]["fetched_at"] = fetched_at
        age = dump_age_hours(fetched_at)
        results["live_dump"]["age_hours"] = round(age, 1) if age is not None else None
        if age is not None and age > LIVE_DUMP_STALE_HOURS:
            results["live_dump"]["status"] = f"stale ({age:.0f}h > {LIVE_DUMP_STALE_HOURS}h)"

        for task_id, meta in ssot_tasks.items():
            live = live_tasks.get(task_id) or live_tasks.get(ALIASES.get(task_id, ""))
            if live is None:
                results["live_enabled_drift"].append(
                    {"task_id": task_id, "ssot": meta["cadence"], "live": "<no live task>"}
                )
                continue

            cadence = meta.get("cadence", "")
            expect_disabled = ("⏸" in cadence) or ("disabled" in cadence.lower())
            if bool(live.get("enabled")) == expect_disabled:
                results["live_enabled_drift"].append(
                    {
                        "task_id": task_id,
                        "ssot": cadence,
                        "live": f"enabled={live.get('enabled')}",
                    }
                )

            ssot_cron = normalize_cron(meta.get("cron"))
            live_cron = normalize_cron(live.get("cronExpression"))
            if ssot_cron and live_cron and ssot_cron != live_cron:
                results["live_cron_drift"].append(
                    {"task_id": task_id, "ssot": ssot_cron, "live": live_cron}
                )

            mism = desc_time_mismatch(live.get("description"), live_cron)
            if mism:
                results["live_desc_time_drift"].append(
                    {"task_id": task_id, "desc_times": mism[0], "cron_time": mism[1]}
                )

        for live_id in live_tasks:
            if live_id not in aliased_ids:
                results["live_orphan"].append({"task_id": live_id})

    exit_code = 0
    if (
        results["missing"]
        or results["orphan"]
        or results["drift"]
        or results["cron_drift"]
        or results["live_enabled_drift"]
        or results["live_cron_drift"]
        or results["live_orphan"]
    ):
        exit_code = 1
    if any(t["severity"] == "hard" for t in results["thick"]):
        exit_code = 1

    return results, exit_code


def print_human(results, exit_code):
    print("🧬 routine-sync-check — ROUTINE.md SSOT vs ~/.claude/scheduled-tasks/ mirrors")
    print()

    if results["ok"]:
        print(f"✅ {len(results['ok'])} routine 薄殼合規:")
        for r in results["ok"]:
            print(f"   {r['task_id']:32s} {r['lines']:>3} lines")
        print()

    if results["missing"]:
        print(f"❌ MISSING ({len(results['missing'])}) — SSOT 有但 mirror 缺:")
        for r in results["missing"]:
            print(f"   {r['task_id']}  ({r.get('reason', 'dir missing')})")
        print()

    if results["orphan"]:
        print(f"❌ ORPHAN ({len(results['orphan'])}) — mirror 有但 SSOT 缺:")
        for r in results["orphan"]:
            print(f"   {r['task_id']}")
        print()

    if results["drift"]:
        print(f"❌ DRIFT ({len(results['drift'])}) — SSOT vs mirror 欄位不一致:")
        for r in results["drift"]:
            print(
                f"   {r['task_id']:32s} {r['field']}: ssot='{r['ssot']}' mirror='{r['mirror']}'"
            )
        print()

    if results["cron_drift"]:
        print(
            f"❌ CRON_DRIFT ({len(results['cron_drift'])}) — SSOT cron 欄位 vs mirror SKILL.md cron 不一致 (REFLEXES #38):"
        )
        for r in results["cron_drift"]:
            print(
                f"   {r['task_id']:32s} ssot='{r['ssot']}' mirror='{r['mirror']}'"
            )
        print()

    if results["thick"]:
        print(f"⚠️  THICK ({len(results['thick'])}) — mirror 違反薄殼鐵律 (per MANIFESTO §指標 over 複寫):")
        for r in sorted(results["thick"], key=lambda x: -x["lines"]):
            marker = "🔴" if r["severity"] == "hard" else "🟡"
            print(
                f"   {marker} {r['task_id']:32s} {r['lines']:>3} lines "
                f"(warn>{r['threshold_warn']} hard>{r['threshold_hard']})"
            )
        print()

    # ── v3 live layer 報告 ──────────────────────────────────────────
    dump = results.get("live_dump", {})
    if dump.get("status") == "missing":
        print("⚠️  LIVE DUMP 缺 — docs/semiont/routine-live-state.json 不存在。")
        print("    產生方式: session 呼叫 list_scheduled_tasks → routine-live-normalize.py（per DATA-REFRESH §live dump）")
        print()
    elif dump.get("status", "ok") != "ok":
        print(f"⚠️  LIVE DUMP {dump['status']} — fetched_at={dump.get('fetched_at')}")
        print()

    for key, label in [
        ("live_enabled_drift", "LIVE_ENABLED_DRIFT — SSOT 標示 vs live enabled 不一致（v2.9 spore-pick 21 天漂移就是這型）"),
        ("live_cron_drift", "LIVE_CRON_DRIFT — SSOT cron vs live cronExpression"),
        ("live_orphan", "LIVE_ORPHAN — live 有 twmd task 但 SSOT 沒列"),
    ]:
        rows = results.get(key, [])
        if rows:
            print(f"❌ {label} ({len(rows)}):")
            for r in rows:
                detail = " ".join(f"{k}='{v}'" for k, v in r.items() if k != "task_id")
                print(f"   {r['task_id']:32s} {detail}")
            print()

    if results.get("live_desc_time_drift"):
        print(f"🟡 LIVE_DESC_TIME_DRIFT ({len(results['live_desc_time_drift'])}) — live description 內的時間字樣 ≠ 實際 cron（warn，不影響 exit）:")
        for r in results["live_desc_time_drift"]:
            print(f"   {r['task_id']:32s} desc 提到 {','.join(r['desc_times'])} / cron 實為 {r['cron_time']}")
        print()

    total_routines = len(results["ok"]) + len(results["thick"]) + len(results["missing"])
    hard_thick = sum(1 for t in results["thick"] if t["severity"] == "hard")
    print(
        f"Summary: {total_routines} routines  "
        f"ok={len(results['ok'])}  thick(warn)={len(results['thick']) - hard_thick}  "
        f"thick(hard)={hard_thick}  missing={len(results['missing'])}  "
        f"orphan={len(results['orphan'])}  drift={len(results['drift'])}  "
        f"cron_drift={len(results['cron_drift'])}  "
        f"live_drift={len(results.get('live_enabled_drift', [])) + len(results.get('live_cron_drift', [])) + len(results.get('live_orphan', []))}  "
        f"exit={exit_code}"
    )
    print()
    print(
        "ℹ️  三層比對: SSOT (ROUTINE.md) ↔ mirror (SKILL.md) ↔ live (routine-live-state.json dump)。"
    )
    print(
        "    dump 由 data-refresh session 每日更新（list_scheduled_tasks → routine-live-normalize.py）；"
        f"超過 {LIVE_DUMP_STALE_HOURS}h 未更新會標 stale。"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Routine 飛輪 SSOT vs mirror drift detector"
    )
    parser.add_argument(
        "--warn-lines",
        type=int,
        default=DEFAULT_WARN_LINES,
        help="mirror line threshold for warn (default 30)",
    )
    parser.add_argument(
        "--hard-lines",
        type=int,
        default=DEFAULT_HARD_LINES,
        help="mirror line threshold for hard fail (default 50)",
    )
    parser.add_argument(
        "--format",
        choices=["human", "json"],
        default="human",
        help="output format",
    )
    args = parser.parse_args()

    results, exit_code = audit(args.warn_lines, args.hard_lines)

    if args.format == "json":
        print(json.dumps({"results": results, "exit_code": exit_code}, indent=2))
    else:
        print_human(results, exit_code)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
