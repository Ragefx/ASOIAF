# Technical Design Document

Godot **4.x** (4.2+). GDScript. 2D top-down. Target: desktop (Windows/Linux/macOS).

---

## 1. Rendering & Pixel Discipline

| Setting | Value | Why |
|---|---|---|
| Base viewport | 384 × 216 | 16:9, divides cleanly, fits 24 × 13.5 tiles at 16px |
| Window override | 1536 × 864 (×4) | Integer scale only |
| Stretch mode | `viewport` | Renders at base res, scales the whole frame |
| Stretch aspect | `keep` | No letterbox distortion |
| Integer scaling | on | Never a half-pixel |
| Texture filter | `Nearest` (project default) | Set in Rendering → Textures → Canvas Textures |
| Mipmaps | off | |
| Snap 2D transforms to pixel | on | Kills sub-pixel shimmer on the camera |
| Snap 2D vertices to pixel | on | |

**Tile size: 16 px.** Character sprites are 16×24 (a 16px footprint with headroom), giving the
Zelda-like read where characters are slightly taller than one tile. Larger NPCs (the Hound,
mounted knights, direwolves) get 32×32 frames on the same 16px footprint.

Import defaults for every sprite: Filter **off**, Mipmaps **off**, Fix Alpha Border **on**.
Store this as a `.godot` import preset so it is not re-set per file.

### Camera
`Camera2D` child of the player with `position_smoothing_enabled = true`,
`position_smoothing_speed = 8.0`, and limits driven by the level's TileMap bounds. Because
"Snap 2D Transforms to Pixel" is on, smoothing never produces a blurred frame.

---

## 2. Movement

Free-roaming, **not grid-locked**.

- `CharacterBody2D` + `move_and_slide()`.
- Input: WASD / arrows / left stick, plus click-to-move via a `NavigationAgent2D` fallback.
- Speed: 60 px/s walk, 95 px/s run (hold Shift). Diagonals normalized.
- **4-directional facing.** The animation direction is derived from the *dominant axis* of the
  input vector, and it is sticky: a diagonal keeps the last committed facing rather than
  flickering between two. See `scripts/actors/player.gd::_resolve_facing()`.
- Collision: a small `CapsuleShape2D` at the character's feet (roughly 12 × 6 px), not the sprite
  bounds. This is what makes top-down movement feel right around furniture and doorframes.

### Y-sorting
The world `TileMap` and all actors sit under one `Node2D` with `y_sort_enabled = true`. Actors set
their `Sprite2D` offset so the *feet* are the sort origin.

---

## 3. Scene Graph

```
Main (Node)
├── World (Node2D, y_sort)          ← the current level is instanced here
│   ├── TileMap                     (layers: Ground, Detail, Overhead, Collision)
│   ├── Actors (Node2D, y_sort)
│   │   ├── Player
│   │   └── NPC × n
│   ├── Triggers (Node2D)           Area2D volumes that fire scene events
│   └── Camera2D
├── UILayer (CanvasLayer)
│   ├── HUD
│   ├── DialogueUI
│   ├── QuestLog
│   └── PauseMenu
└── TransitionLayer (CanvasLayer)   fade-to-black, act cards
```

`Main` is the only persistent scene. Levels are instanced into `World` and freed on transition, so
autoload state is the single source of truth for anything that must survive a level change.

---

## 4. Autoloads (Singletons)

Registered in `project.godot` in this order — later ones may depend on earlier ones.

| Order | Name | File | Responsibility |
|---|---|---|---|
| 1 | `GameManager` | `autoload/game_manager.gd` | Flags, act progression, traits, relationships. The state of record. |
| 2 | `SaveSystem` | `autoload/save_system.gd` | JSON save/load, slots, versioning |
| 3 | `DialogueSystem` | `autoload/dialogue_system.gd` | Loads act files, walks dialogue graphs, emits line/choice signals |
| 4 | `QuestSystem` | `autoload/quest_system.gd` | Objectives, completion, journal |
| 5 | `SceneDirector` | `autoload/scene_director.gd` | Level transitions, act boundaries, cutscene sequencing |
| 6 | `AudioManager` | `autoload/audio_manager.gd` | Music beds, crossfades, SFX pool |

### 4.1 GameManager

The critical rule: **nothing else owns persistent state.** UI reads from it, systems write to it
through methods (never by mutating the dictionary directly), and it emits a signal on every change
so the UI never has to poll.

