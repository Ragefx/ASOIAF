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
    # later scenes: castle yard, great hall, godswood
    "stable": (310, 40),
    "keep_gate": (160, 30),
    "broken_tower": (60, 22),
    "heart_tree": (44, 16),
    "feast_table": (130, 36),
    # the Wolfswood in summer snow
    "tree_pine_snow": (16, 10),
    "tree_oak_snow": (28, 12),
    "holdfast": (80, 24),
    "direwolf_dead": (96, 20),
    "bridge": None,
    # scenes 5-12
    "wheelhouse": (130, 30),
    "crypt_king": (56, 20),
    "lyanna_statue": (30, 14),
    "crypt_stair": (70, 24),
    "hall_wall": (248, 20),
    "high_table": (170, 40),
    "wagon": (90, 24),
    "trunks": (36, 12),
    "black_pool": (80, 30),
    "tower_climber": None,
    "sticks": None,
    "flowers": None,
}

# Plants lean in the wind (shaders/wind_sway.gdshader): px of lean at the top.
SWAY = {"tree_pine_snow": 2.0, "tree_oak_snow": 2.5, "heart_tree": 2.0, "tree_oak": 2.5, "tree_pine": 2.0, "bush": 1.0, "flowers": 1.2}
# Groups a prop joins - trees shed leaves (scripts/life/leaf_fall.gd finds them).
GROUPS = {"tree_oak": ["tree"], "tree_pine": ["tree"], "tree_oak_snow": ["tree"], "tree_pine_snow": ["tree"]}
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


def castle_yard() -> list[tuple]:
    """Winterfell's main yard, scene 2 of Act 1 (Preparing for a King).

    Cobbles inside the walls; the view (1280x720 world px) is held to x +-704, y -470..460
    by the level's CameraLimits, and invisible walls keep the player within x +-650. North:
    the Great Keep's gate in the curtain wall (base y = WALL_Y), torches either side of the
    door, banners on the wall, the Broken Tower at the east end. West: the forge and the
    armoury yard, where the player arrives. East: the stables (the level's Stables node is
    the interaction in front of the doors), horses and hay. South-east: the laundry. South:
    the track out to the gate (the level's ExitSouth). NPCs are placed in the level scene
    itself, not here."""
    WALL_Y = -250
    placed = [
        ("keep_gate", 0, WALL_Y + 2),
        # torches on the gate's face: drawn over the gate (z 1), hung ~36px up the wall
        ("life/wall_torch", -40, WALL_Y - 34, {"z_index": 1}), ("life/wall_torch", 40, WALL_Y - 34, {"z_index": 1}),
        ("life/brazier", -110, WALL_Y + 16), ("life/brazier", 110, WALL_Y + 16),
        ("life/banner_stark", -218, WALL_Y + 4), ("life/banner_stark", 218, WALL_Y + 4),
        ("life/banner_stark", -490, WALL_Y + 4), ("life/banner_stark", 490, WALL_Y + 4),
        ("life/guard_idle", -76, WALL_Y + 30), ("life/guard_idle", 76, WALL_Y + 30),
        ("tower", -354, WALL_Y + 10), ("tower", 354, WALL_Y + 10), ("broken_tower", 640, WALL_Y + 12),
        # the forge and the armoury yard (west), where the player comes in
        ("life/forge", -560, -60), ("life/blacksmith", -470, -30),
        ("weapon_rack", -600, 60), ("weapon_rack", -530, 70), ("barrel", -610, 130),
        ("barrel", -590, 146), ("barrel", -360, 196), ("barrel", -336, 206), ("barrel", -350, 222),
        ("life/hound_sleeping", -380, 60), ("life/crow", -300, -120),
        # the stables (east) with horses out front and hay waiting
        ("stable", 480, -44), ("life/horse", 390, 60), ("life/horse", 580, 50),
        ("hay_bale", 600, 110), ("hay_bale", 620, 136), ("hay_cart", 510, 150),
        ("life/hen", 200, 10), ("life/hen", 170, 40), ("life/hen", 230, 60), ("life/hen", -250, 300),
        ("life/cat", 640, -90),
        # the laundry (south-east): the line and the washerwoman at her tub
        ("life/laundry_line", 470, 262), ("life/washerwoman", 380, 300),
        # the middle of the yard: the well, provisions being counted for the guests
        ("well", -40, 70), ("barrel", 40, 40), ("barrel", 60, 56),
        ("hay_bale", -170, 290), ("log", 170, 320), ("sticks", -80, 330),
        ("life/crow", 20, 200), ("life/crow", 300, 200),
        # the gate south out of the yard, and the men on it
        ("life/guard_idle", -70, 330), ("life/guard_idle", 70, 330),
        ("life/brazier", -130, 350), ("life/brazier", 130, 350),
    ]
    # the curtain wall either side of the gate, closing the north side end to end
    for x in (-150, -286, -422, -558, -694, 150, 286, 422, 558, 694):
        placed.append(("wall", x, WALL_Y))
    # the Great Keep's own walls rising in tiers behind it, so the view above the curtain
    # wall is castle, not more yard (y-sort draws them behind the gate and towers)
    for row, y in enumerate((WALL_Y - 60, WALL_Y - 120, WALL_Y - 180)):
        x = -762 + 68 * (row % 2)
        while x < 800:
            placed.append(("wall", x, y))
            x += 136
    return placed


