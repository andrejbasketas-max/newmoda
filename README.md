# Newmoda — Maison de Parfum

Static landing page for a (fictional) perfume house. Open `index.html` or serve the folder with any static host.

- `index.html`, `assets/styles.css`, `assets/main.js` — page, styles, interactions (bag, scent finder, newsletter).
- `assets/motion.js` — GSAP + ScrollTrigger + SplitText + Lenis: preloader, text reveals, pinned "Origins" scroll, tilt cards, cursor.
- `src/scene.js` → `assets/scene.js` — Three.js 3D glass bottle that follows the hero and the notes section.
- `assets/vendor/` — vendored GSAP, Lenis and Motion (successor to Framer Motion; `motion.js` exposes `window.Motion`, not yet loaded by any page) builds.

Without WebGL the SVG bottles are shown; with `prefers-reduced-motion` the page renders statically.

## Rebuilding the 3D bundle

```bash
npm install
npm run build    # bundles src/scene.js into assets/scene.js
npm run vendor   # re-copies GSAP/Lenis/Motion into assets/vendor
```

## Kafić „Zrno“ (`kafic/`)

Odvojen, samostalan sajt za kafić — otvori `kafic/index.html`. Bez zavisnosti (čist HTML/CSS/JS), prilagođen telefonu: animirana šoljica sa parom, rotirajući bedž, traka sa napicima, meni sa tabovima, kartice koje se prevlače, status „otvoreno/zatvoreno“ i dugme za poziv. Animacije se gase uz `prefers-reduced-motion`.

## Auto salon „Vektor“ (`auto/`)

Sajt za auto salon — otvori `auto/index.html`. Čist HTML/CSS/JS uz Motion (`assets/vendor/motion.js`) za animacije: auto koji uleće u hero, ponuda sa filterima (karoserija, gorivo, sortiranje), prozor sa detaljima vozila, „Auto meseca“ koji se pokreće skrolom, kalkulator rate, otkup i kontakt forma sa proverom polja. Prilagođen telefonu; uz `prefers-reduced-motion` animacije se gase.

- Vozila se menjaju u nizu `CARS` na vrhu `auto/main.js`. Automobili su crtani kodom (`auto/car.js`); za pravu fotografiju dodaj `photo: 'img/naziv.jpg'`.
- Kamata kalkulatora (`APR`), e-mail i `FORM_ENDPOINT` su takođe na vrhu `main.js`. Bez `FORM_ENDPOINT` forma otvara e-mail posetioca sa pripremljenom porukom.
- Ime, adresa, telefon, cene i vozila su primeri — zameni ih pravim podacima pre objavljivanja.

## Outreach agent (`outreach/`)

Pronalazi Instagram biznis profile bez sajta i priprema personalizovane poruke za ručno slanje. Vidi `outreach/README.md`.