```gdscript
signal flag_changed(flag: String, value: bool)
signal trait_changed(trait_name: String, value: int)
signal relationship_changed(npc_id: String, value: int)
signal act_changed(act_id: String)

var flags: Dictionary = {}          # "bran_fell": true
var traits: Dictionary = {}         # "bold": 3, "cautious": -1
var relationships: Dictionary = {}  # "robb_stark": 4
var current_act: String = "act_1"
var current_pov: String = "torren"
```

**Flags** are the join between narrative and systems. A flag is set by a dialogue node, a quest
completion, or a trigger volume; it is read by dialogue conditions, NPC availability, and quest
prerequisites. Naming convention: `act<N>_<subject>_<verb>` — `act1_bran_fell`,
`act2_nyra_overheard_ledger`, `act4_ned_executed`. Flags are never deleted, only set.

**Traits** are a signed integer per axis. Choices nudge them. They gate flavour dialogue and a few
optional scenes; they never gate a canonical event.

| Axis | −  | + |
|---|---|---|
| `bold` | cautious | reckless |
| `honest` | guarded | plainspoken |
| `merciful` | hard | kind |
| `loyal` | self-serving | devoted |

**Relationships** are −10..+10 per NPC id.

### 4.2 DialogueSystem

JSON-driven, graph-walking, with branching choices and flag conditions.

```gdscript
signal dialogue_started(scene_id: String)
signal line_shown(speaker: String, portrait: String, text: String)
signal choices_offered(choices: Array)
signal dialogue_ended(scene_id: String)

func start_scene(act_id: String, scene_id: String) -> void
func advance() -> void                 # next node, or close if terminal
func choose(index: int) -> void        # apply effects, jump to target
```

Act files are loaded lazily and cached: `res://data/scenes/<act_id>.json`. On `start_scene` the
system resolves the scene's `dialogue.start` node and walks it. Every node may carry `sets_flags`,
`traits`, and `relationship` effects, which are applied *on exit* of the node — so a choice's
effects land exactly once, even if the player backs out of the UI.

**Condition evaluation.** `requires_flags` is an AND-list; a leading `!` negates. Choices whose
conditions fail are filtered out before `choices_offered` is emitted, so the UI never needs to know
about conditions. If filtering leaves zero choices, the node's `fallback` is used.

**Text tokens.** `{knight}`, `{girl}`, `{house}` are substituted at display time from
`data/npcs/protagonists.json`. This is why renaming a protagonist is a one-file edit.

### 4.3 QuestSystem

A quest is a list of ordered or unordered objectives. Objectives complete on a flag being set, so
quests never need their own event plumbing — they subscribe to `GameManager.flag_changed`.

```json
{
  "id": "q_act1_feast",
  "title": "The King's Welcome",
  "act": "act_1",
  "ordered": true,
  "objectives": [
    { "id": "o1", "text": "Take your place in the Great Hall", "flag": "act1_entered_feast" },
    { "id": "o2", "text": "Serve at the high table", "flag": "act1_served_high_table" }
  ],
  "completion_flag": "act1_feast_complete"
}
```

### 4.4 SceneDirector

Owns the *only* code path that changes what is on screen: `goto_level()`, `play_cutscene()`,
`begin_act()`. It fades out, frees the old level, instances the new one, places the player at a
named spawn `Marker2D`, fades in, and then fires any `on_enter` scene from the act file. Act
boundaries additionally show an act card (title, POV, date) and force an autosave.

### 4.5 SaveSystem

JSON, human-readable, multiple slots at `user://saves/slot_<n>.json`.

```json
{
  "version": 1,
  "saved_at": "298-08-14",
  "act": "act_3", "pov": "torren", "level": "winterfell_yard", "spawn": "gate",
  "flags": {}, "traits": {}, "relationships": {},
  "quests": { "active": [], "complete": [] },
  "player": { "hp": 34, "max_hp": 40, "equipment": {} }
}
```

`version` is checked on load; a migration table handles older saves rather than rejecting them.
Autosave fires on act change and level transition, into a reserved slot 0.

---

## 5. NPC System

`scenes/actors/NPC.tscn` — `CharacterBody2D` + `AnimatedSprite2D` + `Area2D` interaction zone.

```gdscript
@export var npc_id: String            # "robb_stark"
@export var display_name: String
@export var portrait: Texture2D
@export var default_act: String
@export var default_scene: String     # dialogue entry point
@export var wander: bool = false
```

NPC definitions live in `data/npcs/npcs.json` (id, name, portrait path, house, faction, notes on
voice) so writers can add a character without touching a scene. The NPC node resolves its data by
`npc_id` at `_ready()`.

