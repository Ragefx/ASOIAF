#!/usr/bin/env python3
"""Validate the narrative data under data/ without needing Godot.

Checks, per docs/SCENE_FILE_FORMAT.md:
  * every act file parses and matches its filename
  * every node has exactly one of next / choices / end
  * every next / choice target resolves to a node in the same scene
  * every requires_flags entry is set somewhere in this act or an earlier one
  * every act's declared exit_flags is actually set by some node or scene
  * every quest objective flag exists somewhere in the scene data
  * every speaker resolves to an NPC id, a protagonist, or 'narrator'
  * unreachable dialogue nodes are reported (warning, not an error - many nodes
    are entered from trigger volumes rather than from the graph's start node)

Exit code 0 = clean, 1 = errors.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCENES = ROOT / "data" / "scenes"
ACT_ORDER = ["act_1", "act_2", "act_3", "act_4", "act_5"]

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def load(path: pathlib.Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        err(f"{path.name}: not valid JSON: {exc}")
        return None


def main() -> int:
    npcs = load(ROOT / "data" / "npcs" / "npcs.json")
    protos = load(ROOT / "data" / "npcs" / "protagonists.json")
    quests = load(ROOT / "data" / "quests" / "chapter1_quests.json")
    if npcs is None or protos is None or quests is None:
        report()
        return 1

    speakers_ok = set(npcs["npcs"]) | set(protos["protagonists"]) | {"narrator"}

    acts = {}
    for act_id in ACT_ORDER:
        path = SCENES / f"{act_id}.json"
        if not path.exists():
            err(f"missing act file: {path.relative_to(ROOT)}")
            continue
        data = load(path)
        if data is None:
            continue
        if data.get("act_id") != act_id:
            err(f"{path.name}: act_id {data.get('act_id')!r} does not match filename")
        acts[act_id] = data

    # Flags set, accumulated in act order, so an act may depend on earlier acts.
    set_so_far: set[str] = set()
    all_set: set[str] = set()

    for act_id in ACT_ORDER:
        act = acts.get(act_id)
        if act is None:
            continue
        act_sets: set[str] = set()

        for scene in act["scenes"]:
            sid = f"{act_id}/{scene['scene_id']}"
            act_sets.update(scene.get("sets_flags", []))
            nodes = scene["dialogue"]["nodes"]

            for nid, node in nodes.items():
                where = f"{sid}:{nid}"
                terminals = [k for k in ("next", "choices", "end") if k in node]
                if len(terminals) != 1:
                    err(f"{where}: must have exactly one of next/choices/end, has {terminals}")

                if "speaker" not in node:
                    err(f"{where}: no speaker")
                elif node["speaker"] not in speakers_ok:
                    err(f"{where}: unknown speaker {node['speaker']!r}")

                if "text" not in node:
                    err(f"{where}: no text")

                for token in re.findall(r"\{(\w+)\}", node.get("text", "")):
                    if token not in protos["tokens"]:
                        err(f"{where}: unknown text token {{{token}}}")

                act_sets.update(node.get("sets_flags", []))

                if "next" in node and node["next"] not in nodes:
                    err(f"{where}: next -> {node['next']!r} does not exist in this scene")

                for i, choice in enumerate(node.get("choices", [])):
                    cw = f"{where}.choice[{i}]"
                    if "text" not in choice:
                        err(f"{cw}: no text")
                    if "next" not in choice:
                        err(f"{cw}: no next")
                    elif choice["next"] not in nodes:
                        err(f"{cw}: next -> {choice['next']!r} does not exist in this scene")
                    act_sets.update(choice.get("sets_flags", []))

        # Flags readable by this act: everything set in earlier acts plus this one.
        readable = set_so_far | act_sets

        for scene in act["scenes"]:
            sid = f"{act_id}/{scene['scene_id']}"
            for flag in scene.get("requires_flags", []):
                bare = flag.lstrip("!")
                if bare not in readable:
                    err(f"{sid}: requires_flags {flag!r} is never set")
            for nid, node in scene["dialogue"]["nodes"].items():
                sources = [node] + list(node.get("choices", []))
                for src in sources:
                    for flag in src.get("requires_flags", []):
                        bare = flag.lstrip("!")
                        if bare not in readable:
                            err(f"{sid}:{nid}: requires_flags {flag!r} is never set")

        for flag in act.get("entry_flags", []):
            if flag not in set_so_far:
                err(f"{act_id}: entry_flag {flag!r} is not set by any earlier act")
        for flag in act.get("exit_flags", []):
            if flag not in act_sets:
                err(f"{act_id}: exit_flag {flag!r} is never set in this act")

        # Reachability from each scene's declared start node.
        for scene in act["scenes"]:
            nodes = scene["dialogue"]["nodes"]
            start = scene["dialogue"]["start"]
            if start not in nodes:
                err(f"{act_id}/{scene['scene_id']}: start node {start!r} does not exist")
                continue
            seen = set()
            # Wave clear nodes are graph roots too - the wave director enters
            # them directly rather than the dialogue walking to them.
            stack = [start] + [
                w["on_clear_node"] for w in scene.get("waves", []) if "on_clear_node" in w
            ]
            while stack:
                nid = stack.pop()
                if nid in seen:
                    continue
                seen.add(nid)
                node = nodes[nid]
                if "next" in node:
                    stack.append(node["next"])
                for choice in node.get("choices", []):
                    if "next" in choice:
                        stack.append(choice["next"])
            orphans = sorted(set(nodes) - seen)
            if orphans:
                warn(
                    f"{act_id}/{scene['scene_id']}: {len(orphans)} node(s) not reachable "
                    f"from start (expected for trigger-entered nodes): {', '.join(orphans)}"
                )

        set_so_far |= act_sets
        all_set |= act_sets

    for quest in quests["quests"]:
        for obj in quest["objectives"]:
            if obj["flag"] not in all_set:
                err(f"quest {quest['id']}/{obj['id']}: flag {obj['flag']!r} is never set in any scene")
        if quest["completion_flag"] not in all_set:
            err(f"quest {quest['id']}: completion_flag {quest['completion_flag']!r} is never set")

    report()
    return 1 if errors else 0


def report() -> None:
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    print()
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")


if __name__ == "__main__":
    sys.exit(main())
