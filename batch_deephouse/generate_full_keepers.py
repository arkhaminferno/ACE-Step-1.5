"""Full-length Rana / Luma / Safa — same seeds, short soft-vocal intro, ~3 min."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.haya_signature_recipe import (
    RIMA_COLOR,
    build_signature_payload,
    master_signature_mp3,
)
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"
# ~3 min individual track (FerdausMix song length). Fall back to 120 if OOM.
FULL_DURATION = 180

SONGS = [
    {
        "slug": "rana",
        "title": "Rana",
        "hook": "ارجعي لي",
        "hook_lines": ["ارجعي لي", "ما تبعدي الليلة"],
        "seed": 100212,
        "motif_note": "call phrase 'ارجعي لي' after SHORT soft female hum open (~4–8s)",
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
        "verse3": [
            "الليل يطول عليّا",
            "ونبض يسأل عنك",
            "خليك جنبي شوي",
            "والدنيا تمشي",
        ],
        "bridge": [
            "يا رنا بهدوء",
            "قرب لي الليلة",
            "والعود يرد",
        ],
    },
    {
        "slug": "luma",
        "title": "Luma",
        "hook": "نور الليلة",
        "hook_lines": ["نور الليلة", "خلّيه يضل"],
        "seed": 100434,
        "motif_note": "soft 'نور الليلة' after SHORT soft female hum (~4–8s), beat by 8s",
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
        "verse3": [
            "الضوء في عيونك",
            "يهدّيني شوي",
            "والليل يصير أهدى",
            "وإنتِ معايا",
        ],
        "bridge": [
            "يا لوما نور",
            "خلّيه يضل",
            "والعود يرد بلطف",
        ],
    },
    {
        "slug": "safa",
        "title": "Safa",
        "hook": "صفاء الليلة",
        "hook_lines": ["صفاء الليلة", "هدّيني شوي"],
        "seed": 100545,
        "motif_note": "phrase 'صفاء الليلة' after SHORT soft female hum, groove by ~8s",
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
        "verse3": [
            "الهوا خفيف الليلة",
            "وقلبي يرتاح",
            "قرب لي بلطف",
            "ونظرة تخلّيني",
        ],
        "bridge": [
            "يا صفاء الليلة",
            "هدّيني شوي",
            "والنبض هادي",
        ],
    },
]


def build_full_rima_lyrics(spec: dict) -> str:
    """Expanded Rima-shape lyrics for ~3 min — short hum open, then full form."""
    motif = spec["hook_lines"][0]
    hook_block = "\n".join(spec["hook_lines"])
    v1 = "\n".join(spec["verse1"])
    v2 = "\n".join(spec["verse2"])
    v3 = "\n".join(spec["verse3"])
    br = "\n".join(spec["bridge"])
    return f"""[Intro]
(soft female hum mmm ~4–8s only — light pad under vocal)
(main beat enters by 8 seconds — no long instrumental)

[Verse]
{v1}

[Chorus]
{hook_block}
{motif}

[Verse]
{v2}

[Chorus]
{hook_block}
{motif}
{motif}

[Bridge]
{br}

[Chorus]
{hook_block}
{motif}

[Verse]
{v3}

[Chorus]
{hook_block}
{motif}
{motif}

[Break]
(oud echoes motif: {motif})

[Chorus]
{hook_block}
{motif}

[Outro]
{motif}
(soft natural fade)
"""


def archive_short(slug: str) -> None:
    """Keep approved 60s masters beside the new full versions."""
    out_dir = OUTPUT_DIR / slug
    for name in (f"{slug}_upload.mp3", f"{slug}_human.mp3", f"{slug}.mp3"):
        src = out_dir / name
        if src.is_file():
            dst = out_dir / f"{slug}_60s{src.suffix if name.endswith('.mp3') else ''}"
            # clearer names
            if name.endswith("_upload.mp3"):
                dst = out_dir / f"{slug}_60s_upload.mp3"
            elif name.endswith("_human.mp3"):
                dst = out_dir / f"{slug}_60s_human.mp3"
            else:
                dst = out_dir / f"{slug}_60s.mp3"
            if not dst.exists():
                shutil.copy2(src, dst)


def generate_full(spec: dict, duration: int) -> Path:
    """Regenerate one keeper as a full-length song."""
    slug = spec["slug"]
    out_dir = OUTPUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    archive_short(slug)
    lyrics = build_full_rima_lyrics(spec)
    (out_dir / "lyrics_full.txt").write_text(lyrics, encoding="utf-8")
    raw = out_dir / f"{slug}_full.mp3"
    payload = build_signature_payload(
        hook=spec["hook"],
        slug=slug,
        lyrics=lyrics,
        seed=spec["seed"],
        duration=duration,
        color_note=RIMA_COLOR,
        motif_note=spec["motif_note"],
    )
    print(f"GENERATE FULL {slug} duration={duration}s seed={spec['seed']}")
    meta = generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=raw,
        label=f"{slug}_full",
    )
    # Master into canonical listen/upload names (full becomes the release).
    listen, ai_prob = master_signature_mp3(raw, slug=slug)
    info = {
        "title": spec["title"],
        "slug": slug,
        "hook": spec["hook"],
        "hook_lines": spec["hook_lines"],
        "lyric_shape": "rima_full",
        "motif_note": spec["motif_note"],
        "bpm": 110,
        "key_scale": "A minor",
        "duration_sec": duration,
        "recipe": "haya_signature_recipe (rima full: short soft-vocal intro)",
        "color_note": RIMA_COLOR,
        "thinking": True,
        "seed": spec["seed"],
        "task_id": meta["task_id"],
        "listen": str(listen),
        "raw_full": str(raw),
        "ai_score": ai_prob,
        "archived_60s": True,
    }
    (out_dir / f"{slug}_full.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / f"{slug}.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK FULL {slug} → {listen} ai={ai_prob:.4f}")
    return listen


def main() -> None:
    """Full versions of approved keepers: rana, luma, safa."""
    duration = FULL_DURATION
    for spec in SONGS:
        try:
            generate_full(spec, duration)
        except Exception as exc:  # noqa: BLE001 — fall back once for Mac OOM
            msg = str(exc).lower()
            if duration > 120 and ("memory" in msg or "oom" in msg or "mps" in msg):
                print(f"RETRY {spec['slug']} at 120s after: {exc}")
                generate_full(spec, 120)
            else:
                raise
    print("DONE full keepers: rana, luma, safa")


if __name__ == "__main__":
    main()
