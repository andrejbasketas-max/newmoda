// Generates the three name variants of the sticker-book wallet site.
// Every model is the same page; only the brand name (and the words derived from it) changes.
// Run: node modeli/build.mjs
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));

export const BRANDS = [
  { slug: 'fizz', name: 'Fizz', tagline: 'Your money. Unstuck.' },
  { slug: 'glaze', name: 'Glaze', tagline: 'Your money. Unstuck.' },
  { slug: 'flurry', name: 'Flurry', tagline: 'Your money. Unstuck.' },
];

// ---------- Shared SVG ----------

// Inflated, grainy tube: blur the stroke's alpha into a height map, light it, add grain.
const ribbonFilter = (id, w, h, blur = 22) => `
  <filter id="${id}" filterUnits="userSpaceOnUse" x="-200" y="-200" width="${w + 400}" height="${h + 400}" color-interpolation-filters="sRGB">
    <feGaussianBlur in="SourceAlpha" stdDeviation="${blur}" result="blur"/>
    <feDiffuseLighting in="blur" surfaceScale="14" diffuseConstant="1.15" lighting-color="#ffffff" result="diff">
      <feDistantLight azimuth="235" elevation="40"/>
    </feDiffuseLighting>
    <feComposite in="SourceGraphic" in2="diff" operator="arithmetic" k1="1.22" k2="0" k3="0" k4="0" result="shaded"/>
    <feSpecularLighting in="blur" surfaceScale="14" specularConstant="0.85" specularExponent="26" lighting-color="#ffffff" result="spec">
      <feDistantLight azimuth="235" elevation="52"/>
    </feSpecularLighting>
    <feComposite in="shaded" in2="spec" operator="arithmetic" k1="0" k2="1" k3="0.38" k4="0" result="lit"/>
    <feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="2" seed="7" result="noise"/>
    <feColorMatrix in="noise" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.5 -0.12" result="grain"/>
    <feComposite in="grain" in2="lit" operator="atop" result="grainy"/>
    <feComposite in="grainy" in2="SourceAlpha" operator="in"/>
  </filter>`;

const ribbon = (cls, viewBox, filterId, width, paths, aspect = 'xMidYMid slice') => {
  const [, , w, h] = viewBox.split(' ').map(Number);
  return `<svg class="ribbon ${cls}" viewBox="${viewBox}" preserveAspectRatio="${aspect}" aria-hidden="true" focusable="false">
    <defs>${ribbonFilter(filterId, w, h, width / 6)}</defs>
    ${paths.map((d) => `<path d="${d}" stroke-width="${width}" filter="url(#${filterId})"/>`).join('\n    ')}
  </svg>`;
};

// Back copy draws the whole tube behind the wordmark; the front copy is the same tube
// clipped to one crossing, so it appears to wrap around the letters with no visible seam.
const heroRibbon = (slug, d, clip, front = false) => {
  const id = `${front ? 'rf' : 'rb'}-hero-${slug}`;
  const [x, y, w, h] = clip.split(' ');
  return `<svg class="ribbon ribbon--${front ? 'front' : 'back'}" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">
    <defs>${ribbonFilter(id, 1440, 900, 22)}${front ? `<clipPath id="${id}-clip"><rect x="${x}" y="${y}" width="${w}" height="${h}"/></clipPath>` : ''}</defs>
    <g${front ? ` clip-path="url(#${id}-clip)"` : ''}><path d="${d}" stroke-width="130" filter="url(#${id})"/></g>
  </svg>`;
};

