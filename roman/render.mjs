// Renders film.html frame by frame in headless Chromium (4 workers), encodes segments, joins them and muxes audio.wav.
// Usage: node render.mjs [from] [to]  → roman-soldier-2026.mp4 (1080x1920, 30 fps, 60 s)
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { spawn, execFileSync } from 'child_process';
import fs from 'fs';
const TOTAL = 1800, WORKERS = +(process.env.WORKERS || 4), FPS = 30;
const FROM = +(process.argv[2] || 0), TO = +(process.argv[3] || TOTAL);
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--allow-file-access-from-files', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
fs.mkdirSync('build', { recursive: true });
const t0 = Date.now();
async function worker(w) {
  const from = FROM + Math.floor(((TO - FROM) * w) / WORKERS), to = FROM + Math.floor(((TO - FROM) * (w + 1)) / WORKERS);
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', (e) => console.error('page error', e.message));
  await page.goto('file://' + process.cwd() + '/film.html'); await page.waitForFunction(() => window.ready, null, { timeout: 180000 });
  const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-g', '30', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', `build/seg${w}.mp4`], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = from; f < to; f++) {
    const d = await page.evaluate((f) => { window.renderFrame(f); return document.getElementById('c').toDataURL('image/jpeg', 0.95); }, f);
    if (!ff.stdin.write(Buffer.from(d.slice(23), 'base64'))) await new Promise((r) => ff.stdin.once('drain', r));
    if ((f - from) % 90 === 0) console.log(`worker ${w}: frame ${f}/${to} (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
  }
  ff.stdin.end(); await new Promise((r) => ff.on('close', r));
}
await Promise.all(Array.from({ length: WORKERS }, (_, w) => worker(w)));
await browser.close();
fs.writeFileSync('build/list.txt', Array.from({ length: WORKERS }, (_, w) => `file 'seg${w}.mp4'`).join('\n'));
execFileSync('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'build/list.txt', '-i', 'audio.wav',
  '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-t', String((TO - FROM) / FPS), '-movflags', '+faststart', 'roman-soldier-2026.mp4']);
console.log(`done in ${((Date.now() - t0) / 1000).toFixed(0)} s`);
