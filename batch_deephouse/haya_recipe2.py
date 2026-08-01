"""HAYA Recipe 2 — locked after approved Hanan 3-min (2026-08).

What made it work:
  - Soft short vocal open (~4–8s), groove by ~8s (Rima arrangement)
  - VOCAL GRID LOCK — hook syllables on the kick
  - Equal SHORT chorus hits every repeat (no elongated 3rd line / melisma)
  - BPM 108 pocket, thinking LM 1.7B, night-drive spice, distribute+stealth master
  - Base length ~180s; 35-min = full 3:00 loops with short ~5s blend at the end

Use ``build_recipe2_payload`` to recreate Hanan or mint a new song in this lane.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from batch_deephouse.haya_signature_recipe import (
    EARWORM_MOTIF,
    HOOK_VARIETY,
    NIGHT_DRIVE_SPICE,
    ORGANIC_PRODUCTION,
    RIMA_ARRANGEMENT,
    RIMA_COLOR,
    SIGNATURE_KEY,
    SIGNATURE_LM,
    SIGNATURE_MODEL,
    VOCAL_GRID_LOCK,
    build_signature_payload,
    master_signature_mp3,
)

# --- Locked Recipe 2 defaults (Hanan-approved) ---
RECIPE2_BPM = 108
RECIPE2_KEY = SIGNATURE_KEY
RECIPE2_DURATION = 180
RECIPE2_LM = SIGNATURE_LM
RECIPE2_MODEL = SIGNATURE_MODEL
RECIPE2_CROSSFADE_SEC = 5.0  # short tri blend at ~3:00 (not early 2:45 cuts)

# Reference take that locked the recipe.
RECIPE2_HANAN_HOOK = "يا حنان"
RECIPE2_HANAN_SEED = 81440

CHORUS_EQUAL_HITS = (
    "CHORUS RHYTHM (MANDATORY): sing the hook as a SHORT equal-length motif "
    "every repeat. Do NOT elongate, stretch, or melisma the third chorus line. "
    "No drawn-out 'Ooooh' rubato — same tight kick-locked rhythm for every hit."
)

RECIPE2_NEGATIVE_EXTRA = (
    ", elongated third chorus, stretched oh-name melisma, rubato chorus, "
    "long drawn-out hook on third repeat"
)


def build_recipe2_lyrics(
    *,
    hook: str,
    verse1: list[str],
    verse2: list[str],
    verse3: list[str],
) -> str:
    """Build Recipe 2 lyrics — short soft open, equal short chorus hits.

    Args:
        hook: Arabic hook phrase (e.g. ``يا حنان``).
        verse1: First verse lines.
        verse2: Second verse lines.
        verse3: Third verse lines.

    Returns:
        Tagged lyrics string for ACE-Step.
    """
    v1 = "\n".join(verse1)
    v2 = "\n".join(verse2)
    v3 = "\n".join(verse3)
    return f"""[Intro]
(soft female hum mmm ~4–8s — light pad, almost no kick)
(kick enters by 8 seconds — vocal stays on the grid)

[Verse]
{v1}

[Chorus]
{hook}
{hook}
{hook}
(same short rhythm every time — NO stretched/elongated third line)

[Verse]
{v2}

[Chorus]
{hook}
{hook}
{hook}
{hook}
(every line short and on the kick — equal length, no melisma stretch)

[Bridge]
(soft oud — vocal rests on pocket)
{hook}

[Chorus]
{hook}
{hook}
{hook}

[Verse]
{v3}

[Chorus]
{hook}
{hook}
{hook}

[Outro]
{hook}
(soft natural fade — short, on beat)
"""


def build_recipe2_payload(
    *,
    hook: str,
    slug: str,
    lyrics: str,
    seed: int,
    bpm: int = RECIPE2_BPM,
    key: str = RECIPE2_KEY,
    duration: int = RECIPE2_DURATION,
    color_note: str = "",
) -> dict[str, Any]:
    """Build Recipe 2 text2music payload (Hanan-approved lane).

    Args:
        hook: Arabic hook phrase.
        slug: Song id.
        lyrics: From ``build_recipe2_lyrics``.
        seed: Fixed seed.
        bpm: Tempo (default 108).
        key: Key scale.
        duration: Seconds (default 180).
        color_note: Optional within-lane color.

    Returns:
        ACE-Step ``/release_task`` body.
    """
    color = color_note.strip() or (
        f"{RIMA_COLOR}; tight vocal pocket — every hook syllable on the kick, "
        "equal short chorus hits only, no rushed or stretched chanting"
    )
    payload = build_signature_payload(
        hook=hook,
        slug=slug,
        lyrics=lyrics,
        seed=seed,
        bpm=bpm,
        key=key,
        duration=duration,
        color_note=color,
        motif_note=f"short on-kick '{hook}' — never elongate the third repeat",
        grid_lock=True,
    )
    payload["prompt"] = (
        f"{payload['prompt']} RECIPE2 {CHORUS_EQUAL_HITS} "
        f"{ORGANIC_PRODUCTION} {VOCAL_GRID_LOCK}"
    )
    payload["instruction"] = (
        f"{payload['instruction']} {CHORUS_EQUAL_HITS} "
        f"Apply Recipe 2: {RIMA_ARRANGEMENT} {EARWORM_MOTIF} {HOOK_VARIETY} "
        f"{NIGHT_DRIVE_SPICE}"
    )
    payload["lm_negative_prompt"] = (
        payload["lm_negative_prompt"] + RECIPE2_NEGATIVE_EXTRA
    )
    payload["recipe"] = "haya_recipe2"
    return payload


def master_recipe2_mp3(
    raw: Path, *, slug: str, bpm: int = RECIPE2_BPM
) -> tuple[Path, float]:
    """Distribute humanize + stealth → ``{slug}_human.mp3`` / upload copy."""
    return master_signature_mp3(raw, slug=slug, bpm=bpm)


__all__ = [
    "CHORUS_EQUAL_HITS",
    "RECIPE2_BPM",
    "RECIPE2_CROSSFADE_SEC",
    "RECIPE2_DURATION",
    "RECIPE2_HANAN_HOOK",
    "RECIPE2_HANAN_SEED",
    "RECIPE2_KEY",
    "build_recipe2_lyrics",
    "build_recipe2_payload",
    "master_recipe2_mp3",
]
