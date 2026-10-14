// CLAUDE — Motion Reel 26
// Everything is drawn with Canvas 2D from a single pure function of time.
// Music runs at 128 BPM: 1 bar = 1.875 s, 8 bars = exactly 15 s.
'use strict';

const W = 1920, H = 1080, FPS = 60, DUR = 15;
const BPM = 128, BEAT = 60 / BPM, BAR = BEAT * 4;
const COL = {
  ink: '#0B0B10', cream: '#F2ECE1', coral: '#FF4B1F',
  cobalt: '#2438F5', yellow: '#FFD12A', white: '#FFFFFF',
};
const DISPLAY = 'D', MONO = 'M';

// ---------- utilities ----------
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
const prog = (t, a, b) => clamp((t - a) / (b - a));
const TAU = Math.PI * 2;
const E = {
  outExpo: t => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t)),
  inExpo: t => (t <= 0 ? 0 : Math.pow(2, 10 * t - 10)),
  inOutExpo: t => (t <= 0 ? 0 : t >= 1 ? 1 : t < 0.5 ? Math.pow(2, 20 * t - 10) / 2 : (2 - Math.pow(2, -20 * t + 10)) / 2),
  outCubic: t => 1 - Math.pow(1 - t, 3),
  inCubic: t => t * t * t,
  inOutCubic: t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  outQuint: t => 1 - Math.pow(1 - t, 5),
  outBack: t => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  outElastic: t => (t <= 0 ? 0 : t >= 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * (TAU / 3)) + 1),
};
function rng(seed) { // mulberry32
  return () => {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const hex = h => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
const mix = (a, b, t) => { const A = hex(a), B = hex(b); return `rgb(${A.map((v, i) => Math.round(lerp(v, B[i], t))).join(',')})`; };
// decaying pulse after each hit (to pump with the kick)
const pulse = (t, k = 9) => (t < 0 ? 0 : Math.exp(-t * k));
const beatPulse = (lt, k = 9) => pulse(lt - Math.floor(lt / BEAT) * BEAT, k);

function font(weight, size, family = DISPLAY, italic = false) {
  return `${italic ? 'italic ' : ''}${weight} ${size}px "${family}"`;
}
function spacedText(ctx, str, x, y, tracking, align = 'center') {
  // manual letter tracking (Canvas 2D letterSpacing is not reliable everywhere)
  const ws = [...str].map(ch => ctx.measureText(ch).width);
  const total = ws.reduce((a, b) => a + b, 0) + tracking * (str.length - 1);
  let cx = align === 'center' ? x - total / 2 : align === 'right' ? x - total : x;
  ctx.textAlign = 'left';
  [...str].forEach((ch, i) => { ctx.fillText(ch, cx, y); cx += ws[i] + tracking; });
  return total;
}

// ---------- scene 0 · intro: dot → line → iris ----------
const TYPE_TXT = 'MOTION REEL — 2026';
const TYPE_START = 0.62, TYPE_STEP = 0.034;
function sIntro(ctx, lt) {
  ctx.fillStyle = COL.ink; ctx.fillRect(0, 0, W, H);
  const cx = W / 2, cy = H / 2;
  ctx.save(); ctx.translate(cx, cy);

  // a dot pops in and stretches into a line
  const pop = E.outBack(prog(lt, 0.06, 0.34));
  const stretch = E.outExpo(prog(lt, BEAT, BEAT + 0.5));
  const collapse = E.inExpo(prog(lt, 1.3, 1.62));
  const w = lerp(26 * pop, 1500, stretch) * (1 - collapse);
  const h = lerp(26 * pop, 4, E.outExpo(prog(lt, BEAT, BEAT + 0.2)));
  // on beat 3 the line splits into 7 lines
  const split = E.outExpo(prog(lt, BEAT * 2, BEAT * 2 + 0.45));
  for (let i = -3; i <= 3; i++) {
    const y = i * 46 * split * (1 - collapse);
    const len = w * (i === 0 ? 1 : lerp(1, 0.35 + 0.5 * Math.abs(Math.sin(i * 1.7)), split));
    const off = i === 0 ? 0 : Math.sin(i * 2.3) * 160 * split * (1 - collapse);
    if (i !== 0 && split <= 0) continue;
    ctx.fillStyle = i === 2 ? COL.coral : COL.cream;
    ctx.globalAlpha = i === 0 ? 1 : split;
    const r = Math.min(h / 2, len / 2);
    ctx.beginPath(); ctx.roundRect(-len / 2 + off, y - h / 2, Math.max(len, 0.01), h, r); ctx.fill();
  }
  ctx.globalAlpha = 1;

  // typed text, one character at a time (each one has a click in the music)
  const n = Math.floor(clamp((lt - TYPE_START) / TYPE_STEP, 0, TYPE_TXT.length));
  if (lt > TYPE_START - 0.05 && collapse < 1) {
    ctx.font = font(400, 26, MONO); ctx.fillStyle = COL.cream;
    ctx.globalAlpha = 1 - collapse;
    const shown = TYPE_TXT.slice(0, n);
    spacedText(ctx, shown, -TYPE_TXT.length * 9.2, -205, 3, 'left');
    const cursorOn = Math.floor(lt * 8) % 2 === 0 || n < TYPE_TXT.length;
    if (cursorOn) {
      ctx.font = font(400, 26, MONO);
      const wShown = shown.length ? ctx.measureText('M').width * shown.length + 3 * shown.length : 0;
      ctx.fillStyle = COL.coral; ctx.fillRect(-TYPE_TXT.length * 9.2 + wShown + 2, -228, 14, 30);
    }
    ctx.globalAlpha = 1;
  }
  ctx.restore();

  // coral iris that opens the next scene
  const ir = E.inExpo(prog(lt, 1.42, BAR));
  if (ir > 0) {
    ctx.fillStyle = COL.coral; ctx.beginPath(); ctx.arc(cx, cy, ir * 1150, 0, TAU); ctx.fill();
    ctx.strokeStyle = COL.cream; ctx.lineWidth = 6 * (1 - ir);
    ctx.beginPath(); ctx.arc(cx, cy, ir * 1150 + 30, 0, TAU); ctx.stroke();
  }
}

// ---------- scene 1 · kinetic type ----------
const WORDS = ['MOTION', 'DESIGN', 'RHYTHM', 'TIMING'];
function sType(ctx, lt) {
  ctx.fillStyle = COL.coral; ctx.fillRect(0, 0, W, H);
  ctx.save();
  ctx.translate(W / 2, H / 2);
  ctx.rotate(-0.07 + 0.03 * E.inOutCubic(prog(lt, 0, BAR)));
  const zoom = 1 + 0.06 * lt + 0.03 * beatPulse(lt, 7);
  ctx.scale(zoom, zoom);

  // outlined marquee rows
  ctx.font = font(900, 150); ctx.textBaseline = 'middle';
  const row = 'MOTION — DESIGN — MOTION — DESIGN — MOTION — DESIGN — ';
  const rowW = ctx.measureText(row).width;
  for (let i = -4; i <= 4; i++) {
    if (i === 0) continue;
    const dir = i % 2 ? 1 : -1;
    const ent = 1 - E.outExpo(prog(lt, Math.abs(i) * 0.05, 0.7 + Math.abs(i) * 0.05));
    const x = -rowW / 2 + dir * (lt * 420 + ent * 2400) + (i * 337) % 500;
    ctx.lineWidth = 2.5;
    ctx.strokeStyle = Math.abs(i) === 1 ? COL.ink : 'rgba(11,11,16,0.55)';
    ctx.strokeText(row, x, i * 132);
  }

  // central word: per-letter slot-machine roll on every beat
  const size = 300, cell = size * 0.78, rowH = size * 0.95;
  ctx.font = font(900, size); ctx.textAlign = 'center';
  ctx.fillStyle = COL.ink;
  ctx.fillRect(-W, -rowH / 2 - 8, W * 2, rowH + 16);
  const k = Math.min(3, Math.floor(lt / BEAT));
  const layout = word => {
    const ws = [...word].map(ch => ctx.measureText(ch).width), tr = -4;
    const tot = ws.reduce((x, y) => x + y, 0) + tr * (ws.length - 1);
    let x = -tot / 2; return ws.map(w => { const c = x + w / 2; x += w + tr; return c; });
  };
  ctx.save(); ctx.beginPath(); ctx.rect(-W, -rowH / 2, W * 2, rowH); ctx.clip();
  const inY = j => (1 - E.outBack(prog(lt, 0.02 + j * 0.035, 0.42 + j * 0.035))) * -rowH * 1.2;
  const lp = j => (k === 0 ? 1 : E.inOutExpo(prog(lt, k * BEAT + j * 0.03, k * BEAT + j * 0.03 + 0.3)));
  ctx.fillStyle = COL.cream;
  if (k > 0) layout(WORDS[k - 1]).forEach((x, j) => ctx.fillText(WORDS[k - 1][j], x, -lp(j) * rowH + 22));
  layout(WORDS[k]).forEach((x, j) => {
    const p = lp(j), tc = k * BEAT + j * 0.03;
    const sq = k > 0 ? 1 + 0.18 * pulse(lt - tc - 0.28, 12) : 1;
    ctx.save(); ctx.translate(x, inY(j) + (1 - p) * rowH + 22); ctx.scale(1 / sq, sq);
    ctx.fillText(WORDS[k][j], 0, 0); ctx.restore();
  });
  ctx.restore();
  // thin italic caption
  ctx.font = font(200, 64, DISPLAY, true); ctx.fillStyle = COL.ink; ctx.textAlign = 'right';
  const subA = E.outExpo(prog(lt, 0.35, 0.9));
  ctx.globalAlpha = subA;
  ctx.fillText('kinetic type, on the beat', 3 * cell - 10 + (1 - subA) * 80, rowH / 2 + 70);
  ctx.globalAlpha = 1;
  ctx.restore();

  // exit: black bars wipe in from the right
  const n = 8;
  for (let i = 0; i < n; i++) {
    const p = E.inOutExpo(prog(lt, 1.42 + i * 0.025, 1.78 + i * 0.012));
    if (p <= 0) continue;
    const bh = H / n;
    ctx.fillStyle = COL.ink;
    ctx.fillRect(W - p * W, i * bh - 1, p * W + 2, bh + 2);
  }
}

// ---------- scene 2 · shape morph ----------
function rayPoly(verts, th) {
  const dx = Math.cos(th), dy = Math.sin(th);
  let best = 1e9;
  for (let i = 0; i < verts.length; i++) {
    const [ax, ay] = verts[i], [bx, by] = verts[(i + 1) % verts.length];
    const ex = bx - ax, ey = by - ay;
    const den = dx * ey - dy * ex;
    if (Math.abs(den) < 1e-9) continue;
    const s = (ax * ey - ay * ex) / den;
    const u = (ax * dy - ay * dx) / den;
    if (s > 0 && u >= -1e-6 && u <= 1 + 1e-6) best = Math.min(best, s);
  }
  return best;
}
const ngon = (n, r = 1, rot = -Math.PI / 2) => Array.from({ length: n }, (_, i) => [Math.cos(rot + (i * TAU) / n) * r, Math.sin(rot + (i * TAU) / n) * r]);
const star = (n, r1, r2) => Array.from({ length: n * 2 }, (_, i) => { const a = -Math.PI / 2 + (i * Math.PI) / n, r = i % 2 ? r2 : r1; return [Math.cos(a) * r, Math.sin(a) * r]; });
const NPTS = 360;
const SHAPES = [
  Array(NPTS).fill(1),
  ngon(4, 1.15, Math.PI / 4),
  ngon(3, 1.25),
  star(5, 1.25, 0.55),
].map(s => (Array.isArray(s[0]) ? Array.from({ length: NPTS }, (_, i) => rayPoly(s, (i / NPTS) * TAU)) : s));
const SHAPE_COL = [COL.cream, COL.yellow, COL.coral, COL.cobalt];

function shapeAt(lt) {
  // shape index from time, plus morph progress
  const k = clamp(Math.floor(lt / BEAT), 0, 3);
  const p = k === 0 ? 1 : E.outBack(prog(lt, k * BEAT, k * BEAT + 0.32));
  const a = SHAPES[Math.max(0, k - 1)], b = SHAPES[k];
  const radii = b.map((r, i) => lerp(a[i], r, p));
  const col = k === 0 ? SHAPE_COL[0] : mix(SHAPE_COL[k - 1], SHAPE_COL[k], clamp(p));
  return { radii, col, k, p };
}
function pathRadii(ctx, radii, R, rot) {
  ctx.beginPath();
  for (let i = 0; i <= NPTS; i++) {
    const th = (i / NPTS) * TAU, r = radii[i % NPTS] * R;
    const x = Math.cos(th + rot) * r, y = Math.sin(th + rot) * r;
    i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
  }
  ctx.closePath();
}
function sMorph(ctx, lt) {
  ctx.fillStyle = COL.ink; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.translate(W / 2, H / 2);
  const intro = E.outElastic(prog(lt, 0, 0.7));
  const exit = E.inExpo(prog(lt, 1.5, BAR));
  const R = 250 * intro * (1 + 0.08 * beatPulse(lt, 8)) * (1 + exit * 30);
  const rotOf = t => t * 0.9 + Math.floor(t / BEAT) * (Math.PI / 4) * 0 + E.outBack(prog(t % BEAT, 0, 0.3)) * 0.4 + Math.floor(t / BEAT) * 0.4;

  // orbiting ring of dots
  if (exit < 0.6) {
    for (let i = 0; i < 24; i++) {
      const a = (i / 24) * TAU - lt * 0.6;
      const rr = 470 * E.outExpo(prog(lt, 0.05 + i * 0.008, 0.6)) + 18 * Math.sin(lt * 6 + i);
      const s = (i % 6 === 0 ? 10 : 4) * (1 + 0.8 * beatPulse(lt - i * 0.01, 10));
      ctx.fillStyle = i % 6 === 0 ? COL.coral : COL.cream;
      ctx.globalAlpha = 1 - exit;
      ctx.beginPath(); ctx.arc(Math.cos(a) * rr, Math.sin(a) * rr, s, 0, TAU); ctx.fill();
    }
    ctx.globalAlpha = 1;
    // dashed guide circle, like a design tool overlay
    ctx.strokeStyle = 'rgba(242,236,225,0.35)'; ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 10]); ctx.lineDashOffset = -lt * 60;
    ctx.beginPath(); ctx.arc(0, 0, 360 * intro, 0, TAU); ctx.stroke();
    ctx.setLineDash([]);
  }

  // outlined echoes (the shape's recent past)
  for (let e = 7; e >= 1; e--) {
    const tt = lt - e * 0.03;
    if (tt < 0) continue;
    const s = shapeAt(tt);
    const Re = 250 * E.outElastic(prog(tt, 0, 0.7)) * (1 + 0.08 * beatPulse(tt, 8)) * (1 + E.inExpo(prog(tt, 1.5, BAR)) * 30);
    pathRadii(ctx, s.radii, Re, rotOf(tt));
    ctx.strokeStyle = s.col; ctx.globalAlpha = (1 - e / 8) * 0.55; ctx.lineWidth = 3;
    ctx.stroke();
  }
  ctx.globalAlpha = 1;
  const s = shapeAt(lt);
  pathRadii(ctx, s.radii, R, rotOf(lt));
  ctx.fillStyle = exit > 0 ? mix(SHAPE_COL[3], COL.cream, E.outCubic(exit * 1.6 > 1 ? 1 : exit * 1.6)) : s.col; ctx.fill();

  // shape label
  if (exit < 0.3) {
    const names = ['CIRCLE', 'SQUARE', 'TRIANGLE', 'STAR'];
    ctx.font = font(400, 22, MONO); ctx.fillStyle = COL.cream; ctx.globalAlpha = 1 - exit / 0.3;
    spacedText(ctx, `${names[s.k]}  ·  ${String(Math.round(s.p * 100)).padStart(3, '0')}%`, 0, 560 - 40, 4);
    ctx.globalAlpha = 1;
  }
  ctx.restore();
}

