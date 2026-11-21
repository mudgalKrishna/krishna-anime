// Canvas player for src/timeline.json. Mirrors tools/render.py so the web
// version and the README WebP/GIF show the same film.
const W = 1440, H = 600;               // internal resolution (2x the README card)
const canvas = document.getElementById("film");
const ctx = canvas.getContext("2d");
canvas.width = W; canvas.height = H;
const off = Object.assign(document.createElement("canvas"), { width: W, height: H });
const octx = off.getContext("2d");
const mask = Object.assign(document.createElement("canvas"), { width: W, height: H });
const mctx = mask.getContext("2d");
const bar = document.getElementById("progress");

const frac = (x) => x - Math.floor(x);
const hsh = (i, k) => frac(Math.sin(i * 12.9898 + k * 78.233) * 43758.5453);
const clamp = (x, a = 0, b = 1) => Math.min(Math.max(x, a), b);
const smooth = (p) => { p = clamp(p); return p * p * (3 - 2 * p); };
const lerp = (a, b, p) => a + (b - a) * p;
const EASE = { linear: (p) => p, in: (p) => p * p, out: (p) => 1 - (1 - p) ** 2, inOut: (p) => p * p * (3 - 2 * p) };

let TL, SHOTS, starts = [], TOTAL, LAST_END;
const IMG = {};

async function load() {
  TL = await (await fetch("src/timeline.json")).json();
  SHOTS = TL.shots;
  let t = 0;
  for (const s of SHOTS) { starts.push(t); t += s.dur; }
  LAST_END = t; TOTAL = t + TL.tail;
  const names = [...new Set(SHOTS.flatMap((s) => s.src))];
  // load in story order; playback starts once the opening shots are ready
  const loaders = names.map((n) => new Promise((res) => {
    const im = new Image(); im.decoding = "async";
    im.onload = () => { IMG[n] = im; res(); }; im.onerror = res;
    im.src = `public/frames/${n}.jpg`;
  }));
  await Promise.all(loaders.slice(0, 4));
  Promise.all(loaders).then(() => document.body.classList.add("ready"));
}

function camera(i, tg) {
  const s = SHOTS[i];
  const nxt = i + 1 < SHOTS.length ? SHOTS[i + 1].in.dur : TL.tail;
  const p = EASE[s.ease || "inOut"](clamp((tg - starts[i]) / (s.dur + nxt)));
  const c = {};
  for (const k of "xyzr") c[k] = lerp(s.from[k], s.to[k], p);
  return c;
}

const FX = {
  leaves: [16, "38,28,40", 1.2, 3.0], debris: [24, "34,27,40", 1.0, 3.4],
  sparks: [28, "214,196,255", 0.6, 1.6], motes: [20, "255,214,170", 0.7, 1.8],
};
function particle(kind, k, t) {
  const h1 = hsh(k, 1), h2 = hsh(k, 2), h3 = hsh(k, 3), h4 = hsh(k, 4);
  if (kind === "leaves") return [frac(h1 - t * (0.18 + 0.2 * h2)), frac(h3 - t * 0.04) + 0.02 * Math.sin(t * 3 + k), h4, 0.75];
  if (kind === "debris") return [frac(h1 + 0.03 * Math.sin(t + k)), frac(h3 - t * (0.45 + 0.6 * h2)), h4, 0.85];
  if (kind === "sparks") return [h1, frac(h3 - t * 0.03), h4, 0.25 + 0.75 * Math.max(0, Math.sin(t * 2.2 + h2 * 6.283))];
  return [frac(h1 + t * 0.02), frac(h3 - t * (0.02 + 0.02 * h2) + 0.01 * Math.sin(t + k)), h4,
    0.2 + 0.45 * Math.sin(t * 1.3 + h2 * 6.283) ** 2];
}
function drawFx(c, kind, t, seed) {
  const [n, col, smin, smax] = FX[kind];
  const sc = W / 720, flat = kind === "leaves" || kind === "debris" ? 0.7 : 1;
  for (let k = 0; k < n; k++) {
    const [u, v, s01, al] = particle(kind, k + seed * 101, t);
    const r = (smin + (smax - smin) * s01) * sc;
    c.fillStyle = `rgba(${col},${al})`;
    c.beginPath(); c.ellipse(u * W, v * H, r, r * flat, 0, 0, 6.283); c.fill();
  }
}

