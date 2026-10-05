#!/bin/bash
# RootSpeak - Advanced Messaging System for Linux
# Builds the archive that is downloaded from the website: the programs built
# on the oldest supported distribution (RHEL 9 and its rebuilds, glibc 2.34),
# so that they run on all the distributions of tests/distros/list, plus
# install.sh, the files it installs, the manuals and the licence. No source.
#   tools/release.sh
# Result: build/release/rootspeak-VERSION-linux-x86_64.tar.gz and SHA256SUMS.
# The programs are built on the test server, in the rhel-9 image of the
# compatibility tests (tests/distros/run.sh rhel-9 builds it if it is missing).
# To test the archive on every distribution:
#   RSPEAK_ARCHIVE=build/release/rootspeak-VERSION-linux-x86_64.tar.gz tests/distros/run.sh
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
SERVER=${RSPEAK_SERVER:-192.168.0.2}
DIR=${RSPEAK_DIR:-/media/ROOTSPEAK}
VERSION=$(sed -n 's/^#define RSPEAK_VERSION "\(.*\)"/\1/p' "$ROOT/src/common.h")
NAME=rootspeak-$VERSION-linux-x86_64
OUT=$ROOT/build/release
# the oldest C library the programs may need: that of RHEL 9
MAX_GLIBC=2.34
SSHOPT=(-o BatchMode=yes -o LogLevel=ERROR)
x() { ssh "${SSHOPT[@]}" "$SERVER" "export TERM=dumb; $*" 2> >(grep -v '^tput:' >&2); }

tag=$(cat "$ROOT/tests/container/Containerfile" "$ROOT/tests/container/setup.sh" | sha256sum | cut -c1-12)
IMAGE=localhost/rootspeak-test-rhel-9:$tag
x "podman --root $DIR/distros/storage image exists $IMAGE" ||
	{ echo "the image $IMAGE is missing on $SERVER: run tests/distros/run.sh rhel-9 first" >&2; exit 2; }

echo "building on $SERVER, in $IMAGE…"
# only the files under version control
git -C "$ROOT" ls-files -z | tar -C "$ROOT" --null -T - -cf - |
	x "rm -rf $DIR/release && mkdir -p $DIR/release/src $DIR/release/out && tar -xf - -C $DIR/release/src"
x "podman --root $DIR/distros/storage run --rm --network none --entrypoint /bin/sh \
	-v $DIR/release/src:/src:Z -v $DIR/release/out:/out:Z $IMAGE -c \
	'cd /src && make B=/out all >/out/make.log 2>&1 && strip /out/rspeak /out/rootspeak-user'" ||
	{ x "cat $DIR/release/out/make.log"; echo "build failed" >&2; exit 1; }

rm -rf "$OUT" && mkdir -p "$OUT/$NAME/build" "$OUT/$NAME/docs"
x "tar -C $DIR/release/out -cf - rspeak rootspeak-user" | tar -C "$OUT/$NAME/build" -xf -

# what the programs need from the C library
need=$(objdump -T "$OUT/$NAME/build/rspeak" "$OUT/$NAME/build/rootspeak-user" |
	grep -o 'GLIBC_[0-9.]*' | sed 's/GLIBC_//' | sort -uV | tail -1)
if [ "$(printf '%s\n%s\n' "$need" "$MAX_GLIBC" | sort -V | tail -1)" != "$MAX_GLIBC" ]; then
	echo "the programs need glibc $need, newer than $MAX_GLIBC" >&2; exit 1
fi
grep -qaF /usr/local/lib/rootspeak "$OUT/$NAME/build/rspeak" ||
	{ echo "the programs were not built for /usr/local" >&2; exit 1; }

cp "$ROOT/install.sh" "$ROOT/LICENSE" "$ROOT/NOTICE.md" "$OUT/$NAME/"
cp -r "$ROOT/etc" "$OUT/$NAME/"
cp "$ROOT/docs/User Manual.html" "$ROOT/docs/Technical Manual.html" "$OUT/$NAME/docs/"
cat >"$OUT/$NAME/README.txt" <<EOF
RootSpeak $VERSION - Advanced Messaging System for Linux
https://rootspeak.nicfio.it

The administrators of a Linux machine send messages to its users, in every
terminal and on the desktop, and see who has confirmed reading them.

Requirements: a Linux distribution with systemd (x86-64), sudo, zenity for the
desktop dialog (optional on servers without a desktop).

Install, as an administrator:
    ./install.sh
Then:
    rspeak            the full-screen interface
    rspeak --help     the built-in help

Remove:
    ./install.sh --uninstall    (keeps the messages and the configuration)
    ./install.sh --purge        (removes them too)

Manuals: docs/User Manual.html and docs/Technical Manual.html, also installed
in /usr/local/share/doc/rootspeak/.

RootSpeak is freeware: see LICENSE. Copyright (c) 2026 Nicola Fiorillo.
Contact: rootspeak@nicfio.it
EOF

tar -C "$OUT" --owner=0 --group=0 --mode=u=rwX,go=rX --sort=name -czf "$OUT/$NAME.tar.gz" "$NAME"
(cd "$OUT" && sha256sum "$NAME.tar.gz" >SHA256SUMS)
echo "built $OUT/$NAME.tar.gz ($(stat -c %s "$OUT/$NAME.tar.gz") bytes, glibc $need or newer):"
tar -tvzf "$OUT/$NAME.tar.gz" | awk '{s=$3; for (i=1; i<6; i++) $i=""; sub(/^ +/, ""); print "  " $0 "  " s}'
