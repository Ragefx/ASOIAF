# World Design - one Westeros to walk through

The game is one continuous world, from the Wall to Dorne, drawn and populated, that the player
walks through. The story happens *inside* that world. It isn't a chain of separate scene levels.
This document replaces the scene-by-scene level plan used to build Act 1. The scenes' dialogue,
flags and scripted beats carry over; where they happen changes.

## 0. Decisions (2026-09-25)

| # | Question | Decision |
|---|---|---|
| 1 | Free roaming or story-gated? | **The story decides, the way the world would.** If King's Landing is closed to visitors at that point, it's closed to you too; if a war is raging in an area, you may not be able to pass. There are no invisible walls "because it's Act 2". |
| 2 | How much world? | **All of Westeros**, from the Wall down to Dorne. Essos and beyond the Wall come later. |
| 3 | Art approval | **Kits are approved as kits.** A building kit, a tileset or a crowd of background people is approved once and reused everywhere. Named characters are still approved one by one. |
| 4 | Distances | **Shortened, not 1:1**, but with a lot of space left between places for optional fights, side quests and discoveries. |

Earlier decisions that still stand: people are true to size (§2), and canon is fixed while the
player's relationship to it is not (README, Design Principles).

## 1. Shape of the world

```
macro map of Westeros (one cell = one chunk)
      │  biome, height, roads, rivers, coast, region, danger
      ▼
chunks (1024 × 1024 px, built from the macro cell + a fixed seed)
      │  ground from tilesets, scattered props, wildlife, encounters
      ▼
sites (hand-made scenes stamped into the chunks)
         castles, towns, villages, inns, holdfasts, ruins, camps, battlefields
```

- **The macro map** is Westeros drawn small, one pixel per chunk. It records the biome
  (pine forest, moor, farmland, marsh, snowfield, desert, ...), roads, rivers, coast, which
  of the nine regions a cell belongs to, and its danger level. It's the one picture that decides
  where everything is. It gets drafted from canon geography and approved like any other layout.
- **Chunks** are built from their macro cell and a fixed seed, so the same place always looks the
  same, and they're streamed in around the player as they walk. The countryside is far too
  big to place by hand (§2), so it's generated. It isn't random, though: the macro map fixes
  its roads, rivers and borders, and the seed keeps it the same every time.
- **Sites** are made by hand like the current levels: Winterfell, Winter Town, the Twins,
  Riverrun, King's Landing and hundreds of smaller places. A site is stamped over the chunks it
  covers and replaces their generated contents.
- **Interiors** such as the Great Hall, the crypts and the Red Keep's corridors stay separate
  scenes behind a door, as they are now. Everything outside a door is one continuous world.

## 2. Scale

People and things keep the scale the proportion checker enforces: a grown man is 56 px (1.78 m),
31.5 px per metre (`docs/STYLE_GUIDE.md`, `tools/check_proportions.py`). Distances are shortened
on two levels:

| | Shortening | Why |
|---|---|---|
| Inside a site (a castle, a town) | about **1 : 4** | Winterfell's walls enclose several acres. At true scale the yard alone would take a minute to cross. At a quarter, every building a person must walk into still fits people at true size, and doors still fit a man. |
| Countryside between sites | about **1 : 120** (`WORLD_COMPRESSION`, tunable) | Long enough to feel like travel, and to leave room for the optional content between places (decision 4). |

At 1:120, with walking at 120 px/s, running at 190 px/s and a horse at about 400 px/s (riding isn't
built yet):

| Journey (canon distance, approx.) | Distance in game | Running | On horseback |
|---|---|---|---|
| Winterfell to Winter Town's far edge | inside the site | under a minute | - |
| Winterfell to the Wall (~800 km) | 6.7 km | ~18 min | ~9 min |
| Winterfell to the Twins (~1,300 km) | 11 km | ~29 min | ~14 min |
| Winterfell to King's Landing (~2,400 km) | 20 km | ~53 min | ~25 min |
| The Wall to Sunspear (~4,800 km) | 40 km | ~1 h 50 | ~52 min |

That's a world about 1.26 million pixels from north to south, around 1,230 × 500 chunks. Nobody
places that much by hand, which is why §1 generates the countryside and hand-makes the sites.
If the travel times feel wrong in play, `WORLD_COMPRESSION` is one number to change; the macro
map doesn't change with it.

**Getting about.** On foot, on horseback (to be built), and by ship along the coasts later. Travel
over long distances by map, between places you have already reached, is still an open question
(§9), not a decision.

## 3. The story decides where you can go

Every region, site and road has a **state** that follows the story, set by the same flags the act
files already use. The rules live in `data/world/regions.json`, and `WorldState` (autoload)
evaluates them whenever a flag changes.

| State | What it means in the world |
|---|---|
| `open` | Normal. Gates open, roads travelled, markets trading. |
| `guarded` | Open, but with checkpoints. Guards question you, some doors need a reason or a pass. |
| `closed` | The gates are shut to people like you. Guards turn you back with a line, not a wall. |
| `contested` | War. Raiders, burned villages, patrols that attack on sight, roads cut. You can try to pass, at a risk. |
| `sealed` | Nobody passes at all: the Bloody Gate held, the causeway at Moat Cailin garrisoned against you. Rare, and always explained in the world. |

Examples from the Book 1 timeline:

- **The Riverlands** turn `contested` when the Lannisters raid after Catelyn takes Tyrion
  (Month 5), and stay that way.
- **King's Landing** turns `guarded` after Robert's death, and `closed` after Ned's arrest; the
  gates are shut while the gold cloaks purge the Stark household.
