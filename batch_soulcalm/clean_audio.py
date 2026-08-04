"""Clean soulcalm masters: denoise, tame harsh hats, then stealth harden."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from batch_birthday.ai_music_detector import DEFAULT_THRESHOLD, run_ai_detectors
from batch_birthday.ai_stealth import harden_for_upload
from batch_birthday.humanize_audio import humanize_mp3


def measure_ai(mp3: Path) -> float:
    """Return primary fakeprint AI probability."""
    detections = run_ai_detectors(mp3, threshold=DEFAULT_THRESHOLD)
    return detections[0].ai_probability if detections else 1.0


def denoise_tame_hats(src: Path, dst: Path) -> Path:
    """Remove hiss/AI grit and soften noisy high drum / hat energy.

    Sleep tracks should stay soft in the top octave — cut harsh 6–12 kHz
    hash without killing the piano body.
    """
    src = src.resolve()
    dst = dst.resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)
    # afftdn = spectral denoise; EQ cuts tinny AI hats; soft lowpass for sleep.
    af = (
        "highpass=f=35,"
        "afftdn=nr=12:nf=-28,"
        "equalizer=f=5500:t=q:w=1.1:g=-3.5,"
        "equalizer=f=8500:t=q:w=1.0:g=-6.0,"
        "equalizer=f=12000:t=h:w=0.7:g=-8.0,"
        "lowpass=f=14000,"
        "asoftclip=type=tanh:threshold=0.90:output=1,"
        "loudnorm=I=-16:TP=-1.5:LRA=9"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(src),
        "-af",
        af,
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


def clean_for_listen(
    src: Path,
    *,
    slug: str,
    bpm: int = 72,
    light: bool = True,
) -> tuple[Path, dict]:
    """Clean for listen. Default light=denoise only (keeps piano clear).

    Args:
        src: Raw ACE-Step mp3.
        slug: Track slug for report naming.
        bpm: Unused in light mode; kept for stealth path.
        light: If True, skip humanize/stealth (prefer musical clarity).

    Returns:
        (listen_path, report_dict)
    """
    out_dir = src.parent
    listen = out_dir / f"{src.stem}_clean.mp3"

    ai_before = measure_ai(src)
    if light:
        denoise_tame_hats(src, listen)
        ai_after = measure_ai(listen)
        pitch_rate = 1.0
    else:
        cleaned = out_dir / f"{src.stem}_denoised.mp3"
        pre = out_dir / f"{src.stem}_pre.mp3"
        denoise_tame_hats(src, cleaned)
        humanize_mp3(cleaned, pre, style="distribute", bpm=bpm)
        _path, pitch_rate, ai_after = harden_for_upload(pre, listen, name=slug)
        for path in (cleaned, pre):
            if path.is_file():
                path.unlink()

    report = {
        "src": str(src),
        "listen": str(listen),
        "ai_before": round(ai_before, 4),
        "ai_after": round(ai_after, 4),
        "pitch_rate": pitch_rate,
        "light": light,
        "passed": ai_after < DEFAULT_THRESHOLD,
    }
    (out_dir / f"{src.stem}_ai_report.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    return listen, report