def wolfswood() -> list[tuple]:
    """A holdfast clearing in the Wolfswood, scene 3 of Act 1 (A Deserter's Head).

    Summer snow. The ring - a ragged half-circle of horses and men - stands north of the
    block at (0, -40); Lord Stark, his sons, Theon and Jory are NPCs placed in the level
    scene, as are Hune by the south-west treeline where the party comes in and "your
    place" at the left of the ring. The road home leaves east. Same view limits as the
    castle yard: x +-704, y -470..460; the player is kept within x +-650, y -380..400."""
    placed = [
        ("stump", 0, -58), ("life/gared", 0, -40),
        ("holdfast", 250, -250), ("rock_pile", 320, -214), ("boulder", 180, -210),
    ]
    # the ring: horses on a half-circle north of the block, heads in, a guard at each
    tints = ["Color(1, 1, 1, 1)", "Color(0.55, 0.5, 0.48, 1)", "Color(1.1, 1.05, 1, 1)",
             "Color(0.4, 0.36, 0.34, 1)", "Color(0.85, 0.8, 0.75, 1)", "Color(1, 0.95, 0.9, 1)"]
    for i, deg in enumerate((200, 225, 250, 290, 315, 340)):
        a = math.radians(deg)
        x, y = round(200 * math.cos(a)), round(-40 + 120 * math.sin(a))
        placed.append(("life/horse", x, y - 20, {"modulate": tints[i]}))
    placed += [("life/guard_idle", -150, -150), ("life/guard_idle", 150, -150),
               ("life/guard_idle", -236, -60), ("life/guard_idle", 236, -60),
               ("life/crow", 60, 60), ("life/crow", -340, -200), ("life/stag", 560, 260),
               ("life/hare", -560, -120), ("life/hare", 420, 330)]

    rng = random.Random("wolfswood_holdfast")
    taken = [(e[1], e[2]) for e in placed]

    def free(x, y, gap):
        return all(math.hypot(x - a, y - b) >= gap for a, b in taken)

    def clearing(x, y):
        in_ring = (x / 330) ** 2 + ((y + 40) / 230) ** 2 < 1
        on_track_in = -520 <= x <= -200 and 40 <= y <= 330
        on_road_home = x > 200 and -90 <= y <= 0
        return in_ring or on_track_in or on_road_home

    trees = 0
    for _ in range(8000):
        if trees >= 70:
            break
        x, y = rng.uniform(-720, 720), rng.uniform(-470, 520)
        if clearing(x, y) or not free(x, y, 70):
            continue
        placed.append((rng.choice(["tree_pine_snow"] * 3 + ["tree_oak_snow"]), round(x), round(y)))
        taken.append((x, y))
        trees += 1
    added = 0
    for _ in range(6000):
        if added >= 40:
            break
        x, y = rng.uniform(-700, 700), rng.uniform(-440, 460)
        if (x / 260) ** 2 + ((y + 40) / 170) ** 2 < 1 or not free(x, y, 36):
            continue
        placed.append((rng.choice(["boulder", "rock_pile", "sticks", "sticks", "stump", "log"]), round(x), round(y)))
        taken.append((x, y))
        added += 1
    return placed


