"""Generate 'Dalia' — groovy afro deep-house + Arabic girl vocal (fresh take)."""

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
    build_simple_lyrics,
)

API_BASE = "http://127.0.0.1:8001"
OUT_DIR = Path("/Users/infy/Downloads/ACE-Step-1.5/batch_deephouse/output/dalia")
SLUG = "dalia"
TITLE = "Dalia"
HOOK = "داليا داليا"
SEED = 90441
BPM = 110
DURATION = 60

LYRICS = build_simple_lyrics(
    hook=HOOK,
    verse1=[
        "داليا في بالي الليلة",
        "تمشي على الإيقاع",
        "والدقات ناعمة",
        "وإنتِ بترقصيني",
    ],
    verse2=[
        "قرب لي شوية",
        "يا داليا بهدوء",
        "واللحن يلفّني",
        "ونظرة تخلّيني",
    ],
)

PROMPT = (
    "GROOVY afro deep house banger — bounce like Rema, smooth like Odeal, "
    "four-on-floor deep kick, warm rubbery bassline, swung hats, soft percussion, "
    "catchy melodic synth pluck, night-club but chill, head-nod groove, "
    "spacious modern mix. NOT oriental oud lead, NOT trap, NOT brass. "
    f"HAYA song '{SLUG}'. MANDATORY VOCAL: {HUMAN_VOCAL} "
    f"MANDATORY TIMING: {BEAT_LOCK} "
    f"Sticky hook = {HOOK}. Groove + vocal from beat 1. "
    f"Tempo {BPM} BPM. Key {DEFAULT_KEY}. Soft fade."
)

INSTRUCTION = (
    "Generate ONE groovy afro deep-house song with Arabic female vocal. "
    f"CRITICAL VOCAL: {HUMAN_VOCAL} "
    f"CRITICAL TIMING: {BEAT_LOCK} "
    f"Sing '{HOOK}' on the groove at {BPM} BPM in {DEFAULT_KEY}. "
    "Danceable bounce. Hook first. Soft fade."
)

NEGATIVE = (
    SHORT_NEGATIVE
    + ", oud lead, oriental maqam solo, trap, amapiano spam, brass, "
    "guzheng, pipa, male vocal, stiff beat"
)


def build_payload() -> dict[str, Any]:
    """Build groovy text2music payload."""
    return {
        "prompt": PROMPT,
        "lyrics": LYRICS,
        "instruction": INSTRUCTION,
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
        "lm_negative_prompt": NEGATIVE,
        "model": DEFAULT_MODEL,
        "use_random_seed": False,
        "task_type": "text2music",
        "seed": SEED,
        "audio_format": "mp3",
        "batch_size": 1,
    }


def main() -> None:
    """Generate Dalia and write master + metadata."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "lyrics.txt").write_text(LYRICS, encoding="utf-8")
    out_path = OUT_DIR / f"{SLUG}.mp3"
    print(f"GENERATE {SLUG} groovy seed={SEED} bpm={BPM} duration={DURATION}")
    meta = generate_to_file(
        build_payload(),
        api_base=API_BASE,
        api_key="",
        out_path=out_path,
        label=SLUG,
    )
    info = {
        "title": TITLE,
        "slug": SLUG,
        "hook": HOOK,
        "bpm": BPM,
        "key_scale": DEFAULT_KEY,
        "duration_sec": DURATION,
        "style": "groovy afro deep house + Arabic girl vocal",
        "engine": "ACE-Step acestep-v15-turbo text2music",
        "thinking": False,
        "batch_size": 1,
        "seed": SEED,
        "task_id": meta["task_id"],
    }
    (OUT_DIR / f"{SLUG}.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK {out_path}")


if __name__ == "__main__":
    main()
