"""Unit tests for extract track mapping and payload building."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from batch_deephouse.stem_extract import (
    build_extract_payload,
    require_base_checkpoint,
    resolve_extract_track,
)


class TestResolveExtractTrack(unittest.TestCase):
    """Lead → ACE-Step class mapping."""

    def test_oud_maps_to_guitar(self) -> None:
        self.assertEqual(resolve_extract_track("oud"), "guitar")

    def test_ney_maps_to_woodwinds(self) -> None:
        self.assertEqual(resolve_extract_track("ney"), "woodwinds")

    def test_unknown_raises(self) -> None:
        with self.assertRaises(ValueError):
            resolve_extract_track("sitar")


class TestRequireBaseCheckpoint(unittest.TestCase):
    """Base model presence gate."""

    def test_missing_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                require_base_checkpoint(Path(tmp))

    def test_present_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "acestep-v15-base"
            base.mkdir()
            (base / "config.json").write_text("{}")
            self.assertEqual(require_base_checkpoint(Path(tmp)), base.resolve())


class TestBuildExtractPayload(unittest.TestCase):
    """Payload fields for DiT extract."""

    def test_payload_uses_staged_src_and_track(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            mix = Path(tmp) / "mix.mp3"
            mix.write_bytes(b"x")
            with patch(
                "batch_deephouse.stem_extract.stage_cover_src",
                return_value="/tmp/staged_mix.mp3",
            ):
                payload = build_extract_payload(src_audio=mix, lead="oud")
            self.assertEqual(payload["task_type"], "extract")
            self.assertEqual(payload["track_name"], "guitar")
            self.assertEqual(payload["src_audio_path"], "/tmp/staged_mix.mp3")
            self.assertFalse(payload["thinking"])
            self.assertFalse(payload["use_adg"])
            self.assertIn("guitar", payload["instruction"])


if __name__ == "__main__":
    unittest.main()
