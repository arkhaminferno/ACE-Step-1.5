#!/usr/bin/env bash
# Start ACE-Step API for deep house generation (macOS).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ACESTEP_DIR="${ACESTEP_ROOT:-$ROOT}"

if [[ ! -d "$ACESTEP_DIR/acestep" ]]; then
  echo "ACE-Step not found at: $ACESTEP_DIR"
  echo "Run from ACE-Step-1.5 or set ACESTEP_ROOT."
  exit 1
fi

export ACESTEP_INIT_LLM="${ACESTEP_INIT_LLM:-true}"
export ACESTEP_LM_BACKEND="${ACESTEP_LM_BACKEND:-mlx}"

# Apple Silicon: disable PyTorch MPS private-pool ceiling (OOM during long gens).
if [[ "$(uname -s)" == "Darwin" ]]; then
  export PYTORCH_MPS_HIGH_WATERMARK_RATIO="${PYTORCH_MPS_HIGH_WATERMARK_RATIO:-0.0}"
fi

cd "$ACESTEP_DIR"
if [[ -x "$ACESTEP_DIR/python_embeded/bin/python3.11" ]]; then
  exec env PYTHONPATH="$ACESTEP_DIR" "$ACESTEP_DIR/python_embeded/bin/python3.11" \
    -m uvicorn acestep.api_server:app --host 127.0.0.1 --port 8001 --workers 1
fi
if [[ -f "$ACESTEP_DIR/start_api_server_macos.sh" ]]; then
  exec bash "$ACESTEP_DIR/start_api_server_macos.sh"
fi
exec bash "$ACESTEP_DIR/start_api_server.sh"
