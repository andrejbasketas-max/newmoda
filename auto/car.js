/* Parametric side-profile car illustration. carSVG({ body, color, id }) returns an SVG string.
   Used as a stand-in until real photos are added to a listing (see `photo` in main.js). */
(() => {
  const W = 480, GROUND = 172;

  /* Silhouettes: x positions run nose (left) → tail (right); y grows downward. */
  const BODIES = {
    sedan: { nose: 22, tail: 458, hood: 98, ws: 176, roofA: 244, roofB: 322, rear: 400, deck: 90, roof: 50, bottom: 146, fw: 108, rw: 372, r: 31, glassEnd: 392 },
    coupe: { nose: 20, tail: 460, hood: 102, ws: 186, roofA: 256, roofB: 300, rear: 424, deck: 96, roof: 56, bottom: 148, fw: 108, rw: 374, r: 31, glassEnd: 380 },
    hatch: { nose: 46, tail: 432, hood: 96, ws: 170, roofA: 236, roofB: 368, rear: 422, deck: 74, roof: 46, bottom: 146, fw: 118, rw: 356, r: 31, glassEnd: 386 },
    wagon: { nose: 22, tail: 458, hood: 98, ws: 176, roofA: 244, roofB: 410, rear: 450, deck: 76, roof: 50, bottom: 146, fw: 108, rw: 372, r: 31, glassEnd: 420 },
    suv:   { nose: 26, tail: 456, hood: 84, ws: 168, roofA: 232, roofB: 400, rear: 448, deck: 64, roof: 30, bottom: 136, fw: 112, rw: 370, r: 36, glassEnd: 414 },
  };

  const hex = (h) => h.replace('#', '').match(/../g).map((x) => parseInt(x, 16));
  const mix = (a, b, t) => '#' + hex(a).map((v, i) => Math.round(v + (hex(b)[i] - v) * t).toString(16).padStart(2, '0')).join('');

  function shell(b) {
    const { nose: n, tail: t, hood: h, ws, roofA, roofB, rear, deck, roof, bottom: y, fw, rw, r } = b;
    const belt = h - 8, arch = r + 9;
    return [
      `M${n + 10},${y}`,
      `C${n + 1},${y - 2} ${n - 2},${h + 26} ${n + 3},${h + 13}`,
      `C${n + 7},${h + 4} ${n + 22},${h} ${n + 44},${h - 2}`,
      `L${ws},${belt}`,
      `C${ws + (roofA - ws) * 0.4},${belt - 10} ${roofA - 22},${roof + 2} ${roofA},${roof}`,
      `C${(roofA + roofB) / 2},${roof - 3} ${(roofA + roofB) / 2},${roof - 3} ${roofB},${roof}`,
      `C${roofB + (rear - roofB) * 0.5},${roof + 3} ${rear - 12},${deck - 10} ${rear},${deck}`,
      `L${t - 12},${deck + 2}`,
      `C${t - 3},${deck + 4} ${t},${deck + 12} ${t},${deck + 26}`,
      `L${t - 1},${y - 12}`,
      `C${t - 2},${y - 3} ${t - 8},${y} ${t - 18},${y}`,
      `L${rw + arch},${y}`,
      `A${arch},${arch} 0 0 0 ${rw - arch},${y}`,
      `L${fw + arch},${y}`,
      `A${arch},${arch} 0 0 0 ${fw - arch},${y}`,
      'Z',
    ].join(' ');
  }

  function glass(b) {
    const { hood: h, ws, roofA, roofB, roof, glassEnd: g, deck } = b;
    const belt = h - 10, top = roof + 7, end = Math.min(belt, deck + 2);
    return [
      `M${ws + 16},${belt}`,
      `C${ws + (roofA - ws) * 0.5},${belt - 12} ${roofA - 16},${top + 1} ${roofA + 2},${top}`,
      `L${roofB - 6},${top}`,
      `C${roofB + (g - roofB) * 0.5},${top + 2} ${g - 6},${end - 8} ${g},${end}`,
      'Z',
    ].join(' ');
  }

  function wheel(cx, cy, r, id) {
    const spokes = Array.from({ length: 5 }, (_, i) =>
      `<path d="M${cx - 2.6},${cy - 5} L${cx - 4.2},${cy - r * 0.62} L${cx + 4.2},${cy - r * 0.62} L${cx + 2.6},${cy - 5} Z" transform="rotate(${i * 72} ${cx} ${cy})"/>`).join('');
    return `<g class="wheel" style="transform-origin:${cx}px ${cy}px">
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="#0c0d10"/>
      <circle cx="${cx}" cy="${cy}" r="${r - 3}" fill="none" stroke="#1d2027" stroke-width="2"/>
      <circle cx="${cx}" cy="${cy}" r="${r * 0.68}" fill="url(#rim-${id})"/>
      <g fill="#2a2e36">${spokes}</g>
      <circle cx="${cx}" cy="${cy}" r="${r * 0.68}" fill="none" stroke="#c9ced6" stroke-opacity=".5"/>
      <circle cx="${cx}" cy="${cy}" r="4.5" fill="#c9ced6"/>
    </g>`;
  }

  window.carSVG = ({ body = 'sedan', color = '#c8102e', id = Math.random().toString(36).slice(2, 8) } = {}) => {
    const b = BODIES[body] || BODIES.sedan;
    const cy = GROUND - b.r, belt = b.hood - 8;
    const light = mix(color, '#ffffff', 0.38), dark = mix(color, '#000000', 0.55);
    return `<svg viewBox="0 0 ${W} 190" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
  <defs>
    <linearGradient id="paint-${id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="${light}"/><stop offset=".34" stop-color="${color}"/><stop offset=".62" stop-color="${mix(color, '#000000', 0.18)}"/><stop offset="1" stop-color="${dark}"/>
    </linearGradient>
    <linearGradient id="glass-${id}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#3a4250"/><stop offset=".55" stop-color="#151920"/><stop offset="1" stop-color="#0b0d12"/>
    </linearGradient>
    <radialGradient id="rim-${id}"><stop offset="0" stop-color="#e8ebf0"/><stop offset=".7" stop-color="#9aa1ad"/><stop offset="1" stop-color="#5b616c"/></radialGradient>
    <radialGradient id="shadow-${id}"><stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
  </defs>
  <ellipse cx="${(b.nose + b.tail) / 2}" cy="${GROUND + 2}" rx="${(b.tail - b.nose) / 2 + 14}" ry="11" fill="url(#shadow-${id})"/>
  ${[b.fw, b.rw].map((x) => `<path d="M${x - b.r - 10},${b.bottom + 1} A${b.r + 10},${b.r + 10} 0 0 1 ${x + b.r + 10},${b.bottom + 1} Z" fill="#07080a"/>`).join('')}
  <path d="${shell(b)}" fill="url(#paint-${id})"/>
  <path d="M${b.fw + b.r + 10},${b.bottom - 7} L${b.rw - b.r - 10},${b.bottom - 7} L${b.rw - b.r - 10},${b.bottom} L${b.fw + b.r + 10},${b.bottom} Z" fill="#000" fill-opacity=".28"/>
  <path d="M${b.nose + 6},${b.bottom - 12} L${b.nose + 34},${b.bottom - 12}" stroke="#000" stroke-opacity=".45" stroke-width="5" stroke-linecap="round"/>
  <path d="${glass(b)}" fill="url(#glass-${id})"/>
  <path d="M${b.roofA + 26},${b.roof + 10} L${b.roofA + 60},${b.roof + 10}" stroke="#fff" stroke-opacity=".18" stroke-width="3" stroke-linecap="round"/>
  <path d="M${b.nose + 34},${belt + 14} C${b.nose + 140},${belt + 6} ${b.tail - 140},${belt + 2} ${b.tail - 8},${b.deck + 18}" fill="none" stroke="#fff" stroke-opacity=".28" stroke-width="1.6"/>
  <path d="M${b.nose + 30},${b.bottom - 16} L${b.tail - 30},${b.bottom - 16}" stroke="#000" stroke-opacity=".22" stroke-width="2"/>
  <path d="M${(b.ws + b.glassEnd) / 2 - 4},${belt - 2} L${(b.ws + b.glassEnd) / 2 - 2},${b.bottom - 6}" stroke="#000" stroke-opacity=".3" stroke-width="1.4"/>
  <rect x="${(b.ws + b.glassEnd) / 2 - 34}" y="${belt + 10}" width="16" height="3.5" rx="1.75" fill="#000" fill-opacity=".35"/>
  <rect x="${(b.ws + b.glassEnd) / 2 + 30}" y="${belt + 10}" width="16" height="3.5" rx="1.75" fill="#000" fill-opacity=".35"/>
  <path d="M${b.ws + 4},${belt - 4} q-2,-10 10,-10 h6 q2,8 -6,12 Z" fill="${mix(color, '#000000', 0.25)}"/>
  <path class="headlight" d="M${b.nose + 4},${b.hood + 8} C${b.nose + 14},${b.hood + 2} ${b.nose + 34},${b.hood + 1} ${b.nose + 46},${b.hood + 3} L${b.nose + 40},${b.hood + 10} C${b.nose + 26},${b.hood + 12} ${b.nose + 12},${b.hood + 13} ${b.nose + 4},${b.hood + 8} Z" fill="#f4f7fb"/>
  <path class="taillight" d="M${b.tail - 2},${b.deck + 8} L${b.tail - 26},${b.deck + 9} L${b.tail - 24},${b.deck + 16} L${b.tail - 1},${b.deck + 17} Z" fill="#ff2a3d"/>
  ${wheel(b.fw, cy, b.r, id)}
  ${wheel(b.rw, cy, b.r, id)}
</svg>`;
  };
})();
