#!/bin/bash
# RootSpeak - Advanced Messaging System for Linux
# Gira sul server delle prove: avvia la VM di prova da una copia pulita del disco
# base (prepare.sh) e attende che risponda su ssh (127.0.0.1:2222 del server).
#   start.sh CARTELLA_VM
set -euo pipefail
DIR=$1
cd "$DIR"
[ -f base.qcow2 ] || { echo "manca il disco base: lanciare prima prepare.sh" >&2; exit 1; }
"$(dirname "$0")/stop.sh" "$DIR" 2>/dev/null || true
rm -f prova.qcow2 monitor.sock
qemu-img create -q -f qcow2 -b base.qcow2 -F qcow2 prova.qcow2
qemu-system-x86_64 -enable-kvm -cpu host -m 8G -smp 6 -name rootspeak-prova-vm \
	-drive file=prova.qcow2,if=virtio -nic user,model=virtio-net-pci,hostfwd=tcp:127.0.0.1:2222-:22 \
	-display none -vga virtio -monitor unix:"$DIR/monitor.sock",server,nowait \
	-serial file:"$DIR/prova.log" -daemonize -pidfile "$DIR/prova.pid"
for i in $(seq 1 120); do
	# pronto quando sshd risponde con il suo saluto
	if [ "$(timeout 2 bash -c 'exec 3<>/dev/tcp/127.0.0.1/2222; head -c 4 <&3' 2>/dev/null)" = SSH- ]; then
		echo "VM pronta dopo ${i}s"
		exit 0
	fi
	sleep 1
done
echo "la VM non risponde su ssh" >&2
exit 1
