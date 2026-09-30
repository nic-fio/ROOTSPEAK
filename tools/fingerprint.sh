#!/bin/bash
# AMS - Advanced Messaging System
# Impronta del codice: SHA-256 (primi 12 caratteri) dei file che fanno AMS
# (src/, po/, Makefile, etc/, install.sh). Le prove la registrano con i risultati e il
# manuale tecnico la confronta con il codice attuale: un risultato vale per il
# codice con la stessa impronta.
#   tools/fingerprint.sh            impronta del codice
#   tools/fingerprint.sh --commit   commit del repository (con -modificato se ci sono modifiche non registrate)
set -euo pipefail
cd "$(dirname "$0")/.."
if [ "${1:-}" = --commit ]; then
	c=$(git rev-parse --short=10 HEAD 2>/dev/null) || { echo sconosciuto; exit 0; }
	git diff --quiet HEAD -- src po Makefile etc install.sh 2>/dev/null || c+=-modificato
	echo "$c"
	exit 0
fi
find src po Makefile etc install.sh -type f -print0 | LC_ALL=C sort -z | xargs -0 sha256sum | sha256sum | cut -c1-12
