"""Atmosphere beds: rain loops and sparse soft laugh moments."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from batch_deephouse.extend_mix import probe_duration_sec

ASSETS = Path(__file__).resolve().parent / "assets" / "sfx"


def synthesize_rain_loop(dst: Path, *, duration_sec: float = 60.0) -> Path:
    """Build a soft night-rain bed with ffmpeg noise (no external download)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    # Pink-ish rain: dual noise bands + light modulation feel via filters.
    af = (
        "highpass=f=400,lowpass=f=9000,"
        "equalizer=f=2000:t=q:w=1.2:g=2,"
        "equalizer=f=6000:t=q:w=1.0:g=-2,"
        "volume=-22dB,"
        "asoftclip=type=tanh:threshold=0.9"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"anoisesrc=color=pink:amplitude=0.35:d={duration_sec}:r=48000",
        "-af",
        af,
        "-ar",
        "48000",
        "-ac",
        "2",
        "-c:a",
        "pcm_s16le",
        str(dst),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return dst


def loop_to_duration(src: Path, dst: Path, *, target_sec: float) -> Path:
    """Loop a short bed to cover target_sec."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-stream_loop",
        "-1",
        "-i",
        str(src),
        "-t",
        f"{target_sec:.3f}",
        "-af",
        "afade=t=in:st=0:d=3,afade=t=out:st="
        f"{max(target_sec - 4, 0):.3f}:d=4",
        "-ar",
        "48000",
        "-c:a",
        "pcm_s16le",
        str(dst),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return dst


def mix_rain_under(
    music: Path,
    rain: Path,
    dst: Path,
    *,
    rain_db: float = -18.0,
) -> Path:
    """Lay a quiet rain bed under the music master."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    dur = probe_duration_sec(music)
    with tempfile.TemporaryDirectory() as tmp:
        rain_long = Path(tmp) / "rain_long.wav"
        loop_to_duration(rain, rain_long, target_sec=dur)
        filter_complex = (
            f"[1:a]volume={rain_db}dB[rain];"
            f"[0:a][rain]amix=inputs=2:duration=first:dropout_transition=0,"
            f"loudnorm=I=-16:TP=-1.5:LRA=9[out]"
        )
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(music),
            "-i",
            str(rain_long),
            "-filter_complex",
            filter_complex,
            "-map",
            "[out]",
            "-ar",
            "48000",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(dst),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
    return dst


def sprinkle_laughs(
    music: Path,
    laugh: Path,
    dst: Path,
    *,
    interval_sec: float = 420.0,
    first_at_sec: float = 95.0,
    laugh_db: float = -14.0,
) -> Path:
    """Insert soft distant laughs sparsely (fast itsoffset mix, no loudnorm)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    dur = probe_duration_sec(music)
    laugh_dur = probe_duration_sec(laugh)
    starts: list[float] = []
    t = first_at_sec
    while t + laugh_dur < dur - 30:
        starts.append(t)
        t += interval_sec
    if not starts:
        starts = [min(90.0, dur * 0.25)]

    # Cap sparse moments so the filter graph stays light on 1-hour masters.
    starts = starts[:8]

    cmd: list[str] = ["ffmpeg", "-y", "-i", str(music)]
    for start in starts:
        cmd.extend(["-itsoffset", f"{start:.3f}", "-i", str(laugh)])

    n = 1 + len(starts)
    weights = "1 " + " ".join(["0.18"] * len(starts))
    # Soften laughs once, then amix; keep full music duration.
    parts = [f"[0:a]anull[a0]"]
    for i in range(1, n):
        parts.append(
            f"[{i}:a]volume={laugh_db}dB,lowpass=f=6500,highpass=f=250[a{i}]"
        )
    mix_in = "".join(f"[a{i}]" for i in range(n))
    parts.append(
        f"{mix_in}amix=inputs={n}:duration=first:dropout_transition=0:"
        f"normalize=0:weights={weights}[out]"
    )
    cmd.extend(
        [
            "-filter_complex",
            ";".join(parts),
            "-map",
            "[out]",
            "-t",
            f"{dur:.3f}",
            "-ar",
            "48000",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(dst),
        ]
    )
    subprocess.run(cmd, check=True, capture_output=True)
    return dst


def ensure_rain_asset() -> Path:
    """Return a reusable rain bed under assets/sfx (prefers Mixkit download)."""
    ASSETS.mkdir(parents=True, exist_ok=True)
    preferred = (
        ASSETS / "night_rain_loop.mp3",
        ASSETS / "night_rain_loop.wav",
    )
    for path in preferred:
        if path.is_file() and path.stat().st_size > 10_000:
            return path
    path = ASSETS / "night_rain_loop.wav"
    synthesize_rain_loop(path, duration_sec=45.0)
    return path
