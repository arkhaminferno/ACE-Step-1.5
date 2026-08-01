"""Generate two Hanan-style Arabic deep house songs: Noura + Lama."""

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

ORGANIC = (
    "Live human studio take, real Arabic woman singer with breath and vibrato, "
    "soft imperfect timing, warm dry mix, gentle room, analog warmth, "
    "NOT AI, NOT TTS, NOT synthetic, NOT sterile digital polish, NOT vocoder."
)

SONGS = [
    {
        "slug": "noura",
        "title": "Noura",
        "hook": "نورة نورة",
        "seed": 90317,  # Hawa B-seed family
        "verse1": [
            "في عيني نورة هادية",
            "يلفّ القلب بلطف",
            "والليل يسمعني",
            "وأنت بعيد عني",
        ],
        "verse2": [
            "كل نفس يقول",
            "ارجع لي بهدوء",
            "والنور يحضنني",
            "ولحن يبقى معي",
        ],
    },
    {
        "slug": "lama",
        "title": "Lama",
        "hook": "لما لما",
        "seed": 83420,  # Shouf-range seed
        "verse1": [
            "لما أشوفك بهدوء",
            "قلبي يلين شوية",
            "والليل يلفّني",
            "وأنت قريب مني",
        ],
        "verse2": [
            "كل لحن ينادي",
            "قرب لي بلطف",
            "والدقات هادية",
            "ونظرة تبقيني",
        ],
    },
]


def _build_payload(spec: dict[str, Any], lyrics: str) -> dict[str, Any]:
    """Hanan/Hawa natural-vocal payload with organic cues."""
    payload = build_text2music_payload(
        hook=spec["hook"],
        slug=spec["slug"],
        lyrics=lyrics,
        seed=spec["seed"],
        thinking=True,
        duration=DURATION,
    )
    payload["batch_size"] = 1
    payload["lm_model_path"] = "acestep-5Hz-lm-1.7B"
    payload["prompt"] = f"{payload['prompt']} {ORGANIC}"
    payload["instruction"] = (
        f"{payload['instruction']} Sound like a real human recording session. "
        "Reject synthetic/AI/robotic production."
    )
    payload["lm_negative_prompt"] = (
        payload["lm_negative_prompt"]
        + ", synthetic, AI generated, sterile, robotic, TTS, hyper polished"
    )
    return payload


def _master_organic(raw: Path, slug: str) -> tuple[Path, float]:
    """Distribute humanize + stealth harden → *_human.mp3."""
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
    """Generate one song and write raw + humanized masters."""
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
    print(f"GENERATE {slug} hanan-style thinking=True seed={spec['seed']}")
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
        "bpm": 108,
        "key_scale": "A minor",
        "duration_sec": DURATION,
        "recipe": "Hanan/Hawa natural_vocal_recipe + thinking 1.7B + distribute master",
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
    print(f"OK {slug} listen={listen} ai={ai_prob:.4f}")
    return listen


def main() -> None:
    """Generate Noura and Lama sequentially."""
    for spec in SONGS:
        generate_song(spec)
    print("DONE:", ", ".join(s["slug"] for s in SONGS))


if __name__ == "__main__":
    main()
