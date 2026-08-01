"""HAYA prompts — sound-bible + hook-first (structured ACE Studio style)."""

from __future__ import annotations

from batch_deephouse.haya_sound_bible import (
    HAYA_BPM,
    HAYA_KEY,
    VOCAL_PERSONA,
    instrumental_prompt,
    palette_for_slug,
    vocal_instruction,
    vocal_prompt,
)
from batch_deephouse.lyrics_packs import LYRICS_BY_SLUG
from batch_deephouse.maqam_prompt import default_haya_genre_tags
from batch_deephouse.sonic_identity import format_sonic_block, get_sonic

# Per-slug maqam colour for genre tags (audio ref still beats text alone).
_MAQAM_BY_SLUG: dict[str, str] = {
    "yalil": "hijaz",
    "noor": "nahawand",
    "gharib": "kurd",
    "hayati": "bayati",
}

DEFAULT_BPM = HAYA_BPM
DEFAULT_KEY = HAYA_KEY
DEFAULT_DURATION_SEC = 120

LM_NEGATIVE_PROMPT = (
    "no trumpet, no brass, no guzheng, no pipa, no male vocal, no choir, no opera, "
    "no cinematic soundtrack, no festival EDM, no mumbled lyrics, "
    "no robotic vocals, no TTS, no vocoder, no auto-tune artifacts, "
    "no pitch-shifted sample chops, no off-key singing, no out-of-time vocals, "
    "no artificial AI voice, no English copy of Delina lyrics"
)


def build_instrumental_caption(
    *,
    bpm: int | None = None,
    slug: str = "",
    maqam: str | None = None,
) -> str:
    """Return structured instrumental-only caption with Arabic genre tags."""
    tempo = bpm or HAYA_BPM
    slug_key = (slug or "").strip().lower()
    maqam_name = maqam or _MAQAM_BY_SLUG.get(slug_key, "hijaz")
    base = instrumental_prompt(
        bpm=tempo,
        instruments=palette_for_slug(slug),
    )
    tags = default_haya_genre_tags(bpm=tempo, maqam=maqam_name)
    return f"{base}\n\nGenreTags: {tags}."


def build_caption(
    *,
    slug: str = "",
    mood_note: str = "",
    bpm: int | None = None,
    key_scale: str | None = None,
    maqam: str | None = None,
) -> str:
    """Return structured vocal caption for HAYA."""
    identity = get_sonic(slug)
    hook = identity.hook_name if identity else ""
    key = key_scale or HAYA_KEY
    palette = palette_for_slug(slug)
    tempo = bpm or HAYA_BPM
    slug_key = (slug or "").strip().lower()
    maqam_name = maqam or _MAQAM_BY_SLUG.get(slug_key, "hijaz")
    genre_tags = default_haya_genre_tags(bpm=tempo, maqam=maqam_name)
    parts = [
        vocal_prompt(
            bpm=tempo,
            key=key,
            hook=hook,
            instruments=palette,
        )
    ]
    if identity:
        parts.append(format_sonic_block(identity))
    note = " ".join((mood_note or "").split())
    if note:
        parts.append(f"Direction: {note}.")
    parts.append(f"Palette: {palette}.")
    parts.append(f"GenreTags: {genre_tags}.")
    parts.append(
        "Maqam guidance: prefer microtonal slides and melisma from an audio "
        "reference (ACE-Step cover/src-audio); do not flatten to rigid 12-TET."
    )
    return "\n".join(parts)


def build_instruction(
    *,
    slug: str = "",
    mood_note: str = "",
    bpm: int | None = None,
    key_scale: str | None = None,
) -> str:
    """Return vocal-pass instruction."""
    identity = get_sonic(slug)
    hook = identity.hook_name if identity else "يا ليالي"
    key = key_scale or HAYA_KEY
    parts = [vocal_instruction(hook=hook, key=key)]
    if identity:
        parts.append(format_sonic_block(identity))
    if bpm is not None:
        parts.append(f"Lock {bpm} BPM.")
    note = " ".join((mood_note or "").split())
    if note:
        parts.append(f"Direction: {note}.")
    parts.append(f"Singer: {VOCAL_PERSONA}. Original HAYA track — not a Delina clone.")
    return " ".join(parts)


def build_lyrics(slug: str = "yalil") -> str:
    """Return clean hook-first Arabic lyrics for a song slug."""
    key = (slug or "yalil").strip().lower()
    if key in LYRICS_BY_SLUG:
        return LYRICS_BY_SLUG[key]
    return LYRICS_BY_SLUG["yalil"]


def build_negative_prompt() -> str:
    """Return LM negative prompt."""
    return LM_NEGATIVE_PROMPT
