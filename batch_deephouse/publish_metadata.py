"""Build Batch Upload Studio metadata.json for HAYA YouTube uploads."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from batch_deephouse.paths import BATCH_ROOT, OUTPUT_DIR

METADATA_DIR = BATCH_ROOT / "metadata"
METADATA_PATH = METADATA_DIR / "metadata.json"

BRAND_NAME = "HAYA"
BRAND_HANDLE = "@hayamusic"
BRAND_TAGLINE = "Arabic Deep House · Night Drive · Dark Chill"
PLAYLIST = "HAYA — Arabic Deep Chill House | Night Drive Mixes 2026"

# Catalog: published=True for songs already on YouTube.
SONG_CATALOG: list[dict[str, Any]] = [
    {
        "slug": "yalil",
        "name": "Yalil",
        "native": "يا ليل",
        "hook": "يا ليل يا ليلي",
        "published": True,
    },
    {
        "slug": "noor",
        "name": "Noor",
        "native": "نور",
        "hook": "نور نور",
        "published": True,
    },
    {
        "slug": "hawa",
        "name": "Hawa",
        "native": "هوا",
        "hook": "هوا هوا",
        "published": False,
    },
    {
        "slug": "rouh",
        "name": "Rouh",
        "native": "روح",
        "hook": "روح روح",
        "published": False,
    },
    {
        "slug": "ward",
        "name": "Ward",
        "native": "ورد",
        "hook": "ورد ورد",
        "published": False,
    },
    {
        "slug": "shouf",
        "name": "Shouf",
        "native": "شوف",
        "hook": "شوف شوف",
        "published": False,
    },
    {
        "slug": "baid",
        "name": "Baid",
        "native": "بعيد",
        "hook": "بعيد بعيد",
        "published": False,
    },
]


def build_title(*, name: str, native: str) -> str:
    """English name + Arabic + fixed night-drive suffix (≤100 chars)."""
    return (
        f"{name} {native} — Arabic Deep House Night Drive Mix 2026 "
        "| Dark Chill Vocal House"
    )


def build_description(*, name: str, native: str, hook: str) -> str:
    """Yalil/Noor-style description with hashtags."""
    return f"""🌙 {name} | {native} — Arabic Deep Chill House Night Drive

Late-night Arabic deep house for dark drives, headphones, and quiet focus.
Warm sub bass · four-on-the-floor · female Arabic vocal · oriental melody.

{hook}

🎧 Best with: car speakers / good headphones / lights low

Channel: HAYA ({BRAND_HANDLE})
Playlist: {PLAYLIST}
New Arabic deep house mixes every week — subscribe 🔔

#ArabicDeepHouse #DeepHouse #NightDrive #{name} #{native.replace(' ', '_')} #HAYA #MelodicDeepHouse #ChillHouse #DarkChill #CarMusic #OrientalHouse #VocalHouse #ArabicMusic2026
"""


def build_tags(*, slug: str, name: str, native: str, hook: str) -> list[str]:
    """Tag list aiming for ~500 chars when comma-joined in Studio."""
    tags = [
        slug,
        native,
        hook,
        "arabic deep house",
        "deep house mix",
        "night drive music",
        "melodic deep house",
        "arabic chill house",
        "oriental deep house",
        "dark chill",
        "female arabic vocals",
        "car music",
        "vocal house",
        "haya music",
        "arabic music 2026",
        "chill house mix",
        "eastern deep house",
        "late night house",
        "arabic deep chill house mix",
        f"dark mood {slug}",
        "night vibes house",
        "lounge deep house",
        "emotional arabic house",
        "oud deep house",
        "four on the floor house",
        "warm sub bass house",
        "arabic night drive mix 2026",
        "deep chill vocal house",
    ]
    # Trim so comma-joined length stays near YouTube's ~500 soft limit.
    joined: list[str] = []
    for tag in tags:
        trial = ", ".join([*joined, tag])
        if len(trial) > 500:
            break
        joined.append(tag)
    return joined


def build_song(entry: dict[str, Any]) -> dict[str, Any]:
    """Return one extension-ready publish object."""
    slug = str(entry["slug"])
    name = str(entry["name"])
    native = str(entry["native"])
    hook = str(entry["hook"])
    title = build_title(name=name, native=native)
    description = build_description(name=name, native=native, hook=hook).strip() + "\n"
    tags = build_tags(slug=slug, name=name, native=native, hook=hook)
    return {
        "slug": slug,
        "name": name,
        "nativeName": native,
        "nativeNameUrdu": "",
        "language": "ar",
        "country": "",
        "countries": "",
        "greeting": "",
        "secondaryGreeting": "",
        "gender": "female",
        "youtubeId": "",
        "published": bool(entry.get("published", False)),
        "title": title,
        "description": description,
        "tags": tags,
        "shortsTitle": title,
        "shortsDescription": description,
        "shortsTags": tags,
        "legacySlugs": [f"{slug}_human", f"{slug}_upload", f"{slug}_35min_human"],
        "wave": "haya",
        "youtubeFilename": f"{slug}-youtube.mp4",
        "reelFilename": f"{slug}-reel.mp4",
        "audioFilename": f"{slug}_35min_human.mp3",
        "bpm": 108,
        "durationSec": 2100,
        "brand": BRAND_NAME,
        "playlist": PLAYLIST,
    }


def _slug_aliases(songs: dict[str, dict[str, Any]]) -> dict[str, str]:
    """Filename stems → canonical slug for extension matching."""
    aliases: dict[str, str] = {}
    for slug, song in songs.items():
        for stem in (
            slug,
            f"{slug}_human",
            f"{slug}_upload",
            f"{slug}_35min",
            f"{slug}_35min_human",
            f"{slug}_35min_upload",
            f"{slug}-youtube",
            f"{slug}-youtube-2min",
        ):
            aliases[stem] = slug
        for legacy in song.get("legacySlugs") or []:
            aliases[str(legacy)] = slug
    # Keep old Yalil catalog aliases.
    aliases.update(
        {
            "haya-01-yalil-pulse": "yalil",
            "haya-01-yalil-pulse-35m": "yalil",
            "yalil-35m": "yalil",
            "yalil-pulse": "yalil",
            "yalil-35m_upload": "yalil",
        }
    )
    return aliases


def export_metadata(*, path: Path | None = None) -> Path:
    """Write metadata.json + per-song publish sidecars for the extension."""
    out = path or METADATA_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    songs = {entry["slug"]: build_song(entry) for entry in SONG_CATALOG}
    payload = {
        "version": 1,
        "exportedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "brand": BRAND_NAME,
        "handle": BRAND_HANDLE,
        "tagline": BRAND_TAGLINE,
        "playlist": PLAYLIST,
        "slugAliases": _slug_aliases(songs),
        "songs": songs,
    }
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for slug, song in songs.items():
        song_dir = OUTPUT_DIR / slug
        song_dir.mkdir(parents=True, exist_ok=True)
        (song_dir / f"{slug}.youtube.json").write_text(
            json.dumps(song, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return out


def main() -> int:
    """CLI entry for metadata export."""
    path = export_metadata()
    songs = json.loads(path.read_text(encoding="utf-8"))["songs"]
    pending = [s for s, v in songs.items() if not v.get("published")]
    print(f"Exported: {path}")
    print(f"Songs: {len(songs)} brand={BRAND_NAME}")
    print(f"Already uploaded: yalil, noor")
    print(f"To schedule: {', '.join(pending)}")
    print("Import this file in Batch Upload Studio (HAYA brand).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
