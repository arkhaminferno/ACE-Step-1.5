"""Remake Amira as pure instrumental — no vocals, no hum (lyrics later)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.haya_recipe3 import (
    RECIPE3_BPM,
    RECIPE3_DURATION,
    RECIPE3_KEY,
    build_recipe3_payload,
    master_recipe3_mp3,
)
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"
SLUG = "amira"
SEED = 95111  # fresh take, same Amira lane
LEAD = "piano_oud_ney"

# Pure instrumental form — never a sung line.
LYRICS = """[Intro]
(soft intimate piano only — absolute silence from any human voice)
(NO vocal, NO hum, NO mmm, NO singing)
(kick + warm sub enter by 6 seconds — piano on the kick grid)

[Instrumental Chorus]
(DRY ACOUSTIC OUD star motif ON every kick + warm sub)
(piano dust only — NO vocal)

[Instrumental]
(soft piano bed, oud answers in gaps ON the kick — instruments only)

[Instrumental Chorus]
(oud motif bigger ON the kick — still NO vocal — no ney yet)

[Instrumental]
(four-on-floor groove + piano/oud dialogue — NO singing)

[Instrumental Chorus]
(LONG oud instrumental chorus — main replay reason — ON the kick)
(brief airy NEY answers in gaps near the end — oud still lead)

[Instrumental]
(oud motif; soft NEY color phrase — one lead at a time)

[Outro]
(sparse airy ney + fading soft piano — soft fade — NO vocal ever)
"""


def main() -> int:
    """Text2music instrumental Amira — zero human voice."""
    out_dir = OUTPUT_DIR / SLUG
    sources = OUTPUT_DIR / "_recipe3_sources"
    out_dir.mkdir(parents=True, exist_ok=True)
    sources.mkdir(parents=True, exist_ok=True)

    (out_dir / "lyrics_instrumental.txt").write_text(LYRICS, encoding="utf-8")
    payload = build_recipe3_payload(
        hook="أميرة",
        slug=SLUG,
        lyrics=LYRICS,
        seed=SEED,
        bpm=RECIPE3_BPM,
        key=RECIPE3_KEY,
        duration=RECIPE3_DURATION,
        lead=LEAD,
        color_note=(
            "Amira PURE INSTRUMENTAL — piano intro, oud heart, ney outro; "
            "ZERO human voice of any kind"
        ),
    )
    # Do not inherit the vocal master — fresh instrumental generate.
    payload["task_type"] = "text2music"
    payload.pop("src_audio_path", None)
    payload.pop("audio_cover_strength", None)
    payload["thinking"] = False
    payload["lyrics"] = LYRICS
    payload["prompt"] = (
        f"Arabic deep chill house INSTRUMENTAL ONLY, {RECIPE3_BPM} BPM, "
        f"{RECIPE3_KEY}, night-drive. NO vocals, NO humming, NO choir. "
        "Soft piano intro → dry acoustic oud instrumental choruses ON the kick "
        "→ sparse airy ney in late/outro. Warm sub, four-on-floor. "
        "One melodic lead at a time. Real recording feel."
    )
    payload["instruction"] = (
        "Generate PURE INSTRUMENTAL Amira bed. ABSOLUTELY NO singing, humming, "
        "mmm, whispers, or any human voice. Soft piano opens; kick by ~6s; "
        "oud is the star of instrumental choruses ON the kick grid; brief ney "
        "only late/outro. Sparse arrangement, tight pocket, 180 seconds."
    )
    payload["lm_negative_prompt"] = (
        "female vocal, male vocal, singing, humming, mmm, choir, whisper, "
        "spoken word, Arabic lyrics sung, vocal hook, human voice, "
        "guzheng, pipa, brass, trap, off-grid, rubato"
    )

    raw = sources / f"{SLUG}_3min_instrumental_raw.mp3"
    print(f"GENERATE pure instrumental {SLUG} seed={SEED}", flush=True)
    meta = generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=raw,
        label=f"{SLUG}-inst-pure",
    )
    listen, ai = master_recipe3_mp3(
        raw, slug=f"{SLUG}_3min_instrumental", bpm=RECIPE3_BPM
    )
    final = out_dir / f"{SLUG}_3min_instrumental.mp3"
    final.write_bytes(listen.read_bytes())

    cues = out_dir / "cues"
    cues.mkdir(exist_ok=True)
    for name, start, dur in (
        ("20_instrumental_intro.mp3", "0", "14"),
        ("21_instrumental_oud.mp3", "95", "28"),
        ("22_instrumental_late.mp3", "140", "35"),
    ):
        subprocess.run(
            [
                "ffmpeg", "-y", "-ss", start, "-t", dur, "-i", str(final),
                "-codec:a", "libmp3lame", "-b:a", "192k", str(cues / name),
            ],
            check=False,
            capture_output=True,
        )

    info = {
        "slug": SLUG,
        "kind": "pure_instrumental_text2music",
        "lead": LEAD,
        "seed": SEED,
        "file": str(final.resolve()),
        "task_id": meta.get("task_id"),
        "ai_score": ai,
        "note": "Remake: no cover of vocal mix — zero vocals by design",
    }
    (out_dir / f"{SLUG}_instrumental.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("DONE", final, "ai", ai, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
