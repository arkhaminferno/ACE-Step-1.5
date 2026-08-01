"""Per-song identity for HAYA pilots — hook is the product."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SonicIdentity:
    """Unique identity for one HAYA track."""

    slug: str
    hook_name: str
    arrangement: str
    contrast: str


SONIC_BY_SLUG: dict[str, SonicIdentity] = {
    "yalil": SonicIdentity(
        slug="yalil",
        hook_name="يا ليل يا ليلي",
        arrangement="approved release reference only — do not clone",
        contrast="catalog keep",
    ),
    "noor": SonicIdentity(
        slug="noor",
        hook_name="نور نور",
        arrangement="approved release reference only — do not clone",
        contrast="catalog keep",
    ),
    "gharib": SonicIdentity(
        slug="gharib",
        hook_name="يا غريبي",
        arrangement=(
            "FULL vocal song (~120s), NOT hook-only. "
            "Structure: intro → Verse 1 (story lines) → Pre-Chorus → Chorus "
            "→ Verse 2 → Chorus → Bridge → final Chorus → outro. "
            "Real female Arabic vocal sings full verses with different melodies "
            "from the chorus. Chorus hook = يا غريبي. "
            "Beat pocket: Thrace/Delina-inspired deep-house dance-pop. "
            "Do NOT copy Delina melody or English lyrics."
        ),
        contrast=(
            "must include verse + chorus vocals — never only repeat the hook"
        ),
    ),
    "hayati": SonicIdentity(
        slug="hayati",
        hook_name="يا حياتي",
        arrangement=(
            "COVER of a local reference beat (Mi Chico groove): KEEP the source "
            "drums, bassline, and instrumental groove exactly — same kick pattern, "
            "same bounce, same energy. REPLACE all vocals and melody with an "
            "ORIGINAL Arabic song: Verse 1 → Pre-Chorus → Chorus يا حياتي → "
            "Verse 2 → Chorus → Bridge → final Chorus. Real female Arabic vocal, "
            "no Spanish/English words, no Mi Chico melody or lyrics."
        ),
        contrast="beats from reference, vocals 100% new HAYA Arabic",
    ),
}


def get_sonic(slug: str) -> SonicIdentity | None:
    """Return sonic identity for slug, if defined."""
    return SONIC_BY_SLUG.get((slug or "").strip().lower())


def format_sonic_block(identity: SonicIdentity) -> str:
    """Short mandatory identity constraints for caption/instruction."""
    return (
        f"THIS SONG '{identity.slug}': memorable hook = {identity.hook_name}. "
        f"Arrangement = {identity.arrangement}. "
        f"Note = {identity.contrast}."
    )
