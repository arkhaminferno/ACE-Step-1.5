#!/usr/bin/env bash
# Transcribe an isolated stem to MIDI via Basic Pitch (with pitch bends).
#
# Usage (from repo root):
#   ./batch_deephouse/scripts/audio_to_midi.sh path/to/oud_stem.mp3
#   ./batch_deephouse/scripts/audio_to_midi.sh path/to/ney_stem.wav ./output/midi_exports
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AUDIO_FILE="${1:-}"
OUTPUT_DIR="${2:-$ROOT/output/midi_exports}"

if [[ -z "$AUDIO_FILE" ]]; then
  echo "Usage: $0 <isolated_audio_stem> [output_dir]" >&2
  exit 1
fi

cd "$ROOT"
# shellcheck disable=SC1091
source "$ROOT/batch_deephouse/scripts/env_mps.sh"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
exec "$ROOT/python_embeded/bin/python3.11" -m batch_deephouse.datasets.midi_transcriber \
  --input "$AUDIO_FILE" \
  --output-dir "$OUTPUT_DIR"