function drawShot(c, i, tg) {
  const s = SHOTS[i], lt = tg - starts[i];
  const name = s.src.length > 1 ? s.src[Math.floor(lt / s.period) % s.src.length] : s.src[0];
  const im = IMG[name];
  c.fillStyle = "#08060e"; c.fillRect(0, 0, W, H);
  if (!im) return;
  const w = im.naturalWidth, h = im.naturalHeight, cam = camera(i, tg);
  let sc = Math.max(W / w, H / h) * cam.z;
  const r = (cam.r * Math.PI) / 180, cs = Math.abs(Math.cos(r)), sn = Math.abs(Math.sin(r));
  let ex = (W * cs + H * sn) / (2 * sc), ey = (W * sn + H * cs) / (2 * sc);
  if (ex * 2 > w || ey * 2 > h) {
    sc *= Math.max((ex * 2) / w, (ey * 2) / h) * 1.001;
    ex = (W * cs + H * sn) / (2 * sc); ey = (W * sn + H * cs) / (2 * sc);
  }
  let px = clamp(cam.x * w, ex, w - ex), py = clamp(cam.y * h, ey, h - ey);
  if (s.shake) {
    const f = s.shake.freq, amp = (s.shake.amp * (W / 720) * Math.exp(-s.shake.decay * lt)) / sc;
    px += amp * (Math.sin(lt * f * 6.283) + 0.5 * Math.sin(lt * f * 15.1));
    py += amp * (Math.cos(lt * f * 5.31) + 0.5 * Math.sin(lt * f * 11.7));
  }
  c.save();
  c.imageSmoothingQuality = "high";
  c.translate(W / 2, H / 2); c.rotate(r); c.scale(sc, sc); c.translate(-px, -py);
  c.drawImage(im, 0, 0);
  c.restore();
  for (const fx of s.fx || []) drawFx(c, fx, lt, i);
}

function transition(kind, p) {
  // ctx holds the outgoing shot, off holds the incoming one
  const q = smooth(p);
  if (kind === "dissolve" || kind === "fadeblack") {
    ctx.globalAlpha = q; ctx.drawImage(off, 0, 0); ctx.globalAlpha = 1; return;
  }
  if (kind === "wipe") {
    const gx = 0.75 / W, gy = 0.25 / H, g2 = gx * gx + gy * gy;
    const grad = (a, b) => octx.createLinearGradient(0, 0, gx / g2, gy / g2);
    const d1 = q * 1.35, d0 = d1 - 0.22;
    const m = grad();
    m.addColorStop(clamp(d0), `rgba(0,0,0,${d0 < 0 ? clamp(d1 / 0.22) : 1})`);
    m.addColorStop(clamp(d1), "rgba(0,0,0,0)");
    octx.globalCompositeOperation = "destination-in"; octx.fillStyle = m; octx.fillRect(0, 0, W, H);
    octx.globalCompositeOperation = "source-over";
    ctx.drawImage(off, 0, 0);
    const gl = grad(), mid = d1 - 0.11, a = 0.45 * Math.sin(Math.PI * p);
    gl.addColorStop(clamp(mid - 0.12), "rgba(235,215,255,0)");
    gl.addColorStop(clamp(mid), `rgba(235,215,255,${a})`);
    gl.addColorStop(clamp(mid + 0.12), "rgba(235,215,255,0)");
    ctx.globalCompositeOperation = "lighter"; ctx.fillStyle = gl; ctx.fillRect(0, 0, W, H);
    ctx.globalCompositeOperation = "source-over"; return;
  }
  if (kind === "blocks") {
    const bs = Math.max(3, Math.round(W / 120)), bw = Math.floor(W / bs) + 1, bh = Math.floor(H / bs) + 1;
    mctx.clearRect(0, 0, W, H);
    for (let y = 0; y < bh; y++) for (let x = 0; x < bw; x++) {
      const a = clamp((q * 1.5 - (0.45 * hsh(x + 7, y + 3) + 0.55 * (1 - x / bw))) / 0.5);  // sweeps from the window (right)
      if (a <= 0) continue;
      mctx.fillStyle = `rgba(0,0,0,${a})`; mctx.fillRect(x * bs, y * bs, bs, bs);
    }
    octx.globalCompositeOperation = "destination-in"; octx.drawImage(mask, 0, 0);
    octx.globalCompositeOperation = "source-over"; ctx.drawImage(off, 0, 0); return;
  }
  if (kind === "focus") {
    ctx.globalAlpha = smooth(p * 1.6);
    ctx.filter = `blur(${(1 - q) * 6 * (W / 720)}px)`;
    ctx.drawImage(off, 0, 0);
    ctx.filter = "none"; ctx.globalAlpha = 1; return;
  }
  ctx.drawImage(off, 0, 0);
}

