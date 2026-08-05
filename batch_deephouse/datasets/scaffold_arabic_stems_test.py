"""Tests for Arabic stem scaffold."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from batch_deephouse.datasets.scaffold_arabic_stems import SLOTS, write_slot


class TestScaffoldArabicStems(unittest.TestCase):
    """Fresh v2 slots cover core Recipe4 instruments."""

    def test_slots_include_core_leads(self) -> None:
        """Qanun/violin/oud/ney slots exist for full-palette training."""
        ids = " ".join(str(s["id"]) for s in SLOTS)
        for needle in ("oud_", "qanun_", "violin_", "ney_", "darbuka_", "kick_"):
            self.assertIn(needle, ids)

    def test_write_slot_creates_json_and_lyrics(self) -> None:
        """Each slot writes matching sidecars without audio."""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            write_slot(out, SLOTS[0], force=True)
            stem = str(SLOTS[0]["id"])
            self.assertTrue((out / f"{stem}.json").is_file())
            self.assertTrue((out / f"{stem}.lyrics.txt").is_file())
            self.assertFalse((out / f"{stem}.mp3").exists())


if __name__ == "__main__":
    unittest.main()
