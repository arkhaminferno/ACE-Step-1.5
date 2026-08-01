"""Hanan 3-min v3 — same grid take, fix elongated third chorus line."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.extend_mix import probe_duration_sec
from batch_deephouse.haya_signature_recipe import (
    RIMA_COLOR,
    build_signature_payload,
    master_signature_mp3,
)
from batch_deephouse.paths import OUTPUT_DIR

API_BASE = "http://127.0.0.1:8001"
SLUG = "hanan"
BPM = 108
DURATION = 180
# Same seed as approved grid take — only chorus rhythm wording changes.
SEED = 81440
HOOK = "يا حنان"

# All chorus hits identical short pocket — NO elongated / melisma third line.
LYRICS = f"""[Intro]
(soft female hum mmm ~4–8s — light pad, almost no kick)
(kick enters by 8 seconds — vocal stays on the grid)

[Verse]
في عيني حنان هادي
يلفّ القلب بلطف
والليل يسمعني
وأنت بعيد عني

[Chorus]
يا حنان
يا حنان
يا حنان
(same short rhythm every time — NO stretched/elongated third line)

[Verse]
كل نفس يقول
ارجع لي بهدوء
والحنان يحضنني
ولحن يبقى معي

[Chorus]
يا حنان
يا حنان
يا حنان
يا حنان
(every line short and on the kick — equal length, no melisma stretch)

[Bridge]
(soft oud — vocal rests on pocket)
يا حنان

[Chorus]
يا حنان
يا حنان
يا حنان

[Verse]
الطريق فاضي الليلة
ونبض يسأل عنك
قرب لي شوي
والدنيا تمشي

[Chorus]
يا حنان
يا حنان
يا حنان

[Outro]
يا حنان
(soft natural fade — short, on beat)
"""

CHORUS_FIX = (
    "CHORUS RHYTHM FIX: sing 'يا حنان' as a SHORT equal-length motif every "
    "repeat. Do NOT elongate, stretch, or melisma the third chorus line. "
    "No 'Ooooh Hanan' rubato — same tight kick-locked rhythm for line 1, 2, and 3."
)


def main() -> None:
    """Regenerate Hanan 3-min with equal short chorus hits only."""
    out_dir = OUTPUT_DIR / SLUG
    out_dir.mkdir(parents=True, exist_ok=True)

    prev = out_dir / f"{SLUG}_3min.mp3"
    if prev.is_file():
        archived = out_dir / f"{SLUG}_3min_longchorus.mp3"
        shutil.move(str(prev), str(archived))
        print(f"archived → {archived.name}")

    (out_dir / "lyrics_3min.txt").write_text(LYRICS, encoding="utf-8")
    raw = out_dir / f"{SLUG}_3min_raw.mp3"
    payload = build_signature_payload(
        hook=HOOK,
        slug=SLUG,
        lyrics=LYRICS,
        seed=SEED,
        bpm=BPM,
        duration=DURATION,
        grid_lock=True,
        color_note=(
            f"{RIMA_COLOR}; {CHORUS_FIX} tight equal chorus hits only"
        ),
        motif_note="short on-kick يا حنان — never elongate the third repeat",
    )
    # Extra negative for this specific bug.
    payload["lm_negative_prompt"] = (
        payload["lm_negative_prompt"]
        + ", elongated third chorus, stretched oh-hanan, melisma rubato chorus, "
        "long drawn-out hook on third repeat"
    )
    payload["instruction"] = f"{payload['instruction']} {CHORUS_FIX}"

    print(f"GENERATE hanan 3min chorus-fix seed={SEED}")
    generate_to_file(
        payload,
        api_base=API_BASE,
        api_key="",
        out_path=raw,
        label="hanan_3min_chorusfix",
    )
    listen, ai = master_signature_mp3(raw, slug=f"{SLUG}_3min", bpm=BPM)
    three = out_dir / f"{SLUG}_3min.mp3"
    shutil.copy2(listen, three)
    info = {
        "slug": SLUG,
        "hook": HOOK,
        "bpm": BPM,
        "duration_sec": probe_duration_sec(three),
        "seed": SEED,
        "recipe": "signature grid-lock + equal short chorus (no 3rd-line stretch)",
        "listen": str(three),
        "ai_score": ai,
    }
    (out_dir / f"{SLUG}_3min.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"OK → {three} ({info['duration_sec']:.1f}s) ai≈{ai:.4f}")


if __name__ == "__main__":
    main()
