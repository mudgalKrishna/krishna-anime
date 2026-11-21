"""Make labelled contact sheets of extracted panels for visual review."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "extracted-frames"
OUT = ROOT / "assets" / "previews"

def sheet(prefixes, out, w=330, cols=4):
    files = sorted(f for f in SRC.glob("*.png") if f.name.split("_")[0] in prefixes)
    h = int(w / 2.4)
    rows = (len(files) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * w, rows * (h + 16)), "black")
    d = ImageDraw.Draw(canvas)
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGB").resize((w - 4, h))
        x, y = (i % cols) * w, (i // cols) * (h + 16)
        canvas.paste(im, (x + 2, y + 14))
        d.text((x + 4, y + 1), f.stem + f" {Image.open(f).size}", fill="yellow")
    canvas.save(OUT / out)
    print(out, canvas.size)

if __name__ == "__main__":
    groups = sys.argv[1:] or ["AB", "CD", "EF", "GH", "IJ"]
    for g in groups:
        sheet(list(g), f"contact_{g}.png")
