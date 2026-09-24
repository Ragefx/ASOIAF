#!/usr/bin/env python3
"""Animated life for levels - animals, people at work, banners, fire - as scenes.

    python3 tools/build_life.py            # (re)build every entry in LIFE
    python3 tools/build_life.py hen crow   # just these

For each entry: fit its SpriteCook strip(s) from assets/life/raw/ to game scale with
tools/fit_animation.py (character/subject height in px, relative to Torren's 48),
write a SpriteFrames resource, and write scenes/life/<name>.tscn:

    critter  AnimatedSprite2D + scripts/life/critter.gd - idles, potters, flees the player
    walker   AnimatedSprite2D + scripts/life/walker.gd  - walks a route (points set per level)
    static   StaticBody2D + looping AnimatedSprite2D (+ collider at the base if footprint)
    deco     looping AnimatedSprite2D, no collision (banners)
    frames   SpriteFrames only, for scripts that spawn it (the bird flyover)

Every scene's origin is the subject's base (its ground shadow), so it y-sorts against
the player like the props do. Raw strips are the untouched SpriteCook downloads.
"""
import argparse
import pathlib
import subprocess
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required: pip install Pillow")

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "assets" / "life" / "raw"
OUT = ROOT / "assets" / "life"
SCENES = ROOT / "scenes" / "life"

