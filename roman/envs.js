// Sets and props. Each set is a Group toggled per shot; all built once.
import * as THREE from 'three';
import { mat, basic, canvasTex, mesh, add, sphere, box, cyl, rbox, capsule, hash, makeHuman, C } from './lib.js';

const FONT = '"Inter", "Inter Display", sans-serif';

export function skyTex(top, mid, bottom, clouds = 0) {
  return canvasTex(64, 1024, (g, w, h) => {
    const gr = g.createLinearGradient(0, 0, 0, h);
    gr.addColorStop(0, top); gr.addColorStop(0.55, mid); gr.addColorStop(1, bottom);
    g.fillStyle = gr; g.fillRect(0, 0, w, h);
  });
}

// ---------- props ----------
export function makeCar(color = 0xd23b3b, { autonomous = false } = {}) {
  const car = new THREE.Group(); const body = new THREE.Group(); car.add(body);
  const paint = new THREE.MeshPhysicalMaterial({ color, roughness: 0.28, metalness: 0.4, clearcoat: 1, clearcoatRoughness: 0.08 });
  const glass = new THREE.MeshPhysicalMaterial({ color: 0x1b2433, roughness: 0.05, metalness: 0.2, transparent: true, opacity: 0.88 });
  add(body, mesh(rbox(1.9, 0.62, 4.3, 0.22, 4), paint), 0, 0.62, 0);
  const cab = add(body, mesh(rbox(1.62, 0.6, 2.3, 0.26, 4), glass), 0, 1.12, -0.2);
  add(body, mesh(rbox(1.66, 0.07, 2.1, 0.03, 2), paint), 0, 1.43, -0.22);
  // pillars
  for (const sx of [-1, 1]) for (const z of [-1.25, 0.85]) add(body, mesh(box(0.07, 0.56, 0.1), paint), sx * 0.8, 1.12, z);
  const wheels = [];
  for (const sx of [-1, 1]) for (const z of [-1.35, 1.35]) {
    const w = add(car, new THREE.Group(), sx * 0.86, 0.36, z);
    const tire = mesh(cyl(0.36, 0.36, 0.26, 28), mat(0x151515, 0.9)); tire.rotation.z = Math.PI / 2; w.add(tire);
    const rim = mesh(cyl(0.22, 0.22, 0.27, 20), mat(0xc9cdd2, 0.25, 1)); rim.rotation.z = Math.PI / 2; w.add(rim);
    for (let k = 0; k < 5; k++) { const sp = add(w, mesh(box(0.28, 0.06, 0.05), mat(0x8d9399, 0.3, 1)), 0, 0, 0); sp.rotation.x = k * Math.PI * 2 / 5; sp.position.x = sx * 0.14; sp.scale.x = 0.1; }
    wheels.push(w);
  }
  const headM = basic(0xfff6d8), tailM = new THREE.MeshStandardMaterial({ color: 0x7a0b0b, emissive: 0xff1a1a, emissiveIntensity: 0.3 });
  for (const sx of [-1, 1]) {
    add(body, mesh(rbox(0.42, 0.12, 0.08, 0.04, 2), headM), sx * 0.62, 0.75, 2.15);
    add(body, mesh(rbox(0.42, 0.12, 0.08, 0.04, 2), tailM), sx * 0.62, 0.78, -2.15);
  }
  add(body, mesh(rbox(1.0, 0.16, 0.06, 0.03, 2), mat(0x222222, 0.6)), 0, 0.5, 2.16);
  car.userData = { wheels, tailM, body };
  if (autonomous) {
    const lid = add(body, new THREE.Group(), 0, 1.56, -0.1);
    add(lid, mesh(cyl(0.2, 0.22, 0.12, 24), mat(0x1c1c1c, 0.4, 0.3)), 0, 0, 0);
    const spin = add(lid, mesh(cyl(0.16, 0.16, 0.12, 24), mat(0x2a2f38, 0.2, 0.6)), 0, 0.12, 0);
    add(spin, mesh(box(0.05, 0.05, 0.02), basic(0x4cd3ff)), 0, 0, 0.16);
    const led = new THREE.MeshStandardMaterial({ color: 0x0b2a40, emissive: 0x36c9ff, emissiveIntensity: 1.3 });
    add(body, mesh(box(1.5, 0.04, 0.04), led), 0, 0.95, 2.12);
    for (const sx of [-1, 1]) add(body, mesh(box(0.02, 0.05, 2.4), led), sx * 0.96, 0.9, 0);
    // side decal
    const decal = canvasTex(512, 96, (g, w, h) => { g.fillStyle = '#16a9e8'; g.font = `800 58px ${FONT}`; g.textBaseline = 'middle'; g.fillText('AUTOPILOT', 18, h / 2); });
    for (const sx of [-1, 1]) { const d = add(body, mesh(new THREE.PlaneGeometry(1.7, 0.32), basic(0xffffff, { map: decal, transparent: true }), { cast: false }), sx * 0.962, 0.62, 0.1); d.rotation.y = sx * Math.PI / 2; }
    car.userData.spin = spin; car.userData.led = led;
  }
  return car;
}

