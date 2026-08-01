"""Load deep house track rows from CSV."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TrackRow:
    """One deep house track catalog entry."""

    title: str
    slug: str
    bpm: int
    key_scale: str
    duration_sec: int
    seed: int | None
    mood: str
    enabled: bool
    cover_strength: float | None = None
    # Optional cover/remaster source (path relative to batch root or absolute).
    cover_src: str = ""


def _parse_bool(value: str) -> bool:
    """Parse CSV boolean flags."""
    return (value or "").strip().lower() in {"1", "true", "yes", "y"}


def _parse_optional_int(value: str) -> int | None:
    """Parse optional integer; empty becomes None."""
    text = (value or "").strip()
    if not text:
        return None
    return int(text)


def _parse_optional_float(value: str) -> float | None:
    """Parse optional float; empty becomes None."""
    text = (value or "").strip()
    if not text:
        return None
    return float(text)


def load_tracks(csv_path: Path) -> list[TrackRow]:
    """Load enabled and disabled tracks from CSV."""
    rows: list[TrackRow] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            title = (raw.get("title") or "").strip()
            slug = (raw.get("slug") or "").strip()
            if not title or not slug:
                continue
            rows.append(
                TrackRow(
                    title=title,
                    slug=slug,
                    bpm=int((raw.get("bpm") or "120").strip()),
                    key_scale=(raw.get("key_scale") or "A minor").strip(),
                    duration_sec=int((raw.get("duration_sec") or "120").strip()),
                    seed=_parse_optional_int(raw.get("seed") or ""),
                    mood=(raw.get("mood") or "").strip(),
                    enabled=_parse_bool(raw.get("enabled") or "false"),
                    cover_strength=_parse_optional_float(raw.get("cover_strength") or ""),
                    cover_src=(raw.get("cover_src") or "").strip(),
                )
            )
    return rows


def enabled_tracks(csv_path: Path) -> list[TrackRow]:
    """Return only enabled catalog rows."""
    return [row for row in load_tracks(csv_path) if row.enabled]
