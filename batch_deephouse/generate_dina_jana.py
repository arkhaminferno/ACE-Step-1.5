"""Generate Dina + Jana with locked HAYA signature recipe (distinct colors)."""

from __future__ import annotations

import json
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.haya_signature_recipe import (
    build_signature_payload,
    build_simple_lyrics,
    master_signature_mp3,
)
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"

SONGS = [
    {
        "slug": "dina",
        "title": "Dina",
        "hook": "دينا دينا",
        "seed": 94833,
        "color_note": (
            "intimate Rima-lane vocal, warm oud replies in gaps, "
            "slightly softer pads, unique sticky melodic motif"
        ),
        "verse1": [
            "دينا في بالي الليلة",
            "تمشي مع دقات الطريق",
            "والليل هادي",
            "وإنتِ بعيدة عني",
        ],
        "verse2": [
            "كل نفس ينادي",
            "يا دينا اقتربي",
            "والعود يرد بلطف",
            "ونظرة تخلّيني",
        ],
    },
    {
        "slug": "jana",
        "title": "Jana",
        "hook": "جنى جنى",
        "seed": 95944,
        "color_note": (
            "slightly more driving night-drive hats, deeper sub presence, "
            "sparser oud, emotional present vocal, distinct chorus melody"
        ),
        "verse1": [
            "جنى على آخر الليل",
            "نور خفيف في عينيّا",
            "والدقات ثابتة",
            "وأنت لسه بعيد",
        ],
        "verse2": [
            "كل جنى تقول",
            "ارجع لي بهدوء",
            "والدرب فاضي",
            "ولحن يبقى معي",
        ],
    },
]


def generate_song(spec: dict) -> Path:
    """Generate one signature song."""
    slug = spec["slug"]
    out_dir = OUTPUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    lyrics = build_simple_lyrics(
        hook=spec["hook"],
        verse1=spec["verse1"],
        verse2=spec["verse2"],
    )
    (out_dir / "lyrics.txt").write_text(lyrics, encoding="utf-8")
    raw = out_dir / f"{slug}.mp3"
    payload = build_signature_payload(
        hook=spec["hook"],
        slug=slug,
        lyrics=lyrics,
        seed=spec["seed"],
        color_note=spec["color_note"],
    )
    print(f"GENERATE {slug} signature seed={spec['seed']}")
    meta = generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=raw,
        label=slug,
    )
    listen, ai_prob = master_signature_mp3(raw, slug=slug)
    info = {
        "title": spec["title"],
        "slug": slug,
        "hook": spec["hook"],
        "bpm": 110,
        "key_scale": "A minor",
        "duration_sec": 60,
        "recipe": "haya_signature_recipe",
        "color_note": spec["color_note"],
        "thinking": True,
        "seed": spec["seed"],
        "task_id": meta["task_id"],
        "listen": str(listen),
        "ai_score": ai_prob,
    }
    (out_dir / f"{slug}.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK {slug} → {listen} ai={ai_prob:.4f}")
    return listen


def main() -> None:
    """Generate Dina and Jana."""
    for spec in SONGS:
        generate_song(spec)
    print("DONE: dina, jana")


if __name__ == "__main__":
    main()
