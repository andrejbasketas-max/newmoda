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

## Outreach agent (`outreach/`)

Pronalazi Instagram biznis profile bez sajta i priprema personalizovane poruke za ručno slanje. Vidi `outreach/README.md`.

## VRANA — streetwear sajt (`vrana/`)

Izmišljen beogradski streetwear brend. Bez slika i biblioteka: odeća je nacrtana u SVG-u sa ravnim bojama i tvrdim senkama, sve radi u čistom HTML/CSS/JS.

**Dizajn:** papir, mastilo i jedna crvena; oštri uglovi, tanke linije, numerisane sekcije, rukopisne beleške, asimetrična mreža. Pet fontova sa jasnom ulogom: Archivo (promenljiva širina i težina, naslovi), Instrument Serif (editorijalni akcenti), Pirata One (gotički logo), DM Mono (oznake) i Caveat (rukopis).

**Animacije:** preloader, slova koja se šire pod mišem (osa širine promenljivog fonta), kursor sa oznakama, magnetna dugmad, dve trake koje reaguju na brzinu skrola, reči manifesta koje se otkrivaju skrolom, zakačen horizontalni lookbook, brojači, vremenska linija koja se iscrtava, plutajući pregled u arhivi, maskirani ulazak naslova. Sve se gasi uz `prefers-reduced-motion`.

**Funkcije:** torba sa pamćenjem, boje i veličine, odbrojavanje do dropa, pronalazač kroja, arhiva, zakazivanje termina, newsletter, meni za telefon.

- Izvor: `vrana/index.html`, `styles.css`, `main.js`, `fonts/`.
- Produkcija: `npm install && npm run build:vrana` pravi `vrana/dist/` (CSS ubačen u HTML, JS sa hešom, `_headers` i `.htaccess` za keširanje). Postavi sadržaj `vrana/dist/` na statički hosting.
- Lokalno sa kompresijom: `npm run serve:vrana`.

**Lighthouse (mobilni profil, spora 4G):** performanse 98–99, pristupačnost 100, best practices 100, SEO 100, CLS 0, LCP oko 1,8 s. Fontovi su hostovani lokalno i isečeni na korišćena slova (latinica + č ć š đ ž), ukupno oko 115 KB.
