"""Paths and layer names for the HAYA After Effects template."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from batch_deephouse.paths import BATCH_ROOT

TEMPLATE_ROOT = BATCH_ROOT / "ae_template"
TEMPLATE_AEP = TEMPLATE_ROOT / "Haya songs.aep"
TEMPLATE_ASSETS = TEMPLATE_ROOT / "assets"

EDIT_COMP_NAME = "EDIT HERE"
EDIT_COMP_FALLBACKS = ("EDIT HERE", "Happy Birthday")
RENDER_COMP_NAME = "MAIN 2min+"
# Template ships with English placeholder; JSX overwrites text with Arabic.
TITLE_TEXT_LAYER = "Yalil"
BACKGROUND_FOOTAGE_HINT = "bd4a5f15-a571-44f2-a9e0-349a48312fa3.png"

AE_WORK_ROOT = BATCH_ROOT / "ae_work"
AE_JOBS_DIR = AE_WORK_ROOT / "jobs"
AE_PROJECTS_DIR = AE_WORK_ROOT / "projects"
AE_BG_PREPARED_DIR = AE_WORK_ROOT / "bg_prepared"
AE_SCRIPTS_DIR = BATCH_ROOT / "ae_scripts"

MAC_AE_APP_CANDIDATES = (
    "/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app",
    "/Applications/Adobe After Effects 2024/Adobe After Effects 2024.app",
)
MAC_AERENDER_CANDIDATES = (
    "/Applications/Adobe After Effects 2025/aerender",
    "/Applications/Adobe After Effects 2024/aerender",
)
WIN_AERENDER_CANDIDATES = (
    r"C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\aerender.exe",
    r"C:\Program Files\Adobe\Adobe After Effects 2024\Support Files\aerender.exe",
)
WIN_AFTERFX_COM_CANDIDATES = (
    r"C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\AfterFX.com",
    r"C:\Program Files\Adobe\Adobe After Effects 2024\Support Files\AfterFX.com",
)


def resolve_ae_app_bundle() -> Path:
    """Return the After Effects .app bundle path for Mac open --args."""
    override = os.environ.get("AE_APP_PATH", "").strip()
    if override and Path(override).is_dir():
        return Path(override)
    for candidate in MAC_AE_APP_CANDIDATES:
        path = Path(candidate)
        if path.is_dir():
            return path
    raise FileNotFoundError(
        "After Effects app not found. Install AE 2024/2025 or set AE_APP_PATH."
    )


def resolve_aerender() -> Path:
    """Return aerender for headless comp export."""
    override = os.environ.get("AERENDER_PATH", "").strip()
    if override and Path(override).is_file():
        return Path(override)
    candidates = (
        WIN_AERENDER_CANDIDATES if sys.platform == "win32" else MAC_AERENDER_CANDIDATES
    )
    for candidate in candidates:
        path = Path(candidate)
        if path.is_file():
            return path
    found = shutil.which("aerender")
    if found:
        return Path(found)
    raise FileNotFoundError(
        "aerender not found. Install After Effects or set AERENDER_PATH."
    )


def resolve_afterfx_com() -> Path:
    """Return AfterFX.com on Windows for JSX scripting."""
    for candidate in WIN_AFTERFX_COM_CANDIDATES:
        path = Path(candidate)
        if path.is_file():
            return path
    override = os.environ.get("AFTERFX_COM_PATH", "").strip()
    if override and Path(override).is_file():
        return Path(override)
    raise FileNotFoundError(
        "AfterFX.com not found. Install After Effects or set AFTERFX_COM_PATH."
    )