const stickerDefs = (letter) => `
<svg width="0" height="0" class="sr-only" aria-hidden="true" focusable="false">
  <defs>
    <symbol id="st-rocket" viewBox="0 0 120 120">
      <g stroke="#000" stroke-width="2" stroke-linejoin="round">
        <path d="M60 8c18 14 26 34 24 60H36c-2-26 6-46 24-60z" fill="#fb4903"/>
        <path d="M36 62 20 82l18 4zM84 62l16 20-18 4z" fill="#fb4903"/>
        <circle cx="60" cy="44" r="10" fill="#fff"/>
        <path d="M46 68h28l-4 14H50z" fill="#fff"/>
        <path d="M52 86c0 10 4 18 8 24 4-6 8-14 8-24z" fill="#ffd731"/>
      </g>
    </symbol>
    <symbol id="st-coin" viewBox="0 0 120 120">
      <g stroke="#000" stroke-width="2">
        <ellipse cx="64" cy="62" rx="48" ry="50" fill="#ffd731"/>
        <ellipse cx="58" cy="58" rx="48" ry="50" fill="#ffd731"/>
        <ellipse cx="58" cy="58" rx="36" ry="38" fill="none"/>
      </g>
      <text x="58" y="76" text-anchor="middle" font-family="Anton, Impact, sans-serif" font-size="50" fill="#000">${letter}</text>
    </symbol>
    <symbol id="st-wallet" viewBox="0 0 120 120">
      <g stroke="#000" stroke-width="2" stroke-linejoin="round">
        <path d="M18 30 82 14l8 22" fill="#e9ccff"/>
        <rect x="12" y="34" width="96" height="70" rx="16" fill="#5c4ade"/>
        <rect x="70" y="56" width="42" height="26" rx="13" fill="#5c4ade"/>
        <circle cx="84" cy="69" r="6" fill="#fff"/>
      </g>
    </symbol>
    <symbol id="st-check" viewBox="0 0 120 120">
      <circle cx="60" cy="60" r="50" fill="#55db9c" stroke="#000" stroke-width="2"/>
      <path d="m36 62 16 16 32-34" fill="none" stroke="#000" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
    </symbol>
    <symbol id="st-star" viewBox="0 0 120 120">
      <path d="M60 6c4 30 16 44 54 54-38 10-50 24-54 54-4-30-16-44-54-54C44 50 56 36 60 6z" fill="#e9ccff" stroke="#000" stroke-width="2" stroke-linejoin="round"/>
    </symbol>
    <symbol id="st-bolt" viewBox="0 0 120 120">
      <path d="M68 6 22 70h32l-6 44 50-66H64z" fill="#ffd731" stroke="#000" stroke-width="2" stroke-linejoin="round"/>
    </symbol>
    <symbol id="i-star" viewBox="0 0 16 16"><path d="m8 1 2.1 4.4 4.9.6-3.6 3.4.9 4.8L8 11.9l-4.3 2.3.9-4.8L1 6l4.9-.6z" fill="#000"/></symbol>
    <symbol id="i-arrow" viewBox="0 0 16 16"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></symbol>
  </defs>
</svg>`;

const sticker = (id, style) =>
  `<span class="sticker" style="${style}" aria-hidden="true"><svg><use href="#st-${id}"/></svg></span>`;

// Deterministic QR-like pattern (decorative; links to download).
function qr() {
  const n = 25;
  let seed = 1337;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const finder = (x, y) =>
    `<rect x="${x}" y="${y}" width="7" height="7"/><rect x="${x + 1}" y="${y + 1}" width="5" height="5" fill="#fff"/><rect x="${x + 2}" y="${y + 2}" width="3" height="3"/>`;
  let cells = '';
  for (let y = 0; y < n; y++)
    for (let x = 0; x < n; x++) {
      const inFinder = (x < 8 && y < 8) || (x > n - 9 && y < 8) || (x < 8 && y > n - 9);
      if (!inFinder && rnd() > 0.52) cells += `<rect x="${x}" y="${y}" width="1" height="1"/>`;
    }
  return `<svg viewBox="0 0 ${n} ${n}" shape-rendering="crispEdges" aria-hidden="true"><g fill="#000">${cells}${finder(0, 0)}${finder(n - 7, 0)}${finder(0, n - 7)}</g></svg>`;
}

