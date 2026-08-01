"""Generate five new HAYA songs with the approved natural_vocal_recipe."""

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

# Five fresh night-drive titles (not in the approved 7 / rejected set).
SONGS = [
    {
        "slug": "shawq",
        "title": "Shawq",
        "hook": "شوق شوق",
        "seed": 85101,
        "verse1": [
            "شوق هادي في صدري",
            "يمشي مع دقات الليل",
            "والطريق فاضي",
            "وأنت في بالي",
        ],
        "verse2": [
            "كل شوق ينادي",
            "ارجع لي بلطف",
            "واللحن يلفّني",
            "ونظرة تبقيني",
        ],
    },
    {
        "slug": "sahr",
        "title": "Sahr",
        "hook": "سهر سهر",
        "seed": 86212,
        "verse1": [
            "سهرت والمدينة نايمة",
            "والقلب يسأل عنك",
            "والنبض خفيف",
            "والليل يسمعني",
        ],
        "verse2": [
            "كل سهر يقول",
            "قرب لي بهدوء",
            "والدنيا ساكتة",
            "ولحن يبقى معي",
        ],
    },
    {
        "slug": "najm",
        "title": "Najm",
        "hook": "نجم نجم",
        "seed": 87323,
        "verse1": [
            "نجم بعيد في السما",
            "يشبه عيوني عليك",
            "والليل طويل",
            "وأنا لسه هنا",
        ],
        "verse2": [
            "كل نجم يقول",
            "ارجع لي بلطف",
            "والصوت هادي",
            "واللحن يبقيني",
        ],
    },
    {
        "slug": "amal",
        "title": "Amal",
        "hook": "أمل أمل",
        "seed": 88434,
        "verse1": [
            "أمل خفيف في قلبي",
            "مثل ضوء بعيد",
            "والريح باردة",
            "وأنت بعيد عني",
        ],
        "verse2": [
            "كل أمل ينادي",
            "قرب لي بهدوء",
            "واللحن يلفّني",
            "ونظرة تبقيني",
        ],
    },
    {
        "slug": "nida",
        "title": "Nida",
        "hook": "نداء نداء",
        "seed": 89545,
        "verse1": [
            "نداء هادي من قلبي",
            "يمشي في الليل الطويل",
            "والمدينة نايمة",
            "وأنا أناديلك",
        ],
        "verse2": [
            "كل نداء يقول",
            "ارجع لي بلطف",
            "والدنيا ساكتة",
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
        "recipe": "natural_vocal_recipe (same as approved Hawa/Rouh/Ward)",
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
    """Generate all five songs sequentially."""
    for spec in SONGS:
        generate_song(spec)
    print("DONE five songs:", ", ".join(s["slug"] for s in SONGS))


if __name__ == "__main__":
    main()