def kingsroad() -> list[tuple]:
    """The kingsroad north of Winterfell, scene 4 of Act 1 (Six Pups and a Seventh).

    The road runs bottom to top through snowy woods (x within +-64). The player comes in
    at the south (the "bridge" marker: two logs over a frozen ditch) and the column has
    stopped up the road, where the dead direwolf lies on the west verge at (-190, -230)
    with the party around her (NPCs in the level scene). The white pup sits alone in
    the trees east of the road at (430, -60) - only found by leaving the road."""
    placed = [
        ("direwolf_dead", -190, -230),
        ("life/ghost_pup", 430, -60),
        ("log", -70, 372), ("log", 70, 372),
    ]
    # the stopped column: horses nose to tail up the road, riders beside them
    tints = ["Color(1, 1, 1, 1)", "Color(0.55, 0.5, 0.48, 1)", "Color(0.4, 0.36, 0.34, 1)",
             "Color(0.85, 0.8, 0.75, 1)", "Color(1.1, 1.05, 1, 1)", "Color(0.7, 0.66, 0.6, 1)"]
    for i, y in enumerate((-400, -330, -120, -40, 40, 120)):
        placed.append(("life/horse", 20 if i % 2 else -24, y, {"modulate": tints[i]}))
    placed += [("life/guard_idle", 60, -380), ("life/guard_idle", -60, -100),
               ("life/guard_idle", 64, 60), ("life/crow", -300, -380), ("life/crow", 220, 200),
               ("life/hare", -520, 160), ("life/stag", 600, -300)]

    rng = random.Random("kingsroad_north")
    taken = [(e[1], e[2]) for e in placed]

    def free(x, y, gap):
        return all(math.hypot(x - a, y - b) >= gap for a, b in taken)

    def open_ground(x, y):
        on_road = abs(x) < 110
        # tall canopies reach far above their base: keep trees well south of her too
        by_the_wolf = -360 <= x <= -60 and -330 <= y <= 20
        # a small clearing, and nothing tall just south of it to hide the pup behind
        pup_clearing = math.hypot(x - 430, y + 60) < 70 or (abs(x - 430) < 110 and -60 <= y <= 190)
        return on_road or by_the_wolf or pup_clearing

    trees = 0
    for _ in range(8000):
        if trees >= 80:
            break
        x, y = rng.uniform(-720, 720), rng.uniform(-470, 520)
        if open_ground(x, y) or not free(x, y, 64):
            continue
        placed.append((rng.choice(["tree_pine_snow"] * 3 + ["tree_oak_snow"]), round(x), round(y)))
        taken.append((x, y))
        trees += 1
    added = 0
    for _ in range(6000):
        if added >= 40:
            break
        x, y = rng.uniform(-700, 700), rng.uniform(-440, 460)
        if abs(x) < 90 or (-330 <= x <= -60 and -330 <= y <= -130) or not free(x, y, 36):
            continue
        placed.append((rng.choice(["boulder", "rock_pile", "sticks", "sticks", "stump", "log"]), round(x), round(y)))
        taken.append((x, y))
        added += 1
    return placed


def _yard_people(extra: list[tuple], clear: tuple | None = None) -> list[tuple]:
    """The castle yard as scene 2 dressed it, plus a later scene's people and baggage.
    `clear` (x0, y0, x1, y1) empties that part of scene 2's yard - the well and the
    barrels are not in the road when a king rides up it."""
    base = castle_yard()
    if clear:
        x0, y0, x1, y1 = clear
        base = [e for e in base if not (x0 <= e[1] <= x1 and y0 <= e[2] <= y1)]
    return base + extra


