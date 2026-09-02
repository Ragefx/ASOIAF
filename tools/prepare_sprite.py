#!/usr/bin/env python3
"""Turn a SpriteCook illustration into an actual game sprite.

SpriteCook returns large, many-coloured images even in pixel-art mode (the Torren
base came back 166x166 with 3029 colours). The project's spec is 16x24 frames on a
tight palette, so every downloaded asset goes through this before import:

    1. trim transparent margins so the character fills the frame
    2. nearest-neighbour downscale to the target height, preserving aspect
    3. quantise to a fixed palette size, no dithering
    4. hard-threshold alpha, since a pixel sprite has no partial transparency

Usage:
    python3 tools/prepare_sprite.py assets/sprites/torren/torren_base.png \
        --height 24 --colors 24

    # a horizontal spritesheet of N frames keeps its frames aligned:
    python3 tools/prepare_sprite.py walk_down.png --height 24 --frames 8

Requires Pillow (pip install Pillow). UNTESTED against a real SpriteCook file -
no asset could be downloaded in the session that wrote it. Check the first output
by eye before running it over a whole directory.
"""
import argparse
import pathlib
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required: pip install Pillow")

ALPHA_CUTOFF = 128


def prepare(path: pathlib.Path, height: int, colors: int, frames: int, out: pathlib.Path) -> None:
    img = Image.open(path).convert("RGBA")

    if frames > 1:
        # Trim and scale the sheet as a whole; trimming frames independently would
        # destroy the alignment between them and make the animation jitter.
        frame_w = img.width // frames
        if img.width % frames:
            print(f"warning: {img.width}px does not divide into {frames} frames", file=sys.stderr)
        scale = height / img.height
        target = (max(1, round(frame_w * scale)) * frames, height)
    else:
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        target = (max(1, round(img.width * height / img.height)), height)

    img = img.resize(target, Image.NEAREST)

    # Quantise colour and alpha separately: quantising RGBA directly spends palette
    # entries on semi-transparent edge pixels that are about to be thrown away.
    alpha = img.getchannel("A").point(lambda a: 255 if a >= ALPHA_CUTOFF else 0)
    rgb = img.convert("RGB").quantize(colors=colors, dither=Image.Dither.NONE).convert("RGB")
    rgb.putalpha(alpha)

    out.parent.mkdir(parents=True, exist_ok=True)
    rgb.save(out)
    print(f"{path.name}: {Image.open(path).size} -> {rgb.size}, {colors} colours -> {out}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=pathlib.Path)
    ap.add_argument("--height", type=int, default=24, help="target frame height (default 24)")
    ap.add_argument("--colors", type=int, default=24, help="palette size (default 24)")
    ap.add_argument("--frames", type=int, default=1, help="frames in a horizontal sheet")
    ap.add_argument("--out", type=pathlib.Path, help="output path (default: <source>_prepared.png)")
    args = ap.parse_args()

    out = args.out or args.source.with_name(args.source.stem + "_prepared.png")
    prepare(args.source, args.height, args.colors, args.frames, out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