# name: kind, height (px at game scale), animations {anim: (raw file, fps, loop, mirror)},
#       footprint (w, h) for static colliders, props written onto the root node, base inset
LIFE = {
    "banner_stark": dict(kind="deco", height=96, anims={"idle": ("banner_stark", 7, True, False)}),
    "brazier": dict(kind="static", height=40, footprint=(20, 10), anims={"idle": ("brazier", 10, True, False)}),
    "hound_sleeping": dict(kind="static", height=26, footprint=(40, 12), anims={"idle": ("hound", 5, True, False)}),
    "horse": dict(kind="static", height=58, footprint=(48, 14), anims={"idle": ("horse", 6, True, False)}),
    "hen": dict(kind="critter", height=20, anims={"idle": ("hen", 8, True, False)},
                props={"flees_by": '"run"', "wander_radius": 36.0}),
    "crow": dict(kind="critter", height=16, anims={"idle": ("crow", 7, True, False)},
                 props={"flees_by": '"fly"', "wander_radius": 20.0, "flee_radius": 90.0}),
    "cat": dict(kind="critter", height=20, anims={"idle": ("cat", 5, True, False)},
                props={"flees_by": '"none"', "wander_radius": 0.0}),
    "hare": dict(kind="critter", height=18, anims={"idle": ("hare", 8, True, False)},
                 props={"flees_by": '"run"', "wander_radius": 30.0, "flee_radius": 110.0}),
    "stag": dict(kind="critter", height=56, anims={"idle": ("stag", 6, True, False)},
                 props={"flees_by": '"run"', "wander_radius": 30.0, "flee_radius": 160.0}),
    # grown men stand taller than Torren (45px idle, 48px walking)
    "guard_idle": dict(kind="static", height=56, footprint=(18, 8), anims={"idle": ("guard_idle", 6, True, False)}),
    # a sparring pair: the same drill, one mirrored, placed facing each other. Height counts
    # the raised sword (frame 2); the body in its fighting crouch comes out ~53px.
    "guard_spar_r": dict(kind="static", height=62, footprint=(18, 8), anims={"idle": ("guard_spar", 9, True, False)}),
    "guard_spar_l": dict(kind="static", height=62, footprint=(18, 8), anims={"idle": ("guard_spar", 9, True, True)}),
    "stable_boy": dict(kind="walker", height=42, anims={"walk_right": ("stable_boy_walk", 8, True, False)}),
    # later scenes: fire and cloth that move, and townsfolk at work (grown adults: taller than Torren)
    "forge": dict(kind="static", height=104, footprint=(90, 20), anims={"idle": ("forge", 8, True, False)}),
    "wall_torch": dict(kind="deco", height=34, anims={"idle": ("wall_torch", 10, True, False)}),
    "candelabra": dict(kind="static", height=60, footprint=(14, 6), anims={"idle": ("candelabra", 8, True, False)}),
    "laundry_line": dict(kind="deco", height=68, anims={"idle": ("laundry_line", 6, True, False)}),
    # height counts the raised hammer; his body stooped at the anvil comes out ~62px
    "blacksmith": dict(kind="static", height=78, footprint=(30, 10), anims={"idle": ("blacksmith", 8, True, False)}),
    # kneeling at her tub: a kneeling grown woman, head about where Torren's is standing
    "washerwoman": dict(kind="static", height=60, footprint=(40, 10), anims={"idle": ("washerwoman", 8, True, False)}),
    # Act 1 people, frames only: NPCs load these through data/npcs/npcs.json's sprite_frames.
    # Grown men 56px (Torren is 45 standing); Rodrik stout and a touch shorter; Hodor is
    # near seven feet in the books - 72px, a head and more over everyone - barrel included.
    "rodrik": dict(kind="frames", height=55, anims={"idle": ("rodrik_idle", 6, True, False)}),
    "jory": dict(kind="frames", height=57, anims={"idle": ("jory_idle", 6, True, False)}),
    "hodor": dict(kind="frames", height=72, anims={"idle": ("hodor_idle", 6, True, False)}),
    "stable_hand": dict(kind="frames", height=42, anims={"idle": ("stable_boy_idle", 8, True, False)}),
    # scene 3, the deserter: Lord Stark with Ice 57px, Hune 56, Theon (nineteen) 55,
    # Robb (fifteen) 50 - just over Torren's 45 - and Bran, seven, 36.
    "eddard": dict(kind="frames", height=57, anims={"idle": ("ned_idle", 6, True, False)}),
    "hune": dict(kind="frames", height=56, anims={"idle": ("hune_idle", 6, True, False)}),
    "theon": dict(kind="frames", height=55, anims={"idle": ("theon_idle", 6, True, False)}),
    "robb": dict(kind="frames", height=50, anims={"idle": ("robb_idle", 6, True, False)}),
    "bran": dict(kind="frames", height=36, anims={"idle": ("bran_idle", 8, True, False)}),
    # the deserter, kneeling and bound; not someone you can talk to
    "gared": dict(kind="static", height=40, footprint=(28, 8), anims={"idle": ("gared_idle", 6, True, False)}),
    # scene 4, the ride home. Stills only for now (one-frame strips): Jon 49px - fourteen,
    # between Torren and Robb - and the white pup, alone in the snow, 17px.
    "jon": dict(kind="frames", height=49, anims={"idle": ("jon_still", 1, True, False)}),
    "ghost_pup": dict(kind="deco", height=17, anims={"idle": ("ghost_pup", 1, True, False)}),
    # frames only: used by scripts/life/bird_flyover.gd, not placed as a scene
    "bird": dict(kind="frames", height=18, anims={"fly": ("bird_fly", 12, True, False)}),
}


def fit(raw: pathlib.Path, out: pathlib.Path, height: int, mirror: bool) -> None:
    frames = Image.open(raw).width // Image.open(raw).height
    cmd = [sys.executable, str(ROOT / "tools" / "fit_animation.py"), str(raw), str(out),
           "--frames", str(frames), "--char-height", str(height), "--frame", "0"]
    if mirror:
        cmd.append("--mirror")
    subprocess.run(cmd, check=True, capture_output=True)


def spriteframes(name: str, anims: dict) -> tuple[str, int]:
    """Write assets/life/<name>.tres; return its res path and the (square) cell size."""
    ext, subs, entries, cell = [], [], [], 0
    for i, (anim, (_, fps, loop, _m)) in enumerate(anims.items()):
        png = OUT / f"{name}_{anim}.png"
        im = Image.open(png)
        cell, n = im.height, im.width // im.height
        ext.append(f'[ext_resource type="Texture2D" path="res://assets/life/{name}_{anim}.png" id="t{i}"]')
        refs = []
        for f in range(n):
            sid = f"a{i}_{f}"
            subs.append(f'[sub_resource type="AtlasTexture" id="{sid}"]\natlas = ExtResource("t{i}")\n'
                        f"region = Rect2({f * cell}, 0, {cell}, {cell})\n")
            refs.append(f'{{\n"duration": 1.0,\n"texture": SubResource("{sid}")\n}}')
        entries.append(f'{{\n"frames": [{", ".join(refs)}],\n"loop": {str(loop).lower()},\n'
                       f'"name": &"{anim}",\n"speed": {float(fps)}\n}}')
    text = (f'[gd_resource type="SpriteFrames" load_steps={len(ext) + len(subs) + 1} format=3]\n\n'
            + "\n".join(ext) + "\n\n" + "\n".join(subs) + "\n[resource]\n"
            + f"animations = [{', '.join(entries)}]\n")
    (OUT / f"{name}.tres").write_text(text)
    return f"res://assets/life/{name}.tres", cell


