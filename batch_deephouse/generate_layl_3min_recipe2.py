"""Layl 3-min — Recipe 2 minimal + kick-locked vocals (approve before 35-min)."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from batch_birthday.ai_stealth import harden_for_upload
from batch_birthday.humanize_audio import humanize_mp3
from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.extend_mix import probe_duration_sec
from batch_deephouse.haya_recipe2 import build_recipe2_payload
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"
SLUG = "layl"
# Short on-kick hook (same pocket as يا حنان / يا لمى).
HOOK = "يا ليل"
BPM = 104
SEED = 98240

MINIMAL = (
    "MINIMAL ARRANGEMENT (MANDATORY): ONLY these layers — "
    "(1) intimate female Arabic vocal, "
    "(2) soft four-on-floor kick, "
    "(3) warm sub bass, "
    "(4) one light pad. "
    "NO oud, NO guitar, NO tar, NO setar, NO Persian plucked strings, "
    "NO darbuka, NO percussion fills, NO brass, NO busy melodic leads. "
    "Sparse night-drive deep house — empty space is OK. "
    "Every layer locked to the kick grid."
)

SHORT_INTRO = (
    "INTRO: ~3–5s soft female hum + light pad only, then kick+bass. "
    "No plucked instruments anywhere in the song."
)

VOCAL_GRID = (
    "VOCALS (MANDATORY): every syllable of 'يا ليل' lands ON the kick. "
    "Short verses — one phrase per bar, start on the downbeat. "
    "No rushing, no dragging, no free-rubato. Danceable tight pocket."
)

# Clean Arabic only — no English stage directions (they get sung).
LYRICS = """[Intro]
ممم
ممم

[Verse]
الليل يطول
دنيا ساكتة
قلبي ينادي
صوتك في بالي

[Chorus]
يا ليل
يا ليل
يا ليل

[Verse]
كل نبضة تقول
قرب لي الليلة
الطريق فاضي
نظرة تبقيني

[Chorus]
يا ليل
يا ليل
يا ليل
يا ليل

[Bridge]
يا ليل

[Chorus]
يا ليل
يا ليل
يا ليل

[Verse]
يا ليل بلطف
تمشي معايا
الليل يهدي
لحن يبقى معي

[Chorus]
يا ليل
يا ليل
يا ليل

[Outro]
يا ليل
يا ليل
"""


def _master_human(raw: Path, *, slug: str, bpm: int) -> tuple[Path, float]:
    """One distribute humanize + stealth."""
    out_dir = raw.parent
    pre = out_dir / f"{slug}_prehuman.mp3"
    listen = out_dir / f"{slug}_human.mp3"
    humanize_mp3(raw, pre, style="distribute", bpm=bpm)
    _path, _rate, ai_prob = harden_for_upload(pre, listen, name=slug)
    pre.unlink(missing_ok=True)
    return listen, float(ai_prob)


def main() -> None:
    """Generate Layl Recipe 2 3-min for listen/approval."""
    out_dir = OUTPUT_DIR / SLUG
    sources = OUTPUT_DIR / "_recipe2_sources"
    out_dir.mkdir(parents=True, exist_ok=True)
    sources.mkdir(parents=True, exist_ok=True)

    (out_dir / "lyrics_3min.txt").write_text(LYRICS, encoding="utf-8")
    raw = sources / f"{SLUG}_3min_recipe2_raw.mp3"
    payload = build_recipe2_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=LYRICS,
        seed=SEED,
        bpm=BPM,
        color_note=(
            f"ليل — {MINIMAL} {SHORT_INTRO} {VOCAL_GRID} "
            "intimate close-mic Arabic female, warm analog pocket, "
            "vocals on kick, clean sparse mix"
        ),
    )
    payload["instruction"] = (
        "Generate ONE sparse Arabic deep-house song. "
        f"{MINIMAL} {SHORT_INTRO} {VOCAL_GRID} "
        f"Sing hook '{HOOK}' on the kick every chorus. "
        "Lyrics are Arabic only — never sing English. Soft fade outro. "
        "Reject busy arrangements and off-grid vocals/instruments."
    )
    payload["prompt"] = (
        "Minimal oriental deep house, warm sub-bass, soft four-on-floor kick, "
        "ONE light pad, intimate young Arabic female vocal close-mic. "
        f"HAYA song '{SLUG}'. Hook '{HOOK}'. Tempo {BPM} BPM. A minor. "
        f"{MINIMAL} {SHORT_INTRO} {VOCAL_GRID} "
        "Live human studio take, breath and vibrato, NOT AI, NOT TTS. "
        "No brass. No East-Asian zither."
    )
    payload["lm_negative_prompt"] = (
        "oud, guitar, tar, setar, Persian guitar, plucked strings, darbuka, "
        "percussion fills, busy arrangement, melodic lead clutter, "
        "off-beat instruments, off-beat vocals, rushed hook, dragging vocal, "
        "free-time rubato, vocals not matching the rhythm, "
        "singing English, robotic vocal, TTS, brass, guzheng, pipa, "
        "synthetic AI noise, harsh digital artifacts"
    )
    payload["guidance_scale"] = 16.0
    payload["lm_cfg_scale"] = 4.0

    print(f"GENERATE layl 3min Recipe2 minimal+grid seed={SEED}")
    meta_gen = generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=raw,
        label="layl_3min_recipe2",
    )
    listen, ai = _master_human(raw, slug=f"{SLUG}_3min_recipe2", bpm=BPM)

    mastered = sources / f"{SLUG}_3min_recipe2_mastered.mp3"
    shutil.copy2(listen, mastered)
    three = out_dir / f"{SLUG}_3min.mp3"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(mastered),
            "-af",
            "volume=-3dB,loudnorm=I=-18:TP=-2.0:LRA=11",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "320k",
            str(three),
        ],
        check=True,
        capture_output=True,
    )

    info = {
        "slug": SLUG,
        "hook": HOOK,
        "bpm": BPM,
        "duration_sec": probe_duration_sec(three),
        "seed": SEED,
        "recipe": "haya_recipe2 — minimal + vocal grid (Lama-approved lane)",
        "task_id": meta_gen.get("task_id"),
        "listen": str(three),
        "raw": str(raw),
        "ai_score": ai,
        "master": "distribute humanize + stealth once + quiet loudnorm",
        "next": "approve 3min → 35min with full-3:00 + 5s tri blend",
    }
    (out_dir / f"{SLUG}_3min.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK → {three} ({info['duration_sec']:.1f}s) ai≈{ai:.4f}")
    print(f"task_id={info['task_id']}")


if __name__ == "__main__":
    main()
