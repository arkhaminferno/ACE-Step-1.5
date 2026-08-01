"""FerdausMix-inspired song structure templates for HAYA / ACE-Step.

Derived from audio analysis of FerdausMix channel (vocal entry ~5s,
bass drop ~24s, chorus lifts ~50–95s). See research/ferdaus_mix/SONG_STRUCTURE.md.
"""

from __future__ import annotations

# FerdausMix lane: slightly slower, darker than Valessa.
FERDAUS_BPM = 108
FERDAUS_KEY = "D minor"

FERDAUS_MOOD = (
    "dark Arabic deep chill house, emotional night drive, cinematic, hypnotic, "
    "lonely but beautiful, oriental melody, warm sub bass"
)

FERDAUS_VOCAL = (
    "ONE real young Arabic woman singing live in studio — warm breath, "
    "natural vibrato, soft human consonants, intimate close-mic. "
    "Syllables ON the four-on-floor kick. Sounds human, NOT robotic/TTS/vocoder. "
    "Never male, never choir, never English-accent Arabic"
)

FERDAUS_INSTRUMENTS = (
    "four-on-the-floor kick (filtered then full at drop), sidechained warm sub bass, "
    "offbeat hats, lush dark pads, filtered chord stabs, sparse dry oud reply, "
    "NO brass, NO guzheng, NO pipa"
)

# Full ~3:45 map (target when duration allows).
FERDAUS_ARRANGEMENT_LONG = """
0:00-0:05 HOOK TEASER — female Arabic vocal hook audible immediately, no silence
0:05-0:20 INTRO BUILD — hook repeats, filtered kick, pads swell, sub NOT full yet
0:20-0:25 BASS DROP — full kick + sub together, groove locks
0:25-0:45 VERSE 1 — real Arabic story lyrics, intimate
0:45-0:55 PRE-CHORUS — rising 2 lines, tension
0:55-1:15 CHORUS 1 — title hook repeated 4x, full energy lift
1:15-1:35 VERSE 2 — new lyrics, same groove
1:35-1:55 CHORUS 2 — identical hook and lift to chorus 1
1:55-2:15 BREAKDOWN — strip to kick + vocal ad-lib or oud
2:15-2:35 CHORUS 3 FINAL — biggest emotional peak
2:35-3:30 OUTRO — hook fragment, soft natural fade
"""

# Compressed ~2:00 map for ACE-Step default duration.
FERDAUS_ARRANGEMENT_120S = """
0:00-0:05 HOOK TEASER — vocal hook NOW
0:05-0:18 INTRO BUILD — hook ×2, filtered groove
0:18-0:22 BASS DROP — kick + sub arrive
0:22-0:38 VERSE 1
0:38-0:45 PRE-CHORUS
0:45-0:58 CHORUS 1 — hook ×4
0:58-1:10 VERSE 2
1:10-1:22 CHORUS 2
1:22-1:32 BREAKDOWN — 4 bars
1:32-1:48 FINAL CHORUS
1:48-2:00 OUTRO fade
"""


def build_ferdaus_prompt(*, hook: str, slug: str = "", duration_sec: int = 120) -> str:
    """Build ACE-Step caption prompt with FerdausMix structure."""
    arrangement = FERDAUS_ARRANGEMENT_120S if duration_sec <= 150 else FERDAUS_ARRANGEMENT_LONG
    title = f" '{slug}'" if slug else ""
    return (
        f"Arabic deep chill house for HAYA{title}. {FERDAUS_MOOD}. "
        f"{FERDAUS_VOCAL}. {FERDAUS_INSTRUMENTS}. "
        f"Memorable hook = {hook}. Tempo {FERDAUS_BPM} BPM, key {FERDAUS_KEY}. "
        f"STRUCTURE (mandatory):{arrangement}"
    ).strip()


def build_ferdaus_instruction(*, hook: str) -> str:
    """Build ACE-Step instruction emphasizing FerdausMix entry + drops."""
    return (
        "Generate ONE complete Arabic deep chill house song. "
        "CRITICAL STRUCTURE: (1) Hook vocal in first 3 seconds — listener hooked immediately. "
        "(2) Bass drop ~18-25s — full kick+sub together. "
        "(3) Real Arabic verses with story — NOT hook-only. "
        f"(4) Identical chorus hook '{hook}' at least 3 times with energy lift each time. "
        "(5) Breakdown before final chorus. (6) Soft outro fade. "
        f"CRITICAL VOCAL: {FERDAUS_VOCAL}. "
        f"Lock {FERDAUS_BPM} BPM and {FERDAUS_KEY}. Reject male vocals and brass."
    )


def build_ferdaus_lyrics(*, hook: str, verse1: list[str], verse2: list[str], pre_chorus: list[str]) -> str:
    """Format lyrics with FerdausMix section flow for ACE-Step."""
    v1 = "\n".join(verse1)
    v2 = "\n".join(verse2)
    pre = "\n".join(pre_chorus)
    chorus = "\n".join([hook] * 4)
    return f"""[Hook]
{hook}

[Intro]
{hook}
{hook}
(filtered groove building — bass drop coming)

[Verse]
{v1}

[Pre-Chorus]
{pre}

[Chorus]
{chorus}

[Verse]
{v2}

[Chorus]
{chorus}

[Break]
(vocal ad-lib over kick — 4 bars, emotional)

[Chorus]
{chorus}

[Outro]
{hook}
(soft natural fade)
"""
