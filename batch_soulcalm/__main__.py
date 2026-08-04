"""Allow: python -m batch_soulcalm render-still [slug] | export-metadata."""

from __future__ import annotations

import sys


def main() -> int:
    """Dispatch soulcalm subcommands."""
    if len(sys.argv) > 1 and sys.argv[1] == "export-metadata":
        from batch_soulcalm.publish_metadata import main as export_main

        return export_main()
    if len(sys.argv) > 1 and sys.argv[1] == "render-still":
        from batch_soulcalm.paths import ASSETS_DIR, OUTPUT_DIR
        from batch_soulcalm.video_still import render_still_video

        slug = sys.argv[2] if len(sys.argv) > 2 else "search_her_name_2am"
        image = ASSETS_DIR / f"{slug}.jpg"
        if not image.is_file():
            image = ASSETS_DIR / f"{slug}.png"
        audio = OUTPUT_DIR / slug / f"{slug}_60min.mp3"
        out = OUTPUT_DIR / slug / f"{slug}-youtube.mp4"
        print(f"image: {image}")
        print(f"audio: {audio}")
        path = render_still_video(
            image_path=image,
            audio_path=audio,
            output_path=out,
            fade_sec=4.0,
        )
        print(f"Rendered: {path}")
        return 0
    print("Usage: python -m batch_soulcalm render-still [slug] | export-metadata")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
