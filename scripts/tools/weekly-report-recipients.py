#!/usr/bin/env python3
"""
weekly-report-recipients.py — COMPUTEX.md 週報收件人清單收成器 / weekly-report BCC harvester

中文：
COMPUTEX.md 的週報信會 BCC 給過去 N 天內對這個 repo 有貢獻或互動過的每一個人。
本工具負責：(a) 從 GitHub 三個來源（commits / issues+PRs / comments）撈出這些人
+ 他們的活躍程度，(b) 解出每個人的 email（commit email → GitHub profile
email → unreachable），(c) 把機器可讀的收件人清單寫到 repo 之外（因為含真實
email，不可進版控），(d) 印一份不含任何 raw email 的人類可讀活躍度摘要。
Email 解不出來的人不會消失——他們仍在 JSON 的 recipients 陣列裡（reachable
=false），只是不進 bcc 陣列，方便人類自己去 chase。

English:
COMPUTEX.md's weekly report email is BCC'd to everyone who contributed to or
interacted with this repo in the last N days. This tool harvests that list:
(a) pulls people + activity levels from three GitHub-adjacent sources
(commits, issues/PRs, comments), (b) resolves each person's email (commit
email → GitHub profile email → unreachable), (c) writes a machine-readable
recipients JSON OUTSIDE the repo (it contains real email addresses, so it
must never enter version control), and (d) prints a human-readable activity
summary that never contains a raw email address.

Usage:
    python3 scripts/tools/weekly-report-recipients.py \\
        [--window-days 90] [--repo frank890417/taiwan-md] \\
        [--json-out PATH] [--summary] [--quiet]

Data sources (mailmap-aware git log + gh api, all read-only):
    1. commits    — `git log --since="N days ago" --format=%aN|%aE|%aI`
    2. issues/PRs — `gh api repos/{repo}/issues?state=all&since=...`
    3. comments   — `gh api repos/{repo}/issues/comments` +
                     `gh api repos/{repo}/pulls/comments`

Output:
    Default JSON: ~/.config/taiwan-md/weekly-report/recipients-latest.json
    (chmod 600) + a dated copy recipients-YYYY-MM-DD.json next to it.
    Neither file is ever written inside the repo.

Exit codes:
    0 = success
    2 = a git/gh call failed (fail loud — see stderr)
    3 = bcc list is empty after filtering (fail loud so the pipeline notices)
"""

import argparse
import collections
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOL_TAG = "[weekly-report-recipients]"

DEFAULT_REPO = "frank890417/taiwan-md"
CONFIG_DIR = Path.home() / ".config/taiwan-md/weekly-report"
DEFAULT_JSON_OUT = CONFIG_DIR / "recipients-latest.json"
LOCAL_OPTOUT_PATH = CONFIG_DIR / "optout-emails.txt"
REPO_OPTOUT_PATH = REPO_ROOT / "docs/community/weekly-report-optout.json"

# Owner (哲宇) is the report's To: recipient, never a bcc entry.
OWNER_LOGIN = "frank890417"
OWNER_EMAILS = {"cheyu.wu@monoame.com", "frank890417@gmail.com"}
OWNER_NAME = "Che-Yu Wu"

# Resend 免費方案上限：一天 100 封（含 To + 每個 BCC）。一次週報廣播 = 收件人數封。
# 名單接近上限時提醒升級 Pro（決策見 reports/weekly-report-audience-upgrade-2026-07-12.md §「深度分析」）。
FREE_TIER_DAILY_LIMIT = 100
FREE_TIER_WARN_AT = 80  # +1 是 To（哲宇），留 ~19 封餘裕給批次抖動

BOT_EXACT_LOGINS = {"dependabot", "github-actions", "copilot"}

# e.g. 12345+someuser@users.noreply.github.com → login "someuser"
NOREPLY_RE = re.compile(r"^\d+\+([^@]+)@users\.noreply\.github\.com$", re.IGNORECASE)

BAD_DOMAIN_SUFFIXES = (
    ".local",
    ".localdomain",
    ".internal",
    ".lan",
    ".invalid",
    ".test",
    ".example",
)

_profile_cache: dict[str, str | None] = {}


# ─────────────────────────────────────────────────────────
# Small helpers
# ─────────────────────────────────────────────────────────


def log(msg: str, quiet: bool) -> None:
    if not quiet:
        print(f"{TOOL_TAG} {msg}", file=sys.stderr)


