"""Build a long continuous mix by crossfading an approved short master.

ACE-Step caps single generates at ~600s, so a 35-minute version of a loved
~3-minute track is built as a seamless night-drive mix (soft acrossfades),
preserving the exact approved audio.
"""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

SAMPLE_RATE = 48000


def probe_duration_sec(path: Path) -> float:
    """Return media duration in seconds via ffprobe."""
    import json

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def build_crossfade_long_mix(
    src: Path,
    dst: Path,
    *,
    target_sec: float = 35 * 60,
    crossfade_sec: float = 5.0,
    fade_in_sec: float = 0.0,
    fade_out_sec: float = 8.0,
) -> Path:
    """Loop a full ~3:00 master; short blend only at each 3:00 boundary.

    Plays each copy to the end (no early intro/outro cuts). A short triangular
    acrossfade (~5s) starts near 2:55 so the transition lands on 3:00 — not
    ~2:45. No open fade-in (that caused a silent hole). Soft fade only at the
    very end of the long mix.

    Args:
        src: Approved short MP3 (~3 min).
        dst: Output long MP3 path.
        target_sec: Desired total length (default 35 minutes).
        crossfade_sec: Overlap at each loop join (default 5s near 3:00).
        fade_in_sec: Soft open (default 0 — no silence at start).
        fade_out_sec: Soft close at the very end of the long mix.

    Returns:
        Path to the written long mix.
    """
    src = src.resolve()
    dst = dst.resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)

    src_dur = probe_duration_sec(src)
    if src_dur <= crossfade_sec + 5:
        raise ValueError(f"Source too short for crossfade: {src_dur:.1f}s")

    fade_in_sec = max(0.0, min(fade_in_sec, target_sec / 4))
    fade_out_sec = max(0.0, min(fade_out_sec, target_sec / 4))
    fade_out_start = max(0.0, target_sec - fade_out_sec)

    # Full song each loop; step advances by (duration - overlap).
    step = src_dur - crossfade_sec
    loops_needed = max(2, int(math.ceil((target_sec - crossfade_sec) / step)) + 1)

    inputs: list[str] = []
    for _ in range(loops_needed):
        inputs.extend(["-i", str(src)])

    if fade_in_sec > 0.05:
        edge_fades = (
            f"afade=t=in:st=0:d={fade_in_sec},"
            f"afade=t=out:st={fade_out_start}:d={fade_out_sec}"
        )
    else:
        edge_fades = f"afade=t=out:st={fade_out_start}:d={fade_out_sec}"

    if loops_needed == 1:
        filter_complex = (
            f"[0:a]atrim=0:{target_sec},asetpts=PTS-STARTPTS,{edge_fades}[out]"
        )
    else:
        # Triangular — keeps energy; long exp curves dipped to silence.
        xf = f"acrossfade=d={crossfade_sec}:c1=tri:c2=tri"
        filter_parts = [f"[0:a][1:a]{xf}[a1]"]
        last = "a1"
        for i in range(2, loops_needed):
            nxt = f"a{i}"
            filter_parts.append(f"[{last}][{i}:a]{xf}[{nxt}]")
            last = nxt
        filter_parts.append(
            f"[{last}]atrim=0:{target_sec},asetpts=PTS-STARTPTS,{edge_fades}[out]"
        )
        filter_complex = ";".join(filter_parts)

    cmd = [
        "ffmpeg",
        "-y",
        *inputs,
        "-filter_complex",
        filter_complex,
        "-map",
        "[out]",
        "-ar",
        str(SAMPLE_RATE),
        "-c:a",
        "libmp3lame",
        "-b:a",
        "192k",
        str(dst),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg failed for {src.name}: {result.stderr[-2000:]}"
        )
    return dst
