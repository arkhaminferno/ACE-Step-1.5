"""Recipe 3 leads — DEPRECATED. Use ``haya_recipe4_leads`` (no piano)."""

from __future__ import annotations

# lead_id → prompt lock + lyric stage + ban. Optional section map for trio form.
LEAD_SPECS: dict[str, dict[str, str]] = {
    "oud": {
        "label": "dry acoustic oud",
        "lock": (
            "LEAD LOCK — DRY ACOUSTIC OUD (MANDATORY): solo plucked wooden oud, "
            "warm mid-body, clear close-mic. Instrumental choruses: oud is the "
            "STAR (memorable 3–6 note motif ON the kick). NOT guzheng/pipa, "
            "NOT ney solo, NOT piano lead, NOT piercing high squeals."
        ),
        "stage": "sticky dry acoustic oud motif ON the kick — warm wooden plucks",
        "ban": ", ney lead, qanun lead, piano lead, guzheng, pipa",
    },
    "ney": {
        "label": "airy ney flute",
        "lock": (
            "LEAD LOCK — NEY (MANDATORY): solo breathy Arabic ney flute, airy "
            "night color, soft sustain ON the kick pocket. Instrumental choruses: "
            "ney is the STAR motif. Sparse only — no busy runs. "
            "NOT saxophone, NOT bright synth lead, NOT guzheng, NOT loud oud solo."
        ),
        "stage": "airy ney flute motif ON the kick — soft breathy night phrases",
        "ban": ", saxophone, trumpet, guzheng, pipa, loud oud lead, piano lead",
    },
    "qanun": {
        "label": "sparse qanun",
        "lock": (
            "LEAD LOCK — SPARSE QANUN (MANDATORY): classical Arabic qanun, "
            "sparkling short arpeggios ON the kick, sparse not busy. "
            "Instrumental choruses: qanun is the STAR. "
            "CRITICAL: real qanun timbre — NOT Chinese guzheng, NOT pipa."
        ),
        "stage": "sparse sparkling qanun arpeggios ON the kick — Arabic qanun only",
        "ban": ", guzheng, pipa, Chinese zither, harp wall, oud lead, ney lead",
    },
    "piano_oud": {
        "label": "soft piano + oud answer",
        "lock": (
            "LEAD LOCK — SOFT PIANO + OUD ANSWER (MANDATORY): intimate soft "
            "piano first; dry oud answers in gaps ON the kick. "
            "NOT loud concert piano, NOT guzheng, NOT brass."
        ),
        "stage": "soft piano then dry oud answer ON the kick — dialogue",
        "ban": ", loud concert piano, guzheng, pipa, brass, ney lead, qanun lead",
    },
    # Driving soft piano lead — still 108 BPM but clear pulse (not ballad-slow).
    "piano": {
        "label": "rhythmic soft piano",
        "lock": (
            "LEAD LOCK — RHYTHMIC SOFT PIANO ON-GRID (MANDATORY): soft piano STAR. "
            "EVERY piano chord and melody note lands ON the kick or even eighth "
            "at 108 BPM — quantized house pocket, same grid as the kick/sub. "
            "No rubato piano, no floating free-time chords over the beat. "
            "Female vocal syllables also ON that same kick grid. "
            "Kick by ~5s; warm sub pumps with kick. "
            "Driving night-drive — NOT ballad, NOT ambient drift, NOT beat-only "
            "with loose instruments. Optional tiny oud dust in gaps only. "
            "NOT loud concert piano, NOT guzheng, NOT brass, NOT ney solo."
        ),
        "stage": (
            "rhythmic soft piano ON every kick/eighth — vocal+piano+kick one pocket"
        ),
        "ban": (
            ", slow ballad, ambient drift, empty sparse bars, off-grid piano, "
            "rubato piano, floating chords, off-beat vocals, beat-only mix, "
            "loud concert piano, guzheng, pipa, brass, ney lead, qanun lead"
        ),
    },
    # Default Recipe3 blend: one voice per role — never all three at once.
    "piano_oud_ney": {
        "label": "soft piano intro + oud chorus + ney color",
        "lock": (
            "LEAD MAP (MANDATORY — one lead role per section, never stack all 3): "
            "(1) INTRO: soft intimate piano only under female hum — no oud/ney yet. "
            "(2) INSTRUMENTAL CHORUS: dry acoustic oud is the STAR motif ON the kick "
            "(warm mid-body wooden plucks) — piano drops to dust or silence; no ney. "
            "(3) VERSES: soft piano bed under vocal; oud may answer only in gaps. "
            "(4) BREAK / late color / OUTRO: sparse airy ney flute ON the pocket — "
            "brief, breathy; oud rests; piano very soft or out. "
            "Density: max one melodic lead at a time. "
            "NOT guzheng/pipa, NOT sax, NOT brass, NOT busy qanun, NOT loud piano."
        ),
        "stage": "section-mapped: piano intro → oud chorus → ney outro color",
        "ban": (
            ", guzheng, pipa, saxophone, trumpet, brass, qanun spam, "
            "all three leads at once, busy stacked melodies, loud concert piano"
        ),
    },
}


