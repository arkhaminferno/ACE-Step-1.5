"""Tests for HAYA Recipe 4 (feel-good maqam + call-response + no piano)."""

from __future__ import annotations

import unittest

from batch_deephouse.haya_recipe4 import (
    RECIPE4_BPM,
    RECIPE4_DEFAULT_LEAD,
    RECIPE4_DURATION,
    RECIPE4_KEY,
    RECIPE4_REF_HOOK,
    TARAB_VOCAL,
    build_recipe4_lyrics,
    build_recipe4_payload,
)
from batch_deephouse.haya_recipe4_leads import resolve_lead


class TestHayaRecipe4(unittest.TestCase):
    """Recipe 4: bright maqam, qanun/violin, call-response, no piano."""

    def test_payload_feelgood_no_piano_bright_key(self) -> None:
        """Payload locks BPM/key and bans piano / HAYA clones."""
        lyrics = build_recipe4_lyrics(
            hook=RECIPE4_REF_HOOK,
            answer="ويا قلبي",
            verse1=["ا", "ب", "ج", "د"],
            verse2=["ه", "و", "ز", "ح"],
            lead="qanun_violin",
        )
        payload = build_recipe4_payload(
            hook=RECIPE4_REF_HOOK,
            slug="basma",
            lyrics=lyrics,
            seed=42001,
            lead="qanun_violin",
            answer="ويا قلبي",
        )
        self.assertEqual(payload["bpm"], RECIPE4_BPM)
        self.assertEqual(payload["audio_duration"], RECIPE4_DURATION)
        self.assertEqual(payload.get("key_scale"), RECIPE4_KEY)
        self.assertEqual(payload.get("recipe"), "haya_recipe4")
        self.assertIn("NO PIANO", payload["instruction"])
        self.assertIn("Rast", payload["prompt"])
        self.assertIn(TARAB_VOCAL, payload["prompt"])
        self.assertIn("piano", payload["lm_negative_prompt"])
        self.assertIn("NOT a remix/cover", payload["prompt"])
        self.assertEqual(payload.get("recipe4_lead"), "qanun_violin")

    def test_lyrics_call_response_and_drops(self) -> None:
        """Form includes call-response choruses and instrumental drops."""
        lyrics = build_recipe4_lyrics(
            hook="يا سماء",
            answer="ويا قلبي",
            verse1=["نبض خفيف", "والليل صافي", "لحن يفرح", "والقلب يطير"],
            verse2=["خذني بلطف", "فوق السحاب", "صوت ينادي", "ويا سماء"],
            lead=RECIPE4_DEFAULT_LEAD,
        )
        self.assertIn("CALL-AND-RESPONSE", lyrics)
        self.assertIn("يا سماء", lyrics)
        self.assertIn("ويا قلبي", lyrics)
        self.assertGreaterEqual(lyrics.count("[Instrumental Drop]"), 2)
        self.assertEqual(lyrics.count("[Chorus]"), 2)
        self.assertIn("no piano", lyrics.lower())

    def test_resolve_lead_rejects_piano(self) -> None:
        """Piano is not a Recipe4 lead — was removed as messy."""
        with self.assertRaises(ValueError):
            resolve_lead("piano")
        spec = resolve_lead("qanun")
        self.assertIn("QANUN", spec["lock"])


if __name__ == "__main__":
    unittest.main()
