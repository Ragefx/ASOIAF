#!/usr/bin/env python3
"""Make a scene per environment prop, and dress a level with them.

    python3 tools/build_props.py scenes      # (re)write scenes/props/<name>.tscn
    python3 tools/build_props.py place winterfell_training_yard

Each prop scene is a StaticBody2D whose origin is the prop's base - the middle of its
ground shadow - so it y-sorts against the player correctly: walk above a tree's base
and you pass behind the canopy, below it and you pass in front. Props with a
footprint get a small rectangle collider at the base only (a trunk, not the canopy);
decorations without one (flowers, sticks) are walked over.

`place` rewrites the level's prop nodes: every node named prop_* under Actors and
every ext_resource with an id starting prop_ is removed, then the layout below is
written back. Hand-placed nodes that don't use the prop_ prefix are never touched.
A layout entry may carry a 4th item, a dict of node properties written verbatim
(e.g. the drill dummy's completion flag). Scenes not in PROPS - training_dummy -
are hand-written in scenes/props/ and only placed here.
Placement is fixed points plus a seeded scatter, so reruns give the same level.

Sprites come from assets/props/<name>.png (prepared from assets/props/raw/ with
tools/prepare_sprite.py - majority filter, or box for shrinks below ~0.5).
"""
import argparse
import math
import pathlib
import random
import re
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required: pip install Pillow")

ROOT = pathlib.Path(__file__).resolve().parent.parent

# name -> collision footprint (w, h) at the base in world px, or None to walk over it.
PROPS = {
    "tree_oak": (28, 12),
    "tree_pine": (16, 10),
    "bush": (30, 12),
    "boulder": (32, 14),
    "rock_pile": (32, 12),
    "stump": (24, 10),
    "log": (42, 10),
    "dummy": (12, 8),
    "weapon_rack": (50, 10),
    "barrel": (20, 10),
    "fence": (36, 8),
    "fence_straight": (116, 8),
    "wall": (136, 18),
    "tower": (64, 22),
    "hay_bale": (40, 12),
    "well": (44, 16),
    "hay_cart": (60, 14),
    "archery_target": (30, 10),
    "sticks": None,
    "flowers": None,
}

# Plants lean in the wind (shaders/wind_sway.gdshader): px of lean at the top.
SWAY = {"tree_oak": 2.5, "tree_pine": 2.0, "bush": 1.0, "flowers": 1.2}
# Groups a prop joins - trees shed leaves (scripts/life/leaf_fall.gd finds them).
GROUPS = {"tree_oak": ["tree"], "tree_pine": ["tree"]}
BASE_INSET = 3  # px from the sprite's bottom edge up to its origin (inside the shadow)


def write_scenes() -> None:
    out_dir = ROOT / "scenes" / "props"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, footprint in PROPS.items():
        png = ROOT / "assets" / "props" / f"{name}.png"
        h = Image.open(png).height
        sway = SWAY.get(name)
        steps = 2 + (1 if footprint else 0) + (2 if sway else 0)
        lines = [f'[gd_scene load_steps={steps} format=3]', "",
                 f'[ext_resource type="Texture2D" path="res://assets/props/{name}.png" id="1_tex"]']
        if sway:
            lines += ['[ext_resource type="Shader" path="res://shaders/wind_sway.gdshader" id="2_sway"]']
        lines += [""]
        if footprint:
            lines += ['[sub_resource type="RectangleShape2D" id="RectangleShape2D_base"]',
                      f"size = Vector2({footprint[0]}, {footprint[1]})", ""]
        if sway:
            lines += ['[sub_resource type="ShaderMaterial" id="ShaderMaterial_sway"]',
                      'shader = ExtResource("2_sway")', f"shader_parameter/strength = {sway}", ""]
        groups = GROUPS.get(name)
        group_attr = f' groups=[{", ".join(chr(34) + g + chr(34) for g in groups)}]' if groups else ""
        lines += [f'[node name="{name}" type="StaticBody2D"{group_attr}]', "collision_layer = 1", "collision_mask = 0", "",
                  '[node name="Sprite2D" type="Sprite2D" parent="."]', "texture_filter = 1"]
        if sway:
            lines += ['material = SubResource("ShaderMaterial_sway")']
        lines += ['texture = ExtResource("1_tex")', f"offset = Vector2(0, {-(h // 2) + BASE_INSET})", ""]
        if footprint:
            lines += ['[node name="CollisionShape2D" type="CollisionShape2D" parent="."]',
                      f"position = Vector2(0, {-footprint[1] // 2})",
                      'shape = SubResource("RectangleShape2D_base")', ""]
        (out_dir / f"{name}.tscn").write_text("\n".join(lines))
        print(f"scenes/props/{name}.tscn")


