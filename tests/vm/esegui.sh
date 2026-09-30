#!/bin/bash
# AMS - Advanced Messaging System for linux
# Prove dal vero nella VM con desktop, sul server delle prove (per non caricare
# il PC): copia il codice sul server, avvia la VM da una copia pulita del disco
# base, installa AMS, esegue gli scenari (tests/container/scenari.py, con quelli
# del desktop), scatta le schermate richieste e riporta tutto in
# tests/vm/risultati/. La VM si spegne alla fine.
#   tests/vm/esegui.sh               AMS_SERVER e AMS_DIR per cambiare server e cartella;
#                                    AMS_PROVA_LINGUA=en per il desktop in inglese (predefinito: it);
#                                    AMS_PROVA_SOLO=i_desktop,… per eseguire solo alcuni gruppi
# Il disco base si prepara una volta con --prepara (circa 10 minuti).
set -uo pipefail
QUI=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$QUI/../.." && pwd)
SERVER=${AMS_SERVER:-192.168.0.2}
DIR=${AMS_DIR:-/media/AMS}
DESK=sara
case ${AMS_PROVA_LINGUA:-it} in
it) LOCALE_DESK=it_IT.UTF-8 ;;
en) LOCALE_DESK=en_US.UTF-8 ;;
*) echo "AMS_PROVA_LINGUA: it o en" >&2; exit 1 ;;
esac
OPZ=(-o BatchMode=yes -o LogLevel=ERROR)
VMOPZ=(-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -J "$SERVER" -p 2222)

# (il profilo della shell del server stampa avvisi di tput senza terminale: si scartano)
x() { ssh "${OPZ[@]}" "$SERVER" "export TERM=dumb; $*" 2> >(grep -v '^tput:' >&2); }
v() { ssh "${OPZ[@]}" "${VMOPZ[@]}" root@127.0.0.1 "$@"; }

echo "codice sul server ($SERVER:$DIR/src)…"
tar --exclude=.git --exclude='./tests/*/risultati' -cf - -C "$ROOT" . |
	x "rm -rf $DIR/src && mkdir -p $DIR/src $DIR/vm/catture && tar -xf - -C $DIR/src" || exit 1

if [ "${1:-}" = --prepara ] || ! x "test -f $DIR/vm/base.qcow2"; then
	cat ~/.ssh/id_ed25519.pub | x "cat > $DIR/vm/chiavi.pub"
	x "$DIR/src/tests/vm/prepara.sh $DIR/vm $DIR/vm/chiavi.pub" || exit 1
fi

x "$DIR/src/tests/vm/avvia.sh $DIR/vm" || exit 1
trap 'x "$DIR/src/tests/vm/ferma.sh $DIR/vm"; echo "VM spenta"' EXIT

echo "AMS nella VM…"
tar --exclude=.git -cf - -C "$ROOT" . |
	v "rm -rf /opt/ams-src && mkdir -p /opt/ams-src && tar -xf - -C /opt/ams-src && /opt/ams-src/install.sh | head -1"
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
	pgrep -u $DESK -f '^/bin/bash /usr/local/lib/ams/ams-user agent\$' >/dev/null && { echo \"desktop di $DESK pronto dopo \${i}s\"; exit 0; }
	sleep 1; done; echo 'desktop non pronto' >&2; exit 1" || exit 1

rm -rf "$QUI/risultati" && mkdir -p "$QUI/risultati/catture"
x "rm -f $DIR/vm/catture/*"
v "LANG=it_IT.UTF-8 AMS_PROVA_SOLO=${AMS_PROVA_SOLO:-} AMS_PROVA_DESKTOP=$DESK python3 -u /opt/ams-src/tests/container/scenari.py /opt/risultati" |
	while IFS= read -r riga; do
		case $riga in
		"@@CATTURA "*) x "python3 $DIR/src/tests/vm/cattura.py $DIR/vm/monitor.sock $DIR/vm/catture/${riga#@@CATTURA }.ppm" ;;
		*) printf '%s\n' "$riga" ;;
		esac
	done
esito=${PIPESTATUS[0]}

v "tar -cf - -C /opt/risultati ." | tar -xf - -C "$QUI/risultati"
x "tar -cf - -C $DIR/vm/catture ." | tar -xf - -C "$QUI/risultati/catture"
python3 - "$QUI/risultati/catture" <<'PY'
import pathlib, sys
from PIL import Image
for f in pathlib.Path(sys.argv[1]).glob("*.ppm"):
    Image.open(f).save(f.with_suffix(".png"))
    f.unlink()
PY
echo "risultati in $QUI/risultati"
exit "$esito"
