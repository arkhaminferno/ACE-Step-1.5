"""Generate Basma 3-min — first Recipe4 feel-good track (qanun+violin)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.haya_recipe4 import (
    RECIPE4_BPM,
    RECIPE4_DEFAULT_LEAD,
    RECIPE4_DURATION,
    RECIPE4_KEY,
    build_recipe4_lyrics,
    build_recipe4_payload,
    master_recipe4_mp3,
)
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"
SLUG = "basma"
HOOK = "يا بسمة"
ANSWER = "ويا قلبي"
LEAD = RECIPE4_DEFAULT_LEAD  # qanun_violin
SEED = 42011
BPM = RECIPE4_BPM
KEY = RECIPE4_KEY

VERSE1 = [
    "بسمة على الليل",
    "والنبض يصفى",
    "لحن يفتحني",
    "والقلب يرتاح",
]
VERSE2 = [
    "خذني بلطف",
    "فوق السحاب",
    "صوت ينادي",
    "ويا بسمة",
]


def _cut_cues(final: Path, cues: Path) -> None:
    """Write section cues (no autoplay)."""
    cues.mkdir(exist_ok=True)
    for name, start, dur in (
        ("01_intro.mp3", "0", "12"),
        ("02_groove.mp3", "8", "16"),
        ("03_drop.mp3", "25", "28"),
        ("04_call_response.mp3", "70", "20"),
        ("05_drop_reprise.mp3", "110", "28"),
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
    """Generate ORIGINAL Basma — Recipe4 feel-good, no piano."""
    out_dir = OUTPUT_DIR / SLUG
    sources = OUTPUT_DIR / "_recipe4_sources"
    out_dir.mkdir(parents=True, exist_ok=True)
    sources.mkdir(parents=True, exist_ok=True)

    lyrics = build_recipe4_lyrics(
        hook=HOOK,
        answer=ANSWER,
        verse1=VERSE1,
        verse2=VERSE2,
        lead=LEAD,
    )
    (out_dir / "lyrics_3min.txt").write_text(lyrics, encoding="utf-8")
    raw = sources / f"{SLUG}_3min_raw.mp3"
    payload = build_recipe4_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=lyrics,
        seed=SEED,
        bpm=BPM,
        key=KEY,
        duration=RECIPE4_DURATION,
        lead=LEAD,
        answer=ANSWER,
        color_note=(
            "ORIGINAL Basma — Recipe4 feel-good smile lane, "
            "qanun build + violin chorus hook, call-response tarab, NO piano"
        ),
    )
    print(
        f"GENERATE {SLUG} recipe4 lead={LEAD} bpm={BPM} key={KEY} seed={SEED}",
        flush=True,
    )
    meta = generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=raw,
        label=f"{SLUG}-r4",
    )
    listen, ai = master_recipe4_mp3(raw, slug=f"{SLUG}_3min", bpm=BPM)
    final = out_dir / f"{SLUG}_3min.mp3"
    final.write_bytes(listen.read_bytes())
    _cut_cues(final, out_dir / "cues")
    info = {
        "slug": SLUG,
        "recipe": "haya_recipe4",
        "lead": LEAD,
        "key": KEY,
        "bpm": BPM,
        "hook": HOOK,
        "answer": ANSWER,
        "seed": SEED,
        "note": "feel-good Rast/Bayati — qanun+violin — no piano",
        "file": str(final.resolve()),
        "task_id": meta.get("task_id"),
        "ai_score": ai,
    }
    (out_dir / f"{SLUG}_recipe4.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("DONE", final, "ai", ai, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
