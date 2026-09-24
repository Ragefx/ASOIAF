#!/usr/bin/env python3
"""Check that people, animals and things are the right size for one another.

    python3 tools/check_proportions.py            # table + PASS/FAIL, writes the lineup sheet
    python3 tools/check_proportions.py --sheet docs/screenshots/proportions.png

The scale is fixed by the grown men: 56px is a man of about 1.78 m, so 1 m = 31.5px.
Everything below has a real-world height (books first, then common sense) and a
tolerance; the check measures what is actually drawn - the visible pixels of the game-
ready sprite, frame 0 for animations - not the size of its canvas. Run it after adding or
refitting any art. Torren (45px) is the one deliberate exception: approved small, with
the world scaled up around him.

Requires Pillow.
"""
import argparse
import pathlib
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Pillow is required: pip install Pillow")

ROOT = pathlib.Path(__file__).resolve().parent.parent
PX_PER_M = 56 / 1.78

# name -> (sprite, real height in metres, tolerance in px, why)
PEOPLE = {
    "bran": ("life/bran_idle", 1.22, 2, "seven"),
    "tyrion": ("life/tyrion_idle", 1.24, 2, "a dwarf; about 0.7 of a man, not half"),
    "stable_hand": ("life/stable_hand_idle", 1.35, 3, "a boy of twelve or so"),
    "torren": ("sprites/torren/v7/idle", 1.43, 1, "approved at 45px; the world is scaled around him"),
    "nyra_covered": ("life/nyra_covered_idle", 1.43, 3, "Torren's height"),
    "joffrey": ("life/joffrey_idle", 1.49, 2, "twelve"),
    "jon": ("life/jon_idle", 1.55, 2, "fourteen"),
    "cley": ("sprites/cley/v1/idle", 1.52, 2, "Torren's age and rank"),
    "robb": ("life/robb_idle", 1.6, 2, "fifteen, tall for it"),
    "catelyn": ("life/catelyn_idle", 1.63, 2, "a tall woman"),
    "rodrik": ("life/rodrik_idle", 1.68, 2, "stout and old; shorter, wider"),
    "theon": ("life/theon_idle", 1.75, 2, "a grown man"),
    "wells": ("life/wells_idle", 1.73, 2, "a grown man"),
    "guard": ("life/guard_idle_idle", 1.75, 2, "a grown man"),
    "hune": ("life/hune_idle", 1.78, 2, "a grown man"),
    "eddard": ("life/eddard_idle", 1.8, 2, "a grown man"),
    "jaime": ("life/jaime_idle", 1.85, 2, "tall"),
    "benjen": ("life/benjen_idle", 1.85, 2, "tall"),
    "robert": ("life/robert_idle", 2.0, 2, "six foot six and massive"),
    "sandor": ("life/sandor_idle", 2.13, 2, "nearly seven feet"),
    "hodor": ("life/hodor_idle", 2.26, 3, "seven feet and more, barrel on his shoulder"),
}
ANIMALS = {
    "crow": ("life/crow_idle", 0.35, 2, "a crow on the ground"),
    "hare": ("life/hare_idle", 0.38, 2, "a sitting hare"),
    "hen": ("life/hen_idle", 0.41, 2, "a hen"),
    "cat": ("life/cat_idle", 0.41, 2, "a sitting cat, ears up"),
    "ghost_pup": ("life/ghost_pup_idle", 0.38, 2, "a newborn pup, sitting"),
    "pup_howl": ("life/pup_howl_idle", 0.67, 3, "a direwolf pup weeks old, head up"),
    "hound_sleeping": ("life/hound_sleeping_idle", 0.83, 3, "a big hound curled up"),
    "stag": ("life/stag_idle", 1.65, 5, "a red deer stag, antlers included"),
    "horse": ("life/horse_idle", 2.16, 3, "ears well above a man's head"),
    "direwolf_pups": ("life/direwolf_pups_idle", 1.52, 4, "lying down; the size of a pony"),
}
THINGS = {
    "barrel": ("props/barrel", 1.08, 4, "waist-to-chest high (3/4 view adds the top)"),
    "fence_straight": ("props/fence_straight", 1.08, 4, "a rail fence"),
    "brazier": ("life/brazier_idle", 1.11, 4, "a standing brazier"),
    "well": ("props/well", 1.78, 5, "a well with its roof"),
    "candelabra": ("life/candelabra_idle", 1.9, 6, "a standing candelabra"),
    "weapon_rack": ("props/weapon_rack", 2.03, 6, "spears taller than a man"),
    "feast_table": ("props/feast_table", 2.54, 8, "table with benches, seen from above"),
    "wagon": ("props/wagon", 3.17, 10, "a loaded baggage wagon"),
    "hearth": ("life/hearth_idle", 3.56, 10, "a great hall's hearth"),
    "wheelhouse": ("props/wheelhouse", 4.83, 12, "the king's two-storey wheelhouse"),
    "keep_gate": ("props/keep_gate", 5.62, 12, "the Great Keep's gate; its door is taller than a man"),
    "stable": ("props/stable", 7.27, 15, "a long stable, doors fit a horse"),
}


