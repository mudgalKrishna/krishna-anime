"""Render the animation (from src/timeline.json) into the README card.

Outputs (public/):
  animation.gif   - card + film, GitHub README embed
  animation.webp  - same, higher quality / smaller (animated WebP)
  poster.jpg      - still of the reveal
Usage: python tools/render.py [--scale 1.0] [--fps 12.5] [--only gif|webp|frames]
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "assets" / "processed"
PUB = ROOT / "public"
TL = json.loads((ROOT / "src" / "timeline.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- helpers
def frac(x):
    return x - math.floor(x)


def h(i, k):  # deterministic hash in [0,1) - mirrored in player.js
    return frac(math.sin(i * 12.9898 + k * 78.233) * 43758.5453)


EASE = {
    "linear": lambda p: p,
    "in": lambda p: p * p,
    "out": lambda p: 1 - (1 - p) ** 2,
    "inOut": lambda p: p * p * (3 - 2 * p),
}


def smooth(p):
    p = min(max(p, 0.0), 1.0)
    return p * p * (3 - 2 * p)


def lerp(a, b, p):
    return a + (b - a) * p


# ---------------------------------------------------------------- timeline
SHOTS = TL["shots"]
starts, t = [], 0.0
for s in SHOTS:
    starts.append(t)
    t += s["dur"]
TOTAL = t + TL["tail"]
IMGS = {}


def img(name):
    if name not in IMGS:
        IMGS[name] = Image.open(PROC / f"{name}.png").convert("RGB")
    return IMGS[name]


def camera(shot, i, tg):
    nxt = SHOTS[i + 1]["in"]["dur"] if i + 1 < len(SHOTS) else TL["tail"]
    span = shot["dur"] + nxt
    p = EASE[shot.get("ease", "inOut")](min(max((tg - starts[i]) / span, 0), 1))
    a, b = shot["from"], shot["to"]
    return {k: lerp(a[k], b[k], p) for k in "xyzr"}


def render_shot(i, tg, W, H):
    shot = SHOTS[i]
    lt = tg - starts[i]
    srcs = shot["src"]
    name = srcs[int(lt / shot["period"]) % len(srcs)] if len(srcs) > 1 else srcs[0]
    im = img(name)
    w, hh = im.size
    c = camera(shot, i, tg)
    s = max(W / w, H / hh) * c["z"]
    r = math.radians(c["r"])
    cos, sin = math.cos(r), math.sin(r)
    # keep the frame inside the image (account for roll)
    ex = (W * abs(cos) + H * abs(sin)) / (2 * s)
    ey = (W * abs(sin) + H * abs(cos)) / (2 * s)
    if ex * 2 > w or ey * 2 > hh:  # need a touch more zoom to hide edges
        s *= max(ex * 2 / w, ey * 2 / hh) * 1.001
        ex = (W * abs(cos) + H * abs(sin)) / (2 * s)
        ey = (W * abs(sin) + H * abs(cos)) / (2 * s)
    px = min(max(c["x"] * w, ex), w - ex)
    py = min(max(c["y"] * hh, ey), hh - ey)
    sh = shot.get("shake")
    if sh:
        amp = sh["amp"] * math.exp(-sh["decay"] * lt) / s
        px += amp * (math.sin(lt * sh["freq"] * 6.283) + 0.5 * math.sin(lt * sh["freq"] * 15.1))
        py += amp * (math.cos(lt * sh["freq"] * 5.31) + 0.5 * math.sin(lt * sh["freq"] * 11.7))
    a, b = cos / s, sin / s
    d, e = -sin / s, cos / s
    cc = px - (a * W / 2 + b * H / 2)
    f = py - (d * W / 2 + e * H / 2)
    out = im.transform((W, H), Image.AFFINE, (a, b, cc, d, e, f), resample=Image.BICUBIC)
    for fx in shot.get("fx", []):
        draw_fx(out, fx, lt, i)
    return out


# ---------------------------------------------------------------- particles
FX = {
    #        n,  color,            size range
    "leaves": (16, (38, 28, 40), (1.2, 3.0)),
    "debris": (24, (34, 27, 40), (1.0, 3.4)),
    "sparks": (28, (214, 196, 255), (0.6, 1.6)),
    "motes": (20, (255, 214, 170), (0.7, 1.8)),
}


def fx_particle(kind, k, t):
    """returns (u, v, size01, alpha) - identical maths in player.js"""
    h1, h2, h3, h4 = h(k, 1), h(k, 2), h(k, 3), h(k, 4)
    if kind == "leaves":
        u = frac(h1 - t * (0.18 + 0.2 * h2))
        v = frac(h3 - t * 0.04) + 0.02 * math.sin(t * 3 + k)
        return u, v, h4, 0.75
    if kind == "debris":
        u = frac(h1 + 0.03 * math.sin(t + k))
        v = frac(h3 - t * (0.45 + 0.6 * h2))
        return u, v, h4, 0.85
    if kind == "sparks":
        u = h1
        v = frac(h3 - t * 0.03)
        return u, v, h4, 0.25 + 0.75 * max(0.0, math.sin(t * 2.2 + h2 * 6.283))
    u = frac(h1 + t * 0.02)  # motes
    v = frac(h3 - t * (0.02 + 0.02 * h2) + 0.01 * math.sin(t + k))
    return u, v, h4, 0.2 + 0.45 * math.sin(t * 1.3 + h2 * 6.283) ** 2


def draw_fx(im, kind, t, seed):
    n, col, (smin, smax) = FX[kind]
    W, H = im.size
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    scale = W / 720
    for k in range(n):
        u, v, s01, al = fx_particle(kind, k + seed * 101, t)
        r = (smin + (smax - smin) * s01) * scale
        x, y = u * W, v * H
        dr.ellipse((x - r, y - r * (0.7 if kind in ("leaves", "debris") else 1), x + r,
                    y + r * (0.7 if kind in ("leaves", "debris") else 1)), fill=col + (int(255 * al),))
    im.paste(layer, (0, 0), layer)


# ---------------------------------------------------------------- transitions
def blend(a, b, p):
    return Image.blend(a, b, p)


def transition(kind, a, b, p, W, H):
    q = smooth(p)
    if kind in ("dissolve", "fadeblack"):
        return blend(a, b, q)
    if kind == "wipe":  # diagonal light sweep, the dimensional edge
        yy, xx = np.mgrid[0:H, 0:W]
        d = (xx / W) * 0.75 + (yy / H) * 0.25
        m = np.clip((q * 1.35 - d) / 0.22, 0, 1)
        A, B = np.asarray(a, np.float32), np.asarray(b, np.float32)
        out = A * (1 - m[..., None]) + B * m[..., None]
        glow = np.exp(-((m - 0.5) / 0.22) ** 2) * math.sin(math.pi * p) * 0.75
        out += glow[..., None] * np.array([235, 215, 255], np.float32) * 0.6
        return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    if kind == "blocks":  # dream dissolving into blocks
        bs = max(3, round(W / 120))
        bw, bh = W // bs + 1, H // bs + 1
        n = np.array([[0.45 * h(x + 7, y + 3) + 0.55 * (1 - x / bw) for x in range(bw)] for y in range(bh)], np.float32)
        m = np.clip((q * 1.5 - n) / 0.5, 0, 1)
        m = np.repeat(np.repeat(m, bs, 0), bs, 1)[:H, :W]
        A, B = np.asarray(a, np.float32), np.asarray(b, np.float32)
        out = A * (1 - m[..., None]) + B * m[..., None]
        return Image.fromarray(out.astype(np.uint8))
    if kind == "focus":  # bring the paper into focus
        bb = b.filter(ImageFilter.GaussianBlur((1 - q) * 6 * W / 720))
        return blend(a, bb, smooth(p * 1.6))
    return b


def film_frame(tg, W, H):
    # active shot = last whose start <= tg
    i = max(k for k in range(len(SHOTS)) if starts[k] <= tg) if tg >= 0 else 0
    cur = render_shot(i, tg, W, H)
    tin = SHOTS[i]["in"]
    lt = tg - starts[i]
    if tin["type"] != "cut" and lt < tin["dur"]:
        prev = render_shot(i - 1, tg, W, H) if i > 0 else Image.new("RGB", (W, H), (8, 6, 14))
        cur = transition(tin["type"], prev, cur, lt / tin["dur"], W, H)
    # fin + fade out
    last_end = starts[-1] + SHOTS[-1]["dur"]
    if SHOTS[i].get("end") == "fin":
        a = smooth((tg - (last_end - 1.8)) / 0.8)
        if a > 0:
            draw_fin(cur, a)
    if tg > last_end:
        cur = blend(cur, Image.new("RGB", (W, H), (8, 6, 14)), smooth((tg - last_end) / TL["tail"]))
    return cur, i


def font(name, size):
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


def draw_fin(im, a):
    W, H = im.size
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font("YuGothM.ttc", round(H * 0.11))
    d.text((W - H * 0.08, H - H * 0.07), "終", font=f, anchor="rs", fill=(250, 236, 220, int(230 * a)))
    im.paste(layer, (0, 0), layer)


def vignette(W, H):
    yy, xx = np.mgrid[0:H, 0:W]
    dx, dy = (xx / W - 0.5) * 2, (yy / H - 0.5) * 2
    v = 1 - 0.28 * np.clip((dx ** 2 * 0.6 + dy ** 2 * 0.9) - 0.15, 0, 1)
    return v[..., None].astype(np.float32)


# ---------------------------------------------------------------- card
class Card:
    def __init__(self, scale):
        S = scale
        self.S = S
        self.FW, self.FH = round(720 * S), round(300 * S)
        self.pad = round(12 * S)
        self.cap = round(34 * S)
        self.W = self.FW + 2 * self.pad
        self.H = self.FH + self.pad + self.cap
        self.bg = self.make_bg()
        self.mask = self.film_mask()
        self.vig = vignette(self.FW, self.FH)

    def make_bg(self):
        S, W, H = self.S, self.W, self.H
        bg = Image.new("RGB", (W, H), (13, 17, 23))  # github dark outside corners
        d = ImageDraw.Draw(bg)
        rad = round(14 * S)
        d.rounded_rectangle((0, 0, W - 1, H - 1), rad, fill=(22, 19, 34), outline=(84, 72, 120), width=max(1, round(S)))
        y = self.pad + self.FH + round(21 * S)
        serif = font("georgia.ttf", round(13 * S))
        jp = font("YuGothM.ttc", round(11 * S))
        d.text((self.pad + round(2 * S), y), "KRISHNA MUDGAL", font=serif, anchor="ls", fill=(244, 222, 204))
        x2 = self.pad + round(2 * S) + d.textlength("KRISHNA MUDGAL", font=serif) + round(10 * S)
        d.text((x2, y), "AI RESEARCHER", font=font("georgia.ttf", round(11 * S)), anchor="ls", fill=(176, 160, 214))
        d.text((W - self.pad - round(2 * S), y), "ep.01  夢落ち", font=jp, anchor="rs", fill=(150, 136, 190))
        return bg

    def film_mask(self):
        m = Image.new("L", (self.FW, self.FH), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, self.FW - 1, self.FH - 1), round(8 * self.S), fill=255)
        return m

    def compose(self, film, progress):
        f = np.asarray(film, np.float32) * self.vig
        film = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))
        out = self.bg.copy()
        out.paste(film, (self.pad, self.pad), self.mask)
        d = ImageDraw.Draw(out)
        y = self.pad + self.FH + round(5 * self.S)
        x0, x1 = self.pad, self.pad + self.FW
        d.line((x0, y, x1, y), fill=(44, 38, 64), width=max(1, round(2 * self.S)))
        d.line((x0, y, x0 + (x1 - x0) * progress, y), fill=(242, 163, 122), width=max(1, round(2 * self.S)))
        return out


# ---------------------------------------------------------------- output
def render(scale, fps):
    card = Card(scale)
    n = int(TOTAL * fps)
    frames, keys = [], []
    for k in range(n):
        tg = k / fps
        film, i = film_frame(tg, card.FW, card.FH)
        frames.append(card.compose(film, min(tg / TOTAL, 1)))
        keys.append(i)
    print(f"{n} frames, {TOTAL:.1f}s, card {card.W}x{card.H}")
    return frames, keys, card


def save_gif(frames, keys, fps, path, dither=True):
    # one palette per shot (local colour tables) -> no palette flicker within a shot
    pals = {}
    for key in sorted(set(keys)):
        idx = [j for j, k in enumerate(keys) if k == key]
        sample = [frames[j] for j in idx[:: max(1, len(idx) // 6)]][:6]
        w, hh = sample[0].size
        strip = Image.new("RGB", (w, hh * len(sample)))
        for j, s in enumerate(sample):
            strip.paste(s, (0, j * hh))
        pals[key] = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pals[k], dither=Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE) for f, k in zip(frames, keys)]
    q[0].save(path, save_all=True, append_images=q[1:], duration=round(1000 / fps), loop=0, optimize=False, disposal=1)
    print(path.name, f"{path.stat().st_size / 1e6:.2f} MB")


def save_webp(frames, fps, path, quality):
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=round(1000 / fps),
                   loop=0, quality=quality, method=4)
    print(path.name, f"{path.stat().st_size / 1e6:.2f} MB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--fps", type=float, default=TL["fps"])
    ap.add_argument("--only", default="all")
    ap.add_argument("--quality", type=int, default=78)
    ap.add_argument("--suffix", default="")
    ap.add_argument("--nodither", action="store_true")
    a = ap.parse_args()
    frames, keys, card = render(a.scale, a.fps)
    # contact sheet of every ~1s for QA
    step = max(1, round(a.fps))
    pick = frames[::step]
    tw, th = card.W // 3, card.H // 3
    cols = 6
    sheet = Image.new("RGB", (cols * tw, ((len(pick) + cols - 1) // cols) * th))
    for j, f in enumerate(pick):
        sheet.paste(f.resize((tw, th)), ((j % cols) * tw, (j // cols) * th))
    sheet.save(ROOT / "assets" / "previews" / f"timeline_contact{a.suffix}.jpg", quality=85)
    # poster = reveal hold
    ri = next(k for k, s in enumerate(SHOTS) if s["id"] == "reveal")
    frames[int((starts[ri] + 2.4) * a.fps)].convert("RGB").save(PUB / f"poster{a.suffix}.jpg", quality=92)
    if a.only in ("all", "gif"):
        save_gif(frames, keys, a.fps, PUB / f"animation{a.suffix}.gif", not a.nodither)
    if a.only in ("all", "webp"):
        save_webp(frames, a.fps, PUB / f"animation{a.suffix}.webp", a.quality)


if __name__ == "__main__":
    main()
