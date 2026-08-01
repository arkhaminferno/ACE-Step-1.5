"""CLI: batch-render HAYA AE YouTube videos from approved song MP3s."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from batch_deephouse.ae_config import AE_WORK_ROOT, TEMPLATE_AEP
from batch_deephouse.ae_launcher import SMOKE_PROJECT, write_active_script, write_smoke_script
from batch_deephouse.ae_render_job import build_render_job, write_render_job
from batch_deephouse.ae_runner import prepare_project, render_job, run_active_script
from batch_deephouse.ae_titles import BACKGROUND_STILLS, DISPLAY_TITLES
from batch_deephouse.paths import OUTPUT_DIR


def _embed_metadata(mp4_path, *, title: str, artist: str) -> None:
    """Best-effort ffmpeg metadata stamp (non-fatal if ffmpeg fails)."""
    import subprocess
    import tempfile
    from pathlib import Path

    tmp = Path(tempfile.mkstemp(suffix=".mp4")[1])
    try:
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(mp4_path),
            "-c",
            "copy",
            "-metadata",
            f"title={title}",
            "-metadata",
            f"artist={artist}",
            str(tmp),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0 and tmp.is_file() and tmp.stat().st_size > 1_000_000:
            tmp.replace(mp4_path)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    """Batch AE render entrypoint for HAYA songs."""
    parser = argparse.ArgumentParser(
        description="Batch render HAYA AE template videos (1080p YouTube)",
    )
    parser.add_argument("--slug", default="", help="Render one slug only (e.g. yalil)")
    parser.add_argument("--force", action="store_true", help="Re-render even if MP4 exists")
    parser.add_argument("--inspect", action="store_true", help="List comps/layers in template")
    parser.add_argument("--smoke", action="store_true", help="Test AE scripting without render")
    parser.add_argument("--dry-run", action="store_true", help="Write job JSON only, no AE")
    parser.add_argument("--prep-only", action="store_true", help="Run JSX prep but skip aerender")
    parser.add_argument(
        "--short",
        action="store_true",
        help="Use short master MP3 instead of *_35min.mp3",
    )
    parser.add_argument(
        "--mp3",
        type=Path,
        default=None,
        help="Explicit audio path (e.g. shouf_human.mp3) for a one-off test",
    )
    parser.add_argument("--cooldown", type=int, default=5, help="Seconds after render")
    args = parser.parse_args(argv)

    if not TEMPLATE_AEP.is_file():
        raise SystemExit(f"Template not found: {TEMPLATE_AEP}")

    if args.smoke:
        if SMOKE_PROJECT.exists():
            SMOKE_PROJECT.unlink()
        write_smoke_script()
        run_active_script(expect_project=SMOKE_PROJECT, timeout_sec=300)
        print("SMOKE TEST PASSED")
        return 0

    if args.inspect:
        AE_WORK_ROOT.mkdir(parents=True, exist_ok=True)
        write_active_script(
            "inspect_project.jsx",
            job={"template_aep": str(TEMPLATE_AEP.resolve())},
        )
        run_active_script(timeout_sec=300)
        report = AE_WORK_ROOT / "inspect_report.txt"
        if report.is_file():
            print(report.read_text(encoding="utf-8"))
        else:
            print("Inspect finished but report missing:", report)
        return 0

    slug = args.slug.strip().lower()
    if not slug:
        # Default: locked YouTube catalog only (needs title + still + MP3).
        from batch_deephouse.ae_titles import LOCKED_YOUTUBE_SLUGS

        slugs = [
            s
            for s in LOCKED_YOUTUBE_SLUGS
            if s in DISPLAY_TITLES and s in BACKGROUND_STILLS
        ]
    else:
        slugs = [slug]

    if not slugs:
        print("No songs queued (need Arabic title + background still mapped).")
        return 0

    print(f"HAYA AE BATCH: {len(slugs)} video(s) queued")
    done = 0
    for key in slugs:
        folder = OUTPUT_DIR / key
        output_mp4 = folder / f"{key}-youtube.mp4"
        if not args.force and output_mp4.is_file():
            print(f"SKIP (video exists): {key} → {output_mp4}")
            continue

        job = build_render_job(
            slug=key,
            prefer_long=not args.short,
            mp3_override=args.mp3,
        )
        print(
            f"RENDER: {key} | title={job.display_name} | "
            f"{job.duration_sec / 60:.1f} min | {job.mp3_path.name} | "
            f"bg={job.bg_fit_mode}"
        )
        if args.dry_run:
            write_render_job(job)
            print(f"DRY RUN job: {job.job_json_path}")
            continue

        if args.prep_only:
            prepare_project(job)
            print(f"PREP DONE: {job.project_path}")
            continue

        raw_mp4 = render_job(job, cooldown_sec=args.cooldown)
        _embed_metadata(raw_mp4, title=job.title, artist=job.artist)
        done += 1
        print(f"VIDEO READY: {key} → {raw_mp4}")

    print(f"HAYA AE BATCH COMPLETE: {done}/{len(slugs)} rendered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
