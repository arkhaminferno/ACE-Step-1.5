"""Generate 3-min FerdausMix-structured track 'Layl' via ACE-Step."""

from __future__ import annotations

import json
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.ferdaus_structure import (
    FERDAUS_BPM,
    FERDAUS_KEY,
    build_ferdaus_instruction,
    build_ferdaus_lyrics,
    build_ferdaus_prompt,
)

API_BASE = "http://127.0.0.1:8001"
OUT_DIR = Path("/Users/infy/Downloads/ACE-Step-1.5/batch_deephouse/output/layl")
SLUG = "layl"
HOOK = "ليل ليل"
DURATION = 180
SEEDS = [44021, 77803]

LYRICS = build_ferdaus_lyrics(
    hook=HOOK,
    verse1=[
        "في عيني ليل طويل",
        "قلبي يسأل عنك",
        "والمدينة نايمة",
        "وأنا لسه هنا",
    ],
    verse2=[
        "كل نجمة تقول",
        "ارجع لي بهدوء",
        "والليل يحضنني",
        "وأغنية تبقى",
    ],
    pre_chorus=[
        "قربني… قربني",
        "قبل ما يروح الليل",
    ],
)

PROMPT = build_ferdaus_prompt(hook=HOOK, slug=SLUG, duration_sec=DURATION)
INSTRUCTION = build_ferdaus_instruction(hook=HOOK)
NEGATIVE = (
    "male vocal, male voice, choir, duet, robotic vocal, TTS, vocoder, "
    "trumpet, brass, guzheng, pipa, happy bright pop, weak intro, silent start, "
    "hook-only track, no verses, abrupt ending, crackle, hiss, noise"
)

OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "lyrics.txt").write_text(LYRICS, encoding="utf-8")

results = []
for seed in SEEDS:
    tag = f"a{seed}" if seed == SEEDS[0] else f"b{seed}"
    out_path = OUT_DIR / f"layl_{tag}.mp3"
    payload = {
        "prompt": PROMPT,
        "lyrics": LYRICS,
        "instruction": INSTRUCTION,
        "thinking": False,
        "use_format": False,
        "use_cot_caption": False,
        "use_cot_language": False,
        "vocal_language": "ar",
        "audio_duration": DURATION,
        "bpm": FERDAUS_BPM,
        "key_scale": FERDAUS_KEY,
        "inference_steps": 24,
        "guidance_scale": 14.0,
        "lm_cfg_scale": 3.0,
        "lm_negative_prompt": NEGATIVE,
        "model": "acestep-v15-turbo",
        "use_random_seed": False,
        "task_type": "text2music",
        "seed": seed,
        "audio_format": "mp3",
    }
    print(f"GENERATE layl seed={seed} duration={DURATION}s")
    meta = generate_to_file(payload, api_base=API_BASE, api_key="", out_path=out_path, label=f"layl-{seed}")
    results.append({"seed": seed, "file": str(out_path), "task_id": meta["task_id"]})

# Default master copy = first take
master = OUT_DIR / "layl.mp3"
master.write_bytes((OUT_DIR / f"layl_a{SEEDS[0]}.mp3").read_bytes())

meta = {
    "title": "Layl",
    "slug": SLUG,
    "hook": HOOK,
    "bpm": FERDAUS_BPM,
    "key_scale": FERDAUS_KEY,
    "duration_sec": DURATION,
    "engine": "ACE-Step acestep-v15-turbo text2music",
    "structure": "FerdausMix (hook @0s, bass drop ~20s, 3 choruses, breakdown, fade)",
    "seeds": results,
}
(OUT_DIR / "layl.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print("DONE", OUT_DIR)
