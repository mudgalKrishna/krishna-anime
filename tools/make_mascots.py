"""Original animated mascots that sit on top of each project card (SVG + CSS).

  mascot-paper.svg   Mirra   - half-lavender / half-peach symmetry fox merging two orbs
  mascot-humble.svg  Humbo   - shield-shell turtle flipping a BLOCK -> PASS sign
  mascot-riptide.svg Lure    - ember anglerfish whose lure is a clicking mouse cursor
  mascot-vla.svg     Bimo    - two-armed robot lifting a plate and a mug

Each file is a transparent strip; the mascot sits on its bottom edge so it rests
on the card image placed directly below it in the README.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "profile" / "assets"


def grad(gid, hi, base, dk, cx=".35", cy=".3"):
    return (f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r=".75">'
            f'<stop offset="0" stop-color="{hi}"/><stop offset=".55" stop-color="{base}"/><stop offset="1" stop-color="{dk}"/></radialGradient>')


TAGS = {}


def nameplate(x, h, name, typ, col, lv):
    w = 132
    x0 = x - 70 - w
    return (f'<g transform="translate({x0},{h - 46})">'
            f'<rect width="{w}" height="36" rx="8" fill="#1a1530" stroke="#544878"/>'
            f'<text x="10" y="15" font-family="Consolas,monospace" font-size="12" font-weight="700" fill="#f4dccb">{name}</text>'
            f'<text x="{w - 10}" y="15" font-family="Consolas,monospace" font-size="10" fill="#a99fd6" text-anchor="end">Lv.{lv}</text>'
            f'<rect x="10" y="21" width="{len(typ) * 6.2 + 12:.0f}" height="11" rx="5.5" fill="{col}"/>'
            f'<text x="16" y="29.5" font-family="Consolas,monospace" font-size="8.5" font-weight="700" fill="#1a1530">{typ.upper()}</text>'
            f'<rect x="{len(typ) * 6.2 + 28:.0f}" y="24.5" width="{w - len(typ) * 6.2 - 38:.0f}" height="4" rx="2" fill="#2e2648"/>'
            f'<rect class="hp" x="{len(typ) * 6.2 + 28:.0f}" y="24.5" width="{w - len(typ) * 6.2 - 38:.0f}" height="4" rx="2" fill="#8fe3a0"/></g>')


def wrap(w, h, x, css, defs, body, label, scale=1.0, tag=None):
    common = (".blink{transform-box:fill-box;transform-origin:center;animation:blink 4s infinite}"
              "@keyframes blink{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.1)}}"
              ".bob{animation:bob 2.4s ease-in-out infinite}@keyframes bob{50%{transform:translateY(-3px)}}"
              ".shadow{transform-box:fill-box;transform-origin:center;animation:sh 2.4s ease-in-out infinite}@keyframes sh{50%{transform:scaleX(.85);opacity:.25}}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">'
            f"<style>{common}{css}.hp{{transform-box:fill-box;animation:hp 6s ease-in-out infinite}}@keyframes hp{{0%,100%{{transform:scaleX(1)}}40%{{transform:scaleX(.55)}}}}</style><defs>{defs}</defs>"
            + f'<ellipse class="shadow" cx="{x}" cy="{h - 2}" rx="{34 * scale:.0f}" ry="3" fill="#000" opacity=".35"/>'
            + (nameplate(x, h, *tag) if tag else "")
            + f'<g transform="translate({x},{h}) scale({scale})">{body}</g></svg>')


def eye(x, y, r=4.2):
    return (f'<g class="blink"><ellipse cx="{x}" cy="{y}" rx="{r * .8:.1f}" ry="{r:.1f}" fill="#1a1426"/>'
            f'<circle cx="{x + r * .3:.1f}" cy="{y - r * .4:.1f}" r="{r * .32:.1f}" fill="#fff"/></g>')


# ------------------------------------------------------------ Mirra (paper)
def mirra(w=880, h=118, x=800):
    css = (".tail{transform-box:fill-box;transform-origin:0% 100%;animation:tail 1.6s ease-in-out infinite alternate}"
           "@keyframes tail{to{transform:rotate(14deg)}}"
           ".oL{animation:oL 4s ease-in-out infinite}@keyframes oL{0%,15%{transform:translateX(0)}55%,70%{transform:translateX(34px)}71%,100%{transform:translateX(0)}}"
           ".oR{animation:oR 4s ease-in-out infinite}@keyframes oR{0%,15%{transform:translateX(0)}55%,70%{transform:translateX(-34px)}71%,100%{transform:translateX(0)}}"
           ".fused{transform-box:fill-box;transform-origin:center;opacity:0;animation:fz 4s ease-in-out infinite}"
           "@keyframes fz{0%,52%{opacity:0;transform:scale(.4)}58%{opacity:1;transform:scale(1.25)}68%{opacity:1;transform:scale(1)}72%,100%{opacity:0;transform:scale(.6)}}"
           ".spark{animation:sp 4s linear infinite;opacity:0}@keyframes sp{0%,55%{opacity:0}58%{opacity:1}75%,100%{opacity:0;transform:translateY(-12px)}}")
    defs = (grad("mL", "#ece4ff", "#b6a4f2", "#6e5cc0") + grad("mR", "#ffe6d0", "#f4ad86", "#c96d52")
            + grad("orbL", "#ffffff", "#c9b8ff", "#7a64e0", ".4", ".35") + grad("orbR", "#ffffff", "#ffc49a", "#e0784e", ".4", ".35")
            + grad("orbF", "#ffffff", "#ffe2b8", "#c49cff", ".45", ".4")
            + '<clipPath id="cl"><rect x="-80" y="-140" width="80" height="150"/></clipPath>'
              '<clipPath id="cr"><rect x="0" y="-140" width="80" height="150"/></clipPath>')

    def half(fill, clip):
        return (f'<g clip-path="url(#{clip})">'
                f'<ellipse cx="0" cy="-24" rx="25" ry="22" fill="url(#{fill})"/>'
                f'<circle cx="0" cy="-62" r="23" fill="url(#{fill})"/>'
                f'<polygon points="-20,-74 -26,-100 -6,-82" fill="url(#{fill})"/><polygon points="20,-74 26,-100 6,-82" fill="url(#{fill})"/>'
                f'</g>')
    body = (
        '<g class="bob">'
        '<path class="tail" d="M18 -12 C 44 -14 50 -40 40 -56 C 36 -40 30 -28 16 -26 Z" fill="url(#mR)"/>'
        + half("mL", "cl") + half("mR", "cr")
        + '<polygon points="-19,-79 -22,-94 -11,-84" fill="#4b3a8a" opacity=".45"/><polygon points="19,-79 22,-94 11,-84" fill="#8a3f2c" opacity=".4"/>'
        '<line x1="0" y1="-104" x2="0" y2="-2" stroke="#fff" stroke-opacity=".35" stroke-dasharray="2 3"/>'
        '<ellipse cx="0" cy="-54" rx="9" ry="6" fill="#fff4ea" opacity=".9"/><ellipse cx="0" cy="-57" rx="2.6" ry="2" fill="#2a1d36"/>'
        + eye(-9, -66) + eye(9, -66)
        + '<ellipse cx="-15" cy="-56" rx="4" ry="2.2" fill="#ff8fb0" opacity=".45"/><ellipse cx="15" cy="-56" rx="4" ry="2.2" fill="#ff8fb0" opacity=".45"/>'
        '<ellipse cx="-12" cy="-3" rx="8" ry="4.5" fill="url(#mL)"/><ellipse cx="12" cy="-3" rx="8" ry="4.5" fill="url(#mR)"/>'
        '</g>'
        '<g class="oL"><circle cx="-44" cy="-34" r="9" fill="url(#orbL)"/><circle cx="-47" cy="-37" r="2.4" fill="#fff" opacity=".9"/></g>'
        '<g class="oR"><circle cx="44" cy="-34" r="9" fill="url(#orbR)"/><circle cx="41" cy="-37" r="2.4" fill="#fff" opacity=".9"/></g>'
        '<circle class="fused" cx="-10" cy="-34" r="11" fill="url(#orbF)"/>'
        '<g class="spark" fill="#ffe08a"><rect x="-14" y="-52" width="2" height="2"/><rect x="-4" y="-56" width="2" height="2"/><rect x="-22" y="-48" width="2" height="2"/></g>'
    )
    return wrap(w, h, x, css, defs, body, "Mirra, a half-lavender half-peach symmetry fox, merges two glowing orbs into one", tag=("MIRRA", "symmetry", "#c9b8ff", 26))


# ------------------------------------------------------------ Humbo (HUMBLE)
def humbo(w=420, h=104, x=330):
    css = (".head{animation:hd 2.4s ease-in-out infinite}@keyframes hd{50%{transform:translate(2px,-2px)}}"
           ".sign{transform-box:fill-box;transform-origin:50% 100%;animation:sg 6s ease-in-out infinite}"
           "@keyframes sg{0%,40%{transform:scaleX(1)}45%{transform:scaleX(0)}50%,90%{transform:scaleX(1)}95%{transform:scaleX(0)}100%{transform:scaleX(1)}}"
           ".blk{animation:bk 6s steps(1) infinite}@keyframes bk{0%{opacity:1}45%{opacity:0}95%{opacity:1}}"
           ".pas{animation:ps 6s steps(1) infinite;opacity:0}@keyframes ps{0%{opacity:0}45%{opacity:1}95%{opacity:0}}"
           ".glint{animation:gl 6s ease-in-out infinite;opacity:0}@keyframes gl{0%,50%{opacity:0;transform:translateX(-30px)}60%{opacity:.8}75%,100%{opacity:0;transform:translateX(30px)}}")
    defs = (grad("shell", "#cfe0ff", "#6f93e8", "#33479a") + grad("skin", "#e8fff0", "#9edcb8", "#4f9a78")
            + '<clipPath id="shc"><path d="M-36 -8 C -36 -52 36 -52 36 -8 Z"/></clipPath>')
    hexes = "".join(f'<path d="M{cx - 7} {cy} l3.5 -6 h7 l3.5 6 l-3.5 6 h-7 Z" fill="none" stroke="#c8d8ff" stroke-opacity=".55"/>'
                    for cx, cy in [(-14, -24), (0, -32), (14, -24), (0, -16), (-24, -12), (24, -12)])
    body = (
        '<ellipse cx="-24" cy="-4" rx="9" ry="5" fill="url(#skin)"/><ellipse cx="22" cy="-4" rx="9" ry="5" fill="url(#skin)"/>'
        '<path d="M-36 -8 C -36 -52 36 -52 36 -8 Z" fill="url(#shell)"/>'
        f'<g clip-path="url(#shc)">{hexes}<rect class="glint" x="-6" y="-60" width="8" height="70" fill="#fff" transform="skewX(-20)"/></g>'
        '<path d="M-38 -8 H38" stroke="#2a3a7a" stroke-width="3" stroke-linecap="round"/>'
        '<path d="M-4 -40 l4 -4 l4 4 v6 c0 4 -4 6 -4 6 c0 0 -4 -2 -4 -6 Z" fill="#fff" opacity=".85"/>'
        '<g class="head"><ellipse cx="44" cy="-22" rx="15" ry="13" fill="url(#skin)"/>'
        + eye(48, -25, 3.6)
        + '<path d="M50 -15 q4 2 7 -1" stroke="#2a4a3a" stroke-width="1.4" fill="none" stroke-linecap="round"/>'
        '<ellipse cx="40" cy="-17" rx="3.5" ry="2" fill="#ff8fb0" opacity=".4"/></g>'
        # sign on a stick held by the front flipper
        '<line x1="26" y1="-12" x2="20" y2="-62" stroke="#8a5a3c" stroke-width="3" stroke-linecap="round"/>'
        '<g class="sign"><rect x="-6" y="-88" width="52" height="24" rx="4" fill="#fff8ee" stroke="#3a2d4d" stroke-width="1.5"/>'
        '<text class="blk" x="20" y="-71" text-anchor="middle" font-family="Consolas,monospace" font-size="12" font-weight="700" fill="#e05a5a">BLOCK</text>'
        '<text class="pas" x="20" y="-71" text-anchor="middle" font-family="Consolas,monospace" font-size="12" font-weight="700" fill="#2f9a5a">PASS ✓</text></g>'
    )
    return wrap(w, h, x, css, defs, body, "Humbo, a turtle with a shield-shaped shell, flips a sign from BLOCK to PASS", tag=("HUMBO", "guard", "#8fb3ff", 15))


# ------------------------------------------------------------ Lure (Riptide)
def lure(w=420, h=104, x=320):
    css = (".swim{animation:sw 3s ease-in-out infinite}@keyframes sw{50%{transform:translate(-4px,-6px) rotate(-3deg)}}"
           ".rod{transform-box:fill-box;transform-origin:0% 100%;animation:rod 2s ease-in-out infinite alternate}@keyframes rod{to{transform:rotate(-16deg)}}"
           ".click{transform-box:fill-box;transform-origin:20% 10%;animation:ck 2s ease-in-out infinite}@keyframes ck{0%,70%{transform:scale(1)}78%{transform:scale(.8)}86%,100%{transform:scale(1)}}"
           ".rip{transform-box:fill-box;transform-origin:center;animation:rp 2s ease-out infinite;opacity:0}@keyframes rp{0%,76%{opacity:0;transform:scale(.2)}80%{opacity:.9}100%{opacity:0;transform:scale(1.6)}}"
           ".fin{transform-box:fill-box;transform-origin:100% 50%;animation:fn .5s ease-in-out infinite alternate}@keyframes fn{to{transform:scaleX(.7)}}"
           ".bub{animation:bu 3s linear infinite}@keyframes bu{from{transform:translateY(0);opacity:.8}to{transform:translateY(-40px);opacity:0}}")
    defs = grad("ember", "#ffd2a0", "#ff8f45", "#b8431f") + grad("belly", "#fff0d8", "#ffc890", "#e08850")
    body = (
        '<g class="swim" transform="translate(0,-38)">'
        '<path class="fin" d="M-30 0 L-50 -16 L-46 0 L-50 16 Z" fill="#e0662e"/>'
        '<ellipse cx="0" cy="0" rx="32" ry="26" fill="url(#ember)"/>'
        '<ellipse cx="4" cy="10" rx="20" ry="11" fill="url(#belly)" opacity=".7"/>'
        '<path d="M8 6 Q 22 4 30 0 Q 24 16 8 14 Z" fill="#3a1424"/>'
        '<path d="M12 7 l2 3 l2 -3 M18 6 l2 3 l2 -3 M24 4 l2 3 l2 -3" stroke="#fff" stroke-width="1.2" fill="none"/>'
        '<path d="M-6 -22 L0 -32 L6 -24 L12 -30 L14 -20" fill="#e0662e"/>'
        + eye(12, -8, 5.5)
        + '<g class="rod"><path d="M8 -24 C 10 -50 34 -58 46 -44" stroke="#8a3a1c" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
        '<g transform="translate(44,-46)"><circle class="rip" cx="2" cy="2" r="10" fill="none" stroke="#ffe08a" stroke-width="2"/>'
        '<path class="click" d="M0 0 L0 15 L4 11 L7 18 L10 16.6 L7 10 L12 10 Z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></g></g>'
        '</g>'
        '<g fill="none" stroke="#bfe6ff" stroke-opacity=".8">'
        '<circle class="bub" cx="-40" cy="-30" r="3"/><circle class="bub" cx="-34" cy="-20" r="2" style="animation-delay:-1.2s"/>'
        '<circle class="bub" cx="-46" cy="-14" r="2.4" style="animation-delay:-2.1s"/></g>'
    )
    return wrap(w, h, x, css, defs, body, "Lure, an ember anglerfish whose glowing lure is a mouse cursor, clicks while it swims", scale=1.0, tag=("LURE", "ember", "#ffa86b", 21))


# ------------------------------------------------------------ Bimo (Bi-Manual VLA)
def bimo(w=420, h=104, x=320):
    css = (".armL{transform-box:fill-box;transform-origin:100% 0%;animation:aL 2.2s ease-in-out infinite}@keyframes aL{50%{transform:rotate(28deg)}}"
           ".armR{transform-box:fill-box;transform-origin:0% 0%;animation:aR 2.2s ease-in-out infinite}@keyframes aR{0%,100%{transform:rotate(-28deg)}50%{transform:rotate(0)}}"
           ".ant{animation:an 1s steps(1) infinite}@keyframes an{50%{fill:#5a4a8a}}"
           ".steam{animation:st 2s linear infinite}@keyframes st{from{opacity:.8;transform:translateY(0)}to{opacity:0;transform:translateY(-10px)}}"
           ".legs{transform-box:fill-box;transform-origin:50% 0%;animation:lg 1.4s ease-in-out infinite alternate}@keyframes lg{to{transform:rotate(-8deg)}}")
    defs = grad("metal", "#ffffff", "#cfc8ee", "#7c74ae") + grad("dark", "#4a4070", "#241c40", "#120e22")
    body = (
        '<g class="legs"><rect x="-14" y="-12" width="8" height="12" rx="3" fill="url(#metal)"/><rect x="6" y="-12" width="8" height="12" rx="3" fill="url(#metal)"/></g>'
        '<g class="bob">'
        '<rect x="-24" y="-52" width="48" height="42" rx="12" fill="url(#metal)"/>'
        '<rect x="-17" y="-46" width="34" height="22" rx="7" fill="url(#dark)"/>'
        '<g class="blink"><rect x="-11" y="-40" width="6" height="9" rx="3" fill="#8fe8ff"/><rect x="5" y="-40" width="6" height="9" rx="3" fill="#8fe8ff"/></g>'
        '<path d="M-5 -28 q5 3 10 0" stroke="#8fe8ff" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
        '<line x1="0" y1="-52" x2="0" y2="-62" stroke="#7c74ae" stroke-width="2"/><circle class="ant" cx="0" cy="-64" r="3.5" fill="#ff9e7a"/>'
        '<rect x="-14" y="-20" width="28" height="4" rx="2" fill="#a59dd0"/>'
        # left arm with a plate
        '<g class="armL"><path d="M-24 -34 L-40 -26 L-46 -40" stroke="#9a92c8" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        '<ellipse cx="-48" cy="-44" rx="14" ry="3.6" fill="#fff6ea" stroke="#c9b8ff"/><ellipse cx="-48" cy="-45" rx="7" ry="1.6" fill="#e9dccb"/></g>'
        # right arm with a mug
        '<g class="armR"><path d="M24 -34 L40 -26 L46 -40" stroke="#9a92c8" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        '<rect x="40" y="-58" width="14" height="14" rx="2" fill="#f2a37a"/><path d="M54 -55 q6 2 0 8" stroke="#f2a37a" stroke-width="2.4" fill="none"/>'
        '<path class="steam" d="M44 -62 q2 -3 0 -6 M49 -62 q2 -3 0 -6" stroke="#fff" stroke-opacity=".7" fill="none"/></g>'
        '</g>'
    )
    return wrap(w, h, x, css, defs, body, "Bimo, a little two-armed robot, lifts a plate and a mug like it is setting a table", tag=("BIMO", "steel", "#cfc8ee", 12))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("paper", mirra), ("humble", humbo), ("riptide", lure), ("vla", bimo)]:
        (OUT / f"mascot-{name}.svg").write_text(fn(), encoding="utf-8")
        print(name, (OUT / f"mascot-{name}.svg").stat().st_size)
