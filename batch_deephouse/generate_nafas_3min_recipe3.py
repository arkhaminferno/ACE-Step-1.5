"""Generate Nafas 3-min — Recipe 3 v2 (Recipe2 intro + verses + inst chorus)."""

from __future__ import annotations

import json
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.haya_recipe3 import (
    RECIPE3_BPM,
    RECIPE3_DURATION,
    build_recipe3_lyrics,
    build_recipe3_payload,
    master_recipe3_mp3,
)
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"
SLUG = "nafas"
HOOK = "يا نفس"
SEED = 90101
BPM = RECIPE3_BPM

VERSE1 = [
    "نفسي تمشي بهدوء",
    "والليل على الدرب",
    "لحن العود يناديني",
    "وأنت في البال",
]
VERSE2 = [
    "خذني على النبض",
    "قبل ما يروح السكون",
    "نفس خفيف يلفّني",
    "والقلب يصفى",
]


def main() -> int:
    """Generate one full 3-min Recipe 3 song for approval."""
    out_dir = OUTPUT_DIR / SLUG
    sources = OUTPUT_DIR / "_recipe3_sources"
    out_dir.mkdir(parents=True, exist_ok=True)
    sources.mkdir(parents=True, exist_ok=True)

    lyrics = build_recipe3_lyrics(hook=HOOK, verse1=VERSE1, verse2=VERSE2)
    (out_dir / "lyrics_3min.txt").write_text(lyrics, encoding="utf-8")

    raw = sources / f"{SLUG}_3min_raw.mp3"
    payload = build_recipe3_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=lyrics,
        seed=SEED,
        bpm=BPM,
        duration=RECIPE3_DURATION,
        color_note=(
            "Nafas Recipe3 v2 — Recipe2 soft hum intro, two short verses, "
            "instrumental oud chorus heart, hook يا نفس only 2–4 hits"
        ),
    )
    print(
        f"GENERATE {SLUG} recipe3v2 seed={SEED} "
        f"duration={RECIPE3_DURATION}s bpm={BPM}",
        flush=True,
    )
    meta = generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=raw,
        label=f"{SLUG}-recipe3",
    )
    listen, ai = master_recipe3_mp3(raw, slug=f"{SLUG}_3min", bpm=BPM)
    final = out_dir / f"{SLUG}_3min.mp3"
    final.write_bytes(listen.read_bytes())

    info = {
        "slug": SLUG,
        "recipe": "haya_recipe3 v2 — Recipe2 intro + verses + inst chorus heart",
        "hook": HOOK,
        "seed": SEED,
        "bpm": BPM,
        "duration_sec": RECIPE3_DURATION,
        "file": str(final.resolve()),
        "raw": str(raw.resolve()),
        "task_id": meta.get("task_id"),
        "ai_score": ai,
    }
    (out_dir / f"{SLUG}_recipe3.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("DONE", final, final.stat().st_size, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
