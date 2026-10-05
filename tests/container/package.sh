#!/bin/sh
# RootSpeak - Advanced Messaging System for Linux
# Installs, reinstalls and removes the RootSpeak package of this distribution
# with its package manager, from the folder of tools/release.sh, as an
# administrator would (the test machine has no network: only the
# dependencies already installed count).
#   package.sh install|reinstall|remove|purge|manager [FOLDER]
set -eu
DIR=${2:-/opt/release}
if command -v apt-get >/dev/null; then m=apt
elif command -v dnf >/dev/null; then m=dnf
elif command -v zypper >/dev/null; then m=zypper
elif command -v pacman >/dev/null; then m=pacman
else echo "package.sh: unknown package manager" >&2; exit 2
fi
deb=$(ls "$DIR"/rootspeak_*_amd64.deb 2>/dev/null || true)
rpm=$(ls "$DIR"/rootspeak-*.x86_64.rpm 2>/dev/null || true)
pkg=$(ls "$DIR"/rootspeak-*-x86_64.pkg.tar.zst 2>/dev/null || true)
export DEBIAN_FRONTEND=noninteractive
# (the package managers answer in English: the test machine is in Italian on purpose)
export LC_ALL=C
case $m:$1 in
*:manager) echo $m ;;
apt:install) apt-get install -y -q --no-install-recommends "$deb" ;;
apt:reinstall) apt-get install -y -q --no-install-recommends --reinstall "$deb" ;;
apt:remove) apt-get remove -y -q rootspeak ;;
apt:purge) apt-get purge -y -q rootspeak ;;
dnf:install) dnf -y -q --disablerepo='*' install "$rpm" ;;
dnf:reinstall) dnf -y -q --disablerepo='*' reinstall "$rpm" ;;
dnf:remove | dnf:purge) dnf -y -q --disablerepo='*' remove rootspeak ;;
zypper:install) zypper -n -q --no-remote --no-refresh install --no-recommends --allow-unsigned-rpm "$rpm" ;;
zypper:reinstall) zypper -n -q --no-remote --no-refresh install --no-recommends --allow-unsigned-rpm --force "$rpm" ;;
zypper:remove | zypper:purge) zypper -n -q --no-remote --no-refresh remove rootspeak ;;
pacman:install | pacman:reinstall) pacman -U --noconfirm "$pkg" ;;
pacman:remove | pacman:purge) pacman -R --noconfirm rootspeak ;;
*) echo "Usage: package.sh install|reinstall|remove|purge|manager [FOLDER]" >&2; exit 2 ;;
esac
