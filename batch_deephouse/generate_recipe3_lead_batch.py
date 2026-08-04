"""Generate 4 brand-new Recipe3 songs — one per lead (oud/ney/qanun/piano+oud)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.haya_recipe3 import (
    RECIPE3_BPM,
    RECIPE3_DURATION,
    build_recipe3_lyrics,
    build_recipe3_payload,
    master_recipe3_mp3,
)
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"

# Brand-new titles — not in launched HAYA catalog / not Nafas remixes.
SONGS: list[dict[str, object]] = [
    {
        "slug": "lujain",
        "hook": "يا لجين",
        "lead": "oud",
        "seed": 94101,
        "verse1": ["لجين تمشي بهدوء", "والليل على الدرب", "لحن العود يناديني", "وأنت في البال"],
        "verse2": ["خذني على النبض", "قبل ما يروح السكون", "نفس خفيف يلفّني", "والقلب يصفى"],
    },
    {
        "slug": "yasmin",
        "hook": "يا ياسمين",
        "lead": "ney",
        "seed": 94201,
        "verse1": ["ياسمين في الهوا", "والليل يبرد شوي", "ناي خفيف يناديني", "وأنت بعيد"],
        "verse2": ["خذني مع النَفَس", "قبل ما يروح العطر", "لحن هادي يلفّني", "والقلب يرتاح"],
    },
    {
        "slug": "farah",
        "hook": "يا فرح",
        "lead": "qanun",
        "seed": 94301,
        "verse1": ["فرحي خفيف الليلة", "والقمر قريب", "قانون يرد لي", "وأنت في الخاطر"],
        "verse2": ["خذني على اللحن", "قبل ما يروح الفرح", "نبض هادي يلفّني", "والليل يصفى"],
    },
    {
        "slug": "salma",
        "hook": "يا سلمى",
        "lead": "piano_oud",
        "seed": 94401,
        "verse1": ["سلمى في السكون", "والبيانو هادي", "عود يرد بلطف", "وأنت في البال"],
        "verse2": ["خذني على الهمس", "قبل ما يروح الليل", "لحن خفيف يلفّني", "والقلب يصفى"],
    },
]


def _cut_cues(final: Path, cues: Path) -> None:
    """Write quick listen clips (no autoplay)."""
    cues.mkdir(exist_ok=True)
    for name, start, dur in (
        ("01_intro.mp3", "0", "12"),
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


def generate_one(song: dict[str, object]) -> Path:
    """Generate one ORIGINAL Recipe3 song for its lead."""
    slug = str(song["slug"])
    hook = str(song["hook"])
    lead = str(song["lead"])
    seed = int(song["seed"])  # type: ignore[arg-type]
    verse1 = list(song["verse1"])  # type: ignore[arg-type]
    verse2 = list(song["verse2"])  # type: ignore[arg-type]

    out_dir = OUTPUT_DIR / slug
    sources = OUTPUT_DIR / "_recipe3_sources"
    out_dir.mkdir(parents=True, exist_ok=True)
    sources.mkdir(parents=True, exist_ok=True)

    lyrics = build_recipe3_lyrics(
        hook=hook, verse1=verse1, verse2=verse2, lead=lead
    )
    (out_dir / "lyrics_3min.txt").write_text(lyrics, encoding="utf-8")
    raw = sources / f"{slug}_3min_raw.mp3"
    payload = build_recipe3_payload(
        hook=hook,
        slug=slug,
        lyrics=lyrics,
        seed=seed,
        bpm=RECIPE3_BPM,
        duration=RECIPE3_DURATION,
        lead=lead,
        color_note=(
            f"ORIGINAL {slug} — Recipe3 {lead} heart; NOT a remix of any HAYA song"
        ),
    )
    print(f"GENERATE {slug} lead={lead} seed={seed} hook={hook}", flush=True)
    meta = generate_to_file(
        payload, api_base=API_BASE, api_key="", out_path=raw, label=f"{slug}-r3"
    )
    listen, ai = master_recipe3_mp3(raw, slug=f"{slug}_3min", bpm=RECIPE3_BPM)
    final = out_dir / f"{slug}_3min.mp3"
    final.write_bytes(listen.read_bytes())
    _cut_cues(final, out_dir / "cues")
    info = {
        "slug": slug,
        "lead": lead,
        "hook": hook,
        "seed": seed,
        "recipe": "haya_recipe3 ORIGINAL (not a HAYA remix)",
        "file": str(final.resolve()),
        "task_id": meta.get("task_id"),
        "ai_score": ai,
    }
    (out_dir / f"{slug}_recipe3.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("DONE", final, "ai", ai, flush=True)
    return final


def main() -> int:
    """Generate all four lead variants sequentially."""
    paths = [generate_one(s) for s in SONGS]
    print("ALL DONE", [str(p) for p in paths], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
