"""Build Batch Upload Studio metadata for i still search her name."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from batch_soulcalm.brand import BRAND_HANDLE, BRAND_NAME, BRAND_TAGLINE
from batch_soulcalm.paths import BATCH_ROOT, OUTPUT_DIR

METADATA_DIR = BATCH_ROOT / "metadata"
METADATA_PATH = METADATA_DIR / "metadata.json"

# Stable brand key for the extension library map (matches channel title).
EXTENSION_BRAND = BRAND_NAME  # "i still search her name."

# Catalog for extension autofill (tags built by build_tags to ~500 chars).
SONG_CATALOG: list[dict[str, Any]] = [
    {
        "slug": "search_her_name_2am",
        "title": "i still search her name at 2am",
        "blurb": "couldn't sleep.\nkept searching her name again.\n\nsoft piano + rain.",
        "extra_tags": [
            "i still search her name at 2am",
            "search her name",
            "searching her name",
            "2am overthinking",
        ],
        "published": False,
        "duration_sec": 3600,
    },
    {
        "slug": "its_2am_almost_texted_her",
        "title": "it's 2am, almost texted her again",
        "blurb": "it's 2am.\nalmost texted her again.\n\nsoft piano + rain.",
        "extra_tags": [
            "it's 2am almost texted her again",
            "almost texted her",
            "it's 2am go to sleep",
            "2am music",
        ],
        "published": False,
        "duration_sec": 3600,
    },
    {
        "slug": "she_is_just_a_wallpaper",
        "title": "she is just a wallpaper now",
        "blurb": "unlock phone.\nshe is just a wallpaper now.\n\nsoft piano + rain.",
        "extra_tags": [
            "she is just a wallpaper now",
            "she is just a memory",
            "she was just a dream",
            "wallpaper memories",
        ],
        "published": False,
        "duration_sec": 3600,
    },
    {
        "slug": "i_still_think_about_her",
        "title": "i still think about her",
        "blurb": "i still think about her.\n\nsoft piano + rain.",
        "extra_tags": [
            "i still think about her",
            "i still miss her",
            "thinking about her",
            "can't stop thinking about her",
        ],
        "published": False,
        "duration_sec": 3600,
    },
]

# Shared high-volume tags for this niche (order = search value).
_SHARED_SEO_TAGS: list[str] = [
    "sleep music",
    "soft piano",
    "rain sounds",
    "piano music",
    "relaxing piano",
    "ambient piano",
    "sad piano",
    "chill piano",
    "late night music",
    "overthinking",
    "go to sleep",
    "it's late go to sleep",
    "2am",
    "rainy night",
    "piano rain",
    "sleep music piano",
    "calm music",
    "relaxing music",
    "ambient music",
    "instrumental piano",
    "soft instrumental",
    "heartbreak music",
    "i miss her",
    "missing her",
    "night rain",
    "study music",
    "focus music",
    "lofi piano",
    "lo-fi ambient",
    "peaceful piano",
    "emotional piano",
    "deep sleep music",
    "rain ambience",
    "soft rain",
    "nighttime music",
    "insomnia music",
    "melancholy piano",
    "nostalgic music",
    "quiet music",
]


def build_description(*, blurb: str) -> str:
    """Short personal note — not SEO copy."""
    return blurb.strip() + "\n"


def _trim_tags_to_limit(tags: list[str], *, limit: int = 500) -> list[str]:
    """Keep tags that fit YouTube's ~500-character joined soft limit."""
    joined: list[str] = []
    for tag in tags:
        trial = ", ".join([*joined, tag])
        if len(trial) > limit:
            break
        joined.append(tag)
    return joined


def build_tags(
    *,
    title: str = "",
    slug: str = "",
    extra_tags: list[str] | None = None,
) -> list[str]:
    """SEO tags for soulcalm uploads; fill close to YouTube's 500-char limit."""
    tags: list[str] = [
        *(extra_tags or []),
        title.strip().lower() if title else "",
        slug.replace("_", " ") if slug else "",
        *_SHARED_SEO_TAGS,
        "i still search her name",
        "soft piano to overthink",
        "rain piano sleep",
        "1 hour piano",
        "1 hour sleep music",
        "long piano music",
        "ambient sleep music 2026",
    ]
    seen: set[str] = set()
    unique: list[str] = []
    for tag in tags:
        cleaned = " ".join(str(tag).split()).strip()
        if not cleaned:
            continue
        key = cleaned.casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append(cleaned)
    return _trim_tags_to_limit(unique, limit=500)


def build_song(entry: dict[str, Any]) -> dict[str, Any]:
    """One extension song row from the catalog."""
    slug = entry["slug"]
    title = entry["title"]
    description = build_description(blurb=entry["blurb"])
    tags = build_tags(
        title=title,
        slug=slug,
        extra_tags=list(entry.get("extra_tags") or []),
    )
    return {
        "slug": slug,
        "name": title,
        "nativeName": "",
        "nativeNameUrdu": "",
        "language": "en",
        "country": "",
        "countries": "",
        "greeting": "",
        "secondaryGreeting": "",
        "gender": "",
        "youtubeId": "",
        "published": bool(entry.get("published")),
        "title": title,
        "description": description,
        "tags": tags,
        "shortsTitle": title,
        "shortsDescription": description,
        "shortsTags": tags,
        "legacySlugs": [
            f"{slug}_60min",
            f"{slug}_upload",
            f"{slug}_human",
        ],
        "wave": "soulcalm",
        "youtubeFilename": f"{slug}-youtube.mp4",
        "reelFilename": "",
        "audioFilename": f"{slug}_60min.mp3",
        "bpm": 0,
        "durationSec": int(entry.get("duration_sec") or 3600),
        "brand": EXTENSION_BRAND,
        "playlist": "",
    }


def _slug_aliases(songs: dict[str, dict[str, Any]]) -> dict[str, str]:
    """Filename stems → canonical slug for extension matching."""
    aliases: dict[str, str] = {}
    for slug, song in songs.items():
        for stem in (
            slug,
            f"{slug}_60min",
            f"{slug}_upload",
            f"{slug}_human",
            f"{slug}-youtube",
            f"{slug}-youtube.mp4",
        ):
            aliases[stem] = slug
        for legacy in song.get("legacySlugs") or []:
            aliases[str(legacy)] = slug
    # Old slug names → new
    aliases.update(
        {
            "almost_texted_her": "its_2am_almost_texted_her",
            "almost_texted_her-youtube": "its_2am_almost_texted_her",
            "her_photo_wallpaper": "she_is_just_a_wallpaper",
            "her_photo_wallpaper-youtube": "she_is_just_a_wallpaper",
            "closed_the_app_again": "i_still_think_about_her",
            "closed_the_app_again-youtube": "i_still_think_about_her",
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
        "brand": EXTENSION_BRAND,
        "handle": BRAND_HANDLE,
        "tagline": BRAND_TAGLINE,
        "playlist": "",
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
    sample = next(iter(songs.values()))
    print(f"Exported: {path}")
    print(f"Songs: {len(songs)} brand={EXTENSION_BRAND!r}")
    print(f"Handle: {BRAND_HANDLE}")
    for slug, song in songs.items():
        tag_chars = len(", ".join(song["tags"]))
        print(f"  - {slug}: {song['title']} | tags={tag_chars}/500 chars")
    print(f"Sample description:\n{sample['description']}")
    print("Import this file in Batch Upload Studio.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
