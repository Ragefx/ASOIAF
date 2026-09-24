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
| Age | 20 | 20 |
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

> **Scope decision (2026-09-24):** the first release runs **up to Ned Stark's execution** — Acts 1–4.
> Act 5 happens after Ned's death and is out of scope for now; its scene data stays in the repo but
> isn't being built. Whether both original protagonists stay in the first release (the user described
> "a made-up character, with more to follow") is still unconfirmed.
>
> **Art direction:** the confirmed target look is `docs/reference/target_screenshot.webp` —
> see `docs/STYLE_GUIDE.md` §0 for the measured spec. Pokémon *look* only; gameplay unchanged.
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

## Playing / testing the opening scenes

Act 1 opens in Winterfell's training yard: finish your drill on the straw man (left mouse),
then talk to Ser Cley at the fence (E) for the news that the king is coming, then take the
track south into the castle yard.

Scene 2, Preparing for a King: Winterfell is being scrubbed for the royal visit. Report to
Ser Rodrik at the keep door, see to the stables (E at the stable doors), and - optionally -
talk to Jory about the honour guard, the stable hand, and Hodor. Then take the track south.

Scene 3, A Deserter's Head: three days later, a clearing in the Wolfswood under summer snow.
Serjeant Hune briefs you; speak with Jory, Theon, Robb and Cley if you like, then take your place
at the left of the ring (E). The camera watches Bran, not the block. The road home runs east.

Scene 4, Six Pups and a Seventh: the column has stopped on the kingsroad. Walk up the road to
find out why (no button - you find it). A sixth pup sits alone in the trees east of the road,
and only a player who leaves the road finds it. The column rides on north, home.

Scenes 5 to 12 finish the act:
- **The King Comes North** - held in the honour guard line (you can shuffle, not leave), the
  king rides up the yard and the household kneels.
- **Torchlight** - the crypts; you hold a torch at the stair head and may step closer twice.
- **The Feast** - free roam of the great hall; face the serving girl as she crosses and you
  meet her eyes (the first brief encounter).
- **Days of Feasting** - the yard during the visit: Robb, Jon, Tyrion, Benjen.
- **The Fall** - carry the lances to the south gate; look up at the Broken Tower if you like.
- **Aftermath** - the godswood and the heart tree.
- **The Departure** and **Winter Is Coming** - the trunk, the column leaving, the wall.

The later levels are generated from data: `tools/build_act1_levels.py` (people, scripted
beats as `scripts/world/sequence.gd` steps) plus `tools/build_props.py place <level>`.

`tools/godot/playtest_act1_opening.gd` plays the whole act automatically and screenshots each beat:

    xvfb-run -s "-screen 0 2560x1440x24" godot --path . --resolution 2560x1440 \
        -s tools/godot/playtest_act1_opening.gd -- /tmp/playtest

It needs a fresh start (no autosave in `user://saves`). `tools/godot/test_systems.gd` checks the
plumbing around the scenes - music per level and the scripted silences, autosave and continue,
the Esc pause menu and New game - the same way.

In game, Esc pauses: Resume, New game (asks twice; forgets the autosave), Quit. Launching
continues from the autosave taken at every level transition.

What art is still to make, with costs, for approval in one pass: `docs/ART_BACKLOG.md`.
