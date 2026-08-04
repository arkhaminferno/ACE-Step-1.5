"""HAYA Recipe 3 — DEPRECATED. Use ``haya_recipe4`` instead.

Kept for old scripts/tests only. New songs: ``batch_deephouse.haya_recipe4``.

Legacy design (do not extend):
  - Soft female hum ~4–8s, groove by ~8s
  - Short Arabic verses + INSTRUMENTAL lead chorus as replay reason
  - Vocal hook only 2–4 short hits; ~180s night-drive deep house
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from batch_deephouse.haya_recipe3_leads import build_lead_lyrics_body, resolve_lead
from batch_deephouse.haya_signature_recipe import (
    NIGHT_DRIVE_SPICE,
    ORGANIC_PRODUCTION,
    RIMA_ARRANGEMENT,
    SIGNATURE_KEY,
    SIGNATURE_LM,
    SIGNATURE_MODEL,
    build_signature_payload,
    master_signature_mp3,
)

RECIPE3_BPM = 108
RECIPE3_KEY = SIGNATURE_KEY
RECIPE3_DURATION = 180
RECIPE3_LM = SIGNATURE_LM
RECIPE3_MODEL = SIGNATURE_MODEL
RECIPE3_MAX_VOCAL_HITS = 4
RECIPE3_REF_HOOK = "روح"
RECIPE3_REF_SEED = 81255

SPARSE_HOOK_RULE = (
    "SPARSE HOOK (MANDATORY): sing the Arabic chorus hook at most "
    f"{RECIPE3_MAX_VOCAL_HITS} short on-kick times in the ENTIRE song. "
    "Verses short; after 2–4 hook hits stay on instrumental motif."
)
RHYTHM_GRID_LOCK = (
    "RHYTHM GRID LOCK (MANDATORY) at 108 BPM: four-on-floor kick is the clock. "
    "Female Arabic vocal syllables AND lead notes land ON kick/even eighths — "
    "tight pocket, no rubato, no rushing/dragging the lyric off the beat."
)
RECIPE3_ARRANGEMENT = (
    "RECIPE3 FORM: hum intro~4–8s, kick by~8s; INSTRUMENTAL chorus; verse; "
    "inst chorus; 2 hook hits; verse2; LONG inst chorus; ≤2 hook hits; "
    "inst outro. Most runtime = instrumental; hook rare."
)
RECIPE3_NEGATIVE_BASE = (
    ", vocal-heavy, hook chanted many times, choir, vocal covering instrumental, "
    "off-grid lead, rubato, free-time, out of pocket rhythm, brass"
)


def build_recipe3_lyrics(
    *,
    hook: str,
    verse1: list[str],
    verse2: list[str],
    lead: str = "piano_oud_ney",
) -> str:
    """Recipe2 intro + verses + sparse hook + section-mapped instrumental leads."""
    resolve_lead(lead)  # validate early
    return build_lead_lyrics_body(
        hook=hook,
        verse1="\n".join(verse1[:4]),
        verse2="\n".join(verse2[:4]),
        lead=lead,
    )


def build_recipe3_payload(
    *,
    hook: str,
    slug: str,
    lyrics: str,
    seed: int,
    bpm: int = RECIPE3_BPM,
    key: str = RECIPE3_KEY,
    duration: int = RECIPE3_DURATION,
    color_note: str = "",
    lead: str = "piano_oud_ney",
) -> dict[str, Any]:
    """Build Recipe 3 payload for a lead variant (original song, not a cover)."""
    spec = resolve_lead(lead)
    color = color_note.strip() or (
        f"Recipe3 ORIGINAL — {spec['label']} instrumental heart; hook ≤4 hits"
    )
    heart = (
        f"INSTRUMENTAL CHORUS IS THE HEART: sticky {spec['label']} + warm sub + "
        "four-on-floor as FULL INSTRUMENTAL choruses (no singing there)."
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
            f"instrumental {spec['label']} chorus is the product; "
            f"sing '{hook}' ≤{RECIPE3_MAX_VOCAL_HITS} times total"
        ),
        grid_lock=True,
    )
    payload["prompt"] = (
        f"ORIGINAL Arabic deep chill house (NOT a remix/cover of any HAYA song), "
        f"{bpm} BPM, {key}. FEMALE Arabic only. Soft hum intro, kick by ~8s. "
        f"{RHYTHM_GRID_LOCK} {heart} {SPARSE_HOOK_RULE} {spec['lock']} "
        f"{RIMA_ARRANGEMENT} {ORGANIC_PRODUCTION} {NIGHT_DRIVE_SPICE} "
        f"COLOR: {color}"
    )
    payload["instruction"] = (
        f"Generate brand-new ORIGINAL Recipe3 '{slug}' — do not clone Yalil, "
        f"Noor, Nafas, Rouh, Ward, or any prior HAYA track. "
        f"{RECIPE3_ARRANGEMENT} {RHYTHM_GRID_LOCK} {heart} {SPARSE_HOOK_RULE} "
        f"{spec['lock']} Do NOT sing the hook in every chorus — instrumental "
        f"choruses have NO singing. Sing '{hook}' at most "
        f"{RECIPE3_MAX_VOCAL_HITS} short on-kick hits total."
    )
    payload["lm_negative_prompt"] = (
        payload["lm_negative_prompt"] + RECIPE3_NEGATIVE_BASE + spec["ban"]
        + ", Yalil clone, Nafas clone, remix of existing HAYA song"
    )
    payload["recipe"] = "haya_recipe3"
    payload["recipe3_lead"] = lead
    return payload


def master_recipe3_mp3(
    raw: Path, *, slug: str, bpm: int = RECIPE3_BPM
) -> tuple[Path, float]:
    """Distribute humanize + stealth master."""
    return master_signature_mp3(raw, slug=slug, bpm=bpm)


# Back-compat names used by older tests/scripts
INSTRUMENTAL_CHORUS_RULE = (
    "INSTRUMENTAL CHORUS IS THE HEART: sticky dry acoustic oud + warm sub"
)
OUD_GRID_LOCK = resolve_lead("oud")["lock"]

__all__ = [
    "INSTRUMENTAL_CHORUS_RULE",
    "OUD_GRID_LOCK",
    "RECIPE3_ARRANGEMENT",
    "RECIPE3_BPM",
    "RECIPE3_DURATION",
    "RECIPE3_KEY",
    "RECIPE3_MAX_VOCAL_HITS",
    "RECIPE3_REF_HOOK",
    "RECIPE3_REF_SEED",
    "RHYTHM_GRID_LOCK",
    "SPARSE_HOOK_RULE",
    "build_recipe3_lyrics",
    "build_recipe3_payload",
    "master_recipe3_mp3",
]
