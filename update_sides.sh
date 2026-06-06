#!/usr/bin/env bash
set -euo pipefail

PACKWIZ_BIN="${PACKWIZ_BIN:-packwiz}"

echo "Side metadata is managed by packwiz in this repository."
echo "No packwiz-managed TOML files are edited by this helper."
"$PACKWIZ_BIN" refresh
