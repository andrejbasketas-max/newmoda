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

  // ---------- Honey emblems (order picker) ----------
  // A honeycomb cell filled with the honey's colour and the plant it comes from.
  // Plant glyphs: Phosphor Icons (MIT), duotone weight.
  const GLYPHS = {"bagrem": "<path d=\"M206.35,136.29c-8.87-5.13-24.46-7.38-39.4-8.29,14.94-.91,30.53-3.16,39.4-8.29a32,32,0,1,0-32-55.42c-8.87,5.12-18.61,17.48-26.87,30C154.17,80.87,160,66.25,160,56a32,32,0,0,0-64,0c0,10.25,5.83,24.87,12.52,38.26-8.26-12.49-18-24.85-26.87-30a32,32,0,1,0-32,55.42c8.87,5.13,24.46,7.38,39.4,8.29-14.94.91-30.53,3.16-39.4,8.29a32,32,0,1,0,32,55.42c8.87-5.12,18.61-17.48,26.87-30C101.83,175.13,96,189.75,96,200a32,32,0,0,0,64,0c0-10.25-5.83-24.87-12.52-38.26,8.26,12.49,18,24.85,26.87,30a32,32,0,1,0,32-55.42ZM155.71,144A32,32,0,1,1,160,128,31.74,31.74,0,0,1,155.71,144Z\" opacity=\"0.2\"/><path d=\"M210.35,129.36c-.81-.47-1.7-.92-2.62-1.36.92-.44,1.81-.89,2.62-1.36a40,40,0,1,0-40-69.28c-.81.47-1.65,1-2.48,1.59.08-1,.13-2,.13-3a40,40,0,0,0-80,0c0,.94,0,1.94.13,3-.83-.57-1.67-1.12-2.48-1.59a40,40,0,1,0-40,69.28c.81.47,1.7.92,2.62,1.36-.92.44-1.81.89-2.62,1.36a40,40,0,1,0,40,69.28c.81-.47,1.65-1,2.48-1.59-.08,1-.13,2-.13,2.95a40,40,0,0,0,80,0c0-.94-.05-1.94-.13-2.95.83.57,1.67,1.12,2.48,1.59A39.79,39.79,0,0,0,190.29,204a40.43,40.43,0,0,0,10.42-1.38,40,40,0,0,0,9.64-73.28ZM104,128a24,24,0,1,1,24,24A24,24,0,0,1,104,128Zm74.35-56.79a24,24,0,1,1,24,41.57c-6.27,3.63-18.61,6.13-35.16,7.19A40,40,0,0,0,154.53,98.1C163.73,84.28,172.08,74.84,178.35,71.21ZM128,32a24,24,0,0,1,24,24c0,7.24-4,19.19-11.36,34.06a39.81,39.81,0,0,0-25.28,0C108,75.19,104,63.24,104,56A24,24,0,0,1,128,32ZM44.86,80a24,24,0,0,1,32.79-8.79c6.27,3.63,14.62,13.07,23.82,26.89A40,40,0,0,0,88.81,120c-16.55-1.06-28.89-3.56-35.16-7.18A24,24,0,0,1,44.86,80ZM77.65,184.79a24,24,0,1,1-24-41.57c6.27-3.63,18.61-6.13,35.16-7.19a40,40,0,0,0,12.66,21.87C92.27,171.72,83.92,181.16,77.65,184.79ZM128,224a24,24,0,0,1-24-24c0-7.24,4-19.19,11.36-34.06a39.81,39.81,0,0,0,25.28,0C148,180.81,152,192.76,152,200A24,24,0,0,1,128,224Zm83.14-48a24,24,0,0,1-32.79,8.79c-6.27-3.63-14.62-13.07-23.82-26.89A40,40,0,0,0,167.19,136c16.55,1.06,28.89,3.56,35.16,7.18A24,24,0,0,1,211.14,176Z\"/>", "livadski": "<path d=\"M169.23,66v0A80,80,0,0,0,128,136,80,80,0,0,0,86.77,66v0C100,38,128,24,128,24S156,38,169.23,66Z\" opacity=\"0.2\"/><path d=\"M208,48a87.48,87.48,0,0,0-35.36,7.43c-15.1-25.37-39.92-38-41.06-38.59a8,8,0,0,0-7.16,0c-1.14.58-26,13.22-41.06,38.59A87.48,87.48,0,0,0,48,48a8,8,0,0,0-8,8V96a88.11,88.11,0,0,0,80,87.63v35.43L83.58,200.84a8,8,0,1,0-7.16,14.32l48,24a8,8,0,0,0,7.16,0l48-24a8,8,0,0,0-7.16-14.32L136,219.06V183.63A88.11,88.11,0,0,0,216,96V56A8,8,0,0,0,208,48ZM128,33.21c6.65,4.08,21.08,14.19,30.64,30A88.46,88.46,0,0,0,128,99.36,88.4,88.4,0,0,0,97.36,63.19C106.93,47.4,121.35,37.29,128,33.21ZM56,96V64.44A72.1,72.1,0,0,1,120,136v31.56A72.1,72.1,0,0,1,56,96Zm144,0a72.1,72.1,0,0,1-64,71.56V136a72.1,72.1,0,0,1,64-71.56Z\"/>", "lipa": "<path d=\"M63.81,192.19c-47.89-79.81,16-159.62,151.64-151.64C223.43,176.23,143.62,240.08,63.81,192.19Z\" opacity=\"0.2\"/><path d=\"M223.45,40.07a8,8,0,0,0-7.52-7.52C139.8,28.08,78.82,51,52.82,94a87.09,87.09,0,0,0-12.76,49c.57,15.92,5.21,32,13.79,47.85l-19.51,19.5a8,8,0,0,0,11.32,11.32l19.5-19.51C81,210.73,97.09,215.37,113,215.94q1.67.06,3.33.06A86.93,86.93,0,0,0,162,203.18C205,177.18,227.93,116.21,223.45,40.07ZM153.75,189.5c-22.75,13.78-49.68,14-76.71.77l88.63-88.62a8,8,0,0,0-11.32-11.32L65.73,179c-13.19-27-13-54,.77-76.71,22.09-36.47,74.6-56.44,141.31-54.06C210.2,114.89,190.22,167.41,153.75,189.5Z\"/>", "kesten": "<path d=\"M216,112v16c0,53-88,88-88,112,0-24-88-59-88-112V112Z\" opacity=\"0.2\"/><path d=\"M232,104a56.06,56.06,0,0,0-56-56H136a24,24,0,0,1,24-24,8,8,0,0,0,0-16,40,40,0,0,0-40,40H80a56.06,56.06,0,0,0-56,56,16,16,0,0,0,8,13.83V128c0,35.53,33.12,62.12,59.74,83.49C103.66,221.07,120,234.18,120,240a8,8,0,0,0,16,0c0-5.82,16.34-18.93,28.26-28.51C190.88,190.12,224,163.53,224,128V117.83A16,16,0,0,0,232,104ZM80,64h96a40.06,40.06,0,0,1,40,40H40A40,40,0,0,1,80,64Zm74.25,135c-10.62,8.52-20,16-26.25,23.37-6.25-7.32-15.63-14.85-26.25-23.37C77.8,179.79,48,155.86,48,128v-8H208v8C208,155.86,178.2,179.79,154.25,199Z\"/>", "suma": "<path d=\"M232,127.82c.09,33.94-28.41,63.3-62.34,64.16a63.72,63.72,0,0,1-41.66-14,63.71,63.71,0,0,1-41.65,14c-33.93-.86-62.44-30.22-62.35-64.16a64,64,0,0,1,40.13-59.2,68,68,0,0,1,127.74,0A64,64,0,0,1,232,127.82Z\" opacity=\"0.2\"/><path d=\"M198.1,62.59a76,76,0,0,0-140.2,0A71.71,71.71,0,0,0,16,127.8C15.9,166,48,199,86.14,200A72.22,72.22,0,0,0,120,192.47V232a8,8,0,0,0,16,0V192.47A72.17,72.17,0,0,0,168,200l1.82,0C208,199,240.11,166,240,127.8A71.71,71.71,0,0,0,198.1,62.59ZM169.45,184a56.08,56.08,0,0,1-33.45-10v-41l43.58-21.78a8,8,0,1,0-7.16-14.32L136,115.06V88a8,8,0,0,0-16,0v51.06L83.58,120.84a8,8,0,1,0-7.16,14.32L120,156.94v17a56,56,0,0,1-33.45,10C56.9,183.23,31.92,157.52,32,127.84A55.79,55.79,0,0,1,67.11,76a8,8,0,0,0,4.53-4.67,60,60,0,0,1,112.72,0A8,8,0,0,0,188.89,76,55.79,55.79,0,0,1,224,127.84C224.08,157.52,199.1,183.23,169.45,184Z\"/>"};
  GLYPHS.sace = '<g fill="none" stroke="currentColor" stroke-width="14" stroke-linejoin="round">'
    + '<path d="M88 40l36 20v40l-36 20-36-20V60z"/><path d="M168 40l36 20v40l-36 20-36-20V60z"/>'
    + '<path d="M128 112l36 20v40l-36 20-36-20v-40z" fill="currentColor" fill-opacity=".25"/></g>';
  function emblemSVG(p) {
    const dark = p.level === 3;
    const hex = 'M50 4l40 23v46L50 96 10 73V27z';
    const ink = dark ? C.gold : C.clove;
    return `<svg class="emblem-svg" viewBox="0 0 100 100" role="img" aria-label="${p.name}">
      <defs><linearGradient id="eg-${p.id}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="${dark ? p.honey : '#ffe39a'}"/><stop offset=".55" stop-color="${p.honey}"/>
        <stop offset="1" stop-color="${dark ? '#2a0f04' : C.saffron}"/></linearGradient></defs>
      <path d="${hex}" fill="url(#eg-${p.id})" stroke="${C.gold}" stroke-width="3" stroke-linejoin="round"/>
      <path d="M50 11l34 19.6" stroke="#fff6dc" stroke-opacity=".55" stroke-width="3" stroke-linecap="round" fill="none"/>
      <svg x="27" y="15" width="46" height="46" viewBox="0 0 256 256" style="color:${ink}" fill="currentColor">${GLYPHS[p.id]}</svg>
      <path d="M43.5 81c0 4.5 3 7 6.5 7s6.5-2.5 6.5-7c0-4-6.5-11-6.5-11s-6.5 7-6.5 11z" fill="${dark ? C.gold : C.clove}" fill-opacity=".85"/>
    </svg>`;
  }

  return { C, PRODUCTS, LEVELS, byId, jarSVG, artSVG, emblemSVG };
})();
