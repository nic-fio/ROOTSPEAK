#!/bin/bash
# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# RootSpeak - Advanced Messaging System for Linux
# Builds the archive that is downloaded from the website: the programs built
# on the oldest supported distribution (RHEL 9 and its rebuilds, glibc 2.34),
# so that they run on all the distributions of tests/distros/list, plus
# install.sh, the files it installs, the manuals and the licence. No source:
# the source is a separate archive (see below).
# And the packages, with the same programs built for /usr: .deb (Debian, Ubuntu),
# .rpm (Fedora, RHEL and its rebuilds, openSUSE, SLES) and .pkg.tar.zst (Arch),
# each made with the tool of its family (tools/packages/make-package.sh).
#   tools/release.sh
# Result in build/release/: rootspeak-VERSION-linux-x86_64.tar.gz,
# rootspeak_VERSION-1_amd64.deb, rootspeak-VERSION-1.x86_64.rpm,
# rootspeak-VERSION-1-x86_64.pkg.tar.zst, rootspeak-VERSION-source.tar.gz and
# SHA256SUMS.
# The programs are built on the test server, in the rhel-9 image of the
# compatibility tests; the packages in the debian-12, rhel-9 and arch images
# (tests/distros/run.sh debian-12 rhel-9 arch builds them if they are missing).
# The rpm and Arch tools are installed in a throwaway container, from the network
# (the host's: the server has no pasta for rootless podman networks).
# To test archive and packages on every distribution:
#   RSPEAK_RELEASE=build/release tests/distros/run.sh
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
image() { echo "localhost/rootspeak-test-$1:$tag"; }
for d in rhel-9 debian-12 arch; do
	x "podman --root $DIR/distros/storage image exists $(image $d)" ||
		{ echo "the image $(image $d) is missing on $SERVER: run tests/distros/run.sh $d first" >&2; exit 2; }
done
podman_run() { x "podman --root $DIR/distros/storage run --rm --entrypoint /bin/sh $*"; }

echo "building on $SERVER, in $(image rhel-9)…"
# the files under version control, and the new ones not ignored
git -C "$ROOT" ls-files -co --exclude-standard -z | tar -C "$ROOT" --null -T - -cf - |
	x "rm -rf $DIR/release && mkdir -p $DIR/release/src $DIR/release/out $DIR/release/pkg && tar -xf - -C $DIR/release/src"
# the archive's programs for /usr/local, the packages' for /usr
podman_run "--network none -v $DIR/release/src:/src:Z -v $DIR/release/out:/out:Z $(image rhel-9) -c \
	'cd /src && make B=/out all >/out/make.log 2>&1 && strip /out/rspeak /out/rootspeak-user &&
	 make B=/out/usr PREFIX=/usr all >>/out/make.log 2>&1 && strip /out/usr/rspeak /out/usr/rootspeak-user &&
	 mkdir -p /src/build && cp /out/usr/rspeak /out/usr/rootspeak-user /src/build/'" ||
	{ x "cat $DIR/release/out/make.log"; echo "build failed" >&2; exit 1; }

echo "packages…"
MP="/src/tools/packages/make-package.sh"
podman_run "--network none -v $DIR/release/src:/src:ro,Z -v $DIR/release/pkg:/out:Z $(image debian-12) -c \
	'$MP deb $VERSION /src /out'" || { echo "the .deb failed" >&2; exit 1; }
podman_run "--network host -v $DIR/release/src:/src:ro,Z -v $DIR/release/pkg:/out:Z $(image rhel-9) -c \
	'dnf -q -y install rpm-build >/dev/null && $MP rpm $VERSION /src /out'" || { echo "the .rpm failed" >&2; exit 1; }
podman_run "--network host -v $DIR/release/src:/src:ro,Z -v $DIR/release/pkg:/out:Z $(image arch) -c \
	'pacman -Sy --noconfirm --needed fakeroot >/dev/null && $MP arch $VERSION /src /out'" || { echo "the Arch package failed" >&2; exit 1; }

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

cp "$ROOT/install.sh" "$ROOT/LICENSE.md" "$ROOT/NOTICE.md" "$OUT/$NAME/"
cp -r "$ROOT/etc" "$OUT/$NAME/"
mkdir -p "$OUT/$NAME/logos" && cp "$ROOT"/logos/rootspeak-icon* "$OUT/$NAME/logos/"
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

