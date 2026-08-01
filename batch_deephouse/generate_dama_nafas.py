"""Generate two HAYA songs with the approved Hawa recipe."""

from __future__ import annotations

import json
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.natural_vocal_recipe import (
    build_simple_lyrics,
    build_text2music_payload,
)

API_BASE = "http://127.0.0.1:8001"
OUT_ROOT = Path("/Users/infy/Downloads/ACE-Step-1.5/batch_deephouse/output")

SONGS = [
    {
        "slug": "dama",
        "title": "Dama",
        "hook": "دمعة دمعة",
        "seed": 82411,
        "verse1": [
            "في عيني دمعة هادية",
            "تمشي ببطء على خدي",
            "والليل يشوفني",
            "وأنت بعيد عني",
        ],
        "verse2": [
            "كل دمعة تقول",
            "ارجع لي بهدوء",
            "والقلب يسمعني",
            "ولحن يبقى معي",
        ],
    },
    {
        "slug": "nafas",
        "title": "Nafas",
        "hook": "نفس نفس",
        "seed": 83522,
        "verse1": [
            "خذ نفس واهدأ",
            "الليل طويل عليّ",
            "والنبض يمشي معي",
            "وأنت في بالي",
        ],
        "verse2": [
            "كل نفس ينادي",
            "قرب لي بهدوء",
            "والدنيا ساكتة",
            "واللحن يبقيني",
        ],
    },
]


def generate_song(spec: dict) -> Path:
    """Generate one song and write master + metadata."""
    slug = spec["slug"]
    out_dir = OUT_ROOT / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    lyrics = build_simple_lyrics(
        hook=spec["hook"],
        verse1=spec["verse1"],
        verse2=spec["verse2"],
    )
    (out_dir / "lyrics.txt").write_text(lyrics, encoding="utf-8")
    out_path = out_dir / f"{slug}.mp3"
    payload = build_text2music_payload(
        hook=spec["hook"],
        slug=slug,
        lyrics=lyrics,
        seed=spec["seed"],
        thinking=True,
    )
    print(f"GENERATE {slug} seed={spec['seed']} thinking=True")
    meta = generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=out_path,
        label=slug,
    )
    info = {
        "title": spec["title"],
        "slug": slug,
        "hook": spec["hook"],
        "bpm": 108,
        "key_scale": "A minor",
        "duration_sec": 120,
        "engine": "ACE-Step acestep-v15-turbo text2music",
        "recipe": "natural_vocal_recipe (same as approved Hawa)",
        "thinking": True,
        "seed": spec["seed"],
        "task_id": meta["task_id"],
    }
    (out_dir / f"{slug}.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK {out_path}")
    return out_path


def main() -> None:
    """Generate Dama and Nafas sequentially."""
    for spec in SONGS:
        generate_song(spec)
    print("DONE both songs")


if __name__ == "__main__":
    main()
