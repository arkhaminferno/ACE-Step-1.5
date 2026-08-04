"""Unit tests for Recipe 3 lead variants."""

from __future__ import annotations

import unittest

from batch_deephouse.haya_recipe3 import build_recipe3_lyrics, build_recipe3_payload
from batch_deephouse.haya_recipe3_leads import resolve_lead


class TestRecipe3Leads(unittest.TestCase):
    """Lead specs and payload wiring."""

    def test_resolve_oud_default(self) -> None:
        spec = resolve_lead("oud")
        self.assertIn("DRY ACOUSTIC OUD", spec["lock"])

    def test_resolve_piano_oud_alias(self) -> None:
        spec = resolve_lead("piano+oud")
        self.assertIn("PIANO", spec["lock"])

    def test_resolve_trio(self) -> None:
        spec = resolve_lead("trio")
        self.assertIn("LEAD MAP", spec["lock"])
        self.assertIn("piano", spec["lock"].lower())

    def test_payload_ney_ban_and_lock(self) -> None:
        lyrics = build_recipe3_lyrics(
            hook="يا ياسمين",
            verse1=["ا", "ب", "ج", "د"],
            verse2=["ه", "و", "ز", "ح"],
            lead="ney",
        )
        payload = build_recipe3_payload(
            hook="يا ياسمين",
            slug="yasmin",
            lyrics=lyrics,
            seed=1,
            lead="ney",
        )
        self.assertIn("LEAD LOCK — NEY", payload["prompt"])
        self.assertIn("saxophone", payload["lm_negative_prompt"])
        self.assertIn("airy ney", lyrics.lower())
        self.assertNotIn("every chorus, break, and outro", payload["instruction"])

    def test_trio_lyrics_section_map(self) -> None:
        lyrics = build_recipe3_lyrics(
            hook="يا أميرة",
            verse1=["ا", "ب", "ج", "د"],
            verse2=["ه", "و", "ز", "ح"],
            lead="piano_oud_ney",
        )
        self.assertIn("SOFT intimate piano only", lyrics)
        self.assertIn("DRY ACOUSTIC OUD star", lyrics)
        self.assertIn("airy NEY", lyrics)


if __name__ == "__main__":
    unittest.main()
