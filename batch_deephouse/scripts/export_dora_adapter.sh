#!/usr/bin/env bash
# Export a Side-Step DoRA checkpoint to ComfyUI .safetensors.
#
# Usage:
#   ./batch_deephouse/scripts/export_dora_adapter.sh 200
#   ./batch_deephouse/scripts/export_dora_adapter.sh best
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SIDESTEP_DIR="${SIDESTEP_DIR:-$(cd "$ROOT/.." && pwd)/Side-Step}"
EPOCH="${1:-200}"
DORA_ROOT="${DORA_ROOT:-$ROOT/output/arabic_deep_house_dora}"
export PATH="${HOME}/.local/bin:${PATH}"

if [[ "$EPOCH" == "best" || "$EPOCH" == "final" ]]; then
  ADAPTER="$DORA_ROOT/$EPOCH"
else
  ADAPTER="$DORA_ROOT/checkpoints/epoch_${EPOCH}"
fi
OUT="${2:-$DORA_ROOT/arabic_deep_house_${EPOCH}.safetensors}"

[[ -d "$ADAPTER" ]] || { echo "ERROR: missing adapter dir: $ADAPTER" >&2; exit 1; }
[[ -d "$SIDESTEP_DIR" ]] || { echo "ERROR: Side-Step not found: $SIDESTEP_DIR" >&2; exit 1; }

cd "$SIDESTEP_DIR"
echo "Exporting $ADAPTER → $OUT"
uv run sidestep export "$ADAPTER" --output "$OUT" --format comfyui --normalize-alpha
echo "DONE: $OUT"