# --- level layouts -------------------------------------------------------------------

def training_yard() -> list[tuple]:
    """Winterfell's training yard, scene 1 of Act 1 (Morning Duties).

    Invisible walls at +-320 (north: the castle wall); the earth yard spans roughly x +-256, y -352..224, with a
    track leaving south (|x| < 48). The castle's curtain wall closes the north side
    (base y = WALL_Y) with two towers; the trees west, east and south are the edge of
    the godswood. The ground image covers +-960 x +-704."""
    WALL_Y = -300
    placed = [
        # the straw men; the middle one is Torren's, and counts the drill
        ("training_dummy", 0, -66, {"completion_flag": '"act1_drill_done"', "hits_needed": 5}),
        ("training_dummy", -120, -86), ("training_dummy", 120, -86),
        # Cley's fence rail, east of the dummies, where the player sees it from the start
        ("fence_straight", 196, -168), ("fence_straight", 300, -168),
        # kit along the north side of the yard, under the wall
        ("weapon_rack", -170, -236), ("weapon_rack", -96, -244),
        ("barrel", 180, -240), ("barrel", 206, -228), ("barrel", 190, -214),
        ("stump", 236, -110), ("log", -226, 170), ("sticks", -40, 196),
        ("rock_pile", 236, 190),
        ("fence_straight", -250, 250),
        # farm corner on the west side of the yard: hay, a cart, the horse, the hens
        ("hay_bale", -282, -70), ("hay_bale", -276, -44), ("hay_cart", -262, 30),
        ("life/horse", -238, 104), ("well", 286, 60), ("archery_target", 210, 110),
        ("life/hen", -236, -14), ("life/hen", -214, 8), ("life/hen", -250, 50),
        # life in the yard
        ("life/guard_spar_r", -162, 160), ("life/guard_spar_l", -98, 160),
        ("life/guard_idle", -300, -250), ("life/guard_idle", 300, -236),
        ("life/hound_sleeping", 132, -222), ("life/cat", 266, 80),
        ("life/crow", 70, 180), ("life/crow", -60, -214), ("life/crow", 180, 30),
        ("life/brazier", -250, -262), ("life/brazier", 250, -262),
        ("life/stable_boy", 100, 206, {"points": "PackedVector2Array(0, 0, 140, 0)", "speed": 34.0}),
        # Stark banners hang on the curtain wall's face
        ("life/banner_stark", -200, -296), ("life/banner_stark", -64, -296),
        ("life/banner_stark", 64, -296), ("life/banner_stark", 200, -296),
    ]
    # the godswood's creatures, beyond the yard where the player sees but can't reach them
    placed += [("life/stag", -470, 150), ("life/hare", 400, 170), ("life/hare", -390, -130),
               ("life/hare", 520, -40), ("life/crow", 420, -200)]
    # butterflies over the grass, each a different colour
    tints = ['Color(1, 1, 1, 1)', 'Color(1, 0.9, 0.35, 1)', 'Color(0.55, 0.75, 1, 1)',
             'Color(1, 0.6, 0.35, 1)', 'Color(0.85, 0.65, 1, 1)']
    for i, (bx, by) in enumerate([(-296, -150), (292, -40), (-300, 200), (296, 180), (-360, 40),
                                  (380, -110), (-420, -60), (440, 90)]):
        placed.append(("life/butterfly", bx, by, {"modulate": tints[i % len(tints)]}))
    # the curtain wall, with a tower either side of the yard
    x = -960 + 68
    while x < 960 + 68:
        placed.append(("wall", x, WALL_Y))
        x += 134
    placed += [("tower", -420, WALL_Y + 10), ("tower", 420, WALL_Y + 10)]

    rng = random.Random("winterfell_training_yard")
    taken = [(e[1], e[2]) for e in placed if e[0] not in ("wall", "life/butterfly")]

    def free(x, y, gap):
        return all(math.hypot(x - a, y - b) >= gap for a, b in taken)

    def blocked(x, y):
        on_yard = -280 <= x <= 280 and -360 <= y <= 250
        on_track = abs(x) < 72 and y > 200
        by_wall = y < WALL_Y + 60   # nothing grows against or beyond the curtain wall
        return on_yard or on_track or by_wall

    # godswood: never on the yard, the track, or against the wall
    trees = 0
    for _ in range(6000):
        if trees >= 60:
            break
        x, y = rng.uniform(-930, 930), rng.uniform(-660, 700)
        if blocked(x, y) or math.hypot(x / 1.4, y) < 330 or not free(x, y, 78):
            continue
        placed.append((rng.choice(["tree_oak", "tree_oak", "tree_pine"]), round(x), round(y)))
        taken.append((x, y))
        trees += 1

    # undergrowth and ground clutter on the grass, some of it inside the walls
    clutter = ["bush"] * 4 + ["boulder"] * 2 + ["rock_pile"] * 2 + ["flowers"] * 6 + ["sticks"] * 3 + ["stump"]
    added = 0
    for _ in range(6000):
        if added >= 80:
            break
        x, y = rng.uniform(-930, 930), rng.uniform(-660, 700)
        if blocked(x, y) or not free(x, y, 40):
            continue
        placed.append((rng.choice(clutter), round(x), round(y)))
        taken.append((x, y))
        added += 1
    return placed


