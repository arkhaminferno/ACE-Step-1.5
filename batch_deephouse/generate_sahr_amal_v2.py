"""Generate enhanced v2 takes for Sahr and Amal (A/B each).

Fixes vs v1 spectrogram/QC issues:
- Late energy / sparse first half → hook + kick from 0–2s
- Robotic / off-grid risk → 1.7B LM + stronger beat-lock negatives
- East-Asian fallback / brass → explicit bans in negative + prompt
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.natural_vocal_recipe import (
    SHORT_NEGATIVE,
    build_simple_lyrics,
    build_text2music_payload,
)

API_BASE = "http://127.0.0.1:8001"
OUT_ROOT = Path("/Users/infy/Downloads/ACE-Step-1.5/batch_deephouse/output")

V2_EXTRA_PROMPT = (
    "START IMMEDIATELY: soft four-on-floor kick on beat 1, female Arabic hook "
    "sung within the first 2 seconds — NO long atmospheric intro, NO silence. "
    "Clear verse lines with different words than the hook. Dry present vocal. "
    "Solo dry oud reply only in gaps. No guzheng, no pipa, no brass, no choir."
)

V2_EXTRA_INSTRUCTION = (
    "Kick and sung hook must start in 0–2 seconds. Verses use real Arabic lines, "
    "not hook-only. Every syllable on the kick grid. Reject delayed intros."
)

V2_NEGATIVE = (
    SHORT_NEGATIVE
    + ", long intro, delayed vocals, silence at start, atmospheric pad-only intro, "
    "hook-only song, mumbled Arabic, East Asian zither, guzheng, pipa, koto"
)

SONGS = [
    {
        "slug": "sahr",
        "title": "Sahr",
        "hook": "سهر سهر",
        "seeds": [86241, 87102],
        "verse1": [
            "سهرت والمدينة نايمة",
            "قلبي يسأل عنك بهدوء",
            "والنبض يمشي مع الليل",
            "وأنا لسه بستناك",
        ],
        "verse2": [
            "كل سهر يناديني",
            "قرب لي قبل الفجر",
            "والدنيا ساكتة حواليا",
            "ولحن خفيف يبقيني",
        ],
    },
    {
        "slug": "amal",
        "title": "Amal",
        "hook": "أمل أمل",
        "seeds": [88461, 89203],
        "verse1": [
            "أمل خفيف في قلبي",
            "مثل ضوء بعيد بالليل",
            "والريح باردة عليّ",
            "وأنت لسه بعيد عني",
        ],
        "verse2": [
            "كل أمل يناديلك",
            "ارجع لي بلطف",
            "واللحن يلفّني بهدوء",
            "ونظرة تخليني أستنى",
        ],
    },
]


def _enhance_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Tighten start timing, negatives, and LM for v2 remakes."""
    payload = dict(payload)
    payload["prompt"] = f"{payload['prompt']} {V2_EXTRA_PROMPT}"
    payload["instruction"] = f"{payload['instruction']} {V2_EXTRA_INSTRUCTION}"
    payload["lm_negative_prompt"] = V2_NEGATIVE
    payload["lm_model_path"] = "acestep-5Hz-lm-1.7B"
    payload["guidance_scale"] = 15.0
    return payload


def generate_song_v2(spec: dict) -> list[dict]:
    """Generate A/B v2 takes; promote A to master until user picks."""
    slug = spec["slug"]
    out_dir = OUT_ROOT / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    lyrics = build_simple_lyrics(
        hook=spec["hook"],
        verse1=spec["verse1"],
        verse2=spec["verse2"],
    )
    (out_dir / "lyrics.txt").write_text(lyrics, encoding="utf-8")
    (out_dir / "lyrics_v2.txt").write_text(lyrics, encoding="utf-8")

    results: list[dict] = []
    for i, seed in enumerate(spec["seeds"]):
        tag = f"v2_a{seed}" if i == 0 else f"v2_b{seed}"
        out_path = out_dir / f"{slug}_{tag}.mp3"
        payload = _enhance_payload(
            build_text2music_payload(
                hook=spec["hook"],
                slug=slug,
                lyrics=lyrics,
                seed=seed,
                thinking=True,
            )
        )
        print(f"GENERATE {slug} {tag} seed={seed} thinking=True lm=1.7B")
        meta = generate_to_file(
            payload,
            api_base=API_BASE,
            api_key="",
            out_path=out_path,
            label=f"{slug}-{tag}",
        )
        results.append(
            {"seed": seed, "tag": tag, "file": str(out_path), "task_id": meta["task_id"]}
        )

    # Default master = take A until user chooses.
    master = out_dir / f"{slug}.mp3"
    master.write_bytes(Path(results[0]["file"]).read_bytes())

    info = {
        "title": spec["title"],
        "slug": slug,
        "hook": spec["hook"],
        "bpm": 108,
        "key_scale": "A minor",
        "duration_sec": 120,
        "engine": "ACE-Step acestep-v15-turbo text2music",
        "recipe": "natural_vocal_recipe v2 (early hook/kick + 1.7B LM)",
        "thinking": True,
        "lm_model_path": "acestep-5Hz-lm-1.7B",
        "version": "v2",
        "seeds": results,
        "master": str(master),
        "notes": (
            "v1 archived in _v1/. Listen A/B; promote better take to "
            f"{slug}.mp3. Fixes: delayed intro, sparse first half, vocal lock."
        ),
    }
    (out_dir / f"{slug}.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK {slug} master={master}")
    return results


def main() -> None:
    """Generate Sahr + Amal v2 A/B takes."""
    for spec in SONGS:
        generate_song_v2(spec)
    print("DONE sahr + amal v2 — pick A or B per song")


if __name__ == "__main__":
    main()