// ---------- scene 3 · particles that form a word ----------
const NP = 2600;
let PARTS = null;
function initParticles() {
  const oc = document.createElement('canvas'); oc.width = W; oc.height = H;
  const o = oc.getContext('2d');
  o.font = font(900, 470); o.textAlign = 'center'; o.textBaseline = 'middle'; o.fillStyle = '#000';
  spacedText(o, 'CODE', W / 2, H / 2 + 10, -8);
  const d = o.getImageData(0, 0, W, H).data;
  const pts = [];
  for (let y = 0; y < H; y += 7) for (let x = 0; x < W; x += 7) if (d[(y * W + x) * 4 + 3] > 128) pts.push([x, y]);
  const r = rng(7);
  for (let i = pts.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [pts[i], pts[j]] = [pts[j], pts[i]]; }
  PARTS = Array.from({ length: NP }, (_, i) => {
    const [tx, ty] = pts[i % pts.length];
    return {
      tx: tx + (i >= pts.length ? (r() - 0.5) * 4 : 0), ty,
      a: r() * TAU, r0: 120 + Math.pow(r(), 0.7) * 900, w: (0.6 + r() * 1.4) * (r() < 0.5 ? 1 : 1),
      delay: r() * 0.22, size: r() < 0.08 ? 7 : 3 + r() * 2.5, coral: r() < 0.14,
      ex: r() * TAU, ev: 900 + r() * 1700,
    };
  });
}
function sParticles(ctx, lt) {
  ctx.fillStyle = COL.cream; ctx.fillRect(0, 0, W, H);
  const cx = W / 2, cy = H / 2;
  const burst = E.outExpo(prog(lt, 0, 0.75));
  for (const p of PARTS) {
    // swirl
    const ang = p.a + p.w * lt * 1.6 + Math.sin(lt * 2 + p.r0 * 0.01) * 0.3;
    const rr = p.r0 * burst;
    const sx = cx + Math.cos(ang) * rr * 1.25, sy = cy + Math.sin(ang) * rr * 0.62;
    // converge onto the word
    const c = E.inOutExpo(prog(lt, BEAT * 1.15 + p.delay, BEAT * 2.15 + p.delay));
    let x = lerp(sx, p.tx, c), y = lerp(sy, p.ty, c);
    // small breathing once the word is formed
    const hold = c >= 1 ? Math.sin(lt * 20 + p.a * 5) * 1.2 : 0;
    x += hold; y += hold;
    // final explosion
    const ex = E.inExpo(prog(lt, 1.56, BAR));
    x += Math.cos(p.ex) * p.ev * ex; y += Math.sin(p.ex) * p.ev * ex;
    ctx.fillStyle = p.coral ? COL.coral : COL.ink;
    const s = p.size * (1 + 0.6 * beatPulse(lt - p.delay * 0.3, 10) * (1 - c));
    ctx.fillRect(x - s / 2, y - s / 2, s, s);
  }
  // blue curtain rising from below
  const n = 12;
  for (let i = 0; i < n; i++) {
    const p = E.inOutExpo(prog(lt, 1.5 + Math.abs(i - n / 2) * 0.018, 1.84));
    if (p <= 0) continue;
    const bw = W / n;
    ctx.fillStyle = COL.cobalt; ctx.fillRect(i * bw - 1, H - p * H, bw + 2, p * H);
  }
}

