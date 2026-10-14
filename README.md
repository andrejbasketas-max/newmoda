# Newmoda — Maison de Parfum

Static landing page for a (fictional) perfume house. Open `index.html` or serve the folder with any static host.

- `index.html`, `assets/styles.css`, `assets/main.js` — page, styles, interactions (bag, scent finder, newsletter).
- `assets/motion.js` — GSAP + ScrollTrigger + SplitText + Lenis: preloader, text reveals, pinned "Origins" scroll, tilt cards, cursor.
- `src/scene.js` → `assets/scene.js` — Three.js 3D glass bottle that follows the hero and the notes section.
- `assets/vendor/` — vendored GSAP and Lenis builds.

Without WebGL the SVG bottles are shown; with `prefers-reduced-motion` the page renders statically.

## Rebuilding the 3D bundle

```bash
npm install
npm run build    # bundles src/scene.js into assets/scene.js
npm run vendor   # re-copies GSAP/Lenis into assets/vendor
```

## Kafić „Zrno“ (`kafic/`)

Odvojen, samostalan sajt za kafić — otvori `kafic/index.html`. Bez zavisnosti (čist HTML/CSS/JS), prilagođen telefonu: animirana šoljica sa parom, rotirajući bedž, traka sa napicima, meni sa tabovima, kartice koje se prevlače, status „otvoreno/zatvoreno“ i dugme za poziv. Animacije se gase uz `prefers-reduced-motion`.
