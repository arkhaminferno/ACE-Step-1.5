"""Generate four new HAYA songs with the approved natural_vocal_recipe."""

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

# Fresh titles — not in approved 7 or prior rejected set.
SONGS = [
    {
        "slug": "ghayeb",
        "title": "Ghayeb",
        "hook": "غايب غايب",
        "seed": 81201,
        "verse1": [
            "وأنت غايب عني",
            "والليل طويل عليّ",
            "كل نبضة تقول",
            "ارجع لي بهدوء",
        ],
        "verse2": [
            "غيابك يسألني",
            "متى تعود بلطف",
            "لحن خفيف يلفّني",
            "وباسمك أبقى هنا",
        ],
    },
    {
        "slug": "ouyoun",
        "title": "Ouyoun",
        "hook": "عيون عيون",
        "seed": 82312,
        "verse1": [
            "عيونك في بالي",
            "تمشي مع دقات الليل",
            "والطريق فاضي",
            "وأنا بستناك",
        ],
        "verse2": [
            "كل نظرة تنادي",
            "قرب لي بهدوء",
            "والدنيا ساكتة",
            "ولحن يبقى معي",
        ],
    },
    {
        "slug": "sabr",
        "title": "Sabr",
        "hook": "صبر صبر",
        "seed": 83420,
        "verse1": [
            "صبري يطول معاك",
            "والقلب يسأل عنك",
            "والنبض خفيف",
            "والليل يسمعني",
        ],
        "verse2": [
            "كل صبر ينادي",
            "ارجع لي بلطف",
            "واللحن يلفّني",
            "ونظرة تبقيني",
        ],
    },
    {
        "slug": "shams",
        "title": "Shams",
        "hook": "شمس شمس",
        "seed": 84531,
        "verse1": [
            "شمس بعيدة في قلبي",
            "تدفيني بالليل",
            "والريح باردة",
            "وأنت لسه بعيد",
        ],
        "verse2": [
            "كل شمس تقول",
            "قرب لي بهدوء",
            "والدنيا هادية",
            "ولحن يبقى معي",
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
        thinking=False,
    )
    # batch=2 OOMs on VAE decode for long audio on 24GB Mac — force one sample.
    payload["batch_size"] = 1
    print(f"GENERATE {slug} seed={spec['seed']} thinking=False batch=1")
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
        "recipe": "natural_vocal_recipe (batch=1, DiT-only; MLX VAE off)",
        "thinking": False,
        "batch_size": 1,
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
    """Generate all four songs sequentially."""
    for spec in SONGS:
        generate_song(spec)
    print("DONE four songs:", ", ".join(s["slug"] for s in SONGS))


if __name__ == "__main__":
    main()