def warn(msg: str) -> None:
    print(f"{TOOL_TAG} ⚠️  {msg}", file=sys.stderr)


def die(msg: str, code: int = 2) -> None:
    print(f"{TOOL_TAG} ❌ {msg}", file=sys.stderr)
    sys.exit(code)


def run_or_die(cmd: list[str], timeout: int, what: str) -> str:
    """Run git/gh with subprocess.run(capture_output=True); fail loud on error.

    ❌ ANTI-EXAMPLE (do not do this): swallowing a nonzero exit and continuing
    with an empty list. Every caller of this function trusts its output is
    complete — a silent partial dataset would under-count real contributors.
    """
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        die(f"{what} timed out after {timeout}s — cmd: {' '.join(cmd)}")
        return ""  # unreachable; keeps control flow explicit
    if r.returncode != 0:
        stderr = (r.stderr or "").strip()
        die(f"{what} failed (exit {r.returncode}) — cmd: {' '.join(cmd)}\n{stderr}")
        return ""
    return r.stdout


def parse_iso(ts: str | None) -> datetime | None:
    """Parse an ISO8601 timestamp (git %aI offset form or GitHub 'Z' form)."""
    if not ts:
        return None
    t = ts.strip()
    if t.endswith("Z"):
        t = t[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(t)
    except ValueError:
        return None


def parse_json_array_maybe_concat(text: str) -> list:
    """Parse `gh api ... --paginate` stdout into a flat list of items.

    Empirically (gh 2.87.3), --paginate merges all pages of a JSON-array
    endpoint into a single JSON array. Older/newer gh versions have been
    known to instead print pages back-to-back with no separator (`[...][...]`),
    which is not valid single-document JSON. Handle both shapes.
    """
    text = text.strip()
    if not text:
        return []
    try:
        data = json.loads(text)
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    items: list = []
    idx = 0
    n = len(text)
    while idx < n:
        while idx < n and text[idx] in " \t\r\n":
            idx += 1
        if idx >= n:
            break
        try:
            obj, end = decoder.raw_decode(text, idx)
        except json.JSONDecodeError as e:
            die(f"failed to parse gh api --paginate output as JSON: {e}")
            return []
        items.extend(obj) if isinstance(obj, list) else items.append(obj)
        idx = end
    return items


def md_escape(s: str | None) -> str:
    if not s:
        return ""
    return s.replace("|", "\\|").replace("\n", " ").strip()


# ─────────────────────────────────────────────────────────
# Data collection — three sources
# ─────────────────────────────────────────────────────────


def fetch_commits(window_days: int) -> dict[str, dict]:
    """git log, mailmap-aware. Keyed by %aN (canonical commit author name).

    ❌ ANTI-EXAMPLE: using %an|%ae (raw, bypasses .mailmap) — MUST use
    %aN|%aE so multiple emails/spellings for the same human collapse per
    .mailmap before we ever start person-merging.
    """
    out = run_or_die(
        ["git", "log", f"--since={window_days} days ago", "--format=%aN|%aE|%aI"],
        timeout=60,
        what="git log (commits)",
    )
    people: dict[str, dict] = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("|", 2)
        if len(parts) != 3:
            continue
        name, email, ts = (p.strip() for p in parts)
        if not name:
            continue
        rec = people.setdefault(
            name, {"emails": collections.Counter(), "commits": 0, "last_active_dt": None}
        )
        rec["commits"] += 1
        if email:
            rec["emails"][email] += 1
        dt = parse_iso(ts)
        if dt and (rec["last_active_dt"] is None or dt > rec["last_active_dt"]):
            rec["last_active_dt"] = dt
    return people


def new_api_record() -> dict:
    return {"prs": 0, "issues": 0, "comments": 0, "last_active_dt": None}


def touch_last_active(rec: dict, dt: datetime | None) -> None:
    if dt is None:
        return
    if rec["last_active_dt"] is None or dt > rec["last_active_dt"]:
        rec["last_active_dt"] = dt


def fetch_issues_and_prs(
    repo: str, window_start_iso: str, api_activity: dict[str, dict], quiet: bool
) -> None:
    """gh api issues?state=all — includes PRs (they share the issues endpoint).

    ❌ ANTI-EXAMPLE: counting every returned item. `since=` filters by
    *updated_at* server-side (over-fetch, safe), so we MUST client-side
    filter created_at >= window_start before counting authorship — an old
    issue that merely got a label change this week is not "activity".
    """
    out = run_or_die(
        [
            "gh",
            "api",
            f"repos/{repo}/issues?state=all&per_page=100&since={window_start_iso}",
            "--paginate",
        ],
        timeout=180,
        what="gh api issues (list, incl. PRs)",
    )
    items = parse_json_array_maybe_concat(out)
    n_issues = n_prs = n_skipped = 0
    for item in items:
        created_at = item.get("created_at")
        if not created_at or created_at < window_start_iso:
            n_skipped += 1
            continue
        user = item.get("user") or {}
        login = user.get("login")
        if not login:
            continue
        rec = api_activity.setdefault(login, new_api_record())
        if "pull_request" in item:
            rec["prs"] += 1
            n_prs += 1
        else:
            rec["issues"] += 1
            n_issues += 1
        touch_last_active(rec, parse_iso(created_at))
    log(
        f"issues+PRs: {len(items)} fetched, {n_skipped} outside window "
        f"(created_at < window_start), counted issues={n_issues} prs={n_prs}",
        quiet,
    )


def fetch_comments(
    repo: str, window_start_iso: str, endpoint: str, api_activity: dict[str, dict], quiet: bool
) -> None:
    """gh api .../issues/comments or .../pulls/comments — same created_at filter."""
    out = run_or_die(
        ["gh", "api", f"repos/{repo}/{endpoint}?per_page=100&since={window_start_iso}", "--paginate"],
        timeout=180,
        what=f"gh api {endpoint}",
    )
    items = parse_json_array_maybe_concat(out)
    counted = 0
    for item in items:
        created_at = item.get("created_at")
        if not created_at or created_at < window_start_iso:
            continue
        user = item.get("user") or {}
        login = user.get("login")
        if not login:
            continue
        rec = api_activity.setdefault(login, new_api_record())
        rec["comments"] += 1
        counted += 1
        touch_last_active(rec, parse_iso(created_at))
    log(f"{endpoint}: {len(items)} fetched, {counted} inside window", quiet)


# ─────────────────────────────────────────────────────────
# Email resolution
# ─────────────────────────────────────────────────────────


def is_invalid_email(email: str) -> bool:
    """commit-email validity gate (priority-1 source).

    Invalid = no "@", OR a GitHub noreply address (not a human inbox), OR
    domain has no dot at all (e.g. user@localhost), OR domain ends with a
    known non-routable/dev suffix (.local / .localdomain / .internal / .lan
    / .invalid / .test / .example) — e.g. `chilan@qilandeMac-mini.local`
    from this repo's real git history, caught by the ".local" suffix rule.
    """
    if not email or "@" not in email:
        return True
    local, _, domain = email.rpartition("@")
    if not local or not domain:
        return True
    if email.lower().endswith("@users.noreply.github.com"):
        return True
    domain_l = domain.lower()
    if "." not in domain_l:
        return True
    return any(domain_l.endswith(sfx) for sfx in BAD_DOMAIN_SUFFIXES)


def fetch_profile_email(login: str) -> str | None:
    """gh api users/{login} --jq .email — priority-2 source. Cached.

    A 404 (deleted/renamed account) must NOT abort the run — warn and
    continue. This is the one deliberate exception to the fail-loud rule.
    """
    if login in _profile_cache:
        return _profile_cache[login]
    try:
        r = subprocess.run(
            ["gh", "api", f"users/{login}", "--jq", ".email"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        warn(f"gh api users/{login} timed out — treating as no profile email")
        _profile_cache[login] = None
        return None
    if r.returncode != 0:
        warn(
            f"gh api users/{login} failed (exit {r.returncode}, likely deleted/renamed "
            f"account) — continuing without profile email: {(r.stderr or '').strip()}"
        )
        _profile_cache[login] = None
        return None
    val = (r.stdout or "").strip()
    email = val if val and val.lower() != "null" else None
    _profile_cache[login] = email
    return email


def resolve_email(login: str | None, emails: collections.Counter) -> tuple[str | None, str | None]:
    """Priority: commit emails (most-used first, skip invalid) → GitHub
    profile email → unreachable. Returns (email, email_source)."""
    for email, _ in emails.most_common():
        if not is_invalid_email(email):
            return email, "commit"
    if login:
        profile_email = fetch_profile_email(login)
        if profile_email:
            return profile_email, "profile"
    return None, None


# ─────────────────────────────────────────────────────────
# Person construction, merging, bot/owner classification
# ─────────────────────────────────────────────────────────


def new_person(login: str | None, name: str | None, name_is_placeholder: bool) -> dict:
    return {
        "login": login,
        "name": name,
        "name_is_placeholder": name_is_placeholder,
        "emails": collections.Counter(),
        "commits": 0,
        "prs": 0,
        "issues": 0,
        "comments": 0,
        "last_active_dt": None,
    }


def is_bot(login: str | None, name: str | None) -> bool:
    if login:
        ll = login.lower()
        if ll.endswith("[bot]") or ll in BOT_EXACT_LOGINS:
            return True
    if name and name.lower().endswith("[bot]"):
        return True
    return False


def is_owner(login: str | None, name: str | None, emails: collections.Counter) -> bool:
    if login and login.lower() == OWNER_LOGIN.lower():
        return True
    if name == OWNER_NAME:
        return True
    return any(e.lower() in OWNER_EMAILS for e in emails)


def build_people(repo: str, window_days: int, window_start_iso: str, quiet: bool) -> dict[str, dict]:
    """Gather all three sources and merge into one dict of person records.

    Merge key: GitHub login when known, else a name-scoped standalone key.
    A commit-person links to a login when (a) any commit email matches the
    GitHub noreply pattern (extract login), or (b) the commit author name
    equals a known login case-insensitively. Otherwise they stay standalone
    (login=None) — there is no reliable way to fold them into anyone else.
    """
    log(f"gathering commits (mailmap-aware, --since='{window_days} days ago') …", quiet)
    commit_people = fetch_commits(window_days)
    log(f"  {len(commit_people)} distinct commit-author names", quiet)

    api_activity: dict[str, dict] = {}
    log("gathering issues + PRs …", quiet)
    fetch_issues_and_prs(repo, window_start_iso, api_activity, quiet)
    log("gathering issue/PR discussion comments …", quiet)
    fetch_comments(repo, window_start_iso, "issues/comments", api_activity, quiet)
    log("gathering PR review comments …", quiet)
    fetch_comments(repo, window_start_iso, "pulls/comments", api_activity, quiet)
    log(f"  {len(api_activity)} distinct API logins with activity", quiet)

    # login_by_lower is the mutable "known logins" pool used for (b) name
    # matching. Seed it from the API, then let pass 1 (noreply extraction)
    # widen it before pass 2 (name matching) runs, so name-matching sees the
    # fullest possible set.
    login_by_lower: dict[str, str] = {lg.lower(): lg for lg in api_activity}

    # Pass 1: noreply-email extraction.
    for name, cdata in commit_people.items():
        linked = None
        for email, _ in cdata["emails"].most_common():
            m = NOREPLY_RE.match(email)
            if m:
                linked = m.group(1)
                break
        cdata["linked_login"] = linked
        if linked:
            login_by_lower.setdefault(linked.lower(), linked)

    # Pass 2: case-insensitive commit-name == known-login fallback.
    for name, cdata in commit_people.items():
        if cdata["linked_login"]:
            continue
        cdata["linked_login"] = login_by_lower.get(name.lower())

    final: dict[str, dict] = {}

    def key_for(login: str | None, name: str | None) -> str:
        return f"login::{login.lower()}" if login else f"name::{(name or '').lower()}"

    # Seed final with API-only people (placeholder display name = login).
    for login, adata in api_activity.items():
        rec = new_person(login=login, name=login, name_is_placeholder=True)
        rec["prs"] = adata["prs"]
        rec["issues"] = adata["issues"]
        rec["comments"] = adata["comments"]
        touch_last_active(rec, adata["last_active_dt"])
        final[key_for(login, None)] = rec

    # Fold in commit people.
    for name, cdata in commit_people.items():
        login = cdata["linked_login"]
        k = key_for(login, name)
        rec = final.get(k)
        if rec is None:
            rec = new_person(login=login, name=name, name_is_placeholder=False)
            final[k] = rec
        elif rec["name_is_placeholder"]:
            # Real commit-derived name beats the bare-login placeholder.
            rec["name"] = name
            rec["name_is_placeholder"] = False
        # else: an earlier commit alias already supplied a real display
        # name for this login — first-seen (most-recent commit, since git
        # log is newest-first) wins; don't flip-flop between aliases.
        rec["commits"] += cdata["commits"]
        rec["emails"] += cdata["emails"]
        touch_last_active(rec, cdata["last_active_dt"])

    return final


# ─────────────────────────────────────────────────────────
# Opt-out layers
# ─────────────────────────────────────────────────────────


def load_repo_optout() -> tuple[set[str], set[str]]:
    """docs/community/weekly-report-optout.json — missing file = empty, no error."""
    if not REPO_OPTOUT_PATH.exists():
        return set(), set()
    try:
        data = json.loads(REPO_OPTOUT_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        warn(f"failed to parse {REPO_OPTOUT_PATH} ({e}) — treating as empty")
        return set(), set()
    logins = {str(x).lower() for x in (data.get("optout_logins") or [])}
    names = {str(x).lower() for x in (data.get("optout_names") or [])}
    return logins, names


def load_local_optout_emails() -> set[str]:
    """~/.config/taiwan-md/weekly-report/optout-emails.txt — missing = empty."""
    if not LOCAL_OPTOUT_PATH.exists():
        return set()
    out: set[str] = set()
    for line in LOCAL_OPTOUT_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.add(line.lower())
    return out


# ─────────────────────────────────────────────────────────
# Finalize: email resolution + owner/optout flags + activity_score
# ─────────────────────────────────────────────────────────


def finalize_records(
    final: dict[str, dict],
    optout_logins: set[str],
    optout_names: set[str],
    optout_emails: set[str],
) -> list[dict]:
    records: list[dict] = []
    for rec in final.values():
        login = rec["login"]
        name = rec["name"] or login or "(unknown)"
        email, email_source = resolve_email(login, rec["emails"])
        reachable = email is not None
        owner = is_owner(login, name, rec["emails"])

        opted_out = False
        if login and login.lower() in optout_logins:
            opted_out = True
        if name and name.lower() in optout_names:
            opted_out = True
        if email and email.lower() in optout_emails:
            opted_out = True

        activity_score = rec["commits"] * 3 + rec["prs"] * 2 + rec["issues"] * 2 + rec["comments"] * 1
        last_active = rec["last_active_dt"].isoformat() if rec["last_active_dt"] else None

        records.append(
            {
                "login": login,
                "name": name,
                "email": email,
                "email_source": email_source,
                "role": "owner" if owner else "contributor",
                "commits": rec["commits"],
                "prs": rec["prs"],
                "issues": rec["issues"],
                "comments": rec["comments"],
                "activity_score": activity_score,
                "last_active": last_active,
                "optout": opted_out,
                "reachable": reachable,
            }
        )
    records.sort(key=lambda r: (-r["activity_score"], (r["name"] or "").lower()))
    return records


def build_bcc(records: list[dict]) -> list[str]:
    seen: dict[str, str] = {}
    for r in records:
        if r["role"] == "owner" or r["optout"] or not r["reachable"]:
            continue
        seen.setdefault(r["email"].lower(), r["email"])
    return sorted(seen.values(), key=str.lower)


# ─────────────────────────────────────────────────────────
# --summary rendering (NEVER prints a raw email address)
# ─────────────────────────────────────────────────────────


def render_summary(
    window_days: int,
    window_start_iso: str,
    generated_at_iso: str,
    repo: str,
    records: list[dict],
    bcc: list[str],
    json_out_path: Path,
) -> str:
    lines: list[str] = []
    lines.append(f"# COMPUTEX.md 週報收件人活躍度摘要 — {repo}")
    lines.append("")
    lines.append(f"視窗：過去 {window_days} 天（{window_start_iso} ～ {generated_at_iso}）")
    lines.append("")
    lines.append("| 名字 (login) | commits | PR | issue | 留言 | 最後活躍 | ✉️ |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for r in records:
        label = f"{md_escape(r['name'])} ({r['login']})" if r["login"] else md_escape(r["name"])
        if r["optout"]:
            mark = "🚫"
        elif r["reachable"]:
            mark = "✓"
        else:
            mark = "✗"
        last_active_date = (r["last_active"] or "—")[:10]
        lines.append(
            f"| {label} | {r['commits']} | {r['prs']} | {r['issues']} | "
            f"{r['comments']} | {last_active_date} | {mark} |"
        )
    lines.append("")

    reachable_n = sum(1 for r in records if r["reachable"])
    unreachable_n = sum(1 for r in records if not r["reachable"])
    optout_n = sum(1 for r in records if r["optout"])
    lines.append(
        f"總計 {len(records)} 人／可聯繫 {reachable_n}／無法聯繫 {unreachable_n}／"
        f"opt-out {optout_n}／bcc 名單 {len(bcc)} 人"
    )
    if len(bcc) >= FREE_TIER_DAILY_LIMIT:
        lines.append(
            f"🚨 bcc {len(bcc)} 已達／超過 Resend 免費方案單日 {FREE_TIER_DAILY_LIMIT} 封上限"
            f"（含 To 共 {len(bcc)+1} 封）——本週廣播會被截斷，該升級 Pro 了。"
        )
    elif len(bcc) >= FREE_TIER_WARN_AT:
        lines.append(
            f"⚠️ bcc {len(bcc)} 逼近 Resend 免費方案單日 {FREE_TIER_DAILY_LIMIT} 封上限"
            f"——快到該考慮升級 Pro（$20/月，無單日上限）的時候了。"
        )

    unreachable_ids = []
    for r in records:
        if r["reachable"]:
            continue
        unreachable_ids.append(f"@{r['login']}" if r["login"] else md_escape(r["name"]))
    if unreachable_ids:
        lines.append(f"無法解析 email（需要人工去 issue/PR 底下邀請）：{', '.join(unreachable_ids)}")
    else:
        lines.append("無法解析 email：（無，全員可聯繫）")

    lines.append(f"JSON 輸出：`{json_out_path}`")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--window-days", type=int, default=90, help="Lookback window in days (default 90)")
    ap.add_argument("--repo", default=DEFAULT_REPO, help=f"owner/name (default {DEFAULT_REPO})")
    ap.add_argument(
        "--json-out",
        default=None,
        help=f"Output JSON path (default {DEFAULT_JSON_OUT})",
    )
    ap.add_argument("--summary", action="store_true", help="Print a markdown activity table to stdout")
    ap.add_argument("--quiet", action="store_true", help="Suppress informational progress logs on stderr")
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    window_start_dt = now - timedelta(days=args.window_days)
    window_start_iso = window_start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    generated_at_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    log(f"repo={args.repo} window_days={args.window_days} since={window_start_iso}", args.quiet)

    final = build_people(args.repo, args.window_days, window_start_iso, args.quiet)
    log(f"{len(final)} distinct people before bot filter", args.quiet)

    final = {k: v for k, v in final.items() if not is_bot(v["login"], v["name"])}
    log(f"{len(final)} people after bot filter", args.quiet)

    optout_logins, optout_names = load_repo_optout()
    optout_emails = load_local_optout_emails()
    log(
        f"optout config: {len(optout_logins)} logins + {len(optout_names)} names (repo) "
        f"+ {len(optout_emails)} emails (local)",
        args.quiet,
    )

    records = finalize_records(final, optout_logins, optout_names, optout_emails)
    bcc = build_bcc(records)
    counts = {
        "people": len(records),
        "reachable": sum(1 for r in records if r["reachable"]),
        "unreachable": sum(1 for r in records if not r["reachable"]),
        "optout": sum(1 for r in records if r["optout"]),
        "bcc": len(bcc),
    }
    log(f"counts: {counts}", args.quiet)

    bcc_n = len(bcc)
    free_tier = {
        "daily_limit": FREE_TIER_DAILY_LIMIT,
        "warn_at": FREE_TIER_WARN_AT,
        "send_count": bcc_n + 1,  # + To (哲宇)
        "status": (
            "over" if bcc_n >= FREE_TIER_DAILY_LIMIT
            else "warn" if bcc_n >= FREE_TIER_WARN_AT
            else "ok"
        ),
    }
    payload = {
        "generated_at": generated_at_iso,
        "window_days": args.window_days,
        "window_start": window_start_iso,
        "repo": args.repo,
        "counts": counts,
        "free_tier": free_tier,
        "recipients": records,
        "bcc": bcc,
    }

    json_out_path = Path(args.json_out).expanduser() if args.json_out else DEFAULT_JSON_OUT
    json_out_path.parent.mkdir(parents=True, exist_ok=True)
    dated_path = json_out_path.parent / f"recipients-{now.strftime('%Y-%m-%d')}.json"

    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    json_out_path.write_text(text, encoding="utf-8")
    os.chmod(json_out_path, 0o600)
    dated_path.write_text(text, encoding="utf-8")
    os.chmod(dated_path, 0o600)
    log(f"wrote {json_out_path} + {dated_path} (chmod 600)", args.quiet)

    if args.summary:
        print(
            render_summary(
                args.window_days, window_start_iso, generated_at_iso, args.repo, records, bcc, json_out_path
            )
        )

    if counts["bcc"] == 0:
        print(f"{TOOL_TAG} ❌ FAIL: bcc list is empty after filtering — nothing to send to", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
