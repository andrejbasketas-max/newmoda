// Shared helpers: easing, materials, canvas textures, and the character rig.
import * as THREE from 'three';

export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const smooth = (t) => { t = clamp(t); return t * t * (3 - 2 * t); };
export const inOut = (t) => { t = clamp(t); return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
export const outCubic = (t) => 1 - Math.pow(1 - clamp(t), 3);
export const outBack = (t, s = 1.70158) => { t = clamp(t) - 1; return t * t * ((s + 1) * t + s) + 1; };
export const outElastic = (t) => { t = clamp(t); return t === 0 || t === 1 ? t : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * (2 * Math.PI / 3)) + 1; };
// 0→1 between a and b
export const seg = (t, a, b) => clamp((t - a) / (b - a));
export const hash = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
export const noise1 = (x) => { const i = Math.floor(x), f = x - i; const u = f * f * (3 - 2 * f); return lerp(hash(i), hash(i + 1), u) * 2 - 1; };

// ---------- materials ----------
const matCache = new Map();
export function mat(color, rough = 0.65, metal = 0, extra = {}) {
  const key = [color, rough, metal, JSON.stringify(extra)].join('|');
  if (!extra.map && matCache.has(key)) return matCache.get(key);
  const m = new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: metal, ...extra });
  if (!extra.map) matCache.set(key, m);
  return m;
}
export const basic = (color, extra = {}) => new THREE.MeshBasicMaterial({ color, ...extra });

export function canvasTex(w, h, draw, { repeat = null, srgb = true } = {}) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d'); draw(g, w, h);
  const t = new THREE.CanvasTexture(c);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
  t.userData.canvas = c; t.userData.ctx = g;
  return t;
}

export function mesh(geo, material, { cast = true, receive = true } = {}) {
  const m = new THREE.Mesh(geo, material); m.castShadow = cast; m.receiveShadow = receive; return m;
}
export function add(parent, obj, x = 0, y = 0, z = 0) { obj.position.set(x, y, z); parent.add(obj); return obj; }
export const sphere = (r, ws = 32, hs = 20) => new THREE.SphereGeometry(r, ws, hs);
export const capsule = (r, len) => new THREE.CapsuleGeometry(r, len, 8, 20);
export const box = (x, y, z) => new THREE.BoxGeometry(x, y, z);
export const cyl = (rt, rb, h, s = 32, open = false) => new THREE.CylinderGeometry(rt, rb, h, s, 1, open);
export function rbox(w, h, d, r = 0.05, seg = 4) {
  // rounded box via extrude of a rounded rect
  const s = new THREE.Shape(); const x = -w / 2, y = -h / 2;
  s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r);
  s.lineTo(x + w, y + h - r); s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r); s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y);
  const g = new THREE.ExtrudeGeometry(s, { depth: Math.max(0.001, d - 2 * r), bevelEnabled: true, bevelThickness: r, bevelSize: r * 0.98, bevelSegments: seg, curveSegments: seg * 2 });
  g.translate(0, 0, -(d - 2 * r) / 2); g.computeVertexNormals(); return g;
}

// ---------- palette ----------
export const C = {
  skin: 0xd9996a, skinDark: 0xc98656, hair: 0x23160f, bronze: 0xc48a3e, bronzeDark: 0x8a5a24,
  red: 0xb81d24, redDark: 0x8e1219, leather: 0x6e4224, leatherDark: 0x4a2a14, wood: 0x9b6a3c,
  white: 0xf4f1ea, black: 0x111111,
};

