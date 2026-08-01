"""Wait for flowing 35-min masters, then AE-render all locked YouTube videos."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from batch_deephouse.ae_titles import LOCKED_YOUTUBE_SLUGS
from batch_deephouse.extend_mix import probe_duration_sec
from batch_deephouse.paths import BATCH_ROOT, OUTPUT_DIR

TARGET_SEC = 35 * 60
# Flowing masters are continuous; looped archives were ~2100s but restart.
# Detect "done" via regenerate summary recipe string OR continue work final.
SUMMARY = OUTPUT_DIR / "_youtube_35min_summary.json"
CONTINUE_WORK = OUTPUT_DIR / "_continue_work"
POLL_SEC = 60


def _song_ready(slug: str) -> bool:
    """True when flowing 35-min master is finalized for *slug*."""
    if SUMMARY.is_file():
        try:
            rows = json.loads(SUMMARY.read_text(encoding="utf-8"))
            for row in rows:
                if (
                    row.get("slug") == slug
                    and "continuation" in str(row.get("recipe", ""))
                    and float(row.get("duration_sec", 0)) >= TARGET_SEC - 5
                ):
                    return True
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            pass

    final = OUTPUT_DIR / slug / f"{slug}_35min.mp3"
    meta = CONTINUE_WORK / slug / "continue_meta.json"
    # Finalized package removes work masters after replace; check summary first.
    # While regenerating, looped file still present — not ready until KEEP logged.
    flow_final = CONTINUE_WORK / slug / "flow_final.mp3"
    if flow_final.is_file() and probe_duration_sec(flow_final) >= TARGET_SEC - 5:
        # Not yet copied to output — wait for package step
        return False
    if final.is_file() and (CONTINUE_WORK / slug / "flow_raw.mp3").is_file():
        # After package_flowing copies final and cleans folder, flow_raw still in work
        try:
            if probe_duration_sec(final) >= TARGET_SEC - 5:
                # Heuristic: flowing recipe written to summary
                if SUMMARY.is_file():
                    rows = json.loads(SUMMARY.read_text(encoding="utf-8"))
                    return any(
                        r.get("slug") == slug
                        and "continuation" in str(r.get("recipe", ""))
                        for r in rows
                    )
        except (OSError, ValueError, json.JSONDecodeError):
            return False
    return False


def wait_for_all_audio() -> None:
    """Block until all locked songs have flowing 35-min masters."""
    print("Waiting for flowing 35-min masters...")
    while True:
        ready = [s for s in LOCKED_YOUTUBE_SLUGS if _song_ready(s)]
        print(f"  audio ready {len(ready)}/{len(LOCKED_YOUTUBE_SLUGS)}: {ready}")
        if len(ready) == len(LOCKED_YOUTUBE_SLUGS):
            return
        time.sleep(POLL_SEC)


def render_all_videos() -> int:
    """Run AE batch CLI for the locked catalog."""
    import os

    env = os.environ.copy()
    env["PYTHONPATH"] = str(BATCH_ROOT.parent)
    cmd = [
        sys.executable,
        str(BATCH_ROOT / "ae_batch_cli.py"),
        "--force",
    ]
    print("Starting AE batch render:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(BATCH_ROOT.parent), env=env, check=False)
    return int(result.returncode)


def main() -> int:
    """Wait for audio, render videos, exit with render status."""
    wait_for_all_audio()
    print("All flowing masters ready — rendering YouTube videos...")
    return render_all_videos()


if __name__ == "__main__":
    raise SystemExit(main())