// ---------- scene 4 · 3D cubes ----------
const CUBE_V = [[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]];
const CUBE_F = [[0,1,2,3],[5,4,7,6],[4,0,3,7],[1,5,6,2],[4,5,1,0],[3,2,6,7]];
function rot3(v, ax, ay, az) {
  let [x, y, z] = v;
  let c = Math.cos(ax), s = Math.sin(ax); [y, z] = [y * c - z * s, y * s + z * c];
  c = Math.cos(ay); s = Math.sin(ay); [x, z] = [x * c + z * s, -x * s + z * c];
  c = Math.cos(az); s = Math.sin(az); [x, y] = [x * c - y * s, x * s + y * c];
  return [x, y, z];
}
function sCubes(ctx, lt) {
  ctx.fillStyle = COL.cobalt; ctx.fillRect(0, 0, W, H);
  // perspective floor grid
  ctx.save(); ctx.strokeStyle = 'rgba(242,236,225,0.18)'; ctx.lineWidth = 1.5;
  const horizon = H * 0.52;
  for (let i = 0; i < 18; i++) {
    const z = ((i + (lt * 4) % 1) / 18);
    const y = horizon + Math.pow(z, 2.2) * (H - horizon) * 1.1;
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
  }
  for (let i = -16; i <= 16; i++) {
    ctx.beginPath(); ctx.moveTo(W / 2 + i * 30, horizon); ctx.lineTo(W / 2 + i * 260, H * 1.2); ctx.stroke();
  }
  ctx.restore();

  const cols = 7, rows = 3, gap = 250, F = 1500;
  const camY = Math.sin(lt * 0.9) * 0.35 - 0.15, camX = -0.32;
  const cubes = [];
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const gx = (c - (cols - 1) / 2) * gap, gy = (r - (rows - 1) / 2) * gap;
    const d = Math.hypot(c - 3, r - 1);
    const pop = E.outBack(prog(lt, d * 0.05, 0.45 + d * 0.05));
    const kb = Math.floor(lt / BEAT);
    // on every beat the cubes snap 90° in a wave
    const snap = Array.from({ length: kb + 1 }, (_, b) => E.inOutExpo(prog(lt, b * BEAT + d * 0.03, b * BEAT + 0.35 + d * 0.03))).reduce((a, b) => a + b, 0);
    const fly = E.inExpo(prog(lt, 1.42 + d * 0.025, 1.85));
    const size = 70 * pop * (1 + 0.12 * beatPulse(lt - d * 0.03, 9));
    cubes.push({ gx, gy, size, ax: snap * Math.PI / 2 + lt * 0.5, ay: snap * Math.PI / 2 * (r % 2 ? -1 : 1) + lt * 0.7, fly, hot: (r * cols + c) % 5 === 2 });
  }
  const polys = [];
  const L = [0.4, -0.7, -0.6]; const ln = Math.hypot(...L); L.forEach((v, i) => (L[i] = v / ln));
  for (const cb of cubes) {
    if (cb.size <= 0.5) continue;
    const vs = CUBE_V.map(v => {
      let p = rot3(v.map(x => x * cb.size), cb.ax, cb.ay, 0);
      p = [p[0] + cb.gx, p[1] + cb.gy, p[2] - cb.fly * 1400];
      p = rot3(p, camX, camY, 0);
      p[2] += 1300;
      return p;
    });
    for (const f of CUBE_F) {
      const [a, b, c] = f.map(i => vs[i]);
      const u = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], v = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
      const n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
      const nl = Math.hypot(...n) || 1;
      const center = f.reduce((acc, i) => [acc[0] + vs[i][0] / 4, acc[1] + vs[i][1] / 4, acc[2] + vs[i][2] / 4], [0, 0, 0]);
      if (n[0] * center[0] + n[1] * center[1] + n[2] * center[2] >= 0) continue; // back face
      const lam = clamp(-(n[0] * L[0] + n[1] * L[1] + n[2] * L[2]) / nl, 0, 1);
      const pts = f.map(i => { const p = vs[i]; const z = Math.max(p[2], 60); return [W / 2 + (p[0] * F) / z, H / 2 + (p[1] * F) / z]; });
      polys.push({ z: center[2], pts, col: cb.hot ? mix('#A82A08', COL.coral, 0.35 + 0.65 * lam) : mix('#2A3AC8', COL.cream, 0.3 + 0.7 * Math.pow(lam, 0.8)) });
    }
  }
  polys.sort((a, b) => b.z - a.z);
  ctx.lineJoin = 'round';
  for (const p of polys) {
    ctx.beginPath(); p.pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.closePath();
    ctx.fillStyle = p.col; ctx.fill();
    ctx.strokeStyle = p.col; ctx.lineWidth = 1; ctx.stroke();
  }
  // fade to ink before the cut
  const fl = prog(lt, 1.76, BAR);
  if (fl > 0) { ctx.fillStyle = `rgba(11,11,16,${E.inCubic(fl)})`; ctx.fillRect(0, 0, W, H); }
}

