#!/usr/bin/env bash
# Generate deep house track(s) from input/tracks.csv
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
PY="${ROOT}/python_embeded/bin/python3.11"
if [[ ! -x "$PY" ]]; then
  PY="python3"
fi
exec env PYTHONPATH="$ROOT" "$PY" -m batch_deephouse "$@"
