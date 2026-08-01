"""Tests for HAYA Recipe 2 (Hanan-approved lane)."""

from __future__ import annotations

import unittest

from batch_deephouse.haya_recipe2 import (
    CHORUS_EQUAL_HITS,
    RECIPE2_BPM,
    RECIPE2_DURATION,
    RECIPE2_HANAN_HOOK,
    RECIPE2_HANAN_SEED,
    build_recipe2_lyrics,
    build_recipe2_payload,
)


class TestHayaRecipe2(unittest.TestCase):
    """Recipe 2 locks grid + equal short chorus."""

    def test_payload_locks_bpm_grid_and_chorus_fix(self) -> None:
        """Payload must use 108 BPM, grid lock, and equal-chorus rule."""
        lyrics = build_recipe2_lyrics(
            hook=RECIPE2_HANAN_HOOK,
            verse1=["ا", "ب", "ج", "د"],
            verse2=["ه", "و", "ز", "ح"],
            verse3=["ط", "ي", "ك", "ل"],
        )
        payload = build_recipe2_payload(
            hook=RECIPE2_HANAN_HOOK,
            slug="hanan",
            lyrics=lyrics,
            seed=RECIPE2_HANAN_SEED,
        )
        self.assertEqual(payload["bpm"], RECIPE2_BPM)
        self.assertEqual(payload["audio_duration"], RECIPE2_DURATION)
        self.assertTrue(payload["thinking"])
        self.assertIn(CHORUS_EQUAL_HITS, payload["prompt"])
        self.assertIn("NO stretched/elongated third line", lyrics)
        self.assertIn("elongated third chorus", payload["lm_negative_prompt"])
        self.assertEqual(payload.get("recipe"), "haya_recipe2")

    def test_lyrics_repeat_hook_without_downbeat_stretch_note(self) -> None:
        """Lyrics must not ask for a special elongated downbeat third line."""
        lyrics = build_recipe2_lyrics(
            hook="يا حنان",
            verse1=["ا", "ب", "ج", "د"],
            verse2=["ه", "و", "ز", "ح"],
            verse3=["ط", "ي", "ك", "ل"],
        )
        self.assertNotIn("on the downbeat", lyrics)
        self.assertIn("يا حنان", lyrics)


if __name__ == "__main__":
    unittest.main()
