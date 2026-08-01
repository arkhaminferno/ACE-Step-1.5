"""Generate 'Zeina' — Odeal x Rema afro type-beat x deep house + Arabic girl vocal."""

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
OUT_DIR = Path("/Users/infy/Downloads/ACE-Step-1.5/batch_deephouse/output/zeina")
SLUG = "zeina"
TITLE = "Zeina"
HOOK = "زينة زينة"
SEED = 87105
BPM = 108
DURATION = 60  # Mac VAE-safe pilot length

# Afro type-beat x melodic deep house (Rema/Odeal pocket) — not oriental-oud HAYA default.
AFRO_PROMPT = (
    "Afro type beat x melodic deep house, Rema and Odeal inspired romantic afro-R&B pocket, "
    "soft log drums, warm bouncing sub bass, gentle four-on-floor deep-house kick, "
    "syncopated afro hats, airy pads, melodic afro pluck motif, clean spacious mix, "
    "night-drive sensual vibe, NOT trap, NOT amapiano log-drum spam, NOT brass. "
    f"HAYA song '{SLUG}'. "
    f"MANDATORY VOCAL: {HUMAN_VOCAL} "
    f"MANDATORY TIMING: {BEAT_LOCK} "
    f"Memorable hook = {HOOK}. Groove and vocal from the first 2 seconds. "
    f"Tempo {BPM} BPM. Key {DEFAULT_KEY}. Soft natural fade."
)

AFRO_INSTRUCTION = (
    "Generate ONE afro deep-house song with Arabic female vocal. "
    f"CRITICAL VOCAL: {HUMAN_VOCAL} "
    f"CRITICAL TIMING: {BEAT_LOCK} "
    f"Sing hook '{HOOK}' on beat, in {DEFAULT_KEY}, near {BPM} BPM. "
    "Afro type-beat groove + deep-house kick/sub. Hook first (0–2s). "
    "Verses are real Arabic lines — not hook-only. Soft natural fade."
)

AFRO_NEGATIVE = (
    SHORT_NEGATIVE
    + ", trap 808 spam, drill, heavy amapiano, brass, trumpet, guzheng, pipa, "
    "male vocal, choir, English rap"
)

LYRICS = build_simple_lyrics(
    hook=HOOK,
    verse1=[
        "زينة في عينيّا",
        "تمشي مع دقات القلب",
        "والليل يلفّني",
        "وإنتِ في بالي",
    ],
    verse2=[
        "كل لحن ينادي",
        "قرب لي بهدوء",
        "والدنيا هادية",
        "ونظرة تبقيني",
    ],
)


def build_payload() -> dict[str, Any]:
    """Build afro deep-house text2music payload."""
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
    """Generate Zeina and write master + metadata."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "lyrics.txt").write_text(LYRICS, encoding="utf-8")
    out_path = OUT_DIR / f"{SLUG}.mp3"
    payload = build_payload()
    print(f"GENERATE {SLUG} afro-deephouse seed={SEED} duration={DURATION} batch=1")
    meta = generate_to_file(
        payload,
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
        "style": "Odeal x Rema afro type-beat x deep house + Arabic girl vocal",
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