// ---------- character rig ----------
// Faces +z. Pose angles in radians; see applyPose for meaning.
export function makeHuman(o = {}) {
  const roman = o.outfit === 'roman';
  const marble = o.outfit === 'marble';
  const M = (c, r = 0.65, m = 0) => marble ? mat(0xe8e4dc, 0.45, 0) : mat(c, r, m);
  const skin = M(o.skin ?? C.skin, 0.55);
  const s = o.scale ?? 1;
  const bulk = o.bulk ?? (roman || marble ? 1.12 : 1);
  const root = new THREE.Group(); root.scale.setScalar(s);
  const hips = add(root, new THREE.Group(), 0, 0.98, 0);
  const torso = add(hips, new THREE.Group(), 0, 0, 0);
  const H = { root, hips, torso, o };

  // --- torso ---
  if (roman || marble) {
    add(torso, mesh(sphere(0.3), M(C.red, 0.8)), 0, 0.2, 0).scale.set(1.15 * bulk, 0.9, 0.85);
    const chest = add(torso, mesh(sphere(0.34, 40, 24), M(C.bronze, 0.32, 0.85)), 0, 0.46, 0);
    chest.scale.set(1.12 * bulk, 1.0, 0.82);
    // segmented bands of the lorica
    for (let i = 0; i < 4; i++) {
      const band = add(torso, mesh(new THREE.TorusGeometry(0.33, 0.018, 8, 40), M(C.bronzeDark, 0.35, 0.85)), 0, 0.22 + i * 0.075, 0);
      band.rotation.x = Math.PI / 2; band.scale.set(1.13 * bulk * (0.96 + i * 0.02), 0.84, 1);
    }
    // pecs line
    const pec = add(torso, mesh(new THREE.TorusGeometry(0.11, 0.012, 6, 24, Math.PI), M(C.bronzeDark, 0.35, 0.85)), -0.11, 0.56, 0.27);
    pec.rotation.z = Math.PI; const pec2 = pec.clone(); pec2.position.x = 0.11; torso.add(pec2);
    // belt + pteruges strips
    const belt = add(torso, mesh(new THREE.TorusGeometry(0.33, 0.035, 10, 40), M(C.leather, 0.7)), 0, 0.12, 0);
    belt.rotation.x = Math.PI / 2; belt.scale.set(1.12 * bulk, 0.84, 1);
    add(torso, mesh(sphere(0.045), M(C.bronze, 0.3, 0.9)), 0, 0.12, 0.29);
    const skirt = add(hips, mesh(cyl(0.34 * bulk, 0.42 * bulk, 0.34, 40, true), M(C.red, 0.85)), 0, -0.05, 0);
    skirt.material = skirt.material.clone(); skirt.material.side = THREE.DoubleSide; skirt.scale.z = 0.82;
    for (let i = 0; i < 14; i++) {
      const a = (i / 14) * Math.PI * 2;
      const strip = add(hips, mesh(box(0.07, 0.3, 0.015), M(i % 2 ? C.leather : C.leatherDark, 0.7)), Math.sin(a) * 0.37 * bulk, -0.06, Math.cos(a) * 0.37 * 0.84 * bulk);
      strip.rotation.y = a; strip.rotation.x = 0.12;
      add(strip, mesh(sphere(0.02, 8, 6), M(C.bronze, 0.3, 0.9)), 0, -0.13, 0.01);
    }
  } else {
    const shirt = M(o.shirt ?? 0x3a6fd8, 0.8);
    add(torso, mesh(capsule(0.27, 0.32), shirt), 0, 0.38, 0).scale.set(1.0 * bulk, 1, 0.75);
    add(hips, mesh(sphere(0.27), M(o.pants ?? 0x2b3448, 0.8)), 0, 0.02, 0).scale.set(1.02, 0.6, 0.8);
    if (o.apron) add(torso, mesh(box(0.42, 0.5, 0.02), M(o.apron, 0.8)), 0, 0.12, 0.22);
    if (o.logo) add(torso, mesh(new THREE.CircleGeometry(0.07, 24), M(o.logo, 0.6)), 0.1, 0.5, 0.205);
  }
  // neck
  add(torso, mesh(cyl(0.085, 0.1, 0.18), skin), 0, 0.78, 0);

  // --- head ---
  const head = add(torso, new THREE.Group(), 0, 0.84, 0); H.head = head;
  const skull = add(head, mesh(sphere(0.27, 48, 32), skin), 0, 0.22, 0); skull.scale.set(0.95, 1.04, 0.97);
  const jaw = add(head, mesh(sphere(0.21, 40, 24), skin), 0, 0.1, 0.05); jaw.scale.set(roman || marble ? 1.08 : 0.95, 0.82, 1.0);
  for (const sx of [-1, 1]) add(head, mesh(sphere(0.06, 16, 12), skin), sx * 0.255, 0.2, 0).scale.set(0.5, 1, 0.8);
  const nose = add(head, mesh(sphere(0.055, 20, 14), M(o.skin ?? C.skin, 0.5)), 0, 0.175, 0.265); nose.scale.set(1, 1.15, 1.25);
  // hair
  const hairM = M(o.hair ?? C.hair, 0.85);
  const hairStyle = o.hairStyle ?? 'short';
  if (hairStyle !== 'bald') {
    const cap = add(head, mesh(new THREE.SphereGeometry(0.285, 40, 20, 0, Math.PI * 2, 0, Math.PI * (hairStyle === 'long' ? 0.62 : 0.5)), hairM), 0, 0.24, -0.015);
    cap.rotation.x = -0.32; cap.scale.set(0.97, 1.04, 1.0);
    if (roman || marble || hairStyle === 'short') {
      // fringe tufts
      for (let i = -4; i <= 4; i++) {
        const a = i * 0.21;
        const tuft = add(head, mesh(new THREE.ConeGeometry(0.035, 0.09, 8), hairM), Math.sin(a) * 0.235, 0.405 - Math.abs(i) * 0.012, Math.cos(a) * 0.2 - 0.02);
        tuft.rotation.set(1.9, 0, -a * 0.8);
      }
    }
    if (hairStyle === 'bun') add(head, mesh(sphere(0.11, 20, 14), hairM), 0, 0.5, -0.12);
    if (hairStyle === 'long') { const back = add(head, mesh(capsule(0.2, 0.25), hairM), 0, 0.08, -0.12); back.scale.set(1.25, 1, 0.6); }
  }
  if (o.cap) {
    const capM = M(o.cap, 0.7);
    const c = add(head, mesh(new THREE.SphereGeometry(0.29, 32, 16, 0, Math.PI * 2, 0, Math.PI * 0.45), capM), 0, 0.27, 0);
    c.scale.y = 0.9; const brim = add(head, mesh(cyl(0.16, 0.16, 0.02, 24), capM), 0, 0.33, 0.28); brim.scale.z = 0.7;
  }
  if (marble) {
    // laurel wreath
    const wreath = add(head, new THREE.Group(), 0, 0.36, -0.02); wreath.rotation.x = -0.25;
    for (let i = 0; i < 22; i++) {
      const a = (i / 22) * Math.PI * 2; if (Math.abs(Math.sin(a / 2)) < 0.12) continue;
      const leaf = add(wreath, mesh(sphere(0.04, 10, 6), M(0)), Math.sin(a) * 0.27, 0, Math.cos(a) * 0.27);
      leaf.scale.set(0.5, 0.3, 1.2); leaf.rotation.y = a;
    }
  }
  // eyes
  const eyeM = M(C.white, 0.25), pupilM = mat(0x16100c, 0.2), irisM = mat(o.iris ?? 0x5a3a1e, 0.35);
  H.eyes = [];
  for (const sx of [-1, 1]) {
    const eye = add(head, new THREE.Group(), sx * 0.095, 0.245, 0.215);
    const ball = add(eye, mesh(sphere(0.062, 24, 16), marble ? M(0) : eyeM, { cast: false }), 0, 0, 0); ball.scale.z = 0.7;
    const look = add(eye, new THREE.Group(), 0, 0, 0);
    if (!marble) {
      const iris = add(look, mesh(sphere(0.034, 16, 12), irisM, { cast: false }), 0, 0, 0.034); iris.scale.z = 0.4;
      add(look, mesh(sphere(0.019, 12, 10), pupilM, { cast: false }), 0, 0, 0.044).scale.z = 0.4;
      add(look, mesh(sphere(0.008, 8, 6), basic(0xffffff), { cast: false }), 0.012, 0.012, 0.05);
    }
    // eyelid (skin cap that slides down for blinks)
    const lid = add(eye, mesh(new THREE.SphereGeometry(0.066, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), skin, { cast: false }), 0, 0, 0);
    lid.scale.z = 0.75;
    H.eyes.push({ eye, look, lid, ball });
  }
  // brows
  H.brows = [];
  for (const sx of [-1, 1]) {
    const b = add(head, mesh(rbox(0.12, 0.026, 0.03, 0.012, 2), M(o.hair ?? C.hair, 0.8)), sx * 0.1, 0.335, 0.235);
    H.brows.push(b);
  }
  // mouth
  const mouth = add(head, new THREE.Group(), 0, 0.06, 0.235); H.mouth = mouth;
  const cavity = add(mouth, mesh(sphere(0.07, 24, 16), mat(0x3a0d10, 0.6), { cast: false }), 0, 0, 0.0); cavity.scale.set(1, 0.6, 0.35);
  const teeth = add(mouth, mesh(box(0.085, 0.018, 0.012), M(C.white, 0.3), { cast: false }), 0, 0.02, 0.006);
  const tongue = add(mouth, mesh(sphere(0.04, 16, 10), mat(0xc4505a, 0.5), { cast: false }), 0, -0.025, 0.012); tongue.scale.set(1.1, 0.5, 0.6);
  const lipM = mat(o.lip ?? 0x9c5040, 0.5);
  const smile = add(mouth, mesh(new THREE.TorusGeometry(0.06, 0.011, 8, 24, Math.PI), lipM, { cast: false }), 0, 0.02, 0.012);
  smile.rotation.z = Math.PI;
  H.mouthParts = { cavity, teeth, tongue, smile };
  // --- arms ---
  H.arms = [];
  for (const side of [1, -1]) { // 1 = character's left (+x)
    const sh = add(torso, new THREE.Group(), side * 0.4 * bulk, 0.66, 0);
    const upperM = roman || marble ? skin : M(o.shirt ?? 0x3a6fd8, 0.8);
    const up = add(sh, mesh(capsule(0.095 * bulk, 0.26), upperM), 0, -0.17, 0);
    if (roman || marble) {
      const bicep = add(sh, mesh(sphere(0.1 * bulk), skin), 0, -0.14, 0.03); bicep.scale.set(1, 1.3, 1);
      const pad = add(sh, mesh(new THREE.SphereGeometry(0.16, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), M(C.bronze, 0.32, 0.85)), 0, 0.02, 0);
      pad.scale.set(1.05, 0.85, 1.05);
      for (let i = 1; i <= 2; i++) {
        const p = add(sh, mesh(new THREE.SphereGeometry(0.165 - i * 0.01, 24, 8, 0, Math.PI * 2, Math.PI * 0.42, Math.PI * 0.12), M(C.bronzeDark, 0.35, 0.85)), 0, 0.02 - i * 0.045, 0);
        p.scale.set(1.05, 0.85, 1.05);
      }
    } else if (o.longSleeve) { /* full sleeve handled by forearm color */ }
    const el = add(sh, new THREE.Group(), 0, -0.34, 0);
    const foreM = (!roman && !marble && o.longSleeve) ? upperM : skin;
    add(el, mesh(capsule(0.08 * bulk, 0.24), foreM), 0, -0.15, 0);
    if (roman) add(el, mesh(cyl(0.092 * bulk, 0.085 * bulk, 0.16, 20), M(C.leather, 0.7)), 0, -0.2, 0);
    const hand = add(el, new THREE.Group(), 0, -0.32, 0);
    add(hand, mesh(sphere(0.082, 20, 14), skin), 0, -0.03, 0).scale.set(0.85, 1.15, 0.7);
    const th = add(hand, mesh(capsule(0.026, 0.05), skin), side * -0.05, -0.01, 0.04); th.rotation.z = side * 0.6;
    H.arms.push({ sh, el, hand, side });
  }
  // --- legs ---
  H.legs = [];
  for (const side of [1, -1]) {
    const hp = add(hips, new THREE.Group(), side * 0.15, -0.04, 0);
    const legM = roman || marble ? skin : M(o.pants ?? 0x2b3448, 0.8);
    add(hp, mesh(capsule(0.11 * (roman ? 1.05 : 1), 0.3), legM), 0, -0.22, 0);
    const kn = add(hp, new THREE.Group(), 0, -0.45, 0);
    add(kn, mesh(capsule(0.085, 0.3), legM), 0, -0.2, 0);
    if (roman) {
      const calf = add(kn, mesh(sphere(0.09), skin), 0, -0.12, -0.02); calf.scale.set(1, 1.5, 1);
      for (let i = 0; i < 3; i++) {
        const strap = add(kn, mesh(new THREE.TorusGeometry(0.088, 0.012, 6, 20), M(C.leatherDark, 0.7)), 0, -0.24 - i * 0.06, 0);
        strap.rotation.x = Math.PI / 2 + (i % 2 ? 0.25 : -0.25);
      }
    }
    const ft = add(kn, new THREE.Group(), 0, -0.42, 0);
    const shoeM = roman ? M(C.leather, 0.7) : marble ? M(0) : M(o.shoes ?? 0xf2f2f2, 0.6);
    if (roman) {
      add(ft, mesh(rbox(0.13, 0.035, 0.28, 0.015, 2), shoeM), 0, -0.05, 0.05);
      add(ft, mesh(rbox(0.12, 0.06, 0.24, 0.03, 2), skin), 0, -0.01, 0.05);
      for (let i = 0; i < 2; i++) { const s2 = add(ft, mesh(box(0.135, 0.015, 0.03), shoeM), 0, 0.0, 0.0 + i * 0.09); }
    } else add(ft, mesh(rbox(0.13, 0.09, 0.28, 0.04, 2), shoeM), 0, -0.02, 0.05);
    H.legs.push({ hp, kn, ft, side });
  }

  // --- cape ---
  if (roman) {
    const cw = 0.86, ch = 1.25, nx = 10, ny = 16;
    const geo = new THREE.PlaneGeometry(cw, ch, nx, ny); geo.translate(0, -ch / 2, 0);
    const capeM = mat(C.red, 0.85, 0, { side: THREE.DoubleSide });
    const cape = add(torso, mesh(geo, capeM), 0, 0.72, -0.24);
    cape.userData.base = Float32Array.from(geo.attributes.position.array);
    H.cape = cape;
    // cape clasps
    for (const sx of [-1, 1]) add(torso, mesh(sphere(0.045, 16, 10), M(C.bronze, 0.3, 0.9)), sx * 0.3, 0.72, 0.12);
  }
  // --- props ---
  if (roman) {
    // shield (scutum), curved wood with bronze rim and boss — held on the left forearm
    const sg = new THREE.Group();
    const shW = 1.05, shH = 1.12, R = 0.75, th = shW / R;
    const woodTex = canvasTex(512, 512, (g, w, h) => {
      g.fillStyle = '#9b6a3c'; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 7; i++) { // planks
        const x = (i / 7) * w; g.fillStyle = i % 2 ? '#a7733f' : '#8f6034'; g.fillRect(x, 0, w / 7, h);
        g.strokeStyle = 'rgba(40,20,5,.55)'; g.lineWidth = 4; g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke();
        for (let k = 0; k < 18; k++) { g.strokeStyle = `rgba(60,30,10,${0.08 + hash(i * 31 + k) * 0.12})`; g.lineWidth = 1.5; g.beginPath(); const yy = hash(i * 7 + k) * h; g.moveTo(x + 4, yy); g.bezierCurveTo(x + w / 21, yy + 20, x + w / 10, yy - 20, x + w / 7 - 4, yy + 8); g.stroke(); }
      }
      // painted red wings + lightning (scutum motif)
      g.strokeStyle = '#a3171d'; g.lineWidth = 16; g.lineCap = 'round';
      g.beginPath(); g.moveTo(w * 0.5, h * 0.5); g.quadraticCurveTo(w * 0.2, h * 0.2, w * 0.12, h * 0.12); g.moveTo(w * 0.5, h * 0.5); g.quadraticCurveTo(w * 0.8, h * 0.2, w * 0.88, h * 0.12);
      g.moveTo(w * 0.5, h * 0.5); g.quadraticCurveTo(w * 0.2, h * 0.8, w * 0.12, h * 0.88); g.moveTo(w * 0.5, h * 0.5); g.quadraticCurveTo(w * 0.8, h * 0.8, w * 0.88, h * 0.88); g.stroke();
    });
    const face = add(sg, mesh(new THREE.CylinderGeometry(R, R, shH, 32, 1, true, -th / 2, th), mat(0xffffff, 0.7, 0, { map: woodTex, side: THREE.DoubleSide })), 0, 0, -R);
    for (const yy of [-shH / 2, shH / 2]) {
      const rim = add(sg, mesh(new THREE.TorusGeometry(R, 0.022, 8, 40, th), M(C.bronze, 0.3, 0.9)), 0, yy, -R);
      rim.rotation.x = Math.PI / 2; rim.rotation.z = Math.PI / 2 - th / 2;
    }
    for (const sx of [-1, 1]) add(sg, mesh(cyl(0.022, 0.022, shH, 10), M(C.bronze, 0.3, 0.9)), Math.sin(th / 2) * R * sx, 0, Math.cos(th / 2) * R - R);
    add(sg, mesh(new THREE.SphereGeometry(0.13, 28, 14, 0, Math.PI * 2, 0, Math.PI / 2), M(C.bronze, 0.25, 0.95)), 0, 0, 0.01).rotation.x = Math.PI / 2;
    H.shield = sg;
    // gladius
    const gl = new THREE.Group();
    add(gl, mesh(box(0.06, 0.5, 0.012), mat(0xd7dde2, 0.18, 1.0)), 0, 0.34, 0);
    const tip = add(gl, mesh(new THREE.ConeGeometry(0.0425, 0.08, 4), mat(0xd7dde2, 0.18, 1.0)), 0, 0.63, 0); tip.rotation.y = Math.PI / 4; tip.scale.z = 0.3;
    add(gl, mesh(rbox(0.13, 0.04, 0.05, 0.015, 2), M(C.bronze, 0.3, 0.9)), 0, 0.08, 0);
    add(gl, mesh(cyl(0.022, 0.022, 0.12, 12), M(C.leatherDark, 0.7)), 0, 0.0, 0);
    add(gl, mesh(sphere(0.035, 14, 10), M(C.bronze, 0.3, 0.9)), 0, -0.07, 0);
    H.sword = gl;
    // scabbard on right hip
    const sc = add(hips, mesh(rbox(0.08, 0.5, 0.03, 0.012, 2), M(C.leatherDark, 0.6)), -0.38, -0.12, 0.05); sc.rotation.z = -0.15; H.scabbard = sc;
  }
  if (o.phone) {
    const ph = new THREE.Group();
    add(ph, mesh(rbox(0.085, 0.17, 0.012, 0.006, 2), mat(0x1a1a1f, 0.3, 0.4)), 0, 0, 0);
    H.phoneScreen = add(ph, mesh(new THREE.PlaneGeometry(0.076, 0.158), basic(0x222222), { cast: false }), 0, 0, 0.0071);
    H.phoneScreenBack = add(ph, mesh(new THREE.PlaneGeometry(0.076, 0.158), basic(0x9aa7c7), { cast: false }), 0, 0, -0.0071);
    H.phoneScreenBack.rotation.y = Math.PI;
    H.phone = ph;
  }
  root.traverse((m) => { if (m.isMesh) m.userData.owner = H; });
  H.pose = {};
  return H;
}

