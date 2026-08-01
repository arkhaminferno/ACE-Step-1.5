"""Regenerate all locked YouTube masters as continuous 35-min songs (no loop)."""

from __future__ import annotations

import json
import shutil
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
from batch_deephouse.continue_extend import elongate_to_target, extract_audio
from batch_deephouse.extend_mix import probe_duration_sec
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"
TARGET_SEC = 35 * 60
BPM = 110

# Seed length to cut from the old looped 35min (before the first restart).
SEED_SEC = {
    "hanan": 52.0,
    "lama": 52.0,
    "layl": 52.0,
    "luma": 168.0,
    "mira": 52.0,
    "noura": 52.0,
    "qamar": 52.0,
    "rana": 168.0,
    "rima": 52.0,
    "safa": 168.0,
}

SONGS = list(SEED_SEC.keys())


def _measure_ai(mp3: Path) -> float:
    """Primary fakeprint AI probability."""
    detections = run_ai_detectors(mp3, threshold=DEFAULT_THRESHOLD)
    return detections[0].ai_probability if detections else 1.0


def _extract_excerpt(src: Path, dst: Path) -> Path:
    """Mid excerpt for fast stealth scoring."""
    extract_audio(src, dst, start=60.0, duration=90.0)
    return dst


def _harden_long(src: Path, dst: Path, *, slug: str) -> float:
    """Pick stealth pitch via excerpt, apply once to full file."""
    preferred = stealth_pitch_rate_for(slug)
    candidates = [preferred, *[r for r in STEALTH_PITCH_RATES if r != preferred]]
    best_rate = preferred
    best_ai = 1.0
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        excerpt = tmp / "ex.mp3"
        _extract_excerpt(src, excerpt)
        for rate in candidates:
            cand = tmp / f"s_{rate:.4f}.mp3"
            apply_stealth_mp3(excerpt, cand, pitch_rate=rate)
            ai = _measure_ai(cand)
            print(f"  stealth rate={rate:.4f} ai≈{ai:.4f}")
            if ai < best_ai:
                best_ai = ai
                best_rate = rate
            if ai <= STEALTH_AI_TARGET:
                break
        apply_stealth_mp3(src, dst, pitch_rate=best_rate)
    return best_ai


def package_flowing_35min(slug: str) -> dict:
    """Continuous-extend one song to 35 min, humanize, replace folder contents."""
    out_dir = OUTPUT_DIR / slug
    looped = out_dir / f"{slug}_35min.mp3"
    if not looped.is_file():
        raise FileNotFoundError(f"Missing looped master: {looped}")

    work = OUTPUT_DIR / "_continue_work" / slug
    work.mkdir(parents=True, exist_ok=True)
    seed = work / "seed.mp3"
    raw_long = work / "flow_raw.mp3"
    human = work / "flow_human.mp3"
    final_tmp = work / "flow_final.mp3"
    final = out_dir / f"{slug}_35min.mp3"

    seed_sec = SEED_SEC[slug]
    if not seed.exists():
        # Cut seed from old loop BEFORE the first restart point.
        extract_audio(looped, seed, start=0.0, duration=seed_sec)
        # Move looped aside so we don't destroy the only copy mid-run.
        archived = work / f"{slug}_looped_archive.mp3"
        if not archived.exists():
            shutil.copy2(looped, archived)

    print(f"\n=== FLOW {slug} seed={seed_sec}s ===")
    elongate_to_target(
        seed,
        raw_long,
        api_base=API_BASE,
        target_sec=float(TARGET_SEC),
        seed=hash(slug) % 100_000,
        work_dir=work / "masters",
    )
    print(f"  raw flow {probe_duration_sec(raw_long):.1f}s")

    humanize_mp3(raw_long, human, style="distribute", bpm=BPM)
    ai = _harden_long(human, final_tmp, slug=slug)
    print(f"  stealth ai≈{ai:.4f}")

    # Replace folder: only the new flowing 35min remains.
    for child in list(out_dir.iterdir()):
        if child.is_file():
            child.unlink()
        elif child.is_dir():
            shutil.rmtree(child)
    shutil.copy2(final_tmp, final)

    meta = {
        "slug": slug,
        "file": str(final),
        "duration_sec": probe_duration_sec(final),
        "ai_score_approx": ai,
        "seed_sec": seed_sec,
        "recipe": "sliding-window repaint continuation + distribute + stealth",
    }
    print(f"  KEEP {final.name} ({meta['duration_sec'] / 60:.1f} min)")
    return meta


def main() -> None:
    """Regenerate all 10 songs as continuous 35-min masters."""
    results = []
    summary_path = OUTPUT_DIR / "_youtube_35min_summary.json"
    for slug in SONGS:
        results.append(package_flowing_35min(slug))
        summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nDONE flowing 35min for {len(results)} songs")
    for row in results:
        print(
            f"  {row['slug']}: {row['duration_sec'] / 60:.1f}min "
            f"ai≈{row['ai_score_approx']:.4f}"
        )


if __name__ == "__main__":
    main()
