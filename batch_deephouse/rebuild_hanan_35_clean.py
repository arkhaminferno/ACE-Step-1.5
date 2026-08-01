"""Rebuild Hanan 35-min cleanly: Recipe 2 3-min once, then smooth loop ONLY.

No second humanize/stealth on the long mix — that was adding noise vs the
approved 3-min listen.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.extend_mix import build_crossfade_long_mix, probe_duration_sec
from batch_deephouse.haya_recipe2 import (
    RECIPE2_BPM,
    RECIPE2_CROSSFADE_SEC,
    RECIPE2_DURATION,
    RECIPE2_HANAN_HOOK,
    RECIPE2_HANAN_SEED,
    build_recipe2_lyrics,
    build_recipe2_payload,
    master_recipe2_mp3,
)
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"
SLUG = "hanan"
TARGET_35 = 35 * 60

VERSE1 = [
    "في عيني حنان هادي",
    "يلفّ القلب بلطف",
    "والليل يسمعني",
    "وأنت بعيد عني",
]
VERSE2 = [
    "كل نفس يقول",
    "ارجع لي بهدوء",
    "والحنان يحضنني",
    "ولحن يبقى معي",
]
VERSE3 = [
    "الطريق فاضي الليلة",
    "ونبض يسأل عنك",
    "قرب لي شوي",
    "والدنيا تمشي",
]


def _loudnorm_only(src: Path, dst: Path) -> Path:
    """Light LUFS match only — no pitch/extrastereo noise."""
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(src),
        "-af",
        "loudnorm=I=-13:TP=-1.0:LRA=11",
        "-ar",
        "48000",
        "-c:a",
        "libmp3lame",
        "-b:a",
        "192k",
        str(dst),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-1500:])
    return dst


def main() -> None:
    """Regenerate clean Recipe 2 3-min, loop to 35-min without noisy remaster."""
    out_dir = OUTPUT_DIR / SLUG
    out_dir.mkdir(parents=True, exist_ok=True)
    sources = OUTPUT_DIR / "_recipe2_sources"
    sources.mkdir(parents=True, exist_ok=True)

    lyrics = build_recipe2_lyrics(
        hook=RECIPE2_HANAN_HOOK,
        verse1=VERSE1,
        verse2=VERSE2,
        verse3=VERSE3,
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        raw = tmp / "raw.mp3"
        payload = build_recipe2_payload(
            hook=RECIPE2_HANAN_HOOK,
            slug=SLUG,
            lyrics=lyrics,
            seed=RECIPE2_HANAN_SEED,
        )
        print(
            f"GENERATE clean Recipe2 3min seed={RECIPE2_HANAN_SEED} "
            f"bpm={RECIPE2_BPM}"
        )
        generate_to_file(
            payload,
            api_base=API_BASE,
            api_key="",
            out_path=raw,
            label="hanan_recipe2_clean",
        )
        # Single master pass (same as the approved listen path).
        three_listen, ai3 = master_recipe2_mp3(raw, slug=f"{SLUG}_3min")
        three_clean = sources / f"{SLUG}_3min_recipe2_clean.mp3"
        shutil.copy2(three_listen, three_clean)
        print(f"clean 3min → {three_clean} ai≈{ai3:.4f}")

        # Loop ONLY — no distribute/stealth on the 35-min (avoids noise stack).
        long_raw = tmp / "long_raw.mp3"
        long_final = tmp / "long_final.mp3"
        build_crossfade_long_mix(
            three_clean,
            long_raw,
            target_sec=float(TARGET_35),
            crossfade_sec=RECIPE2_CROSSFADE_SEC,
            fade_in_sec=4.0,
            fade_out_sec=10.0,
        )
        _loudnorm_only(long_raw, long_final)
        print(f"clean 35min loop → {probe_duration_sec(long_final):.1f}s")

        for child in list(out_dir.iterdir()):
            if child.is_file():
                child.unlink()
            elif child.is_dir():
                shutil.rmtree(child)

        final = out_dir / f"{SLUG}_35min.mp3"
        shutil.copy2(long_final, final)
        meta = {
            "slug": SLUG,
            "recipe": "haya_recipe2",
            "hook": RECIPE2_HANAN_HOOK,
            "seed": RECIPE2_HANAN_SEED,
            "bpm": RECIPE2_BPM,
            "base_duration_sec": RECIPE2_DURATION,
            "crossfade_sec": RECIPE2_CROSSFADE_SEC,
            "file": str(final),
            "duration_sec": probe_duration_sec(final),
            "ai_score_3min_approx": ai3,
            "mastering": (
                "3min: single distribute+stealth; "
                "35min: acrossfade loop + loudnorm only (no 2nd humanize)"
            ),
            "clean_3min_source": str(three_clean),
        }
        (out_dir / f"{SLUG}_recipe2.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(f"DONE clean {final} ({meta['duration_sec']/60:.1f} min)")


if __name__ == "__main__":
    main()
