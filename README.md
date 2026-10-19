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

## Med „Gladni Medved“ (`med/`)

Online prodavnica meda — otvori `med/index.html`. Vizuelno prati Hungry Tiger stil sa [Refero Styles](https://styles.refero.design/style/47f15da7-8905-45b3-bcab-06a4277c6168): rđasto-braon platno (`#823513`), jedan zlatni akcenat (`#faae33`), ogromni naslovi, pilule umesto dugmića, tačkaste zlatne linije, bez senki. Struktura stranice prati njihov sajt: hero → tegla koja putuje kroz tri ekrana → „Šta je unutra“ → prodavnica (6 sorti, izbor veličine, oznaka jačine) → tradicija → „Zašto je tegla važna“ → recepti (sa detaljima) → newsletter → footer, plus korpa, mini-igra „Uhvati 50 kapi“ i plutajuća dugmad.

- `data.js` — proizvodi, cene, recepti i SVG tegle/ilustracije (cene i sorte menjaš ovde).
- `main.js` — korpa (čuva se u `localStorage`), porudžbina, recepti, meni, efekat „punjenja medom“ na naslovima.
- `game.js` — mini-igra.
- `src/jar3d.js` → `jar3d.js` — prave 3D tegle u WebGL-u (Three.js): stakleni odsjaji, med koji „svetli“, etiketa sa zlatnom folijom, rebrasti poklopac. U hero delu tegla se okreće i prate je kapi meda; dok skroluješ, tegla putuje kroz tri ekrana i poklopac se odvrće uz nit meda; u prodavnici se tegla zavrti kad pređeš mišem. Jedan renderer crta sve vidljive tegle, a bez WebGL-a ostaju SVG tegle. Posle izmene: `npm install && npm run build:med`.

Porudžbina i newsletter nemaju backend: forma samo potvrđuje lokalno. Brend, adresa, telefon i e-mail su izmišljeni (placeholder).
