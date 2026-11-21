"""Copy the chosen keyframes into assets/processed with story names,
export web-ready JPGs into public/frames, and cut the profile picture."""
import json
import shutil
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "assets" / "extracted-frames"
REF = ROOT / "assets" / "character-references"
PROC = ROOT / "assets" / "processed"
WEB = ROOT / "public" / "frames"

# story name -> source panel (see assets/inventory.json for sheet ids)
PICKS = {
    "01_wide_run": EX / "E_r0c0.png",
    "02_run_chase": REF / "run_hero.png",
    "03a_run_cycle": EX / "H_r0c1.png",
    "03b_run_cycle": EX / "H_r0c2.png",
    "04_cliff_edge": EX / "E_r0c2.png",
    "05_lose_balance": EX / "E_r1c0.png",
    "06_fall_hero": REF / "fall_hero.png",
    "07_fall_small": EX / "E_r1c1.png",
    "08_abyss": EX / "E_r1c2.png",
    "09_boundary": EX / "E_r2c0.png",
    "10_ai_cubes": EX / "E_r2c1.png",
    "11_ai_terrain": EX / "E_r2c2.png",
    "12_vortex": EX / "E_r3c0.png",
    "13_dream_fade": EX / "H_r3c1.png",
    "14_wake": EX / "E_r3c1.png",
    "15_eyes": EX / "E_r4c1.png",
    "16_reading": EX / "E_r3c2.png",
    "17_over_shoulder": EX / "H_r4c0.png",
    "18_pov_page": EX / "F_r4c1.png",
    "19_reveal": EX / "F_r4c0.png",
    "20_horizon": EX / "E_r4c2.png",
}


def main():
    PROC.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)
    sizes = {}
    for name, src in PICKS.items():
        im = Image.open(src).convert("RGB")
        im.save(PROC / f"{name}.png")
        web = im
        if im.width > 1400:  # the two full-res keyframes
            web = im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS)
        web.save(WEB / f"{name}.jpg", quality=90, optimize=True)
        sizes[name] = web.size
    (ROOT / "src" / "frame-sizes.json").write_text(json.dumps(sizes, indent=1))

    # profile picture: square crop around the falling figure in the hero shot
    hero = Image.open(REF / "fall_hero.png").convert("RGB")
    cx, cy, half = 690, 520, 330
    pfp = hero.crop((cx - half, cy - half, cx + half, cy + half))
    pfp = pfp.resize((800, 800), Image.LANCZOS).filter(
        ImageFilter.UnsharpMask(radius=1.2, percent=40, threshold=2))
    pfp.save(ROOT / "public" / "pfp.png")
    print("processed", len(PICKS), "frames; pfp.png written")


if __name__ == "__main__":
    main()
