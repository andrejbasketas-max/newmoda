// 3D bottle stage. Bundled to assets/scene.js with `npm run build`.
// One fixed, transparent canvas renders a glass bottle that follows whichever
// [data-3d-anchor] element is on screen (hero, then the notes section).
// If WebGL is unavailable the SVG bottles in the page stay visible instead.
import {
  WebGLRenderer, Scene, PerspectiveCamera, Group, Mesh, Points, Color,
  MeshPhysicalMaterial, MeshStandardMaterial, PointsMaterial, CylinderGeometry, TorusGeometry,
  PlaneGeometry, BufferGeometry, Float32BufferAttribute, CanvasTexture, SRGBColorSpace,
  PMREMGenerator, DirectionalLight, PointLight, ACESFilmicToneMapping, AdditiveBlending, MathUtils,
} from 'three';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/examples/jsm/geometries/RoundedBoxGeometry.js';

const canvas = document.querySelector('[data-stage]');
const anchors = [...document.querySelectorAll('[data-3d-anchor]')];
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function webglAvailable() {
  try {
    const c = document.createElement('canvas');
    return !!(window.WebGL2RenderingContext && c.getContext('webgl2'));
  } catch { return false; }
}

if (canvas && anchors.length && webglAvailable()) init();

function init() {
  const renderer = new WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
  renderer.toneMapping = ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.95;
  renderer.setClearColor(0x000000, 0);

  const scene = new Scene();
  const pmrem = new PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.55;
  pmrem.dispose();

  const camera = new PerspectiveCamera(32, 1, 0.1, 100);
  camera.position.set(0, 0, 10);
  const viewHeight = 2 * camera.position.z * Math.tan(MathUtils.degToRad(camera.fov / 2));

  const key = new DirectionalLight(0xffe2b8, 2.2);
  key.position.set(3, 4, 5);
  const rim = new DirectionalLight(0xffc27a, 3);
  rim.position.set(-4, 2, -3);
  const glow = new PointLight(0xff9a3c, 1.6, 5, 1.8);
  glow.position.set(0, -0.4, -1.2);
  scene.add(key, rim);

  /* ---------- Bottle ---------- */
  const rig = new Group();       // follows the anchor on screen
  const tilt = new Group();      // reacts to the pointer
  const spin = new Group();      // idle + scroll rotation
  const bottle = new Group();
  rig.add(tilt); tilt.add(spin); spin.add(bottle); scene.add(rig);
  bottle.add(glow);

  const glass = new MeshPhysicalMaterial({
    color: 0xffffff, metalness: 0, roughness: 0, transmission: 1, thickness: 0.35, ior: 1.5,
    clearcoat: 1, clearcoatRoughness: 0.02, envMapIntensity: 0.9, specularIntensity: 0.8,
  });
  const body = new Mesh(new RoundedBoxGeometry(1.6, 2, 0.95, 6, 0.17), glass);

  const liquidColor = new Color('#B4651E');
  const liquidTarget = new Color('#B4651E');
  const liquid = new MeshPhysicalMaterial({
    color: liquidColor, roughness: 0.12, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.06,
    emissive: liquidColor.clone().multiplyScalar(0.06), envMapIntensity: 0.6,
  });
  const juice = new Mesh(new RoundedBoxGeometry(1.4, 1.74, 0.74, 4, 0.1), liquid);
  juice.position.y = -0.06;

  const gold = new MeshStandardMaterial({ color: 0xd9a64a, metalness: 1, roughness: 0.22, envMapIntensity: 1.6 });
  const collar = new Mesh(new CylinderGeometry(0.27, 0.3, 0.22, 48), gold);
  collar.position.y = 1.1;
  const lacquer = new MeshPhysicalMaterial({ color: 0x141110, metalness: 0.2, roughness: 0.28, clearcoat: 1, clearcoatRoughness: 0.08 });
  const cap = new Mesh(new RoundedBoxGeometry(0.82, 0.86, 0.82, 4, 0.07), lacquer);
  cap.position.y = 1.64;
  const band = new Mesh(new TorusGeometry(0.58, 0.018, 12, 4), gold);
  band.rotation.set(Math.PI / 2, 0, Math.PI / 4);
  band.scale.set(1, 1, 1);
  band.position.y = 1.34;

  const labelTex = makeLabel();
  const label = new Mesh(new PlaneGeometry(0.8, 0.556), new MeshStandardMaterial({ map: labelTex, roughness: 0.6 }));
  // Redraw once the brand fonts arrive.
  document.fonts?.ready.then(() => { drawLabel(labelTex.image); labelTex.needsUpdate = true; });
  label.position.set(0, -0.12, 0.478);

  bottle.add(body, juice, collar, cap, band, label);
  bottle.position.y = -0.5; // centre the whole silhouette (≈ -1 … 2.07)
  const BOTTLE_H = 3.1;

  /* ---------- Gold dust ---------- */
  const COUNT = 220;
  const pos = new Float32Array(COUNT * 3);
  const seeds = new Float32Array(COUNT);
  for (let i = 0; i < COUNT; i++) {
    const r = 1.2 + Math.random() * 1.6;
    const a = Math.random() * Math.PI * 2;
    pos[i * 3] = Math.cos(a) * r;
    pos[i * 3 + 1] = (Math.random() - 0.5) * 4;
    pos[i * 3 + 2] = Math.sin(a) * r * 0.6;
    seeds[i] = Math.random();
  }
  const dustGeo = new BufferGeometry();
  dustGeo.setAttribute('position', new Float32BufferAttribute(pos, 3));
  const dust = new Points(dustGeo, new PointsMaterial({
    size: 0.05, map: makeSprite(), transparent: true, depthWrite: false, blending: AdditiveBlending,
    color: 0xf3c97a, opacity: 0.85, sizeAttenuation: true,
  }));
  tilt.add(dust);

  /* ---------- State ---------- */
  const state = {
    w: 0, h: 0,
    pointer: { x: 0, y: 0 }, tiltNow: { x: 0, y: 0 },
    pos: { x: 0, y: 0, s: 1 }, active: null, opacity: 0,
    intro: reduceMotion ? 1 : 0, introStarted: reduceMotion,
  };

  function resize() {
    state.w = window.innerWidth; state.h = window.innerHeight;
    renderer.setSize(state.w, state.h, false);
    camera.aspect = state.w / state.h;
    camera.updateProjectionMatrix();
  }
  resize();
  window.addEventListener('resize', resize);

  window.addEventListener('pointermove', (e) => {
    state.pointer.x = (e.clientX / state.w) * 2 - 1;
    state.pointer.y = (e.clientY / state.h) * 2 - 1;
  }, { passive: true });

  const HERO_LIQUID = '#B4651E';
  let notesLiquid = '#D08A3E';
  window.addEventListener('newmoda:liquid', (e) => {
    notesLiquid = e.detail;
    if (state.active?.dataset['3dAnchor'] === 'notes') liquidTarget.set(notesLiquid);
  });
  window.addEventListener('newmoda:intro', () => { state.introStarted = true; });
  // Start anyway if the motion layer never fires (e.g. GSAP failed to load).
  setTimeout(() => { state.introStarted = true; }, 2600);

  document.documentElement.classList.add('has-3d');

  /* ---------- Loop ---------- */
  let last = performance.now();
  const easeOutExpo = (t) => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t));

  function measure() {
    // Pick the anchor with the most on-screen area.
    let best = null, bestVis = 0, bestRect = null;
    for (const el of anchors) {
      const r = el.getBoundingClientRect();
      const vis = Math.max(0, Math.min(r.bottom, state.h) - Math.max(r.top, 0)) / Math.max(1, Math.min(r.height, state.h));
      if (vis > bestVis) { best = el; bestVis = vis; bestRect = r; }
    }
    return { el: best, vis: bestVis, rect: bestRect };
  }

  function frame(now) {
    const dt = Math.min((now - last) / 1000, 0.05);
    last = now;
    const t = now / 1000;
    const { el, vis, rect } = measure();

    const targetOpacity = el ? MathUtils.smoothstep(vis, 0.55, 0.92) : 0;
    state.opacity += (targetOpacity - state.opacity) * Math.min(1, dt * 8);
    if (targetOpacity === 0 && state.opacity < 0.04) state.opacity = 0;
    canvas.style.opacity = state.opacity.toFixed(3);

    if (el && state.opacity > 0.002) {
      const wpp = viewHeight / state.h; // world units per CSS pixel
      const cx = (rect.left + rect.width / 2 - state.w / 2) * wpp;
      const cy = -(rect.top + rect.height / 2 - state.h / 2) * wpp;
      const fit = el.dataset['3dAnchor'] === 'hero' ? 0.74 : 0.56;
      const s = Math.min(rect.height * fit, rect.width * 1.1) * wpp / BOTTLE_H;
      if (state.active !== el) { // jump when switching anchors (both are off screen at that point)
        state.active = el;
        Object.assign(state.pos, { x: cx, y: cy, s });
        liquidTarget.set(el.dataset['3dAnchor'] === 'notes' ? notesLiquid : HERO_LIQUID);
      }
      const k = Math.min(1, dt * 10);
      state.pos.x += (cx - state.pos.x) * k;
      state.pos.y += (cy - state.pos.y) * k;
      state.pos.s += (s - state.pos.s) * k;

      // Intro: rise and unwind into place.
      if (state.introStarted && state.intro < 1) state.intro = Math.min(1, state.intro + dt / 2.2);
      const ie = easeOutExpo(state.intro);

      rig.position.set(state.pos.x, state.pos.y - (1 - ie) * 2.2, 0);
      rig.scale.setScalar(state.pos.s * (0.75 + 0.25 * ie));

      // Pointer tilt
      const tx = reduceMotion ? 0 : state.pointer.y * 0.18;
      const ty = reduceMotion ? 0 : state.pointer.x * 0.35;
      state.tiltNow.x += (tx - state.tiltNow.x) * Math.min(1, dt * 3);
      state.tiltNow.y += (ty - state.tiltNow.y) * Math.min(1, dt * 3);
      tilt.rotation.set(state.tiltNow.x, state.tiltNow.y, 0);

      // Rotation: hero sways and turns as it scrolls away; notes turns with scroll progress.
      let rotY;
      if (el.dataset['3dAnchor'] === 'notes') {
        const section = el.closest('section');
        const sr = section.getBoundingClientRect();
        const p = MathUtils.clamp(-sr.top / Math.max(1, sr.height - state.h), 0, 1);
        rotY = p * Math.PI * 2;
      } else {
        const p = MathUtils.clamp(-rect.top / Math.max(1, rect.height), 0, 1);
        rotY = (reduceMotion ? 0 : Math.sin(t * 0.5) * 0.45) + p * 1.4;
      }
      rotY -= (1 - ie) * Math.PI * 1.25;
      spin.rotation.y += (rotY - spin.rotation.y) * Math.min(1, dt * 6);
      bottle.position.y = -0.5 + (reduceMotion ? 0 : Math.sin(t * 1.1) * 0.06);

      // Liquid colour
      liquidColor.lerp(liquidTarget, Math.min(1, dt * 3));
      liquid.emissive.copy(liquidColor).multiplyScalar(0.06);
      glow.color.copy(liquidColor).offsetHSL(0, 0.1, 0.15);

      // Dust drifts upward
      if (!reduceMotion) {
        const arr = dustGeo.attributes.position.array;
        for (let i = 0; i < COUNT; i++) {
          let y = arr[i * 3 + 1] + dt * (0.12 + seeds[i] * 0.25);
          if (y > 2.2) y = -2.2;
          arr[i * 3 + 1] = y;
          arr[i * 3] += Math.sin(t * 0.6 + seeds[i] * 12) * dt * 0.05;
        }
        dustGeo.attributes.position.needsUpdate = true;
      }
      dust.material.opacity = 0.85 * ie;

      renderer.render(scene, camera);
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

function makeLabel() {
  const c = document.createElement('canvas');
  c.width = 512; c.height = 356;
  drawLabel(c);
  const tex = new CanvasTexture(c);
  tex.colorSpace = SRGBColorSpace;
  tex.anisotropy = 4;
  return tex;
}

function drawLabel(c) {
  const g = c.getContext('2d');
  g.fillStyle = '#F7F2EA'; g.fillRect(0, 0, c.width, c.height);
  g.strokeStyle = '#A16207'; g.lineWidth = 3; g.strokeRect(22, 22, c.width - 44, c.height - 44);
  g.lineWidth = 1; g.strokeRect(32, 32, c.width - 64, c.height - 64);
  g.fillStyle = '#1C1917'; g.textAlign = 'center';
  g.font = 'italic 500 132px Cormorant, Georgia, serif';
  g.fillText('N', c.width / 2, 196);
  g.font = '600 26px Montserrat, Arial, sans-serif';
  g.letterSpacing = '8px';
  g.fillText('NEWMODA', c.width / 2, 262);
  g.fillStyle = '#A16207'; g.font = '500 18px Montserrat, Arial, sans-serif';
  g.fillText('EAU DE PARFUM · 100 ML', c.width / 2, 298);
}

function makeSprite() {
  const c = document.createElement('canvas');
  c.width = c.height = 64;
  const g = c.getContext('2d');
  const grd = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  grd.addColorStop(0, 'rgba(255,255,255,1)');
  grd.addColorStop(0.3, 'rgba(255,230,170,.6)');
  grd.addColorStop(1, 'rgba(255,200,120,0)');
  g.fillStyle = grd; g.fillRect(0, 0, 64, 64);
  const tex = new CanvasTexture(c);
  tex.colorSpace = SRGBColorSpace;
  return tex;
}
