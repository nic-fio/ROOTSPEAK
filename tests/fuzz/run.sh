#!/bin/bash
# RootSpeak - Advanced Messaging System for Linux
# Fuzzing with libFuzzer (clang) in a Debian 13 container, without touching the
# system: builds tests/fuzz/fuzz.c with AddressSanitizer and UBSan and runs it
# for each target. A defect stops the fuzzing and leaves the case in
# tests/fuzz/results/.
#   tests/fuzz/run.sh [SECONDS_PER_TARGET]      (default 60)
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
SEC=${1:-60}
IMG=rootspeak-fuzz
mkdir -p "$HERE/results"
if ! podman image exists $IMG; then
	printf 'FROM docker.io/library/debian:trixie\nRUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends clang libclang-rt-dev libsystemd-dev pkg-config libc6-dev && rm -rf /var/lib/apt/lists/*\n' |
		podman build -q -t $IMG -f - "$HERE" >/dev/null || exit 1
fi
podman run --rm -v "$ROOT:/src:ro,Z" -v "$HERE/results:/out:Z" $IMG bash -c "
	set -e
	cd /tmp
	clang -g -O1 -std=c17 -D_GNU_SOURCE -fsanitize=fuzzer,address,undefined -fno-sanitize-recover=undefined \
		-I/src/src /src/tests/fuzz/fuzz.c /src/src/common.c /src/src/text.c \
		/src/src/store.c /src/src/user.c /src/src/sessions.c /src/src/event.c \
		-o fuzz \$(pkg-config --libs libsystemd)
	status=0
	for b in 0 1 2 3; do
		mkdir -p seeds\$b
		printf \"\\\\x0\$b\" > seeds\$b/zero
		if ./fuzz -max_total_time=$SEC -max_len=4096 -artifact_prefix=/out/target\$b- -print_final_stats=0 seeds\$b 2>log\$b; then
			echo \"target \$b: no defects (\$(grep -o 'cov: [0-9]*' log\$b | tail -1), \$(grep -o 'Done [0-9]* runs' log\$b | tail -1))\"
		else
			echo \"target \$b: DEFECT\"; tail -30 log\$b; status=1
		fi
	done
	exit \$status
"
