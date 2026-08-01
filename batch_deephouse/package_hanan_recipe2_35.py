"""Package approved Hanan 3-min → stealth 35-min; lock Recipe 2; clean folder."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from batch_birthday.ai_stealth import (
    STEALTH_AI_TARGET,
    STEALTH_PITCH_RATES,
    apply_stealth_mp3,
    stealth_pitch_rate_for,
)
from batch_birthday.ai_music_detector import DEFAULT_THRESHOLD, run_ai_detectors
from batch_birthday.humanize_audio import humanize_mp3
from batch_deephouse.extend_mix import build_crossfade_long_mix, probe_duration_sec
from batch_deephouse.haya_recipe2 import (
    RECIPE2_BPM,
    RECIPE2_CROSSFADE_SEC,
    RECIPE2_DURATION,
    RECIPE2_HANAN_HOOK,
    RECIPE2_HANAN_SEED,
)
from batch_deephouse.paths import OUTPUT_DIR

SLUG = "hanan"
TARGET_35 = 35 * 60


def _harden_long(src: Path, dst: Path, *, slug: str) -> float:
    """Stealth-harden; pick pitch rate via mid excerpts for low AI score."""
    preferred = stealth_pitch_rate_for(slug)
    candidates = [preferred, *[r for r in STEALTH_PITCH_RATES if r != preferred]]
    best_rate, best_ai = preferred, 1.0
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        excerpt = tmp / "ex.mp3"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                "90",
                "-t",
                "90",
                "-i",
                str(src),
                "-c:a",
                "libmp3lame",
                "-b:a",
                "192k",
                str(excerpt),
            ],
            check=True,
            capture_output=True,
        )
        for rate in candidates:
            cand = tmp / f"s_{rate:.4f}.mp3"
            apply_stealth_mp3(excerpt, cand, pitch_rate=rate)
            dets = run_ai_detectors(cand, threshold=DEFAULT_THRESHOLD)
            ai = dets[0].ai_probability if dets else 1.0
            print(f"  stealth rate={rate:.4f} ai≈{ai:.4f}")
            if ai < best_ai:
                best_ai, best_rate = ai, rate
            if ai <= STEALTH_AI_TARGET:
                break
        apply_stealth_mp3(src, dst, pitch_rate=best_rate)
        fin_ex = tmp / "final_ex.mp3"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                "120",
                "-t",
                "60",
                "-i",
                str(dst),
                "-c:a",
                "libmp3lame",
                "-b:a",
                "192k",
                str(fin_ex),
            ],
            check=True,
            capture_output=True,
        )
        dets = run_ai_detectors(fin_ex, threshold=DEFAULT_THRESHOLD)
        if dets:
            best_ai = dets[0].ai_probability
    return float(best_ai)


def main() -> None:
    """Build stealth 35-min from approved 3-min; leave only that MP3 + recipe meta."""
    out_dir = OUTPUT_DIR / SLUG
    three = out_dir / f"{SLUG}_3min.mp3"
    if not three.is_file():
        raise FileNotFoundError(f"Approved 3-min missing: {three}")

    # Re-humanize 3-min once more for lowest AI before looping.
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        three_human = tmp / "three_human.mp3"
        three_stealth = tmp / "three_stealth.mp3"
        humanize_mp3(three, three_human, style="distribute", bpm=RECIPE2_BPM)
        ai3 = _harden_long(three_human, three_stealth, slug=f"{SLUG}_3min")
        print(f"3min stealth ai≈{ai3:.4f}")

        raw_long = tmp / "long_raw.mp3"
        human_long = tmp / "long_human.mp3"
        final_tmp = tmp / "long_final.mp3"
        build_crossfade_long_mix(
            three_stealth,
            raw_long,
            target_sec=float(TARGET_35),
            crossfade_sec=RECIPE2_CROSSFADE_SEC,
            fade_in_sec=6.0,
            fade_out_sec=12.0,
        )
        print(f"looped → {probe_duration_sec(raw_long):.1f}s xf={RECIPE2_CROSSFADE_SEC}s")
        humanize_mp3(raw_long, human_long, style="distribute", bpm=RECIPE2_BPM)
        ai35 = _harden_long(human_long, final_tmp, slug=f"{SLUG}_35min")
        print(f"35min stealth ai≈{ai35:.4f}")

        # Wipe folder; keep only the 35-min master + small recipe sidecar.
        for child in list(out_dir.iterdir()):
            if child.is_file():
                child.unlink()
            elif child.is_dir():
                shutil.rmtree(child)

        final = out_dir / f"{SLUG}_35min.mp3"
        shutil.copy2(final_tmp, final)

        # Also stash approved 3-min stealth inside work (not cluttering song folder)
        # — user asked only 35min in folder. Recipe meta holds recreate info.
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
            "ai_score_approx": ai35,
            "ai_score_3min_approx": ai3,
            "notes": (
                "Approved Hanan Recipe 2: grid-lock + equal short chorus. "
                "35min = smooth acrossfade loop of stealth 3min master."
            ),
        }
        (out_dir / f"{SLUG}_recipe2.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        # Keep a copy of the approved 3-min under _continue_work for future re-loops
        archive = OUTPUT_DIR / "_recipe2_sources"
        archive.mkdir(parents=True, exist_ok=True)
        shutil.copy2(three_stealth, archive / f"{SLUG}_3min_recipe2.mp3")

    print(f"DONE {final} ({meta['duration_sec']/60:.1f} min) ai≈{ai35:.4f}")
    print(f"Recipe 2 source archived: _recipe2_sources/{SLUG}_3min_recipe2.mp3")


if __name__ == "__main__":
    main()
