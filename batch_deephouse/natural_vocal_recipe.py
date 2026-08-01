"""Locked ACE-Step recipe for natural Arabic vocals locked to the beat.

Used after Layl/Hanin failures: robotic Arabic + off-grid singing came from
(1) thinking LM disabled, (2) over-long FerdausMix timing scripts, (3) 180s
duration. This module clones the approved Noor payload shape with stronger
human-vocal and kick-grid constraints.

For new HAYA releases, prefer ``haya_signature_recipe`` (this core + Qamar
night-drive spice + organic master) — locked Aug 2026.
"""

from __future__ import annotations

from typing import Any

# Proven sweet spot from approved Noor master.
DEFAULT_BPM = 108
DEFAULT_KEY = "A minor"
DEFAULT_DURATION = 120
DEFAULT_MODEL = "acestep-v15-turbo"
DEFAULT_STEPS = 20
DEFAULT_GUIDANCE = 14.0
DEFAULT_LM_CFG = 3.0

HUMAN_VOCAL = (
    "ONE real young Arabic woman singing live in a studio — warm breath, "
    "natural vibrato, soft human consonants, slight imperfect timing like a "
    "real singer, intimate close-mic. Must sound like a human performance. "
    "NOT robotic, NOT TTS, NOT vocoder, NOT Auto-Tune chipmunk, NOT sample chops, "
    "NOT English accent trying Arabic, NOT male."
)

BEAT_LOCK = (
    "Every syllable lands ON the four-on-floor kick grid. Melody stays in key. "
    "Vocal phrase starts on downbeats. No rushing, no dragging, no free-time singing."
)

SHORT_NEGATIVE = (
    "robotic vocal, TTS, vocoder, Auto-Tune artifacts, chipmunk, sample chops, "
    "male vocal, choir, English accent Arabic, off-beat vocals, out of time, "
    "off-key, brass, trumpet, guzheng, pipa"
)


def build_noor_style_prompt(*, hook: str, slug: str, key: str = DEFAULT_KEY, bpm: int = DEFAULT_BPM) -> str:
    """Short caption like the approved Noor master — no second-by-second script."""
    return (
        "Oriental deep house, warm sub-bass, minimalist electronic kick, solo dry "
        f"acoustic oud, spacious mix, 10% wet room reverb. HAYA song '{slug}'. "
        f"MANDATORY VOCAL: {HUMAN_VOCAL} "
        f"MANDATORY TIMING: {BEAT_LOCK} "
        f"Memorable hook = {hook}. Soft four-on-floor kick every beat from the start. "
        f"Sticky melodic motif. Tempo {bpm} BPM. Key {key}. "
        "Hook first in 0–3s. Clear dry PRESENT female Arabic vocal upfront. "
        "No brass. No East-Asian zither fallback."
    )


def build_noor_style_instruction(*, hook: str, key: str = DEFAULT_KEY, bpm: int = DEFAULT_BPM) -> str:
    """Instruction: human Arabic vocal locked to kick — no complex drop map."""
    return (
        "Generate ONE Arabic deep-house song. "
        f"CRITICAL VOCAL: {HUMAN_VOCAL} "
        f"CRITICAL TIMING: {BEAT_LOCK} "
        f"Sing hook '{hook}' on beat, in {key}, near {bpm} BPM. "
        "Hook first (0–3s). Soft four-on-floor kick audible from the start. "
        "Verses are real Arabic lines — not hook-only. Soft natural fade. "
        "Reject robotic/TTS/off-grid vocals."
    )


def build_simple_lyrics(*, hook: str, verse1: list[str], verse2: list[str]) -> str:
    """Simple Noor/Yalil lyric shape — short hook repeats, two short verses."""
    h = "\n".join([hook] * 4)
    v1 = "\n".join(verse1)
    v2 = "\n".join(verse2)
    return f"""[Hook]
{h}

[Verse]
{v1}

[Hook]
{h}

[Chorus]
{hook}
{hook}
{hook}
{hook}

[Break]
(soft kick + dry oud motif)

[Hook]
{h}

[Outro]
{hook}
(soft natural fade)
"""


def build_text2music_payload(
    *,
    hook: str,
    slug: str,
    lyrics: str,
    seed: int,
    bpm: int = DEFAULT_BPM,
    key: str = DEFAULT_KEY,
    duration: int = DEFAULT_DURATION,
    thinking: bool = True,
) -> dict[str, Any]:
    """Build the locked text2music payload for natural aligned Arabic vocals."""
    return {
        "prompt": build_noor_style_prompt(hook=hook, slug=slug, key=key, bpm=bpm),
        "lyrics": lyrics,
        "instruction": build_noor_style_instruction(hook=hook, key=key, bpm=bpm),
        "thinking": thinking,
        "use_format": False,
        "use_cot_caption": False,
        "use_cot_language": False,
        "vocal_language": "ar",
        "audio_duration": duration,
        "bpm": bpm,
        "key_scale": key,
        "inference_steps": DEFAULT_STEPS,
        "guidance_scale": DEFAULT_GUIDANCE,
        "lm_cfg_scale": DEFAULT_LM_CFG,
        "lm_negative_prompt": SHORT_NEGATIVE,
        "model": DEFAULT_MODEL,
        "use_random_seed": False,
        "task_type": "text2music",
        "seed": seed,
        "audio_format": "mp3",
    }
