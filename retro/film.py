"""Dreamfall (retro cut): a fully code-drawn pixel-art short.

Everything is drawn procedurally at 320x135 with a fixed palette, then
scaled 3x with nearest-neighbour. No source images are used.

    python retro/film.py            # full render -> public/retro.gif (+ .webp)
    python retro/film.py --sheet    # contact sheet only (fast QA)
    python retro/film.py --at 12.5  # single frame png
"""
import argparse
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
PREV = ROOT / "assets" / "previews"
W, H, FPS, UP = 320, 135, 12, 3

# ------------------------------------------------------------------ palette
PAL = {
    "ink": "0b0915", "gh": "0d1117", "frame": "544878",
    # dusk sky, top -> horizon
    "s0": "251a44", "s1": "3d2763", "s2": "6a3673", "s3": "a24c78", "s4": "d86b6e", "s5": "f29a6a", "s6": "ffcb87",
    "sun": "fff0c4",
    # night / dream
    "n0": "0e0b22", "n1": "17123a", "n2": "221a52",
    "grid": "6d5cf0", "gridhi": "c4b5ff", "node": "ffd08a", "pink": "ff9ec8", "star": "ffffff",
    # land
    "ruin0": "4a3270", "ruin1": "34245a", "hill": "281d47", "ground": "1c1534", "grass": "33275a", "tuft": "4f3d7e",
    "rock": "3d2f52", "rockhi": "5d4a78", "rockdk": "251c36",
    # character
    "hair": "141020", "hood": "2c2340", "hoodhi": "4a3c66", "hoodd": "1f1930", "skin": "e6a780", "skinsh": "b8785c",
    "pants": "221b34", "pantsd": "17122a", "shoe": "efe5d4", "shoesh": "a39488", "glint": "d9ecff",
    # room
    "wall": "3b2d4d", "walllit": "6d4c60", "floor": "2a2036", "plank": "211a2c", "winA": "ffc98a", "winB": "ffe2a8",
    "sheet": "8c7cab", "sheetsh": "5f5384", "pillow": "dccfe8", "wood": "5c3e3c", "wooddk": "3b2729",
    "laptop": "2d2c40", "screen": "8fd3ff", "leaf": "4a8a62", "leafdk": "2d5a42",
    "paper": "f1e8d8", "papersh": "cfc2ae", "txt": "2a2040", "txt2": "8a7fa6",
}
RGB = {k: tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) for k, v in PAL.items()}
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 + 1 / 32


def C(n):
    return RGB[n]


def frac(x):
    return x - math.floor(x)


def hsh(i, k=0):
    return frac(math.sin(i * 12.9898 + k * 78.233) * 43758.5453)


def clamp(x, a=0.0, b=1.0):
    return min(max(x, a), b)


def ease(p):
    p = clamp(p)
    return p * p * (3 - 2 * p)


