# Generated Assets — SpriteCook

Assets generated into the project's SpriteCook account. **The bytes are not in this repo yet.**
This session's egress policy denies `api.spritecook.ai`, so generation works but downloading does
not — every result comes back as a signed URL on that blocked host.

**The loop that does work:** Claude generates → you download from the SpriteCook web app in your
own browser → you drag the file into the chat → Claude prepares, commits and wires it.

Record every generation here at the time it is made, so an asset id is never lost to scrollback.

---

## Current — style-matched to `docs/STYLE_GUIDE.md`

| Asset ID | What | Size | Goes to |
|---|---|---|---|
| `fd7937d5-e43e-4e48-b64e-0e3e939d7ba7` | **Ser Torren Slate** — base idle, top-down | 80×80 | `assets/sprites/torren/torren_base.png` |
| `e7cb78f6-617f-44d0-852e-b1f46c093d5d` | **Nyra** — base idle, top-down | 170×170 | `assets/sprites/nyra/nyra_base.png` |
| `84003171-f998-46cf-bbd1-21a317d6254c` | **Grass + dirt path** — 15-piece autotile, 16px, two-surface | 64×64 (4×4) | `assets/tilesets/grass_dirt.png` |

The tileset is already the right shape for Godot: a 16px 15-piece atlas at 64×64, 4 columns by
4 rows, generated with the §4 palette locked via `force_colors`. It should need no preparation.

The two characters will need `tools/prepare_sprite.py` before import — see below.

## Superseded — do not use

Generated before the style reference arrived, with prompts that asked for a muted, grim, cold
palette. They are competent and they are the wrong game. Kept only so the ids are not reused.

| Asset ID | What | Why dropped |
|---|---|---|
| `ee4b3f23-1d49-45a5-89c3-679e20b44548` | Torren, first attempt | 166×166, 3029 colours, muted palette |
| `062acbc2-bd27-47d1-8276-772083b5c432` | Nyra, first attempt | Muted palette |

---

## Before the characters are usable

Neither base is a sprite yet — they are illustrations at illustration scale. The spec is 16×24
frames on the §4 palette. After downloading:

```bash
python3 tools/prepare_sprite.py assets/sprites/torren/torren_base.png --height 24 --colors 24
python3 tools/prepare_sprite.py assets/sprites/nyra/nyra_base.png   --height 24 --colors 24
```

Check the first output by eye. `prepare_sprite.py` has never been run against a real SpriteCook
file, because no asset could be downloaded in the session that wrote it.

## Animation sets — deliberately not generated

A full top-down set is ~550 credits per character and every frame is derived from the base sprite
above. The base has to be **seen and approved** first; generating animations from a base that is
off-style wastes the entire spend.

Tier 1 is 8 animations plus 7 preps, ~244 credits per character, and is the whole of what Nyra
ever needs. The tier table is in `docs/ASSET_SOURCING.md` under "Animation contract".

**Credits:** 2,886 remaining of 2,946 at the start. 60 spent (5 generations, 2 superseded).
