#!/usr/bin/env bash
# Build every registered statement, run the axiom checker on each module,
# and write one JSON report per module to build/check/<Module>.json.
# Exit non-zero if any check fails. Code licence: Apache-2.0.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build/check
lake build Conjectures check
status=0
for f in $(find Conjectures -name 'S*.lean' | sort); do
  mod="${f%.lean}"; mod="${mod//\//.}"
  echo "== $mod"
  lake exe check "build/check/$mod.json" "$mod" || status=1
done
exit $status
