"""Generate 'Hanan' — natural Arabic deep house (human vocal + organic production)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.natural_vocal_recipe import (
    DEFAULT_BPM,
    DEFAULT_KEY,
    build_simple_lyrics,
    build_text2music_payload,
)

API_BASE = "http://127.0.0.1:8001"
OUT_DIR = Path("/Users/infy/Downloads/ACE-Step-1.5/batch_deephouse/output/hanan")
SLUG = "hanan"
TITLE = "Hanan"
HOOK = "حنان حنان"
SEED = 83420  # near approved Hawa/Shouf range
DURATION = 60

NATURAL_EXTRA = (
    "NATURAL HUMAN RECORDING: sounds like a real indie deep-house session, "
    "slight room noise, soft breath before phrases, natural vibrato, "
    "imperfect human timing, warm analog bass, dry intimate vocal, "
    "gentle tape warmth, NOT sterile AI polish, NOT perfect quantized grid, "
    "NOT robotic TTS Arabic, NOT hyper-compressed YouTube AI mix."
)

LYRICS = build_simple_lyrics(
    hook=HOOK,
    verse1=[
        "حنان في صوتي الليلة",
        "والقلب يهمس بهدوء",
        "والدقات ناعمة",
        "وأنت قريب مني",
    ],
    verse2=[
        "كل نَفَس ينادي",
        "قرب لي بلطف",
        "والعود يرد خفيف",
        "ونظرة تبقيني",
    ],
)


def build_payload() -> dict[str, Any]:
    """Natural-vocal payload with thinking LM + organic production cues."""
    payload = build_text2music_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=LYRICS,
        seed=SEED,
        thinking=True,
        duration=DURATION,
        bpm=DEFAULT_BPM,
        key=DEFAULT_KEY,
    )
    payload["batch_size"] = 1
    # 0.6B checkpoint is incomplete locally; 1.7B has model.safetensors.
    payload["lm_model_path"] = "acestep-5Hz-lm-1.7B"
    payload["prompt"] = f"{payload['prompt']} {NATURAL_EXTRA}"
    payload["instruction"] = (
        f"{payload['instruction']} Make it sound human-made and organic. "
        "Reject AI/sterile/robotic production."
    )
    payload["lm_negative_prompt"] = (
        payload["lm_negative_prompt"]
        + ", AI generated, sterile digital mix, robotic Arabic, TTS, "
        "perfectly quantized, hyper polished, synthetic singer"
    )
    return payload


def main() -> None:
    """Generate Hanan and write master + metadata."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "lyrics.txt").write_text(LYRICS, encoding="utf-8")
    out_path = OUT_DIR / f"{SLUG}.mp3"
    print(f"GENERATE {SLUG} natural deep house thinking=True seed={SEED}")
    meta = generate_to_file(
        build_payload(),
        api_base=API_BASE,
        api_key="",
        out_path=out_path,
        label=SLUG,
    )
    info = {
        "title": TITLE,
        "slug": SLUG,
        "hook": HOOK,
        "bpm": DEFAULT_BPM,
        "key_scale": DEFAULT_KEY,
        "duration_sec": DURATION,
        "style": "Arabic deep house — natural human female vocal",
        "engine": "ACE-Step acestep-v15-turbo text2music",
        "recipe": "natural_vocal_recipe + thinking LM 1.7B + organic production",
        "thinking": True,
        "batch_size": 1,
        "seed": SEED,
        "task_id": meta["task_id"],
    }
    (OUT_DIR / f"{SLUG}.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK {out_path}")


if __name__ == "__main__":
    main()
