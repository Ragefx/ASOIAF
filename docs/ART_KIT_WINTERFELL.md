# Art kit - Winterfell (for approval)

The first kit from `docs/WORLD_DESIGN.md` §6. It replaces the grey placeholder massings in
the walkable castle (`scenes/world/winterfell.tscn`, built from the approved layout) with real
art. Approve it as a whole ("approve the kit"), piece by piece, or with changes. **Nothing here
has been generated yet.**

Everything is made the same way as the Act 1 art: SpriteCook, in the props style
(`9e5dd20a-...`), top-down 3/4 like the stables, then sized by the proportion rules (a grown
man is 56 px) and checked by `tools/check_proportions.py`. Costs are credits: a still is 12, an
animation 20 (26 on pixel-engine-v1.5), a tileset 24.

## 1. Walls and towers - reused along every wall in the castle (~170)

| Piece | Kind | Cost | Game size | Notes |
|---|---|---|---|---|
| Curtain wall, straight run | still, cut to tile left-right | 12 | 256 × ~230 | grey granite, wall-walk and merlons on top; about 4 men tall. Repeated end to end along the north and south walls |
| Curtain wall, east-west ends (the top seen from above) | still, cut to tile top-bottom | 12 | ~130 × 256 | the wall-walk seen from above, for the east and west runs |
| Outer wall, straight run | still | 12 | 256 × ~180 | older, lower, darker stone than the inner wall |
| Round wall tower | still | 12 | ~220 × 330 | squat, crenellated; corners and along the walls |
| Main gatehouse | still | 12 | ~420 × 360 | twin towers, arched gate, portcullis raised |
| Hunter's Gate | still | 12 | ~200 × 300 | smaller, plain arch |
| Drawbridge / timber bridge over the moat | still | 12 | 150 × ~180 | |
| Moat water | tileset (two surfaces: water / muddy bank) | 24 | 32 px tiles | also the hot pools, and every river and lake later |
| Crenellated wall corner | still | 12 | ~150 × 250 | where runs meet |
| Wall-walk stair | still | 12 | ~90 × 200 | up to the wall-walk (scene 12) |
| Banner hung on the wall | reuse `banner_stark` | 0 | | |

## 2. The buildings - one still each, at their footprint (~190)

| Building | Cost | About (w × h) | What it must show |
|---|---|---|---|
| Great Keep | 12 | 600 × 700 | the biggest thing in the castle; many-storeyed grey stone, slate roof, the lord's door with the keep's gate in front (existing `keep_gate` stays) |
| Great Hall | 12 | 760 × 450 | long, high-roofed stone hall; big double doors in the middle of the south face |
| First Keep | 12 | 380 × 480 | round, older and darker than the rest, **gargoyles** on the parapet, disused |
| Broken Tower | 12 | 240 × 600 | tall, round, the top burnt and broken open; replaces the small `broken_tower` |
| Library Tower | 12 | 180 × 480 | round, narrow windows |
| Maester's Turret with rookery | 12 | 180 × 520 | round, the rookery on top, a few ravens |
| Bell Tower | 12 | 160 × 420 | bell visible in the open top |
| Armory | 12 | 320 × 360 | stone, heavy door; the covered bridge leaves it at the upper floor |
| Covered bridge | 12 | 160 × 90 | timber gallery between the armory and the keep, overhead |
| Guards Hall | 12 | 420 × 320 | plainer stone hall |
| Guest house | 12 | 560 × 380 | two storeys, timber upper floor over stone |
| Kitchens and brewhouse | 12 | 360 × 280 | chimneys, smoke |
| Forge (Mikken's) | 12 | 260 × 240 | open-fronted smithy; the existing forge fire and blacksmith stand in front |
| Sept | 12 | 280 × 330 | seven-sided, small, stone, a southern building in a northern castle |
| Kennels | 12 | 460 × 200 | low timber, a run fenced in front |
| Granary and storehouses | 12 | 620 × 320 | timber over stone, a loading door |
| Barracks | 12 | 700 × 280 | long, plain |
| Glass gardens | 12 | 700 × 380 | glasshouses, green inside, steam; warm from the hot springs |
| Lichyard gravestones | 12 | a sheet of 4-6 | small, weathered, old northern stones |

## 3. People and animals for a lived-in castle (~150)

Background people kit (docs/WORLD_DESIGN.md §5): the base bodies are identity edits of the
approved guardsman, like every person so far, sized by the proportion rules.

| Piece | Kind | Cost | Notes |
|---|---|---|---|
| Castle man, walking | still + walk | 32 | servant's wool, several colourings by palette swap (no extra cost) |
| Castle woman, walking | still + walk | 32 | |
| Castle boy / girl, walking | still + walk | 32 | ~36 px, children about the yards |
| Guard, walking (patrols the walls) | walk of `guard_idle` | 20 | |
| Dog, walking | still + walk | 32 | kennel dogs loose in the yard |

## Total: about 510 credits

About 1,880 credits were left at the last check, so this kit fits with room for the Winter
Town kit after it.

**Risks, so nothing is a surprise:**
- SpriteCook's biggest images come out around 1,000 px. The Great Keep and the Great Hall are
  near that limit, so they may need one retry each at a wider aspect, as the holdfast did.
- Wall pieces that repeat need clean left and right edges. I'll cut a clean repeating section
  out of each image, the way the ground tiles were handled, and show you a stretch of wall
  before building the whole ring.