function vignette() {
  const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, W * 0.62);
  g.addColorStop(0, "rgba(10,6,20,0)"); g.addColorStop(1, "rgba(10,6,20,0.32)");
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}

function frame(tg) {
  let i = 0;
  for (let k = 0; k < SHOTS.length; k++) if (starts[k] <= tg) i = k;
  const tin = SHOTS[i].in, lt = tg - starts[i];
  if (tin.type !== "cut" && lt < tin.dur) {
    if (i > 0) drawShot(ctx, i - 1, tg); else { ctx.fillStyle = "#08060e"; ctx.fillRect(0, 0, W, H); }
    drawShot(octx, i, tg);
    transition(tin.type, lt / tin.dur);
  } else drawShot(ctx, i, tg);
  if (SHOTS[i].end === "fin") {
    const a = smooth((tg - (LAST_END - 1.8)) / 0.8);
    if (a > 0) {
      ctx.fillStyle = `rgba(250,236,220,${0.9 * a})`;
      ctx.font = `${Math.round(H * 0.11)}px "Yu Gothic","Hiragino Mincho ProN","Noto Serif JP",serif`;
      ctx.textAlign = "right"; ctx.textBaseline = "alphabetic";
      ctx.fillText("終", W - H * 0.08, H - H * 0.07);
    }
  }
  vignette();
  if (tg > LAST_END) {
    ctx.fillStyle = `rgba(8,6,14,${smooth((tg - LAST_END) / TL.tail)})`; ctx.fillRect(0, 0, W, H);
  }
  bar.style.transform = `scaleX(${clamp(tg / TOTAL)})`;
}

// ------------------------------------------------------------- playback
let t0 = null, playing = true, ended = false;
function tick(now) {
  if (t0 === null) t0 = now;
  let tg = (now - t0) / 1000;
  if (tg >= TOTAL) { tg = TOTAL - 1e-3; ended = true; document.body.classList.add("ended"); }
  frame(tg);
  if (!ended) requestAnimationFrame(tick);
}
function replay() {
  ended = false; t0 = null; document.body.classList.remove("ended");
  Sound.restart(0);
  requestAnimationFrame(tick);
}
document.getElementById("replay").addEventListener("click", replay);
canvas.addEventListener("click", () => ended && replay());

