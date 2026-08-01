"""Noura 3-min v9 — keep v8; female chorus only + sync Persian guitar."""

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
SLUG = "noura"
HOOK = "يا نورة"
BPM = 104
# Same seed as approved v8.
SEED = 90520

ARRANGEMENT = (
    "ARRANGEMENT: intimate young ARABIC FEMALE vocal, soft four-on-floor kick, "
    "warm sub bass, one light pad, and optional SHORT dry Persian/oud guitar "
    "replies ONLY between vocal phrases. "
    "No brass, no darbuka spam, no busy leads, no East-Asian zither."
)

SHORT_INTRO = (
    "INTRO: ~3–5s soft FEMALE hum + light pad only, then kick+bass."
)

FEMALE_CHORUS = (
    "FEMALE VOCAL ONLY (MANDATORY): the ENTIRE song — especially every "
    "chorus 'يا نورة' — is sung by ONE young Arabic WOMAN. "
    "Close-mic, breathy, feminine. "
    "NO male voice, NO male chant, NO baritone, NO man singing the hook."
)

GUITAR_SYNC = (
    "PERSIAN/OUD GUITAR SYNC (MANDATORY): any Persian guitar / oud plucks "
    "land ON the kick or even eighths only — short answers in gaps. "
    "No free-time rubato, no off-beat runs, no out-of-sync strums. "
    "Guitar follows the four-on-floor under the female vocal."
)

FULL_SYNC = (
    "FULL SYNC: kick, bass, pad, guitar, and female vocal share ONE 104 BPM grid. "
    "Same steady groove in verses and choruses. "
    "Hook 'يا نورة' = short equal hits ON the kick. "
    "Every lyric line = 2–3 Arabic words on the downbeat."
)

# Same short lyrics as approved v8.
LYRICS = """[Intro]
ممم
ممم

[Verse]
نورة هادية
قرب لي
الليل يهدي
وأنت بعيد

[Chorus]
يا نورة
يا نورة
يا نورة

[Verse]
ارجع لي
بهدوء
النور بلطف
لحن معي

[Chorus]
يا نورة
يا نورة
يا نورة
يا نورة

[Bridge]
يا نورة
قرب لي

[Chorus]
يا نورة
يا نورة
يا نورة

[Verse]
ضوء ينادي
بلطف
تبقيني
خليك جنبي

[Chorus]
يا نورة
يا نورة
يا نورة

[Outro]
يا نورة
يا نورة
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
    """Regenerate Noura: female chorus + on-grid Persian guitar."""
    out_dir = OUTPUT_DIR / SLUG
    sources = OUTPUT_DIR / "_recipe2_sources"
    out_dir.mkdir(parents=True, exist_ok=True)
    sources.mkdir(parents=True, exist_ok=True)

    prev = out_dir / f"{SLUG}_3min.mp3"
    if prev.is_file():
        archived = out_dir / f"{SLUG}_3min_v8_approved.mp3"
        shutil.copy2(prev, archived)
        shutil.copy2(prev, sources / f"{SLUG}_3min_v8_approved.mp3")
        shutil.move(str(prev), str(out_dir / f"{SLUG}_3min_v8_pre_female.mp3"))
        print(f"kept approved v8 → {archived.name}")

    (out_dir / "lyrics_3min.txt").write_text(LYRICS, encoding="utf-8")
    raw = sources / f"{SLUG}_3min_v9_raw.mp3"
    payload = build_recipe2_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=LYRICS,
        seed=SEED,
        bpm=BPM,
        color_note=(
            f"نورة — {ARRANGEMENT} {SHORT_INTRO} {FEMALE_CHORUS} "
            f"{GUITAR_SYNC} {FULL_SYNC} "
            "SAME warm night pocket as the approved take"
        ),
    )
    payload["instruction"] = (
        "Generate ONE sparse Arabic deep-house song. "
        f"{ARRANGEMENT} {SHORT_INTRO} {FEMALE_CHORUS} {GUITAR_SYNC} {FULL_SYNC} "
        f"Sing hook '{HOOK}' as a young Arabic WOMAN on the kick every chorus. "
        "Soft fade outro."
    )
    payload["prompt"] = (
        "Minimal oriental deep house, warm sub-bass, soft four-on-floor kick, "
        "ONE light pad, ONE young Arabic FEMALE vocal close-mic only, "
        "short dry Persian/oud guitar ON the kick in gaps. "
        f"HAYA song '{SLUG}'. Hook '{HOOK}'. Tempo {BPM} BPM. A minor. "
        f"{FEMALE_CHORUS} {GUITAR_SYNC} {FULL_SYNC} "
        "Live human studio take, feminine breath and vibrato, NOT AI, NOT TTS. "
        "No male vocal. No brass. No East-Asian zither."
    )
    payload["lm_negative_prompt"] = (
        "male vocal, male chorus, man singing, baritone hook, male chant, "
        "ya noora sung by man, off-beat Persian guitar, free-time oud rubato, "
        "out of sync guitar, off-beat plucks, guitar not matching the rhythm, "
        "off-beat vocals, chorus groove change, busy arrangement, "
        "darbuka spam, brass, guzheng, pipa, singing English, robotic vocal, TTS"
    )
    payload["guidance_scale"] = 16.5
    payload["lm_cfg_scale"] = 4.2

    print(f"GENERATE noura 3min v9 female chorus + guitar sync seed={SEED}")
    meta_gen = generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=raw,
        label="noura_3min_v9",
    )
    listen, ai = _master_human(raw, slug=f"{SLUG}_3min_v9", bpm=BPM)

    mastered = sources / f"{SLUG}_3min_v9_mastered.mp3"
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
        "recipe": "haya_recipe2 v9 — v8 pocket + female chorus + guitar on grid",
        "task_id": meta_gen.get("task_id"),
        "listen": str(three),
        "v8_approved": str(out_dir / f"{SLUG}_3min_v8_approved.mp3"),
        "ai_score": ai,
    }
    (out_dir / f"{SLUG}_3min.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK → {three} ({info['duration_sec']:.1f}s) ai≈{ai:.4f}")
    print(f"task_id={info['task_id']}")


if __name__ == "__main__":
    main()
