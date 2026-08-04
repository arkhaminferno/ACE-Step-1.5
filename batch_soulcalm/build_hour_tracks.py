"""Build 1-hour soulcalm masters (instrumental + optional rain)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.extend_mix import build_crossfade_long_mix
from batch_soulcalm.atmosphere import ensure_rain_asset, mix_rain_under, sprinkle_laughs
from batch_soulcalm.brand import FULL_DURATION_SEC
from batch_soulcalm.clean_audio import clean_for_listen
from batch_soulcalm.paths import ASSETS_DIR, OUTPUT_DIR
from batch_soulcalm.prompts import build_payload

API_BASE = "http://127.0.0.1:8001"

# Song 1 already shipped; kept here for reference / regen.
SONG1 = {
    "slug": "search_her_name_2am",
    "title": "i still search her name at 2am",
    "bpm": 70,
    "key": "A minor",
    "seed": 70201,
    "mood": (
        "Rainy night through the window. Soft felt piano + warm retro pads. "
        "INSTRUMENTAL ONLY. Very soft muted pulse or no drums. "
        "Dark quiet top end — no bright hats. Lonely overthinking sleep mood."
    ),
    "with_rain": True,
    "with_laughs": False,
}

SONG2 = {
    "slug": "its_2am_almost_texted_her",
    "title": "it's 2am, almost texted her again",
    "bpm": 70,
    "key": "A minor",
    "seed": 81407,
    "mood": (
        "Simple clear soft felt piano melody repeating gently. "
        "Warm quiet pads. Instrumental only — no voice. "
        "Rainy night window. Easy to hear every piano note."
    ),
    "with_rain": True,
    "with_laughs": False,
}

SONG3 = {
    "slug": "she_is_just_a_wallpaper",
    "title": "she is just a wallpaper now",
    "bpm": 68,
    "key": "D minor",
    "seed": 82619,
    "mood": (
        "Simple clear soft felt piano melody, slightly warmer and nostalgic. "
        "Warm quiet pads. Instrumental only — no voice. "
        "Rainy night. Easy to hear every piano note."
    ),
    "with_rain": True,
    "with_laughs": False,
}

SONG4 = {
    "slug": "i_still_think_about_her",
    "title": "i still think about her",
    "bpm": 70,
    "key": "A minor",
    "seed": 85203,
    "mood": (
        "Simple clear soft felt piano melody repeating gently. "
        "Warm quiet pads. Instrumental only — no voice. "
        "Rainy night window. Easy to hear every piano note."
    ),
    "with_rain": True,
    "with_laughs": False,
}

NEW_BATCH: list[dict] = [SONG4]

CATALOG: dict[str, dict] = {
    SONG1["slug"]: SONG1,
    SONG2["slug"]: SONG2,
    SONG3["slug"]: SONG3,
    SONG4["slug"]: SONG4,
}


def generate_short(spec: dict) -> Path:
    """Generate + light-clean a 3-min instrumental seed (clear piano)."""
    from batch_soulcalm.prompts import DEFAULT_INSTRUMENTAL_LYRICS

    slug = spec["slug"]
    out_dir = OUTPUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = out_dir / f"{slug}_3min.mp3"
    lyrics = str(spec.get("lyrics") or DEFAULT_INSTRUMENTAL_LYRICS)
    payload = build_payload(
        lyrics=lyrics,
        duration_sec=180,
        bpm=int(spec["bpm"]),
        key_scale=str(spec["key"]),
        seed=int(spec["seed"]),
        mood_note=str(spec["mood"]),
        thinking=True,
    )
    print(f"GENERATE short {slug} seed={spec['seed']} bpm={spec['bpm']} …")
    generate_to_file(payload, api_base=API_BASE, api_key="", out_path=raw, label=slug)
    # Light clean only — heavy stealth was making the piano unintelligible.
    listen, report = clean_for_listen(
        raw, slug=slug, bpm=int(spec["bpm"]), light=True
    )
    print(f"CLEAN light {slug} ai={report['ai_before']}→{report['ai_after']}")
    if spec.get("with_rain"):
        rain = ensure_rain_asset()
        rainy_short = out_dir / f"{slug}_3min_clean_rain.mp3"
        mix_rain_under(listen, rain, rainy_short, rain_db=-18.0)
        print(f"PREVIEW with rain: {rainy_short}")
    return listen


def make_laugh_clip() -> Path:
    """Return a soft laugh clip for sparse memory moments."""
    sfx_dir = ASSETS_DIR / "sfx"
    sfx_dir.mkdir(parents=True, exist_ok=True)
    preferred = sfx_dir / "soft_girl_laugh.mp3"
    if preferred.is_file() and preferred.stat().st_size > 5_000:
        return preferred
    for name in ("laugh_414.mp3", "laugh_424.mp3", "laugh_2882.mp3", "laugh_try.mp3"):
        cand = sfx_dir / name
        if cand.is_file() and cand.stat().st_size > 5_000:
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(cand),
                "-af",
                "volume=-3dB,lowpass=f=7000,highpass=f=200,afade=t=in:st=0:d=0.1",
                "-ar",
                "48000",
                "-c:a",
                "libmp3lame",
                "-b:a",
                "192k",
                str(preferred),
            ]
            import subprocess

            subprocess.run(cmd, check=True, capture_output=True)
            return preferred
    raise FileNotFoundError(
        f"No laugh SFX in {sfx_dir}. Drop soft_girl_laugh.mp3 there."
    )


def build_hour(spec: dict, short: Path) -> Path:
    """Extend cleaned short to 1 hour and optionally layer atmosphere."""
    slug = spec["slug"]
    out_dir = OUTPUT_DIR / slug
    hour_raw = out_dir / f"{slug}_60min_raw.mp3"
    print(f"EXTEND {slug} → 3600s …")
    build_crossfade_long_mix(
        short,
        hour_raw,
        target_sec=float(FULL_DURATION_SEC),
        crossfade_sec=5.0,
        fade_in_sec=0.0,
        fade_out_sec=10.0,
    )
    current = hour_raw
    if spec.get("with_rain"):
        rain = ensure_rain_asset()
        rainy = out_dir / f"{slug}_60min_rain.mp3"
        print(f"MIX rain under {slug} …")
        mix_rain_under(current, rain, rainy, rain_db=-18.0)
        current = rainy
    if spec.get("with_laughs"):
        laugh = make_laugh_clip()
        final = out_dir / f"{slug}_60min.mp3"
        print(f"SPRINKLE laughs on {slug} …")
        sprinkle_laughs(
            current,
            laugh,
            final,
            interval_sec=480.0,
            first_at_sec=110.0,
            laugh_db=-16.0,
        )
        current = final
    else:
        final = out_dir / f"{slug}_60min.mp3"
        final.write_bytes(current.read_bytes())
        current = final

    meta = {
        "title": spec["title"],
        "slug": slug,
        "duration_sec": FULL_DURATION_SEC,
        "file": str(current),
        "with_rain": bool(spec.get("with_rain")),
        "with_laughs": bool(spec.get("with_laughs")),
        "notes": "Instrumental only — no laugh/speech overlays",
        "short_seed": str(short),
    }
    (out_dir / f"{slug}_60min.json").write_text(
        json.dumps(meta, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"DONE hour: {current}")
    return current


def build_one(spec: dict) -> Path:
    """Generate short seed then 1-hour master for one catalog entry."""
    short = generate_short(spec)
    return build_hour(spec, short)


def main(argv: list[str] | None = None) -> int:
    """Generate new batch, or one slug: python -m … build_hour_tracks [slug]."""
    args = list(sys.argv[1:] if argv is None else argv)
    ensure_rain_asset()

    if args:
        slug = args[0].strip()
        spec = CATALOG.get(slug)
        if not spec:
            print(f"Unknown slug: {slug}")
            print("Known:", ", ".join(CATALOG))
            return 1
        hour = build_one(spec)
        print(f"READY: {spec['title']} → {hour}")
        return 0

    paths: list[tuple[str, Path]] = []
    for spec in NEW_BATCH:
        hour = build_one(spec)
        paths.append((spec["title"], hour))

    print("\nBATCH READY")
    for i, (title, path) in enumerate(paths, start=2):
        print(f"{i}) {title}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
