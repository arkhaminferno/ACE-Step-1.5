"""Tests for HAYA YouTube metadata export."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from batch_deephouse.ae_titles import LOCKED_YOUTUBE_SLUGS
from batch_deephouse.publish_metadata import (
    build_song,
    build_tags,
    build_title,
    export_metadata,
)


class TestHayaPublishFields(unittest.TestCase):
    """Titles/tags front-load searchable deep-house terms."""

    def test_title_starts_with_english_then_arabic_name(self) -> None:
        """Title is Name + Arabic, then genre/mood suffix."""
        title = build_title(name="Hanan", native="حنان")
        self.assertEqual(
            title,
            "Hanan حنان — Arabic Deep House Mix 2026 | "
            "Dark Mood Night Drive Chill",
        )
        self.assertLessEqual(len(title), 100)
        self.assertTrue(title.startswith("Hanan حنان —"))

    def test_tags_prioritize_high_volume_seo(self) -> None:
        """Tags start with broad searchable terms and stay ≤500 chars."""
        tags = build_tags(slug="hanan", name="Hanan", native="حنان", hook="يا حنان")
        joined = ", ".join(tags)
        self.assertEqual(tags[0], "deep house")
        self.assertIn("arabic deep house", tags)
        self.assertIn("night drive music", tags)
        self.assertIn("دييب هاوس", tags)
        self.assertIn("موسيقى عربية", tags)
        self.assertGreater(len(joined), 250)
        self.assertLessEqual(len(joined), 500)

    def test_description_opens_with_search_snippet(self) -> None:
        """First description line carries primary SEO phrase."""
        song = build_song(
            {
                "slug": "hanan",
                "name": "Hanan",
                "native": "حنان",
                "hook": "يا حنان",
                "published": False,
            }
        )
        first_line = song["description"].splitlines()[0]
        self.assertIn("Arabic Deep House Mix 2026", first_line)
        self.assertIn("35-minute", song["description"])
        self.assertIn("@hayamusic.official", song["description"])

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
        self.assertEqual(song["audioFilename"], "noor_35min.mp3")


class TestExportMetadata(unittest.TestCase):
    """Export writes brand payload with locked catalog songs."""

    def test_exports_locked_songs(self) -> None:
        """metadata.json includes locked batch + prior uploads."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            meta = root / "metadata.json"
            out_dir = root / "output"
            with patch("batch_deephouse.publish_metadata.OUTPUT_DIR", out_dir):
                export_metadata(path=meta)
            data = json.loads(meta.read_text(encoding="utf-8"))
            self.assertEqual(data["brand"], "HAYA")
            for slug in LOCKED_YOUTUBE_SLUGS:
                self.assertIn(slug, data["songs"])
                self.assertFalse(data["songs"][slug]["published"])
            self.assertTrue(data["songs"]["yalil"]["published"])
            self.assertTrue(data["songs"]["noor"]["published"])
            self.assertTrue((out_dir / "safa" / "safa.youtube.json").is_file())
            self.assertEqual(data["handle"], "@hayamusic.official")
            self.assertTrue(data["songs"]["safa"]["title"].startswith("Safa صفاء —"))
            self.assertEqual(
                data["slugAliases"]["safa-youtube"],
                "safa",
            )


if __name__ == "__main__":
    unittest.main()