export function makeScooter(color = 0x2fbf71) {
  const s = new THREE.Group();
  const deck = add(s, mesh(rbox(0.2, 0.06, 0.95, 0.025, 2), mat(0x24272c, 0.5, 0.3)), 0, 0.14, 0);
  add(deck, mesh(box(0.17, 0.005, 0.8), mat(0x0f0f0f, 0.95)), 0, 0.033, 0);
  const stem = add(s, mesh(cyl(0.025, 0.03, 1.05, 14), mat(color, 0.35, 0.3)), 0, 0.68, 0.46); stem.rotation.x = -0.18;
  const bar = add(s, mesh(cyl(0.02, 0.02, 0.55, 12), mat(0x24272c, 0.4, 0.4)), 0, 1.2, 0.56); bar.rotation.z = Math.PI / 2;
  for (const sx of [-1, 1]) add(s, mesh(cyl(0.028, 0.028, 0.11, 12), mat(0x111111, 0.9)), sx * 0.27, 1.2, 0.56).rotation.z = Math.PI / 2;
  add(s, mesh(rbox(0.08, 0.05, 0.03, 0.01, 1), basic(0xfffbe8)), 0, 1.08, 0.6);
  const wheels = [];
  for (const z of [-0.42, 0.5]) {
    const w = add(s, new THREE.Group(), 0, 0.11, z);
    const t = mesh(cyl(0.11, 0.11, 0.06, 20), mat(0x121212, 0.85)); t.rotation.z = Math.PI / 2; w.add(t);
    const h = mesh(cyl(0.06, 0.06, 0.065, 12), mat(color, 0.4, 0.3)); h.rotation.z = Math.PI / 2; w.add(h);
    wheels.push(w);
  }
  add(s, mesh(rbox(0.22, 0.05, 0.22, 0.02, 1), mat(color, 0.5)), 0, 0.2, -0.45);
  s.userData.wheels = wheels;
  return s;
}

export function makePortal() {
  const p = new THREE.Group();
  const ringM = new THREE.MeshStandardMaterial({ color: 0x7a3cff, emissive: 0x9b5cff, emissiveIntensity: 2.2, roughness: 0.3 });
  const ring = add(p, mesh(new THREE.TorusGeometry(1.25, 0.09, 16, 80), ringM, { cast: false }), 0, 0, 0);
  const ring2 = add(p, mesh(new THREE.TorusGeometry(1.36, 0.035, 10, 80), new THREE.MeshStandardMaterial({ color: 0x31e0ff, emissive: 0x31e0ff, emissiveIntensity: 2.5 }), { cast: false }), 0, 0, 0);
  const swirlM = new THREE.ShaderMaterial({
    transparent: true, side: THREE.DoubleSide, depthWrite: false,
    uniforms: { t: { value: 0 }, a: { value: 1 } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: `varying vec2 vUv; uniform float t; uniform float a;
      void main(){ vec2 p=vUv*2.-1.; float r=length(p); float ang=atan(p.y,p.x);
        float s=sin(ang*5.+r*14.-t*7.)*.5+.5; float s2=sin(ang*3.-r*9.+t*4.)*.5+.5;
        vec3 c=mix(vec3(.25,.05,.6),vec3(.2,.85,1.),s*s2); c=mix(c,vec3(1.,.95,1.),pow(1.-r,4.)*1.4);
        float al=smoothstep(1.,.86,r)*a*(.75+.25*s); gl_FragColor=vec4(c*1.6,al); }`,
  });
  const disc = add(p, new THREE.Mesh(new THREE.CircleGeometry(1.22, 64), swirlM), 0, 0, 0);
  // sparks
  const n = 140, pos = new Float32Array(n * 3);
  const sparks = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ color: 0xbfe9ff, size: 0.06, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false }));
  sparks.geometry.setAttribute('position', new THREE.BufferAttribute(pos, 3)); p.add(sparks);
  const light = add(p, new THREE.PointLight(0xa070ff, 0, 9, 1.6), 0, 0, 0.5);
  p.userData = { ring, ring2, swirlM, sparks, light, n };
  return p;
}
export function updatePortal(p, t, open) {
  const u = p.userData; const k = Math.max(0.0001, open);
  p.scale.setScalar(k); p.visible = open > 0.001;
  u.ring.rotation.z = t * 0.6; u.ring2.rotation.z = -t * 0.9;
  u.swirlM.uniforms.t.value = t; u.swirlM.uniforms.a.value = Math.min(1, open * 1.2);
  u.light.intensity = 14 * Math.min(1, open);
  const a = u.sparks.geometry.attributes.position;
  for (let i = 0; i < u.n; i++) {
    const ph = (t * (0.4 + hash(i) * 0.5) + hash(i * 3)) % 1;
    const ang = hash(i * 7) * 6.283 + t * (1 + hash(i) * 2);
    const r = 1.3 + ph * 0.9;
    a.setXYZ(i, Math.cos(ang) * r, Math.sin(ang) * r, (hash(i * 11) - 0.5) * 0.6 + ph * 0.4);
  }
  a.needsUpdate = true; u.sparks.material.opacity = 0.9 * Math.min(1, open);
}

export function makeBurger() {
  const b = new THREE.Group();
  const bun = mat(0xd38a3a, 0.6);
  add(b, mesh(cyl(0.11, 0.1, 0.04, 24), bun), 0, 0.02, 0);
  add(b, mesh(cyl(0.115, 0.115, 0.035, 24), mat(0x5a2c16, 0.8)), 0, 0.055, 0);
  add(b, mesh(box(0.2, 0.008, 0.2), mat(0xf7c331, 0.5)), 0, 0.075, 0).rotation.y = 0.4;
  add(b, mesh(cyl(0.125, 0.125, 0.012, 16), mat(0x5fb43a, 0.7)), 0, 0.085, 0);
  const top = add(b, mesh(new THREE.SphereGeometry(0.115, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), bun), 0, 0.09, 0); top.scale.y = 0.7;
  for (let i = 0; i < 9; i++) add(b, mesh(sphere(0.008, 6, 4), mat(0xfff2cf, 0.6), { cast: false }), Math.cos(i * 2.4) * 0.06 * (0.5 + hash(i)), 0.155 + hash(i) * 0.01, Math.sin(i * 2.4) * 0.06 * (0.5 + hash(i)));
  return b;
}
let bagTex;
export function makeBag() {
  bagTex ??= canvasTex(256, 256, (g, w, h) => {
    g.fillStyle = '#c99a62'; g.fillRect(0, 0, w, h);
    g.fillStyle = '#d42a1f'; g.beginPath(); g.arc(w / 2, h / 2, 62, 0, 7); g.fill();
    g.fillStyle = '#ffd23a'; g.font = `900 46px ${FONT}`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('BURG', w / 2, h / 2 + 2);
  });
  const b = new THREE.Group();
  const m = mat(0xffffff, 0.85, 0, { map: bagTex });
  add(b, mesh(box(0.28, 0.36, 0.18), m), 0, 0.18, 0);
  const fold = add(b, mesh(box(0.28, 0.06, 0.05), mat(0xb4864f, 0.9)), 0, 0.39, 0); fold.rotation.x = 0.2;
  return b;
}