// ---------- scene 5 · liquid metaballs ----------
const MW = 640, MH = 360;
let MB = null;
function sLiquid(ctx, lt) {
  if (!MB) { const c = document.createElement('canvas'); c.width = MW; c.height = MH; MB = { c, x: c.getContext('2d'), img: null }; MB.img = MB.x.createImageData(MW, MH); }
  const sc = MW / W;
  const merge = E.inOutExpo(prog(lt, 1.25, 1.7));
  const grow = E.inExpo(prog(lt, 1.62, BAR));
  const balls = [];
  const nb = 8;
  for (let i = 0; i < nb; i++) {
    const ph = (i / nb) * TAU;
    const orbit = (300 + 140 * Math.sin(lt * 2.1 + i * 1.3)) * (1 + 0.25 * beatPulse(lt, 6)) * (1 - merge) * E.outExpo(prog(lt, 0, 0.6));
    const a = ph + lt * (i % 2 ? 1.1 : -0.8);
    balls.push([W / 2 + Math.cos(a) * orbit * 1.5, H / 2 + Math.sin(a * 1.3) * orbit * 0.75, (85 + 35 * Math.sin(i * 2.7)) * (1 + merge * 0.9) * (1 + grow * 14)]);
  }
  balls.push([W / 2, H / 2, 120 * E.outBack(prog(lt, 0.0, 0.5)) * (1 + grow * 14)]);
  const data = MB.img.data;
  const yA = hex(COL.yellow), cA = hex(COL.coral), kA = hex(COL.ink), bA = hex(COL.cobalt);
  const bs = balls.map(([x, y, r]) => [x * sc, y * sc, (r * sc) * (r * sc)]);
  for (let py = 0; py < MH; py++) {
    for (let px = 0; px < MW; px++) {
      let f = 0;
      for (let b = 0; b < bs.length; b++) { const dx = px - bs[b][0], dy = py - bs[b][1]; f += bs[b][2] / (dx * dx + dy * dy + 1); }
      const i4 = (py * MW + px) * 4;
      // soft edge plus inner shading for a sense of volume
      const inside = clamp((f - 1) / 0.06);
      const rim = clamp((f - 1.0) / 0.5);
      const g = clamp(px / MW * 0.7 + py / MH * 0.3 + Math.sin(lt * 1.5) * 0.15);
      let r = lerp(cA[0], yA[0], g), gg = lerp(cA[1], yA[1], g), bl = lerp(cA[2], yA[2], g);
      const shade = 0.55 + 0.45 * Math.pow(rim, 0.6);
      r *= shade; gg *= shade; bl *= shade;
      // specular highlight
      const hl = clamp((f - 2.6) / 1.5) * 0.5;
      r = lerp(r, 255, hl); gg = lerp(gg, 250, hl); bl = lerp(bl, 235, hl);
      data[i4] = lerp(kA[0], r, inside); data[i4 + 1] = lerp(kA[1], gg, inside); data[i4 + 2] = lerp(kA[2], bl, inside); data[i4 + 3] = 255;
    }
  }
  MB.x.putImageData(MB.img, 0, 0);
  ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(MB.c, 0, 0, W, H);
  // word on top, inverted by the blobs (difference blend)
  ctx.save();
  ctx.globalCompositeOperation = 'difference';
  ctx.font = font(200, 220, DISPLAY, true); ctx.fillStyle = COL.cream; ctx.textBaseline = 'middle';
  const a = E.outExpo(prog(lt, 0.2, 0.9));
  ctx.globalAlpha = a * (1 - grow);
  spacedText(ctx, 'liquid', W / 2 + (1 - a) * 200, H / 2, 6);
  ctx.restore();
}

