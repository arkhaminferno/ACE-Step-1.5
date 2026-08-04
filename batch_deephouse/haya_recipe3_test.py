"""Tests for HAYA Recipe 3 (intro + verses + instrumental chorus)."""

from __future__ import annotations

import unittest

from batch_deephouse.haya_recipe3 import (
    RECIPE3_BPM,
    RECIPE3_DURATION,
    RECIPE3_MAX_VOCAL_HITS,
    RECIPE3_REF_HOOK,
    SPARSE_HOOK_RULE,
    build_recipe3_lyrics,
    build_recipe3_payload,
)


class TestHayaRecipe3(unittest.TestCase):
    """Recipe 3: Recipe2 intro, verses, sparse hook, instrumental heart."""

    def test_payload_original_not_cover_and_sparse_hook(self) -> None:
        """Payload locks duration/BPM and forbids HAYA clones / hook spam."""
        lyrics = build_recipe3_lyrics(
            hook=RECIPE3_REF_HOOK,
            verse1=["ا", "ب", "ج", "د"],
            verse2=["ه", "و", "ز", "ح"],
            lead="oud",
        )
        payload = build_recipe3_payload(
            hook=RECIPE3_REF_HOOK,
            slug="lujain",
            lyrics=lyrics,
            seed=90101,
            lead="oud",
        )
        self.assertEqual(payload["bpm"], RECIPE3_BPM)
        self.assertEqual(payload["audio_duration"], RECIPE3_DURATION)
        self.assertEqual(payload.get("recipe"), "haya_recipe3")
        self.assertIn(SPARSE_HOOK_RULE, payload["instruction"])
        self.assertIn("DRY ACOUSTIC OUD", payload["prompt"])
        self.assertIn("NOT a remix/cover", payload["prompt"])
        self.assertIn("Do NOT sing the hook in every chorus", payload["instruction"])
        self.assertNotIn("every chorus, break, and outro", payload["instruction"])

    def test_lyrics_have_recipe2_intro_two_verses_and_sparse_hook(self) -> None:
        """Form: Recipe2 intro, 2 verses, 4 inst choruses, ≤4 hook hits."""
        lyrics = build_recipe3_lyrics(
            hook="روح",
            verse1=["روحي معك بهدوء", "والليل يحفظنا", "كل نبضة تنادي", "وأنت بعيد"],
            verse2=["خذني معك بلطف", "قبل ما يروح الليل", "لحن خفيف يلفّني", "وروحك تبقيني"],
        )
        self.assertIn("soft female hum mmm ~4–8s", lyrics)
        self.assertIn("kick enters by 8 seconds", lyrics)
        self.assertEqual(lyrics.count("[Verse]"), 2)
        self.assertEqual(lyrics.count("[Vocal Chorus]"), 2)
        self.assertEqual(lyrics.count("[Instrumental Chorus]"), 4)
        hits = [ln.strip() for ln in lyrics.splitlines() if ln.strip() == "روح"]
        self.assertEqual(len(hits), RECIPE3_MAX_VOCAL_HITS)

    def test_verse_lines_capped_at_four(self) -> None:
        """Each verse keeps at most four lines."""
        lyrics = build_recipe3_lyrics(
            hook="روح",
            verse1=["1", "2", "3", "4", "5"],
            verse2=["a", "b", "c", "d", "e"],
        )
        self.assertIn("4", lyrics)
        self.assertNotIn("\n5\n", f"\n{lyrics}\n")
        self.assertNotIn("\ne\n", f"\n{lyrics}\n")


if __name__ == "__main__":
    unittest.main()
