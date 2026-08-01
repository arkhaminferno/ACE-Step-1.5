"""Headless After Effects launch helpers for HAYA (macOS and Windows)."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from batch_deephouse.ae_config import resolve_ae_app_bundle, resolve_afterfx_com

AE_UI_MODE = os.environ.get("AE_UI_MODE", "applescript").strip().lower()


def is_ae_running() -> bool:
    """Return True when the main After Effects app process is still alive."""
    result = subprocess.run(
        ["pgrep", "-x", "After Effects"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def quit_ae_mac(*, wait_sec: int = 30) -> None:
    """Quit After Effects and wait until the process exits."""
    if not is_ae_running():
        return
    # Avoid the "Save changes?" modal that blocks automation.
    subprocess.run(
        [
            "osascript",
            "-e",
            'tell application "Adobe After Effects 2025" to quit saving no',
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    deadline = time.time() + wait_sec
    while time.time() < deadline:
        if not is_ae_running():
            time.sleep(2)
            return
        time.sleep(1)
    subprocess.run(
        ["pkill", "-9", "-f", "Adobe After Effects 20"],
        capture_output=True,
        text=True,
        check=False,
    )
    time.sleep(2)


def quit_ae(*, wait_sec: int = 30) -> None:
    """Quit After Effects and wait until the process exits."""
    if sys.platform == "win32":
        subprocess.run(
            ["taskkill", "/IM", "AfterFX.exe", "/F"],
            capture_output=True,
            text=True,
            check=False,
        )
        time.sleep(min(wait_sec, 5))
        return
    quit_ae_mac(wait_sec=wait_sec)


def launch_jsx(script_path: Path) -> None:
    """Launch JSX on the current platform and block until the script finishes."""
    if sys.platform == "win32":
        quit_ae()
        time.sleep(2)
        afterfx = resolve_afterfx_com()
        result = subprocess.run(
            [str(afterfx), "-r", str(script_path.resolve())],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "AfterFX.com failed").strip()
            raise RuntimeError(detail)
        return
    launch_jsx_mac(script_path)


def launch_jsx_mac(script_path: Path) -> None:
    """Launch JSX on macOS via AppleScript DoScriptFile (most reliable on AE 2025)."""
    quit_ae_mac()
    time.sleep(2)
    script = str(script_path.resolve())
    mode = AE_UI_MODE

    if mode == "gui":
        app_bundle = resolve_ae_app_bundle()
        subprocess.Popen(
            ["open", "-g", "-a", str(app_bundle), "--args", "-r", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return

    app_name = resolve_ae_app_bundle().stem
    escaped = script.replace("\\", "\\\\").replace('"', '\\"')
    applescript = (
        f"with timeout of 900 seconds\n"
        f'tell application "{app_name}"\n'
        f"activate\n"
        f'DoScriptFile "{escaped}" with override\n'
        f"end tell\n"
        f"end timeout"
    )
    for attempt in range(1, 4):
        print(f"Launching AE via AppleScript ({app_name})... attempt {attempt}/3")
        result = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return
        detail = (result.stderr or result.stdout or "AppleScript failed").strip()
        if attempt < 3 and (
            "timed out" in detail.lower()
            or "-1712" in detail
            or "second script" in detail.lower()
        ):
            print(f"AppleScript busy, quitting AE and retrying: {detail}")
            quit_ae_mac()
            time.sleep(5)
            continue
        raise RuntimeError(detail)
