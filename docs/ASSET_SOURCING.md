# Asset Sourcing Plan

The constraint is fixed: **the developer cannot create art assets.** The plan is a three-stage
hybrid, ordered so that stage 1 gets a playable Act 1 on screen without spending anything or
waiting for anyone.

| Stage | What | When | Cost |
|---|---|---|---|
| 1 | Free CC0 packs for environments, generic NPCs, UI | Now — unblocks the whole project | £0 |
| 2 | AI-generated sprites for the two protagonists and named NPCs | Once Act 1 blocks out | credits/tokens |
| 3 | Commissioned polish on the sprites that carry the story | Only if the game is worth it | £££ |

> **Verify every licence at download time.** Licences on itch.io and OpenGameArt change, and a
> pack's page is the only authority. Nothing below is a guarantee — treat each entry as "check
> this one first," not "this one is cleared." Record what you actually used in
> `assets/ATTRIBUTION.md` as you import it, not later.

---

## Stage 1 — Free packs

### Environments and tilesets (the biggest need)

The chapter needs three visually distinct location clusters: **Winterfell** (grey stone, snow,
timber, greens), **King's Landing** (warm sandstone, red tile, crowded interiors), and the
**Riverlands** (mud, tents, autumn wood).

| Pack | Source | Typical licence | Use for |
|---|---|---|---|
| **Kenney — Tiny Town / Tiny Dungeon / Roguelike-RPG pack** | kenney.nl | CC0 | The safest starting point in the whole hobby. 16px, huge coverage, no attribution required, no licence anxiety. Blocks out every level. |
| **Tiny Swords** (Pixel Frog) | itch.io | CC0 | Medieval castles, siege props, banners, knights. Aimed at RTS scale but the props and structures re-dress well for Act 5's camps. |
| **Ninja Adventure Asset Pack** (Pixel-Boy) | itch.io | CC0 | Very large top-down set — tiles, characters, UI, music, SFX. The single most useful free pack for a Zelda-like. Art style is bright; it needs a palette pass to sit next to grimmer work. |
| **LPC (Liberated Pixel Cup) base assets** | OpenGameArt | CC-BY-SA 3.0 / GPL 3.0 | Enormous medieval-fantasy tile and character library. **Caution:** CC-BY-SA is *share-alike* and viral — it can force licence terms on derived art. Read it before mixing LPC into anything commissioned. |
| **DENZI's CC0 tiles** | OpenGameArt | CC0 | Small, old, and endlessly reusable for props and clutter. |

**Recommendation:** start on **Kenney + Ninja Adventure**, both CC0, both large enough to build all
three location clusters. Add Tiny Swords for Act 5's military props. Treat LPC as a last resort
precisely because of share-alike.

### Characters and generic NPCs

| Pack | Source | Typical licence | Use for |
|---|---|---|---|
| **Universal LPC Spritesheet Generator** (sanderfrenken, web) | GitHub / liberatedpixelcup.github.io | per-layer, mostly CC-BY-SA / GPL | Generates a walk-cycle character from layered parts. Ideal for the *crowd*: feast guests, gold cloaks, servants, Northern levies. Exports a credits file — keep it. |
| **Ninja Adventure characters** | itch.io | CC0 | Generic NPC bodies at 16px. |

### UI, portraits, fonts

| Need | Source |
|---|---|
| Dialogue frames, bars, buttons | Kenney UI packs (CC0) |
| Pixel font | **m5x7** or **m6x11** (Daniel Linssen, free), or **Press Start 2P** (SIL OFL) |
| Portraits | Stage 2 — none of the free packs will give you Cersei Lannister |

### Audio

| Need | Source |
|---|---|
| SFX | Kenney audio packs (CC0), sfxr/jfxr for one-offs |
| Music | Ninja Adventure's included tracks as scratch; commission or license later |

Chapter 1's score is unusually quiet by design (several key scenes are scored with silence — see
the `music: "none"` fields in the act files), which lowers the music budget considerably.

---

## Stage 2 — AI-generated sprites

