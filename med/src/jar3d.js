// Real-time 3D honey jars for Gladni Medved.
// One WebGL renderer draws every visible jar and copies the frame into that jar's own 2D canvas,
// so the jars stay in normal page flow (text can sit on top, sections keep their backgrounds).
import {
  WebGLRenderer, Scene, PerspectiveCamera, Group, Mesh, Vector2, Vector3, SplineCurve, CatmullRomCurve3,
  QuadraticBezierCurve3, LatheGeometry, TubeGeometry, CylinderGeometry, CircleGeometry, SphereGeometry,
  TorusGeometry, PlaneGeometry, MeshPhysicalMaterial, MeshStandardMaterial, MeshBasicMaterial, ShaderMaterial,
  InstancedMesh, Object3D, CanvasTexture, Color, DirectionalLight, PMREMGenerator, NeutralToneMapping,
  SRGBColorSpace, RepeatWrapping, BackSide, FrontSide, DoubleSide, AdditiveBlending, MathUtils,
} from 'three';

const { PRODUCTS, byId, C } = window.MED;
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const DISPLAY = 'Telma, Sentient, Georgia, serif';
const UI = 'Sentient, Georgia, serif';

let renderer;
try {
  renderer = new WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
} catch {
  renderer = null;
}

if (renderer) start();

