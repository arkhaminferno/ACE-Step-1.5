"""Fixed HAYA artist sound bible — Valessa-style deep house + natural Arabic vocal.

Instrumental groove = commercial melodic deep house.
Vocal pass = real sung hook locked to key, BPM, and kick grid.
"""

from __future__ import annotations

# Locked production targets (Valessa lane: 120–125).
HAYA_BPM = 122
HAYA_KEY = "D minor"

# Real singer — avoid chop/sample/TTS cues that push robotic vocals.
VOCAL_PERSONA = (
    "Real young Arabic woman singing live in a studio, "
    "warm human voice with natural breath and slight vibrato, "
    "clear Arabic diction, intimate close-mic, emotional but controlled — "
    "every syllable ON the four-on-floor kick, melody in key — "
    "sounds like a real person singing live, NOT AI, NOT TTS, NOT vocoder, "
    "NOT robotic, NOT Auto-Tune chipmunk, NOT pitched sample chops"
)

INSTRUMENT_PALETTE = (
    "four-on-the-floor deep kick every beat, clap/snare on 2 and 4, "
    "syncopated offbeat hi-hats with slight swing, warm analog sub bass sidechained to kick, "
    "filtered electric-piano / chord stabs, lush atmospheric pads with medium hall reverb, "
    "soft pluck, subtle dry oud only as sparse reply, rare ney fill, "
    "tiny darbuka texture — spacious, NOT busy"
)

# Dance-pop deep-house pocket (Thrace/Delina-lane groove feel — not a clone).
DELINA_LANE_PALETTE = (
    "punchy four-on-the-floor club kick, layered clap on beats 2 and 4, "
    "swung offbeat open hats, groovy bouncing sidechained bass, "
    "filtered dance-pop chord stabs, wide atmospheric pads, "
    "subtle pluck ear-candy, sparse dry oud reply only — clean modern deep house"
)

STRUCTURED_INSTRUMENTAL = """Genre:
Melodic Deep House / Commercial Deep House

Mood:
Warm, hypnotic, soulful, elegant, late-night drive, atmospheric

Energy:
Medium

Tempo:
{bpm} BPM

Vocals:
No vocals. Instrumental only.

Instruments:
{instruments}

Arrangement:
FULL SHORT SONG (~120s). Kick in by 4s. Room for verse + chorus + bridge.
intro → verse → pre → chorus → verse → chorus → bridge → chorus → out.
NOT hook-only — leave space for storytelling vocals.

Production:
Clean punchy low end, mono bass, wide pads, medium sidechain pumping, 
crisp hats, modern club mix, Spotify quality, Valessa-style deep house instrumental
"""

STRUCTURED_VOCAL = """Genre:
Melodic Deep House / Commercial Deep House

Mood:
Warm, hypnotic, soulful, elegant, late-night drive

Energy:
Medium

Tempo:
{bpm} BPM

Key:
{key} — every sung note must sit in this key / scale (chord tones and scale tones only)

Vocals:
{persona}
KEEP THE EXISTING INSTRUMENTAL GROOVE intact (kick, bass, hats, chord stabs, pads).
Add ONE lead female vocal singing a simple melodic hook ON THE BEAT.
Phrases start on the kick / downbeat. Syllables land with the groove — not ahead, not late.
Melody is in tune with the chords (D minor). Same short phrase, natural human delivery.
Light plate reverb only. Dry-present lead. No male vocal. No choir. No opera.

Instruments:
Preserve the deep-house instrumental. Do not rewrite drums or bass.
Oud only answers in gaps when the singer pauses.

Arrangement:
FULL SONG. 0:00–0:08 groove intro, 0:08 Verse 1 with real lyric lines (not just the hook),
0:25 Pre-Chorus, 0:35 Chorus hook, 0:50 Verse 2 new lines, 1:05 Chorus,
1:20 Bridge, 1:35 final Chorus, clean end by ~2:00.
MUST sing verses with different words/melody than the chorus. NOT hook-only.

Production:
Vocal always in front. Pitch-perfect to the track. Timing locked to 4/4 kick.
Spacious stereo. Commercial deep house. Natural human vocal take.
"""


def instrumental_prompt(
    *,
    bpm: int = HAYA_BPM,
    instruments: str | None = None,
) -> str:
    """Sectioned prompt for instrumental-only generation."""
    return STRUCTURED_INSTRUMENTAL.format(
        bpm=bpm,
        instruments=instruments or INSTRUMENT_PALETTE,
    ).strip()


def vocal_prompt(
    *,
    bpm: int = HAYA_BPM,
    key: str = HAYA_KEY,
    hook: str = "",
    instruments: str | None = None,
) -> str:
    """Sectioned prompt for vocal pass over a locked groove."""
    body = STRUCTURED_VOCAL.format(
        bpm=bpm,
        key=key,
        persona=VOCAL_PERSONA,
        instruments=instruments or INSTRUMENT_PALETTE,
    ).strip()
    if hook:
        body += (
            f"\n\nCore sung hook (in {key}, on the beat): {hook}\n"
            f"Sing '{hook}' as a real melodic line — few notes, in tune, "
            f"syllables on the kick grid. Human performance, not a sample loop."
        )
    return body


def vocal_instruction(*, hook: str, key: str = HAYA_KEY) -> str:
    """Short instruction for the vocal cover pass — natural pitch + timing."""
    return (
        "CRITICAL: preserve the source instrumental groove "
        "(kick, bass, hats, chord stabs, sidechain). "
        f"Only ADD {VOCAL_PERSONA}. "
        "FULL vocal song: sing Verse 1 with real lyric lines first, then Pre-Chorus, "
        f"then Chorus hook '{hook}', then Verse 2 with NEW lines, Bridge, final Chorus. "
        "Do NOT make a hook-only track — verses must have different words and melody. "
        f"Pitch MUST match {key}. Timing locked to the four-on-floor kick. "
        "Natural human singing; reject robotic/TTS/vocoder/sample-chop vocals. "
        "Vocal centered and louder than pads. Clean ending."
    )


def palette_for_slug(slug: str = "") -> str:
    """Return instrument palette for a song slug."""
    if (slug or "").strip().lower() == "gharib":
        return DELINA_LANE_PALETTE
    return INSTRUMENT_PALETTE

