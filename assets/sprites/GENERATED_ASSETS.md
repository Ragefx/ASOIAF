# Generated Assets — SpriteCook

Assets generated into the project's SpriteCook account. **The bytes are now in this repo** — all
eleven files were downloaded on 2026-09-09 and committed.

> **The egress block is fixed.** `api.spritecook.ai` was denied for the first sessions here: the
> cloud environment's network access was set to **Trusted**, which allowlists package registries
> and GitHub and nothing else, so `curl` got `403` on CONNECT while the MCP tools kept working —
> MCP connector traffic goes through Anthropic's servers and never touches the session allowlist.
> That asymmetry is why generation succeeded and downloading did not.
>
> The fix was to set the environment's **Network access** to **Custom** with `*.spritecook.ai`
> added and *"also include default list of common package managers"* ticked. It is reachable only
> from the cloud icon above the message box at claude.ai/code — there is no settings URL for it.
> **If downloads start failing again, check that first.** Signed URLs also expire in about a week,
> so always fetch fresh ones from the MCP tools rather than reusing a link from these notes.

**The loop now:** Claude generates → Claude downloads with `curl` from a freshly-issued signed URL
→ Claude prepares, commits and wires it. No browser round trip.

> Kept in case the allowlist is ever lost: the fallback is to download in your own browser and
> **attach the files, not paste them.** A pasted image can be *looked at* but never reaches the
> session filesystem, so it cannot be committed or run through `prepare_sprite.py`.

Record every generation here at the time it is made, so an asset id is never lost to scrollback.

---

## What is in the repo

