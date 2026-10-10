#!/bin/bash
# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# RootSpeak - Advanced Messaging System for Linux
# Runs on the test server. Builds once the base disk of a test VM with a desktop,
# from the cloud image named in its profile (tests/vm/desktops/NAME.yaml): at
# the first boot cloud-init installs the desktop and the users (users.sh), then
# the VM shuts down. Every test run starts from a clean copy of this disk (run.sh).
# The profile's fingerprint is kept with the disk: run.sh prepares it again when
# the profile or users.sh change.
#   prepare.sh VM_FOLDER PUBLIC_KEYS_FILE PROFILE [MEMORY]
set -euo pipefail
DIR=$1
KEYS_FILE=$2
PROFILE=$3
MEM=${4:-8G}
HERE=$(cd "$(dirname "$0")" && pwd)
url=$(sed -n 's/^# image: //p' "$PROFILE")
image=$(dirname "$DIR")/images/$(basename "$url")
mkdir -p "$DIR" "$(dirname "$image")"
cd "$DIR"
[ -f "$image" ] || { echo "downloading $(basename "$url")…"; curl -sSfL -o "$image.part" "$url" && mv "$image.part" "$image"; }

keys=$(sed '/^$/d; s/.*/"&"/' "$KEYS_FILE" | paste -sd, -)
# users.sh goes into the VM as /usr/local/sbin/rootspeak-test-users (the profile runs it)
common="  - path: /usr/local/sbin/rootspeak-test-users\n    permissions: '0755'\n    encoding: b64\n    content: $(base64 -w0 "$HERE/users.sh")"
sed -e "s|\[@KEYS@\]|[$keys]|" -e "s|^  @COMMON@\$|$common|" "$PROFILE" >user-data
printf 'instance-id: rootspeak-desktop-%s\nlocal-hostname: rootspeak-desktop\n' "$(date +%s)" >meta-data
genisoimage -quiet -output seed.iso -volid cidata -joliet -rock user-data meta-data

rm -f base.qcow2 base.fingerprint prepare.log
qemu-img create -q -f qcow2 -b "$image" -F qcow2 base.qcow2 30G
echo "installing $(basename "$PROFILE" .yaml) in the VM: it takes several minutes…"
timeout 5400 qemu-system-x86_64 -enable-kvm -cpu host -m "$MEM" -smp 6 -name "rootspeak-prepare-$(basename "$DIR")" \
	-drive file=base.qcow2,if=virtio -drive file=seed.iso,media=cdrom,readonly=on \
	-nic user,model=virtio-net-pci -display none -vga virtio -serial file:prepare.log
# ready only if the users were made and no cloud-init module failed (packages included)
if grep -q "rootspeak-test-users: done" prepare.log &&
	! grep -qE "Failed to run module|Failure when attempting to install packages" prepare.log; then
	grep -hv '^ *# ' "$PROFILE" "$HERE/users.sh" | sha256sum | cut -c1-12 >base.fingerprint
	echo "base disk ready: $DIR/base.qcow2 ($(du -h base.qcow2 | cut -f1))"
else
	echo "cloud-init did not finish: see $DIR/prepare.log" >&2
	exit 1
fi
