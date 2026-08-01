"""HAYA signature recipe — locked after Hanan/Qamar approval (2026-08).

Core (do not remove):
  thinking LM 1.7B + natural Arabic vocal beat-lock + organic distribute master

Signature spice (Qamar lane):
  darker night-drive — deeper sub, firmer kick, tiny darbuka

Earworm rule (required — every song):
  One SHORT addictive signature motif that REPEATS after the open so the
  listener remembers it and wants to replay. Motif can be a sticky Arabic
  vocal phrase, a dry oud lick, or a kick/bass figure — but it must return
  often (chorus / break / outro). NOT a doubled song title (``ريما ريما``).
  Each song's motif must be unique from other HAYA songs.

Rima arrangement (preferred — approved gold):
  SHORT soft female hum/vocal first (~4–8s, light pad under), then main
  four-on-floor by ~8s + earworm. Do NOT use a long instrumental intro
  (12–40s loses listeners). Do NOT jump straight into a chanted chorus.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from batch_birthday.ai_stealth import harden_for_upload
from batch_birthday.humanize_audio import humanize_mp3
from batch_deephouse.natural_vocal_recipe import (
    SHORT_NEGATIVE,
    build_simple_lyrics,
    build_text2music_payload,
)

# --- Locked defaults (Qamar-approved pocket) ---
SIGNATURE_BPM = 110
SIGNATURE_KEY = "A minor"
SIGNATURE_DURATION = 60
SIGNATURE_LM = "acestep-5Hz-lm-1.7B"
SIGNATURE_MODEL = "acestep-v15-turbo"

ORGANIC_PRODUCTION = (
    "Live human studio take, real Arabic woman singer with breath and vibrato, "
    "soft imperfect timing, warm dry mix, gentle room, analog warmth, "
    "NOT AI, NOT TTS, NOT synthetic, NOT sterile digital polish, NOT vocoder."
)

NIGHT_DRIVE_SPICE = (
    "SIGNATURE SPICE: darker night-drive — deeper warm sub bass, firmer "
    "four-on-floor kick every beat, tiny soft darbuka dust in the back only, "
    "dry oud reply in gaps, cinematic pads, late-night highway mood. "
    "Still oriental deep house. No brass. No East-Asian zither."
)

# Sticky motif = the addictive "why you replay this song" element.
EARWORM_MOTIF = (
    "EARWORM (MANDATORY): invent ONE short addictive signature motif unique "
    "to THIS song. After the soft vocal open, REPEAT the motif in every "
    "chorus, echo it in the break, close on it. Motif may be a sticky Arabic "
    "vocal phrase OR a dry oud lick OR a kick/bass figure that listeners "
    "hum later. Make it memorable and replay-addictive. "
    "Do NOT chant the song title twice (no Name-Name). "
    "Do NOT copy another HAYA song's motif."
)

# Approved gold from Rima: short soft vocal open, then beat.
RIMA_ARRANGEMENT = (
    "RIMA ARRANGEMENT (MANDATORY): SHORT soft INTRO only (~4–8 seconds) = "
    "intimate young Arabic female vocal humming (mmm) or softly singing a "
    "gentle line, with light pad under her — NOT a long instrumental. "
    "Main four-on-floor kick + warm sub MUST enter by ~8 seconds. "
    "Never let the intro run past 10s. Never open with 20–40s of pads/oud alone. "
    "After the short vocal open, drop the groove and earworm. Perfectly sung, "
    "close-mic, human. Do NOT jump straight into a doubled-name chorus."
)

RIMA_COLOR = (
    "more intimate close-mic vocal, slightly softer pads, "
    "oud answers more often in the gaps, distinct short melodic motif, "
    "SHORT soft female hum/vocal intro then groove by ~8s"
)

HOOK_VARIETY = (
    "HOOK RULE: the earworm motif is the hook — a UNIQUE short phrase or lick, "
    "not the song title repeated twice. Different contour than other HAYA songs."
)

# Fix off-grid Arabic hooks (e.g. "حنان" drifting off the kick).
VOCAL_GRID_LOCK = (
    "VOCAL GRID LOCK (MANDATORY): female Arabic vocal MUST sit on the kick grid. "
    "Each syllable of the hook lands ON a kick (downbeat or even eighth). "
    "No rushing the name, no dragging behind the beat, no free-rubato chanting. "
    "Hook words like حنان / ريما are sung in time with the four-on-floor — "
    "tight pocket, danceable, quantized feel while still sounding human."
)

SIGNATURE_NEGATIVE = (
    SHORT_NEGATIVE
    + ", synthetic, AI generated, sterile, robotic, TTS, hyper polished, "
    "trap, amapiano spam, soft weak kick, thin bass, "
    "title name chanted twice, identical chorus every song, "
    "no repeating motif, forgettable hook, wandering melody with no earworm, "
    "instant full chorus slam, long instrumental intro, 20 second intro, "
    "40 second intro, pads-only open, listener skip intro, "
    "off-beat vocals, rushed hook syllables, behind the beat, ahead of the beat, "
    "out of pocket singing, free-time chanting over the kick"
)

LyricShape = Literal["rima", "phrase", "call", "story", "soft"]


def build_signature_lyrics(
    *,
    hook_lines: list[str],
    verse1: list[str],
    verse2: list[str],
    shape: LyricShape = "rima",
    bridge: list[str] | None = None,
) -> str:
    """Build lyrics that hammer one earworm motif without doubled-name chants.

    Args:
        hook_lines: 1–3 unique Arabic lines for the sticky motif (not ``Name Name``).
        verse1: Verse one lines (sung soft in the open on ``rima`` shape).
        verse2: Verse two lines.
        shape: Layout — default ``rima`` (soft vocal open → beat/chorus).
        bridge: Optional bridge lines (used by ``story`` / ``soft``).

    Returns:
        Tagged lyrics string with soft open then motif in chorus/break/outro.
    """
    if not hook_lines:
        raise ValueError("hook_lines must include at least one Arabic line")
    # Motif line = first hook line; keep it short and sticky.
    motif = hook_lines[0]
    hook_block = "\n".join(hook_lines)
    v1 = "\n".join(verse1)
    v2 = "\n".join(verse2)
    br = "\n".join(bridge or [])

    if shape == "rima":
        # Short soft vocal/hum, then main beat + earworm (keep intros brief).
        return f"""[Intro]
