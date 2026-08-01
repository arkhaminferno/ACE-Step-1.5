"""DoRA eval mix → extract Oud/Ney stems → Basic Pitch MIDI.

Usage (API with base model loaded):
  PYTHONPATH="$PWD" python_embeded/bin/python3.11 \\
    -m batch_deephouse.dora_midi_pipeline \\
    --mix output/test_outputs/arabic_house_test_epoch_50.mp3 \\
    --leads oud,ney
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from loguru import logger

from batch_deephouse.datasets.midi_transcriber import transcribe_audio_to_midi
from batch_deephouse.paths import DEFAULT_API_BASE
from batch_deephouse.stem_extract import (
    BASE_MODEL_DIRNAME,
    extract_lead_to_file,
    require_base_checkpoint,
)


def run_extract_midi(
    *,
    mix_path: Path,
    leads: list[str],
    stem_dir: Path,
    midi_dir: Path,
    api_base: str,
    api_key: str,
    checkpoints_dir: Path,
    extract_steps: int,
    seed: int,
    skip_extract: bool,
) -> list[Path]:
    """Extract each lead (unless skipped) then write matching ``.mid`` files.

    Returns:
        List of written MIDI paths.
    """
    mix_path = mix_path.expanduser().resolve()
    if not mix_path.is_file():
        raise FileNotFoundError(f"Mix not found: {mix_path}")

    stem_dir.mkdir(parents=True, exist_ok=True)
    midi_dir.mkdir(parents=True, exist_ok=True)
    midi_paths: list[Path] = []

    if not skip_extract:
        require_base_checkpoint(checkpoints_dir)

    for lead in leads:
        stem = stem_dir / f"{mix_path.stem}_{lead}_stem.mp3"
        if skip_extract:
            if not stem.is_file():
                raise FileNotFoundError(
                    f"--skip-extract set but stem missing: {stem}"
                )
            logger.info("Using existing stem: {}", stem)
        else:
            logger.info("Extracting lead={!r} from {}", lead, mix_path.name)
            extract_lead_to_file(
                mix_path=mix_path,
                lead=lead,
                out_path=stem,
                api_base=api_base,
                api_key=api_key,
                steps=extract_steps,
                seed=seed,
                model=BASE_MODEL_DIRNAME,
            )
        mid = transcribe_audio_to_midi(stem, midi_dir)
        midi_paths.append(mid)
    return midi_paths


def main(argv: list[str] | None = None) -> int:
    """CLI: mix → extract → MIDI for configured leads."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mix", type=Path, required=True, help="Full mix mp3/wav")
    parser.add_argument(
        "--leads",
        default="oud,ney",
        help="Comma-separated leads (oud,ney,...)",
    )
    parser.add_argument(
        "--stem-dir",
        type=Path,
        default=Path("output/test_outputs/stems"),
    )
    parser.add_argument(
        "--midi-dir",
        type=Path,
        default=Path("output/midi_exports"),
    )
    parser.add_argument("--api-base", default=os.environ.get("ACE_API_BASE", DEFAULT_API_BASE))
    parser.add_argument("--api-key", default=os.environ.get("ACE_API_KEY", ""))
    parser.add_argument(
        "--checkpoints-dir",
        type=Path,
        default=Path("checkpoints"),
    )
    parser.add_argument("--extract-steps", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="MIDI existing {mix}_{lead}_stem.mp3 files only",
    )
    args = parser.parse_args(argv)

    leads = [x.strip() for x in args.leads.split(",") if x.strip()]
    if not leads:
        parser.error("--leads must list at least one instrument")

    try:
        mids = run_extract_midi(
            mix_path=args.mix,
            leads=leads,
            stem_dir=args.stem_dir,
            midi_dir=args.midi_dir,
            api_base=args.api_base,
            api_key=args.api_key,
            checkpoints_dir=args.checkpoints_dir,
            extract_steps=args.extract_steps,
            seed=args.seed,
            skip_extract=args.skip_extract,
        )
    except Exception as exc:
        logger.error("{}", exc)
        return 1

    for mid in mids:
        print(mid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