export function makePigeon() {
  const p = new THREE.Group(); const grey = mat(0x8a8f99, 0.8);
  const body = add(p, mesh(sphere(0.09, 16, 12), grey), 0, 0.1, 0); body.scale.set(0.8, 0.8, 1.2);
  const head = add(p, mesh(sphere(0.05, 14, 10), mat(0x6b7280, 0.7)), 0, 0.19, 0.08);
  add(head, mesh(new THREE.ConeGeometry(0.012, 0.04, 6), mat(0xe0b060, 0.6)), 0, 0, 0.055).rotation.x = Math.PI / 2;
  for (const sx of [-1, 1]) add(head, mesh(sphere(0.008, 6, 4), basic(0x111111)), sx * 0.03, 0.01, 0.035);
  const wings = [];
  for (const sx of [-1, 1]) {
    const w = add(p, new THREE.Group(), sx * 0.06, 0.12, 0);
    const f = add(w, mesh(box(0.16, 0.012, 0.12), mat(0x767c87, 0.8)), sx * 0.08, 0, -0.02);
    wings.push(w);
  }
  p.userData = { wings, head };
  return p;
}

// ---------- facades ----------
function facadeTex(base, accent, sign, seed) {
  return canvasTex(512, 1024, (g, w, h) => {
    g.fillStyle = base; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 400; i++) { g.fillStyle = `rgba(0,0,0,${hash(seed + i) * 0.04})`; g.fillRect(hash(i * 3 + seed) * w, hash(i * 5 + seed) * h, 6, 6); }
    const cols = 4, rows = 6;
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      const x = 40 + c * 112, y = 60 + r * 125;
      g.fillStyle = 'rgba(0,0,0,.18)'; g.fillRect(x - 6, y - 6, 76, 100);
      const lit = hash(seed * 13 + r * 7 + c) > 0.7;
      const gr = g.createLinearGradient(x, y, x + 64, y + 88);
      gr.addColorStop(0, lit ? '#ffe7a8' : '#9cc3e6'); gr.addColorStop(1, lit ? '#f0b95c' : '#2f4f73');
      g.fillStyle = gr; g.fillRect(x, y, 64, 88);
      g.fillStyle = '#f4f1ea'; g.fillRect(x + 30, y, 4, 88); g.fillRect(x, y + 42, 64, 4);
      g.fillStyle = accent; g.fillRect(x - 8, y + 90, 80, 8);
    }
    // ground floor shop
    g.fillStyle = '#2a2f36'; g.fillRect(0, 820, w, 204);
    const gl = g.createLinearGradient(0, 860, 0, 1024); gl.addColorStop(0, '#bfe1f5'); gl.addColorStop(1, '#5d7d96');
    g.fillStyle = gl; g.fillRect(30, 880, 300, 144); g.fillRect(360, 880, 120, 144);
    g.fillStyle = accent; g.fillRect(0, 812, w, 60);
    for (let i = 0; i < 12; i++) { g.fillStyle = i % 2 ? accent : '#f4f1ea'; g.beginPath(); g.moveTo(i * 43, 872); g.lineTo(i * 43 + 43, 872); g.lineTo(i * 43 + 21, 900); g.fill(); }
    g.fillStyle = '#fff'; g.font = `900 40px ${FONT}`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(sign, w / 2, 843);
  });
}
const FACADES = [
  ['#e9a46b', '#c4472f', 'PIZZA NAPOLI', 1], ['#f2e3c4', '#2e7d6b', 'CAFÉ 2026', 2], ['#7fb6c9', '#e0533d', 'PHONE REPAIR', 3],
  ['#f2c75c', '#3b5ba5', 'BOOKS', 4], ['#e8a3a8', '#5b3a8a', 'GELATO', 5], ['#c9d39a', '#b0402a', 'MARKET', 6],
];
export function makeBuilding(i, w = 8, h = 16, d = 8) {
  const [base, accent, sign, seed] = FACADES[i % FACADES.length];
  const tex = facadeTex(base, accent, sign, seed);
  const g = new THREE.Group();
  const front = mat(0xffffff, 0.85, 0, { map: tex });
  const side = mat(new THREE.Color(base).multiplyScalar(0.85), 0.9);
  const b = add(g, mesh(box(w, h, d), [side, side, mat(0x5a5f66, 0.9), side, front, side]), 0, h / 2, 0);
  add(g, mesh(box(w + 0.3, 0.4, d + 0.3), mat(new THREE.Color(accent), 0.7)), 0, h + 0.2, 0);
  return g;
}
function makeTree() {
  const t = new THREE.Group();
  add(t, mesh(cyl(0.12, 0.17, 2.4, 10), mat(0x6b4a2f, 0.9)), 0, 1.2, 0);
  const leaf = mat(0x4f9a3c, 0.85);
  for (let i = 0; i < 6; i++) add(t, mesh(sphere(0.9 + hash(i) * 0.4, 16, 12), leaf), Math.cos(i * 2.1) * 0.6, 2.8 + hash(i * 5) * 0.9, Math.sin(i * 2.1) * 0.6);
  return t;
}
function makeLamp() {
  const l = new THREE.Group(); const m = mat(0x2d333b, 0.5, 0.6);
  add(l, mesh(cyl(0.06, 0.09, 4.2, 12), m), 0, 2.1, 0);
  add(l, mesh(box(0.08, 0.08, 1.0), m), 0, 4.15, 0.45);
  add(l, mesh(rbox(0.3, 0.12, 0.45, 0.04, 2), m), 0, 4.08, 0.95);
  add(l, mesh(box(0.24, 0.02, 0.36), basic(0xfff3d0)), 0, 4.01, 0.95);
  return l;
}

