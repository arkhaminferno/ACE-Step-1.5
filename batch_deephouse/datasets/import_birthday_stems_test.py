"""Tests for import_birthday_stems Signature Sounds → birthday slots."""

from __future__ import annotations

import json
import tempfile
import unittest
import wave
from pathlib import Path

from batch_deephouse.datasets.import_birthday_stems import (
    _classify,
    import_birthday_stems,
)


def _write_silent_wav(path: Path, frames: int = 8000) -> None:
    """Write a tiny mono WAV for import tests."""
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * frames)


class ImportBirthdayStemsTests(unittest.TestCase):
    """Cover classification and copy+sidecar success path."""

    def test_classify_kick_and_clap(self) -> None:
        self.assertEqual(_classify("Punchy_Kick_01.wav"), "kick")
        self.assertEqual(_classify("Burial_Clap_A.wav"), "clap")
        self.assertEqual(_classify("Closed_HiHat.wav"), "hat")
        self.assertIsNone(_classify("random_noise.wav"))

    def test_imports_with_sidecars(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "signature_sounds" / "Kick Drums"
            src.mkdir(parents=True)
            _write_silent_wav(src / "House_Kick_A.wav", frames=16000)
            _write_silent_wav(src / "House_Kick_B.wav", frames=8000)
            clap_dir = root / "signature_sounds" / "Burial Styled Claps"
            clap_dir.mkdir(parents=True)
            _write_silent_wav(clap_dir / "Burial_Clap_01.wav", frames=4000)

            out = root / "birthday_edm_dataset"
            # Minimal template so seed does not fail hard
            tpl = root / "tpl"
            (tpl / "examples").mkdir(parents=True)
            (tpl / "README.md").write_text("x\n", encoding="utf-8")

            # Bypass default template by seeding manually then importing
            out.mkdir(parents=True)
            total, counts = import_birthday_stems(
                root / "signature_sounds",
                out,
                limit=10,
                template_dir=tpl,
            )

            self.assertGreaterEqual(total, 3)
            self.assertGreaterEqual(counts["kick"], 2)
            self.assertGreaterEqual(counts["clap"], 1)
            kick = out / "kick_four_on_floor_128bpm.wav"
            self.assertTrue(kick.is_file())
            meta = json.loads((out / "kick_four_on_floor_128bpm.json").read_text(encoding="utf-8"))
            self.assertIn("kick", meta["caption"].lower())
            self.assertTrue((out / "kick_four_on_floor_128bpm.lyrics.txt").is_file())


if __name__ == "__main__":
    unittest.main()
