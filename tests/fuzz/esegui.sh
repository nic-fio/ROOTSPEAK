#!/bin/bash
# AMS - Advanced Messaging System
# Fuzzing con libFuzzer (clang) in un container Debian 13, senza toccare il
# sistema: compila tests/fuzz/fuzz.c con AddressSanitizer e UBSan e lo lancia
# per ogni bersaglio. Un difetto ferma il fuzzing e lascia il caso in
# tests/fuzz/risultati/.
#   tests/fuzz/esegui.sh [SECONDI_PER_BERSAGLIO]      (predefinito 60)
set -uo pipefail
QUI=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$QUI/../.." && pwd)
SEC=${1:-60}
IMG=ams-fuzz
mkdir -p "$QUI/risultati"
if ! podman image exists $IMG; then
	printf 'FROM docker.io/library/debian:trixie\nRUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends clang libclang-rt-dev libsystemd-dev pkg-config libc6-dev && rm -rf /var/lib/apt/lists/*\n' |
		podman build -q -t $IMG -f - "$QUI" >/dev/null || exit 1
fi
podman run --rm -v "$ROOT:/src:ro,Z" -v "$QUI/risultati:/out:Z" $IMG bash -c "
	set -e
	cd /tmp
	clang -g -O1 -std=c17 -D_GNU_SOURCE -fsanitize=fuzzer,address,undefined -fno-sanitize-recover=undefined \
		-I/src/src /src/tests/fuzz/fuzz.c /src/src/comune.c /src/src/testo.c /src/src/lingua.c \
		/src/src/archivio.c /src/src/utente.c /src/src/sessioni.c /src/src/evento.c \
		-o fuzz \$(pkg-config --libs libsystemd)
	esito=0
	for b in 0 1 2 3 4 5; do
		mkdir -p semi\$b
		printf \"\\\\x0\$b\" > semi\$b/zero
		if ./fuzz -max_total_time=$SEC -max_len=4096 -artifact_prefix=/out/bersaglio\$b- -print_final_stats=0 semi\$b 2>log\$b; then
			echo \"bersaglio \$b: nessun difetto (\$(grep -o 'cov: [0-9]*' log\$b | tail -1), \$(grep -o 'Done [0-9]* runs' log\$b | tail -1))\"
		else
			echo \"bersaglio \$b: DIFETTO\"; tail -30 log\$b; esito=1
		fi
	done
	exit \$esito
"
