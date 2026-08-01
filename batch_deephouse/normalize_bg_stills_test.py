"""Tests for 16:9 background still normalization (auto / stretch / cover)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from batch_deephouse.normalize_bg_stills import (
    is_approx_16x9,
    prepare_still_for_render,
    resolve_bg_source,
    stretch_to_16x9,
)


class TestAspectDetect(unittest.TestCase):
    """16:9 detection for stretch vs uniform."""

    def test_yalil_size_is_16x9(self) -> None:
        """1672x941 (Yalil) counts as already 16:9."""
        self.assertTrue(is_approx_16x9(1672, 941))

    def test_chatgpt_3x2_is_not_16x9(self) -> None:
        """1536x1024 must stretch."""
        self.assertFalse(is_approx_16x9(1536, 1024))


class TestPrepareStillForRender(unittest.TestCase):
    """Auto mode: uniform for 16:9, stretch otherwise."""

    def test_16x9_uses_uniform(self) -> None:
        """Near-16:9 source reports uniform and fills 1920x1080."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "yalil.png"
            Image.new("RGB", (1672, 941), color=(20, 30, 40)).save(src)
            dst = root / "out.png"
            mode = prepare_still_for_render(src, dst)
            self.assertEqual(mode, "uniform")
            with Image.open(dst) as im:
                self.assertEqual(im.size, (1920, 1080))

    def test_3x2_uses_stretch(self) -> None:
        """ChatGPT 3:2 source reports stretch."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "hawa.png"
            Image.new("RGB", (1536, 1024), color=(180, 40, 60)).save(src)
            dst = root / "out.png"
            mode = prepare_still_for_render(src, dst)
            self.assertEqual(mode, "stretch")
            with Image.open(dst) as im:
                self.assertEqual(im.size, (1920, 1080))


class TestResolveBgSource(unittest.TestCase):
    """Mapped assets win over ChatGPT backups."""

    def test_mapped_wins_over_original_chatgpt(self) -> None:
        """User-replaced ``assets/hawa.png`` is preferred over the backup."""
        with tempfile.TemporaryDirectory() as tmp:
            assets = Path(tmp)
            (assets / "_original_chatgpt").mkdir()
            orig = assets / "_original_chatgpt" / "hawa.png"
            mapped = assets / "hawa.png"
            Image.new("RGB", (10, 10), color=(1, 2, 3)).save(orig)
            Image.new("RGB", (10, 10), color=(9, 9, 9)).save(mapped)
            self.assertEqual(resolve_bg_source("hawa", "hawa.png", assets), mapped)

    def test_falls_back_to_original_chatgpt(self) -> None:
        """Backup is used only when the mapped asset is missing."""
        with tempfile.TemporaryDirectory() as tmp:
            assets = Path(tmp)
            (assets / "_original_chatgpt").mkdir()
            orig = assets / "_original_chatgpt" / "hawa.png"
            Image.new("RGB", (10, 10), color=(1, 2, 3)).save(orig)
            self.assertEqual(resolve_bg_source("hawa", "hawa.png", assets), orig)

    def test_falls_back_to_mapped_yalil(self) -> None:
        """Yalil-style UUID filenames use the mapped asset."""
        with tempfile.TemporaryDirectory() as tmp:
            assets = Path(tmp)
            mapped = assets / "bd4a5f15.png"
            Image.new("RGB", (16, 9), color=(1, 2, 3)).save(mapped)
            self.assertEqual(resolve_bg_source("yalil", "bd4a5f15.png", assets), mapped)


class TestStretchTo16x9(unittest.TestCase):
    """Stretch fills without cropping."""

    def test_3x2_becomes_1920x1080(self) -> None:
        """1536x1024 stretches to full frame."""
        im = Image.new("RGB", (1536, 1024), color=(180, 40, 60))
        out = stretch_to_16x9(im)
        self.assertEqual(out.size, (1920, 1080))


if __name__ == "__main__":
    unittest.main()
