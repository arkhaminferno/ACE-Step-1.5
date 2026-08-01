"""Maqam-aware tagging and lyric formatting for HAYA generation.

Text-only maqam names (e.g. "Maqam Rast") often flatten to 12-TET on base
models. Prefer: (1) structured 5-component genre tags, (2) ACE-Step cover /
src-audio conditioning off a short authentic Arabic reference clip.
Dual-track ICL stem paths are for YuE-style runners, not ACE-Step cover.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

ARABIC_INSTRUMENTS: dict[str, str] = {
    "oud": "traditional acoustic dry oud",
    "qanun": "classical microtonal qanun arpeggios",
    "nay": "hypnotic nay flute",
    "ney": "hypnotic ney flute",
    "darbuka": "light darbuka hand-drum accents",
    "riq": "soft riq frame-drum pulse",
}

ARABIC_RHYTHMS: dict[str, str] = {
    "samai": "samai rhythmic feel under four-on-floor",
    "maqsum": "maqsum-flavored groove under four-on-floor",
    "saidi": "saidi accent pattern under four-on-floor",
}

# Named maqamat — use with audio reference; text alone is weak guidance.
MAQAMAT: dict[str, str] = {
    "hijaz": "maqam hijaz colour (raised second feel), expressive melisma",
    "bayati": "maqam bayati colour, warm melancholic contour",
    "rast": "maqam rast colour, grounded open melodic centre",
    "kurd": "maqam kurd colour, dark minor-leaning contour",
    "nahawand": "maqam nahawand colour, close to natural minor with tarab slides",
}


def build_genre_tags(
    *,
    genre: str = "arabic melodic deep house",
    instrument: str = "",
    rhythm: str = "",
    mood: str = "hypnotic melancholic late-night",
    gender: str = "female",
    timbre: str = "airy warm expressive vocal melisma",
    maqam: str = "",
) -> str:
    """Build a space-delimited genre/instrument/mood/gender/timbre tag string.

    Args:
        genre: Style/genre core (may include BPM words).
        instrument: Instrument phrase(s).
        rhythm: Rhythm flavour under the house kick.
        mood: Emotional tone words.
        gender: Vocal gender cue.
        timbre: Vocal/instrument timbre words.
        maqam: Optional maqam colour phrase (best paired with audio ref).

    Returns:
        Single-line tag prompt suitable for caption append.
    """
    parts = [genre, instrument, rhythm, maqam, mood, gender, timbre]
    return " ".join(p.strip() for p in parts if p and p.strip())


def format_lyric_sections(sections: Mapping[str, str]) -> str:
    """Join lyric sections with exactly two newlines between blocks.

    Args:
        sections: Ordered mapping of section name -> lyric body
            (e.g. {"verse": "...", "chorus": "..."}).

    Returns:
        Lyrics string with ``[section]`` labels and ``\\n\\n`` separators.
    """
    blocks: list[str] = []
    for name, text in sections.items():
        label = f"[{name.strip().lower()}]"
        body = (text or "").strip()
        if not body:
            continue
        blocks.append(f"{label}\n{body}")
    return "\n\n".join(blocks)


def resolve_icl_stems(reference_dir: Path, track_name: str) -> dict[str, object]:
    """Locate optional dual-track ICL stems for YuE-style runners.

    Expects ``{track_name}_vocal.wav`` and ``{track_name}_instrumental.wav``
    under ``reference_dir`` (e.g. after UVR separation).

    Args:
        reference_dir: Directory holding separated stems.
        track_name: Stem basename prefix.

    Returns:
        Dict with vocal/instrumental paths, readiness flag, and optional warning.
    """
    root = Path(reference_dir)
    vocal = root / f"{track_name}_vocal.wav"
    instrumental = root / f"{track_name}_instrumental.wav"
    ready = vocal.is_file() and instrumental.is_file()
    return {
        "vocal_prompt_path": str(vocal) if vocal.is_file() else None,
        "instrumental_prompt_path": str(instrumental) if instrumental.is_file() else None,
        "dual_track_ready": ready,
        "warning": (
            None
            if ready
            else (
                f"Stems not found under {root}: need "
                f"{track_name}_vocal.wav and {track_name}_instrumental.wav"
            )
        ),
    }


def default_haya_genre_tags(
    *,
    bpm: int,
    maqam: str = "hijaz",
    instruments: str = "oud+nay",
) -> str:
    """Return HAYA default Arabic deep-house genre tags for a BPM/maqam.

    Args:
        bpm: Target tempo.
        maqam: Key into ``MAQAMAT`` (falls back to raw string).
        instruments: ``+``-joined keys into ``ARABIC_INSTRUMENTS``.

    Returns:
        Space-delimited genre tag line.
    """
    inst_parts = [
        ARABIC_INSTRUMENTS.get(k.strip().lower(), k.strip())
        for k in instruments.split("+")
        if k.strip()
    ]
    maqam_phrase = MAQAMAT.get(maqam.strip().lower(), maqam.strip())
    return build_genre_tags(
        genre=f"arabic melodic deep house {bpm} bpm",
        instrument=" ".join(inst_parts),
        rhythm=ARABIC_RHYTHMS["maqsum"],
        mood="hypnotic melancholic elegant late-night",
        gender="female",
        timbre="airy warm expressive vocal melisma",
        maqam=maqam_phrase,
    )
