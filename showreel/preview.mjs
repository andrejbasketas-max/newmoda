import { chromium } from 'playwright';
import fs from 'fs';
const frames = process.argv.slice(2).map(Number);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--allow-file-access-from-files'] }).catch(() => chromium.launch({ args: ['--allow-file-access-from-files'] }));
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
p.on('pageerror', e => console.log('ERR', e.message)); p.on('console', m => console.log('LOG', m.text()));
await p.goto('file://' + process.cwd() + '/reel.html');
await p.evaluate(() => window.ready);
fs.mkdirSync('prev', { recursive: true });
for (const f of frames) {
  const t0 = Date.now();
  const d = await p.evaluate(f => { renderFrame(f); return document.getElementById('c').toDataURL('image/png'); }, f);
  fs.writeFileSync(`prev/f${String(f).padStart(4, '0')}.png`, Buffer.from(d.split(',')[1], 'base64'));
  console.log(f, Date.now() - t0, 'ms');
}
await b.close();
