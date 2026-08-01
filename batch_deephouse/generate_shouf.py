"""Generate 'Shouf' — approved Hawa/Rouh/Ward recipe, two takes."""

from __future__ import annotations

import json
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.natural_vocal_recipe import (
    build_simple_lyrics,
    build_text2music_payload,
)

API_BASE = "http://127.0.0.1:8001"
OUT_DIR = Path("/Users/infy/Downloads/ACE-Step-1.5/batch_deephouse/output/shouf")
SLUG = "shouf"
HOOK = "شوف شوف"
SEEDS = [83420, 94531]

LYRICS = build_simple_lyrics(
    hook=HOOK,
    verse1=[
        "شوف عيني بهدوء",
        "فيها كلام كتير",
        "والليل يسمعني",
        "وأنت بعيد عني",
    ],
    verse2=[
        "شوف قلبي ينادي",
        "ارجع لي بلطف",
        "لحن خفيف يلفّني",
        "ونظرة تبقيني",
    ],
)

OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "lyrics.txt").write_text(LYRICS, encoding="utf-8")

results = []
for seed in SEEDS:
    tag = f"a{seed}" if seed == SEEDS[0] else f"b{seed}"
    out_path = OUT_DIR / f"shouf_{tag}.mp3"
    payload = build_text2music_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=LYRICS,
        seed=seed,
        thinking=True,
    )
    print(f"GENERATE shouf seed={seed} thinking=True")
    meta = generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=out_path,
        label=f"shouf-{seed}",
    )
    results.append({"seed": seed, "file": str(out_path), "task_id": meta["task_id"]})

master = OUT_DIR / "shouf.mp3"
master.write_bytes((OUT_DIR / f"shouf_a{SEEDS[0]}.mp3").read_bytes())

info = {
    "title": "Shouf",
    "slug": SLUG,
    "hook": HOOK,
    "bpm": 108,
    "key_scale": "A minor",
    "duration_sec": 120,
    "engine": "ACE-Step acestep-v15-turbo text2music",
    "recipe": "natural_vocal_recipe (same as approved Hawa/Rouh/Ward)",
    "thinking": True,
    "seeds": results,
    "notes": "Two takes — listen A and B; keep the better one.",
}
(OUT_DIR / "shouf.json").write_text(
    json.dumps(info, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("DONE", OUT_DIR)