// ---------- humans: background cast ----------
export function crowdMember(i, extra = {}) {
  const shirts = [0x3a6fd8, 0xf2994a, 0x27ae60, 0xeb5757, 0x9b51e0, 0xf2c94c, 0x2d9cdb, 0x111827];
  const pants = [0x2b3448, 0x5c4033, 0x1f2937, 0x6b7280, 0x384e77];
  const skins = [0xf0c4a0, 0xd9996a, 0x8d5a3b, 0xe8b48a, 0xb87a52];
  const hairs = [0x2a1a10, 0x6b4423, 0xd8b26a, 0x111111, 0x8a3b1e];
  const styles = ['short', 'bun', 'long', 'short', 'bald'];
  return makeHuman({ shirt: shirts[i % 8], pants: pants[i % 5], skin: skins[(i * 3) % 5], hair: hairs[(i * 7) % 5], hairStyle: styles[(i * 3) % 5], bulk: 0.92, scale: 0.9 + hash(i) * 0.08, ...extra });
}

// ---------- sets ----------
export function buildBattlefield(scene) {
  const g = new THREE.Group();
  const groundTex = canvasTex(512, 512, (c, w, h) => {
    c.fillStyle = '#8c8a4a'; c.fillRect(0, 0, w, h);
    for (let i = 0; i < 3000; i++) { c.fillStyle = hash(i) > 0.5 ? 'rgba(110,120,50,.35)' : 'rgba(140,110,60,.3)'; c.fillRect(hash(i * 3) * w, hash(i * 7) * h, 3 + hash(i) * 6, 2 + hash(i * 2) * 4); }
  }, { repeat: [14, 14] });
  const geo = new THREE.PlaneGeometry(200, 200, 80, 80);
  const pa = geo.attributes.position;
  for (let i = 0; i < pa.count; i++) { const x = pa.getX(i), y = pa.getY(i); const d = Math.hypot(x, y); pa.setZ(i, d > 14 ? (Math.sin(x * 0.07) + Math.cos(y * 0.05)) * 2.2 * Math.min(1, (d - 14) / 30) : 0); }
  geo.computeVertexNormals();
  const ground = add(g, mesh(geo, mat(0xffffff, 0.95, 0, { map: groundTex })), 0, 0, 0); ground.rotation.x = -Math.PI / 2;
  // tents
  const tentTex = canvasTex(256, 256, (c, w, h) => { for (let i = 0; i < 8; i++) { c.fillStyle = i % 2 ? '#e8dcc0' : '#c8442f'; c.fillRect(i * 32, 0, 32, h); } });
  const tents = [[-9, -16], [-4, -20], [5, -18], [11, -14], [-14, -11], [16, -22]];
  tents.forEach(([x, z], i) => {
    const t = add(g, mesh(new THREE.ConeGeometry(2.2, 2.8, 4, 1), mat(0xffffff, 0.85, 0, { map: tentTex })), x, 1.4, z); t.rotation.y = Math.PI / 4 + i;
  });
  // standards with SPQR banners
  const spqr = canvasTex(256, 320, (c, w, h) => {
    c.fillStyle = '#a3171d'; c.fillRect(0, 0, w, h); c.strokeStyle = '#e6b23a'; c.lineWidth = 12; c.strokeRect(10, 10, w - 20, h - 20);
    c.fillStyle = '#f2c14e'; c.font = `900 70px ${FONT}`; c.textAlign = 'center'; c.fillText('SPQR', w / 2, h / 2 + 24);
  });
  const banners = [];
  [[-3.2, -5], [3.4, -7], [-7, -9]].forEach(([x, z]) => {
    const pole = add(g, new THREE.Group(), x, 0, z);
    add(pole, mesh(cyl(0.05, 0.05, 4.4, 10), mat(0x6b4a2f, 0.8)), 0, 2.2, 0);
    add(pole, mesh(sphere(0.14), mat(C.bronze, 0.3, 0.9)), 0, 4.45, 0);
    add(pole, mesh(cyl(0.03, 0.03, 1.2, 8), mat(C.bronze, 0.3, 0.9)), 0, 4.0, 0).rotation.z = Math.PI / 2;
    const flag = add(pole, mesh(new THREE.PlaneGeometry(1.0, 1.25, 6, 8), mat(0xffffff, 0.8, 0, { map: spqr, side: THREE.DoubleSide })), 0, 3.35, 0.03);
    flag.userData.base = Float32Array.from(flag.geometry.attributes.position.array); banners.push(flag);
  });
  // spears & shields on the ground, rocks, smoke
  for (let i = 0; i < 14; i++) {
    const x = (hash(i) - 0.5) * 24, z = -3 - hash(i * 3) * 14; if (Math.abs(x) < 2.2 && z > -6) continue;
    const s = add(g, mesh(cyl(0.025, 0.025, 2.6, 6), mat(0x6b4a2f, 0.8)), x, 1.0, z); s.rotation.set((hash(i * 5) - 0.5) * 0.6, 0, (hash(i * 9) - 0.5) * 0.6);
  }
  for (let i = 0; i < 16; i++) add(g, mesh(new THREE.DodecahedronGeometry(0.3 + hash(i * 2) * 0.5), mat(0x8a8275, 0.95)), (hash(i * 4) - 0.5) * 30, 0.1, -2 - hash(i * 6) * 20);
  const smokeM = new THREE.MeshBasicMaterial({ color: 0x9a8f86, transparent: true, opacity: 0.25, depthWrite: false });
  const smokes = [];
  for (let i = 0; i < 10; i++) { const s = add(g, new THREE.Mesh(sphere(1, 12, 8), smokeM), -12 + i * 2.6, 2, -26 - hash(i) * 6); smokes.push(s); }
  g.userData = { banners, smokes, sky: skyTex('#3f5f9e', '#f2a65a', '#f6d39a'), fog: [0xf0b77a, 22, 70], sun: [8, 10, -6], sunColor: 0xffc890, sunI: 3.0, hemi: [0xffd9b0, 0x5a4a3a, 1.0], env: 0.55 };
  scene.add(g); return g;
}

