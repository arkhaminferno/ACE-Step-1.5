"""Two spiced Hanan-core songs: Sama (airy) + Qamar (darker night).

Core stays locked (natural_vocal_recipe + thinking 1.7B + distribute master).
Only light spices change color so takes don't clone Hanan/Noura/Lama.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from batch_birthday.ai_stealth import harden_for_upload
from batch_birthday.humanize_audio import humanize_mp3
from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.natural_vocal_recipe import (
    build_simple_lyrics,
    build_text2music_payload,
)

API_BASE = "http://127.0.0.1:8001"
OUT_ROOT = Path("/Users/infy/Downloads/ACE-Step-1.5/batch_deephouse/output")
DURATION = 60

# Locked organic line from Hanan (do not remove).
ORGANIC = (
    "Live human studio take, real Arabic woman singer with breath and vibrato, "
    "soft imperfect timing, warm dry mix, gentle room, analog warmth, "
    "NOT AI, NOT TTS, NOT synthetic, NOT sterile digital polish, NOT vocoder."
)

SONGS = [
    {
        "slug": "sama",
        "title": "Sama",
        "hook": "سما سما",
        "seed": 87112,
        "bpm": 106,
        "key": "D minor",
        # Spice: airier, more intimate, soft ney color (still deep house).
        "spice": (
            "SPICE: airy intimate night — softer kick, wider pads, sparse dry ney "
            "answering in gaps only, less busy hats, closer whispered Arabic vocal, "
            "dreamy space. Still oriental deep house, not ambient."
        ),
        "verse1": [
            "سما فوق المدينة",
            "والنجوم هادية",
            "والنبض خفيف",
            "وأنت في بالي",
        ],
        "verse2": [
            "كل نَفَس يطلع",
            "قرب لي بهدوء",
            "والناي يرد خفيف",
            "ونظرة تبقيني",
        ],
    },
    {
        "slug": "qamar",
        "title": "Qamar",
        "hook": "قمر قمر",
        "seed": 89244,
        "bpm": 110,
        "key": "A minor",
        # Spice: darker night-drive, warmer sub, tiny percussion dust.
        "spice": (
            "SPICE: darker night-drive — deeper warm sub bass, slightly firmer "
            "four-on-floor, tiny soft darbuka dust in the back, dry oud reply only "
            "in gaps, cinematic pads, late-night highway mood. Still deep house."
        ),
        "verse1": [
            "قمر على الطريق",
            "يمشي معايا الليلة",
            "والدقات ثابتة",
            "وأنت بعيد عني",
        ],
        "verse2": [
            "كل ضوء ينادي",
            "ارجع لي بلطف",
            "والعود يرد بهدوء",
            "ولحن يبقى معي",
        ],
    },
]


def _build_payload(spec: dict[str, Any], lyrics: str) -> dict[str, Any]:
    """Hanan core + one spice line."""
    payload = build_text2music_payload(
        hook=spec["hook"],
        slug=spec["slug"],
        lyrics=lyrics,
        seed=spec["seed"],
        thinking=True,
        duration=DURATION,
        bpm=spec["bpm"],
        key=spec["key"],
    )
    payload["batch_size"] = 1
    payload["lm_model_path"] = "acestep-5Hz-lm-1.7B"
    payload["prompt"] = f"{payload['prompt']} {ORGANIC} {spec['spice']}"
    payload["instruction"] = (
        f"{payload['instruction']} Sound like a real human recording session. "
        f"Apply spice: {spec['spice']} Reject synthetic/AI/robotic production."
    )
    payload["lm_negative_prompt"] = (
        payload["lm_negative_prompt"]
        + ", synthetic, AI generated, sterile, robotic, TTS, hyper polished, "
        "brass, guzheng, pipa, trap"
    )
    return payload


def _master_organic(raw: Path, slug: str) -> tuple[Path, float]:
    """Distribute humanize + stealth → *_human.mp3."""
    out_dir = raw.parent
    pre = out_dir / f"{slug}_prehuman.mp3"
    listen = out_dir / f"{slug}_human.mp3"
    upload = out_dir / f"{slug}_upload.mp3"
    humanize_mp3(raw, pre, style="distribute", bpm=108)
    _path, _rate, ai_prob = harden_for_upload(pre, listen, name=slug)
    upload.write_bytes(listen.read_bytes())
    pre.unlink(missing_ok=True)
    return listen, ai_prob


def generate_song(spec: dict[str, Any]) -> Path:
    """Generate one spiced song."""
    slug = spec["slug"]
    out_dir = OUT_ROOT / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    lyrics = build_simple_lyrics(
        hook=spec["hook"],
        verse1=spec["verse1"],
        verse2=spec["verse2"],
    )
    (out_dir / "lyrics.txt").write_text(lyrics, encoding="utf-8")
    raw = out_dir / f"{slug}.mp3"
    print(
        f"GENERATE {slug} spiced-hanan thinking=True "
        f"seed={spec['seed']} bpm={spec['bpm']} key={spec['key']}"
    )
    meta = generate_to_file(
        _build_payload(spec, lyrics),
        api_base=API_BASE,
        api_key="",
        out_path=raw,
        label=slug,
    )
    listen, ai_prob = _master_organic(raw, slug)
    info = {
        "title": spec["title"],
        "slug": slug,
        "hook": spec["hook"],
        "bpm": spec["bpm"],
        "key_scale": spec["key"],
        "duration_sec": DURATION,
        "recipe": "Hanan core + light spice",
        "spice": spec["spice"],
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
    """Generate Sama + Qamar."""
    for spec in SONGS:
        generate_song(spec)
    print("DONE spiced pair: sama, qamar")


if __name__ == "__main__":
    main()
