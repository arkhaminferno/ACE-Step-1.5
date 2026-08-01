#!/usr/bin/env bash
# Phase 3 — Side-Step 1.1.x: preprocess → analyze (PP++) → DoRA train
#
# Prerequisites:
#   1. Dry stems (.mp3/.wav) in batch_deephouse/datasets/arabic_house_dataset/
#      with matching .json (+ optional .lyrics.txt)
#   2. Side-Step at ../Side-Step (git clone https://github.com/koda-dernet/Side-Step.git)
#   3. uv on PATH; ACE-Step checkpoints under ./checkpoints
#   4. NVIDIA CUDA recommended (MPS training is experimental)
#
# Usage (from ACE-Step-1.5 root):
#   source batch_deephouse/scripts/env_mps.sh
#   ./batch_deephouse/scripts/phase3_dora_train.sh preprocess
#   ./batch_deephouse/scripts/phase3_dora_train.sh analyze
#   ./batch_deephouse/scripts/phase3_dora_train.sh train
#   ./batch_deephouse/scripts/phase3_dora_train.sh all
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SIDESTEP_DIR="${SIDESTEP_DIR:-$(cd "$ROOT/.." && pwd)/Side-Step}"
AUDIO_DIR="${AUDIO_DIR:-$ROOT/batch_deephouse/datasets/arabic_house_dataset}"
DATASET_JSON="${DATASET_JSON:-$AUDIO_DIR/dataset.json}"
TENSOR_DIR="${TENSOR_DIR:-$ROOT/batch_deephouse/datasets/preprocessed_tensors}"
CHECKPOINT_DIR="${CHECKPOINT_DIR:-$ROOT/checkpoints}"
MODEL="${MODEL:-base}"
OUTPUT_DIR="${OUTPUT_DIR:-$ROOT/output/arabic_deep_house_dora}"
EPOCHS="${EPOCHS:-1000}"
LR="${LR:-5e-4}"
RANK_MIN="${RANK_MIN:-16}"
RANK_MAX="${RANK_MAX:-128}"
ACTION="${1:-all}"

export PATH="${HOME}/.local/bin:${PATH}"

if [[ "$(uname -s)" == "Darwin" ]]; then
  export PYTORCH_MPS_HIGH_WATERMARK_RATIO="${PYTORCH_MPS_HIGH_WATERMARK_RATIO:-0.0}"
fi

die() { echo "ERROR: $*" >&2; exit 1; }

need_sidestep() {
  [[ -d "$SIDESTEP_DIR" ]] || die "Side-Step not found at $SIDESTEP_DIR"
  command -v uv >/dev/null 2>&1 || die "uv not on PATH"
}

need_audio() {
  local count
  count="$(find "$AUDIO_DIR" -type f \( -iname '*.mp3' -o -iname '*.wav' -o -iname '*.flac' -o -iname '*.m4a' \) ! -path '*/examples/*' | wc -l | tr -d ' ')"
  [[ "$count" -gt 0 ]] || die "No audio stems under $AUDIO_DIR
Drop dry Oud/Ney .mp3/.wav next to matching .json files, then re-run.
(Only examples/*.json|lyrics exist right now — no .mp3 found.)"
  echo "Found $count audio file(s) under $AUDIO_DIR"
}

build_json() {
  cd "$ROOT"
  PYTHONPATH="$ROOT" "${ROOT}/python_embeded/bin/python3.11" \
    -m batch_deephouse.datasets.build_dataset_json \
    --dataset-dir "$AUDIO_DIR" \
    --output "$DATASET_JSON"
}

pick_model() {
  if [[ -d "$CHECKPOINT_DIR/acestep-v15-base" ]]; then
    MODEL="base"
  elif [[ -d "$CHECKPOINT_DIR/acestep-v15-sft" ]]; then
    MODEL="sft"
  else
    echo "WARN: base/sft missing under $CHECKPOINT_DIR — falling back to turbo"
    MODEL="turbo"
  fi
  echo "Model: $MODEL"
}

preprocess() {
  need_sidestep
  need_audio
  build_json
  pick_model
  mkdir -p "$TENSOR_DIR"
  echo "=== sidestep preprocess → $TENSOR_DIR ==="
  cd "$SIDESTEP_DIR"
  uv run sidestep preprocess \
    --audio-dir "$AUDIO_DIR" \
    --tensor-output "$TENSOR_DIR" \
    --checkpoint-dir "$CHECKPOINT_DIR" \
    --model "$MODEL" \
    --normalize peak \
    --dataset-json "$DATASET_JSON"
}

analyze() {
  need_sidestep
  [[ -d "$TENSOR_DIR" ]] || die "Missing tensors at $TENSOR_DIR — run preprocess first"
  pick_model
  echo "=== sidestep analyze (PP++ / fisher_map) ==="
  cd "$SIDESTEP_DIR"
  # Global --yes (before subcommand) skips "Save fisher_map.json?"
  uv run sidestep --yes analyze \
    --checkpoint-dir "$CHECKPOINT_DIR" \
    --model "$MODEL" \
    --dataset-dir "$TENSOR_DIR"
}

train() {
  need_sidestep
  [[ -d "$TENSOR_DIR" ]] || die "Missing tensors at $TENSOR_DIR — run preprocess first"
  pick_model
  mkdir -p "$OUTPUT_DIR"
  echo "=== sidestep train DoRA → $OUTPUT_DIR ==="
  cd "$SIDESTEP_DIR"
  # Global --yes (before subcommand) skips Proceed? prompts.
  # fisher_map.json (from analyze) auto-assigns adaptive ranks; --rank is base.
  uv run sidestep --yes train \
    --checkpoint-dir "$CHECKPOINT_DIR" \
    --model "$MODEL" \
    --dataset-dir "$TENSOR_DIR" \
    --output-dir "$OUTPUT_DIR" \
    --adapter dora \
    --rank 64 \
    --target-modules q_proj k_proj v_proj o_proj condition_embedder \
    --timestep-mode continuous \
    --learning-rate "$LR" \
    --epochs "$EPOCHS"
}

case "$ACTION" in
  preprocess) preprocess ;;
  analyze|estimate) analyze ;;
  train) train ;;
  all) preprocess; analyze; train ;;
  *) die "Usage: $0 {preprocess|analyze|train|all}" ;;
esac

echo "DONE: $ACTION"