def measure(sprite: str) -> tuple[int, int]:
    path = ROOT / "assets" / f"{sprite}.png"
    im = Image.open(path).convert("RGBA")
    if sprite.startswith(("life/", "sprites/")) and im.width > im.height:
        im = im.crop((0, 0, im.height, im.height))  # frame 0 of a strip
    box = im.getbbox()
    return box[2] - box[0], box[3] - box[1]


def sprite_image(sprite: str) -> Image.Image:
    im = Image.open(ROOT / "assets" / f"{sprite}.png").convert("RGBA")
    if sprite.startswith(("life/", "sprites/")) and im.width > im.height:
        im = im.crop((0, 0, im.height, im.height))
    return im.crop(im.getbbox())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sheet", type=pathlib.Path, default=ROOT / "docs" / "screenshots" / "proportions.png")
    a = ap.parse_args()
    failures = 0
    for title, table in (("PEOPLE", PEOPLE), ("ANIMALS", ANIMALS), ("THINGS", THINGS)):
        print(f"--- {title}")
        for name, (sprite, metres, tol, why) in table.items():
            want = round(metres * PX_PER_M)
            w, h = measure(sprite)
            ok = abs(h - want) <= tol
            failures += not ok
            print(f"{'PASS' if ok else 'FAIL'}  {name:16s} {h:4d}px (want {want}+-{tol}, {metres:.2f} m)  w{w:<4d} {why}")

    # the lineup: everyone on one ground line with a 1.78 m (56px) man's-height line, shown 3x
    rows = [list(PEOPLE.items()), list(ANIMALS.items()) + list(THINGS.items())[:6], list(THINGS.items())[6:]]
    scale, pad = 3, 8
    rendered = []
    for row in rows:
        ims = [sprite_image(s) for _, (s, *_r) in row]
        width = sum(i.width for i in ims) + pad * (len(ims) + 1)
        height = max(i.height for i in ims) + 2 * pad
        sheet = Image.new("RGBA", (width, height), (128, 132, 128, 255))
        draw = ImageDraw.Draw(sheet)
        ground = height - pad
        draw.line([(0, ground - 56), (width, ground - 56)], fill=(200, 60, 60, 255))
        x = pad
        for im in ims:
            sheet.alpha_composite(im, (x, ground - im.height))
            x += im.width + pad
        rendered.append(sheet.resize((width * scale, height * scale), Image.NEAREST))
    out = Image.new("RGBA", (max(r.width for r in rendered), sum(r.height for r in rendered)), (40, 40, 40, 255))
    y = 0
    for r in rendered:
        out.alpha_composite(r, (0, y))
        y += r.height
    a.sheet.parent.mkdir(parents=True, exist_ok=True)
    out.save(a.sheet)
    print(f"lineup (red line = a 1.78 m man) -> {a.sheet}")
    print(f"PROPORTIONS {'PASS' if failures == 0 else 'FAIL'} ({failures} out of range)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
