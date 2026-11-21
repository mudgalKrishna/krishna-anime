"""Original animated mascots that sit on top of each project card (SVG + CSS).

  mascot-paper.svg   Mirra  - half-lavender / half-peach symmetry fox   hover: Mirror Beam
  mascot-humble.svg  Humbo  - shield-shell turtle with a BLOCK/PASS sign hover: Aqua Jet
  mascot-riptide.svg Lure   - ember anglerfish with a cursor lure       hover: Ember Burst
  mascot-vla.svg     Bimo   - two-armed table-setting robot             hover: Volt Shock

Surfaces are lit with SVG lighting filters (diffuse + specular on a blurred
height map, plus a noise bump for fur) so they read as soft 3D figures.
Idle motion always plays. Hover moves play wherever the SVG is live
(opened directly or embedded via <object>); GitHub README <img> tags ignore hover.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "profile" / "assets"


def grad(gid, hi, base, dk, cx=".35", cy=".3", r=".75"):
    return (f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}">'
            f'<stop offset="0" stop-color="{hi}"/><stop offset=".55" stop-color="{base}"/><stop offset="1" stop-color="{dk}"/></radialGradient>')


def lin(gid, stops, x2="0", y2="1"):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + ("" if a is None else f' stop-opacity="{a}"') + '/>' for o, c, a in stops)
    return f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def light(fid, blur=3.0, scale=5.0, spec=.55, fur=0.0):
    bump = "b"
    noise = ""
    if fur:
        noise = (f'<feTurbulence type="fractalNoise" baseFrequency="1.3 2.4" numOctaves="2" seed="4" result="n"/>'
                 f'<feComposite in="b" in2="n" operator="arithmetic" k2="1" k3="{fur}" k4="{-fur / 2}" result="bn"/>')
        bump = "bn"
    return (f'<filter id="{fid}" x="-25%" y="-25%" width="150%" height="150%" color-interpolation-filters="sRGB">'
            f'<feGaussianBlur in="SourceAlpha" stdDeviation="{blur}" result="b"/>{noise}'
            f'<feDiffuseLighting in="{bump}" surfaceScale="{scale}" diffuseConstant="1.12" lighting-color="#fff" result="d"><feDistantLight azimuth="225" elevation="50"/></feDiffuseLighting>'
            f'<feSpecularLighting in="{bump}" surfaceScale="{scale}" specularConstant="{spec}" specularExponent="22" lighting-color="#fff" result="s"><feDistantLight azimuth="225" elevation="50"/></feSpecularLighting>'
            f'<feComposite in="SourceGraphic" in2="d" operator="arithmetic" k1="1" result="lit"/>'
            f'<feComposite in="s" in2="SourceAlpha" operator="in" result="s2"/>'
            f'<feComposite in="lit" in2="s2" operator="arithmetic" k2="1" k3="1" result="o"/>'
            f'<feComposite in="o" in2="SourceAlpha" operator="in"/></filter>')


COMMON_DEFS = (
    '<filter id="soft" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="2.6"/></filter>'
    '<filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3" result="g"/>'
    '<feMerge><feMergeNode in="g"/><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
)

COMMON_CSS = (
    ".blink{transform-box:fill-box;transform-origin:center;animation:blink 4s infinite}"
    "@keyframes blink{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.1)}}"
    ".bob{animation:bob 2.4s ease-in-out infinite}@keyframes bob{50%{transform:translateY(-3px)}}"
    ".shadow{transform-box:fill-box;transform-origin:center;animation:sh 2.4s ease-in-out infinite}@keyframes sh{50%{transform:scaleX(.88);opacity:.3}}"
    ".hp{transform-box:fill-box;animation:hp 6s ease-in-out infinite}@keyframes hp{0%,100%{transform:scaleX(1)}40%{transform:scaleX(.55)}}"
    ".atk{opacity:0}.hit{cursor:pointer}"
    ".mv{opacity:0;transition:opacity .2s}svg:hover .mv{opacity:1}svg:hover .idle{opacity:0}"
    "svg:hover .hp{animation:none;transform:scaleX(1)}"
)


def nameplate(x, h, name, typ, col, lv, move):
    w = 132
    x0 = x - 70 - w
    tw = len(typ) * 6.2 + 12
    return (f'<g transform="translate({x0},{h - 46})">'
            f'<rect width="{w}" height="36" rx="8" fill="#1a1530" stroke="#544878"/>'
            f'<text x="10" y="15" font-family="Consolas,monospace" font-size="12" font-weight="700" fill="#f4dccb">{name}</text>'
            f'<text class="idle" x="{w - 10}" y="15" font-family="Consolas,monospace" font-size="10" fill="#a99fd6" text-anchor="end">Lv.{lv}</text>'
            f'<text class="mv" x="{w - 10}" y="15" font-family="Consolas,monospace" font-size="9.5" font-weight="700" fill="{col}" text-anchor="end">{move}!</text>'
            f'<rect x="10" y="21" width="{tw:.0f}" height="11" rx="5.5" fill="{col}"/>'
            f'<text x="16" y="29.5" font-family="Consolas,monospace" font-size="8.5" font-weight="700" fill="#1a1530">{typ.upper()}</text>'
            f'<rect x="{tw + 16:.0f}" y="24.5" width="{w - tw - 26:.0f}" height="4" rx="2" fill="#2e2648"/>'
            f'<rect class="hp" x="{tw + 16:.0f}" y="24.5" width="{w - tw - 26:.0f}" height="4" rx="2" fill="#8fe3a0"/></g>')


def wrap(w, h, x, css, defs, body, label, tag, shadow_rx=36):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">'
            f"<style>{COMMON_CSS}{css}</style><defs>{COMMON_DEFS}{defs}</defs>"
            f'<rect class="hit" x="{x - 90}" y="0" width="{min(170, w - x + 90)}" height="{h}" fill="none" pointer-events="all"/>'
            f'<ellipse class="shadow" cx="{x}" cy="{h - 3}" rx="{shadow_rx}" ry="4" fill="#0a0614" opacity=".55" filter="url(#soft)"/>'
            + nameplate(x, h, *tag)
            + f'<g transform="translate({x},{h})">{body}</g></svg>')


def eye(x, y, r, iris):
    return (f'<g class="blink">'
            f'<ellipse cx="{x}" cy="{y}" rx="{r * .84:.2f}" ry="{r:.2f}" fill="#fffaf4"/>'
            f'<ellipse cx="{x + r * .08:.2f}" cy="{y + r * .1:.2f}" rx="{r * .66:.2f}" ry="{r * .8:.2f}" fill="url(#{iris})"/>'
            f'<ellipse cx="{x + r * .1:.2f}" cy="{y + r * .16:.2f}" rx="{r * .32:.2f}" ry="{r * .44:.2f}" fill="#100a18"/>'
            f'<circle cx="{x - r * .18:.2f}" cy="{y - r * .32:.2f}" r="{r * .27:.2f}" fill="#fff"/>'
            f'<circle cx="{x + r * .34:.2f}" cy="{y + r * .42:.2f}" r="{r * .12:.2f}" fill="#fff" opacity=".85"/>'
            f'<path d="M{x - r * .9:.2f} {y - r * .25:.2f} Q {x} {y - r * 1.3:.2f} {x + r * .9:.2f} {y - r * .25:.2f}" stroke="#1a1028" stroke-width="{r * .28:.2f}" fill="none" stroke-linecap="round"/>'
            f'</g>')


def iris(gid, hi, mid, dk):
    return grad(gid, hi, mid, dk, ".5", ".62", ".6")


# ------------------------------------------------------------ Mirra (paper)
def mirra(w=880, h=124, x=800):
    css = (
        ".tail{transform-box:fill-box;transform-origin:0% 100%;animation:tail 1.6s ease-in-out infinite alternate}"
        "@keyframes tail{to{transform:rotate(12deg)}}"
        ".oL{animation:oL 4s ease-in-out infinite}@keyframes oL{0%,15%{transform:translateX(0)}55%,70%{transform:translateX(34px)}71%,100%{transform:translateX(0)}}"
        ".oR{animation:oR 4s ease-in-out infinite}@keyframes oR{0%,15%{transform:translateX(0)}55%,70%{transform:translateX(-34px)}71%,100%{transform:translateX(0)}}"
        ".fused{transform-box:fill-box;transform-origin:center;opacity:0;animation:fz 4s ease-in-out infinite}"
        "@keyframes fz{0%,52%{opacity:0;transform:scale(.4)}58%{opacity:1;transform:scale(1.25)}68%{opacity:1;transform:scale(1)}72%,100%{opacity:0;transform:scale(.6)}}"
        ".spark{animation:sp 4s linear infinite;opacity:0}@keyframes sp{0%,55%{opacity:0}58%{opacity:1}75%,100%{opacity:0;transform:translateY(-12px)}}"
        # hover: Mirror Beam
        "svg:hover .oL,svg:hover .oR,svg:hover .fused,svg:hover .spark{animation:none;opacity:0}"
        ".fox{transform-box:fill-box;transform-origin:50% 100%}"
        "svg:hover .fox{animation:recoil 1.6s ease-out infinite}"
        "@keyframes recoil{0%,18%{transform:translateX(0) scale(1)}24%{transform:translateX(7px) scale(1.04,.95)}40%,100%{transform:translateX(0) scale(1)}}"
        ".charge{transform-box:fill-box;transform-origin:center}"
        "svg:hover .charge{animation:chg 1.6s ease-in-out infinite}"
        "@keyframes chg{0%{opacity:0;transform:scale(.2)}16%{opacity:1;transform:scale(1.3)}22%{transform:scale(.8)}60%{opacity:1;transform:scale(1)}80%,100%{opacity:0;transform:scale(.3)}}"
        ".beam{transform-box:fill-box;transform-origin:100% 50%}"
        "svg:hover .beam{animation:beam 1.6s ease-out infinite}"
        "@keyframes beam{0%,18%{opacity:0;transform:scaleX(0)}20%{opacity:1}36%{transform:scaleX(1);opacity:1}62%{opacity:1;transform:scaleX(1) scaleY(1)}80%,100%{opacity:0;transform:scaleX(1) scaleY(.2)}}"
        ".ring{transform-box:fill-box;transform-origin:center}"
        "svg:hover .ring{animation:ring 1.6s ease-out infinite}"
        "@keyframes ring{0%,34%{opacity:0;transform:scale(.2)}38%{opacity:1}80%,100%{opacity:0;transform:scale(2.6)}}"
        "svg:hover .shard{animation:shard 1.6s ease-out infinite}"
        "@keyframes shard{0%,36%{opacity:0;transform:translate(0,0)}42%{opacity:1}85%,100%{opacity:0;transform:translate(var(--dx),var(--dy))}}"
    )
    defs = (
        grad("mL", "#f3eeff", "#b9a8f3", "#7a68c8") + grad("mR", "#fff0e2", "#f6b38c", "#cf7a5a")
        + grad("cream", "#ffffff", "#fff3e6", "#e8cdb8")
        + grad("orbL", "#ffffff", "#c9b8ff", "#7a64e0", ".4", ".35") + grad("orbR", "#ffffff", "#ffc49a", "#e0784e", ".4", ".35")
        + grad("orbF", "#ffffff", "#ffe2b8", "#c49cff", ".45", ".4")
        + iris("irL", "#ffd9bf", "#e88a5c", "#7a3220") + iris("irR", "#e6dcff", "#8f74ea", "#3b2a8a")
        + lin("beamG", [(0, "#c9b8ff", 0), (.25, "#c9b8ff", .9), (.7, "#ffe2c8", 1), (1, "#ffffff", 1)], x2="1", y2="0")
        + light("fur", blur=3.2, scale=5, spec=.45, fur=.13) + light("clay", blur=2.4, scale=4, spec=.6)
        + '<clipPath id="cl"><rect x="-90" y="-140" width="90" height="150"/></clipPath>'
          '<clipPath id="cr"><rect x="0" y="-140" width="90" height="150"/></clipPath>'
    )

    def half(fill, clip):
        return (f'<g clip-path="url(#{clip})">'
                f'<ellipse cx="0" cy="-25" rx="25" ry="22" fill="url(#{fill})"/>'
                f'<circle cx="0" cy="-63" r="23" fill="url(#{fill})"/>'
                # cheek tufts
                f'<path d="M-20 -60 L-31 -52 L-22 -51 L-29 -45 L-16 -48 Z" fill="url(#{fill})"/>'
                f'<path d="M20 -60 L31 -52 L22 -51 L29 -45 L16 -48 Z" fill="url(#{fill})"/>'
                # ears
                f'<path d="M-21 -74 Q -30 -96 -25 -104 Q -14 -94 -6 -83 Z" fill="url(#{fill})"/>'
                f'<path d="M21 -74 Q 30 -96 25 -104 Q 14 -94 6 -83 Z" fill="url(#{fill})"/>'
                f'</g>')

    shards = "".join(
        f'<rect class="shard atk" x="-602" y="-64" width="4" height="4" fill="{c}" transform="rotate(45 -600 -62)" '
        f'style="--dx:{dx}px;--dy:{dy}px"/>'
        for dx, dy, c in [(-18, -20, "#fff"), (-24, 8, "#ffe2c8"), (6, -26, "#c9b8ff"), (10, 18, "#fff"), (-30, -4, "#c9b8ff")])
    body = (
        '<g class="fox"><g class="bob">'
        '<g filter="url(#fur)"><path class="tail" d="M16 -14 C 44 -10 62 -32 54 -62 C 50 -76 38 -82 32 -74 C 40 -54 34 -34 14 -28 Z" fill="url(#mR)"/></g>'
        '<path class="tail" d="M16 -14 C 44 -10 62 -32 54 -62 C 50 -76 38 -82 32 -74 C 42 -70 46 -62 44 -54 C 50 -66 46 -76 38 -78 Z" fill="url(#cream)" opacity=".95"/>'
        '<g filter="url(#fur)">' + half("mL", "cl") + half("mR", "cr") + '</g>'
        # inner ears
        '<path d="M-19 -79 Q -24 -93 -22 -98 Q -15 -90 -10 -84 Z" fill="#5a4396" opacity=".55"/>'
        '<path d="M19 -79 Q 24 -93 22 -98 Q 15 -90 10 -84 Z" fill="#9a4a32" opacity=".5"/>'
        # chest fluff + muzzle
        '<g filter="url(#fur)"><path d="M-13 -42 L-8 -30 L-4 -38 L0 -26 L4 -38 L8 -30 L13 -42 Q 0 -48 -13 -42 Z" fill="url(#cream)"/>'
        '<ellipse cx="0" cy="-54" rx="11" ry="8" fill="url(#cream)"/></g>'
        '<line x1="0" y1="-104" x2="0" y2="-2" stroke="#fff" stroke-opacity=".3" stroke-dasharray="2 3"/>'
        '<ellipse cx="0" cy="-58" rx="3.4" ry="2.5" fill="#24182e"/><ellipse cx="-1" cy="-59" rx="1.2" ry=".7" fill="#fff" opacity=".7"/>'
        '<path d="M-4 -52 Q 0 -49 0 -53 Q 0 -49 4 -52" stroke="#3a2840" stroke-width="1.1" fill="none" stroke-linecap="round"/>'
        '<g stroke="#fff" stroke-opacity=".55" stroke-width=".7"><path d="M-8 -55 L-22 -57 M-8 -53 L-21 -51"/><path d="M8 -55 L22 -57 M8 -53 L21 -51"/></g>'
        + eye(-9, -67, 5.2, "irL") + eye(9, -67, 5.2, "irR")
        + '<ellipse cx="-16" cy="-57" rx="4" ry="2.2" fill="#ff8fb0" opacity=".45"/><ellipse cx="16" cy="-57" rx="4" ry="2.2" fill="#ff8fb0" opacity=".45"/>'
        '<g filter="url(#clay)"><ellipse cx="-12" cy="-4" rx="8.5" ry="5" fill="url(#mL)"/><ellipse cx="12" cy="-4" rx="8.5" ry="5" fill="url(#mR)"/></g>'
        '</g></g>'
        '<g class="oL"><circle cx="-44" cy="-34" r="9" fill="url(#orbL)" filter="url(#glow)"/><circle cx="-47" cy="-37" r="2.4" fill="#fff" opacity=".9"/></g>'
        '<g class="oR"><circle cx="44" cy="-34" r="9" fill="url(#orbR)" filter="url(#glow)"/><circle cx="41" cy="-37" r="2.4" fill="#fff" opacity=".9"/></g>'
        '<circle class="fused" cx="-10" cy="-34" r="11" fill="url(#orbF)" filter="url(#glow)"/>'
        '<g class="spark" fill="#ffe08a"><rect x="-14" y="-52" width="2" height="2"/><rect x="-4" y="-56" width="2" height="2"/><rect x="-22" y="-48" width="2" height="2"/></g>'
        # Mirror Beam
        '<g class="beam atk" filter="url(#glow)"><rect x="-600" y="-67" width="560" height="10" rx="5" fill="url(#beamG)"/>'
        '<rect x="-560" y="-63.5" width="520" height="3" rx="1.5" fill="#fff"/></g>'
        '<circle class="ring atk" cx="-600" cy="-62" r="9" fill="none" stroke="#c9b8ff" stroke-width="2.4"/>'
        '<circle class="ring atk" cx="-600" cy="-62" r="5" fill="none" stroke="#ffe2c8" stroke-width="2" style="animation-delay:.08s"/>'
        + shards
        + '<circle class="charge atk" cx="-38" cy="-62" r="10" fill="url(#orbF)" filter="url(#glow)"/>'
    )
    return wrap(w, h, x, css, defs, body, "Mirra, a half-lavender half-peach symmetry fox, merges two glowing orbs; hover to fire a mirror beam",
                ("MIRRA", "symmetry", "#c9b8ff", 26, "MIRROR BEAM"))


# ------------------------------------------------------------ Humbo (HUMBLE)
def humbo(w=420, h=112, x=330):
    css = (
        ".head{animation:hd 2.4s ease-in-out infinite}@keyframes hd{50%{transform:translate(-2px,-2px)}}"
        ".sign{transform-box:fill-box;transform-origin:50% 100%;animation:sg 6s ease-in-out infinite}"
        "@keyframes sg{0%,40%{transform:scaleX(1)}45%{transform:scaleX(0)}50%,90%{transform:scaleX(1)}95%{transform:scaleX(0)}100%{transform:scaleX(1)}}"
        ".blk{animation:bk 6s steps(1) infinite}@keyframes bk{0%{opacity:1}45%{opacity:0}95%{opacity:1}}"
        ".pas{animation:ps 6s steps(1) infinite;opacity:0}@keyframes ps{0%{opacity:0}45%{opacity:1}95%{opacity:0}}"
        ".glint{animation:gl 6s ease-in-out infinite;opacity:0}@keyframes gl{0%,50%{opacity:0;transform:translateX(-30px)}60%{opacity:.8}75%,100%{opacity:0;transform:translateX(30px)}}"
        # hover: Aqua Jet
        "svg:hover .head{animation:hdj 1.4s ease-in-out infinite}"
        "@keyframes hdj{0%{transform:translate(0,0)}14%,70%{transform:translate(-6px,-12px) rotate(-12deg)}86%,100%{transform:translate(0,0)}}"
        "svg:hover .sign{animation:none}svg:hover .blk{animation:none;opacity:0}svg:hover .pas{animation:none;opacity:1}"
        "svg:hover .jet{animation:jet 1.4s ease-out infinite}"
        "@keyframes jet{0%,12%{stroke-dashoffset:100;opacity:1}34%{stroke-dashoffset:0;opacity:1}66%{stroke-dashoffset:0;opacity:1}84%,100%{stroke-dashoffset:-100;opacity:0}}"
        "svg:hover .flow{animation:flow .35s linear infinite,flowv 1.4s ease-out infinite}"
        "@keyframes flow{to{stroke-dashoffset:-16}}@keyframes flowv{0%,26%{opacity:0}34%,66%{opacity:1}80%,100%{opacity:0}}"
        ".spl{transform-box:fill-box;transform-origin:center}"
        "svg:hover .spl{animation:spl 1.4s ease-out infinite}"
        "@keyframes spl{0%,32%{opacity:0;transform:translate(0,0) scale(.5)}36%{opacity:1}76%,100%{opacity:0;transform:translate(var(--dx),var(--dy)) scale(1)}}"
        ".splr{transform-box:fill-box;transform-origin:center}"
        "svg:hover .splr{animation:splr 1.4s ease-out infinite}"
        "@keyframes splr{0%,32%{opacity:0;transform:scale(.3)}38%{opacity:.9}74%,100%{opacity:0;transform:scale(2.2,1.4)}}"
        "svg:hover .drip{animation:drip 1.4s ease-in infinite}"
        "@keyframes drip{0%,40%{opacity:0;transform:translateY(0)}46%{opacity:.9}90%,100%{opacity:0;transform:translateY(26px)}}"
    )
    defs = (grad("shell", "#d6e4ff", "#6f93e8", "#2f428e") + grad("skin", "#ecfff3", "#9edcb8", "#4a8f70")
            + grad("plastron", "#fff6dc", "#f0d79a", "#b8944e")
            + iris("irT", "#e0fff0", "#3fa878", "#13442e")
            + lin("water", [(0, "#e8fbff", None), (.4, "#7fd3ff", None), (1, "#2f7fe0", None)])
            + light("clay", blur=2.6, scale=5, spec=.7) + light("scaly", blur=2.2, scale=4, spec=.5, fur=.1)
            + '<clipPath id="shc"><path d="M-36 -8 C -36 -54 36 -54 36 -8 Z"/></clipPath>')
    scutes = "".join(
        f'<path d="M{cx - 7} {cy} l3.5 -6 h7 l3.5 6 l-3.5 6 h-7 Z" fill="#000" fill-opacity=".08" stroke="#d8e4ff" stroke-opacity=".6" stroke-width="1.2"/>'
        for cx, cy in [(-14, -26), (0, -34), (14, -26), (0, -18), (-25, -14), (25, -14), (-14, -12), (14, -12)])
    splash = "".join(
        f'<circle class="spl atk" cx="-292" cy="-62" r="{r}" fill="#9fe0ff" style="--dx:{dx}px;--dy:{dy}px"/>'
        for dx, dy, r in [(-16, -22, 2.6), (-24, -4, 2.2), (-6, -28, 2), (8, -20, 1.8), (-20, 14, 2.4), (4, 16, 1.8), (-30, -16, 1.6)])
    drips = "".join(
        f'<circle class="drip atk" cx="{cx}" cy="{cy}" r="1.7" fill="#9fe0ff" style="animation-delay:{d}s"/>'
        for cx, cy, d in [(-120, -84, 0), (-170, -88, .12), (-220, -80, .06), (-255, -70, .18)])
    body = (
        '<g filter="url(#scaly)"><ellipse cx="-24" cy="-5" rx="10" ry="5.5" fill="url(#skin)"/><ellipse cx="24" cy="-5" rx="10" ry="5.5" fill="url(#skin)"/>'
        '<path d="M34 -14 L46 -10 L34 -8 Z" fill="url(#skin)"/></g>'
        '<g filter="url(#clay)"><path d="M-36 -8 C -36 -54 36 -54 36 -8 Z" fill="url(#shell)"/></g>'
        f'<g clip-path="url(#shc)">{scutes}<rect class="glint" x="-6" y="-60" width="8" height="70" fill="#fff" transform="skewX(-20)"/></g>'
        '<path d="M-38 -8 H38" stroke="url(#plastron)" stroke-width="5" stroke-linecap="round"/>'
        '<path d="M-4 -42 l4 -4 l4 4 v6 c0 4 -4 6 -4 6 c0 0 -4 -2 -4 -6 Z" fill="#fff" opacity=".85"/>'
        # head faces left
        '<g class="head"><g filter="url(#scaly)"><path d="M-30 -18 Q -36 -20 -38 -22" stroke="url(#skin)" stroke-width="10" stroke-linecap="round"/>'
        '<ellipse cx="-46" cy="-24" rx="15" ry="13" fill="url(#skin)"/></g>'
        + eye(-49, -27, 4.6, "irT")
        + '<path d="M-58 -17 q-4 1 -6 -2" stroke="#2a4a3a" stroke-width="1.4" fill="none" stroke-linecap="round"/>'
        '<circle cx="-59" cy="-25" r=".9" fill="#2a4a3a"/>'
        '<ellipse cx="-40" cy="-18" rx="3.5" ry="2" fill="#ff8fb0" opacity=".4"/></g>'
        # sign on a stick held by the rear flipper
        '<line x1="28" y1="-12" x2="36" y2="-62" stroke="#8a5a3c" stroke-width="3" stroke-linecap="round"/>'
        '<g class="sign"><rect x="12" y="-88" width="52" height="24" rx="4" fill="#fff8ee" stroke="#3a2d4d" stroke-width="1.5"/>'
        '<text class="blk" x="38" y="-71" text-anchor="middle" font-family="Consolas,monospace" font-size="12" font-weight="700" fill="#e05a5a">BLOCK</text>'
        '<text class="pas" x="38" y="-71" text-anchor="middle" font-family="Consolas,monospace" font-size="12" font-weight="700" fill="#2f9a5a">PASS ✓</text></g>'
        # Aqua Jet
        '<g filter="url(#glow)" opacity=".95">'
        '<path class="jet atk" pathLength="100" stroke-dasharray="100 100" d="M-62 -40 Q -140 -112 -292 -62" stroke="url(#water)" stroke-width="8" fill="none" stroke-linecap="round"/>'
        '<path class="flow atk" d="M-62 -40 Q -140 -112 -292 -62" stroke="#fff" stroke-width="2.2" stroke-dasharray="6 10" fill="none" stroke-linecap="round"/>'
        '</g>'
        '<ellipse class="splr atk" cx="-292" cy="-62" rx="8" ry="5" fill="none" stroke="#bfeaff" stroke-width="2"/>'
        + splash + drips
    )
    return wrap(w, h, x, css, defs, body, "Humbo, a turtle with a shield-shaped shell, flips a sign from BLOCK to PASS; hover to fire an aqua jet",
                ("HUMBO", "guard", "#8fb3ff", 15, "AQUA JET"))


# ------------------------------------------------------------ Lure (Riptide)
def lure(w=420, h=112, x=320):
    css = (
        ".swim{animation:sw 3s ease-in-out infinite}@keyframes sw{50%{transform:translate(4px,-6px) rotate(3deg)}}"
        ".rod{transform-box:fill-box;transform-origin:0% 100%;animation:rod 2s ease-in-out infinite alternate}@keyframes rod{to{transform:rotate(-16deg)}}"
        ".click{transform-box:fill-box;transform-origin:20% 10%;animation:ck 2s ease-in-out infinite}@keyframes ck{0%,70%{transform:scale(1)}78%{transform:scale(.8)}86%,100%{transform:scale(1)}}"
        ".rip{transform-box:fill-box;transform-origin:center;animation:rp 2s ease-out infinite;opacity:0}@keyframes rp{0%,76%{opacity:0;transform:scale(.2)}80%{opacity:.9}100%{opacity:0;transform:scale(1.6)}}"
        ".fin{transform-box:fill-box;transform-origin:100% 50%;animation:fn .5s ease-in-out infinite alternate}@keyframes fn{to{transform:scaleX(.7)}}"
        ".bub{animation:bu 3s linear infinite}@keyframes bu{from{transform:translateY(0);opacity:.8}to{transform:translateY(-40px);opacity:0}}"
        ".jaw{transform-box:fill-box;transform-origin:100% 0%}"
        ".lglow{opacity:.35;transform-box:fill-box;transform-origin:center;animation:lg 2s ease-in-out infinite}@keyframes lg{50%{opacity:.6}}"
        # hover: Ember Burst
        "svg:hover .swim{animation:lunge .9s ease-in-out infinite}@keyframes lunge{0%,100%{transform:translate(0,0) rotate(0deg)}30%{transform:translate(5px,1px) rotate(-4deg)}55%{transform:translate(-3px,-2px) rotate(2deg)}}"
        "svg:hover .jaw{animation:none;transform:rotate(-24deg)}"
        "svg:hover .click{animation:ck .4s ease-in-out infinite}svg:hover .rip{animation:rp .4s ease-out infinite}"
        "svg:hover .lglow{animation:none;opacity:1}"
        "svg:hover .fl{animation:fl .9s ease-in infinite}"
        "@keyframes fl{0%{opacity:0;transform:translate(0,0) scale(.3)}10%{opacity:1}100%{opacity:0;transform:translate(-190px,-52px) scale(2.8)}}"
        "svg:hover .em{animation:em 1.1s ease-out infinite}"
        "@keyframes em{0%{opacity:0;transform:translate(0,0)}10%{opacity:1}100%{opacity:0;transform:translate(var(--dx),var(--dy))}}"
        ".fl,.em{transform-box:fill-box;transform-origin:center}"
    )
    defs = (grad("ember", "#ffd6a6", "#ff8f45", "#a83a1a") + grad("belly", "#fff2dc", "#ffc890", "#e08850")
            + grad("flame", "#ffffff", "#ffd36a", "#ff5a1e", ".5", ".5", ".5")
            + '<radialGradient id="flameE" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff6c8"/><stop offset=".45" stop-color="#ffb347"/>'
              '<stop offset=".8" stop-color="#ff4a1c" stop-opacity=".7"/><stop offset="1" stop-color="#c0201a" stop-opacity="0"/></radialGradient>'
            + '<radialGradient id="lg" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff2a8"/><stop offset="1" stop-color="#ffb347" stop-opacity="0"/></radialGradient>'
            + iris("irF", "#fff4c0", "#ffb000", "#7a3a00")
            + lin("finG", [(0, "#ff9c5a", .95), (1, "#ff5a2a", .55)], x2="1", y2="0")
            + light("clay", blur=3.2, scale=6, spec=.85) + light("clayf", blur=1.4, scale=2.5, spec=.4))
    spots = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#ffe2b8" opacity=".55"/>' for cx, cy, r in [(-14, -14, 2.4), (-20, -4, 1.8), (-8, -20, 1.6), (-24, 6, 1.4)])
    rays = "".join(f'<path d="M-32 0 L{-50 + k} {v}" stroke="#ffd2a0" stroke-opacity=".6" stroke-width=".8"/>' for k, v in [(2, -12), (0, -4), (0, 4), (2, 12)])
    # fish is drawn facing right, then mirrored so it faces the card and breathes fire to the left
    fish = (
        '<g transform="translate(0,-40)"><g class="swim">'
        f'<g class="fin"><path d="M-30 0 L-52 -18 L-47 0 L-52 18 Z" fill="url(#finG)"/>{rays}</g>'
        '<path d="M-4 -24 L2 -36 L8 -26 L14 -33 L16 -21" fill="url(#finG)"/>'
        '<path d="M-4 22 L4 32 L10 22" fill="url(#finG)"/>'
        '<g filter="url(#clay)"><ellipse cx="0" cy="0" rx="32" ry="26" fill="url(#ember)"/></g>'
        '<ellipse cx="4" cy="10" rx="20" ry="11" fill="url(#belly)" opacity=".65"/>'
        + spots
        + '<path d="M-22 2 Q 0 -6 22 -2" stroke="#ffe2b8" stroke-opacity=".5" stroke-width="1" fill="none" stroke-dasharray="2 2"/>'
        '<path d="M-6 -6 q -4 8 0 14" stroke="#a83a1a" stroke-opacity=".5" stroke-width="1.4" fill="none"/>'
        '<path d="M6 6 Q 22 4 31 0 Q 26 9 10 10 Z" fill="#3a1424"/>'
        '<g class="jaw"><path d="M8 9 Q 22 12 30 1 Q 24 18 8 15 Z" fill="#3a1424"/>'
        '<path d="M12 11 l2 -3 l2 3 M18 11 l2 -3 l2 3 M24 8 l2 -3 l2 3" stroke="#fff" stroke-width="1.1" fill="none"/></g>'
        '<path d="M12 6 l2 3 l2 -3 M18 5 l2 3 l2 -3 M24 3 l2 3 l2 -3" stroke="#fff" stroke-width="1.1" fill="none"/>'
        + eye(12, -9, 6.4, "irF")
        + '<g class="rod"><path d="M8 -24 C 10 -50 34 -58 46 -44" stroke="#8a3a1c" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
        '<g transform="translate(44,-46)"><circle class="lglow" cx="4" cy="7" r="16" fill="url(#lg)"/>'
        '<circle class="rip" cx="2" cy="2" r="10" fill="none" stroke="#ffe08a" stroke-width="2"/>'
        '<path class="click" d="M0 0 L0 15 L4 11 L7 18 L10 16.6 L7 10 L12 10 Z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></g></g>'
        '</g></g>'
    )
    flames = "".join(
        f'<ellipse class="fl atk" cx="-32" cy="-36" rx="12" ry="9" fill="url(#flameE)" style="animation-delay:-{d}s"/>'
        for d in [0, .15, .3, .45, .6, .75])
    core = "".join(
        f'<ellipse class="fl atk" cx="-32" cy="-36" rx="5" ry="4" fill="url(#flame)" style="animation-delay:-{d}s;animation-duration:.6s"/>'
        for d in [0, .2, .4])
    embers = "".join(
        f'<rect class="em atk" x="-34" y="-38" width="2.4" height="2.4" fill="{c}" style="--dx:{dx}px;--dy:{dy}px;animation-delay:-{dl}s"/>'
        for dx, dy, c, dl in [(-220, -70, "#ffe08a", 0), (-180, -30, "#ff9c5a", .3), (-240, -50, "#fff2a8", .55), (-150, -76, "#ff7a3a", .8), (-200, -16, "#ffd36a", .2)])
    body = (
        f'<g transform="scale(-1,1)">{fish}</g>'
        '<g fill="none" stroke="#bfe6ff" stroke-opacity=".8">'
        '<circle class="bub" cx="40" cy="-30" r="3"/><circle class="bub" cx="34" cy="-20" r="2" style="animation-delay:-1.2s"/>'
        '<circle class="bub" cx="46" cy="-14" r="2.4" style="animation-delay:-2.1s"/></g>'
        f'<g filter="url(#glow)">{flames}{core}</g>{embers}'
    )
    return wrap(w, h, x, css, defs, body, "Lure, an ember anglerfish whose glowing lure is a mouse cursor; hover to breathe an ember burst",
                ("LURE", "ember", "#ffa86b", 21, "EMBER BURST"))


# ------------------------------------------------------------ Bimo (Bi-Manual VLA)
def bimo(w=420, h=112, x=320):
    css = (
        ".armL{transform-box:fill-box;transform-origin:100% 0%;animation:aL 2.2s ease-in-out infinite}@keyframes aL{50%{transform:rotate(28deg)}}"
        ".armR{transform-box:fill-box;transform-origin:0% 0%;animation:aR 2.2s ease-in-out infinite}@keyframes aR{0%,100%{transform:rotate(-28deg)}50%{transform:rotate(0)}}"
        ".ant{animation:an 1s steps(1) infinite}@keyframes an{50%{fill:#5a4a8a}}"
        ".steam{animation:st 2s linear infinite}@keyframes st{from{opacity:.8;transform:translateY(0)}to{opacity:0;transform:translateY(-10px)}}"
        ".legs{transform-box:fill-box;transform-origin:50% 0%;animation:lg 1.4s ease-in-out infinite alternate}@keyframes lg{to{transform:rotate(-8deg)}}"
        # hover: Volt Shock
        "svg:hover .armL{animation:none;transform:rotate(40deg)}svg:hover .armR{animation:none;transform:rotate(-40deg)}"
        "svg:hover .ant{animation:anf .12s steps(1) infinite}@keyframes anf{50%{fill:#fff6a8}}"
        "svg:hover .bob{animation:jit .1s steps(2) infinite}@keyframes jit{50%{transform:translate(1px,-1px)}}"
        "svg:hover .b1{animation:b1 .5s steps(1) infinite}@keyframes b1{0%{opacity:1}25%{opacity:0}50%{opacity:1}75%{opacity:0}}"
        "svg:hover .b2{animation:b2 .5s steps(1) infinite}@keyframes b2{0%{opacity:0}25%{opacity:1}50%{opacity:0}75%{opacity:1}}"
        "svg:hover .arc{animation:b1 .3s steps(1) infinite}"
        "svg:hover .zap{animation:zap .5s steps(1) infinite}@keyframes zap{0%{opacity:.5}20%{opacity:0}60%{opacity:.35}80%{opacity:0}}"
        ".bolt-hit{transform-box:fill-box;transform-origin:center}"
        "svg:hover .bolt-hit{animation:bh .5s ease-out infinite}@keyframes bh{0%{opacity:1;transform:scale(.4)}100%{opacity:0;transform:scale(2.2)}}"
    )
    defs = (grad("metal", "#ffffff", "#d4cef0", "#6f67a6") + grad("dark", "#4a4070", "#1e1838", "#0e0a1c")
            + lin("visor", [(0, "#ffffff", .35), (.4, "#ffffff", 0), (1, "#ffffff", 0)], x2="1", y2="1")
            + grad("mug", "#ffd6bc", "#f2a37a", "#b8603c") + grad("plate", "#ffffff", "#fff3e4", "#d8c6b4")
            + light("metalf", blur=2.4, scale=4, spec=1.1) + light("clay", blur=1.6, scale=3, spec=.6))
    bolt1 = "M0 -70 L-30 -84 L-46 -70 L-82 -92 L-104 -74 L-140 -96 L-166 -78 L-204 -94 L-236 -80"
    bolt2 = "M0 -70 L-24 -90 L-52 -78 L-76 -98 L-110 -80 L-132 -100 L-170 -84 L-198 -100 L-236 -80"
    arcs = ('<path class="arc atk" d="M-56 -60 l6 6 l-5 3 l7 6" stroke="#fff6a8" stroke-width="1.6" fill="none"/>'
            '<path class="arc atk" d="M56 -60 l-6 6 l5 3 l-7 6" stroke="#fff6a8" stroke-width="1.6" fill="none" style="animation-delay:-.15s"/>'
            '<path class="arc atk" d="M-26 -20 l-6 4 l4 3 l-7 5" stroke="#bfefff" stroke-width="1.4" fill="none" style="animation-delay:-.07s"/>'
            '<path class="arc atk" d="M26 -22 l6 4 l-4 3 l7 5" stroke="#bfefff" stroke-width="1.4" fill="none" style="animation-delay:-.2s"/>')
    body = (
        '<g class="legs" filter="url(#metalf)"><rect x="-14" y="-13" width="9" height="13" rx="3" fill="url(#metal)"/><rect x="5" y="-13" width="9" height="13" rx="3" fill="url(#metal)"/></g>'
        '<g class="bob">'
        '<g filter="url(#metalf)"><rect x="-25" y="-54" width="50" height="44" rx="13" fill="url(#metal)"/></g>'
        '<path d="M-25 -30 H25" stroke="#8a82bc" stroke-opacity=".5"/>'
        '<g fill="#8a82bc"><circle cx="-20" cy="-15" r="1.2"/><circle cx="20" cy="-15" r="1.2"/><circle cx="-20" cy="-49" r="1.2"/><circle cx="20" cy="-49" r="1.2"/></g>'
        '<rect x="-18" y="-48" width="36" height="23" rx="8" fill="url(#dark)"/>'
        '<rect x="-18" y="-48" width="36" height="23" rx="8" fill="url(#visor)"/>'
        '<g class="idle"><g class="blink" filter="url(#glow)"><rect x="-11" y="-42" width="6" height="10" rx="3" fill="#8fe8ff"/><rect x="5" y="-42" width="6" height="10" rx="3" fill="#8fe8ff"/></g>'
        '<path d="M-5 -29.5 q5 3 10 0" stroke="#8fe8ff" stroke-width="1.6" fill="none" stroke-linecap="round"/></g>'
        '<g class="mv" stroke="#fff6a8" stroke-width="2.2" fill="none" stroke-linecap="round" filter="url(#glow)">'
        '<path d="M-12 -42 l6 4 l-6 4"/><path d="M12 -42 l-6 4 l6 4"/><path d="M-5 -29 l2.5 -2 l2.5 2 l2.5 -2 l2.5 2"/></g>'
        '<line x1="0" y1="-54" x2="0" y2="-64" stroke="#7c74ae" stroke-width="2.4"/><circle class="ant" cx="0" cy="-67" r="4" fill="#ff9e7a" filter="url(#glow)"/>'
        '<rect x="-15" y="-21" width="30" height="4" rx="2" fill="#a59dd0"/>'
        '<rect class="zap atk" x="-25" y="-54" width="50" height="44" rx="13" fill="#fff6a8"/>'
        # left arm with a plate
        '<g class="armL"><path d="M-25 -36 L-40 -28 L-46 -42" stroke="#8f87c0" stroke-width="4.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="-40" cy="-28" r="2.6" fill="#6f67a6"/>'
        '<g filter="url(#clay)"><ellipse cx="-48" cy="-46" rx="14" ry="3.8" fill="url(#plate)"/></g><ellipse cx="-48" cy="-47" rx="7" ry="1.6" fill="#e9dccb"/></g>'
        # right arm with a mug
        '<g class="armR"><path d="M25 -36 L40 -28 L46 -42" stroke="#8f87c0" stroke-width="4.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="40" cy="-28" r="2.6" fill="#6f67a6"/>'
        '<g filter="url(#clay)"><rect x="40" y="-60" width="14" height="15" rx="2.5" fill="url(#mug)"/></g><path d="M54 -57 q6 2 0 8" stroke="#e08a60" stroke-width="2.4" fill="none"/>'
        '<path class="steam" d="M44 -64 q2 -3 0 -6 M49 -64 q2 -3 0 -6" stroke="#fff" stroke-opacity=".7" fill="none"/></g>'
        '</g>'
        # Volt Shock
        f'<g filter="url(#glow)" stroke-linejoin="round" stroke-linecap="round" fill="none">'
        f'<g class="b1 atk"><path d="{bolt1}" stroke="#ffe86a" stroke-width="4.5"/><path d="{bolt1}" stroke="#fff" stroke-width="1.6"/></g>'
        f'<g class="b2 atk"><path d="{bolt2}" stroke="#ffe86a" stroke-width="4.5"/><path d="{bolt2}" stroke="#fff" stroke-width="1.6"/></g>'
        f'{arcs}</g>'
        '<circle class="bolt-hit atk" cx="-236" cy="-80" r="9" fill="none" stroke="#fff6a8" stroke-width="2.4"/>'
    )
    return wrap(w, h, x, css, defs, body, "Bimo, a little two-armed robot, lifts a plate and a mug; hover to unleash a volt shock",
                ("BIMO", "steel", "#cfc8ee", 12, "VOLT SHOCK"))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("paper", mirra), ("humble", humbo), ("riptide", lure), ("vla", bimo)]:
        (OUT / f"mascot-{name}.svg").write_text(fn(), encoding="utf-8")
        print(name, (OUT / f"mascot-{name}.svg").stat().st_size)
