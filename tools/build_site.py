#!/usr/bin/env python3
"""Build a walkable site from its approved layout (data/world/sites/<id>.json).

    python3 tools/build_site.py winterfell

Writes:
  assets/world/<id>_ground.png   the material map WorldGround streams from: one pixel
                                 per 32 px grid vertex, red = material (0 grass,
                                 1 earth, 2 cobble)
  scenes/world/<id>.tscn         the site: streamed ground, moat, walls, gates, every
                                 building, the godswood, props, people and animals

Buildings without art yet are `blockout` massings at their real footprint and height
(scripts/world/blockout.gd) until the building kit replaces them; walls and towers too.
Existing art is used where it fits (the stables, the heart tree, the crypt stair, the
keep's gate, trees, yard props, the people and animals of scenes/life).
Placement is data plus a seeded scatter, so reruns give the same site. Hand edits to
the .tscn are overwritten; change the layout or this file instead.
"""
import json
import math
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from PIL import Image  # noqa: E402

from build_act1_levels import gd, strs, v  # noqa: E402
from build_props import PROPS  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
TILE = 32
GRASS, EARTH, COBBLE = 0, 1, 2

# How tall each kind of blockout stands (front face, px). A grown man is 56.
HEIGHTS = {
    "great_keep": 300, "great_hall": 170, "armory": 150, "kitchens": 120, "guards_hall": 140,
    "guest_house": 150, "forge": 100, "sept": 150, "kennels": 80, "granary": 140, "barracks": 120,
    "library_tower": 330, "maesters_turret": 360, "bell_tower": 300, "first_keep": 260,
    "broken_tower": 420, "glass_gardens": 70,
}
OUTER_WALL_H, INNER_WALL_H, TOWER_H = 150, 190, 250
STONE = "Color(0.52, 0.51, 0.49, 1)"
STONE_OLD = "Color(0.44, 0.44, 0.42, 1)"
SLATE = "Color(0.33, 0.35, 0.40, 1)"
WALLTOP = "Color(0.46, 0.45, 0.43, 1)"


