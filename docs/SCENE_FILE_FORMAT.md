# Scene File Format

One JSON file per act: `data/scenes/<act_id>.json`. Loaded and cached by `DialogueSystem`,
validated by `tools/validate_data.py`.

## Top level

```json
{
  "act_id": "act_2",
  "title": "The Investigation",
  "pov": "nyra",
  "timeline": "Months 3–5, 298 AC",
  "locations": ["red_keep", "kings_landing_city", "tourney_grounds"],
  "summary": "One paragraph. What the act is about.",
  "entry_flags": ["act1_complete"],
  "exit_flags": ["act2_complete", "act2_robert_died"],
  "scenes": [ ... ]
}
```

| Field | Type | Notes |
|---|---|---|
| `act_id` | string | Must match the filename. |
| `pov` | `"torren"` \| `"nyra"` | Selects the player scene and HUD. |
| `entry_flags` | string[] | Must all be set before the act may begin. |
| `exit_flags` | string[] | Guaranteed set by the time the act ends. The validator checks each is set by some node. |

## Scene

```json
{
  "scene_id": "s2_01_arrival",
  "title": "The Red Keep",
  "level": "red_keep_service_corridor",
  "spawn": "kitchen_door",
  "time_of_day": "morning",
  "mode": "explore",
  "stage_directions": "Prose for the level designer and the composer. Not shown to the player.",
  "objectives": ["Report to the head laundress"],
  "requires_flags": [],
  "sets_flags": ["act2_arrived"],
  "music": "kl_service_quiet",
  "dialogue": { "start": "n1", "nodes": { ... } }
}
```

`mode` is one of:

| Mode | Meaning |
|---|---|
| `explore` | Free-roam. Dialogue fires on interact or trigger volume. |
| `cutscene` | Player input limited to advance. Camera scripted. |
| `stealth` | Nyra only. Detection meter active. |
| `battle` | Torren only. Wave director active; `waves` array required. |
| `fixed` | Player can look and talk but not leave the marked area. |

## Dialogue node

```json
"n7": {
  "speaker": "jory_cassel",
  "portrait": "jory_neutral",
  "text": "You'll want to look at the boy, not the block. That's what he'll remember.",
  "direction": "Jory does not look at Torren while saying this.",
  "requires_flags": ["!act1_asked_about_gared"],
  "sets_flags": ["act1_talked_to_jory"],
  "traits": { "bold": 1 },
  "relationship": { "jory_cassel": 1 },
  "next": "n8"
}
```

| Field | Required | Notes |
|---|---|---|
| `speaker` | yes | An NPC id, `"torren"`, `"nyra"`, or `"narrator"` for stage text shown in italics. |
| `portrait` | no | Portrait key; omitted for `narrator`. |
| `text` | yes | Supports `{knight}`, `{girl}`, `{house}` tokens. |
| `direction` | no | Author/designer note. Never displayed. |
| `requires_flags` | no | AND-list. `!` prefix negates. If it fails, the node is skipped to `next`. |
| `sets_flags` | no | Applied on node exit. |
| `traits` / `relationship` | no | Signed deltas, applied on node exit. |
| `next` | one of | Node id to continue to. |
| `choices` | one of | Array of choices. Mutually exclusive with `next`. |
| `end` | one of | `true` terminates the scene. |

Exactly one of `next`, `choices`, or `end` must be present.

## Choice

```json
{
  "text": "Say nothing.",
  "next": "n12",
  "requires_flags": [],
  "sets_flags": ["act4_said_nothing"],
  "traits": { "honest": -1, "merciful": 1 },
  "relationship": {},
  "tag": "silent"
}
```

Choices whose `requires_flags` fail are filtered out before display. If all are filtered, the
node's `fallback` node id is used. `tag` is an optional short key for analytics and for later
chapters to ask "how did they play this."

## Battle scenes

```json
"waves": [
  { "id": "w1", "enemies": [{ "type": "lannister_footman", "count": 4 }],
    "on_clear_node": "n20" },
  { "id": "w2", "enemies": [{ "type": "lannister_footman", "count": 6 },
                            { "type": "lannister_serjeant", "count": 1 }],
    "on_clear_node": "n24" }
]
```

`on_clear_node` fires a dialogue node between waves. Battle scenes cannot be lost in Chapter 1 —
on death the player is pulled from the line by an ally, takes a relationship hit, and the wave
restarts. Canon does not permit Torren to die.

## Conventions

- Node ids are `n<number>`, unique within a scene, and need not be contiguous.
- Scene ids are `s<act>_<order>_<slug>`, e.g. `s4_07_the_steps`.
- Flags are `act<N>_<subject>_<verb>`, lowercase, never deleted, only set.
- Every canonical event a scene depicts should be named in its `stage_directions`, so the writer
  and the validator can both find it.
