"""Tests for HAYA sound bible and hook-first two-pass payloads."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from batch_deephouse.catalog import TrackRow
from batch_deephouse.haya_sound_bible import HAYA_BPM, VOCAL_PERSONA
from batch_deephouse.hook_pipeline import (
    VOCAL_COVER_STRENGTH,
    build_instrumental_payload,
    build_vocal_cover_payload,
)
from batch_deephouse.prompts import build_caption, build_lyrics


class TestHayaSoundBible(unittest.TestCase):
    """Artist bible stays locked and structured."""

    def test_bpm_locked(self) -> None:
        """Default HAYA tempo is Valessa-lane deep house ~122."""
        self.assertEqual(HAYA_BPM, 122)

    def test_vocal_persona_not_generic_arabic(self) -> None:
        """Persona must demand a real human singer, not stock Arabic vocals."""
        self.assertIn("Real young female", VOCAL_PERSONA)
        self.assertIn("NOT TTS", VOCAL_PERSONA)
        self.assertNotIn("Beautiful Arabic", VOCAL_PERSONA)

    def test_caption_is_sectioned(self) -> None:
        """Vocal caption uses Genre:/Vocals: sections and pitch lock."""
        caption = build_caption(slug="gharib", bpm=124, key_scale="A minor")
        self.assertIn("Genre:", caption)
        self.assertIn("Vocals:", caption)
        self.assertIn("يا غريبي", caption)
        self.assertIn("A minor", caption)
        self.assertIn("ON THE BEAT", caption)

    def test_gharib_lyrics_have_verses_not_hook_only(self) -> None:
        """Gharib must include verse storytelling lines beyond the hook."""
        lyrics = build_lyrics("gharib")
        self.assertIn("[Verse 1", lyrics)
        self.assertIn("[Verse 2", lyrics)
        self.assertIn("[Bridge", lyrics)
        self.assertIn("شفتك من بعيد", lyrics)
        self.assertIn("كل ليلة أفكّر", lyrics)
        # Hook present but not the only content.
        self.assertIn("يا غريبي", lyrics)
        self.assertGreater(len(lyrics.splitlines()), 20)


class TestHookPipelinePayloads(unittest.TestCase):
    """Two-pass payloads: instrumental then vocal cover."""

    def _row(self) -> TrackRow:
        return TrackRow(
            title="Gharib",
            slug="gharib",
            bpm=124,
            key_scale="A minor",
            duration_sec=120,
            seed=1,
            mood="full vocals",
            enabled=True,
        )

    def test_instrumental_has_no_sung_lyrics(self) -> None:
        """Pass 1 must be instrumental-only."""
        payload = build_instrumental_payload(self._row())
        self.assertEqual(payload["lyrics"], "[Instrumental]")
        self.assertEqual(payload["task_type"], "text2music")
        self.assertIn("No vocals", payload["prompt"])

    def test_vocal_pass_is_cover_of_instrumental(self) -> None:
        """Pass 2 covers the instrumental and plants full verse+chorus vocals."""
        with patch(
            "batch_deephouse.hook_pipeline.stage_cover_src",
            return_value="/tmp/haya_cover_gharib_instrumental.mp3",
        ):
            payload = build_vocal_cover_payload(
                self._row(),
                Path("/tmp/fake_instrumental.mp3"),
            )
        self.assertEqual(payload["task_type"], "cover")
        self.assertTrue(payload["thinking"])
        self.assertIn("يا غريبي", payload["lyrics"])
        self.assertIn("شفتك من بعيد", payload["lyrics"])
        self.assertAlmostEqual(payload["audio_cover_strength"], 0.78)
        self.assertAlmostEqual(VOCAL_COVER_STRENGTH, 0.78)
        self.assertEqual(payload["inference_steps"], 28)
        self.assertIn("NOT hook-only", payload["instruction"])


if __name__ == "__main__":
    unittest.main()
