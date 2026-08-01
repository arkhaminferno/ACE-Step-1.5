"""Tests for DUORUSH genre-anchor prompt injection and DoRA scale clamp."""

from __future__ import annotations

import unittest

from batch_deephouse.genre_anchor import (
    DEFAULT_DORA_SCALE,
    GENRE_ANCHOR,
    clamp_dora_scale,
    format_prompt,
)


class TestGenreAnchor(unittest.TestCase):
    """Genre anchor must lead the prompt and stay Deep House first."""

    def test_format_prompt_prefixes_anchor(self) -> None:
        """User text follows the Deep House genre anchor."""
        out = format_prompt("melancholic oud textures")
        self.assertTrue(out.startswith("Deep House"))
        self.assertIn(GENRE_ANCHOR, out)
        self.assertIn("melancholic oud textures", out)
        self.assertLess(out.index("Deep House"), out.index("oud"))

    def test_format_prompt_injects_bpm(self) -> None:
        """Optional BPM lands after the anchor."""
        out = format_prompt("ambient pads", bpm=122)
        self.assertIn("122 BPM", out)

    def test_clamp_dora_scale_bounds(self) -> None:
        """Scale is clamped to [0, 1]; default sits in the DUORUSH blend band."""
        self.assertEqual(clamp_dora_scale(-0.2), 0.0)
        self.assertEqual(clamp_dora_scale(1.5), 1.0)
        self.assertAlmostEqual(clamp_dora_scale(0.45), 0.45)
        self.assertGreaterEqual(DEFAULT_DORA_SCALE, 0.30)
        self.assertLessEqual(DEFAULT_DORA_SCALE, 0.40)
        self.assertAlmostEqual(DEFAULT_DORA_SCALE, 0.35)


if __name__ == "__main__":
    unittest.main()
