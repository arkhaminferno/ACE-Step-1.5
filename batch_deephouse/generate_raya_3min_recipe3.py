"""Generate Raya 3-min — Recipe3 at 108 BPM, dry oud only (no piano)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.haya_recipe3 import (
    RECIPE3_BPM,
    RECIPE3_DURATION,
    RECIPE3_KEY,
    build_recipe3_lyrics,
    build_recipe3_payload,
    master_recipe3_mp3,
)
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"
SLUG = "raya"
HOOK = "يا ريا"
LEAD = "oud"  # no piano — cleaner pocket
SEED = 99401
BPM = RECIPE3_BPM
KEY = RECIPE3_KEY

VERSE1 = [
    "ريا على النبض",
    "والليل يمشي",
    "عود يرد لي",
    "وأنت هنا",
]
VERSE2 = [
    "خذني بلطف",
    "قبل السهر",
    "لحن خفيف",
    "والقلب يصفى",
]


def _cut_cues(final: Path, cues: Path) -> None:
    """Write section cues (no autoplay)."""
    cues.mkdir(exist_ok=True)
    for name, start, dur in (
        ("01_intro.mp3", "0", "12"),
        ("02_groove.mp3", "8", "16"),
        ("03_oud_chorus.mp3", "95", "28"),
        ("05_hook.mp3", "70", "18"),
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
    """Generate ORIGINAL Raya — 108 A minor, dry oud star, no piano."""
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
        key=KEY,
        duration=RECIPE3_DURATION,
        lead=LEAD,
        color_note=(
            "ORIGINAL Raya — 108 BPM A minor, dry oud STAR only, "
            "NO piano (piano made prior gens messy)"
        ),
    )
    payload["guidance_scale"] = 15.5
    payload["instruction"] = (
        f"{payload['instruction']} NO PIANO anywhere. Soft pad + kick by ~6s. "
        "Dry acoustic oud is the only melodic lead — ON the kick grid. "
        "Female vocal syllables ON the same kick pocket. "
        f"Hook {HOOK} ≤4 short on-kick hits. Clear four-on-floor night-drive."
    )
    payload["lm_negative_prompt"] = (
        payload["lm_negative_prompt"]
        + ", piano, soft piano, piano lead, concert piano, keys solo, "
        "off-grid oud, off-beat vocal, rubato, guzheng, pipa, brass"
    )
    print(
        f"GENERATE {SLUG} lead={LEAD} (no piano) bpm={BPM} key={KEY} seed={SEED}",
        flush=True,
    )
    meta = generate_to_file(
        payload, api_base=API_BASE, api_key="", out_path=raw, label=f"{SLUG}-oud"
    )
    listen, ai = master_recipe3_mp3(raw, slug=f"{SLUG}_3min", bpm=BPM)
    final = out_dir / f"{SLUG}_3min.mp3"
    final.write_bytes(listen.read_bytes())
    _cut_cues(final, out_dir / "cues")
    info = {
        "slug": SLUG,
        "lead": LEAD,
        "key": KEY,
        "bpm": BPM,
        "hook": HOOK,
        "seed": SEED,
        "note": "no piano — dry oud only",
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
