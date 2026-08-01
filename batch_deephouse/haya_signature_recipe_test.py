"""Tests for HAYA signature recipe — Rima open + earworm."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from batch_deephouse.haya_signature_recipe import (
    EARWORM_MOTIF,
    NIGHT_DRIVE_SPICE,
    ORGANIC_PRODUCTION,
    RIMA_ARRANGEMENT,
    RIMA_COLOR,
    SIGNATURE_BPM,
    SIGNATURE_KEY,
    SIGNATURE_LM,
    build_signature_lyrics,
    build_signature_payload,
    master_signature_mp3,
)


class TestHayaSignatureRecipe(unittest.TestCase):
    """Signature payload, Rima lyrics shape, and master helpers."""

    def test_payload_locks_rima_open_and_earworm(self) -> None:
        """Payload must include Rima arrangement + thinking LM + spice."""
        lyrics = build_signature_lyrics(
            hook_lines=["خليني أحلم", "الليلة معك"],
            verse1=["سطر واحد", "سطر اثنين", "سطر ثلاثة", "سطر اربعة"],
            verse2=["سطر واحد", "سطر اثنين", "سطر ثلاثة", "سطر اربعة"],
            shape="rima",
        )
        payload = build_signature_payload(
            hook="خليني أحلم",
            slug="layan",
            lyrics=lyrics,
            seed=99201,
            motif_note="soft vocal phrase خليني أحلم after beat drop",
        )
        self.assertTrue(payload["thinking"])
        self.assertEqual(payload["lm_model_path"], SIGNATURE_LM)
        self.assertEqual(payload["batch_size"], 1)
        self.assertEqual(payload["bpm"], SIGNATURE_BPM)
        self.assertEqual(payload["key_scale"], SIGNATURE_KEY)
        self.assertIn(RIMA_ARRANGEMENT, payload["prompt"])
        self.assertIn(EARWORM_MOTIF, payload["prompt"])
        self.assertIn(NIGHT_DRIVE_SPICE, payload["prompt"])
        self.assertIn(ORGANIC_PRODUCTION, payload["prompt"])
        self.assertIn(RIMA_COLOR, payload["prompt"])
        self.assertIn("SHORT soft female hum/vocal", payload["instruction"])

    def test_rima_lyrics_open_before_chorus(self) -> None:
        """Rima shape must put soft intro + verse before chorus motif."""
        lyrics = build_signature_lyrics(
            hook_lines=["خليني أحلم"],
            verse1=["الليل هادي", "وصوتي خفيف", "والنبض بطيء", "وأنتِ في بالي"],
            verse2=["ه", "و", "ز", "ح"],
            shape="rima",
        )
        intro_at = lyrics.index("[Intro]")
        verse_at = lyrics.index("[Verse]")
        chorus_at = lyrics.index("[Chorus]")
        self.assertLess(intro_at, verse_at)
        self.assertLess(verse_at, chorus_at)
        self.assertIn("soft female hum mmm ~4–8s", lyrics)
        self.assertIn("beat enters by 8 seconds", lyrics)
        self.assertIn("خليني أحلم", lyrics)
        self.assertNotIn("ليان ليان", lyrics)

    def test_master_writes_human_and_upload(self) -> None:
        """Master helper writes listen + upload and returns AI score."""
        raw = Path("/tmp/fake_rima.mp3")
        listen = Path("/tmp/fake_rima_human.mp3")
        with (
            patch(
                "batch_deephouse.haya_signature_recipe.humanize_mp3"
            ) as mock_humanize,
            patch(
                "batch_deephouse.haya_signature_recipe.harden_for_upload",
                return_value=(listen, 48000, 0.01),
            ),
            patch.object(Path, "write_bytes"),
            patch.object(Path, "unlink"),
            patch.object(Path, "read_bytes", return_value=b"x"),
        ):
            out, ai = master_signature_mp3(raw, slug="fake_rima")
        self.assertEqual(out.name, "fake_rima_human.mp3")
        self.assertAlmostEqual(ai, 0.01)
        mock_humanize.assert_called_once()


if __name__ == "__main__":
    unittest.main()
