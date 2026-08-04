"""Generate instrumental soulcalm pilot — it's late (3-min sample)."""

from __future__ import annotations

import json

from batch_deephouse.acestep_task import generate_to_file
from batch_soulcalm.brand import SAMPLE_DURATION_SEC
from batch_soulcalm.paths import OUTPUT_DIR
from batch_soulcalm.prompts import (
    DEFAULT_BPM,
    DEFAULT_INSTRUMENTAL_LYRICS,
    DEFAULT_KEY,
    build_payload,
)

API_BASE = "http://127.0.0.1:8001"
SLUG = "its_late"
TITLE = "it's late, you should be asleep"
SEED = 72044

MOOD = (
    "Night city glow through the window. Soft piano + warm retro synth pads. "
    "Instrumental only — sleep and overthinking, never vocals."
)


def main() -> int:
    """Generate the 3-min instrumental sample."""
    out_dir = OUTPUT_DIR / SLUG
    out_dir.mkdir(parents=True, exist_ok=True)
    lyrics_path = out_dir / "structure.txt"
    lyrics_path.write_text(DEFAULT_INSTRUMENTAL_LYRICS.strip() + "\n", encoding="utf-8")
    raw = out_dir / f"{SLUG}_3min.mp3"
    payload = build_payload(
        lyrics=DEFAULT_INSTRUMENTAL_LYRICS,
        duration_sec=SAMPLE_DURATION_SEC,
        bpm=DEFAULT_BPM,
        key_scale=DEFAULT_KEY,
        seed=SEED,
        mood_note=MOOD,
        thinking=True,
    )
    print(f"GENERATE {SLUG} instrumental {SAMPLE_DURATION_SEC}s bpm={DEFAULT_BPM} seed={SEED}")
    meta = generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=raw,
        label=SLUG,
    )
    info = {
        "title": TITLE,
        "slug": SLUG,
        "instrumental": True,
        "bpm": DEFAULT_BPM,
        "key_scale": DEFAULT_KEY,
        "duration_sec": SAMPLE_DURATION_SEC,
        "seed": SEED,
        "mood": MOOD,
        "thinking": True,
        "task_id": meta["task_id"],
        "file": str(raw),
        "structure_file": str(lyrics_path),
        "video_plan": "static girl still + fade in/out only (no overlays)",
    }
    (out_dir / f"{SLUG}_3min.json").write_text(
        json.dumps(info, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"DONE: {raw}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
