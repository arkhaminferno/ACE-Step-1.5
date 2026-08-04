"""Captions and generation defaults — clear instrumental piano + pads."""

from __future__ import annotations

DEFAULT_BPM = 70
DEFAULT_KEY = "A minor"
DEFAULT_LANGUAGE = "en"

# Keep prompts short — long bans can confuse the model into muddy output.
CHANNEL_CAPTION = (
    "Instrumental only, no vocals. Soft felt piano with a simple clear melody "
    "you can follow easily, warm retro synth pads underneath, slow and calm. "
    "Quiet night ambient for sleep. Soft low end, dark top, no bright drums, "
    "no hats, no cymbals. Melancholic rainy-window mood. High fidelity, soft."
)

CHANNEL_INSTRUCTION = (
    "Create an ORIGINAL instrumental track. No singing, no humming, no speech. "
    "Lead: soft felt piano playing a simple repeating motif with clear notes. "
    "Bed: warm quiet pads. Very slow. Leave space between phrases. Soft fade out."
)

LM_NEGATIVE_PROMPT = (
    "vocals, singing, humming, choir, speech, whisper, "
    "EDM drop, heavy drums, bright hi-hats, noisy cymbals, "
    "digital grit, trap 808, brass, upbeat pop, dance beat, chaos, noise wall"
)

DEFAULT_INSTRUMENTAL_LYRICS = """[Intro]
(soft felt piano alone — clear simple notes)

[Section]
(same piano motif repeats gently, warm pad under)

[Section]
(piano motif continues, slightly quieter)

[Breakdown]
(pads only, soft)

[Section]
(piano motif returns clear and soft)

[Outro]
(piano fades into pad)
"""


def build_caption(*, mood_note: str = "") -> str:
    """Return caption for an instrumental soulcalm pilot."""
    parts = [CHANNEL_CAPTION]
    note = " ".join((mood_note or "").split())
    if note:
        parts.append(f"Direction: {note}.")
    return " ".join(parts)


def build_instruction(*, mood_note: str = "") -> str:
    """Return instruction for an instrumental soulcalm pilot."""
    parts = [CHANNEL_INSTRUCTION]
    note = " ".join((mood_note or "").split())
    if note:
        parts.append(f"Direction: {note}.")
    return " ".join(parts)


def build_payload(
    *,
    lyrics: str = DEFAULT_INSTRUMENTAL_LYRICS,
    duration_sec: int,
    bpm: int = DEFAULT_BPM,
    key_scale: str = DEFAULT_KEY,
    seed: int | None = None,
    mood_note: str = "",
    thinking: bool = True,
) -> dict:
    """Build ACE-Step text2music payload for instrumental soulcalm."""
    payload: dict = {
        "task_type": "text2music",
        "prompt": build_caption(mood_note=mood_note),
        "instruction": build_instruction(mood_note=mood_note),
        "lyrics": lyrics,
        "negative_prompt": LM_NEGATIVE_PROMPT,
        "duration": float(duration_sec),
        "bpm": int(bpm),
        "key_scale": key_scale,
        "time_signature": "4/4",
        "language": DEFAULT_LANGUAGE,
        "thinking": thinking,
        "batch_size": 1,
        "instrumental": True,
    }
    if seed is not None:
        payload["seed"] = int(seed)
    return payload
