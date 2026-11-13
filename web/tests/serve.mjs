import { createReadStream } from 'node:fs';
import { createServer } from 'node:http';
import { stat } from 'node:fs/promises';
import { extname, resolve, sep } from 'node:path';

const base = process.env.SITE_BASE_PATH ?? '/osint-rondonia';
const root = resolve('build');
const types = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.wasm': 'application/wasm',
  '.sqlite': 'application/vnd.sqlite3',
  '.pmtiles': 'application/vnd.pmtiles',
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
    const { size } = await stat(target);
    const headers = {
      'Accept-Ranges': 'bytes',
      'Content-Type': types[extname(target)] ?? 'application/octet-stream',
    };
    const range = request.headers.range;
    if (range) {
      const match = /^bytes=(\d+)-(\d*)$/u.exec(range);
      if (!match) {
        response.writeHead(416, { 'Content-Range': `bytes */${size}` }).end();
        return;
      }
      const start = Number(match[1]);
      const end = Math.min(match[2] ? Number(match[2]) : size - 1, size - 1);
      if (start >= size || start > end) {
        response.writeHead(416, { 'Content-Range': `bytes */${size}` }).end();
        return;
      }
      response.writeHead(206, {
        ...headers,
        'Content-Length': end - start + 1,
        'Content-Range': `bytes ${start}-${end}/${size}`,
      });
      createReadStream(target, { start, end }).pipe(response);
      return;
    }
    response.writeHead(200, { ...headers, 'Content-Length': size });
    createReadStream(target).pipe(response);
  } catch {
    response.writeHead(404).end();
  }
}).listen(4173, '127.0.0.1');