export function buildCity(scene) {
  const g = new THREE.Group();
  const roadTex = canvasTex(512, 512, (c, w, h) => {
    c.fillStyle = '#3a3d42'; c.fillRect(0, 0, w, h);
    for (let i = 0; i < 2500; i++) { c.fillStyle = `rgba(255,255,255,${hash(i) * 0.05})`; c.fillRect(hash(i * 3) * w, hash(i * 7) * h, 2, 2); }
    c.fillStyle = '#f2f2f2'; c.fillRect(0, h / 2 - 5, w * 0.45, 10);
  }, { repeat: [12, 1] });
  const road = add(g, mesh(new THREE.PlaneGeometry(120, 8), mat(0xffffff, 0.85, 0, { map: roadTex })), 0, 0.001, 0); road.rotation.x = -Math.PI / 2;
  // crosswalk
  for (let i = 0; i < 8; i++) { const s = add(g, mesh(new THREE.PlaneGeometry(3.2, 0.5), mat(0xf4f4f4, 0.7), { cast: false }), 6, 0.006, -3.5 + i * 1.0); s.rotation.x = -Math.PI / 2; }
  const walkTex = canvasTex(256, 256, (c, w, h) => {
    c.fillStyle = '#c9c5bc'; c.fillRect(0, 0, w, h); c.strokeStyle = '#a9a59b'; c.lineWidth = 3;
    for (let i = 0; i <= 4; i++) { c.beginPath(); c.moveTo(i * 64, 0); c.lineTo(i * 64, h); c.stroke(); c.beginPath(); c.moveTo(0, i * 64); c.lineTo(w, i * 64); c.stroke(); }
  }, { repeat: [60, 3] });
  for (const sz of [-1, 1]) {
    const sw = add(g, mesh(box(120, 0.18, 6), [mat(0xb9b5ac, 0.8), mat(0xb9b5ac, 0.8), mat(0xffffff, 0.85, 0, { map: walkTex }), mat(0xb9b5ac, 0.8), mat(0xb9b5ac, 0.8), mat(0xb9b5ac, 0.8)]), 0, 0.09, sz * 7);
    add(g, mesh(box(120, 0.2, 0.25), mat(0xe2ded5, 0.7)), 0, 0.1, sz * 4.1);
  }
  // buildings behind (z<0) and in front (z>0, seen in reverse shots)
  const bld = [];
  for (let i = 0; i < 12; i++) {
    const w = 7.5, h = 13 + hash(i * 3) * 9, d = 8;
    const b = add(g, makeBuilding(i, w, h, d), -40 + i * 7.6, 0, -14.2); bld.push(b);
    const f = add(g, makeBuilding(i + 3, w, 12 + hash(i) * 8, d), -40 + i * 7.6, 0, 16.2); f.rotation.y = Math.PI;
  }
  for (let i = 0; i < 8; i++) { add(g, makeTree(), -30 + i * 9, 0.18, -9.3); add(g, makeTree(), -22.5 + i * 9, 0.18, 9.4); }
  for (let i = 0; i < 7; i++) { const l = add(g, makeLamp(), -33 + i * 10, 0.18, -4.5); const l2 = add(g, makeLamp(), -28 + i * 10, 0.18, 4.6); l2.rotation.y = Math.PI; }
  // bench + bin + traffic light
  const bench = add(g, new THREE.Group(), -4, 0.18, 8.4);
  add(bench, mesh(box(1.8, 0.08, 0.5), mat(0x8a5a33, 0.8)), 0, 0.45, 0); add(bench, mesh(box(1.8, 0.5, 0.06), mat(0x8a5a33, 0.8)), 0, 0.75, -0.22);
  for (const sx of [-0.8, 0.8]) add(bench, mesh(box(0.06, 0.45, 0.5), mat(0x2d333b, 0.5, 0.5)), sx, 0.22, 0);
  const tl = add(g, new THREE.Group(), 4.3, 0.18, 4.7);
  add(tl, mesh(cyl(0.07, 0.07, 3.2, 10), mat(0x2d333b, 0.5, 0.6)), 0, 1.6, 0);
  add(tl, mesh(rbox(0.32, 0.9, 0.3, 0.05, 2), mat(0x22262b, 0.5)), 0, 3.4, 0);
  const tlLights = [0xff3b30, 0xffcc00, 0x34c759].map((c, k) => add(tl, mesh(sphere(0.09, 14, 10), new THREE.MeshStandardMaterial({ color: 0x222222, emissive: c, emissiveIntensity: k === 2 ? 2 : 0.05 })), 0, 3.7 - k * 0.28, 0.14));
  // billboard
  const bb = canvasTex(1024, 512, (c, w, h) => {
    const gr = c.createLinearGradient(0, 0, w, h); gr.addColorStop(0, '#5b2cff'); gr.addColorStop(1, '#ff3ea5'); c.fillStyle = gr; c.fillRect(0, 0, w, h);
    c.fillStyle = '#fff'; c.font = `900 150px ${FONT}`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('2026', w / 2, h / 2 - 40);
    c.font = `700 52px ${FONT}`; c.fillText('THE FUTURE IS NOW', w / 2, h / 2 + 90);
  });
  const board = add(g, mesh(new THREE.PlaneGeometry(8, 4), basic(0xffffff, { map: bb })), 2, 15, -10.15);
  g.userData = { tlLights, sky: skyTex('#4d8fe0', '#9cc9f2', '#e8f2fa'), fog: [0xcfe2f2, 35, 110], sun: [10, 18, 12], sunColor: 0xfff1dc, sunI: 3.2, hemi: [0xdfefff, 0x6a6458, 1.25], env: 0.6 };
  scene.add(g); return g;
}

