"""Import Signature Sounds WAVs into birthday_edm_dataset (stdlib-only).

Usage (repo root):
  PYTHONPATH=. python -m batch_deephouse.datasets.import_birthday_stems \\
    --stem-packs C:/Users/Inferno/Downloads/stem_packs/signature_sounds --limit 40
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import wave
from pathlib import Path

AUDIO_EXTS = {".wav", ".mp3", ".flac", ".aiff", ".aif"}
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TEMPLATE = (
    REPO_ROOT / "batch_deephouse" / "datasets" / "templates" / "birthday_edm_dataset"
)
DEFAULT_OUT = REPO_ROOT / "batch_birthday" / "datasets" / "birthday_edm_dataset"

KIND_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("kick", re.compile(r"kick|bd_|bass.?drum|paper.?bag.?kick", re.I)),
    ("clap", re.compile(r"clap|hand.?clap|burial", re.I)),
    ("hat", re.compile(r"hat|hihat|hi.?hat|hh_", re.I)),
    ("snare", re.compile(r"snare|sd_", re.I)),
    ("perc", re.compile(r"perc|foley|tap|coin|brush|shaker|rim", re.I)),
]

CAPTIONS = {
    "kick": "Four-on-the-floor EDM kick, punchy festival kick, dry low end, no melody",
    "clap": "Party hand clap / crowd clap, crisp EDM clap on 2 and 4, dry, no melody",
    "hat": "Closed or open hi-hat one-shot or loop, tight EDM hat, dry, no melody",
    "snare": "Snappy EDM snare one-shot, dry, no melody",
    "perc": "Light percussion / foley hit for party EDM bed, dry, no melody",
}


def _wav_duration_s(path: Path) -> float:
    """Return WAV duration in seconds; 0.0 if unreadable."""
    if path.suffix.lower() not in {".wav", ".aiff", ".aif"}:
        return 0.0
    try:
        with wave.open(str(path), "rb") as wf:
            return wf.getnframes() / float(wf.getframerate() or 1)
    except Exception:  # noqa: BLE001 — skip corrupt / non-PCM
        return 0.0


def _classify(name: str) -> str | None:
    """Return instrument kind from filename, or None."""
    for kind, pattern in KIND_PATTERNS:
        if pattern.search(name):
            return kind
    return None


def _seed_templates(out_dir: Path, template_dir: Path) -> None:
    """Copy birthday templates when ``examples/`` is missing."""
    out_dir.mkdir(parents=True, exist_ok=True)
    if (out_dir / "examples").is_dir() or not template_dir.is_dir():
        return
    shutil.copytree(template_dir, out_dir, dirs_exist_ok=True)
    print(f"Seeded templates from {template_dir}")


def _collect_candidates(stem_root: Path) -> dict[str, list[Path]]:
    """Group audio files under *stem_root* by instrument kind."""
    buckets: dict[str, list[Path]] = {k: [] for k in CAPTIONS}
    for path in sorted(stem_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in AUDIO_EXTS:
            continue
        if path.name.startswith("."):
            continue
        kind = _classify(path.name)
        if kind is None:
            continue
        buckets[kind].append(path)
    for files in buckets.values():
        files.sort(key=lambda p: (_wav_duration_s(p), p.stat().st_size), reverse=True)
    return buckets


def _write_sidecar(dest_stem: Path, kind: str, bpm: int) -> None:
    """Write ``.json`` + ``.lyrics.txt`` next to the audio stem."""
    meta = {
        "caption": CAPTIONS[kind],
        "bpm": bpm,
        "keyscale": "C major",
        "timesignature": "4",
        "language": "unknown",
    }
    dest_stem.with_suffix(".json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    dest_stem.with_suffix(".lyrics.txt").write_text(
        f"[Instrumental]\n({kind} only)\n", encoding="utf-8"
    )


def _stem_name(kind: str, idx: int) -> str:
    """Stable slot basename for the first of each kind, else numbered."""
    first = {
        "kick": "kick_four_on_floor_128bpm",
        "clap": "clap_party_128bpm",
        "hat": "hats_closed_128bpm",
    }
    if idx == 1 and kind in first:
        return first[kind]
    return f"{kind}_punchy_{idx:02d}"


def import_birthday_stems(
    stem_packs: Path,
    out_dir: Path,
    *,
    limit: int = 40,
    bpm: int = 128,
    template_dir: Path | None = None,
) -> tuple[int, dict[str, int]]:
    """Copy classified stems into *out_dir* with sidecars.

    Returns:
        ``(total_copied, counts_by_kind)``.
    """
    if not stem_packs.is_dir():
        raise SystemExit(f"Missing stem packs dir: {stem_packs}")

    _seed_templates(out_dir, template_dir or DEFAULT_TEMPLATE)
    buckets = _collect_candidates(stem_packs)
    quotas = {
        "kick": max(12, limit // 2),
        "clap": max(6, limit // 5),
        "hat": max(4, limit // 8),
        "snare": max(2, limit // 10),
        "perc": max(2, limit // 10),
    }
    planned = sum(min(quotas[k], len(buckets[k])) for k in quotas)
    if planned > limit:
        quotas["kick"] = max(8, quotas["kick"] - (planned - limit))

    counts: dict[str, int] = {k: 0 for k in quotas}
    total = 0
    for kind, quota in quotas.items():
        for src in buckets[kind][:quota]:
            counts[kind] += 1
            stem = _stem_name(kind, counts[kind])
            dest = out_dir / f"{stem}{src.suffix.lower()}"
            if dest.suffix == ".aif":
                dest = dest.with_suffix(".aiff")
            shutil.copy2(src, dest)
            _write_sidecar(out_dir / stem, kind, bpm)
            total += 1
            print(f"  {kind:5} → {dest.name}  ← {src.name}")
    return total, counts


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Import Signature Sounds → birthday dataset.")
    parser.add_argument("--stem-packs", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--bpm", type=int, default=128)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    stem = args.stem_packs or (
        Path.home() / "Downloads" / "stem_packs" / "signature_sounds"
    )
    if args.dry_run:
        if not stem.is_dir():
            raise SystemExit(f"Missing: {stem}")
        for kind, files in _collect_candidates(stem).items():
            print(f"{kind}: {len(files)}")
            for f in files[:3]:
                print(f"  e.g. {f.relative_to(stem)}")
        return 0

    total, counts = import_birthday_stems(stem, args.out, limit=args.limit, bpm=args.bpm)
    print(f"Done. copied={total} by_kind={counts}")
    print(f"Dataset: {args.out}")
    print("Next: SIDESTEP_DIR=... ./scripts/train_project_adapter.sh birthday all")
    return 0 if total else 1


if __name__ == "__main__":
    raise SystemExit(main())
