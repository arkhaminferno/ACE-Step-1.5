"""DUORUSH-style Deep House genre anchor for prompt injection.

Forces house structure before Arabic timbre so DoRA accents colour
without collapsing into a traditional acoustic recital.
"""

from __future__ import annotations

# Opt-in diagnostic default only — HAYA production uses base turbo (no DoRA).
DEFAULT_DORA_SCALE = 0.35

# Prefixed onto every caption / diagnostic prompt.
GENRE_ANCHOR = (
    "Deep House, Modern Club Production, four-on-floor side-chained kick, "
    "deep sub-bass pump, tight house percussion, ethereal atmosphere, "
    "high-fidelity club mix."
)


def format_prompt(user_input: str, *, bpm: int | None = None) -> str:
    """Prefix user/song text with a Deep House genre anchor.

    Args:
        user_input: Caption, mood, or free-form prompt body.
        bpm: Optional tempo lock injected after the anchor.

    Returns:
        Genre-anchored prompt string.
    """
    body = " ".join((user_input or "").split())
    if bpm is not None:
        return f"{GENRE_ANCHOR} {bpm} BPM. {body}".strip()
    return f"{GENRE_ANCHOR} {body}".strip()


def clamp_dora_scale(weight: float) -> float:
    """Clamp DoRA / LoRA scale to the API-safe [0, 1] range.

    Args:
        weight: Requested adapter scale.

    Returns:
        Clamped scale in [0.0, 1.0].
    """
    return max(0.0, min(1.0, float(weight)))