export function buildRestaurant(scene) {
  const g = new THREE.Group();
  const floorTex = canvasTex(256, 256, (c, w, h) => { for (let y = 0; y < 4; y++) for (let x = 0; x < 4; x++) { c.fillStyle = (x + y) % 2 ? '#f3efe6' : '#d23a2c'; c.fillRect(x * 64, y * 64, 64, 64); } }, { repeat: [8, 8] });
  const floor = add(g, mesh(new THREE.PlaneGeometry(20, 20), mat(0xffffff, 0.35, 0, { map: floorTex })), 0, 0, 0); floor.rotation.x = -Math.PI / 2;
  const wallM = mat(0xf6c445, 0.8), wall2 = mat(0xe24b3b, 0.8);
  add(g, mesh(box(20, 6, 0.3), wallM), 0, 3, -5);
  add(g, mesh(box(0.3, 6, 20), wall2), -7, 3, 3); add(g, mesh(box(0.3, 6, 20), wall2), 7, 3, 3);
  add(g, mesh(box(20, 0.3, 20), mat(0xf4efe4, 0.9)), 0, 6, 3);
  // stripe
  add(g, mesh(box(20, 0.35, 0.05), mat(0xd23a2c, 0.6)), 0, 2.2, -4.83);
  // counter
  const counter = add(g, new THREE.Group(), 0, 0, -2.2);
  add(counter, mesh(rbox(6.4, 1.05, 1.1, 0.06, 2), mat(0xd23a2c, 0.5)), 0, 0.53, 0);
  add(counter, mesh(rbox(6.6, 0.08, 1.25, 0.03, 2), mat(0xf2efe8, 0.25, 0.1)), 0, 1.09, 0);
  // menu boards
  const menu = (title, price, hue) => canvasTex(512, 320, (c, w, h) => {
    c.fillStyle = '#1d1d22'; c.fillRect(0, 0, w, h);
    c.fillStyle = hue; c.beginPath(); c.arc(140, 170, 95, 0, 7); c.fill();
    // burger icon
    c.fillStyle = '#e09a3e'; c.beginPath(); c.ellipse(140, 145, 80, 45, 0, Math.PI, 0); c.fill();
    c.fillStyle = '#5fb43a'; c.fillRect(62, 150, 156, 12); c.fillStyle = '#5a2c16'; c.fillRect(66, 162, 148, 26); c.fillStyle = '#e09a3e'; c.fillRect(70, 188, 140, 22);
    c.fillStyle = '#fff'; c.font = `900 44px ${FONT}`; c.fillText(title, 260, 140); c.fillStyle = '#ffd23a'; c.font = `900 56px ${FONT}`; c.fillText(price, 260, 210);
  });
  [['CLASSIC', '$5', '#d23a2c'], ['DOUBLE', '$7', '#f2994a'], ['VEGGIE', '$6', '#27ae60']].forEach(([a, b, c], i) =>
    add(g, mesh(new THREE.PlaneGeometry(2.2, 1.375), basic(0xffffff, { map: menu(a, b, c) })), -2.4 + i * 2.4, 3.9, -4.84));
  const logo = canvasTex(1024, 256, (c, w, h) => { c.fillStyle = '#d23a2c'; c.font = `900 170px ${FONT}`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('BURG·RUSH', w / 2, h / 2); });
  add(g, mesh(new THREE.PlaneGeometry(5, 1.25), basic(0xffffff, { map: logo, transparent: true })), 0, 5.2, -4.84);
  // kiosk (screen texture is redrawn per frame by the film)
  const kiosk = add(g, new THREE.Group(), 4.0, 0, 0.5); kiosk.rotation.y = -0.5;
  add(kiosk, mesh(rbox(0.5, 1.0, 0.35, 0.05, 2), mat(0xf2f2f2, 0.4)), 0, 0.5, 0);
  add(kiosk, mesh(rbox(0.86, 1.4, 0.12, 0.04, 2), mat(0x1b1b1f, 0.3)), 0, 1.65, 0.05).rotation.x = -0.12;
  const ktex = canvasTex(576, 960, () => {});
  const screen = add(kiosk, mesh(new THREE.PlaneGeometry(0.76, 1.27), basic(0xffffff, { map: ktex }), { cast: false }), 0, 1.65, 0.118); screen.rotation.x = -0.12;
  // pendant lights
  const lamps = [];
  for (let i = 0; i < 3; i++) {
    const p = add(g, new THREE.Group(), -2.4 + i * 2.4, 4.4, -1.6);
    add(p, mesh(cyl(0.01, 0.01, 1.6, 6), mat(0x222222)), 0, 0.8, 0);
    add(p, mesh(new THREE.ConeGeometry(0.35, 0.35, 24, 1, true), mat(0x1f6f5c, 0.5, 0, { side: THREE.DoubleSide })), 0, 0, 0);
    add(p, mesh(sphere(0.1), basic(0xfff1c8)), 0, -0.1, 0);
    const pl = add(g, new THREE.PointLight(0xffd9a0, 6, 7, 1.6), -2.4 + i * 2.4, 4.1, -1.6); lamps.push(pl);
  }
  // tables
  for (const [x, z] of [[-4.5, 2.5], [-2.0, 3.6]]) {
    const t = add(g, new THREE.Group(), x, 0, z);
    add(t, mesh(cyl(0.6, 0.6, 0.06, 28), mat(0xf2efe8, 0.3)), 0, 0.78, 0); add(t, mesh(cyl(0.06, 0.06, 0.76, 10), mat(0x2d333b, 0.4, 0.6)), 0, 0.38, 0);
    for (const a of [0, Math.PI]) { const st = add(t, mesh(cyl(0.22, 0.22, 0.08, 20), mat(0xd23a2c, 0.5)), Math.cos(a) * 0.9, 0.48, Math.sin(a) * 0.9); add(t, mesh(cyl(0.04, 0.04, 0.45, 8), mat(0x2d333b, 0.4, 0.6)), Math.cos(a) * 0.9, 0.22, Math.sin(a) * 0.9); }
  }
  // glass door frame at the front right
  const door = add(g, new THREE.Group(), 5.2, 0, 5.5);
  add(door, mesh(box(0.1, 2.6, 0.1), mat(0x9aa3ad, 0.3, 0.8)), -0.9, 1.3, 0); add(door, mesh(box(0.1, 2.6, 0.1), mat(0x9aa3ad, 0.3, 0.8)), 0.9, 1.3, 0); add(door, mesh(box(1.9, 0.1, 0.1), mat(0x9aa3ad, 0.3, 0.8)), 0, 2.6, 0);
  g.userData = { kiosk, ktex, screen, counter, lamps, sky: null, bg: 0xf6c445, fog: null, sun: [3, 8, 6], sunColor: 0xfff1dc, sunI: 1.6, hemi: [0xfff3df, 0x8a5a3a, 1.35], env: 0.7 };
  scene.add(g); return g;
}

