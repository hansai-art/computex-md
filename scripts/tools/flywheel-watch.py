#!/usr/bin/env python3
"""flywheel-watch.py — 從外面看 routine 飛輪還有沒有在轉。

## 為什麼存在

2026-07-24 起 routine 飛輪整批遷到 mouhouse 營運，指揮部這台不再跑任何 twmd routine。
好處是飛輪不跟著筆電闔蓋停；代價是**沒人在看它**——飛輪曾經靜默死 15 天，全部儀器
無聲，因為那些儀器都跑在飛輪自己身上（儀器只看見存在，看不見缺席）。

所以這條檢查刻意跑在**不營運的那台**：它的唯一資訊來源是 `origin/main` 的 commit 紀錄，
git 是兩台機器都騙不了的 ground truth。飛輪在別的地方死掉，這裡看得見。

## 判準

    CRITICAL  過去 24 小時 origin/main 零筆 🧬 [routine] commit  → 飛輪整體停轉
    WARN      某條該跑的 routine 在窗口內沒留下 commit           → 單條靜默
    WARN      routine-live-state.json 超過 48 小時沒更新          → 感知層自己過期

## 用法

    python3 scripts/tools/flywheel-watch.py              # 人看的報告
    python3 scripts/tools/flywheel-watch.py --json       # 給 routine session 讀
    python3 scripts/tools/flywheel-watch.py --hours 48   # 換窗口

Exit code: 0 = 飛輪在轉；1 = 有靜默（CRITICAL 或 WARN）；2 = 環境壞掉。

## 誠實的限制

`last_due` 只處理 `分 時 * * 星期` 這種單點 cron，不展開 `*/N`、多時段等語法（無
croniter 依賴）。算不出來的一律列進 `unknown_cron` 不判定，**不假裝知道**。

「跑過了」有兩把獨立的尺：`[routine]` commit tag，以及 MEMORY.md 索引列的 session-id
handle。兩把都不中才算靜默——只認 commit tag 會把「跑完但 commit 沒帶 taskId」誤報成
死亡（2026-07-26 distill-weekly 首例）。

「有沒有留下痕跡」是效果的代理指標而非效果本身：空場 cycle（真的跑了但沒事可做）在
這裡看起來跟死掉一樣。所以單條靜默只給 WARN，要不要當死掉看它上次 fire 時間再判；
只有「整體零筆」才升 CRITICAL。這條限制是刻意的——把它做成零假陽性需要讀排程器的
執行紀錄，而那份紀錄住在營運機上，一旦依賴它就失去「從外面看」這個唯一價值。
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ROUTINE_SSOT = REPO_ROOT / "docs" / "semiont" / "ROUTINE.md"
MEMORY_INDEX = REPO_ROOT / "docs" / "semiont" / "MEMORY.md"
LIVE_STATE = REPO_ROOT / "docs" / "semiont" / "routine-live-state.json"
LIVE_STALE_HOURS = 48
# 索引列：| YYYY-MM-DD | HHMMSS-handle | 摘要 | 教訓 | link |
MEMORY_ROW = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(\d{6})-([a-z0-9-]+)\s*\|")



def local_node_name():
    """本機節點名（`.taiwanmd/node-name.local`，gitignored）。給 🖥️ 節點標記比對用。"""
    f = REPO_ROOT / ".taiwanmd" / "node-name.local"
    try:
        return f.read_text(encoding="utf-8").strip().splitlines()[0].strip()
    except (OSError, IndexError):
        return ""


def belongs_to_this_node(row_text, node):
    """排程表某列帶 `🖥️<節點名>` 時，只屬那台機器；沒有標記 = 所有營運機都該有。

    沒這道判斷的話，只跑在指揮部的 flywheel-watch 會讓營運機每天被報成缺一條 prompt。
    """
    m = re.search(r"🖥️\s*([A-Za-z0-9._-]+)", row_text)
    if not m:
        return True
    return m.group(1).strip() == node


def memory_index_handles(window_start, now):
    """第二把尺：MEMORY.md 索引列的 session-id handle（`| 日期 | HHMMSS-handle |`）。

    commit tag 是一把尺，收官索引列是另一把——兩把獨立才接得住「跑完了但 commit
    沒帶 taskId」這種靜默假警報。2026-07-26 首個排程 cycle 就抓到：distill-weekly
    當天 03:15 真的跑完（索引列 `031527-twmd-distill-weekly`），但它的產出 commit
    寫成 `[semiont] distill:`，窗口內沒有任何一筆 subject 帶得出 taskId，於是被報
    成靜默。同一種「名字的替身」前一晚才讓 weekly-report 誤報 maintainer-daily
    靜默死亡（REFLEXES #69 每層自評都需要外部尺 / #82 訊號別選代理）。
    """
    if not MEMORY_INDEX.exists():
        return set()
    hits = set()
    tz = now.tzinfo
    for line in MEMORY_INDEX.read_text(encoding="utf-8").splitlines():
        m = MEMORY_ROW.match(line)
        if not m:
            continue
        date_s, hhmmss, handle = m.groups()
        try:
            stamp = datetime.strptime(date_s + hhmmss, "%Y-%m-%d%H%M%S").replace(tzinfo=tz)
        except ValueError:
            continue
        if window_start <= stamp <= now:
            hits.add(handle if handle.startswith("twmd-") else f"twmd-{handle}")
    return hits


def sh(*args):
    return subprocess.run(
        args, cwd=REPO_ROOT, capture_output=True, text=True, check=False
    ).stdout


def parse_enabled_routines():
    """撈 ROUTINE.md 排程表裡 enabled 的 taskId → cron。退休與暫停的不算。

    區塊判定跟 routine-sync.py 同一套（認表不只認字）——那邊踩過「PAUSED 表裡的列
    沒有 ⏸️ 字樣就被當 enabled」的坑，這裡不重犯。
    """
    if not ROUTINE_SSOT.exists():
        print(f"flywheel-watch: 讀不到 {ROUTINE_SSOT}", file=sys.stderr)
        sys.exit(2)
    out, section, node = {}, "schedule", local_node_name()
    if not node:
        # 沒有節點身份時，帶 🖥️ 標記的列會整批靜靜消失（本檔自己就是其中一列）。
        # 這種降級只在 worktree／新機器上出現，正好是最不會有人盯著看的場合。
        print(
            "flywheel-watch: 讀不到 .taiwanmd/node-name.local，"
            "帶 🖥️ 節點標記的 routine 這次不納入檢查",
            file=sys.stderr,
        )
    for line in ROUTINE_SSOT.read_text(encoding="utf-8").splitlines():
        if "⏸️ PAUSED" in line:
            section = "paused"
        elif "🪦 已退休" in line:
            section = "retired"
        elif line.startswith("#"):
            section = "schedule"
        if not line.startswith("|") or section != "schedule":
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        m = re.search(r"`(twmd-[a-z0-9-]+)`", cells[0]) if cells else None
        if not m:
            continue
        row = " ".join(cells)
        if "⏸️" in row or "PAUSED" in row:
            continue
        if not belongs_to_this_node(row, node):
            continue
        cron = ""
        for c in cells:
            cm = re.fullmatch(r"`([-\d*/, ]+)`", c)
            if cm and len(cm.group(1).split()) == 5:
                cron = cm.group(1).strip()
                break
        out[m.group(1)] = cron
    return out


def last_due(cron, now):
    """這條 cron 上一次「應該」響的時刻。算不出來回 None，不裝作知道。

    daily：今天 h:m 已過就是今天，否則昨天。
    weekly：往回找最近一個符合的星期幾且時刻已過。
    只判「有沒有到期」，不展開完整 cron 語法（無 croniter 依賴）。
    """
    parts = cron.split()
    if len(parts) != 5 or not parts[0].lstrip("0").isdigit() and parts[0] != "0":
        return None
    try:
        minute, hour = int(parts[0]), int(parts[1])
    except ValueError:
        return None
    dow = parts[4]
    if dow == "*":
        cand = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return cand if cand <= now else cand - timedelta(days=1)
    try:
        wanted = {int(x) % 7 for x in re.split(r"[,\-]", dow) if x.isdigit()}
    except ValueError:
        return None
    if not wanted:
        return None
    for back in range(0, 8):
        d = now - timedelta(days=back)
        if d.isoweekday() % 7 in wanted:
            cand = d.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if cand <= now:
                return cand
    return None


def main():
    ap = argparse.ArgumentParser(description="從外部看 routine 飛輪是否還在轉")
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    sh("git", "fetch", "--quiet", "origin")
    log = sh(
        "git",
        "log",
        "origin/main",
        f"--since={args.hours} hours ago",
        "--format=%h|%ai|%s",
    )
    lines = [l for l in log.splitlines() if l.strip()]
    routine_commits = [l for l in lines if "[routine]" in l]

    # fired 有兩種痕跡：`[routine] <slug>:` 主產出，以及收官那筆 `[semiont] memory:
    # twmd-xxx 收官`。只認前者會把「真的跑了但只留收官紀錄」誤報成靜默——2026-07-25
    # 首跑就對 maintainer-daily 誤報一次（REFLEXES #66：閾值用真實產出校準）。
    fired = set()
    for l in routine_commits:
        m = re.search(r"\[routine\]\s+([a-z0-9-]+)", l)
        if m:
            slug = m.group(1)
            fired.add(slug if slug.startswith("twmd-") else f"twmd-{slug}")
    mentioned = set(re.findall(r"twmd-[a-z0-9-]+", log))

    enabled = parse_enabled_routines()
    now = datetime.now(timezone.utc).astimezone()
    window_start = now - timedelta(hours=args.hours)
    logged = memory_index_handles(window_start, now)
    silent, unknown_cron = [], []
    for task_id, cron in sorted(enabled.items()):
        due = last_due(cron, now)
        if due is None:
            unknown_cron.append(task_id)
            continue
        if due < window_start:
            continue  # 上次到期落在窗口之前，本窗口不該有它
        # commit slug 跟 taskId 不總是逐字相同（spore-harvest / embeddings 等會簡寫），
        # 兩邊互為前綴就算命中；再退一步接受收官 commit 提到 taskId
        hit = (
            any(
                f == task_id or task_id.startswith(f) or f.startswith(task_id)
                for f in fired
            )
            or task_id in mentioned
            or task_id in logged
        )
        if not hit:
            silent.append(task_id)

    live_age = None
    if LIVE_STATE.exists():
        try:
            fetched = json.loads(LIVE_STATE.read_text(encoding="utf-8")).get("fetched_at")
            dt = datetime.fromisoformat(fetched)
            live_age = (datetime.now(dt.tzinfo or timezone.utc) - dt).total_seconds() / 3600
        except (json.JSONDecodeError, ValueError, TypeError):
            live_age = None

    severity = "ok"
    if not routine_commits:
        severity = "critical"
    elif silent or (live_age is not None and live_age > LIVE_STALE_HOURS):
        severity = "warn"

    result = {
        "severity": severity,
        "window_hours": args.hours,
        "total_commits": len(lines),
        "routine_commits": len(routine_commits),
        "fired": sorted(fired),
        "logged": sorted(logged),
        "silent": silent,
        "unknown_cron": unknown_cron,
        "live_state_age_hours": round(live_age, 1) if live_age is not None else None,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        icon = {"ok": "✅", "warn": "⚠️ ", "critical": "🚨"}[severity]
        print(f"{icon} 飛輪狀態（過去 {args.hours} 小時，看 origin/main）\n")
        print(f"  commit 總數 {len(lines)}，其中 [routine] 標記 {len(routine_commits)} 筆")
        if fired:
            print(f"  有動靜（commit 標記）：{', '.join(sorted(fired))}")
        only_logged = sorted(logged - fired)
        if only_logged:
            print(f"  有動靜（只留收官索引）：{', '.join(only_logged)}")
        if silent:
            print(f"  ⚠️  該跑但沒留下 commit：{', '.join(silent)}")
        if unknown_cron:
            print(f"  （cron 讀不出來，未判定：{', '.join(unknown_cron)}）")
        if live_age is not None:
            flag = " ⚠️ 過期" if live_age > LIVE_STALE_HOURS else ""
            print(f"  live 狀態 dump 齡 {live_age:.1f} 小時{flag}")
        else:
            print("  live 狀態 dump 讀不到或無時間戳")
        if severity == "critical":
            print("\n🚨 窗口內零筆 routine commit — 飛輪整體停轉。先確認營運機的 Claude app 活著、額度沒到頂。")
        elif severity == "warn":
            print("\n⚠️  部分靜默。單條靜默常見原因：那條 routine 空場（沒事可做也不 commit）、額度耗盡、或真的死了。看它上一次 fire 的時間再判。")
        else:
            print("\n✅ 飛輪在轉")

    sys.exit(1 if severity != "ok" else 0)


if __name__ == "__main__":
    main()
