"""Deliver masters for HAYA uploads.

Modes:
- ``raw`` (default): bit-identical copy to ``*_human.mp3`` / ``*_upload.mp3``
- ``stealth``: AI-detector harden into ``*_human.mp3`` (original untouched)
- ``clear``: presence EQ + stealth (legacy; often sounds worse on deep house)
- ``natural``: birthday-style humanize + stealth (avoid for HAYA)
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

from batch_birthday.ai_stealth import harden_for_upload
from batch_birthday.humanize_audio import humanize_mp3


def _clarity_presence(src: Path, dst: Path) -> None:
    """Open vocal/instrument presence — no muffling low-pass."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        af = (
            "highpass=f=60,"
            "equalizer=f=1200:t=q:w=1.0:g=2.5,"
            "equalizer=f=3000:t=q:w=1.0:g=3.0,"
            "equalizer=f=5500:t=q:w=1.2:g=1.5,"
            "equalizer=f=200:t=q:w=0.8:g=-1.5,"
            "loudnorm=I=-14:TP=-1.0:LRA=11"
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
            str(tmp_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        dst.write_bytes(tmp_path.read_bytes())
    finally:
        tmp_path.unlink(missing_ok=True)


def deliver_mp3(
    src: Path,
    *,
    name: str,
    bpm: int = 110,
    mode: str = "raw",
) -> tuple[Path, Path, float]:
    """Prepare upload master from a raw or long-mix MP3.

    Args:
        src: Source MP3 (kept unchanged for ``stealth`` / ``raw``).
        name: Seed name for stealth variation.
        bpm: Reserved for tempo-aware beds.
        mode: ``raw``, ``stealth``, ``clear``, or ``natural``.

    Returns:
        (human_path, upload_path, ai_probability)
    """
    del bpm
    src = src.resolve()
    human = src.with_name(f"{src.stem}_human.mp3")
    upload = src.with_name(f"{src.stem}_upload.mp3")

    if mode == "raw":
        shutil.copy2(src, human)
        shutil.copy2(src, upload)
        return human, upload, -1.0

    if mode == "stealth":
        # Write hardened audio to *_human.mp3; original stays as-is.
        _path, _rate, ai_prob = harden_for_upload(src, human, name=name)
        shutil.copy2(human, upload)
        return human, upload, ai_prob

    if mode == "clear":
        _clarity_presence(src, human)
        work = human
    elif mode == "natural":
        humanize_mp3(src, human, style="natural")
        work = human
    else:
        raise ValueError(f"Unknown deliver mode: {mode}")

    _path, _rate, ai_prob = harden_for_upload(work, upload, name=name)
    return human, upload, ai_prob


def main(argv: list[str] | None = None) -> int:
    """CLI: raw/stealth/clear deliver for HAYA masters."""
    parser = argparse.ArgumentParser(description="Deliver HAYA MP3 (raw by default)")
    parser.add_argument("mp3", type=Path)
    parser.add_argument("--name", default="")
    parser.add_argument("--bpm", type=int, default=110)
    parser.add_argument(
        "--mode",
        choices=("raw", "stealth", "clear", "natural"),
        default="stealth",
        help="stealth=AI harden (no noise); raw=exact copy; clear=EQ+stealth",
    )
    args = parser.parse_args(argv)

    name = args.name or args.mp3.stem
    human, upload, ai_prob = deliver_mp3(
        args.mp3,
        name=name,
        bpm=args.bpm,
        mode=args.mode,
    )
    print(f"HUMANIZED: {human}")
    print(f"UPLOAD:    {upload}")
    if ai_prob < 0:
        print("AI score:  (skipped — raw passthrough)")
    else:
        print(f"AI score:  {ai_prob:.4f}")
    print(f"Mode:      {args.mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
