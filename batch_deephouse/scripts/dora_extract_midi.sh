#!/usr/bin/env bash
# Extract Oud/Ney leads from a DoRA test mix, then transcribe each to MIDI.
#
# Requires: ACE-Step API on :8001 with acestep-v15-base available.
#
# Usage (repo root):
#   ./batch_deephouse/scripts/dora_extract_midi.sh \
#     output/test_outputs/arabic_house_test_epoch_50.mp3
#   ./batch_deephouse/scripts/dora_extract_midi.sh mix.mp3 oud,ney
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MIX="${1:-}"
LEADS="${2:-oud,ney}"

if [[ -z "$MIX" ]]; then
  echo "Usage: $0 <mix.mp3> [leads=oud,ney]" >&2
  exit 1
fi

cd "$ROOT"
# shellcheck disable=SC1091
source "$ROOT/batch_deephouse/scripts/env_mps.sh"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
exec "$ROOT/python_embeded/bin/python3.11" -m batch_deephouse.dora_midi_pipeline \
  --mix "$MIX" \
  --leads "$LEADS"