def bayer_mask(k, w=W, h=H):
    """boolean mask with fraction k of pixels set, ordered-dither pattern"""
    tile = BAYER < k
    return np.tile(tile, (h // 4 + 1, w // 4 + 1))[:h, :w]


def bayer_mix(a, b, k):
    """pixel-select blend of two images (retro dissolve, no new colours)"""
    A, B = np.asarray(a), np.asarray(b)
    m = bayer_mask(k, A.shape[1], A.shape[0])
    return Image.fromarray(np.where(m[..., None], B, A))


@lru_cache(maxsize=64)
def gradient(colors, w=W, h=H, y0=0, y1=None):
    """vertical ordered-dither gradient through a tuple of palette names"""
    y1 = h if y1 is None else y1
    arr = np.zeros((h, w, 3), np.uint8)
    n = len(colors) - 1
    for y in range(h):
        t = clamp((y - y0) / max(1, (y1 - y0))) * n
        i = min(int(t), n - 1)
        f = t - i
        row = np.where((BAYER[y % 4][np.arange(w) % 4] < f)[:, None], C(colors[i + 1]), C(colors[i]))
        arr[y] = row
    return Image.fromarray(arr)


# ------------------------------------------------------------------ bitmap font (5x7)
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "G": ["01111", "10000", "10000", "10011", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "0": ["01110", "10011", "10101", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    " ": ["00000"] * 7,
}


def text(d, x, y, s, color, scale=1):
    for ch in s:
        g = FONT[ch]
        for r, row in enumerate(g):
            for c, v in enumerate(row):
                if v == "1":
                    d.rectangle((x + c * scale, y + r * scale, x + (c + 1) * scale - 1, y + (r + 1) * scale - 1), fill=C(color))
        x += 6 * scale


# ------------------------------------------------------------------ character
HEAD = [  # 8x9, facing right. K hair, S skin, s shade, g glasses glint, H hoodie
    ".KKKKK..",
    "KKKKKKK.",
    "KKKKKKKK",
    "KKKKSKSK",
    "KKKSKggK",
    "KKSSSSSS",
    ".KsSSSSs",
    "..sSSSs.",
    "..HHH...",
]
HEAD_KEYS = {"K": "hair", "S": "skin", "s": "skinsh", "g": "glint", "H": "hood"}


@lru_cache(maxsize=256)
def head_sprite(scale, angle, flip):
    im = Image.new("RGBA", (8, 9), (0, 0, 0, 0))
    px = im.load()
    for y, row in enumerate(HEAD):
        for x, ch in enumerate(row):
            if ch != ".":
                px[x, y] = C(HEAD_KEYS[ch]) + (255,)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = im.resize((8 * scale, 9 * scale), Image.NEAREST)
    if angle:
        im = im.rotate(angle, resample=Image.NEAREST, expand=True)
    return im


def vdown(a, L):
    r = math.radians(a)
    return (L * math.sin(r), L * math.cos(r))


def vup(a, L):
    r = math.radians(a)
    return (L * math.sin(r), -L * math.cos(r))


def draw_char(img, hip, pose, s=1, facing=1, rot=0.0, hide_below=None):
    """pose: torso, head, thA knA thB knB arA elA arB elB (degrees, 0 = down/up, + = forward)"""
    d = ImageDraw.Draw(img)
    P = {}
    neck = vup(pose["torso"], 9 * s)
    sh = (neck[0] * 0.86, neck[1] * 0.86)
    hc = vup(pose["torso"], 9 * s + 3.6 * s)
    P["neck"], P["sh"], P["hc"] = neck, sh, hc
    shoes = {}
    for L in "AB":
        th, kn = pose["th" + L], pose["kn" + L]
        k = vdown(th, 7 * s)
        f = vdown(th + kn, 7 * s)
        foot = (k[0] + f[0], k[1] + f[1])
        toe = vdown(th + kn + 90, 2.6 * s)
        P["knee" + L], P["foot" + L] = k, foot
        P["toe" + L] = (foot[0] + toe[0], foot[1] + toe[1])
    for A in "AB":
        e = vdown(pose["ar" + A], 5 * s)
        el = (sh[0] + e[0], sh[1] + e[1])
        hd = vdown(pose["ar" + A] + pose["el" + A], 4.6 * s)
        P["elb" + A], P["hand" + A] = el, (el[0] + hd[0], el[1] + hd[1])
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def T(p):
        x, y = p
        x2, y2 = x * cr - y * sr, x * sr + y * cr
        return (hip[0] + facing * x2, hip[1] + y2)

    Q = {k: T(v) for k, v in P.items()}
    Q["hip"] = hip

    def limb(a, b, c, w, col):
        d.line([Q[a], Q[b], Q[c]], fill=C(col), width=w, joint="curve")

    lw, aw = max(2, round(2.6 * s)), max(1, round(1.8 * s))
    # back arm + back leg
    limb("sh", "elbB", "handB", aw, "hoodd")
    d.line([Q["footB"], Q["toeB"]], fill=C("shoesh"), width=max(2, 2 * s))
    limb("hip", "kneeB", "footB", lw, "pantsd")
    # torso
    d.line([Q["hip"], Q["neck"]], fill=C("hood"), width=max(3, round(4.6 * s)))
    hx, hy = Q["neck"]
    # front leg
    limb("hip", "kneeA", "footA", lw, "pants")
    d.line([Q["footA"], Q["toeA"]], fill=C("shoe"), width=max(2, 2 * s))
    # head
    ang = -(pose["torso"] + pose.get("head", 0) + rot) * facing
    hs = head_sprite(s, int(round(ang / 5) * 5) % 360, facing < 0)
    cx, cy = Q["hc"]
    img.paste(hs, (round(cx - hs.width / 2), round(cy - hs.height / 2)), hs)
    # front arm + hands
    limb("sh", "elbA", "handA", aw, "hoodhi")
    for hnd in ("handA", "handB"):
        x, y = Q[hnd]
        r = max(1, s) * 0.9
        d.ellipse((x - r, y - r, x + r, y + r), fill=C("skin"))
    return Q


def run_pose(ph, lean=14):
    def leg(p):
        return 40 * math.sin(p), -14 - 72 * max(0.0, math.cos(p))
    thA, knA = leg(ph)
    thB, knB = leg(ph + math.pi)
    return dict(torso=lean, head=-6, thA=thA, knA=knA, thB=thB, knB=knB,
                arA=-48 * math.sin(ph), elA=85, arB=48 * math.sin(ph), elB=85)


def fall_pose(t):
    return dict(torso=8 * math.sin(t * 5), head=-20, thA=40 + 22 * math.sin(t * 7), knA=-75,
                thB=-5 + 22 * math.sin(t * 7 + 2), knB=-45,
                arA=155 + 28 * math.sin(t * 9), elA=-25, arB=-150 + 28 * math.sin(t * 9 + 1.3), elB=20)


def float_pose(t):
    w = math.sin(t * 1.6)
    return dict(torso=4 * w, head=-10, thA=24 + 4 * w, knA=-18, thB=-18 - 4 * w, knB=-12,
                arA=118 + 8 * w, elA=12, arB=-112 - 8 * w, elB=-12)


def lerp_pose(a, b, p):
    return {k: a.get(k, 0) + (b.get(k, 0) - a.get(k, 0)) * p for k in set(a) | set(b)}


# ------------------------------------------------------------------ scenery
def sun(d, cx, cy, r):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=C("sun"))
    for i, yy in enumerate(range(int(cy + 2), int(cy + r + 1), 3)):  # retro stripes
        d.line((cx - r, yy, cx + r, yy), fill=C("s5"), width=1 + i // 2)


def clouds(d, scroll, y, seed, col, n=6, spread=420):
    for i in range(n):
        w = 30 + 40 * hsh(i, seed)
        x = ((hsh(i, seed + 1) * spread - scroll) % spread) - 60
        yy = y + 18 * hsh(i, seed + 2)
        d.rounded_rectangle((x, yy, x + w, yy + 4), 2, fill=C(col))
        d.rounded_rectangle((x + w * 0.2, yy - 3, x + w * 0.7, yy + 2), 2, fill=C(col))


def ruins(d, scroll, base, col, seed, density=1.0, tall=40, period=520):
    for i in range(int(14 * density)):
        x = ((hsh(i, seed) * period - scroll) % period) - 40
        w = 8 + 16 * hsh(i, seed + 3)
        h = tall * (0.35 + 0.65 * hsh(i, seed + 4))
        d.rectangle((x, base - h, x + w, base), fill=C(col))
        for k in range(int(w // 4)):  # crenellations
            if k % 2 == 0:
                d.rectangle((x + k * 4, base - h - 3, x + k * 4 + 2, base - h), fill=C(col))
        if hsh(i, seed + 5) > 0.5 and w > 14:  # arch window
            d.rectangle((x + w / 2 - 2, base - h * 0.6, x + w / 2 + 1, base - h * 0.35), fill=C("s3" if col == "ruin0" else "s2"))


def hills(d, scroll, base, amp, col, seed):
    pts = [(0, H)]
    for x in range(0, W + 8, 8):
        X = x + scroll
        y = base - amp * (0.5 + 0.3 * math.sin(X * 0.013 + seed) + 0.2 * math.sin(X * 0.031 + seed * 2))
        pts.append((x, y))
    pts.append((W, H))
    d.polygon(pts, fill=C(col))


def tree(d, x, base):
    d.polygon([(x - 3, base), (x + 4, base), (x + 2, base - 30), (x - 1, base - 30)], fill=C("ink"))
    d.line([(x, base - 22), (x - 14, base - 34)], fill=C("ink"), width=2)
    d.line([(x + 2, base - 26), (x + 16, base - 40)], fill=C("ink"), width=2)
    for i in range(14):
        cx = x - 22 + 46 * hsh(i, 70)
        cy = base - 34 - 18 * hsh(i, 71)
        r = 6 + 6 * hsh(i, 72)
        d.ellipse((cx - r, cy - r * 0.7, cx + r, cy + r * 0.7), fill=C("ink" if i % 3 else "hill"))


def ground(d, scroll, gy, edge=None):
    x1 = W if edge is None else min(W, edge)
    if x1 <= 0:
        return
    d.rectangle((0, gy, x1, H), fill=C("ground"))
    d.line((0, gy, x1, gy), fill=C("grass"), width=2)
    for i in range(40):
        x = ((hsh(i, 40) * 400 - scroll) % 400) - 20
        if x > x1 - 2:
            continue
        hgt = 2 + 3 * hsh(i, 41)
        d.line((x, gy, x - 1, gy - hgt), fill=C("tuft"))
        d.line((x + 1, gy, x + 2, gy - hgt + 1), fill=C("tuft"))
        if hsh(i, 42) > 0.6:
            d.rectangle((x + 4, gy + 4 + 8 * hsh(i, 43), x + 7, gy + 6 + 8 * hsh(i, 43)), fill=C("grass"))


def cliff_face(d, edge, gy, scroll_y=0.0, slope=0.12):
    """cliff wall dropping from the ground edge"""
    pts = [(edge - 400, gy), (edge, gy)]
    for k in range(0, H - int(gy) + 400, 6):
        jag = 4 * math.sin((k + scroll_y) * 0.21) + 3 * math.sin((k + scroll_y) * 0.07)
        pts.append((edge - 6 - k * slope + jag, gy + k))
    pts += [(edge - 400, H + 400)]
    d.polygon(pts, fill=C("rock"))
    for i in range(60):  # texture blocks
        yy = gy + ((hsh(i, 90) * 300 - scroll_y) % 300)
        xx = edge - 10 - (yy - gy) * slope - 60 * hsh(i, 91)
        col = "rockhi" if hsh(i, 92) > 0.5 else "rockdk"
        d.rectangle((xx, yy, xx + 2 + 4 * hsh(i, 93), yy + 1), fill=C(col))


def creature(img, cx, cy, t, scale=1.0):
    d = ImageDraw.Draw(img)
    for k in range(6):  # tendrils trailing left
        pts = []
        for j in range(9):
            x = cx - j * 6 * scale
            y = cy - 6 * scale + k * 3 * scale + math.sin(t * 7 + j * 0.9 + k) * (1 + j * 0.7) * scale
            pts.append((x, y))
        d.line(pts, fill=C("ink"), width=max(1, round((3 - k % 2) * scale)))
    for j in range(5):
        r = (7 + 2 * math.sin(t * 6 + j)) * scale
        ox = (j - 2) * 4 * scale
        oy = math.sin(t * 5 + j * 1.7) * 2 * scale
        d.ellipse((cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r), fill=C("ink"))
    if frac(t / 1.7) > 0.08:  # blink
        for ex in (3, 8):
            d.rectangle((cx + ex * scale, cy - 3 * scale, cx + (ex + 2) * scale - 1, cy - 2 * scale), fill=C("node"))


def leaves(d, t, n=14, seed=5, col="ink", speed=1.0):
    for i in range(n):
        x = (hsh(i, seed) * W * 1.2 - t * (60 + 50 * hsh(i, seed + 1)) * speed) % (W * 1.2) - 20
        y = (hsh(i, seed + 2) * H + math.sin(t * 3 + i) * 6) % H
        if int(t * 8 + i) % 2:
            d.rectangle((x, y, x + 1, y), fill=C(col))
        else:
            d.rectangle((x, y, x, y + 1), fill=C(col))


# ------------------------------------------------------------------ scenes
DUSK = ("s0", "s1", "s2", "s3", "s4", "s5", "s6")


def chase_bg(t, scroll, gy, edge=None, with_tree=True):
    img = gradient(DUSK, y1=gy + 6).copy()
    d = ImageDraw.Draw(img)
    sun(d, 236, gy - 26, 15)
    clouds(d, scroll * 0.05, 14, 1, "s2", n=7)
    clouds(d, scroll * 0.09, 30, 2, "s3", n=6)
    ruins(d, scroll * 0.18, gy - 18, "ruin0", 3, density=0.55, tall=34)
    hills(d, scroll * 0.35, gy - 4, 26, "ruin1", 1.3)
    ruins(d, scroll * 0.45, gy - 2, "hill", 7, density=0.35, tall=26)
    if with_tree:
        tx = 60 - scroll
        if -60 < tx < W + 60:
            tree(d, tx, gy)
    ground(d, scroll, gy, edge)
    return img, d


def scene_chase_wide(t):
    gy = 112
    v = 95
    img, d = chase_bg(t, t * v, gy)
    ph = t * 2 * math.pi * 2.3
    bob = -1.2 * max(0.0, math.cos(2 * ph))
    draw_char(img, (176, gy - 12.3 + bob), run_pose(ph), s=1)
    creature(img, 92 + 10 * math.sin(t * 1.3) + min(t, 3) * 4, gy - 22 + 3 * math.sin(t * 2.1), t)
    leaves(d, t)
    return img


def scene_chase_close(t):
    gy = 124
    v = 190
    img = gradient(DUSK, y1=gy).copy()
    d = ImageDraw.Draw(img)
    sun(d, 250, gy - 40, 22)
    clouds(d, t * v * 0.06, 10, 4, "s2", n=7)
    clouds(d, t * v * 0.1, 28, 6, "s3", n=6)
    ruins(d, t * v * 0.22, gy - 26, "ruin0", 11, density=0.5, tall=50)
    hills(d, t * v * 0.4, gy - 6, 30, "ruin1", 2.1)
    ground(d, t * v, gy)
    ph = t * 2 * math.pi * 2.0
    bob = -2.4 * max(0.0, math.cos(2 * ph))
    draw_char(img, (172, gy - 24.6 + bob), run_pose(ph, lean=16), s=2)
    creature(img, 36 + 8 * math.sin(t * 2), gy - 52 + 4 * math.sin(t * 3), t, scale=2.0)
    leaves(d, t, n=20, speed=2.0)
    for i in range(10):  # foreground grass blur
        x = ((hsh(i, 61) * 500 - t * v * 1.4) % 500) - 40
        d.polygon([(x, H), (x + 6, H - 12 - 8 * hsh(i, 62)), (x + 10, H)], fill=C("ink"))
    return img


CLIFF_T0 = 0.0


def scene_cliff(t):
    """camera tracks, stops when the edge arrives; he runs off, hangs, and drops."""
    gy, v = 112, 95
    edge_world = 380
    cam = min(t * v, edge_world - 215)
    edge = edge_world - cam
    img, d = chase_bg(t, cam, gy, edge=edge, with_tree=False)
    # the abyss beyond the edge: misty drop with floating ruins far below
    abyss = gradient(("s4", "s3", "s2", "s1", "s0"), w=W, h=H, y0=gy, y1=H)
    A, B = np.asarray(img).copy(), np.asarray(abyss)
    xs_ = np.arange(W)[None, :]
    ys_ = np.arange(H)[:, None]
    m = (xs_ > edge) & (ys_ > gy - 1)
    A[m] = B[m]
    img = Image.fromarray(A)
    d = ImageDraw.Draw(img)
    for i in range(7):
        x = edge + 18 + i * 19 + 6 * hsh(i, 3)
        top = gy + 2 + 14 * hsh(i, 4)
        col = "ruin0" if i % 2 else "s2"
        d.polygon([(x, top), (x + 8, top), (x + 6, top + 10), (x + 4, top + 16), (x + 2, top + 10)], fill=C(col))
        d.rectangle((x + 2, top - 6 - 6 * hsh(i, 5), x + 5, top), fill=C(col))
    # cliff mass: rock under the grass, jagged face at the edge
    d.rectangle((0, gy + 3, edge, H), fill=C("rock"))
    face = [(edge, gy)]
    for k in range(0, H - gy + 4, 4):
        face.append((edge - 2 - k * 0.25 + 2 * math.sin(k * 0.6), gy + k))
    face += [(edge - 60, H), (edge - 60, gy)]
    d.polygon(face, fill=C("rock"))
    for i in range(40):
        xx = edge - 8 - 220 * hsh(i, 91)
        yy = gy + 6 + (H - gy - 8) * hsh(i, 90)
        if xx < edge - 4 - (yy - gy) * 0.25:
            d.rectangle((xx, yy, xx + 2 + 4 * hsh(i, 93), yy), fill=C("rockhi" if hsh(i, 92) > 0.5 else "rockdk"))
    d.line([(edge, gy), (edge - 2 - (H - gy) * 0.25, H)], fill=C("rockhi"))
    d.rectangle((0, gy, edge, gy + 3), fill=C("ground"))
    d.line((0, gy, edge, gy), fill=C("grass"), width=2)
    ph = t * 2 * math.pi * 2.3
    t_off = (edge_world - 176) / v
    xs = 176 + t * v - cam
    if t < t_off:
        bob = -1.2 * max(0.0, math.cos(2 * ph))
        draw_char(img, (xs, gy - 12.3 + bob), run_pose(ph), s=1)
    else:
        u = t - t_off
        hang = 0.45
        xs = edge + min(u, hang) * v * 0.5 + max(0.0, u - hang) * 30
        if u < hang:  # cartoon beat: legs still pumping in the air, looking down
            pose = run_pose(ph * 1.5)
            pose["head"] = 30
            draw_char(img, (xs, gy - 12.3), pose, s=1)
        else:
            k = u - hang
            y = gy - 12.3 + 0.5 * 300 * k * k
            pose = lerp_pose(run_pose(ph), fall_pose(t), ease(k * 3))
            draw_char(img, (xs, y), pose, s=1, rot=-30 * ease(k * 2))
    cx = min(92 + t * 38, edge - 36)
    creature(img, cx + 6 * math.sin(t * 1.3), gy - 22 + 3 * math.sin(t * 2.1), t)
    leaves(d, t)
    return img


FALL_DUSK = ("s0", "s1", "s2", "s3", "s4", "s5")
FALL_DEEP = ("n0", "n1", "n2", "s1", "s2", "s3")
NIGHT = ("n0", "n0", "n1", "n2", "s0", "s1")


def debris(d, t, n, seed, vy, scale=1):
    for i in range(n):
        x = 40 + hsh(i, seed) * 260 + math.sin(t * 2 + i) * 4
        y = (hsh(i, seed + 1) * (H + 40) - t * vy * (0.3 + 0.7 * hsh(i, seed + 2))) % (H + 40) - 20
        r = (1 + 2 * hsh(i, seed + 3)) * scale
        d.polygon([(x - r, y), (x, y - r), (x + r, y + r * 0.4), (x - r * 0.3, y + r)], fill=C("rockdk" if i % 2 else "rock"))


def speedlines(d, t, n=16, col="s4"):
    for i in range(n):
        x = hsh(i, 33) * W
        L = 8 + 14 * hsh(i, 34)
        y = (hsh(i, 35) * (H + 40) - t * 420) % (H + 40) - 20
        d.line((x, y, x, y + L), fill=C(col))


def scene_fall_close(t):
    dk = clamp(t / 2.4)
    img = bayer_mix(gradient(FALL_DUSK), gradient(FALL_DEEP), dk * 0.6)
    d = ImageDraw.Draw(img)
    cliff_face(d, 44, -400, scroll_y=t * 300, slope=0.0)
    speedlines(d, t)
    debris(d, t, 10, 7, 160, scale=2)
    draw_char(img, (170 + 6 * math.sin(t * 2), 68 + 3 * math.sin(t * 3)), fall_pose(t), s=2, rot=t * 140 + 20)
    debris(d, t + 3, 4, 17, 260, scale=3)
    return img


def ai_world(t, char=None):
    img = gradient(("n0", "n1", "n2", "n1"), y1=H).copy()
    d = ImageDraw.Draw(img)
    for i in range(55):  # stars
        x, y = hsh(i, 101) * W, hsh(i, 102) * H * 0.7
        if math.sin(t * 2.4 + i) > -0.3:
            d.point((x, y), fill=C("star" if i % 5 == 0 else "gridhi"))
    # wireframe loss landscape
    cam_z = 3.2 + t * 0.15
    def proj(x, y, z):
        zz = z - 0.0 + 4.0
        return (W / 2 + x * 120 / zz, 92 + (y + 1.4) * 70 / zz - 30)
    nx, nz = 22, 12
    grid = {}
    for i in range(nx):
        for j in range(nz):
            x = (i - nx / 2) * 0.55
            z = j * 0.55 - frac(t * 0.2) * 0.55
            hgt = 0.55 * math.sin(x * 0.9 + t * 0.6) * math.cos(z * 0.8) - 0.9 * math.exp(-(x * x + (z - 2.5) ** 2) / 2.5)
            grid[i, j] = proj(x, -hgt, z)
    for (i, j), p in grid.items():
        col = "gridhi" if j < 3 else "grid"
        if (i + 1, j) in grid:
            d.line([p, grid[i + 1, j]], fill=C(col))
        if (i, j + 1) in grid:
            d.line([p, grid[i, j + 1]], fill=C(col))
    # rotating wireframe cubes
    for ci, (cx, cy, sz, sp) in enumerate([(52, 34, 13, 0.9), (268, 40, 10, -1.2), (226, 18, 6, 1.6)]):
        a, b = t * sp, t * sp * 0.7 + ci
        V = []
        for vx in (-1, 1):
            for vy in (-1, 1):
                for vz in (-1, 1):
                    x1 = vx * math.cos(a) - vz * math.sin(a)
                    z1 = vx * math.sin(a) + vz * math.cos(a)
                    y1 = vy * math.cos(b) - z1 * math.sin(b)
                    z2 = vy * math.sin(b) + z1 * math.cos(b)
                    f = 3 / (3 + z2 * 0.5)
                    V.append((cx + x1 * sz * f, cy + y1 * sz * f))
        for e1 in range(8):
            for e2 in range(e1 + 1, 8):
                if bin(e1 ^ e2).count("1") == 1:
                    d.line([V[e1], V[e2]], fill=C("gridhi" if ci == 0 else "grid"))
    # neural net with travelling pulses
    layers = [[(118, 14), (118, 30), (118, 46)], [(142, 8), (142, 22), (142, 36), (142, 50)], [(166, 20), (166, 38)]]
    for la in range(2):
        for a_ in layers[la]:
            for b_ in layers[la + 1]:
                d.line([a_, b_], fill=C("n2"))
    for k in range(6):
        la = k % 2
        a_ = layers[la][k % len(layers[la])]
        b_ = layers[la + 1][(k * 3) % len(layers[la + 1])]
        p = frac(t * 0.9 + k * 0.37)
        d.point((a_[0] + (b_[0] - a_[0]) * p, a_[1] + (b_[1] - a_[1]) * p), fill=C("pink"))
    for L in layers:
        for (x, y) in L:
            d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=C("node"))
    return img, d


def scene_fall_wide(t):
    """falling past the cliff, sky darkens, glowing boundary sweeps up into the AI world"""
    dk = clamp(t / 3.0)
    img = bayer_mix(gradient(FALL_DEEP), gradient(NIGHT), dk)
    d = ImageDraw.Draw(img)
    cliff_face(d, 56, -400, scroll_y=300 + t * 160, slope=0.0)
    ruins(d, 0, H + 10 - t * 18, "n2", 21, tall=45)
    speedlines(d, t, n=10, col="s2")
    debris(d, t, 14, 9, 120)
    cx, cy = 186 + 4 * math.sin(t * 2), 56 + t * 4
    draw_char(img, (cx, cy), fall_pose(t), s=1, rot=t * 120)
    tb = 2.4  # boundary sweep
    if t > tb:
        k = (t - tb) / 1.3
        ai, _ = ai_world(t)
        yb = np.array([H + 6 - k * (H + 20) + 3 * math.sin(x * 0.07 + t * 7) for x in range(W)])
        A, B = np.asarray(img).copy(), np.asarray(ai)
        ys = np.arange(H)[:, None]
        m = ys > yb[None, :]
        A[m] = B[m]
        img = Image.fromarray(A)
        d = ImageDraw.Draw(img)
        d.line([(x, yb[x]) for x in range(W)], fill=C("gridhi"))
        d.line([(x, yb[x] + 1) for x in range(W)], fill=C("star"))
        if k > 0.55:  # character re-drawn on top once he is through
            draw_char(img, (cx, cy), fall_pose(t), s=1, rot=t * 120)
    return img


def scene_ai(t, dur):
    img, d = ai_world(t + 4)
    y = 14 + 22 * ease(t / dur) + 3 * math.sin(t * 1.4)
    draw_char(img, (W / 2 + 40, y + 20), float_pose(t), s=2, rot=12 * math.sin(t * 0.8))
    # glowing particles rising
    for i in range(16):
        x = hsh(i, 120) * W
        yy = (hsh(i, 121) * H - t * 18) % H
        d.point((x, yy), fill=C("pink" if i % 3 else "node"))
    return img


def room(t, light=1.0):
    img = Image.new("RGB", (W, H), C("wall"))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 116, W, H), fill=C("floor"))
    for x in range(0, W + 20, 28):
        d.line((x, 116, x - 12, H), fill=C("plank"))
    # window with sunrise
    win = gradient(("s4", "s5", "winA", "winB"), w=68, h=54)
    img.paste(win, (216, 12))
    d.ellipse((252, 46, 276, 70), fill=C("sun"))
    d.rectangle((216, 60, 284, 66), fill=C("s5"))
    d.rectangle((214, 10, 285, 67), outline=C("wooddk"), width=2)
    d.line((250, 10, 250, 67), fill=C("wooddk"), width=2)
    d.line((214, 38, 285, 38), fill=C("wooddk"), width=2)
    d.rectangle((210, 66, 289, 69), fill=C("wood"))
    # dithered sunlight falling across wall and floor
    pm = Image.new("L", (W, H), 0)
    ImageDraw.Draw(pm).polygon([(216, 69), (284, 69), (196, 135), (96, 135)], fill=255)
    A = np.asarray(img).copy()
    m = (np.asarray(pm) > 0) & bayer_mask(0.4 * light)
    is_bg = np.all(A == C("wall"), axis=2) | np.all(A == C("floor"), axis=2)
    A[m & is_bg] = C("walllit")
    img = Image.fromarray(A)
    d = ImageDraw.Draw(img)
    # shelf of books above the bed
    d.rectangle((70, 50, 152, 53), fill=C("wood"))
    x = 74
    while x < 148:
        w = 3 + int(3 * hsh(x, 2))
        hh = 12 + int(6 * hsh(x, 5))
        col = ["s3", "s5", "grid", "sheet", "leaf", "s4", "node"][int(7 * hsh(x, 8))]
        d.rectangle((x, 50 - hh, x + w - 1, 49), fill=C(col))
        x += w + 1
    # poster: a little network diagram
    d.rectangle((166, 18, 198, 44), fill=C("paper"))
    pts = [(173, 31), (182, 24), (182, 38), (191, 31)]
    for i1, i2 in [(0, 1), (0, 2), (1, 3), (2, 3), (1, 2)]:
        d.line([pts[i1], pts[i2]], fill=C("txt2"))
    for q in pts:
        d.rectangle((q[0] - 1, q[1] - 1, q[0] + 1, q[1] + 1), fill=C("s3"))
    # desk, glowing laptop, plant
    d.rectangle((228, 92, 318, 96), fill=C("wood"))
    d.rectangle((232, 96, 235, 116), fill=C("wooddk"))
    d.rectangle((312, 96, 315, 116), fill=C("wooddk"))
    d.polygon([(250, 91), (284, 91), (280, 70), (254, 70)], fill=C("laptop"))
    d.rectangle((257, 73, 277, 87), fill=C("screen"))
    for k in range(4):
        d.line((259, 75 + k * 3, 262 + int(10 * hsh(k, 3)), 75 + k * 3), fill=C("grid"))
    d.rectangle((296, 82, 306, 92), fill=C("wooddk"))
    for k in range(6):
        d.ellipse((292 + k * 3 - 4, 68 + (k % 2) * 5, 292 + k * 3 + 4, 78 + (k % 2) * 5), fill=C("leaf" if k % 2 else "leafdk"))
    # bed
    d.rectangle((20, 72, 27, 116), fill=C("wooddk"))
    d.rectangle((24, 104, 222, 112), fill=C("wood"))
    d.rectangle((26, 112, 31, 116), fill=C("wooddk"))
    d.rectangle((215, 112, 220, 116), fill=C("wooddk"))
    d.rectangle((24, 97, 222, 104), fill=C("sheetsh"))
    d.rounded_rectangle((28, 88, 66, 100), 4, fill=C("pillow"))
    d.line((32, 98, 62, 98), fill=C("sheet"))
    return img


def blanket(img, sit=0.0):
    d = ImageDraw.Draw(img)
    x0 = 68 + 26 * sit
    top = 90 + 4 * sit
    d.polygon([(x0, 104), (x0 + 4, top + 3), (120, top - 2), (170, top), (214, top + 3), (222, 104)], fill=C("sheet"))
    d.line([(x0 + 8, top + 6), (216, top + 8)], fill=C("sheetsh"))
    d.line([(140, top), (150, 103)], fill=C("sheetsh"))
    d.line([(184, top + 1), (190, 103)], fill=C("sheetsh"))


def bang(img, x, y):
    d = ImageDraw.Draw(img)
    d.rectangle((x - 3, y - 3, x + 12, y + 23), fill=C("ink"))
    text(d, x - 1, y, "!", "node", scale=3)


def paper_small(d, x, y, w=12, h=9, col="paper"):
    d.rectangle((x, y, x + w, y + h), fill=C(col))
    d.line((x + 3, y + 3, x + w - 3, y + 3), fill=C("txt"))
    for k in range(1, int((h - 3) / 3)):
        d.line((x + 3, y + 3 + k * 3, x + w - 3 - 3 * (k % 2), y + 3 + k * 3), fill=C("txt2"))


def scene_room(t):
    img = room(t)
    d = ImageDraw.Draw(img)
    hip = (84, 101)
    lying = dict(torso=-88, head=-4, thA=88, knA=0, thB=90, knB=0, arA=-84, elA=0, arB=-84, elB=0)
    sitting = dict(torso=-2, head=6, thA=88, knA=0, thB=90, knB=0, arA=28, elA=36, arB=20, elB=44)
    reach = dict(sitting, torso=14, head=24, arA=64, elA=6)
    hold = dict(sitting, torso=4, head=26, arA=54, elA=-48, arB=46, elB=-40)
    paper_on_bed = t < 3.35
    sit = ease((t - 1.4) / 0.45) if t > 1.4 else 0.0
    if t < 1.4:  # asleep, breathing
        pose = dict(lying)
        pose["torso"] += 1.2 * math.sin(t * 3)
    elif t < 1.85:  # jolt awake
        pose = lerp_pose(lying, sitting, sit)
    elif t < 2.7:  # looks around
        pose = dict(sitting)
        pose["head"] = 6 + 10 * math.sin((t - 1.85) * 6) * max(0.0, 1 - (t - 1.85))
    elif t < 3.35:
        pose = lerp_pose(sitting, reach, ease((t - 2.7) / 0.6))
    else:
        pose = lerp_pose(reach, hold, ease((t - 3.35) / 0.6))
    if paper_on_bed:
        paper_small(d, 102, 88, w=18, h=5)
    Q = draw_char(img, hip, pose, s=3)
    blanket(img, sit)
    if not paper_on_bed:
        hx = (Q["handA"][0] + Q["handB"][0]) / 2
        hy = (Q["handA"][1] + Q["handB"][1]) / 2
        dd = ImageDraw.Draw(img)
        paper_small(dd, hx - 12, hy - 16, w=24, h=18)
        for hnd in ("handA", "handB"):
            x, y = Q[hnd]
            dd.ellipse((x - 2.5, y - 2.5, x + 2.5, y + 2.5), fill=C("skin"))
    if 1.55 < t < 2.6:
        bang(img, 104, 30)
    return img


def scene_pov(t):
    img = gradient(("wall", "wall", "walllit"), y1=H).copy()
    d = ImageDraw.Draw(img)
    d.rectangle((230, 0, 320, 40), fill=C("winA"))  # out-of-focus window glow
    A = np.asarray(img).copy()
    m = bayer_mask(0.5)
    blur = np.zeros_like(m)
    blur[:52, 210:] = True
    A[blur & m] = C("winB")
    img = Image.fromarray(A)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 116, W, H), fill=C("wood"))
    bob = 1.2 * math.sin(t * 2.1)
    lift = 30 * (1 - ease(t / 0.8))
    px0, py0, pw, ph = 50, 6 + bob + lift, 220, 100
    # paper with slight shade edge
    d.rectangle((px0 + 3, py0 + 3, px0 + pw + 3, py0 + ph + 3), fill=C("plank"))
    d.rectangle((px0, py0, px0 + pw, py0 + ph), fill=C("paper"))
    d.line((px0 + pw, py0, px0 + pw, py0 + ph), fill=C("papersh"), width=2)
    # tiny network glyph
    gx, gy = px0 + pw / 2, py0 + 12
    for a, b in [((-8, 0), (0, -4)), ((-8, 0), (0, 4)), ((0, -4), (8, 0)), ((0, 4), (8, 0))]:
        d.line([(gx + a[0], gy + a[1]), (gx + b[0], gy + b[1])], fill=C("txt2"))
    for p in [(-8, 0), (0, -4), (0, 4), (8, 0)]:
        d.rectangle((gx + p[0] - 1, gy + p[1] - 1, gx + p[0] + 1, gy + p[1] + 1), fill=C("s3"))
    # typed title
    name, role = "KRISHNA MUDGAL", "AI RESEARCHER"
    tt = t - 0.9
    n1 = int(clamp(tt / 1.4) * len(name))
    n2 = int(clamp((tt - 1.7) / 1.2) * len(role))
    nx = px0 + (pw - len(name) * 12) / 2
    rx = px0 + (pw - len(role) * 12) / 2
    text(d, round(nx), round(py0 + 28), name[:n1], "txt", scale=2)
    if tt > 1.5:
        d.line((px0 + 40, py0 + 49, px0 + pw - 40, py0 + 49), fill=C("txt2"))
    text(d, round(rx), round(py0 + 55), role[:n2], "s3", scale=2)
    cur_on = int(t * 3) % 2 == 0
    if cur_on and tt > 0:
        if n1 < len(name):
            cx, cy = nx + n1 * 12, py0 + 28
        else:
            cx, cy = rx + n2 * 12, py0 + 55
        d.rectangle((cx, cy, cx + 9, cy + 13), fill=C("txt2"))
    # faux body text
    for k in range(3):
        yy = py0 + 76 + k * 5
        d.line((px0 + 24, yy, px0 + 24 + 150 + 30 * hsh(k, 5), yy), fill=C("papersh"), width=2)
    # hands: hoodie sleeves from the bottom corners, thumbs on the front of the paper
    for side in (-1, 1):
        ex = px0 + 26 if side < 0 else px0 + pw - 26
        ey = py0 + ph - 6
        bx = ex - 34 * side
        d.polygon([(bx - 26, H), (bx + 26, H), (ex + 14, ey + 18), (ex - 14, ey + 10)], fill=C("hood"))
        d.line([(bx - 6 * side, H), (ex - 2 * side, ey + 16)], fill=C("hoodhi"), width=2)
        d.ellipse((ex - 15, ey - 4, ex + 15, ey + 22), fill=C("skin"))
        d.ellipse((ex - 15 + 9 * side, ey + 4, ex + 15 + 4 * side, ey + 22), fill=C("skinsh"))
        tx = ex + 6 * side
        d.rounded_rectangle((tx - 5, ey - 20, tx + 5, ey + 4), 5, fill=C("skin"))
        d.rounded_rectangle((tx - 3, ey - 18, tx + 3, ey - 12), 2, fill=C("skinsh"))
        d.line((tx - 4 * side, ey - 6, tx - 4 * side, ey + 2), fill=C("skinsh"))
    return img


