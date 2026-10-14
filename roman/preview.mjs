// Renders chosen frames (or test modes) to PNGs for review. Usage: node preview.mjs film|test <frames...>
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs';
const [page_, ...ids] = process.argv.slice(2);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--allow-file-access-from-files', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
p.on('pageerror', e => console.log('ERR', e.message)); p.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.log(m.text()); });
await p.goto('file://' + process.cwd() + '/' + page_ + '.html'); await p.waitForFunction(() => window.ready, null, { timeout: 120000 });
fs.mkdirSync('preview', { recursive: true });
for (const id of ids) {
  const d = await p.evaluate((id) => { window.show(+id); return document.getElementById(window.OUT_ID || 'c').toDataURL('image/jpeg', 0.9); }, id);
  fs.writeFileSync(`preview/${page_}-${id}.jpg`, Buffer.from(d.split(',')[1], 'base64'));
}
await b.close();