// ---------- scene 6 · fast-cut montage ----------
const FLASH_WORDS = ['TYPE', 'SHAPE', 'PARTICLES', '3D', 'LIQUID', 'RHYTHM', 'TIMING', 'CRAFT'];
function sMontage(ctx, lt, frameNo) {
  const k = Math.min(3, Math.floor(lt / BEAT));
  const t = lt - k * BEAT;
  if (k === 0) {
    // halftone wave
    ctx.fillStyle = COL.ink; ctx.fillRect(0, 0, W, H);
    const cols = 32, rows = 18, s = W / cols;
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      const x = (c + 0.5) * s, y = (r + 0.5) * s;
      const d = Math.hypot(x - W / 2, y - H / 2);
      const v = 0.5 + 0.5 * Math.sin(d * 0.012 - lt * 14);
      const rad = s * 0.46 * v * E.outExpo(prog(t, d / 4000, d / 4000 + 0.2));
      ctx.fillStyle = (r + c) % 7 === 0 ? COL.coral : COL.cream;
      ctx.beginPath(); ctx.arc(x, y, Math.max(rad, 0), 0, TAU); ctx.fill();
    }
  } else if (k === 1) {
    // radial burst
    ctx.fillStyle = COL.cream; ctx.fillRect(0, 0, W, H);
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.rotate(t * 1.4);
    const n = 56;
    for (let i = 0; i < n; i++) {
      const a = (i / n) * TAU;
      const l0 = 150 + 40 * E.outExpo(prog(t, 0, 0.2)), l1 = l0 + (300 + 500 * Math.abs(Math.sin(i * 1.7 + t * 6))) * E.outExpo(prog(t, i * 0.002, 0.25));
      ctx.strokeStyle = i % 4 === 0 ? COL.coral : COL.ink; ctx.lineWidth = i % 4 === 0 ? 10 : 5; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(Math.cos(a) * l0, Math.sin(a) * l0); ctx.lineTo(Math.cos(a) * l1, Math.sin(a) * l1); ctx.stroke();
    }
    ctx.fillStyle = COL.ink; ctx.beginPath(); ctx.arc(0, 0, 110 * E.outBack(prog(t, 0, 0.25)), 0, TAU); ctx.fill();
    ctx.restore();
  } else if (k === 2) {
    // tech specs and the real frame counter
    ctx.fillStyle = COL.yellow; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = COL.ink; ctx.textBaseline = 'alphabetic';
    ctx.font = font(900, 360); ctx.textAlign = 'left';
    const fy = 700 + (1 - E.outExpo(prog(t, 0, 0.25))) * 300;
    ctx.save(); ctx.beginPath(); ctx.rect(0, 320, W, 420); ctx.clip();
    spacedText(ctx, String(frameNo).padStart(4, '0'), 150, fy, -10, 'left');
    ctx.restore();
    ctx.font = font(400, 30, MONO);
    const lines = ['FRAME / 900', '1920 × 1080 · 60 FPS', '0 IMAGES · 0 SAMPLES · 100% CODE'];
    lines.forEach((l, i) => {
      const a = E.outExpo(prog(t, 0.04 + i * 0.05, 0.3 + i * 0.05));
      ctx.globalAlpha = a; spacedText(ctx, l, 160 + (1 - a) * 60, 800 + i * 48, 4, 'left');
    });
    ctx.globalAlpha = 1;
    ctx.fillRect(160, 290, 1600 * E.outExpo(prog(t, 0, 0.3)), 8);
  } else {
    // 32nd-note word flashes with colour inversion (snare roll)
    const idx = Math.min(7, Math.floor(t / (BEAT / 8)));
    const inv = idx % 2 === 1;
    ctx.fillStyle = inv ? COL.cream : COL.ink; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = idx === 7 ? COL.coral : inv ? COL.ink : COL.cream;
    ctx.font = font(900, 300); ctx.textBaseline = 'middle';
    const word = FLASH_WORDS[idx];
    const sz = Math.min(300, 1700 / (word.length * 0.7));
    ctx.font = font(900, sz);
    const zoom = 1 + 0.15 * (t / BEAT);
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(zoom, zoom);
    spacedText(ctx, word, 0, 10, -6);
    ctx.restore();
  }
}