# ------------------------------------------------------------------ timeline
SCENES = [
    # name, duration, fn(local_t, dur) -> img, transition-in
    ("chase_wide", 3.4, lambda t, D: scene_chase_wide(t), "fadein"),
    ("chase_close", 3.0, lambda t, D: scene_chase_close(t), "cut"),
    ("cliff", 4.0, lambda t, D: scene_cliff(t), "cut"),
    ("fall_close", 2.6, lambda t, D: scene_fall_close(t), "cut"),
    ("fall_wide", 3.8, lambda t, D: scene_fall_wide(t), "cut"),
    ("ai", 5.0, lambda t, D: scene_ai(t, D), "cut"),
    ("room", 5.4, lambda t, D: scene_room(t), "whitedissolve"),
    ("pov", 6.2, lambda t, D: scene_pov(t), "dither"),
]
TOTAL = sum(s[1] for s in SCENES)


def film(tg):
    t0 = 0.0
    for i, (name, dur, fn, tin) in enumerate(SCENES):
        if tg < t0 + dur or i == len(SCENES) - 1:
            lt = tg - t0
            img = fn(lt, dur)
            if tin == "fadein" and lt < 0.7:
                img = bayer_mix(Image.new("RGB", (W, H), C("ink")), img, lt / 0.7)
            elif tin == "whitedissolve" and lt < 1.0:
                img = bayer_mix(Image.new("RGB", (W, H), C("star")), img, ease(lt / 1.0))
            elif tin == "dither" and lt < 0.5:
                prev = SCENES[i - 1]
                img = bayer_mix(prev[2](prev[1] + lt, prev[1]), img, lt / 0.5)
            # white flash at end of AI world
            if name == "ai" and lt > dur - 0.8:
                img = bayer_mix(img, Image.new("RGB", (W, H), C("star")), ease((lt - (dur - 0.8)) / 0.8))
            if name == "pov" and lt > dur - 0.8:
                img = bayer_mix(img, Image.new("RGB", (W, H), C("ink")), ease((lt - (dur - 0.8)) / 0.8))
            return img
        t0 += dur


