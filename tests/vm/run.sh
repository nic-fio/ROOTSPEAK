#!/bin/bash
# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# RootSpeak - Advanced Messaging System for Linux
# Real-world tests in a VM with a desktop, on the test server (so as not to load
# the PC): copies the code to the server, starts the VM from a clean copy of the
# base disk, installs RootSpeak, runs the scenarios (tests/container/scenarios.py,
# with the desktop ones), takes the screenshots asked for and brings everything
# back. The VM is shut down at the end.
#   tests/vm/run.sh [DESKTOP]     a profile of tests/vm/desktops (debian-gnome by default):
#                                    debian-gnome, ubuntu-gnome, ubuntu-cinnamon, fedora-kde, rocky-gnome
#   --prepare                     prepares the base disk again (it is prepared anyway when it
#                                    is missing or its profile or users.sh have changed)
#   RSPEAK_SERVER and RSPEAK_DIR to change server and folder, RSPEAK_VM_MEMORY (default 8G),
#   RSPEAK_TEST_ONLY=i_desktop,… to run only some groups.
# Results: tests/vm/results/ for debian-gnome, tests/vm/desktops/results/NAME/ for the others.
# The desktop is in Italian on purpose: RootSpeak must speak English anyway.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
SERVER=${RSPEAK_SERVER:-192.168.0.2}
DIR=${RSPEAK_DIR:-/media/ROOTSPEAK}
MEM=${RSPEAK_VM_MEMORY:-8G}
PREPARE=
NAME=debian-gnome
for a in "$@"; do
	case $a in
	--prepare) PREPARE=1 ;;
	*) NAME=$a ;;
	esac
