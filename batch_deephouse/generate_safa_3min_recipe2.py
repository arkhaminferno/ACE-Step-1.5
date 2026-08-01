"""Safa 3-min Recipe2 v3 — female on-grid chorus, then ready for 35min."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from batch_birthday.ai_stealth import harden_for_upload
from batch_birthday.humanize_audio import humanize_mp3
from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.extend_mix import build_crossfade_long_mix, probe_duration_sec
from batch_deephouse.haya_recipe2 import RECIPE2_CROSSFADE_SEC, build_recipe2_payload
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"
SLUG = "safa"
HOOK = "يا صفاء"
BPM = 104
# New seed — v2 pocket ok but chorus gender/grid failed.
SEED = 92501

MINIMAL = (
    "MINIMAL ARRANGEMENT (MANDATORY): ONLY these layers — "
    "(1) intimate young ARABIC FEMALE vocal, "
    "(2) soft four-on-floor kick, "
    "(3) warm sub bass, "
    "(4) one light pad. "
    "NO oud, NO guitar, NO darbuka, NO brass, NO busy leads."
)

STEADY = (
    "ONE GROOVE ONLY (MANDATORY): SAME soft four-on-floor kick + bass "
    "after the short intro until soft outro. "
    "NO rhythm change, NO half-time, NO breakdown, NO chorus lift, "
    "NO kick stop. Verses and choruses share IDENTICAL drum/bass rhythm."
)

FEMALE_CHORUS = (
    "FEMALE VOCAL ONLY (MANDATORY): the ENTIRE song — especially every "
    "chorus 'يا صفاء' — is sung by ONE young Arabic WOMAN. "
    "Close-mic, breathy, feminine. "
    "NO male voice, NO male chant, NO baritone, NO man singing the hook."
)

HOOK_GRID = (
    "HOOK RHYTHM (MANDATORY): 'يا صفاء' = two short equal hits ON the kick, "
    "same timing every repeat. "
    "Ya on kick 1, sa-fa on the next kick(s) — tight, no stretch, no melisma, "
    "no rubato, no off-beat. Same pocket as the verse vocals."
)

SHORT_INTRO = (
    "INTRO: ~3–5s soft FEMALE hum + pad only, then the ONE groove starts."
)

# Same short lyrics as approved v2 pocket.
LYRICS = """[Intro]
ممم
ممم

[Verse]
صفاء هادية
قرب لي
ليل هادي
معك بهدوء

[Chorus]
يا صفاء
يا صفاء
يا صفاء

[Verse]
لحن خفيف
قلبي لين
صوت ناعم
خليك جنبي

[Chorus]
يا صفاء
يا صفاء
يا صفاء
يا صفاء

[Bridge]
يا صفاء
قرب لي

[Chorus]
يا صفاء
يا صفاء
يا صفاء

[Verse]
صفاء بلطف
تملي بالي
هدّيني
خليك معي

[Chorus]
يا صفاء
يا صفاء
يا صفاء

[Outro]
يا صفاء
يا صفاء
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
    """Fix Safa female on-grid chorus, then build 35min + clean folder."""
    out_dir = OUTPUT_DIR / SLUG
    sources = OUTPUT_DIR / "_recipe2_sources"
    out_dir.mkdir(parents=True, exist_ok=True)
    sources.mkdir(parents=True, exist_ok=True)

    prev = out_dir / f"{SLUG}_3min.mp3"
    if prev.is_file():
        shutil.copy2(prev, sources / f"{SLUG}_3min_v2_pre_chorus_fix.mp3")
        print("kept v2 pre-chorus-fix copy in sources")

    (out_dir / "lyrics_3min.txt").write_text(LYRICS, encoding="utf-8")
    raw = sources / f"{SLUG}_3min_v3_raw.mp3"
    payload = build_recipe2_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=LYRICS,
        seed=SEED,
        bpm=BPM,
        color_note=(
            f"صفاء — {MINIMAL} {STEADY} {FEMALE_CHORUS} {HOOK_GRID} "
            f"{SHORT_INTRO} same warm night pocket as v2"
        ),
    )
    payload["instruction"] = (
        "Generate ONE sparse Arabic deep-house song. "
        f"{MINIMAL} {STEADY} {FEMALE_CHORUS} {HOOK_GRID} {SHORT_INTRO} "
        f"Sing EVERY chorus '{HOOK}' as a young Arabic WOMAN on the kick. "
        "Arabic only. Soft fade outro. "
        "Male hook or off-grid hook = failed take."
    )
    payload["prompt"] = (
        "Minimal oriental deep house, ONE unchanging four-on-floor groove, "
        "warm sub-bass, soft kick, ONE light pad, "
        "ONE young Arabic FEMALE vocal close-mic only. "
        f"HAYA song '{SLUG}'. Hook '{HOOK}' sung by woman on the kick. "
        f"Tempo {BPM} BPM steady. A minor. "
        f"{STEADY} {FEMALE_CHORUS} {HOOK_GRID} {MINIMAL} {SHORT_INTRO} "
        "Live human studio take, feminine breath and vibrato, NOT AI, NOT TTS. "
        "No male vocal. No brass. No East-Asian zither."
    )
    payload["lm_negative_prompt"] = (
        "male vocal, male chorus, man singing, baritone hook, male chant, "
        "ya safa sung by man, off-beat hook, stretched hook, melisma hook, "
        "rubato chorus, hook not on kick, rhythm change, half-time, breakdown, "
        "chorus lift, kick stop, oud, guitar, darbuka, brass, guzheng, pipa, "
        "singing English, robotic vocal, TTS"
    )
    payload["guidance_scale"] = 16.5
    payload["lm_cfg_scale"] = 4.2

    print(f"GENERATE safa 3min v3 female on-grid chorus seed={SEED}")
    meta_gen = generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=raw,
        label="safa_3min_v3",
    )
    listen, ai = _master_human(raw, slug=f"{SLUG}_3min_v3", bpm=BPM)

    mastered = sources / f"{SLUG}_3min_v3_mastered.mp3"
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
    shutil.copy2(three, sources / f"{SLUG}_3min_approved.mp3")

    # 35min from full approved 3:00 with locked blend
    dst35 = out_dir / f"{SLUG}_35min.mp3"
    build_crossfade_long_mix(
        three,
        dst35,
        target_sec=35 * 60,
        crossfade_sec=RECIPE2_CROSSFADE_SEC,
        fade_in_sec=0.0,
        fade_out_sec=8.0,
    )

    # Keep 3min for chorus check; delivery also has 35min.
    info = {
        "slug": SLUG,
        "hook": HOOK,
        "bpm": BPM,
        "seed": SEED,
        "recipe": "haya_recipe2 v3 — female on-grid يا صفاء + steady groove",
        "task_id": meta_gen.get("task_id"),
        "dur_3min": probe_duration_sec(three),
        "dur_35min": probe_duration_sec(dst35),
        "ai_score": ai,
        "crossfade_sec": RECIPE2_CROSSFADE_SEC,
        "listen_3min": str(three),
        "listen_35": str(dst35),
        "approved_3min": str(sources / f"{SLUG}_3min_approved.mp3"),
    }
    (out_dir / f"{SLUG}_3min.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (sources / "safa_recipe2.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK 3min → {three} ({info['dur_3min']:.1f}s) ai≈{ai:.4f}")
    print(f"OK 35min → {dst35} ({info['dur_35min']:.1f}s)")
    print("folder:", sorted(p.name for p in out_dir.iterdir()))


if __name__ == "__main__":
    main()
