"""Build JSON job specs for one HAYA AE YouTube render."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from batch_deephouse.ae_config import (
    AE_BG_PREPARED_DIR,
    AE_JOBS_DIR,
    AE_PROJECTS_DIR,
    EDIT_COMP_FALLBACKS,
    EDIT_COMP_NAME,
    RENDER_COMP_NAME,
    TEMPLATE_AEP,
    TEMPLATE_ASSETS,
    TITLE_TEXT_LAYER,
)
from batch_deephouse.ae_titles import arabic_title_for, background_still_for, display_title_for
from batch_deephouse.normalize_bg_stills import prepare_still_for_render, resolve_bg_source
from batch_deephouse.paths import OUTPUT_DIR


def probe_duration_sec(path: Path) -> float:
    """Return media duration in seconds via ffprobe."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def resolve_song_mp3(
    slug: str,
    *,
    prefer_long: bool = True,
    prefer_human: bool = True,
    mp3_override: Path | None = None,
) -> Path:
    """Resolve the audio master for one song.

    Preference order when ``prefer_long`` and ``prefer_human``:
    ``{slug}_35min_human.mp3`` → ``{slug}_35min_upload.mp3`` → ``{slug}_35min.mp3``
    → short ``{slug}_human.mp3`` / ``{slug}.mp3``.

    Args:
        slug: Song folder name.
        prefer_long: Prefer the 35-min mix when present.
        prefer_human: Prefer stealth/human masters when present.
        mp3_override: Explicit audio path (wins over all preferences).
    """
    if mp3_override is not None:
        path = Path(mp3_override).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Override MP3 missing: {path}")
        return path
    folder = OUTPUT_DIR / slug
    candidates: list[Path] = []
    if prefer_long:
        if prefer_human:
            candidates.append(folder / f"{slug}_35min_human.mp3")
            candidates.append(folder / f"{slug}_35min_upload.mp3")
        candidates.append(folder / f"{slug}_35min.mp3")
    if prefer_human:
        candidates.append(folder / f"{slug}_human.mp3")
        candidates.append(folder / f"{slug}_upload.mp3")
    candidates.append(folder / f"{slug}.mp3")
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError(f"Missing MP3 for {slug} under {folder}")


@dataclass(frozen=True)
class RenderJob:
    """One HAYA AE render request."""

    slug: str
    display_name: str
    mp3_path: Path
    background_path: Path
    output_mp4: Path
    project_path: Path
    job_json_path: Path
    duration_sec: float
    title: str
    artist: str
    bg_fit_mode: str = "uniform"

    def to_dict(self) -> dict[str, object]:
        """Serialize for ExtendScript JSON loader."""
        return {
            "template_aep": str(TEMPLATE_AEP.resolve()),
            "project_path": str(self.project_path.resolve()),
            "mp3_path": str(self.mp3_path.resolve()),
            "background_path": str(self.background_path.resolve()),
            "output_mp4": str(self.output_mp4.resolve()),
            "slug": self.slug,
            "display_name": self.display_name,
            "duration_sec": self.duration_sec,
            "edit_comp": EDIT_COMP_NAME,
            "edit_comp_fallbacks": list(EDIT_COMP_FALLBACKS),
            "render_comp": RENDER_COMP_NAME,
            "title_text_layer": TITLE_TEXT_LAYER,
            "title": self.title,
            "artist": self.artist,
            "bg_fit_mode": self.bg_fit_mode,
        }


def build_render_job(
    *,
    slug: str,
    title: str = "",
    artist: str = "HAYA",
    prefer_long: bool = True,
    mp3_override: Path | None = None,
) -> RenderJob:
    """Resolve paths and Arabic title for one song slug."""
    key = slug.strip().lower()
    folder = OUTPUT_DIR / key
    mp3_path = resolve_song_mp3(
        key, prefer_long=prefer_long, mp3_override=mp3_override
    )
    bg_name = background_still_for(key)
    bg_source = resolve_bg_source(key, bg_name, TEMPLATE_ASSETS)
    prepared = AE_BG_PREPARED_DIR / f"{key}.png"
    bg_fit_mode = prepare_still_for_render(bg_source, prepared)

    AE_JOBS_DIR.mkdir(parents=True, exist_ok=True)
    AE_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    job_json_path = AE_JOBS_DIR / f"{key}.json"
    project_path = AE_PROJECTS_DIR / f"{key}.aep"
    output_mp4 = folder / f"{key}-youtube.mp4"
    duration_sec = probe_duration_sec(mp3_path)
    display = display_title_for(key)
    arabic = arabic_title_for(key)
    resolved_title = title.strip() or f"{display.title()} | {arabic} | Arabic Deep House | HAYA"

    return RenderJob(
        slug=key,
        display_name=display,
        mp3_path=mp3_path,
        background_path=prepared,
        output_mp4=output_mp4,
        project_path=project_path,
        job_json_path=job_json_path,
        duration_sec=duration_sec,
        title=resolved_title,
        artist=artist,
        bg_fit_mode=bg_fit_mode,
    )


def write_render_job(job: RenderJob) -> Path:
    """Persist job JSON for the ExtendScript runner."""
    job.job_json_path.write_text(
        json.dumps(job.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return job.job_json_path
