"""Normalize HAYA AE background stills to full-bleed 16:9.

ChatGPT often exports ~1536x1024 (3:2). Render prep auto-picks:
- already ~16:9 → uniform scale (no stretch, no crop)
- other aspects → horizontal stretch to fill (no crop, slight widen)
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

TARGET_W = 1920
TARGET_H = 1080
TARGET_ASPECT = TARGET_W / TARGET_H
# Absolute aspect delta — 3:2 (1.5) stretches; 1672x941 (~1.777) stays uniform.
ASPECT_TOLERANCE = 0.03
_BLACK_LUMA = 12


def _content_bbox(im: Image.Image, *, luma: int = _BLACK_LUMA) -> tuple[int, int, int, int]:
    """Return (left, top, right, bottom) of non-near-black pixels."""
    gray = im.convert("L")
    mask = gray.point(lambda p: 255 if p > luma else 0)
    box = mask.getbbox()
    if box is None:
        return (0, 0, im.width, im.height)
    return box


def is_approx_16x9(width: int, height: int, *, tol: float = ASPECT_TOLERANCE) -> bool:
    """True when width/height is within *tol* of 16:9."""
    if height < 1:
        return False
    return abs((width / height) - TARGET_ASPECT) <= tol


def stretch_to_16x9(
    im: Image.Image,
    *,
    out_w: int = TARGET_W,
    out_h: int = TARGET_H,
    trim_black_bars: bool = True,
) -> Image.Image:
    """Stretch image to exact 16:9 — no crop, may distort horizontally."""
    src = im.convert("RGB")
    if trim_black_bars:
        left, top, right, bottom = _content_bbox(src)
        if (right - left) < src.width * 0.98 or (bottom - top) < src.height * 0.98:
            src = src.crop((left, top, right, bottom))
    return src.resize((out_w, out_h), Image.Resampling.LANCZOS)


def uniform_to_16x9(
    im: Image.Image,
    *,
    out_w: int = TARGET_W,
    out_h: int = TARGET_H,
) -> Image.Image:
    """Uniform resize to out size — for sources that are already ~16:9."""
    return im.convert("RGB").resize((out_w, out_h), Image.Resampling.LANCZOS)


def prepare_still_for_render(
    src: Path,
    dst: Path,
    *,
    out_w: int = TARGET_W,
    out_h: int = TARGET_H,
) -> str:
    """Write a fullscreen still; stretch only when not already ~16:9.

    Args:
        src: Source PNG (prefer ChatGPT original when available).
        dst: Output path used by AE (typically ae_work/bg_prepared/).
        out_w: Comp width.
        out_h: Comp height.

    Returns:
        ``uniform`` if already 16:9, else ``stretch``.
    """
    src = Path(src)
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        w, h = im.size
        if is_approx_16x9(w, h):
            out = uniform_to_16x9(im, out_w=out_w, out_h=out_h)
            mode = "uniform"
        else:
            out = stretch_to_16x9(im, out_w=out_w, out_h=out_h)
            mode = "stretch"
    out.save(dst, format="PNG", optimize=True)
    return mode


def resolve_bg_source(slug: str, mapped_filename: str, assets_dir: Path) -> Path:
    """Use the mapped asset first (user-replaced 16:9 stills).

    ``_original_chatgpt/`` is only a fallback backup — never override a file the
    user dropped into ``ae_template/assets/``.
    """
    mapped = assets_dir / mapped_filename
    if mapped.is_file():
        return mapped
    original = assets_dir / "_original_chatgpt" / f"{slug}.png"
    if original.is_file():
        return original
    raise FileNotFoundError(
        f"Missing background still: {mapped} (also no _original_chatgpt/{slug}.png)"
    )


def normalize_still(
    path: Path,
    *,
    backup_dir: Path | None = None,
    mode: str = "auto",
) -> Path:
    """Overwrite a still with a full-bleed 16:9 1920x1080 PNG.

    Args:
        path: PNG to normalize in place.
        backup_dir: Optional folder for a copy of the original.
        mode: ``auto`` (16:9→uniform else stretch), ``stretch``, or ``cover``.

    Returns:
        The same path after overwrite.
    """
    path = Path(path)
    if backup_dir is not None:
        backup_dir.mkdir(parents=True, exist_ok=True)
        dest = backup_dir / path.name
        if not dest.exists():
            dest.write_bytes(path.read_bytes())

    with Image.open(path) as im:
        if mode == "auto":
            if is_approx_16x9(im.width, im.height):
                out = uniform_to_16x9(im)
            else:
                out = stretch_to_16x9(im)
        elif mode == "stretch":
            out = stretch_to_16x9(im)
        elif mode == "cover":
            src = im.convert("RGB")
            left, top, right, bottom = _content_bbox(src)
            if (right - left) < src.width * 0.98 or (bottom - top) < src.height * 0.98:
                src = src.crop((left, top, right, bottom))
            w, h = src.size
            if w / h > TARGET_ASPECT:
                new_w = int(round(h * TARGET_ASPECT))
                x0 = (w - new_w) // 2
                src = src.crop((x0, 0, x0 + new_w, h))
            elif w / h < TARGET_ASPECT:
                new_h = int(round(w / TARGET_ASPECT))
                y0 = (h - new_h) // 2
                src = src.crop((0, y0, w, y0 + new_h))
            out = src.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
        else:
            raise ValueError(f"Unknown normalize mode: {mode}")

    out.save(path, format="PNG", optimize=True)
    return path
