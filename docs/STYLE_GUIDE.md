# Art Style Guide

The reference is a bright 16-bit SNES-era top-down action RPG — Zelda-like, sunny, saturated,
thick-outlined, chunky and readable. Everything below is derived from it. When a generation, a
commission or a free pack disagrees with this document, this document wins.

---

## 0. The confirmed target (2026-09-24) — read this first

The user confirmed one reference image as *the* target: `docs/reference/target_screenshot.webp`
(hero cropped in `target_character_crop.png`). "A sprite RPG with a Pokémon look" — the **look**
only; gameplay stays as built (free movement, real-time combat). Ignore the reference's HUD and
explosion VFX; the user explicitly doesn't want those.

**Measured from the reference, not eyeballed:**

| | Target |
|---|---|
| Screen | Native **320×180** shown at 4×. The project's existing 384×216 @ 4× is effectively the same scale — **keep it**, and keep **16px tiles**. |
| Character size | About **20×28 px** native. Small against the world: trees, logs, barrels dwarf the hero. That smallness is the "Pokémon" feel. |
| Proportions | Big head + hair ≈ **40–45% of height**; tiny body, short legs. Hair mass carries the silhouette. |
| Shading | **4–5 tones per material** (the hair runs dark red → red → orange → yellow highlight). Not flat 2-tone. |
| Outlines | Dark, but tinted with the material's hue, not pure black. |
| Face | A few pixels — one or two eye pixels, no drawn mouth. |
| View | Three-quarter / slightly-from-above, soft dark ellipse shadow under the feet. |
| World | Lush, saturated greens; large detailed props (trees ~2–3× hero height). |

### Approved hero and the new world scale (2026-09-24, later the same day)

**Torren v7 is approved** — `assets/sprites/torren/torren_base_v7_65.png`, **31×48 px**. The user
chose it over shrinking further to the reference's 20×28 ("the world will have to be bigger in
comparison to keep the ratio"). It is the look of the reference — big hair mass, crisp 4–5-tone
shading, flat-toned mail, ground shadow — drawn at about **1.7× the reference's scale**.

So **the hero keeps its size and the world scales up to match**, keeping the reference's
hero-to-world ratio. Everything measured from the reference above multiplies by ~1.7:

| | Reference | This project from now on |
|---|---|---|
| Hero | ~20×28 | **31×48** (the approved sprite) |
| Hero height in tiles | ~1.75 tiles of 16px | the same ~1.75 tiles → tiles of roughly **27px** |
| Trees, big props | ~2–3× hero height | still 2–3× hero height → **~100–150px** tall |
| Visible screen | 320×180 | ~550×310 to show the same amount of world |

**Decided 2026-09-24: 32px tiles, 1280×720 viewport** (shown at 2× on the user's 2560×1440
screen). Tile size came from comparing mockups of the reference world scaled 1.5× and 2× with
Torren dropped in: at 2× the world, Torren (48px) stands a little smaller than the reference hero
would (56px), the "tiny hero in a big world" feel. The viewport came second: 640×360 at 4× made
Torren "way too big" on screen, and the user confirmed from a screenshot that Torren should be
about **1/15 of the screen height (96px on 1440p)** while the camera shows more world — about
**40 × 22 tiles**. So: the hero-to-world ratio is fixed by the tiles; how much world is visible
is fixed by the viewport. Rejected: 24px tiles; 640×360 and 853×480 viewports.
This supersedes "keep 16px tiles" in the table above and in section 3.
(The earlier rejection of 48px tiles was of the *RPG Maker look*, not of bigger tiles as such.)

**Revised the same day — fixed pixel size, not a fixed viewport.** Every game pixel is always
drawn **2×2** on screen; the screen size decides how much world fits around Torren. Torren and
every tile and prop are the same on-screen size on every 1080p/1440p monitor — a smaller screen
just shows less around him, with no black border:

