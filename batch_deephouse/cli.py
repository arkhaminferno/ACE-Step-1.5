"""CLI for deep house track generation.

Always uses base ACE-Step turbo with no DoRA/LoRA unless you opt into
``test_dora_inference`` / ``test_checkpoint.sh`` separately.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from batch_deephouse.api_client import get_lora_status, unload_lora
from batch_deephouse.catalog import enabled_tracks, load_tracks
from batch_deephouse.generator import generate_track
from batch_deephouse.paths import DEFAULT_API_BASE, DEFAULT_CSV, track_dir, track_mp3


def _assert_no_dora(api_base: str, api_key: str = "") -> None:
    """Unload any adapter and abort if LoRA is still active."""
    try:
        unload_lora(api_base, api_key)
    except Exception as exc:  # noqa: BLE001
        print(f"DoRA unload note: {exc}")
    status = get_lora_status(api_base, api_key)
    data = status.get("data", status) if isinstance(status, dict) else {}
    loaded = bool(data.get("lora_loaded"))
    use_lora = bool(data.get("use_lora"))
    adapters = data.get("adapters") or []
    print(f"LoRA status: loaded={loaded} use_lora={use_lora} adapters={adapters}")
    if loaded or use_lora or adapters:
        raise SystemExit(
            "DoRA/LoRA still active — restart the API, then retry. "
            "HAYA generation requires a clean base turbo."
        )
    print("Confirmed: base turbo only (no DoRA)")


def _build_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="batch_deephouse",
        description="Generate Arabic deep house pilots via ACE-Step (base turbo, no DoRA).",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV,
        help="Track catalog CSV (default: input/tracks.csv)",
    )
    parser.add_argument(
        "--slug",
        type=str,
        default="",
        help="Generate only this slug (must exist in CSV)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max enabled tracks to generate (0 = all)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate even if MP3 already exists",
    )
    parser.add_argument(
        "--vocals-only",
        action="store_true",
        help="Reuse existing {slug}_instrumental.mp3; only re-run vocal cover",
    )
    parser.add_argument(
        "--repaint-start",
        type=float,
        default=None,
        help="Surgical repaint window start (seconds); requires --repaint-end",
    )
    parser.add_argument(
        "--repaint-end",
        type=float,
        default=None,
        help="Surgical repaint window end (seconds); requires --repaint-start",
    )
    parser.add_argument(
        "--extract-vocals",
        action="store_true",
        help="After mix exists, extract vocal stem via acestep-v15-base",
    )
    parser.add_argument(
        "--api-base",
        default=os.environ.get("ACESTEP_API_BASE", DEFAULT_API_BASE),
        help="ACE-Step API base URL",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("ACESTEP_API_KEY", ""),
        help="Optional API key",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List catalog tracks and exit",
    )
    parser.add_argument(
        "--deliver",
        action="store_true",
        help="After generate, humanize + AI-stealth to *_upload.mp3",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run deep house generation CLI."""
    args = _build_parser().parse_args(argv)
    if not args.csv.exists():
        raise SystemExit(f"CSV not found: {args.csv}")

    rows = load_tracks(args.csv)
    if args.list:
        for row in rows:
            flag = "on" if row.enabled else "off"
            print(
                f"{row.slug:40} {row.duration_sec:4}s  "
                f"{row.bpm} BPM  [{flag}]  {row.title}"
            )
        return 0

    selected = enabled_tracks(args.csv)
    if args.slug:
        selected = [row for row in rows if row.slug == args.slug]
        if not selected:
            raise SystemExit(f"Slug not in CSV: {args.slug}")

    if args.limit and args.limit > 0:
        selected = selected[: args.limit]

    if not selected:
        print("No tracks selected.")
        return 0

    repaint = args.repaint_start is not None or args.repaint_end is not None
    if repaint and (args.repaint_start is None or args.repaint_end is None):
        raise SystemExit("Both --repaint-start and --repaint-end are required.")

    _assert_no_dora(args.api_base, args.api_key)

    for row in selected:
        if repaint:
            from batch_deephouse.repaint import repaint_track_window

            print(
                f"REPAINT: {row.title} ({row.slug}) "
                f"{args.repaint_start}s–{args.repaint_end}s"
            )
            out = repaint_track_window(
                row,
                start_sec=float(args.repaint_start),
                end_sec=float(args.repaint_end),
                api_base=args.api_base,
                api_key=args.api_key,
            )
        else:
            print(f"GENERATE: {row.title} ({row.slug}) — {row.duration_sec}s")
            out = generate_track(
                row,
                api_base=args.api_base,
                api_key=args.api_key,
                force=args.force,
                vocals_only=args.vocals_only,
            )

        if args.extract_vocals:
            from batch_deephouse.stem_extract import extract_lead_to_file

            mix = track_mp3(row.slug) if not repaint else out
            vocal_out = track_dir(row.slug) / f"{row.slug}_vocals.mp3"
            print(f"EXTRACT vocals → {vocal_out.name}")
            extract_lead_to_file(
                mix_path=mix,
                lead="vocals",
                out_path=vocal_out,
                api_base=args.api_base,
                api_key=args.api_key,
            )
            print(f"OK: {vocal_out}")

        if args.deliver:
            from batch_deephouse.deliver import deliver_mp3

            human, upload, ai_prob = deliver_mp3(
                out,
                name=row.title,
                bpm=row.bpm,
                mode="stealth",
            )
            print(f"HUMANIZED: {human}")
            if ai_prob < 0:
                print(f"UPLOAD:    {upload} (raw passthrough)")
            else:
                print(f"UPLOAD:    {upload} (AI score {ai_prob:.4f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
