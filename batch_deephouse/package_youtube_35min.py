"""Package all locked HAYA songs as 35-min humanized YouTube masters.

For each song folder under ``batch_deephouse/output``:
  1. Crossfade-extend the approved ``*_upload.mp3`` to 35 minutes
  2. Distribute-humanize + stealth-harden (low AI score)
  3. Delete every other file/folder in that song dir — keep only the 35-min MP3
"""

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
from batch_deephouse.paths import OUTPUT_DIR

TARGET_SEC = 35 * 60
BPM = 110
# Locked catalog currently in output/
SONGS = [
    "hanan",
    "lama",
    "layl",
    "luma",
    "mira",
    "noura",
    "qamar",
    "rana",
    "rima",
    "safa",
]


def _pick_source(out_dir: Path, slug: str) -> Path:
    """Prefer the current upload master (full length when available)."""
    candidates = [
        out_dir / f"{slug}_upload.mp3",
        out_dir / f"{slug}_human.mp3",
        out_dir / f"{slug}_full.mp3",
        out_dir / f"{slug}_60s_upload.mp3",
        out_dir / f"{slug}.mp3",
    ]
    for path in candidates:
        if path.is_file() and path.stat().st_size > 10_000:
            return path
    raise FileNotFoundError(f"No source MP3 for {slug} in {out_dir}")


def _extract_excerpt(
    src: Path,
    dst: Path,
    *,
    start_sec: float = 45.0,
    dur_sec: float = 90.0,
) -> Path:
    """Cut a short mid excerpt for fast AI scoring."""
    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        str(start_sec),
        "-t",
        str(dur_sec),
        "-i",
        str(src),
        "-c:a",
        "libmp3lame",
        "-b:a",
        "192k",
        str(dst),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return dst


def _measure_ai(mp3: Path) -> float:
    """Return primary fakeprint AI probability."""
    detections = run_ai_detectors(mp3, threshold=DEFAULT_THRESHOLD)
    return detections[0].ai_probability if detections else 1.0


def _harden_long(src: Path, dst: Path, *, slug: str) -> float:
    """Stealth-harden a long mix; pick pitch rate via excerpt scores only."""
    preferred = stealth_pitch_rate_for(slug)
    candidates = [preferred]
    for rate in STEALTH_PITCH_RATES:
        if rate not in candidates:
            candidates.append(rate)

    best_rate = preferred
    best_ai = 1.0
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        excerpt_src = tmp / "excerpt_src.mp3"
        _extract_excerpt(src, excerpt_src)
        for rate in candidates:
            cand = tmp / f"stealth_{rate:.4f}.mp3"
            apply_stealth_mp3(excerpt_src, cand, pitch_rate=rate)
            ai_prob = _measure_ai(cand)
            print(f"  stealth rate={rate:.4f} ai≈{ai_prob:.4f}")
            if ai_prob < best_ai:
                best_ai = ai_prob
                best_rate = rate
            if ai_prob <= STEALTH_AI_TARGET:
                break
        apply_stealth_mp3(src, dst, pitch_rate=best_rate)
    return best_ai


def _clean_song_dir(out_dir: Path, keep: Path) -> None:
    """Remove everything in *out_dir* except the keep file."""
    keep = keep.resolve()
    for child in list(out_dir.iterdir()):
        if child.resolve() == keep:
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink(missing_ok=True)


def package_song(slug: str) -> dict:
    """Build one 35-min upload master and wipe other song-folder files."""
    out_dir = OUTPUT_DIR / slug
    if not out_dir.is_dir():
        raise FileNotFoundError(f"Missing song folder: {out_dir}")

    src = _pick_source(out_dir, slug)
    src_dur = probe_duration_sec(src)
    final_name = f"{slug}_35min.mp3"
    final = out_dir / final_name

    print(f"\n=== {slug} ===")
    print(f"source={src.name} ({src_dur:.1f}s) → {final_name}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        long_raw = tmp / f"{slug}_35_raw.mp3"
        long_human = tmp / f"{slug}_35_human.mp3"
        long_final = tmp / f"{slug}_35_final.mp3"

        build_crossfade_long_mix(
            src,
            long_raw,
            target_sec=float(TARGET_SEC),
            crossfade_sec=8.0 if src_dur >= 50 else 4.0,
        )
        print(f"  extended → {probe_duration_sec(long_raw):.1f}s")

        humanize_mp3(long_raw, long_human, style="distribute", bpm=BPM)
        print("  humanize distribute OK")

        ai_prob = _harden_long(long_human, long_final, slug=slug)
        print(f"  stealth OK ai≈{ai_prob:.4f}")

        # Move final in, then delete everything else in the song folder.
        if final.exists():
            final.unlink()
        shutil.copy2(long_final, final)

    _clean_song_dir(out_dir, final)
    dur = probe_duration_sec(final)
    meta = {
        "slug": slug,
        "file": str(final),
        "duration_sec": dur,
        "ai_score_approx": ai_prob,
        "source_was": src.name,
        "source_duration_sec": src_dur,
        "recipe": "35min crossfade + distribute humanize + stealth",
    }
    print(f"  KEEP {final.name} ({dur / 60:.1f} min) ai≈{ai_prob:.4f}")
    return meta


def main() -> None:
    """Package all locked songs for YouTube."""
    results = []
    for slug in SONGS:
        results.append(package_song(slug))
    summary = OUTPUT_DIR / "_youtube_35min_summary.json"
    summary.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nDONE {len(results)} songs. Summary: {summary}")
    for row in results:
        print(
            f"  {row['slug']}: {row['duration_sec'] / 60:.1f}min "
            f"ai≈{row['ai_score_approx']:.4f}"
        )


if __name__ == "__main__":
    main()
