"""Generate 'Leila' — classic HAYA Arabic deep house + female Arabic vocal."""

from __future__ import annotations

import json
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.natural_vocal_recipe import (
    build_simple_lyrics,
    build_text2music_payload,
)

API_BASE = "http://127.0.0.1:8001"
OUT_DIR = Path("/Users/infy/Downloads/ACE-Step-1.5/batch_deephouse/output/leila")
SLUG = "leila"
TITLE = "Leila"
HOOK = "ليلى ليلى"
SEED = 81201
DURATION = 60  # Mac VAE-safe pilot; extend later if approved

LYRICS = build_simple_lyrics(
    hook=HOOK,
    verse1=[
        "ليلى والليل طويل",
        "قلبي يسأل عنك",
        "والدقات هادية",
        "وأنت بعيد عني",
    ],
    verse2=[
        "كل لحن ينادي",
        "ارجع لي بهدوء",
        "والعود يرد بلطف",
        "ونظرة تبقيني",
    ],
)


def main() -> None:
    """Generate Leila with the approved natural_vocal_recipe."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "lyrics.txt").write_text(LYRICS, encoding="utf-8")
    out_path = OUT_DIR / f"{SLUG}.mp3"
    payload = build_text2music_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=LYRICS,
        seed=SEED,
        thinking=False,
        duration=DURATION,
    )
    payload["batch_size"] = 1
    print(f"GENERATE {SLUG} arabic deep house seed={SEED} duration={DURATION}")
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
        "duration_sec": DURATION,
        "style": "Arabic deep house + female Arabic vocal (natural_vocal_recipe)",
        "engine": "ACE-Step acestep-v15-turbo text2music",
        "recipe": "natural_vocal_recipe (Noor/Hawa lane)",
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