def _pair(name: str, x: int, y: int) -> list[tuple]:
    """A man of the household standing, and the same man kneeling (hidden) in his place."""
    return [(name, x, y, {"groups": ["standing"]}),
            ("life/guard_kneel", x, y, {"groups": ["kneeling"], "visible": "false"})]


def yard_arrival() -> list[tuple]:
    """Scene 5: the royal party rides in from the south gate to the keep door, between two
    lines of the household - Torren in the left line at (-100, 20)."""
    extra = []
    for y in (-140, -80, 80, 140):
        extra += _pair("life/guard_idle", -100, y)
    for y in (-140, -80, 20, 80, 140):
        extra += _pair("life/guard_idle", 100, y)
    extra += [
        ("wheelhouse", 0, 330), ("life/kingsguard", -96, 250), ("life/kingsguard", 96, 250),
        ("life/goldcloak", -60, 350), ("life/goldcloak", 60, 350), ("life/goldcloak", -150, 340),
        ("life/goldcloak", 150, 340),
        # the baggage train at the back, and in it a girl with a covered head carrying water
        ("wagon", 330, 330), ("trunks", 400, 310), ("life/nyra_covered", 270, 318),
        ("life/banner_baratheon", -354, -246), ("life/banner_lannister", 354, -246),
    ]
    return _yard_people(extra, clear=(-160, -200, 160, 380))


def yard_visit() -> list[tuple]:
    """Scene 8: nine days in. Lannister men and Stark men circle each other in the yard."""
    return _yard_people([
        ("training_dummy", -330, 120), ("training_dummy", -270, 110),
        ("life/lannister_soldier", 120, 170), ("life/lannister_soldier", 170, 190),
        ("life/lannister_soldier", 90, 210), ("life/guard_idle", 30, 150), ("life/guard_idle", -10, 190),
        ("life/goldcloak", -60, 330), ("life/goldcloak", 60, 330),
        ("life/kingsguard", 40, -200), ("wagon", 400, 300), ("trunks", 340, 320),
        ("life/banner_baratheon", -354, -246), ("life/banner_lannister", 354, -246),
    ])


def yard_fall() -> list[tuple]:
    """Scene 9: the half-empty morning. A small figure goes up the outside of the Broken
    Tower (group "climber", hidden once he falls); the pup stands over him after."""
    return _yard_people([
        ("tower_climber", 646, -316, {"groups": ["climber"]}),
        ("life/pup_howl", 596, -176, {"groups": ["fallen"], "visible": "false"}),
        ("training_dummy", -330, 120),
        ("life/banner_baratheon", -354, -246), ("life/banner_lannister", 354, -246),
    ])


def yard_departure() -> list[tuple]:
    """Scene 11: the royal column forming up to leave, the yard all elbows."""
    extra = [("wheelhouse", 60, 90), ("wagon", 200, 190), ("wagon", 330, 250), ("wagon", -220, 180),
             ("trunks", -120, 240), ("trunks", 120, 290), ("trunks", -300, 260),
             ("life/kingsguard", -40, 60), ("life/kingsguard", 160, 60)]
    for x in (-200, -120, 200, 280):
        extra.append(("life/goldcloak", x, 320))
    for x, y in ((-300, 120), (300, 140), (-20, 180)):
        extra.append(("life/lannister_soldier", x, y))
    extra += [("life/horse", -40, 150, {"modulate": "Color(0.4, 0.36, 0.34, 1)"}), ("life/horse", 420, 180),
              ("life/banner_baratheon", -354, -246), ("life/banner_lannister", 354, -246)]
    return _yard_people(extra, clear=(-160, -200, 160, 380))


def crypts() -> list[tuple]:
    """Scene 6: the crypts. Stone kings in two rows down a flagstone aisle; Torren at the
    stair head at the north end, the king and Lord Stark at Lyanna's tomb at the south."""
    placed = [("crypt_stair", 0, -252), ("lyanna_statue", 0, 290),
              ("life/candelabra", -70, 270), ("life/candelabra", 70, 270)]
    for y in (-150, -40, 70, 180):
        placed += [("crypt_king", -120, y), ("crypt_king", 120, y)]
        placed += [("life/wall_torch", -150, y - 60, {"z_index": 1}), ("life/wall_torch", 150, y - 60, {"z_index": 1})]
    return placed