const appIcons = [
  '<circle cx="50" cy="50" r="38" fill="#4da2ff" stroke="#000" stroke-width="3"/>',
  '<path d="M50 10 90 86H10z" fill="#fb4903" stroke="#000" stroke-width="3" stroke-linejoin="round"/>',
  '<rect x="14" y="14" width="72" height="72" rx="18" fill="#55db9c" stroke="#000" stroke-width="3"/>',
  '<path d="M50 8 62 38l30 2-24 20 8 30-26-17-26 17 8-30L8 40l30-2z" fill="#ffd731" stroke="#000" stroke-width="3" stroke-linejoin="round"/>',
  '<path d="M14 50a36 36 0 0 1 72 0z" fill="#5c4ade" stroke="#000" stroke-width="3"/><path d="M14 58h72a36 36 0 0 1-72 0z" fill="#e9ccff" stroke="#000" stroke-width="3"/>',
  '<path d="M50 10 88 50 50 90 12 50z" fill="#e9ccff" stroke="#000" stroke-width="3" stroke-linejoin="round"/>',
  '<circle cx="34" cy="50" r="24" fill="#fb4903" stroke="#000" stroke-width="3"/><circle cx="66" cy="50" r="24" fill="#4da2ff" stroke="#000" stroke-width="3"/>',
  '<path d="M20 80V30l30-20 30 20v50z" fill="#ffd731" stroke="#000" stroke-width="3" stroke-linejoin="round"/>',
  '<path d="M10 50c20-40 60-40 80 0-20 40-60 40-80 0z" fill="#55db9c" stroke="#000" stroke-width="3"/><circle cx="50" cy="50" r="12" fill="#000"/>',
  '<rect x="10" y="30" width="80" height="40" rx="20" fill="#5c4ade" stroke="#000" stroke-width="3"/>',
  '<path d="M50 12a38 38 0 1 0 0 76 26 26 0 0 1 0-76z" fill="#ffd731" stroke="#000" stroke-width="3"/>',
  '<path d="M18 18h64v64H18z" fill="#4da2ff" stroke="#000" stroke-width="3" transform="rotate(12 50 50)"/>',
  '<path d="M50 86S12 62 12 36a20 20 0 0 1 38-8 20 20 0 0 1 38 8c0 26-38 50-38 50z" fill="#fb4903" stroke="#000" stroke-width="3" stroke-linejoin="round"/>',
  '<circle cx="50" cy="50" r="38" fill="#e9ccff" stroke="#000" stroke-width="3"/><circle cx="50" cy="50" r="18" fill="#55db9c" stroke="#000" stroke-width="3"/>',
  '<path d="M14 70 38 30l14 24 10-16 24 32z" fill="#55db9c" stroke="#000" stroke-width="3" stroke-linejoin="round"/>',
  '<path d="M30 14h40l16 36-16 36H30L14 50z" fill="#4da2ff" stroke="#000" stroke-width="3" stroke-linejoin="round"/>',
];

const socialIcons = {
  Discord: '<path d="M13.5 3.2A12.6 12.6 0 0 0 10.4 2l-.4.8a11.7 11.7 0 0 0-4 0L5.6 2a12.6 12.6 0 0 0-3.1 1.2C.6 6.2.1 9 .3 11.8a12.7 12.7 0 0 0 3.8 1.9l.8-1.3a8 8 0 0 1-1.3-.6l.3-.2a9 9 0 0 0 8.2 0l.3.2-1.3.6.8 1.3a12.7 12.7 0 0 0 3.8-1.9c.3-3.2-.5-6-2.2-8.6zM5.4 10.1c-.8 0-1.4-.7-1.4-1.6s.6-1.6 1.4-1.6 1.4.7 1.4 1.6-.6 1.6-1.4 1.6zm5.2 0c-.8 0-1.4-.7-1.4-1.6s.6-1.6 1.4-1.6S12 7.6 12 8.5s-.6 1.6-1.4 1.6z" fill="currentColor"/>',
  X: '<path d="M12.2 1.5h2.2L9.6 7l5.6 7.5h-4.4L7.4 10 3.5 14.5H1.3l5.1-5.9L1 1.5h4.5l3.1 4.1zm-.8 11.7h1.2L4.7 2.7H3.4z" fill="currentColor"/>',
  Instagram: '<rect x="1.5" y="1.5" width="13" height="13" rx="4" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="8" cy="8" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="4" r="1" fill="currentColor"/>',
  YouTube: '<path d="M15.3 4.4a2 2 0 0 0-1.4-1.4C12.7 2.7 8 2.7 8 2.7s-4.7 0-5.9.3A2 2 0 0 0 .7 4.4 21 21 0 0 0 .4 8a21 21 0 0 0 .3 3.6 2 2 0 0 0 1.4 1.4c1.2.3 5.9.3 5.9.3s4.7 0 5.9-.3a2 2 0 0 0 1.4-1.4 21 21 0 0 0 .3-3.6 21 21 0 0 0-.3-3.6zM6.5 10.3V5.7L10.4 8z" fill="currentColor"/>',
};

