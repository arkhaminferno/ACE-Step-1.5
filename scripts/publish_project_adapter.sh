#!/usr/bin/env bash
# Copy a trained adapter into the git-tracked adapters folder for Mac pull.
#
# Usage (macOS or Git Bash on Windows):
#   ./scripts/publish_project_adapter.sh arabic best
#   ./scripts/publish_project_adapter.sh arabic final
#   ./scripts/publish_project_adapter.sh soulcalm best
#   ./scripts/publish_project_adapter.sh birthday final
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="${1:-}"
EPOCH="${2:-best}"

SIDESTEP_DIR="${SIDESTEP_DIR:-}"
if [[ -z "$SIDESTEP_DIR" ]]; then
  if [[ -d "$ROOT/Side-Step" ]]; then SIDESTEP_DIR="$ROOT/Side-Step"
  elif [[ -d "$(cd "$ROOT/.." && pwd)/Side-Step" ]]; then
    SIDESTEP_DIR="$(cd "$ROOT/.." && pwd)/Side-Step"
  fi
fi
export PATH="${HOME}/.local/bin:${PATH}"

die() { echo "ERROR: $*" >&2; exit 1; }

_python_ok() {
  "$@" -c "import sys" >/dev/null 2>&1
}

# Write ADAPTER_META.json with any working Python (Windows Store stub skipped).
run_python() {
  local code="$1"
  if [[ -x "${ROOT}/python_embeded/bin/python3.11" ]] \
      && _python_ok "${ROOT}/python_embeded/bin/python3.11"; then
    "${ROOT}/python_embeded/bin/python3.11" -c "$code"
    return
  fi
  if [[ -n "${SIDESTEP_DIR:-}" && -d "$SIDESTEP_DIR" ]] \
      && command -v uv >/dev/null 2>&1; then
    (cd "$SIDESTEP_DIR" && uv run python -c "$code")
    return
  fi
  if command -v py >/dev/null 2>&1 && _python_ok py -3; then
    py -3 -c "$code"
    return
  fi
  if command -v python3 >/dev/null 2>&1 && _python_ok python3; then
    python3 -c "$code"
    return
  fi
  if command -v python >/dev/null 2>&1 && _python_ok python; then
    python -c "$code"
    return
  fi
  die "No working Python found for ADAPTER_META.json"
}

case "$PROJECT" in
  arabic|deephouse|haya)
    SRC_ROOT="$ROOT/output/arabic_deep_house_dora"
    DEST_ROOT="$ROOT/batch_deephouse/adapters/arabic_deep_house"
    NAME="arabic_deep_house"
    ;;
  soulcalm|piano)
    SRC_ROOT="$ROOT/output/soulcalm_piano_dora"
    DEST_ROOT="$ROOT/batch_soulcalm/adapters/soulcalm_piano"
    NAME="soulcalm_piano"
    ;;
  birthday|edm)
    SRC_ROOT="$ROOT/output/birthday_edm_dora"
    DEST_ROOT="$ROOT/batch_birthday/adapters/birthday_edm"
    NAME="birthday_edm"
    ;;
  *) die "Usage: $0 {arabic|soulcalm|birthday} {best|final|N}" ;;
esac

if [[ "$EPOCH" == "best" || "$EPOCH" == "final" ]]; then
  SRC="$SRC_ROOT/$EPOCH"
else
  SRC="$SRC_ROOT/checkpoints/epoch_${EPOCH}"
fi

[[ -d "$SRC" ]] || die "missing $SRC"
[[ -f "$SRC/adapter_model.safetensors" || -f "$SRC/adapter_model.bin" ]] \
  || die "no adapter_model.* in $SRC"

rm -rf "$DEST_ROOT/best"
mkdir -p "$DEST_ROOT/best"
cp -R "$SRC/." "$DEST_ROOT/best/"
rm -f "$DEST_ROOT/best/training_state.pt" "$DEST_ROOT/best/"*.pt 2>/dev/null || true

run_python "
import json
from datetime import datetime, timezone
from pathlib import Path
meta = {
    'name': '${NAME}',
    'project': '${PROJECT}',
    'source_epoch': '${EPOCH}',
    'published_at': datetime.now(timezone.utc).isoformat(),
    'path': str(Path('${DEST_ROOT}/best').relative_to('${ROOT}')),
}
Path('${DEST_ROOT}/ADAPTER_META.json').write_text(
    json.dumps(meta, indent=2) + chr(10), encoding='utf-8'
)
print('Wrote', Path('${DEST_ROOT}/ADAPTER_META.json'))
"

echo "Published → $DEST_ROOT/best"
echo "Next: git add $DEST_ROOT && git commit && git push"