**Dialogue routing.** An NPC's current dialogue entry point is chosen by walking a prioritized list
of `{ requires_flags, scene_id }` rules from most specific to least. This is how the same Jory
Cassel can say something different before and after Bran's fall without a wall of `if`s.

**Relationships.** Talking, choices, and quest outcomes call
`GameManager.adjust_relationship(npc_id, delta)`. NPCs read their own value to pick greeting lines.

---

## 6. Combat

**Real-time, light RPG.** Not turn-based. The reference feel is *Hyper Light Drifter* slowed down
and given weight — think three-hit commitment, not twitch cancels.

### Actor model
`scripts/combat/combat_actor.gd` is shared by the player and enemies:

- `hp`, `max_hp`, `stamina`, `armor`, `poise`
- State machine: `IDLE → MOVE → ATTACK → RECOVER`, plus `HURT`, `DODGE`, `DEAD`
- `Hitbox` (Area2D, enabled only on active attack frames) and `Hurtbox` (Area2D, always on)

### Player kit
| Action | Input | Notes |
|---|---|---|
| Light attack | LMB / X | 3-hit chain, 0.35 s window to continue |
| Heavy attack | Hold LMB | Breaks shields, costs stamina, slow recovery |
| Shield / block | RMB | Reduces damage by `armor`, drains stamina on hit |
| Dodge roll | Space | 0.2 s i-frames, costs stamina |
| Interact | E | Context-sensitive; shares the button with dialogue advance |

Damage: `max(1, attack + weapon - target.armor)` with a ±10% roll. No crits — the fantasy is a
soldier in a line, not a rogue.

### Progression
Deliberately shallow. Torren gains `max_hp` and one of three **battle traits** at each act
boundary, chosen by the player. Equipment is narrative (Blackpool mail → a dead man's better
hauberk), not a loot treadmill. Nyra has no combat kit; her Act 2/4 threat scenes are stealth and
dialogue, resolved by `detection` rather than `hp`.

### Battle scenes (Act 5)
Whispering Wood and the Battle of the Camps are **scripted arena waves**, not open combat: a fixed
sequence of enemy groups with narrative beats between them, driven by `SceneDirector` firing
dialogue nodes at wave boundaries. This keeps the canonical outcome fixed while letting the player
actually fight.

---

## 7. Data Contracts

Everything narrative is JSON under `data/`, validated by `tools/validate_data.py` (runs without
Godot, so it belongs in CI):

- Every `next` and choice target resolves to a node in the same scene.
- Every `requires_flags` entry is set *somewhere* in the act graph or an earlier act.
- Every quest objective flag exists in a scene file.
- Every `speaker` resolves to an NPC id or a protagonist token.
- No unreachable dialogue nodes.

See [`SCENE_FILE_FORMAT.md`](SCENE_FILE_FORMAT.md) for the full schema.

---

## 8. Directory Conventions

| Path | Contains |
|---|---|
| `autoload/` | Singletons only. No node logic. |
| `scripts/actors/` | Player, NPC, actor stats |
| `scripts/combat/` | Combat actor, hitbox, hurtbox, enemy AI, wave director |
| `scripts/systems/` | Interaction, triggers, spawn markers |
| `scripts/ui/` | Dialogue UI, HUD, quest log, menus |
| `scenes/world/` | One `.tscn` per level, named `<location>_<area>.tscn` |
| `assets/` | Imported art/audio, mirrored by source pack in `assets/ATTRIBUTION.md` |

Naming: files `snake_case`, classes `PascalCase`, signals past-tense (`dialogue_ended`), flags
`snake_case` with an act prefix.

---

## 9. Performance Notes

Nothing here is expensive, but two things will bite if ignored:

1. **Y-sorting a large TileMap.** Keep the overhead layer as a *separate* non-y-sorted TileMap
   drawn above actors, rather than y-sorting thousands of tiles.
2. **Dialogue file size.** Act files are cached after first load and never re-parsed. Do not parse
   JSON inside `_process`.

---

## 10. Open Technical Questions

- **Click-to-move pathing** needs a baked `NavigationRegion2D` per level; the alternative is to
  ship keyboard-only for the first playable and add it in a later pass. *Recommendation: ship
  keyboard/gamepad first, it removes a whole class of level-authoring work.*
- **Localization** is not designed for. If it is ever wanted, dialogue text must move to keys with
  a CSV table, which is a large retrofit. Decide before Act 3 is written, not after.
- **Controller glyph swapping** in the dialogue UI is unimplemented.
