"""Project paths for batch_deephouse."""

from __future__ import annotations

from pathlib import Path

BATCH_ROOT = Path(__file__).resolve().parent
INPUT_DIR = BATCH_ROOT / "input"
OUTPUT_DIR = BATCH_ROOT / "output"
TEMPLATES_DIR = BATCH_ROOT / "templates" / "presets"
AUDIO_TEMPLATES_DIR = BATCH_ROOT / "templates" / "audio"
# Approved Yalil groove pocket used as cover reference for new pilots.
YALIL_GROOVE_REF = AUDIO_TEMPLATES_DIR / "yalil-groove-120.mp3"
DEFAULT_CSV = INPUT_DIR / "tracks.csv"
DEFAULT_API_BASE = "http://127.0.0.1:8001"


def track_dir(slug: str) -> Path:
    """Return output folder for one track slug."""
    return OUTPUT_DIR / slug


def track_mp3(slug: str) -> Path:
    """Return primary MP3 path for a track."""
    return track_dir(slug) / f"{slug}.mp3"


def track_meta(slug: str) -> Path:
    """Return sidecar JSON path for a track."""
    return track_dir(slug) / f"{slug}.json"