(soft female hum mmm ~4–8s only — light pad under vocal, almost no kick)
(beat enters by 8 seconds)

[Verse]
{v1}

[Chorus]
{hook_block}
{motif}

[Verse]
{v2}

[Chorus]
{hook_block}
{motif}
{motif}

[Break]
(oud echoes motif: {motif})

[Chorus]
{hook_block}
{motif}

[Outro]
{motif}
(soft natural fade)
"""

    if shape == "call":
        lead = motif
        answer = hook_lines[1] if len(hook_lines) > 1 else verse1[0]
        return f"""[Intro]
{lead}
(soft kick + breath)

[Verse]
{v1}

[Chorus]
{lead}
{answer}
{lead}
{answer}

[Verse]
{v2}

[Chorus]
{lead}
{answer}
{lead}
{answer}

[Break]
(oud echoes: {lead})

[Chorus]
{lead}
{answer}
{lead}

[Outro]
{lead}
(soft natural fade)
"""

    if shape == "story":
        return f"""[Intro]
{motif}

[Verse]
{v1}

[Pre-Chorus]
{hook_block}

[Chorus]
{hook_block}
{motif}

[Verse]
{v2}

[Chorus]
{hook_block}
{motif}

[Bridge]
{br or motif}

[Chorus]
{hook_block}
{motif}

[Outro]
{motif}
(soft natural fade)
"""

    if shape == "soft":
        return f"""[Intro]
{motif}

[Hook]
{hook_block}
{motif}

[Verse]
{v1}

[Hook]
{hook_block}
{motif}

[Verse]
{v2}

[Break]
(oud / kick echo of: {motif})

[Hook]
{hook_block}

[Outro]
{motif}
(soft natural fade)
"""

    # Default phrase shape — motif returns often for replay addiction.
    return f"""[Intro]
{motif}

[Hook]
{hook_block}
{motif}

[Verse]
{v1}

[Chorus]
{hook_block}
{motif}
{motif}

[Verse]
{v2}

[Chorus]
{hook_block}
{motif}
{motif}

[Break]
(oud echoes motif: {motif})

[Chorus]
{hook_block}
{motif}

