# Generated Assets — SpriteCook

Assets generated into the project's SpriteCook account. **The bytes are not in this repo yet.**
This session's egress policy denies `api.spritecook.ai`, so generation works but downloading does
not — every result comes back as a signed URL on that blocked host.

**The loop that works:** Claude generates → you download from the SpriteCook web app in your own
browser → you attach the file here → Claude prepares, commits and wires it.

> **Attach as files, not pasted images.** An image pasted inline can be *looked at* but never
> reaches the session filesystem, so it cannot be committed or run through `prepare_sprite.py`.
> A file attachment lands on disk and can be. This distinction has already cost one round trip.

Record every generation here at the time it is made, so an asset id is never lost to scrollback.

---

## The three to download

Every asset is now **labelled in SpriteCook**, and the label becomes the downloaded filename — so
the right files are identifiable without matching UUIDs by eye. Grab the three named `USE THIS`.

| SpriteCook label → filename | Asset ID | Size | Colours | Goes to |
|---|---|---|---|---|
| `USE_THIS_01_-_Torren_SPRITE_chibi_big_head` | `e0659339…` | 44×44 | 359 | `assets/sprites/torren/torren_base.png` |
| `USE_THIS_02_-_Nyra_SPRITE_chibi_big_head` | `e6085562…` | 80×80 | 748 | `assets/sprites/nyra/nyra_base.png` |
| `USE_THIS_03_-_Grass_Dirt_TILESET_flat` | `0c490d4c…` | 64×64 (4×4) | **9** | `assets/tilesets/grass_dirt.png` |

Everything else is prefixed `zz` (portrait bases) or `zzz` (superseded) and sorts to the bottom.

**Telling them apart by eye:** the sprites are *chibi* — head roughly one third of the figure,
stubby body, almost no face. The portrait bases are tall and slender, about five heads, with soft
shading and a detailed face. If the figure looks like a nicely drawn person, it is the portrait
base and it is the wrong file.

### Colour count as a quality signal

Worth watching, because it predicts how well `prepare_sprite.py` will do:

| Asset | Colours | Read |
|---|---|---|
| Flat tileset | **9** | Exactly the forced palette. Perfect — needs no preparation. |
| Chibi Torren | 359 | Usable; quantises down cleanly. |
| Chibi Nyra | 748 | Usable, slightly soft. |
| Torren v1 (muted) | 3029 | An illustration, not a sprite. |

## Approved for a different use — portrait bases

These two were generated as sprites and came back at portrait fidelity: roughly five heads tall,
soft multi-tone shading, detailed faces. Wrong for a 24px sprite, and **exactly right for the
32×32 or 48×48 portrait set**, which is the register the dialogue UI wants.

Nyra's in particular is the one to keep: the violet reads clearly, which is precisely what the
three "your hair / your eyes" scenes in Acts 2 and 4 depend on and what a sprite can never carry.

| Asset ID | What | Use as |
|---|---|---|
| `fd7937d5-e43e-4e48-b64e-0e3e939d7ba7` | Torren, detailed | `torren_neutral` portrait base |
| `e7cb78f6-617f-44d0-852e-b1f46c093d5d` | Nyra, detailed | `nyra_neutral` portrait base |

## Superseded — do not use

| Asset ID | What | Why dropped |
|---|---|---|
| `ee4b3f23-1d49-45a5-89c3-679e20b44548` | Torren, first attempt | 166×166, 3029 colours, muted palette |
| `062acbc2-bd27-47d1-8276-772083b5c432` | Nyra, first attempt | Muted palette |
| `84003171-f998-46cf-bbd1-21a317d6254c` | Grass + dirt, first attempt | Grass mottled with noise instead of flat fills |

---

## What the prompt iterations taught

Worth keeping, because it is reproducible and it saved real credits:

| Prompt approach | Torren came back as |
|---|---|
| Character description first, "muted / grim / cold" | **166 × 166**, 3029 colours, illustration |
| Style block first, "bright, thick outlines, flat fills" | **80 × 80**, still ~5 heads tall |
| Explicit pixel height + "CHIBI, head is one third", face detail forbidden | **44 × 44** |

The lever is **stating the target pixel height and the head-to-body ratio as a hard constraint**,
and explicitly forbidding facial detail. Style adjectives alone do not shrink the output.

For tilesets the equivalent lever is forbidding texture in the negative: "do NOT speckle or mottle
the grass, large areas of untouched flat green" produced a far flatter atlas than asking for
"flat colour fills" positively.

---

## Before the characters are usable

```bash
python3 tools/prepare_sprite.py assets/sprites/torren/torren_base.png --height 24 --colors 16
python3 tools/prepare_sprite.py assets/sprites/nyra/nyra_base.png   --height 24 --colors 16
```

The tilesets should need no preparation: a 16px 15-piece atlas returns 64×64 in a 4×4 grid with
the palette already locked by `force_colors`.

## Animation sets — still deferred

~550 credits per character for a full set, ~244 for tier 1, and every frame derives from the base
sprite. The base has to be seen and approved first.

**Credits:** 2,850 remaining of 2,946. 96 spent across 8 generations.
