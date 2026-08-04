"""Tests for soulcalm prompts and video path checks."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from batch_soulcalm.prompts import build_caption, build_payload
from batch_soulcalm.video_still import render_still_video


class TestSoulcalmPrompts(unittest.TestCase):
    """Caption/payload stay instrumental, slow, and sleep-safe."""

    def test_caption_is_instrumental_only(self) -> None:
        """Caption must forbid vocals and favor piano + retro pads."""
        caption = build_caption()
        self.assertIn("instrumental only", caption.lower())
        self.assertIn("piano", caption.lower())
        self.assertIn("retro", caption.lower())

    def test_payload_sample_duration(self) -> None:
        """Payload uses requested duration and instrumental flag."""
        payload = build_payload(duration_sec=180, seed=1)
        self.assertEqual(payload["duration"], 180.0)
        self.assertEqual(payload["bpm"], 70)
        self.assertEqual(payload["key_scale"], "A minor")
        self.assertEqual(payload["task_type"], "text2music")
        self.assertTrue(payload.get("instrumental"))


class TestRenderStillGuards(unittest.TestCase):
    """render_still_video fails clearly when inputs are missing."""

    def test_missing_image_raises(self) -> None:
        """Missing still image raises FileNotFoundError."""
        with patch("batch_soulcalm.video_still.shutil.which", return_value="/usr/bin/ffmpeg"):
            with self.assertRaises(FileNotFoundError):
                render_still_video(
                    image_path=Path("/tmp/does-not-exist-soulcalm.jpg"),
                    audio_path=Path("/tmp/also-missing.mp3"),
                    output_path=Path("/tmp/out.mp4"),
                )


if __name__ == "__main__":
    unittest.main()
