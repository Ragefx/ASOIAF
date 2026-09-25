#!/usr/bin/env python3
"""Draw a site's layout plan (data/world/sites/<id>.json) for approval.

    python3 tools/draw_site_layout.py winterfell

Writes docs/world/<id>_layout.png: walls, moat, gates, buildings, yards, the Act 1
beats as numbered pins, the 1024 px chunk grid, and a scale bar with a 56 px man and
the old castle-yard level for comparison. It's a plan, not art. Requires Pillow.
"""
import json
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
K = 1 / 3            # plan pixels per game pixel
PAD = 40
COL = {
    "ground": (122, 146, 96), "wall": (118, 118, 124), "wall_edge": (70, 70, 76),
    "moat": (74, 104, 132), "building": (150, 118, 88), "edge": (60, 44, 32),
    "yard": (178, 156, 118), "wood": (58, 96, 58), "tree": (220, 220, 230),
    "water": (60, 112, 140), "graves": (132, 132, 118), "glass": (170, 204, 200),
    "bridge": (110, 84, 60), "stair": (40, 36, 40), "gatehouse": (100, 100, 108),
    "pin": (190, 40, 40), "grid": (0, 0, 0, 40), "text": (20, 20, 20),
}


def font(size):
    for f in ("DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def P(x, y):
    return PAD + x * K, PAD + y * K


def box(r):
    x, y, w, h = r
    return [P(x, y), P(x + w, y + h)]


def ring(d, r, thick, fill):
    x, y, w, h = r
    for rr in ([x, y, w, thick], [x, y + h - thick, w, thick], [x, y, thick, h], [x + w - thick, y, thick, h]):
        d.rectangle(box(rr), fill=fill)


def label(d, xy, text, f, anchor="mm"):
    d.text(xy, text, font=f, fill=COL["text"], anchor=anchor, stroke_width=2, stroke_fill=(245, 240, 228))


def main(site_id):
    site = json.loads((ROOT / "data/world/sites" / f"{site_id}.json").read_text())
    W, H = site["size"]
    img = Image.new("RGBA", (int(W * K) + 2 * PAD, int(H * K) + 2 * PAD + 260), (245, 240, 228, 255))
    d = ImageDraw.Draw(img, "RGBA")
    f_s, f_m, f_l = font(11), font(13), font(20)
    d.rectangle(box([0, 0, W, H]), fill=COL["ground"])

    for w in site["walls"]:
        if w.get("kind") == "moat":
            ring(d, w["rect"], w["thick"], COL["moat"])
        else:
            ring(d, w["rect"], w["thick"], COL["wall"])
            x, y, ww, hh = w["rect"]
            d.rectangle(box(w["rect"]), outline=COL["wall_edge"], width=1)
            d.rectangle(box([x + w["thick"], y + w["thick"], ww - 2 * w["thick"], hh - 2 * w["thick"]]),
                        outline=COL["wall_edge"], width=1)
    # inside the inner wall is packed earth and grass
    for a in site["areas"]:
        fill = COL[a["kind"]]
        if "rect" in a:
            d.rectangle(box(a["rect"]), fill=fill, outline=COL["edge"] if a["kind"] != "wood" else None)
        else:
            cx, cy, r = a["circle"]
            d.ellipse([P(cx - r, cy - r), P(cx + r, cy + r)], fill=fill, outline=COL["edge"])
    for b in site["buildings"]:
        fill = COL.get(b.get("kind", "building"), COL["building"])
        if "rect" in b:
            d.rectangle(box(b["rect"]), fill=fill, outline=COL["edge"], width=2)
        else:
            cx, cy, r = b["circle"]
            d.ellipse([P(cx - r, cy - r), P(cx + r, cy + r)], fill=fill, outline=COL["edge"], width=2)
    for g in site["gates"]:
        x, y = P(*g["at"])
        d.polygon([(x, y - 9), (x + 9, y), (x, y + 9), (x - 9, y)], fill=(230, 190, 60), outline=COL["edge"])

    # labels last, so nothing paints over them
    for a in site["areas"]:
        if a["kind"] in ("tree", "water"):
            cx, cy, r = a["circle"]
            label(d, P(cx, cy + r + 40), a["name"], f_s)
        else:
            x, y, w, h = a["rect"]
            label(d, P(x + w / 2, y + 60), a["name"], f_m)
    for b in site["buildings"]:
        if b.get("kind") in ("bridge", "stair") or b["id"] == "hunters_gatehouse":
            continue
        if "rect" in b:
            x, y, w, h = b["rect"]
            c = (x + w / 2, y + h / 2)
        else:
            c = tuple(b["circle"][:2])
        label(d, P(*c), b["name"], f_s)
    for b in site["buildings"]:
        if b.get("kind") in ("bridge", "stair"):
            x, y, w, h = b["rect"]
            label(d, P(x + w / 2, y - 30), b["name"], f_s)
    for g in site["gates"]:
        gx, gy = g["at"]
        off = {"south": (0, 90), "west": (0, -110)}[g["side"]]
        label(d, P(gx + off[0], gy + off[1]), g["name"], f_m)
    for o in site["outside"]:
        label(d, P(*o["at"]), "→ " + o["name"] if o["dir"] != "west" else "← " + o["name"], f_m)

    # chunk grid
    for gx in range(0, W + 1, 1024):
        d.line([P(gx, 0), P(gx, H)], fill=COL["grid"], width=1)
    for gy in range(0, H + 1, 1024):
        d.line([P(0, gy), P(W, gy)], fill=COL["grid"], width=1)

    for bt in site["beats"]:
        x, y = P(*bt["at"])
        d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=COL["pin"], outline=(255, 255, 255), width=2)
        d.text((x, y), str(bt["scene"]), font=f_s, fill=(255, 255, 255), anchor="mm")

    # legend: scale, the old yard level, beats
    ly = PAD + H * K + 20
    x0 = PAD
    d.text((x0, ly), site["name"] + " - layout proposal", font=f_l, fill=COL["text"])
    bar = 1024 * K
    d.rectangle([x0, ly + 40, x0 + bar, ly + 46], fill=COL["text"])
    d.text((x0, ly + 52), "1024 px = one chunk = 32.5 m in game (~130 m of canon at 1:4)", font=f_s, fill=COL["text"])
    man = 56 * K
    d.rectangle([x0 + bar + 20, ly + 46 - man, x0 + bar + 20 + 6, ly + 46], fill=COL["pin"])
    d.text((x0 + bar + 32, ly + 36), "a grown man (56 px)", font=f_s, fill=COL["text"])
    ow, oh = 1300 * K, 640 * K
    ox = x0 + bar + 170
    d.rectangle([ox, ly + 30, ox + ow, ly + 30 + oh], outline=COL["pin"], width=2)
    d.text((ox + 4, ly + 34), "the old castle-yard level, for size", font=f_s, fill=COL["pin"])
    bx = ox + ow + 30
    beats = site["beats"]
    half = (len(beats) + 1) // 2
    for i, bt in enumerate(beats):
        cx = bx + (i // half) * 260
        cy = ly + 8 + (i % half) * 20
        d.ellipse([cx, cy, cx + 14, cy + 14], fill=COL["pin"])
        d.text((cx + 7, cy + 7), str(bt["scene"]), font=font(9), fill=(255, 255, 255), anchor="mm")
        d.text((cx + 20, cy), bt["what"], font=f_s, fill=COL["text"])

    out = ROOT / "docs/world" / f"{site_id}_layout.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out)
    print(out.relative_to(ROOT))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "winterfell")