// ---------- scene 7 · end card ----------
function sOutro(ctx, lt) {
  ctx.fillStyle = COL.ink; ctx.fillRect(0, 0, W, H);
  const cx = W / 2, cy = H / 2;
  const end = E.inExpo(prog(lt, 1.35, 1.75));
  // impact shockwave
  for (let i = 0; i < 3; i++) {
    const p = E.outExpo(prog(lt, i * 0.06, 0.9 + i * 0.06));
    if (p <= 0 || p >= 1) continue;
    ctx.strokeStyle = i === 0 ? COL.coral : COL.cream; ctx.globalAlpha = 1 - p; ctx.lineWidth = 30 * (1 - p) + 1;
    ctx.beginPath(); ctx.arc(cx, cy, p * 1100, 0, TAU); ctx.stroke();
  }
  ctx.globalAlpha = 1;
  const drift = 1 + 0.025 * lt;
  ctx.save(); ctx.translate(cx, cy - 40); ctx.scale(drift, drift);
  // name: letters rise out of a mask
  ctx.font = font(900, 250); ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left';
  const name = 'CLAUDE';
  const ws = [...name].map(ch => ctx.measureText(ch).width);
  const track = lerp(60, -6, E.outExpo(prog(lt, 0, 0.9)));
  const total = ws.reduce((a, b) => a + b, 0) + track * 5;
  let x = -total / 2 - 28;
  ctx.save(); ctx.beginPath(); ctx.rect(-W, -260, W * 2, 290); ctx.clip();
  [...name].forEach((ch, i) => {
    const p = E.outExpo(prog(lt, 0.04 + i * 0.045, 0.6 + i * 0.045));
    const out = E.inExpo(prog(lt, 1.3 + (5 - i) * 0.03, 1.62 + (5 - i) * 0.03));
    ctx.fillStyle = COL.cream;
    ctx.fillText(ch, x, 20 + (1 - p) * 280 + out * 280);
    x += ws[i] + track;
  });
  ctx.restore();
  // the dot from the intro returns as the full stop
  const dotP = E.outBack(prog(lt, 0.42, 0.7));
  const dotX = total / 2 - 28 + 46, dotY = -8;
  // at the end the dot returns to centre and vanishes (bookend)
  const back = E.inOutExpo(prog(lt, 1.45, 1.75));
  const dx = lerp(dotX, 0, back), dy = lerp(dotY, 40 / drift, back);
  const dr = 26 * dotP * (1 - E.inExpo(prog(lt, 1.72, 1.86)));
  ctx.fillStyle = COL.coral; ctx.beginPath(); ctx.arc(dx, dy, Math.max(dr, 0), 0, TAU); ctx.fill();

  // subtitle revealed by a wiping bar
  const barIn = E.inOutExpo(prog(lt, 0.3, 0.6)), barOut = E.inOutExpo(prog(lt, 0.6, 0.9));
  ctx.font = font(500, 46); ctx.fillStyle = COL.cream;
  const subW = 760;
  if (barOut > 0 && end < 1) {
    ctx.save(); ctx.beginPath(); ctx.rect(-subW / 2 + barOut * subW - subW, 60, subW, 80); ctx.clip();
    ctx.globalAlpha = 1 - end;
    spacedText(ctx, 'MOTION DESIGNER', 0, 118, 18);
    ctx.restore();
  }
  if (barIn > 0 && barOut < 1) {
    ctx.fillStyle = COL.coral;
    const x0 = -subW / 2 + barOut * subW, x1 = -subW / 2 + barIn * subW;
    ctx.fillRect(x0, 70, x1 - x0, 64);
  }
  // tech line
  ctx.font = font(400, 22, MONO); ctx.fillStyle = 'rgba(242,236,225,0.6)';
  const ml = E.outExpo(prog(lt, 0.7, 1.1));
  ctx.globalAlpha = ml * (1 - end);
  spacedText(ctx, 'SHOWREEL 2026  ·  CANVAS + NUMPY  ·  0 ASSETS', 0, 210, 4);
  ctx.globalAlpha = 1;
  ctx.restore();
  // white impact flash
  const fl = 1 - prog(lt, 0, 0.07);
  if (fl > 0) { ctx.fillStyle = `rgba(255,255,255,${fl})`; ctx.fillRect(0, 0, W, H); }
}