// Attach a prop to a hand; local offsets/rotation relative to the hand.
export function holdIn(H, prop, side, p = [0, -0.09, 0.03], r = [0, 0, 0]) {
  const arm = H.arms[side === 'L' ? 0 : 1];
  arm.hand.add(prop); prop.position.set(...p); prop.rotation.set(...r);
}

export const ZERO_POSE = {
  x: 0, y: 0, z: 0, ry: 0, hipsY: 0, hipsRx: 0, hipsRy: 0, hipsRz: 0, spineRx: 0, spineRy: 0, spineRz: 0,
  headRx: 0, headRy: 0, headRz: 0,
  lShX: 0, lShY: 0, lShZ: 0.12, lEl: 0.15, lWr: 0, rShX: 0, rShY: 0, rShZ: 0.12, rEl: 0.15, rWr: 0,
  lHipX: 0, lHipZ: 0.03, lKnee: 0, lFoot: 0, rHipX: 0, rHipZ: 0.03, rKnee: 0, rFoot: 0,
  browL: 0, browR: 0, browUp: 0, eyeX: 0, eyeY: 0, eyeOpen: 1, eyeSize: 1, mouthOpen: 0, mouthSmile: 0.2, mouthWide: 1,
};
export function pose(over = {}) { return { ...ZERO_POSE, ...over }; }
export function mixPose(a, b, t) {
  const o = {}; for (const k in a) o[k] = lerp(a[k], b[k] ?? a[k], t); return o;
}
export function addPose(a, d) { const o = { ...a }; for (const k in d) o[k] = (o[k] ?? 0) + d[k]; return o; }

