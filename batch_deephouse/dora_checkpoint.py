"""Resolve Side-Step DoRA checkpoint directories for inference testing."""

from __future__ import annotations

from pathlib import Path

# Default Side-Step train output for the Arabic house DoRA run
DEFAULT_DORA_ROOT = (
    Path(__file__).resolve().parents[1] / "output" / "arabic_deep_house_dora"
)


def resolve_adapter_dir(dora_root: Path, epoch: int | str) -> Path:
    """Map an epoch token to a Side-Step adapter directory.

    Side-Step writes ``checkpoints/epoch_{N}/`` (not ``checkpoint-N``).
    Special tokens: ``best``, ``final``, or an absolute/relative path.

    Args:
        dora_root: Training output root (contains ``checkpoints/``).
        epoch: Epoch number, special name, or explicit path.

    Returns:
        Absolute path to the adapter directory.

    Raises:
        FileNotFoundError: When the resolved directory does not exist.
    """
    token = str(epoch).strip().lower()
    root = dora_root.expanduser().resolve()

    if token in {"best", "final"}:
        path = root / token
    elif token.isdigit():
        path = root / "checkpoints" / f"epoch_{int(token)}"
    else:
        path = Path(epoch).expanduser()
        if not path.is_absolute():
            path = (root / path).resolve()

    if not path.is_dir():
        raise FileNotFoundError(
            f"Adapter not found: {path}\n"
            f"Wait for Side-Step to save (every 50 epochs) under "
            f"{root / 'checkpoints'}"
        )
    return path.resolve()


def list_epoch_checkpoints(dora_root: Path) -> list[int]:
    """Return sorted epoch numbers that have been checkpointed."""
    ckpt_root = dora_root.expanduser().resolve() / "checkpoints"
    if not ckpt_root.is_dir():
        return []
    epochs: list[int] = []
    for child in ckpt_root.iterdir():
        if child.is_dir() and child.name.startswith("epoch_"):
            suffix = child.name.removeprefix("epoch_")
            if suffix.isdigit():
                epochs.append(int(suffix))
    return sorted(epochs)
