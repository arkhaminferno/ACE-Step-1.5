"""Hanan v2 — clone approved Hawa natural-vocal path + organic master."""

from __future__ import annotations

import json
from pathlib import Path

from batch_birthday.ai_stealth import harden_for_upload
from batch_birthday.humanize_audio import humanize_mp3
from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.natural_vocal_recipe import (
    build_simple_lyrics,
    build_text2music_payload,
)

API_BASE = "http://127.0.0.1:8001"
OUT_DIR = Path("/Users/infy/Downloads/ACE-Step-1.5/batch_deephouse/output/hanan")
SLUG = "hanan"
HOOK = "حنان حنان"
# Same seed family as approved Hawa A take.
SEED = 81201
DURATION = 60

LYRICS = build_simple_lyrics(
    hook=HOOK,
    verse1=[
        "في عيني حنان هادي",
        "يلفّ القلب بلطف",
        "والليل يسمعني",
        "وأنت بعيد عني",
    ],
    verse2=[
        "كل نفس يقول",
        "ارجع لي بهدوء",
        "والحنان يحضنني",
        "ولحن يبقى معي",
    ],
)

ORGANIC = (
    "Live human studio take, real Arabic woman singer with breath and vibrato, "
    "soft imperfect timing, warm dry mix, gentle room, analog warmth, "
    "NOT AI, NOT TTS, NOT synthetic, NOT sterile digital polish, NOT vocoder."
)


def main() -> None:
    """Generate Hanan v2 and write organic humanized masters."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "lyrics.txt").write_text(LYRICS, encoding="utf-8")
    raw = OUT_DIR / f"{SLUG}.mp3"

    payload = build_text2music_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=LYRICS,
        seed=SEED,
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

    print(f"GENERATE {SLUG} v2 hawa-path thinking=True seed={SEED}")
    meta = generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=raw,
        label=f"{SLUG}-v2",
    )

    # Organic distribute master, then stealth harden into listen path.
    pre = OUT_DIR / f"{SLUG}_prehuman.mp3"
    listen = OUT_DIR / f"{SLUG}_human.mp3"
    upload = OUT_DIR / f"{SLUG}_upload.mp3"
    humanize_mp3(raw, pre, style="distribute", bpm=108)
    _path, _rate, ai_prob = harden_for_upload(pre, listen, name=SLUG)
    upload.write_bytes(listen.read_bytes())
    pre.unlink(missing_ok=True)

    info = {
        "title": "Hanan",
        "slug": SLUG,
        "hook": HOOK,
        "bpm": 108,
        "key_scale": "A minor",
        "duration_sec": DURATION,
        "version": "v2",
        "recipe": "exact Hawa natural_vocal_recipe + thinking 1.7B + distribute master",
        "thinking": True,
        "seed": SEED,
        "task_id": meta["task_id"],
        "listen": str(listen),
        "ai_score": ai_prob,
        "notes": "v1 synthetic takes in _v1/. Listen hanan_human.mp3",
    }
    (OUT_DIR / f"{SLUG}.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK raw={raw}")
    print(f"OK listen={listen} ai={ai_prob:.4f}")


if __name__ == "__main__":
    main()
