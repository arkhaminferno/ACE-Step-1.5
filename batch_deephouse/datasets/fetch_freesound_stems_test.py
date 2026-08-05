"""Tests for Freesound stem slot mapping (no network)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from batch_deephouse.datasets.fetch_freesound_stems import (
    _query_for,
    list_empty_slots,
)


class TestFetchFreesoundStems(unittest.TestCase):
    """Offline helpers for auto stem fill."""

    def test_query_maps_oud_and_qanun(self) -> None:
        """Known prefixes resolve to search strings."""
        self.assertIn("oud", (_query_for("oud_bayati_108_01") or "").lower())
        self.assertIn("qanun", (_query_for("qanun_rast_108_01") or "").lower())

    def test_list_empty_slots(self) -> None:
        """Slots with json but no mp3 are listed."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "oud_bayati_108_01.json").write_text("{}", encoding="utf-8")
            (root / "qanun_rast_108_01.json").write_text("{}", encoding="utf-8")
            (root / "qanun_rast_108_01.mp3").write_bytes(b"x")
            empty = list_empty_slots(root)
            self.assertEqual(empty, ["oud_bayati_108_01"])


if __name__ == "__main__":
    unittest.main()
