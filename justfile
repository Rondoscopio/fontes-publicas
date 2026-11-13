set shell := ["bash", "-euo", "pipefail", "-c"]

compose := "docker compose -f .config/compose.yaml"
export CATALOG_UID := `id -u`
export CATALOG_GID := `id -g`

default:
    @just --list

build:
    {{compose}} build catalog

import-ibge: build
    {{compose}} run --rm import-ibge python scripts/import_ibge.py

validate: build
    {{compose}} run --rm catalog frictionless validate datapackage.json
    {{compose}} run --rm catalog python scripts/validate_package.py

test: build
    {{compose}} run --rm catalog python -m unittest discover -s tests -v

sqlite: validate
    {{compose}} run --rm sqlite python scripts/export_sqlite.py

check: lint test validate sqlite-check web-check

web-image:
    {{compose}} build web

web-add *ARGS:
    mkdir -p .cache/pnpm web/node_modules
    {{compose}} build web
    {{compose}} run --rm web-deps pnpm install --store-dir /pnpm/store
    {{compose}} run --rm web-deps pnpm add --store-dir /pnpm/store --save-exact {{ARGS}}

web-clean-deps: web-image
    {{compose}} run --rm --entrypoint sh web-deps -euc 'find node_modules -mindepth 1 -maxdepth 1 -exec rm -rf {} +'

web-add-dev *ARGS:
    mkdir -p .cache/pnpm web/node_modules
    {{compose}} build web
    {{compose}} run --rm web-deps pnpm install --store-dir /pnpm/store
    {{compose}} run --rm web-deps pnpm add --store-dir /pnpm/store --save-dev --save-exact {{ARGS}}

import-map: web-image
    mkdir -p .cache/geodata web/static/maps
    {{compose}} run --rm web-map-import

web-dev: web-image
    mkdir -p .local/web-dev-kit .local/web-vite-temp .local/web-vite-cache
    SITE_BASE_PATH= {{compose}} run --rm --service-ports web-dev

web-check:
    {{compose}} build web-check
    {{compose}} run --rm web-check sh -euc 'pnpm check && pnpm test && pnpm build && pnpm test:browser'

web-format:
    {{compose}} build web-check
    {{compose}} run --rm web-format

web-build: web-image
    mkdir -p .local/site .local/web-kit .local/web-vite-temp .local/web-vite-cache
    SITE_BASE_PATH=/osint-rondonia {{compose}} run --rm -e WEB_OUTPUT_DIR=/output/site web-build

clean-cache:
    rm -rf .cache .local/share/osint-rondonia

quality-image:
    {{compose}} build quality

lint: quality-image
    {{compose}} build markdown
    {{compose}} run --rm quality actionlint
    {{compose}} run --rm quality zizmor --offline .github/workflows
    {{compose}} run --rm quality hadolint .config/container/Dockerfile
    {{compose}} run --rm quality yamllint -c .config/yamllint.yml .github/workflows .github/ISSUE_TEMPLATE .config/compose.yaml
    {{compose}} run --rm quality ruff check --config .config/ruff.toml scripts tests
    {{compose}} run --rm quality ruff format --check --config .config/ruff.toml scripts tests
    {{compose}} run --rm quality shellcheck .config/check-sqlite.sh .config/audit-provenance.sh
    {{compose}} run --rm quality shfmt -d -i 4 .config/check-sqlite.sh .config/audit-provenance.sh
    {{compose}} run --rm markdown --config .config/markdownlint.json README.md docs .github/pull_request_template.md
    {{compose}} run --rm links-offline --offline --no-progress --cache=false README.md 'docs/**/*.md' .github/pull_request_template.md
    {{compose}} run --rm quality gitleaks dir --redact --config .config/gitleaks.toml .

sqlite-check: quality-image
    {{compose}} run --rm quality sh .config/check-sqlite.sh

audit: build quality-image
    #!/usr/bin/env bash
    set -euo pipefail
    {{compose}} build audit
    mkdir -p .local/audit .cache/trivy
    report_dir="$(mktemp -d .local/audit/run.XXXXXXXX)"
    image=osint-rondonia-catalog:local
    image_id="$(docker image inspect --format '{{{{.Id}}' "$image")"
    image_digest="$(docker image inspect --format '{{{{json .RepoDigests}}' "$image")"
    archive="$(mktemp .local/audit-image.XXXXXXXX)"
    trap 'rm -f "$archive"' EXIT
    docker save "$image_id" -o "$archive"
    status=0
    run_report() {
        local filename="$1" code=0
        local findings="$2" result=ok
        shift 2
        "$@" > "$report_dir/$filename" || code=$?
        if [[ "$code" != 0 ]]; then
            result=error
            if [[ "$code" == "$findings" ]]; then result=findings; fi
        fi
        printf '%s\t%s\t%s\n' "$filename" "$result" "$code" >> "$report_dir/results.tsv"
        if [[ "$code" != 0 ]]; then status=1; fi
    }
    run_report provenance.txt - {{compose}} run --rm -T quality sh .config/audit-provenance.sh "$image_id" "$image_digest" "$archive"
    run_report trivy.json - {{compose}} run --rm -T audit trivy --cache-dir /trivy-cache image --input "$archive" --scanners vuln --format json
    run_report trivy-policy.txt 10 {{compose}} run --rm -T quality python scripts/check_trivy.py "$report_dir/trivy.json"
    run_report image.cdx.json - {{compose}} run --rm -T audit trivy --cache-dir /trivy-cache image --input "$archive" --format cyclonedx
    run_report sbom-schema.txt - {{compose}} run --rm -T sbom validate --input-file "/reports/${report_dir##*/}/image.cdx.json" --input-format json --fail-on-errors
    run_report sbom-image.txt - {{compose}} run --rm -T quality python scripts/check_sbom.py "$report_dir/image.cdx.json" "$archive"
    run_report osv.json 1 {{compose}} run --rm -T audit osv-scanner scan source --lockfile .config/container/requirements.txt --format json
    run_report osv-web.json 1 {{compose}} run --rm -T audit osv-scanner scan source --lockfile web/pnpm-lock.yaml --format json
    run_report semgrep.json 1 {{compose}} run --rm -T semgrep scan --config p/python --metrics=off --error --json scripts
    links_code=0
    {{compose}} run --rm -T links --no-progress --cache=false --max-concurrency 4 --max-retries 0 --timeout 8 --exclude-all-private --scheme https --scheme http --format json README.md 'docs/**/*.md' > "$report_dir/links.json" || links_code=$?
    printf 'links.json\tinformativo\t%s\n' "$links_code" >> "$report_dir/results.tsv"
    echo "Relatórios: $report_dir"
    exit "$status"
