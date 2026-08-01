"""Generate 'Hawa' with locked natural-vocal + beat-lock recipe."""

from __future__ import annotations

import json
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.natural_vocal_recipe import (
    build_simple_lyrics,
    build_text2music_payload,
)

API_BASE = "http://127.0.0.1:8001"
OUT_DIR = Path("/Users/infy/Downloads/ACE-Step-1.5/batch_deephouse/output/hawa")
SLUG = "hawa"
HOOK = "هوا هوا"
SEEDS = [81201, 90317]

LYRICS = build_simple_lyrics(
    hook=HOOK,
    verse1=[
        "في عيني هوا هادي",
        "يلفّ القلب بلطف",
        "والليل يسمعني",
        "وأنت بعيد عني",
    ],
    verse2=[
        "كل نفس يقول",
        "ارجع لي بهدوء",
        "والهوا يحضنني",
        "ولحن يبقى معي",
    ],
)

OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "lyrics.txt").write_text(LYRICS, encoding="utf-8")

results = []
for seed in SEEDS:
    tag = f"a{seed}" if seed == SEEDS[0] else f"b{seed}"
    out_path = OUT_DIR / f"hawa_{tag}.mp3"
    payload = build_text2music_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=LYRICS,
        seed=seed,
        thinking=True,
    )
    print(f"GENERATE hawa seed={seed} thinking={payload['thinking']}")
    meta = generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=out_path,
        label=f"hawa-{seed}",
    )
    results.append({"seed": seed, "file": str(out_path), "task_id": meta["task_id"]})

# Default master = first take
master = OUT_DIR / "hawa.mp3"
master.write_bytes((OUT_DIR / f"hawa_a{SEEDS[0]}.mp3").read_bytes())

meta = {
    "title": "Hawa",
    "slug": SLUG,
    "hook": HOOK,
    "bpm": 108,
    "key_scale": "A minor",
    "duration_sec": 120,
    "engine": "ACE-Step acestep-v15-turbo text2music",
    "recipe": "natural_vocal_recipe (Noor-style + thinking LM 1.7B)",
    "thinking": True,
    "seeds": results,
}
(OUT_DIR / "hawa.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print("DONE", OUT_DIR)
