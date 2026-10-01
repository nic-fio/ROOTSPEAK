#!/bin/bash
# RootSpeak - Advanced Messaging System for Linux
# Runs on the test server: starts the test VM from a clean copy of the base
# disk (prepare.sh) and waits until it answers on ssh (127.0.0.1:2222 of the server).
#   start.sh VM_FOLDER
set -euo pipefail
DIR=$1
cd "$DIR"
[ -f base.qcow2 ] || { echo "the base disk is missing: run prepare.sh first" >&2; exit 1; }
"$(dirname "$0")/stop.sh" "$DIR" 2>/dev/null || true
rm -f test.qcow2 monitor.sock
qemu-img create -q -f qcow2 -b base.qcow2 -F qcow2 test.qcow2
qemu-system-x86_64 -enable-kvm -cpu host -m 8G -smp 6 -name rootspeak-test-vm \
	-drive file=test.qcow2,if=virtio -nic user,model=virtio-net-pci,hostfwd=tcp:127.0.0.1:2222-:22 \
	-display none -vga virtio -monitor unix:"$DIR/monitor.sock",server,nowait \
	-serial file:"$DIR/test.log" -daemonize -pidfile "$DIR/test.pid"
for i in $(seq 1 120); do
	# ready when sshd answers with its greeting
	if [ "$(timeout 2 bash -c 'exec 3<>/dev/tcp/127.0.0.1/2222; head -c 4 <&3' 2>/dev/null)" = SSH- ]; then
		echo "VM ready after ${i}s"
		exit 0
	fi
	sleep 1
done
echo "the VM does not answer on ssh" >&2
exit 1
