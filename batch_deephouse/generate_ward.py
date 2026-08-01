"""Generate 'Ward' — approved Hawa/Rouh recipe, two takes."""

from __future__ import annotations

import json
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.natural_vocal_recipe import (
    build_simple_lyrics,
    build_text2music_payload,
)

API_BASE = "http://127.0.0.1:8001"
OUT_DIR = Path("/Users/infy/Downloads/ACE-Step-1.5/batch_deephouse/output/ward")
SLUG = "ward"
HOOK = "ورد ورد"
SEEDS = [82601, 92714]

LYRICS = build_simple_lyrics(
    hook=HOOK,
    verse1=[
        "في عيني ورد هادي",
        "يفتح بهدوء لقلبي",
        "والليل يشمّه معي",
        "وأنت بعيد عني",
    ],
    verse2=[
        "كل وردة تقول",
        "ابقَ معي بلطف",
        "لحن خفيف يلفّني",
        "والورد يبقى في يدي",
    ],
)

OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "lyrics.txt").write_text(LYRICS, encoding="utf-8")

results = []
for seed in SEEDS:
    tag = f"a{seed}" if seed == SEEDS[0] else f"b{seed}"
    out_path = OUT_DIR / f"ward_{tag}.mp3"
    payload = build_text2music_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=LYRICS,
        seed=seed,
        thinking=True,
    )
    print(f"GENERATE ward seed={seed} thinking=True")
    meta = generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=out_path,
        label=f"ward-{seed}",
    )
    results.append({"seed": seed, "file": str(out_path), "task_id": meta["task_id"]})

master = OUT_DIR / "ward.mp3"
master.write_bytes((OUT_DIR / f"ward_a{SEEDS[0]}.mp3").read_bytes())

info = {
    "title": "Ward",
    "slug": SLUG,
    "hook": HOOK,
    "bpm": 108,
    "key_scale": "A minor",
    "duration_sec": 120,
    "engine": "ACE-Step acestep-v15-turbo text2music",
    "recipe": "natural_vocal_recipe (same as approved Hawa/Rouh)",
    "thinking": True,
    "seeds": results,
    "notes": "Two takes — listen A and B; keep the better one.",
}
(OUT_DIR / "ward.json").write_text(
    json.dumps(info, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("DONE", OUT_DIR)