// ---------- HUD layer (drawn after motion blur, stays crisp) ----------
const SCENE_NAMES = ['INTRO', 'KINETIC TYPE', 'SHAPE MORPH', 'PARTICLES', '3D / CUBES', 'LIQUID', 'MONTAGE', 'CLAUDE'];
function hud(ctx, t, frameNo) {
  const bar = Math.min(7, Math.floor(t / BAR));
  const a = clamp(prog(t, 0.35, 0.7)) * (1 - prog(t, 14.25, 14.6));
  if (a <= 0) return;
  ctx.save();
  ctx.globalCompositeOperation = 'difference';
  ctx.globalAlpha = a;
  ctx.strokeStyle = '#fff'; ctx.fillStyle = '#fff'; ctx.lineWidth = 2;
  const m = 56, L = 34;
  [[m, m, 1, 1], [W - m, m, -1, 1], [m, H - m, 1, -1], [W - m, H - m, -1, -1]].forEach(([x, y, sx, sy]) => {
    ctx.beginPath(); ctx.moveTo(x, y + sy * L); ctx.lineTo(x, y); ctx.lineTo(x + sx * L, y); ctx.stroke();
  });
  ctx.font = font(400, 19, MONO); ctx.textBaseline = 'middle';
  spacedText(ctx, 'CLAUDE / MOTION REEL 26', m + 52, m + 6, 2, 'left');
  spacedText(ctx, `${String(bar).padStart(2, '0')} — ${SCENE_NAMES[bar]}`, W - m - 52, m + 6, 2, 'right');
  const s = Math.floor(t), ff = frameNo % 60;
  spacedText(ctx, `TC 00:00:${String(s).padStart(2, '0')}:${String(ff).padStart(2, '0')}`, m + 52, H - m - 6, 2, 'left');
  // bar indicator
  const segW = 34, segG = 8, x0 = W - m - 52 - (segW * 8 + segG * 7);
  for (let i = 0; i < 8; i++) {
    const x = x0 + i * (segW + segG);
    ctx.globalAlpha = a * 0.35; ctx.fillRect(x, H - m - 8, segW, 4);
    const f = i < bar ? 1 : i === bar ? (t - bar * BAR) / BAR : 0;
    ctx.globalAlpha = a; ctx.fillRect(x, H - m - 8, segW * f, 4);
  }
  // tempo pulse
  const bp = beatPulse(t, 8);
  ctx.globalAlpha = a; ctx.beginPath(); ctx.arc(x0 - 26, H - m - 6, 4 + 4 * bp, 0, TAU); ctx.fill();
  ctx.restore();
}