RootSpeak is free for any noncommercial use: see LICENSE.md (PolyForm
Noncommercial License 1.0.0). The source code is downloaded from the website. Copyright (c) 2026 Nicola Fiorillo.
Contact: rootspeak@nicfio.it
EOF

tar -C "$OUT" --owner=0 --group=0 --mode=u=rwX,go=rX --sort=name -czf "$OUT/$NAME.tar.gz" "$NAME"

# The source archive (PolyForm Noncommercial License 1.0.0): what is needed to
# read, build, test and install RootSpeak, and how the packages are made. Only
# the files listed here: the working notes (CLAUDE.md, docs/decisions-and-history.md),
# the website and the test infrastructure stay in the repository only.
SRCNAME=rootspeak-$VERSION-source
SRCFILES=(Makefile LICENSE.md NOTICE.md install.sh src etc 'logos/rootspeak-icon*'
	'docs/User Manual.html' 'docs/Technical Manual.html' tests/unit-tests.c tests/engine.sh tools/fingerprint.sh tools/packages)
mkdir -p "$OUT/$SRCNAME"
git -C "$ROOT" ls-files -co --exclude-standard -z -- "${SRCFILES[@]}" | tar -C "$ROOT" --null -T - -cf - |
	tar -C "$OUT/$SRCNAME" -xf -
cat >"$OUT/$SRCNAME/README.txt" <<EOF
RootSpeak $VERSION - Advanced Messaging System for Linux - source code
https://rootspeak.nicfio.it

The source code of RootSpeak, published so that anyone can check what it does
on their machines. It is published under the PolyForm Noncommercial License
1.0.0: free for any noncommercial use, including changes; commercial use
needs a licence from the author. The terms are in LICENSE.md.

Build (gcc, make, pkg-config and the systemd development files: libsystemd-dev
on Debian and Ubuntu, systemd-devel on Fedora, RHEL and openSUSE):
    make              builds build/rspeak and build/rootspeak-user
    make unit         the unit tests
    tests/engine.sh   the engine tests, in test mode: no root, a temporary store

Install, as an administrator (builds first if needed):
    ./install.sh
Remove:
    ./install.sh --uninstall    (keeps the messages and the configuration)
    ./install.sh --purge        (removes them too)

How the packages are made: tools/packages/. The manuals are in docs/; the
technical manual describes the architecture, the message store and security.

Copyright (c) 2026 Nicola Fiorillo. Contact: rootspeak@nicfio.it
EOF
for f in src/rspeak.c install.sh LICENSE.md; do
	[ -s "$OUT/$SRCNAME/$f" ] || { echo "the source archive has no $f" >&2; exit 1; }
done
for f in CLAUDE.md site tools/release.sh docs/decisions-and-history.md; do
	[ ! -e "$OUT/$SRCNAME/$f" ] || { echo "the source archive must not contain $f" >&2; exit 1; }
done
tar -C "$OUT" --owner=0 --group=0 --mode=u=rwX,go=rX --sort=name -czf "$OUT/$SRCNAME.tar.gz" "$SRCNAME"
x "tar -C $DIR/release/pkg -cf - ." | tar -C "$OUT" -xf -
PKGS=(rootspeak_$VERSION-1_amd64.deb rootspeak-$VERSION-1.x86_64.rpm rootspeak-$VERSION-1-x86_64.pkg.tar.zst)
for p in "${PKGS[@]}"; do [ -s "$OUT/$p" ] || { echo "missing package $p" >&2; exit 1; }; done
(cd "$OUT" && sha256sum "$NAME.tar.gz" "${PKGS[@]}" "$SRCNAME.tar.gz" >SHA256SUMS)
echo "built $OUT/$NAME.tar.gz ($(stat -c %s "$OUT/$NAME.tar.gz") bytes, glibc $need or newer):"
tar -tvzf "$OUT/$NAME.tar.gz" | awk '{s=$3; for (i=1; i<6; i++) $i=""; sub(/^ +/, ""); print "  " $0 "  " s}'
for p in "${PKGS[@]}" "$SRCNAME.tar.gz"; do echo "built $OUT/$p ($(stat -c %s "$OUT/$p") bytes)"; done