const stars = `<span class="stars" aria-label="5 out of 5">${'<svg><use href="#i-star"/></svg>'.repeat(5)}</span>`;

// ---------- Page ----------

function page(b) {
  const N = b.name;
  const UP = N.toUpperCase();
  const L = UP[0];
  const nav = [
    ['get started', '#get-started'],
    ['card', '#card'],
    ['defi', '#defi'],
    ['security', '#security'],
    ['guides', '#guides'],
    ['download', '#download'],
  ];
  const marquee = Array.from({ length: 10 }, () => `<span>${N} Card Waitlist is Live</span>`).join('');

  const features = [
    ['Frictionless Onboarding', 'Sign in with Google or Apple and you are in. No seed phrase to write down on day one.', 'star', '-10deg'],
    ["Don't Just Hodl. Grow.", 'Stake and earn from vetted protocols without leaving your wallet.', 'rocket', '8deg'],
    ['Pay Anyone Instantly', 'Send to a username, an address or a link. Fees so low you will forget they exist.', 'bolt', '-6deg'],
    ['Crypto That Works', 'Swaps, NFTs and apps in one place, with clear prompts before every signature.', 'check', '10deg'],
  ];

  const reviews = [
    ['User Friendly Wallet', 'Clean, fast and honestly fun to use. Moving my funds took two minutes.', 'iOS user'],
    ['Great Wallet', 'The staking screen finally makes sense. I can see what I earn before I confirm.', 'Android user'],
    ['Smooth from day one', 'Signed in with my Google account and had my first swap done in under a minute.', 'Android user'],
    ['Best extension I use', 'Connecting to apps is instant and every prompt tells me exactly what I am signing.', 'Extension user'],
    ['Finally simple', 'I recommended it to my parents. That says everything.', 'iOS user'],
    ['Love the design', 'Feels like a sticker book, works like a bank. Withdrawals land in seconds.', 'Web user'],
  ];
  const reviewCards = reviews
    .map(
      ([t, q, who]) => `<article class="review">
          ${stars}
          <h3 class="heading-sm">${t}</h3>
          <p>“${q}”</p>
          <footer><span class="label">${who}</span><span class="caption">Example review</span></footer>
        </article>`,
    )
    .join('\n        ');

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>${N} — ${b.tagline}</title>
  <meta name="description" content="${N} is the wallet that makes crypto feel easy. Earn, swap and pay in a few taps.">
  <meta name="theme-color" content="#dceeff">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../shared/styles.css">
  <script src="../shared/main.js" defer></script>
</head>
<body>
${stickerDefs(L)}
  <a class="skip" href="#main">Skip to content</a>

  <a class="marquee" href="#card" aria-label="${N} Card waitlist is live">
    <div class="marquee__track" aria-hidden="true">${marquee}${marquee}</div>
  </a>

  <header class="nav">
    <a class="logo" href="#top" aria-label="${N} home">
      <span class="logo__badge" aria-hidden="true">${L}</span>
      <span class="logo__word">${N}</span>
    </a>
    <nav class="nav__pills" aria-label="Main">
      ${nav.map(([t, h]) => `<a class="pill" href="${h}">${t}</a>`).join('\n      ')}
    </nav>
    <div class="nav__end">
      <a class="btn btn--solid" href="#download">Launch App</a>
      <button class="plus" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="menu" data-menu-toggle>
        <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1v14M1 8h14" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>
      </button>
    </div>
  </header>

  <nav class="menu" id="menu" aria-label="Mobile">
    ${nav.map(([t, h]) => `<a href="${h}" data-menu-link>${t}</a>`).join('\n    ')}
  </nav>

  <main id="main">
    <!-- HERO -->
    <section class="hero" id="top">
      ${heroRibbon(b.slug, 'M-140 250 C 260 80, 1060 30, 1240 230 C 1400 420, 1040 590, 700 570 C 380 550, 140 520, -140 560', '360 440 800 240')}
      <h1 class="display hero__word" style="--len:${N.length}">${N}</h1>
      ${heroRibbon(b.slug, 'M-140 250 C 260 80, 1060 30, 1240 230 C 1400 420, 1040 590, 700 570 C 380 550, 140 520, -140 560', '360 440 800 240', true)}
      ${sticker('rocket', '--s:150px;--r:18deg;left:6%;top:22%')}
      ${sticker('coin', '--s:120px;--r:-14deg;right:8%;top:18%')}
      ${sticker('wallet', '--s:130px;--r:10deg;right:12%;bottom:12%')}
      ${sticker('check', '--s:96px;--r:-8deg;left:12%;bottom:16%')}
      <div class="hero__tag"><p class="heading">${b.tagline}</p></div>
      <div class="hero__cta">
        <a class="btn btn--lg" href="#download">Launch web app</a>
        <a class="btn btn--lg" href="#download">Download for Chrome</a>
      </div>
      <a class="link-sm hero__more" href="#reach">available on other devices</a>
    </section>

    <!-- ALL IN -->
    <section class="band band--paper" id="download">
      <div class="wrap allin">
        <div class="allin__word">
          <p class="label allin__kicker">All things crypto</p>
          ${ribbon('', '0 0 1000 600', `r-allin-${b.slug}`, 110, [
            'M-60 520 C 200 380, 280 80, 520 120 S 860 520, 1060 260',
          ])}
          <h2 class="display">All<br>in</h2>
        </div>
        <a class="qr" href="#download" aria-label="Download ${N}">
          <span class="qr__code">${qr()}</span>
          <span class="qr__side">
            <span class="display">Down<br>load</span>
            <span>Scan to get ${N} on iOS and Android.</span>
            <span class="btn">download</span>
          </span>
          ${sticker('star', '--s:90px;--r:12deg;right:-26px;top:-40px')}
        </a>
      </div>
    </section>

    <!-- DEFI -->
    <section class="band band--concrete" id="defi">
      <div class="wrap defi">
        <div class="defi__copy">
          <p class="label">${N} wallet</p>
          <p class="sub">Your shortcut to DeFi.</p>
          <div class="stack">
            <h2 class="display display--md">Explore DeFi Opportunities</h2>
            ${sticker('rocket', '--s:110px;--r:22deg;right:4%;top:-30px')}
          </div>
          <p class="sub">Discover vetted ways to put your crypto to work through DeFi protocols, all from your ${N} wallet.</p>
          <a class="btn btn--lg" href="#defi">start now</a>
        </div>
        <div class="defi__cards">
          <div class="panel">
            <p class="label">Simple, direct execution</p>
            <h3 class="heading-sm">Enter and manage in a few taps. Withdraw rewards in the asset you choose.</h3>
            <div class="ui">
              <div class="ui-row"><span class="ui-left"><span class="ui-coin" style="background:var(--blue)">${L}</span><span><b>Stake</b><small>Liquid staking</small></span></span><b>4.2% APY</b></div>
              <div class="ui-row"><span class="ui-left"><span class="ui-coin" style="background:var(--mint)">$</span><span><b>Lend USDC</b><small>Money market</small></span></span><b>6.8% APY</b></div>
              <div class="ui-row"><span class="ui-left"><span class="ui-coin" style="background:var(--sun)">₿</span><span><b>BTC vault</b><small>Auto-compound</small></span></span><b>3.1% APY</b></div>
            </div>
          </div>
          <div class="panel panel--lav">
            <p class="label">Wallet ready, simplified options</p>
            <h3 class="heading-sm">Compare potential rewards and confirm when ready</h3>
            <p class="amount">1,250.00</p>
            <p class="caption">USDC · est. +$85.00 / year</p>
            <div class="ui">
              <div class="chips"><span class="chip chip--on">USDC</span><span class="chip">${UP}</span><span class="chip">BTC</span><span class="chip">ETH</span></div>
              <span class="btn btn--solid">Confirm deposit</span>
            </div>
            ${sticker('coin', '--s:96px;--r:16deg;right:-18px;top:-30px')}
          </div>
        </div>
      </div>
    </section>

    <!-- FEATURES -->
    <section class="band band--sky" id="get-started">
      <div class="wrap">
        <div class="features-intro">
          <div class="section-head" style="margin:0">
            <p class="label">Wallet ready, simplified options</p>
            <div class="stack">
              <h2 class="display display--md">Earn, swap, and explore securely — with none of the hassle</h2>
              ${sticker('coin', '--s:96px;--r:-16deg;right:-8px;top:-46px')}
            </div>
          </div>
          <div>
            <div class="hero__cta">
              <a class="btn btn--lg" href="#download">Launch web app</a>
              <a class="btn btn--lg" href="#download">Download for Chrome</a>
            </div>
            <p style="text-align:right;margin:12px 0 0"><a class="link-sm" href="#reach">available on other devices</a></p>
          </div>
        </div>
        <div class="features">
          ${features
            .map(
              ([t, d, s, r]) => `<article class="feature">
            <svg class="feature__art" style="--r:${r}" aria-hidden="true"><use href="#st-${s}"/></svg>
            <h3 class="heading-sm">${t}</h3>
            <p>${d}</p>
            <a class="btn" href="#download">Get ${N}</a>
          </article>`,
            )
            .join('\n          ')}
        </div>
      </div>
    </section>

    <!-- REACH -->
    <section class="band band--paper" id="reach">
      <div class="wrap reach">
        <div>
          <div class="stack">
            <h2 class="display display--md">${N} is always within reach</h2>
            ${sticker('wallet', '--s:100px;--r:-12deg;right:2%;top:-40px')}
          </div>
          <div class="tabs" role="tablist" aria-label="Platforms">
            <button class="tab" role="tab" id="tab-mobile" aria-controls="panel-mobile" aria-selected="true" data-tab="mobile">mobile app</button>
            <button class="tab" role="tab" id="tab-web" aria-controls="panel-web" aria-selected="false" tabindex="-1" data-tab="web">web app</button>
            <button class="tab" role="tab" id="tab-ext" aria-controls="panel-ext" aria-selected="false" tabindex="-1" data-tab="ext">browser extension</button>
          </div>
          <div class="tabpanel" role="tabpanel" id="panel-mobile" aria-labelledby="tab-mobile">
            <h3 class="heading-sm">Full control, anytime, anywhere.</h3>
            <p class="sub">Swap, stake and explore DeFi from your pocket on iOS and Android.</p>
            <a class="btn btn--lg" href="#download">Get ${N}</a>
          </div>
          <div class="tabpanel" role="tabpanel" id="panel-web" aria-labelledby="tab-web" hidden>
            <h3 class="heading-sm">A powerful wallet, no downloads required.</h3>
            <p class="sub">Open ${N} in any browser and pick up right where you left off.</p>
            <a class="btn btn--lg" href="#download">Get ${N}</a>
          </div>
          <div class="tabpanel" role="tabpanel" id="panel-ext" aria-labelledby="tab-ext" hidden>
            <h3 class="heading-sm">Seamless DeFi &amp; dApp access.</h3>
            <p class="sub">Connect to apps, manage NFTs and sign with confidence, straight from your browser.</p>
            <a class="btn btn--lg" href="#download">Get ${N}</a>
          </div>
        </div>
        <div class="stage" aria-hidden="true">
          ${ribbon('', '0 0 600 600', `r-stage-${b.slug}`, 90, ['M-40 120 C 200 40, 520 160, 420 330 S 80 420, 140 640'])}
          <div class="device is-active" data-device="mobile">
            <div class="phone">
              <div class="phone__notch"></div>
              <div class="wallet-head"><span class="logo__badge" style="width:34px;height:34px;font-size:20px">${L}</span><span class="chip">Main</span></div>
              <div><div class="balance-label">Total balance</div><div class="balance">$2,480</div></div>
              <div class="actions"><span>Send</span><span>Earn</span><span>Swap</span><span>Buy</span></div>
              <div class="ui-row"><span class="ui-left"><span class="ui-coin" style="background:var(--blue)">${L}</span><b>${UP}</b></span><b>$1,204</b></div>
              <div class="ui-row"><span class="ui-left"><span class="ui-coin" style="background:var(--mint)">$</span><b>USDC</b></span><b>$980</b></div>
              <div class="ui-row"><span class="ui-left"><span class="ui-coin" style="background:var(--sun)">₿</span><b>BTC</b></span><b>$296</b></div>
            </div>
          </div>
          <div class="device" data-device="web">
            <div class="browser">
              <div class="browser__bar"><i></i><i></i><i></i><span class="browser__url">app.${b.slug}.com</span></div>
              <div class="browser__body">
                <div class="wallet-head"><div><div class="balance-label">Total balance</div><div class="balance">$2,480</div></div><span class="btn btn--solid">Swap</span></div>
                <div class="actions"><span>Send</span><span>Earn</span><span>Swap</span><span>Buy</span></div>
                <div class="ui-row"><span class="ui-left"><span class="ui-coin" style="background:var(--blue)">${L}</span><b>${UP}</b></span><b>$1,204</b></div>
                <div class="ui-row"><span class="ui-left"><span class="ui-coin" style="background:var(--mint)">$</span><b>USDC</b></span><b>$980</b></div>
              </div>
            </div>
          </div>
          <div class="device" data-device="ext">
            <div class="ext">
              <div class="wallet-head"><span class="logo__badge" style="width:34px;height:34px;font-size:20px">${L}</span><span class="chip chip--on">Connected</span></div>
              <p class="heading-sm" style="font-size:20px">app.example wants to connect</p>
              <div class="ui-row"><span>View balance</span><b>✓</b></div>
              <div class="ui-row"><span>Request approvals</span><b>✓</b></div>
              <div class="chips"><span class="btn">Cancel</span><span class="btn btn--solid">Approve</span></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- REVIEWS -->
    <section class="band band--concrete" id="reviews">
      <div class="wrap reviews-top">
        <div class="section-head" style="margin:0">
          <p class="label">Trusted by millions</p>
          <div class="stack">
            ${ribbon('', '0 0 1000 500', `r-rev-${b.slug}`, 90, ['M-80 80 C 260 -20, 520 220, 760 120 S 1040 60, 1100 200'])}
            <h2 class="display display--lg">Don't believe us?<br>See for yourself</h2>
            ${sticker('check', '--s:96px;--r:-10deg;left:-24px;bottom:-30px')}
            ${sticker('wallet', '--s:110px;--r:14deg;right:-10px;top:-20px')}
          </div>
        </div>
        <a class="btn btn--lg btn--solid" href="#download">join the millions</a>
      </div>
      <div class="reviews">
        <div class="reviews__track">
        ${reviewCards}
        ${reviewCards.replaceAll('<article class="review">', '<article class="review" aria-hidden="true">')}
        </div>
      </div>
    </section>

    <!-- AUDIENCES -->
    <section class="band band--sky" id="security">
      <div class="wrap">
        <div class="section-head">
          <div class="stack">
            <h2 class="display display--lg">Crypto for humans.<br>Not just degens.</h2>
            ${sticker('star', '--s:110px;--r:8deg;right:6%;top:-20px')}
            ${sticker('bolt', '--s:90px;--r:-14deg;right:18%;bottom:-30px')}
          </div>
        </div>
        <div class="audiences">
          <article class="audience">
            <span class="num">01</span>
            <h3 class="heading-sm">Frictionless Onboarding</h3>
            <p>Create a wallet with the account you already have. Back it up later, when you are ready.</p>
            <a class="btn" href="#get-started">learn more</a>
          </article>
          <article class="audience">
            <span class="num">02</span>
            <h3 class="heading-sm">For DeFi Power Users</h3>
            <p>Staking, lending and swaps with clear rates, routes and fees before every confirmation.</p>
            <a class="btn" href="#defi">Earn</a>
          </article>
          <article class="audience">
            <span class="num">03</span>
            <h3 class="heading-sm">For Developers</h3>
            <p>A standard wallet interface, open SDKs and a community that answers questions fast.</p>
            <a class="btn" href="#support">our discord</a>
          </article>
        </div>
      </div>
    </section>

    <!-- ECOSYSTEM -->
    <section class="band band--paper" id="guides">
      <div class="wrap eco">
        <div class="eco__copy">
          <div class="stack">
            <h2 class="display display--md">Seamlessly connect to the ecosystem</h2>
            ${sticker('rocket', '--s:100px;--r:-20deg;right:0;top:-50px')}
          </div>
          <p class="sub">Hundreds of apps, one wallet. Sign in once and go.</p>
          <a class="btn btn--lg" href="#download">Download for Chrome</a>
        </div>
        <div class="eco__grid" aria-hidden="true">
          ${appIcons.map((p) => `<span class="app"><svg viewBox="0 0 100 100">${p}</svg></span>`).join('\n          ')}
        </div>
      </div>
    </section>

    <!-- NEWSLETTER + SUPPORT -->
    <section class="band band--concrete" id="card">
      <div class="wrap news">
        <div class="section-head" style="margin:0">
          <div class="stack">
            <h2 class="display display--md">Your inbox just got better</h2>
            ${sticker('coin', '--s:92px;--r:12deg;right:4%;top:-40px')}
          </div>
          <p class="sub">Subscribe to our newsletter for VIP access to news, offers, and insights!</p>
        </div>
        <form class="news__form" data-newsletter novalidate>
          <label class="sr-only" for="email">Email address</label>
          <div class="field">
            <input id="email" name="email" type="email" autocomplete="email" placeholder="your@email.com" required>
            <button class="btn btn--solid" type="submit">subscribe</button>
          </div>
          <label class="check"><input type="checkbox" name="consent" required> I agree to receive communications from ${N} Labs.</label>
          <p class="form-msg" role="status" aria-live="polite"></p>
        </form>
      </div>
      <div class="wrap" style="margin-top:clamp(48px,7vw,96px)" id="support">
        <div class="support">
          <div class="section-head" style="margin:0">
            <h2 class="heading">Always Here to Help</h2>
            <p class="sub">Whether you're a first-time user or a DeFi pro, our 24/7 support team has you covered.</p>
          </div>
          <div class="support__cta">
            <a class="btn btn--lg btn--solid" href="#support">Get support</a>
            <a class="btn btn--lg" href="#support">help center</a>
          </div>
          ${sticker('check', '--s:84px;--r:-12deg;right:22px;top:-44px')}
        </div>
      </div>
    </section>
  </main>

  <footer class="footer">
    <div class="wrap">
      <div class="footer__top">
        <div class="stack">
          <h2 class="display display--md">Download ${N}.<br>Then make it all happen.</h2>
          ${sticker('check', '--s:84px;--r:10deg;right:4%;top:-40px')}
        </div>
        <a class="btn btn--lg btn--solid" href="#download">Get ${N}</a>
      </div>
      <nav class="footer__links" aria-label="Footer">
        <a class="pill" href="#top">home</a>
        <a class="pill" href="#card">card</a>
        <a class="pill" href="#defi">defi / earn</a>
        <a class="pill" href="#get-started">get started</a>
        <a class="pill" href="#security">security</a>
        <a class="pill" href="#download">download</a>
        <a class="pill" href="#guides">guides</a>
      </nav>
      <div class="footer__meta">
        <div class="socials">
          ${Object.entries(socialIcons).map(([n, p]) => `<a href="#top" aria-label="${n}"><svg viewBox="0 0 16 16" aria-hidden="true">${p}</svg></a>`).join('\n          ')}
        </div>
        <nav aria-label="Legal">
          <a href="#support">FAQ</a><a href="#top">Brand assets</a><a href="#top">Privacy Notice</a><a href="#top">Terms of Service</a>
        </nav>
        <span class="caption">© ${new Date().getFullYear()} ${N} Labs, Inc.</span>
      </div>
    </div>
    <div class="footer__giant" aria-hidden="true">
      <p class="display">${N}</p>
      ${ribbon('', '0 0 1440 600', `r-foot-${b.slug}`, 120, ['M-100 420 C 240 260, 520 560, 760 380 S 1180 140, 1560 360'])}
    </div>
  </footer>

  <nav class="switcher" aria-label="Choose model">
    ${BRANDS.map((o) => `<a href="../${o.slug}/"${o.slug === b.slug ? ' aria-current="page"' : ''}>${o.name}</a>`).join('')}
  </nav>
</body>
</html>
`;
}

for (const b of BRANDS) {
  const out = join(root, b.slug, 'index.html');
  mkdirSync(dirname(out), { recursive: true });
  writeFileSync(out, page(b));
  console.log('wrote', out);
}
