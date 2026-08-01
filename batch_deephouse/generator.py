"""Build ACE-Step payloads for original Arabic deep-house pilots.

New songs are text2music by default (do not clone Yalil via cover).
Remasters set cover_strength + cover_src to rewrite the same master.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from batch_deephouse.catalog import TrackRow
from batch_deephouse.mps_safety import clamp_cover_strength_for_mps
from batch_deephouse.paths import BATCH_ROOT, YALIL_GROOVE_REF, track_dir, track_meta, track_mp3
from batch_deephouse.prompts import (
    build_caption,
    build_instruction,
    build_lyrics,
    build_negative_prompt,
)

TEXT2MUSIC_GUIDANCE = 14.0
TEXT2MUSIC_STEPS = 20
LM_CFG_SCALE = 3.0

# Remaster slugs may map to a parent lyric pack when needed.
LYRICS_ALIAS: dict[str, str] = {}


def stage_cover_src(src: Path) -> str:
    """Copy cover source into system temp (API allows absolute temp paths only)."""
    src = src.resolve()
    if not src.exists():
        raise FileNotFoundError(f"Missing cover source: {src}")
    dest = Path(tempfile.gettempdir()) / f"haya_cover_{src.name}"
    if not dest.exists() or dest.stat().st_mtime < src.stat().st_mtime:
        shutil.copy2(src, dest)
    return str(dest.resolve())


def resolve_cover_src(row: TrackRow) -> Path:
    """Resolve remaster/cover audio path for a catalog row."""
    raw = (row.cover_src or "").strip()
    if raw:
        path = Path(raw)
        if not path.is_absolute():
            path = BATCH_ROOT / path
        return path
    return YALIL_GROOVE_REF


def build_payload(row: TrackRow) -> dict[str, Any]:
    """Build text2music payload (optional remaster/cover when configured)."""
    lyrics_slug = LYRICS_ALIAS.get(row.slug, row.slug)
    is_remaster = row.cover_strength is not None and bool((row.cover_src or "").strip())

    payload: dict[str, Any] = {
        "prompt": build_caption(
            slug=row.slug,
            mood_note=row.mood,
            bpm=row.bpm,
            key_scale=row.key_scale,
        ),
        "lyrics": build_lyrics(lyrics_slug),
        "instruction": build_instruction(
            slug=row.slug,
            mood_note=row.mood,
            bpm=row.bpm,
            key_scale=row.key_scale,
        ),
        # Remasters keep LM from rewriting song form.
        "thinking": not is_remaster,
        "use_format": False,
        "use_cot_caption": False,
        "use_cot_language": False,
        "vocal_language": "ar",
        "audio_duration": row.duration_sec,
        "bpm": row.bpm,
        "key_scale": row.key_scale,
        "inference_steps": TEXT2MUSIC_STEPS,
        "guidance_scale": TEXT2MUSIC_GUIDANCE,
        "lm_cfg_scale": LM_CFG_SCALE,
        "lm_negative_prompt": build_negative_prompt(),
        "model": "acestep-v15-turbo",
        "use_random_seed": False,
        "task_type": "text2music",
    }
    if row.seed is not None:
        payload["seed"] = row.seed

    # Opt-in cover / remaster — require cover_strength; prefer explicit cover_src.
    if row.cover_strength is not None:
        payload["task_type"] = "cover"
        payload["src_audio_path"] = stage_cover_src(resolve_cover_src(row))
        # Remasters need room to improvise beats/melody; allow fractional strength.
        payload["audio_cover_strength"] = clamp_cover_strength_for_mps(
            float(row.cover_strength),
            force_full=not is_remaster,
        )

    return payload


def generate_track(
    row: TrackRow,
    *,
    api_base: str,
    api_key: str = "",
    force: bool = False,
    vocals_only: bool = False,
) -> Path:
    """Generate one track MP3 + sidecar JSON under output/{slug}/."""
    is_remaster = row.cover_strength is not None and bool((row.cover_src or "").strip())
    if not is_remaster:
        from batch_deephouse.hook_pipeline import generate_hook_first_track

        return generate_hook_first_track(
            row,
            api_base=api_base,
            api_key=api_key,
            force=force,
            vocals_only=vocals_only,
        )

    out_mp3 = track_mp3(row.slug)
    if out_mp3.exists() and not force:
        print(f"SKIP (exists): {out_mp3}")
        return out_mp3

    from batch_deephouse.acestep_task import generate_to_file

    payload = build_payload(row)
    track_dir(row.slug).mkdir(parents=True, exist_ok=True)
    mode = payload.get("task_type", "text2music")
    print(f"MODE ({row.slug}): {mode}")
    result = generate_to_file(
        payload,
        api_base=api_base,
        api_key=api_key,
        out_path=out_mp3,
        label=row.slug,
    )
    meta = {
        "title": row.title,
        "slug": row.slug,
        "bpm": row.bpm,
        "key_scale": row.key_scale,
        "duration_target_sec": row.duration_sec,
        "mood": row.mood,
        "seed": row.seed,
        "cover_strength": row.cover_strength,
        "cover_src": row.cover_src,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task_id": result["task_id"],
        "payload": payload,
        "stage": "remaster",
        "style": "arabic_deep_house_remaster",
        "notes": "Same-song remaster via cover.",
    }
    track_meta(row.slug).write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"OK: {out_mp3}")
    return out_mp3
