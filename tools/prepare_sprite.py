#!/usr/bin/env python3
"""Turn a SpriteCook illustration into an actual game sprite.

SpriteCook returns large, many-coloured images even in pixel-art mode (the Torren
base came back 166x166 with 3029 colours). The project's spec is 16x24 frames on a
tight palette, so every downloaded asset goes through this before import:

    1. trim transparent margins so the character fills the frame
    2. downscale to the target height, preserving aspect
    3. quantise to a fixed palette size, no dithering
    4. hard-threshold alpha, since a pixel sprite has no partial transparency

Usage:
    python3 tools/prepare_sprite.py assets/sprites/torren/torren_base.png \
        --height 24 --colors 24

    # a horizontal spritesheet of N frames keeps its frames aligned:
    python3 tools/prepare_sprite.py walk_down.png --height 24 --frames 8

    # a missing direction, mirrored from one that exists (no extra generation spend):
    python3 tools/prepare_sprite.py walk_right.png --height 24 --frames 8 --mirror \
        --out walk_left_prepared.png

On the resampling filter, which matters more than it sounds: nearest-neighbour is
the right choice for *enlarging* pixel art, and the wrong one for shrinking it a
long way. Shrinking by 0.27 - which is what an 88px SpriteCook sprite does on its
way to a 24px frame - makes nearest sample roughly one pixel in four, and a thick
dark outline comes out dashed. Measured on Nyra's base: nearest broke her outline
into fragments, BOX (area-average) kept it solid. So the filter is chosen by scale
factor: BOX when shrinking past --nearest-above, nearest otherwise. Override with
--filter when a source really is clean pixel art at an integer multiple.

--filter majority is the third option, and the one the approved 2026-09-24 Torren
(v7, shipped at 65%) was made with. Each output pixel takes the most common opaque
colour in the source area it covers, and a dark outline colour wins whenever it holds
at least half that area. It never invents a blended colour, so edges stay hard like
nearest, but it looks at every source pixel, so outlines don't break up the way they
do with nearest. It is for a *modest* shrink of an already-clean sprite (0.6-0.9);
for a big shrink of a noisy illustration, BOX is still the safer choice.

Requires Pillow (pip install Pillow).
"""
import argparse
import pathlib
import sys
from collections import Counter

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is required: pip install Pillow")

ALPHA_CUTOFF = 128

# Shrinking by more than this keeps whole pixels; below it, nearest starts dropping
# every second or third row and thick outlines come out dashed. 0.75 sits just above
# the ratios that still looked clean by eye.
NEAREST_ABOVE = 0.75

FILTERS = {"nearest": Image.NEAREST, "box": Image.BOX, "lanczos": Image.LANCZOS,
           "majority": "majority"}

# Luminance below which a colour counts as outline for the majority filter.
OUTLINE_LUMA = 45


def _luma(p) -> float:
    return 0.3 * p[0] + 0.59 * p[1] + 0.11 * p[2]


