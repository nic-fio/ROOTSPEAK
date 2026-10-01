#!/bin/bash
# RootSpeak - Advanced Messaging System for Linux
# Prove dal vero nella VM con desktop, sul server delle prove (per non caricare
# il PC): copia il codice sul server, avvia la VM da una copia pulita del disco
# base, installa RootSpeak, esegue gli scenari (tests/container/scenarios.py, con quelli
# del desktop), scatta le schermate richieste e riporta tutto in
# tests/vm/results/. La VM si spegne alla fine.
#   tests/vm/run.sh               RSPEAK_SERVER e RSPEAK_DIR per cambiare server e cartella;
#                                    RSPEAK_PROVA_LINGUA=en per il desktop in inglese (predefinito: it);
#                                    RSPEAK_PROVA_SOLO=i_desktop,… per eseguire solo alcuni gruppi
# Il disco base si prepara una volta con --prepara (circa 10 minuti).
set -uo pipefail
QUI=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$QUI/../.." && pwd)
SERVER=${RSPEAK_SERVER:-192.168.0.2}
DIR=${RSPEAK_DIR:-/media/ROOTSPEAK}
DESK=sara
case ${RSPEAK_PROVA_LINGUA:-it} in
it) LOCALE_DESK=it_IT.UTF-8 ;;
en) LOCALE_DESK=en_US.UTF-8 ;;
*) echo "RSPEAK_PROVA_LINGUA: it o en" >&2; exit 1 ;;
esac
OPZ=(-o BatchMode=yes -o LogLevel=ERROR)
VMOPZ=(-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -J "$SERVER" -p 2222)

# (il profilo della shell del server stampa avvisi di tput senza terminale: si scartano)
x() { ssh "${OPZ[@]}" "$SERVER" "export TERM=dumb; $*" 2> >(grep -v '^tput:' >&2); }
v() { ssh "${OPZ[@]}" "${VMOPZ[@]}" root@127.0.0.1 "$@"; }

echo "codice sul server ($SERVER:$DIR/src)…"
tar --exclude=.git --exclude='./tests/*/results' -cf - -C "$ROOT" . |
	x "rm -rf $DIR/src && mkdir -p $DIR/src $DIR/vm/captures && tar -xf - -C $DIR/src" || exit 1

if [ "${1:-}" = --prepara ] || ! x "test -f $DIR/vm/base.qcow2"; then
	cat ~/.ssh/id_ed25519.pub | x "cat > $DIR/vm/chiavi.pub"
	x "$DIR/src/tests/vm/prepare.sh $DIR/vm $DIR/vm/chiavi.pub" || exit 1
fi

x "$DIR/src/tests/vm/start.sh $DIR/vm" || exit 1
trap 'x "$DIR/src/tests/vm/stop.sh $DIR/vm"; echo "VM spenta"' EXIT

echo "RootSpeak nella VM…"
tar --exclude=.git -cf - -C "$ROOT" . |
	v "rm -rf /opt/rootspeak-src && mkdir -p /opt/rootspeak-src && tar -xf - -C /opt/rootspeak-src && /opt/rootspeak-src/install.sh | head -1"
# niente tour di benvenuto né avvisi degli aggiornamenti sul desktop di prova
# (anche in user-data.tpl, per i dischi base preparati dopo)
v "apt-get -qq -y purge gnome-tour gnome-software >/dev/null 2>&1; true"
# lingue: il sistema in italiano (le sessioni ssh degli scenari), il desktop di
# prova nella lingua scelta (AccountsService): la finestra segue la sessione grafica
v "dpkg -s locales >/dev/null 2>&1 || apt-get -qq -y install locales >/dev/null
	sed -i 's/^# *\\(it_IT.UTF-8\\|en_US.UTF-8\\)/\\1/' /etc/locale.gen && locale-gen >/dev/null
	echo LANG=it_IT.UTF-8 >/etc/default/locale
	f=/var/lib/AccountsService/users/$DESK
	if grep -q '^Language=' \$f 2>/dev/null; then sed -i 's/^Language=.*/Language=$LOCALE_DESK/' \$f
	else printf '[User]\\nLanguage=$LOCALE_DESK\\n' >>\$f; fi" || exit 1
# un nuovo login grafico, perché l'agente parta dall'avvio automatico come su un sistema vero
v "systemctl restart gdm; for i in \$(seq 1 90); do
	pgrep -u $DESK -f '^(/bin/bash )?/usr/local/lib/rootspeak/rootspeak-user agent\$' >/dev/null && { echo \"desktop di $DESK pronto dopo \${i}s\"; exit 0; }
	sleep 1; done; echo 'desktop non pronto' >&2; exit 1" || exit 1

rm -rf "$QUI/results" && mkdir -p "$QUI/results/captures"
x "rm -f $DIR/vm/captures/*"
v "LANG=it_IT.UTF-8 RSPEAK_PROVA_COMMIT=$("$ROOT/tools/fingerprint.sh" --commit) RSPEAK_PROVA_IMPRONTA=$("$ROOT/tools/fingerprint.sh") RSPEAK_PROVA_SOLO=${RSPEAK_PROVA_SOLO:-} RSPEAK_PROVA_DESKTOP=$DESK python3 -u /opt/rootspeak-src/tests/container/scenarios.py /opt/results" |
	while IFS= read -r riga; do
		case $riga in
		"@@CATTURA "*) x "python3 $DIR/src/tests/vm/capture.py $DIR/vm/monitor.sock $DIR/vm/captures/${riga#@@CATTURA }.ppm" ;;
		*) printf '%s\n' "$riga" ;;
		esac
	done
esito=${PIPESTATUS[0]}

v "tar -cf - -C /opt/results ." | tar -xf - -C "$QUI/results"
x "tar -cf - -C $DIR/vm/captures ." | tar -xf - -C "$QUI/results/captures"
python3 - "$QUI/results/captures" <<'PY'
import pathlib, sys
from PIL import Image
for f in pathlib.Path(sys.argv[1]).glob("*.ppm"):
    Image.open(f).save(f.with_suffix(".png"))
    f.unlink()
PY
echo "risultati in $QUI/results"
exit "$esito"
