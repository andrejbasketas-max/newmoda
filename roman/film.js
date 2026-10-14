// "A Roman Soldier Gets Transported to 2026" — the whole film as renderFrame(frame).
import * as THREE from 'three';
import { RoomEnvironment } from './RoomEnvironment.js';
import * as L from './lib.js';
import * as E from './envs.js';
const { clamp, lerp, smooth, inOut, outCubic, outBack, outElastic, seg, hash, noise1, pose, mixPose, addPose, applyPose } = L;

const W = 1080, H = 1920, TLN = window.TIMELINE, FPS = TLN.fps;
const FONT = '"Inter", "Inter Display", sans-serif';

// ---------- renderer ----------
const glc = document.createElement('canvas'); glc.width = W; glc.height = H;
const renderer = new THREE.WebGLRenderer({ canvas: glc, antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H, false); renderer.setPixelRatio(1);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;
const out = document.getElementById('c'); const ctx = out.getContext('2d');

const scene = new THREE.Scene();
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
const hemi = new THREE.HemisphereLight(0xffffff, 0x666666, 1); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffffff, 3); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.02; scene.add(sun); scene.add(sun.target);
const cam = new THREE.PerspectiveCamera(35, W / H, 0.05, 400);

// ---------- sets ----------
const SETS = {
  battle: E.buildBattlefield(scene), city: E.buildCity(scene), food: E.buildRestaurant(scene),
  plaza: E.buildPlaza(scene), museum: E.buildMuseum(scene),
};
function setEnv(name, focus = [0, 0, 0], span = 14) {
  for (const k in SETS) SETS[k].visible = k === name;
  const u = SETS[name].userData;
  scene.background = u.sky ?? new THREE.Color(u.bg);
  scene.fog = u.fog ? new THREE.Fog(u.fog[0], u.fog[1], u.fog[2]) : null;
  hemi.color.set(u.hemi[0]); hemi.groundColor.set(u.hemi[1]); hemi.intensity = u.hemi[2];
  sun.color.set(u.sunColor); sun.intensity = u.sunI;
  sun.position.set(focus[0] + u.sun[0], focus[1] + u.sun[1], focus[2] + u.sun[2]); sun.target.position.set(...focus);
  Object.assign(sun.shadow.camera, { left: -span, right: span, top: span, bottom: -span, near: 0.5, far: 80 }); sun.shadow.camera.updateProjectionMatrix();
  scene.environmentIntensity = u.env;
}

// ---------- cast ----------
const marcus = L.makeHuman({ outfit: 'roman' });
scene.add(marcus.root); marcus.root.add(marcus.shield);
L.holdIn(marcus, marcus.sword, 'R', [0, -0.07, 0.02], [Math.PI, 0, 0]);
const girl = E.crowdMember(0, { shirt: 0xf28ab2, pants: 0x37415a, hairStyle: 'bun', hair: 0x5a3420, skin: 0xf0c4a0, phone: true, bulk: 0.88, scale: 0.92, iris: 0x2f6b4f });
const worker = L.makeHuman({ shirt: 0xd23a2c, pants: 0x222831, cap: 0xd23a2c, apron: 0xf4f1ea, logo: 0xffd23a, hairStyle: 'short', skin: 0x8d5a3b, hair: 0x111111, bulk: 0.95 });
const visitor = E.crowdMember(4, { shirt: 0x2d9cdb, hairStyle: 'long', hair: 0xd8b26a, skin: 0xe8b48a, phone: true, scale: 0.93 });
const walkers = [1, 2, 3, 5, 6, 7].map((i) => E.crowdMember(i));
const riders = [8, 9].map((i) => E.crowdMember(i, { hairStyle: 'short' }));
const fans = [10, 11, 12, 13, 14].map((i) => E.crowdMember(i, { phone: true }));
const tourists = [15, 16].map((i) => E.crowdMember(i));
const humans = [girl, worker, visitor, ...walkers, ...riders, ...fans, ...tourists];
for (const h of humans) scene.add(h.root);
for (const h of [girl, visitor, ...fans]) { scene.add(h.phone); h.phone.scale.setScalar(1.45); }

const carColors = [0xd23b3b, 0x2f6fd8, 0xf2c94c, 0x2a2a2e, 0x27ae60];
const traffic = carColors.map((c) => { const k = E.makeCar(c); scene.add(k); return k; });
const robo = E.makeCar(0xf4f6f8, { autonomous: true }); scene.add(robo);
const riderScooters = riders.map((_, i) => { const s = E.makeScooter([0x2fbf71, 0xff7a2f][i]); scene.add(s); return s; });
const scooter = E.makeScooter(0x2fbf71); scene.add(scooter);
const portal = E.makePortal(); scene.add(portal);
const pigeons = Array.from({ length: 7 }, () => { const p = E.makePigeon(); scene.add(p); return p; });
const bags = Array.from({ length: 40 }, () => { const b = E.makeBag(); scene.add(b); return b; });
const handBurger = E.makeBurger(); handBurger.scale.setScalar(1.3);

const ACTORS = [marcus.root, ...humans.map((h) => h.root), girl.phone, visitor.phone, ...fans.map((f) => f.phone), ...traffic, robo, ...riderScooters, scooter, portal, ...pigeons, ...bags];
function cast(list) { for (const a of ACTORS) a.visible = false; for (const a of list) a.visible = true; }

// phone render targets (selfie screen + meme)
const rtSelfie = new THREE.WebGLRenderTarget(432, 900, { samples: 4 }); rtSelfie.texture.colorSpace = THREE.SRGBColorSpace;
const rtMeme = new THREE.WebGLRenderTarget(432, 432, { samples: 4 }); rtMeme.texture.colorSpace = THREE.SRGBColorSpace;
const phoneCam = new THREE.PerspectiveCamera(62, 432 / 900, 0.05, 200);
const memeCam = new THREE.PerspectiveCamera(32, 1, 0.05, 200);
const memeTex = L.canvasTex(432, 900, () => {});

// ---------- helpers ----------
const V = (x, y, z) => new THREE.Vector3(x, y, z);
function look(pos, target, fov = 35, roll = 0) {
  cam.fov = fov; cam.position.copy(pos); cam.up.set(Math.sin(roll), Math.cos(roll), 0); cam.lookAt(target); cam.updateProjectionMatrix();
}
const vlerp = (a, b, t) => a.clone().lerp(b, t);
function shake(t, amt) { return V(noise1(t * 23) * amt, noise1(t * 19 + 5) * amt, noise1(t * 17 + 9) * amt); }
function face(H, t, who, extra = {}) {
  const tk = L.talk(t, TLN.lines, who);
  return { mouthOpen: tk.open, eyeOpen: L.blink(t, who.length * 0.7), ...extra, _talk: tk };
}
function headWorld(H) { return H.head.localToWorld(V(0, 0.22, 0.1)); }
// shield transform blend: 0 carried at the side, 1 raised in front of the chest
function shieldPose(H, k, back = false) {
  const s = H.shield;
  H.cape.position.z = back ? -0.6 : -0.24;
  if (back) { s.position.set(0, 1.42, -0.44); s.rotation.set(0.05, Math.PI, 0); return; }
  s.position.set(lerp(0.62, 0.05, k), lerp(1.0, 1.4, k), lerp(0.05, 0.62, k));
  s.rotation.set(lerp(0, -0.08, k), lerp(Math.PI / 2 - 0.25, 0, k), lerp(0.08, 0, k));
}
function swordOut(H, on) { H.sword.visible = on; }
const ROMAN = { lShZ: 0.3, rShZ: 0.26, lEl: 0.35, rEl: 0.3, lShX: 0.15 };
// Marcus stands holding the shield at his side by default
function mpose(o = {}) { return pose({ ...ROMAN, ...o }); }
function place(H, p) { applyPose(H, p); }
// while the shield is carried at the side, the left arm stays put
function carry(p) { return { ...p, lShX: 0.15 + (p.lShX - 0.15) * 0.15, lShZ: 0.3, lEl: 0.35 + (p.lEl - 0.35) * 0.15 }; }
function walkAlong(H, t, a, b, t0, t1, base = {}, speed = 1.0) {
  const k = seg(t, t0, t1), e = k;
  const x = lerp(a[0], b[0], e), z = lerp(a[1], b[1], e);
  const ry = Math.atan2(b[0] - a[0], b[1] - a[1]);
  const moving = k > 0 && k < 1;
  const ph = (t - t0) * 7.5 * speed;
  return moving ? L.walkPose(pose({ ...base, x, z, ry }), ph, 1) : pose({ ...base, x, z, ry });
}
function phoneHold(H, phone, t, target, side = 'R') {
  const hand = H.arms[side === 'L' ? 0 : 1].hand;
  hand.updateWorldMatrix(true, false);
  const p = hand.localToWorld(V(0, -0.08, 0));
  p.add(target.clone().sub(p).normalize().multiplyScalar(0.11));
  phone.position.copy(p); phone.lookAt(target);
}

