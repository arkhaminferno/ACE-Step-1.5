"""Hanan 3-min — grid-locked vocal (hook syllables on the kick)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.extend_mix import probe_duration_sec
from batch_deephouse.haya_signature_recipe import (
    RIMA_COLOR,
    build_signature_payload,
    master_signature_mp3,
)
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"
SLUG = "hanan"
# Slightly slower pocket = more room for Arabic syllables on the grid.
BPM = 108
DURATION = 180
# Fresh seed near the approved Hanan/Hawa family.
SEED = 81440
# Phrase hook — clearer rhythm than rushed "حنان حنان".
HOOK = "يا حنان"

LYRICS = f"""[Intro]
(soft female hum mmm ~4–8s — light pad, almost no kick)
(kick enters by 8 seconds — vocal stays on the grid)

[Verse]
في عيني حنان هادي
يلفّ القلب بلطف
والليل يسمعني
وأنت بعيد عني

[Chorus]
يا حنان
(on the kick)
يا حنان
(on the kick)
يا حنان
(on the downbeat)

[Verse]
كل نفس يقول
ارجع لي بهدوء
والحنان يحضنني
ولحن يبقى معي

[Chorus]
يا حنان
(on the kick)
يا حنان
(on the kick)
يا حنان
يا حنان

[Bridge]
(soft oud — vocal rests on pocket)
يا حنان
(on the kick)

[Chorus]
يا حنان
(on the kick)
يا حنان
(on the kick)
يا حنان

[Verse]
الطريق فاضي الليلة
ونبض يسأل عنك
قرب لي شوي
والدنيا تمشي

[Chorus]
يا حنان
(on the kick)
يا حنان
(on the kick)

[Outro]
يا حنان
(soft natural fade — still on beat)
"""


def main() -> None:
    """Generate one grid-locked Hanan 3-min master for approval."""
    out_dir = OUTPUT_DIR / SLUG
    out_dir.mkdir(parents=True, exist_ok=True)

    # Archive previous off-grid 3-min if present.
    old = out_dir / f"{SLUG}_3min.mp3"
    if old.is_file():
        archived = out_dir / f"{SLUG}_3min_offgrid.mp3"
        shutil.move(str(old), str(archived))
        print(f"archived previous → {archived.name}")

    (out_dir / "lyrics_3min.txt").write_text(LYRICS, encoding="utf-8")
    raw = out_dir / f"{SLUG}_3min_raw.mp3"
    payload = build_signature_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=LYRICS,
        seed=SEED,
        bpm=BPM,
        duration=DURATION,
        grid_lock=True,
        color_note=(
            f"{RIMA_COLOR}; tight vocal pocket — every 'حنان' syllable on the kick, "
            "no rushed chanting, human but quantized to the groove"
        ),
        motif_note="ya-hanan phrase sung on-kick as the sticky earworm",
    )
    print(f"GENERATE hanan 3min GRID-LOCK bpm={BPM} seed={SEED} hook='{HOOK}'")
    generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=raw,
        label="hanan_3min_grid",
    )
    listen, ai = master_signature_mp3(raw, slug=f"{SLUG}_3min", bpm=BPM)
    three = out_dir / f"{SLUG}_3min.mp3"
    shutil.copy2(listen, three)
    info = {
        "slug": SLUG,
        "hook": HOOK,
        "bpm": BPM,
        "duration_sec": probe_duration_sec(three),
        "seed": SEED,
        "recipe": "signature + VOCAL_GRID_LOCK (3min approval)",
        "listen": str(three),
        "ai_score": ai,
    }
    (out_dir / f"{SLUG}_3min.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK → {three} ({info['duration_sec']:.1f}s) ai≈{ai:.4f}")
    print("Listen and approve before any 35min loop.")


if __name__ == "__main__":
    main()
