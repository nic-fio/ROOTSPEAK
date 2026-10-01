#!/bin/bash
# RootSpeak - Advanced Messaging System for Linux
# Real-world tests in a test machine (container with systemd, without root):
# builds the image if it is missing, starts the machine, builds and installs
# RootSpeak there from a copy of the repository, runs the scenarios and saves the
# results in tests/container/results/.
#   tests/container/run.sh            (--rebuild to build the image again)
# Debian 13 by default; tests/distros/run.sh uses it for the other distributions with
#   RSPEAK_BASE (image of the distribution), RSPEAK_NAME (name of image and machine)
#   RSPEAK_IMAGE (image name, if different), RSPEAK_RESULTS (results folder) and
#   RSPEAK_PODMAN_ROOT (where podman keeps images and machines).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
NAME=${RSPEAK_NAME:-rootspeak-test}
IMAGE=${RSPEAK_IMAGE:-$NAME}
RESULTS=${RSPEAK_RESULTS:-$HERE/results}
BUILD=()
[ -n "${RSPEAK_BASE:-}" ] && BUILD=(--build-arg "BASE=$RSPEAK_BASE")
mkdir -p "$RESULTS"
# (--root, not a storage.conf: rootless podman ignores the graphroot of CONTAINERS_STORAGE_CONF)
podman() { command podman ${RSPEAK_PODMAN_ROOT:+--root "$RSPEAK_PODMAN_ROOT"} "$@"; }

if [ "${1:-}" = --rebuild ] || ! podman image exists "$IMAGE"; then
	echo "building the image…"
	podman build -t "$IMAGE" "${BUILD[@]}" -f "$HERE/Containerfile" "$HERE" >"$RESULTS/image.log" 2>&1 ||
		{ tail -20 "$RESULTS/image.log"; exit 1; }
fi
podman rm -f "$NAME" >/dev/null 2>&1
podman run -d --name "$NAME" --systemd=always --network=none \
	-v "$ROOT:/opt/rootspeak-src:ro,Z" -v "$RESULTS:/opt/results:Z" "$IMAGE" >/dev/null || exit 1
trap 'podman rm -f "$NAME" >/dev/null 2>&1' EXIT
for i in $(seq 1 60); do
	s=$(podman exec "$NAME" systemctl is-system-running 2>/dev/null)
	[ "$s" = running ] || [ "$s" = degraded ] && break
	sleep 1
done
echo "test machine: $s ($(podman exec "$NAME" sh -c '. /etc/os-release; echo $PRETTY_NAME'))"
# built on the test machine itself, with its compiler and libraries, as a customer would
podman exec "$NAME" sh -c 'rm -rf /opt/rootspeak && mkdir /opt/rootspeak &&
	tar -C /opt/rootspeak-src --exclude=./build --exclude=./build-san --exclude=./build-analyze \
		--exclude="./tests/*/results" -cf - . | tar -C /opt/rootspeak -xf - &&
	/opt/rootspeak/install.sh' >"$RESULTS/install.log" 2>&1 ||
	{ cat "$RESULTS/install.log"; echo "installation failed"; exit 1; }
grep -v '^Warning: zenity is missing' "$RESULTS/install.log" | head -1
# the system language of the test machine is Italian on purpose: RootSpeak must speak English anyway
# (commit and fingerprint can come from outside: on the test server the copy has no git)
podman exec -e LANG=it_IT.UTF-8 -e RSPEAK_TEST_COMMIT="${RSPEAK_TEST_COMMIT:-$("$ROOT/tools/fingerprint.sh" --commit)}" \
	-e RSPEAK_TEST_FINGERPRINT="${RSPEAK_TEST_FINGERPRINT:-$("$ROOT/tools/fingerprint.sh")}" -e RSPEAK_TEST_ONLY="${RSPEAK_TEST_ONLY:-}" \
	"$NAME" python3 /opt/rootspeak-src/tests/container/scenarios.py /opt/results
