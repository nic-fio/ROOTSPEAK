#!/bin/bash
# RootSpeak - Advanced Messaging System for Linux
# Runs on the test server. Builds once the base disk of the test VM (Debian 13
# + GNOME, users, automatic login of sara): at the first boot cloud-init
# installs and configures everything, then the VM shuts down. Every test run
# starts from a clean copy of this disk (run.sh).
#   prepare.sh VM_FOLDER PUBLIC_KEYS_FILE
set -euo pipefail
DIR=$1
KEYS_FILE=$2
HERE=$(cd "$(dirname "$0")" && pwd)
BASE=debian-13-generic-amd64.qcow2
cd "$DIR"
[ -f $BASE ] || curl -sSfL -o $BASE https://cloud.debian.org/images/cloud/trixie/latest/$BASE

keys=$(sed '/^$/d; s/.*/"&"/' "$KEYS_FILE" | paste -sd, -)
sed "s|@KEYS@|$keys|" "$HERE/user-data.tpl" >user-data
printf 'instance-id: rootspeak-desktop-%s\nlocal-hostname: rootspeak-desktop\n' "$(date +%s)" >meta-data
genisoimage -quiet -output seed.iso -volid cidata -joliet -rock user-data meta-data

rm -f base.qcow2 prepare.log
qemu-img create -q -f qcow2 -b $BASE -F qcow2 base.qcow2 24G
echo "installing in the VM (GNOME): it takes a few minutes…"
timeout 3600 qemu-system-x86_64 -enable-kvm -cpu host -m 8G -smp 6 -name rootspeak-prepare \
	-drive file=base.qcow2,if=virtio -drive file=seed.iso,media=cdrom,readonly=on \
	-nic user,model=virtio-net-pci -display none -vga virtio -serial file:prepare.log
if grep -q "Cloud-init v.* finished" prepare.log; then
	echo "base disk ready: $DIR/base.qcow2 ($(du -h base.qcow2 | cut -f1))"
else
	echo "cloud-init did not finish: see $DIR/prepare.log" >&2
	exit 1
fi
