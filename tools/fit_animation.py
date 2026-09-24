#!/usr/bin/env python3
"""Turn a SpriteCook animation strip into a game-ready strip that matches the approved bases.

Two steps, both needed so every animation of every character lines up in Godot:

    1. shrink the strip (majority filter, see prepare_sprite.py) so the character's tallest
       frame is exactly --char-height pixels - the height of the approved base sprites (48)
    2. re-lay each frame into a fixed --frame x --frame cell (56): the character's union
       bounding box across all frames is centred horizontally and its bottom - the ground
       shadow - sits on the cell's bottom row. One anchor for every animation, so switching
       direction never makes the character jump.

SpriteCook returns frames of varying size (86, 96, 154px...) depending on the source pose, so
the shrink factor is found per strip rather than fixed.

Usage:
    python3 tools/fit_animation.py raw/walk_down.png walk_down.png
    python3 tools/fit_animation.py raw/walk_right.png walk_left.png --mirror   # free left-facing

Requires Pillow.
"""
import argparse
import pathlib
import sys
import tempfile

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is required: pip install Pillow")

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from prepare_sprite import prepare  # noqa: E402


def frames_of(img: Image.Image, n: int) -> list[Image.Image]:
    fw = img.width // n
    return [img.crop((i * fw, 0, (i + 1) * fw, img.height)) for i in range(n)]


def char_height(img: Image.Image, n: int) -> int:
    return max(b[3] - b[1] for b in (f.getbbox() for f in frames_of(img, n)) if b)


def fit(src: pathlib.Path, out: pathlib.Path, frames: int, target: int, cell: int, mirror: bool) -> None:
    raw = Image.open(src).convert("RGBA")
    guess = round(raw.height * target / char_height(raw, frames))
    with tempfile.TemporaryDirectory() as tmp:
        shrunk_path = pathlib.Path(tmp) / "shrunk.png"
        # Rounding can land a pixel either side of the target; try the neighbours.
        for sheet_h in sorted(range(guess - 2, guess + 3), key=lambda h: abs(h - guess)):
            prepare(src, sheet_h, 256, frames, shrunk_path, filter_name="majority")
            shrunk = Image.open(shrunk_path).convert("RGBA")
            if char_height(shrunk, frames) == target:
                break
        else:
            sys.exit(f"{src}: could not hit a {target}px character height")

    parts = frames_of(shrunk, frames)
    boxes = [f.getbbox() for f in parts]
    x0, y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    x1, y1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    w, h = x1 - x0, y1 - y0
    if w > cell or h > cell:
        sys.exit(f"{src}: character {w}x{h} does not fit a {cell}px cell")

    sheet = Image.new("RGBA", (cell * frames, cell), (0, 0, 0, 0))
    for i, f in enumerate(parts):
        c = f.crop((x0, y0, x1, y1))
        if mirror:
            c = ImageOps.mirror(c)
        sheet.paste(c, (i * cell + (cell - w) // 2, cell - h))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(f"{src.name}: {raw.width // frames}px frames -> {frames} x {cell}px, "
          f"character {w}x{h}{', mirrored' if mirror else ''} -> {out}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=pathlib.Path)
    ap.add_argument("out", type=pathlib.Path)
    ap.add_argument("--frames", type=int, default=8)
    ap.add_argument("--char-height", type=int, default=48, help="character height in px (default 48)")
    ap.add_argument("--frame", type=int, default=56, help="output cell size in px (default 56)")
    ap.add_argument("--mirror", action="store_true", help="flip each frame, e.g. walk_right -> walk_left")
    a = ap.parse_args()
    fit(a.source, a.out, a.frames, a.char_height, a.frame, a.mirror)
    return 0


if __name__ == "__main__":
    sys.exit(main())
