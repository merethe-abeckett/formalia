#!/usr/bin/env bash
# Independently re-verify every registered statement module with lean4checker,
# which replays the .olean files through a fresh kernel. This guards against a
# tampered build environment. Code licence: Apache-2.0.
#
# lean4checker must be built with the SAME Lean toolchain as the registry.
# Its tag is read from scripts/lean4checker.rev.
set -euo pipefail
cd "$(dirname "$0")/.."
REV="$(cat scripts/lean4checker.rev)"
DIR="build/lean4checker"
if [ ! -x "$DIR/.lake/build/bin/lean4checker" ]; then
  rm -rf "$DIR"
  git clone -q --depth 1 --branch "$REV" https://github.com/leanprover/lean4checker "$DIR"
  cp lean-toolchain "$DIR/lean-toolchain"
  (cd "$DIR" && lake build lean4checker)
fi
status=0
for f in $(find Conjectures -name 'S*.lean' | sort); do
  mod="${f%.lean}"; mod="${mod//\//.}"
  echo "== lean4checker $mod"
  lake env "$DIR/.lake/build/bin/lean4checker" "$mod" || status=1
done
exit $status
