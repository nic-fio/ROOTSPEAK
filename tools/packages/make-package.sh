#!/bin/bash
# RootSpeak - Advanced Messaging System for Linux
# Makes one package from the programs already built for /usr, inside a container
# of the distribution family (tools/release.sh starts it): the files are copied
# by install.sh with DESTDIR, the package manager's own tool makes the package.
#   make-package.sh deb|rpm|arch VERSION SOURCE OUT
# SOURCE: the source tree, with the programs built for /usr in SOURCE/build;
# OUT: where the package goes. deb on Debian 12 (dpkg-deb), rpm on RHEL 9
# (rpmbuild), arch on Arch (makepkg). After installing, every package runs
# /usr/lib/rootspeak/rootspeak-setup configure, as install.sh does.
set -euo pipefail
FORMAT=$1 VERSION=$2 SRC=$3 OUT=$4
HERE=$SRC/tools/packages
REL=1
SUMMARY="Messages from the administrators to the users, with read confirmation"
WORK=$(mktemp -d)
chmod 755 "$WORK"
STAGE=$WORK/stage

DESTDIR=$STAGE PREFIX=/usr "$SRC/install.sh"
# the files the package says what they are: the configuration, kept on upgrades
fill() { sed -e "s|@VERSION@|$VERSION|g" -e "s|@REL@|$REL|g" -e "s|@SUMMARY@|$SUMMARY|g" "$1"; }

case $FORMAT in
deb)
	install -d "$STAGE/DEBIAN"
	# (the size in KiB, as dpkg wants it)
	fill "$HERE/debian/control" | sed "s|@SIZE@|$(du -sk --exclude=DEBIAN "$STAGE" | cut -f1)|" >"$STAGE/DEBIAN/control"
	for f in postinst prerm postrm; do install -m 755 "$HERE/debian/$f" "$STAGE/DEBIAN/$f"; done
	echo /etc/rootspeak/rootspeak.conf >"$STAGE/DEBIAN/conffiles"
	# the licence where Debian looks for it
	cp "$SRC/LICENSE" "$STAGE/usr/share/doc/rootspeak/copyright"
	dpkg-deb --root-owner-group -Zxz --build "$STAGE" "$OUT/rootspeak_$VERSION-${REL}_amd64.deb" >/dev/null
	;;
rpm)
	install -d "$WORK"/{SPECS,RPMS,BUILD,BUILDROOT}
	fill "$HERE/rpm/rootspeak.spec" >"$WORK/SPECS/rootspeak.spec"
	# xz: the payload that every supported rpm reads, SLES 15's 4.14 included
	rpmbuild -bb --quiet --define "_topdir $WORK" --define "stage $STAGE" \
		--define '_binary_payload w6.xzdio' "$WORK/SPECS/rootspeak.spec"
	cp "$WORK"/RPMS/x86_64/rootspeak-"$VERSION"-$REL.x86_64.rpm "$OUT/"
	;;
arch)
	# makepkg does not run as root: as nobody, in a folder of its own
	install -d -o nobody "$WORK/arch"
	fill "$HERE/arch/PKGBUILD" >"$WORK/arch/PKGBUILD"
	cp "$HERE/arch/rootspeak.install" "$WORK/arch/"
	chown -R nobody "$WORK/arch"
	chmod -R a+rX "$STAGE"
	(cd "$WORK/arch" && runuser -u nobody -- env STAGE="$STAGE" PACKAGER="Nicola Fiorillo <rootspeak@nicfio.it>" PKGDEST="$WORK/arch" PKGEXT=.pkg.tar.zst \
		makepkg --nodeps --noconfirm --nocheck >/dev/null)
	cp "$WORK"/arch/rootspeak-"$VERSION"-$REL-x86_64.pkg.tar.zst "$OUT/"
	;;
*) echo "make-package.sh: unknown format $FORMAT" >&2; exit 2 ;;
esac
rm -rf "$WORK"
