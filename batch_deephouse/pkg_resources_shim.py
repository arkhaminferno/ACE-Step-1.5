"""Minimal pkg_resources shim for resampy under setuptools>=82.

setuptools 82 removed ``pkg_resources``; Basic Pitch → resampy still imports
``resource_filename``. This shim is injected into ``sys.modules`` before that import.
"""

from __future__ import annotations

import importlib.resources
from pathlib import Path


def resource_filename(package_or_requirement: str, resource_name: str) -> str:
    """Return filesystem path for a package data file (resampy compatibility).

    Args:
        package_or_requirement: Package name (e.g. ``resampy``).
        resource_name: Relative resource path inside the package.

    Returns:
        Absolute path string to the resource file.
    """
    root = importlib.resources.files(package_or_requirement)
    return str(Path(str(root)) / resource_name)
