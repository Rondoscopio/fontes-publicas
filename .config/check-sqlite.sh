#!/bin/sh
set -eu

artifact=data/exports/catalog.sqlite
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

if ! git show "HEAD:$artifact" >"$scratch/revision.sqlite"; then
    echo "SQLite ausente na revisão. Execute just sqlite e inclua $artifact no commit." >&2
    exit 1
fi

python scripts/export_sqlite.py --output "$scratch/generated.sqlite"
if ! cmp -s "$scratch/revision.sqlite" "$scratch/generated.sqlite"; then
    echo "SQLite divergente. Execute just sqlite e inclua $artifact atualizado no commit." >&2
    exit 1
fi
sha256sum "$scratch/generated.sqlite"
