#!/bin/sh
# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Packs the whole project into a single file: a git bundle with every branch,
# every tag and the complete history. It is restored without network and
# without GitHub:
#
#     tools/backup.sh ~/backup                 # writes rspeak-YYYY-MM-DD.bundle
#     git clone rspeak-2026-09-30.bundle RootSpeak
#     cd RootSpeak && tools/setup-dev.sh --install && make test
#
# RootSpeak has no personal files outside the repository: the bundle is enough.
# The base disk of the test VM lives on the test server and is rebuilt with
# tests/vm/run.sh --prepare.
set -eu

DEST=${1:-.}
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DAY=$(date +%F)
OUT="$DEST/rspeak-$DAY.bundle"

[ -d "$DEST" ] || mkdir -p "$DEST"
git -C "$ROOT" bundle create "$OUT" --all
git -C "$ROOT" bundle verify "$OUT" >/dev/null

if [ -n "$(git -C "$ROOT" status --porcelain)" ]; then
    echo "warning: the changes not yet committed are NOT in the bundle:"
    git -C "$ROOT" status --short
fi
if [ -n "$(git -C "$ROOT" log --oneline '@{upstream}..HEAD' 2>/dev/null)" ]; then
    echo "note: the bundle has commits that are not on GitHub yet."
fi

printf '%s: %s, %s commits, tags: %s\n' "$OUT" "$(du -h "$OUT" | cut -f1)" \
    "$(git -C "$ROOT" rev-list --count HEAD)" \
    "$(git -C "$ROOT" tag | tr '\n' ' ')"