export function buildPlaza(scene) {
  const g = new THREE.Group();
  const tile = canvasTex(256, 256, (c, w, h) => {
    c.fillStyle = '#d9cdb8'; c.fillRect(0, 0, w, h);
    c.strokeStyle = '#b8aa92'; c.lineWidth = 3;
    for (let y = 0; y < 8; y++) for (let x = 0; x < 4; x++) { const ox = (y % 2) * 32; c.strokeRect(x * 64 + ox, y * 32, 64, 32); }
    for (let i = 0; i < 200; i++) { c.fillStyle = `rgba(0,0,0,${hash(i) * 0.05})`; c.fillRect(hash(i * 3) * w, hash(i * 7) * h, 4, 4); }
  }, { repeat: [40, 40] });
  const ground = add(g, mesh(new THREE.PlaneGeometry(120, 120), mat(0xffffff, 0.8, 0, { map: tile })), 0, 0, 0); ground.rotation.x = -Math.PI / 2;
  // fountain at origin-ish
  const f = add(g, new THREE.Group(), 0, 0, -6);
  add(f, mesh(cyl(3, 3.2, 0.6, 48), mat(0xd8d0c0, 0.6)), 0, 0.3, 0);
  add(f, mesh(cyl(2.75, 2.75, 0.5, 48), mat(0x3d8fbf, 0.08, 0.1, { transparent: true, opacity: 0.85 })), 0, 0.36, 0);
  add(f, mesh(cyl(0.3, 0.45, 1.6, 20), mat(0xd8d0c0, 0.6)), 0, 1.2, 0);
  add(f, mesh(cyl(1.0, 0.7, 0.25, 32), mat(0xd8d0c0, 0.6)), 0, 2.0, 0);
  const n = 220, pos = new Float32Array(n * 3);
  const drops = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ color: 0xcfefff, size: 0.07, transparent: true, opacity: 0.85, depthWrite: false }));
  drops.geometry.setAttribute('position', new THREE.BufferAttribute(pos, 3)); f.add(drops);
  // surrounding buildings
  for (let i = 0; i < 9; i++) { const a = -1.3 + i * 0.33; const b = add(g, makeBuilding(i + 1, 8, 12 + hash(i) * 8, 8), Math.sin(a) * 30, 0, -Math.cos(a) * 30 - 4); b.rotation.y = -a; }
  for (let i = 0; i < 6; i++) add(g, makeTree(), -14 + i * 5.6, 0, -14 - (i % 2) * 2);
  // planters & benches
  for (const [x, z] of [[-6, 4], [6, 5], [-9, -2], [9, -1]]) { const p = add(g, mesh(cyl(0.8, 0.7, 0.7, 24), mat(0x9b6a4a, 0.8)), x, 0.35, z); add(p, mesh(sphere(0.75, 16, 12), mat(0x4f9a3c, 0.85)), 0, 0.7, 0).scale.y = 0.7; }
  g.userData = { drops, fountain: f, sky: skyTex('#3f86e0', '#a6d0f5', '#f2f6fa'), fog: [0xd7e7f5, 30, 90], sun: [-8, 16, 10], sunColor: 0xfff1dc, sunI: 3.2, hemi: [0xdfefff, 0x8a7a68, 1.2], env: 0.6 };
  scene.add(g); return g;
}
export function updateFountain(P, t) {
  const a = P.userData.drops.geometry.attributes.position;
  for (let i = 0; i < a.count; i++) {
    const ph = (t * 0.9 + hash(i)) % 1, ang = hash(i * 3) * 6.283, sp = 0.8 + hash(i * 5) * 0.5;
    a.setXYZ(i, Math.cos(ang) * ph * sp * 1.1, 2.2 + ph * 2.2 - ph * ph * 3.6, Math.sin(ang) * ph * sp * 1.1);
  }
  a.needsUpdate = true;
}

