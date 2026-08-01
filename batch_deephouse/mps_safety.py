"""MPS-safe defaults for HAYA generation / LEGO payloads."""

from __future__ import annotations

from typing import Any


# Fractional cover on Apple MPS can hit conditioner batch shape mismatch.
SAFE_COVER_STRENGTH_MPS = 1.0


def clamp_cover_strength_for_mps(
    strength: float,
    *,
    force_full: bool = True,
) -> float:
    """Return cover strength safe for MPS backends.

    Args:
        strength: Requested audio_cover_strength in [0, 1].
        force_full: When True (default), always use 1.0 until upstream
            fractional-cover MPS concat is fixed.

    Returns:
        Safe cover strength value.
    """
    value = float(strength)
    if force_full and value < 1.0:
        return SAFE_COVER_STRENGTH_MPS
    return max(0.0, min(1.0, value))


def apply_lego_payload_guards(payload: dict[str, Any]) -> dict[str, Any]:
    """Force LEGO-safe payload flags (thinking off so stems stay locked).

    Args:
        payload: Generation request body.

    Returns:
        Mutated payload (same dict) with thinking disabled.
    """
    payload["thinking"] = False
    return payload
