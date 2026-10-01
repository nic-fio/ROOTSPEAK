#!/bin/bash
# RootSpeak - Advanced Messaging System for Linux
# Real-world tests in a test machine (container with systemd, without root):
# builds the image if it is missing, starts the machine, installs RootSpeak from the
# repository, runs the scenarios and saves the results in tests/container/results/.
#   tests/container/run.sh            (--rebuild to build the image again)
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
NAME=rootspeak-test
mkdir -p "$HERE/results"

if [ "${1:-}" = --rebuild ] || ! podman image exists $NAME; then
	echo "building the image…"
	podman build -q -t $NAME -f "$HERE/Containerfile" "$HERE" >/dev/null || exit 1
fi
podman rm -f $NAME >/dev/null 2>&1
podman run -d --name $NAME --systemd=always \
	-v "$ROOT:/opt/rootspeak-src:ro,Z" -v "$HERE/results:/opt/results:Z" $NAME >/dev/null || exit 1
trap 'podman rm -f $NAME >/dev/null 2>&1' EXIT
for i in $(seq 1 30); do
	s=$(podman exec $NAME systemctl is-system-running 2>/dev/null)
	[ "$s" = running ] || [ "$s" = degraded ] && break
	sleep 1
done
echo "test machine: $s"
podman exec $NAME /opt/rootspeak-src/install.sh 2>&1 | grep -v '^Warning: zenity is missing' | head -1
# the system language of the test machine is Italian on purpose: RootSpeak must speak English anyway
podman exec -e LANG=it_IT.UTF-8 -e RSPEAK_TEST_COMMIT="$("$ROOT/tools/fingerprint.sh" --commit)" \
	-e RSPEAK_TEST_FINGERPRINT="$("$ROOT/tools/fingerprint.sh")" -e RSPEAK_TEST_ONLY="${RSPEAK_TEST_ONLY:-}" \
	$NAME python3 /opt/rootspeak-src/tests/container/scenarios.py /opt/results
