"""Unit tests for oud grid-snap helpers."""

from __future__ import annotations

import unittest

import numpy as np

from batch_deephouse.oud_grid_align import (
    build_sixteenth_phase,
    nearest_grid_time,
    warp_oud_to_grid,
)


class TestNearestGridTime(unittest.TestCase):
    """Sixteenth-note snap math."""

    def test_snaps_midway_to_nearest(self) -> None:
        grid = 0.1
        self.assertAlmostEqual(nearest_grid_time(0.14, grid), 0.1)
        self.assertAlmostEqual(nearest_grid_time(0.16, grid), 0.2)

    def test_respects_phase(self) -> None:
        self.assertAlmostEqual(nearest_grid_time(0.25, 0.2, phase=0.05), 0.25)


class TestBuildPhase(unittest.TestCase):
    """Beat-phase estimation."""

    def test_empty_beats_zero_phase(self) -> None:
        self.assertEqual(build_sixteenth_phase(np.array([]), 108.0), 0.0)

    def test_aligned_beats_near_zero(self) -> None:
        beat = 60.0 / 108.0
        beats = np.array([0.0, beat, 2 * beat, 3 * beat])
        phase = build_sixteenth_phase(beats, 108.0)
        self.assertLess(abs(phase), 0.02)


class TestWarpOud(unittest.TestCase):
    """Warp keeps length and returns a move count."""

    def test_returns_same_length(self) -> None:
        sr = 22050
        y = np.zeros(sr * 2, dtype=np.float32)
        # Sharp click slightly off a 16th at 108 BPM.
        t = 0.40
        i = int(t * sr)
        y[i : i + 64] = 1.0
        out, moves = warp_oud_to_grid(
            y, sr, bpm=108.0, phase=0.0, start_sec=0.0, end_sec=2.0
        )
        self.assertEqual(len(out), len(y))
        self.assertIsInstance(moves, int)


if __name__ == "__main__":
    unittest.main()