class Site:
    def __init__(self, data):
        self.d = data
        self.id = data["id"]
        self.W, self.H = data["size"]
        self.ext, self.subs, self.nodes, self.actors = [], [], [], []
        self.markers = {}
        self.n = 0
        self.rng = random.Random(self.id)
        self.blocked = []  # rects (x0, y0, x1, y1) nothing may be scattered into

    # --- resources ---------------------------------------------------------------
    def ext_res(self, kind, path, rid):
        if all(e[2] != rid for e in self.ext):
            self.ext.append((kind, path, rid))
        return rid

    def shape(self, w, h):
        sid = f"rect_{int(w)}x{int(h)}"
        if all(f'id="{sid}"' not in s for s in self.subs):
            self.subs.append(f'[sub_resource type="RectangleShape2D" id="{sid}"]\nsize = {v(w, h)}\n')
        return sid

    def name(self, base):
        self.n += 1
        return f"{base}_{self.n:03d}"

    # --- building blocks ---------------------------------------------------------
    def solid(self, parent, x0, y0, x1, y1, label="Solid"):
        """An invisible collider over a plan rectangle."""
        n = self.name(label)
        sid = self.shape(x1 - x0, y1 - y0)
        self.nodes.append(f'[node name="{n}" type="StaticBody2D" parent="{parent}"]\n'
                          f"position = {v((x0 + x1) / 2, (y0 + y1) / 2)}\ncollision_layer = 1\ncollision_mask = 0\n")
        self.nodes.append(f'[node name="CollisionShape2D" type="CollisionShape2D" parent="{parent}/{n}"]\nshape = SubResource("{sid}")\n')

    def blockout(self, label, x0, y0, x1, y1, height, round_=False, battlements=False, door=True,
                 wall=STONE, roof=SLATE, collide=True):
        """A placeholder massing over the plan rect (x0, y0)-(x1, y1), origin at its south edge."""
        self.ext_res("Script", "res://scripts/world/blockout.gd", "blockout")
        w, d = x1 - x0, y1 - y0
        n = self.name(label)
        self.actors.append(
            f'[node name="{n}" type="Node2D" parent="Actors"]\nposition = {v((x0 + x1) / 2, y1)}\n'
            f'script = ExtResource("blockout")\nfootprint = {v(w, d)}\nheight = {float(height)}\n'
            f"round = {gd(round_)}\nroof_color = {roof}\nwall_color = {wall}\ndoor = {gd(door)}\nbattlements = {gd(battlements)}\n")
        if collide:
            inset = 0.15 if round_ else 0.0
            sid = self.shape(w * (1 - inset), d * (1 - inset))
            self.actors.append(f'[node name="Body" type="StaticBody2D" parent="Actors/{n}"]\nposition = {v(0, -d / 2)}\n'
                               f"collision_layer = 1\ncollision_mask = 0\n")
            self.actors.append(f'[node name="CollisionShape2D" type="CollisionShape2D" parent="Actors/{n}/Body"]\n'
                               f'shape = SubResource("{sid}")\n')
        self.blocked.append((x0 - 24, y0 - height, x1 + 24, y1 + 24))
        return n

    def place(self, scene, x, y, extra=""):
        """Instance scenes/<scene>.tscn ("props/well", "life/hen") with its base at (x, y)."""
        rid = self.ext_res("PackedScene", f"res://scenes/{scene}.tscn", "s_" + scene.replace("/", "_"))
        n = self.name(scene.split("/")[-1])
        self.actors.append(f'[node name="{n}" parent="Actors" instance=ExtResource("{rid}")]\nposition = {v(x, y)}\n{extra}')
        fw, fh = (PROPS.get(scene.split("/")[-1]) or (30, 12)) if scene.startswith("props/") else (30, 12)
        self.blocked.append((x - fw / 2 - 8, y - fh - 8, x + fw / 2 + 8, y + 8))

    def free(self, x, y, gap=0):
        return not any(x0 - gap <= x <= x1 + gap and y0 - gap <= y <= y1 + gap for x0, y0, x1, y1 in self.blocked)

    def scatter(self, scenes, rect, count, gap=30, tries=40):
        x0, y0, x1, y1 = rect
        for _ in range(count):
            for _ in range(tries):
                x, y = self.rng.uniform(x0, x1), self.rng.uniform(y0, y1)
                if self.free(x, y, gap):
                    self.place(self.rng.choice(scenes), round(x), round(y))
                    break

    # --- output ------------------------------------------------------------------
    def write(self, player_at):
        root = "".join(w.capitalize() for w in self.id.split("_"))
        out = [f"[gd_scene load_steps={len(self.ext) + len(self.subs) + 1} format=3]", ""]
        out += [f'[ext_resource type="{k}" path="{p}" id="{i}"]' for k, p, i in self.ext] + [""]
        out += self.subs
        out.append(f'[node name="{root}" type="Node2D"]\n')
        out += self.nodes
        out.append('[node name="Markers" type="Node2D" parent="."]\n')
        for n, (x, y) in self.markers.items():
            out.append(f'[node name="{n}" type="Marker2D" parent="Markers"]\nposition = {v(x, y)}\n')
        out.append('[node name="Actors" type="Node2D" parent="."]\ny_sort_enabled = true\n')
        out.append(f'[node name="Player" parent="Actors" instance=ExtResource("player")]\nposition = {v(*player_at)}\n')
        out += self.actors
        path = ROOT / "scenes" / "world" / f"{self.id}.tscn"
        path.write_text("\n".join(out))
        print(f"-> {path.relative_to(ROOT)} ({len(self.actors)} actor blocks)")


def rect_of(item):
    if "rect" in item:
        x, y, w, h = item["rect"]
        return x, y, x + w, y + h
    cx, cy, r = item["circle"]
    return cx - r, cy - r, cx + r, cy + r


def by_id(items, key):
    return next(i for i in items if i["id"] == key)


# --- the material map ----------------------------------------------------------------

