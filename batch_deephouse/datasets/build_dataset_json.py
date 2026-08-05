"""Build Side-Step ``dataset.json`` from audio + per-file JSON sidecars.

Scans a dataset folder for ``.mp3`` / ``.wav`` / ``.flac`` files and pairs each
with a matching ``<stem>.json`` (and optional ``<stem>.lyrics.txt``) using the
ACE-Step dataset builder conventions.

Usage (repo root):
  PYTHONPATH=. python -m batch_deephouse.datasets.build_dataset_json \\
    --dataset-dir batch_deephouse/datasets/arabic_house_dataset_v2 \\
    --output batch_deephouse/datasets/arabic_house_dataset_v2/dataset.json
"""

from __future__ import annotations

import argparse
from pathlib import Path

from acestep.training.dataset_builder_modules.builder import DatasetBuilder

AUDIO_EXTS = {".mp3", ".wav", ".flac", ".ogg", ".opus"}


def _relativize_audio_paths(samples: list, json_path: Path) -> None:
    """Store audio paths relative to the dataset JSON parent when possible."""
    base = json_path.parent.resolve()
    for sample in samples:
        try:
            audio = Path(sample.audio_path).resolve()
            sample.audio_path = str(audio.relative_to(base))
        except ValueError:
            pass


def build_dataset_json(
    dataset_dir: str | Path,
    output: str | Path,
    *,
    name: str = "local_dataset",
    custom_tag: str = "",
    all_instrumental: bool = True,
) -> tuple[Path, str]:
    """Scan *dataset_dir* and write ACE-Step-compatible ``dataset.json``.

    Args:
        dataset_dir: Folder containing audio files and per-file ``.json`` sidecars.
        output: Destination path for ``dataset.json``.
        name: Dataset name stored in metadata.
        custom_tag: Optional trigger tag applied to all samples.
        all_instrumental: Default instrumental flag for samples without lyrics.

    Returns:
        ``(output_path, status_message)``.

    Raises:
        SystemExit: When no audio files are found.
    """
    builder = DatasetBuilder()
    builder.metadata.name = name
    builder.metadata.custom_tag = custom_tag
    builder.metadata.all_instrumental = all_instrumental

    samples, status = builder.scan_directory(str(dataset_dir))
    if not samples:
        raise SystemExit(status)

    out_path = Path(output)
    _relativize_audio_paths(builder.samples, out_path)
    save_status = builder.save_dataset(str(out_path), name)
    return out_path, f"{status}\n{save_status}"


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Build dataset.json from audio + per-file JSON sidecars.",
    )
    parser.add_argument(
        "--dataset-dir",
        required=True,
        help="Directory with audio files and matching .json sidecars",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output dataset.json path",
    )
    parser.add_argument("--name", default="local_dataset", help="Dataset name")
    parser.add_argument("--tag", default="", help="Custom trigger tag for all samples")
    args = parser.parse_args(argv)

    out_path, status = build_dataset_json(
        args.dataset_dir,
        args.output,
        name=args.name,
        custom_tag=args.tag,
    )
    print(status)
    print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
