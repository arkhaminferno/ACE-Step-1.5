"""HAYA Recipe 4 — feel-good Arabic deep house (dopamine / tarab design).

Replaces Recipe 3. Design goals from neurochemistry + maqam research:
  - Bright major-like maqamat (Rast / Bayati); Hijaz/Nahawand only in breaks
  - High-affect leads: qanun, violin, oud, santur (NO piano — muddies gens)
  - 108 BPM four-on-floor + light darbuka; slight hat swing
  - Call-and-response Arabic vocals (tarab / bonding)
  - Dry kick/bass; moderate verb + tempo-synced delay on leads
  - Instrumental "main chorus beat" drops are the replay earworm
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from batch_deephouse.haya_recipe4_leads import build_lead_lyrics_body, resolve_lead
from batch_deephouse.haya_signature_recipe import (
    NIGHT_DRIVE_SPICE,
    ORGANIC_PRODUCTION,
    SIGNATURE_LM,
    SIGNATURE_MODEL,
    build_signature_payload,
    master_signature_mp3,
)

RECIPE4_BPM = 108
# Bright tonal center — prompt also locks Maqam Rast/Bayati (not dark A minor).
RECIPE4_KEY = "C major"
RECIPE4_DURATION = 180
RECIPE4_LM = SIGNATURE_LM
RECIPE4_MODEL = SIGNATURE_MODEL
RECIPE4_DEFAULT_LEAD = "qanun_violin"
RECIPE4_REF_HOOK = "يا سماء"
RECIPE4_REF_ANSWER = "ويا قلبي"
RECIPE4_REF_SEED = 42001

MAQAM_LOCK = (
    "MAQAM (MANDATORY): bright joyful Maqam Rast or Bayati as home color — "
    "uplifting, noble, major-like. Occasional Hijaz or Nahawand only in "
    "breakdown/bridge for brief nostalgia, then resolve back to bright home."
)
GROOVE_LOCK = (
    "GROOVE (MANDATORY) at 108 BPM: solid four-on-floor kick is the clock; "
    "warm mono sub; light darbuka dum/tek dust (not spam). "
    "Slight swing (~60%) on hats/shakers only — kick/snare stay on grid. "
    "Moderate syncopation — hypnotic, not complex."
)
SOUND_DESIGN = (
    "SOUND DESIGN: dry punchy kick+bass (little reverb); short–medium room/hall "
    "on melodic leads and vocals (pre-delay ~20–30ms); tempo-synced dotted-8th "
    "or quarter delay at 108 BPM, low feedback on vocals; gentle tape saturation "
    "warmth on oud/qanun; NOT muddy, NOT harsh, NOT hyper-loud."
)
TARAB_VOCAL = (
    "TARAB VOCALS (MANDATORY): intimate female Arabic call-and-response — "
    "lead phrase then short answer chorus/reply. Syllables ON the kick. "
    "Short equal hits, light melisma only; joyful / mystical mood. "
    "NOT vocal spam covering the instrumental drop; NOT piano under vocal."
)
RECIPE4_ARRANGEMENT = (
    "RECIPE4 FORM (~180s): soft pad+motif intro~4–8s, kick by~8s; build with "
    "qanun/darbuka; INSTRUMENTAL main-chorus-beat drop (catchy lead motif); "
    "short verse; call-response chorus; breakdown (ney/oud color); bridge chant; "
    "drop reprise; final call-response; soft outro. Drops = replay reason."
)
RECIPE4_NEGATIVE = (
    ", piano, soft piano, concert piano, keys solo, dark A-minor ballad, "
    "depressing drone, vocal-only wall, hook spam every bar, choir wall, "
    "guzheng, pipa, brass, off-grid lead, rubato free-time, muddy reverb wash, "
    "harsh clipping, trap hats spam"
)


def build_recipe4_lyrics(
    *,
    hook: str,
    verse1: list[str],
    verse2: list[str],
    answer: str = "",
    lead: str = RECIPE4_DEFAULT_LEAD,
) -> str:
    """Build Recipe4 lyrics — call-response + instrumental drops.

    Args:
        hook: Arabic call phrase (sticky).
        verse1: First verse lines (max 4 used).
        verse2: Second verse lines (max 4 used).
        answer: Response phrase; defaults to a short echo of ``hook``.
        lead: Lead id from ``haya_recipe4_leads``.

    Returns:
        Tagged lyrics string for ACE-Step.
    """
    resolve_lead(lead)
    reply = (answer or hook).strip()
    return build_lead_lyrics_body(
        hook=hook,
        answer=reply,
        verse1="\n".join(verse1[:4]),
        verse2="\n".join(verse2[:4]),
        lead=lead,
    )


def build_recipe4_payload(
    *,
    hook: str,
    slug: str,
    lyrics: str,
    seed: int,
    bpm: int = RECIPE4_BPM,
    key: str = RECIPE4_KEY,
    duration: int = RECIPE4_DURATION,
    color_note: str = "",
    lead: str = RECIPE4_DEFAULT_LEAD,
    answer: str = "",
) -> dict[str, Any]:
    """Build Recipe 4 text2music payload (original song, not a HAYA cover)."""
    spec = resolve_lead(lead)
    reply = (answer or hook).strip()
    color = color_note.strip() or (
        f"Recipe4 feel-good — {spec['label']}; Rast/Bayati; call '{hook}' / '{reply}'"
    )
    heart = (
        f"MAIN CHORUS BEAT IS THE HEART: sticky {spec['label']} motif + warm sub "
        "+ four-on-floor as catchy INSTRUMENTAL drops (replay earworm)."
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
        motif_note=(
            f"instrumental {spec['label']} drop is the product; "
            f"call-response '{hook}' / '{reply}' on-kick"
        ),
        grid_lock=True,
    )
    # Brighter than signature night-drive — keep spice but tilt joyful.
    feel_good = (
        "FEEL-GOOD LANE: uplifting warm deep house — dopamine melodies, "
        "bright resonant timbres, steady groovy pulse, communal tarab energy. "
        "Still oriental deep house night-drive, but joyful not gloomy."
    )
    payload["prompt"] = (
        f"ORIGINAL Arabic deep chill house (NOT a remix/cover of any HAYA song), "
        f"{bpm} BPM, {key}, bright Maqam Rast/Bayati. FEMALE Arabic only. "
        f"NO PIANO. Soft pad intro, kick by ~8s. {MAQAM_LOCK} {GROOVE_LOCK} "
        f"{SOUND_DESIGN} {TARAB_VOCAL} {heart} {spec['lock']} "
        f"{ORGANIC_PRODUCTION} {feel_good} {NIGHT_DRIVE_SPICE} COLOR: {color}"
    )
    payload["instruction"] = (
        f"Generate brand-new ORIGINAL Recipe4 '{slug}' — do not clone Yalil, "
        f"Noor, Nafas, Rouh, Ward, Raya, or any prior HAYA track. "
        f"{RECIPE4_ARRANGEMENT} {MAQAM_LOCK} {GROOVE_LOCK} {heart} "
        f"{TARAB_VOCAL} {spec['lock']} NO PIANO. "
        f"Call '{hook}' answered by '{reply}' — short, on-kick, joyful."
    )
    payload["lm_negative_prompt"] = (
        payload["lm_negative_prompt"]
        + RECIPE4_NEGATIVE
        + spec["ban"]
        + ", Yalil clone, Nafas clone, Raya clone, remix of existing HAYA song"
    )
    payload["recipe"] = "haya_recipe4"
    payload["recipe4_lead"] = lead
    return payload


def master_recipe4_mp3(
    raw: Path, *, slug: str, bpm: int = RECIPE4_BPM
) -> tuple[Path, float]:
    """Distribute humanize + stealth master."""
    return master_signature_mp3(raw, slug=slug, bpm=bpm)


__all__ = [
    "GROOVE_LOCK",
    "MAQAM_LOCK",
    "RECIPE4_ARRANGEMENT",
    "RECIPE4_BPM",
    "RECIPE4_DEFAULT_LEAD",
    "RECIPE4_DURATION",
    "RECIPE4_KEY",
    "RECIPE4_REF_ANSWER",
    "RECIPE4_REF_HOOK",
    "RECIPE4_REF_SEED",
    "SOUND_DESIGN",
    "TARAB_VOCAL",
    "build_recipe4_lyrics",
    "build_recipe4_payload",
    "master_recipe4_mp3",
]
