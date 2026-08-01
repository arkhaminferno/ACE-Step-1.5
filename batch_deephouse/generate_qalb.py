"""Generate 'Qalb' — approved Hawa recipe, two takes."""

from __future__ import annotations

import json
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.natural_vocal_recipe import (
    build_simple_lyrics,
    build_text2music_payload,
)

API_BASE = "http://127.0.0.1:8001"
OUT_DIR = Path("/Users/infy/Downloads/ACE-Step-1.5/batch_deephouse/output/qalb")
SLUG = "qalb"
HOOK = "قلبي قلبي"
# Seeds near approved Hawa/Shouf range.
SEEDS = [81288, 83501]

LYRICS = build_simple_lyrics(
    hook=HOOK,
    verse1=[
        "قلبي ينادي باسمك",
        "في الليل بهدوء",
        "كل نبضة تقول",
        "ارجع لي حبيبي",
    ],
    verse2=[
        "والعالم نايم",
        "وأنا لسه هنا",
        "لحن خفيف يلفّني",
        "وقلبي يبقى معك",
    ],
)

OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "lyrics.txt").write_text(LYRICS, encoding="utf-8")

results = []
for seed in SEEDS:
    tag = f"a{seed}" if seed == SEEDS[0] else f"b{seed}"
    out_path = OUT_DIR / f"qalb_{tag}.mp3"
    payload = build_text2music_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=LYRICS,
        seed=seed,
        thinking=True,
    )
    payload["lm_model_path"] = "acestep-5Hz-lm-1.7B"
    print(f"GENERATE qalb seed={seed} thinking=True")
    meta = generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=out_path,
        label=f"qalb-{seed}",
    )
    results.append({"seed": seed, "file": str(out_path), "task_id": meta["task_id"]})

info = {
    "title": "Qalb",
    "slug": SLUG,
    "hook": HOOK,
    "bpm": 108,
    "key_scale": "A minor",
    "duration_sec": 120,
    "engine": "ACE-Step acestep-v15-turbo text2music",
    "recipe": "natural_vocal_recipe (same as approved Hawa/Rouh/Ward/Shouf)",
    "thinking": True,
    "lm_model_path": "acestep-5Hz-lm-1.7B",
    "seeds": results,
    "notes": "Two takes — listen A and B; promote the better one to qalb.mp3.",
}
(OUT_DIR / "qalb.json").write_text(
    json.dumps(info, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("DONE — pick A or B:")
for item in results:
    print(" ", item["file"])
