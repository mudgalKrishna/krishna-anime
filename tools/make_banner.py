"""Animated profile banner (pure SVG + CSS, renders in GitHub READMEs).

A side-scrolling level set in the pfp's dream world: peach dusk sky with
lavender cloud clumps over an indigo abyss with floating cliff islands. A pixel
Claude mascot runs and hops island to island, collecting coins; at every jump
he grabs a paper scroll and a toast shows one of Krishna's wins.
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "profile" / "assets"
W, H = 840, 240
FONT = '"IBM Plex Mono","JetBrains Mono",Consolas,monospace'
C = dict(
    sky0="#eea777", sky1="#d9836f", sky2="#a8667c", sky3="#6d4d80", sky4="#3f3266", sky5="#241c42",
    cloud="#b98aa6", cloud2="#8f6c98", ink="#251a3e", sub="#4b3367",
    rock="#4a3b68", rockhi="#6b5688", rockdk="#33284d", moss="#8a6d8c", mosshi="#b08aa0",
    ruin="#2f2652", cube="#c9b8ff", debris="#2c2240",
    clawd="#d97757", clawd_dk="#b65a3f", clawd_hi="#eb9474", eye="#1a1220",
    coin="#ffd08a", coin_dk="#d9893f", coin_hi="#fff3d0", paper="#f4ead9", paper_ln="#8d7fa8",
    toast="#1c1534", gold="#ffe08a", text="#f4dccb",
)


def h(i, k=0):
    x = math.sin(i * 12.9898 + k * 78.233) * 43758.5453
    return x - math.floor(x)


def pix(rows, keys, px, x0=0, y0=0):
    out = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            ch = row[x]
            if ch == ".":
                x += 1
                continue
            x2 = x
            while x2 < len(row) and row[x2] == ch:
                x2 += 1
            out.append(f'<rect x="{x0 + x * px}" y="{y0 + y * px}" width="{(x2 - x) * px}" height="{px}" fill="{keys[ch]}"/>')
            x = x2
    return "".join(out)


BODY = [
    "...XXXXXXX...",
    "..XHHXXXXXX..",
    "..XXXEXXXEX..",
    "XXXXXEXXXEXXX",
    "XXXXXXXXXXXXX",
    "..XXXXXXXXX..",
    "..DDDDDDDDD..",
]
LEGS_A = ["...X.X..X.X..", "...X.X..X.X.."]
LEGS_B = ["..X.X....X.X.", ".X...X..X...X"]
LEGS_J = ["..X.X...X.X..", "..X.......X.."]
KEYS = {"X": C["clawd"], "D": C["clawd_dk"], "H": C["clawd_hi"], "E": C["eye"]}
COIN = [".KKKK.", "KCHCCK", "KHCCCK", "KCCCCK", "KCCCDK", ".KKKK."]
COIN_KEYS = {"K": C["coin_dk"], "C": C["coin"], "H": C["coin_hi"], "D": C["coin_dk"]}
SCROLL = [
    ".KKKKKKK.",
    "KPPPPPPPK",
    "KPLLLLLPK",
    "KPPPPPPPK",
    "KPLLLLPPK",
    "KPPPPPPPK",
    "KPLLLPPPK",
    ".KKKKKKK.",
]
SCROLL_KEYS = {"K": C["coin_dk"], "P": C["paper"], "L": C["paper_ln"]}

TOP = 188          # platform top
PX = 4
XM = 150           # mascot left
CX = XM + 13 * PX / 2
v = 140.0
L = 1260.0
D = L / v          # 9 s loop
PLATS = [(0, 270), (330, 600), (660, 930), (990, 1200)]   # track x ranges; gaps between
GAPS = [(a[1] + b[0]) / 2 for a, b in zip(PLATS, PLATS[1:])] + [(PLATS[-1][1] + L) / 2]
WINS = ["NeurIPS 2026 workshop paper", "winner · HackIIITD 2026", "HUMBLE · honest fine-tunes", "Bi-Manual VLA · SmolVLA"]
COINS = [90, 150, 210, 420, 480, 540, 760, 820, 880, 1060, 1120]


def pick_p(x):
    return ((x - CX) % L) / L


def pct(p):
    return f"{p * 100:.2f}%"


def hide_rules(name, x):
    """copy-0 / copy-1 visibility so each item vanishes when the mascot reaches it"""
    p = pick_p(x)
    rule = f"@keyframes {name}{{0%{{opacity:1}}{pct(p)}{{opacity:0}}100%{{opacity:0}}}}"
    if x >= CX:
        return (f".{name}0{{animation:{name} {D}s steps(1) infinite}}{rule}", "")
    return (f".{name}0{{opacity:0}}", f".{name}1{{animation:{name} {D}s steps(1) infinite}}{rule}")


def banner():
    css = [f"text{{font-family:{FONT}}}",
           f".trk{{animation:trk {D}s linear infinite}}@keyframes trk{{to{{transform:translateX(-{L}px)}}}}",
           ".cl1{animation:pan 70s linear infinite}.cl2{animation:pan 38s linear infinite}.far{animation:pan 26s linear infinite}",
           "@keyframes pan{to{transform:translateX(-840px)}}",
           ".la{animation:la .3s steps(1) infinite}@keyframes la{50%{opacity:0}}",
           ".lb{animation:lb .3s steps(1) infinite}@keyframes lb{0%{opacity:0}50%{opacity:1}}",
           ".bob{animation:bob .15s steps(1) infinite alternate}@keyframes bob{to{transform:translateY(-2px)}}",
           ".spin{transform-box:fill-box;transform-origin:center;animation:spin .9s ease-in-out infinite}@keyframes spin{50%{transform:scaleX(.25)}}",
           ".fl{animation:fl 5s ease-in-out infinite alternate}@keyframes fl{to{transform:translateY(-6px)}}",
           ".up{animation:up 9s linear infinite}@keyframes up{to{transform:translateY(-120px)}}"]
    # jumps over each gap
    jk = ["0%{transform:translateY(0)}"]
    run_kf = ["0%{opacity:1}"]
    for g in GAPS:
        p = pick_p(g)
        a, b = p - 0.032, p + 0.032
        jk += [f"{pct(a)}{{transform:translateY(0)}}", f"{pct(p - 0.012)}{{transform:translateY(-38px)}}",
               f"{pct(p + 0.012)}{{transform:translateY(-38px)}}", f"{pct(b)}{{transform:translateY(0)}}"]
        run_kf += [f"{pct(a)}{{opacity:0}}", f"{pct(b)}{{opacity:1}}"]
    jk.append("100%{transform:translateY(0)}")
    css.append(f".jump{{animation:jump {D}s linear infinite}}@keyframes jump{{{''.join(jk)}}}")
    css.append(f".run{{animation:run {D}s steps(1) infinite}}@keyframes run{{{''.join(run_kf)}100%{{opacity:1}}}}")
    air_kf = "".join(k.replace("opacity:0", "X").replace("opacity:1", "opacity:0").replace("X", "opacity:1") for k in run_kf)
    css.append(f".air{{animation:air {D}s steps(1) infinite}}@keyframes air{{{air_kf}100%{{opacity:0}}}}")
    # item visibility
    for i, x in enumerate(COINS):
        a, b = hide_rules(f"c{i}_", x)
        css += [a, b]
    for i, g in enumerate(GAPS):
        a, b = hide_rules(f"s{i}_", g)
        css += [a, b]
    # coin counter + toasts
    events = sorted(pick_p(x) for x in COINS)
    bounds = [0.0] + events + [1.0]
    for n in range(len(events) + 1):
        a, b = bounds[n], bounds[n + 1]
        kf = ("0%{opacity:1}" if a == 0 else f"0%{{opacity:0}}{pct(a)}{{opacity:1}}") + (f"{pct(b)}{{opacity:0}}100%{{opacity:0}}" if b < 1 else "100%{opacity:1}")
        css.append(f".k{n}{{animation:k{n} {D}s steps(1) infinite}}@keyframes k{n}{{{kf}}}")
    for i, g in enumerate(GAPS):
        p = pick_p(g)
        css.append(f".t{i}{{opacity:0;animation:t{i} {D}s linear infinite}}@keyframes t{i}{{0%,{pct(p)}{{opacity:0;transform:translateY(6px)}}"
                   f"{pct(p + 0.015)}{{opacity:1;transform:translateY(0)}}{pct(p + 0.16)}{{opacity:1;transform:translateY(0)}}"
                   f"{pct(p + 0.18)}{{opacity:0;transform:translateY(-4px)}}100%{{opacity:0}}}}")
        css.append(f".p{i}{{opacity:0;animation:p{i} {D}s linear infinite}}@keyframes p{i}{{0%,{pct(p)}{{opacity:0;transform:translateY(0)}}"
                   f"{pct(p + 0.004)}{{opacity:1}}{pct(p + 0.07)}{{opacity:0;transform:translateY(-18px)}}100%{{opacity:0}}}}")

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         'aria-label="Krishna Mudgal, AI researcher: continual learning, model merging, LLM reliability. A pixel Claude mascot hops across floating islands at dusk collecting coins and paper scrolls for each win: NeurIPS 2026 workshop paper, HackIIITD 2026 winner, HUMBLE, Bi-Manual VLA.">',
         f"<style>{''.join(css)}</style><defs>",
         f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["sky0"]}"/><stop offset=".3" stop-color="{C["sky1"]}"/>'
         f'<stop offset=".52" stop-color="{C["sky2"]}"/><stop offset=".7" stop-color="{C["sky3"]}"/><stop offset=".86" stop-color="{C["sky4"]}"/><stop offset="1" stop-color="{C["sky5"]}"/></linearGradient>',
         '<clipPath id="r"><rect width="840" height="240" rx="14"/></clipPath></defs>',
         '<g clip-path="url(#r)">',
         f'<rect width="{W}" height="{H}" fill="url(#sky)"/>']

    def clumps(seed, n, y0, y1, col, op, scale):
        out = []
        for rep in (0, 840):
            for i in range(n):
                x = rep + h(i, seed) * 840
                y = y0 + h(i, seed + 1) * (y1 - y0)
                for k in range(5):
                    r = (8 + 9 * h(i * 7 + k, seed + 2)) * scale
                    out.append(f'<circle cx="{x + (k - 2) * 11 * scale:.0f}" cy="{y + (3 if k in (0, 4) else 0) * scale - (4 if k == 2 else 0) * scale:.0f}" r="{r:.0f}" fill="{col}" opacity="{op}"/>')
        return "".join(out)

    s.append(f'<g class="cl1">{clumps(3, 5, 22, 60, C["cloud"], .55, 1.0)}</g>')
    s.append(f'<g class="cl2">{clumps(9, 4, 70, 110, C["cloud2"], .6, 1.3)}</g>')
    # distant floating ruins + slowly rising debris
    fr = []
    for rep in (0, 840):
        for i in range(6):
            x = rep + 30 + i * 140 + 40 * h(i, 41)
            top = 128 + 34 * h(i, 42)
            w = 26 + 22 * h(i, 43)
            col = C["sky3"] if i % 2 else C["ruin"]
            fr.append(f'<polygon points="{x:.0f},{top:.0f} {x + w:.0f},{top:.0f} {x + w * .8:.0f},{top + 7:.0f} {x + w * .55:.0f},{top + 15:.0f} {x + w * .3:.0f},{top + 8:.0f}" fill="{col}"/>')
            tw = 4 + 3 * h(i, 44)
            th = 8 + 14 * h(i, 45)
            fr.append(f'<rect x="{x + w * .35:.0f}" y="{top - th:.0f}" width="{tw:.0f}" height="{th:.0f}" fill="{col}"/>')
            fr.append(f'<rect x="{x + w * .62:.0f}" y="{top - th * .6:.0f}" width="{tw * .8:.0f}" height="{th * .6:.0f}" fill="{col}"/>')
    s.append(f'<g class="far">{"".join(fr)}</g>')
    # wireframe cubes (the AI layer of the dream)
    for (cx, cy, sz) in [(560, 128, 12), (705, 98, 8), (420, 150, 7)]:
        o = sz * .5
        s.append(f'<g class="fl" fill="none" stroke="{C["cube"]}" stroke-opacity=".55">'
                 f'<rect x="{cx - sz}" y="{cy - sz}" width="{2 * sz}" height="{2 * sz}"/><rect x="{cx - sz + o}" y="{cy - sz - o}" width="{2 * sz}" height="{2 * sz}"/>'
                 f'<path d="M{cx - sz} {cy - sz}l{o} {-o}M{cx + sz} {cy - sz}l{o} {-o}M{cx - sz} {cy + sz}l{o} {-o}M{cx + sz} {cy + sz}l{o} {-o}"/></g>')
    deb = "".join(f'<rect x="{h(i, 61) * 840:.0f}" y="{150 + h(i, 62) * 210:.0f}" width="{2 + 3 * h(i, 63):.0f}" height="{2 + 2 * h(i, 64):.0f}" fill="{C["debris"]}" transform="rotate({h(i, 65) * 40:.0f} {h(i, 61) * 840:.0f} {150 + h(i, 62) * 210:.0f})"/>' for i in range(22))
    s.append(f'<g class="up">{deb}</g>')
    # title
    s.append(f'<text x="30" y="52" font-size="28" font-weight="700" fill="{C["ink"]}" letter-spacing="2">KRISHNA MUDGAL</text>')
    s.append(f'<text x="32" y="76" font-size="13" fill="{C["sub"]}">ai researcher · continual learning · model merging · llm reliability</text>')

    # track: islands, coins, scrolls (two copies)
    tr = []
    for copy in (0, 1):
        off = copy * L
        for i, (a, b) in enumerate(PLATS):
            a, b = a + off, b + off
            jag = []
            n = int((b - a) / 14)
            for k in range(n + 1):
                x = a + (b - a) * k / n
                depth = 14 + 30 * math.sin(math.pi * k / n) + 6 * h(k + i * 13, 71)
                jag.append(f"{x:.0f},{TOP + depth:.0f}")
            tr.append(f'<polygon points="{a},{TOP} {b},{TOP} {" ".join(reversed(jag))}" fill="{C["rock"]}"/>')
            for k in range(int((b - a) / 26)):
                xx = a + 10 + k * 26 + 8 * h(k, i + 80)
                tr.append(f'<rect x="{xx:.0f}" y="{TOP + 8 + 10 * h(k, i + 81):.0f}" width="{4 + 6 * h(k, i + 82):.0f}" height="2" fill="{C["rockhi" if k % 2 else "rockdk"]}"/>')
            tr.append(f'<rect x="{a}" y="{TOP}" width="{b - a}" height="4" fill="{C["moss"]}"/>')
            for k in range(int((b - a) / 9)):
                xx = a + 3 + k * 9 + 4 * h(k, i + 90)
                tr.append(f'<rect x="{xx:.0f}" y="{TOP - 2 - 2 * h(k, i + 91):.0f}" width="2" height="{3 + 2 * h(k, i + 91):.0f}" fill="{C["mosshi"]}"/>')
        for i, x in enumerate(COINS):
            tr.append(f'<g class="c{i}_{copy}"><g transform="translate({x + off - 9},{TOP - 30})"><g class="spin">{pix(COIN, COIN_KEYS, 3)}</g></g></g>')
        for i, g in enumerate(GAPS):
            tr.append(f'<g class="s{i}_{copy}"><g class="fl"><g transform="translate({g + off - 13.5},{TOP - 80})">{pix(SCROLL, SCROLL_KEYS, 3)}</g></g></g>')
    s.append(f'<g class="trk">{"".join(tr)}</g>')

    # mascot
    s.append(f'<g class="jump"><g transform="translate({XM},{TOP - 10 * PX})">'
             f'<g class="bob">{pix(BODY, KEYS, PX)}</g>'
             f'<g class="run"><g class="la">{pix(LEGS_A, KEYS, PX, 0, 7 * PX)}</g><g class="lb">{pix(LEGS_B, KEYS, PX, 0, 7 * PX)}</g></g>'
             f'<g class="air">{pix(LEGS_J, KEYS, PX, 0, 7 * PX)}</g>'
             f'</g></g>')
    # pickup pops
    for i in range(len(GAPS)):
        s.append(f'<g class="p{i}"><text x="{CX + 22:.0f}" y="{TOP - 84}" font-size="12" fill="{C["gold"]}">+paper</text></g>')
    # HUD
    s.append(f'<g transform="translate(700,26)">{pix(COIN, COIN_KEYS, 3)}</g>')
    for n in range(len(COINS) + 1):
        s.append(f'<text class="k{n}" x="726" y="42" font-size="15" font-weight="700" fill="{C["ink"]}">× {n:02d}</text>')
    s.append(f'<g transform="translate(772,24)">{pix(SCROLL, SCROLL_KEYS, 2)}</g>')
    s.append(f'<text x="794" y="42" font-size="15" font-weight="700" fill="{C["ink"]}">×4</text>')
    # win toasts
    for i, txt in enumerate(WINS):
        w = len(txt) * 7.8 + 44
        s.append(f'<g class="t{i}"><rect x="{W - 24 - w:.0f}" y="58" width="{w:.0f}" height="26" rx="6" fill="{C["toast"]}" opacity=".9" stroke="{C["gold"]}" stroke-opacity=".7"/>'
                 f'<text x="{W - 24 - w + 14:.0f}" y="76" font-size="13" fill="{C["gold"]}">★ <tspan fill="{C["text"]}">{txt}</tspan></text></g>')
    s.append("</g>")
    s.append(f'<rect x=".75" y=".75" width="838.5" height="238.5" rx="14" fill="none" stroke="{C["sky3"]}" stroke-width="1.5"/>')
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "banner.svg").write_text(banner(), encoding="utf-8")
    for f in ("header.svg", "quest.svg"):
        (OUT / f).unlink(missing_ok=True)
    print("banner.svg", (OUT / "banner.svg").stat().st_size, "bytes")