def scene(name: str, spec: dict, frames_path: str, cell: int) -> None:
    kind = spec["kind"]
    offset_y = -(cell // 2) + spec.get("inset", 2)
    props = "".join(f"{k} = {v}\n" for k, v in spec.get("props", {}).items())
    first_anim = next(iter(spec["anims"]))
    lines = []
    if kind in ("critter", "walker"):
        script = "critter" if kind == "critter" else "walker"
        lines = [f'[gd_scene load_steps=3 format=3]', "",
                 f'[ext_resource type="SpriteFrames" path="{frames_path}" id="1_frames"]',
                 f'[ext_resource type="Script" path="res://scripts/life/{script}.gd" id="2_script"]', "",
                 f'[node name="{name}" type="AnimatedSprite2D"]', "texture_filter = 1",
                 'sprite_frames = ExtResource("1_frames")', f'animation = &"{first_anim}"',
                 f"offset = Vector2(0, {offset_y})", 'script = ExtResource("2_script")', props]
    else:
        fp = spec.get("footprint")
        root_type = "StaticBody2D" if kind == "static" else "Node2D"
        steps = 3 + (1 if fp else 0)
        lines = [f'[gd_scene load_steps={steps} format=3]', "",
                 f'[ext_resource type="SpriteFrames" path="{frames_path}" id="1_frames"]',
                 '[ext_resource type="Script" path="res://scripts/life/idle_anim.gd" id="2_script"]', ""]
        if fp:
            lines += ['[sub_resource type="RectangleShape2D" id="RectangleShape2D_base"]',
                      f"size = Vector2({fp[0]}, {fp[1]})", ""]
        lines += [f'[node name="{name}" type="{root_type}"]']
        if kind == "static":
            lines += ["collision_layer = 1", "collision_mask = 0"]
        lines += ["", '[node name="Sprite" type="AnimatedSprite2D" parent="."]', "texture_filter = 1",
                  'sprite_frames = ExtResource("1_frames")', f'animation = &"{first_anim}"',
                  f"offset = Vector2(0, {offset_y})", 'script = ExtResource("2_script")',
                  f'anim = &"{first_anim}"', ""]
        if fp:
            lines += ['[node name="CollisionShape2D" type="CollisionShape2D" parent="."]',
                      f"position = Vector2(0, {-fp[1] // 2})", 'shape = SubResource("RectangleShape2D_base")', ""]
    SCENES.mkdir(parents=True, exist_ok=True)
    (SCENES / f"{name}.tscn").write_text("\n".join(lines))


def build(name: str) -> None:
    spec = LIFE[name]
    for anim, (raw, _fps, _loop, mirror) in spec["anims"].items():
        fit(RAW / f"{raw}.png", OUT / f"{name}_{anim}.png", spec["height"], mirror)
    frames_path, cell = spriteframes(name, spec["anims"])
    if spec["kind"] != "frames":
        scene(name, spec, frames_path, cell)
    print(f"{name}: {spec['kind']}, {spec['height']}px in {cell}px frames -> scenes/life/{name}.tscn")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help="entries to build (default: all whose raw strips exist)")
    a = ap.parse_args()
    for name in a.names or LIFE:
        if all((RAW / f"{r}.png").exists() for r, *_ in LIFE[name]["anims"].values()):
            build(name)
        elif a.names:
            sys.exit(f"{name}: raw strip missing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
