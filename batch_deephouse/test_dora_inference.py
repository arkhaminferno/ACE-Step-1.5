"""Hot-swap a Side-Step DoRA checkpoint and generate a test loop via API.

Usage (from repo root, API on :8001):
  ./test_checkpoint.sh final 0.45
  ./test_checkpoint.sh 50 --weight 0.50 --wait
"""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.api_client import get_lora_status, load_lora, set_lora_scale
from batch_deephouse.dora_checkpoint import (
    DEFAULT_DORA_ROOT,
    list_epoch_checkpoints,
    resolve_adapter_dir,
)
from batch_deephouse.genre_anchor import (
    DEFAULT_DORA_SCALE,
    clamp_dora_scale,
    format_prompt,
)
from batch_deephouse.paths import DEFAULT_API_BASE

# DiT-only probe — genre-anchored; Arabic colour is texture, not recital.
DEFAULT_PROMPT_BODY = (
    "melancholic filtered oud textures behind the kick, ambient synth pads, "
    "warm reese sub, driving club-ready groove, no trumpet, no brass, "
    "no guzheng, no pipa, no dry solo taksim"
)
DEFAULT_LYRICS = "[Instrumental]"


def _wait_for_adapter(dora_root: Path, epoch: str, timeout_sec: int) -> Path:
    """Poll until the target checkpoint directory exists."""
    deadline = time.time() + timeout_sec
    while True:
        try:
            return resolve_adapter_dir(dora_root, epoch)
        except FileNotFoundError as exc:
            found = list_epoch_checkpoints(dora_root)
            print(f"Waiting for epoch={epoch} (have: {found or 'none'})...")
            if time.time() >= deadline:
                raise TimeoutError(str(exc)) from exc
            time.sleep(30)


def build_test_payload(
    *,
    bpm: int,
    key_scale: str,
    duration_sec: float,
    steps: int,
    seed: int,
    prompt_extras: str = "",
) -> dict:
    """Build a MPS-safe, genre-anchored text2music payload for DoRA evaluation."""
    extras = " ".join((prompt_extras or "").split())
    body = f"{DEFAULT_PROMPT_BODY} {extras}".strip()
    return {
        "prompt": format_prompt(body, bpm=bpm),
        "lyrics": DEFAULT_LYRICS,
        "thinking": False,
        "use_adg": False,
        "use_format": False,
        "use_cot_caption": False,
        "use_cot_language": False,
        "bpm": bpm,
        "key_scale": key_scale,
        "audio_duration": duration_sec,
        "inference_steps": steps,
        "guidance_scale": 14.0,
        "model": "acestep-v15-turbo",
        "task_type": "text2music",
        "vocal_language": "ar",
        "audio_format": "mp3",
        "use_random_seed": False,
        "seed": seed,
    }


def main() -> int:
    """CLI entry: load adapter → set scale → generate → save mp3."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epoch", default="50", help="Epoch N, best, final, or path")
    parser.add_argument("--dora-root", type=Path, default=DEFAULT_DORA_ROOT)
    parser.add_argument("--api-base", default=os.environ.get("ACE_API_BASE", DEFAULT_API_BASE))
    parser.add_argument("--api-key", default=os.environ.get("ACE_API_KEY", ""))
    parser.add_argument(
        "--lora-scale",
        "--weight",
        type=float,
        default=DEFAULT_DORA_SCALE,
        dest="lora_scale",
        help=f"DoRA blend weight 0–1 (default {DEFAULT_DORA_SCALE})",
    )
    parser.add_argument("--bpm", type=int, default=122)
    parser.add_argument("--key-scale", default="D minor")
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--steps", type=int, default=8, help="Turbo default is 8")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--wait", action="store_true", help="Wait until checkpoint exists")
    parser.add_argument("--wait-timeout", type=int, default=60 * 60 * 8)
    parser.add_argument(
        "--prompt-extras",
        default="",
        help="Extra prompt text appended after the genre-anchored body",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output mp3 path (default under output/test_outputs/)",
    )
    parser.add_argument(
        "--extract-midi",
        action="store_true",
        help="After generate: extract oud,ney stems (needs base model) → MIDI",
    )
    parser.add_argument(
        "--leads",
        default="oud,ney",
        help="Leads for --extract-midi (comma-separated)",
    )
    args = parser.parse_args()
    weight = clamp_dora_scale(args.lora_scale)

    adapter = (
        _wait_for_adapter(args.dora_root, args.epoch, args.wait_timeout)
        if args.wait
        else resolve_adapter_dir(args.dora_root, args.epoch)
    )
    adapter_name = adapter.name
    print(f"Loading adapter: {adapter}")
    print(f"DoRA weight: {weight}")

    status = get_lora_status(args.api_base, args.api_key)
    data = status.get("data", status) if isinstance(status, dict) else {}
    loaded = set(data.get("adapters") or [])
    if adapter_name in loaded:
        print(f"Adapter '{adapter_name}' already loaded — skipping reload")
    else:
        load_lora(
            args.api_base,
            str(adapter),
            args.api_key,
            adapter_name=adapter_name,
        )
    set_lora_scale(args.api_base, weight, args.api_key, adapter_name=adapter_name)
    status = get_lora_status(args.api_base, args.api_key)
    print(f"LoRA status: {status.get('data', status)}")

    out = args.out or (
        Path("output/test_outputs")
        / f"arabic_house_test_epoch_{args.epoch}_w{weight:.2f}.mp3"
    )
    payload = build_test_payload(
        bpm=args.bpm,
        key_scale=args.key_scale,
        duration_sec=args.duration,
        steps=args.steps,
        seed=args.seed,
        prompt_extras=args.prompt_extras,
    )
    meta = generate_to_file(
        payload,
        api_base=args.api_base,
        api_key=args.api_key,
        out_path=out,
        label=f"dora-{args.epoch}-w{weight:.2f}",
    )
    print(f"Saved: {out.resolve()} (task={meta['task_id']})")

    if args.extract_midi:
        from batch_deephouse.dora_midi_pipeline import run_extract_midi

        leads = [x.strip() for x in args.leads.split(",") if x.strip()]
        mids = run_extract_midi(
            mix_path=out,
            leads=leads,
            stem_dir=Path("output/test_outputs/stems"),
            midi_dir=Path("output/midi_exports"),
            api_base=args.api_base,
            api_key=args.api_key,
            checkpoints_dir=Path("checkpoints"),
            extract_steps=max(args.steps, 50),
            seed=args.seed,
            skip_extract=False,
        )
        for mid in mids:
            print(f"MIDI: {mid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
