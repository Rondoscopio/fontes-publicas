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

FROM ghcr.io/protomaps/go-pmtiles@sha256:7095e0e53e2940b6fa055611f6cd48386df6bba33fb1e5bf284f72bb42e323c2 AS pmtiles

FROM web AS web-map-builder
USER root
RUN apt-get update && apt-get install --no-install-recommends -y build-essential ca-certificates git libsqlite3-dev zlib1g-dev && rm -rf /var/lib/apt/lists/*
RUN git init /tmp/tippecanoe && git -C /tmp/tippecanoe remote add origin https://github.com/felt/tippecanoe.git && git -C /tmp/tippecanoe fetch --depth=1 origin 68ab8dcc229f95b8b25877697d5e8d66783af503 && git -C /tmp/tippecanoe checkout --detach FETCH_HEAD && make -C /tmp/tippecanoe -j2 && make -C /tmp/tippecanoe install && rm -rf /tmp/tippecanoe
COPY --from=pmtiles /go-pmtiles /usr/local/bin/pmtiles
USER node
