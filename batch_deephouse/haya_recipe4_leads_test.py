"""Tests for Recipe 4 lead specs."""

from __future__ import annotations

import unittest

from batch_deephouse.haya_recipe4_leads import LEAD_SPECS, resolve_lead


class TestRecipe4Leads(unittest.TestCase):
    """Lead catalog: high-affect Arabic timbres, no piano."""

    def test_default_alias_is_qanun_violin(self) -> None:
        """default/feelgood aliases resolve to qanun_violin."""
        self.assertEqual(resolve_lead("default")["label"], resolve_lead("qanun_violin")["label"])
        self.assertEqual(resolve_lead("feelgood")["label"], resolve_lead("qanun_violin")["label"])

    def test_no_piano_in_catalog(self) -> None:
        """Piano leads are intentionally absent."""
        self.assertNotIn("piano", LEAD_SPECS)
        self.assertNotIn("piano_oud", LEAD_SPECS)
        for spec in LEAD_SPECS.values():
            self.assertIn("piano", spec["ban"].lower())


if __name__ == "__main__":
    unittest.main()