def material_map(site):
    d = site.d
    vw, vh = site.W // TILE + 1, site.H // TILE + 1
    m = [[GRASS] * vw for _ in range(vh)]

    def paint(x0, y0, x1, y1, mat):
        for vy in range(max(0, round(y0 / TILE)), min(vh, round(y1 / TILE) + 1)):
            for vx in range(max(0, round(x0 / TILE)), min(vw, round(x1 / TILE) + 1)):
                m[vy][vx] = mat

    def path(points, width=96):
        for (ax, ay), (bx, by) in zip(points, points[1:]):
            paint(min(ax, bx) - width / 2, min(ay, by) - width / 2, max(ax, bx) + width / 2, max(ay, by) + width / 2, EARTH)

    walls = {w["id"]: w for w in d["walls"]}
    ox, oy, ow, oh = walls["outer_wall"]["rect"]
    ix, iy, iw, ih = walls["inner_wall"]["rect"]
    # everything from the outer wall's foot to the inner wall's is stone, water or mud underfoot
    paint(ox - 16, oy - 16, ox + ow + 16, oy + oh + 16, EARTH)
    t = walls["inner_wall"]["thick"]
    paint(ix + t + 32, iy + t + 32, ix + iw - t - 32, iy + ih - t - 32, GRASS)

    areas = {a["id"]: a for a in d["areas"]}
    b = {x["id"]: x for x in d["buildings"]}
    for key in ("training_yard", "lichyard"):
        paint(*rect_of(areas[key]), EARTH)
    x0, y0, x1, y1 = rect_of(areas["castle_yard"])
    paint(x0, y0, x1, y1, EARTH)
    paint(x0 + 64, y0 + 64, x1 - 64, y1 - 32, COBBLE)

    gx, gy = by_id(d["gates"], "main_gate")["at"]
    path([(gx, y1), (gx, site.H)], 160)                        # the gate passage and the road south
    hx, hy = by_id(d["gates"], "hunters_gate")["at"]
    ty0 = rect_of(areas["training_yard"])
    path([(0, hy), (ix + t + 60, hy), (ix + t + 60, hy)], 128)  # the Hunter's Gate passage
    kx0, ky0, kx1, ky1 = rect_of(b["kennels"])
    path([(ix + t + 60, hy), ((kx0 + kx1) / 2, hy), ((kx0 + kx1) / 2, (ty0[1] + ty0[3]) / 2), (ty0[0], (ty0[1] + ty0[3]) / 2)])
    path([(gx, y0), (gx, ty0[3])], 128)                         # castle yard up to the training yard
    hall = rect_of(b["great_hall"])
    path([((hall[0] + hall[2]) / 2, ty0[1]), ((hall[0] + hall[2]) / 2, hall[3])])
    keep = rect_of(b["great_keep"])
    arm = rect_of(b["armory"])
    path([(ty0[0] + 40, ty0[1]), (ty0[0] + 40, keep[3] + 40), ((keep[0] + keep[2]) / 2, keep[3] + 40)])
    path([((arm[0] + arm[2]) / 2, arm[3]), ((arm[0] + arm[2]) / 2, keep[3] + 40)])
    gw = rect_of(areas["godswood"])
    hx_, hy_, _ = areas["heart_tree"]["circle"]
    path([(ty0[0] + 40, hy_ + 180), (gw[2] - 40, hy_ + 180), (hx_, hy_ + 180), (hx_, hy_ + 60)], 64)
    stair = rect_of(b["crypt_stair"])
    path([(ty0[2], (ty0[1] + ty0[3]) / 2), ((stair[0] + stair[2]) / 2, (ty0[1] + ty0[3]) / 2),
          ((stair[0] + stair[2]) / 2, stair[3])])
    for key in ("stables", "guest_house", "granary"):
        r = rect_of(b[key])
        path([(x1, r[3] - 60), (r[0], r[3] - 60)])
    for key in ("forge", "sept"):
        r = rect_of(b[key])
        path([(r[2], r[3] - 50), (x0, r[3] - 50)])

    img = Image.new("RGB", (vw, vh))
    img.putdata([(m[y][x], 0, 0) for y in range(vh) for x in range(vw)])
    out = ROOT / "assets" / "world" / f"{site.id}_ground.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"-> {out.relative_to(ROOT)} ({vw}x{vh} vertices)")
    return f"res://assets/world/{site.id}_ground.png"


# --- walls, moat, gates --------------------------------------------------------------

