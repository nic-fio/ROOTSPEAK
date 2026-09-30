#!/bin/bash
# AMS - Advanced Messaging System
# Prove dal vero in una macchina di prova (container con systemd, senza root):
# costruisce l'immagine se manca, avvia la macchina, installa AMS dal repository,
# esegue gli scenari e salva i risultati in tests/container/results/.
#   tests/container/run.sh            (--ricostruisci per rifare l'immagine)
set -uo pipefail
QUI=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$QUI/../.." && pwd)
NOME=ams-prova
mkdir -p "$QUI/results"

if [ "${1:-}" = --ricostruisci ] || ! podman image exists $NOME; then
	echo "costruzione dell'immagine…"
	podman build -q -t $NOME -f "$QUI/Containerfile" "$QUI" >/dev/null || exit 1
fi
podman rm -f $NOME >/dev/null 2>&1
podman run -d --name $NOME --systemd=always \
	-v "$ROOT:/opt/ams-src:ro,Z" -v "$QUI/results:/opt/results:Z" $NOME >/dev/null || exit 1
trap 'podman rm -f $NOME >/dev/null 2>&1' EXIT
for i in $(seq 1 30); do
	s=$(podman exec $NOME systemctl is-system-running 2>/dev/null)
	[ "$s" = running ] || [ "$s" = degraded ] && break
	sleep 1
done
echo "macchina di prova: $s"
podman exec $NOME /opt/ams-src/install.sh 2>&1 | grep -v '^Attenzione: manca zenity' | head -1
podman exec -e LANG=it_IT.UTF-8 -e AMS_PROVA_COMMIT="$("$ROOT/tools/fingerprint.sh" --commit)" \
	-e AMS_PROVA_IMPRONTA="$("$ROOT/tools/fingerprint.sh")" $NOME python3 /opt/ams-src/tests/container/scenarios.py /opt/results
