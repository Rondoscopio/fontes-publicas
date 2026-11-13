import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { extname, resolve, sep } from 'node:path';

const base = process.env.SITE_BASE_PATH ?? '/osint-rondonia';
const root = resolve('build');
const types = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.wasm': 'application/wasm',
  '.sqlite': 'application/vnd.sqlite3',
  '.woff2': 'font/woff2',
};

createServer(async (request, response) => {
  try {
    const path = new URL(request.url, 'http://localhost').pathname;
    if (!path.startsWith(base + '/')) throw new Error('Not found');
    const file = resolve(
      root,
      '.' + decodeURIComponent(path.slice(base.length)),
    );
    if (file !== root && !file.startsWith(root + sep))
      throw new Error('Not found');
    const target = (await stat(file)).isDirectory()
      ? resolve(file, 'index.html')
      : file;
    const data = await readFile(target);
    response.writeHead(200, {
      'Content-Type': types[extname(target)] ?? 'application/octet-stream',
    });
    response.end(data);
  } catch {
    response.writeHead(404).end();
  }
}).listen(4173, '127.0.0.1');
