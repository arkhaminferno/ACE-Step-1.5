#!/usr/bin/env bash
# Train a project DoRA adapter (arabic | soulcalm | birthday | all).
#
# Usage (repo root, Git Bash on Windows):
#   export SIDESTEP_DIR="$PWD/Side-Step"
#   ./scripts/train_project_adapter.sh arabic preprocess
#   ./scripts/train_project_adapter.sh arabic analyze
#   ./scripts/train_project_adapter.sh arabic train
#   ./scripts/train_project_adapter.sh soulcalm all
#   ./scripts/train_project_adapter.sh all all
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="${1:-}"
ACTION="${2:-all}"
RANK="${RANK:-32}"
EPOCHS="${EPOCHS:-400}"
LR="${LR:-1e-4}"

SIDESTEP_DIR="${SIDESTEP_DIR:-}"
if [[ -z "$SIDESTEP_DIR" ]]; then
  if [[ -d "$ROOT/Side-Step" ]]; then SIDESTEP_DIR="$ROOT/Side-Step"
  elif [[ -d "$(cd "$ROOT/.." && pwd)/Side-Step" ]]; then
    SIDESTEP_DIR="$(cd "$ROOT/.." && pwd)/Side-Step"
  else SIDESTEP_DIR="$ROOT/Side-Step"
  fi
fi
CHECKPOINT_DIR="${CHECKPOINT_DIR:-$ROOT/checkpoints}"
export PATH="${HOME}/.local/bin:${PATH}"

die() { echo "ERROR: $*" >&2; exit 1; }

resolve_paths() {
  local p="$1"
  case "$p" in
    arabic|deephouse|haya)
      AUDIO_DIR="${AUDIO_DIR:-$ROOT/batch_deephouse/datasets/arabic_house_dataset_v2}"
      TENSOR_DIR="${TENSOR_DIR:-$ROOT/batch_deephouse/datasets/preprocessed_tensors_arabic_v2}"
      OUTPUT_DIR="${OUTPUT_DIR:-$ROOT/output/arabic_deep_house_dora}"
      LABEL="arabic"
      ;;
    soulcalm|piano)
      AUDIO_DIR="$ROOT/batch_soulcalm/datasets/soulcalm_piano_dataset"
      TENSOR_DIR="$ROOT/batch_soulcalm/datasets/preprocessed_tensors"
      OUTPUT_DIR="$ROOT/output/soulcalm_piano_dora"
      LABEL="soulcalm"
      ;;
    birthday|edm)
      AUDIO_DIR="$ROOT/batch_birthday/datasets/birthday_edm_dataset"
      TENSOR_DIR="$ROOT/batch_birthday/datasets/preprocessed_tensors"
      OUTPUT_DIR="$ROOT/output/birthday_edm_dora"
      LABEL="birthday"
      ;;
    *) die "Unknown project '$p'. Use: arabic | soulcalm | birthday | all" ;;
  esac
  DATASET_JSON="$AUDIO_DIR/dataset.json"
}

pick_model() {
  if [[ -d "$CHECKPOINT_DIR/acestep-v15-base" ]]; then MODEL="base"
  elif [[ -d "$CHECKPOINT_DIR/acestep-v15-sft" ]]; then MODEL="sft"
  else echo "WARN: falling back to turbo"; MODEL="turbo"
  fi
  echo "Model: $MODEL"
}

need_sidestep() {
  [[ -d "$SIDESTEP_DIR" ]] || die "Side-Step missing at $SIDESTEP_DIR"
  command -v uv >/dev/null 2>&1 || die "uv not on PATH"
}

