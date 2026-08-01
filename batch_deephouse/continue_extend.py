"""Continuously elongate a short HAYA master via ACE-Step repaint (no loop restart).

Uses a sliding context window: take the last N seconds, pad with silence, repaint
the tail so the model *continues* the song, then splice onto the growing master.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from batch_deephouse.acestep_task import generate_to_file
from batch_deephouse.extend_mix import probe_duration_sec

SAMPLE_RATE = 48000
# Tutorial: repaint region 3–90s. Keep generated extension under that.
CONTEXT_SEC = 45.0
OVERLAP_SEC = 10.0
EXTEND_SEC = 78.0  # OVERLAP+EXTEND=88s ≤ 90s repaint cap


CONTINUE_PROMPT = (
    "Oriental deep house continuation, warm sub-bass, four-on-floor kick, "
    "intimate Arabic female vocal, dry oud, cinematic pads, same song energy, "
    "seamless continuation of the previous bars — do NOT restart the intro, "
    "do NOT fade out, do NOT begin the song again. Keep groove flowing."
)

CONTINUE_INSTRUCTION = (
    "Continue this Arabic deep-house track seamlessly from the marked region. "
    "Maintain the same BPM, key, vocal timbre, bass, and motif. "
    "No hard stop, no song restart, no new intro."
)


def _run_ffmpeg(cmd: list[str]) -> None:
    """Run ffmpeg and raise with stderr on failure."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr[-2000:]}")


def extract_audio(src: Path, dst: Path, *, start: float, duration: float) -> Path:
    """Extract a time slice to *dst*."""
    _run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{start:.3f}",
            "-t",
            f"{duration:.3f}",
            "-i",
            str(src),
            "-ar",
            str(SAMPLE_RATE),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(dst),
        ]
    )
    return dst


def pad_with_silence(src: Path, dst: Path, *, pad_sec: float) -> Path:
    """Append *pad_sec* of silence after *src*."""
    _run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-f",
            "lavfi",
            "-t",
            f"{pad_sec:.3f}",
            "-i",
            f"anullsrc=r={SAMPLE_RATE}:cl=stereo",
            "-filter_complex",
            "[0:a][1:a]concat=n=2:v=0:a=1[out]",
            "-map",
            "[out]",
            "-ar",
            str(SAMPLE_RATE),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(dst),
        ]
    )
    return dst


def concat_crossfade(a: Path, b: Path, dst: Path, *, crossfade_sec: float) -> Path:
    """Append *b* onto *a* with a soft acrossfade (no hard restart click)."""
    a_dur = probe_duration_sec(a)
    if a_dur <= crossfade_sec + 1:
        raise ValueError(f"Left clip too short for crossfade: {a_dur:.1f}s")
    _run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(a),
            "-i",
            str(b),
            "-filter_complex",
            f"[0:a][1:a]acrossfade=d={crossfade_sec}:c1=tri:c2=tri[out]",
            "-map",
            "[out]",
            "-ar",
            str(SAMPLE_RATE),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(dst),
        ]
    )
    return dst


def trim_to(src: Path, dst: Path, *, duration: float) -> Path:
    """Hard-trim *src* to *duration* seconds."""
    _run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-t",
            f"{duration:.3f}",
            "-ar",
            str(SAMPLE_RATE),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(dst),
        ]
    )
    return dst


def build_repaint_payload(
    *,
    src_audio_path: Path,
    repaint_start: float,
    repaint_end: float,
    audio_duration: float,
    seed: int,
    bpm: int = 110,
    key: str = "A minor",
) -> dict[str, Any]:
    """Build ACE-Step repaint payload for seamless continuation."""
    return {
        "task_type": "repaint",
        "src_audio_path": str(src_audio_path.resolve()),
        "repainting_start": float(repaint_start),
        "repainting_end": float(repaint_end),
        "audio_duration": float(audio_duration),
        "prompt": CONTINUE_PROMPT,
        "instruction": CONTINUE_INSTRUCTION,
        "lyrics": "",
        "thinking": False,
        "vocal_language": "ar",
        "bpm": bpm,
        "key_scale": key,
        "batch_size": 1,
        "inference_steps": 20,
        "guidance_scale": 14.0,
        "model": "acestep-v15-turbo",
        "use_random_seed": False,
        "seed": seed,
        "audio_format": "mp3",
    }