| Screen | Game pixel | Torren on screen | World visible |
|---|---|---|---|
| 2560×1440 (the user's) | 2×2 | 96px | 1280×720 — ~40 × 22 tiles |
| 1920×1080 | 2×2 | 96px | 960×540 — ~30 × 17 tiles |
| 3840×2160 (4K) | 4×4 | 192px | 960×540 (integer scaling picks 4× there) |

**The target is `docs/reference/screen_target_1440p.webp`** — confirmed by the user as *the* look
on their 2560×1440 screen. `screen_scale_agreed.webp` is the same screen with a red box marking
what a 1080p player would see instead (for other players only; it changes nothing on 1440p).

In Godot this is settings only: base viewport **960×540** (the smallest area anyone sees),
`window/stretch/aspect="expand"` so bigger screens reveal more world instead of adding borders,
and the existing `scale_mode="integer"`.

**Level-design rule that follows:** bigger screens see further, so nothing a player must notice
should sit more than ~15 tiles sideways or ~8 tiles up/down from where the camera centres —
that is all a 1080p screen shows.

**A bigger view means more world to build per screen** — dress each area for 40 × 22 tiles
visible (the user's screen), but keep what matters inside 30 × 17 (1080p).

**Not applied to the game yet.** `project.godot` is still 384×216 and the level still uses 16px
tiles and the old chibi sprites. Switching the viewport alone would shrink the current level into
a corner, so the switch happens together with the first 32px tileset and the v7 animations.

**How it was made, so the next sprite can be made the same way:**

1. `generate_game_art` with the reference uploaded as a **style** reference
   (`style_asset_ids`, asset `5bebfe17…`) → v5: right proportions, but too detailed.
2. Edit v5 (`edit_asset_id`) with the style reference again, asking for crisp, flat, low-res →
   v6: exactly the sharpness wanted, **but it copied the reference's red-haired character**. When
   a style reference is passed alongside an edit, it can override the character's identity.
3. Edit v6 with **no** style reference, changing only hair, tunic and colours → **v7**. Sharpness kept.
4. SpriteCook will **not** draw a figure much smaller than ~48×74, whatever `width`/`height` say
   (they are hints; a 24×32 request came back unchanged). Size is done locally:
   `tools/prepare_sprite.py torren_base_v7.png --height 48 --filter majority --colors 256`.
   Don't quantise it to 32 colours — that visibly pulls the tunic toward brown.

**What was tried and rejected, so nobody repeats it:**

- *Flat chibi* (16×24, 2-tone, dot eyes, thick uniform outline) — right size, wrong rendering: read as a toy.
- *Natural proportions, detailed cel-shading* (~5 heads, 48px frames) — "way too detailed and wrong size".
- *Compact 3.5–4-head hero at ~77px source* — closer, but still too tall and too big.
- *RPG Maker generator look* at 48×48 — "not it"; and bumping the whole game to 48px tiles was explicitly rejected.
- **Describing the style in words alone never landed.** Next attempt must upload
  `target_character_crop.png` to SpriteCook and pass it as a style reference
  (`style_asset_ids` / `reference_asset_id` on `generate_game_art`), then generate **one** test
  sprite and show it before anything else. The user wants to go slowly — one step, one check-in.

Sections 2 and 3 below were written for the rejected flat-chibi pass. Where they conflict with
this table (flat fills, 2–3 tones, 16×24 frames), **this table wins** until they're rewritten
against an approved sprite.

---

## 1. The tonal decision, stated on purpose

**The art is bright. The story is not.** Chapter 1 ends with a man's head coming off in front of a
cheering crowd, and it is drawn in the same sunny green as a meadow with mushrooms in it.

This is deliberate and it is the single most important aesthetic choice in the project. It is not
an accident of asset sourcing, and nobody should "fix" it later by desaturating the game.

- Bright art makes Winterfell in Act 1 *worth losing*. A grim game has nowhere to fall from.
- It follows the original brief, which asked for a vibrant palette in greens, browns and stone
  greys. An earlier draft of the asset docs drifted toward "muted, cold, grim" — that drift was
  wrong and has been reverted.
- The precedent is well-established: bright pixel worlds carrying genuinely dark stories.

**The one place the palette bends** is the seasonal arc the brief asked for: Act 1 is spring
green and gold, Act 5 is rust, mud and low grey light. That is a *shift within* this style — the
outlines stay thick, the fills stay flat, the shapes stay chunky. It is not a change of style, and
Act 4's execution is played in full daylight.

## 2. Hard rules

Every sprite and tile, no exceptions:

| Rule | |
|---|---|
| **Thick dark outlines** | Every shape is outlined. The outline is a dark version of the shape's own hue — dark green on foliage, dark brown on wood — **not** pure black. |
| **Flat fills** | Two or three shading tones per material. A base, a shadow, and sometimes a highlight. |
| **No dithering** | None. Not for gradients, not for texture. |
| **No gradients, no anti-aliasing, no soft edges** | Every pixel is fully opaque or fully transparent. |
| **Chunky, low detail** | Readability at 16px beats detail. If a thing is not readable in silhouette, simplify it. |
| **Cartoon proportions** | Characters roughly three heads tall. Large head, short sturdy body. Hair and hats carry the silhouette. |

## 3. Scale

| | |
|---|---|
| Tile | **32 × 32** as of 2026-09-24 (was 16 × 16; see §0) |
| Character frame | **16 × 24** (a 16px footprint, headroom above) |
| Large actors | 32 × 32 on a 16px footprint — mounted knights, the Hound, direwolves |
| Sprite origin | The **feet**. `AnimatedSprite2D` offset `(0, -8)`. |

## 4. Palette

Read off the reference. Use these as the spine; a scene may add a few accents, but grass is this
green and dirt is this tan across the whole game.

### Foliage and grass
`#8FD94F` `#6FC23A` `#4E9E2E` `#377A22` `#245C1A` `#143D12`

### Earth and path
`#E3C48C` `#D0A96B` `#B0854C` `#8A6438` `#5E4225`

### Wood
`#C79A5E` `#9C7040` `#6B4A28`

### Stone
`#9AA3AD` `#6E7A85`

### Accents — use sparingly, they are what make the world feel alive
`#E8E4D0` white flowers · `#F2D24B` yellow flowers · `#A163C9` purple flowers ·
`#D64B3E` mushrooms · `#5FC9AE` teal shrub

### Universal outline
`#10280F`

Pass this list to SpriteCook as `force_colors` on every tileset generation. It works — the first
grass/dirt atlas was generated with exactly this list.

### Act 5 shift
Rotate the greens toward `#7A8232`, `#5C5F26`, `#3E3D1C` and push the earth darker and wetter.
Same structure, same outlines. Do not desaturate the accents; a red mushroom in a grey field is
the point.

## 5. Character direction

Both protagonists must read instantly at 16px, and read *differently* from each other in
silhouette.

**Torren** — shoulder-length dark brown hair carrying the silhouette. Steel-grey mail over a
moss-green tunic, warm brown leather, small round shield on the back, plain sword. **No crest, no
emblem, no gold** — House Slate is too minor to have a device anyone would paint, and he should
look cheaply equipped next to any southron knight in frame. Cheap, not grim: bright steel, not
rust.

**Nyra** — same build and height as Torren; both protagonists read as the same age and neither
should be drawn shorter or slighter than the other. Pale silver-blonde hair under a soft pale-grey
cap with strands loose; the hair is the silhouette and the reason she is memorable, carrying the
distinction from Torren that height no longer does. Dove-grey dress at the knee — long enough to
read as a dress, short enough that both legs stay visible in a chibi sprite — cream apron, brown
cloth shoes. No jewellery, no ornament.

At 16px **her eye colour will not read, and that is correct.** Violet reads in the *portrait*,
which is where all three "your hair / your eyes" scenes land. Do not try to force it into the
sprite; it will only make her look ill.

## 6. Generation settings that work

Measured, not guessed:

| | |
|---|---|
| Characters | `generate_character`, `perspective: topdown`, 12 credits |
| Tilesets | `generate_tileset`, `style_mode: pixel`, `piece_set: 15-piece`, `tile_size: 16`, `edges: two_surfaces`, 12 credits |
| Palette lock | `force_enabled: true` + `force_colors` with §4 |
| Output | A 16px 15-piece atlas returns **64 × 64, 4 × 4** — drop straight into a Godot `TileSet` |

**"Drop straight into a Godot `TileSet`" is not what happened, the one time this was checked.**
The grass/dirt atlas actually in the repo (`assets/tilesets/grass_dirt.png`) is one continuous
painted scene sliced into a 4×4 grid, not a set of tiles that recombine against each other — see
`assets/sprites/GENERATED_ASSETS.md` and `docs/TECHNICAL_DESIGN.md`'s Scene Graph section for what
that meant for the first level. Before trusting this row for a future tileset, generate one and
look at the actual tile grid — grid lines drawn over an upscaled copy make it obvious in seconds —
rather than assuming the settings alone guarantee a modular result.

**Lead every character prompt with the style, not the character.** The blocks in §2 belong at the
top of the prompt in almost those words; the character description comes after. Prompts that led
with the character produced 166 × 166 illustrations at 3,000 colours. Prompts that led with the
style produced 80 × 80.

Two words to never use in a prompt for this project: *muted* and *grim*. They produce competent
work in the wrong game.
