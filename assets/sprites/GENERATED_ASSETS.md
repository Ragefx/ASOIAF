# Generated Assets — SpriteCook

Assets generated into the project's SpriteCook account. **The bytes are not in this repo yet.**
The egress policy denies `api.spritecook.ai`, so generation works but downloading does
not — every result comes back as a signed URL on that blocked host.

> **Re-tested 2026-09-03 and still blocked.** A direct `curl` of a fresh signed sprite URL returns
> `curl: (56) CONNECT tunnel failed, response 403`. The agent proxy README classifies 403 on
> CONNECT as an organization egress denial and says not to route around it. This is not a stale
> note and not worth re-testing casually — assume the browser loop below until an admin allows
> the host.

**The loop that works:** Claude generates → you download from the SpriteCook web app in your own
browser → you attach the file here → Claude prepares, commits and wires it.

> **Attach as files, not pasted images.** An image pasted inline can be *looked at* but never
> reaches the session filesystem, so it cannot be committed or run through `prepare_sprite.py`.
> A file attachment lands on disk and can be. This distinction has already cost one round trip.

Record every generation here at the time it is made, so an asset id is never lost to scrollback.

---

## What to download

**Eleven files now:** the three bases below, plus the eight animation strips in the
[tier-1 section](#tier-1-animations--generated-2026-09-03). Everything is **labelled in SpriteCook**
and the label becomes the downloaded filename, so the right files are identifiable without matching
UUIDs by eye — every one of the eleven starts `USE_THIS`.

### The three bases

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

## Tier-1 animations — generated 2026-09-03

Generated with `generate_character_animations`, `perspective: topdown`, `bg_removal_provider: basic`.
"Tier 1" is the top-down pack's own default set: **idle, walk_down, walk_up, walk_right**. Walk-left
is deliberately not generated — mirror `walk_right` horizontally in Godot rather than paying for it.

Each run reserves **122 credits**: 62 for the four animations and 60 for the five pose preps the
pack derives first (back idle, back walk, right idle, right walk, front walk). The preps are
themselves reusable assets — a later tier-2 run over run/attack/hurt reuses them and costs less.

### The output is a sheet, not a frame

Every animation asset carries **two** URLs, and the difference matters:

- `sprite_url` / `pixel_url` — a single preview frame.
- `spritesheet_url` (the `…/signed-content/raw` link) — **the horizontal strip of all 8 frames.
  This is the one to download.** Grabbing the preview instead yields a still image and the mistake
  is not obvious until the animation refuses to play.

Prepare a downloaded strip with `--frames`, which scales the sheet whole so frames stay aligned:

```bash
python3 tools/prepare_sprite.py assets/sprites/torren/idle.png --height 24 --colors 16 --frames 8
```

### Torren — run `3419d902-ba92-4604-adfa-dfa95a1dc935`

Source: `e0659339…`. All frames 46×46, 8 frames each.

| Animation | Asset ID | Goes to |
|---|---|---|
| Idle | `336b47b9-3f18-4204-b576-fe0579be99a4` | `assets/sprites/torren/idle.png` |
| Walk Down | `90017efc-ef6e-4a6c-92f3-8593ddfe2c5e` | `assets/sprites/torren/walk_down.png` |
| Walk Up | `9a881171-43a4-437b-865f-bfde211f7cbe` | `assets/sprites/torren/walk_up.png` |
| Walk Right | `49f6016a-3b70-45f2-8b15-77acf5f1885f` | `assets/sprites/torren/walk_right.png` |

Pose preps, kept for a future tier-2 run: back idle `03cd7475…`, back walk `08d5b61d…`,
right idle `b1109e7f…`, right walk `35108f6a…`, front walk `793d79ad…`.

### Nyra — queue item `889219d0-7f5b-4b8d-a09d-68af3ff07eaa`

Source: `e6085562…`. All frames 86×86, 8 frames each. The second run was queued rather than started
immediately — the account allows 5 concurrent jobs and Torren's four were holding them — so this
one reports a queue item id rather than a run id until it starts.

| Animation | Asset ID | Goes to |
|---|---|---|
| Idle | `2cd76905-ca5e-4f0b-99b2-ce9f90d5825d` | `assets/sprites/nyra/idle.png` |
| Walk Down | `a18b6dc3-effe-4852-9a27-dd270ad197a8` | `assets/sprites/nyra/walk_down.png` |
| Walk Up | `1ada3ed0-b961-41ec-a756-8a7eff491942` | `assets/sprites/nyra/walk_up.png` |
| Walk Right | `a465f06d-e7a6-4888-a51f-20e13635eaec` | `assets/sprites/nyra/walk_right.png` |

Pose preps: back idle `e792f7b7…`, back walk `c0ea53d1…`, right idle `df7a4d70…`,
right walk `0ec8713b…`, front walk `918650e1…`.

**Nyra's strips are the softer of the two.** Her frames report 748–997 colours against Torren's
base 359, and the frame is 86×86 against his 46×46 — the animator inherits the base's colour count
and then adds to it. Quantise her harder if 16 colours leaves her muddy; that is the same softness
the base already showed, not a fault in the animation.

## Credits

| | |
|---|---|
| Before this session | 2,850 |
| Torren tier 1 | −122 |
| Nyra tier 1 | −122 |
| **Remaining** | **2,606** (confirmed) |

A full top-down set (adding run, attack, hurt, death in four directions) is roughly 550 per
character on top of this. Not worth spending until the tier-1 strips have been seen moving in
Godot at 16×24.
