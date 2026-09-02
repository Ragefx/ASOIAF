# Art Style Guide

The reference is a bright 16-bit SNES-era top-down action RPG — Zelda-like, sunny, saturated,
thick-outlined, chunky and readable. Everything below is derived from it. When a generation, a
commission or a free pack disagrees with this document, this document wins.

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
| Tile | **16 × 16** |
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

**Nyra** — small and slight, the shortest silhouette in most scenes. Pale silver-blonde hair under
a soft pale-grey cap with strands loose; the hair is the silhouette and the reason she is
memorable. Dove-grey dress, cream apron, brown cloth shoes. No jewellery, no ornament.

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

**Lead every character prompt with the style, not the character.** The blocks in §2 belong at the
top of the prompt in almost those words; the character description comes after. Prompts that led
with the character produced 166 × 166 illustrations at 3,000 colours. Prompts that led with the
style produced 80 × 80.

Two words to never use in a prompt for this project: *muted* and *grim*. They produce competent
work in the wrong game.
