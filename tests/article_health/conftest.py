"""Test config — adjust sys.path so `lib.article_health` is importable."""

import sys
from pathlib import Path

# Add scripts/tools to path so `from lib.article_health import ...` works
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "scripts" / "tools"))
