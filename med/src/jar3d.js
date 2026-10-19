// Real-time 3D honey jars for Gladni Medved.
// One WebGL renderer draws every visible jar and copies the frame into that jar's own 2D canvas,
// so the jars stay in normal page flow (text can sit on top, sections keep their backgrounds).
import {
  WebGLRenderer, Scene, PerspectiveCamera, Group, Mesh, Vector2, SplineCurve, LatheGeometry,
  CylinderGeometry, CircleGeometry, SphereGeometry, TorusGeometry, MeshPhysicalMaterial, MeshStandardMaterial,
  CanvasTexture, Color, DirectionalLight, PMREMGenerator, NeutralToneMapping, SRGBColorSpace,
  BackSide, FrontSide, AdditiveBlending, MathUtils,
} from 'three';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';

const { PRODUCTS, byId, C } = window.MED;
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

// ---------- Renderer ----------
let renderer;
try {
  renderer = new WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
} catch {
  renderer = null;
}

if (renderer) start();

function start() {
  const DPR = Math.min(devicePixelRatio || 1, 2);
  renderer.setPixelRatio(1);
  renderer.toneMapping = NeutralToneMapping;
  renderer.toneMappingExposure = 1;
  renderer.outputColorSpace = SRGBColorSpace;
  renderer.setClearColor(0x000000, 0);

  const scene = new Scene();
  const pmrem = new PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

  const key = new DirectionalLight(0xfff1d6, 2.2);
  key.position.set(-4, 6, 6);
  const rim = new DirectionalLight(0xffb347, 5);
  rim.position.set(5, 3, -6);
  const fill = new DirectionalLight(0xffd59a, 0.8);
  fill.position.set(4, -1, 5);
  scene.add(key, rim, fill);

  const camera = new PerspectiveCamera(28, 1, 0.1, 50);

  // ---------- Geometry ----------
  const smooth = (pts, n) => new SplineCurve(pts.map(([x, y]) => new Vector2(x, y))).getPoints(n);

  // Outer glass profile (radius, height) — a squat jar with rounded shoulder and short neck
  const outer = smooth([
    [0.001, 0], [0.82, 0], [0.97, 0.05], [1.0, 0.22], [1.0, 1.9], [0.98, 2.06], [0.9, 2.18],
    [0.76, 2.25], [0.72, 2.3], [0.72, 2.5], [0.69, 2.53],
  ], 90);
  const inner = smooth([
    [0.001, 0.12], [0.8, 0.12], [0.93, 0.18], [0.955, 0.3], [0.955, 1.88], [0.935, 2.02],
    [0.86, 2.13], [0.72, 2.2], [0.67, 2.26], [0.67, 2.53],
  ], 90);
  const honeyProfile = smooth([
    [0.001, 0.125], [0.79, 0.125], [0.92, 0.18], [0.948, 0.3], [0.948, 1.86], [0.93, 1.97],
    [0.6, 1.995], [0.001, 2.0],
  ], 70);

  const glassOuterGeo = new LatheGeometry(outer, 128);
  const glassInnerGeo = new LatheGeometry(inner, 128);
  const honeyGeo = new LatheGeometry(honeyProfile, 96);

  // Ribbed metal lid
  const lidGeo = new CylinderGeometry(0.79, 0.79, 0.36, 240, 2);
  {
    const p = lidGeo.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i), z = p.getZ(i);
      const r = Math.hypot(x, z);
      if (r < 0.785) continue;
      const a = Math.atan2(z, x);
      const k = 1 + 0.012 * Math.pow(Math.abs(Math.sin(a * 60)), 0.6);
      p.setX(i, x * k);
      p.setZ(i, z * k);
    }
    lidGeo.computeVertexNormals();
  }
  const lidTopGeo = new CircleGeometry(0.62, 96);
  const lidRingGeo = new TorusGeometry(0.7, 0.035, 12, 120);

  const LABEL_ARC = Math.PI * 2 * 0.86;
  const labelGeo = new CylinderGeometry(1.012, 1.012, 0.98, 160, 1, true, -LABEL_ARC / 2, LABEL_ARC);

  // Honey thread between lid and jar when the lid lifts
  const threadGeo = new CylinderGeometry(1, 1, 1, 20, 8, true);
  const dropGeo = new SphereGeometry(1, 24, 16);

  // ---------- Materials ----------
  // Glass adds only its reflections (black diffuse + additive blend), so the honey behind stays saturated
  const glassOuter = new MeshPhysicalMaterial({
    color: 0x000000, metalness: 0, roughness: 0.03, transparent: true, blending: AdditiveBlending,
    clearcoat: 1, clearcoatRoughness: 0.02, envMapIntensity: 1.6, side: FrontSide, depthWrite: false,
    specularIntensity: 1, ior: 1.5,
  });
  const glassInner = glassOuter.clone();
  glassInner.side = BackSide;
  glassInner.envMapIntensity = 0.7;

  const lidMat = new MeshStandardMaterial({ color: 0x1a0c05, metalness: 0.75, roughness: 0.3, envMapIntensity: 1.4 });

  // Honey: glossy, glowing core and deeper edges, like light passing through a thick liquid
  const honeyMats = new Map();
  function honeyMat(hex) {
    if (honeyMats.has(hex)) return honeyMats.get(hex);
    const base = new Color(hex);
    const m = new MeshPhysicalMaterial({
      color: base.clone().multiplyScalar(0.3), roughness: 0.16, metalness: 0, clearcoat: 0.8, clearcoatRoughness: 0.05,
      emissive: base.clone().multiplyScalar(0.78), envMapIntensity: 0.3,
    });
    // Fake light transport: a glowing, saturated core with deeper edges
    m.onBeforeCompile = (sh) => {
      sh.fragmentShader = sh.fragmentShader.replace(
        '#include <opaque_fragment>',
        `float facing = abs(dot(normalize(normal), normalize(vViewPosition)));
         outgoingLight *= mix(0.42, 1.0, pow(facing, 1.2));
         float luma = dot(outgoingLight, vec3(0.2126, 0.7152, 0.0722));
         outgoingLight = mix(vec3(luma), outgoingLight, 1.12);
         #include <opaque_fragment>`,
      );
    };
    honeyMats.set(hex, m);
    return m;
  }

  // Label: paper + gold foil. Metalness/roughness come from a second canvas (B = metal, G = rough).
  const labelMats = new Map();
  function bearPath(ctx, x, y, s) {
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(s / 48, s / 48);
    ctx.lineWidth = 2.4;
    ctx.lineJoin = ctx.lineCap = 'round';
    ctx.beginPath(); ctx.arc(10, 9, 6, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath(); ctx.arc(38, 9, 6, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(24, 5); ctx.bezierCurveTo(35, 5, 42, 13, 42, 23); ctx.bezierCurveTo(42, 32, 34, 38, 24, 38);
    ctx.bezierCurveTo(14, 38, 6, 32, 6, 23); ctx.bezierCurveTo(6, 13, 13, 5, 24, 5); ctx.closePath();
    ctx.fill(); ctx.stroke();
    ctx.save(); ctx.globalCompositeOperation = 'destination-out';
    ctx.beginPath(); ctx.ellipse(24, 27, 6.6, 4.8, 0, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(17, 19, 1.6, 0, Math.PI * 2); ctx.arc(31, 19, 1.6, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
    ctx.beginPath(); ctx.ellipse(24, 27, 8, 6, 0, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(21, 24.5); ctx.lineTo(27, 24.5); ctx.lineTo(24, 27.5); ctx.closePath(); ctx.fill();
    ctx.restore();
  }
  function drawLabel(ctx, p, W, H, ink, paper) {
    ctx.fillStyle = paper;
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = ctx.fillStyle = ink;
    const cx = W / 2;
    // Fine double border across the whole wrap
    ctx.lineWidth = 3;
    ctx.strokeRect(14, 14, W - 28, H - 28);
    ctx.lineWidth = 1.5;
    ctx.strokeRect(26, 26, W - 52, H - 52);
    bearPath(ctx, cx - 44, 46, 88);
    ctx.textAlign = 'center';
    ctx.font = `800 ${p.label.length > 6 ? 72 : 84}px Outfit, sans-serif`;
    ctx.fillText(p.label, cx, 214);
    ctx.font = '500 26px Outfit, sans-serif';
    ctx.letterSpacing = '6px';
    ctx.fillText(`GLADNI MEDVED · ${p.sizes[0][0]}`, cx, 262);
    ctx.letterSpacing = '0px';
    // Side panels
    ctx.font = '700 24px Outfit, sans-serif';
    ctx.letterSpacing = '4px';
    ctx.fillText('SIROVI MED · ŠUMADIJA', cx - 560, 150);
    ctx.fillText('HLADNO VRCANO', cx + 560, 150);
    ctx.font = '500 20px Outfit, sans-serif';
    ctx.fillText('BEZ DODATAKA · BEZ PASTERIZACIJE', cx - 560, 190);
    ctx.fillText('ČUVATI NA SOBNOJ TEMPERATURI', cx + 560, 190);
    ctx.letterSpacing = '0px';
    ctx.lineWidth = 2;
    for (const x of [cx - 330, cx + 330]) { ctx.beginPath(); ctx.moveTo(x, 50); ctx.lineTo(x, H - 50); ctx.stroke(); }
    // Honeycomb row on the side panels
    for (const s of [-1, 1]) {
      for (let i = 0; i < 5; i++) {
        const hx = cx + s * 560 + (i - 2) * 40, hy = 240;
        ctx.beginPath();
        for (let k = 0; k < 6; k++) {
          const a = Math.PI / 3 * k + Math.PI / 6;
          ctx[k ? 'lineTo' : 'moveTo'](hx + 17 * Math.cos(a), hy + 17 * Math.sin(a));
        }
        ctx.closePath(); ctx.stroke();
      }
    }
  }
  function labelMat(p) {
    if (labelMats.has(p.id)) return labelMats.get(p.id);
    const W = 2048, H = 320;
    const mk = () => { const c = document.createElement('canvas'); c.width = W; c.height = H; return c; };
    const colorC = mk(), ormC = mk();
    drawLabel(colorC.getContext('2d'), p, W, H, C.gold, C.clove);
    // Paper: rough, non-metal. Foil: smooth, metallic.
    drawLabel(ormC.getContext('2d'), p, W, H, 'rgb(255,70,255)', 'rgb(255,215,0)');
    const map = new CanvasTexture(colorC);
    map.colorSpace = SRGBColorSpace;
    map.anisotropy = 8;
    const orm = new CanvasTexture(ormC);
    const m = new MeshStandardMaterial({ map, roughnessMap: orm, metalnessMap: orm, roughness: 1, metalness: 1, envMapIntensity: 1.6 });
    labelMats.set(p.id, m);
    return m;
  }

  // Lid top: gold foil bear on black metal
  const lidTopC = document.createElement('canvas');
  lidTopC.width = lidTopC.height = 512;
  {
    const ctx = lidTopC.getContext('2d');
    ctx.fillStyle = '#1a0c05';
    ctx.fillRect(0, 0, 512, 512);
    ctx.strokeStyle = ctx.fillStyle = C.gold;
    ctx.lineWidth = 6;
    ctx.beginPath(); ctx.arc(256, 256, 200, 0, Math.PI * 2); ctx.stroke();
    bearPath(ctx, 256 - 110, 256 - 100, 220);
  }
  const lidTopTex = new CanvasTexture(lidTopC);
  lidTopTex.colorSpace = SRGBColorSpace;
  const lidTopMat = new MeshStandardMaterial({ map: lidTopTex, metalness: 0.85, roughness: 0.28, envMapIntensity: 1.5 });

  // ---------- Jar assembly ----------
  const jar = new Group();
  const honey = new Mesh(honeyGeo, honeyMat(C.amber));
  const gIn = new Mesh(glassInnerGeo, glassInner);
  const gOut = new Mesh(glassOuterGeo, glassOuter);
  honey.renderOrder = 0; gIn.renderOrder = 2; gOut.renderOrder = 3;
  const label = new Mesh(labelGeo, labelMat(PRODUCTS[1]));
  label.position.y = 1.08;
  label.renderOrder = 1;

  const lid = new Group();
  const lidBody = new Mesh(lidGeo, lidMat);
  lidBody.position.y = 0.18;
  const lidTop = new Mesh(lidTopGeo, lidTopMat);
  lidTop.rotation.x = -Math.PI / 2;
  lidTop.position.y = 0.362;
  const lidRing = new Mesh(lidRingGeo, lidMat);
  lidRing.rotation.x = Math.PI / 2;
  lidRing.position.y = 0.36;
  lid.add(lidBody, lidTop, lidRing);
  const LID_Y = 2.27;
  const JAR_H = 2.78, JAR_W = 2.05, JAR_MID = 1.32;
  lid.position.y = LID_Y;

  const thread = new Mesh(threadGeo, honeyMat(C.amber));
  const drop = new Mesh(dropGeo, honeyMat(C.amber));
  jar.add(honey, label, gIn, gOut, lid, thread, drop);
  scene.add(jar);

  // Floating honey drops for the hero
  const floaters = new Group();
  const dropSpecs = [[-1.9, 2.3, 0.4, 0.14], [2.0, 1.5, -0.2, 0.11], [-1.6, 0.5, 0.6, 0.09], [1.7, 2.8, 0.3, 0.08], [1.55, 0.35, 0.8, 0.12]];
  for (const [x, y, z, s] of dropSpecs) {
    const d = new Mesh(dropGeo, honeyMat(C.amber));
    d.position.set(x, y, z);
    d.scale.set(s, s * 1.25, s);
    d.userData.base = [x, y, z];
    floaters.add(d);
  }
  scene.add(floaters);

  function setVariant(p) {
    honey.material = thread.material = drop.material = honeyMat(p.honey);
    label.material = labelMat(p);
  }

  // ---------- Views ----------
  const views = [];
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) e.target.__view.visible = e.isIntersecting;
  }, { rootMargin: '120px' });

  function addView(el) {
    if (el.__view) return;
    const canvas = document.createElement('canvas');
    canvas.className = 'jar-3d';
    canvas.setAttribute('aria-hidden', 'true');
    el.appendChild(canvas);
    const v = {
      el, canvas, ctx: canvas.getContext('2d'), visible: false,
      variant: byId(el.dataset.jar), mode: el.dataset.mode || 'idle',
      phase: Math.random() * Math.PI * 2, hover: 0, hoverT: 0, spin: 0, pointer: [0, 0],
    };
    el.__view = v;
    const card = el.closest('.product, .r-card, .tile');
    if (card) {
      card.addEventListener('pointerenter', () => { v.hoverT = 1; });
      card.addEventListener('pointerleave', () => { v.hoverT = 0; });
    }
    views.push(v);
    io.observe(el);
  }
  document.querySelectorAll('.jar[data-jar]').forEach((el) => {
    if (el.closest('.c-jar')) return; // cart thumbnails stay 2D
    addView(el);
  });

  let mouse = [0, 0];
  addEventListener('pointermove', (e) => {
    mouse = [e.clientX / innerWidth * 2 - 1, e.clientY / innerHeight * 2 - 1];
  }, { passive: true });

  // ---------- Frame ----------
  let maxW = 0, maxH = 0;
  function ensureSize(w, h) {
    if (w <= maxW && h <= maxH) return;
    maxW = Math.max(maxW, w);
    maxH = Math.max(maxH, h);
    renderer.setSize(maxW, maxH, false);
  }

  function pose(v, t, dt) {
    v.hover += (v.hoverT - v.hover) * Math.min(1, dt * 6);
    let rotY = 0, tilt = 0, lift = 0, bob = 0, showFloaters = false;
    const ext = v.el.j3d; // set by main.js for scroll-driven jars
    switch (v.mode) {
      case 'hero':
        rotY = reduce ? -0.35 : t * 0.35 + v.phase;
        bob = reduce ? 0 : Math.sin(t * 1.1) * 0.06;
        tilt = mouse[0] * -0.08;
        showFloaters = true;
        break;
      case 'journey':
        rotY = (ext?.spin ?? 0) * Math.PI * 2.2 - 0.4;
        lift = ext?.lid ?? 0;
        bob = reduce ? 0 : Math.sin(t * 1.3) * 0.04;
        break;
      default:
        v.spin += dt * (0.25 + v.hover * 2.2);
        rotY = reduce ? -0.35 : Math.sin(t * 0.5 + v.phase) * 0.45 + v.spin * (v.hover > 0.02 ? 1 : 0) - 0.2;
        bob = reduce ? 0 : Math.sin(t * 0.9 + v.phase) * 0.03;
        lift = v.mode === 'open' ? 0.55 : v.hover * 0.35;
    }
    jar.rotation.set(0, rotY, tilt);
    jar.position.y = bob;

    // Lid: unscrew (two turns) and rise, then tip back slightly
    const up = MathUtils.smoothstep(lift, 0, 1);
    lid.position.y = LID_Y + up * 0.9;
    lid.rotation.set(-up * 0.22, up * Math.PI * 2, up * 0.08);
    lid.position.z = up * -0.18;

    // Honey thread from the underside of the lid to the honey surface
    const gap = lid.position.y - 1.98;
    const on = up > 0.05;
    thread.visible = on && up < 0.97;
    drop.visible = on;
    if (on) {
      const thin = MathUtils.lerp(0.06, 0.012, Math.min(1, up * 1.15));
      thread.scale.set(thin, gap, thin);
      thread.position.set(0, 1.98 + gap / 2, lid.position.z / 2);
      const fall = (t * 0.7 + v.phase) % 1;
      drop.scale.set(0.05, 0.065, 0.05);
      drop.position.set(0, lid.position.y - 0.02 - fall * (gap - 0.05), lid.position.z * (1 - fall));
    }

    floaters.visible = showFloaters;
    if (showFloaters) {
      floaters.children.forEach((d, i) => {
        const [x, y, z] = d.userData.base;
        d.position.set(x + Math.sin(t * 0.6 + i) * 0.08, y + Math.sin(t * 0.9 + i * 2) * 0.12, z);
        d.rotation.z = Math.sin(t + i) * 0.2;
      });
    }
  }

  let last = performance.now();
  function frame(now) {
    const t = now / 1000;
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    for (const v of views) {
      if (!v.visible) continue;
      const r = v.canvas.getBoundingClientRect();
      if (r.width < 2 || r.height < 2) continue;
      const w = Math.round(r.width * DPR), h = Math.round(r.height * DPR);
      if (v.canvas.width !== w || v.canvas.height !== h) { v.canvas.width = w; v.canvas.height = h; }
      ensureSize(w, h);

      setVariant(v.variant);
      pose(v, t, dt);

      // Frame the jar so it fills the element's box (the canvas overhangs it for lid/rotation room)
      const aspect = w / h;
      camera.aspect = aspect;
      camera.updateProjectionMatrix();
      const tan = 2 * Math.tan(MathUtils.degToRad(camera.fov / 2));
      const boxW = v.el.offsetWidth || 1, boxH = v.el.offsetHeight || 1;
      const dist = Math.max(
        (JAR_H * (v.canvas.offsetHeight / boxH)) / tan,
        (JAR_W * (v.canvas.offsetWidth / boxW)) / (tan * aspect),
      );
      const px = v.mode === 'hero' ? mouse[0] * 0.6 : 0;
      const py = v.mode === 'hero' ? -mouse[1] * 0.4 : 0;
      camera.position.set(px, JAR_MID + dist * 0.14 + py, dist);
      camera.lookAt(0, JAR_MID, 0);

      renderer.setViewport(0, maxH - h, w, h);
      renderer.setScissor(0, maxH - h, w, h);
      renderer.setScissorTest(true);
      renderer.clear();
      renderer.render(scene, camera);
      v.ctx.clearRect(0, 0, w, h);
      v.ctx.drawImage(renderer.domElement, 0, 0, w, h, 0, 0, w, h);
      if (!v.ready) { v.ready = true; v.el.classList.add('is-3d'); }
    }
    requestAnimationFrame(frame);
  }

  // Wait for the label font so the foil text renders in Outfit
  (document.fonts?.load('800 80px Outfit') ?? Promise.resolve())
    .catch(() => {})
    .then(() => {
      labelMats.forEach((m) => { m.map.dispose(); });
      labelMats.clear();
      requestAnimationFrame(frame);
    });

  window.MED3D = { addView };
}
