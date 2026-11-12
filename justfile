set shell := ["bash", "-euo", "pipefail", "-c"]

compose := "docker compose -f .config/compose.yaml"

default:
    @just --list

build:
    {{compose}} build catalog

validate: build
    {{compose}} run --rm catalog frictionless validate datapackage.json
    {{compose}} run --rm catalog python scripts/validate_package.py

test: build
    {{compose}} run --rm catalog python -m unittest discover -s tests -v

sqlite: validate
    {{compose}} run --rm catalog python scripts/export_sqlite.py

check: lint test validate sqlite-check

clean-cache:
    {{compose}} run --rm --entrypoint python catalog -c "import shutil; from pathlib import Path; [shutil.rmtree(path, ignore_errors=True) for path in (Path('/workspace/.cache'), Path('/workspace/.local/share/osint-rondonia'))]"

quality-image:
    {{compose}} build quality

lint: quality-image
    {{compose}} run --rm quality actionlint
    {{compose}} run --rm quality zizmor --offline .github/workflows
    {{compose}} run --rm quality hadolint .config/container/Dockerfile
    {{compose}} run --rm quality yamllint -c .config/yamllint.yml .github/workflows .config/compose.yaml
    {{compose}} run --rm quality ruff check --config .config/ruff.toml scripts tests
    {{compose}} run --rm quality ruff format --check --config .config/ruff.toml scripts tests
    {{compose}} run --rm quality shellcheck .config/check-sqlite.sh .config/audit-provenance.sh
    {{compose}} run --rm quality gitleaks dir --redact --config .config/gitleaks.toml .

sqlite-check: quality-image
    {{compose}} run --rm quality sh .config/check-sqlite.sh

audit: build
    #!/usr/bin/env bash
    set -euo pipefail
    {{compose}} build audit
    mkdir -p .local/audit .cache/trivy
    report_dir="$(mktemp -d .local/audit/run.XXXXXXXX)"
    image=osint-rondonia-catalog:local
    image_id="$(docker image inspect --format '{{{{.Id}}' "$image")"
    archive="$(mktemp .local/audit-image.XXXXXXXX)"
    trap 'rm -f "$archive"' EXIT
    docker save "$image_id" -o "$archive"
    status=0
    run_report() {
        local filename="$1" code=0
        shift
        "$@" > "$report_dir/$filename" || code=$?
        printf '%s=%s\n' "$filename" "$code" >> "$report_dir/exit-codes.txt"
        if [[ "$code" != 0 ]]; then status=1; fi
    }
    run_report provenance.txt {{compose}} run --rm -T audit sh .config/audit-provenance.sh "$image_id"
    run_report trivy.json {{compose}} run --rm -T audit trivy --cache-dir /workspace/.cache/trivy image --input "$archive" --scanners vuln --exit-code 10 --format json
    run_report image.cdx.json {{compose}} run --rm -T audit trivy --cache-dir /workspace/.cache/trivy image --input "$archive" --format cyclonedx
    run_report osv.json {{compose}} run --rm -T audit osv-scanner scan source --lockfile .config/container/requirements.txt --format json
    run_report semgrep.json {{compose}} run --rm -T semgrep scan --config p/python --metrics=off --error --json scripts
    echo "Relatórios: $report_dir"
    exit "$status"
