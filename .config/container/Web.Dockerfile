FROM node:24-bookworm-slim@sha256:dc26ae92c9fb15cf6b1d63e20f0944b2efe0f115b20e00be48fb23fceb061c54 AS web
RUN npm install --global --ignore-scripts pnpm@10.34.9
WORKDIR /workspace/web
COPY web/package.json web/pnpm-lock.yaml ./
RUN chown node:node /workspace/web
USER node
RUN --mount=type=cache,target=/pnpm/store,uid=1000,gid=1000 pnpm install --frozen-lockfile --store-dir /pnpm/store
RUN mkdir -p /workspace/web/node_modules/.vite-temp /workspace/web/node_modules/.vite
USER root
RUN /workspace/web/node_modules/.bin/playwright install-deps chromium
USER node
RUN pnpm exec playwright install --only-shell chromium
ENV PLAYWRIGHT_BROWSERS_PATH=/home/node/.cache/ms-playwright
COPY web/ ./
COPY data/exports/catalog.sqlite ../data/exports/catalog.sqlite

FROM web AS web-check
