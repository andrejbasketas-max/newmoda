// Products and the SVG artwork (jars + illustrations) used across the page.
window.MED = (() => {
  const C = {
    gold: '#faae33', rust: '#823513', saffron: '#9f531b', spice: '#402011',
    clove: '#281006', cardamom: '#6b2e12', chili: '#d1255c', amber: '#e8961f', cream: '#f3dcaa',
  };

  const PRODUCTS = [
    { id: 'bagrem', name: 'Bagremov med', label: 'BAGREMOV', honey: '#f2b53a', level: 1,
      notes: 'Svetao, nežan i blag. Najsporije se kristališe — idealan za čaj i decu.',
      sizes: [['450 g', 950], ['900 g', 1750]] },
    { id: 'livadski', name: 'Livadski med', label: 'LIVADSKI', honey: '#e98406', level: 2,
      notes: 'Cvetni i pun, sa notama divljeg cveća sa šumadijskih livada.',
      sizes: [['450 g', 850], ['900 g', 1550]] },
    { id: 'lipa', name: 'Lipov med', label: 'LIPOV', honey: '#eb9d1e', level: 2,
      notes: 'Svež, skoro mentolast, sa mirisom lipe u junu.',
      sizes: [['450 g', 900], ['900 g', 1650]] },
    { id: 'kesten', name: 'Kestenov med', label: 'KESTENOV', honey: '#8f3f10', level: 3,
      notes: 'Taman, gorkast i karakteran. Za one koji vole jak ukus.',
      sizes: [['450 g', 1150], ['900 g', 2100]] },
    { id: 'suma', name: 'Šumski med', label: 'ŠUMSKI', honey: '#5c260b', level: 3,
      notes: 'Medljikovac iz hrastovih šuma. Bogat mineralima, sa notom karamele.',
      sizes: [['450 g', 1200], ['900 g', 2200]] },
    { id: 'sace', name: 'Med u saću', label: 'SAĆE', honey: '#f0a62e', level: 2,
      notes: 'Netaknut, pravo iz okvira. Jede se zajedno sa voskom.',
      sizes: [['300 g', 1400], ['600 g', 2600]] },
  ];
  const LEVELS = ['', 'Blag', 'Srednji', 'Jak'];

  const byId = (id) => PRODUCTS.find((p) => p.id === id) || PRODUCTS[1];

  // ---------- Jar ----------
  // Inner markup in a 200×270 box; lid is its own group so it can lift off.
  function jarInner(p, { lid = true } = {}) {
    let ridges = '';
    for (let x = 50; x <= 150; x += 8) ridges += `M${x} 13v24`;
    const small = p.label.length > 6 ? 17 : 21;
    return `
      ${lid ? `<g class="jar-lid">
        <rect x="40" y="6" width="120" height="34" rx="7" fill="#1a0a03"/>
        <path d="${ridges}" stroke="#3a1a0b" stroke-width="2.4"/>
        <rect x="40" y="6" width="120" height="6" rx="3" fill="#3a1a0b"/>
      </g>` : ''}
      <rect x="46" y="38" width="108" height="24" rx="4" fill="${C.gold}" fill-opacity=".22" stroke="${C.gold}" stroke-opacity=".35"/>
      <path d="M30 88q0-28 30-28h80q30 0 30 28v148q0 28-28 28H58q-28 0-28-28z" fill="${p.honey}"/>
      <path d="M30 88q0-28 30-28h80q30 0 30 28v148q0 28-28 28H58q-28 0-28-28z" fill="none" stroke="${C.gold}" stroke-opacity=".55" stroke-width="2"/>
      <path d="M44 96v128" stroke="#ffe3a0" stroke-opacity=".42" stroke-width="7" stroke-linecap="round"/>
      <path d="M58 80h24" stroke="#ffe3a0" stroke-opacity=".35" stroke-width="5" stroke-linecap="round"/>
      <path d="M163 100v120" stroke="${C.gold}" stroke-opacity=".5" stroke-width="3" stroke-linecap="round"/>
      <rect x="30" y="118" width="140" height="100" fill="${C.clove}"/>
      <rect x="38" y="125" width="124" height="86" rx="3" fill="none" stroke="${C.gold}" stroke-width="1.3"/>
      <use href="#logo" x="84" y="127" width="32" height="32" style="color:${C.gold}"/>
      <text x="100" y="${p.label.length > 6 ? 182 : 185}" text-anchor="middle" fill="${C.gold}" font-family="Telma, Georgia, serif" font-weight="700" font-size="${small}" letter-spacing="-.3">${p.label}</text>
      <text x="100" y="200" text-anchor="middle" fill="${C.gold}" font-family="Sentient, Georgia, serif" font-weight="700" font-size="7.6" letter-spacing=".9">GLADNI MEDVED · ${p.sizes[0][0]}</text>`;
  }
  const jarSVG = (p, opts) =>
    `<svg class="jar-svg" viewBox="0 0 200 270" role="img" aria-label="Tegla: ${p.name}">${jarInner(p, opts)}</svg>`;

  // ---------- Illustrations (400×300, cropped to fill) ----------
  const hexPath = (cx, cy, r) => {
    let d = '';
    for (let i = 0; i < 6; i++) {
      const a = Math.PI / 3 * i + Math.PI / 6;
      d += (i ? 'L' : 'M') + (cx + r * Math.cos(a)).toFixed(1) + ' ' + (cy + r * Math.sin(a)).toFixed(1);
    }
    return d + 'z';
  };
  const drip = (x, y, len, fill) => `<path d="M${x - 9} ${y}h18v${len}a9 9 0 0 1-18 0z" fill="${fill}"/>`;
  const bee = (x, y, s = 1) => `<g transform="translate(${x} ${y}) scale(${s})">
      <ellipse cx="-6" cy="-9" rx="7" ry="5" fill="none" stroke="${C.gold}" stroke-width="2"/>
      <ellipse cx="6" cy="-9" rx="7" ry="5" fill="none" stroke="${C.gold}" stroke-width="2"/>
      <ellipse cx="0" cy="0" rx="11" ry="8" fill="${C.gold}"/>
      <path d="M-3-7v14M3-7v14" stroke="${C.clove}" stroke-width="3"/></g>`;

  const ART = {
    hives() {
      const hive = (x, y, w) => {
        const h = w * 0.45;
        return `<g>
          <rect x="${x - 6}" y="${y + h * 3}" width="${w + 12}" height="10" fill="${C.cardamom}"/>
          <rect x="${x}" y="${y + h * 2}" width="${w}" height="${h}" fill="${C.rust}"/>
          <rect x="${x}" y="${y + h}" width="${w}" height="${h}" fill="${C.saffron}"/>
          <rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${C.rust}"/>
          <path d="M${x - 10} ${y}L${x + w / 2} ${y - h * 0.8}L${x + w + 10} ${y}z" fill="${C.cardamom}"/>
          <path d="M${x} ${y + h}h${w}M${x} ${y + h * 2}h${w}" stroke="${C.gold}" stroke-width="2" stroke-dasharray="2 5"/>
          <rect x="${x + w * 0.3}" y="${y + h * 3 - 9}" width="${w * 0.4}" height="5" fill="${C.clove}"/>
        </g>`;
      };
      return `<rect width="400" height="300" fill="${C.clove}"/>
        <circle cx="318" cy="72" r="40" fill="${C.gold}"/>
        <path d="M0 225Q110 180 210 216T400 200V300H0z" fill="${C.spice}"/>
        ${hive(70, 120, 110)}${hive(230, 160, 80)}
        <path d="M150 90q40-40 80-10t70 0" fill="none" stroke="${C.gold}" stroke-width="2" stroke-dasharray="3 7"/>
        ${bee(150, 90, 0.9)}${bee(232, 74, 0.7)}${bee(345, 150, 0.8)}`;
    },
    comb() {
      let cells = '';
      const fills = [C.gold, C.amber, C.gold, C.saffron, '#f4c95d'];
      for (let r = -1; r < 8; r++) {
        for (let c = -1; c < 10; c++) {
          const cx = c * 52 + (r & 1) * 26, cy = r * 45;
          cells += `<path d="${hexPath(cx, cy, 29)}" fill="${fills[Math.abs(r * 7 + c * 3) % 5]}" stroke="${C.rust}" stroke-width="5"/>`;
        }
      }
      return `<rect width="400" height="300" fill="#eea236"/>${cells}
        ${drip(78, 262, 26, C.amber)}${drip(182, 172, 40, '#f4c95d')}${drip(286, 262, 20, C.amber)}${drip(338, 82, 32, C.gold)}`;
    },
    pour() {
      const p = byId('livadski');
      return `<rect width="400" height="300" fill="${C.saffron}"/>
        <circle cx="70" cy="60" r="90" fill="${C.rust}" fill-opacity=".45"/>
        <svg x="132" y="112" width="136" height="184" viewBox="0 0 200 270">${jarInner(p, { lid: false })}</svg>
        <path d="M206 98c-6 14 6 22-2 40" fill="none" stroke="${C.amber}" stroke-width="8" stroke-linecap="round"/>
        <path d="M352 14L240 76" stroke="${C.spice}" stroke-width="11" stroke-linecap="round"/>
        <ellipse cx="216" cy="88" rx="30" ry="19" transform="rotate(-28 216 88)" fill="${C.amber}" stroke="${C.spice}" stroke-width="4"/>
        <path d="M194 92l40-21M200 101l40-21M190 83l36-19" stroke="${C.spice}" stroke-width="3"/>`;
    },
  };
  const artSVG = (name) =>
    `<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" aria-hidden="true">${ART[name]()}</svg>`;

  return { C, PRODUCTS, LEVELS, byId, jarSVG, artSVG };
})();
