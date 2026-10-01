#!/bin/bash
# RootSpeak - Advanced Messaging System for Linux
# Real-world tests in the VM with a desktop, on the test server (so as not to load
# the PC): copies the code to the server, starts the VM from a clean copy of the
# base disk, installs RootSpeak, runs the scenarios (tests/container/scenarios.py,
# with the desktop ones), takes the screenshots asked for and brings everything
# back to tests/vm/results/. The VM is shut down at the end.
#   tests/vm/run.sh               RSPEAK_SERVER and RSPEAK_DIR to change server and folder;
#                                    RSPEAK_TEST_ONLY=i_desktop,… to run only some groups
# The desktop is in Italian on purpose: RootSpeak must speak English anyway.
# The base disk is prepared once with --prepare (about 10 minutes).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
SERVER=${RSPEAK_SERVER:-192.168.0.2}
DIR=${RSPEAK_DIR:-/media/ROOTSPEAK}
DESK=sara
LOCALE_DESK=it_IT.UTF-8
SSHOPT=(-o BatchMode=yes -o LogLevel=ERROR)
VMOPT=(-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -J "$SERVER" -p 2222)

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
echo "code on the server ($SERVER:$DIR/src)…"
tar --exclude=.git --exclude='./tests/*/results' -cf - -C "$ROOT" . |
	x "rm -rf $DIR/src && mkdir -p $DIR/src $DIR/vm/captures && tar -xf - -C $DIR/src" || exit 1

if [ "${1:-}" = --prepare ] || ! x "test -f $DIR/vm/base.qcow2"; then
	cat ~/.ssh/id_ed25519.pub | x "cat > $DIR/vm/keys.pub"
	x "$DIR/src/tests/vm/prepare.sh $DIR/vm $DIR/vm/keys.pub" || exit 1
fi

x "$DIR/src/tests/vm/start.sh $DIR/vm" || exit 1
trap 'x "$DIR/src/tests/vm/stop.sh $DIR/vm"; echo "VM shut down"' EXIT

echo "RootSpeak in the VM…"
tar --exclude=.git -cf - -C "$ROOT" . |
	v "rm -rf /opt/rootspeak-src && mkdir -p /opt/rootspeak-src && tar -xf - -C /opt/rootspeak-src && /opt/rootspeak-src/install.sh | head -1"
# no welcome tour and no update notices on the test desktop
# (also in user-data.tpl, for the base disks prepared later)
v "apt-get -qq -y purge gnome-tour gnome-software >/dev/null 2>&1; true"
# languages: the system in Italian (the scenarios' ssh sessions) and the test
# desktop in Italian too (AccountsService): RootSpeak must speak English to both
v "dpkg -s locales >/dev/null 2>&1 || apt-get -qq -y install locales >/dev/null
	sed -i 's/^# *\\(it_IT.UTF-8\\|en_US.UTF-8\\)/\\1/' /etc/locale.gen && locale-gen >/dev/null
	echo LANG=it_IT.UTF-8 >/etc/default/locale
	f=/var/lib/AccountsService/users/$DESK
	if grep -q '^Language=' \$f 2>/dev/null; then sed -i 's/^Language=.*/Language=$LOCALE_DESK/' \$f
	else printf '[User]\\nLanguage=$LOCALE_DESK\\n' >>\$f; fi" || exit 1
# a new graphical login, so that the agent starts from the autostart as on a real system
v "systemctl restart gdm; for i in \$(seq 1 90); do
	pgrep -u $DESK -f '^(/bin/bash )?/usr/local/lib/rootspeak/rootspeak-user agent\$' >/dev/null && { echo \"desktop of $DESK ready after \${i}s\"; exit 0; }
	sleep 1; done; echo 'desktop not ready' >&2; exit 1" || exit 1

rm -rf "$HERE/results" && mkdir -p "$HERE/results/captures"
x "rm -f $DIR/vm/captures/*"
v "LANG=it_IT.UTF-8 RSPEAK_TEST_COMMIT=$("$ROOT/tools/fingerprint.sh" --commit) RSPEAK_TEST_FINGERPRINT=$("$ROOT/tools/fingerprint.sh") RSPEAK_TEST_ONLY=${RSPEAK_TEST_ONLY:-} RSPEAK_TEST_DESKTOP=$DESK python3 -u /opt/rootspeak-src/tests/container/scenarios.py /opt/results" |
	while IFS= read -r line; do
		case $line in
		"@@CAPTURE "*) x "python3 $DIR/src/tests/vm/capture.py $DIR/vm/monitor.sock $DIR/vm/captures/${line#@@CAPTURE }.ppm" ;;
		*) printf '%s\n' "$line" ;;
		esac
	done
outcome=${PIPESTATUS[0]}

v "tar -cf - -C /opt/results ." | tar -xf - -C "$HERE/results"
x "tar -cf - -C $DIR/vm/captures ." | tar -xf - -C "$HERE/results/captures"
python3 - "$HERE/results/captures" <<'PY'
import pathlib, sys
from PIL import Image
for f in pathlib.Path(sys.argv[1]).glob("*.ppm"):
    Image.open(f).save(f.with_suffix(".png"))
    f.unlink()
PY
echo "results in $HERE/results"
exit "$outcome"
