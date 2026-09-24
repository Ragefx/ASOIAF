#!/usr/bin/env python3
"""Bake a level's ground into one PNG from a corner-matching 32px tileset.

The SpriteCook 15-piece top-down tileset (assets/tilesets/grass_dirt_32.png) is a
corner-matching autotile: each tile says which of its four corners are grass, and a
level is described by a grid of *vertices* - grass or not - with each cell picking
the tile whose corners match. Non-grass shows as the tileset's other surface: a tan
dirt edge running into dark packed earth, which is a training yard.

Baking to a PNG (drawn by a Sprite2D, like the level's ground always has been) keeps
the scene file trivial and makes the result identical in Godot and in previews made
outside it. The matching TileSet resource (assets/tilesets/grass_dirt_32.tres) is also
in the repo for painting levels by hand in the editor later.

To stop a large field of one grass tile looking like wallpaper, full-grass and
full-earth cells get a random flip/rotation (fixed seed, so the bake is reproducible),
and the full-grass tile's decorations (a flower, mushrooms, pebbles - anything that
isn't green) are painted out to make a plain variant. The decorated original is used
for only DECORATED_SHARE of grass cells; otherwise every tile carries a flower and the
field turns to confetti.

Usage:
    python3 tools/build_ground.py winterfell_training_yard

Level layouts live in LEVELS below. Requires Pillow.
"""
import argparse
import pathlib
import random
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required: pip install Pillow")

ROOT = pathlib.Path(__file__).resolve().parent.parent
TILESET = ROOT / "assets" / "tilesets" / "grass_dirt_32.png"
TILE = 32
DECORATED_SHARE = 0.12

# Atlas (column, row) for each set of grass corners, from SpriteCook's Godot export
# (terrain peering bits of Terrain Set 0). Corners: TL, TR, BL, BR.
CORNERS_TO_ATLAS = {
    frozenset(): (0, 3),
    frozenset({"BL"}): (0, 0),
    frozenset({"TR", "BR"}): (1, 0),
    frozenset({"TL", "BL", "BR"}): (2, 0),
    frozenset({"BL", "BR"}): (3, 0),
    frozenset({"TL", "BR"}): (0, 1),
    frozenset({"TR", "BL", "BR"}): (1, 1),
    frozenset({"TL", "TR", "BL", "BR"}): (2, 1),
    frozenset({"TL", "TR", "BL"}): (3, 1),
    frozenset({"TR"}): (0, 2),
    frozenset({"TL", "TR"}): (1, 2),
    frozenset({"TL", "TR", "BR"}): (2, 2),
    frozenset({"TL", "BL"}): (3, 2),
    frozenset({"BR"}): (1, 3),
    frozenset({"TR", "BL"}): (2, 3),
    frozenset({"TL"}): (3, 3),
}

# Each level: size in tiles (the ground is centred on the scene origin) and a list of
# rectangles of *non-grass vertices*, in tile units relative to the origin
# (x0, y0, x1, y1), inclusive. Everything else is grass.
LEVELS = {
    # Walls sit at +-320px (+-10 tiles). The ground runs well past them so a 1280x720
    # view (the agreed 1440p framing) never shows its edge.
    "winterfell_training_yard": {
        "size": (60, 44),
        "earth": [
            (-8, -9, 8, 7),      # the yard itself; its north edge runs under the castle
                                 # wall (base y = -300), so no earth shows above it
            (-9, -8, -9, 5),     # soften the long edges so it isn't a perfect box
            (9, -8, 9, 5),
            (-6, 8, 6, 8),
            (-1, 9, 1, 22),      # the track leading south out of the yard
        ],
    },
    # Inside the castle: cobbles (the tileset's "upper" surface, grass's role above), with
    # packed earth where horses stand and work gets done. The view is 1280x720 world px,
    # held to x +-704, y -470..460 by the level's CameraLimits; the ground covers that.
    "winterfell_yard": {
        "size": (46, 30),
        "tileset": "cobble_earth_32.png",
        "plain": False,   # no painted-out variant: every cobble tile is fine as it is
        "earth": [
            (10, -2, 20, 3),     # the stable forecourt, trodden to mud
            (9, 0, 10, 2),
            (-19, -2, -14, 3),   # the forge and armoury corner
            (-15, 4, -13, 5),
            (-1, 8, 1, 15),      # the track south to the gate and the winter town
            (10, 6, 17, 10),     # the laundry green, worn bare
        ],
    },
}


def _pixels(img: Image.Image) -> list:
    # getdata() is deprecated from Pillow 12; get_flattened_data() is its replacement.
    return list(img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata())


def plain_variant(tile: Image.Image) -> Image.Image:
    """Paint out non-green pixels with the most common green in the tile."""
    px = [p for p in _pixels(tile) if p[3] and p[1] > p[0] and p[1] > p[2]]
    base = max(set(px), key=px.count)
    out = tile.copy()
    data = [p if (p[1] > p[0] and p[1] > p[2]) else base for p in _pixels(tile)]
    out.putdata(data)
    return out


def build(name: str) -> pathlib.Path:
    spec = LEVELS[name]
    w, h = spec["size"]
    ox, oy = w // 2, h // 2  # tile (0,0) of the layout sits at the image centre
    grass = [[True] * (w + 1) for _ in range(h + 1)]  # vertices
    for x0, y0, x1, y1 in spec["earth"]:
        for vy in range(y0, y1 + 1):
            for vx in range(x0, x1 + 1):
                if 0 <= vx + ox <= w and 0 <= vy + oy <= h:
                    grass[vy + oy][vx + ox] = False

    tileset = ROOT / "assets" / "tilesets" / spec["tileset"] if "tileset" in spec else TILESET
    atlas = Image.open(tileset).convert("RGBA")
    tiles = {
        pos: atlas.crop((pos[0] * TILE, pos[1] * TILE, (pos[0] + 1) * TILE, (pos[1] + 1) * TILE))
        for pos in CORNERS_TO_ATLAS.values()
    }
    full_grass = CORNERS_TO_ATLAS[frozenset({"TL", "TR", "BL", "BR"})]
    plain_grass = plain_variant(tiles[full_grass]) if spec.get("plain", True) else tiles[full_grass]
    rng = random.Random(name)
    out = Image.new("RGBA", (w * TILE, h * TILE))
    for cy in range(h):
        for cx in range(w):
            corners = {k for k, (dx, dy) in {"TL": (0, 0), "TR": (1, 0), "BL": (0, 1), "BR": (1, 1)}.items()
                       if grass[cy + dy][cx + dx]}
            pos = CORNERS_TO_ATLAS[frozenset(corners)]
            tile = tiles[pos]
            if pos == full_grass and rng.random() >= DECORATED_SHARE:
                tile = plain_grass
            if len(corners) in (0, 4):  # uniform cells can be turned freely
                tile = tile.rotate(90 * rng.randrange(4))
                if rng.random() < 0.5:
                    tile = tile.transpose(Image.FLIP_LEFT_RIGHT)
            out.paste(tile, (cx * TILE, cy * TILE))

    path = ROOT / "assets" / "tilesets" / f"{name}_ground.png"
    out.save(path)
    print(f"{name}: {w}x{h} tiles -> {out.size[0]}x{out.size[1]}px -> {path.relative_to(ROOT)}")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("level", nargs="+", choices=sorted(LEVELS))
    for level in ap.parse_args().level:
        build(level)
    return 0


if __name__ == "__main__":
    sys.exit(main())
