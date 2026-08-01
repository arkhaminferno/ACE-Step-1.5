"""Zeina v2 — keep afro deep-house beat lane, add denser Arabic singing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.natural_vocal_recipe import (
    BEAT_LOCK,
    DEFAULT_GUIDANCE,
    DEFAULT_KEY,
    DEFAULT_LM_CFG,
    DEFAULT_MODEL,
    DEFAULT_STEPS,
    HUMAN_VOCAL,
    SHORT_NEGATIVE,
)

API_BASE = "http://127.0.0.1:8001"
OUT_DIR = Path("/Users/infy/Downloads/ACE-Step-1.5/batch_deephouse/output/zeina")
SLUG = "zeina"
TITLE = "Zeina"
HOOK = "زينة زينة"
SEED = 88217
BPM = 108
DURATION = 60

# Richer lyric map — more sung lines, less empty instrumental space.
LYRICS = f"""[Hook]
{HOOK}
{HOOK}
يا زينة يا زينة
{HOOK}

[Verse]
زينة في عينيّا
تمشي مع دقات القلب
والليل يلفّني بلطف
وإنتِ في بالي دايماً
قرب لي شوية
خلّيني أسمع صوتك

[Pre-Chorus]
قوليلي بهدوء
ما تروحيش بعيد
اللحن بينا
يخلّيني أستنى

[Chorus]
{HOOK}
يا زينة لا تروحي
{HOOK}
قلبي بيناديلك
{HOOK}
خلّيكي هنا معايا
{HOOK}

[Verse]
كل نظرة منك
تسبّبني في الليل
والدنيا هادية حوالينا
ونبضي يمشي معاك
ارجعي لي بلطف
قبل ما يروح الفجر

[Chorus]
{HOOK}
يا زينة يا حبيبة
{HOOK}
قرب لي بهدوء
{HOOK}
ونظرة تبقيني
{HOOK}

[Bridge]
يا زينة… يا زينة
ما بينساك قلبي
لحن خفيف يلفّني
وباسمك أبقى هنا

[Outro]
{HOOK}
يا زينة
(soft natural fade)
"""

AFRO_PROMPT = (
    "Afro type beat x melodic deep house, Rema and Odeal romantic afro-R&B pocket, "
    "soft log drums, warm bouncing sub, gentle four-on-floor deep-house kick, "
    "syncopated afro hats, airy pads, melodic afro pluck — KEEP this groove feel. "
    "VOCAL-FORWARD REMAKE: song is mostly SUNG, not instrumental. "
    "Female Arabic lead sings almost continuously — hook, verses, pre-chorus, chorus, bridge. "
    "Clear dry PRESENT vocal upfront from 0–2s. Sparse instrumental breaks only. "
    f"HAYA song '{SLUG}'. MANDATORY VOCAL: {HUMAN_VOCAL} "
    f"MANDATORY TIMING: {BEAT_LOCK} "
    f"Hook = {HOOK}. Tempo {BPM} BPM. Key {DEFAULT_KEY}."
)

AFRO_INSTRUCTION = (
    "Remake as VOCAL-FORWARD afro deep-house. "
    f"CRITICAL VOCAL: {HUMAN_VOCAL} Sing most of the song — verses AND chorus. "
    f"CRITICAL TIMING: {BEAT_LOCK} "
    f"Sing hook '{HOOK}' often, plus full Arabic verse lines. "
    "Do NOT leave long instrumental-only sections. Soft fade out."
)

AFRO_NEGATIVE = (
    SHORT_NEGATIVE
    + ", instrumental-only, long intro without vocal, sparse singing, "
    "hook-only, mumbled Arabic, trap spam, brass, guzheng, pipa, male vocal"
)


def build_payload() -> dict[str, Any]:
    """Build vocal-forward text2music remake (same afro-deep-house lane)."""
    # text2music only — cover on low-RAM Mac often jetsams; keep beat style in prompt.
    return {
        "prompt": AFRO_PROMPT,
        "lyrics": LYRICS,
        "instruction": AFRO_INSTRUCTION,
        "thinking": False,
        "use_format": False,
        "use_cot_caption": False,
        "use_cot_language": False,
        "vocal_language": "ar",
        "audio_duration": DURATION,
        "bpm": BPM,
        "key_scale": DEFAULT_KEY,
        "inference_steps": DEFAULT_STEPS,
        "guidance_scale": DEFAULT_GUIDANCE,
        "lm_cfg_scale": DEFAULT_LM_CFG,
        "lm_negative_prompt": AFRO_NEGATIVE,
        "model": DEFAULT_MODEL,
        "use_random_seed": False,
        "task_type": "text2music",
        "seed": SEED,
        "audio_format": "mp3",
        "batch_size": 1,
    }


def main() -> None:
    """Generate Zeina v2 vocal-forward remake."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "lyrics.txt").write_text(LYRICS, encoding="utf-8")
    (OUT_DIR / "lyrics_v2.txt").write_text(LYRICS, encoding="utf-8")
    out_path = OUT_DIR / f"{SLUG}.mp3"
    payload = build_payload()
    mode = payload["task_type"]
    print(f"GENERATE {SLUG} v2 mode={mode} seed={SEED} duration={DURATION} vocal-forward")
    meta = generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=out_path,
        label=f"{SLUG}-v2",
    )
    info = {
        "title": TITLE,
        "slug": SLUG,
        "hook": HOOK,
        "bpm": BPM,
        "key_scale": DEFAULT_KEY,
        "duration_sec": DURATION,
        "version": "v2",
        "style": "Odeal x Rema afro deep house — vocal-forward remake",
        "task_type": mode,
        "engine": "ACE-Step acestep-v15-turbo",
        "thinking": False,
        "batch_size": 1,
        "seed": SEED,
        "task_id": meta["task_id"],
        "notes": "v1 archived in _v1/. Fuller lyrics + denser singing; same afro deep-house lane.",
    }
    (OUT_DIR / f"{SLUG}.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK {out_path}")


if __name__ == "__main__":
    main()