def walls_and_moat(site):
    d = site.d
    walls = {w["id"]: w for w in d["walls"]}
    ox, oy, ow, oh = walls["outer_wall"]["rect"]
    ot = walls["outer_wall"]["thick"]
    mx, my, mw, mh = walls["moat"]["rect"]
    mt = walls["moat"]["thick"]
    ix, iy, iw, ih = walls["inner_wall"]["rect"]
    it = walls["inner_wall"]["thick"]
    gx, _ = by_id(d["gates"], "main_gate")["at"]
    _, hy = by_id(d["gates"], "hunters_gate")["at"]
    gate_half, hunt_half = 70, 60

    # moat: four strips of water, drawn under everything that stands
    site.ext_res("Shader", "res://shaders/moat_water.gdshader", "water")
    site.subs.append('[sub_resource type="ShaderMaterial" id="water_mat"]\nshader = ExtResource("water")\n')
    site.nodes.append('[node name="Moat" type="Node2D" parent="."]\n')
    for i, (x0, y0, x1, y1) in enumerate([(mx, my, mx + mw, my + mt), (mx, my + mh - mt, mx + mw, my + mh),
                                          (mx, my + mt, mx + mt, my + mh - mt), (mx + mw - mt, my + mt, mx + mw, my + mh - mt)]):
        site.nodes.append(f'[node name="Water{i}" type="Polygon2D" parent="Moat"]\nmaterial = SubResource("water_mat")\n'
                          f"polygon = PackedVector2Array({x0}, {y0}, {x1}, {y0}, {x1}, {y1}, {x0}, {y1})\n")
    # bridges over it at both gates
    for i, (x0, y0, x1, y1) in enumerate([(gx - gate_half, my + mh - mt, gx + gate_half, my + mh),
                                          (mx, hy - hunt_half, mx + mt, hy + hunt_half)]):
        site.nodes.append(f'[node name="Bridge{i}" type="Polygon2D" parent="Moat"]\ncolor = Color(0.42, 0.3, 0.19, 1)\n'
                          f"polygon = PackedVector2Array({x0}, {y0}, {x1}, {y0}, {x1}, {y1}, {x0}, {y1})\n")

    # colliders: the whole band from the outer wall's face to the inner wall's, gates cut out
    site.nodes.append('[node name="Walls" type="Node2D" parent="."]\n')
    band_in = (ix + it, iy + it, ix + iw - it, iy + ih - it)
    band_out = (ox, oy, ox + ow, oy + oh)
    site.solid("Walls", band_out[0], band_out[1], band_out[2], band_in[1])                  # north
    site.solid("Walls", band_in[2], band_in[1], band_out[2], band_out[3])                   # east
    site.solid("Walls", band_out[0], band_in[3], gx - gate_half, band_out[3])               # south, west of gate
    site.solid("Walls", gx + gate_half, band_in[3], band_in[2], band_out[3])                # south, east of gate
    site.solid("Walls", band_out[0], band_in[1], band_in[0], hy - hunt_half)                # west, north of gate
    site.solid("Walls", band_out[0], hy + hunt_half, band_in[0], band_in[3])                # west, south of gate
    # the edge of the built world, for now: fields outside the walls, then nothing
    W, H = site.W, site.H
    site.solid("Walls", -40, -40, W + 40, 0, "Edge")
    site.solid("Walls", -40, H, W + 40, H + 40, "Edge")
    site.solid("Walls", -40, 0, 0, H, "Edge")
    site.solid("Walls", W, 0, W + 40, H, "Edge")

    # the curtain walls as massings, split at the gates; towers along the inner one
    def ring(x, y, w, h, t, height, label, wall):
        # north and south runs, then the east and west runs between them
        runs = [(x, y, x + w, y + t), (x, y + h - t, gx - gate_half, y + h), (gx + gate_half, y + h - t, x + w, y + h),
                (x + w - t, y + t, x + w, y + h - t),
                (x, y + t, x + t, hy - hunt_half), (x, hy + hunt_half, x + t, y + h - t)]
        for r in runs:
            site.blockout(label, *r, height, battlements=True, door=False, wall=wall, roof=WALLTOP, collide=False)

    ring(ox, oy, ow, oh, ot, OUTER_WALL_H, "OuterWall", STONE_OLD)
    ring(ix, iy, iw, ih, it, INNER_WALL_H, "InnerWall", STONE)
    for tx, ty in [(ix, iy), (ix + iw, iy), (ix, iy + ih), (ix + iw, iy + ih)] + \
                  [(ix + iw * f, iy) for f in (0.33, 0.66)] + [(ix + iw, iy + ih * f) for f in (0.3, 0.7)] + \
                  [(ix, iy + ih * 0.25)]:
        r = 110
        site.blockout("WallTower", tx - r, ty - r * 0.7, tx + r, ty + r * 0.7, TOWER_H, round_=True,
                      battlements=True, door=False, roof=WALLTOP, collide=False)
    # gatehouses: two towers either side of each passage
    for dx in (-1, 1):
        cx = gx + dx * (gate_half + 70)
        site.blockout("MainGate", cx - 70, iy + ih - it - 40, cx + 70, iy + ih + 40, TOWER_H + 30,
                      battlements=True, door=False, collide=True)
        site.blockout("OuterGate", cx - 60, oy + oh - ot - 20, cx + 60, oy + oh + 20, OUTER_WALL_H + 40,
                      battlements=True, door=False, collide=True)
    for dy in (-1, 1):
        cy = hy + dy * (hunt_half + 60)
        site.blockout("HuntersGate", ix - 40, cy - 60, ix + it + 40, cy + 60, TOWER_H,
                      battlements=True, door=False, collide=True)


