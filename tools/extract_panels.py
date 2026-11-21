"""Split storyboard contact sheets into individual panels.

Detects the white gutters between panels (rows/columns that are almost
entirely near-white), crops each panel, trims leftover white edges, and
writes them to assets/extracted-frames/<sheet-id>_r<row>c<col>.png.
Single-image keyframes (no gutters) are copied to character-references/.
Originals are never modified.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ORIG = ROOT / "assets" / "original"
OUT = ROOT / "assets" / "extracted-frames"
REF = ROOT / "assets" / "character-references"

# short, stable ids for each sheet
SHEETS = {
    "A": "From_Twilight_Fall_to_AI_Research-1_(1).png",
    "B": "From_Clifffall_to_AI_Dreamscape-4.png",
    "C": "From_Cliffside_Chase_to_AI_Awakening-2_(1).png",
    "D": "From_Falling_to_AI_Researcher-3.png",
    "E": "Dreamfall_An_AI_Researchers_Awakening-6.png",
    "F": "From_Cliffside_Fall_to_AI_Dreamscape-4.png",
    "G": "From_Clifffall_to_AI_Researcher-5.png",
    "H": "From_Cliffside_Fall_to_AI_Researcher-2.png",
    "I": "From_Cliffside_Run_to_AI_Researcher-5.png",
    "J": "From_Cliffside_Chase_to_AI_Dreamscape-3.png",
}
SINGLES = {
    "fall_hero": "Dreamfall_Into_the_Digital_Abyss_(1).png",
    "run_hero": "Sunset_Sprint_Through_Ruins-1.png",
}


def runs(mask):
    """Return [start, end) index ranges where mask is False (content)."""
    out, start = [], None
    for i, m in enumerate(mask):
        if not m and start is None:
            start = i
        elif m and start is not None:
            out.append((start, i))
            start = None
    if start is not None:
        out.append((start, len(mask)))
    return out


def gutters(arr, axis):
    white = (arr.min(axis=2) > 225)  # near-white pixels
    frac = white.mean(axis=axis)
    return frac > 0.85


def split(img):
    a = np.asarray(img).astype(np.int16)
    rows = [r for r in runs(gutters(a, 1)) if r[1] - r[0] > 40]
    panels = []
    for ri, (y0, y1) in enumerate(rows):
        band = a[y0:y1]
        cols = [c for c in runs(gutters(band, 0)) if c[1] - c[0] > 60]
        for ci, (x0, x1) in enumerate(cols):
            # shave 2px to drop anti-aliased gutter edges
            panels.append((ri, ci, (x0 + 2, y0 + 2, x1 - 2, y1 - 2)))
    return panels


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    REF.mkdir(parents=True, exist_ok=True)
    inventory = {}
    for sid, fn in SHEETS.items():
        img = Image.open(ORIG / fn).convert("RGB")
        ps = split(img)
        nrows = max(p[0] for p in ps) + 1
        ncols = max(p[1] for p in ps) + 1
        inventory[sid] = {"file": fn, "grid": f"{ncols}x{nrows}", "panels": []}
        for ri, ci, box in ps:
            name = f"{sid}_r{ri}c{ci}.png"
            img.crop(box).save(OUT / name)
            inventory[sid]["panels"].append({"name": name, "box": box})
        print(sid, fn, f"{ncols} cols x {nrows} rows", len(ps), "panels", ps[0][2])
    for key, fn in SINGLES.items():
        Image.open(ORIG / fn).convert("RGB").save(REF / f"{key}.png")
        inventory[key] = {"file": fn, "grid": "single"}
    (ROOT / "assets" / "inventory.json").write_text(json.dumps(inventory, indent=2))


if __name__ == "__main__":
    main()