For characters the free packs cannot give you: the two protagonists, and the named canon NPCs whose
faces the story depends on (Ned, Robb, Cersei, Littlefinger, the Greatjon, Jory, Mabb, Hune).

**This session has the `spritecook` MCP server attached**, which is a game-asset generation service
with a Godot-shaped pipeline:

| Tool | What it does |
|---|---|
| `generate_character` / `generate_character_animations` | A character with a consistent identity across animations |
| `generate_tileset` | Tilesets to a chosen preset |
| `export_godot_character_package` | Exports a character ready to drop into a Godot project |
| `export_godot_tileset_package` | Same for tilesets |
| `remove_background` / `auto_slice_asset` | Transparent cutouts, slicing sheets into frames |

That last pair matters more than it sounds: consistency across the 4 directions × 5 animations that
`scripts/actors/player.gd` expects is the hard part of AI sprite work, and a per-character workflow
handles it far better than generating frames one at a time.

**Animation set each protagonist needs**, matching `_update_animation()`:

```
idle_{down,up,left,right}      walk_{down,up,left,right}
attack1/2/3_{down,up,left,right}   (Torren only)
dodge_{...}   hurt_{...}   dead_{...}   (Torren only)
```

Nyra needs `idle` and `walk` only — she has no combat kit, which halves her art budget and is one of
the quieter reasons the design gives her stealth instead of a sword.

**Prompt anchors** (keep these identical across every generation for one character, or the identity
drifts):

- **Torren** — 16×24, 4-directional top-down RPG sprite, dark hair, grey-green wool and dull mail,
  no heraldry (House Slate is too minor to have a device anyone would paint), muddy boots. Should
  look *cheaply equipped* next to any southron knight in frame.
- **Nyra** — 16×24, plain grey servant's dress, **grey coif that does not quite cover the hair**.
  Silver-blonde hair, violet eyes. At 16px the eye colour will not read — that is fine and
  intentional; it reads in the **portrait**, which is where the three "your hair / your eyes"
  scenes land.

**Portraits** are the higher-value generation: 32×32 or 48×48, one neutral plus 3–5 moods per
character, matching the `portrait_set` keys in `data/npcs/npcs.json` (e.g. `nyra_blank`,
`baelish_pleasant`, `hune_kind`). Grep the act files for every portrait key actually used — that
list is your art order, and it is much shorter than the NPC list:

```bash
grep -ho '"portrait": "[^"]*"' data/scenes/*.json | sort -u
```

---

## Stage 3 — Commission

Only after a playable Act 1 exists. Commission in this order, because this is the order in which
bad art costs the story most:

1. **Nyra's portrait set.** The entire Valyrian arc is carried by one face across two chapters.
2. **Torren's portrait set.**
3. **The two protagonist sprite sheets**, matched to the commissioned portraits.
4. **The Sept of Baelor plaza tileset.** Act 4's climax is one location and it has to be the best
   thing in the game.

Everything else can stay free forever.

---

## Import discipline

Non-negotiable, because getting it wrong costs a full re-import pass later:

- Every sprite: **Filter off, Mipmaps off, Fix Alpha Border on.** Save as a Godot import preset so
  it is not re-set per file.
- 16px grid for tiles; 16×24 frames for characters, with the **feet** as the sprite origin (the
  `AnimatedSprite2D` offset in `scenes/actors/Player.tscn` is `(0, -8)` for exactly this reason).
- Keep source packs in their original folder structure under `assets/`, one directory per pack, so a
  licence problem means deleting one directory rather than auditing every file.
- `assets/ATTRIBUTION.md` gets a row **at import time**: pack name, author, URL, licence, and which
  directory it landed in.

## Palette

The brief asks for a vibrant palette (greens, browns, stone greys) and a spring→autumn arc across
the chapter. Mixing four free packs will otherwise look like mixing four free packs, so run every
imported tileset through a single shared palette before it goes in — an existing curated ramp such
as **AAP-64** or **Endesga-32** works, or extract one from whichever pack does most of the heavy
lifting. This one step does more for visual coherence than any amount of commissioned art.
