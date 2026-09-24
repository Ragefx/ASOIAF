#!/usr/bin/env python3
"""Build a Godot 4 SpriteFrames .tres from prepared animation strips.

Every character's animations live as separate horizontal strips (one PNG per
animation, N frames wide) because that's what SpriteCook and prepare_sprite.py
produce. Godot's AnimatedSprite2D wants one SpriteFrames resource with all
animations in it, each frame an AtlasTexture region of its strip. This writes
that resource directly as text - no Godot editor or headless export needed,
so it works in this sandbox and reproduces identically on a real machine.

Usage:
    python3 tools/build_spriteframes.py torren/v7 nyra/v3     # current sets (see below)
    python3 tools/build_spriteframes.py torren nyra           # the old 16x24 chibi set

A versioned folder (torren/v7, nyra/v3) holds strips made by tools/fit_animation.py,
named plainly (idle.png, walk_down.png, ...), and gets <character>.tres inside it.
A bare character folder is the original layout: *_prepared.png strips, <char>.tres beside them.

Reads assets/sprites/<char>/<anim>_prepared.png for each animation in ANIMATIONS
below and writes assets/sprites/<char>/<char>.tres. Animation names match what
scripts/actors/player.gd's ANIM_FALLBACKS / _resolve_animation expect exactly:
"idle" (no direction suffix - it's a single forward-facing pose) and
"walk_<down|up|left|right>". fps and loop come from FPS/LOOP below, not from
Godot project settings, since this never touches the editor.
"""
import argparse
import pathlib
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required: pip install Pillow")

ROOT = pathlib.Path(__file__).resolve().parent.parent
FPS = 8.0  # matches SpriteCook's animation_fps for every tier-1 strip generated so far
FRAMES = 8

# (animation name in the SpriteFrames resource, source file stem, loop)
ANIMATIONS = [
    ("idle", "idle_prepared", True),
    ("walk_down", "walk_down_prepared", True),
    ("walk_up", "walk_up_prepared", True),
    ("walk_right", "walk_right_prepared", True),
    ("walk_left", "walk_left_prepared", True),
]


def build(char: str) -> pathlib.Path:
    char_dir = ROOT / "assets" / "sprites" / char
    name = char.split("/")[0]
    out_path = char_dir / f"{name}.tres"
    versioned = "/" in char

    ext_lines = []
    atlas_blocks = []
    anim_entries = []
    ext_id_by_file = {}
    load_steps = 1  # the [resource] block itself counts as one step

    for anim_name, stem, loop in ANIMATIONS:
        if versioned:
            stem = anim_name
        png_path = char_dir / f"{stem}.png"
        if not png_path.exists():
            print(f"warning: {png_path} missing, skipping animation '{anim_name}'", file=sys.stderr)
            continue

        img = Image.open(png_path)
        if img.width % FRAMES:
            print(f"warning: {png_path} width {img.width} does not divide into {FRAMES} frames",
                  file=sys.stderr)
        frame_w = img.width // FRAMES
        frame_h = img.height

        if stem not in ext_id_by_file:
            ext_id = f"tex_{stem}"
            ext_id_by_file[stem] = ext_id
            rel_path = f"res://assets/sprites/{char}/{stem}.png"
            ext_lines.append(f'[ext_resource type="Texture2D" path="{rel_path}" id="{ext_id}"]')
            load_steps += 1
        ext_id = ext_id_by_file[stem]

        frame_refs = []
        for i in range(FRAMES):
            atlas_id = f"atlas_{stem}_{i}"
            atlas_blocks.append(
                f'[sub_resource type="AtlasTexture" id="{atlas_id}"]\n'
                f'atlas = ExtResource("{ext_id}")\n'
                f'region = Rect2({i * frame_w}, 0, {frame_w}, {frame_h})\n'
            )
            frame_refs.append(
                f'{{\n"duration": 1.0,\n"texture": SubResource("{atlas_id}")\n}}'
            )
            load_steps += 1

        frames_joined = ", ".join(frame_refs)
        anim_entries.append(
            f'{{\n"frames": [{frames_joined}],\n'
            f'"loop": {"true" if loop else "false"},\n'
            f'"name": &"{anim_name}",\n'
            f'"speed": {FPS}\n}}'
        )

    if not anim_entries:
        sys.exit(f"no animation strips found for '{char}' under {char_dir}")

    animations_joined = ", ".join(anim_entries)
    out = []
    out.append(f'[gd_resource type="SpriteFrames" load_steps={load_steps} format=3]')
    out.append("")
    out.extend(ext_lines)
    out.append("")
    out.extend(atlas_blocks)
    out.append("[resource]")
    out.append(f"animations = [{animations_joined}]")
    out.append("")

    out_path.write_text("\n".join(out))
    print(f"{char}: {len(anim_entries)} animation(s), {load_steps - 1} sub/ext resources -> {out_path}")
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("character", nargs="+", help="character directory name(s) under assets/sprites/")
    args = ap.parse_args()
    for char in args.character:
        build(char)
    return 0


if __name__ == "__main__":
    sys.exit(main())
