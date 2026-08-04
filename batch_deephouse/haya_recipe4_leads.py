"""Recipe 4 lead variants — bright feel-good timbres (no piano).

Priority by positive affect (research): qanun > violin > oud > santur > ney.
"""

from __future__ import annotations

# lead_id → prompt lock + lyric stage + ban. No piano — it muddied gens.
LEAD_SPECS: dict[str, dict[str, str]] = {
    "qanun": {
        "label": "sparkling qanun",
        "lock": (
            "LEAD LOCK — QANUN STAR (MANDATORY): classical Arabic qanun, "
            "bright harp-like plucked arpeggios ON the kick pocket. "
            "Main chorus motif = short memorable qanun phrase. "
            "CRITICAL: real qanun — NOT guzheng, NOT pipa, NOT piano."
        ),
        "stage": "sparkling qanun arpeggio motif ON the kick — bright Arabic qanun",
        "ban": ", piano, guzheng, pipa, Chinese zither, harp wall, loud ney solo",
    },
    "violin": {
        "label": "bright Arabic violin",
        "lock": (
            "LEAD LOCK — VIOLIN STAR (MANDATORY): warm bright solo violin "
            "(Arabic-style legato, slight slides), lyrical ON the kick. "
            "Main chorus motif = catchy violin hook. "
            "NOT erhu, NOT harsh screech, NOT piano, NOT brass."
        ),
        "stage": "bright violin melodic hook ON the kick — warm legato",
        "ban": ", piano, erhu, brass, saxophone, guzheng, busy qanun spam",
    },
    "oud": {
        "label": "warm dry oud",
        "lock": (
            "LEAD LOCK — DRY OUD (MANDATORY): solo plucked wooden oud, "
            "warm mid-body, clear close-mic, motif ON the kick. "
            "Nostalgic support or star when chosen. NOT piano, NOT guzheng."
        ),
        "stage": "warm dry oud motif ON the kick — wooden plucks",
        "ban": ", piano, guzheng, pipa, brass, piercing high squeals",
    },
    "santur": {
        "label": "bright santur",
        "lock": (
            "LEAD LOCK — SANTUR (MANDATORY): sparkling hammered santur "
            "rhythmic motif or short double-time sparkle ON the pocket. "
            "NOT piano, NOT guzheng, NOT busy wall of hits."
        ),
        "stage": "bright santur rhythmic sparkle ON the kick",
        "ban": ", piano, guzheng, pipa, harp wall, loud ney solo",
    },
    "ney": {
        "label": "airy ney fills",
        "lock": (
            "LEAD LOCK — SPARSE NEY (MANDATORY): breathy Arabic ney flute "
            "as sparse fills/breakdown color only — airy, not busy. "
            "NOT saxophone, NOT piano, NOT continuous solo over full drop."
        ),
        "stage": "airy ney flute sparse fills ON the pocket",
        "ban": ", saxophone, piano, trumpet, continuous ney solo, guzheng",
    },
    # Default Recipe4 blend: qanun motif + violin counter (highest affect).
    "qanun_violin": {
        "label": "qanun motif + violin counter",
        "lock": (
            "LEAD MAP (MANDATORY — one melodic star at a time): "
            "(1) INTRO/BUILD: sparkling qanun arpeggio establishes maqam. "
            "(2) MAIN DROP / CHORUS BEAT: bright violin plays the catchy hook; "
            "qanun may double lightly or rest. "
            "(3) BREAKDOWN: sparse airy ney OR dry oud nostalgia — not both loud. "
            "(4) DROP REPRISE: violin hook returns; optional qanun sparkle in gaps. "
            "Max one loud melodic lead at a time. NO PIANO anywhere."
        ),
        "stage": "section-mapped: qanun build → violin chorus hook → ney/oud break",
        "ban": (
            ", piano, soft piano, concert piano, keys solo, guzheng, pipa, "
            "brass, all leads stacked loud, busy melody pile-up"
        ),
    },
}


def resolve_lead(lead: str) -> dict[str, str]:
    """Return lead spec or raise for unknown id."""
    key = lead.strip().lower().replace("+", "_").replace("-", "_")
    aliases = {
        "qanun+violin": "qanun_violin",
        "default": "qanun_violin",
        "feelgood": "qanun_violin",
    }
    key = aliases.get(key, key)
    if key not in LEAD_SPECS:
        raise ValueError(f"Unknown lead {lead!r}. Choose: {sorted(LEAD_SPECS)}")
    return LEAD_SPECS[key]


def build_lead_lyrics_body(
    *,
    hook: str,
    answer: str,
    verse1: str,
    verse2: str,
    lead: str,
) -> str:
    """Return Recipe4 lyrics: feel-good form + call-and-response tarab."""
    stage = resolve_lead(lead)["stage"]
    key = lead.strip().lower().replace("+", "_").replace("-", "_")
    if key in ("qanun_violin", "default", "feelgood", "qanun+violin"):
        lead_intro = "sparkling qanun arpeggio ON the kick — establish bright maqam"
        lead_drop = "bright VIOLIN catchy hook ON the kick — main chorus beat"
        lead_break = "sparse airy ney OR warm oud nostalgia — one voice only"
        lead_drop2 = "violin hook reprise; qanun sparkle in gaps only"
    else:
        lead_intro = f"tease: {stage}"
        lead_drop = f"{stage} — MAIN CHORUS BEAT (instrumental heart)"
        lead_break = "strip drums; sparse melodic fill only"
        lead_drop2 = f"{stage} — bigger reprise"

    return f"""[Intro]
(soft pad + subtle bass ~4–8s — almost no kick)
({lead_intro})
(kick enters by 8 seconds — four-on-floor + warm sub; slight swing on hats)

[Build]
(darbuka tek dust + qanun/lead arpeggio growing — still bright)

[Instrumental Drop]
({lead_drop} + warm sub + darbuka doubling kick — FULLY catchy)

[Verse]
{verse1}
(female Arabic, on-kick; soft call energy)

[Chorus]
{hook}
{answer}
{hook}
{answer}
(CALL-AND-RESPONSE tarab — short equal hits ON the kick — joyful)

[Breakdown]
({lead_break} — kick soft or out — emotional contrast)

[Bridge]
{hook}
{answer}
(chant call-response over light darbuka — bonding / oxytocin feel)

[Instrumental Drop]
({lead_drop2} — MAIN CHORUS BEAT returns — replay reason)

[Chorus]
{hook}
{answer}
{hook}
(last call-response — stay short, on-grid, uplifting)

[Outro]
(pad + ghost of motif — soft natural fade — no piano)
"""


__all__ = ["LEAD_SPECS", "build_lead_lyrics_body", "resolve_lead"]