// traffic lanes: cars loop along the road
function placeTraffic(t, skip = []) {
  traffic.forEach((car, i) => {
    if (skip.includes(i)) { car.visible = false; return; }
    const dir = i % 2 ? -1 : 1, lane = dir > 0 ? 1.9 : -1.9, sp = 10 + i * 1.3;
    const x = ((i * 23.7 + t * sp) % 90) - 45;
    car.position.set(dir * x, 0, lane); car.rotation.y = dir > 0 ? Math.PI / 2 : -Math.PI / 2;
    for (const w of car.userData.wheels) w.rotation.x = t * sp / 0.36;
  });
}
function placeWalkers(t, list = walkers) {
  list.forEach((h, i) => {
    const dir = i % 2 ? -1 : 1, z = i < 3 ? 8.6 + (i % 2) * 0.6 : -7.2 - (i % 2) * 0.6, sp = 1.3 + hash(i) * 0.3;
    const x = (((i * 9.1 + t * sp) % 40) - 20) * dir;
    applyPose(h, L.walkPose(pose({ x, y: 0.18, z, ry: dir > 0 ? Math.PI / 2 : -Math.PI / 2, mouthSmile: 0.3, eyeOpen: L.blink(t, i) }), t * 7 * sp / 1.3 + i, 0.9));
  });
}

