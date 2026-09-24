#!/usr/bin/env python3
"""Write the level scenes for Act 1 scenes 5 to 12 (everything after the kingsroad).

    python3 tools/build_act1_levels.py            # all of them
    python3 tools/build_act1_levels.py winterfell_crypts

Each level is described below as data - ground, light, bounds, spawn markers, the NPCs
who can be spoken to, and the scripted beats (scripts/world/sequence.gd steps) - and
written as a .tscn. Props and background life are then placed by
`tools/build_props.py place <level>` (layouts live there, as for the first four levels).
Hand edits to these .tscn files are overwritten; change this file instead.

The castle yard is four levels here, not one: the same yard dressed for the king's
arrival, the days of the visit, the morning of the fall and the departure. Each reuses
winterfell_yard's ground and walls (castle_yard() in build_props.py) with its own people.
"""
import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

YARD_CAMERA = "Rect2(-704, -470, 1408, 930)"
TORREN = "res://assets/sprites/torren/v7/torren.tres"


def v(x, y):
    return f"Vector2({x}, {y})"


def gd(value) -> str:
    """Python value -> Godot text-resource literal."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    if isinstance(value, tuple):  # a Vector2
        return v(*value)
    if isinstance(value, list):
        return "[" + ", ".join(gd(x) for x in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{gd(k)}: {gd(x)}" for k, x in value.items()) + "}"
    raise TypeError(value)


def strs(values) -> str:
    return "Array[String]([" + ", ".join(gd(x) for x in values) + "])"


def dicts(values) -> str:
    return "Array[Dictionary]([" + ", ".join(gd(x) for x in values) + "])"


class Level:
    def __init__(self, name, ground, light, camera=YARD_CAMERA, bounds=(-650, 650, -262, 380), south_gap=0):
        self.name = name
        self.ext = []        # (type, path, id)
        self.subs = []       # text blocks
        self.nodes = []      # text blocks, after the root
        self.actors = []     # text blocks, under Actors
        self.root = "".join(w.capitalize() for w in name.split("_"))
        self._ext("Texture2D", ground, "ground")
        self._ext("PackedScene", "res://scenes/actors/Player.tscn", "player")
        self._ext("PackedScene", "res://scenes/actors/NPC.tscn", "npc")
        self.nodes.append(f'[node name="Light" type="CanvasModulate" parent="."]\ncolor = {light}\n')
        self.nodes.append(f'[node name="Ground" type="Sprite2D" parent="."]\ntexture_filter = 1\ntexture = ExtResource("ground")\n')
        if camera:
            self._ext("Script", "res://scripts/world/camera_limits.gd", "camera")
            self.nodes.append(f'[node name="CameraLimits" type="Node2D" parent="."]\nscript = ExtResource("camera")\nrect = {camera}\n')
        self._bounds(*bounds, south_gap)
        self.markers = {}

    def _ext(self, kind, path, rid):
        if all(e[2] != rid for e in self.ext):
            self.ext.append((kind, path, rid))
        return rid

    def _bounds(self, x0, x1, y0, y1, gap):
        w, h = x1 - x0, y1 - y0
        self.subs.append(f'[sub_resource type="RectangleShape2D" id="wall_h"]\nsize = {v(w + 200, 24)}\n')
        self.subs.append(f'[sub_resource type="RectangleShape2D" id="wall_v"]\nsize = {v(24, h + 200)}\n')
        blocks = [("WallNorth", ((x0 + x1) / 2, y0), "wall_h"), ("WallWest", (x0, (y0 + y1) / 2), "wall_v"),
                  ("WallEast", (x1, (y0 + y1) / 2), "wall_v")]
        if gap:  # a gate in the south wall
            half = (w + 200) / 2
            blocks += [("WallSouthWest", (-gap / 2 - half, y1), "wall_h"), ("WallSouthEast", (gap / 2 + half, y1), "wall_h")]
        else:
            blocks.append(("WallSouth", ((x0 + x1) / 2, y1), "wall_h"))
        self.nodes.append('[node name="Bounds" type="Node2D" parent="."]\n')
        for n, (x, y), shape in blocks:
            self.nodes.append(f'[node name="{n}" type="StaticBody2D" parent="Bounds"]\nposition = {v(x, y)}\n'
                              f'collision_layer = 1\ncollision_mask = 0\n')
            self.nodes.append(f'[node name="CollisionShape2D" type="CollisionShape2D" parent="Bounds/{n}"]\n'
                              f'shape = SubResource("{shape}")\n')

    def node(self, text):
        self.nodes.append(text)

    def marker(self, name, x, y):
        self.markers[name] = (x, y)

    def npc(self, node_name, npc_id, x, y, rules=(), extra=""):
        text = f'[node name="{node_name}" parent="Actors" instance=ExtResource("npc")]\nposition = {v(x, y)}\nnpc_id = "{npc_id}"\n'
        if rules:
            text += f"dialogue_rules = {dicts(list(rules))}\n"
        self.actors.append(text + extra)

    def instance(self, node_name, path, x, y, extra=""):
        rid = self._ext("PackedScene", path, "i_" + pathlib.Path(path).stem)
        self.actors.append(f'[node name="{node_name}" parent="Actors" instance=ExtResource("{rid}")]\n'
                           f"position = {v(x, y)}\n{extra}")

    def sequence(self, node_name, scene_id, steps, requires=(), done_flag=""):
        self._ext("Script", "res://scripts/world/sequence.gd", "sequence")
        self.nodes.append(f'[node name="{node_name}" type="Node" parent="."]\nscript = ExtResource("sequence")\n'
                          f'scene_id = "{scene_id}"\nrequires_flags = {strs(requires)}\ndone_flag = "{done_flag}"\n'
                          f"steps = {dicts(steps)}\n")

    def trigger(self, node_name, scene_id, node, requires=()):
        self._ext("Script", "res://scripts/world/scene_trigger.gd", "trigger")
        self.nodes.append(f'[node name="{node_name}" type="Node" parent="."]\nscript = ExtResource("trigger")\n'
                          f'scene_id = "{scene_id}"\nnode = "{node}"\nrequires_flags = {strs(requires)}\n')

    def _area(self, node_name, script_rid, x, y, w, h, props):
        sid = f"shape_{node_name}"
        self.subs.append(f'[sub_resource type="RectangleShape2D" id="{sid}"]\nsize = {v(w, h)}\n')
        self.nodes.append(f'[node name="{node_name}" type="Area2D" parent="."]\nposition = {v(x, y)}\n'
                          f'script = ExtResource("{script_rid}")\n{props}')
        self.nodes.append(f'[node name="CollisionShape2D" type="CollisionShape2D" parent="{node_name}"]\n'
                          f'shape = SubResource("{sid}")\n')

    def zone(self, node_name, scene_id, node, x, y, w, h, done_flag="", requires=()):
        self._ext("Script", "res://scripts/world/trigger_zone.gd", "zone")
        self._area(node_name, "zone", x, y, w, h,
                   f'scene_id = "{scene_id}"\nnode = "{node}"\nrequires_flags = {strs(requires)}\ndone_flag = "{done_flag}"\n')

    def exit(self, node_name, x, y, w, h, level, spawn, requires, card="", card_only=False):
        self._ext("Script", "res://scripts/world/exit_zone.gd", "exit")
        self._area(node_name, "exit", x, y, w, h,
                   f'collision_layer = 0\ncollision_mask = 2\ntarget_level = "{level}"\ntarget_spawn = "{spawn}"\n'
                   f"requires_flags = {strs(requires)}\nunbuilt_card = {gd(card or 'To be continued.')}\n"
                   f"card_only = {gd(card_only)}\n")

    def interact(self, node_name, scene_id, node, x, y, w, h, requires=(), done_flag="", not_yet=""):
        self._ext("Script", "res://scripts/world/interact_point.gd", "interact")
        sid = f"shape_{node_name}"
        self.subs.append(f'[sub_resource type="RectangleShape2D" id="{sid}"]\nsize = {v(w, h)}\n')
        self.nodes.append(f'[node name="{node_name}" type="Node2D" parent="."]\nposition = {v(x, y)}\n'
                          f'script = ExtResource("interact")\nscene_id = "{scene_id}"\nnode = "{node}"\n'
                          f'requires_flags = {strs(requires)}\ndone_flag = "{done_flag}"\nnot_yet_node = "{not_yet}"\n')
        self.nodes.append(f'[node name="Area2D" type="Area2D" parent="{node_name}"]\ncollision_layer = 32\ncollision_mask = 0\n')
        self.nodes.append(f'[node name="CollisionShape2D" type="CollisionShape2D" parent="{node_name}/Area2D"]\n'
                          f'shape = SubResource("{sid}")\n')

    def tether(self, x, y, radius):
        self._ext("Script", "res://scripts/world/tether.gd", "tether")
        self.nodes.append(f'[node name="Tether" type="Node2D" parent="."]\nposition = {v(x, y)}\n'
                          f'script = ExtResource("tether")\nradius = {float(radius)}\n')

    def drift(self, node_name, texture, drift, z=0, alpha=1.0):
        self._ext("Script", "res://scripts/life/drifting_layer.gd", "drift")
        rid = self._ext("Texture2D", texture, "t_" + pathlib.Path(texture).stem)
        self.nodes.append(f'[node name="{node_name}" type="Sprite2D" parent="."]\n' + (f"z_index = {z}\n" if z else "")
                          + f"modulate = Color(1, 1, 1, {alpha})\ntexture_filter = 1\ntexture_repeat = 2\n"
                          f'texture = ExtResource("{rid}")\nregion_enabled = true\nregion_rect = Rect2(0, 0, 3000, 2200)\n'
                          f'script = ExtResource("drift")\ndrift = {v(*drift)}\n')

    def birds(self):
        self._ext("Script", "res://scripts/life/bird_flyover.gd", "birds")
        self._ext("SpriteFrames", "res://assets/life/bird.tres", "bird")
        self.nodes.append('[node name="BirdFlyover" type="Node2D" parent="."]\nscript = ExtResource("birds")\n'
                          'bird_frames = ExtResource("bird")\n')

    def write(self, player_at):
        out = [f"[gd_scene load_steps={len(self.ext) + len(self.subs) + 1} format=3]", ""]
        out += [f'[ext_resource type="{k}" path="{p}" id="{i}"]' for k, p, i in self.ext] + [""]
        out += self.subs
        out.append(f'[node name="{self.root}" type="Node2D"]\n')
        out += self.nodes
        out.append('[node name="Markers" type="Node2D" parent="."]\n')
        for n, (x, y) in self.markers.items():
            out.append(f'[node name="{n}" type="Marker2D" parent="Markers"]\nposition = {v(x, y)}\n')
        out.append('[node name="Actors" type="Node2D" parent="."]\ny_sort_enabled = true\n')
        out.append(f'[node name="Player" parent="Actors" instance=ExtResource("player")]\nposition = {v(*player_at)}\n')
        out += self.actors
        path = ROOT / "scenes" / "world" / f"{self.name}.tscn"
        path.write_text("\n".join(out))
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_props.py"), "place", self.name], check=True)
        print(f"-> {path.relative_to(ROOT)}")


YARD_GROUND = "res://assets/tilesets/winterfell_yard_ground.png"
DAY = "Color(1, 0.98, 0.95, 1)"


def yard(name, light=DAY):
    lvl = Level(name, YARD_GROUND, light, south_gap=96)
    lvl.drift("CloudShadows", "res://assets/fx/cloud_shadows.png", (-9, -3))
    lvl.birds()
    return lvl


# --- scene 5 --------------------------------------------------------------------------
def arrival():
    s = "s1_05_the_arrival"
    lvl = yard("winterfell_yard_arrival", "Color(1, 0.95, 0.88, 1)")
    lvl.marker("honour_guard_left", -100, 20)
    lvl.tether(-100, 20, 64)  # "cannot move more than two tiles"
    # the household at the keep door, the king's party coming in at the south gate
    lvl.npc("Eddard", "eddard_stark", 0, -196)
    lvl.npc("Catelyn", "catelyn_stark", 40, -194)
    lvl.npc("Robb", "robb_stark", -40, -192)
    lvl.npc("Bran", "bran_stark", 72, -188)
    lvl.npc("Jon", "jon_snow", -150, -200)
    lvl.npc("Hune", "hune", -100, -60)
    lvl.npc("Cley", "cley", -100, 80)
    lvl.npc("Wells", "wells", -48, 40)
    lvl.npc("Robert", "robert_baratheon", 0, 330)
    lvl.npc("Jaime", "jaime_lannister", 40, 300)
    lvl.npc("Joffrey", "joffrey_baratheon", -40, 300)
    lvl.npc("Tyrion", "tyrion_lannister", 120, 290)
    lvl.npc("Sandor", "sandor_clegane", -120, 300)
    kneel = [{"hide": "standing"}, {"show": "kneeling"}, {"look": "res://assets/life/torren_kneel.tres"}, {"lock": True}]
    rise = [{"show": "standing"}, {"hide": "kneeling"}, {"look": TORREN}, {"lock": False}]
    lvl.sequence("Arrival", s, [
        {"play": "n1"},   # n1 -> n2 -> n3: Hune, the riders, Ser Emmon's needling

        {"focus": "../Actors/Robert", "time": 1.5},
        {"move": "../Actors/Robert", "to": (0, -130), "time": 7.0, "wait_for_it": False},
        {"move": "../Actors/Joffrey", "to": (-40, 120), "time": 6.0, "wait_for_it": False},
        {"move": "../Actors/Jaime", "to": (40, 110), "time": 6.0, "wait_for_it": False},
        {"move": "../Actors/Sandor", "to": (-110, 180), "time": 6.5, "wait_for_it": False},
        {"move": "../Actors/Tyrion", "to": (130, 200), "time": 7.5, "wait_for_it": False},
        {"wait": 4.0}, *kneel, {"wait": 3.2},
        {"play": "n10"},
        {"focus": "", "time": 1.2}, *rise,
        {"play": "n20"},
        # "Robert goes straight to the crypts"
        {"move": "../Actors/Robert", "to": (0, -240), "time": 3.0, "wait_for_it": False},
        {"move": "../Actors/Eddard", "to": (10, -250), "time": 3.0},
        {"fade": True}, {"goto": "winterfell_crypts", "spawn": "stair_head"},
    ], requires=["act1_found_pups"], done_flag="act1_arrival_done")
    lvl.write((-100, 20))


# --- scene 6 --------------------------------------------------------------------------
def crypts():
    s = "s1_06_the_crypts"
    lvl = Level("winterfell_crypts", "res://assets/tilesets/winterfell_crypts_ground.png",
                "Color(0.34, 0.33, 0.42, 1)", bounds=(-150, 150, -330, 360))
    lvl.marker("stair_head", 0, -230)
    lvl.tether(0, -230, 4)
    lvl._ext("Script", "res://scripts/world/flag_move.gd", "flagmove")
    lvl.node('[node name="StepCloser" type="Node" parent="."]\nscript = ExtResource("flagmove")\n'
             'target = NodePath("../Tether")\n'
             'moves = {"act1_heard_crypt_1": Vector2(0, 40), "act1_heard_crypt_2": Vector2(0, 40)}\n')
    # warm light where there is fire: Torren's torch and the king's, far down the aisle
    lvl.subs.append('[sub_resource type="Gradient" id="glow"]\ncolors = PackedColorArray(1, 0.8, 0.5, 1, 1, 0.8, 0.5, 0)\n')
    lvl.subs.append('[sub_resource type="GradientTexture2D" id="glow_tex"]\ngradient = SubResource("glow")\n'
                    'width = 256\nheight = 256\nfill = 1\nfill_from = Vector2(0.5, 0.5)\nfill_to = Vector2(1, 0.5)\n')
    lvl.node('[node name="KingsTorch" type="PointLight2D" parent="."]\nposition = Vector2(20, 210)\n'
             'energy = 1.1\ntexture = SubResource("glow_tex")\ntexture_scale = 1.6\n')
    lvl.npc("Robert", "robert_baratheon", -26, 238)
    lvl.npc("Eddard", "eddard_stark", 30, 236)
    lvl.sequence("Torchlight", s, [
        {"lock": True}, {"look": "res://assets/life/torren_torch.tres"}, {"play": "n1"},
        {"wait": 1.0}, {"fade": True}, {"goto": "winterfell_great_hall", "spawn": "lower_bench"},
    ], requires=["act1_king_arrived"], done_flag="act1_crypts_done")
    lvl.write((0, -230))
    # the torch's own light rides on the player
    path = ROOT / "scenes" / "world" / "winterfell_crypts.tscn"
    text = path.read_text()
    text += ('\n[node name="Torch" type="PointLight2D" parent="Actors/Player"]\nposition = Vector2(8, -40)\n'
             'energy = 1.2\ntexture = SubResource("glow_tex")\ntexture_scale = 1.3\n')
    path.write_text(text)


# --- scene 7 --------------------------------------------------------------------------
def great_hall():
    s = "s1_07_the_feast"
    lvl = Level("winterfell_great_hall", "res://assets/tilesets/winterfell_great_hall_ground.png",
                "Color(1, 0.86, 0.68, 1)", camera="Rect2(-640, -380, 1280, 750)",
                bounds=(-610, 610, -214, 350), south_gap=96)
    lvl.marker("lower_bench", -300, 290)
    lvl.trigger("Intro", s, "n1", requires=["!act1_entered_feast"])
    # the high table: the king, Lord Stark, the prince; Jon apart with his uncle; the Imp
    # behind the high table, drawn over it (z 1) so the table's chairs don't hide them
    for n, i, x in (("Robert", "robert_baratheon", -40), ("Eddard", "eddard_stark", 20), ("Joffrey", "joffrey_baratheon", 70)):
        lvl.npc(n, i, x, -248, extra="z_index = 1\n")
    lvl.npc("Jon", "jon_snow", -470, 110)
    lvl.npc("Benjen", "benjen_stark", -430, 116)
    lvl.npc("Tyrion", "tyrion_lannister", 420, -60)
    lvl.npc("Hune", "hune", -210, 300, [{"requires_flags": ["!act1_feast_hune"], "scene_id": s, "node": "n10"}])
    lvl.npc("Jory", "jory_cassel", -120, 262, [{"requires_flags": ["!act1_feast_jory"], "scene_id": s, "node": "n20"}])
    lvl.npc("Wells", "wells", 240, 252, [{"requires_flags": ["act1_met_wells", "!act1_feast_wells"], "scene_id": s, "node": "n30"}])
    lvl.npc("Cley", "cley", -360, 250)
    # the serving girl crosses the hall on her route; the glance only if Torren faces her
    lvl._ext("Script", "res://scripts/world/glance_zone.gd", "glance")
    lvl.subs.append('[sub_resource type="CircleShape2D" id="glance_shape"]\nradius = 64.0\n')
    lvl.instance("ServingGirl", "res://scenes/life/serving_girl.tscn", -520, 40,
                 'points = PackedVector2Array(0, 0, 1040, 0)\nspeed = 30.0\npause_range = Vector2(2, 5)\n')
    lvl.actors.append('[node name="Glance" type="Area2D" parent="Actors/ServingGirl"]\nscript = ExtResource("glance")\n'
                      f'scene_id = "{s}"\nnode = "n40"\ndone_flag = "act1_encounter_feast"\n')
    lvl.actors.append('[node name="CollisionShape2D" type="CollisionShape2D" parent="Actors/ServingGirl/Glance"]\n'
                      'shape = SubResource("glance_shape")\n')
    lvl.zone("KitchenDoor", s, "n42", 560, 40, 60, 90, done_flag="act1_followed_her", requires=["act1_encounter_feast"])
    # down by Jon and his uncle - clear of the serving girl's route (y 40)
    lvl.zone("FarEnd", s, "n50", -440, 150, 220, 100, done_flag="act1_feast_observed")
    lvl.exit("ExitSouth", 0, 330, 96, 24, "winterfell_yard_visit", "training_yard_gate", ["act1_entered_feast"])
    lvl.write((-300, 290))


# --- scene 8 --------------------------------------------------------------------------
def visit():
    s = "s1_08_days_of_feasting"
    lvl = yard("winterfell_yard_visit")
    lvl.marker("training_yard_gate", 0, 300)
    lvl.trigger("Intro", s, "n1", requires=["act1_entered_feast", "!act1_visit_arrived"])
    lvl.npc("Cley", "cley", 50, 290)
    lvl.npc("Robb", "robb_stark", -300, 170, [{"requires_flags": ["!act1_talked_robb_yard"], "scene_id": s, "node": "n10"}])
    lvl.npc("Jon", "jon_snow", -380, 190, [{"requires_flags": ["!act1_talked_to_jon"], "scene_id": s, "node": "n20"}])
    lvl.npc("Tyrion", "tyrion_lannister", 300, 130, [{"requires_flags": ["!act1_met_tyrion"], "scene_id": s, "node": "n30"}])
    lvl.npc("Benjen", "benjen_stark", 150, -170, [{"requires_flags": ["!act1_met_benjen"], "scene_id": s, "node": "n40"}])
    lvl.sequence("NinthDay", s, [
        {"await_flag": "act1_talked_robb_yard"}, {"wait": 1.0}, {"play": "n50"},
        {"wait": 0.5}, {"fade": True}, {"goto": "winterfell_yard_fall", "spawn": "armoury_door"},
    ], requires=["act1_entered_feast"], done_flag="act1_visit_done")
    lvl.exit("ExitSouth", 0, 360, 96, 24, "winterfell_yard_fall", "armoury_door", ["act1_explored_during_visit"])
    lvl.write((0, 300))


# --- scene 9 --------------------------------------------------------------------------
def fall():
    s = "s1_09_the_fall"
    lvl = yard("winterfell_yard_fall", "Color(0.97, 0.97, 1, 1)")
    lvl.marker("armoury_door", -470, 150)
    lvl.npc("Hune", "hune", -420, 120)
    lvl.npc("BranFallen", "bran_stark", 560, -170, extra='rotation = 1.5708\nvisible = false\n')
    lvl.npc("Catelyn", "catelyn_stark", 470, -120, extra='visible = false\n')
    lvl.zone("LookUp", s, "n10", 470, -150, 360, 200, done_flag="act1_saw_bran_climbing")
    lvl.interact("Shutter", s, "n12", 600, -226, 90, 40, done_flag="act1_noticed_shutter")
    # the lances go to the training yard, out through the south gate: the fall happens
    # on the way, behind him
    lvl.zone("LancesDown", s, "n20", 0, 250, 220, 120, done_flag="act1_bran_fell")
    lvl.sequence("TheFall", s, [
        {"play": "n1"}, {"look": "res://assets/life/torren_lances.tres"},
        {"await_flag": "act1_bran_fell"}, {"hide": "climber"},
        {"fade": True},
        {"look": TORREN},
        {"show": "fallen"},
        {"place_player": (520, -160)}, {"lock": True},
        {"fade": False},
        {"play": "n22"},
        {"wait": 1.0}, {"fade": True}, {"goto": "winterfell_godswood", "spawn": "yard_gate"},
    ], requires=["act1_explored_during_visit"], done_flag="act1_fall_done")
    lvl.write((-470, 150))
    # the fallen boy and his mother join the "fallen" group so the sequence can show them
    path = ROOT / "scenes" / "world" / "winterfell_yard_fall.tscn"
    text = path.read_text()
    for n in ("BranFallen", "Catelyn"):
        text = text.replace(f'[node name="{n}" parent="Actors" instance=', f'[node name="{n}" parent="Actors" groups=["fallen"] instance=')
    path.write_text(text)


# --- scene 10 -------------------------------------------------------------------------
def godswood():
    s = "s1_10_aftermath"
    lvl = Level("winterfell_godswood", "res://assets/tilesets/winterfell_godswood_ground.png",
                "Color(0.82, 0.8, 0.9, 1)", south_gap=0)
    lvl.marker("yard_gate", 0, 330)
    lvl.drift("CloudShadows", "res://assets/fx/cloud_shadows.png", (-6, -2), alpha=0.7)
    lvl.birds()
    lvl.npc("Cley", "cley", 50, 310)
    lvl.sequence("Recalled", s, [{"lock": True}, {"play": "n1"}, {"lock": False}],
                 requires=["act1_bran_fell"], done_flag="act1_recalled")
    lvl.zone("HeartTree", s, "n20", 0, -60, 260, 140, done_flag="act1_godswood", requires=["act1_aftermath"])
    lvl.sequence("Onward", s, [
        {"await_flag": "act1_godswood"}, {"wait": 1.5}, {"fade": True},
        {"goto": "winterfell_yard_departure", "spawn": "gate"},
    ], requires=["act1_bran_fell"], done_flag="act1_godswood_done")
    lvl.write((0, 330))


# --- scene 11 -------------------------------------------------------------------------
def departure():
    s = "s1_11_the_departure"
    lvl = yard("winterfell_yard_departure", "Color(0.9, 0.9, 1, 1)")
    lvl.marker("gate", -60, 250)
    lvl.npc("Hune", "hune", -140, 250)
    lvl.npc("Girl", "serving_girl", -20, 246, extra='visible = false\n')
    lvl.sequence("Departure", s, [
        # n1 -> n2 (the trunk) -> n3 -> n5 -> n6: the girl is in the press from the start
        {"lock": True}, {"show": "trunk_girl"}, {"play": "n1"},
        {"hide": "trunk_girl"}, {"wait": 1.0},
        {"fade": True}, {"goto": "winterfell_walls", "spawn": "south_rampart"},
    ], requires=["act1_aftermath"], done_flag="act1_departure_done")
    lvl.write((-60, 250))
    path = ROOT / "scenes" / "world" / "winterfell_yard_departure.tscn"
    text = path.read_text().replace('[node name="Girl" parent="Actors" instance=',
                                    '[node name="Girl" parent="Actors" groups=["trunk_girl"] instance=')
    text += ('\n[node name="Trunk" type="AnimatedSprite2D" parent="Actors/Girl"]\ntexture_filter = 1\n'
             'sprite_frames = ExtResource("i_nyra_trunk")\nanimation = &"idle"\nautoplay = "idle"\n'
             'offset = Vector2(0, -24)\n')
    text = text.replace('[ext_resource type="PackedScene" path="res://scenes/actors/NPC.tscn" id="npc"]',
                        '[ext_resource type="PackedScene" path="res://scenes/actors/NPC.tscn" id="npc"]\n'
                        '[ext_resource type="SpriteFrames" path="res://assets/life/nyra_trunk.tres" id="i_nyra_trunk"]')
    path.write_text(text)


# --- scene 12 -------------------------------------------------------------------------
def walls():
    s = "s1_12_winter_is_coming"
    lvl = Level("winterfell_walls", "res://assets/tilesets/winterfell_walls_ground.png",
                "Color(0.86, 0.88, 1, 1)", camera=None, bounds=(-1200, 1200, -60, 60))
    lvl.marker("south_rampart", 0, 20)
    lvl.drift("Snow", "res://assets/fx/snow_far.png", (3, -12), z=60)
    lvl.npc("Cley", "cley", 60, 18)
    lvl.sequence("WinterIsComing", s, [
        {"lock": True}, {"wait": 1.0}, {"play": "n1"},
        {"zoom": 0.5, "time": 9.0},
        {"card": "End of Act One.\n\nAct Two is still being built."},
    ], requires=["act1_encounter_departure"], done_flag="act1_walls_done")
    lvl.write((0, 20))


LEVELS = {"winterfell_yard_arrival": arrival, "winterfell_crypts": crypts, "winterfell_great_hall": great_hall,
          "winterfell_yard_visit": visit, "winterfell_yard_fall": fall, "winterfell_godswood": godswood,
          "winterfell_yard_departure": departure, "winterfell_walls": walls}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("level", nargs="*", choices=sorted(LEVELS) + [[]])
    names = ap.parse_args().level or list(LEVELS)
    for n in names:
        LEVELS[n]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
