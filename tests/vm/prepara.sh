#!/bin/bash
# AMS - Advanced Messaging System for linux
# Gira sul server delle prove. Costruisce una volta il disco base della VM di
# prova (Debian 13 + GNOME, utenti, login automatico di sara): al primo avvio
# cloud-init installa e configura tutto, poi la VM si spegne. Le esecuzioni dei
# test partono ogni volta da una copia pulita di questo disco (esegui.sh).
#   prepara.sh CARTELLA_VM FILE_CHIAVI_PUBBLICHE
set -euo pipefail
DIR=$1
CHIAVI_FILE=$2
QUI=$(cd "$(dirname "$0")" && pwd)
BASE=debian-13-generic-amd64.qcow2
cd "$DIR"
[ -f $BASE ] || curl -sSfL -o $BASE https://cloud.debian.org/images/cloud/trixie/latest/$BASE

chiavi=$(sed '/^$/d; s/.*/"&"/' "$CHIAVI_FILE" | paste -sd, -)
sed "s|@CHIAVI@|$chiavi|" "$QUI/user-data.tpl" >user-data
printf 'instance-id: ams-desktop-%s\nlocal-hostname: ams-desktop\n' "$(date +%s)" >meta-data
genisoimage -quiet -output seed.iso -volid cidata -joliet -rock user-data meta-data

rm -f base.qcow2 prepara.log
qemu-img create -q -f qcow2 -b $BASE -F qcow2 base.qcow2 24G
echo "installazione nella VM (GNOME): richiede alcuni minuti…"
timeout 3600 qemu-system-x86_64 -enable-kvm -cpu host -m 8G -smp 6 -name ams-prepara \
	-drive file=base.qcow2,if=virtio -drive file=seed.iso,media=cdrom,readonly=on \
	-nic user,model=virtio-net-pci -display none -vga virtio -serial file:prepara.log
if grep -q "Cloud-init v.* finished" prepara.log; then
	echo "disco base pronto: $DIR/base.qcow2 ($(du -h base.qcow2 | cut -f1))"
else
	echo "cloud-init non è terminato: vedi $DIR/prepara.log" >&2
	exit 1
fi
