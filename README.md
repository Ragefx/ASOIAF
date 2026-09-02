# A Song of Ice and Fire — Pixel Art RPG

A top-down, pixel-art RPG built in **Godot 4.x** that retells the events of *A Game of Thrones*
(Book 1) through two original playable characters who witness canonical events firsthand.

> Fan project. Non-commercial. All rights to *A Song of Ice and Fire* belong to George R. R. Martin.

---

## The Pitch

Two protagonists. One war. Neither of them is a Stark, a Lannister, or a Targaryen — they are the
people standing three feet behind them.

| | **Ser Torren Slate** | **Nyra** |
|---|---|---|
| Age | 23 | 18 |
| Role | Household knight, House Slate of Blackpool | Servant in the queen's household, Red Keep |
| POV Acts | 1, 3, 5 | 2, 4 |
| Arc | Earn a name for a house nobody remembers | Survive a court that eats people like her |

*(Names are the recommended defaults — see [`docs/CHARACTER_BIBLE.md`](docs/CHARACTER_BIBLE.md)
for alternates and the reasoning. They are defined in one place, `data/npcs/protagonists.json`,
so changing them is a one-file edit.)*

## Chapter 1 — Structure

Chapter 1 covers Book 1's timeline: **Spring to Autumn, 298 AC** (~7 months), in five acts that
alternate POV.

| Act | Title | POV | Location | Canonical spine |
|-----|-------|-----|----------|-----------------|
| 1 | The Fall | Torren | Winterfell | Robert's arrival, the feast, Bran's fall |
| 2 | The Investigation | Nyra | Red Keep | Ned as Hand, the bastards, Robert's death |
| 3 | The Young Wolf | Torren | Winterfell | Robb calls the banners, the host rides south |
| 4 | The Traitor's Daughter | Nyra | King's Landing | Ned's arrest, the Sept of Baelor |
| 5 | The Sword in the Morning | Torren | Riverlands | Whispering Wood, Battle of the Camps, the crowning |

The two protagonists pass each other **twice** in Act 1 and do not meet again in Chapter 1.
See [`docs/CHAPTER1_PERSPECTIVE_MAP.md`](docs/CHAPTER1_PERSPECTIVE_MAP.md).

## Design Principles

1. **Direct witness, never hearsay.** If the player is told about an event instead of seeing it,
   the scene is wrong. Torren fights in real battles; Nyra watches Ned die from the crowd.
2. **Canon is fixed; the player's relationship to it is not.** Choices move personality traits and
   NPC relationships. They never change what happens to Ned Stark.
3. **Original dialogue.** Written in the characters' voices. No verbatim book quotes.
4. **Scope discipline.** Three location clusters in Chapter 1. No Essos, no Wall, no Riverlands
   interior beyond the marching camp.

## Repository Layout

```
project.godot            Godot 4.x project file
autoload/                Singletons: GameManager, DialogueSystem, QuestSystem, SaveSystem, SceneDirector
scripts/                 Gameplay code (actors, combat, systems, UI)
scenes/                  Godot .tscn scenes
data/scenes/             Act scene files — dialogue, stage directions, choices, flags (JSON)
data/npcs/               NPC + protagonist definitions
data/quests/             Quest and objective definitions
docs/                    Design documentation (start here)
tools/                   Validation scripts
```

## Documentation

| Document | What it is |
|---|---|
| [`docs/TECHNICAL_DESIGN.md`](docs/TECHNICAL_DESIGN.md) | Godot architecture, systems, data contracts |
| [`docs/BOOK1_TIMELINE.md`](docs/BOOK1_TIMELINE.md) | Month-by-month canonical events, Spring–Autumn 298 AC |
| [`docs/CHAPTER1_PERSPECTIVE_MAP.md`](docs/CHAPTER1_PERSPECTIVE_MAP.md) | Which protagonist witnesses what, act by act |
| [`docs/CHARACTER_BIBLE.md`](docs/CHARACTER_BIBLE.md) | Protagonist naming, voice, traits, the romance arc |
| [`docs/SCENE_FILE_FORMAT.md`](docs/SCENE_FILE_FORMAT.md) | The JSON schema every act file conforms to |
| [`docs/ASSET_SOURCING.md`](docs/ASSET_SOURCING.md) | Specific free packs, licensing rules, AI generation pipeline |

## Getting Started

```bash
# Validate all scene/quest/NPC data (no Godot required)
python3 tools/validate_data.py

# Open in Godot 4.x
godot --path . --editor
```

## Status

- [x] Technical design document
- [x] Book 1 timeline
- [x] Chapter 1 perspective map
- [x] Act 1–5 scene files (dialogue, choices, flags)
- [x] Character naming + bible
- [x] Godot project scaffold, autoloads, core systems
- [x] Asset sourcing plan with named packs
- [ ] Art assets imported
- [ ] Tilemaps built (Winterfell, Red Keep, Riverlands camp)
- [ ] Combat encounter tuning
- [ ] Audio pass
