# Art backlog - Act 1, scenes 4 to 12

Everything still to generate before Act 1 can be finished, grouped so it can be approved in one pass
("approve all", "approve scene 5", "skip X"). Nothing below has been generated yet.

Costs are SpriteCook credits: a still is 12, an animation 20 (26 on pixel-engine-v1.5, which is
used when the default engine makes a character grow mid-loop), a tileset 24. Balance on
2026-09-24: about 3,014.

How everything is made (unchanged from scenes 1-4, so new art matches what's in the game):
- **People** are identity edits of the guardsman still `95f8d239-...` (the same look as Torren and
  the guards), described by appearance, not name - the content filter refuses named characters.
  Each gets an 8-frame idle, and is sized against Torren (45px): grown men 55-57, women ~52,
  teenagers 48-50, children ~36.
- **Props and buildings** use the props style reference `9e5dd20a-...`; big buildings are asked
  for at a 9:16 or 16:9 hint so SpriteCook draws them large enough that doors fit a man.
- **Ground** is a 32px 15-piece corner-match tileset in two surfaces, like the grass, cobble
  and snow ones.

## Scene 4 - Six Pups and a Seventh (built; these finish it) - 72

| Item | Kind | Cost | Notes |
|---|---|---|---|
| Jon Snow idle | animation of `daa326b0-...` | 20 | he's a still now |
| White pup idle | animation of `e863e62c-...` | 20 | ears, a blink, breath |
| The pups at her belly | animation of `0cba210c-...` | 20 | the five pups squirm; she stays still |
| Wooden bridge over a frozen stream | still | 12 | the "bridge" spawn; two logs stand in now |

## Scene 5 - The King Comes North (castle yard, fixed position) - about 350

| Item | Kind | Cost | Notes |
|---|---|---|---|
| Robert Baratheon | still + idle | 32 | enormous, bearded, crowned, black-and-gold; about 60px; not played for laughs |
| The wheelhouse | still | 12 | a huge gilded carriage; the queen does not get down |
| Jaime Lannister | still + idle | 32 | golden, white Kingsguard cloak and armour |
| Kingsguard knight | still + idle | 32 | white cloak and plate; reused 2-3 times |
| Gold cloak | still + idle | 32 | City Watch; reused in a line |
| Tyrion Lannister | still + idle | 32 | about 30px; walks with the party in scene 8 too |
| Joffrey | still + idle | 32 | twelve, golden, bored |
| Sandor Clegane | still + idle | 32 | huge, burned face, dog helm under his arm |
| Ser Emmon Wells | still + idle | 32 | a speaker in scenes 5 and 7; southron knight |
| Kneeling | animations | 40 | Torren and the guard kneel (the household kneels) |
| Baratheon and Lannister banners | 2 stills + 2 animations | 64 | same hang as the Stark banners |
| Nyra, covered head, carrying water | edit of Nyra v3 | 12 | in the baggage train; unflagged, not meant to be noticed |

## Scene 6 - Torchlight (the crypts) - about 100

| Item | Kind | Cost | Notes |
|---|---|---|---|
| Crypt floor and wall | tileset | 24 | dark flagstones against black |
| Stone king on his throne, sword across his knees | still | 12 | reused down both walls |
| Lyanna's tomb statue | still | 12 | |
| Stair head | still | 12 | where Torren stands |
| Torren holding a torch | edit of Torren v7 + idle | 32 | the torch flickers |
| Dripping water, torchlight | code | 0 | no generation needed |

## Scene 7 - The Feast (great hall, night) - about 200

| Item | Kind | Cost | Notes |
|---|---|---|---|
| Hall floor | tileset | 24 | stone flags with rushes |
| Hall wall section, high table | 2 stills | 24 | the feast table and candelabra already exist |
| Hearth fire | still + animation | 32 | |
| Seated diners | 3 stills + 3 idles | 96 | eating, drinking, laughing; reused down the benches |
| Servant with a wine jug | walk (Nyra v3 re-dressed) | 32 | the first brief encounter |

## Scenes 8 to 12 - about 280

| Item | Kind | Cost | Scene |
|---|---|---|---|
| Benjen Stark | still + idle | 32 | 8 |
| Lannister soldier | still + idle | 32 | 8 |
| Catelyn Stark | still + idle | 32 | 9 |
| Torren carrying lances | edit + walk | 32 | 9 |
| Small figure on the Broken Tower | still | 12 | 9 |
| Black pool under the heart tree | still | 12 | 10 (the heart tree exists) |
| Howling pup | still + animation | 32 | 10 |
| Nyra losing grip of a trunk | edit + animation | 32 | 11, the second brief encounter |
| Wagons and packed trunks | 2 stills | 24 | 11 |
| Wall-walk and crenellations | tileset + still | 36 | 12 |

**Total for the rest of Act 1: about 1,000 credits.**

## Not art, but also waiting on you

- **Music and sound.** `AudioManager` now plays each scene's music bed and the scripted silences,
  but `assets/audio/` is empty. Act 1 names 11 music beds (`winterfell_morning`, `winterfell_busy`,
  `north_cold_open`, `north_open_road`, `royal_column`, `feast_warm`, ...; 30 across all five acts),
  plus the SFX they need. Options: licensed packs, commissioned tracks, or placeholder CC0 music. Your call.
- **Wording I wrote**: scene 3's execution beats (`n50`-`n55` in `data/scenes/act_1.json`) and the
  "not yet" lines at the castle yard's stables (`n51`) and in the Wolfswood (`n55`).
