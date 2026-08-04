"""DSP: nudge dry-oud pluck onsets onto a fixed BPM grid.

Keeps kick/sub/pads/vocals from the original mix. Builds a Wiener mid-band
oud estimate, time-warps it onto a 16th-note grid, then puts it back over
the residual bed.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

OUD_LO_HZ = 350.0
OUD_HI_HZ = 3500.0
MAX_SHIFT_SEC = 0.090
MIN_CREST = 4.5
N_FFT = 2048
HOP = 512


def nearest_grid_time(t: float, grid_sec: float, phase: float = 0.0) -> float:
    """Snap time ``t`` to the nearest ``phase + n * grid_sec``."""
    if grid_sec <= 0:
        raise ValueError("grid_sec must be positive")
    n = round((t - phase) / grid_sec)
    return phase + n * grid_sec


def build_sixteenth_phase(beats: np.ndarray, bpm: float) -> float:
    """Pick grid phase from detected beat times (or 0 if none)."""
    beat_sec = 60.0 / bpm
    if beats.size == 0:
        return 0.0
    residuals = np.mod(beats, beat_sec)
    folded = residuals - beat_sec * np.round(residuals / beat_sec)
    return float(np.median(folded) % beat_sec)


def _onset_crest(oud: np.ndarray, sr: int, t: float) -> float:
    """Crest factor just after onset — high means plucked attack."""
    i0 = int(max(0, (t - 0.005) * sr))
    i1 = int(min(len(oud), (t + 0.060) * sr))
    seg = oud[i0:i1]
    if seg.size < 8:
        return 0.0
    mean = float(np.mean(np.abs(seg)) + 1e-8)
    return float(np.max(np.abs(seg)) / mean)


def estimate_oud_layers(y: np.ndarray, sr: int) -> tuple[np.ndarray, np.ndarray]:
    """Return (oud_estimate, residual_bed) via mid-band Wiener mask."""
    harmonic, _ = librosa.effects.hpss(y, margin=2.0)
    y_stft = librosa.stft(harmonic, n_fft=N_FFT, hop_length=HOP)
    mix_stft = librosa.stft(y, n_fft=N_FFT, hop_length=HOP)
    freqs = librosa.fft_frequencies(sr=sr, n_fft=N_FFT)
    mid = ((freqs >= OUD_LO_HZ) & (freqs <= OUD_HI_HZ))[:, None]
    mag_h, mag_m = np.abs(y_stft), np.abs(mix_stft)
    w = (mag_h**2) / (mag_h**2 + mag_m**2 * 0.15 + 1e-8)
    w = np.where(mid, w, 0.0).astype(np.float32)
    oud = librosa.istft(mix_stft * w, hop_length=HOP, length=len(y))
    bed = librosa.istft(mix_stft * (1.0 - w), hop_length=HOP, length=len(y))
    return oud.astype(np.float32), bed.astype(np.float32)


def _warp_anchors(
    oud: np.ndarray,
    sr: int,
    *,
    bpm: float,
    phase: float,
    start_sec: float,
    end_sec: float,
    max_shift_sec: float,
) -> tuple[list[float], list[float], int]:
    """Build monotonic src→dst time anchors from pluck onsets."""
    grid = (60.0 / bpm) / 4.0
    onsets = librosa.onset.onset_detect(
        y=oud, sr=sr, units="time", backtrack=True, delta=0.07
    )
    src_t = [start_sec]
    dst_t = [start_sec]
    moves = 0
    for t in onsets:
        if t < start_sec or t > end_sec:
            continue
        if _onset_crest(oud, sr, float(t)) < MIN_CREST:
            continue
        target = nearest_grid_time(float(t), grid, phase)
        delta = target - float(t)
        if abs(delta) < 0.004 or abs(delta) > max_shift_sec:
            continue
        src_t.append(float(t))
        dst_t.append(float(target))
        moves += 1
    src_t.append(end_sec)
    dst_t.append(end_sec)
    pairs = sorted(zip(src_t, dst_t))
    src_t = [p[0] for p in pairs]
    dst_t = [p[1] for p in pairs]
    for i in range(1, len(dst_t)):
        if dst_t[i] <= dst_t[i - 1]:
            dst_t[i] = dst_t[i - 1] + 1e-3
    return src_t, dst_t, moves


def warp_oud_to_grid(
    oud: np.ndarray,
    sr: int,
    *,
    bpm: float,
    phase: float,
    start_sec: float,
    end_sec: float,
    max_shift_sec: float = MAX_SHIFT_SEC,
) -> tuple[np.ndarray, int]:
    """Piecewise-linear time-warp oud onto the 16th grid in ``[start, end]``."""
    src_t, dst_t, moves = _warp_anchors(
        oud,
        sr,
        bpm=bpm,
        phase=phase,
        start_sec=start_sec,
        end_sec=end_sec,
        max_shift_sec=max_shift_sec,
    )
    n0 = int(start_sec * sr)
    n1 = int(min(len(oud), end_sec * sr))
    out_times = np.arange(n1 - n0) / sr + start_sec
    # Inverse map: output grid time → source time to read.
    inv_src = np.interp(out_times, dst_t, src_t)
    idx = np.clip(inv_src * sr, 0, len(oud) - 2)
    i0 = np.floor(idx).astype(np.int64)
    frac = idx - i0
    warped = oud[i0] * (1.0 - frac) + oud[i0 + 1] * frac
    out = oud.copy()
    out[n0:n1] = warped.astype(np.float32)
    return out, moves


def align_mix_file(
    src: Path,
    dst: Path,
    *,
    bpm: float = 108.0,
    start_sec: float = 90.0,
    end_sec: float | None = None,
) -> dict[str, object]:
    """Write an aligned mix; never overwrites ``src``."""
    y, sr = librosa.load(str(src), sr=44100, mono=True)
    if end_sec is None:
        end_sec = len(y) / sr

    _tempo, beats = librosa.beat.beat_track(y=y, sr=sr, start_bpm=bpm, units="time")
    beats = np.atleast_1d(np.asarray(beats, dtype=np.float64))
    phase = build_sixteenth_phase(beats, bpm)

    oud, bed = estimate_oud_layers(y, sr)
    warped, moves = warp_oud_to_grid(
        oud, sr, bpm=bpm, phase=phase, start_sec=start_sec, end_sec=end_sec
    )
    out = bed + warped
    peak = float(np.max(np.abs(out)) + 1e-8)
    if peak > 0.99:
        out = out * (0.99 / peak)
    dst.parent.mkdir(parents=True, exist_ok=True)
    wav = dst.with_suffix(".wav")
    sf.write(str(wav), np.stack([out, out], axis=-1).astype(np.float32), sr)
    cmd = ["ffmpeg", "-y", "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "192k", str(dst)]
    subprocess.run(cmd, check=True, capture_output=True)
    wav.unlink(missing_ok=True)
    return {
        "src": str(src.resolve()),
        "dst": str(dst.resolve()),
        "bpm": bpm,
        "phase_sec": phase,
        "window_sec": [start_sec, end_sec],
        "moves": moves,
        "method": "wiener-mid + piecewise warp",
    }
