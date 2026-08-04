"""Generate Hala 3-min — Recipe3 A minor 108 piano, tight pocket (not Lina)."""

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
SLUG = "hala"
HOOK = "يا هالة"
LEAD = "piano"
SEED = 98301
BPM = RECIPE3_BPM
KEY = RECIPE3_KEY

VERSE1 = [
    "هالة على النبض",
    "والليل يمشي",
    "بيانو يرد",
    "وأنت هنا",
]
VERSE2 = [
    "خذني بلطف",
    "قبل السهر",
    "لحن خفيف",
    "والقلب يصفى",
]

FULL_POCKET = (
    "FULL POCKET LOCK (MANDATORY): kick is the clock at 108 BPM. "
    "Soft piano chords AND every female vocal syllable land ON the kick or "
    "even eighths — one quantized pocket. No rubato piano, no floating vocal, "
    "no beat-only mix with loose melodies. Sub pumps with the kick."
)


def _cut_cues(final: Path, cues: Path) -> None:
    """Write section cues (no autoplay)."""
    cues.mkdir(exist_ok=True)
    for name, start, dur in (
        ("01_intro.mp3", "0", "12"),
        ("02_groove.mp3", "8", "16"),
        ("03_inst_chorus.mp3", "95", "28"),
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
    """Generate ORIGINAL Hala — new hook/lyrics, piano on-grid."""
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
            "ORIGINAL Hala — A minor 108, soft piano STAR, NOT Lina/Jana/Amira "
            "or any prior HAYA song"
        ),
    )
    payload["guidance_scale"] = 16.5
    payload["instruction"] = (
        f"{payload['instruction']} {FULL_POCKET} "
        "Kick clear by 5s. Piano chord stabs on downbeats + short on-grid motif. "
        "Sing يا هالة only ≤4 short on-kick hits. Tight deep-house motion."
    )
    payload["lm_negative_prompt"] = (
        payload["lm_negative_prompt"]
        + ", Lina clone, يا لينا, off-grid piano, off-beat vocal, rubato, "
        "beat-only, floating chords, instruments ignoring kick"
    )
    print(
        f"GENERATE {SLUG} seed={SEED} key={KEY} bpm={BPM} hook={HOOK}",
        flush=True,
    )
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
        "key": KEY,
        "bpm": BPM,
        "hook": HOOK,
        "seed": SEED,
        "note": "new lyrics (not Lina); full pocket piano+vocal",
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
