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
with a Godot-shaped pipeline. Measured costs and behaviour, from an actual run:

| | |
|---|---|
| Tier / balance | `adventurer`, 2,946 credits at the start of the first run, 5 concurrent jobs |
| Base character | **12 credits** (`generate_character`, `perspective: topdown`) |
| One animation | **20 credits** basic background removal, 36-44 with photoroom |
| Pose prep | **12 credits** each, shared by every animation using that source view |
| Default model | `gemini-3.1-flash-image` (12 cr/image at 1K); `gpt-image-2` at `low` is 2 cr/image |
| Full top-down set | 24 animations + 6 preps ≈ **550 credits per character** |

**The output is not pixel art in this project's sense.** The Torren base came back **166×166 with
3,029 colours** — an illustration with a pixel filter, against a spec of 16×24 on a tight palette.
Every asset must go through `tools/prepare_sprite.py` (trim → nearest-neighbour downscale →
quantise → hard alpha threshold) before it is imported. Budget for that step; it is not optional
and it changes how the art reads.

**Network caveat.** In a Claude Code web session, `api.spritecook.ai` may be denied by the
environment's egress policy, in which case assets can be *generated* but not *downloaded* — every
result is a signed URL on that host. The assets still land in the SpriteCook account and can be
fetched from the web app. To download them from inside a session, the environment's network policy
has to allow that host; see https://code.claude.com/docs/en/claude-code-on-the-web.

The tools:

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

### Animation contract

`player.gd` asks for `<action>_<direction>` and resolves misses through a fallback chain
(`_resolve_animation`), so **a partial art set runs correctly** — a missing `attack2` uses
`attack1`, a missing `dodge` uses `walk`, a missing direction falls back to the undirected
animation. Build the set in priority order and the game is playable from the first tier.

SpriteCook's `topdown` preset ids do not match the engine's names. Rename on import:

| SpriteCook preset | Engine animation | Tier |
|---|---|---|
| `idle` | `idle_down` | 1 — minimum playable |
| `idle_back` | `idle_up` | 1 |
| `idle_right` / `idle_left` | `idle_right` / `idle_left` | 1 |
| `walk_down` / `walk_up` | `walk_down` / `walk_up` | 1 |
| `walk_right` / `walk_left` | `walk_right` / `walk_left` | 1 |
| `attack` | `attack1_down` | 2 — Torren only |
| `attack_back` / `attack_right` / `attack_left` | `attack1_up` / `attack1_right` / `attack1_left` | 2 |
| `hurt` (+ `_back`/`_right`/`_left`) | `hurt_down` / `hurt_up` / … | 3 — Torren only |
| `death` (+ directions) | `dead_down` / … | 3 — Torren only |
| *(no preset)* | `attack2_*`, `attack3_*`, `dodge_*` | 4 — custom animations, or leave to fallback |

**Tier 1 is 8 animations and 7 preps: ~244 credits per character, and it is the whole of what Nyra
ever needs** — she has no combat kit in Chapter 1, which halves her art budget and is one of the
quieter reasons the design gave her stealth instead of a sword.

Nyra needs `idle` and `walk` only — she has no combat kit, which halves her art budget and is one of
the quieter reasons the design gives her stealth instead of a sword.

**Prompt anchors** (keep these identical across every generation for one character, or the identity
drifts):

Character direction lives in [`STYLE_GUIDE.md`](STYLE_GUIDE.md) §5. The short version: lead every
prompt with the style block, not the character — prompts that led with the character produced
166×166 illustrations at 3,000 colours, prompts that led with the style produced 80×80. Torren is
cheaply equipped but *bright* steel, not rust; Nyra's hair carries her silhouette and her eye
colour is not meant to read at 16px.

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

## Palette and style

**See [`STYLE_GUIDE.md`](STYLE_GUIDE.md).** It carries the hard rules, the scale, and the exact
hex palette read off the project's reference image, and it overrides anything in this document.

Mixing four free packs looks like mixing four free packs, so every imported tileset gets run
through that one palette before it goes in. That single step does more for visual coherence than
any amount of commissioned art.

Note that the style is **bright** — vivid saturated greens, thick dark outlines, flat fills. An
earlier draft of this document described the target as muted and cold. That was wrong; the words
*muted* and *grim* should not appear in a generation prompt for this project.