LEVELS = {"winterfell_training_yard": training_yard}


def place(level: str) -> None:
    path = ROOT / "scenes" / "world" / f"{level}.tscn"
    text = path.read_text()
    # drop previous prop_ ext_resources and prop_ node blocks
    text = re.sub(r'\[ext_resource [^\]]*id="prop_[^"]*"\]\n', "", text)
    text = re.sub(r'\[node name="prop_[^"]*"[^\]]*parent="Actors"[^\]]*\]\n(?:[^\[\n].*\n|\n)*', "", text)
    text = text.rstrip("\n") + "\n"

    layout = LEVELS[level]()
    used = sorted({e[0] for e in layout})

    def scene_path(n: str) -> str:  # "life/hen" -> scenes/life/hen.tscn, "barrel" -> scenes/props/
        return f"res://scenes/{n}.tscn" if "/" in n else f"res://scenes/props/{n}.tscn"

    def rid(n: str) -> str:
        return "prop_" + n.replace("/", "_")

    ext = "".join(f'[ext_resource type="PackedScene" path="{scene_path(n)}" id="{rid(n)}"]\n' for n in used)
    # ext_resources go after the last existing one
    last = list(re.finditer(r"\[ext_resource [^\]]*\]\n", text))[-1]
    text = text[:last.end()] + ext + text[last.end():]
    # load_steps is advisory; keep it roughly honest
    n_ext = len(re.findall(r"\[ext_resource ", text)); n_sub = len(re.findall(r"\[sub_resource ", text))
    text = re.sub(r"load_steps=\d+", f"load_steps={n_ext + n_sub + 1}", text, count=1)

    nodes = []
    for i, entry in enumerate(layout):
        name, x, y = entry[:3]
        extra = "".join(f"{k} = {v}\n" for k, v in (entry[3] if len(entry) > 3 else {}).items())
        nodes.append(f'\n[node name="prop_{i:03d}_{name.replace("/", "_")}" parent="Actors" '
                     f'instance=ExtResource("{rid(name)}")]\n'
                     f"position = Vector2({x}, {y})\n{extra}")
    path.write_text(text + "".join(nodes))
    counts = {n: sum(1 for e in layout if e[0] == n) for n in used}
    print(f"{level}: {len(layout)} props {counts}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scenes")
    p = sub.add_parser("place")
    p.add_argument("level", choices=sorted(LEVELS))
    a = ap.parse_args()
    if a.cmd == "scenes":
        write_scenes()
    else:
        place(a.level)
    return 0


if __name__ == "__main__":
    sys.exit(main())