// Shoulder: X = forward raise, Z = outward raise, Y = twist. Elbow bend forward. Hip X = forward, knee bends back.
export function applyPose(H, p) {
  H.pose = p;
  H.root.position.set(p.x, p.y, p.z); H.root.rotation.y = p.ry;
  H.hips.position.y = 0.98 + p.hipsY; H.hips.rotation.set(p.hipsRx, p.hipsRy, p.hipsRz);
  H.torso.rotation.set(p.spineRx, p.spineRy, p.spineRz);
  H.head.rotation.set(p.headRx, p.headRy, p.headRz);
  const [L, R] = H.arms;
  L.sh.rotation.set(-p.lShX, p.lShY, p.lShZ); L.el.rotation.set(-p.lEl, 0, 0); L.hand.rotation.set(-p.lWr, 0, 0);
  R.sh.rotation.set(-p.rShX, -p.rShY, -p.rShZ); R.el.rotation.set(-p.rEl, 0, 0); R.hand.rotation.set(-p.rWr, 0, 0);
  const [LL, RL] = H.legs;
  LL.hp.rotation.set(-p.lHipX, 0, p.lHipZ); LL.kn.rotation.x = p.lKnee; LL.ft.rotation.x = p.lFoot;
  RL.hp.rotation.set(-p.rHipX, 0, -p.rHipZ); RL.kn.rotation.x = p.rKnee; RL.ft.rotation.x = p.rFoot;
  // face
  H.brows[0].rotation.z = p.browL; H.brows[1].rotation.z = -p.browR;
  H.brows[0].position.y = H.brows[1].position.y = 0.335 + p.browUp * 0.04;
  for (const e of H.eyes) {
    e.look.position.set(p.eyeX * 0.02, p.eyeY * 0.016, 0);
    e.eye.scale.setScalar(p.eyeSize);
    const open = clamp(p.eyeOpen, 0, 1);
    e.lid.rotation.x = lerp(Math.PI * 0.62, -0.75, open); // lid rotates down to close
  }
  const mo = clamp(p.mouthOpen, 0, 1.3), mp = H.mouthParts;
  const showOpen = mo > 0.06;
  mp.cavity.visible = mp.teeth.visible = mp.tongue.visible = showOpen;
  mp.cavity.scale.set(0.8 * p.mouthWide + mo * 0.25, 0.12 + mo * 0.75, 0.35);
  mp.cavity.position.y = -mo * 0.02;
  mp.teeth.position.y = 0.07 * (0.12 + mo * 0.75) * 0.72 - mo * 0.02 - 0.008; mp.teeth.scale.x = p.mouthWide * (0.7 + mo * 0.2);
  mp.tongue.position.y = -0.02 - mo * 0.03;
  mp.smile.visible = !showOpen;
  const sm = p.mouthSmile;
  mp.smile.scale.set(p.mouthWide * 0.9, Math.max(0.15, Math.abs(sm)), 1);
  mp.smile.rotation.z = sm >= 0 ? Math.PI : 0;
  mp.smile.position.y = sm >= 0 ? 0.02 : -0.03;
}

