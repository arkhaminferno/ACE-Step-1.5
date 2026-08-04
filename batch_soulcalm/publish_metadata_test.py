"""Tests for soulcalm YouTube metadata export."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from batch_soulcalm.brand import BRAND_HANDLE, BRAND_NAME
from batch_soulcalm.publish_metadata import (
    build_description,
    build_song,
    build_tags,
    export_metadata,
)


class TestSoulcalmPublishFields(unittest.TestCase):
    """Descriptions stay personal; tags fill the YouTube SEO budget."""

    def test_description_is_short_personal_note(self) -> None:
        """Description is a few lines, no hashtag dump."""
        text = build_description(
            blurb="couldn't sleep.\nkept searching her name again.\n\nsoft piano + rain."
        )
        self.assertLess(len(text), 200)
        self.assertNotIn("#", text)
        self.assertNotIn("subscribe", text.lower())
        self.assertIn("soft piano", text)

    def test_tags_fill_near_500_chars(self) -> None:
        """SEO tags approach YouTube's ~500-char soft limit without exceeding."""
        tags = build_tags(
            title="i still search her name at 2am",
            slug="search_her_name_2am",
            extra_tags=["search her name", "2am overthinking"],
        )
        joined = ", ".join(tags)
        self.assertGreaterEqual(len(joined), 450)
        self.assertLessEqual(len(joined), 500)
        self.assertIn("sleep music", tags)
        self.assertIn("soft piano", tags)
        self.assertIn("rain sounds", tags)

    def test_build_song_title_matches_catalog(self) -> None:
        """Song title is the personal track name."""
        song = build_song(
            {
                "slug": "search_her_name_2am",
                "title": "i still search her name at 2am",
                "blurb": "couldn't sleep.\n\nsoft piano + rain.",
                "extra_tags": ["search her name"],
                "published": False,
                "duration_sec": 3600,
            }
        )
        self.assertEqual(song["title"], "i still search her name at 2am")
        self.assertEqual(song["youtubeFilename"], "search_her_name_2am-youtube.mp4")
        self.assertEqual(song["brand"], BRAND_NAME)
        self.assertLessEqual(len(", ".join(song["tags"])), 500)


class TestExportMetadata(unittest.TestCase):
    """Export writes brand payload for the extension."""

    def test_exports_search_her_name_2am(self) -> None:
        """metadata.json includes the first keeper track with SEO tags."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            meta = root / "metadata.json"
            out_dir = root / "output"
            with patch("batch_soulcalm.publish_metadata.OUTPUT_DIR", out_dir):
                export_metadata(path=meta)
            data = json.loads(meta.read_text(encoding="utf-8"))
            self.assertEqual(data["brand"], BRAND_NAME)
            self.assertEqual(data["handle"], BRAND_HANDLE)
            self.assertIn("search_her_name_2am", data["songs"])
            self.assertIn("its_2am_almost_texted_her", data["songs"])
            self.assertEqual(
                data["songs"]["its_2am_almost_texted_her"]["title"],
                "it's 2am, almost texted her again",
            )
            self.assertEqual(
                data["songs"]["she_is_just_a_wallpaper"]["title"],
                "she is just a wallpaper now",
            )
            self.assertEqual(
                data["songs"]["i_still_think_about_her"]["title"],
                "i still think about her",
            )
            song = data["songs"]["search_her_name_2am"]
            self.assertFalse(song["published"])
            self.assertLess(len(song["description"]), 200)
            tag_chars = len(", ".join(song["tags"]))
            self.assertGreaterEqual(tag_chars, 450)
            self.assertLessEqual(tag_chars, 500)
            self.assertEqual(
                data["slugAliases"]["search_her_name_2am-youtube"],
                "search_her_name_2am",
            )
            self.assertTrue(
                (out_dir / "search_her_name_2am" / "search_her_name_2am.youtube.json").is_file()
            )


if __name__ == "__main__":
    unittest.main()