def continue_once(
    master: Path,
    *,
    out_path: Path,
    api_base: str,
    seed: int,
    step_idx: int,
    context_sec: float = CONTEXT_SEC,
    overlap_sec: float = OVERLAP_SEC,
    extend_sec: float = EXTEND_SEC,
) -> Path:
    """Grow *master* by one seamless continuation step → write *out_path*."""
    master_dur = probe_duration_sec(master)
    ctx_dur = min(context_sec, master_dur)
    ctx_start = max(0.0, master_dur - ctx_dur)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        context = tmp / "context.mp3"
        padded = tmp / "padded.mp3"
        repainted = tmp / "repainted.mp3"
        new_tail = tmp / "new_tail.mp3"
        head = tmp / "head.mp3"

        extract_audio(master, context, start=ctx_start, duration=ctx_dur)
        pad_with_silence(context, padded, pad_sec=extend_sec)
        padded_dur = probe_duration_sec(padded)

        repaint_start = max(0.0, ctx_dur - overlap_sec)
        payload = build_repaint_payload(
            src_audio_path=padded,
            repaint_start=repaint_start,
            repaint_end=padded_dur,
            audio_duration=padded_dur,
            seed=seed + step_idx,
        )
        print(
            f"  continue step={step_idx} master={master_dur:.1f}s "
            f"ctx={ctx_dur:.1f}s repaint={repaint_start:.1f}→{padded_dur:.1f}s"
        )
        generate_to_file(
            payload,
            api_base=api_base,
            api_key="",
            out_path=repainted,
            label=f"continue_{step_idx}",
        )

        # Keep everything before the overlap on the master, then soft-join the
        # newly generated tail (from overlap point in the repaint result).
        head_dur = max(0.5, master_dur - overlap_sec)
        extract_audio(master, head, start=0.0, duration=head_dur)
        extract_audio(
            repainted,
            new_tail,
            start=repaint_start,
            duration=max(1.0, probe_duration_sec(repainted) - repaint_start),
        )
        concat_crossfade(head, new_tail, out_path, crossfade_sec=min(2.0, overlap_sec / 2))
    return out_path


def elongate_to_target(
    seed_mp3: Path,
    dst: Path,
    *,
    api_base: str,
    target_sec: float = 35 * 60,
    seed: int = 42,
    work_dir: Path | None = None,
) -> Path:
    """Elongate *seed_mp3* into a continuous *target_sec* master at *dst*."""
    work = work_dir or dst.parent / "_continue_work"
    work.mkdir(parents=True, exist_ok=True)
    current = work / "master_000.mp3"
    if not current.exists():
        # Copy seed as starting master
        _run_ffmpeg(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(seed_mp3),
                "-ar",
                str(SAMPLE_RATE),
                "-c:a",
                "libmp3lame",
                "-b:a",
                "192k",
                str(current),
            ]
        )

    step = 0
    # Resume from highest existing master_NNN if present
    existing = sorted(work.glob("master_*.mp3"))
    if existing:
        current = existing[-1]
        step = int(current.stem.split("_")[1])

    while probe_duration_sec(current) < target_sec - 1.0:
        step += 1
        nxt = work / f"master_{step:03d}.mp3"
        if nxt.exists() and probe_duration_sec(nxt) > probe_duration_sec(current):
            current = nxt
            continue
        continue_once(
            current,
            out_path=nxt,
            api_base=api_base,
            seed=seed,
            step_idx=step,
        )
        current = nxt
        print(f"  master now {probe_duration_sec(current):.1f}s")

    trim_to(current, dst, duration=target_sec)
    meta = {
        "seed": str(seed_mp3),
        "steps": step,
        "target_sec": target_sec,
        "final": str(dst),
        "method": "sliding-window repaint continuation",
    }
    (work / "continue_meta.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    return dst


__all__ = [
    "CONTEXT_SEC",
    "EXTEND_SEC",
    "OVERLAP_SEC",
    "continue_once",
    "elongate_to_target",
    "extract_audio",
]
