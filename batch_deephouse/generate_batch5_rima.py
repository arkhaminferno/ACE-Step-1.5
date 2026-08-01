"""Generate 5 Rima-lane songs — long instrument + female hum intro, then beat."""

from __future__ import annotations

import json
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.haya_signature_recipe import (
    RIMA_COLOR,
    build_signature_lyrics,
    build_signature_payload,
    master_signature_mp3,
)
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"

# Five unique earworms — soft instrument+hum open, then groove (not Name Name).
SONGS = [
    {
        "slug": "hiba",
        "title": "Hiba",
        "hook": "يا هبة الليلة",
        "hook_lines": ["يا هبة الليلة", "قرّبي شوي"],
        "seed": 100101,
        "motif_note": "sticky 'يا هبة الليلة' after long pad+oud+hum intro",
        "verse1": [
            "الليل يهمس بهدوء",
            "والنبض خفيف عليّا",
            "هبة في بالي",
            "والدنيا ساكتة",
        ],
        "verse2": [
            "كل لحن يقرب",
            "يا هبة بلطف",
            "والعود يرد",
            "ونظرة تخلّيني",
        ],
    },
    {
        "slug": "rana",
        "title": "Rana",
        "hook": "ارجعي لي",
        "hook_lines": ["ارجعي لي", "ما تبعدي الليلة"],
        "seed": 100212,
        "motif_note": "call phrase 'ارجعي لي' after instrument + soft mmm vocal open",
        "verse1": [
            "الطريق فاضي الليلة",
            "وصوتك بعيد",
            "قلبي ينادي بهدوء",
            "ورنا في خيالي",
        ],
        "verse2": [
            "كل كلمة تقول",
            "ارجعي لي بلطف",
            "والدقات ثابتة",
            "ولحن يبقى معي",
        ],
    },
    {
        "slug": "yara",
        "title": "Yara",
        "hook": "يا يارا وينك",
        "hook_lines": ["يا يارا وينك", "خليني أشوفك"],
        "seed": 100323,
        "motif_note": "earworm 'يا يارا وينك' after long oud+pad+hum open",
        "verse1": [
            "الليل طويل عليّا",
            "ويارا بعيدة",
            "والدنيا تمشي بطيء",
            "ونبض يسأل عنك",
        ],
        "verse2": [
            "كل نظرة تنادي",
            "يا يارا اقتربي",
            "والعود يرد بلطف",
            "وصوتك في بالي",
        ],
    },
    {
        "slug": "luma",
        "title": "Luma",
        "hook": "نور الليلة",
        "hook_lines": ["نور الليلة", "خلّيه يضل"],
        "seed": 100434,
        "motif_note": "soft 'نور الليلة' motif after pad/keys + female hum intro",
        "verse1": [
            "لمعة خفيفة في الليل",
            "تمشي مع أنفاسي",
            "والقلب هادي",
            "ولوما قريبة",
        ],
        "verse2": [
            "كل لحن يضيء",
            "يا نور بلطف",
            "والصوت دافئ",
            "ونظرة تبقيني",
        ],
    },
    {
        "slug": "safa",
        "title": "Safa",
        "hook": "صفاء الليلة",
        "hook_lines": ["صفاء الليلة", "هدّيني شوي"],
        "seed": 100545,
        "motif_note": "phrase 'صفاء الليلة' after long instrument + soft-sung open",
        "verse1": [
            "الصوت ناعم عليّا",
            "والليل صافي",
            "صفاء في بالي",
            "والدنيا ساكتة",
        ],
        "verse2": [
            "كل نبضة تقول",
            "يا صفاء بهدوء",
            "والعود يرد",
            "ولحن يبقى معي",
        ],
    },
]


def generate_song(spec: dict) -> Path:
    """Generate one Rima-lane song with long instrument+hum intro."""
    slug = spec["slug"]
    out_dir = OUTPUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    lyrics = build_signature_lyrics(
        hook_lines=spec["hook_lines"],
        verse1=spec["verse1"],
        verse2=spec["verse2"],
        shape="rima",
    )
    (out_dir / "lyrics.txt").write_text(lyrics, encoding="utf-8")
    raw = out_dir / f"{slug}.mp3"
    payload = build_signature_payload(
        hook=spec["hook"],
        slug=slug,
        lyrics=lyrics,
        seed=spec["seed"],
        color_note=RIMA_COLOR,
        motif_note=spec["motif_note"],
    )
    print(f"GENERATE {slug} earworm='{spec['hook']}' seed={spec['seed']}")
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
        "lyric_shape": "rima",
        "motif_note": spec["motif_note"],
        "bpm": 110,
        "key_scale": "A minor",
        "duration_sec": 60,
        "recipe": "haya_signature_recipe (rima: instrument+hum intro)",
        "color_note": RIMA_COLOR,
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
    """Generate the five-song Rima-lane batch."""
    for spec in SONGS:
        generate_song(spec)
    print("DONE batch5: hiba, rana, yara, luma, safa")


if __name__ == "__main__":
    main()
