FROM rhysd/actionlint:1.7.12@sha256:b1934ee5f1c509618f2508e6eb47ee0d3520686341fec936f3b79331f9315667 AS actionlint
FROM ghcr.io/zizmorcore/zizmor:1.31.1@sha256:42d409dbb851d4c5d35a058cf042b828bea1e3f2884378c526eb0974780e18d9 AS zizmor
FROM hadolint/hadolint:v2.15.1@sha256:32dac94127fd60b7b7e3fbfc65e1383b9b5e25c9bfd7b8536de7a539fe68a12d AS hadolint
FROM zricethezav/gitleaks:v8.30.1@sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f AS gitleaks
FROM ghcr.io/google/osv-scanner:v2.5.1@sha256:8108ae94eadea5a02c9bec6e646909d5b790b44bd62d7f5b7f0b1d6d0ffc7734 AS osv
FROM aquasec/trivy:0.74.0@sha256:62b1e65e8869bc4b4c6aa4fa2b21595256c7c2f6018a9d9ad61caf87187c1969 AS trivy

FROM python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df AS catalog

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    XDG_CONFIG_HOME=/workspace/.config \
    XDG_CACHE_HOME=/workspace/.cache \
    XDG_DATA_HOME=/workspace/.local/share

WORKDIR /workspace

COPY .config/container/requirements.txt /opt/catalog/requirements.txt
RUN python -m pip install --no-cache-dir -r /opt/catalog/requirements.txt \
    && python -m pip check

CMD ["frictionless", "--help"]

FROM catalog AS quality

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

ENV GIT_CONFIG_COUNT=1 \
    GIT_CONFIG_KEY_0=safe.directory \
    GIT_CONFIG_VALUE_0=/workspace

FROM quality AS audit
COPY --from=osv /osv-scanner /usr/local/bin/osv-scanner
COPY --from=trivy /usr/local/bin/trivy /usr/local/bin/trivy