[Outro]
{motif}
(soft natural fade)
"""


def build_signature_payload(
    *,
    hook: str,
    slug: str,
    lyrics: str,
    seed: int,
    bpm: int = SIGNATURE_BPM,
    key: str = SIGNATURE_KEY,
    duration: int = SIGNATURE_DURATION,
    color_note: str = "",
    motif_note: str = "",
    grid_lock: bool = True,
) -> dict[str, Any]:
    """Build the locked HAYA signature text2music payload.

    Args:
        hook: Primary Arabic earworm phrase (unique — not ``Name Name``).
        slug: Song folder / id.
        lyrics: From ``build_signature_lyrics`` (preferred) or simple lyrics.
        seed: Fixed seed (no random).
        bpm: Tempo (default 110).
        key: Key scale (default A minor).
        duration: Seconds (60 on Mac; raise when VRAM allows).
        color_note: Optional within-lane color (defaults to Rima intimate color).
        motif_note: What the addictive signature motif IS for this song
            (e.g. sticky oud 3-note lick, vocal phrase contour, kick figure).
        grid_lock: If True, force hook syllables onto the kick grid.

    Returns:
        ACE-Step ``/release_task`` body with thinking LM + Rima open + earworm.
    """
    payload = build_text2music_payload(
        hook=hook,
        slug=slug,
        lyrics=lyrics,
        seed=seed,
        thinking=True,
        duration=duration,
        bpm=bpm,
        key=key,
    )
    payload["batch_size"] = 1
    payload["model"] = SIGNATURE_MODEL
    payload["lm_model_path"] = SIGNATURE_LM
    color_text = color_note.strip() or RIMA_COLOR
    color = f" COLOR: {color_text}"
    motif = (
        f" THIS SONG'S SIGNATURE MOTIF: {motif_note.strip()}"
        if motif_note.strip()
        else f" THIS SONG'S SIGNATURE MOTIF: sticky vocal phrase '{hook}'"
    )
    grid = f" {VOCAL_GRID_LOCK}" if grid_lock else ""
    payload["prompt"] = (
        f"{payload['prompt']} {ORGANIC_PRODUCTION} {NIGHT_DRIVE_SPICE} "
        f"{RIMA_ARRANGEMENT} {EARWORM_MOTIF} {HOOK_VARIETY}{grid}{motif}{color}"
    )
    payload["instruction"] = (
        f"{payload['instruction']} Sound like a real human recording. "
        f"Apply: {RIMA_ARRANGEMENT} {NIGHT_DRIVE_SPICE} {EARWORM_MOTIF} "
        f"{HOOK_VARIETY}{grid}{motif}{color} "
        "Open with a SHORT soft female hum/vocal (~4–8s, light pad only) — "
        f"main beat by 8 seconds — then sing hook '{hook}' ON the kick grid "
        "in every chorus, break, and outro. "
        "Each syllable locked to the beat — no rushing the name off-rhythm. "
        "Reject synthetic/AI/robotic/off-beat production."
    )
    payload["lm_negative_prompt"] = SIGNATURE_NEGATIVE
    if grid_lock:
        # Slightly stronger guidance helps keep Arabic syllables on grid.
        payload["guidance_scale"] = 15.0
        payload["lm_cfg_scale"] = 3.5
    return payload


def master_signature_mp3(raw: Path, *, slug: str, bpm: int = SIGNATURE_BPM) -> tuple[Path, float]:
    """Organic distribute master + stealth harden → ``{slug}_human.mp3``.

    Args:
        raw: Fresh ACE-Step MP3.
        slug: Song id for output names / stealth seed.
        bpm: Tempo hint for humanize.

    Returns:
        (listen_path, ai_probability). ``{slug}_upload.mp3`` is a copy of human.
    """
    out_dir = raw.parent
    pre = out_dir / f"{slug}_prehuman.mp3"
    listen = out_dir / f"{slug}_human.mp3"
    upload = out_dir / f"{slug}_upload.mp3"
    humanize_mp3(raw, pre, style="distribute", bpm=bpm)
    _path, _rate, ai_prob = harden_for_upload(pre, listen, name=slug)
    upload.write_bytes(listen.read_bytes())
    pre.unlink(missing_ok=True)
    return listen, float(ai_prob)


__all__ = [
    "EARWORM_MOTIF",
    "HOOK_VARIETY",
    "NIGHT_DRIVE_SPICE",
    "ORGANIC_PRODUCTION",
    "RIMA_ARRANGEMENT",
    "RIMA_COLOR",
    "SIGNATURE_BPM",
    "SIGNATURE_DURATION",
    "SIGNATURE_KEY",
    "SIGNATURE_LM",
    "VOCAL_GRID_LOCK",
    "build_signature_lyrics",
    "build_signature_payload",
    "build_simple_lyrics",
    "master_signature_mp3",
]
