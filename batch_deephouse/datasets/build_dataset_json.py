"""Build Side-Step ``dataset.json`` from audio + per-file JSON sidecars.

Stdlib-only so Windows Git Bash can run this without ACE-Step/torch/loguru installed.
Side-Step ``preprocess`` recomputes audio duration from the files.

Usage (repo root):
  PYTHONPATH=. python -m batch_deephouse.datasets.build_dataset_json \\
    --dataset-dir batch_deephouse/datasets/arabic_house_dataset_v2 \\
    --output batch_deephouse/datasets/arabic_house_dataset_v2/dataset.json
"""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

AUDIO_EXTS = {".mp3", ".wav", ".flac", ".ogg", ".opus", ".m4a"}


def _read_text(path: Path) -> str:
    """Read UTF-8 text; return empty string if missing."""
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace").strip()


def _load_json_sidecar(audio_path: Path) -> dict[str, Any]:
    """Load ``<stem>.json`` metadata sidecar if present."""
    json_path = audio_path.with_suffix(".json")
    if not json_path.is_file():
        return {}
    try:
        data = json.loads(json_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _load_lyrics(audio_path: Path) -> tuple[str, bool]:
    """Load lyrics from ``.lyrics.txt`` then legacy ``.txt``."""
    stem = audio_path.with_suffix("")
    for suffix in (".lyrics.txt", ".txt"):
        content = _read_text(Path(str(stem) + suffix))
        if content:
            return content, True
    return "", False


def _parse_bpm(raw: Any) -> int | None:
    """Parse BPM from sidecar; return None when invalid."""
    if raw in (None, ""):
        return None
    try:
        return int(float(raw))
    except (TypeError, ValueError):
        return None


def _scan_samples(dataset_dir: Path, *, custom_tag: str = "") -> list[dict[str, Any]]:
    """Collect ACE-Step-compatible sample dicts from *dataset_dir*."""
    samples: list[dict[str, Any]] = []
    for audio_path in sorted(dataset_dir.rglob("*")):
        if not audio_path.is_file():
            continue
        if audio_path.suffix.lower() not in AUDIO_EXTS:
            continue
        if "examples" in audio_path.parts:
            continue

        meta = _load_json_sidecar(audio_path)
        lyrics_raw, has_lyrics = _load_lyrics(audio_path)
        caption = str(meta.get("caption", "") or "").strip()
        if not caption:
            caption = audio_path.stem.replace("_", " ").replace("-", " ")

        lyrics = lyrics_raw if has_lyrics else "[Instrumental]"
        is_instrumental = not has_lyrics or "[Instrumental]" in lyrics_raw

        try:
            rel_audio = str(audio_path.resolve().relative_to(dataset_dir.resolve()))
        except ValueError:
            rel_audio = str(audio_path)

        samples.append(
            {
                "id": uuid.uuid4().hex[:8],
                "audio_path": rel_audio.replace("\\", "/"),
                "filename": audio_path.name,
                "caption": caption,
                "genre": str(meta.get("genre", "") or ""),
                "lyrics": lyrics,
                "raw_lyrics": lyrics_raw,
                "formatted_lyrics": "",
                "bpm": _parse_bpm(meta.get("bpm")),
                "keyscale": str(meta.get("keyscale", meta.get("key", "")) or ""),
                "timesignature": str(meta.get("timesignature", meta.get("signature", "")) or ""),
                "duration": 0,
                "language": str(meta.get("language", "unknown") or "unknown"),
                "is_instrumental": is_instrumental,
                "custom_tag": str(meta.get("custom_tag", custom_tag) or custom_tag),
                "labeled": bool(meta.get("caption")),
                "prompt_override": meta.get("prompt_override"),
            }
        )
    return samples


def build_dataset_json(
    dataset_dir: str | Path,
    output: str | Path,
    *,
    name: str = "local_dataset",
    custom_tag: str = "",
) -> tuple[Path, str]:
    """Scan *dataset_dir* and write ACE-Step-compatible ``dataset.json``.

    Args:
        dataset_dir: Folder containing audio files and per-file ``.json`` sidecars.
        output: Destination path for ``dataset.json``.
        name: Dataset name stored in metadata.
        custom_tag: Optional trigger tag applied to all samples.

    Returns:
        ``(output_path, status_message)``.

    Raises:
        SystemExit: When no audio files are found.
    """
    base = Path(dataset_dir).resolve()
    if not base.is_dir():
        raise SystemExit(f"Dataset directory not found: {base}")

    samples = _scan_samples(base, custom_tag=custom_tag)
    if not samples:
        raise SystemExit(f"No audio files found in {base} (supported: {', '.join(sorted(AUDIO_EXTS))})")

    with_meta = sum(1 for s in samples if s.get("labeled"))
    all_instrumental = all(s.get("is_instrumental", False) for s in samples)
    out_path = Path(output)
    dataset = {
        "metadata": {
            "name": name,
            "custom_tag": custom_tag,
            "tag_position": "prepend",
            "created_at": datetime.now().isoformat(),
            "num_samples": len(samples),
            "all_instrumental": all_instrumental,
            "genre_ratio": 0,
        },
        "samples": samples,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(dataset, indent=2, ensure_ascii=False), encoding="utf-8")

    status = (
        f"Found {len(samples)} audio file(s) in {base}\n"
        f"   JSON sidecars with caption: {with_meta}\n"
        f"Dataset saved to {out_path}"
    )
    return out_path, status


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
