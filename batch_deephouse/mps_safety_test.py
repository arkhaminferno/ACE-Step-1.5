"""Tests for MPS cover/LEGO safety helpers."""

from __future__ import annotations

import unittest

from batch_deephouse.mps_safety import (
    apply_lego_payload_guards,
    clamp_cover_strength_for_mps,
)


class TestMpsSafety(unittest.TestCase):
    """Guardrails for Apple Silicon generation quirks."""

    def test_fractional_cover_clamped_to_full(self) -> None:
        """Fractional cover becomes 1.0 to avoid MPS batch mismatch."""
        self.assertEqual(clamp_cover_strength_for_mps(0.5), 1.0)
        self.assertEqual(clamp_cover_strength_for_mps(0.82), 1.0)

    def test_full_cover_unchanged(self) -> None:
        """Strength 1.0 stays 1.0."""
        self.assertEqual(clamp_cover_strength_for_mps(1.0), 1.0)

    def test_lego_disables_thinking(self) -> None:
        """LEGO payloads must not let LM codes override stem latents."""
        payload = {"thinking": True, "task_type": "text2music"}
        apply_lego_payload_guards(payload)
        self.assertFalse(payload["thinking"])


if __name__ == "__main__":
    unittest.main()
