#!/bin/bash
# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# RootSpeak - Advanced Messaging System for Linux: installation and removal.
#   ./install.sh              installs
#   ./install.sh --uninstall  removes (the messages in /var/lib/rootspeak stay)
#   ./install.sh --purge      also removes the messages
# Installs the programs built in build/: from the source tree it builds them
# (make) if they are missing; the downloadable archive has them already built,
# for /usr/local, and builds nothing.
# With DESTDIR it only copies the files into DESTDIR, as root:root, without
# touching the system: tools/release.sh makes the packages this way, with
# PREFIX=/usr; the packages then run rootspeak-setup configure.
set -euo pipefail

PREFIX=${PREFIX:-/usr/local}
DESTDIR=${DESTDIR:-}
LIBDIR=$PREFIX/lib/rootspeak
BINDIR=$PREFIX/bin
VARDIR=/var/lib/rootspeak
DOCDIR=$PREFIX/share/doc/rootspeak
ICONDIR=$PREFIX/share/icons/hicolor
METAINFO=$PREFIX/share/metainfo/it.nicfio.rootspeak.metainfo.xml
FISHCONF=/etc/fish/conf.d/rootspeak.fish
SRC=$(dirname "$(readlink -f "$0")")
# where the packages install
PACKAGE_LIBDIR=/usr/lib/rootspeak

[ -n "$DESTDIR" ] || [ "$(id -u)" -eq 0 ] || exec sudo -- "$(readlink -f "$0")" "$@"

subst() { sed -e "s|@LIBDIR@|$LIBDIR|g" -e "s|@BINDIR@|$BINDIR|g" -e "s|@VARDIR@|$VARDIR|g" "$1"; }

# The files of the installation, into $DESTDIR (empty: the system itself).
copy_files() {
	local d=$DESTDIR
	install -d -m 755 "$d$LIBDIR" "$d$BINDIR" "$d/etc/rootspeak" "$d/etc/profile.d" "$d/etc/xdg/autostart" \
		"$d$(dirname "$FISHCONF")" "$d$DOCDIR"
	install -m 755 "$SRC/build/rootspeak-user" "$d$LIBDIR/rootspeak-user"
	# the group is set by rootspeak-setup configure
	install -m 750 "$SRC/build/rspeak" "$d$BINDIR/rspeak"
	[ -e "$d/etc/rootspeak/rootspeak.conf" ] ||
		install -m 644 "$SRC/etc/rootspeak/rootspeak.conf" "$d/etc/rootspeak/rootspeak.conf"
	# the manuals, one file each
	install -m 644 "$SRC/docs/User Manual.html" "$SRC/docs/Technical Manual.html" "$SRC/LICENSE.md" "$SRC/NOTICE.md" "$d$DOCDIR/"
	# the logo as the icon (notifications, software centres) and the software centres' description
	install -D -m 644 "$SRC/logos/rootspeak-icon.svg" "$d$ICONDIR/scalable/apps/rootspeak.svg"
	for n in 48 128 256; do
		install -D -m 644 "$SRC/logos/rootspeak-icon-$n.png" "$d$ICONDIR/${n}x$n/apps/rootspeak.png"
	done
	install -D -m 644 "$SRC/etc/rootspeak.metainfo.xml" "$d$METAINFO"
	subst "$SRC/etc/rootspeak-setup" >"$d$LIBDIR/rootspeak-setup"
	subst "$SRC/etc/profile.d/rootspeak.sh" >"$d/etc/profile.d/rootspeak.sh"
	subst "$SRC/etc/rootspeak.bash" >"$d$LIBDIR/rootspeak.bash"
	subst "$SRC/etc/rootspeak.zsh" >"$d$LIBDIR/rootspeak.zsh"
	subst "$SRC/etc/rootspeak.fish" >"$d$FISHCONF"
	subst "$SRC/etc/xdg/autostart/rootspeak-agent.desktop" >"$d/etc/xdg/autostart/rootspeak-agent.desktop"
	chmod 755 "$d$LIBDIR/rootspeak-setup"
	chmod 644 "$d$LIBDIR/rootspeak.bash" "$d$LIBDIR/rootspeak.zsh" "$d$FISHCONF" \
		"$d/etc/profile.d/rootspeak.sh" "$d/etc/xdg/autostart/rootspeak-agent.desktop"
}

