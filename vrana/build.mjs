// Gradi vrana/dist: minifikovan CSS (ubačen u HTML), minifikovan JS sa hešom u imenu,
// zaglavlja za keširanje. Pokreni: npm run build:vrana
import { transform } from 'esbuild';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, mkdirSync, rmSync, cpSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const dist = join(root, 'dist');
rmSync(dist, { recursive: true, force: true });
mkdirSync(dist, { recursive: true });

const read = f => readFileSync(join(root, f), 'utf8');
const css = (await transform(read('styles.css'), { loader: 'css', minify: true })).code.trim();
const js = (await transform(read('main.js'), { loader: 'js', minify: true, target: 'es2020' })).code;
const hash = createHash('sha1').update(js).digest('hex').slice(0, 8);
const jsName = `main.${hash}.js`;
writeFileSync(join(dist, jsName), js);

// Preload ključnih fontova samo u produkciji (sa file:// izvora ga CORS blokira i pravi buku u konzoli)
const preload = ['archivo-normal-latin', 'archivo-normal-latin-ext']
  .map(n => `<link rel="preload" href="fonts/${n}.woff2" as="font" type="font/woff2" crossorigin>`).join('\n');
let html = read('index.html')
  .replace('<link rel="stylesheet" href="styles.css">', () => `${preload}\n<link rel="stylesheet" href="styles.css">`)
  .replace('<link rel="stylesheet" href="styles.css">', () => `<style>${css}</style>`)
  .replace('<script src="main.js" defer></script>', `<script src="${jsName}" defer></script>`)
  .replace(/<!--[\s\S]*?-->/g, '')
  .replace(/\n\s+/g, '\n')
  .replace(/\n{2,}/g, '\n');
if (html.includes('styles.css') || html.includes('"main.js"')) throw new Error('Ostala je referenca na izvorne fajlove');
writeFileSync(join(dist, 'index.html'), html);
cpSync(join(root, 'fonts'), join(dist, 'fonts'), { recursive: true });

// Netlify / Cloudflare Pages
writeFileSync(join(dist, '_headers'), `/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
/index.html
  Cache-Control: public, max-age=0, must-revalidate
/main.*.js
  Cache-Control: public, max-age=31536000, immutable
/fonts/*
  Cache-Control: public, max-age=31536000, immutable
`);

// Apache
writeFileSync(join(dist, '.htaccess'), `<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml
</IfModule>
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType font/woff2 "access plus 1 year"
  ExpiresByType text/html "access plus 0 seconds"
</IfModule>
<FilesMatch "(^main\\..*\\.js|\\.woff2)$">
  Header set Cache-Control "public, max-age=31536000, immutable"
</FilesMatch>
`);

const kb = n => (n / 1024).toFixed(1) + ' KB';
console.log(`dist/index.html ${kb(html.length)} (CSS ${kb(css.length)} ubačen) · ${jsName} ${kb(js.length)}`);
