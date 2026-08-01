"""Tests for HAYA Arabic titles and AE job builder."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from batch_deephouse.ae_titles import arabic_title_for, background_still_for, display_title_for


class TestHayaTitles(unittest.TestCase):
    """On-screen Alhambra Latin titles and background mapping."""

    def test_yalil_display_title_is_latin(self) -> None:
        """AE title stays Latin 'yalil' (Alhambra), matching the AEP."""
        self.assertEqual(display_title_for("yalil"), "yalil")

    def test_yalil_arabic_for_metadata(self) -> None:
        """Arabic spelling is for metadata only, not the AE glyphs."""
        self.assertEqual(arabic_title_for("yalil"), "يا ليل")

    def test_yalil_background_still(self) -> None:
        """Yalil uses the provided portrait still filename."""
        self.assertIn("bd4a5f15", background_still_for("yalil"))

    def test_locked_catalog_backgrounds(self) -> None:
        """Locked songs use slug-named PNGs in ae_template/assets/."""
        self.assertEqual(background_still_for("rima"), "rima.png")
        self.assertEqual(background_still_for("luma"), "luma.png")
        self.assertEqual(display_title_for("safa"), "safa")
        self.assertEqual(arabic_title_for("qamar"), "قمر")

    def test_unknown_slug_raises(self) -> None:
        """Unmapped songs fail loudly until a still is provided."""
        with self.assertRaises(KeyError):
            background_still_for("nar")


class TestBuildRenderJob(unittest.TestCase):
    """Render job prefers long mixes when present."""

    def test_prefers_35min_mp3(self) -> None:
        """Job builder picks *_35min.mp3 over the short master."""
        from PIL import Image

        from batch_deephouse import ae_render_job as mod

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "yalil"
            folder.mkdir()
            short = folder / "yalil.mp3"
            long = folder / "yalil_35min.mp3"
            short.write_bytes(b"short")
            long.write_bytes(b"long")
            assets = root / "assets"
            assets.mkdir()
            bg = assets / "bd4a5f15-a571-44f2-a9e0-349a48312fa3.png"
            # Already 16:9 — prepare should use uniform (no stretch).
            Image.new("RGB", (1672, 941), color=(10, 20, 30)).save(bg)
            prepared_dir = root / "bg_prepared"

            with (
                patch.object(mod, "OUTPUT_DIR", root),
                patch.object(mod, "TEMPLATE_ASSETS", assets),
                patch.object(mod, "AE_JOBS_DIR", root / "jobs"),
                patch.object(mod, "AE_PROJECTS_DIR", root / "projects"),
                patch.object(mod, "AE_BG_PREPARED_DIR", prepared_dir),
                patch.object(mod, "probe_duration_sec", return_value=2100.0),
            ):
                job = mod.build_render_job(slug="yalil")
            self.assertEqual(job.mp3_path.name, "yalil_35min.mp3")
            self.assertEqual(job.display_name, "yalil")
            self.assertAlmostEqual(job.duration_sec, 2100.0)
            self.assertEqual(job.bg_fit_mode, "uniform")
            self.assertTrue(job.background_path.is_file())

    def test_prefers_35min_human_mp3(self) -> None:
        """Human 35-min master wins over raw 35-min when both exist."""
        from PIL import Image

        from batch_deephouse import ae_render_job as mod

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "hawa"
            folder.mkdir()
            (folder / "hawa.mp3").write_bytes(b"short")
            (folder / "hawa_35min.mp3").write_bytes(b"long")
            (folder / "hawa_35min_human.mp3").write_bytes(b"human")
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (1672, 941), color=(10, 20, 30)).save(assets / "hawa.png")
            prepared_dir = root / "bg_prepared"

            with (
                patch.object(mod, "OUTPUT_DIR", root),
                patch.object(mod, "TEMPLATE_ASSETS", assets),
                patch.object(mod, "AE_JOBS_DIR", root / "jobs"),
                patch.object(mod, "AE_PROJECTS_DIR", root / "projects"),
                patch.object(mod, "AE_BG_PREPARED_DIR", prepared_dir),
                patch.object(mod, "probe_duration_sec", return_value=2100.0),
            ):
                job = mod.build_render_job(slug="hawa")
            self.assertEqual(job.mp3_path.name, "hawa_35min_human.mp3")
            self.assertEqual(job.bg_fit_mode, "uniform")


if __name__ == "__main__":
    unittest.main()
