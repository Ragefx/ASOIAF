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

## Act 1 opening scene assets — 2026-09-24

| Asset | SpriteCook id | In repo |
|---|---|---|
| Ser Cley base (identity edit of Torren v7) | `79d81465-c09f-414e-97b5-5832ad71e407` | `sprites/cley/v1/raw/base.png` |
| Cley idle, eating his apple | `588c3686-77ad-4ffc-89fa-2650d2dc1dca` | `sprites/cley/v1/idle.png` |
| Torren attack down (6 fr) | `fe90ddd5-63f3-4cdf-a658-98b5a4fb0e03` | `sprites/torren/v7/attack_down.png` |
| Torren attack up (6 fr) | `4731498e-2c5e-40a4-9077-44972404b988` | `sprites/torren/v7/attack_up.png` |
| Torren attack right (6 fr; left mirrored) | `d9ae13c6-d4e1-47dd-95db-6bd8b3861a6d` | `sprites/torren/v7/attack_right.png` |
| Curtain wall section (tiles side by side) | `bf48eba2-7ee8-4884-af47-a876287b2c53` | `props/wall.png` |
| Round tower | `ab8dd578-6dfd-4f23-a8b1-250e9355d739` | `props/tower.png` |
| Straight fence | `135b4ac0-298f-410e-98ac-0bea1594bee0` | `props/fence_straight.png` |

