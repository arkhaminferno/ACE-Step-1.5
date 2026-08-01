"""Two-pass HAYA generation: Valessa-style instrumental, then vocal hook cover."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.catalog import TrackRow
from batch_deephouse.generator import stage_cover_src
from batch_deephouse.haya_sound_bible import HAYA_BPM
from batch_deephouse.mps_safety import clamp_cover_strength_for_mps
from batch_deephouse.paths import track_dir, track_meta, track_mp3
from batch_deephouse.prompts import (
    build_caption,
    build_instruction,
    build_instrumental_caption,
    build_lyrics,
    build_negative_prompt,
)
from batch_deephouse.sonic_identity import get_sonic

TEXT2MUSIC_GUIDANCE = 14.0
TEXT2MUSIC_STEPS = 20
# Mid-high: keep groove, but leave room so vocals can sit in key/time.
VOCAL_COVER_STRENGTH = 0.78
VOCAL_INFERENCE_STEPS = 28
VOCAL_GUIDANCE = 12.0


def _base_payload(row: TrackRow) -> dict[str, Any]:
    """Shared turbo text2music fields."""
    payload: dict[str, Any] = {
        "use_format": False,
        "use_cot_caption": False,
        "use_cot_language": False,
        "vocal_language": "ar",
        "audio_duration": row.duration_sec,
        "bpm": row.bpm or HAYA_BPM,
        "key_scale": row.key_scale,
        "inference_steps": TEXT2MUSIC_STEPS,
        "guidance_scale": TEXT2MUSIC_GUIDANCE,
        "lm_cfg_scale": 3.0,
        "lm_negative_prompt": build_negative_prompt(),
        "model": "acestep-v15-turbo",
        "use_random_seed": False,
        "task_type": "text2music",
        "audio_format": "mp3",
    }
    if row.seed is not None:
        payload["seed"] = row.seed
    return payload


def build_instrumental_payload(row: TrackRow) -> dict[str, Any]:
    """Pass 1: Valessa-style groove only — no vocals."""
    payload = _base_payload(row)
    payload["prompt"] = build_instrumental_caption(bpm=row.bpm, slug=row.slug)
    payload["lyrics"] = "[Instrumental]"
    if row.slug == "gharib":
        payload["instruction"] = (
            "Instrumental only. Punchy commercial deep-house / dance-pop groove "
            "inspired by Thrace/Delina beat pocket: four-on-floor kick, clap on 2/4, "
            "swung hats, bouncing sidechained bass, filtered chord stabs. "
            "No vocals. Leave space for a future Arabic vocal hook. "
            "Do not recreate Delina's melody."
        )
    else:
        payload["instruction"] = (
            "Instrumental commercial melodic deep house only. No vocals. "
            "Four-on-the-floor kick, warm sidechained bass, filtered chord stabs, "
            "spacious pads — Valessa-style night-drive groove with room for a vocal hook."
        )
    payload["thinking"] = True
    return payload


def build_vocal_cover_payload(row: TrackRow, instrumental_path: Path) -> dict[str, Any]:
    """Pass 2: keep groove, plant natural on-beat sung hook in key."""
    payload = _base_payload(row)
    # Fresh seed so vocal take isn't stuck to the bad robotic pass.
    if row.seed is not None:
        payload["seed"] = int(row.seed) + 41
    payload["prompt"] = build_caption(
        slug=row.slug,
        mood_note=row.mood,
        bpm=row.bpm,
        key_scale=row.key_scale,
    )
    payload["lyrics"] = build_lyrics(row.slug)
    payload["instruction"] = build_instruction(
        slug=row.slug,
        mood_note=row.mood,
        bpm=row.bpm,
        key_scale=row.key_scale,
    )
    payload["task_type"] = "cover"
    payload["src_audio_path"] = stage_cover_src(instrumental_path)
    payload["audio_cover_strength"] = clamp_cover_strength_for_mps(
        VOCAL_COVER_STRENGTH,
        force_full=False,
    )
    # More steps + softer CFG help natural pitch/timing vs robotic paste.
    payload["inference_steps"] = VOCAL_INFERENCE_STEPS
    payload["guidance_scale"] = VOCAL_GUIDANCE
    # Allow CoT so the model plans a sung line in key (Yalil-style).
    payload["thinking"] = True
    return payload


def _write_meta(
    row: TrackRow,
    *,
    instrumental: Path,
    inst_task_id: str | None,
    vocal_result: dict[str, Any],
    vocal_payload: dict[str, Any],
    reused_instrumental: bool,
) -> None:
    """Write sidecar JSON for the final vocal mix."""
    identity = get_sonic(row.slug)
    meta = {
        "title": row.title,
        "slug": row.slug,
        "bpm": row.bpm,
        "key_scale": row.key_scale,
        "duration_target_sec": row.duration_sec,
        "mood": row.mood,
        "seed": row.seed,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workflow": "hook_first_two_pass_valessa",
        "instrumental_path": str(instrumental),
        "instrumental_task_id": inst_task_id,
        "reused_instrumental": reused_instrumental,
        "vocal_cover_strength": VOCAL_COVER_STRENGTH,
        "task_id": vocal_result["task_id"],
        "hook": identity.hook_name if identity else "",
        "payload": vocal_payload,
        "stage": "hook_first",
        "style": "haya_valessa_bible",
        "notes": (
            "Pass1 instrumental; Pass2 cover at mid-high strength with thinking — "
            "natural pitched vocals locked to key/BPM (no DoRA)."
        ),
    }
    track_meta(row.slug).write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def generate_hook_first_track(
    row: TrackRow,
    *,
    api_base: str,
    api_key: str = "",
    force: bool = False,
    vocals_only: bool = False,
) -> Path:
    """Generate instrumental (optional), then vocal cover; write final MP3 + meta."""
    out_mp3 = track_mp3(row.slug)
    out_dir = track_dir(row.slug)
    out_dir.mkdir(parents=True, exist_ok=True)
    instrumental = out_dir / f"{row.slug}_instrumental.mp3"

    if out_mp3.exists() and not force and not vocals_only:
        print(f"SKIP (exists): {out_mp3}")
        return out_mp3

    inst_task_id: str | None = None
    reused = False

    if vocals_only:
        if not instrumental.exists():
            raise FileNotFoundError(
                f"vocals-only requires existing instrumental: {instrumental}"
            )
        reused = True
        print(f"PASS1 skipped — reusing {instrumental.name}")
    else:
        print(f"PASS1 instrumental ({row.slug})")
        inst_result = generate_to_file(
            build_instrumental_payload(row),
            api_base=api_base,
            api_key=api_key,
            out_path=instrumental,
            label=f"{row.slug}-inst",
        )
        inst_task_id = inst_result["task_id"]

    print(f"PASS2 vocal hook cover ({row.slug}) strength={VOCAL_COVER_STRENGTH}")
    vocal_payload = build_vocal_cover_payload(row, instrumental)
    vocal_result = generate_to_file(
        vocal_payload,
        api_base=api_base,
        api_key=api_key,
        out_path=out_mp3,
        label=f"{row.slug}-vocal",
    )
    _write_meta(
        row,
        instrumental=instrumental,
        inst_task_id=inst_task_id,
        vocal_result=vocal_result,
        vocal_payload=vocal_payload,
        reused_instrumental=reused,
    )
    print(f"OK: {out_mp3}")
    return out_mp3
