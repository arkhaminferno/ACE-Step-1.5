"""Scaffold a clean Arabic stem dataset (JSON + lyrics only — you add real .mp3).

Do NOT train on ACE-Step-generated audio — that reinforces bad timbres.
Source dry real / library recordings instead (see STEM_SOURCE_GUIDE.md).

Usage (from repo root):
  PYTHONPATH=. python -m batch_deephouse.datasets.scaffold_arabic_stems
  PYTHONPATH=. python -m batch_deephouse.datasets.scaffold_arabic_stems --force
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

# Fresh dataset root (old oud/ney mp3s stay in arabic_house_dataset/ — do not mix).
DEFAULT_OUT = (
    Path(__file__).resolve().parent / "arabic_house_dataset_v2"
)

# basename → caption fields. User drops matching .mp3 next to these files.
SLOTS: list[dict[str, object]] = [
    # --- oud (5) ---
    {"id": "oud_bayati_108_01", "caption": "Dry close-mic acoustic oud solo, Maqam Bayati, warm wooden plucks, authentic Middle Eastern lute, NOT guzheng NOT pipa", "bpm": 108, "key": "D minor"},
    {"id": "oud_rast_108_01", "caption": "Dry close-mic acoustic oud solo, Maqam Rast, bright joyful phrases, authentic oud, NOT guzheng", "bpm": 108, "key": "C major"},
    {"id": "oud_hijaz_108_01", "caption": "Dry close-mic acoustic oud solo, Maqam Hijaz, expressive slides, authentic oud", "bpm": 108, "key": "D minor"},
    {"id": "oud_nahawand_100_01", "caption": "Dry acoustic oud melody, Maqam Nahawand, nostalgic contour, close-mic", "bpm": 100, "key": "A minor"},
    {"id": "oud_ostinato_108_01", "caption": "Dry acoustic oud repeating ostinato motif on grid, Maqam Bayati, house-friendly pocket", "bpm": 108, "key": "D minor"},
    # --- qanun (5) ---
    {"id": "qanun_rast_108_01", "caption": "Classical Arabic qanun arpeggios, Maqam Rast, sparkling plucked zither, authentic qanun, NOT guzheng NOT harp wall NOT piano", "bpm": 108, "key": "C major"},
    {"id": "qanun_bayati_108_01", "caption": "Sparse classical qanun motif, Maqam Bayati, bright short arpeggios, authentic qanun NOT guzheng", "bpm": 108, "key": "D minor"},
    {"id": "qanun_rast_108_02", "caption": "Qanun rhythmic sparkle pattern, Maqam Rast, dry room, Arabic qanun only", "bpm": 108, "key": "C major"},
    {"id": "qanun_hijaz_100_01", "caption": "Qanun melodic phrase, Maqam Hijaz, clear plucks, authentic Arabic qanun", "bpm": 100, "key": "D minor"},
    {"id": "qanun_ostinato_108_01", "caption": "Qanun looping house-friendly ostinato, Maqam Rast, sparse not busy", "bpm": 108, "key": "C major"},
    # --- violin (5) ---
    {"id": "violin_bayati_108_01", "caption": "Warm Arabic violin solo, Maqam Bayati, legato slides, lyrical, NOT erhu NOT harsh screech", "bpm": 108, "key": "D minor"},
    {"id": "violin_rast_108_01", "caption": "Bright Arabic violin hook melody, Maqam Rast, emotive legato, dry close-mic", "bpm": 108, "key": "C major"},
    {"id": "violin_hijaz_100_01", "caption": "Arabic violin expressive phrase, Maqam Hijaz, slight vibrato, warm tone", "bpm": 100, "key": "D minor"},
    {"id": "violin_nahawand_108_01", "caption": "Arabic violin nostalgic line, Maqam Nahawand, singing legato", "bpm": 108, "key": "A minor"},
    {"id": "violin_counter_108_01", "caption": "Arabic violin short counter-melody motif on grid, Maqam Bayati", "bpm": 108, "key": "D minor"},
    # --- ney (4) ---
    {"id": "ney_hijaz_108_01", "caption": "Breathy Arabic ney flute solo, Maqam Hijaz, airy sparse phrases, NOT saxophone", "bpm": 108, "key": "D minor"},
    {"id": "ney_bayati_100_01", "caption": "Soft Arabic ney flute fills, Maqam Bayati, intimate breathy tone", "bpm": 100, "key": "D minor"},
    {"id": "ney_rast_108_01", "caption": "Arabic ney flute, Maqam Rast, gentle sustained phrases, sparse", "bpm": 108, "key": "C major"},
    {"id": "ney_break_90_01", "caption": "Sparse airy ney flute breakdown color, Maqam Nahawand, soft and breathy", "bpm": 90, "key": "A minor"},
    # --- santur (3) ---
    {"id": "santur_rast_108_01", "caption": "Bright hammered santur sparkle, Maqam Rast, rhythmic motif, NOT piano NOT guzheng", "bpm": 108, "key": "C major"},
    {"id": "santur_bayati_108_01", "caption": "Santur melodic sparkle, Maqam Bayati, dry short hits", "bpm": 108, "key": "D minor"},
    {"id": "santur_ostinato_108_01", "caption": "Santur double-time sparkle ostinato for deep house, Maqam Rast", "bpm": 108, "key": "C major"},
    # --- perc (4) ---
    {"id": "darbuka_tek_108_01", "caption": "Dry darbuka dum-tek loop, Arabic goblet drum, tight attack, 108 BPM pocket, minimal room", "bpm": 108, "key": "C major"},
    {"id": "darbuka_fill_108_01", "caption": "Darbuka fill pattern, dry close-mic, house-friendly accents", "bpm": 108, "key": "C major"},
    {"id": "riq_pulse_108_01", "caption": "Soft riq frame-drum pulse, light jingles, Arabic percussion, subtle", "bpm": 108, "key": "C major"},
    {"id": "tabla_light_108_01", "caption": "Light tabla groove accents under four-on-floor feel, dry, not busy", "bpm": 108, "key": "C major"},
    # --- house bed (5) ---
    {"id": "kick_four_on_floor_108_01", "caption": "Four-on-the-floor deep house kick drum loop, punchy mono, 108 BPM, dry", "bpm": 108, "key": "C major"},
    {"id": "sub_bass_108_01", "caption": "Warm mono sub bass sine loop sidechain-ready, 108 BPM deep house, no mid clutter", "bpm": 108, "key": "C major"},
    {"id": "hats_swing_108_01", "caption": "Swung closed hi-hat loop, slight groove, deep house, 108 BPM, dry", "bpm": 108, "key": "C major"},
    {"id": "pad_lush_108_01", "caption": "Lush warm atmospheric synth pad, soft evolving chords, deep house night mood, 108 BPM", "bpm": 108, "key": "A minor"},
    {"id": "pad_bright_rast_108_01", "caption": "Bright warm pad bed suggesting Maqam Rast colour, soft, deep house, 108 BPM", "bpm": 108, "key": "C major"},
    # --- experiment extras (4) ---
    {"id": "pluck_soft_108_01", "caption": "Soft synthetic pluck motif, deep house ear candy, dry short decay, 108 BPM", "bpm": 108, "key": "C major"},
    {"id": "epiano_stabs_108_01", "caption": "Filtered electric-piano chord stabs only, deep house, short and rhythmic, NOT concert piano solo", "bpm": 108, "key": "A minor"},
    {"id": "guitar_reply_108_01", "caption": "Sparse dry acoustic guitar reply phrases, Middle Eastern flavour, gaps only, 108 BPM", "bpm": 108, "key": "D minor"},
    {"id": "buzuq_bayati_108_01", "caption": "Dry buzuq (long-neck lute) melodic phrases, Maqam Bayati, authentic, close-mic", "bpm": 108, "key": "D minor"},
]


def _lyrics_for(slot_id: str) -> str:
    """Return instrumental lyrics sidecar text."""
    name = slot_id.split("_")[0]
    return f"[Instrumental]\n(dry {name} only — no vocals)\n"


def write_slot(out_dir: Path, slot: dict[str, object], *, force: bool) -> None:
    """Write json + lyrics for one stem slot."""
    stem_id = str(slot["id"])
    json_path = out_dir / f"{stem_id}.json"
    lyrics_path = out_dir / f"{stem_id}.lyrics.txt"
    if json_path.exists() and not force:
        return
    payload = {
        "caption": slot["caption"],
        "bpm": slot["bpm"],
        "keyscale": slot["key"],
        "timesignature": "4",
        "language": "unknown",
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lyrics_path.write_text(_lyrics_for(stem_id), encoding="utf-8")


def main() -> int:
    """Scaffold v2 Arabic dataset slots."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--force", action="store_true", help="Overwrite existing json/lyrics")
    args = parser.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    for slot in SLOTS:
        write_slot(out, slot, force=args.force)
    readme = out / "README.md"
    if not readme.exists() or args.force:
        readme.write_text(
            "# Arabic house dataset v2 (fresh)\n\n"
            "JSON + lyrics slots are ready. **Add a matching `.mp3` for each id.**\n\n"
            "Do **not** use ACE-Step-generated audio as stems.\n"
            "See `STEM_SOURCE_GUIDE.md` in this folder.\n\n"
            f"Slots: **{len(SLOTS)}** — fill as many as you can (aim 40+).\n"
            "Train with:\n"
            "```bash\n"
            "AUDIO_DIR=batch_deephouse/datasets/arabic_house_dataset_v2 \\\n"
            "  ./scripts/train_project_adapter.sh arabic all\n"
            "```\n",
            encoding="utf-8",
        )
    print(f"Scaffolded {len(SLOTS)} slots → {out}")
    print("Next: add real dry .mp3 files with the same basenames.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
