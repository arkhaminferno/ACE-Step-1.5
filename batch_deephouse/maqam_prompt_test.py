"""Tests for maqam-aware HAYA prompt helpers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from batch_deephouse.maqam_prompt import (
    ARABIC_INSTRUMENTS,
    MAQAMAT,
    build_genre_tags,
    default_haya_genre_tags,
    format_lyric_sections,
    resolve_icl_stems,
)
from batch_deephouse.prompts import build_caption


class TestMaqamPromptBuilder(unittest.TestCase):
    """Structured tags and lyric formatting stay stable."""

    def test_genre_tags_join_nonempty_components(self) -> None:
        """Empty fields are dropped; order stays genre→instrument→…"""
        tags = build_genre_tags(
            genre="arabic deep house",
            instrument=ARABIC_INSTRUMENTS["oud"],
            rhythm="",
            mood="hypnotic",
            gender="female",
            timbre="airy",
            maqam=MAQAMAT["hijaz"],
        )
        self.assertIn("arabic deep house", tags)
        self.assertIn("traditional acoustic dry oud", tags)
        self.assertIn("female", tags)
        self.assertNotIn("  ", tags)

    def test_lyric_sections_use_double_newlines(self) -> None:
        """Section blocks must be separated by exactly two newlines."""
        out = format_lyric_sections(
            {
                "verse": "line one\nline two",
                "chorus": "hook line",
            }
        )
        self.assertIn("[verse]\nline one\nline two", out)
        self.assertIn("[chorus]\nhook line", out)
        self.assertIn("\n\n", out)
        self.assertEqual(out.count("\n\n"), 1)

    def test_icl_stems_report_missing(self) -> None:
        """Missing stems return dual_track_ready=False and a warning."""
        with tempfile.TemporaryDirectory() as tmp:
            result = resolve_icl_stems(Path(tmp), "ref_track")
        self.assertFalse(result["dual_track_ready"])
        self.assertIsNone(result["vocal_prompt_path"])
        self.assertIn("Stems not found", str(result["warning"]))

    def test_icl_stems_ready_when_both_exist(self) -> None:
        """Both UVR stems present → dual_track_ready."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ref_vocal.wav").write_bytes(b"RIFF")
            (root / "ref_instrumental.wav").write_bytes(b"RIFF")
            result = resolve_icl_stems(root, "ref")
        self.assertTrue(result["dual_track_ready"])
        self.assertIsNone(result["warning"])

    def test_caption_includes_maqam_genre_tags(self) -> None:
        """Vocal captions append structured Arabic genre tags."""
        caption = build_caption(slug="hayati", bpm=112, key_scale="G minor")
        self.assertIn("GenreTags:", caption)
        self.assertIn("arabic melodic deep house", caption)
        self.assertIn("maqam", caption.lower())

    def test_default_tags_include_bpm(self) -> None:
        """Default HAYA tags lock the requested BPM into the genre line."""
        tags = default_haya_genre_tags(bpm=124, maqam="bayati")
        self.assertIn("124 bpm", tags)
        self.assertIn("bayati", tags)


if __name__ == "__main__":
    unittest.main()
