"""Animated SVG card for the NeurIPS workshop paper.

Numbers are from "Symmetry Alignment Across Depth in Transformer Merging"
(NeurReps @ NeurIPS 2026): (6,12) pair on WikiText-2, vanilla averaging
barrier 2.279 nats -> P+O alignment 0.138 nats; across all pairs the
alignment removes 90.1-94.6% and leaves 0.098-0.244 nats.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "profile" / "assets" / "neurips-barrier.svg"
X0, X1, Y0, PX_PER_NAT = 70, 520, 250, 62
N = 48


def path(peak):
    pts = []
    for i in range(N + 1):
        lam = i / N
        b = peak * 4 * lam * (1 - lam) * (1 + 0.12 * (lam - 0.5))  # slight skew toward the deep end
        pts.append((X0 + (X1 - X0) * lam, Y0 - b * PX_PER_NAT))
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


naive, aligned = path(2.279), path(0.138)
floor_y = Y0 - 0.138 * PX_PER_NAT
DUR = "8s"
KT = "0;0.22;0.5;0.88;1"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 300" width="880" height="300" role="img" aria-label="Animated plot: aligning a shallow and a deep Transformer removes about 94 percent of the loss barrier but leaves a residual floor">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1b1730"/><stop offset="1" stop-color="#121022"/></linearGradient>
  <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f2a37a" stop-opacity=".35"/><stop offset="1" stop-color="#f2a37a" stop-opacity="0"/></linearGradient>
  <style>
    .t{{font-family:Georgia,'Times New Roman',serif}} .m{{font-family:ui-monospace,Consolas,monospace}}
    .fade1{{animation:f1 {DUR} infinite}} .fade2{{animation:f2 {DUR} infinite}}
    @keyframes f1{{0%,18%{{opacity:1}}30%,88%{{opacity:.35}}100%{{opacity:1}}}}
    @keyframes f2{{0%,40%{{opacity:0}}52%,86%{{opacity:1}}94%,100%{{opacity:0}}}}
  </style>
</defs>
<rect x="1" y="1" width="878" height="298" rx="14" fill="url(#bg)" stroke="#544878"/>
<text x="28" y="38" class="t" font-size="17" fill="#f4dccb">Symmetry Alignment Across Depth in Transformer Merging</text>
<text x="28" y="60" class="m" font-size="12" fill="#a99fd6">NeurIPS 2026 workshop · NeurReps · shallow ⟷ deep Transformer, linear path</text>
<g stroke="#3a3358" stroke-width="1">
  <line x1="{X0}" y1="{Y0}" x2="{X1}" y2="{Y0}"/><line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y0 - 2.5 * PX_PER_NAT:.0f}"/>
  <line x1="{X0}" y1="{Y0 - PX_PER_NAT}" x2="{X1}" y2="{Y0 - PX_PER_NAT}" stroke-dasharray="2 5"/>
  <line x1="{X0}" y1="{Y0 - 2 * PX_PER_NAT}" x2="{X1}" y2="{Y0 - 2 * PX_PER_NAT}" stroke-dasharray="2 5"/>
</g>
<g class="m" font-size="10" fill="#7d74a8">
  <text x="{X0 - 8}" y="{Y0 + 4}" text-anchor="end">0</text><text x="{X0 - 8}" y="{Y0 - PX_PER_NAT + 4}" text-anchor="end">1</text><text x="{X0 - 8}" y="{Y0 - 2 * PX_PER_NAT + 4}" text-anchor="end">2</text>
  <text x="{X0}" y="{Y0 + 18}">shallow (padded)</text><text x="{X1}" y="{Y0 + 18}" text-anchor="end">deep</text>
  <text x="{(X0 + X1) / 2}" y="{Y0 + 18}" text-anchor="middle">interpolation λ</text>
  <text x="22" y="{Y0 - 70}" transform="rotate(-90 22 {Y0 - 70})" text-anchor="middle">loss barrier (nats)</text>
</g>
<path d="{naive}" fill="none" stroke="#f2a37a" stroke-width="1.2" stroke-dasharray="3 4" class="fade1"/>
<text x="{(X0 + X1) / 2}" y="{Y0 - 2.279 * PX_PER_NAT - 10:.0f}" text-anchor="middle" class="m fade1" font-size="11" fill="#f2a37a">naive averaging · 2.28</text>
<path d="{naive}L{X1} {Y0} L{X0} {Y0}Z" fill="url(#fill)" stroke="none">
  <animate attributeName="d" dur="{DUR}" repeatCount="indefinite" keyTimes="{KT}" calcMode="spline" keySplines=".4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1"
   values="{naive}L{X1} {Y0} L{X0} {Y0}Z;{naive}L{X1} {Y0} L{X0} {Y0}Z;{aligned}L{X1} {Y0} L{X0} {Y0}Z;{aligned}L{X1} {Y0} L{X0} {Y0}Z;{naive}L{X1} {Y0} L{X0} {Y0}Z"/>
</path>
<path d="{naive}" fill="none" stroke="#f6c3a2" stroke-width="2.4" stroke-linecap="round">
  <animate attributeName="d" dur="{DUR}" repeatCount="indefinite" keyTimes="{KT}" calcMode="spline" keySplines=".4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1"
   values="{naive};{naive};{aligned};{aligned};{naive}"/>
  <animate attributeName="stroke" dur="{DUR}" repeatCount="indefinite" keyTimes="{KT}" values="#f6c3a2;#f6c3a2;#c9b8ff;#c9b8ff;#f6c3a2"/>
</path>
<g class="fade2">
  <line x1="{X0}" y1="{floor_y:.1f}" x2="{X1}" y2="{floor_y:.1f}" stroke="#c9b8ff" stroke-width="1" stroke-dasharray="4 4"/>
  <text x="{(X0 + X1) / 2}" y="{floor_y - 10:.0f}" text-anchor="middle" class="m" font-size="11" fill="#c9b8ff">permutation + orthogonal alignment · 0.14, never 0</text>
</g>
<line x1="560" y1="84" x2="560" y2="262" stroke="#2c2747"/>
<g class="t">
  <text x="590" y="122" font-size="40" fill="#f2a37a">−94.6%</text>
  <text x="592" y="144" class="m" font-size="11" fill="#cfc6ee">barrier removed (best of 5 pairs)</text>
  <text x="590" y="196" font-size="26" fill="#c9b8ff">0.098 – 0.244</text>
  <text x="592" y="216" class="m" font-size="11" fill="#cfc6ee">nats of residual in every config</text>
  <text x="592" y="252" class="m" font-size="10.5" fill="#8d84b8">5 depth pairs · 3 corpora · 3 seeds</text>
</g>
</svg>
'''
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg, encoding="utf-8")
print("wrote", OUT, len(svg), "bytes")