// ------------------------------------------------------------- sound (procedural, muted by default)
const Sound = (() => {
  let ac = null, master = null, on = false, nodes = [];
  const noise = () => {
    const b = ac.createBuffer(1, ac.sampleRate * 2, ac.sampleRate), d = b.getChannelData(0);
    for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    return b;
  };
  let nbuf;
  const at = (tg, from) => ac.currentTime + (tg - from);
  function noiseSrc(type, freq, q) {
    const s = ac.createBufferSource(); s.buffer = nbuf; s.loop = true;
    const f = ac.createBiquadFilter(); f.type = type; f.frequency.value = freq; f.Q.value = q;
    const g = ac.createGain(); g.gain.value = 0;
    s.connect(f).connect(g).connect(master); nodes.push(s); return { s, g, f };
  }
  function schedule(from) {
    const span = (id) => { const i = SHOTS.findIndex((s) => s.id === id); return [starts[i], starts[i] + SHOTS[i].dur]; };
    const [r0] = span("wide_run"), [, r1] = span("run_cycle"), [c0, c1] = span("cliff_edge");
    const [f0] = span("lose_balance"), [, f1] = span("abyss"), [a0] = span("boundary"), [, a1] = span("vortex");
    const [m0] = span("dream_fade");
    // ambience wind under everything
    const amb = noiseSrc("lowpass", 500, 0.5); amb.s.start();
    amb.g.gain.setValueAtTime(0.0001, at(Math.max(from, 0), from));
    amb.g.gain.linearRampToValueAtTime(0.05, at(Math.max(from, 1), from));
    // footsteps that speed up toward the cliff, then silence
    for (let t = r0 + 0.2, gap = 0.36; t < c1 - 0.6; t += gap, gap = Math.max(0.24, gap * 0.985)) {
      if (t < from) continue;
      const s = ac.createBufferSource(); s.buffer = nbuf;
      const f = ac.createBiquadFilter(); f.type = "bandpass"; f.frequency.value = 160 + Math.random() * 60; f.Q.value = 1.2;
      const g = ac.createGain(); g.gain.setValueAtTime(0.0001, at(t, from));
      g.gain.exponentialRampToValueAtTime(0.5, at(t + 0.01, from)); g.gain.exponentialRampToValueAtTime(0.0001, at(t + 0.12, from));
      s.connect(f).connect(g).connect(master); s.start(at(t, from), Math.random()); s.stop(at(t + 0.15, from)); nodes.push(s);
    }
    // fall: rushing wind swell
    const wind = noiseSrc("bandpass", 700, 0.7); wind.s.start();
    const W0 = Math.max(f0, from);
    wind.g.gain.setValueAtTime(0.0001, at(W0, from));
    wind.g.gain.linearRampToValueAtTime(0.35, at(Math.max(f0 + 2.5, from), from));
    wind.g.gain.linearRampToValueAtTime(0.0001, at(Math.max(a0 + 0.8, from), from));
    wind.f.frequency.setValueAtTime(500, at(W0, from)); wind.f.frequency.linearRampToValueAtTime(1300, at(Math.max(f1, from), from));
    // AI world: soft detuned pad
    [220, 277.18, 329.63, 440.5].forEach((hz, k) => {
      const o = ac.createOscillator(); o.type = k % 2 ? "triangle" : "sine"; o.frequency.value = hz;
      const g = ac.createGain(); g.gain.setValueAtTime(0.0001, at(Math.max(a0 - 0.5, from), from));
      g.gain.linearRampToValueAtTime(0.045, at(Math.max(a0 + 1.5, from), from));
      g.gain.linearRampToValueAtTime(0.0001, at(Math.max(a1 + 1.2, from), from));
      o.connect(g).connect(master); o.start(); o.stop(at(Math.max(a1 + 1.5, from), from)); nodes.push(o);
    });
    // morning: gentle piano-like notes
    const notes = [523.25, 659.25, 783.99, 659.25, 587.33, 783.99, 880, 783.99, 659.25, 523.25, 587.33, 659.25];
    notes.forEach((hz, k) => {
      const t = m0 + 1.2 + k * 1.15; if (t < from || t > TOTAL) return;
      const o = ac.createOscillator(); o.type = "sine"; o.frequency.value = hz;
      const o2 = ac.createOscillator(); o2.type = "sine"; o2.frequency.value = hz * 2;
      const g = ac.createGain(), g2 = ac.createGain(); g2.gain.value = 0.25;
      g.gain.setValueAtTime(0.0001, at(t, from)); g.gain.exponentialRampToValueAtTime(0.12, at(t + 0.02, from));
      g.gain.exponentialRampToValueAtTime(0.0001, at(t + 2.4, from));
      o.connect(g); o2.connect(g2).connect(g); g.connect(master);
      o.start(at(t, from)); o2.start(at(t, from)); o.stop(at(t + 2.5, from)); o2.stop(at(t + 2.5, from)); nodes.push(o, o2);
    });
    amb.g.gain.linearRampToValueAtTime(0.0001, at(Math.max(TOTAL, from), from));
  }
  function stopAll() { nodes.forEach((n) => { try { n.stop(); } catch (e) {} }); nodes = []; }
  return {
    toggle() {
      on = !on;
      if (on && !ac) { ac = new AudioContext(); master = ac.createGain(); master.gain.value = 0.8; master.connect(ac.destination); nbuf = noise(); }
      stopAll();
      if (on) { ac.resume(); schedule(t0 === null ? 0 : (performance.now() - t0) / 1000); }
      return on;
    },
    restart(from) { if (on) { stopAll(); schedule(from); } },
  };
})();
const sndBtn = document.getElementById("sound");
sndBtn.addEventListener("click", () => {
  const on = Sound.toggle();
  sndBtn.textContent = on ? "sound on" : "sound off";
  sndBtn.setAttribute("aria-pressed", on);
});

// ?t=12.5 renders a single still at that time (handy for previews / QA)
const still = new URLSearchParams(location.search).get("t");
load().then(async () => {
  if (still === null) return requestAnimationFrame(tick);
  await new Promise((r) => { const w = () => document.body.classList.contains("ready") ? r() : setTimeout(w, 50); w(); });
  frame(parseFloat(still));
});
