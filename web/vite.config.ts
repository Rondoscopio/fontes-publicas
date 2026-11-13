import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

const database = readFileSync(
  new URL('../data/exports/catalog.sqlite', import.meta.url),
);
const filename =
  'catalog.' + createHash('sha256').update(database).digest('hex') + '.sqlite';
const commitSha = process.env.CATALOG_BUILD_COMMIT_SHA ?? '';
const runNumber = process.env.CATALOG_BUILD_RUN_NUMBER ?? '';
const runUrl = process.env.CATALOG_BUILD_RUN_URL ?? '';
const repositoryUrl = 'https://github.com/Rondoscopio/osint-rondonia';

export default defineConfig({
  define: {
    __CATALOG_FILE__: JSON.stringify(filename),
    __BUILD_INFO__: JSON.stringify({
      commit: commitSha.slice(0, 7),
      commitUrl: commitSha ? `${repositoryUrl}/commit/${commitSha}` : '',
      runNumber,
      runUrl,
    }),
  },
  plugins: [
    {
      name: 'catalog-database',
      generateBundle() {
        this.emitFile({ type: 'asset', fileName: filename, source: database });
      },
      configureServer(server) {
        server.middlewares.use((request, response, next) => {
          if (request.url?.split('?')[0] !== server.config.base + filename)
            return next();
          response.setHeader('Content-Type', 'application/vnd.sqlite3');
          response.end(database);
        });
      },
    },
    sveltekit(),
  ],
});
