"""Tests for long-mix builder and clean lyrics."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from batch_deephouse.extend_mix import build_crossfade_long_mix
from batch_deephouse.prompts import build_lyrics


class TestLyricsClean(unittest.TestCase):
    """Ensure debut lyrics stay clean / non-vulgar."""

    def test_lyrics_are_clean_night_longing(self) -> None:
        """Lyrics contain romantic night phrases, not vulgar words."""
        lyrics = build_lyrics()
        self.assertIn("يا ليل يا ليلي", lyrics)
        self.assertIn("خذني بعيداً بهدوء", lyrics)
        banned = ("جنس", "نيك", "شرموط", "كس", "زب")
        lower = lyrics.lower()
        for word in banned:
            self.assertNotIn(word, lyrics)
            self.assertNotIn(word, lower)


class TestExtendMix(unittest.TestCase):
    """Long-mix helper behavior."""

    def test_rejects_very_short_source(self) -> None:
        """Crossfade builder rejects sources that are too short."""
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "short.mp3"
            src.write_bytes(b"x")
            dst = Path(tmp) / "out.mp3"
            with patch(
                "batch_deephouse.extend_mix.probe_duration_sec",
                return_value=8.0,
            ):
                with self.assertRaises(ValueError):
                    build_crossfade_long_mix(src, dst, target_sec=60, crossfade_sec=6)

    def test_default_fade_in_is_zero(self) -> None:
        """Default open fade is off; joins use a short blend near 3:00."""
        import inspect

        params = inspect.signature(build_crossfade_long_mix).parameters
        self.assertEqual(params["fade_in_sec"].default, 0.0)
        self.assertLessEqual(params["crossfade_sec"].default, 6.0)
        self.assertNotIn("loop_skip_intro_sec", params)


if __name__ == "__main__":
    unittest.main()
