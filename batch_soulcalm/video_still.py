"""Render a still-image YouTube video: fade in → hold → fade out (no overlays)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def render_still_video(
    *,
    image_path: Path,
    audio_path: Path,
    output_path: Path,
    fade_sec: float = 4.0,
) -> Path:
    """Build MP4 from one still + audio with fade in/out only.

    Args:
        image_path: Full-bleed still of the girl (jpg/png).
        audio_path: Mastered audio (mp3/wav).
        output_path: Destination mp4 path.
        fade_sec: Fade duration at start and end.

    Returns:
        Path to the written MP4.
    """
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg not found on PATH")
    if not image_path.is_file():
        raise FileNotFoundError(f"Still image missing: {image_path}")
    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio missing: {audio_path}")

    # Probe audio duration for fade-out start.
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    duration = float(probe.stdout.strip())
    fade_out_start = max(duration - fade_sec, 0.0)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Scale/crop still to 1920x1080 HD, loop for audio length, soft fades only.
    vf = (
        "scale=1920:1080:flags=lanczos:force_original_aspect_ratio=increase,"
        "crop=1920:1080,"
        "setsar=1,"
        f"fade=t=in:st=0:d={fade_sec},"
        f"fade=t=out:st={fade_out_start}:d={fade_sec}"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-framerate",
        "30",
        "-i",
        str(image_path),
        "-i",
        str(audio_path),
        "-vf",
        vf,
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        "17",
        "-tune",
        "stillimage",
        "-pix_fmt",
        "yuv420p",
        "-profile:v",
        "high",
        "-level",
        "4.1",
        "-c:a",
        "aac",
        "-b:a",
        "320k",
        "-ar",
        "48000",
        "-shortest",
        "-movflags",
        "+faststart",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)
    return output_path
