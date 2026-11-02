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

Izmišljen beogradski streetwear brend, napravljen po uzoru na redizajne sa TikToka (tamni editorijal, numerisane liste, tabela veličina, vremenska linija, rotirajuća traka). Bez slika i bez biblioteka: odeća je nacrtana u SVG-u, sve radi u čistom HTML/CSS/JS. Radi: torba sa memorisanjem, boje i veličine, odbrojavanje do dropa, pronalazač kroja, arhiva sa pregledom, zakazivanje termina, newsletter, meni za telefon.

- Izvor: `vrana/index.html`, `styles.css`, `main.js`, `fonts/` (otvori `vrana/index.html` direktno).
- Produkcija: `npm install && npm run build:vrana` pravi `vrana/dist/` (minifikovan CSS ubačen u HTML, JS sa hešom u imenu, `_headers` i `.htaccess` za keširanje). Postavi sadržaj `vrana/dist/` na bilo koji statički hosting (Netlify, Cloudflare Pages, Vercel, Apache).
- Test lokalno sa kompresijom: `npm run serve:vrana`.

### Optimizacija (Lighthouse, mobilni profil, spora 4G veza)

| | Pre | Posle |
|---|---|---|
| Performanse | 72 | 100 |
| FCP / LCP | 4,5 s / 4,5 s | 1,4 s / 1,5 s |
| Skok rasporeda (CLS) | 0 | 0 |
| Pristupačnost / Best practices / SEO | 99 / 96 / 100 | 100 / 100 / 100 |

Šta je urađeno: fontovi hostovani lokalno i isečeni na korišćena slova (228 KB → 76 KB, trajni keš), CSS ubačen u HTML (nema blokirajućih zahteva), JS minifikovan i odložen, rezervni fontovi sa istim metrikama protiv skokova rasporeda, favicon bez 404, ispravljen redosled naslova i naziv dugmeta, `touch-action` bez kašnjenja na dodir, odbrojavanje se pauzira u pozadini.
