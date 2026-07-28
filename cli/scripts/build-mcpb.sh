#!/usr/bin/env bash
#
# build-mcpb.sh — pack the COMPUTEX.md Claude Desktop / one-click bundle.
#
# Produces cli/dist/taiwanmd.mcpb from cli/mcpb/ (manifest.json + server/).
# A .mcpb is a zip archive; we prefer the official `mcpb` packer (it validates
# the manifest against the v0.3 schema) and fall back to `zip` if unavailable.
#
# Usage:  cli/scripts/build-mcpb.sh
#
set -euo pipefail

CLI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$CLI_DIR/mcpb"
OUT_DIR="$CLI_DIR/dist"
OUT_FILE="$OUT_DIR/taiwanmd.mcpb"

# Keep the bundle version in lockstep with package.json.
PKG_VERSION="$(node -p "require('$CLI_DIR/package.json').version")"
MANIFEST_VERSION="$(node -p "require('$SRC_DIR/manifest.json').version")"
if [ "$PKG_VERSION" != "$MANIFEST_VERSION" ]; then
  echo "✗ version drift: package.json=$PKG_VERSION but manifest.json=$MANIFEST_VERSION" >&2
  echo "  update cli/mcpb/manifest.json \"version\" to $PKG_VERSION" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"
rm -f "$OUT_FILE"

if command -v mcpb >/dev/null 2>&1; then
  echo "→ packing with official mcpb (validates manifest)…"
  mcpb pack "$SRC_DIR" "$OUT_FILE"
elif npx --no-install @anthropic-ai/mcpb --version >/dev/null 2>&1; then
  echo "→ packing with npx @anthropic-ai/mcpb…"
  npx --no-install @anthropic-ai/mcpb pack "$SRC_DIR" "$OUT_FILE"
else
  echo "→ mcpb CLI not found; packing with zip (no schema validation)…"
  echo "  for a public release, validate first: npx @anthropic-ai/mcpb pack" >&2
  ( cd "$SRC_DIR" && zip -r -q -X "$OUT_FILE" manifest.json server )
fi

echo "✓ built $OUT_FILE ($(du -h "$OUT_FILE" | cut -f1)) — v$PKG_VERSION"
