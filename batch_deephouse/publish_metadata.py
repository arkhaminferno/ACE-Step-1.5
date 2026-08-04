"""Build Batch Upload Studio metadata.json for HAYA YouTube uploads."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from batch_deephouse.ae_titles import ARABIC_TITLES, LOCKED_YOUTUBE_SLUGS
from batch_deephouse.paths import BATCH_ROOT, OUTPUT_DIR

METADATA_DIR = BATCH_ROOT / "metadata"
METADATA_PATH = METADATA_DIR / "metadata.json"

BRAND_NAME = "HAYA"
BRAND_HANDLE = "@hayamusic.official"
BRAND_TAGLINE = "Arabic Deep House · Night Drive · Dark Chill"
PLAYLIST = "HAYA — Arabic Deep Chill House | Night Drive Mixes 2026"

# Vocal hooks for description / tags (Recipe2 + approved masters).
HOOKS_BY_SLUG: dict[str, str] = {
    "hanan": "يا حنان",
    "lama": "يا لمى",
    "layl": "يا ليل",
    "luma": "يا لوما",
    "mira": "ميرا ميرا",
    "noura": "يا نورة",
    "qamar": "يا قمر",
    "rana": "يا رنا",
    "rima": "يا ريما",
    "safa": "يا صفاء",
    "yalil": "يا ليل يا ليلي",
    "noor": "نور نور",
}

# Display names (English) for titles/descriptions.
NAMES_BY_SLUG: dict[str, str] = {
    "hanan": "Hanan",
    "lama": "Lama",
    "layl": "Layl",
    "luma": "Luma",
    "mira": "Mira",
    "noura": "Noura",
    "qamar": "Qamar",
    "rana": "Rana",
    "rima": "Rima",
    "safa": "Safa",
    "yalil": "Yalil",
    "noor": "Noor",
}


def _catalog_entry(slug: str, *, published: bool) -> dict[str, Any]:
    """One SONG_CATALOG row from locked title/hook maps."""
    return {
        "slug": slug,
        "name": NAMES_BY_SLUG[slug],
        "native": ARABIC_TITLES[slug],
        "hook": HOOKS_BY_SLUG[slug],
        "published": published,
    }


# Locked Aug 2026 YouTube batch (all uploaded) + prior uploads (yalil/noor).
SONG_CATALOG: list[dict[str, Any]] = [
    *[_catalog_entry(slug, published=True) for slug in LOCKED_YOUTUBE_SLUGS],
    _catalog_entry("yalil", published=True),
    _catalog_entry("noor", published=True),
]


def build_title(*, name: str, native: str) -> str:
    """Song-first title: English + Arabic, then genre/mood (≤100 chars)."""
    return (
        f"{name} {native} — Arabic Deep House Mix 2026 | "
        f"Dark Mood Night Drive Chill"
    )


def build_description(*, name: str, native: str, hook: str) -> str:
    """Keyword-rich description; first ~150 chars are the search snippet."""
    native_tag = native.replace(" ", "_")
    return f"""Arabic Deep House Mix 2026 — {name} ({native}) | Dark Mood Night Drive Chill House

35-minute Arabic deep chill house for night drives, late study, cafe focus, and headphones.
Warm sub bass · soft four-on-the-floor · female Arabic vocal · oriental melody · melodic deep house vibe.

Hook: {hook}

Best for:
• Night drive / car music / highway chill
• Deep house mix / chill house / lounge house
• Study music, focus playlist, quiet late-night sessions
• Oriental deep house & Middle Eastern vocal house

Timestamps:
0:00 — Cold open / vocal hook
~3:00 — Full groove locked
~35:00 — Soft fade out

Channel: HAYA ({BRAND_HANDLE})
Playlist: {PLAYLIST}
New Arabic deep house mixes every week — subscribe 🔔

Related searches: arabic deep house, deep house mix 2026, night drive music, chill house mix, melodic deep house, arabic chill house, oriental house, vocal house, cafe music, lounge mix, dark chill, female arabic vocals

#ArabicDeepHouse #DeepHouse #DeepHouseMix #NightDrive #ChillHouse #MelodicDeepHouse #ArabicMusic #OrientalHouse #VocalHouse #LoungeMusic #CarMusic #StudyMusic #CafeMusic #HouseMusic2026 #DarkMood #HAYA #{name} #{native_tag}
"""


def build_tags(*, slug: str, name: str, native: str, hook: str) -> list[str]:
    """High-volume SEO tags first; trim to YouTube ~500-char soft limit."""
    # Order = search volume / ranking value. Skip ultra-niche filler.
    tags = [
        # Broad genre (highest volume)
        "deep house",
        "arabic deep house",
        "deep house mix",
        "chill house",
        "melodic deep house",
        "house music",
        "chill house mix",
        "lounge music",
        # Intent / use-case searches
        "night drive music",
        "night drive mix",
        "car music",
        "study music",
        "cafe music",
        "focus music",
        "late night music",
        # Arabic / oriental lane (EN + AR script for MENA discovery)
        "arabic music",
        "arabic chill house",
        "oriental deep house",
        "oriental house",
        "middle eastern house",
        "female arabic vocals",
        "vocal house",
        "دييب هاوس",
        "موسيقى عربية",
        "هاوس شرقي",
        # Mood / year / format
        "dark chill",
        "dark mood",
        "deep chill",
        "arabic music 2026",
        "house music 2026",
        "35 minute mix",
        "long mix",
        # Song / brand identity last
        name.lower(),
        slug,
        native,
        hook,
        "haya music",
    ]
    # Dedupe (name.lower() often equals slug) while keeping order.
    seen: set[str] = set()
    unique: list[str] = []
    for tag in tags:
        key = tag.casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append(tag)

    joined: list[str] = []
    for tag in unique:
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
        "audioFilename": f"{slug}_35min.mp3",
        "bpm": 104,
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
    sample = songs[pending[0]] if pending else next(iter(songs.values()))
    print(f"Exported: {path}")
    print(f"Songs: {len(songs)} brand={BRAND_NAME}")
    print(f"Already uploaded: yalil, noor")
    print(f"To schedule: {', '.join(pending)}")
    print(f"Sample title ({len(sample['title'])} chars): {sample['title']}")
    print(f"Sample tags ({len(', '.join(sample['tags']))} chars): {', '.join(sample['tags'][:8])}…")
    print("Import this file in Batch Upload Studio (HAYA brand).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