def great_hall() -> list[tuple]:
    """Scene 7: the feast. The high table on its dais at the north wall, long tables down
    the hall, the hearth, candles; the low benches at the south-west end are Torren's."""
    WALL_Y = -214
    placed = [("high_table", 0, -150), ("life/hearth", -420, WALL_Y + 8)]
    for x in (-620, -372, -124, 124, 372, 620):
        placed.append(("hall_wall", x, WALL_Y))
    for x in (-250, 250):
        for y in (-40, 110, 250):
            placed.append(("feast_table", x, y))
    diners = ["life/diner_ale", "life/diner_bread", "life/diner_woman"]
    i = 0
    for x in (-250, 250):
        for y in (-40, 110, 250):
            for dx in (-44, 0, 44):
                if (x, y) == (-250, 250) and dx == -44:
                    continue  # Torren's seat on the lowest bench
                # on the far bench: set back far enough that head and shoulders show over
                # the table's back edge (the table is 80px tall and y-sorts in front)
                placed.append((diners[i % 3], x + dx, y - 64))
                i += 1
    placed += [("life/candelabra", -120, -180), ("life/candelabra", 120, -180),
               ("life/candelabra", -560, 200), ("life/candelabra", 560, 200),
               ("barrel", 540, 300), ("barrel", 566, 316), ("life/hound_sleeping", -520, 300)]
    return placed


def godswood() -> list[tuple]:
    """Scene 10: the godswood - the heart tree over its black pool, old trees close round."""
    placed = [("heart_tree", 0, -96), ("black_pool", 70, -40),
              ("life/crow", -120, -150), ("life/crow", 160, -160), ("life/hare", -300, 100)]
    rng = random.Random("winterfell_godswood")
    taken = [(e[1], e[2]) for e in placed]
    for _ in range(9000):
        if len(taken) > 70:
            break
        x, y = rng.uniform(-720, 720), rng.uniform(-470, 520)
        if (abs(x) < 60 and y > 0) or (abs(x) < 170 and -230 < y < 20):
            continue
        if not all(math.hypot(x - a, y - b) >= 66 for a, b in taken):
            continue
        placed.append((rng.choice(["tree_oak", "tree_oak", "tree_pine"]), round(x), round(y)))
        taken.append((x, y))
    for _ in range(3000):
        if len(placed) > 110:
            break
        x, y = rng.uniform(-700, 700), rng.uniform(-440, 460)
        if (abs(x) < 50 and y > 0) or (abs(x) < 150 and -210 < y < 10):
            continue
        placed.append((rng.choice(["bush", "flowers", "sticks", "boulder"]), round(x), round(y)))
    return placed


def walls() -> list[tuple]:
    """Scene 12: the south rampart. The parapet's face along the walk's south edge."""
    placed = []
    x = -1260
    while x < 1300:
        placed.append(("wall", x, 88))
        x += 134
    placed += [("tower", -700, 96), ("tower", 700, 96)]
    return placed


LEVELS = {"winterfell_training_yard": training_yard, "winterfell_yard": castle_yard,
          "wolfswood_holdfast": wolfswood, "kingsroad_north": kingsroad,
          "winterfell_yard_arrival": yard_arrival, "winterfell_yard_visit": yard_visit,
          "winterfell_yard_fall": yard_fall, "winterfell_yard_departure": yard_departure,
          "winterfell_crypts": crypts, "winterfell_great_hall": great_hall,
          "winterfell_godswood": godswood, "winterfell_walls": walls}


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
        props = dict(entry[3]) if len(entry) > 3 else {}
        # "groups" goes in the node header (sequences show/hide by group), the rest are properties
        groups = props.pop("groups", [])
        group_attr = f' groups=[{", ".join(chr(34) + g + chr(34) for g in groups)}]' if groups else ""
        extra = "".join(f"{k} = {v}\n" for k, v in props.items())
        nodes.append(f'\n[node name="prop_{i:03d}_{name.replace("/", "_")}" parent="Actors"{group_attr} '
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
