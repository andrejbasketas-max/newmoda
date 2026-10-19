// Products, recipes and the SVG artwork (jars + illustrations) used across the page.
window.MED = (() => {
  const C = {
    gold: '#faae33', rust: '#823513', saffron: '#9f531b', spice: '#402011',
    clove: '#281006', cardamom: '#6b2e12', chili: '#d1255c', amber: '#e8961f', cream: '#f3dcaa',
  };

  const PRODUCTS = [
    { id: 'bagrem', name: 'Bagremov med', label: 'BAGREMOV', honey: '#f4c95d', level: 1,
      notes: 'Svetao, nežan i blag. Najsporije se kristališe — idealan za čaj i decu.',
      sizes: [['450 g', 950], ['900 g', 1750]] },
    { id: 'livadski', name: 'Livadski med', label: 'LIVADSKI', honey: '#e8961f', level: 2,
      notes: 'Cvetni i pun, sa notama divljeg cveća sa šumadijskih livada.',
      sizes: [['450 g', 850], ['900 g', 1550]] },
    { id: 'lipa', name: 'Lipov med', label: 'LIPOV', honey: '#eab13c', level: 2,
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

  const RECIPES = [
    {
      id: 'palacinke', art: 'pancakes', time: '15 min',
      title: 'Palačinke sa medom i orasima',
      desc: 'Tanke palačinke, prepečeni orasi i obilno livadskog meda. Nedeljno jutro za 15 minuta.',
      breakdown: [['Priprema', '5 min'], ['Pečenje', '10 min'], ['Porcije', '2'], ['Ukupno', '~15 min']],
      ingredients: ['2 jaja', '250 ml mleka', '120 g brašna', 'Prstohvat soli', '1 kašika ulja + malo za tiganj', '50 g oraha, grubo seckanih', '4 kašike livadskog meda Gladni Medved'],
      tip: 'Orahe prepeci na suvom tiganju dok ne zamirišu — med ih posle lepi za palačinku.',
      steps: [
        ['Umuti testo', 'Izmešaj jaja, mleko, brašno, so i ulje u glatko testo. Ostavi 5 minuta.'],
        ['Prepeci orahe', 'Na suvom tiganju prepeci orahe 2–3 minuta, pa ih skloni.'],
        ['Peci palačinke', 'Na blago nauljenom tiganju peci tanke palačinke po 1 minut sa svake strane.'],
        ['Složi i prelij', 'Složi palačinke, pospi orasima i prelij medom. Odmah posluži.'],
      ],
    },
    {
      id: 'feta', art: 'feta', time: '20 min',
      title: 'Pečeni feta sa medom i timijanom',
      desc: 'Topao, slan i sladak u isto vreme. Kestenov med i timijan na zapečenom siru.',
      breakdown: [['Priprema', '5 min'], ['Pečenje', '15 min'], ['Porcije', '4'], ['Ukupno', '~20 min']],
      ingredients: ['200 g feta sira u komadu', '2 kašike maslinovog ulja', '2 kašike kestenovog meda Gladni Medved', '3 grančice svežeg timijana', 'Sveže mleveni biber', 'Hrskav hleb za služenje'],
      tip: 'Za još jaču notu, pred kraj upali grejač odozgo da med karamelizuje.',
      steps: [
        ['Zagrej rernu', 'Zagrej rernu na 200 °C.'],
        ['Pripremi sir', 'Stavi feta sir u manju posudu, prelij uljem i pospi timijanom i biberom.'],
        ['Peci', 'Peci 12–15 minuta, dok sir ne omekša i ivice ne porumene.'],
        ['Prelij medom', 'Izvadi, prelij kestenovim medom i služi toplo uz hleb.'],
      ],
    },
    {
      id: 'caj', art: 'tea', time: '5 min',
      title: 'Čaj od đumbira sa lipovim medom',
      desc: 'Topla šolja za hladne večeri. Đumbir, limun i kašika lipovog meda.',
      breakdown: [['Priprema', '2 min'], ['Kuvanje', '3 min'], ['Porcije', '1'], ['Ukupno', '~5 min']],
      ingredients: ['300 ml vode', '3 cm svežeg đumbira, tanko sečenog', '2 kriške limuna', '1–2 kašike lipovog meda Gladni Medved'],
      tip: 'Med dodaj tek kad čaj malo prohladi (ispod 40 °C) — tako čuva enzime i aromu.',
      steps: [
        ['Prokuvaj', 'Prokuvaj vodu sa đumbirom 3 minuta.'],
        ['Procedi', 'Procedi u šolju i dodaj kriške limuna.'],
        ['Zasladi', 'Sačekaj minut-dva, pa umešaj lipov med.'],
      ],
    },
  ];

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
      <use href="#bear" x="85" y="131" width="30" height="25" style="color:${C.gold}"/>
      <text x="100" y="${p.label.length > 6 ? 182 : 185}" text-anchor="middle" fill="${C.gold}" font-family="Outfit, sans-serif" font-weight="800" font-size="${small}" letter-spacing="-.3">${p.label}</text>
      <text x="100" y="200" text-anchor="middle" fill="${C.gold}" font-family="Outfit, sans-serif" font-weight="500" font-size="7.6" letter-spacing=".9">GLADNI MEDVED · ${p.sizes[0][0]}</text>`;
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
    pancakes() {
      let stack = '';
      for (let i = 0; i < 5; i++) {
        const y = 226 - i * 18;
        stack += `<ellipse cx="200" cy="${y + 6}" rx="112" ry="27" fill="${C.saffron}"/><ellipse cx="200" cy="${y}" rx="112" ry="27" fill="${i & 1 ? '#f0b75a' : '#e8a548'}"/>`;
      }
      return `<rect width="400" height="300" fill="${C.rust}"/>
        <ellipse cx="200" cy="246" rx="160" ry="42" fill="${C.spice}"/>
        ${stack}
        <path d="M120 150c20-22 140-22 160 0c-10 12-30 6-36 30a8 8 0 0 1-15 0c-4-14-20-16-40-14c-12 2-14 34-24 34s-8-26-22-30c-12-4-20-8-23-20z" fill="${C.amber}"/>
        <path d="M170 140l10 8-12 4zM214 136l12 6-11 7zM238 150l9 9-12 2z" fill="${C.cardamom}"/>
        ${bee(330, 70, 0.8)}`;
    },
    feta() {
      return `<rect width="400" height="300" fill="${C.clove}"/>
        <ellipse cx="200" cy="190" rx="168" ry="88" fill="${C.saffron}"/>
        <ellipse cx="200" cy="182" rx="150" ry="74" fill="${C.rust}"/>
        <path d="M128 150l140-22 10 70-140 22z" fill="${C.cream}"/>
        <path d="M138 220l140-22 4 16-140 22z" fill="#d9b981"/>
        <path d="M140 160c20 20 30-14 50 6s30-16 50 4 24-12 34 0" fill="none" stroke="${C.gold}" stroke-width="6" stroke-linecap="round"/>
        <path d="M150 190c20 14 40-12 60 2s30-10 56-2" fill="none" stroke="${C.amber}" stroke-width="5" stroke-linecap="round"/>
        <g stroke="${C.gold}" stroke-width="2.5" stroke-linecap="round" fill="${C.gold}">
          <path d="M84 120l60 24"/><ellipse cx="100" cy="122" rx="5" ry="2.6"/><ellipse cx="112" cy="134" rx="5" ry="2.6"/><ellipse cx="124" cy="132" rx="5" ry="2.6"/>
          <path d="M300 230l46-30"/><ellipse cx="316" cy="214" rx="5" ry="2.6"/><ellipse cx="328" cy="214" rx="5" ry="2.6"/>
        </g>`;
    },
    tea() {
      return `<rect width="400" height="300" fill="${C.chili}"/>
        <g fill="#a81a49"><circle cx="40" cy="40" r="60"/><circle cx="380" cy="280" r="80"/></g>
        <path d="M140 110h120v100a44 44 0 0 1-44 44h-32a44 44 0 0 1-44-44z" fill="${C.clove}"/>
        <path d="M258 140c40-6 44 50 0 48" fill="none" stroke="${C.clove}" stroke-width="14"/>
        <ellipse cx="200" cy="112" rx="60" ry="10" fill="${C.saffron}"/>
        <path d="M180 92c-12-16 10-22 0-40M206 90c-12-16 10-22 0-44M232 92c-12-16 10-22 0-40" fill="none" stroke="${C.gold}" stroke-width="5" stroke-linecap="round"/>
        <circle cx="96" cy="230" r="34" fill="${C.gold}"/><circle cx="96" cy="230" r="26" fill="none" stroke="${C.amber}" stroke-width="3"/>
        <path d="M96 204v52M70 230h52M78 212l36 36M114 212l-36 36" stroke="${C.amber}" stroke-width="2.5"/>
        <path d="M296 250c10-20 40-20 50-6 6 10-6 18-20 14-10 10-26 8-30-8z" fill="${C.gold}"/>`;
    },
  };
  const artSVG = (name) =>
    `<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" aria-hidden="true">${ART[name]()}</svg>`;

  return { C, PRODUCTS, LEVELS, RECIPES, byId, jarSVG, artSVG };
})();