All eleven — the three bases below and the eight animation strips in the
[tier-1 section](#tier-1-animations--generated-2026-09-03) — are committed, each alongside a
`*_prepared.png` produced by `tools/prepare_sprite.py`. **Import the `_prepared` files into Godot;**
the un-suffixed file is the untouched original, kept so preparation can be redone with different
settings without spending credits.

Everything is **labelled in SpriteCook** and the label becomes the downloaded filename, so if these
ever need re-fetching the right files are identifiable without matching UUIDs by eye — every one of
the eleven starts `USE_THIS`.

### The three bases

| SpriteCook label → filename | Asset ID | Size | Colours | Goes to |
|---|---|---|---|---|
| `USE_THIS_01_-_Torren_SPRITE_chibi_big_head` | `e0659339…` | 44×44 | 359 | `assets/sprites/torren/torren_base.png` |
| `USE_THIS_02_v2_-_Nyra_SPRITE_chibi_matched_to_Torren` | `20ffa3a7…` | 88×88 | 1528 | `assets/sprites/nyra/nyra_base.png` |
| `USE_THIS_03_-_Grass_Dirt_TILESET_flat` | `0c490d4c…` | 64×64 (4×4) | **9** | `assets/tilesets/grass_dirt.png` |

**Nyra is on her second base as of 2026-09-09.** The original `e6085562…` (80×80, 748 colours) read
as roughly four and a half heads tall against Torren's three, and both protagonists needed to read
the same age. It is relabelled `zzz SUPERSEDED` below, not deleted, so the prompt history stays
intact. See [the re-roll](#the-re-roll--nyra-v2-2026-09-09) for what changed and why.

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
| Chibi Nyra v2 | 1528 | Higher than Torren's, and higher than Nyra v1's 748 — a bigger source
  canvas (88×88 vs 80×80) invites more colour noise even under the same prompt. Quantises down
  fine at `--colors 16`; see the comparison below. |
| Chibi Nyra v1 (superseded) | 748 | Correct palette, wrong proportions — see the re-roll. |
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
| `e6085562-7c8a-487b-a072-8dae47cc5399` | Nyra chibi v1 | Correct style, wrong proportions — 0.436 aspect against Torren's 0.585, read four and a half heads tall instead of three. Its four tier-1 animations are superseded with it: `2cd76905…` idle, `a18b6dc3…` walk_down, `1ada3ed0…` walk_up, `a465f06d…` walk_right. |

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

## Preparation — run 2026-09-09

`prepare_sprite.py` has now been run for real, against real SpriteCook files, for the first time.
The commands, all of which produced committed output:

```bash
# bases
python3 tools/prepare_sprite.py assets/sprites/torren/torren_base.png --height 24 --colors 16
python3 tools/prepare_sprite.py assets/sprites/nyra/nyra_base.png     --height 24 --colors 16

# the eight animation strips — --frames keeps frames aligned
for c in torren nyra; do for a in idle walk_down walk_up walk_right; do
  python3 tools/prepare_sprite.py "assets/sprites/$c/$a.png" --height 24 --colors 16 --frames 8
done; done
```

The tileset needed no preparation, as predicted: 64×64 in a 4×4 grid, palette already locked by
`force_colors`.

**"Needs no preparation" turned out to mean the pixels, not the design.** Building the first level
(`scenes/world/winterfell_training_yard.tscn`, 2026-09-09) required actually looking at the 4×4
grid tile by tile, and it isn't a modular tileset — it's one continuous painted meadow-and-path
scene cut into 16 pieces. Adjacent pieces align only in the exact layout they were painted in; the
dirt path enters and exits particular tile edges, so there's no "plain grass" or "plain dirt" tile
that recombines cleanly against arbitrary neighbours the way an autotile edge set would. Full
writeup and the workaround used for this one level: `docs/TECHNICAL_DESIGN.md`, in the Scene Graph
section. A real modular atlas — true tileable edge and corner pieces — is unbuilt and is the
blocker for any level bigger or more varied than a single static yard.

| Input | → output | Note |
|---|---|---|
| `torren_base` 44×44 | 14×24 | Reads cleanly. |
| `nyra_base` 88×88 (v2) | 19×24 | Reads cleanly — see the re-roll below for why this replaced an
  earlier 80×80 source that came out thin. |
| Each strip | 192×24, i.e. **24×24 per frame** | Frames stay aligned; the walk cycles read. |

**The script works**, and now needed a second pass — see the re-roll below for a resampling bug
the first pass didn't catch. Its docstring warned it was untested going in; it no longer is.
Confirmed by running against real files: `--frames` scales the sheet as a whole so frames do not
jitter, and the separate alpha/colour quantisation left no halo, because both sources turned out
to have **no partial alpha at all** (every pixel fully opaque or fully transparent). The
`ALPHA_CUTOFF` threshold is therefore doing nothing on these files — useful to know, not a bug.

Note the frame is **24×24, not the 16×24** in `STYLE_GUIDE.md` §3, because SpriteCook returns a
square frame. The extra width is transparent padding; set the `AnimatedSprite2D` offset from the
feet as §3 requires and it does not matter.

### The re-roll — Nyra v2, 2026-09-09

The user's call: both protagonists read the **same age**, not Nyra as visibly younger. That
settled it — the two live proportion fixes considered were `--height 20` on prep (free, but leaves
the same-age intent unmet since it makes her shorter) or a re-roll matching Torren's build
(costs credits, gets the actual outcome asked for). Re-rolled.

**What changed in the prompt, concretely** — not just "try again":

1. Dropped "the shortest figure in the game" from the character description. It was pulling the
   model toward a slighter build regardless of the style block above it.
2. Dropped the ankle-length dress for one that "stops at the knee so both stubby legs and small
   brown shoes are clearly visible below it." A long dress reads as a single tapered shape; cutting
   it at the knee gives the resizer two legs to anchor on, the same way Torren's tunic-over-boots
   does.
3. Added an explicit proportion paragraph modelled directly on Torren: *"SHORT, WIDE, STOCKY...
   exactly like a chibi knight standing beside her... NOT slender, NOT tall, NOT willowy."*
   Comparing her to a known-good reference in the prompt worked better than describing the target
   shape in the abstract.
4. Generated at **128×128 intent** instead of 64×64. The first pass at 64×64 came back 32×32 —
   right proportions (0.742 aspect, close to Torren's 0.585) but too small a source for a second
   problem below. The 128×128 pass came back **88×88**, still correctly proportioned, with enough
   pixels to survive downscaling.

**A second bug this surfaced, in the tool rather than the art:** even with correct proportions,
the 88×88 source's outline broke up into speckle after `--height 24`. Not a colour problem — a
resampling one. `prepare_sprite.py` used nearest-neighbour unconditionally, which is right for
*enlarging* pixel art and wrong for shrinking it by more than about a quarter. Nyra's source
shrinks by 0.27; nearest samples roughly one pixel in four and a three-pixel outline comes apart.
Torren's 44×44 base only shrinks by 0.585 and mostly survived, which is why this went unnoticed
until there were two characters to compare side by side.

Fixed in `prepare_sprite.py`: the resample filter is now chosen by scale factor — `BOX`
(area-average) below 0.75, `NEAREST` at or above it — overridable with `--filter`. Re-running
Torren through the fixed tool improved him too; his arms had the same dashing, just less of it.

**Net result**, figure bounding box measured the same way as before:

| | Figure in source | Aspect w/h |
|---|---|---|
| Torren | 24 × 41 | 0.585 |
| Nyra v1 (superseded) | 34 × 78 | 0.436 |
| **Nyra v2** | **69 × 88** | **0.784** — closer to Torren than v1 was, and with the tool fix both
  now prepare to solid 24px outlines instead of one of them speckling. |

Both prepare to full height 24 with `--colors 16` and no other flags — the standard command below,
unchanged. Same age, same build register, matching the user's call.

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

### Nyra v1 (superseded) — queue item `889219d0-7f5b-4b8d-a09d-68af3ff07eaa`

Source: `e6085562…`, the proportion-mismatched base. All four animations and their bytes were
replaced by the v2 run below on 2026-09-09; this record stays only so the asset ids resolve.

| Animation | Asset ID |
|---|---|
| Idle | `2cd76905-ca5e-4f0b-99b2-ce9f90d5825d` |
| Walk Down | `a18b6dc3-effe-4852-9a27-dd270ad197a8` |
| Walk Up | `1ada3ed0-b961-41ec-a756-8a7eff491942` |
| Walk Right | `a465f06d-e7a6-4888-a51f-20e13635eaec` |

### Nyra v2 — from the re-rolled base, 2026-09-09

Source: `20ffa3a7…`. All frames 96×96, 8 frames each. Run started as one call for all four but
stalled twice after the first item or two completed — `check_character_animation_run` reported no
error and `list_active_jobs` came back empty, so each stall was invisible except as "nothing new
downloads." Re-issuing the still-missing preset ids against the same character resumed it each
time rather than restarting from scratch; total reserved credits across the three calls was
122 + 82 + 44 = 248, more than a single clean 122-credit run because prep steps got re-derived on
the second and third calls instead of being reused. Worth knowing if a run looks stuck: don't wait
indefinitely, re-issue the missing `animation_ids` on the same `character_id`.

| Animation | Asset ID | Goes to |
|---|---|---|
| Idle | `33f43a63-6ffa-499d-9bb1-3354df39acf1` | `assets/sprites/nyra/idle.png` |
| Walk Down | `e941dfdb-d89f-4332-bd05-544092d18eae` | `assets/sprites/nyra/walk_down.png` |
| Walk Up | `49867dd2-45ff-433c-a8f6-60d946b29f2c` | `assets/sprites/nyra/walk_up.png` |
| Walk Right | `8c1c0e8d-e527-4681-b92f-b46e669a5eb4` | `assets/sprites/nyra/walk_right.png` |

Pose preps on the v2 base: back idle `c475bcbd…`, back walk `d86ad826…`, right idle `1a0f6d30…`,
right walk `11cc6277…`, front walk `d7516f2e…`.

**Nyra's strips are still the softer of the two.** Her frames report ~1300–1500 colours against
Torren's base 359, and the frame is 96×96 against his 46×46 — the animator inherits the base's
colour count and then adds to it, and a bigger source canvas gives it more room to add noise in.
Quantises fine at `--colors 16` after the resample-filter fix below; if a future re-roll makes her
mushy again, check the resampling before assuming the colour count is the problem.

---

## Torren v7 — the approved "reference look" base, 2026-09-24

Made against `docs/reference/target_character_crop.png` (uploaded as `5bebfe17-2ca4-413d-9b9a-0600fced3541`).
See `docs/STYLE_GUIDE.md` §0 for why and how. 48 credits across four generations.

| SpriteCook label | Asset ID | What |
|---|---|---|
| `USE THIS 04 v7 - Torren BASE (approved …)` | `c5dacea6-62f6-4040-bc18-a791200820f8` | **Approved.** 48×74 figure → `torren/torren_base_v7.png` (untouched) and `torren/torren_base_v7_65.png` (**31×48, the one to use**) |
| `zzz v5 Torren test (superseded by v7)` | `54623217-6766-40c6-ac05-70346e504361` | First try with the style reference; too detailed |
| `zzz v6 sharp but copied the reference girl …` | `68c3340f-631f-4aca-af98-87f4d9ebca13` | Right sharpness, wrong character; v7 is an edit of it |
| `zzz v8 Torren smaller-size attempt …` | `97cc0df2-0462-4728-bc71-cc78dfcf2880` | Asked for 22×30; came back the same size as v7 |

The older `torren_base.png` / animations in `torren/` are the **rejected** flat-chibi pass and are
still what the game has wired in. They stay until v7's animations exist; nothing references the
v7 files yet.

## Nyra v3 — the approved "reference look" base, 2026-09-24

Made as an **edit of the approved Torren v7** (`c5dacea6…`), changing only identity (no style
reference passed — see STYLE_GUIDE §0 on why). That gave her Torren's exact sharpness,
proportions, height and shadow in one generation, 12 credits. Approved first try. Shrunk with
`tools/prepare_sprite.py nyra_base_v3.png --height 48 --filter majority --colors 256` → 29×48,
the same height as Torren.

| SpriteCook label | Asset ID | What |
|---|---|---|
| `USE THIS 05 v3 - Nyra BASE (approved …)` | `b8aa9b49-10fe-4bee-9329-b4d16fb15efc` | **Approved.** → `nyra/nyra_base_v3.png` (untouched) and `nyra/nyra_base_v3_65.png` (**29×48, the one to use**) |

Her dress came out a bluish slate grey rather than the "dove grey" in the style guide; the user
approved it as is. As with Torren, the old chibi files in `nyra/` are still what Godot uses.

## Torren v7 and Nyra v3 — movement animations, 2026-09-24

Idle + walk down / up / right for both, walk left mirrored from walk right (free). Game-ready strips
live in `torren/v7/` and `nyra/v3/`: **8 frames × 56×56**, character exactly 48px tall (Nyra's idle
49 at the top of a breath), union bbox centred, ground shadow on the bottom row — every animation
shares one anchor. Untouched downloads are in each folder's `raw/`. Rebuild any strip with
`tools/fit_animation.py raw/<name>.png <name>.png` (add `--mirror` for walk_left).
Walk down was approved by the user on its own first; the user then handed SpriteCook over
("only ask me if something costs 100 credits or more") and the rest were made and checked together.

**Recipe** (what worked, per direction):

- **Down / idle:** animate the approved base directly.
- **Up:** edit the base into a back view (default model, 12 cr), then animate that.
- **Right:** the default model will *not* turn the body side-on — two edits and a reference-based
  redraw all came back with only the head turned. `model: gpt-image-2.5-sunburst` with the base as
  `edit_asset_id` gave a true profile first time (16 cr, draws larger — ~134px — which the fit
  step absorbs).
- Every animation: `animate_game_art`, default model, 8 frames, `output_format: spritesheet`,
  `colors: 64`, `auto_enhance_prompt: false`, prompt asks to walk *on the spot*, 20 cr.
  Download the `spritesheet_url` (`…/raw`), not the preview.

| Animation | Torren asset | Nyra asset |
|---|---|---|
| Idle | `8812541f-17b4-4259-b037-339ac9990296` | `e2fb172d-41da-4bfd-8ed1-0d06ca37f358` |
| Walk down | `9d868b94-831b-49e3-8b23-ce6ca74ce119` | `5195addd-f1e2-4932-802b-fb60088450cb` |
| Walk up | `a4cdfd70-d04f-4b44-b554-679b2999dba5` | `677674da-3ebd-421c-96eb-36cff3c14b68` |
| Walk right | `0251123a-75ec-4d65-be54-d215e84f0b9d` | `77750aee-4c70-4a42-a528-6c967f0ac72f` |
| Back pose (for up) | `b40d88a1-b255-494c-8462-48f8681d2480` | `ae2176df-6c76-46b3-a4a5-e2de5b6f22f5` |
| Side pose (for right) | `a5ca898b-f73e-4555-bb8d-6016921b67e5` | `c4ebe8f7-2ce3-4be9-aa84-fe67d8a56ac5` |

All animations are labelled `USE THIS 04 v7 - Torren …` / `USE THIS 05 v3 - Nyra …` in SpriteCook.
Failed Torren side-pose attempts, not used: `1f2cf039…`, `b68b27ff…`, `1a9f7d69…`.
Spend for this batch after walk down: 232 credits (4,842 → 4,610).

Walking left is a mirror, so Torren's sword swaps hips when he faces left. Standard for the genre;
generate a real walk_left (~36 cr) if it ever bothers anyone.

## Ground tileset — 32px grass / packed earth, 2026-09-24

`generate_tileset`, pixel, top-down, `15-piece`, `tile_size: 32`, `edges: two_surfaces`,
`style_asset_id` = an upload of the reference screenshot's grass and path
(`cc4a212d-911a-4d0b-8879-06c5646bad7c`), 2 variations per call, 24 cr per call.

- First call (`5be2c091…`, `02afa816…`): the "other surface" came out as a dark void / holes —
  unusable as a yard floor.
- Second call, prompt naming both surfaces and "no dark void": **`27c1a0ed-6797-4795-855e-773e8aab450d`
  is the one in use** → `assets/tilesets/grass_dirt_32.png`; `fddef81c…` had transparent holes.

It is a corner-matching autotile; `tools/build_ground.py` bakes a level's ground from a vertex
layout into one PNG (`assets/tilesets/<level>_ground.png`), and `assets/tilesets/grass_dirt_32.tres`
is the matching TileSet (terrain "Grass", match-corners) for painting in the editor later.
The old 16px `grass_dirt.png` is no longer referenced.

## Environment props — 2026-09-24

`generate_game_art`, default model, 12 cr each, `style_asset_ids` = an upload of the reference
screenshot's trees/logs/flowers (`9e5dd20a-b4e2-4d76-8098-c5ecf2d2b2a3`). All usable first try; 156 cr.
Untouched downloads in `assets/props/raw/`, game-size sprites in `assets/props/` (majority filter,
or box for shrinks below ~0.5 - the weapon rack turned to mush under majority at 0.35).

| Prop | Asset | Game height |
|---|---|---|
| tree_oak | `e3b24fb2-c457-4da5-82af-bf12e28f7599` | 144 |
| tree_pine | `d9656b12-0301-418a-8097-e0710d978035` | 150 |
| bush | `3675d21b-1730-4630-8eb1-be6dee68ecd0` | 32 |
| boulder | `f37d8930-797d-4da0-a4ff-c734e6799ad6` | 36 |
| rock_pile (asked for pebbles; came out a rock pile) | `f196ba68-b626-486a-b163-3f1977e68b3a` | 30 |
| sticks | `8acfcc56-4d6c-4d2f-b2e8-4aa1c191144a` | 16 |
| log | `33fa2c40-884a-40d7-aa42-e526847aefbb` | 18 |
| stump | `bdeb3211-cdff-4626-8a47-abbdbe511a96` | 30 |
| dummy (straw training dummy) | `6e49d9d2-aecd-4e5a-b05f-8be9d2c5ba72` | 56 |
| weapon_rack | `ac72b3b9-973e-469b-9350-1ecc3c03279a` | 64 |
| barrel | `10b9e6b1-4af0-49cb-8ccc-4999d8dd4eda` | 34 |
| fence (drawn at an angle) | `5c2a76d0-a8be-41dc-bc9d-9bf0f66ff65b` | 44 |
| flowers | `ba3b3a8c-e2b7-4ccf-adfe-2361f03c10c5` | 18 |

`tools/build_props.py scenes` makes `scenes/props/<name>.tscn` (StaticBody2D, origin at the base,
collider on the footprint only); `tools/build_props.py place winterfell_training_yard` dresses
the level (fixed placements + seeded scatter, rerunnable). Sizes are relative to Torren (48px).

## Credits

The table below covers spending up to 2026-09-09. Since then (2026-09-24): Torren/Nyra v5-v8
bases, animations, ground tileset and props took the balance from 4,922 to 4,406.

| | |
|---|---|
| Before this session (2026-09-02/03) | 2,850 |
| Torren tier 1 | −122 |
| Nyra v1 tier 1 (superseded) | −122 |
| Balance before the re-roll (2026-09-09) | 2,606 |
| Nyra v2 base, attempt 1, 2 variants at 64×64 (kept for scale, not used) | −24 |
| Nyra v2 base, attempt 2, 2 variants at 128×128 (the one used) | −24 |
| Nyra v2 tier 1, three calls after the run stalled twice (122 + 82 + 44) | −248 |
| **Remaining** | **2,310** (confirmed against `get_credit_balance`) |

A full top-down set (adding run, attack, hurt, death in four directions) is roughly 550 per
character on top of this. Not worth spending until the tier-1 strips have been seen moving in
Godot at 16×24.

## Wired into Godot — 2026-09-09

Both characters now have a `SpriteFrames` resource — `assets/sprites/<char>/<char>.tres` — and
`scripts/actors/player.gd` loads the right one at runtime from `protagonists.json`'s
`sprite_frames` field, keyed off `GameManager.current_pov`. Nothing about this required opening
Godot: `tools/build_spriteframes.py` emits the `.tres` as plain text — an `ExtResource` per
animation strip, an `AtlasTexture` sub-resource per 24×24 frame region, one `[resource]` block
tying them into named, looping animations at 8 fps. Re-run it after any re-prepared strip:

```bash
python3 tools/build_spriteframes.py torren nyra
```

**Walk-left exists now too**, and is the one animation with no SpriteCook spend behind it at all —
exactly the plan recorded above. `prepare_sprite.py` gained a `--mirror` flag that flips each frame
in place without reversing frame order (reversing would play the gait backwards in time, which
reads as wrong even though the character faces the correct way):

```bash
python3 tools/prepare_sprite.py assets/sprites/torren/walk_right.png --height 24 --colors 16 \
    --frames 8 --mirror --out assets/sprites/torren/walk_left_prepared.png
```

**What still can't be verified from here:** none of this has been opened in the Godot editor or
run, since the sandbox has no Godot install. The `.tres` format was hand-verified structurally
(resource/frame counts, region math, animation names matching `player.gd`'s `ANIM_FALLBACKS`
exactly) but the first real test is loading `Player.tscn` in-engine and confirming the sprite
actually animates. Flag anything that doesn't load cleanly.

**What this does not touch:** `scenes/world/` is still empty except `.gitkeep`. Every act's scene
data references a `level` (22 distinct level ids across the five acts, none built) that
`SceneDirector.goto_level()` expects to find as `res://scenes/world/<level_id>.tscn`, containing a
`TileMap` and a child node literally named `Player`. The animations now play *if* a level exists to
put them in; building the first one is the next real milestone, not this one.
