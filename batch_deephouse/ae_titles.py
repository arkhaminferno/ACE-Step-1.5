"""On-screen titles and per-song background stills for HAYA AE videos.

The AEP title layer uses Latin letters in the Alhambra font (stylized to look
Arabic) — e.g. \"rima\", not Arabic script ريما.
"""

from __future__ import annotations

# Locked YouTube catalog (Aug 2026) — 35min flowing masters + assets/{slug}.png
LOCKED_YOUTUBE_SLUGS: tuple[str, ...] = (
    "hanan",
    "lama",
    "layl",
    "luma",
    "mira",
    "noura",
    "qamar",
    "rana",
    "rima",
    "safa",
)

# Bottom-center title in EDIT HERE (Alhambra / Latin, matches template style).
DISPLAY_TITLES: dict[str, str] = {
    "hanan": "hanan",
    "lama": "lama",
    "layl": "layl",
    "luma": "luma",
    "mira": "mira",
    "noura": "noura",
    "qamar": "qamar",
    "rana": "rana",
    "rima": "rima",
    "safa": "safa",
    # Legacy (kept for older renders / tests)
    "yalil": "yalil",
    "hawa": "hawa",
    "rouh": "rouh",
    "ward": "ward",
    "shouf": "shouf",
    "baid": "baid",
    "noor": "noor",
}

# Keep Arabic spellings for YouTube metadata / descriptions (not AE title glyphs).
ARABIC_TITLES: dict[str, str] = {
    "hanan": "حنان",
    "lama": "لمى",
    "layl": "ليل",
    "luma": "لوما",
    "mira": "ميرا",
    "noura": "نورة",
    "qamar": "قمر",
    "rana": "رنا",
    "rima": "ريما",
    "safa": "صفاء",
    "yalil": "يا ليل",
    "hawa": "هوا",
    "rouh": "روح",
    "ward": "ورد",
    "shouf": "شوف",
    "baid": "بعيد",
    "noor": "نور",
}

# Background still filename inside ae_template/assets/ (per song).
BACKGROUND_STILLS: dict[str, str] = {
    "hanan": "hanan.png",
    "lama": "lama.png",
    "layl": "layl.png",
    "luma": "luma.png",
    "mira": "mira.png",
    "noura": "noura.png",
    "qamar": "qamar.png",
    "rana": "rana.png",
    "rima": "rima.png",
    "safa": "safa.png",
    "yalil": "bd4a5f15-a571-44f2-a9e0-349a48312fa3.png",
    "hawa": "hawa.png",
    "rouh": "rouh.png",
    "ward": "ward.png",
    "shouf": "shouf.png",
    "baid": "baid.png",
    "noor": "noor.png",
}


def display_title_for(slug: str) -> str:
    """Return on-screen Alhambra Latin title for a song slug."""
    key = slug.strip().lower()
    if key not in DISPLAY_TITLES:
        raise KeyError(f"No display title mapped for slug: {slug}")
    return DISPLAY_TITLES[key]


def arabic_title_for(slug: str) -> str:
    """Return Arabic spelling for metadata (not the AE title layer)."""
    key = slug.strip().lower()
    if key not in ARABIC_TITLES:
        raise KeyError(f"No Arabic title mapped for slug: {slug}")
    return ARABIC_TITLES[key]


def background_still_for(slug: str) -> str:
    """Return background PNG filename for a song slug."""
    key = slug.strip().lower()
    if key not in BACKGROUND_STILLS:
        raise KeyError(
            f"No background still mapped for slug: {slug}. "
            "Drop the PNG in ae_template/assets/ and add it to BACKGROUND_STILLS."
        )
    return BACKGROUND_STILLS[key]
