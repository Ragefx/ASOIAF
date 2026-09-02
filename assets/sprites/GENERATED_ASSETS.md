# Generated Assets — SpriteCook

Assets generated into the project's SpriteCook account. **The bytes are not in this repo yet**:
this session's egress policy denies `api.spritecook.ai`, so the files must be downloaded from the
SpriteCook web app and dropped into the paths below.

Record every generation here at the time it is made, so an asset id is never lost to a scrollback.

## Base characters

| Asset ID | Character | Size | Colours | Goes to |
|---|---|---|---|---|
| `ee4b3f23-1d49-45a5-89c3-679e20b44548` | Ser Torren Slate — base idle, top-down | 166×166 | 3029 | `assets/sprites/torren/torren_base.png` |
| `062acbc2-bd27-47d1-8276-772083b5c432` | Nyra — base idle, top-down | 84×84 | — | `assets/sprites/nyra/nyra_base.png` |

Both were generated with `gemini-3.1-flash-image`, `perspective: topdown`, 12 credits each.
The exact prompts are stored on the assets and are reproduced in `docs/ASSET_SOURCING.md`.

## Before these are usable

Neither base is shippable as-is. 166×166 at 3,029 colours is an illustration, not a sprite — the
project's spec is **16×24 frames on a tight palette** (`docs/TECHNICAL_DESIGN.md` §1). Run
`tools/prepare_sprite.py` on each downloaded file before importing.

## Animation sets — not yet generated

Deferred deliberately: a full top-down set is ~250 credits per character and is derived from the
base above, so the base has to be looked at and approved first. Generating animations from a bad
base wastes the lot.

When approved, the set the engine needs is in `docs/ASSET_SOURCING.md` under "Animation contract".