# --- the castle ------------------------------------------------------------------

def castle(site):
    d = site.d
    b = {x["id"]: x for x in d["buildings"]}
    areas = {a["id"]: a for a in d["areas"]}

    for key, item in b.items():
        if key in ("main_gatehouse", "hunters_gatehouse", "covered_bridge", "crypt_stair", "stables"):
            continue
        x0, y0, x1, y1 = rect_of(item)
        round_ = "circle" in item
        roof = {"broken_tower": "Color(0.2, 0.18, 0.17, 1)", "glass_gardens": "Color(0.62, 0.78, 0.78, 1)"}.get(key, SLATE)
        wall = STONE_OLD if key in ("first_keep", "broken_tower") else STONE
        if round_:  # a round plan reads as an ellipse in 3/4 view
            cy = (y0 + y1) / 2
            y0, y1 = cy - (y1 - y0) * 0.35, cy + (y1 - y0) * 0.35
        site.blockout(key.title().replace("_", ""), x0, y0, x1, y1, HEIGHTS.get(key, 140), round_=round_,
                      battlements=key in ("first_keep", "bell_tower", "library_tower", "maesters_turret"),
                      wall=wall, roof=roof, door=key not in ("broken_tower",))
    # glass gardens are open inside; the kit will give them doors - for now a solid glasshouse
    # the covered bridge: armory to keep, overhead
    x0, y0, x1, y1 = rect_of(b["covered_bridge"])
    site.blockout("CoveredBridge", x0, y0, x1, y1, 30, door=False, wall="Color(0.40, 0.30, 0.2, 1)",
                  roof="Color(0.45, 0.34, 0.23, 1)", collide=False)

    # existing art where it fits
    sx0, sy0, sx1, sy1 = rect_of(b["stables"])
    for i in range(2):
        site.place("props/stable", sx0 + 170 + i * 300, sy1)
    keep = rect_of(b["great_keep"])
    site.place("props/keep_gate", (keep[0] + keep[2]) / 2, keep[3] + 30)
    st = rect_of(b["crypt_stair"])
    site.place("props/crypt_stair", (st[0] + st[2]) / 2, st[3])
    hx, hy, _ = areas["heart_tree"]["circle"]
    site.place("props/heart_tree", hx, hy)
    site.place("props/black_pool", hx + 10, hy + 60)
    px, py, pr = areas["hot_pools"]["circle"]
    site.nodes.append(f'[node name="HotPool" type="Polygon2D" parent="Moat"]\nmaterial = SubResource("water_mat")\n'
                      "polygon = PackedVector2Array(" + ", ".join(
                          f"{px + math.cos(a / 16 * math.tau) * pr * 1.4:.0f}, {py + math.sin(a / 16 * math.tau) * pr * 0.8:.0f}"
                          for a in range(16)) + ")\n")
    site.blocked.append((px - pr * 1.5, py - pr, px + pr * 1.5, py + pr))

    # the training yard
    tx0, ty0, tx1, ty1 = rect_of(areas["training_yard"])
    for i, x in enumerate(range(int(tx0) + 200, int(tx1) - 150, 180)):
        site.place("props/dummy", x, ty0 + 200)
    for x in (tx0 + 150, tx1 - 150):
        site.place("props/weapon_rack", x, ty0 + 90)
    site.place("props/archery_target", tx1 - 120, ty1 - 160)
    site.place("props/archery_target", tx1 - 120, ty1 - 320)
    site.place("life/guard_spar_l", (tx0 + tx1) / 2 - 40, ty1 - 180)
    site.place("life/guard_spar_r", (tx0 + tx1) / 2 + 40, ty1 - 180)
    site.place("props/barrel", tx0 + 60, ty1 - 60)

    # the castle yard
    cx0, cy0, cx1, cy1 = rect_of(areas["castle_yard"])
    site.place("props/well", (cx0 + cx1) / 2 + 300, (cy0 + cy1) / 2 - 100)
    site.place("props/wagon", cx0 + 180, cy1 - 200)
    site.place("props/hay_cart", cx1 - 200, cy0 + 260)
    for x in (cx0 + 100, cx0 + 140, cx1 - 120):
        site.place("props/barrel", x, cy0 + 120)
    site.place("life/horse", sx0 + 60, sy1 + 90)
    site.place("life/horse", sx0 + 360, sy1 + 110)
    site.place("life/stable_boy", sx0 + 200, sy1 + 80)
    site.place("props/hay_bale", sx1 - 40, sy1 + 60)
    gx, gy = by_id(d["gates"], "main_gate")["at"]
    for dx in (-1, 1):
        site.place("life/guard_idle", gx + dx * 110, cy1 - 40)
        site.place("life/brazier", gx + dx * 150, cy1 - 80)
    site.place("life/banner_stark", (keep[0] + keep[2]) / 2 - 140, keep[3] + 2)
    site.place("life/banner_stark", (keep[0] + keep[2]) / 2 + 140, keep[3] + 2)

    # work and animals around the buildings
    f = rect_of(b["forge"])
    site.place("life/forge", f[2] + 70, f[3] + 10)
    site.place("life/blacksmith", f[2] + 130, f[3] + 30)
    g = rect_of(b["guest_house"])
    site.place("life/laundry_line", g[0] - 180, g[1] + 120)
    site.place("life/washerwoman", g[0] - 120, g[1] + 170)
    k = rect_of(b["kennels"])
    site.place("life/hound_sleeping", k[0] + 120, k[3] + 40)
    site.place("life/hound_sleeping", k[2] - 80, k[3] + 60)
    kit = rect_of(b["kitchens"])
    for i in range(4):
        site.place("life/hen", kit[0] + 40 + i * 70, kit[3] + 50 + (i % 2) * 30)
    gr = rect_of(b["granary"])
    site.place("props/hay_bale", gr[0] + 80, gr[3] + 50)
    site.place("props/trunks", gr[0] + 200, gr[3] + 40)
    site.place("life/cat", gr[2] - 100, gr[3] + 40)
    ba = rect_of(b["barracks"])
    site.place("life/guard_idle", ba[2] - 80, ba[3] + 40)
    gh = rect_of(b["guards_hall"])
    site.place("life/guard_idle", gh[0] + 60, gh[3] + 40)
    lx0, ly0, lx1, ly1 = rect_of(areas["lichyard"])
    for i in range(6):
        site.place("props/rock_pile" if i % 2 else "props/boulder", lx0 + 60 + (i % 3) * 140, ly0 + 100 + (i // 3) * 120)
    site.place("life/crow", lx1 - 60, ly0 + 60)

    # the godswood: dense old wood around a clearing and the path in
    gw = rect_of(areas["godswood"])
    site.blocked.append((hx - 160, hy - 120, hx + 160, hy + 200))
    site.blocked.append((gw[0], hy + 150, gw[2], hy + 210))   # the path in
    site.blocked.append((hx - 40, hy + 60, hx + 40, hy + 210))
    site.scatter(["props/tree_oak", "props/tree_pine", "props/tree_pine", "props/bush"],
                 (gw[0] + 40, gw[1] + 120, gw[2] - 40, gw[3] - 20), 70, gap=34)

    # keep scattered greenery out of the yards and the lichyard
    for key in ("training_yard", "castle_yard", "lichyard", "glass_gardens"):
        x0, y0, x1, y1 = rect_of(areas[key])
        site.blocked.append((x0 - 40, y0 - 40, x1 + 40, y1 + 40))

    # fields outside the walls
    W, H = site.W, site.H
    for rect in [(20, 30, W - 20, 150), (20, 150, 150, H - 20), (W - 150, 150, W - 20, H - 20)]:
        site.scatter(["props/tree_oak", "props/tree_pine", "props/bush", "props/boulder"], rect, 14, gap=60)
    site.scatter(["props/bush", "props/flowers", "props/stump"], (640, 700, 4150, 3650), 30, gap=60)


def main() -> int:
    site_id = sys.argv[1] if len(sys.argv) > 1 else "winterfell"
    data = json.loads((ROOT / "data/world/sites" / f"{site_id}.json").read_text())
    site = Site(data)
    site.ext_res("PackedScene", "res://scenes/actors/Player.tscn", "player")

    ground = material_map(site)
    site.ext_res("Script", "res://scripts/world/world_ground.gd", "ground_script")
    site.ext_res("Texture2D", ground, "ground_map")
    layers = [{"tileset": "res://assets/tilesets/world/grass_dirt_32.tres", "upper": [GRASS]},
              {"tileset": "res://assets/tilesets/world/cobble_earth_32.tres", "upper": [COBBLE], "only_near": [COBBLE]}]
    site.nodes.append('[node name="Light" type="CanvasModulate" parent="."]\ncolor = Color(1, 0.98, 0.95, 1)\n')
    site.nodes.append('[node name="Ground" type="Node2D" parent="."]\nscript = ExtResource("ground_script")\n'
                      f'material_map = ExtResource("ground_map")\nlayers = Array[Dictionary]([{", ".join(gd(x) for x in layers)}])\n')
    site.ext_res("Script", "res://scripts/world/camera_limits.gd", "camera")
    site.nodes.append(f'[node name="CameraLimits" type="Node2D" parent="."]\nscript = ExtResource("camera")\n'
                      f"rect = Rect2(0, 0, {site.W}, {site.H})\n")

    walls_and_moat(site)
    castle(site)

    # the sky: cloud shadows and birds over everything
    site.ext_res("Script", "res://scripts/life/drifting_layer.gd", "drift")
    site.ext_res("Texture2D", "res://assets/fx/cloud_shadows.png", "t_clouds")
    site.ext_res("Script", "res://scripts/life/bird_flyover.gd", "birds")
    site.ext_res("SpriteFrames", "res://assets/life/bird.tres", "bird")
    site.nodes.append('[node name="CloudShadows" type="Sprite2D" parent="."]\nmodulate = Color(1, 1, 1, 0.7)\n'
                      'texture_filter = 1\ntexture_repeat = 2\ntexture = ExtResource("t_clouds")\nregion_enabled = true\n'
                      f"region_rect = Rect2(0, 0, {site.W + 800}, {site.H + 800})\nposition = {v(site.W / 2, site.H / 2)}\n"
                      'script = ExtResource("drift")\ndrift = Vector2(-9, -3)\n')
    site.nodes.append('[node name="BirdFlyover" type="Node2D" parent="."]\nscript = ExtResource("birds")\nbird_frames = ExtResource("bird")\n')

    gx, gy = by_id(data["gates"], "main_gate")["at"]
    areas = {a["id"]: a for a in data["areas"]}
    tx0, ty0, tx1, ty1 = rect_of(areas["training_yard"])
    site.markers["main_gate"] = (gx, 3560)
    site.markers["outside_gate"] = (gx, site.H - 60)
    site.markers["training_yard"] = ((tx0 + tx1) / 2, ty1 - 80)
    site.markers["godswood"] = (areas["heart_tree"]["circle"][0], areas["heart_tree"]["circle"][1] + 170)
    site.write(site.markers["main_gate"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
