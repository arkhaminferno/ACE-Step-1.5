"""Generate 'Salma' — groovy afro type-beat x deep house + Arabic girl vocal."""

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
OUT_DIR = Path("/Users/infy/Downloads/ACE-Step-1.5/batch_deephouse/output/salma")
SLUG = "salma"
TITLE = "Salma"
HOOK = "سلمى سلمى"
SEED = 89330
BPM = 108
DURATION = 60

LYRICS = build_simple_lyrics(
    hook=HOOK,
    verse1=[
        "سلمى بتماشي معايا",
        "على دقات الليل",
        "والنبض يلفّني",
        "وإنتِ قريبة مني",
    ],
    verse2=[
        "كل لحن ينادي",
        "يا سلمى اقتربي",
        "والنبض يمشي معاك",
        "ونظرة تخلّيني",
    ],
)

# Groove-first: bounce + deep-house pocket (what worked on Zeina v1 beats).
PROMPT = (
    "GROOVY afro type beat x melodic deep house — Rema bounce, Odeal smoothness, "
    "punchy soft kick every beat, warm bouncing sub bass with sidechain, "
    "syncopated afro hats, soft log-drum accents, melodic pluck hook, airy pads, "
    "head-nod groove, danceable night drive, spacious clean mix. "
    "NOT trap, NOT amapiano spam, NOT brass, NOT busy. "
    f"HAYA song '{SLUG}'. MANDATORY VOCAL: {HUMAN_VOCAL} "
    f"MANDATORY TIMING: {BEAT_LOCK} "
    f"Catchy hook = {HOOK}. Vocal + groove from 0–2s. "
    f"Tempo {BPM} BPM. Key {DEFAULT_KEY}. Soft natural fade."
)

INSTRUCTION = (
    "Generate ONE groovy afro deep-house song with Arabic female vocal. "
    f"CRITICAL VOCAL: {HUMAN_VOCAL} "
    f"CRITICAL TIMING: {BEAT_LOCK} "
    f"Sing hook '{HOOK}' on the groove, in {DEFAULT_KEY}, near {BPM} BPM. "
    "Keep the beat groovy and danceable. Hook early. Soft fade."
)

NEGATIVE = (
    SHORT_NEGATIVE
    + ", trap spam, drill, heavy amapiano, brass, guzheng, pipa, "
    "male vocal, choir, stiff robotic groove"
)


def build_payload() -> dict[str, Any]:
    """Build groovy afro deep-house text2music payload."""
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
    """Generate Salma and write master + metadata."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "lyrics.txt").write_text(LYRICS, encoding="utf-8")
    out_path = OUT_DIR / f"{SLUG}.mp3"
    print(f"GENERATE {SLUG} groovy afro-deephouse seed={SEED} duration={DURATION}")
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
        "style": "groovy afro type-beat x deep house + Arabic girl vocal",
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
