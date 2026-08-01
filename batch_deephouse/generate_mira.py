"""Generate 'Mira' — Rima-lane color on locked HAYA signature recipe."""

from __future__ import annotations

import json
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.haya_signature_recipe import (
    build_signature_payload,
    build_simple_lyrics,
    master_signature_mp3,
)
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"
SLUG = "mira"
TITLE = "Mira"
HOOK = "ميرا ميرا"
SEED = 93722

# Same intimate/oud color that worked on Rima — new hook + lyrics + seed.
COLOR = (
    "more intimate close-mic vocal, slightly softer pads, "
    "oud answers more often in the gaps, distinct short melodic motif — "
    "same lane as Rima, different melody and lyrics"
)

VERSE1 = [
    "ميرا في عيني الليلة",
    "تمشي بهدوء على الطريق",
    "والدقات ثابتة",
    "وإنتِ قريبة مني",
]
VERSE2 = [
    "كل لحن ينادي",
    "يا ميرا بلطف",
    "والعود يرد خفيف",
    "ونظرة تبقيني",
]


def main() -> None:
    """Generate Mira in the Rima intimate/oud signature color."""
    out_dir = OUTPUT_DIR / SLUG
    out_dir.mkdir(parents=True, exist_ok=True)
    lyrics = build_simple_lyrics(hook=HOOK, verse1=VERSE1, verse2=VERSE2)
    (out_dir / "lyrics.txt").write_text(lyrics, encoding="utf-8")
    raw = out_dir / f"{SLUG}.mp3"
    payload = build_signature_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=lyrics,
        seed=SEED,
        color_note=COLOR,
    )
    print(f"GENERATE {SLUG} rima-lane signature seed={SEED}")
    meta = generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=raw,
        label=SLUG,
    )
    listen, ai_prob = master_signature_mp3(raw, slug=SLUG)
    info = {
        "title": TITLE,
        "slug": SLUG,
        "hook": HOOK,
        "bpm": 110,
        "key_scale": "A minor",
        "duration_sec": 60,
        "recipe": "haya_signature_recipe",
        "lane": "rima-intimate-oud",
        "color_note": COLOR,
        "thinking": True,
        "seed": SEED,
        "task_id": meta["task_id"],
        "listen": str(listen),
        "ai_score": ai_prob,
    }
    (out_dir / f"{SLUG}.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK {listen} ai={ai_prob:.4f}")


if __name__ == "__main__":
    main()
