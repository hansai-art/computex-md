#!/usr/bin/env python3
"""contributor-pr-heal.py — clownfish-mode PR article heal orchestrator.

One-shot pipeline for contributor knowledge/*.md that typically fail on
format rather than content:

  1. footnote-format-fix (GH refs / numbered lists / yaml fence / APA)
  2. article-health --fix (frontmatter / link-target decode+fuzzy / …)
  3. article-health re-check → print hard/warn + advanced-review bucket

Usage:
  python3 scripts/tools/contributor-pr-heal.py knowledge/Economy/萊爾富.md
  python3 scripts/tools/contributor-pr-heal.py --dry-run path1 path2
  python3 scripts/tools/contributor-pr-heal.py --from-pr 1233

Exit codes:
  0 = hard=0 after heal
  1 = still has hard violations (advanced review / manual needed)
  2 = usage / path error
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _run(cmd: list[str], dry: bool = False) -> subprocess.CompletedProcess:
    print("  $", " ".join(cmd))
    if dry and any(x in cmd for x in ("--apply", "--fix")) and "--dry-run" not in cmd:
        # Prefer dry-run flag if the tool supports it
        if "footnote-format-fix.py" in cmd[1] if len(cmd) > 1 else "":
            cmd = [c for c in cmd if c != "--apply"]
        elif "article-health.py" in (cmd[1] if len(cmd) > 1 else ""):
            if "--fix" in cmd and "--dry-run" not in cmd:
                cmd = cmd + ["--dry-run"]
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)


def _files_from_pr(pr: int) -> list[Path]:
    r = subprocess.run(
        ["gh", "pr", "view", str(pr), "--json", "files", "-q", ".files[].path"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    paths = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if line.startswith("knowledge/") and line.endswith(".md"):
            # only zh-TW root categories
            parts = Path(line).parts
            if len(parts) >= 3 and parts[1] not in {"en", "ja", "ko", "es", "fr"}:
                paths.append(Path(line))
    return paths


def _checkout_pr_file(pr: int, rel: Path) -> bool:
    """Write PR head version of rel into working tree via gh api."""
    r = subprocess.run(
        [
            "gh",
            "pr",
            "view",
            str(pr),
            "--json",
            "headRefOid,headRepository,headRepositoryOwner",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        return False
    meta = json.loads(r.stdout)
    oid = meta["headRefOid"]
    owner = meta["headRepositoryOwner"]["login"]
    repo = meta["headRepository"]["name"]
    api = subprocess.run(
        [
            "gh",
            "api",
            f"repos/{owner}/{repo}/contents/{rel.as_posix()}?ref={oid}",
            "-q",
            ".content",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if api.returncode != 0 or not api.stdout.strip():
        print(f"  ❌ cannot fetch {rel} from PR #{pr}", file=sys.stderr)
        return False
    import base64

    content = base64.b64decode(api.stdout.strip()).decode("utf-8")
    dest = REPO / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    print(f"  ⬇️  checked out {rel} from PR #{pr}")
    return True


def heal_file(path: Path, dry_run: bool) -> dict:
    rel = path if path.is_absolute() else REPO / path
    if not rel.exists():
        return {"path": str(path), "error": "missing"}

    # 1. footnote healer
    fn_cmd = [
        sys.executable,
        str(REPO / "scripts/tools/footnote-format-fix.py"),
        str(rel.relative_to(REPO)),
    ]
    if not dry_run:
        fn_cmd.append("--apply")
    r1 = subprocess.run(fn_cmd, cwd=REPO, capture_output=True, text=True)
    print(r1.stdout.strip() or r1.stderr.strip())

    # 2. article-health --fix
    ah_cmd = [
        sys.executable,
        str(REPO / "scripts/tools/article-health.py"),
        str(rel.relative_to(REPO)),
        "--fix",
    ]
    if dry_run:
        ah_cmd.append("--dry-run")
    r2 = subprocess.run(ah_cmd, cwd=REPO, capture_output=True, text=True)
    print(r2.stdout.strip())
    if r2.stderr.strip():
        print(r2.stderr.strip(), file=sys.stderr)

    # 3. re-check —— 必須用部署閘門的同一個 profile
    # 2026-07-25：此處原本不帶 --profile（走預設，較寬），於是 heal 完自報
    # hard=0 而 CI 的 ci-deploy sweep 是 hard=12，PR #1248（旺旺）就這樣
    # 帶紅了 main。heal 工具的「已修好」如果不是用部署的尺量的，那是一句
    # 沒有兌現保證的話。profile 名與 .github/workflows/deploy.yml 的
    # 「Validate article health (SSOT, full sweep)」那行一致。
    r3 = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts/tools/article-health.py"),
            str(rel.relative_to(REPO)),
            "--profile=ci-deploy",
            "--output=json",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    hard = warn = info = 0
    advanced: list[str] = []
    hard_msgs: list[str] = []
    try:
        data = json.loads(r3.stdout)
        # article-health --output=json 的實際 schema：
        #   {fail_on, reports: [{file, …, results: [{check, violations: [...]}]}]}
        # 2026-07-25 修正：此處原本找 data["files"] 與 item["violations"]/
        # ["issues"]，全部不存在，於是每次都拿到空清單、永遠回報 hard=0。
        # PR #1248（旺旺）heal 完自報全綠、CI 卻擋下 12 個 hard——不是
        # profile 太寬，是這裡從來沒讀到任何一筆。schema 對不上要 fail loud，
        # 不能默默當成「沒有問題」。
        reports = data.get("reports") if isinstance(data, dict) else data
        if not isinstance(reports, list):
            raise ValueError(f"預期 reports 是 list，拿到 {type(reports).__name__}")
        seen_any_result = False
        for rep in reports:
            for res in rep.get("results", []):
                seen_any_result = True
                for v in res.get("violations", []):
                    sev = (v.get("severity") or "").lower()
                    msg = v.get("message") or ""
                    if sev == "hard":
                        hard += 1
                        hard_msgs.append(msg)
                    elif sev == "warn":
                        warn += 1
                        if "advanced-review" in msg or "max match" in msg:
                            advanced.append(msg)
                    else:
                        info += 1
        if not seen_any_result:
            raise ValueError("reports 內沒有任何 results — schema 可能又變了")
    except Exception as e:
        print(f"🔴 re-check JSON 解析失敗（{e}）— 不當作通過，請人工確認：",
              file=sys.stderr)
        print(r3.stdout[:2000], file=sys.stderr)
        hard = -1

    return {
        "path": str(rel.relative_to(REPO)),
        "hard": hard,
        "warn": warn,
        "info": info,
        "hard_msgs": hard_msgs[:10],
        "advanced": advanced[:10],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="*", help="knowledge/*.md paths")
    ap.add_argument("--from-pr", type=int, help="Checkout + heal files from PR number")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-checkout", action="store_true", help="With --from-pr, only heal local files")
    args = ap.parse_args()

    files: list[Path] = [Path(f) for f in args.files]
    if args.from_pr:
        pr_files = _files_from_pr(args.from_pr)
        if not args.no_checkout:
            for f in pr_files:
                _checkout_pr_file(args.from_pr, f)
        files.extend(pr_files)

    if not files:
        ap.print_help()
        return 2

    # dedupe
    seen = set()
    uniq: list[Path] = []
    for f in files:
        key = str(f)
        if key not in seen:
            seen.add(key)
            uniq.append(f)

    print(f"🩹 contributor-pr-heal — {len(uniq)} file(s)"
          f"{' [dry-run]' if args.dry_run else ''}")
    results = []
    any_hard = False
    for f in uniq:
        print(f"\n═══ {f} ═══")
        res = heal_file(f, args.dry_run)
        results.append(res)
        if res.get("hard", 0) not in (0,):
            any_hard = True
        print(
            f"  → hard={res.get('hard')} warn={res.get('warn')} "
            f"advanced={len(res.get('advanced') or [])}"
        )
        for m in res.get("hard_msgs") or []:
            print(f"     HARD: {m[:160]}")
        for m in res.get("advanced") or []:
            print(f"     ADV:  {m[:160]}")

    print("\n════════ summary ════════")
    for r in results:
        flag = "✅" if r.get("hard") == 0 else "❌"
        print(f"  {flag} {r.get('path')}: hard={r.get('hard')} warn={r.get('warn')}")
    return 1 if any_hard else 0


if __name__ == "__main__":
    sys.exit(main())
