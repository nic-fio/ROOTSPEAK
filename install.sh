#!/bin/bash
# RootSpeak - Advanced Messaging System for Linux: installazione e rimozione.
#   ./install.sh              installa
#   ./install.sh --uninstall  rimuove (i messaggi in /var/lib/rootspeak restano)
#   ./install.sh --purge      rimuove anche i messaggi
# Installa la versione in C compilata in build/ (make); se manca, la compila.
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
LOCALEDIR=$PREFIX/share/locale
# l'agente del desktop
AGENT_RE="^$LIBDIR/rootspeak-user agent\$"

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
	for c in zenity loginctl systemd-run; do
		command -v "$c" >/dev/null || echo "Attenzione: manca $c" >&2
	done

	# I programmi compilati con le cartelle di questa installazione: se mancano
	# o sono stati compilati per un'altra, si compilano.
	if ! [ -x "$SRC/build/rspeak" ] || ! [ -x "$SRC/build/rootspeak-user" ] ||
		! grep -qaF "$LIBDIR" "$SRC/build/rspeak"; then
		make -C "$SRC" PREFIX="$PREFIX" all >/dev/null ||
			{ echo "Compilazione non riuscita: servono gcc, make, pkg-config, libsystemd-dev e gettext" >&2; exit 1; }
	fi
	install -d -m 755 "$LIBDIR" "$BINDIR" /etc/rootspeak /etc/profile.d /etc/xdg/autostart
	install -m 755 "$SRC/build/rootspeak-user" "$LIBDIR/rootspeak-user"
	for mo in "$SRC"/build/locale/*/LC_MESSAGES/rootspeak.mo; do
		[ -e "$mo" ] || continue
		l=${mo#"$SRC"/build/locale/}
		l=${l%%/*}
		install -d -m 755 "$LOCALEDIR/$l/LC_MESSAGES"
		install -m 644 "$mo" "$LOCALEDIR/$l/LC_MESSAGES/rootspeak.mo"
	done
	install -m 750 -o root -g "$group" "$SRC/build/rspeak" "$BINDIR/rspeak"
	[ -e /etc/rootspeak/rootspeak.conf ] || install -m 644 "$SRC/etc/rootspeak/rootspeak.conf" /etc/rootspeak/rootspeak.conf
	# manuali in un solo file ciascuno
	install -d -m 755 "$DOCDIR"
	install -m 644 "$SRC/docs/User Manual.html" "$SRC/docs/Technical Manual.html" "$DOCDIR/"
	subst "$SRC/etc/profile.d/rootspeak.sh" >/etc/profile.d/rootspeak.sh
	subst "$SRC/etc/rootspeak.bash" >"$LIBDIR/rootspeak.bash"
	subst "$SRC/etc/rootspeak.zsh" >"$LIBDIR/rootspeak.zsh"
	chmod 644 "$LIBDIR/rootspeak.bash" "$LIBDIR/rootspeak.zsh"
	# zsh: un richiamo nello zshrc di sistema, se zsh è installata (se lo sarà
	# dopo, basta rilanciare install.sh); fish: un file in conf.d, che fish
	# legge anche se viene installata dopo
	if [ -f "$ZSHRC" ] && ! grep -qF "$MARK" "$ZSHRC"; then
		echo "[ -r $LIBDIR/rootspeak.zsh ] && . $LIBDIR/rootspeak.zsh  $MARK" >>"$ZSHRC"
	fi
	install -d -m 755 "$(dirname "$FISHCONF")"
	subst "$SRC/etc/rootspeak.fish" >"$FISHCONF"
	chmod 644 "$FISHCONF"
	subst "$SRC/etc/xdg/autostart/rootspeak-agent.desktop" >/etc/xdg/autostart/rootspeak-agent.desktop
	chmod 644 /etc/profile.d/rootspeak.sh /etc/xdg/autostart/rootspeak-agent.desktop

	# Su Debian e Ubuntu le shell non di login (es. i terminali del desktop)
	# non leggono /etc/profile.d: l'hook va richiamato da bash.bashrc.
	if [ -f "$BASHRC" ] && ! grep -qF "$MARK" "$BASHRC"; then
		echo "[ -r /etc/profile.d/rootspeak.sh ] && . /etc/profile.d/rootspeak.sh  $MARK" >>"$BASHRC"
	fi

	install -d -m 755 "$VARDIR" "$VARDIR/users"
	install -d -m 700 "$VARDIR/sent"

	# Gli agenti del desktop di una versione precedente vanno chiusi: il primo
	# `rspeak send` o il prossimo login ne avviano uno aggiornato.
	pkill -f "$AGENT_RE" 2>/dev/null || true

	echo "RootSpeak installato. Comando: $BINDIR/rspeak (utilizzabile dal gruppo $group)."
	echo "Manuali: $DOCDIR/User Manual.html e Technical Manual.html"
	echo "Le sessioni già aperte ricevono i messaggi sul terminale subito e la domanda"
	echo "di conferma dalla prossima shell o dal prossimo login."
}

do_uninstall() {
	rm -f "$BINDIR/rspeak" /etc/profile.d/rootspeak.sh /etc/xdg/autostart/rootspeak-agent.desktop
	rm -rf "$LIBDIR" "$DOCDIR"
	rm -f "$LOCALEDIR"/*/LC_MESSAGES/rootspeak.mo
	if [ -f "$BASHRC" ]; then sed -i "\|$MARK|d" "$BASHRC"; fi
	if [ -f "$ZSHRC" ]; then sed -i "\|$MARK|d" "$ZSHRC"; fi
	rm -f "$FISHCONF"
	pkill -f "$AGENT_RE" 2>/dev/null || true
	if [ "${1:-}" = purge ]; then
		rm -rf "$VARDIR" /etc/rootspeak
		echo "RootSpeak rimosso, insieme ai messaggi e alla configurazione."
	else
		echo "RootSpeak rimosso. Messaggi ($VARDIR) e configurazione (/etc/rootspeak) conservati."
	fi
}

case ${1:-} in
'') do_install ;;
--uninstall) do_uninstall ;;
--purge) do_uninstall purge ;;
*) echo "Uso: $0 [--uninstall | --purge]" >&2; exit 1 ;;
esac
