"""Tests for build_dataset_json sidecar → dataset.json export."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from batch_deephouse.datasets.build_dataset_json import build_dataset_json


class BuildDatasetJsonTests(unittest.TestCase):
    """Cover success path and missing-audio failure."""

    def test_builds_json_from_audio_and_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            audio = root / "oud_bayati_108_01.mp3"
            audio.write_bytes(b"\x00" * 128)
            (root / "oud_bayati_108_01.json").write_text(
                json.dumps(
                    {
                        "caption": "Dry oud solo Bayati",
                        "bpm": 108,
                        "keyscale": "D minor",
                        "timesignature": "4",
                        "language": "unknown",
                    }
                ),
                encoding="utf-8",
            )
            (root / "oud_bayati_108_01.lyrics.txt").write_text(
                "[Instrumental]\n",
                encoding="utf-8",
            )
            out = root / "dataset.json"

            out_path, status = build_dataset_json(root, out, name="test_arabic")

            self.assertEqual(out_path, out)
            self.assertIn("Found 1 audio", status)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["metadata"]["name"], "test_arabic")
            self.assertEqual(len(data["samples"]), 1)
            sample = data["samples"][0]
            self.assertEqual(sample["filename"], "oud_bayati_108_01.mp3")
            self.assertEqual(sample["caption"], "Dry oud solo Bayati")
            self.assertEqual(sample["bpm"], 108)
            self.assertEqual(sample["audio_path"], "oud_bayati_108_01.mp3")

    def test_raises_when_no_audio(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "dataset.json"
            with self.assertRaises(SystemExit):
                build_dataset_json(root, out)


if __name__ == "__main__":
    unittest.main()
