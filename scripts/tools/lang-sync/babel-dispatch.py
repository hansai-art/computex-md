#!/usr/bin/env python3
"""
babel-dispatch.py — Unified worker-pool translation batch dispatcher.

Replaces three hand-rolled bash dispatchers (dispatch-node-v3.sh /
run-p1-v3.sh / their predecessors) with one Python worker pool where each
worker is a *pinned backend endpoint* — an OpenRouter free model, a
local/remote Ollama node, or codex — driven through translate.py's cascade
orchestrator (`--cascade <spec>` with `--no-preflight`, single backend per
worker so there's no fallback ambiguity about which model actually did the
work).

Ported straight from the two legacy scripts (2026-07-24, still running
alongside this dispatcher — see --order below):
  - verify_group  (hard gate: verify-translation.py + cjk-leak-check.py +
    article-health.py --profile=pre-commit)
  - git_lock_commit (loud commit failure + article-health quarantine
    recovery + single retry, using the SAME lock dir the legacy dispatchers
    use: /tmp/taiwan-md-git.lock — mutual exclusion across all engines)

2026-07-24 orchestrator amendment (founder.md 教訓 "寧可 stale 也不要
missing" — legacy dispatchers' plain `unlink()` on gate-fail turned readable
P1/stale pages into 404s, measured en missing climbing 28→34 in one day):
a gate-fail (or a vanished/never-written output) on a path that exists in
git HEAD restores the HEAD version instead of deleting it — the article
just stays stale and gets retried next round. Only a path with NO HEAD
version (a genuine P0 attempt) gets truly unlinked. See
restore_head_or_quarantine(). This dispatcher does NOT duplicate
scripts/tools/lang-sync/salvage-quarantined.py (which does after-the-fact
git-log archaeology on today's deletions) — it just prevents new
degradations at the point of failure.

Usage:
  python3 scripts/tools/lang-sync/babel-dispatch.py \\
    --langs vi,id,pt,hi \\
    --worker "nemo=openrouter:nvidia/nemotron-3-ultra-550b-a55b:free" \\
    --worker "gemma31=openrouter:google/gemma-4-31b-it:free" \\
    $(~/Projects/muse-bot/fleet/fleetctl workers --service llm --format babel) \\
    --order reverse --rounds 50 --commit-every 10

Smoke test:
  python3 scripts/tools/lang-sync/babel-dispatch.py --langs vi \\
    --worker "nemo=openrouter:nvidia/nemotron-3-ultra-550b-a55b:free" \\
    --order reverse --max-articles 2 --commit-every 2

Design doc: reports/ (this file was scaffolded per an orchestrator brief,
2026-07-24 — see git log for the commit that introduced it).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from itertools import zip_longest
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent.parent.parent
KNOWLEDGE = REPO / "knowledge"
STATUS_JSON = KNOWLEDGE / "_translation-status.json"
TRANSLATIONS_JSON = KNOWLEDGE / "_translations.json"
GIT_LOCK = Path("/tmp/taiwan-md-git.lock")
# 難篇記憶：跨 run 累計的失敗次數，決定佇列優先序。選址演化三步（2026-07-27
# 哲宇定案）：/tmp（重開機歸零，通過率 50%→18% 的事故）→ ~/.cache（跨重開機
# 但只有本機看得到）→ **repo 內版控**。關鍵認知：難篇是「文章×語言」的屬性
# 不是機器的屬性——mouhouse、其他節點、任何人跑翻譯撞的都是同一批硬骨頭，
# 這份記憶透過 git 在所有產地之間流動。schema {"lang:zh_path": 失敗次數}，
# 數值為 advisory（混合了不同模型的嘗試）；跨機衝突用逐鍵取 max 合併。
FAIL_MEMO = REPO / "reports" / "babel" / "fail-memo.json"
MAX_FAIL_RETRIES = 3   # 同一篇本 run 失敗幾次後讓出輪次（退避，非永久放棄——下個 run 重來）  # SAME path the legacy bash dispatchers use

sys.path.insert(0, str(Path(__file__).resolve().parent))
from langs import ALL_TRANSLATION_LANGS, ENABLED_TRANSLATION_LANGS  # noqa: E402
import status as status_lib  # noqa: E402 — reuse body_hash()/body_hash_pure() (same algo status.py uses)

# bump-source-sha.py's filename has a hyphen (not import-able as a plain module) —
# load it via spec so we can call its bump_one() directly instead of duplicating
# the frontmatter-upsert logic here (2026-07-27, semantic-noop-bump path below).
# sys.modules registration BEFORE exec_module is required, not cosmetic — any
# @dataclass in the loaded file looks up sys.modules[cls.__module__] during class
# creation, and a None there raises AttributeError (hit this exact crash loading
# babel-dispatch.py itself the same way during validation).
import importlib.util as _importlib_util  # noqa: E402
_bump_spec = _importlib_util.spec_from_file_location(
    "bump_source_sha", str(Path(__file__).resolve().parent / "bump-source-sha.py")
)
bump_source_sha = _importlib_util.module_from_spec(_bump_spec)
sys.modules["bump_source_sha"] = bump_source_sha
_bump_spec.loader.exec_module(bump_source_sha)

NOOP_CHECKER = REPO / "scripts" / "tools" / "lang-sync" / "semantic-noop-check.py"


# ────────────────────────── logging ──────────────────────────

class Logger:
    """tee-style: every line goes to stdout AND run_dir/master.log."""

    def __init__(self, path: Path):
        self.lock = threading.Lock()
        self.fp = open(path, "a", encoding="utf-8")

    def __call__(self, msg: object = "") -> None:
        text = str(msg)
        with self.lock:
            print(text)
            self.fp.write(text if text.endswith("\n") else text + "\n")
            self.fp.flush()


class JsonlWriter:
    def __init__(self, path: Path):
        self.lock = threading.Lock()
        self.path = path
        self.fp = open(path, "a", encoding="utf-8")

    def write(self, obj: dict) -> None:
        with self.lock:
            self.fp.write(json.dumps(obj, ensure_ascii=False) + "\n")
            self.fp.flush()


# ────────────────────────── workers ──────────────────────────

@dataclass
class Worker:
    label: str
    cascade_spec: str            # verbatim --cascade value for translate.py
    host: Optional[str] = None   # OLLAMA_HOST override (only set for ollama+@host)
    model: Optional[str] = None  # OLLAMA_MODEL override (only set for ollama+@host)
    consecutive_failures: int = 0
    frozen_until: Optional[float] = None  # time.monotonic() deadline


def parse_worker_arg(raw: str) -> Worker:
    """label=backendspec[@host]

    backendspec is passed to translate.py --cascade verbatim (the @host
    suffix is always stripped first). If @host is present AND backendspec
    starts with `ollama`, OLLAMA_HOST/OLLAMA_MODEL env vars are set for that
    worker's subprocesses instead, and the cascade spec collapses to the
    bare `ollama` token (translate.py's build_cascade() falls back to
    os.environ["OLLAMA_MODEL"] in that case).
    """
    if "=" not in raw:
        raise SystemExit(f"--worker must be 'label=backendspec[@host]', got: {raw!r}")
    label, _, rest = raw.partition("=")
    spec, sep, host_raw = rest.partition("@")
    label = label.strip()
    spec = spec.strip()
    host_raw = host_raw.strip() if sep else ""
    if not label or not spec:
        raise SystemExit(f"--worker must be 'label=backendspec[@host]', got: {raw!r}")

    host = model = None
    cascade_spec = spec
    if host_raw and spec.startswith("ollama"):
        _, _, model_part = spec.partition(":")
        model = model_part or None
        host = host_raw
        cascade_spec = "ollama"

    return Worker(label=label, cascade_spec=cascade_spec, host=host, model=model)


def worker_env(worker: Worker) -> dict:
    """Per-subprocess env (never mutates os.environ — workers run concurrently
    and may point at different Ollama hosts)."""
    env = os.environ.copy()
    if worker.host:
        env["OLLAMA_HOST"] = worker.host
        if worker.model:
            env["OLLAMA_MODEL"] = worker.model
    return env


# ────────────────────────── git lock + commit (ported from dispatch-node-v3.sh) ──────────────────────────

def git_lock_commit(lang: str, worker_labels: set, files: list, log: Logger) -> bool:
    """mkdir-lock /tmp/taiwan-md-git.lock (120x1s retry, shared with the
    legacy bash dispatchers) → git add <the exact files THIS dispatcher
    verified ok> + the two derived JSONs → commit. Commit failure is LOUD
    (printed, not swallowed) + article-health quarantine recovery + single
    retry — ported from dispatch-node-v3.sh git_lock_commit(), with two
    amendments discovered during the 2026-07-24 smoke test:

    1. `git add knowledge/{lang}/` (the legacy directory-wide pattern) swept
       in the CONCURRENTLY-RUNNING legacy fleet dispatcher's not-yet-committed
       files (it targets the same knowledge/vi/ tree). When the pre-commit
       hook then rejected the batch, the recovery block deleted two files
       that belonged to that OTHER process, not this one — real data loss
       for a process this dispatcher has no authority over. Scoping `git add`
       to exactly the paths this run itself verified eliminates that cross-
       engine blast radius entirely.
    2. The recovery block's raw `unlink()` on a staged-but-failing file hits
       the same founder.md problem the per-article HEAD-restore amendment
       exists for: `.lintstagedrc` runs `prettier --write` on staged files
       BEFORE `article-health.py --staged` checks them, so a translation
       that passed the pre-staging single-file gate can still fail here post-
       reformat. Recovery now goes through restore_head_or_quarantine() too.
    """
    n_files = len(files)
    tries = 0
    while True:
        try:
            GIT_LOCK.mkdir()
            break
        except FileExistsError:
            tries += 1
            if tries > 120:
                log(f"🔴 git lock timeout, skipping commit this round ({lang})")
                return False
            time.sleep(1)

    try:
        subprocess.run(
            ["git", "add", *files,
             "knowledge/_translation-status.json", "knowledge/_translations.json"],
            cwd=REPO, capture_output=True, text=True,
        )
        if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO).returncode == 0:
            return True  # nothing staged, nothing to do

        workers_str = "+".join(sorted(worker_labels)) if worker_labels else "unknown"
        msg = f"🧬 [semiont] babel: {lang} 批次 {n_files} 篇（unified dispatcher, worker={workers_str}）"
        commit = subprocess.run(["git", "commit", "-m", msg], cwd=REPO, capture_output=True, text=True)
        if commit.returncode == 0:
            log(f"✅ committed {lang} ({n_files} files, worker={workers_str})")
            return True

        log(f"🔴 COMMIT FAILED for {lang} — pre-commit rejected staged batch, attempting recovery")
        log((commit.stdout + commit.stderr)[-4000:])

        staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], cwd=REPO, capture_output=True, text=True
        ).stdout.splitlines()
        staged_md = [f for f in staged if f.startswith("knowledge/") and f.endswith(".md")]
        bad = []
        for f in staged_md:
            r = subprocess.run(
                ["python3", "scripts/tools/article-health.py", f, "--profile=pre-commit", "--quiet"],
                cwd=REPO, capture_output=True, text=True,
            )
            if "passed=False" in r.stdout:
                bad.append(f)
        log(f"recovery: {len(bad)}/{len(staged_md)} staged files fail article-health, quarantining")
        for f in bad:
            subprocess.run(["git", "restore", "--staged", f], cwd=REPO, capture_output=True, text=True)
            disposition = restore_head_or_quarantine(f, log)
            log(f"  {disposition}: {f}")

        if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO).returncode != 0:
            msg2 = (f"🧬 [semiont] babel: {lang} 批次 {n_files} 篇"
                    f"（unified dispatcher, worker={workers_str}，post-quarantine retry）")
            commit2 = subprocess.run(["git", "commit", "-m", msg2], cwd=REPO, capture_output=True, text=True)
            if commit2.returncode == 0:
                log("✅ recovery commit succeeded")
            else:
                log("🔴 recovery commit STILL failed — needs manual intervention, leaving staged")
                log((commit2.stdout + commit2.stderr)[-4000:])
        return True
    finally:
        try:
            GIT_LOCK.rmdir()
        except OSError:
            pass


# ────────────────────────── verify trio + HEAD-restore (ported + amended) ──────────────────────────

def verify_one(zh_path: str, trans_path: str, log: Logger) -> tuple[bool, Optional[str]]:
    """The hard gate: verify-translation.py + cjk-leak-check.py +
    article-health.py --profile=pre-commit. Ported from dispatch-node-v3.sh
    verify_group() (per-article body), minus the unlink side effect — the
    caller decides disposition via restore_head_or_quarantine()."""
    r1 = subprocess.run(
        ["python3", "scripts/tools/lang-sync/verify-translation.py", zh_path, trans_path, "--json"],
        cwd=REPO, capture_output=True, text=True,
    )
    try:
        out1 = json.loads(r1.stdout)
    except Exception:
        out1 = {"fails": -1}
    r2 = subprocess.run(
        ["python3", "scripts/tools/lang-sync/cjk-leak-check.py", trans_path],
        cwd=REPO, capture_output=True, text=True,
    )
    leak_fail = r2.returncode != 0
    r3 = subprocess.run(
        ["python3", "scripts/tools/article-health.py", trans_path, "--profile=pre-commit", "--quiet"],
        cwd=REPO, capture_output=True, text=True,
    )
    health_fail = "passed=False" in r3.stdout
    ok = out1.get("fails", 1) == 0 and not leak_fail and not health_fail
    if ok:
        return True, None
    # 失敗原因要帶「是哪幾項」不只「有幾項」——2026-07-27 診斷 verify 類失敗時
    # 發現 `verify=4` 只記數量，log 與 report.jsonl 都查不出敗在哪個檢查，
    # 等於失敗不可診斷（本檔 §儀器化：工具存在不等於問題被檢查）。
    if health_fail:
        # health 分支也要帶項目名。同日修 verify 分支時只改了一半，隔一小時
        # 追 health 失敗就撞上同樣的死路（檔案已 HEAD-restore、log 只寫
        # 「health」，無從得知敗在哪個檢查）——同型病要 grep 全部分支，
        # 這是本檔 §儀器化的第五次驗證。
        # article-health.py renders hard failures with 🔴. Keep ❌ accepted for
        # compatibility with older output captured in long-running workers.
        hnames = re.findall(
            r"(?:🔴|❌)\s+([a-z0-9][a-z0-9 _-]{2,40}?)\s+hard=[1-9]",
            r3.stdout,
        )
        reason = "health" + (f" [{', '.join(hnames[:4])}]" if hnames else "")
    elif leak_fail:
        reason = "leak"
    else:
        failed_names = [c.get("name", "?") for c in (out1.get("checks") or [])
                        if c.get("level") == "FAIL"]
        reason = f"verify={out1.get('fails')}"
        if failed_names:
            reason += f" [{', '.join(failed_names[:4])}]"
    log(f"❌ GATE FAIL {trans_path} ({reason})")
    return False, reason


def restore_head_or_quarantine(path_str: str, log: Logger) -> str:
    """2026-07-24 orchestrator amendment (founder.md 「寧可 stale 也不要
    missing」). Called whenever a translated file is in a bad state after a
    worker's attempt (gate-fail on a produced file, OR the file vanished /
    was never written — e.g. translate.py's own too-small-output unlink,
    which can destroy a just-overwritten stale HEAD version before our
    external verify even runs).

    - If `path_str` exists in git HEAD: restore that exact version. The
      working tree then byte-matches HEAD, so the later `git add` stages
      nothing for this path — the article silently stays stale and is
      retried next round.
    - Only if HEAD has no such path (a genuine P0 attempt that never had a
      committed translation) does this actually unlink → true quarantine,
      article returns to the missing list.

    Returns "restored" | "unlinked".
    """
    p = REPO / path_str
    check = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{path_str}"], cwd=REPO, capture_output=True
    )
    if check.returncode == 0:
        show = subprocess.run(
            ["git", "show", f"HEAD:{path_str}"], cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if show.returncode == 0:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(show.stdout)
            log(f"♻️  restored {path_str} to HEAD version (寧可 stale 也不要 missing)")
            return "restored"
        log(f"⚠️  {path_str}: in HEAD but `git show` failed — unlinking as fallback")
    p.unlink(missing_ok=True)
    return "unlinked"


# ────────────────────────── semantic-noop bump (2026-07-27) ──────────────────────────
# reports/semantic-noop-stale-2026-07-27.md: ~66% of `stale` tasks turn out to be zh
# diffs that are punctuation/whitespace-only (半形逗號→全形、句中分號改句號 etc) —
# zero semantic impact on any translation, since every target language keeps its own
# punctuation conventions regardless of how zh punctuates. Those don't need a model
# call at all: just bump the translation's provenance hashes to the new zh commit.
# semantic-noop-check.py does the (conservative, single-responsibility) judging;
# bump_source_sha.bump_one() does the actual frontmatter write (genuine reuse via the
# importlib load above, not a re-implementation). A model-free hit here still passes
# through the SAME verify-translation.py hard gate as a real translation — if it
# fails (e.g. an unrelated pre-existing passthrough-field drift, observed once during
# validation on pt/Art/li-poetry-society.md), the write is reverted and the task falls
# through to the normal patch/full-translate path below, unchanged.

def zh_current_provenance(zh_path: str) -> tuple[str, str, str]:
    """(sha8, contentHash, bodyHash) for the CURRENT zh source, computed exactly the
    way status.py does (imported, not reimplemented) so the bumped frontmatter matches
    what the next status.py refresh computes — the article reads 'fresh', not stale
    again on the next round."""
    full = KNOWLEDGE / zh_path
    content = full.read_text(encoding="utf-8")
    sha_out = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", f"knowledge/{zh_path}"],
        cwd=REPO, capture_output=True, text=True,
    ).stdout.strip()
    sha8 = sha_out[:8] if sha_out else ""
    return sha8, status_lib.body_hash(content), status_lib.body_hash_pure(content)


def try_semantic_noop_bump(zh_path: str, trans_path: str, log: Logger) -> bool:
    """Returns True iff the stale task at (zh_path, trans_path) was resolved by a
    zero-cost provenance bump (no model call). False means "proceed with the normal
    patch/full-translate path" — the caller does not need to know why (checker said
    no / bump was a no-change race / post-bump verify gate rejected it)."""
    r = subprocess.run(
        ["python3", str(NOOP_CHECKER), zh_path, trans_path, "--json"],
        cwd=REPO, capture_output=True, text=True,
    )
    try:
        verdict = json.loads(r.stdout) if r.stdout.strip() else {}
    except json.JSONDecodeError:
        verdict = {}
    if not verdict.get("noop"):
        return False

    target = REPO / trans_path
    if not target.exists():
        return False
    original_bytes = target.read_bytes()

    sha8, content_hash, body_hash_v = zh_current_provenance(zh_path)
    if not sha8:
        log(f"⚠️  semantic-noop-bump: 無法取得 {zh_path} 目前 commit sha，放棄，走正常翻譯路徑")
        return False

    changed = bump_source_sha.bump_one(target, sha8, content_hash, body_hash_v, apply=True)
    if not changed:
        return False  # already at latest sha (race with another engine) — not a failure, just nothing to do

    ok, reason = verify_one(zh_path, trans_path, log)
    if not ok:
        target.write_bytes(original_bytes)
        log(f"↩️  semantic-noop-bump 還原 {trans_path}（verify 沒過：{reason}）— 走正常翻譯路徑")
        return False

    log(f"✨ semantic-noop-bump {trans_path} → {sha8}（zh diff 只有標點/空白：{verdict.get('reason')}，未呼叫任何模型）")
    return True


# ────────────────────────── round-state ──────────────────────────

class RunState:
    def __init__(self):
        self.lock = threading.Lock()
        self.total_ok: int = 0                            # run 累計成功數（空轉偵測用）
        self.pending_ok: dict = defaultdict(int)          # lang -> count since last commit
        self.pending_since: dict = {}                     # lang -> monotonic time of first pending item
        self.pending_workers: dict = defaultdict(set)     # lang -> {worker labels} since last commit
        self.pending_files: dict = defaultdict(list)      # lang -> [trans_path] since last commit — the
                                                            # ONLY paths git_lock_commit is allowed to add
                                                            # (never a directory wildcard — see git_lock_commit
                                                            # docstring, 2026-07-24 cross-engine incident)
        self.last_worker: dict = {}                       # "lang:zh" -> worker label (soft retry-avoid)
        self.quarantine_log: dict = defaultdict(set)       # lang -> {zh_path} — audit trail
        self.fail_counts: dict = defaultdict(int)          # "lang:zh" -> 累計失敗次數（跨 run 持久化）。
        # 難篇記憶跨 run 保留——不然每次重啟都先拿同一批撞牆文章開刀，
        # 而它們正是最不可能成功的（2026-07-26 優先序佇列改造）。
        try:
            if FAIL_MEMO.exists():
                self.fail_counts.update(json.loads(FAIL_MEMO.read_text(encoding="utf-8")))
        except Exception:
            pass
                                                            # 2026-07-25：原本 quarantine_log 刻意「不排除
                                                            # 未來輪次」讓文章下一輪重試，但沒有退避——同一篇
                                                            # 失敗後立刻被重撈、再失敗、再重撈，撞上 10 分鐘
                                                            # mtime dedupe 就變純空轉。實測 classic track 200
                                                            # 輪只處理 50 篇，約 190 輪空轉。重試仍是對的
                                                            # （多數 gate fail 是模型當次品質問題，換一輪常會過），
                                                            # 但同一篇連 MAX_RETRIES 次失敗就本 run 停手，
                                                            # 把輪次讓給還沒試過的文章。
        self.in_flight: set = set()                        # "lang:zh" currently dispatched (claim protocol)


class TaskQueue:
    """Shared round queue. Tasks are (lang, group_path, zh_path). claim()
    applies a soft last-worker-avoidance preference (2026-07-24 amendment
    spec: quarantined articles "retried next round, preferably by a
    different worker")."""

    def __init__(self, tasks: list):
        self._dq = deque(tasks)
        self._lock = threading.Lock()

    def claim(self, worker_label: str, last_worker: dict):
        with self._lock:
            n = len(self._dq)
            for _ in range(n):
                task = self._dq.popleft()
                lang, _gpath, zh_path = task
                if last_worker.get(f"{lang}:{zh_path}") == worker_label and self._dq:
                    self._dq.append(task)  # try to give it to someone else first
                    continue
                return task
            return None

    def __len__(self):
        with self._lock:
            return len(self._dq)


# ────────────────────────── status / worklist ──────────────────────────

def refresh_status(log: Logger) -> dict:
    r = subprocess.run(
        ["python3", "scripts/tools/lang-sync/status.py"], cwd=REPO, capture_output=True, text=True
    )
    log(r.stdout.strip())
    if r.returncode != 0:
        log(f"⚠️  status.py refresh exit={r.returncode}\n{r.stderr[-1000:]}")
    return json.loads(STATUS_JSON.read_text(encoding="utf-8"))


def default_langs(status_data: dict) -> list:
    result = []
    for lang in ENABLED_TRANSLATION_LANGS:
        s = status_data["_meta"]["summary"].get(lang, {})
        if s.get("missing", 0) > 0 or s.get("stale", 0) > 0 or s.get("metadata_stale", 0) > 0:
            result.append(lang)
    return result


FRESH_WINDOW_DAYS = 5   # 見 build_worklist：新文章的最高優先窗口


def build_worklist(status_data: dict, lang: str, priority: str, order: str,
                    fail_counts: dict | None = None) -> list:
    """四層優先序佇列。

    排序鍵由外到內：
      ① 失敗次數（撞牆多的沉底，不排除——2026-07-26 哲宇 directive
         「失敗的往後排，往下繼續嘗試新的，逐步過濾出不容易處理的文章」）
      ② **新鮮窗**：zh 最後編輯在 FRESH_WINDOW_DAYS 內的文章整批插隊到最前，
         凌駕 P0/P1（2026-07-27 哲宇 directive「最近 5 天內的最新文章排最高
         優先序，日期近的更前面」）。剛寫好或剛大修的文章是讀者當下會看的，
         也是站上編輯標準最新的一批，晚一天翻就少一天的多語觸及。
      ③ P0/P1（缺頁先於過期）
      ④ zh 編輯時間新到舊

    新鮮窗內部同樣依 ①③④ 排（失敗沉底照舊生效，避免新文章裡的硬骨頭
    霸佔隊首），但 `--order reverse` 對它無效——新鮮窗的定義就是由新到舊。
    """
    by_article = status_data["byArticle"]
    fail_counts = fail_counts or {}
    fresh_cut = datetime.now().astimezone() - timedelta(days=FRESH_WINDOW_DAYS)

    def _mtime(raw: str):
        # lastModified 帶時區偏移（…+08:00），字串比較會被不同 offset 騙，
        # 一律解析成 aware datetime 再比。
        try:
            return datetime.fromisoformat(raw)
        except Exception:
            return datetime.min.replace(tzinfo=timezone.utc)

    fresh, p0, p1 = [], [], []
    for zh, info in by_article.items():
        t = info.get("translations", {}).get(lang, {})
        st = t.get("status")
        if st not in ("missing", "stale", "metadata-stale"):
            continue
        raw = info["zh"]["lastModified"]
        nfail = fail_counts.get(f"{lang}:{zh}", 0)
        tier = 0 if st == "missing" else 1          # P0 先於 P1
        entry = (zh, raw, nfail, tier)
        if _mtime(raw) >= fresh_cut:
            fresh.append(entry)
        elif st == "missing":
            p0.append(entry)
        else:
            p1.append(entry)

    # 先按 zh 最後編輯時間排（新的優先，對齊 prepare-batch --top）
    for bucket in (fresh, p0, p1):
        bucket.sort(key=lambda x: _mtime(x[1]), reverse=True)
    if order == "reverse":
        p0 = list(reversed(p0))          # 新鮮窗永遠新到舊，不受 reverse 影響
        p1 = list(reversed(p1))
    # 新鮮窗內：失敗沉底 → 純日期新到舊。**刻意不分 P0/P1**——哲宇的話是
    # 「日期近的在更前面」，窗內若再按缺頁/過期分層，昨天的缺頁會插到今天的
    # 過期前面，違反本意。窗外才輪到 P0/P1 分層。
    fresh.sort(key=lambda x: x[2])
    # 其餘：失敗沉底
    p0.sort(key=lambda x: x[2])
    p1.sort(key=lambda x: x[2])

    fresh_p0 = [z for z, _, _, tier in fresh if tier == 0]
    fresh_p1 = [z for z, _, _, tier in fresh if tier == 1]
    p0_paths = fresh_p0 + [z for z, _, _, _ in p0]
    p1_paths = fresh_p1 + [z for z, _, _, _ in p1]
    if priority == "all":
        # 新鮮窗整批（含 stale）優先於一般 P0
        return ([z for z, _, _, _ in fresh]
                + [z for z, _, _, _ in p0] + [z for z, _, _, _ in p1])
    if priority == "p0":
        return p0_paths
    if priority == "p1":
        return p1_paths
    return p0_paths + p1_paths  # all: P0 first, then P1


def build_slug_map(run_dir: Path) -> Path:
    """From knowledge/_translations.json: for every zh_path with a translation
    in ANY language, slug = that file's basename without .md. Shared across all
    target langs (site convention: slug is the same file basename regardless of
    target language).

    Why any-language and not en-only (2026-07-27): the en-only read starved
    every zh article whose filename is pure Chinese and whose en translation
    doesn't exist yet — no en entry meant no slug, no slug meant the ASCII
    fallback produced TBD-NEEDS-SLUG, and collect_and_filter_groups then
    skipped it forever. 27 articles were in that state, 23 of which already
    had a perfectly good canonical slug sitting in ja/es/fr (唐鳳 →
    audrey-tang, 閃靈 → chthonic). The docstring already claimed the slug is
    language-independent; the code just wasn't reading it that way. en still
    wins when present, so existing canonical slugs never shift.

    TBD-NEEDS-SLUG entries are refused outright: knowledge/_translations.json
    can itself carry them (the orphan rescue committed 8 such files), and
    feeding one back in would propagate the placeholder to every other
    language for that article.

    knowledge/_slug-map.json then fills whatever is still empty — the articles
    with no translation in any language yet, where there is nothing to reverse
    it out of. It is deliberately lowest precedence: a curated entry can never
    move a slug that is already live."""
    trans = json.loads(TRANSLATIONS_JSON.read_text(encoding="utf-8"))
    slug_map = {}
    for key, zh_val in trans.items():
        stem = Path(key).stem
        if "TBD-NEEDS-SLUG" in stem:
            continue
        # en wins; any other language only fills a gap it would otherwise leave.
        if key.startswith("en/") or zh_val not in slug_map:
            slug_map[zh_val] = stem
    curated_path = REPO / "knowledge/_slug-map.json"
    if curated_path.exists():
        curated = json.loads(curated_path.read_text(encoding="utf-8"))
        for zh_val, stem in curated.items():
            if zh_val.startswith("_") or not isinstance(stem, str):
                continue  # _readme block
            slug_map.setdefault(zh_val, stem)
    out = run_dir / "slug-map.json"
    out.write_text(json.dumps(slug_map, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return out


def run_prepare_batch(lang: str, zh_paths: list, slug_map_path: Path, round_dir: Path, log: Logger) -> None:
    round_dir.mkdir(parents=True, exist_ok=True)
    worklist_file = round_dir / "worklist.txt"
    worklist_file.write_text("\n".join(zh_paths) + "\n", encoding="utf-8")
    cmd = [
        "python3", "scripts/tools/lang-sync/prepare-batch.py",
        "--lang", lang, "--input", str(worklist_file),
        "--groups", str(len(zh_paths)),          # one group == one article: gives us per-article
        "--slug-map", str(slug_map_path),         # dispatch/timing/report granularity for free
        "--outdir", str(round_dir),
    ]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    log(f"prepare-batch {lang}: exit={r.returncode}")
    log(r.stdout[-1500:])
    if r.returncode not in (0, 2):  # 2 = "some slugs fell back to ASCII placeholder", non-fatal
        log(f"⚠️  prepare-batch {lang} unexpected exit {r.returncode}\n{r.stderr[-1000:]}")


def collect_and_filter_groups(round_dir: Path, lang: str, seen_missing_slug: set, log: Logger) -> list:
    """Post-process prepare-batch.py's output: drop groups whose slug
    resolution failed (TBD-NEEDS-SLUG, logged once per zh_path for the whole
    run), plus cross-engine dedupe with concurrent dispatchers writing the
    same knowledge/{lang}/ tree.

    Dedupe rule is STATUS-AWARE (2026-07-24 v2 — v1 skipped on bare file
    existence, which is wrong for stale work: a stale article's target file
    exists BY DEFINITION, so the classic-langs run skipped its entire P1
    worklist, queueing 14 of ~600). Now:
      - status "missing": file exists >1KB → another engine just created it;
        skip, next round's status refresh reconciles.
      - stale flavors: file existing is the norm; skip only when its mtime is
        within the last 10 min (a concurrent engine just rewrote it)."""
    good = []
    now = time.time()
    for gf in sorted(round_dir.glob("_group-*.json")):
        try:
            data = json.loads(gf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            # 2026-07-26：prepare-batch 偶爾產出被截斷或多寫一份的 group 檔
            #（"Extra data: line 26"），整條產線就在這裡整個崩掉——一個壞掉的
            # 任務檔不該讓上百篇的佇列一起停擺。跳過該檔繼續，並留訊息可追。
            log(f"⚠️  group 檔解析失敗，跳過：{gf.name}（{e}）")
            continue
        arts = data.get("articles", [])
        if not arts:
            continue
        art = arts[0]
        zh_path, en_path = art["zh_path"], art["en_path"]
        status = art.get("status", "missing")
        if "TBD-NEEDS-SLUG" in en_path:
            key = f"{lang}:{zh_path}"
            if key not in seen_missing_slug:
                seen_missing_slug.add(key)
                log(f"⚠️  skip {zh_path} ({lang}): slug resolution failed (TBD-NEEDS-SLUG) — needs --slug-map entry")
            continue
        target = REPO / en_path
        if target.exists() and target.stat().st_size > 1024:
            if status == "missing":
                log(f"⏭️  skip {zh_path} ({lang}): {en_path} already exists (cross-engine dedupe, was missing)")
                continue
            if now - target.stat().st_mtime < 600:
                log(f"⏭️  skip {zh_path} ({lang}): {en_path} rewritten <10min ago (cross-engine dedupe)")
                continue
        good.append((lang, gf, zh_path))
    return good


def interleave_by_lang(per_lang_tasks: dict) -> list:
    """Round-robin across langs so no lang starves a slow one."""
    tasks = []
    iters = [iter(v) for v in per_lang_tasks.values()]
    for row in zip_longest(*iters, fillvalue=None):
        for item in row:
            if item is not None:
                tasks.append(item)
    return tasks


# ────────────────────────── dispatch ──────────────────────────

def do_commit(lang: str, state: RunState, no_commit: bool, log: Logger) -> None:
    with state.lock:
        n = state.pending_ok[lang]
        workers = set(state.pending_workers[lang])
        files = list(state.pending_files[lang])
        state.pending_ok[lang] = 0
        state.pending_workers[lang] = set()
        state.pending_files[lang] = []
        state.pending_since.pop(lang, None)
    if n == 0:
        return
    if no_commit:
        log(f"⏭️  --no-commit: would commit {lang} batch of {n} (workers={sorted(workers)}) files={files}")
        return
    # Refresh derived JSONs FIRST, then take the lock and commit (matches
    # legacy invariant: status/translations caches never lag behind the
    # commit that introduces the files they describe).
    try:
        FAIL_MEMO.write_text(json.dumps(dict(state.fail_counts), ensure_ascii=False),
                             encoding="utf-8")
    except Exception:
        pass
    files.append(str(FAIL_MEMO.relative_to(REPO)))   # 難篇記憶隨批次入版控
    subprocess.run(["python3", "scripts/tools/sync-translations-json.py"], cwd=REPO, capture_output=True, text=True)
    subprocess.run(["python3", "scripts/tools/lang-sync/status.py"], cwd=REPO, capture_output=True, text=True)
    git_lock_commit(lang, workers, files, log)


def process_task(worker: Worker, lang: str, group_path: Path, zh_path: str,
                  state: RunState, report: JsonlWriter, freezes: JsonlWriter,
                  no_commit: bool, commit_every: int, log: Logger,
                  engine: str = "whole", no_patch: bool = False,
                  no_noop_bump: bool = False) -> None:
    data = json.loads(group_path.read_text(encoding="utf-8"))
    art = data["articles"][0]
    trans_path = art["en_path"]
    status = art.get("status", "missing")

    t0 = time.monotonic()
    # 報表欄位必須在所有 engine / output / gate 分支都有值。v1.7 首版誤把
    # 初始化放進 try_semantic_noop_bump()，導致「模型有落檔但 QA fail」時
    # 寫報表觸發 UnboundLocalError，整個 dispatcher（而非單篇）被殺掉。
    structured_fallback = False
    structured_fallback_exit = None

    # 語意無關 stale 零成本 bump（2026-07-27，見上方 try_semantic_noop_bump 註解 +
    # reports/semantic-noop-stale-2026-07-27.md）：在章節級 diff-patch 之前先問一句
    # 「zh diff 是不是只有標點/空白」——命中就直接 bump provenance hash，完全不叫
    # 任何模型，不占用 worker 名額也不算 worker 失敗/成功次數（沒有 worker 真的做事）。
    if status == "stale" and not no_noop_bump and try_semantic_noop_bump(zh_path, trans_path, log):
        elapsed = time.monotonic() - t0
        report.write({
            "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
            "lang": lang, "zh": zh_path, "trans": trans_path,
            "worker": worker.label, "ok": True, "seconds": round(elapsed, 1),
            "fail_reason": None, "disposition": "kept", "via": "semantic-noop-bump",
        })
        # Bookkeeping mirrors the tail of this function's normal success path
        # (kept as an explicit early-return rather than a shared helper — this
        # file runs in 4 concurrently-active pipelines right now and the tail
        # block is load-bearing/tested; duplicating ~12 lines is cheaper than
        # risking a refactor regression in code already in flight).
        with state.lock:
            state.last_worker[f"{lang}:{zh_path}"] = worker.label
            state.in_flight.discard(f"{lang}:{zh_path}")
            state.total_ok += 1
            state.pending_ok[lang] += 1
            state.pending_workers[lang].add(worker.label)
            state.pending_files[lang].append(trans_path)
            state.pending_since.setdefault(lang, time.monotonic())
            age = time.monotonic() - state.pending_since.get(lang, time.monotonic())
            reached = state.pending_ok[lang] >= commit_every or age >= 5400
        if reached:
            do_commit(lang, state, no_commit, log)
        return

    # --lang MUST be explicit: translate.py's --group mode defaults to
    # `lang = args.lang or group_path.parent.name`, and our run-dir layout is
    # tasks/{lang}/round{N}/_group-*.json — parent.name is "round01", not the
    # lang. Without this, LANG_NAMES.get(lang, lang) silently falls through to
    # the literal string "round01" as the target-language name in the
    # translation prompt (caught in the first smoke-test run — 2/2 verify
    # failures, both explained by this bug once inspected).
    def _backend_spec() -> str:
        b = worker.cascade_spec
        if b.split("@")[0] == "ollama":
            m = worker_env(worker).get("OLLAMA_MODEL", "")
            return f"ollama:{m}" if m else "ollama"
        return b

    # 章節級 diff-patch（2026-07-27）：stale 任務先試只重翻被 zh diff 碰過的 H2
    # 章節，未碰章節原樣保留舊譯文——實測全站 stale 改動比例中位 2.8%，整篇重翻
    # 是為 3% 的改動燒 100% 算力。patch-translate.py exit 2 = 章節數不對齊／改動
    # 過大／sha 不可解析等不適合 patch 的情況，fallback 回下面既有的全文路徑；
    # exit 1 = 有試但驗證沒過（patch-translate.py 自己已跑過三重驗證，沒寫檔），
    # 直接沿用既有 gate-fail 處理，不再重試 fallback 全文（避免同一輪對同一篇
    # 燒兩次算力）。
    proc: subprocess.CompletedProcess | None = None
    engine_label = engine
    if status == "stale" and not no_patch:
        pcmd = ["python3", "-u", "scripts/tools/lang-sync/patch-translate.py",
                zh_path, "--lang", lang, "--backend", _backend_spec(), "--out", trans_path]
        pproc = subprocess.run(pcmd, cwd=REPO, env=worker_env(worker), capture_output=True, text=True)
        if pproc.returncode == 2:
            log(f"⏩ patch-translate not applicable ({lang}:{zh_path}, exit=2) — "
                f"fallback to full retranslate\n{(pproc.stdout + pproc.stderr)[-800:]}")
        else:
            proc = pproc
            engine_label = "patch"

    if proc is None:
        if engine == "structured":
            # 分段式引擎吃單篇介面（zh_path 相對 knowledge/、backend 單一 spec）。
            # ollama worker 的 cascade_spec 是裸 "ollama"（模型在 env OLLAMA_MODEL），
            # structured 端要組回 ollama:<model>；openrouter spec 原樣可用。
            cmd = ["python3", "-u", "scripts/tools/lang-sync/structured-translate.py",
                   zh_path, "--lang", lang, "--backend", _backend_spec(),
                   "--out", trans_path, "--skip-validators"]
            # --skip-validators：dispatcher 的 verify trio 是唯一裁判；引擎內建
            # 驗證再跑一次是同一把尺跑兩遍，純浪費。
        else:
            cmd = ["python3", "-u", "scripts/tools/lang-sync/translate.py",
                   "--group", str(group_path), "--lang", lang,
                   "--cascade", worker.cascade_spec, "--no-preflight"]
        proc = subprocess.run(cmd, cwd=REPO, env=worker_env(worker), capture_output=True, text=True)
    elapsed = time.monotonic() - t0

    log(f"--- worker={worker.label} lang={lang} zh={zh_path} engine={engine_label} "
        f"exit={proc.returncode} ({elapsed:.0f}s) ---")
    tail = (proc.stdout + ("\n" + proc.stderr if proc.returncode != 0 else ""))
    log(tail[-3000:])

    target = REPO / trans_path
    # 第一條路徑完全沒落檔時，改用「工具持有 Markdown 結構、模型只翻文字」
    # 的 structured engine 救一次。2026-07-28 近一小時 40 個失敗中有 10 個
    # 是 no-output；它們混合 patch abort、截斷、腳註流失等成因，繼續重試
    # 同一全文路徑只會複製失敗。structured pilot 6/6 全綠，且最後仍走下方
    # 同一組 verify trio，所以這是換路徑，不是放寬品質門檻。
    #
    # 只在「沒有任何產物」時啟用；已有輸出但 gate fail 的條件式 fallback
    # 留待這一小步有實績後再擴，避免一次改兩個變因。
    if not target.exists() and engine != "structured":
        structured_fallback = True
        scmd = [
            "python3", "-u", "scripts/tools/lang-sync/structured-translate.py",
            zh_path, "--lang", lang, "--backend", _backend_spec(),
            "--out", trans_path, "--skip-validators",
        ]
        log(f"   🔁 no-output → structured fallback ({lang}:{zh_path}, worker={worker.label})")
        sproc = subprocess.run(
            scmd, cwd=REPO, env=worker_env(worker), capture_output=True, text=True,
        )
        structured_fallback_exit = sproc.returncode
        elapsed = time.monotonic() - t0
        log(f"--- structured fallback worker={worker.label} lang={lang} zh={zh_path} "
            f"exit={sproc.returncode} ({elapsed:.0f}s total) ---")
        log((sproc.stdout + ("\n" + sproc.stderr if sproc.returncode != 0 else ""))[-3000:])
        proc = sproc
        engine_label = f"{engine_label}→structured"

    # AFTER fallback, BEFORE any restore — worker-health signal.
    produced_by_backend = target.exists() and target.stat().st_size > 0

    if not target.exists():
        disposition = restore_head_or_quarantine(trans_path, log)
        ok, fail_reason = False, f"no output written by translate.py (exit={proc.returncode})"
    else:
        # Normalize with prettier BEFORE the verify trio, so the gates measure
        # the same bytes the commit-time hook will see: .lintstagedrc runs
        # `prettier --write` on staged files BEFORE `article-health --staged`,
        # so un-normalized output can pass the single-file gate and still fail
        # at commit (2026-07-24 smoke test: 0 issues pre-stage → 11
        # footnote-format violations post-prettier on the same file).
        subprocess.run(["npx", "prettier", "--write", trans_path],
                       cwd=REPO, capture_output=True, text=True)
        # passthrough 欄位機械 heal（2026-07-25）：模型常漏抄 image/imageCredit/
        # featured/readingTime 這類「本來就不該翻譯、逐字照抄即可」的欄位，
        # verify 把它算 hard fail 於是整篇好譯文被退掉重翻。實測本輪 verify=1
        # 占 21 次 fail，抽查全是這類；跨三語同篇同時中鏢＝模型共同行為非個案。
        # 判斷力該用在「翻得好不好」，不是「URL 有沒有被複製過去」（§14）。
        hr = subprocess.run(
            ["python3", "scripts/tools/lang-sync/heal-passthrough-fields.py",
             zh_path, trans_path],
            cwd=REPO, capture_output=True, text=True)
        if hr.returncode != 0 or "缺檔" in hr.stdout or hr.stderr.strip():
            # 2026-07-25：首版只看 stdout，heal 因路徑解析 bug 每次失敗卻
            # 一聲不吭，整輪 0 次生效（今天修了一整天的靜默吞錯，我自己
            # 在接線時又寫了一個）。失敗一律出聲。
            log(f"   🔴 passthrough heal 失敗 rc={hr.returncode}: "
                f"{(hr.stdout + hr.stderr).strip()[:200]}")
        elif hr.stdout.strip():
            log(f"   🔧 passthrough heal: {hr.stdout.strip()[:150]}")

        # 內部連結 category 大小寫是純機械格式，不應耗掉整篇翻譯。2026-07-28
        # 隔離樣本覆盤：近一小時 17/17 個 link-target health fail 都是模型把
        # `/people/`、`/history/` 等輸出成 `/People/`、`/History/`；既有
        # article-health fixer 能保守修 casing／decode／高信心 fuzzy，但先前
        # dispatcher 只把它當裁判、沒把已存在的修復接進熱路徑。
        lr = subprocess.run(
            ["python3", "scripts/tools/article-health.py", trans_path,
             "--profile=pre-commit", "--check=link-target", "--fix", "--quiet"],
            cwd=REPO, capture_output=True, text=True,
        )
        if lr.returncode != 0:
            log(f"   🔴 link-target heal 失敗 rc={lr.returncode}: "
                f"{(lr.stdout + lr.stderr).strip()[-300:]}")
        elif lr.stdout.strip():
            log(f"   🔧 link-target heal: {lr.stdout.strip()[-200:]}")

        # 腳註格式也有一小塊能安全機械修復。2026-07-28 隔離樣本覆盤：
        # 最新 8 個 footnote-format fail 中，safe-only fixer 完整救回 1 個，
        # 另 2 個只修掉安全子集、仍由 hard gate 擋下；其餘 5 個完全不動。
        # fixer 刻意不碰 APA／多連結等可能遺失資訊的格式，所以接進熱路徑
        # 不會放寬 gate，只省掉「純缺 description」這類確定性重翻。
        fr = subprocess.run(
            ["python3", "scripts/tools/article-health.py", trans_path,
             "--profile=pre-commit", "--check=footnote-format", "--fix", "--quiet"],
            cwd=REPO, capture_output=True, text=True,
        )
        if fr.returncode != 0:
            log(f"   🔴 footnote-format heal 失敗 rc={fr.returncode}: "
                f"{(fr.stdout + fr.stderr).strip()[-300:]}")
        elif fr.stdout.strip():
            log(f"   🔧 footnote-format heal: {fr.stdout.strip()[-200:]}")

        ok, fail_reason = verify_one(zh_path, trans_path, log)
        if not ok:
            # 隔離前存證（2026-07-24）：失敗 blob 直接 unlink/restore 就沒有
            # 屍體可驗，反覆 fail 的 pattern 只能用猜的。留一份在 run dir
            # 供 post-mortem（gate 假陽性家族診斷全靠這個）。
            try:
                qdir = report.path.parent / "quarantine"
                qdir.mkdir(exist_ok=True)
                (qdir / f"{lang}--{Path(trans_path).stem}.md").write_text(
                    target.read_text(encoding="utf-8"), encoding="utf-8")
            except Exception:
                pass
        disposition = "kept" if ok else restore_head_or_quarantine(trans_path, log)

    report.write({
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "lang": lang, "zh": zh_path, "trans": trans_path,
        "worker": worker.label, "ok": ok, "seconds": round(elapsed, 1),
        "fail_reason": fail_reason, "disposition": disposition,
        "engine": engine_label,
        "structured_fallback": structured_fallback,
        "structured_fallback_exit": structured_fallback_exit,
    })

    with state.lock:
        state.last_worker[f"{lang}:{zh_path}"] = worker.label
        if not ok:
            state.quarantine_log[lang].add(zh_path)
            state.fail_counts[f"{lang}:{zh_path}"] += 1
        state.in_flight.discard(f"{lang}:{zh_path}")

    # Worker health: 3 consecutive hard failures (exit!=0 AND the backend
    # never even produced a file) → freeze 30min. A gate-fail on output the
    # backend DID produce is a quality issue, not a worker-availability
    # issue, so it does not count here.
    hard_fail = proc.returncode != 0 and not produced_by_backend
    if hard_fail:
        worker.consecutive_failures += 1
        if worker.consecutive_failures >= 3:
            worker.frozen_until = time.monotonic() + 30 * 60
            worker.consecutive_failures = 0
            freezes.write({
                "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
                "worker": worker.label, "reason": "3 consecutive hard failures (no output produced)",
                "frozen_for_s": 1800,
            })
            log(f"🥶 FREEZE worker={worker.label} for 30min — 3 consecutive hard failures")
    else:
        worker.consecutive_failures = 0

    if ok:
        with state.lock:
            state.total_ok += 1
            state.pending_ok[lang] += 1
            state.pending_workers[lang].add(worker.label)
            state.pending_files[lang].append(trans_path)
            state.pending_since.setdefault(lang, time.monotonic())
            # 門檻或年齡任一到就 commit——年齡檢查原本只在輪次結束跑，但一輪
            # 可能長達數小時，譯文在工作區懸空（2026-07-25 21:32 實測 30+ 篇
            # 未 commit 懸空 2 小時）。懸空檔案會被並行 session 的 merge 防護
            # 誤掃，風險大於多一個零頭 commit。
            age = time.monotonic() - state.pending_since.get(lang, time.monotonic())
            reached = state.pending_ok[lang] >= commit_every or age >= 5400
        if reached:
            do_commit(lang, state, no_commit, log)


def wait_if_frozen(worker: Worker, workers: list, log: Logger) -> None:
    while True:
        now = time.monotonic()
        if not worker.frozen_until or now >= worker.frozen_until:
            return
        if all(w.frozen_until and w.frozen_until > now for w in workers):
            log("🥶 all workers frozen — sleeping 5min (work still queued)")
            time.sleep(300)
        else:
            time.sleep(10)


def worker_loop(worker: Worker, workers: list, queue: TaskQueue, state: RunState,
                 report: JsonlWriter, freezes: JsonlWriter, no_commit: bool,
                 commit_every: int, log: Logger,
                 engine: str = "whole", no_patch: bool = False,
                 no_noop_bump: bool = False) -> None:
    while True:
        wait_if_frozen(worker, workers, log)
        with state.lock:
            last_worker_snapshot = dict(state.last_worker)
        task = queue.claim(worker.label, last_worker_snapshot)
        if task is None:
            return
        lang, group_path, zh_path = task
        with state.lock:
            state.in_flight.add(f"{lang}:{zh_path}")
        process_task(worker, lang, group_path, zh_path, state, report, freezes, no_commit, commit_every, log,
                     engine=engine, no_patch=no_patch, no_noop_bump=no_noop_bump)


# ────────────────────────── main ──────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Unified worker-pool translation batch dispatcher (replaces the hand-rolled "
                     "bash dispatchers dispatch-node-v3.sh / run-p1-v3.sh).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""example:
  python3 scripts/tools/lang-sync/babel-dispatch.py \\
    --langs vi,id,pt,hi \\
    --worker "nemo=openrouter:nvidia/nemotron-3-ultra-550b-a55b:free" \\
    --worker "gemma31=openrouter:google/gemma-4-31b-it:free" \\
    --worker "laguna=openrouter:poolside/laguna-xs-2.1:free" \\
    $(~/Projects/muse-bot/fleet/fleetctl workers --service llm --format babel) \\
    --order reverse --rounds 50 --commit-every 10
""",
    )
    ap.add_argument("--langs", default=None,
                     help="comma-separated target langs (default: ENABLED_TRANSLATION_LANGS "
                          "with any missing/stale)")
    ap.add_argument("--worker", action="append", dest="workers", default=[],
                     metavar="label=backendspec[@host]",
                     help="repeatable. backendspec passed to translate.py --cascade verbatim "
                          "(stripped of @host first). @host + ollama backend → OLLAMA_HOST/"
                          "OLLAMA_MODEL env for that worker's subprocesses.")
    ap.add_argument("--order", choices=["reverse", "forward"], default="reverse",
                     help="reverse (default) = process each priority's worklist from the tail "
                          "(anti-collision vs legacy dispatchers, which eat from the head)")
    ap.add_argument("--rounds", type=int, default=50)
    # default 50：2026-07-25 哲宇 directive「commit 50 篇 50 篇做好了，不然
    # 感覺有點洗版 commit history」——多產線 × 每 10 篇一 commit 曾把 git log
    # 刷成整頁 babel 批次。
    ap.add_argument("--commit-every", type=int, default=50,
                     help="commit after this many verified-ok files per lang (also flushed at "
                          "end of each round)")
    ap.add_argument("--max-articles", type=int, default=None, help="global cap across the whole run (smoke tests)")
    ap.add_argument("--no-commit", action="store_true", help="skip git commit (smoke tests)")
    ap.add_argument("--engine", choices=["whole", "structured"], default="whole",
                    help="翻譯引擎：whole=整篇式 translate.py（預設）；structured=分段式 "
                         "structured-translate.py（模型只翻文字、結構由工具持有——"
                         "passthrough/腳註編號/YAML 三類 fail 構造上不會發生；"
                         "pilot 6/6 全綠 2026-07-25，見 reports/structured-translation-pilot）")
    ap.add_argument("--priority", choices=["p0", "p1", "all"], default="all",
                     help="p0=missing only, p1=stale+metadata-stale only, all=P0 first then P1 (default)")
    ap.add_argument("--no-patch", action="store_true",
                     help="disable the chapter-level diff-patch engine (patch-translate.py) for "
                          "stale tasks — always fall back to full retranslation (2026-07-27)")
    ap.add_argument("--no-noop-bump", action="store_true",
                     help="disable the zero-cost semantic-noop bump for stale tasks whose zh diff "
                          "is punctuation/whitespace-only — always go through patch/full-translate "
                          "instead (2026-07-27, see reports/semantic-noop-stale-2026-07-27.md)")
    args = ap.parse_args()

    if not args.workers:
        ap.error("at least one --worker is required")
    workers = [parse_worker_arg(w) for w in args.workers]
    labels = [w.label for w in workers]
    if len(labels) != len(set(labels)):
        ap.error(f"--worker labels must be unique, got: {labels}")

    if args.langs:
        langs_requested = [x.strip() for x in args.langs.split(",") if x.strip()]
        for l in langs_requested:
            if l not in ALL_TRANSLATION_LANGS:
                ap.error(f"unknown lang {l!r} — not in langs.py ALL_TRANSLATION_LANGS {ALL_TRANSLATION_LANGS}")
    else:
        langs_requested = None  # resolved after first status refresh

    run_dir = Path(f"/tmp/babel-unified-{datetime.now().strftime('%Y%m%d-%H%M')}")
    run_dir.mkdir(parents=True, exist_ok=True)
    print(run_dir)  # run dir path — first thing printed, per spec

    log = Logger(run_dir / "master.log")
    report = JsonlWriter(run_dir / "report.jsonl")
    freezes = JsonlWriter(run_dir / "freezes.jsonl")

    log(f"START babel-dispatch.py {datetime.now().astimezone().isoformat(timespec='seconds')}")
    log(f"  run_dir={run_dir}")
    log(f"  workers={[(w.label, w.cascade_spec, w.host) for w in workers]}")
    log(f"  order={args.order} rounds={args.rounds} commit_every={args.commit_every} "
        f"priority={args.priority} max_articles={args.max_articles} no_commit={args.no_commit} "
        f"engine={args.engine} no_patch={args.no_patch} no_noop_bump={args.no_noop_bump}")

    state = RunState()
    seen_missing_slug: set = set()
    total_enqueued = 0

    barren_rounds = 0            # 連續零產出輪數（空轉偵測，見下方 break）
    for round_num in range(1, args.rounds + 1):
        log(f"\n===== ROUND {round_num} {datetime.now().astimezone().isoformat(timespec='seconds')} =====")
        ok_before_round = state.total_ok
        status_data = refresh_status(log)

        langs = langs_requested or default_langs(status_data)
        if not langs:
            log("No target langs (nothing missing/stale anywhere) — done.")
            break

        slug_map_path = build_slug_map(run_dir)

        remaining_budget = None
        if args.max_articles is not None:
            remaining_budget = args.max_articles - total_enqueued
            if remaining_budget <= 0:
                log(f"max-articles budget ({args.max_articles}) exhausted — stopping.")
                break

        # 跨產線失敗記憶合併（2026-07-26 二修）：多條產線的語言互相重疊，
        # 各自的 fail_counts 只有自己的帳——實測同一篇 70 分鐘被不同產線合計
        # 撞 8 次。每輪開始從磁碟 max-merge 別條產線寫的記憶，撞牆的文章在
        # 所有產線一起沉底。首版只在 commit 時存檔，而 commit 要累積 50 篇，
        # 低通過率時整個 run 一次都沒存——記憶檔從未誕生。
        try:
            if FAIL_MEMO.exists():
                for k, v in json.loads(FAIL_MEMO.read_text(encoding="utf-8")).items():
                    if v > state.fail_counts.get(k, 0):
                        state.fail_counts[k] = v
        except Exception:
            pass

        per_lang_tasks: dict = {}
        for lang in langs:
            # 失敗次數決定優先序（2026-07-26 改，此前是硬性 exclude）：撞牆多次
            # 的沉到隊尾，沒試過的先跑，算力優先花在有機會成功的文章上。
            # fail_counts 跨 run 持久化，所以重啟不會又從同一批難篇開始撞。
            worklist = build_worklist(status_data, lang, args.priority, args.order,
                                       fail_counts=state.fail_counts)
            cap = 10 * len(workers)
            if remaining_budget is not None:
                cap = min(cap, remaining_budget - sum(len(v) for v in per_lang_tasks.values()))
            worklist = worklist[: max(cap, 0)]
            if not worklist:
                continue
            round_dir = run_dir / "tasks" / lang / f"round{round_num:02d}"
            run_prepare_batch(lang, worklist, slug_map_path, round_dir, log)
            groups = collect_and_filter_groups(round_dir, lang, seen_missing_slug, log)
            if groups:
                per_lang_tasks[lang] = groups

        if not per_lang_tasks:
            log("All target langs have empty worklists this round — done.")
            break

        tasks = interleave_by_lang(per_lang_tasks)
        total_enqueued += len(tasks)
        log(f"Round {round_num}: {len(tasks)} article(s) queued across {len(per_lang_tasks)} lang(s) "
            f"({', '.join(f'{l}={len(v)}' for l, v in per_lang_tasks.items())})")

        queue = TaskQueue(tasks)
        with ThreadPoolExecutor(max_workers=len(workers)) as pool:
            futures = [
                pool.submit(worker_loop, w, workers, queue, state, report, freezes,
                            args.no_commit, args.commit_every, log,
                            engine=args.engine, no_patch=args.no_patch, no_noop_bump=args.no_noop_bump)
                for w in workers
            ]
            for f in futures:
                f.result()

        # 2026-07-25 哲宇 callout「中間為啥還是 commit 的那麼散」：原本每輪結束
        # 無條件 flush 零頭（1-8 篇的 commit 一輪一串），--commit-every 50 形同
        # 只對單輪內的大批有效。改成跨輪累積：只有零頭放超過 90 分鐘才時間性
        # flush（防 run 中途死掉時未 commit 的工作懸空太久），其餘累到門檻才出手。
        FLUSH_AGE_S = 5400
        now = time.monotonic()
        for lang in list(per_lang_tasks.keys()):
            since = state.pending_since.get(lang)
            if since is not None and now - since >= FLUSH_AGE_S:
                do_commit(lang, state, args.no_commit, log)

        # 失敗記憶每輪落盤（read-merge-write，原子替換；並行產線互相看得見）
        try:
            merged = dict(state.fail_counts)
            if FAIL_MEMO.exists():
                for k, v in json.loads(FAIL_MEMO.read_text(encoding="utf-8")).items():
                    if v > merged.get(k, 0):
                        merged[k] = v
            tmpf = FAIL_MEMO.with_suffix(".tmp")
            tmpf.write_text(json.dumps(merged, ensure_ascii=False), encoding="utf-8")
            tmpf.replace(FAIL_MEMO)
        except Exception:
            pass

        # 空轉偵測（2026-07-26）：worker 的 endpoint 掛掉時（遠端機器離線、
        # ollama 服務停），既有的 freeze 機制會把它凍結，但**單 worker 產線的
        # 唯一 worker 被凍結後，round loop 照樣一輪一輪跑 prepare-batch**——
        # process 活著、log 在動、實際零產出。實撞：l4090 專軌在遠端機器離線後
        # 空轉到第 127 輪才被發現，ps 看起來完全正常。
        # 連續三輪零產出就結束 run，讓外部監護（渦流檢查或 routine）重新起跑。
        if state.total_ok == ok_before_round:
            barren_rounds += 1
            if barren_rounds >= 3:
                log(f"🛑 連續 {barren_rounds} 輪零產出 — 判定空轉（worker endpoint 可能全掛），"
                    f"結束 run 讓外部重新起跑")
                break
        else:
            barren_rounds = 0

        if args.max_articles is not None and total_enqueued >= args.max_articles:
            log(f"max-articles budget ({args.max_articles}) reached after round {round_num} — stopping.")
            break
    else:
        log(f"Reached --rounds limit ({args.rounds}) without exhausting the worklist.")

    # run 結束：把所有語言的零頭一次收乾淨（唯一的無條件 flush 點）
    for lang in list(state.pending_ok.keys()):
        do_commit(lang, state, args.no_commit, log)

    log("\n===== FINAL STATUS =====")
    final = refresh_status(log)
    for lang in (langs_requested or default_langs(final)) or ENABLED_TRANSLATION_LANGS:
        s = final["_meta"]["summary"].get(lang)
        if s:
            log(f"  {lang}: fresh={s['fresh']} stale={s['stale']} missing={s['missing']} "
                f"metadata_stale={s.get('metadata_stale', 0)}")
    log(f"quarantine_log this run: {dict((k, sorted(v)) for k, v in state.quarantine_log.items())}")
    # 難篇清單：累計失敗次數分層，這本身是產物不是噪音——沉底的那批可以拿去
    # 換模型專攻或人工看（2026-07-26 優先序佇列改造）
    tiers = {}
    for k, n in state.fail_counts.items():
        tiers.setdefault(min(n, 5), []).append(k)
    if tiers:
        log("難篇分層（累計失敗次數 → 佇列優先序，多的沉底但不放棄）：")
        for n in sorted(tiers, reverse=True):
            items = sorted(tiers[n])
            log(f"  {n}× 失敗：{len(items)} 篇" +
                (f" — {items[:5]}{' …' if len(items) > 5 else ''}" if n >= 3 else ""))
        log(f"  記憶已存 {FAIL_MEMO}（下個 run 續用，不會又從難篇開始撞）")
    log("DONE")


if __name__ == "__main__":
    main()
