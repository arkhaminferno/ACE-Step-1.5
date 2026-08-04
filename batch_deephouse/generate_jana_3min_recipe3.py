"""Generate Jana 3-min — Recipe3 trio (piano intro, oud chorus, ney color)."""

from __future__ import annotations

import json
import subprocess
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
SLUG = "jana"
HOOK = "يا جنى"
LEAD = "piano_oud_ney"
SEED = 96201
BPM = RECIPE3_BPM

# Short on-grid-friendly lines
VERSE1 = [
    "جنى تمشي بهدوء",
    "والليل على مهله",
    "عود على النبض",
    "وأنت في البال",
]
VERSE2 = [
    "خذني بلطف",
    "قبل ما يروح السهر",
    "ناي في الآخر",
    "والقلب يصفى",
]


def _cut_cues(final: Path, cues: Path) -> None:
    """Write section cues (no autoplay)."""
    cues.mkdir(exist_ok=True)
    for name, start, dur in (
        ("01_intro_piano.mp3", "0", "14"),
        ("03_oud_chorus.mp3", "95", "28"),
        ("05_hook.mp3", "70", "18"),
        ("06_ney_outro_zone.mp3", "150", "28"),
    ):
        subprocess.run(
            [
                "ffmpeg", "-y", "-ss", start, "-t", dur, "-i", str(final),
                "-codec:a", "libmp3lame", "-b:a", "192k", str(cues / name),
            ],
            check=False,
            capture_output=True,
        )


def main() -> int:
    """Generate brand-new Jana with Recipe3 piano→oud→ney map."""
    out_dir = OUTPUT_DIR / SLUG
    sources = OUTPUT_DIR / "_recipe3_sources"
    out_dir.mkdir(parents=True, exist_ok=True)
    sources.mkdir(parents=True, exist_ok=True)

    lyrics = build_recipe3_lyrics(
        hook=HOOK, verse1=VERSE1, verse2=VERSE2, lead=LEAD
    )
    (out_dir / "lyrics_3min.txt").write_text(lyrics, encoding="utf-8")
    raw = sources / f"{SLUG}_3min_raw.mp3"
    payload = build_recipe3_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=lyrics,
        seed=SEED,
        bpm=BPM,
        duration=RECIPE3_DURATION,
        lead=LEAD,
        color_note=(
            "ORIGINAL Jana — piano intro, oud instrumental heart, "
            "sparse ney outro; NOT a remix of Amira/Salma/Nafas/HAYA"
        ),
    )
    # Extra vocal pocket emphasis without rewriting instruments.
    payload["instruction"] = (
        f"{payload['instruction']} VOCAL ON-GRID: every Arabic syllable on the "
        "kick or even eighth — short phrases, no rubato over the groove."
    )
    print(f"GENERATE {SLUG} lead={LEAD} seed={SEED} hook={HOOK}", flush=True)
    meta = generate_to_file(
        payload, api_base=API_BASE, api_key="", out_path=raw, label=f"{SLUG}-r3"
    )
    listen, ai = master_recipe3_mp3(raw, slug=f"{SLUG}_3min", bpm=BPM)
    final = out_dir / f"{SLUG}_3min.mp3"
    final.write_bytes(listen.read_bytes())
    _cut_cues(final, out_dir / "cues")
    info = {
        "slug": SLUG,
        "lead": LEAD,
        "map": "intro=piano, chorus=oud, outro=ney",
        "hook": HOOK,
        "seed": SEED,
        "file": str(final.resolve()),
        "task_id": meta.get("task_id"),
        "ai_score": ai,
    }
    (out_dir / f"{SLUG}_recipe3.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("DONE", final, "ai", ai, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