Attacks are fitted with `tools/fit_animation.py --frames 6 --like raw/walk_<dir>.png`, which
takes the scale from that direction's walk (a raised blade would otherwise shrink Torren) and
anchors on the standing pose in frame 0 (so the body doesn't slide when the blade swings wide).
Spend: 4,406 -> 4,278 (128 cr). `assets/fx/mist.png` is procedural, not SpriteCook.

## Life - animals, people at work, banners, fire - 2026-09-24

Everything here is built by `tools/build_life.py` from the untouched strips in `assets/life/raw/`
into `assets/life/<name>_<anim>.png` + `<name>.tres` and a scene in `scenes/life/` (critter /
walker / static / deco - see the tool's docstring). Placed in levels by `tools/build_props.py`
as `life/<name>`. All reusable for later scenes (the castle yard, stables, kennels, the Wolfswood).

| Name | Still | Animation | Notes |
|---|---|---|---|
| guard_idle | `95f8d239-cd2a-400a-98ba-e407b4a9ef93` (identity edit of Torren v7) | `b6096b6a-6b3b-40a0-80cc-93dc7aef3627` | Winterfell guardsman, grey fur-collared cloak |
| guard_spar_r / _l | side pose `15642454-d020-4c32-b62f-35b0d3ab8aab` (sunburst edit) | `597ec02f-75ae-481e-9083-f84d12221bce` | same drill, one mirrored |
| stable_boy | `d736f106-91c3-486d-aa0f-f0f30b6733fc`; side pose `7aacf84d-8a31-477f-9bd3-85bbc8becba1` | walk `730bb7e0-a0e0-40c1-a7e7-5fb808f7a6dd` | walker with a bucket |
| hen | `5a875294-4c57-4271-b053-571d229fc184` | `20a9a7bd-72eb-4026-8d3b-a0f202cef785` | critter, scurries |
| crow | `8cde80c5-186b-4284-9d6a-ff5fd2876834` | `5aba75f9-6ead-4cd0-96f5-3cc0656dbf7f` | critter, flies off |
| cat | `2fa832ca-45d4-4221-a835-133a176cd5f5` | `b3eee522-bf6f-4f07-b428-4a3960710774` | sits |
| hare | `fd3039c1-ed62-4c8b-a9ee-826085e7251d` | `fdd949ce-914b-4032-9f07-555ebf79c9f1` | critter, bolts |
| stag | `c0a833a2-1a29-4e41-9484-d6895f09357c` | `91ae0835-98a1-47bd-8da4-a8da07c16398` | Wolfswood |
| hound_sleeping | `50ed168e-ce4c-4c0c-818e-2e59cd8b5be5` | `7cac9452-603c-433b-bef5-4636cf9c73cb` | kennels / yard |
| horse | `ee663bc6-aae4-4390-b78c-0acc3623b1b9` | `b4c64093-8e87-4531-847f-85e63d603b06` | saddled, idle |
| brazier | `41dc3c1c-9ceb-4046-b4cb-4670f4c6e20f` | `55d536eb-236b-4ed5-8857-0090e06c3abe` | fire |
| banner_stark | `f96b2a0b-c0d7-4c0a-9b23-6bc79885f437` | `642e85b8-5c86-4f91-9a65-436c5daad2d6` | grey direwolf on white |
| bird (frames only) | `84304c92-04a2-46b7-91d3-8d60f48543bb` | `cdce035a-8ac0-4143-b914-e29028a77d7b` | used by the flyover |

New still props (`assets/props/`, via build_props.py): hay_bale `c5916a42-7a7f-41c8-b04c-96b1a12767b6`,
well `932892d7-32a6-4d1d-9692-31e966971878`, hay_cart `a1a1c350-f8d8-4550-a4b1-9e44078ecc14`,
archery_target `6e9cc1ec-b0b7-4b38-8e21-c13ac2468f7e`.

Procedural (not SpriteCook), in `assets/fx/`: butterfly (2-frame, tinted per instance), leaf,
cloud_shadows, mist. Code-driven life in `scripts/life/`: wind sway shader on trees/bushes/flowers,
drifting cloud shadows, leaves falling from trees near the camera, bird flyovers with ground
shadows, butterflies, critters that potter and flee, walkers.

Spend this round: 4,278 -> 3,794.

## Later scenes - castle yard, great hall, godswood - 2026-09-24

Built ahead of the scenes that need them, all at the training yard's scale (32px tiles; Torren
45px standing; grown adults taller than him). Guards resized the same day: guard_idle 56px,
the sparring pair 62px including the raised sword.

Still props (`assets/props/`, scenes via `tools/build_props.py scenes`; not placed yet):

| Name | SpriteCook asset | Game size | Notes |
|---|---|---|---|
| stable | `55007776-9358-4a1b-88fe-de7707317cd3` | 343x229 (1:1) | regenerated at 400px so a stall door fits a horse; first try `1d665369-...` too small |
| keep_gate | `786a470f-6bce-44ba-9cae-7740a5699dbd` | 165x177 (1:1) | Great Keep entrance; first try `18225c7c-...` had a door smaller than Torren |
| broken_tower | `c7171dd8-9cb1-4b26-bfe5-0ae2c0818cd6` | 74x207 (1:1) | |
| heart_tree | `fd23315c-64e8-4654-8652-9bb9d9718aae` | 158x177 (1:1) | weirwood with face; sways |
| feast_table | `fd271b31-b9ab-4370-96bb-ff91fe43ca3d` | 138x80 (majority) | great hall |

Animated (`tools/build_life.py`, `scenes/life/`); the stills are kept in `assets/props/raw/`
for re-animating:

| Name | Still | Animation | Notes |
|---|---|---|---|
| forge | `8c918ca4-5bbe-477d-b381-8f1fc2333bce` | `9484a695-b1bf-426d-b6ca-40c84e27430e` | coals pulse, sparks; 104px |
| wall_torch | `e3134fa5-8779-4395-b091-a09c4f08c4ff` | `8d33a6b6-3d08-4891-a406-60f416484714` | deco, hang on walls/pillars; 34px |
| candelabra | `5d2e5b5a-d90b-4281-a7d9-a775ed5b2e04` | `6e7fa893-0c8c-4fc4-bfd5-836e697362a7` | hall / crypts; 60px |
| laundry_line | `6860b2a5-c48a-418e-8980-3b0151d3ac37` | `ec3e79ed-b0a2-4d30-bca4-0a9b17e3d434` | sheets flap; 68px |
| blacksmith | `b795d8f8-c690-410d-9e60-a1a82bf92aa6` | `a1fee85c-05d6-46f6-aa8d-26c619a8da19` | hammering; 78px incl. raised hammer |
| washerwoman | `f4333fd1-3a26-46b9-8db3-13a09f7c21ab` | `5867ffdc-eeaf-4bc4-85db-711aae6e7bf3` | kneeling at her tub; 60px |

Ground: `assets/tilesets/cobble_earth_32.png` (+ `.tres`), SpriteCook tileset
`6f35a587-a297-4144-afc6-a9f2f776ed53` - the same 15-piece corner-match layout as grass_dirt_32,
cobbles in the "upper" (grass) role, packed earth below. The alternative `610998a0-...` has a
stray mark on its full-cobble tile. Both raws in `assets/tilesets/raw/`.

Spend this round: 3,662 -> 3,494.

## Act 1 scene 2 - the castle yard's people, 2026-09-24

NPC idles, built by `tools/build_life.py` as frames only (`assets/life/<name>.tres`), linked
from `data/npcs/npcs.json`'s `sprite_frames`. `scripts/actors/npc.gd` now sets the sprite's
offset from the frame size, so NPCs of any height stand on their feet. Heights: grown men
55-57px (Torren 45 standing); Hodor 72px - he is near seven feet in the books.

| NPC | Still (identity edit of guard `95f8d239-...`) | Idle animation | Game height |
|---|---|---|---|
| rodrik_cassel | `00683deb-6766-463f-9ae6-2dea31779785` | `be1dc563-7b83-4c1a-b0c3-007518272837` | 55 |
| jory_cassel | `eb1298dc-0da5-4ad7-8ba8-f1f519ca0efc` | `39beee9d-99d7-4d37-8eaf-e1441432e51b` (pixel-engine-v1.5; the first, `ec7f1955-...`, grew 10px mid-loop) | 57 |
| hodor | `930172f1-169a-4a27-a4b7-d2f28e3076f4` | `9e750a56-c76b-4614-a4cf-ed5d2b4dd879` | 72, barrel on his shoulder |
| stable_hand | stable_boy `d736f106-91c3-486d-aa0f-f0f30b6733fc` | `9de06d63-2661-4268-9e32-4cf4cec87a39` | 42 |

Named-character prompts ("Ser Rodrik Cassel", "Hodor") were refused by SpriteCook's content
filter; describing the look without the name went through.

Level: `scenes/world/winterfell_yard.tscn`, ground `assets/tilesets/winterfell_yard_ground.png`
(`tools/build_ground.py winterfell_yard`, cobble tileset), props and life placed by
`tools/build_props.py place winterfell_yard`.

Spend this round: 3,494 -> 3,352.

## Act 1 scene 3 - the Wolfswood in summer snow, 2026-09-24

People (identity edits of guard `95f8d239-...`, prompts describe the look without names; idles by
`tools/build_life.py`). Heights: Lord Stark 57, Hune 56, Theon 55, Robb 50, Bran 36; Gared kneels at 40.

| Who | Still | Idle animation | Notes |
|---|---|---|---|
| eddard_stark | `9a370e01-b8ed-47f2-8b9d-e4a495dfc7e7` | `49e8424a-bfff-43cd-b438-08c0e5369420` | hands on Ice's crossguard |
| hune | `925792e9-40d9-4f4a-af82-2995162081db` | `4ee83106-4d19-4b7d-af85-32fa713b11a9` | spear |
| theon_greyjoy | `21d01bfe-df03-49bb-94fd-777a6743cdb6` | `a3202c39-a491-4e2f-8399-54a900515b11` | v1.5; the v1.1 try `8415ccdf-...` grew 9px and didn't loop |
| robb_stark | `767df33a-2661-448a-86fb-f12fd03450eb` | `07e36fe1-4b05-441c-9488-c373e077c768` | |
| bran_stark | `953936b6-4018-4298-ab97-6b3140e1cdce` | `f539337e-b1fc-4db6-ab6e-27ad0c5b1a5d` | |
| gared (life/, not an NPC) | `6600cbbc-f51b-4eac-92c4-4d19969cf18b` | `8c7cb88b-82b5-4226-8898-d23d6bffb258` | kneeling, bound; hidden once the sentence is done |

Scenery: tree_pine_snow `7b1fc3d3-b96e-40f1-bc05-16f2b6bc6983`, tree_oak_snow `d9fc0198-d472-405f-a7a5-8c08184b1e7c`
(edits of the yard's trees, same scale); holdfast `956ff13f-0708-4da7-a689-23a1636f08fd` at 0.6 (107x225) - the
two square tries (`ff95b795-...`, `e33e21c0-...`) came out 162px with a doorway shorter than Torren; asking for
9:16 gave a 376px image. Ground: `assets/tilesets/snow_earth_32.png`, tileset `99f21159-ca20-40a5-9ce3-f64b9812f29d`
(alternative `04cb230b-...`), brown flecks painted out of the full-snow tile by build_ground's "snow" plain mode.
Procedural: `assets/fx/snow_far.png`, `snow_near.png` - two drifting layers of falling snow.

Spend this round: 3,352 -> 3,050.

## Act 1 scene 4 - the kingsroad, 2026-09-24

Stills only so far - no animations yet (each new SpriteCook generation now waits for the owner's
approval). Game sizes: the dead direwolf lies 111x64, longer than a horse; Jon Snow 49px (fourteen,
between Torren's 45 and Robb's 50); the white pup 17px.

| Name | SpriteCook asset | Notes |
|---|---|---|
| direwolf_dead (prop) | `0cba210c-0972-4cf3-87ec-d4a12a6ce4d1` | antler at her neck, five grey pups at her belly |
| ghost_pup (life/, one frame) | `e863e62c-ab79-460a-96da-c81ee1243d97` | white, red eyes, sitting |
| jon_snow (NPC, one frame) | `daa326b0-04a3-4f66-9747-64a6739e7c84` | identity edit of the guard |

Wanted later (needs approval): idle animations for Jon and the pup, the pups squirming, a bridge
over a frozen stream for the "bridge" spawn (two logs stand in for it now).

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
