"""Generate Layl + Qurb — signature recipe with sticky earworm motifs."""

from __future__ import annotations

import json
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.haya_signature_recipe import (
    build_signature_lyrics,
    build_signature_payload,
    master_signature_mp3,
)
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"

# Each song: one short addictive motif that returns intro→chorus→break→outro.
SONGS = [
    {
        "slug": "layl",
        "title": "Layl",
        "hook": "يا ليل تعال",
        "hook_lines": ["يا ليل تعال", "خليني معك"],
        "shape": "phrase",
        "seed": 98101,
        "motif_note": (
            "sticky vocal phrase 'يا ليل تعال' + matching 3-note dry oud answer "
            "that returns every chorus and in the break"
        ),
        "color_note": (
            "intimate close-mic, firmer night-drive kick, deeper warm sub, "
            "oud answers the earworm in gaps"
        ),
        "verse1": [
            "الليل يطول عليّا",
            "والدنيا ساكتة",
            "قلبي ينادي بهدوء",
            "وصوتك في بالي",
        ],
        "verse2": [
            "كل نبضة تقول",
            "قرب لي الليلة",
            "والطريق فاضي",
            "ونظرة تبقيني",
        ],
    },
    {
        "slug": "qurb",
        "title": "Qurb",
        "hook": "قرب لي",
        "hook_lines": ["قرب لي", "لا تبعد الليلة"],
        "shape": "call",
        "seed": 98212,
        "motif_note": (
            "call-and-response earworm: vocal 'قرب لي' answered by a soft "
            "kick+sub figure and dry oud reply — same motif every chorus"
        ),
        "color_note": (
            "warmer emotional vocal, slightly deeper pads, unique call motif "
            "not shared with Layl"
        ),
        "verse1": [
            "مسافة بينا تقل",
            "والنبض يقرب",
            "خليك جنبي بهدوء",
            "والدنيا تمشي",
        ],
        "verse2": [
            "كل لحن ينادي",
            "يا قرب بلطف",
            "والعود يرد",
            "ولحن يبقى معي",
        ],
    },
]


def generate_song(spec: dict) -> Path:
    """Generate one signature song with a sticky repeating earworm."""
    slug = spec["slug"]
    out_dir = OUTPUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    lyrics = build_signature_lyrics(
        hook_lines=spec["hook_lines"],
        verse1=spec["verse1"],
        verse2=spec["verse2"],
        shape=spec["shape"],
    )
    (out_dir / "lyrics.txt").write_text(lyrics, encoding="utf-8")
    raw = out_dir / f"{slug}.mp3"
    payload = build_signature_payload(
        hook=spec["hook"],
        slug=slug,
        lyrics=lyrics,
        seed=spec["seed"],
        color_note=spec["color_note"],
        motif_note=spec["motif_note"],
    )
    print(
        f"GENERATE {slug} earworm='{spec['hook']}' "
        f"shape={spec['shape']} seed={spec['seed']}"
    )
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
        "hook_lines": spec["hook_lines"],
        "lyric_shape": spec["shape"],
        "motif_note": spec["motif_note"],
        "bpm": 110,
        "key_scale": "A minor",
        "duration_sec": 60,
        "recipe": "haya_signature_recipe (earworm motif)",
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
    """Generate Layl + Qurb with sticky earworm motifs."""
    for spec in SONGS:
        generate_song(spec)
    print("DONE earworm pair: layl, qurb")


if __name__ == "__main__":
    main()