// ---------- grain and vignette ----------
let GRAIN = null;
function initGrain() {
  GRAIN = [];
  const r = rng(99);
  for (let k = 0; k < 6; k++) {
    const c = document.createElement('canvas'); c.width = 960; c.height = 540;
    const x = c.getContext('2d'); const img = x.createImageData(960, 540);
    for (let i = 0; i < img.data.length; i += 4) { const v = r() * 255; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255; }
    x.putImageData(img, 0, 0); GRAIN.push(c);
  }
}

const SCENES = [sIntro, sType, sMorph, sParticles, sCubes, sLiquid, sMontage, sOutro];
function drawScene(ctx, t, frameNo) {
  t = clamp(t, 0, DUR - 1e-4);
  const i = Math.min(7, Math.floor(t / BAR));
  const lt = t - i * BAR;
  ctx.save();
  // camera shake on strong hits
  const shake = (i >= 1 && i <= 5 ? pulse(lt, 14) * 6 : 0) + (i === 7 ? pulse(lt, 6) * 18 : 0);
  if (shake > 0.2) ctx.translate(Math.sin(t * 91) * shake, Math.cos(t * 77) * shake);
  SCENES[i](ctx, lt, frameNo);
  ctx.restore();
}

// ---------- render with accumulation motion blur ----------
const canvas = document.getElementById('c');
const main = canvas.getContext('2d');
const buf = Object.assign(document.createElement('canvas'), { width: W, height: H });
const bctx = buf.getContext('2d');
const acc = Object.assign(document.createElement('canvas'), { width: W, height: H });
const actx = acc.getContext('2d');

window.renderFrame = function (frameNo, subframes = 6, shutter = 0.5) {
  const t = frameNo / FPS;
  for (let s = 0; s < subframes; s++) {
    const st = t + ((s + 0.5) / subframes - 0.5) * (shutter / FPS);
    bctx.setTransform(1, 0, 0, 1, 0, 0);
    drawScene(bctx, Math.max(0, st), frameNo);
    actx.globalAlpha = 1 / (s + 1);
    actx.drawImage(buf, 0, 0);
  }
  actx.globalAlpha = 1;
  main.drawImage(acc, 0, 0);
  // vignette
  const g = main.createRadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, H * 1.05);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.28)');
  main.fillStyle = g; main.fillRect(0, 0, W, H);
  // grain
  main.save(); main.globalAlpha = 0.045; main.globalCompositeOperation = 'overlay';
  main.drawImage(GRAIN[frameNo % GRAIN.length], 0, 0, W, H); main.restore();
  hud(main, t, frameNo);
  // final fade to black
  const fo = prog(t, 14.88, 15);
  if (fo > 0) { main.fillStyle = `rgba(0,0,0,${fo})`; main.fillRect(0, 0, W, H); }
};

window.ready = (async () => {
  await Promise.all([
    document.fonts.load(font(900, 100)), document.fonts.load(font(500, 100)),
    document.fonts.load(font(200, 100, DISPLAY, true)), document.fonts.load(font(400, 20, MONO)),
  ]);
  initParticles(); initGrain();
  return true;
})();