- **The Kingsroad at the Neck** is `sealed` to anyone but the northern host once Robb marches.
- **The Vale** is `sealed` once Lysa closes the Bloody Gate.

**Where the protagonist is.** Each act has a place it happens (Torren at Winterfell, Nyra in the
Red Keep), and the act's main beats pull the player there. Between those beats you're free to
wander as far as the world's states allow. What the story needs from you is a *place*: when the
next beat is due, the quest log says where. It doesn't lock the rest of the map.

## 4. The space in between

The long roads are the point of shortening distances only so far (decision 4). Between sites:

- **Encounters by region and danger**: wolves in the Wolfswood, bandits on the Kingsroad, raiders
  in the contested Riverlands, shadowcats in the mountains, clansmen in the Mountains of the Moon.
  The danger level comes from the macro map plus the region's state, so a road gets more dangerous
  when war comes to it.
- **Small sites**: hamlets, holdfasts, inns, watchtowers, ruins, shrines, weirwoods, barrows,
  crossings. Each is a small hand-made scene reused from a kit and dressed differently.
- **Side quests**: small, local and in keeping with the world: a missing child in a hamlet, a
  debt at an inn, a knight who wants a squire for a day. They never change canon (README,
  Design Principles).
- **Things to find**: views, landmarks and canon places that aren't story sites, like the Barrow
  of the First King or the Inn at the Crossroads.

## 5. Population

- **Named characters** have a place for each story phase, and a daily routine inside it (Hodor at
  the stables in the morning, Maester Luwin in his turret). A scripted beat overrides the routine
  while it runs.
- **Background people** are built from kits: base bodies (man, woman, youth, child, elder) ×
  clothing for each region and station × hair and colouring. They follow simple routines (work,
  eat, sleep, walk the walls) tied to the time of day.
- **Animals**: dogs, horses, chickens, crows, deer, wolves. Wildlife is chosen by biome.
- **Day and night, and weather**, over all of it; the North's summer snow is a weather state, not
  a separate level.

## 6. Art as kits

A kit is approved once and reused across the whole world (decision 3). It is sized by the
proportion rules and checked by `tools/check_proportions.py` like everything else.

| Kit | Contents | Used for |
|---|---|---|
| Ground tilesets | 32 px corner-match sets: grass, dirt, cobble, snow, mud, sand, marsh, stone floors | every chunk and site |
| Building kits, per region | walls, towers, gatehouses, roofs, doors, windows, stairs, that snap together | castles and towns |
| Village kit, per region | cottages, barns, fences, wells, carts | hamlets, farms, Winter Town |
| Nature kit, per biome | trees, rocks, bushes, grass tufts, fallen logs | scattered by the chunk builder |
| Prop kits | market stalls, camp tents, banners, barrels, crates, signs | sites and encounters |
| Background people | base bodies × clothing × hair | crowds everywhere |
| Named characters | one by one | the cast |

Region kits go in the order the story travels: the North first, then the Riverlands and the
Crownlands, then the rest.

## 7. Technical plan

- **`WorldState` (autoload)**: evaluates region and site states from flags; save data holds
  anything the world has changed (a burned village, a dead bandit captain, a door you opened).
- **`WorldStreamer`**: keeps the 3 × 3 (or 5 × 5 when riding) chunks around the player loaded,
  builds chunks in the background from the macro map, and stamps sites over them. The player,
  the camera and the HUD stay put; only the ground moves in and out underneath.
- **Chunk builder**: bakes ground with the corner-match tilesets (the method
  `tools/build_ground.py` already uses), then scatters props by biome with the seed. Tested
  headless, like the current levels.
- **Sites** are ordinary `.tscn` scenes with a world position. The generated Act 1 levels
  become parts of the Winterfell site; the four copies of the castle yard (arrival, visit, fall,
  departure) merge into one yard whose crowd, banners and people follow the story state.
- **Scripted beats** (`scripts/world/sequence.gd`) keep working; they run at their site instead of
  in a level of their own.
- **Tests**: the Act 1 playtest keeps passing as each scene moves into the world; the world gets
  its own tests (streaming, stamping, state rules) in `tools/godot/`.

## 8. Build order

Each milestone is playable on its own, and each one is shown before the next starts.

1. **Winterfell, whole** - one walkable castle: both walls and the moat, the yards, the Great Keep,
   the Great Hall, the Broken Tower, the First Keep, the godswood, the kennels, the forge, the
   stables, the crypts. Populated, with day and night. Act 1 moved into it and still passing its
   playtest. Starts with a layout for approval (`docs/world/winterfell_layout.png`).
2. **Around Winterfell** - Winter Town, the Wolfswood, the Kingsroad to the Barrow of the First King;
   the chunk streamer and the chunk builder in real use; the first encounters and side quests.
3. **The North** - the macro map drawn for all of Westeros (approved), and the North built out:
   the Wall and the Gift, White Harbor, the Barrowlands, the Neck and Moat Cailin.
4. **South along the story** - the Twins, the Riverlands, the Crownlands and **King's Landing**
   (Acts 2 and 4 happen there, so it comes before the rest of the south).
5. **The rest of Westeros** - the Vale, the Westerlands, the Iron Islands, the Reach, the
   Stormlands and Dorne.

## 9. Open questions (none block milestone 1)

- **Riding.** Horses as a mount the player controls, or only for set journeys?
- **Fast travel.** By map between places you've already reached, only at inns and stables, or not
  at all?
- **Ships.** Coastal travel between ports, and when?
- **Two protagonists, one world.** When Nyra's acts play, does Torren's world state carry over?
  Canon keeps them apart, so for now each act only uses the parts of the world its protagonist
  can reach.
