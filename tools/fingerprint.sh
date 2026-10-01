#!/bin/bash
# RootSpeak - Advanced Messaging System for Linux
# Code fingerprint: SHA-256 (first 12 characters) of the files that make
# RootSpeak (src/, Makefile, etc/, install.sh). The tests record it with their
# results and the technical manual compares it with the current code: a result
# is valid for the code with the same fingerprint.
#   tools/fingerprint.sh            fingerprint of the code
#   tools/fingerprint.sh --commit   commit of the repository (with -modified if there are unrecorded changes)
set -euo pipefail
cd "$(dirname "$0")/.."
if [ "${1:-}" = --commit ]; then
	c=$(git rev-parse --short=10 HEAD 2>/dev/null) || { echo unknown; exit 0; }
	git diff --quiet HEAD -- src Makefile etc install.sh 2>/dev/null || c+=-modified
	echo "$c"
	exit 0
fi
find src Makefile etc install.sh -type f -print0 | LC_ALL=C sort -z | xargs -0 sha256sum | sha256sum | cut -c1-12
