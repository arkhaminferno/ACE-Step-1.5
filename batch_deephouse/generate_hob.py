"""Generate one new HAYA song with the approved natural_vocal_recipe."""

from __future__ import annotations

import json
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.natural_vocal_recipe import (
    build_simple_lyrics,
    build_text2music_payload,
)

API_BASE = "http://127.0.0.1:8001"
OUT_DIR = Path("/Users/infy/Downloads/ACE-Step-1.5/batch_deephouse/output/hob")
SLUG = "hob"
TITLE = "Hob"
HOOK = "حب حب"
SEED = 85601

LYRICS = build_simple_lyrics(
    hook=HOOK,
    verse1=[
        "حبي ليك بهدوء",
        "يمشي مع دقات الليل",
        "والطريق فاضي",
        "وأنت في بالي",
    ],
    verse2=[
        "كل حب ينادي",
        "قرب لي بلطف",
        "واللحن يلفّني",
        "ونظرة تبقيني",
    ],
)


def main() -> None:
    """Generate Hob and write master + metadata."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "lyrics.txt").write_text(LYRICS, encoding="utf-8")
    out_path = OUT_DIR / f"{SLUG}.mp3"
    payload = build_text2music_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=LYRICS,
        seed=SEED,
        thinking=False,
        duration=60,
    )
    payload["batch_size"] = 1
    print(f"GENERATE {SLUG} seed={SEED} thinking=False batch=1 duration=60")
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
        "bpm": 108,
        "key_scale": "A minor",
        "duration_sec": 60,
        "engine": "ACE-Step acestep-v15-turbo text2music",
        "recipe": "natural_vocal_recipe (batch=1, 60s for Mac VAE memory)",
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