done
PROFILE=$HERE/desktops/$NAME.yaml
[ -f "$PROFILE" ] || { echo "no such desktop profile: $PROFILE" >&2; exit 2; }
# each desktop: its own folder on the server, its own ssh port, its own results
case $NAME in
debian-gnome) VMDIR=$DIR/vm PORT=2222 RESULTS=$HERE/results ;;
*) VMDIR=$DIR/vm-$NAME RESULTS=$HERE/desktops/results/$NAME
   PORT=$((2222 + $(ls "$HERE/desktops"/*.yaml | sort | grep -n "/$NAME.yaml$" | cut -d: -f1))) ;;
esac
LABEL=$(sed -n 's/^# desktop: //p' "$PROFILE")
DESK=sara
LOCALE_DESK=it_IT.UTF-8
SSHOPT=(-o BatchMode=yes -o LogLevel=ERROR)
VMOPT=(-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -J "$SERVER" -p "$PORT")

# (the server's shell profile prints tput warnings without a terminal: they are dropped)
x() { ssh "${SSHOPT[@]}" "$SERVER" "export TERM=dumb; $*" 2> >(grep -v '^tput:' >&2); }
v() { ssh "${SSHOPT[@]}" "${VMOPT[@]}" root@127.0.0.1 "$@"; }

# the server's system is rebuilt at every boot (its / is in RAM): the programs the
# tests need may be gone, and only the owner can install them, with sudo
missing=$(x 'for c in qemu-system-x86_64 qemu-img genisoimage curl python3; do command -v $c >/dev/null || printf "%s " $c; done')
if [ -n "$missing" ]; then
	echo "the test server $SERVER lacks: $missing(its system is lost at every reboot). Install with:" >&2
	echo "  ssh -t $SERVER 'sudo apt install -y qemu-system-x86 qemu-utils genisoimage curl python3'" >&2
	exit 2
fi
echo "$NAME ($LABEL): code on the server ($SERVER:$VMDIR/src)…"
tar --exclude=.git --exclude='./build*' --exclude='./tests/*/results' --exclude='./tests/vm/desktops/results' \
	-cf - -C "$ROOT" . |
	x "rm -rf $VMDIR/src && mkdir -p $VMDIR/src $VMDIR/captures && tar -xf - -C $VMDIR/src" || exit 1

# (the comments do not count: they do not change the disk)
fingerprint=$(grep -hv '^ *# ' "$PROFILE" "$HERE/users.sh" | sha256sum | cut -c1-12)
if [ -n "$PREPARE" ] || [ "$(x "cat $VMDIR/base.fingerprint 2>/dev/null")" != "$fingerprint" ]; then
	cat ~/.ssh/id_ed25519.pub | x "cat > $VMDIR/keys.pub"
	x "$VMDIR/src/tests/vm/prepare.sh $VMDIR $VMDIR/keys.pub $VMDIR/src/tests/vm/desktops/$NAME.yaml $MEM" || exit 1
fi

x "$VMDIR/src/tests/vm/start.sh $VMDIR $PORT $MEM" || exit 1
trap 'x "$VMDIR/src/tests/vm/stop.sh $VMDIR"; echo "VM shut down"' EXIT

echo "RootSpeak in the VM…"
tar --exclude=.git --exclude='./build*' --exclude='./tests/*/results' --exclude='./tests/vm/desktops/results' \
	-cf - -C "$ROOT" . |
	v "rm -rf /opt/rootspeak-src && mkdir -p /opt/rootspeak-src && tar -xf - -C /opt/rootspeak-src && /opt/rootspeak-src/install.sh | head -1"
# languages: the system in Italian (the scenarios' ssh sessions) and the test
# desktop in Italian too (AccountsService): RootSpeak must speak English to both
v "localectl set-locale LANG=it_IT.UTF-8 2>/dev/null || echo LANG=it_IT.UTF-8 >/etc/locale.conf
	[ -d /etc/default ] && echo LANG=it_IT.UTF-8 >/etc/default/locale
	f=/var/lib/AccountsService/users/$DESK
	if grep -q '^Language=' \$f 2>/dev/null; then sed -i 's/^Language=.*/Language=$LOCALE_DESK/' \$f
	else mkdir -p \$(dirname \$f); printf '[User]\\nLanguage=$LOCALE_DESK\\n' >>\$f; fi; true" || exit 1
# a new graphical login, so that the agent starts from the autostart as on a real system
v "systemctl restart display-manager; for i in \$(seq 1 120); do
	pgrep -u $DESK -f '^(/bin/bash )?/usr/local/lib/rootspeak/rootspeak-user agent\$' >/dev/null && { echo \"desktop of $DESK ready after \${i}s\"; exit 0; }
	sleep 1; done; echo 'desktop not ready' >&2; exit 1" || exit 1

rm -rf "$RESULTS" && mkdir -p "$RESULTS/captures"
x "rm -f $VMDIR/captures/*"
v "LANG=it_IT.UTF-8 RSPEAK_TEST_COMMIT=$("$ROOT/tools/fingerprint.sh" --commit) RSPEAK_TEST_FINGERPRINT=$("$ROOT/tools/fingerprint.sh") RSPEAK_TEST_ONLY=${RSPEAK_TEST_ONLY:-} RSPEAK_TEST_DESKTOP=$DESK RSPEAK_TEST_DESKTOP_LABEL='$LABEL' python3 -u /opt/rootspeak-src/tests/container/scenarios.py /opt/results" |
	while IFS= read -r line; do
		case $line in
		"@@CAPTURE "*) x "python3 $VMDIR/src/tests/vm/capture.py $VMDIR/monitor.sock $VMDIR/captures/${line#@@CAPTURE }.ppm" ;;
		*) printf '%s\n' "$line" ;;
		esac
	done
outcome=${PIPESTATUS[0]}

v "tar -cf - -C /opt/results ." | tar -xf - -C "$RESULTS"
x "tar -cf - -C $VMDIR/captures ." | tar -xf - -C "$RESULTS/captures"
python3 - "$RESULTS/captures" <<'PY'
import pathlib, sys
from PIL import Image
for f in pathlib.Path(sys.argv[1]).glob("*.ppm"):
    Image.open(f).save(f.with_suffix(".png"))
    f.unlink()
PY
echo "results in $RESULTS"
exit "$outcome"