def majority_resize(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Shrink by taking each output pixel's majority source colour; see the docstring."""
    w, h = size
    sx, sy = img.width / w, img.height / h
    src = img.load()
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    dst = out.load()
    for y in range(h):
        y0 = int(y * sy)
        y1 = min(img.height, max(y0 + 1, int((y + 1) * sy)))
        for x in range(w):
            x0 = int(x * sx)
            x1 = min(img.width, max(x0 + 1, int((x + 1) * sx)))
            area = [src[i, j] for j in range(y0, y1) for i in range(x0, x1)]
            opaque = [p for p in area if p[3] >= ALPHA_CUTOFF]
            if not opaque or len(opaque) * 2 < len(area):
                continue
            dark = [p for p in opaque if _luma(p) < OUTLINE_LUMA]
            pool = dark if dark and len(dark) * 2 >= len(opaque) else opaque
            dst[x, y] = Counter(pool).most_common(1)[0][0]
    return out


def pick_filter(scale: float, override: str | None, nearest_above: float):
    """Nearest preserves hard pixel edges but aliases badly on a big downscale."""
    if override:
        return FILTERS[override], override
    if scale >= nearest_above:
        return Image.NEAREST, "nearest"
    return Image.BOX, "box"


def prepare(
    path: pathlib.Path,
    height: int,
    colors: int,
    frames: int,
    out: pathlib.Path,
    filter_name: str | None = None,
    nearest_above: float = NEAREST_ABOVE,
    mirror: bool = False,
) -> None:
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

    scale = target[1] / img.height
    resample, resample_name = pick_filter(scale, filter_name, nearest_above)
    if resample == "majority":
        # Per frame, so a source pixel never bleeds across a frame boundary.
        fw_src, fw_dst = img.width // frames, target[0] // frames
        sheet = Image.new("RGBA", target, (0, 0, 0, 0))
        for i in range(frames):
            frame = img.crop((i * fw_src, 0, (i + 1) * fw_src, img.height))
            sheet.paste(majority_resize(frame, (fw_dst, target[1])), (i * fw_dst, 0))
        img = sheet
    else:
        img = img.resize(target, resample)

    # Quantise colour and alpha separately: quantising RGBA directly spends palette
    # entries on semi-transparent edge pixels that are about to be thrown away.
    # BOX blends alpha at the silhouette edge, so hard-threshold after resampling
    # either way, not just for nearest.
    alpha = img.getchannel("A").point(lambda a: 255 if a >= ALPHA_CUTOFF else 0)
    rgb = img.convert("RGB").quantize(colors=colors, dither=Image.Dither.NONE).convert("RGB")
    rgb.putalpha(alpha)

    if mirror:
        # Flip each frame in place; do NOT reverse the strip, or the gait plays
        # backwards in time while only looking like it faces the other way.
        # A single (frames=1) image just mirrors whole.
        if frames > 1:
            fw = rgb.width // frames
            flipped = Image.new("RGBA", rgb.size, (0, 0, 0, 0))
            for i in range(frames):
                box = (i * fw, 0, (i + 1) * fw, rgb.height)
                flipped.paste(ImageOps.mirror(rgb.crop(box)), (i * fw, 0))
            rgb = flipped
        else:
            rgb = ImageOps.mirror(rgb)

    out.parent.mkdir(parents=True, exist_ok=True)
    rgb.save(out)
    mirror_note = ", mirrored" if mirror else ""
    print(f"{path.name}: {Image.open(path).size} -> {rgb.size}, {colors} colours, "
          f"{resample_name} resample{mirror_note} -> {out}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=pathlib.Path)
    ap.add_argument("--height", type=int, default=24, help="target frame height (default 24)")
    ap.add_argument("--colors", type=int, default=24, help="palette size (default 24)")
    ap.add_argument("--frames", type=int, default=1, help="frames in a horizontal sheet")
    ap.add_argument("--out", type=pathlib.Path, help="output path (default: <source>_prepared.png)")
    ap.add_argument("--filter", choices=sorted(FILTERS), default=None,
                     help="force a resample filter instead of picking by scale factor")
    ap.add_argument("--nearest-above", type=float, default=NEAREST_ABOVE,
                     help=f"use nearest when shrinking by less than this factor, else box "
                          f"(default {NEAREST_ABOVE})")
    ap.add_argument("--mirror", action="store_true",
                     help="flip each frame horizontally in place (frame order unchanged) - "
                          "for deriving a missing left-facing animation from a right one")
    args = ap.parse_args()

    out = args.out or args.source.with_name(args.source.stem + "_prepared.png")
    prepare(args.source, args.height, args.colors, args.frames, out,
            filter_name=args.filter, nearest_above=args.nearest_above, mirror=args.mirror)
    return 0


if __name__ == "__main__":
    sys.exit(main())
