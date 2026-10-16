// Render every SVG in <svgDir> to a 1920x1080 PNG in <pngDir> using headless Chromium.
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const [svgDir, pngDir, filter] = process.argv.slice(2);
fs.mkdirSync(pngDir, { recursive: true });
const files = fs.readdirSync(svgDir).filter(f => f.endsWith('.svg') && (!filter || new RegExp(filter).test(f))).sort();
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || undefined });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
for (const f of files) {
  const svg = fs.readFileSync(path.join(svgDir, f), 'utf8');
  await page.setContent(`<html><body style="margin:0;overflow:hidden">${svg}</body></html>`);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(pngDir, f.replace(/\.svg$/, '.png')), clip: { x: 0, y: 0, width: 1920, height: 1080 } });
}
await browser.close();
console.log(`rendered ${files.length}`);