# ------------------------------------------------------------------ output
def framed(img):
    """upscale and put in the rounded rectangle card"""
    big = img.resize((W * UP, H * UP), Image.NEAREST)
    m = 6
    card = Image.new("RGB", (W * UP + 2 * m, H * UP + 2 * m), C("gh"))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, card.width - 1, card.height - 1), 12, fill=C("ink"), outline=C("frame"), width=2)
    mask = Image.new("L", big.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, big.width - 1, big.height - 1), 8, fill=255)
    card.paste(big, (m, m), mask)
    return card


def palette_image():
    pal = []
    for v in RGB.values():
        pal += list(v)
    pal += [0, 0, 0] * (256 - len(RGB))
    p = Image.new("P", (1, 1))
    p.putpalette(pal)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--at", type=float)
    a = ap.parse_args()
    PREV.mkdir(parents=True, exist_ok=True)
    if a.at is not None:
        framed(film(a.at)).save(PREV / f"retro_{a.at}.png")
        return
    n = int(TOTAL * FPS)
    print(f"{n} frames, {TOTAL:.1f}s")
    if a.sheet:
        ts = [k * 0.5 for k in range(int(TOTAL / 0.5))]
        cols = 6
        sheet = Image.new("RGB", (cols * W, ((len(ts) + cols - 1) // cols) * H))
        for j, t in enumerate(ts):
            sheet.paste(film(t), ((j % cols) * W, (j // cols) * H))
        sheet.save(PREV / "retro_sheet.png")
        return
    pal = palette_image()
    frames = [framed(film(k / FPS)).quantize(palette=pal, dither=Image.Dither.NONE) for k in range(n)]
    gif = OUT / "retro.gif"
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=round(1000 / FPS), loop=0, optimize=False)
    print(gif.name, f"{gif.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
