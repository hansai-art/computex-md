"""Regression tests — terminology-*.py scripts must derive BASE_DIR from
script location, not hardcoded `/Users/cheyuwu/taiwan-md`.

Audit O5 (2026-05-04): the hardcoded path broke for non-cheyuwu users
and worktree contexts. Fix: `Path(__file__).resolve().parents[2]`.

This test runs the terminology scripts and asserts they don't crash with
"file not found" — which would happen if BASE_DIR was wrong.
"""

import subprocess
from pathlib import Path

import pytest


SCRIPTS = [
    "scripts/tools/terminology-yaml-audit.py",
    "scripts/tools/terminology-yaml-clean.py",
    "scripts/tools/terminology-yaml-dedup.py",
    "scripts/tools/terminology-prose-fix.py",
]


def test_no_hardcoded_user_paths():
    """No `/Users/cheyuwu/...` hardcoded literal in the path-derivation lines."""
    repo_root = Path(__file__).resolve().parents[2]
    for script in SCRIPTS:
        text = (repo_root / script).read_text(encoding="utf-8")
        # The literal must not appear as a Path() arg (allowing comments to mention it)
        for line in text.splitlines():
            if line.strip().startswith("#"):
                continue
            assert 'Path("/Users/cheyuwu' not in line, (
                f"{script}: hardcoded user path found: {line.strip()}"
            )


def test_terminology_audit_imports_cleanly():
    """Module imports without crashing — verifies BASE_DIR resolves to a real dir."""
    repo_root = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        [
            "python3",
            "-c",
            (
                "import sys; sys.path.insert(0, 'scripts/tools'); "
                "import importlib.util; "
                "spec = importlib.util.spec_from_file_location('m', 'scripts/tools/terminology-yaml-audit.py'); "
                "mod = importlib.util.module_from_spec(spec); "
                "spec.loader.exec_module(mod); "
                "print(str(mod.BASE_DIR))"
            ),
        ],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert proc.returncode == 0, f"stderr: {proc.stderr}"
    base_dir = proc.stdout.strip()
    # BASE_DIR should resolve to repo root (where data/, scripts/, knowledge/ live)
    assert (Path(base_dir) / "data").exists() or (Path(base_dir) / "scripts").exists(), (
        f"BASE_DIR={base_dir} doesn't look like repo root"
    )
