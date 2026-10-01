#!/bin/bash
# RootSpeak - Advanced Messaging System for Linux
# Gira sul server delle prove. Costruisce una volta il disco base della VM di
# prova (Debian 13 + GNOME, utenti, login automatico di sara): al primo avvio
# cloud-init installa e configura tutto, poi la VM si spegne. Le esecuzioni dei
# test partono ogni volta da una copia pulita di questo disco (run.sh).
#   prepare.sh CARTELLA_VM FILE_CHIAVI_PUBBLICHE
set -euo pipefail
DIR=$1
CHIAVI_FILE=$2
QUI=$(cd "$(dirname "$0")" && pwd)
BASE=debian-13-generic-amd64.qcow2
cd "$DIR"
[ -f $BASE ] || curl -sSfL -o $BASE https://cloud.debian.org/images/cloud/trixie/latest/$BASE

chiavi=$(sed '/^$/d; s/.*/"&"/' "$CHIAVI_FILE" | paste -sd, -)
sed "s|@CHIAVI@|$chiavi|" "$QUI/user-data.tpl" >user-data
printf 'instance-id: rootspeak-desktop-%s\nlocal-hostname: rootspeak-desktop\n' "$(date +%s)" >meta-data
genisoimage -quiet -output seed.iso -volid cidata -joliet -rock user-data meta-data

rm -f base.qcow2 prepare.log
qemu-img create -q -f qcow2 -b $BASE -F qcow2 base.qcow2 24G
echo "installazione nella VM (GNOME): richiede alcuni minuti…"
timeout 3600 qemu-system-x86_64 -enable-kvm -cpu host -m 8G -smp 6 -name rootspeak-prepara \
	-drive file=base.qcow2,if=virtio -drive file=seed.iso,media=cdrom,readonly=on \
	-nic user,model=virtio-net-pci -display none -vga virtio -serial file:prepare.log
if grep -q "Cloud-init v.* finished" prepare.log; then
	echo "disco base pronto: $DIR/base.qcow2 ($(du -h base.qcow2 | cut -f1))"
else
	echo "cloud-init non è terminato: vedi $DIR/prepare.log" >&2
	exit 1
fi