export function buildMuseum(scene) {
  const g = new THREE.Group();
  const marbleTex = canvasTex(512, 512, (c, w, h) => {
    for (let y = 0; y < 4; y++) for (let x = 0; x < 4; x++) { c.fillStyle = (x + y) % 2 ? '#e9e4da' : '#b9b2a6'; c.fillRect(x * 128, y * 128, 128, 128); }
    for (let i = 0; i < 40; i++) { c.strokeStyle = `rgba(120,110,100,${0.08 + hash(i) * 0.12})`; c.lineWidth = 1 + hash(i * 2) * 2; c.beginPath(); let x = hash(i * 3) * w, y = hash(i * 5) * h; c.moveTo(x, y); for (let k = 0; k < 6; k++) { x += (hash(i * 7 + k) - 0.3) * 90; y += (hash(i * 11 + k) - 0.5) * 90; c.lineTo(x, y); } c.stroke(); }
  }, { repeat: [6, 6] });
  const floor = add(g, mesh(new THREE.PlaneGeometry(40, 40), mat(0xffffff, 0.18, 0.05, { map: marbleTex })), 0, 0, 0); floor.rotation.x = -Math.PI / 2;
  const wallM = mat(0x7a2e2e, 0.85), trim = mat(0xe9e2d4, 0.6);
  add(g, mesh(box(40, 9, 0.3), wallM), 0, 4.5, -8);
  add(g, mesh(box(0.3, 9, 40), wallM), -9, 4.5, 4); add(g, mesh(box(0.3, 9, 40), wallM), 9, 4.5, 4);
  add(g, mesh(box(40, 0.4, 0.4), trim), 0, 0.2, -7.8); add(g, mesh(box(40, 0.5, 0.5), trim), 0, 8.6, -7.8);
  add(g, mesh(box(40, 0.3, 40), mat(0xefe9dd, 0.9)), 0, 9, 4);
  // columns
  for (const x of [-6.5, -3.2, 3.2, 6.5]) {
    const col = add(g, new THREE.Group(), x, 0, -6.6);
    add(col, mesh(cyl(0.45, 0.5, 7.6, 24), mat(0xefe9dd, 0.45)), 0, 4.2, 0);
    add(col, mesh(box(1.25, 0.4, 1.25), trim), 0, 0.2, 0); add(col, mesh(box(1.25, 0.45, 1.25), trim), 0, 8.2, 0);
    for (let k = 0; k < 12; k++) { const a = k / 12 * Math.PI * 2; add(col, mesh(cyl(0.04, 0.04, 7.4, 6), mat(0xd8d1c3, 0.5)), Math.cos(a) * 0.47, 4.2, Math.sin(a) * 0.47); }
  }
  // paintings
  const paint = (seed) => canvasTex(256, 320, (c, w, h) => {
    const gr = c.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, ['#2a4d7a', '#7a4a2a', '#2a6a4a'][seed % 3]); gr.addColorStop(1, '#e8c890'); c.fillStyle = gr; c.fillRect(0, 0, w, h);
    for (let i = 0; i < 6; i++) { c.fillStyle = `hsla(${hash(seed * 9 + i) * 360},50%,45%,.6)`; c.beginPath(); c.arc(hash(seed + i) * w, 120 + hash(seed * 3 + i) * 180, 20 + hash(i) * 50, 0, 7); c.fill(); }
  });
  [[-7.6, 0], [7.6, 1]].forEach(([x, s]) => {
    const fr = add(g, mesh(box(2.2, 2.8, 0.12), mat(0xc79a3a, 0.35, 0.8)), x, 4.2, -7.75);
    add(g, mesh(new THREE.PlaneGeometry(1.8, 2.3), basic(0xffffff, { map: paint(s) })), x, 4.2, -7.68);
  });
  // statue on pedestal
  const ped = add(g, new THREE.Group(), 0, 0, -4.6);
  add(ped, mesh(box(1.8, 1.4, 1.8), mat(0xd9d2c4, 0.5)), 0, 0.7, 0);
  add(ped, mesh(box(2.0, 0.2, 2.0), trim), 0, 1.45, 0); add(ped, mesh(box(2.0, 0.2, 2.0), trim), 0, 0.1, 0);
  const plaque = canvasTex(512, 160, (c, w, h) => { c.fillStyle = '#b8862e'; c.fillRect(0, 0, w, h); c.fillStyle = '#3a2a10'; c.font = `900 84px ${FONT}`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('AVGVSTVS', w / 2, h / 2 + 4); });
  add(ped, mesh(new THREE.PlaneGeometry(1.2, 0.375), mat(0xffffff, 0.3, 0.6, { map: plaque })), 0, 0.85, 0.91);
  const statue = makeHuman({ outfit: 'marble', scale: 1.25 });
  ped.add(statue.root); statue.root.position.y = 1.55;
  // velvet ropes
  for (const x of [-1.6, 1.6]) { const st = add(g, new THREE.Group(), x, 0, -2.6); add(st, mesh(cyl(0.05, 0.05, 1.0, 10), mat(0xc79a3a, 0.3, 0.9)), 0, 0.5, 0); add(st, mesh(sphere(0.08), mat(0xc79a3a, 0.3, 0.9)), 0, 1.02, 0); add(st, mesh(cyl(0.22, 0.25, 0.06, 20), mat(0xc79a3a, 0.3, 0.9)), 0, 0.03, 0); }
  const rope = add(g, mesh(new THREE.TubeGeometry(new THREE.QuadraticBezierCurve3(new THREE.Vector3(-1.6, 0.95, -2.6), new THREE.Vector3(0, 0.55, -2.6), new THREE.Vector3(1.6, 0.95, -2.6)), 20, 0.035, 8), mat(0x8e1219, 0.6)), 0, 0, 0);
  const spot = add(g, new THREE.SpotLight(0xfff0d6, 120, 18, 0.45, 0.5, 1.4), 0, 8.5, 1); spot.target = statue.root; spot.castShadow = true;
  g.userData = { statue, ped, spot, sky: null, bg: 0x3b1818, fog: null, sun: [4, 9, 6], sunColor: 0xfff1dc, sunI: 1.4, hemi: [0xfff3e6, 0x5a3a2a, 1.0], env: 0.75 };
  scene.add(g); return g;
}
