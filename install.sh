#!/bin/bash
# RootSpeak - Advanced Messaging System for Linux: installation and removal.
#   ./install.sh              installs
#   ./install.sh --uninstall  removes (the messages in /var/lib/rootspeak stay)
#   ./install.sh --purge      also removes the messages
# Installs the C version built in build/ (make); if it is missing, builds it.
set -euo pipefail

PREFIX=${PREFIX:-/usr/local}
LIBDIR=$PREFIX/lib/rootspeak
BINDIR=$PREFIX/bin
VARDIR=/var/lib/rootspeak
DOCDIR=$PREFIX/share/doc/rootspeak
BASHRC=/etc/bash.bashrc
ZSHRC=$( [ -d /etc/zsh ] && echo /etc/zsh/zshrc || echo /etc/zshrc )
FISHCONF=/etc/fish/conf.d/rootspeak.fish
MARK='# RootSpeak hook'
SRC=$(dirname "$(readlink -f "$0")")
# the desktop agent
AGENT_RE="^$LIBDIR/rootspeak-user agent\$"

[ "$(id -u)" -eq 0 ] || exec sudo -- "$(readlink -f "$0")" "$@"

# The administrators' group already on the system.
admin_group() {
	local g
	for g in sudo wheel admin; do
		if getent group "$g" >/dev/null; then echo "$g"; return; fi
	done
	echo root
}

subst() { sed -e "s|@LIBDIR@|$LIBDIR|g" -e "s|@VARDIR@|$VARDIR|g" "$1"; }

do_install() {
	local group
	group=$(admin_group)
	for c in zenity loginctl systemd-run; do
		command -v "$c" >/dev/null || echo "Warning: $c is missing" >&2
	done

	# The programs built with the folders of this installation: if they are
	# missing or were built for other folders, they are built.
	if ! [ -x "$SRC/build/rspeak" ] || ! [ -x "$SRC/build/rootspeak-user" ] ||
		! grep -qaF "$LIBDIR" "$SRC/build/rspeak"; then
		make -C "$SRC" PREFIX="$PREFIX" all >/dev/null ||
			{ echo "Build failed: gcc, make, pkg-config and the systemd development files are needed (libsystemd-dev or systemd-devel)" >&2; exit 1; }
	fi
	install -d -m 755 "$LIBDIR" "$BINDIR" /etc/rootspeak /etc/profile.d /etc/xdg/autostart
	install -m 755 "$SRC/build/rootspeak-user" "$LIBDIR/rootspeak-user"
	# the translations of the first 0.2.0 builds: RootSpeak is now in English only
	rm -f "$PREFIX"/share/locale/*/LC_MESSAGES/rootspeak.mo
	install -m 750 -o root -g "$group" "$SRC/build/rspeak" "$BINDIR/rspeak"
	[ -e /etc/rootspeak/rootspeak.conf ] || install -m 644 "$SRC/etc/rootspeak/rootspeak.conf" /etc/rootspeak/rootspeak.conf
	# the manuals, one file each
	install -d -m 755 "$DOCDIR"
	install -m 644 "$SRC/docs/User Manual.html" "$SRC/docs/Technical Manual.html" "$DOCDIR/"
	subst "$SRC/etc/profile.d/rootspeak.sh" >/etc/profile.d/rootspeak.sh
	subst "$SRC/etc/rootspeak.bash" >"$LIBDIR/rootspeak.bash"
	subst "$SRC/etc/rootspeak.zsh" >"$LIBDIR/rootspeak.zsh"
	chmod 644 "$LIBDIR/rootspeak.bash" "$LIBDIR/rootspeak.zsh"
	# zsh: a line in the system zshrc, if zsh is installed (if it is installed
	# later, run install.sh again); the zshrc is created if missing (Arch has
	# only /etc/zsh/zprofile); fish: a file in conf.d, which fish reads even if
	# it is installed later
	if command -v zsh >/dev/null && ! grep -qsF "$MARK" "$ZSHRC"; then
		echo "[ -r $LIBDIR/rootspeak.zsh ] && . $LIBDIR/rootspeak.zsh  $MARK" >>"$ZSHRC"
	fi
	install -d -m 755 "$(dirname "$FISHCONF")"
	subst "$SRC/etc/rootspeak.fish" >"$FISHCONF"
	chmod 644 "$FISHCONF"
	subst "$SRC/etc/xdg/autostart/rootspeak-agent.desktop" >/etc/xdg/autostart/rootspeak-agent.desktop
	chmod 644 /etc/profile.d/rootspeak.sh /etc/xdg/autostart/rootspeak-agent.desktop

	# On Debian and Ubuntu non-login shells (for example the desktop terminals)
	# do not read /etc/profile.d: the hook is called from bash.bashrc.
	if [ -f "$BASHRC" ] && ! grep -qF "$MARK" "$BASHRC"; then
		echo "[ -r /etc/profile.d/rootspeak.sh ] && . /etc/profile.d/rootspeak.sh  $MARK" >>"$BASHRC"
	fi

	install -d -m 755 "$VARDIR" "$VARDIR/users"
	install -d -m 700 "$VARDIR/sent"

	# The desktop agents of a previous version are stopped: the first
	# `rspeak send` or the next login starts an updated one.
	pkill -f "$AGENT_RE" 2>/dev/null || true

	echo "RootSpeak installed. Command: $BINDIR/rspeak (usable by the $group group)."
	echo "Manuals: $DOCDIR/User Manual.html and Technical Manual.html"
	echo "Sessions already open get messages in the terminal at once, and the"
	echo "confirmation question from the next shell or the next login."
}

do_uninstall() {
	rm -f "$BINDIR/rspeak" /etc/profile.d/rootspeak.sh /etc/xdg/autostart/rootspeak-agent.desktop
	rm -rf "$LIBDIR" "$DOCDIR"
	if [ -f "$BASHRC" ]; then sed -i "\|$MARK|d" "$BASHRC"; fi
	if [ -f "$ZSHRC" ]; then sed -i "\|$MARK|d" "$ZSHRC"; fi
	rm -f "$FISHCONF"
	pkill -f "$AGENT_RE" 2>/dev/null || true
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
