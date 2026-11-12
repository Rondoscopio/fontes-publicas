FROM rhysd/actionlint:1.7.12@sha256:b1934ee5f1c509618f2508e6eb47ee0d3520686341fec936f3b79331f9315667 AS actionlint
FROM ghcr.io/zizmorcore/zizmor:1.31.1@sha256:42d409dbb851d4c5d35a058cf042b828bea1e3f2884378c526eb0974780e18d9 AS zizmor
FROM hadolint/hadolint:v2.15.1@sha256:32dac94127fd60b7b7e3fbfc65e1383b9b5e25c9bfd7b8536de7a539fe68a12d AS hadolint
FROM zricethezav/gitleaks:v8.30.1@sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f AS gitleaks
FROM ghcr.io/google/osv-scanner:v2.5.1@sha256:8108ae94eadea5a02c9bec6e646909d5b790b44bd62d7f5b7f0b1d6d0ffc7734 AS osv
FROM aquasec/trivy:0.74.0@sha256:62b1e65e8869bc4b4c6aa4fa2b21595256c7c2f6018a9d9ad61caf87187c1969 AS trivy
FROM mvdan/shfmt:v3.12.0@sha256:307d265ffd25ce832899ae17c93ed5062fc3375c514bba8f52cbf52792735c4d AS shfmt
FROM node:22-bookworm-slim@sha256:e9f565d32859f0cbfb52125eafe8be39390f24dac302dc3cdf566e8ba3ab21ee AS markdown
RUN npm install --global --ignore-scripts markdownlint-cli@0.45.0

FROM python:3.12-slim-trixie@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b AS catalog-build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    XDG_CONFIG_HOME=/workspace/.config \
    XDG_CACHE_HOME=/workspace/.cache \
    XDG_DATA_HOME=/workspace/.local/share

WORKDIR /workspace

COPY .config/container/requirements.txt /opt/catalog/requirements.txt
RUN apt-get update \
    && apt-get install -y --no-install-recommends 'zlib1g=1:1.3.dfsg+really1.3.1-1+deb13u1' \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --no-cache-dir pip==26.3 setuptools==84.2.1 \
    && python -m pip install --no-cache-dir -r /opt/catalog/requirements.txt \
    && python -m pip check

CMD ["frictionless", "--help"]

FROM catalog-build AS catalog
# The runtime uses the resolved packages and does not need pip or its vendored code.
RUN python -m pip uninstall --yes pip

FROM catalog-build AS quality

# Git and ShellCheck receive Debian updates in the tooling image only.
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends git shellcheck \
    && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir ruff==0.15.20 yamllint==1.38.0

COPY --from=actionlint /usr/local/bin/actionlint /usr/local/bin/actionlint
COPY --from=zizmor /usr/bin/zizmor /usr/local/bin/zizmor
COPY --from=hadolint /bin/hadolint /usr/local/bin/hadolint
COPY --from=gitleaks /usr/bin/gitleaks /usr/local/bin/gitleaks
COPY --from=shfmt /bin/shfmt /usr/local/bin/shfmt

ENV GIT_CONFIG_COUNT=1 \
    GIT_CONFIG_KEY_0=safe.directory \
    GIT_CONFIG_VALUE_0=/workspace

FROM quality AS audit
COPY --from=osv /osv-scanner /usr/local/bin/osv-scanner
COPY --from=trivy /usr/local/bin/trivy /usr/local/bin/trivy
