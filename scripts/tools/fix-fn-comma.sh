#!/bin/bash
#
# fix-fn-comma.sh — bad_fn_format Pattern 2 auto-fixer
#
# Replaces footnote lines of shape:
#   [^n]: [Name](URL)，description text
# with the canonical:
#   [^n]: [Name](URL) — description text
#
# Why only Pattern 2:
# - Pattern 1 (no link)            → needs human research, no URL to format
# - Pattern 2 (link + 中文逗號)     → mechanical: 「)，」 → 「) — 」
# - Pattern 3 (link + no desc)     → needs reading the linked page to write a description
# - Pattern 4 (text-first then link) → needs rewrite of footnote structure
#
# Pattern 2 is the only one that's a pure mechanical typography fix:
# the description already exists, the URL already exists, the only thing
# wrong is that the author used a Chinese full-width comma instead of an
# em dash as the separator between citation and description.
#
# Scope:
#   knowledge/*.md (main zh-TW articles only — same scope as format-check.sh)
#   excludes en/ja/ko/es/resources subfolders and _Hub files
#
# Usage:
#   bash scripts/tools/fix-fn-comma.sh             # dry-run (shows diff, no writes)
#   bash scripts/tools/fix-fn-comma.sh --apply     # actually rewrite files
#   bash scripts/tools/fix-fn-comma.sh --apply --quiet   # silent apply
#
# After applying, run `bash scripts/core/sync.sh` to propagate to src/content/.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

APPLY=0
QUIET=0
for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=1 ;;
    --quiet) QUIET=1 ;;
    -h|--help)
      grep -E '^# ' "$0" | sed 's/^# \?//'
      exit 0
      ;;
    *)
      echo "Unknown arg: $arg" >&2
      exit 2
      ;;
  esac
done

# Footnote line pattern matching p2:
#   [^anything]: [link text](http(s)://...)，description (10+ chars after comma)
# Using POSIX ERE because it has to work with both BSD sed (macOS) and GNU sed.
# We let Perl/Python do the heavy lifting for safer multibyte handling.

# Find candidate files (same scope as format-check.sh)
# Use process substitution + while loop instead of mapfile
# (mapfile isn't available in bash 3.x shipped on macOS).

TOTAL_FOUND=0
TOTAL_FILES_CHANGED=0
CHANGED_FILES=""

while IFS= read -r f; do
  # Use Python for multibyte-safe regex match-and-replace.
  # Pattern: line starts with [^id]: [text](http(s)://...)，desc
  #          where desc has at least 10 characters
  # Replace: ) — between the closing paren and the description
  python_out=$(python3 - "$f" <<'PY'
import sys, re, pathlib
path = pathlib.Path(sys.argv[1])
content = path.read_text(encoding='utf-8')
# Anchored to line start, captures: prefix, then closing-paren-comma, then description
pattern = re.compile(
    r'^(\[\^[\w-]+\]: \[[^\]]+\]\(https?://[^)]+\))，(.{10,})$',
    re.MULTILINE,
)
matches = pattern.findall(content)
if not matches:
    sys.exit(0)
new_content = pattern.sub(r'\1 — \2', content)
# Print "FOUND <count>" + each old line for the dry-run report
print(f'FOUND {len(matches)}')
for prefix, desc in matches:
    print(f'  {prefix}，{desc[:80]}{"…" if len(desc) > 80 else ""}')
# Write to a sidecar file so the bash side can decide whether to commit
sidecar = path.with_suffix('.md.fix-fn-comma.tmp')
sidecar.write_text(new_content, encoding='utf-8')
PY
)

  if [[ -z "$python_out" ]]; then
    continue
  fi

  TOTAL_FILES_CHANGED=$((TOTAL_FILES_CHANGED + 1))
  CHANGED_FILES="$CHANGED_FILES$f"$'\n'
  count=$(echo "$python_out" | head -1 | awk '{print $2}')
  TOTAL_FOUND=$((TOTAL_FOUND + count))

  if [[ $QUIET -eq 0 ]]; then
    echo "📄 $f"
    echo "$python_out" | tail -n +2
    echo
  fi

  if [[ $APPLY -eq 1 ]]; then
    mv "$f.fix-fn-comma.tmp" "$f"
  else
    rm -f "$f.fix-fn-comma.tmp"
  fi
done < <(
  find knowledge -maxdepth 2 -name '*.md' \
    ! -path 'knowledge/en/*' ! -path 'knowledge/ja/*' \
    ! -path 'knowledge/es/*' ! -path 'knowledge/ko/*' \
    ! -path 'knowledge/resources/*' ! -name '_*'
)

echo "─────────────────────────────────────────"
if [[ $APPLY -eq 1 ]]; then
  echo "✅ Applied: $TOTAL_FOUND fix(es) across $TOTAL_FILES_CHANGED file(s)"
  echo "   Run \`bash scripts/core/sync.sh\` to propagate to src/content/"
else
  echo "🔍 Dry-run: would apply $TOTAL_FOUND fix(es) to $TOTAL_FILES_CHANGED file(s)"
  echo "   Re-run with --apply to write changes"
fi
