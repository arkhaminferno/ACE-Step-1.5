#!/usr/bin/env bash
# Revert HAYA generation to base turbo (no DoRA).
# Usage (API must be up): ./batch_deephouse/scripts/unload_dora.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
API="${ACESTEP_API_BASE:-http://127.0.0.1:8001}"
curl -s -X POST "$API/v1/lora/unload" | python3 -m json.tool
echo "DoRA unloaded. Generate with: ./batch_deephouse/scripts/generate.sh --force --slug layali"
