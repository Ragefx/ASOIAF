# Asset Attribution

One row per imported pack, added **at import time**, not later. See
[`docs/ASSET_SOURCING.md`](../docs/ASSET_SOURCING.md) for the sourcing plan and the import rules.

| Directory | Pack | Author | Source URL | Licence | Notes |
|---|---|---|---|---|---|
| `assets/sprites/torren/` | Torren chibi sprite + tier-1 top-down animations | AI-generated, SpriteCook (`gemini-3.1-flash-image` base, `pixel_engine` animation) | https://spritecook.ai — project account, not a public pack | Per SpriteCook's terms for generated assets | Imported 2026-09-09. Prompt anchor: style-block-first chibi prompt in `assets/sprites/GENERATED_ASSETS.md`. Base `e0659339…`; animations from run `3419d902…`. `*_prepared.png` are derived locally by `tools/prepare_sprite.py`. |
| `assets/sprites/nyra/` | Nyra chibi sprite + tier-1 top-down animations (v2) | AI-generated, SpriteCook (as above) | https://spritecook.ai — project account | Per SpriteCook's terms for generated assets | Imported 2026-09-09, re-rolled same day. Base `20ffa3a7…`, matched to Torren's proportions and age. The original base `e6085562…` and its animations are superseded — see `GENERATED_ASSETS.md`. |
| `assets/tilesets/` | Grass + dirt 15-piece atlas | AI-generated, SpriteCook | https://spritecook.ai — project account | Per SpriteCook's terms for generated assets | Imported 2026-09-09. Asset `0c490d4c…`, 64×64 4×4, palette locked with `force_colors` from `docs/STYLE_GUIDE.md` §4. No preparation needed. |

## Rules

- Keep each pack in its own directory under `assets/`, in its original structure. A licence problem
  then means deleting one directory rather than auditing every file.
- Record the licence **as stated on the page you downloaded from, on the day you downloaded it**.
- CC-BY-SA is share-alike and viral. If a pack under it is mixed into derived art, that art may
  inherit the terms. Note it in the Notes column, loudly.
- AI-generated assets get a row too: which tool, which prompt anchor, and the date.
