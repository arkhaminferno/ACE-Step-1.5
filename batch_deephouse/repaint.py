"""Surgical ACE-Step repaint for HAYA blueprint sections.

Use after a full-song cover (e.g. hayati.mp3) when only a short window
needs fixing — keeps the rest of the mix intact.
Prefer SFT/base DiT for repaint quality; turbo is weaker here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.catalog import TrackRow
from batch_deephouse.generator import build_payload, stage_cover_src
from batch_deephouse.paths import track_dir, track_mp3


# Repaint is more reliable on base/SFT than turbo.
DEFAULT_REPAINT_MODEL = "acestep-v15-base"


def build_repaint_payload(
    row: TrackRow,
    *,
    src_audio: Path,
    start_sec: float,
    end_sec: float,
    model: str = DEFAULT_REPAINT_MODEL,
) -> dict[str, Any]:
    """Build a repaint payload that rewrites only [start_sec, end_sec].

    Args:
        row: Catalog track (lyrics/prompt/BPM come from here).
        src_audio: Existing mix to mask-edit.
        start_sec: Window start in seconds.
        end_sec: Window end in seconds (must be > start).
        model: DiT checkpoint name (prefer base/SFT).

    Returns:
        Request body for ``/release_task``.

    Raises:
        ValueError: If the time window is invalid.
    """
    if end_sec <= start_sec:
        raise ValueError(f"repaint window invalid: {start_sec} >= {end_sec}")
    if start_sec < 0:
        raise ValueError("repaint start must be >= 0")

    payload = build_payload(row)
    payload["task_type"] = "repaint"
    payload["src_audio_path"] = stage_cover_src(src_audio)
    payload["repainting_start"] = float(start_sec)
    payload["repainting_end"] = float(end_sec)
    payload["model"] = model
    payload["thinking"] = False
    # Cover strength not used for repaint mask, but clear cover path confusion.
    payload.pop("audio_cover_strength", None)
    return payload


def repaint_track_window(
    row: TrackRow,
    *,
    start_sec: float,
    end_sec: float,
    api_base: str,
    api_key: str = "",
    src_audio: Path | None = None,
    out_path: Path | None = None,
    model: str = DEFAULT_REPAINT_MODEL,
) -> Path:
    """Repaint one time window and write a new mix next to the original.

    Default output: ``output/{slug}/{slug}_repaint_{start}_{end}.mp3``.
    """
    src = src_audio or track_mp3(row.slug)
    if not src.exists():
        raise FileNotFoundError(f"Missing source mix for repaint: {src}")

    if out_path is None:
        out_dir = track_dir(row.slug)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / (
            f"{row.slug}_repaint_{int(start_sec)}_{int(end_sec)}.mp3"
        )

    payload = build_repaint_payload(
        row,
        src_audio=src,
        start_sec=start_sec,
        end_sec=end_sec,
        model=model,
    )
    print(
        f"REPAINT ({row.slug}): {start_sec:.1f}s–{end_sec:.1f}s "
        f"model={model}"
    )
    generate_to_file(
        payload,
        api_base=api_base,
        api_key=api_key,
        out_path=out_path,
        label=f"{row.slug}-repaint",
    )
    print(f"OK: {out_path}")
    return out_path
