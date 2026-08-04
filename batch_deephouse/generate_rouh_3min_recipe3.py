"""Generate Rouh 3-min with Recipe 3 v2 (Recipe2 intro + verses + inst chorus)."""

from __future__ import annotations

import json

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.haya_recipe3 import (
    RECIPE3_BPM,
    RECIPE3_DURATION,
    RECIPE3_REF_HOOK,
    build_recipe3_lyrics,
    build_recipe3_payload,
    master_recipe3_mp3,
)
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"
SLUG = "rouh_r3"
HOOK = RECIPE3_REF_HOOK
SEED = 90041
BPM = RECIPE3_BPM

VERSE1 = [
    "روحي معك بهدوء",
    "والليل يحفظنا",
    "كل نبضة تنادي",
    "وأنت بعيد عني",
]
VERSE2 = [
    "خذني معك بلطف",
    "قبل ما يروح الليل",
    "لحن خفيف يلفّني",
    "وروحك تبقيني",
]


def main() -> int:
    """Generate Rouh Recipe 3 v2 sample."""
    out_dir = OUTPUT_DIR / SLUG
    sources = OUTPUT_DIR / "_recipe3_sources"
    out_dir.mkdir(parents=True, exist_ok=True)
    sources.mkdir(parents=True, exist_ok=True)

    lyrics = build_recipe3_lyrics(hook=HOOK, verse1=VERSE1, verse2=VERSE2)
    (out_dir / "lyrics_3min.txt").write_text(lyrics, encoding="utf-8")
    raw = sources / f"{SLUG}_3min_v2_raw.mp3"
    payload = build_recipe3_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=lyrics,
        seed=SEED,
        bpm=BPM,
        duration=RECIPE3_DURATION,
    )
    print(f"GENERATE {SLUG} recipe3v2 seed={SEED}", flush=True)
    meta = generate_to_file(
        payload, api_base=API_BASE, api_key="", out_path=raw, label=f"{SLUG}-r3v2"
    )
    listen, ai = master_recipe3_mp3(raw, slug=f"{SLUG}_3min_v2", bpm=BPM)
    final = out_dir / f"{SLUG}_3min_v2.mp3"
    final.write_bytes(listen.read_bytes())
    (out_dir / f"{SLUG}_recipe3_v2.json").write_text(
        json.dumps(
            {
                "slug": SLUG,
                "recipe": "haya_recipe3 v2",
                "hook": HOOK,
                "seed": SEED,
                "file": str(final.resolve()),
                "task_id": meta.get("task_id"),
                "ai_score": ai,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("DONE", final, final.stat().st_size, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