def resolve_lead(lead: str) -> dict[str, str]:
    """Return lead spec or raise for unknown id."""
    key = lead.strip().lower().replace("+", "_").replace("-", "_")
    aliases = {
        "piano+oud": "piano_oud",
        "trio": "piano_oud_ney",
        "piano_oud_ney_trio": "piano_oud_ney",
    }
    key = aliases.get(key, key)
    if key not in LEAD_SPECS:
        raise ValueError(f"Unknown lead {lead!r}. Choose: {sorted(LEAD_SPECS)}")
    return LEAD_SPECS[key]


def build_lead_lyrics_body(
    *, hook: str, verse1: str, verse2: str, lead: str
) -> str:
    """Return full structured lyrics for the given lead."""
    key = lead.strip().lower().replace("+", "_").replace("-", "_")
    if key in ("trio", "piano_oud_ney"):
        return f"""[Intro]
(soft female hum mmm ~4–8s — SOFT intimate piano only, almost no kick)
(kick enters by 8 seconds — piano still soft; no oud/ney yet)

[Instrumental Chorus]
(DRY ACOUSTIC OUD star motif ON the kick + warm sub — FULLY INSTRUMENTAL)
(piano out or dust only — no ney — oud is the heartbeat)

[Verse]
{verse1}
(soft piano bed under vocal; oud answers only in gaps ON the kick)

[Instrumental Chorus]
(oud motif bigger ON the kick — still NO vocal — piano dust; no ney)

[Vocal Chorus]
{hook}
{hook}
(ONLY two short on-kick hits — then leave the oud motif alone)

[Verse]
{verse2}
(soft piano under vocal; tiny oud gap-answers only)

[Instrumental Chorus]
(LONG oud instrumental chorus — main replay reason — ON every kick)
(near end: brief airy NEY answers in gaps — oud still lead; never stack loud)

[Vocal Chorus]
{hook}
{hook}
(last two short hits — TOTAL ≤4 — then silence)

[Instrumental Chorus]
(oud motif returns; soft NEY color phrase — one at a time)

[Outro]
(sparse airy ney + fading soft piano — oud rests — soft natural fade)
"""
    stage = resolve_lead(lead)["stage"]
    return f"""[Intro]
(soft female hum mmm ~4–8s — light pad, almost no kick)
(kick enters by 8 seconds — tease lead motif)

[Instrumental Chorus]
({stage} + warm sub — FULLY INSTRUMENTAL — song heartbeat)

[Verse]
{verse1}

[Instrumental Chorus]
(same motif bigger ON the kick — still NO vocal — lead upfront)

[Vocal Chorus]
{hook}
{hook}
(ONLY two short on-kick hits — then leave the motif alone)

[Verse]
{verse2}

[Instrumental Chorus]
(LONG instrumental chorus — main replay reason)
({stage})

[Vocal Chorus]
{hook}
{hook}
(last two short hits — TOTAL ≤4 — then silence)

[Instrumental Chorus]
(motif returns alone — no vocal)

[Outro]
(instrumental motif soft fade — no singing)
"""
