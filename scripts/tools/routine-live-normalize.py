#!/usr/bin/env python3
"""
routine-live-normalize.py — scheduler live 狀態 → git 可見的 normalized dump

per dna-audit 2026-07-05 §S1 根治方向：「把 live scheduler 狀態變成 git 可見」。
MCP scheduled-tasks 的 live 狀態存在 server 內部 store（mirror 目錄只有 SKILL.md，
無 config json），bash 工具讀不到 —— 所以 dump 必須由 session 呼叫
`mcp__scheduled-tasks__list_scheduled_tasks` 後，把原始 JSON 餵給本工具落檔。

用法（data-refresh session 的 rider step，per DATA-REFRESH-PIPELINE §live dump）：
    1. session 呼叫 list_scheduled_tasks，把回傳 JSON 存到暫存檔
    2. python3 scripts/tools/routine-live-normalize.py <raw.json> [--session <id>]
    3. 產出 docs/semiont/routine-live-state.json（跟著 refresh commit 進 git）

隱私鐵律：**只保留 taskId 以 twmd- / taiwanmd- 開頭的任務**。scheduler 裡有
觀察者私人 routine（muse-* / fin-*），它們的存在與描述不屬於公開 repo。

下游消費者：routine-sync-check.py v3 第三層比對（SSOT ↔ mirror ↔ live）。
"""

import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUT_PATH = REPO_ROOT / "docs" / "semiont" / "routine-live-state.json"
TWMD_PREFIX = re.compile(r"^(twmd-|taiwanmd-)")

KEEP_FIELDS = [
    "taskId",
    "description",
    "cronExpression",
    "enabled",
    "lastRunAt",
    "nextRunAt",
]


def main():
    args = sys.argv[1:]
    session = "unknown"
    if "--session" in args:
        i = args.index("--session")
        session = args[i + 1]
        del args[i : i + 2]
    if not args:
        print("usage: routine-live-normalize.py <raw-mcp-list.json> [--session <id>]")
        return 1

    raw = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "tasks" in raw:
        raw = raw["tasks"]

    tasks = []
    dropped = 0
    for t in raw:
        if not TWMD_PREFIX.match(t.get("taskId", "")):
            dropped += 1  # 私人 routine，不落公開 repo
            continue
        tasks.append({k: t.get(k) for k in KEEP_FIELDS})
    tasks.sort(key=lambda t: t["taskId"])

    tz = timezone(timedelta(hours=8))
    out = {
        "fetched_at": datetime.now(tz).isoformat(timespec="seconds"),
        "fetched_by": session,
        "source": "mcp scheduled-tasks list_scheduled_tasks",
        "note": "S1 根治第一塊磚（dna-audit 2026-07-05）：live scheduler 狀態 git 可見化。"
        "只含 twmd-/taiwanmd- 任務（私人 routine 已過濾），"
        "消費者 = routine-sync-check.py v3 三層比對。",
        "enabled_count": sum(1 for t in tasks if t["enabled"]),
        "disabled_count": sum(1 for t in tasks if not t["enabled"]),
        "tasks": tasks,
    }
    OUT_PATH.write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"✅ {OUT_PATH.relative_to(REPO_ROOT)}: {out['enabled_count']} enabled "
        f"+ {out['disabled_count']} disabled（過濾 {dropped} 條私人 routine）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
