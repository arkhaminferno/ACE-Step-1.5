#!/usr/bin/env bash
# Load a trained DoRA/LoRA adapter into the local ACE-Step API (Mac inference).
#
# Usage (API must be running on :8001):
#   ./batch_deephouse/scripts/load_arabic_adapter_mac.sh best 0.45
#   ./batch_deephouse/scripts/load_arabic_adapter_mac.sh 200 0.50
#
# After load, generate with Recipe 4 as usual — instrument timbre should improve.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EPOCH="${1:-best}"
SCALE="${2:-0.45}"
cd "$ROOT"
export PYTHONPATH="$ROOT"
exec ./python_embeded/bin/python3.11 -m batch_deephouse.test_dora_inference \
  --epoch "$EPOCH" \
  --lora-scale "$SCALE" \
  --duration 20 \
  --out "batch_deephouse/output/_adapter_smoke/smoke_${EPOCH}_w${SCALE}.mp3"