need_audio() {
  local count
  count="$(find "$AUDIO_DIR" -type f \( -iname '*.mp3' -o -iname '*.wav' -o -iname '*.flac' \) ! -path '*/examples/*' | wc -l | tr -d ' ')"
  # Seed birthday examples from tracked templates if folder is empty.
  if [[ "$LABEL" == "birthday" && ! -d "$AUDIO_DIR/examples" ]]; then
    local tpl="$ROOT/batch_deephouse/datasets/templates/birthday_edm_dataset"
    if [[ -d "$tpl" ]]; then
      mkdir -p "$AUDIO_DIR"
      cp -R "$tpl/." "$AUDIO_DIR/"
      echo "Seeded birthday dataset templates from $tpl"
    fi
  fi
  count="$(find "$AUDIO_DIR" -type f \( -iname '*.mp3' -o -iname '*.wav' -o -iname '*.flac' \) ! -path '*/examples/*' | wc -l | tr -d ' ')"
  [[ "$count" -gt 0 ]] || die "No stems in $AUDIO_DIR — add .mp3/.wav + .json (see examples/)"
  echo "Found $count stem(s) in $AUDIO_DIR"
}

build_json() {
  if [[ -f "$ROOT/batch_deephouse/datasets/build_dataset_json.py" ]]; then
    PYTHONPATH="$ROOT" "${ROOT}/python_embeded/bin/python3.11" \
      -m batch_deephouse.datasets.build_dataset_json \
      --dataset-dir "$AUDIO_DIR" --output "$DATASET_JSON" 2>/dev/null \
    || PYTHONPATH="$ROOT" python -m batch_deephouse.datasets.build_dataset_json \
      --dataset-dir "$AUDIO_DIR" --output "$DATASET_JSON"
  else
    die "build_dataset_json missing"
  fi
}

do_preprocess() {
  need_sidestep; need_audio; build_json; pick_model
  mkdir -p "$TENSOR_DIR"
  echo "=== [$LABEL] preprocess → $TENSOR_DIR ==="
  cd "$SIDESTEP_DIR"
  uv run sidestep preprocess \
    --audio-dir "$AUDIO_DIR" \
    --tensor-output "$TENSOR_DIR" \
    --checkpoint-dir "$CHECKPOINT_DIR" \
    --model "$MODEL" \
    --normalize peak \
    --dataset-json "$DATASET_JSON"
}

do_analyze() {
  need_sidestep
  [[ -d "$TENSOR_DIR" ]] || die "Missing tensors $TENSOR_DIR — preprocess first"
  pick_model
  echo "=== [$LABEL] analyze ==="
  cd "$SIDESTEP_DIR"
  uv run sidestep --yes analyze \
    --checkpoint-dir "$CHECKPOINT_DIR" \
    --model "$MODEL" \
    --dataset-dir "$TENSOR_DIR"
}

do_train() {
  need_sidestep
  [[ -d "$TENSOR_DIR" ]] || die "Missing tensors $TENSOR_DIR — preprocess first"
  pick_model
  mkdir -p "$OUTPUT_DIR"
  echo "=== [$LABEL] train DoRA rank=$RANK epochs=$EPOCHS → $OUTPUT_DIR ==="
  cd "$SIDESTEP_DIR"
  uv run sidestep --yes train \
    --checkpoint-dir "$CHECKPOINT_DIR" \
    --model "$MODEL" \
    --dataset-dir "$TENSOR_DIR" \
    --output-dir "$OUTPUT_DIR" \
    --adapter dora \
    --rank "$RANK" \
    --target-modules q_proj k_proj v_proj o_proj condition_embedder \
    --timestep-mode continuous \
    --learning-rate "$LR" \
    --epochs "$EPOCHS"
}

run_one() {
  resolve_paths "$1"
  case "$ACTION" in
    preprocess) do_preprocess ;;
    analyze|estimate) do_analyze ;;
    train) do_train ;;
    all) do_preprocess; do_analyze; do_train ;;
    *) die "Usage: $0 {arabic|soulcalm|birthday|all} {preprocess|analyze|train|all}" ;;
  esac
  echo "DONE: $LABEL $ACTION"
}

[[ -n "$PROJECT" ]] || die "Usage: $0 {arabic|soulcalm|birthday|all} {preprocess|analyze|train|all}"

if [[ "$PROJECT" == "all" ]]; then
  for p in arabic soulcalm birthday; do
    echo "########## PROJECT $p ##########"
    run_one "$p"
  done
else
  run_one "$PROJECT"
fi
