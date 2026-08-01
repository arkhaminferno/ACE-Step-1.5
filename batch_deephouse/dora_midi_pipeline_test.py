"""Unit tests for extract→MIDI orchestration."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from batch_deephouse.dora_midi_pipeline import run_extract_midi


class TestRunExtractMidi(unittest.TestCase):
    """Orchestration with mocked extract + transcription."""

    def test_skip_extract_uses_existing_stem(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mix = root / "loop.mp3"
            mix.write_bytes(b"mix")
            stem_dir = root / "stems"
            stem_dir.mkdir()
            stem = stem_dir / "loop_oud_stem.mp3"
            stem.write_bytes(b"stem")
            midi_dir = root / "midi"
            fake_mid = midi_dir / "loop_oud_stem.mid"

            with patch(
                "batch_deephouse.dora_midi_pipeline.transcribe_audio_to_midi",
                return_value=fake_mid,
            ) as mock_midi, patch(
                "batch_deephouse.dora_midi_pipeline.extract_lead_to_file"
            ) as mock_extract:
                result = run_extract_midi(
                    mix_path=mix,
                    leads=["oud"],
                    stem_dir=stem_dir,
                    midi_dir=midi_dir,
                    api_base="http://127.0.0.1:8001",
                    api_key="",
                    checkpoints_dir=root,
                    extract_steps=8,
                    seed=1,
                    skip_extract=True,
                )
            mock_extract.assert_not_called()
            mock_midi.assert_called_once()
            self.assertEqual(result, [fake_mid])

    def test_extract_path_requires_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mix = root / "loop.mp3"
            mix.write_bytes(b"mix")
            with self.assertRaises(FileNotFoundError):
                run_extract_midi(
                    mix_path=mix,
                    leads=["oud"],
                    stem_dir=root / "stems",
                    midi_dir=root / "midi",
                    api_base="http://127.0.0.1:8001",
                    api_key="",
                    checkpoints_dir=root,
                    extract_steps=8,
                    seed=1,
                    skip_extract=False,
                )


if __name__ == "__main__":
    unittest.main()
