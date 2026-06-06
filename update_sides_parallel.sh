#!/usr/bin/env bash
set -euo pipefail

PACKWIZ_BIN="${PACKWIZ_BIN:-packwiz}"

echo "Parallel side rewriting is disabled for this migration."
echo "Use packwiz commands for metadata changes, then refresh the index."
"$PACKWIZ_BIN" refresh
