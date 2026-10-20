// Renderuje baner.html u PNG: node baner/render.mjs
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

// require() postuje NODE_PATH, pa radi i sa globalno instaliranim Playwright-om
const { chromium } = createRequire(import.meta.url)("playwright");

const dir = path.dirname(fileURLToPath(import.meta.url));
const page_url = pathToFileURL(path.join(dir, "baner.html")).href;

const formats = [
  { name: "logoforge-baner-1920x1080.png", w: 1920, h: 1080, query: "" },
  { name: "logoforge-baner-1080x1080.png", w: 1080, h: 1080, query: "?format=square" },
];

const browser = await chromium.launch();
for (const f of formats) {
  const page = await browser.newPage({ viewport: { width: f.w, height: f.h }, deviceScaleFactor: 1 });
  await page.goto(page_url + f.query);
  await page.evaluate(() => document.fonts.ready);
  await page.locator("#banner").screenshot({ path: path.join(dir, f.name) });
  await page.close();
  console.log("✓", f.name);
}
await browser.close();
