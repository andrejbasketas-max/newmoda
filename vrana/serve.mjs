// Mali server sa gzip/brotli i keš zaglavljima, sličan pravom hostingu (za test: node vrana/serve.mjs [dist|.] [port])
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { brotliCompressSync, gzipSync } from 'node:zlib';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';

const base = join(fileURLToPath(new URL('.', import.meta.url)), process.argv[2] || 'dist');
const port = +process.argv[3] || 8750;
const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.woff2': 'font/woff2' };

createServer(async (req, res) => {
  let p = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname)).replace(/^(\.\.[/\\])+/, '');
  if (p.endsWith('/')) p += 'index.html';
  try {
    let body = await readFile(join(base, p));
    const ext = extname(p);
    const h = { 'Content-Type': types[ext] || 'application/octet-stream', Vary: 'Accept-Encoding' };
    h['Cache-Control'] = /main\.[0-9a-f]{8}\.js$|\.woff2$/.test(p) ? 'public, max-age=31536000, immutable' : ext === '.html' ? 'public, max-age=0, must-revalidate' : 'public, max-age=3600';
    const ae = req.headers['accept-encoding'] || '';
    if (['.html', '.js', '.css'].includes(ext)) {
      if (ae.includes('br')) { body = brotliCompressSync(body); h['Content-Encoding'] = 'br'; }
      else if (ae.includes('gzip')) { body = gzipSync(body); h['Content-Encoding'] = 'gzip'; }
    }
    h['Content-Length'] = body.length;
    res.writeHead(200, h).end(body);
  } catch { res.writeHead(404).end('404'); }
}).listen(port, () => console.log(`http://localhost:${port}`));