function start() {
  const MAX_Q = Math.min(devicePixelRatio || 1, 1.5);
  renderer.setPixelRatio(1);
  renderer.toneMapping = NeutralToneMapping;
  renderer.toneMappingExposure = 1;
  renderer.outputColorSpace = SRGBColorSpace;
  renderer.setClearColor(0x000000, 0);

  const scene = new Scene();
  const pmrem = new PMREMGenerator(renderer);

  // Product-photography studio for reflections: dark warm room, tall softboxes left and right,
  // a top light and a warm glow behind (that is what reads as "real glass" on a jar).
  {
    const studio = new Scene();
    studio.background = new Color(0x120804);
    const panel = (w, h, hex, power, x, y, z) => {
      const m = new Mesh(new PlaneGeometry(w, h), new MeshBasicMaterial({ color: new Color(hex).multiplyScalar(power), side: DoubleSide }));
      m.material.toneMapped = false;
      m.position.set(x, y, z);
      m.lookAt(0, 0, 0);
      studio.add(m);
    };
    panel(1.1, 9, 0xfff3e2, 5, -6, 1, 4);   // key softbox (narrow = crisp glass highlight)
    panel(0.6, 9, 0xffe4bd, 3.4, 6.5, 0.5, 2.5); // strip light
    panel(9, 2.4, 0xffeccc, 1.4, 0, 8, 1);  // top
    panel(7, 6, 0xff9f3d, 2.2, 1, 1, -7);   // warm back glow
    panel(16, 8, 0x823513, 0.5, 0, -7, 0);  // rust floor bounce
    scene.environment = pmrem.fromScene(studio, 0.02).texture;
  }

  const key = new DirectionalLight(0xfff1d6, 2.2);
  key.position.set(-4, 6, 6);
  const rim = new DirectionalLight(0xffb347, 5);
  rim.position.set(5, 3, -6);
  const fill = new DirectionalLight(0xffd59a, 0.8);
  fill.position.set(4, -1, 5);
  scene.add(key, rim, fill);

  const camera = new PerspectiveCamera(28, 1, 0.1, 60);

  // ---------- Profiles ----------
  const smooth = (pts, n) => new SplineCurve(pts.map(([x, y]) => new Vector2(x, y))).getPoints(n);

  // Outer glass (radius, height): a squat jar with rounded shoulder and short neck
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
  const rAt = (y) => {
    for (let i = 1; i < outer.length; i++) {
      const a = outer[i - 1], b = outer[i];
      if (a.y !== b.y && (y - a.y) * (y - b.y) <= 0) return a.x + (b.x - a.x) * (y - a.y) / (b.y - a.y);
    }
    return 1;
  };

  // ---------- Materials ----------
  // Glass adds only its reflections (black diffuse + additive blend), so the honey behind stays saturated
  const glassOuter = new MeshPhysicalMaterial({
    color: 0x000000, metalness: 0, roughness: 0.03, transparent: true, blending: AdditiveBlending,
    clearcoat: 1, clearcoatRoughness: 0.02, envMapIntensity: 1.25, side: FrontSide, depthWrite: false,
    specularIntensity: 1, ior: 1.5,
  });
  const glassInner = glassOuter.clone();
  glassInner.side = BackSide;
  glassInner.envMapIntensity = 0.7;
  glassInner.clearcoat = 0; // the far wall only needs a faint reflection; skip the second specular layer

  const lidMat = new MeshStandardMaterial({ color: 0x1a0c05, metalness: 0.75, roughness: 0.3, envMapIntensity: 1.4 });

  // Honey as seen in real product shots (cf. Busy Bee raw honey): a translucent liquid lit from behind.
  // Light passing straight through the middle reads pale gold, the long paths between centre and edge
  // turn deep orange-red, the thin rim glows peach, and a little of the background shows through.
  // Reflections still come from the physical material; the honey colour itself is computed here.
  const honeyMats = new Map();
  function honeyMat(hex, kind = 'body') {
    const id = hex + kind;
    if (honeyMats.has(id)) return honeyMats.get(id);
    const base = new Color(hex);
    const m = new MeshPhysicalMaterial({
      color: base.clone().multiplyScalar(0.06), roughness: 0.08, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.03,
      envMapIntensity: 0.55, transparent: true, specularIntensity: 0.8,
    });
    // Tone mapping desaturates bright red-orange towards coral; honey keeps its true colour instead
    m.toneMapped = false;
    const body = kind === 'body';
    const lum = base.r * 0.2126 + base.g * 0.7152 + base.b * 0.0722;
    m.customProgramCacheKey = () => 'honey-' + kind;
    m.onBeforeCompile = (sh) => {
      sh.uniforms.honeyCol = { value: base };
      sh.uniforms.clarity = { value: MathUtils.clamp(lum * 1.5, 0.1, 0.42) };
      sh.vertexShader = sh.vertexShader
        .replace('#include <common>', '#include <common>\nvarying vec3 vObj;')
        .replace('#include <begin_vertex>', '#include <begin_vertex>\nvObj = position;');
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <common>', `#include <common>
          varying vec3 vObj;
          uniform vec3 honeyCol;
          uniform float clarity;
          float hh(vec3 p) { return fract(sin(dot(p, vec3(12.9898, 78.233, 37.719))) * 43758.5453); }
          float vnoise(vec3 p) {
            vec3 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
            return mix(mix(mix(hh(i), hh(i + vec3(1,0,0)), f.x), mix(hh(i + vec3(0,1,0)), hh(i + vec3(1,1,0)), f.x), f.y),
                       mix(mix(hh(i + vec3(0,0,1)), hh(i + vec3(1,0,1)), f.x), mix(hh(i + vec3(0,1,1)), hh(i + vec3(1,1,1)), f.x), f.y), f.z);
          }`)
        .replace('#include <opaque_fragment>', `
          float facing = abs(dot(normalize(normal), normalize(vViewPosition)));
          float edgeGlow = pow(1.0 - facing, 4.0);
          vec3 glow = mix(honeyCol, vec3(1.0, 0.66, 0.06), 0.22 + clarity * 0.65) * mix(1.0, 1.25, clarity * 2.0); // light pooling
          vec3 dark = honeyCol * vec3(0.6, 0.2, 0.02);                             // deep red-orange body
          vec3 col;
          ${body ? `
          // Like real jars on a sunny table: the bottom glows yellow where light collects,
          // the honey turns deep red-orange towards the top, with bright refraction bands.
          float t = smoothstep(0.12, 1.95, vObj.y);
          col = mix(glow, honeyCol, smoothstep(0.0, 0.42, t));
          col = mix(col, dark, smoothstep(0.38, 1.0, t) * 0.7);
          float ang = atan(vObj.z, vObj.x);
          float bands = vnoise(vec3(ang * 5.0, vObj.y * 0.35, 0.0));
          col *= 0.78 + 0.5 * bands;
          col *= mix(0.82, 1.08, facing);
          col = mix(col, glow, edgeGlow * 0.4 * (1.0 - t));
          // the back of the label seen through the honey
          float band = smoothstep(0.56, 0.64, vObj.y) * (1.0 - smoothstep(1.52, 1.6, vObj.y));
          col *= 1.0 - 0.38 * band * pow(facing, 1.5);` : `
          col = mix(honeyCol, glow, 0.35 + 0.3 * facing);
          col *= 0.95 + 0.1 * vnoise(vObj * 6.0);`}
          #ifdef ENVMAP_TYPE_CUBE_UV
            // the studio lights refracted through the liquid, tinted by it
            vec3 inc = normalize(-vViewPosition);
            vec3 refr = inverseTransformDirection(refract(-inc, normal, 0.67), viewMatrix);
            col += textureCubeUV(envMap, envMapRotation * refr, 0.1).rgb * honeyCol * honeyCol * 0.35;
          #endif
          float lumC = dot(col, vec3(0.2126, 0.7152, 0.0722));
          col = max(mix(vec3(lumC), col, 1.3), 0.0);
          outgoingLight = outgoingLight * 0.8 + col * 0.82;
          diffuseColor.a = ${body ? 'mix(0.96, 0.78, edgeGlow)' : 'mix(0.9, 0.68, edgeGlow)'};
          #include <opaque_fragment>`);
    };
    honeyMats.set(id, m);
    return m;
  }

  // ---------- Label: dark paper + gold foil (B channel = metal, G = roughness) ----------
  // Brand mark (same paths as the #logo symbol in index.html): a bear in a honeycomb cell, 64-unit box
  const LOGO_HEX = new Path2D('M32 3l25 14.5v29L32 61 7 46.5v-29z');
  const LOGO_BEAR = new Path2D('M14.5 22a6.5 6.5 0 1 0 13 0a6.5 6.5 0 1 0-13 0ZM36.5 22a6.5 6.5 0 1 0 13 0a6.5 6.5 0 1 0-13 0ZM16.5 36a15.5 14 0 1 0 31 0a15.5 14 0 1 0-31 0ZM18 22a3 3 0 1 1 6 0a3 3 0 1 1-6 0ZM40 22a3 3 0 1 1 6 0a3 3 0 1 1-6 0ZM24 33a2 2 0 1 1 4 0a2 2 0 1 1-4 0ZM36 33a2 2 0 1 1 4 0a2 2 0 1 1-4 0ZM24.5 41.5a7.5 6 0 1 1 15 0a7.5 6 0 1 1-15 0ZM28.8 38.8Q32 37.2 35.2 38.8Q33.8 42.2 32 42.6Q30.2 42.2 28.8 38.8Z');
  function logoMark(ctx, x, y, s) {
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(s / 64, s / 64);
    ctx.lineWidth = 3;
    ctx.lineJoin = 'round';
    ctx.stroke(LOGO_HEX);
    ctx.translate(9, 7);
    ctx.scale(46 / 64, 46 / 64);
    ctx.fill(LOGO_BEAR);
    ctx.restore();
  }
  function hexRow(ctx, cx, y) {
    for (let i = 0; i < 5; i++) {
      const hx = cx + (i - 2) * 40;
      ctx.beginPath();
      for (let k = 0; k < 6; k++) {
        const a = Math.PI / 3 * k + Math.PI / 6;
        ctx[k ? 'lineTo' : 'moveTo'](hx + 17 * Math.cos(a), y + 17 * Math.sin(a));
      }
      ctx.closePath(); ctx.stroke();
    }
  }
  function drawLabel(ctx, p, W, H, ink, paper) {
    ctx.fillStyle = paper;
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = ctx.fillStyle = ink;
    const cx = W / 2;
    ctx.lineWidth = 3;
    ctx.strokeRect(14, 14, W - 28, H - 28);
    ctx.lineWidth = 1.5;
    ctx.strokeRect(26, 26, W - 52, H - 52);
    logoMark(ctx, cx - 38, 26, 76);
    ctx.textAlign = 'center';
    ctx.font = `700 ${p.label.length > 6 ? 82 : 92}px ${DISPLAY}`;
    ctx.letterSpacing = '0px';
    ctx.fillText(p.id === 'sace' ? 'Saće' : p.name.split(' ')[0], cx, 178);
    ctx.font = `500 40px ${DISPLAY}`;
    ctx.letterSpacing = '0px';
    ctx.fillText(p.id === 'sace' ? 'med u saću' : 'sirovi med', cx, 228);
    ctx.font = `700 21px ${UI}`;
    ctx.letterSpacing = '6px';
    ctx.fillText(`GLADNI MEDVED · ${p.sizes[0][0].toUpperCase()}`, cx, 276);
    // Side panels
    ctx.font = `700 23px ${UI}`;
    ctx.letterSpacing = '4px';
    ctx.fillText('ŠUMADIJA · SRBIJA', cx - 560, 140);
    ctx.fillText('HLADNO VRCANO', cx + 560, 140);
    ctx.font = `500 34px ${DISPLAY}`;
    ctx.letterSpacing = '0px';
    ctx.fillText('bez dodataka', cx - 560, 188);
    ctx.fillText('iz naših košnica', cx + 560, 188);
    ctx.lineWidth = 2;
    for (const x of [cx - 330, cx + 330]) { ctx.beginPath(); ctx.moveTo(x, 50); ctx.lineTo(x, H - 50); ctx.stroke(); }
    hexRow(ctx, cx - 560, 242);
    hexRow(ctx, cx + 560, 242);
  }
  const labelMats = new Map();
  function labelMat(p) {
    if (labelMats.has(p.id)) return labelMats.get(p.id);
    const W = 2048, H = 320;
    const mk = () => { const c = document.createElement('canvas'); c.width = W; c.height = H; return c; };
    const colorC = mk(), ormC = mk();
    drawLabel(colorC.getContext('2d'), p, W, H, C.gold, C.clove);
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
    ctx.beginPath(); ctx.arc(256, 256, 214, 0, Math.PI * 2); ctx.stroke();
    logoMark(ctx, 256 - 165, 256 - 165, 330);
  }
  const lidTopTex = new CanvasTexture(lidTopC);
  lidTopTex.colorSpace = SRGBColorSpace;
  const lidTopMat = new MeshStandardMaterial({ map: lidTopTex, metalness: 0.85, roughness: 0.28, envMapIntensity: 1.5 });

  // Wood for the honey dipper
  const woodC = document.createElement('canvas');
  woodC.width = 256; woodC.height = 512;
  {
    const ctx = woodC.getContext('2d');
    const g = ctx.createLinearGradient(0, 0, 256, 0);
    g.addColorStop(0, '#b77a43'); g.addColorStop(0.5, '#d29a5e'); g.addColorStop(1, '#b07040');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 256, 512);
    for (let i = 0; i < 70; i++) {
      ctx.strokeStyle = `rgba(110, 58, 24, ${0.08 + Math.random() * 0.22})`;
      ctx.lineWidth = 0.6 + Math.random() * 2.2;
      const x = Math.random() * 256;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      for (let y = 0; y <= 512; y += 32) ctx.lineTo(x + Math.sin(y / 70 + i) * 5, y);
      ctx.stroke();
    }
  }
  const woodTex = new CanvasTexture(woodC);
  woodTex.colorSpace = SRGBColorSpace;
  woodTex.wrapS = woodTex.wrapT = RepeatWrapping;
  const woodMat = new MeshStandardMaterial({ map: woodTex, roughness: 0.55, metalness: 0, envMapIntensity: 0.9 });

  // ---------- Geometry ----------
  const glassOuterGeo = new LatheGeometry(outer, 80);
  const glassInnerGeo = new LatheGeometry(inner, 72);
  const honeyGeo = new LatheGeometry(honeyProfile, 64);

  const lidGeo = new CylinderGeometry(0.79, 0.79, 0.36, 240, 2);
  {
    const p = lidGeo.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i), z = p.getZ(i);
      if (Math.hypot(x, z) < 0.785) continue;
      const k = 1 + 0.012 * Math.pow(Math.abs(Math.sin(Math.atan2(z, x) * 60)), 0.6);
      p.setX(i, x * k);
      p.setZ(i, z * k);
    }
    lidGeo.computeVertexNormals();
  }

  const LABEL_ARC = Math.PI * 2 * 0.86;
  const labelGeo = new CylinderGeometry(1.012, 1.012, 0.98, 96, 1, true, -LABEL_ARC / 2, LABEL_ARC);
  const dropGeo = new SphereGeometry(1, 24, 16);

  // Tapered tube helper: radius goes from r0 to r1 along the curve, or follows r0(t) when it is a function
  function taperTube(curve, segs, r0, r1, radial = 10) {
    const rad = typeof r0 === 'function' ? r0 : (t) => MathUtils.lerp(r0, r1, t);
    const g = new TubeGeometry(curve, segs, 1, radial, false);
    const pos = g.attributes.position;
    const v = new Vector3();
    for (let i = 0; i <= segs; i++) {
      const c = curve.getPointAt(i / segs);
      const r = rad(i / segs);
      for (let j = 0; j <= radial; j++) {
        const k = i * (radial + 1) + j;
        v.fromBufferAttribute(pos, k).sub(c).multiplyScalar(r).add(c);
        pos.setXYZ(k, v.x, v.y, v.z);
      }
    }
    g.computeVertexNormals();
    return g;
  }

  // Honey running down the outside of the jar from under the lid
  // Honey that seeped out from under the lid and ran down the shoulder: wide where it leaves the lid,
  // thinning as it runs, then gathering into a heavy drop.
  const DRIPS = [[0.62, 1.52, 1], [1.95, 1.2, 0.9], [3.05, 1.78, 0.8], [-1.55, 1.36, 1.1], [-0.35, 2.0, 0.75]];
  const dripRadius = (t) => 0.024 + 0.05 * Math.pow(1 - t, 3) + 0.012 * MathUtils.smoothstep(t, 0.75, 1);
  function dripMeshes(mat) {
    const g = new Group();
    for (const [theta, yEnd, w] of DRIPS) {
      const pts = [];
      for (let k = 0; k <= 30; k++) {
        const y = 2.27 - (2.27 - yEnd) * k / 30;
        const r = rAt(y) + 0.03;
        pts.push(new Vector3(Math.sin(theta) * r, y, Math.cos(theta) * r));
      }
      const curve = new CatmullRomCurve3(pts);
      g.add(new Mesh(taperTube(curve, 60, (t) => dripRadius(t) * w), mat));
      const end = curve.getPointAt(1);
      const bulb = new Mesh(dropGeo, mat);
      bulb.position.set(end.x * 1.012, end.y - 0.04, end.z * 1.012);
      bulb.scale.set(0.05 * w, 0.072 * w, 0.05 * w);
      g.add(bulb);
    }
    return g;
  }

  // ---------- Assembly ----------
  const jar = new Group();   // whole object (tilt, bob)
  const body = new Group();  // turns around its axis
  const honey = new Mesh(honeyGeo, honeyMat(C.amber));
  const gIn = new Mesh(glassInnerGeo, glassInner);
  const gOut = new Mesh(glassOuterGeo, glassOuter);
  const label = new Mesh(labelGeo, labelMat(PRODUCTS[1]));
  label.position.y = 1.08;
  label.renderOrder = 1;
  let drips = dripMeshes(honeyMat(C.amber, 'stream'));

  // Glass thickness: the silhouette of a real jar goes dark where you look through the wall edge-on
  const edge = new Mesh(glassOuterGeo, new ShaderMaterial({
    transparent: true, depthWrite: false,
    uniforms: { tint: { value: new Color(0x120602) }, strength: { value: 0.6 } },
    vertexShader: `varying vec3 vN; varying vec3 vV;
      void main() { vec4 mv = modelViewMatrix * vec4(position, 1.0); vN = normalize(normalMatrix * normal); vV = -mv.xyz; gl_Position = projectionMatrix * mv; }`,
    fragmentShader: `uniform vec3 tint; uniform float strength; varying vec3 vN; varying vec3 vV;
      void main() { float f = 1.0 - abs(dot(normalize(vN), normalize(vV))); gl_FragColor = vec4(tint, pow(f, 2.2) * strength); }`,
  }));
  edge.renderOrder = 2;
  gIn.renderOrder = 3; gOut.renderOrder = 4;

  // Air bubbles trapped against the glass, mostly near the top of the honey
  const BUBBLES = 70;
  const bubbles = new InstancedMesh(new SphereGeometry(1, 12, 8), new MeshPhysicalMaterial({
    color: 0xfff1c9, roughness: 0.05, transparent: true, opacity: 0.55, clearcoat: 1, envMapIntensity: 2, emissive: 0x6b3a08,
  }), BUBBLES);
  {
    const o = new Object3D();
    let seed = 7;
    const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
    for (let i = 0; i < BUBBLES; i++) {
      const a = rnd() * Math.PI * 2;
      const top = rnd() < 0.75;
      const y = top ? 1.6 + rnd() * 0.36 : 0.22 + rnd() * 0.32;
      const r = rAt(y) - 0.047;
      o.position.set(Math.sin(a) * r, y, Math.cos(a) * r);
      o.scale.setScalar(0.006 + Math.pow(rnd(), 3) * 0.022);
      o.updateMatrix();
      bubbles.setMatrixAt(i, o.matrix);
    }
  }
  bubbles.renderOrder = 1;

  body.add(honey, bubbles, label, edge, gIn, gOut, drips);

  // Soft contact shadow for jars that stand on something (shop, tiles)
  const shC = document.createElement('canvas');
  shC.width = shC.height = 256;
  {
    const ctx = shC.getContext('2d');
    const g = ctx.createRadialGradient(128, 128, 10, 128, 128, 128);
    g.addColorStop(0, 'rgba(0,0,0,0.75)');
    g.addColorStop(0.45, 'rgba(0,0,0,0.35)');
    g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 256, 256);
  }
  const shadow = new Mesh(new PlaneGeometry(3.4, 3.4), new MeshBasicMaterial({
    map: new CanvasTexture(shC), transparent: true, depthWrite: false, color: 0x1a0802,
  }));
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.y = 0.002;
  shadow.scale.set(1, 0.62, 1);
  shadow.renderOrder = -1;

  const lid = new Group();
  const lidBody = new Mesh(lidGeo, lidMat);
  lidBody.position.y = 0.18;
  const lidTop = new Mesh(new CircleGeometry(0.62, 96), lidTopMat);
  lidTop.rotation.x = -Math.PI / 2;
  lidTop.position.y = 0.362;
  const lidRing = new Mesh(new TorusGeometry(0.7, 0.035, 12, 120), lidMat);
  lidRing.rotation.x = Math.PI / 2;
  lidRing.position.y = 0.36;
  lid.add(lidBody, lidTop, lidRing);
  const LID_Y = 2.27;

  // Honey thread between lid and jar when the lid lifts
  const thread = new Mesh(new CylinderGeometry(1, 1, 1, 20, 8, true), honeyMat(C.amber, 'stream'));
  const drop = new Mesh(dropGeo, honeyMat(C.amber, 'stream'));

  // Honey dipper (hero): grooved wooden head, honey-coated, pouring a ribbon into the open jar
  const dipper = new Group();
  const headProfile = [[0.001, -0.02], [0.12, 0], [0.19, 0.04]];
  for (let k = 0; k < 6; k++) {
    const y = 0.08 + k * 0.075;
    headProfile.push([0.2, y], [0.155, y + 0.03], [0.2, y + 0.06]);
  }
  headProfile.push([0.13, 0.56], [0.06, 0.6], [0.05, 0.64]);
  const head = new Mesh(new LatheGeometry(headProfile.map(([x, y]) => new Vector2(x, y)), 48), woodMat);
  const handle = new Mesh(new CylinderGeometry(0.045, 0.06, 2.1, 24), woodMat);
  handle.position.y = 0.64 + 1.05;
  const coat = new Mesh(new LatheGeometry(smooth([
    [0.001, -0.2], [0.04, -0.16], [0.11, -0.05], [0.215, 0.06], [0.225, 0.18], [0.212, 0.3], [0.16, 0.34], [0.001, 0.345],
  ], 40), 48), honeyMat(C.amber, 'stream'));
  dipper.add(head, handle, coat);
  dipper.position.set(0.62, 3.3, 0.18);
  dipper.rotation.z = -0.62;

  let streamGeo = null;
  const stream = new Mesh(new SphereGeometry(1, 4, 2), honeyMat(C.amber, 'stream'));
  const pool = new Mesh(new TorusGeometry(0.08, 0.035, 10, 32), honeyMat(C.amber, 'stream'));
  pool.rotation.x = Math.PI / 2;
  const streamDrop = new Mesh(dropGeo, honeyMat(C.amber, 'stream'));

  jar.add(body, lid, thread, drop, dipper, stream, pool, streamDrop);
  scene.add(shadow);
  scene.add(jar);

  let current = null;
  function setVariant(p) {
    if (current === p.id) return;
    current = p.id;
    honey.material = honeyMat(p.honey);
    const s = honeyMat(p.honey, 'stream');
    thread.material = drop.material = coat.material = stream.material = pool.material = streamDrop.material = s;
    drips.traverse((o) => { if (o.isMesh) o.material = s; });
    label.material = labelMat(p);
  }

  const tmp = new Vector3();
  function updateStream(t) {
    // From the bottom of the coated dipper head to the honey surface, swaying slightly
    jar.updateMatrixWorld(true);
    const start = dipper.localToWorld(tmp.set(0, -0.19, 0)).clone();
    jar.worldToLocal(start);
    const end = new Vector3(0.06 + Math.sin(t * 1.3) * 0.03, 2.0, 0.08);
    const ctrl = new Vector3(start.x * 0.4, (start.y + end.y) / 2 + 0.15, start.z * 0.6);
    streamCurve = new QuadraticBezierCurve3(start, ctrl, end);
    streamGeo?.dispose();
    streamGeo = taperTube(streamCurve, 32, 0.034, 0.016, 8);
    streamGeo.userData.built = true;
    stream.geometry = streamGeo;
    pool.position.set(end.x, 2.01, end.z);
  }
  let streamCurve = null;
  // Cheap per-frame part: the pool breathes and a drop slides down the (cached) ribbon
  function animateStream(t) {
    pool.scale.setScalar(1 + Math.sin(t * 2) * 0.06);
    if (!streamCurve) return;
    streamDrop.position.copy(streamCurve.getPointAt((t * 0.55) % 1));
    streamDrop.scale.set(0.04, 0.055, 0.04);
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
      phase: Math.random() * Math.PI * 2, hover: 0, hoverT: 0, spin: 0,
      grounded: !!el.closest('.product, .tile'),
      slot: views.length % 3,
    };
    el.__view = v;
    const card = el.closest('.product, .tile');
    if (card) {
      card.addEventListener('pointerenter', () => { v.hoverT = 1; });
      card.addEventListener('pointerleave', () => { v.hoverT = 0; });
    }
    views.push(v);
    io.observe(el);
  }

  let mouse = [0, 0];
  addEventListener('pointermove', (e) => {
    mouse = [e.clientX / innerWidth * 2 - 1, e.clientY / innerHeight * 2 - 1];
  }, { passive: true });

  function pose(v, t, dt) {
    v.hover += (v.hoverT - v.hover) * Math.min(1, dt * 6);
    let rotY = 0, tilt = 0, lift = 0, bob = 0;
    const hero = v.mode === 'hero';
    const ext = v.el.j3d; // set by main.js for the scroll-driven jar
    switch (v.mode) {
      case 'hero':
        rotY = reduce ? -0.4 : t * 0.3 + v.phase;
        bob = reduce ? 0 : Math.sin(t * 1.1) * 0.05;
        tilt = mouse[0] * -0.06;
        break;
      case 'journey':
        rotY = (ext?.spin ?? 0) * Math.PI * 2.2 - 0.4;
        lift = ext?.lid ?? 0;
        bob = reduce ? 0 : Math.sin(t * 1.3) * 0.04;
        break;
      default:
        v.spin += dt * (0.25 + v.hover * 2.2);
        rotY = reduce ? -0.4 : Math.sin(t * 0.5 + v.phase) * 0.45 + v.spin * (v.hover > 0.02 ? 1 : 0) - 0.2;
        bob = reduce ? 0 : Math.sin(t * 0.9 + v.phase) * 0.03;
        lift = v.mode === 'open' ? 0.55 : v.hover * 0.35;
    }
    jar.rotation.set(0, 0, tilt);
    jar.position.y = v.grounded ? 0 : bob;
    shadow.visible = v.grounded;
    body.rotation.y = rotY;

    dipper.visible = stream.visible = pool.visible = streamDrop.visible = hero;
    if (hero) {
      // Lid set aside, floating up-left; the dipper pours into the open jar
      lid.position.set(-1.72, 1.15 + Math.sin(t * 0.9) * 0.06, 0.35);
      lid.rotation.set(1.1, rotY * 0.5, -0.3 + Math.sin(t * 0.7) * 0.05);
      dipper.rotation.z = -0.62 + (reduce ? 0 : Math.sin(t * 0.8) * 0.035);
      if (!stream.geometry.userData.built || frameNo % 3 === 0) updateStream(reduce ? 0 : t);
      animateStream(reduce ? 0 : t);
      thread.visible = drop.visible = false;
      return;
    }

    // Lid: unscrew (two turns) and rise, then tip back slightly
    const up = MathUtils.smoothstep(lift, 0, 1);
    lid.position.set(0, LID_Y + up * 0.9, up * -0.18);
    lid.rotation.set(-up * 0.22, rotY + up * Math.PI * 2, up * 0.08);

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
  }

  // ---------- Frame ----------
  const JAR_H = 2.8, JAR_W = 2.05;
  let maxW = 0, maxH = 0;
  function ensureSize(w, h) {
    if (w <= maxW && h <= maxH) return;
    maxW = Math.max(maxW, w);
    maxH = Math.max(maxH, h);
    renderer.setSize(maxW, maxH, false);
  }

  // Adaptive resolution: if the 3D work per frame gets expensive, render fewer pixels (and back up when idle).
  let quality = MAX_Q;
  let cost = 0, lastTune = 0, frameNo = 0;
  function tune(now, spent) {
    cost = cost * 0.85 + spent * 0.15;
    if (now - lastTune < 500) return;
    lastTune = now;
    if (cost > 10 && quality > 0.5) quality = Math.max(0.5, quality * 0.8);
    else if (cost < 4 && quality < MAX_Q) quality = Math.min(MAX_Q, quality * 1.08);
  }
  // While the page is being scrolled quickly, background jars hold their last frame
  let lastScrollY = scrollY, scrollSpeed = 0;
  addEventListener('scroll', () => {
    scrollSpeed = Math.max(scrollSpeed, Math.abs(scrollY - lastScrollY));
    lastScrollY = scrollY;
  }, { passive: true });

  let last = performance.now();
  function frame(now) {
    const t = now / 1000;
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    frameNo++;
    const start = performance.now();
    const fastScroll = scrollSpeed > 40;
    scrollSpeed *= 0.6;
    for (const v of views) {
      if (!v.visible) continue;
      // Jars that only sway (shop, tiles, panels) are drawn every third frame and freeze during fast
      // scrolling; the hero, the scroll-driven jar and any jar under the pointer stay at full rate.
      const busy = v.mode === 'hero' || v.mode === 'journey' || v.hoverT > 0 || v.hover > 0.02;
      if (!busy && v.ready && (fastScroll || (frameNo + v.slot) % 3)) continue;
      if (reduce && v.ready && v.drawnQ === quality) continue;
      const cw = v.canvas.offsetWidth, ch = v.canvas.offsetHeight;
      if (cw < 2 || ch < 2) continue;
      const w = Math.round(cw * quality), h = Math.round(ch * quality);
      if (v.canvas.width !== w || v.canvas.height !== h) { v.canvas.width = w; v.canvas.height = h; }
      ensureSize(w, h);
      v.drawnQ = quality;

      setVariant(v.variant);
      pose(v, t, dt);

      // The element's box holds the jar exactly; the canvas may overhang it on any side,
      // so aim the camera at the canvas centre expressed in jar units.
      const boxW = v.el.offsetWidth || 1, boxH = v.el.offsetHeight || 1;
      const ppu = Math.min(boxH / JAR_H, boxW / JAR_W);
      const tx = (v.canvas.offsetLeft + cw / 2 - boxW / 2) / ppu;
      const ty = JAR_H / 2 - (v.canvas.offsetTop + ch / 2 - boxH / 2) / ppu;
      camera.aspect = cw / ch;
      camera.updateProjectionMatrix();
      const dist = (ch / ppu) / (2 * Math.tan(MathUtils.degToRad(camera.fov / 2)));
      const hero = v.mode === 'hero';
      const px = hero ? mouse[0] * 0.5 : 0;
      const py = hero ? -mouse[1] * 0.35 : 0;
      camera.position.set(tx + px, ty + dist * 0.12 + py, dist);
      camera.lookAt(tx, ty, 0);

      renderer.setViewport(0, maxH - h, w, h);
      renderer.setScissor(0, maxH - h, w, h);
      renderer.setScissorTest(true);
      renderer.clear();
      renderer.render(scene, camera);
      v.ctx.clearRect(0, 0, w, h);
      v.ctx.drawImage(renderer.domElement, 0, 0, w, h, 0, 0, w, h);
      if (!v.ready) { v.ready = true; v.el.classList.add('is-3d'); }
    }
    tune(now, performance.now() - start);
    requestAnimationFrame(frame);
  }

  // Wait for the label fonts so the foil text renders in Telma / Sentient
  const fonts = document.fonts
    ? Promise.all([`700 92px Telma`, `500 40px Telma`, `700 21px Sentient`].map((f) => document.fonts.load(f)))
    : Promise.resolve();
  fonts.catch(() => {}).then(() => {
    labelMats.forEach((m) => m.map.dispose());
    labelMats.clear();
    current = null;
    document.querySelectorAll('.jar[data-jar]').forEach((el) => {
      if (!el.closest('.c-jar')) addView(el); // cart thumbnails stay 2D
    });
    requestAnimationFrame(frame);
  });
}