do_install() {
	# The programs built with the folders of this installation: if they are
	# missing or were built for other folders, they are built (only from the
	# source tree: the archive has no source).
	if ! [ -x "$SRC/build/rspeak" ] || ! [ -x "$SRC/build/rootspeak-user" ] ||
		! grep -qaF "$LIBDIR" "$SRC/build/rspeak"; then
		[ -f "$SRC/Makefile" ] ||
			{ echo "The programs of this archive install only in /usr/local (PREFIX=$PREFIX)" >&2; exit 1; }
		make -C "$SRC" PREFIX="$PREFIX" all >/dev/null ||
			{ echo "Build failed: gcc, make, pkg-config and the systemd development files are needed (libsystemd-dev or systemd-devel)" >&2; exit 1; }
	fi
	if [ -n "$DESTDIR" ]; then copy_files; return; fi

	# installed from a package: the package manager updates and removes it
	if [ "$LIBDIR" != "$PACKAGE_LIBDIR" ] && [ -e "$PACKAGE_LIBDIR/rootspeak-user" ]; then
		echo "RootSpeak is installed from a package: update or remove it with the package manager (apt, dnf, zypper, pacman)." >&2
		exit 1
	fi
	for c in zenity loginctl systemd-run; do
		command -v "$c" >/dev/null || echo "Warning: $c is missing" >&2
	done
	# the translations of the first 0.2.0 builds: RootSpeak is now in English only
	rm -f "$PREFIX"/share/locale/*/LC_MESSAGES/rootspeak.mo
	copy_files
	"$LIBDIR/rootspeak-setup" configure

	echo "RootSpeak installed. Command: $BINDIR/rspeak (usable by the $("$LIBDIR/rootspeak-setup" group) group)."
	echo "Manuals: $DOCDIR/User Manual.html and Technical Manual.html"
	echo "Sessions already open get messages in the terminal at once, and the"
	echo "confirmation question from the next shell or the next login."
}

do_uninstall() {
	if [ "$LIBDIR" != "$PACKAGE_LIBDIR" ] && [ -e "$PACKAGE_LIBDIR/rootspeak-user" ] && ! [ -e "$LIBDIR/rootspeak-user" ]; then
		echo "RootSpeak is installed from a package: remove it with the package manager (apt, dnf, zypper, pacman)." >&2
		exit 1
	fi
	# (installations before rootspeak-setup: the same lines, removed here)
	if [ -x "$LIBDIR/rootspeak-setup" ]; then "$LIBDIR/rootspeak-setup" unconfigure; else
		sed -i '\|# RootSpeak hook|d' /etc/bash.bashrc /etc/zsh/zshrc /etc/zshrc 2>/dev/null || true
		pkill -f "^$LIBDIR/rootspeak-user agent\$" 2>/dev/null || true
	fi
	rm -f "$BINDIR/rspeak" /etc/profile.d/rootspeak.sh /etc/xdg/autostart/rootspeak-agent.desktop "$FISHCONF"
	rm -rf "$LIBDIR" "$DOCDIR"
	rm -f "$ICONDIR"/*/apps/rootspeak.svg "$ICONDIR"/*/apps/rootspeak.png "$METAINFO"
	if [ "${1:-}" = purge ]; then
		rm -rf "$VARDIR" /etc/rootspeak
		echo "RootSpeak removed, together with the messages and the configuration."
	else
		echo "RootSpeak removed. Messages ($VARDIR) and configuration (/etc/rootspeak) kept."
	fi
}

case ${1:-} in
'') do_install ;;
--uninstall) do_uninstall ;;
--purge) do_uninstall purge ;;
*) echo "Usage: $0 [--uninstall | --purge]" >&2; exit 1 ;;
esac
