#!/usr/bin/env python3
"""Make the world's streaming tilesets from the 32px corner-match ground sets.

    python3 tools/build_world_tilesets.py

For each two-surface set (grass/dirt, cobble/earth, snow/earth) this writes
assets/tilesets/world/<name>.png - the 4x4 corner atlas plus a fifth row holding the
plain version of the full "upper" tile (decorations painted out, as build_ground.py
does for baked levels) - and a TileSet .tres over it. The two full tiles and the
plain one get the eight flip/transpose alternatives (ids 0-7), so WorldGround can
turn uniform cells freely and a big field doesn't look like wallpaper.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from PIL import Image  # noqa: E402

from build_ground import CORNERS_TO_ATLAS, TILE, plain_snow, plain_variant  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
SETS = {  # name -> how the full upper tile is made plain
    "grass_dirt_32": "grass",
    "cobble_earth_32": None,
    "snow_earth_32": "snow",
}
FULL_UPPER = CORNERS_TO_ATLAS[frozenset({"TL", "TR", "BL", "BR"})]
FULL_LOWER = CORNERS_TO_ATLAS[frozenset()]
PLAIN = (0, 4)
# alternative id -> (flip_h, flip_v, transpose): all eight turns of a square
TURNS = [(h, v, t) for t in (False, True) for v in (False, True) for h in (False, True)]


def main() -> int:
    out_dir = ROOT / "assets/tilesets/world"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, plain in SETS.items():
        atlas = Image.open(ROOT / f"assets/tilesets/{name}.png").convert("RGBA")
        full = atlas.crop((FULL_UPPER[0] * TILE, FULL_UPPER[1] * TILE, (FULL_UPPER[0] + 1) * TILE, (FULL_UPPER[1] + 1) * TILE))
        plain_tile = plain_snow(full) if plain == "snow" else plain_variant(full) if plain == "grass" else full
        img = Image.new("RGBA", (4 * TILE, 5 * TILE))
        img.paste(atlas.crop((0, 0, 4 * TILE, 4 * TILE)), (0, 0))
        img.paste(plain_tile, (PLAIN[0] * TILE, PLAIN[1] * TILE))
        img.save(out_dir / f"{name}.png")

        lines = ['[gd_resource type="TileSet" load_steps=3 format=3]', "",
                 f'[ext_resource type="Texture2D" path="res://assets/tilesets/world/{name}.png" id="1_tex"]', "",
                 '[sub_resource type="TileSetAtlasSource" id="atlas_0"]', 'texture = ExtResource("1_tex")',
                 "texture_region_size = Vector2i(32, 32)"]
        for pos in sorted(set(CORNERS_TO_ATLAS.values()) | {PLAIN}, key=lambda p: (p[1], p[0])):
            key = f"{pos[0]}:{pos[1]}"
            lines.append(f"{key}/0 = 0")
            if pos in (FULL_UPPER, FULL_LOWER, PLAIN):
                for alt, (h, v, t) in enumerate(TURNS[1:], start=1):
                    lines.append(f"{key}/{alt} = {alt}")
                    for flag, on in (("flip_h", h), ("flip_v", v), ("transpose", t)):
                        if on:
                            lines.append(f"{key}/{alt}/{flag} = true")
        lines += ["", "[resource]", "tile_size = Vector2i(32, 32)", 'sources/0 = SubResource("atlas_0")', ""]
        (out_dir / f"{name}.tres").write_text("\n".join(lines))
        print(f"assets/tilesets/world/{name}.png + .tres")
    return 0


if __name__ == "__main__":
    sys.exit(main())
