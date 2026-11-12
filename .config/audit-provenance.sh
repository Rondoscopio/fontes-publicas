#!/bin/sh
set -eu

printf 'git_revision=%s\n' "$(git rev-parse HEAD)"
printf 'catalog_image_id=%s\n' "$1"
printf 'catalog_image_digest=%s\n' "$2"
printf 'catalog_image_archive_sha256='
sha256sum "$3"
printf 'working_tree_changes='
git status --porcelain | wc -l
printf 'sqlite_worktree_sha256='
sha256sum data/exports/catalog.sqlite