// Cape cloth: hangs, trails behind with speed, ripples with wind.
export function updateCape(H, t, speed = 0, wind = 0.2, lift = 0) {
  const c = H.cape; if (!c) return;
  const pos = c.geometry.attributes.position, b = c.userData.base;
  const flow = clamp(speed / 6, 0, 1.4);
  for (let i = 0; i < pos.count; i++) {
    const x = b[i * 3], y = b[i * 3 + 1];
    const v = -y / 1.25; // 0 top → 1 bottom
    const back = v * v * (0.12 + flow * 0.95 + lift * 0.6) + v * 0.05;
    const ripple = Math.sin(t * (5 + flow * 9) - v * 6 + x * 3) * v * (0.03 + wind * 0.06 + flow * 0.1);
    const flare = 1 + v * (0.18 + flow * 0.2);
    const drop = v * v * (flow * 0.5 + lift * 0.5);
    pos.setXYZ(i, x * flare + Math.sin(t * 3 + v * 4) * v * 0.02, y + drop * 0.8, -back + ripple);
  }
  pos.needsUpdate = true; c.geometry.computeVertexNormals();
}

// Procedural cycles
export function walkPose(base, phase, amt = 1, stride = 1) {
  const s = Math.sin(phase), c = Math.cos(phase), s2 = Math.sin(phase * 2);
  return addPose(base, {
    hipsY: -Math.abs(c) * 0.035 * amt + 0.01, hipsRy: s * 0.12 * amt, spineRy: -s * 0.18 * amt, spineRx: 0.04 * amt,
    lHipX: s * 0.5 * amt * stride, rHipX: -s * 0.5 * amt * stride,
    lKnee: Math.max(0, -c) * 0.9 * amt + 0.08, rKnee: Math.max(0, c) * 0.9 * amt + 0.08,
    lFoot: Math.max(0, s) * 0.2 * amt, rFoot: Math.max(0, -s) * 0.2 * amt,
    lShX: -s * 0.45 * amt, rShX: s * 0.45 * amt, lEl: 0.25 * amt + Math.max(0, -s) * 0.3 * amt, rEl: 0.25 * amt + Math.max(0, s) * 0.3 * amt,
    headRy: s * 0.05 * amt, headRx: s2 * 0.02 * amt,
  });
}
export function runPose(base, phase, amt = 1) {
  const s = Math.sin(phase), c = Math.cos(phase);
  return addPose(base, {
    hipsY: Math.abs(s) * 0.07 * amt - 0.03, spineRx: 0.28 * amt, spineRy: -s * 0.2 * amt, hipsRy: s * 0.1 * amt,
    lHipX: s * 0.95 * amt, rHipX: -s * 0.95 * amt, lKnee: (0.6 + Math.max(0, -c) * 1.0) * amt, rKnee: (0.6 + Math.max(0, c) * 1.0) * amt,
    lShX: -s * 0.9 * amt, rShX: s * 0.9 * amt, lEl: 1.3 * amt, rEl: 1.3 * amt, headRx: -0.15 * amt,
  });
}
export function idlePose(base, t, amt = 1) {
  return addPose(base, { hipsY: Math.sin(t * 2.2) * 0.008 * amt, spineRx: Math.sin(t * 2.2) * 0.012 * amt, headRy: noise1(t * 0.6) * 0.06 * amt, headRx: noise1(t * 0.5 + 9) * 0.03 * amt });
}
// Blink: returns eyeOpen multiplier, blinking every ~3.4 s (offset per character)
export function blink(t, off = 0) {
  const p = (t + off) % 3.4; return p < 0.13 ? Math.abs(p - 0.065) / 0.065 : 1;
}
// Mouth from dialogue: syllable-shaped open amount
export function talk(t, lines, who) {
  for (const l of lines) {
    if (l.who !== who || t < l.t0 || t > l.t1) continue;
    const d = l.t1 - l.t0, u = (t - l.t0) / d * l.syl;
    const k = Math.floor(u), f = u - k;
    const shape = Math.sin(Math.PI * f);
    const amp = 0.45 + 0.45 * hash(k * 13.7 + l.t0) + (l.loud ? 0.35 : 0);
    const env = smooth(seg(t, l.t0, l.t0 + 0.08)) * (1 - smooth(seg(t, l.t1 - 0.12, l.t1)));
    return { open: shape * amp * env, loud: !!l.loud, line: l };
  }
  return { open: 0, loud: false, line: null };
}
