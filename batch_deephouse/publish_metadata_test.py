"""Tests for HAYA YouTube metadata export."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from batch_deephouse.publish_metadata import (
    build_song,
    build_tags,
    build_title,
    export_metadata,
)


class TestHayaPublishFields(unittest.TestCase):
    """Titles/tags match Yalil/Noor Dark Mood style."""

    def test_title_uses_english_then_arabic_template(self) -> None:
        """Title is Name + Arabic + fixed night-drive suffix."""
        title = build_title(name="Hawa", native="هوا")
        self.assertEqual(
            title,
            "Hawa هوا — Arabic Deep House Night Drive Mix 2026 | Dark Chill Vocal House",
        )
        self.assertLessEqual(len(title), 100)

    def test_tags_near_500_chars(self) -> None:
        """Comma-joined tags stay within ~500 Studio soft limit."""
        tags = build_tags(slug="hawa", name="Hawa", native="هوا", hook="هوا هوا")
        joined = ", ".join(tags)
        self.assertGreater(len(joined), 250)
        self.assertLessEqual(len(joined), 500)

    def test_build_song_marks_published(self) -> None:
        """Catalog published flag flows into the song object."""
        song = build_song(
            {
                "slug": "noor",
                "name": "Noor",
                "native": "نور",
                "hook": "نور نور",
                "published": True,
            }
        )
        self.assertTrue(song["published"])
        self.assertEqual(song["youtubeFilename"], "noor-youtube.mp4")


class TestExportMetadata(unittest.TestCase):
    """Export writes brand payload with all catalog songs."""

    def test_exports_all_songs(self) -> None:
        """metadata.json includes pending + uploaded HAYA songs."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            meta = root / "metadata.json"
            out_dir = root / "output"
            with patch("batch_deephouse.publish_metadata.OUTPUT_DIR", out_dir):
                export_metadata(path=meta)
            data = json.loads(meta.read_text(encoding="utf-8"))
            self.assertEqual(data["brand"], "HAYA")
            for slug in ("yalil", "noor", "hawa", "rouh", "ward", "shouf", "baid"):
                self.assertIn(slug, data["songs"])
            self.assertTrue(data["songs"]["yalil"]["published"])
            self.assertFalse(data["songs"]["baid"]["published"])
            self.assertTrue((out_dir / "baid" / "baid.youtube.json").is_file())


if __name__ == "__main__":
    unittest.main()
