"""ACE-Step extract-task helpers for isolating leads before MIDI.

``extract`` / ``lego`` / ``complete`` require a **base** DiT checkpoint
(``acestep-v15-base``), not turbo. Arabic Oud maps to ``guitar``; Ney to
``woodwinds`` (closest labeled classes in ACE-Step).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.generator import stage_cover_src

# User-facing lead name → ACE-Step extract track class
LEAD_TO_TRACK: dict[str, str] = {
    "oud": "guitar",
    "ney": "woodwinds",
    "flute": "woodwinds",
    "guitar": "guitar",
    "woodwinds": "woodwinds",
    "bass": "bass",
    "drums": "drums",
    "percussion": "percussion",
    "synth": "synth",
    "vocals": "vocals",
}

BASE_MODEL_DIRNAME = "acestep-v15-base"


def resolve_extract_track(lead: str) -> str:
    """Map a lead name (oud/ney/...) to an ACE-Step extract track class."""
    key = lead.strip().lower()
    if key not in LEAD_TO_TRACK:
        raise ValueError(
            f"Unknown lead {lead!r}. Choose one of: {sorted(LEAD_TO_TRACK)}"
        )
    return LEAD_TO_TRACK[key]


def require_base_checkpoint(checkpoints_dir: Path) -> Path:
    """Return base model dir or raise with a download hint."""
    path = checkpoints_dir.expanduser().resolve() / BASE_MODEL_DIRNAME
    if not path.is_dir() or not any(path.iterdir()):
        raise FileNotFoundError(
            f"Missing {path}\n"
            "ACE-Step extract is base-model-only. Download acestep-v15-base "
            "into ./checkpoints before running extract→MIDI."
        )
    return path


def build_extract_payload(
    *,
    src_audio: Path,
    lead: str,
    steps: int = 50,
    seed: int = 42,
    model: str = BASE_MODEL_DIRNAME,
) -> dict[str, Any]:
    """Build a DiT-only extract payload for one lead."""
    track = resolve_extract_track(lead)
    staged = stage_cover_src(src_audio)  # API needs absolute temp path
    return {
        "task_type": "extract",
        "src_audio_path": staged,
        "track_name": track,
        "instruction": f"Extract the {track} track from the audio:",
        "prompt": f"isolated dry {lead} lead",
        "lyrics": "[Instrumental]",
        "thinking": False,
        "use_adg": False,
        "use_format": False,
        "use_cot_caption": False,
        "use_cot_language": False,
        "model": model,
        "inference_steps": steps,
        "guidance_scale": 14.0,
        "use_random_seed": False,
        "seed": seed,
        "audio_format": "mp3",
        "vocal_language": "ar",
    }


def extract_lead_to_file(
    *,
    mix_path: Path,
    lead: str,
    out_path: Path,
    api_base: str,
    api_key: str = "",
    steps: int = 50,
    seed: int = 42,
    model: str = BASE_MODEL_DIRNAME,
) -> dict[str, Any]:
    """Extract one lead from a mix via /release_task and save the stem."""
    payload = build_extract_payload(
        src_audio=mix_path,
        lead=lead,
        steps=steps,
        seed=seed,
        model=model,
    )
    return generate_to_file(
        payload,
        api_base=api_base,
        api_key=api_key,
        out_path=out_path,
        label=f"extract-{lead}",
    )