// ---------- overlay drawing ----------
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function strokeText(text, x, y, size, fill = '#fff', stroke = '#000', sw = 0.16, weight = 900) {
  ctx.font = `${weight} ${size}px ${FONT}`; ctx.lineJoin = 'round'; ctx.miterLimit = 2;
  ctx.lineWidth = size * sw; ctx.strokeStyle = stroke; ctx.strokeText(text, x, y); ctx.fillStyle = fill; ctx.fillText(text, x, y);
}
function wrap(text, size, maxW) {
  ctx.font = `900 ${size}px ${FONT}`; const words = text.split(' '); const lines = []; let cur = '';
  for (const w of words) { const tst = cur ? cur + ' ' + w : w; if (ctx.measureText(tst).width > maxW && cur) { lines.push(cur); cur = w; } else cur = tst; }
  if (cur) lines.push(cur); return lines;
}
const SPEAKER = { marcus: '#ffd23a', girl: '#ff9cc8', worker: '#ffb36b', visitor: '#8fd8ff' };
function drawSubtitles(t) {
  for (const l of TLN.lines) {
    const a = l.t0 - 0.08, b = l.t1 + 0.2; if (t < a || t > b) continue;
    const kin = outBack(seg(t, a, a + 0.22), 2.2), kout = 1 - smooth(seg(t, b - 0.15, b));
    const size = l.loud ? 76 : 66;
    const lines = wrap(l.text, size, 900);
    const y0 = 1500 - (lines.length - 1) * size * 0.6;
    ctx.save(); ctx.globalAlpha = kout; ctx.translate(W / 2, y0); ctx.scale(0.6 + 0.4 * kin, 0.6 + 0.4 * kin);
    if (l.loud) ctx.rotate(noise1(t * 30) * 0.015);
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    lines.forEach((ln, i) => strokeText(ln, 0, i * size * 1.12, size, l.who === 'marcus' ? '#ffffff' : SPEAKER[l.who], '#111', 0.2));
    ctx.restore();
  }
}
function drawTitle(t) {
  const T = TLN.title; if (t < T.t0 || t > T.t1) return;
  const k1 = outBack(seg(t, T.t0, T.t0 + 0.45), 2.5), k2 = outBack(seg(t, T.t0 + 0.25, T.t0 + 0.75), 3), ko = 1 - smooth(seg(t, T.t1 - 0.35, T.t1));
  ctx.save(); ctx.globalAlpha = ko; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.save(); ctx.translate(W / 2, 250); ctx.scale(k1, k1); ctx.rotate(-0.03 + Math.sin(t * 3) * 0.01);
  strokeText(T.lines[0], 0, 0, 92, '#ffd23a', '#2a0b0b', 0.2); ctx.restore();
  ctx.save(); ctx.translate(W / 2, 370); ctx.scale(k2, k2); ctx.rotate(0.02 + Math.sin(t * 3 + 1) * 0.012);
  ctx.font = `900 150px ${FONT}`; const gr = ctx.createLinearGradient(-260, -70, 260, 70); gr.addColorStop(0, '#59e3ff'); gr.addColorStop(1, '#c86bff');
  ctx.lineWidth = 30; ctx.strokeStyle = '#140a2a'; ctx.lineJoin = 'round'; ctx.strokeText(T.lines[1], 0, 0); ctx.fillStyle = gr; ctx.fillText(T.lines[1], 0, 0);
  ctx.restore(); ctx.restore();
}
function flash(t, at, dur = 0.35, color = '255,255,255', peak = 1) {
  const k = seg(t, at - 0.05, at), k2 = 1 - seg(t, at, at + dur); const a = Math.min(k, k2) * peak;
  if (a > 0) { ctx.fillStyle = `rgba(${color},${a})`; ctx.fillRect(0, 0, W, H); }
}
function heart(x, y, s, color) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.fillStyle = color; ctx.beginPath();
  ctx.moveTo(0, 12); ctx.bezierCurveTo(-26, -6, -14, -30, 0, -14); ctx.bezierCurveTo(14, -30, 26, -6, 0, 12); ctx.fill(); ctx.restore();
}
function fmtViews(n) { return n >= 1e6 ? (n / 1e6).toFixed(1) + 'M' : n >= 1e3 ? Math.round(n / 1e3) + 'K' : String(Math.round(n)); }
function drawSocial(t) {
  if (t < 44.9 || t > 49.95) return;
  const k = outBack(seg(t, 44.9, 45.3), 2), ko = 1 - smooth(seg(t, 49.6, 49.95));
  ctx.save(); ctx.globalAlpha = ko;
  // live pill + views
  ctx.save(); ctx.translate(70, 150); ctx.scale(k, k);
  rr(0, 0, 130, 56, 14); ctx.fillStyle = '#ff2d55'; ctx.fill(); ctx.fillStyle = '#fff'; ctx.font = `900 34px ${FONT}`; ctx.textBaseline = 'middle'; ctx.fillText('LIVE', 24, 29);
  const views = 1200 * Math.pow(10, 4 * smooth(seg(t, 45.0, 49.2)));
  rr(146, 0, 250, 56, 14); ctx.fillStyle = 'rgba(0,0,0,.55)'; ctx.fill(); ctx.fillStyle = '#fff'; ctx.fillText('👁 ' + fmtViews(views), 166, 29);
  ctx.restore();
  // trending card
  const kc = outBack(seg(t, 46.2, 46.6), 1.8);
  if (kc > 0) {
    ctx.save(); ctx.translate(W / 2, 1560); ctx.scale(kc, kc); ctx.rotate(-0.02);
    rr(-400, -70, 800, 140, 30); ctx.fillStyle = 'rgba(255,255,255,.95)'; ctx.fill();
    ctx.fillStyle = '#ff2d55'; ctx.font = `800 30px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('🔥 TRENDING #1', 0, -30);
    ctx.fillStyle = '#111'; ctx.font = `900 56px ${FONT}`; ctx.fillText('#ScooterCaesar', 0, 24); ctx.restore();
  }
  // floating hearts and likes on the right
  for (let i = 0; i < 26; i++) {
    const st = 45.0 + i * 0.17, life = 1.6; const u = (t - st) / life; if (u < 0 || u > 1) continue;
    const x = 960 + Math.sin(u * 6 + i) * 40 - u * 30, y = 1700 - u * 780;
    ctx.globalAlpha = ko * (1 - u) * smooth(u * 6);
    heart(x, y, 1.6 + hash(i) * 1.2, ['#ff2d55', '#ff6b9a', '#ffcc00', '#ff2d55'][i % 4]);
  }
  ctx.globalAlpha = ko;
  // comment toasts
  const comments = [['@julia', 'IS THIS REAL?? 😂'], ['@marco_rm', 'bro speedran 2000 years'], ['@ana.k', 'CAESAR ON A SCOOTER 💀']];
  comments.forEach(([u, c], i) => {
    const st = 45.6 + i * 1.0, ki = outCubic(seg(t, st, st + 0.3)); if (ki <= 0) return;
    ctx.save(); ctx.translate(60 - (1 - ki) * 300, 1250 + i * 92); ctx.globalAlpha = ko * ki;
    rr(0, 0, 620, 76, 38); ctx.fillStyle = 'rgba(0,0,0,.55)'; ctx.fill();
    ctx.fillStyle = '#ffd23a'; ctx.font = `800 28px ${FONT}`; ctx.textBaseline = 'middle'; ctx.textAlign = 'left'; ctx.fillText(u, 28, 38);
    ctx.fillStyle = '#fff'; ctx.font = `700 30px ${FONT}`; ctx.fillText(c, 30 + ctx.measureText(u + '  ').width + 6, 38); ctx.restore();
  });
  ctx.restore();
}
function drawTag(worldPos, text, t, t0, t1, color = '#36c9ff') {
  if (t < t0 || t > t1) return;
  const v = worldPos.clone().project(cam); const x = (v.x * 0.5 + 0.5) * W, y = clamp((-v.y * 0.5 + 0.5) * H, 260, 1200);
  const k = outBack(seg(t, t0, t0 + 0.3), 2), ko = 1 - smooth(seg(t, t1 - 0.2, t1));
  ctx.save(); ctx.translate(x, y); ctx.scale(k, k); ctx.globalAlpha = ko;
  ctx.font = `900 40px ${FONT}`; const w = ctx.measureText(text).width + 60;
  ctx.translate(clamp(x, w / 2 + 30, W - w / 2 - 30) - x, 0);
  rr(-w / 2, -40, w, 80, 18); ctx.fillStyle = 'rgba(8,20,32,.82)'; ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = color; ctx.stroke();
  ctx.fillStyle = color; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(text, 0, 2);
  ctx.beginPath(); ctx.moveTo(0, 40); ctx.lineTo(0, 110); ctx.stroke();
  ctx.restore();
}
let vignette;
function drawVignette() {
  if (!vignette) { vignette = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.72); vignette.addColorStop(0, 'rgba(0,0,0,0)'); vignette.addColorStop(1, 'rgba(0,0,0,.32)'); }
  ctx.fillStyle = vignette; ctx.fillRect(0, 0, W, H);
}

// ---------- kiosk screen ----------
function drawKiosk(qty, state, t) {
  const tex = SETS.food.userData.ktex, g = tex.userData.ctx, w = 576, h = 960;
  g.fillStyle = '#fff7ea'; g.fillRect(0, 0, w, h);
  g.fillStyle = '#d23a2c'; g.fillRect(0, 0, w, 120); g.fillStyle = '#fff'; g.font = `900 56px ${FONT}`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('BURG·RUSH', w / 2, 62);
  if (state === 'done') {
    g.fillStyle = '#27ae60'; g.beginPath(); g.arc(w / 2, 380, 120, 0, 7); g.fill();
    g.strokeStyle = '#fff'; g.lineWidth = 26; g.lineCap = 'round'; g.beginPath(); g.moveTo(w / 2 - 55, 380); g.lineTo(w / 2 - 10, 425); g.lineTo(w / 2 + 60, 335); g.stroke();
    g.fillStyle = '#111'; g.font = `900 54px ${FONT}`; g.fillText('ORDER PLACED!', w / 2, 590);
    g.fillStyle = '#d23a2c'; g.font = `900 92px ${FONT}`; g.fillText('40 × BURGER', w / 2, 700);
    g.fillStyle = '#555'; g.font = `800 48px ${FONT}`; g.fillText('TOTAL  $200.00', w / 2, 800);
  } else {
    // burger illustration
    const cx = w / 2, cy = 330, s = 1 + (state === 'tap' ? Math.max(0, Math.sin(t * 40)) * 0.04 : 0);
    g.save(); g.translate(cx, cy); g.scale(s, s);
    g.fillStyle = '#e09a3e'; g.beginPath(); g.ellipse(0, -30, 170, 100, 0, Math.PI, 0); g.fill();
    g.fillStyle = '#5fb43a'; g.fillRect(-180, -30, 360, 24); g.fillStyle = '#f7c331'; g.fillRect(-170, -8, 340, 18);
    g.fillStyle = '#5a2c16'; g.fillRect(-172, 8, 344, 52); g.fillStyle = '#e09a3e'; rrG(g, -165, 58, 330, 50, 20); g.fill();
    g.fillStyle = '#fff2cf'; for (let i = 0; i < 9; i++) { g.beginPath(); g.ellipse(-110 + i * 28, -80 - (i % 2) * 22, 6, 3, 0.4, 0, 7); g.fill(); }
    g.restore();
    g.fillStyle = '#111'; g.font = `900 58px ${FONT}`; g.fillText('CLASSIC BURGER', w / 2, 520);
    g.fillStyle = '#d23a2c'; g.font = `900 48px ${FONT}`; g.fillText('$5.00', w / 2, 585);
    // quantity selector
    g.fillStyle = '#eee3d0'; rrG(g, 60, 650, w - 120, 130, 30); g.fill();
    g.fillStyle = '#ccc'; g.beginPath(); g.arc(140, 715, 46, 0, 7); g.fill(); g.fillStyle = '#d23a2c'; g.beginPath(); g.arc(w - 140, 715, 46 * (state === 'tap' ? 1 + Math.max(0, Math.sin(t * 50)) * 0.15 : 1), 0, 7); g.fill();
    g.fillStyle = '#fff'; g.font = `900 64px ${FONT}`; g.fillText('–', 140, 712); g.fillText('+', w - 140, 712);
    g.fillStyle = qty >= 20 ? '#d23a2c' : '#111'; g.font = `900 ${qty >= 10 ? 96 : 84}px ${FONT}`; g.fillText(String(qty), w / 2, 718);
    g.fillStyle = '#d23a2c'; rrG(g, 60, 820, w - 120, 100, 50); g.fill(); g.fillStyle = '#fff'; g.font = `900 44px ${FONT}`; g.fillText(`ADD TO ORDER  $${(qty * 5).toFixed(2)}`, w / 2, 871);
  }
  tex.needsUpdate = true;
}
function rrG(g, x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }
function kioskQty(t) {
  if (t < 31.0) return 0; if (t < 32.2) return 1; if (t < 33.0) return 2;
  // accelerating taps from 2 → 40 between 33.0 and 35.3
  const u = seg(t, 33.0, 35.3); return Math.min(40, 2 + Math.floor(Math.pow(u, 0.7) * 38.99));
}

// meme screen texture composited on a canvas: photo + caption
function drawMemeScreen(t) {
  const g = memeTex.userData.ctx, w = 432, h = 900;
  g.fillStyle = '#000'; g.fillRect(0, 0, w, h);
  g.fillStyle = '#fff'; g.fillRect(0, 160, w, 600);
  g.fillStyle = '#111'; g.font = `800 26px ${FONT}`; g.textAlign = 'left'; g.textBaseline = 'middle'; g.fillText('@memes_daily · 9.8M ♥', 20, 120);
  // photo slot drawn by the material (rtMeme) on a separate plane; captions here
  g.textAlign = 'center';
  const cap = (s, y) => { g.font = `900 46px ${FONT}`; g.lineWidth = 9; g.strokeStyle = '#000'; g.lineJoin = 'round'; g.strokeText(s, w / 2, y); g.fillStyle = '#fff'; g.fillText(s, w / 2, y); };
  cap('WHEN YOU FIGHT', 210); cap('A CAR AND WIN', 262);
  g.fillStyle = '#ff2d55'; g.font = `900 40px ${FONT}`; g.fillText('♥ 2.1M   💬 88K', w / 2, 820);
  memeTex.needsUpdate = true;
}

// ================= SHOTS =================
// each returns nothing; sets cast, poses, camera. t = film time.
function shotBattle(t) {
  setEnv('battle', [0, 0, -2], 14);
  cast([marcus.root, portal]);
  const B = SETS.battle.userData;
  B.banners.forEach((f, i) => { const a = f.geometry.attributes.position, b = f.userData.base; for (let k = 0; k < a.count; k++) { const x = b[k * 3], y = b[k * 3 + 1]; const u = (x + 0.5); a.setZ(k, Math.sin(t * 4 + u * 5 + i) * 0.08 * u); } a.needsUpdate = true; f.geometry.computeVertexNormals(); });
  B.smokes.forEach((s, i) => { const k = (t * 0.1 + hash(i)) % 1; s.scale.setScalar(2 + k * 3); s.position.y = 1 + k * 6; s.material.opacity = 0.25 * (1 - k); });
  // portal opens at 0.6 in front of Marcus
  const open = outElastic(seg(t, 0.55, 1.6)) * (1 - smooth(seg(t, 3.15, 3.3)));
  portal.position.set(0, 1.45, -3.2); portal.rotation.set(0, 0, 0); E.updatePortal(portal, t, open);
  // Marcus: idle (back to camera, facing portal = -z), startled jump at 0.6, then walks into portal 1.9–3.2
  let p;
  const jump = Math.sin(Math.PI * seg(t, 0.6, 0.95)) * 0.35;
  if (t < 1.9) {
    p = L.idlePose(mpose({ x: 0, z: 1.2, ry: Math.PI, hipsY: jump, browUp: 1, eyeSize: 1 + 0.25 * seg(t, 0.6, 0.8), mouthOpen: 0.5 * Math.sin(Math.PI * seg(t, 0.6, 1.3)), lShX: 0.15 + jump, rShX: jump * 2, rEl: 0.3 + jump }), t);
    // look back at camera with a shrug 1.2–1.9
    const sh = Math.sin(Math.PI * seg(t, 1.15, 1.9));
    p = addPose(p, { headRy: -0.9 * sh, spineRy: -0.25 * sh, lShZ: 0.4 * sh, rShZ: 0.4 * sh, lEl: 0.9 * sh, rEl: 0.9 * sh, mouthSmile: -0.4 * sh, browL: 0.25 * sh, browR: 0.25 * sh });
  } else {
    const k = seg(t, 1.9, 3.15);
    p = L.walkPose(mpose({ x: 0, z: lerp(1.2, -3.2, k), ry: Math.PI, browUp: 0.6 }), (t - 1.9) * 7.5, 1);
  }
  place(marcus, carry(p)); shieldPose(marcus, 0); swordOut(marcus, false); L.updateCape(marcus, t, t > 1.9 ? 2 : 0, 0.6);
  // camera: high wide descending → behind Marcus following
  const k = inOut(seg(t, 0, 3.2));
  look(vlerp(V(3.5, 4.2, 9.5), V(0.6, 1.6, 4.0), k).add(shake(t, t > 0.55 && t < 1.0 ? 0.04 : 0.004)), vlerp(V(0, 1.2, -3), V(0, 1.3, -3.2), k), lerp(40, 46, k));
}

function shotArrive(t) {
  setEnv('city', [0, 0, 6], 12);
  cast([marcus.root, portal, ...traffic, ...walkers, ...riders.map((r) => r.root), ...riderScooters]);
  placeTraffic(t, [0, 2, 4]); placeWalkers(t);
  // portal on the sidewalk, facing the road (-z)
  const open = outBack(seg(t, 3.2, 3.45), 2) * (1 - smooth(seg(t, 4.0, 4.5)));
  portal.position.set(-1.2, 1.55, 6.9); portal.rotation.set(0, Math.PI, 0); E.updatePortal(portal, t, open);
  // scooter riders zip along the sidewalk (z=5.4) at 4.15 and 4.75
  riders.forEach((h, i) => {
    const t0 = [4.15, 4.75][i], x = lerp(14, -14, seg(t, t0 - 1.1, t0 + 1.1)), z = 5.0 + i * 0.5;
    const s = riderScooters[i]; s.position.set(x, 0.18, z); s.rotation.y = -Math.PI / 2;
    for (const w of s.userData.wheels) w.rotation.x = -t * 40;
    place(h, pose({ x, y: 0.31, z, ry: -Math.PI / 2, hipsY: -0.06, lHipX: 0.15, rHipX: -0.1, lKnee: 0.25, rKnee: 0.2, lShX: 1.0, rShX: 1.0, lEl: 0.4, rEl: 0.4, lShZ: 0.2, rShZ: 0.2, spineRx: 0.1, mouthSmile: 0.4 }));
  });
  // Marcus: stumbles out (3.3), looks around confused, jumps at horn 5.25, line at 5.6
  let p;
  const out = seg(t, 3.25, 3.9);
  const x = -1.2, z = lerp(6.6, 5.4, outCubic(out));
  const lookL = Math.sin(t * 2.6) * 0.9 * seg(t, 3.9, 4.3) * (1 - seg(t, 5.2, 5.4));
  const startle = Math.sin(Math.PI * seg(t, 5.25, 5.65));
  p = L.idlePose(mpose({ x, y: 0.18, z, ry: Math.PI, browUp: 1.1, eyeSize: 1.15, mouthSmile: -0.5, browL: 0.35, browR: 0.35 }), t);
  if (out < 1) p = L.walkPose(p, t * 9, 0.9 * (1 - out));
  p = addPose(p, { headRy: lookL, spineRy: lookL * 0.3, eyeX: lookL, hipsY: startle * 0.4, lShX: startle * 1.1, lEl: startle * 0.6, rShZ: startle * 1.2, rEl: startle * 0.8, eyeSize: startle * 0.35, mouthOpen: startle * 0.8 });
  // head scratch during line
  const scr = smooth(seg(t, 5.7, 6.0)) * (1 - smooth(seg(t, 7.4, 7.8)));
  p = addPose(p, { rShX: 1.2 * scr, rShZ: 0.6 * scr, rEl: 2.0 * scr, headRz: 0.18 * scr, headRx: -0.12 * scr, ...faceTalk(t) });
  place(marcus, p); shieldPose(marcus, startle * 0.7); swordOut(marcus, false); L.updateCape(marcus, t, out < 1 ? 2.5 : 0.3, 0.4);
  // camera A (3.2–4.6) low front; camera B (4.6–8) wide 3/4 with road behind
  if (t < 4.6) { const k = inOut(seg(t, 3.2, 4.6)); look(vlerp(V(1.4, 1.3, 1.6), V(0.8, 1.45, 2.1), k), V(-1.2, 1.5, 6.0), 52); }
  else { const k = inOut(seg(t, 4.6, 8)); look(vlerp(V(0.5, 1.8, 1.9), V(-0.3, 1.9, 2.4), k).add(shake(t, t > 5.25 && t < 5.6 ? 0.03 : 0)), V(-1.2, 1.9, 5.4), lerp(50, 44, k)); }
}
function faceTalk(t, who = 'marcus') { const tk = L.talk(t, TLN.lines, who); return { mouthOpen: tk.open + (tk.loud ? tk.open * 0.3 : 0) }; }

// ---- scene 2: selfie ----
function shotSelfie(t) {
  setEnv('city', [0, 0, 6], 10);
  cast([marcus.root, girl.root, girl.phone, ...traffic, ...walkers]);
  placeTraffic(t); placeWalkers(t, walkers.slice(3));
  // girl at (0.9, 6.6) facing +z (toward camera), phone in right hand raised toward her face
  const raise = smooth(seg(t, 8.0, 8.8)) * (1 - smooth(seg(t, 17.0, 17.4)));
  const lean = smooth(seg(t, 13.0, 13.4)) * (1 - smooth(seg(t, 15.0, 15.4)));
  const leaves = seg(t, 17.2, 18.0);
  let gp = pose({ x: 1.25, y: 0.18, z: 6.6, ry: 0.15, rShX: 1.35 * raise, rShZ: 0.25 + 0.3 * raise, rEl: 0.5 * raise + 0.15, lShZ: 0.1, mouthSmile: 0.6, headRz: 0.12 * raise, headRy: -0.15 * raise, eyeOpen: L.blink(t, 1) });
  gp = addPose(gp, { spineRx: -0.25 * lean, spineRy: 0.2 * lean, headRx: -0.15 * lean, browL: -0.2 * lean, browR: -0.2 * lean, mouthSmile: -0.8 * lean });
  // deadpan line 15.5–17.2
  const dead = smooth(seg(t, 15.3, 15.5)) * (1 - smooth(seg(t, 17.2, 17.4)));
  gp = addPose(gp, { eyeOpen: -0.45 * dead, mouthSmile: -0.6 * dead, browL: -0.1 * dead, ...faceTalk(t, 'girl'), headRy: -0.5 * dead });
  if (leaves > 0) gp = L.walkPose(pose({ x: lerp(1.25, -2.8, leaves), y: 0.18, z: 6.6, ry: -Math.PI / 2, mouthSmile: -0.3 }), t * 7.5, 1);
  place(girl, gp);
  // Marcus behind her left shoulder, leans in at 9.3, steps back and draws sword 12.4, lunges 13.3/13.75/14.2
  const peek = smooth(seg(t, 8.9, 9.5));
  const back = smooth(seg(t, 12.3, 12.7)) * (1 - smooth(seg(t, 16.8, 17.6)));
  const close = smooth(seg(t, 10.0, 10.5)) * (1 - smooth(seg(t, 12.2, 12.5)));
  let p = L.idlePose(mpose({ x: lerp(-0.2, 0.55, peek) + back * -1.0 + close * 0.25, y: 0.18, z: lerp(5.6, 6.0, peek) + back * -0.2 + close * 0.35, ry: lerp(0.3, 0.15, peek), spineRx: 0.22 * peek * (1 - back), spineRy: -0.2 * peek, headRx: 0.15 * peek, eyeSize: 1 + 0.3 * smooth(seg(t, 9.9, 10.2)) * (1 - back), browUp: 0.8 * peek, mouthOpen: 0.3 * peek * (1 - smooth(seg(t, 10.2, 10.3))) }), t);
  // sword pointing at the phone
  const lunge = [13.3, 13.75, 14.2].reduce((s, a) => s + Math.sin(Math.PI * seg(t, a - 0.1, a + 0.22)), 0);
  p = addPose(p, { rShX: 1.45 * back, rShZ: -0.1 * back, rEl: 0.15 * back, spineRy: 0.35 * back, ry: 0.5 * back, lShZ: 0.3 * back, browL: -0.45 * back, browR: -0.45 * back, browUp: -0.8 * back * (1 - dead), hipsY: -0.08 * back, lHipX: 0.3 * back, rHipX: -0.25 * back, lKnee: 0.3 * back, rKnee: 0.2 * back, spineRx: 0.18 * lunge, x: 0.2 * lunge * back, z: 0.15 * lunge * back });
  p = addPose(p, { ...faceTalk(t), browUp: 0.9 * dead, eyeSize: 0.1 * dead, mouthSmile: -0.4 * dead });
  place(marcus, carry(p)); shieldPose(marcus, 0); swordOut(marcus, back > 0.4 || (t > 12.55 && t < 17.0)); L.updateCape(marcus, t, lunge * 2, 0.3);
  // phone: screen faces her face; front camera shows the selfie (mirrored)
  const gHead = headWorld(girl);
  phoneHold(girl, girl.phone, t, gHead);
  girl.phone.updateWorldMatrix(true, false);
  phoneCam.position.copy(girl.phone.localToWorld(V(0, 0.05, 0.02)));
  phoneCam.lookAt(vlerp(gHead, headWorld(marcus), 0.45 + 0.4 * close));
  girl.phoneScreen.material = selfieMat;
  renderPhone = true;
  // cameras
  if (t < 10.0) { const k = inOut(seg(t, 8, 10)); look(vlerp(V(0.6, 1.7, 10.4), V(0.5, 1.75, 9.4), k), V(0.4, 1.55, 6.0), 36); }
  else if (t < 12.4) { // over-the-shoulder on the phone screen
    const ph = girl.phone.position; const k = seg(t, 10.0, 12.4);
    const right = V(-Math.cos(0.15), 0, Math.sin(0.15)), fwd = V(Math.sin(0.15), 0, Math.cos(0.15));
    look(gHead.clone().add(right.multiplyScalar(0.36)).add(V(0, 0.1, 0)).add(fwd.multiplyScalar(-0.12)).lerp(ph, 0.2 + 0.12 * k), ph, 36);
  } else if (t < 15.35) { const k = inOut(seg(t, 12.4, 15.35)); look(vlerp(V(2.6, 1.5, 9.6), V(2.0, 1.45, 9.0), k).add(shake(t, lunge * 0.01)), V(0.3, 1.45, 6.2), 38); }
  else { const k = inOut(seg(t, 15.35, 18)); look(vlerp(V(1.3, 1.62, 8.6), V(1.0, 1.62, 8.3), k), vlerp(V(0.9, 1.6, 6.6), V(0.2, 1.55, 6.3), seg(t, 16.8, 18)), 30); }
}
const selfieMat = new THREE.MeshBasicMaterial({ map: rtSelfie.texture }); rtSelfie.texture.repeat.x = -1; rtSelfie.texture.offset.x = 1;
let renderPhone = false;

// ---- scene 3: self-driving car ----
function roboX(t) {
  // drives +x along lane z=1.9; brakes to stop at x=1.8 by 21.9; then pulls around after 26.6
  const stopX = 1.8, v = 7.5;
  if (t < 21.3) return stopX - v * (21.3 - t) - v * 0.3;
  if (t < 21.9) { const u = seg(t, 21.3, 21.9); return stopX - v * 0.3 * (1 - u) * (1 - u); }
  if (t < 26.6) return stopX;
  const u = t - 26.6; return stopX + 1.2 * u * u + 0.6 * u;
}
function shotRobo(t) {
  setEnv('city', [5, 0, 1], 14);
  cast([marcus.root, robo, ...walkers]);
  placeTraffic(t, [0, 1, 2, 3, 4]); placeWalkers(t);
  const x = roboX(t), dx = (roboX(t + 0.02) - x) / 0.02;
  const pull = smooth(seg(t, 26.6, 28));
  robo.position.set(x, 0, 1.9 - 3.4 * smooth(seg(t, 26.7, 27.8))); robo.rotation.y = Math.PI / 2 - 0.35 * Math.sin(Math.PI * seg(t, 26.7, 27.8));
  for (const w of robo.userData.wheels) w.rotation.x = x / 0.36;
  robo.userData.spin.rotation.y = t * 9;
  const stopped = t > 21.4 && t < 26.6;
  robo.userData.tailM.emissiveIntensity = stopped ? 2.5 : 0.3;
  robo.userData.led.emissive.set(t > 21.5 && t < 24.4 ? 0xff3b30 : 0x36c9ff);
  robo.userData.body.rotation.z = 0; robo.userData.body.rotation.x = 0;
  robo.userData.body.position.y = 0;
  // nose dip when braking
  const dip = Math.sin(Math.PI * seg(t, 21.4, 22.1)) * 0.05; robo.userData.body.rotation.x = dip;
  // Marcus on crosswalk at (6, 1.9) — distracted, notices (18.6), raises shield (19.5), shouts, peeks, celebrates
  const notice = smooth(seg(t, 18.6, 19.0)), raise = smooth(seg(t, 19.35, 19.6)) * (1 - smooth(seg(t, 24.3, 24.6)));
  const peek = Math.sin(Math.PI * seg(t, 22.7, 24.3));
  const party = seg(t, 24.5, 28);
  let p = L.idlePose(mpose({ x: 6.0, y: 0, z: 1.9, ry: lerp(0.3, -Math.PI / 2, notice), headRx: -0.25 * (1 - notice), headRy: 0.5 * (1 - notice), eyeY: 1 - notice }), t);
  p = addPose(p, { lShX: 1.25 * raise, lShZ: -0.1 * raise, lEl: 0.9 * raise, spineRx: 0.12 * raise, hipsY: -0.1 * raise, lHipX: 0.35 * raise, lKnee: 0.35 * raise, rHipX: -0.3 * raise, rKnee: 0.15 * raise, browL: -0.5 * raise, browR: -0.5 * raise, eyeSize: 0.15 * raise, rShX: 0.4 * raise, rEl: 1.0 * raise });
  p = addPose(p, { spineRz: 0.25 * peek, headRz: 0.2 * peek, x: -0.0, browUp: 1.2 * peek, eyeX: 0.8 * peek, eyeSize: 0.2 * peek });
  if (party > 0) {
    const j = Math.abs(Math.sin(party * Math.PI * 4.2)) * (1 - seg(t, 27.2, 27.8));
    p = mpose({ x: 6.0, y: 0, z: 1.9, ry: lerp(-Math.PI / 2, 0.2, smooth(seg(t, 24.5, 24.9))), hipsY: j * 0.38, rShX: 2.9, rShZ: 0.3, rEl: 0.1, lShZ: 0.3, lEl: 0.35, lHipX: j * 0.5, rHipX: j * 0.2, lKnee: j * 1.1, rKnee: j * 0.7, headRx: -0.2, mouthSmile: 1, browUp: 0.8, spineRx: -0.15 });
  }
  p = addPose(p, faceTalk(t));
  place(marcus, p); shieldPose(marcus, raise); swordOut(marcus, party > 0); L.updateCape(marcus, t, party > 0 ? 3 * Math.abs(Math.sin(party * 13)) : 0.2, 0.5, party > 0 ? 0.5 : 0);
  // cameras
  if (t < 19.6) { const k = inOut(seg(t, 18, 19.6)); look(vlerp(V(13.5, 3.2, 9.0), V(12.5, 2.6, 8.0), k), vlerp(V(2, 0.9, 1.8), V(4, 1.0, 1.8), k), 40); }
  else if (t < 21.95) { const cx = Math.max(roboX(t), -8) - 4.4; look(V(cx, 1.5, 4.4).add(shake(t, 0.006 + 0.02 * Math.sin(Math.PI * seg(t, 19.7, 21.4)))), V(6.0, 1.55, 1.9), 30); }
  else if (t < 24.5) { const k = inOut(seg(t, 21.95, 24.5)); look(vlerp(V(8.6, 1.35, -1.2), V(8.3, 1.4, -0.9), k), V(5.0, 1.3, 1.9), 44); }
  else { const k = inOut(seg(t, 24.5, 28)); const a = lerp(0.35, -0.25, k); look(V(6.0 + Math.sin(a) * 5.4, lerp(0.9, 1.5, k), 1.9 + Math.cos(a) * 5.4), V(6.0, 1.45, 1.9), 40); }
}

// ---- scene 4: fast food ----
function bagSlot(i) { const col = i % 10, row = Math.floor(i / 10) % 2, lay = Math.floor(i / 20); return V(-2.6 + col * 0.58, 1.13 + lay * 0.37, -2.45 + row * 0.38); }
function shotFood(t) {
  setEnv('food', [0, 0, 0], 9);
  cast([marcus.root, worker.root, ...bags]);
  const ks = SETS.food.userData.kiosk; ks.visible = true;
  // kiosk screen state
  const qty = kioskQty(t); drawKiosk(qty, t > 35.4 ? 'done' : t > 32.9 ? 'tap' : 'idle', t);
  // bags appear 36.0–38.4
  bags.forEach((b, i) => {
    const st = 36.0 + i * 0.06; const k = outBack(seg(t, st, st + 0.18), 3);
    b.visible = k > 0.01; b.scale.setScalar(Math.max(0.001, k)); const s = bagSlot(i); b.position.set(s.x, s.y + (1 - smooth(seg(t, st, st + 0.12))) * 0.5, s.z); b.rotation.y = (hash(i) - 0.5) * 0.4;
  });
  // worker behind counter
  const slide = Math.sin(t * 9);
  place(worker, L.idlePose(pose({ x: -2.3, z: -3.2, ry: 0.15, mouthSmile: 0.6, ...faceTalk(t, 'worker'), eyeOpen: L.blink(t, 2), lShX: t > 36 && t < 38.4 ? 1.0 + slide * 0.3 : 0.1, rShX: t > 36 && t < 38.4 ? 1.0 - slide * 0.3 : 0.1, lEl: 0.6, rEl: 0.6, headRy: t > 37.2 ? 0.5 : 0 }), t));
  // Marcus: enters 28–30 (door → kiosk), stands at kiosk 30–35.5, walks to counter 35.8–37.0, amazed 37–40
  const kioskStand = V(3.45, 0, 1.42), kioskRy = Math.PI - 0.5;
  let p;
  if (t < 30.0) {
    p = walkAlong(marcus, t, [5.2, 6.4], [kioskStand.x, kioskStand.z], 28.0, 29.9, { ...ROMAN, browUp: 0.6, mouthSmile: 0.6, headRx: -0.25 * Math.sin(Math.PI * seg(t, 28.4, 29.4)), eyeOpen: 1 - 0.7 * Math.sin(Math.PI * seg(t, 28.4, 29.4)) });
    p.ry = lerp(p.ry, kioskRy, smooth(seg(t, 29.5, 30.0)));
  } else if (t < 35.8) {
    const poke = t > 30.8 && t < 31.2 ? Math.sin(Math.PI * seg(t, 30.8, 31.2)) : t > 32.0 && t < 32.4 ? Math.sin(Math.PI * seg(t, 32.0, 32.4)) : 0;
    const frenzy = t > 32.9 && t < 35.35 ? Math.abs(Math.sin((t - 32.9) * (14 + (t - 32.9) * 9))) : 0;
    const squint = smooth(seg(t, 30.0, 30.3)) * (1 - smooth(seg(t, 32.8, 33.0)));
    p = L.idlePose(mpose({ x: kioskStand.x, z: kioskStand.z, ry: kioskRy, spineRx: 0.12 + 0.08 * squint, headRx: 0.1, eyeOpen: 1 - 0.45 * squint, browL: -0.3 * squint, browR: 0.25 * squint, rShX: 0.9 * Math.max(poke, frenzy > 0 ? 0.7 + frenzy * 0.3 : 0) + 0.1, rEl: 1.2 - Math.max(poke, frenzy) * 0.9, mouthSmile: frenzy > 0 ? 1 : 0, eyeSize: 1 + (frenzy > 0 ? 0.2 : 0), browUp: frenzy > 0 ? 1 : 0 }), t);
    p = addPose(p, faceTalk(t));
    if (t > 35.4) p = addPose(p, { headRx: -0.15, mouthOpen: 0.4, eyeSize: 0.2, browUp: 1 });
  } else {
    p = walkAlong(marcus, t, [kioskStand.x, kioskStand.z], [0.2, -1.0], 35.8, 36.9, { ...ROMAN });
    if (t >= 36.9) {
      const amaze = smooth(seg(t, 36.9, 37.4)), arms = smooth(seg(t, 38.1, 38.5));
      p = L.idlePose(mpose({ x: 0.2, z: -1.0, ry: Math.PI + 0.25, eyeSize: 1 + 0.35 * amaze, browUp: 1.2 * amaze, mouthOpen: 0.9 * amaze * (1 - arms), mouthSmile: arms, headRx: -0.15 * amaze, lShZ: 0.3 + 1.6 * arms, rShZ: 0.26 + 1.6 * arms, lEl: 0.5, rEl: 0.5, spineRx: -0.2 * arms }), t);
      p = addPose(p, faceTalk(t));
    }
  }
  place(marcus, p); shieldPose(marcus, 0, true); swordOut(marcus, false); L.updateCape(marcus, t, 0.5, 0.15);
  // cameras
  if (t < 30.0) { const k = inOut(seg(t, 28, 30)); look(vlerp(V(-1.6, 1.8, 2.4), V(-0.6, 1.7, 2.2), k), vlerp(V(4.8, 1.3, 5.0), V(3.6, 1.5, 1.6), k), 40); }
  else if (t < 32.9) { // kiosk POV looking at Marcus
    ks.updateWorldMatrix(true, false); const sp = ks.localToWorld(V(0.05, 1.62, -0.75)); const k = seg(t, 30, 32.9);
    ks.visible = false; look(sp, headWorld(marcus).add(V(0, -0.22, 0)), lerp(46, 38, k));
  } else if (t < 35.8) { // over-shoulder on the screen
    ks.updateWorldMatrix(true, false); const sc = ks.localToWorld(V(0, 1.6, 0.12)); const k = seg(t, 32.9, 35.8);
    look(ks.localToWorld(V(0.95, 2.35, 1.6 - 0.2 * k)).add(shake(t, t < 35.35 ? 0.006 : 0)), sc, 30);
  } else if (t < 38.0) { const k = inOut(seg(t, 35.8, 38)); look(vlerp(V(-0.2, 2.6, -4.55), V(0.0, 2.55, -4.4), k), V(0.4, 1.35, -1.3), 46); }
  else { const k = outCubic(seg(t, 38, 40)); look(vlerp(V(0.1, 2.55, -4.4), V(0.35, 2.45, -3.6), k), headWorld(marcus).add(V(0, -0.2, 0)), lerp(42, 34, k)); }
}

// ---- scene 5: scooter ----
const PATH = new THREE.CatmullRomCurve3([V(-6, 0, 6), V(-3, 0, 6.6), V(0.5, 0, 5.0), V(3.6, 0, 6.6), V(7.2, 0, 4.2), V(6.6, 0, 0.2), V(3.6, 0, -2.0), V(0.8, 0, -2.4)]);
function rideU(t) { // 0..1 along path between 42.25 and 47.9
  const u = seg(t, 42.25, 47.9); return 0.04 * smooth(seg(t, 42.25, 42.7)) * 0 + lerp(0, 1, u * u * (1.6 - 0.6 * u) * 0.92 + u * 0.08);
}
function scooterState(t) {
  if (t < 42.25) return { p: V(-6, 0, 6), yaw: Math.PI / 2 - 0.1, roll: 0, speed: 0 };
  const u = clamp(rideU(t)), p = PATH.getPointAt(u), tan = PATH.getTangentAt(u);
  const yaw = Math.atan2(tan.x, tan.z);
  const u2 = clamp(rideU(t + 0.05)); const speed = PATH.getPointAt(u2).distanceTo(p) / 0.05;
  let roll = Math.sin(t * 7.3) * 0.12 + noise1(t * 3) * 0.1;
  let spin = 0;
  if (t > 47.6) spin = Math.PI * 2 * outCubic(seg(t, 47.6, 48.3));
  return { p, yaw: yaw + spin, roll: roll * (1 - seg(t, 47.6, 48.2)), speed: t > 47.9 ? speed * (1 - seg(t, 47.9, 48.3)) : speed };
}
const FANS = [[-2.5, 3.2, 0.7], [2.2, 2.6, 0.2], [5.2, 8.6, 3.4], [9.2, 1.0, -1.6], [-1.6, 0.4, 2.6]];
function shotScooter(t) {
  setEnv('plaza', [1, 0, 2], 14);
  cast([marcus.root, scooter, ...fans.map((f) => f.root), ...fans.map((f) => f.phone), ...pigeons, ...tourists.map((h) => h.root)]);
  E.updateFountain(SETS.plaza, t);
  const S = scooterState(t);
  scooter.position.copy(S.p); scooter.rotation.set(0, S.yaw, 0); scooter.rotateZ(-S.roll);
  for (const w of scooter.userData.wheels) w.rotation.x = t > 42.25 ? (t - 42.25) * S.speed * 9 : 0;
  // Marcus
  let p;
  const riding = t >= 42.15;
  if (!riding) {
    const walk = walkAlong(marcus, t, [-9.0, 7.8], [-6.6, 6.7], 40.0, 41.0, { ...ROMAN, browUp: 0.8, mouthSmile: 0.7 });
    p = t < 41.0 ? walk : L.idlePose(mpose({ x: -6.6, z: 6.7, ry: Math.PI / 2 + 0.4, spineRx: 0.45 * smooth(seg(t, 41.0, 41.4)), headRx: 0.2, eyeSize: 1.2, browUp: 1, mouthSmile: 0.8, rShX: 0.8 * smooth(seg(t, 41.2, 41.6)), rEl: 0.4 }), t);
    p = addPose(p, faceTalk(t));
  } else {
    const panic = smooth(seg(t, 42.25, 42.5)) * (1 - smooth(seg(t, 48.2, 48.6)));
    const pride = smooth(seg(t, 48.3, 48.8));
    const wob = Math.sin(t * 11) * panic;
    p = mpose({
      x: S.p.x, y: 0.2, z: S.p.z, ry: S.yaw, hipsRz: S.roll * 0.6, spineRx: -0.35 * panic + 0.1, spineRz: S.roll * 0.8 + wob * 0.06,
      lShX: 1.25, rShX: 1.25, lShZ: 0.15, rShZ: 0.15, lEl: 0.25 + 0.3 * panic, rEl: 0.25 + 0.3 * panic,
      lHipX: 0.25, rHipX: -0.15, lKnee: 0.35, rKnee: 0.25, hipsY: -0.05,
      eyeSize: 1 + 0.45 * panic, browUp: 1.3 * panic, mouthOpen: 0.25 * panic, headRx: -0.15 * panic + wob * 0.05, headRy: wob * 0.15,
    });
    if (pride > 0) p = addPose(p, { rShX: 1.6 * pride, rShZ: 0.3 * pride, rEl: -0.2 * pride, mouthSmile: 1.0 * pride, eyeSize: -0.3 * pride, spineRx: -0.15 * pride, headRx: -0.15 * pride, browL: 0.15 * pride, browR: -0.2 * pride });
    p = addPose(p, faceTalk(t));
  }
  place(marcus, p); shieldPose(marcus, 0, true); swordOut(marcus, false);
  L.updateCape(marcus, t, riding ? S.speed * 1.4 : 0.3, 0.4, riding ? clamp(S.speed / 6) * 0.6 : 0);
  // fans filming with phones raised, heads follow Marcus
  fans.forEach((f, i) => {
    const [x, z, ry] = FANS[i]; const active = smooth(seg(t, 43.0 + i * 0.4, 43.5 + i * 0.4));
    const toM = Math.atan2(S.p.x - x, S.p.z - z);
    let dy = toM - ry; while (dy > Math.PI) dy -= 2 * Math.PI; while (dy < -Math.PI) dy += 2 * Math.PI;
    place(f, L.idlePose(pose({ x, z, ry: ry + clamp(dy, -1.2, 1.2) * 0.6 * active, headRy: clamp(dy, -1.2, 1.2) * 0.4 * active, rShX: 1.5 * active + 0.1, rShZ: 0.1, rEl: 0.6 * active + 0.15, mouthOpen: 0.4 * active * (t > 48.3 ? 1 : 0.5), mouthSmile: 0.8, eyeSize: 1 + 0.2 * active, browUp: 0.6 * active, eyeOpen: L.blink(t, i), lShZ: t > 48.3 ? 1.0 * Math.abs(Math.sin(t * 9 + i)) : 0.1 }), t));
    phoneHold(f, f.phone, t, S.p.clone().add(V(0, 1.4, 0)));
  });
  tourists.forEach((h, i) => place(h, L.walkPose(pose({ x: lerp(-12, 12, ((t * 0.07 + i * 0.5) % 1)) * (i ? -1 : 1), z: -0.5 - i * 1.4, ry: i ? -Math.PI / 2 : Math.PI / 2, mouthSmile: 0.3 }), t * 7 + i, 0.9)));
  // pigeons near (2.6, 5.2) scatter when he passes (~44.7)
  pigeons.forEach((g, i) => {
    const bx = 1.6 + (i % 4) * 0.5 + hash(i) * 0.3, bz = 4.6 + Math.floor(i / 4) * 0.6 + hash(i * 3) * 0.3;
    const fly = Math.max(0, t - 44.65 - hash(i) * 0.15);
    g.position.set(bx + fly * (hash(i * 5) - 0.5) * 3, fly * fly * 2.2 + fly * 1.5, bz - fly * (1 + hash(i * 7)) * 1.5);
    g.rotation.y = fly > 0 ? Math.PI + (hash(i) - 0.5) : hash(i * 9) * 6;
    const flap = fly > 0 ? Math.sin(t * 40 + i) * 0.9 : 0;
    g.userData.wings[0].rotation.z = flap; g.userData.wings[1].rotation.z = -flap;
    g.userData.head.position.y = 0.19 + (fly > 0 ? 0 : Math.max(0, Math.sin(t * 6 + i * 2)) * -0.04);
  });
  // cameras
  const m = S.p.clone();
  if (t < 42.25) { const k = inOut(seg(t, 40, 42.25)); look(vlerp(V(-3.4, 1.7, 12.2), V(-4.0, 1.5, 11.2), k), vlerp(V(-7.4, 1.1, 7.0), V(-6.4, 1.0, 6.5), k), 52); }
  else if (t < 45.0) {
    const k = seg(t, 42.25, 45); const fw = V(Math.sin(S.yaw), 0, Math.cos(S.yaw)), side = V(Math.cos(S.yaw), 0, -Math.sin(S.yaw));
    look(m.clone().add(side.multiplyScalar(-2.6)).add(fw.multiplyScalar(2.4)).add(V(0, 1.35, 0)).add(shake(t, 0.03)), m.clone().add(V(0, 1.35, 0)), 48);
  } else if (t < 47.85) {
    const ahead = clamp(rideU(t) + 0.12); const a = PATH.getPointAt(ahead);
    look(a.clone().add(V(0, 1.5, 0)).add(shake(t, 0.025)), m.clone().add(V(0, 1.6, 0)), 46);
  } else { const k = inOut(seg(t, 47.85, 50)); const c = V(0.8, 0, -2.4); look(vlerp(c.clone().add(V(-1.2, 1.0, 4.6)), c.clone().add(V(-0.6, 1.2, 3.6)), k).add(shake(t, t < 48.3 ? 0.04 : 0)), c.clone().add(V(0, 1.2, 0)), 42); }
}

// ---- scene 6: museum ----
const statuePose = pose({ rShX: 2.4, rShZ: 0.25, rEl: 0.1, lShX: 0.35, lEl: 0.9, lShZ: 0.2, rHipX: -0.12, lHipX: 0.1, lKnee: 0.25, headRy: 0.2, headRx: -0.08, spineRy: 0.1, eyeOpen: 1, mouthSmile: 0.05 });
function renderMeme() {
  // photo of Marcus mid-"WHOA" on the scooter, rendered from the plaza set
  const saved = { ...marcus.pose };
  setEnv('plaza', [0, 0, 4], 6);
  const vis = ACTORS.map((a) => a.visible); cast([marcus.root, scooter]);
  scooter.position.set(0, 0, 4); scooter.rotation.set(0, 0.6, 0);
  place(marcus, mpose({ x: 0, y: 0.2, z: 4, ry: 0.6, spineRx: -0.35, lShX: 1.25, rShX: 1.25, lEl: 0.5, rEl: 0.5, lHipX: 0.25, lKnee: 0.35, rKnee: 0.25, hipsY: -0.05, eyeSize: 1.5, browUp: 1.4, mouthOpen: 1.1, headRx: -0.12 }));
  L.updateCape(marcus, 45, 6, 0.4, 0.6); marcus.sword.visible = false; shieldPose(marcus, 0, true);
  memeCam.position.set(1.0, 2.15, 6.2); memeCam.lookAt(0.1, 1.95, 4.0); memeCam.updateProjectionMatrix();
  renderer.setRenderTarget(rtMeme); renderer.render(scene, memeCam); renderer.setRenderTarget(null);
  ACTORS.forEach((a, i) => (a.visible = vis[i]));
}
const memePhotoMat = new THREE.MeshBasicMaterial({ map: rtMeme.texture });
const memeFrameMat = new THREE.MeshBasicMaterial({ map: memeTex });
const memePhoto = new THREE.Mesh(new THREE.PlaneGeometry(0.076 * 0.92, 0.076 * 0.92), memePhotoMat);
visitor.phone.add(memePhoto); memePhoto.position.set(0, -0.016, 0.0075); memePhoto.scale.setScalar(0.07 / (0.076 * 0.92));
function shotMuseum(t) {
  setEnv('museum', [0, 0, -2], 9);
  cast([marcus.root, visitor.root, visitor.phone, ...tourists.map((h) => h.root)]);
  const st = SETS.museum.userData.statue; applyPose(st, { ...statuePose, y: 0, x: 0, z: 0, ry: 0 });
  tourists.forEach((h, i) => place(h, L.idlePose(pose({ x: [-5.5, 5.8][i], z: [-5.6, -5.4][i], ry: [Math.PI - 0.3, Math.PI + 0.4][i], headRx: -0.2, mouthSmile: 0.2, eyeOpen: L.blink(t, i + 3) }), t + i)));
  // visitor with phone at (-1.3,-1.4) facing +z; laughs at 54; shows phone to Marcus 54.6
  const laugh = Math.sin(Math.PI * seg(t, 54.0, 55.6)), show = smooth(seg(t, 54.7, 55.2)) * (1 - smooth(seg(t, 59.0, 59.6)));
  const stepBack = smooth(seg(t, 57.0, 57.8));
  let vp = L.idlePose(pose({ x: -0.15 - 0.9 * stepBack, z: -1.05 + 0.4 * stepBack, ry: 0.5 + 0.9 * show, rShX: 1.0 + 0.35 * show, rEl: 1.1 - 0.7 * show, rShZ: 0.1, headRx: 0.35 * (1 - show) - 0.05, mouthSmile: 0.7, eyeOpen: L.blink(t, 4) - 0.4 * laugh, spineRx: 0.12 * laugh * Math.abs(Math.sin(t * 18)), hipsY: -0.02 * laugh, lShZ: 0.2 + 0.4 * laugh, lEl: 1.2 * laugh }), t);
  vp = addPose(vp, faceTalk(t, 'visitor'));
  place(visitor, vp);
  visitor.updateWorld = true;
  // Marcus walks in 50–51.4, looks up (choir), points 51.6–54, turns to visitor 54.8, gasps 56.0, heroic statue pose 57
  let p;
  if (t < 51.4) p = walkAlong(marcus, t, [4.6, 2.6], [1.2, -1.3], 50.0, 51.4, { ...ROMAN, browUp: 0.5 });
  else {
    const up = smooth(seg(t, 51.3, 51.7)), point = smooth(seg(t, 51.7, 52.0)) * (1 - smooth(seg(t, 54.6, 54.9)));
    const turn = smooth(seg(t, 54.7, 55.1)) * (1 - smooth(seg(t, 56.75, 57.0)));
    const gasp = smooth(seg(t, 56.0, 56.2)) * (1 - smooth(seg(t, 56.75, 56.9)));
    const hero = smooth(seg(t, 56.8, 57.1));
    p = L.idlePose(mpose({ x: 1.2, z: -1.3, ry: Math.PI + 0.35 - 1.6 * turn + -0.2 * hero, headRx: -0.35 * up * (1 - turn) + 0.2 * turn, eyeY: up * (1 - turn), browUp: 0.8 * up, mouthSmile: 0.9 * point, eyeSize: 1 + 0.15 * up }), t);
    p = addPose(p, { rShX: 2.2 * point, rShZ: -0.1 * point, rEl: -0.15 * point, spineRx: -0.15 * point, headRy: -0.2 * point });
    p = addPose(p, { spineRx: 0.25 * turn * (1 - gasp), headRx: 0.2 * turn, eyeY: -1 * turn });
    p = addPose(p, { eyeSize: 0.75 * gasp, browUp: 1.5 * gasp, mouthOpen: 1.0 * gasp, lShX: 0.9 * gasp, rShX: 0.9 * gasp, lEl: 2.3 * gasp, rEl: 2.3 * gasp, lShZ: -0.05 * gasp, rShZ: -0.05 * gasp, spineRx: -0.2 * gasp, hipsY: 0.05 * gasp });
    if (hero > 0) p = mixPose(p, mpose({ ...statuePose, x: 1.2, z: -1.3, ry: Math.PI - 0.25 + Math.PI, lShX: 0.35, lShZ: 0.6, rShX: 2.5, spineRx: -0.12, headRx: -0.25, mouthSmile: 0.9, browUp: 0.6, eyeSize: 1.1, hipsY: 0, lEl: 0.4 }), hero);
    p = addPose(p, faceTalk(t));
  }
  place(marcus, p); shieldPose(marcus, 0, true); swordOut(marcus, t > 57.0); L.updateCape(marcus, t, t > 57 ? 3.5 : 0.4, t > 57 ? 1.2 : 0.2, t > 57 ? 0.4 : 0);
  // phone screen: meme
  const vHead = headWorld(visitor);
  const target = show > 0.5 ? headWorld(marcus) : vHead;
  phoneHold(visitor, visitor.phone, t, vlerp(vHead, headWorld(marcus), show));
  visitor.phoneScreen.material = memeFrameMat;
  drawMemeScreen(t); renderMemeNow = true;
  // cameras
  if (t < 51.6) { const k = inOut(seg(t, 50, 51.6)); look(vlerp(V(-2.2, 1.5, 4.8), V(-2.4, 1.2, 4.0), k), vlerp(V(2.6, 1.5, 0.8), V(0.3, 2.6, -3.4), k), 46); }
  else if (t < 54.0) { const k = inOut(seg(t, 51.6, 54)); look(vlerp(V(-1.5, 0.75, -3.1), V(-1.3, 0.85, -2.8), k), V(1.1, 2.0, -1.4), 46); }
  else if (t < 55.6) { const k = inOut(seg(t, 54, 55.6)); look(vlerp(V(0.5, 1.6, 3.6), V(0.5, 1.6, 3.1), k), V(0.55, 1.5, -1.2), 46); }
  else if (t < 56.0) { const ph = visitor.phone.position; look(ph.clone().add(V(0.32, 0.03, 0.12)), ph, 30); }
  else if (t < 57.0) { const k = outCubic(seg(t, 56.0, 56.3)); const hw = headWorld(marcus); const ry = marcus.root.rotation.y; const fw = V(Math.sin(ry), 0, Math.cos(ry)), sd = V(Math.cos(ry), 0, -Math.sin(ry));
    look(vlerp(hw.clone().add(fw.clone().multiplyScalar(2.2)).add(sd.clone().multiplyScalar(0.6)), hw.clone().add(fw.clone().multiplyScalar(1.45)).add(sd.clone().multiplyScalar(0.35)), k).add(shake(t, 0.01)), hw.clone().add(V(0, -0.12, 0)), lerp(40, 38, k)); }
  else { const k = inOut(seg(t, 57, 60)); look(vlerp(V(-0.4, 0.7, 2.2), V(-1.3, 0.8, 3.4), k), vlerp(V(1.0, 1.9, -1.4), V(0.6, 2.3, -2.6), k), lerp(46, 50, k)); }
}
let renderMemeNow = false;

// ---------- master ----------
const SHOTS = [[0, 3.2, shotBattle], [3.2, 8, shotArrive], [8, 18, shotSelfie], [18, 28, shotRobo], [28, 40, shotFood], [40, 50, shotScooter], [50, 60.1, shotMuseum]];
window.renderFrame = (frame) => {
  const t = frame / FPS;
  renderPhone = false; renderMemeNow = false;
  const shot = SHOTS.find(([a, b]) => t >= a && t < b);
  if (shot[2] === shotMuseum) renderMeme();
  shot[2](t);
  if (renderPhone) {
    girl.phone.visible = false;
    renderer.setRenderTarget(rtSelfie); renderer.render(scene, phoneCam); renderer.setRenderTarget(null);
    girl.phone.visible = true;
  }
  renderer.render(scene, cam);
  ctx.drawImage(glc, 0, 0);
  drawVignette();
  // overlays
  if (t > 3.0 && t < 3.6) flash(t, 3.2, 0.4, '235,220,255');
  flash(t, 9.62, 0.25, '255,255,255', 0.9);
  if (t > 55.9 && t < 56.3) flash(t, 56.02, 0.18, '255,255,255', 0.7);
  drawTitle(t);
  drawTag(robo.position.clone().add(V(0, 2.4, 0)), 'PEDESTRIAN DETECTED', t, 21.7, 24.4, '#ff5a4f');
  drawTag(robo.position.clone().add(V(0, 2.4, 0)), 'YIELDING… 🙂', t, 24.6, 26.4, '#36c9ff');
  drawSocial(t);
  drawSubtitles(t);
  if (t > 59.7) { ctx.fillStyle = `rgba(0,0,0,${seg(t, 59.7, 60)})`; ctx.fillRect(0, 0, W, H); }
};
// preview hook
window.show = (frame) => window.renderFrame(frame);
await document.fonts.load(`900 40px Inter`).catch(() => {});
window.ready = true;
