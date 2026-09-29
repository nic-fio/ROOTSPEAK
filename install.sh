#!/bin/bash
# AMS - Advanced Messaging System for linux: installazione e rimozione.
#   ./install.sh              installa
#   ./install.sh --uninstall  rimuove (i messaggi in /var/lib/ams restano)
#   ./install.sh --purge      rimuove anche i messaggi
set -euo pipefail

PREFIX=${PREFIX:-/usr/local}
LIBDIR=$PREFIX/lib/ams
BINDIR=$PREFIX/bin
VARDIR=/var/lib/ams
DOCDIR=$PREFIX/share/doc/ams
BASHRC=/etc/bash.bashrc
MARK='# AMS hook'
SRC=$(dirname "$(readlink -f "$0")")
AGENT_RE="^/bin/bash $LIBDIR/ams-user agent\$"

[ "$(id -u)" -eq 0 ] || exec sudo -- "$(readlink -f "$0")" "$@"

# Gruppo degli amministratori già presente nel sistema.
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
	for c in zenity notify-send loginctl systemd-run runuser flock; do
		command -v "$c" >/dev/null || echo "Attenzione: manca $c" >&2
	done

	install -d -m 755 "$LIBDIR" "$BINDIR" /etc/ams /etc/profile.d /etc/xdg/autostart
	install -m 644 "$SRC/lib/ams-common.sh" "$LIBDIR/ams-common.sh"
	install -m 755 "$SRC/lib/ams-user" "$LIBDIR/ams-user"
	# Le versioni precedenti installavano in sbin, che su Debian non è nel PATH degli utenti.
	rm -f "$PREFIX/sbin/ams"
	sed "s|^AMS_LIB=.*|AMS_LIB=$LIBDIR|" "$SRC/bin/ams" >"$BINDIR/ams"
	chown "root:$group" "$BINDIR/ams"
	chmod 750 "$BINDIR/ams"
	[ -e /etc/ams/ams.conf ] || install -m 644 "$SRC/etc/ams/ams.conf" /etc/ams/ams.conf
	install -d -m 755 "$DOCDIR/assets"
	install -m 644 "$SRC/docs/user-manual.html" "$DOCDIR/user-manual.html"
	install -m 644 "$SRC/docs/assets/docs.css" "$SRC/docs/assets/docs.js" "$DOCDIR/assets/"
	subst "$SRC/etc/profile.d/ams.sh" >/etc/profile.d/ams.sh
	subst "$SRC/etc/xdg/autostart/ams-agent.desktop" >/etc/xdg/autostart/ams-agent.desktop
	chmod 644 /etc/profile.d/ams.sh /etc/xdg/autostart/ams-agent.desktop

	# Su Debian e Ubuntu le shell non di login (es. i terminali del desktop)
	# non leggono /etc/profile.d: l'hook va richiamato da bash.bashrc.
	if [ -f "$BASHRC" ] && ! grep -qF "$MARK" "$BASHRC"; then
		echo "[ -r /etc/profile.d/ams.sh ] && . /etc/profile.d/ams.sh  $MARK" >>"$BASHRC"
	fi

	install -d -m 755 "$VARDIR" "$VARDIR/users"
	install -d -m 700 "$VARDIR/sent"

	# Gli agenti del desktop di una versione precedente vanno chiusi: il primo
	# `ams send` o il prossimo login ne avviano uno aggiornato.
	pkill -f "$AGENT_RE" 2>/dev/null || true

	echo "AMS installato. Comando: $BINDIR/ams (utilizzabile dal gruppo $group)."
	echo "Manuale: $DOCDIR/user-manual.html"
	echo "Le sessioni già aperte ricevono i messaggi sul terminale subito e la domanda"
	echo "di conferma dalla prossima shell o dal prossimo login."
}

do_uninstall() {
	rm -f "$BINDIR/ams" "$PREFIX/sbin/ams" /etc/profile.d/ams.sh /etc/xdg/autostart/ams-agent.desktop
	rm -rf "$LIBDIR" "$DOCDIR"
	if [ -f "$BASHRC" ]; then sed -i "\|$MARK|d" "$BASHRC"; fi
	pkill -f "$AGENT_RE" 2>/dev/null || true
	if [ "${1:-}" = purge ]; then
		rm -rf "$VARDIR" /etc/ams
		echo "AMS rimosso, insieme ai messaggi e alla configurazione."
	else
		echo "AMS rimosso. Messaggi ($VARDIR) e configurazione (/etc/ams) conservati."
	fi
}

case ${1:-} in
'') do_install ;;
--uninstall) do_uninstall ;;
--purge) do_uninstall purge ;;
*) echo "Uso: $0 [--uninstall | --purge]" >&2; exit 1 ;;
esac
