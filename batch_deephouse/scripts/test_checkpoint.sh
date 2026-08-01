#!/usr/bin/env bash
# Hot-swap a Side-Step DoRA checkpoint and synthesize a microtonal house loop.
#
# Usage (repo root):
#   ./batch_deephouse/scripts/test_checkpoint.sh 50
#   ./batch_deephouse/scripts/test_checkpoint.sh final 0.45
#   ./batch_deephouse/scripts/test_checkpoint.sh 50 --weight 0.50 --wait
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EPOCH="${1:-final}"
shift || true

# Optional 2nd positional = DoRA weight (e.g. 0.45). Flags still pass through.
WEIGHT_ARGS=()
if [[ "${1:-}" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
  WEIGHT_ARGS=(--weight "$1")
  shift
fi

cd "$ROOT"
# shellcheck disable=SC1091
source "$ROOT/batch_deephouse/scripts/env_mps.sh"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
if ((${#WEIGHT_ARGS[@]})); then
  exec "$ROOT/python_embeded/bin/python3.11" -m batch_deephouse.test_dora_inference \
    --epoch "$EPOCH" \
    "${WEIGHT_ARGS[@]}" \
    "$@"
fi
exec "$ROOT/python_embeded/bin/python3.11" -m batch_deephouse.test_dora_inference \
  --epoch "$EPOCH" \
  "$@"
