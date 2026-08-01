"""Tests for HAYA surgical repaint payloads."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from batch_deephouse.catalog import TrackRow
from batch_deephouse.repaint import build_repaint_payload


class TestRepaintPayload(unittest.TestCase):
    """Repaint windows stay surgical and use base DiT by default."""

    def _row(self) -> TrackRow:
        return TrackRow(
            title="Hayati",
            slug="hayati",
            bpm=112,
            key_scale="G minor",
            duration_sec=130,
            seed=1,
            mood="cover beat",
            enabled=True,
            cover_strength=0.75,
            cover_src="/tmp/ref.mp3",
        )

    def test_rejects_inverted_window(self) -> None:
        """end must be after start."""
        with self.assertRaises(ValueError):
            with patch(
                "batch_deephouse.repaint.stage_cover_src",
                return_value="/tmp/staged.mp3",
            ):
                build_repaint_payload(
                    self._row(),
                    src_audio=Path("/tmp/hayati.mp3"),
                    start_sec=50,
                    end_sec=40,
                )

    def test_sets_repaint_fields(self) -> None:
        """Payload uses task_type=repaint and second window bounds."""
        with patch(
            "batch_deephouse.repaint.stage_cover_src",
            return_value="/tmp/staged_hayati.mp3",
        ), patch(
            "batch_deephouse.generator.stage_cover_src",
            return_value="/tmp/staged_ref.mp3",
        ):
            payload = build_repaint_payload(
                self._row(),
                src_audio=Path("/tmp/hayati.mp3"),
                start_sec=45.0,
                end_sec=52.0,
            )
        self.assertEqual(payload["task_type"], "repaint")
        self.assertEqual(payload["repainting_start"], 45.0)
        self.assertEqual(payload["repainting_end"], 52.0)
        self.assertEqual(payload["model"], "acestep-v15-base")
        self.assertFalse(payload["thinking"])
        self.assertNotIn("audio_cover_strength", payload)


if __name__ == "__main__":
    unittest.main()
