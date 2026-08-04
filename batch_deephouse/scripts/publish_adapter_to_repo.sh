#!/usr/bin/env bash
# Copy a trained Side-Step adapter into the git-tracked adapters folder for Mac pull.
#
# Usage (Windows Git Bash / Mac / Linux — after training):
#   ./batch_deephouse/scripts/publish_adapter_to_repo.sh best
#   ./batch_deephouse/scripts/publish_adapter_to_repo.sh final
#   ./batch_deephouse/scripts/publish_adapter_to_repo.sh 200
#
# Then: git add batch_deephouse/adapters && git commit && git push
# Requires: git lfs install  (*.safetensors tracked via .gitattributes)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EPOCH="${1:-best}"
SRC_ROOT="${DORA_ROOT:-$ROOT/output/arabic_deep_house_dora}"
DEST_ROOT="$ROOT/batch_deephouse/adapters/arabic_deep_house"

if [[ "$EPOCH" == "best" || "$EPOCH" == "final" ]]; then
  SRC="$SRC_ROOT/$EPOCH"
else
  SRC="$SRC_ROOT/checkpoints/epoch_${EPOCH}"
fi

[[ -d "$SRC" ]] || { echo "ERROR: missing $SRC" >&2; exit 1; }
[[ -f "$SRC/adapter_model.safetensors" || -f "$SRC/adapter_model.bin" ]] || {
  echo "ERROR: no adapter_model.* in $SRC" >&2
  exit 1
}

mkdir -p "$DEST_ROOT/best"
# Always publish as "best" for a stable Mac path (overwrite previous release).
rm -rf "$DEST_ROOT/best"
mkdir -p "$DEST_ROOT/best"
cp -R "$SRC/." "$DEST_ROOT/best/"
# Drop resume-only blobs — keep inference files only
rm -f "$DEST_ROOT/best/training_state.pt" "$DEST_ROOT/best/"*.pt 2>/dev/null || true

python3 - <<PY
import json
from datetime import datetime, timezone
from pathlib import Path
meta = {
    "name": "arabic_deep_house",
    "source_epoch": "${EPOCH}",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "path": "batch_deephouse/adapters/arabic_deep_house/best",
    "mac_load": "./batch_deephouse/scripts/load_arabic_adapter_mac.sh best 0.45",
    "note": "Inference DoRA only — not full base model",
}
Path("${DEST_ROOT}/ADAPTER_META.json").write_text(
    json.dumps(meta, indent=2) + "\n", encoding="utf-8"
)
print("Wrote", Path("${DEST_ROOT}/ADAPTER_META.json"))
PY

echo "Published → $DEST_ROOT/best"
echo "Next:"
echo "  git add batch_deephouse/adapters/arabic_deep_house"
echo "  git commit -m 'Add Arabic deep-house DoRA adapter for Mac inference.'"
echo "  git push origin HEAD"
echo "On Mac: git lfs pull && ./batch_deephouse/scripts/load_arabic_adapter_mac.sh best 0.45"
