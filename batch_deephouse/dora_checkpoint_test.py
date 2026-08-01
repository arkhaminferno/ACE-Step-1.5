"""Unit tests for Side-Step DoRA checkpoint path resolution."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from batch_deephouse.dora_checkpoint import list_epoch_checkpoints, resolve_adapter_dir


class TestResolveAdapterDir(unittest.TestCase):
    """Cover epoch / best / missing path behavior."""

    def test_resolves_epoch_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "checkpoints" / "epoch_50"
            target.mkdir(parents=True)
            resolved = resolve_adapter_dir(root, 50)
            self.assertEqual(resolved, target.resolve())

    def test_resolves_best_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "best"
            target.mkdir()
            self.assertEqual(resolve_adapter_dir(root, "best"), target.resolve())

    def test_missing_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                resolve_adapter_dir(Path(tmp), 50)

    def test_list_epochs_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for n in (100, 50):
                (root / "checkpoints" / f"epoch_{n}").mkdir(parents=True)
            self.assertEqual(list_epoch_checkpoints(root), [50, 100])


if __name__ == "__main__":
    unittest.main()
