// Renders reel.html frame by frame in headless Chromium, encodes segments in parallel,
// then concatenates them and muxes music.wav. Output: showreel.mp4 (1920x1080, 60 fps).
import { chromium } from 'playwright';
import { spawn, execFileSync } from 'child_process';
import fs from 'fs';

const TOTAL = 900, WORKERS = 3, SUB = 6;
const exe = fs.existsSync('/opt/pw-browsers/chromium') ? '/opt/pw-browsers/chromium' : undefined;
const browser = await chromium.launch({ executablePath: exe, args: ['--allow-file-access-from-files'] }).catch(() => chromium.launch({ args: ['--allow-file-access-from-files'] }));
fs.mkdirSync('build', { recursive: true });
const t0 = Date.now();

async function worker(w) {
  const from = Math.floor((TOTAL * w) / WORKERS), to = Math.floor((TOTAL * (w + 1)) / WORKERS);
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('pageerror', e => console.error('page error', e.message));
  await page.goto('file://' + process.cwd() + '/reel.html');
  await page.evaluate(() => window.ready);
  // warm up state that depends on previous frames (none today, but keeps segments independent)
  const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', '60', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-g', '60', '-bf', '2',
    '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', `build/seg${w}.mp4`], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = from; f < to; f++) {
    const d = await page.evaluate(([f, s]) => { renderFrame(f, s); return document.getElementById('c').toDataURL('image/png'); }, [f, SUB]);
    if (!ff.stdin.write(Buffer.from(d.slice(22), 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - from) % 60 === 0) console.log(`worker ${w}: frame ${f} (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
}
await Promise.all(Array.from({ length: WORKERS }, (_, w) => worker(w)));
await browser.close();
fs.writeFileSync('build/list.txt', Array.from({ length: WORKERS }, (_, w) => `file 'seg${w}.mp4'`).join('\n'));
execFileSync('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'build/list.txt', '-i', 'music.wav',
  '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '320k', '-t', '15', '-movflags', '+faststart', 'showreel.mp4']);
console.log(`done in ${((Date.now() - t0) / 1000).toFixed(0)} s`);
