#!/usr/bin/env bash
# Source before ACE-Step / preprocessing on Apple Silicon:
#   source batch_deephouse/scripts/env_mps.sh
export PYTORCH_MPS_HIGH_WATERMARK_RATIO="${PYTORCH_MPS_HIGH_WATERMARK_RATIO:-0.0}"
echo "PYTORCH_MPS_HIGH_WATERMARK_RATIO=${PYTORCH_MPS_HIGH_WATERMARK_RATIO}"
