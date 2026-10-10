#!/bin/sh
# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# RootSpeak - Advanced Messaging System for Linux
# Prepares the test machine on any distribution with systemd (run once, when the
# image is built, by tests/container/Containerfile): the packages to build and run
# RootSpeak, sshd, the shells of the scenarios, the Italian locale and the test
# users. The package manager says the family: apt, dnf, zypper, pacman.
# A shell the distribution does not have is left out: its scenarios are «not tested».
set -eu

# a package that may be missing on some distributions: no error
try() { "$@" >/dev/null 2>&1 || echo "setup: not available: $*" >&2; }

if command -v apt-get >/dev/null; then
	export DEBIAN_FRONTEND=noninteractive
	apt-get update -q
	apt-get install -y -q --no-install-recommends \
		systemd systemd-sysv dbus libpam-systemd openssh-server openssh-client sudo \
		python3 procps util-linux bsdutils coreutils less locales tar \
		gcc libc6-dev make pkg-config libsystemd-dev
	for p in zsh fish ksh dash; do try apt-get install -y -q --no-install-recommends $p; done
	rm -rf /var/lib/apt/lists/*
	sed -i 's/^# *\(it_IT.UTF-8\|en_US.UTF-8\)/\1/' /etc/locale.gen && locale-gen >/dev/null
elif command -v dnf >/dev/null; then
	# the shells that RHEL and its rebuilds keep in EPEL (fish, dash)
	. /etc/os-release
	# (RHEL's rebuilds say ID_LIKE="rhel centos fedora": only ID tells Fedora apart)
	if [ "$ID" != fedora ]; then
		try dnf install -y epel-release
		try dnf install -y oracle-epel-release-el"${VERSION_ID%%.*}"
	fi
	dnf install -y --setopt=install_weak_deps=False \
		systemd systemd-pam dbus openssh-server openssh-clients sudo python3 procps-ng util-linux less tar shadow-utils \
		gcc make pkgconf-pkg-config systemd-devel
	# (the Red Hat images, UBI, have no Italian)
	for p in glibc-langpack-it glibc-langpack-en; do try dnf install -y $p; done
	for p in zsh fish ksh dash; do try dnf install -y --setopt=install_weak_deps=False $p; done
	dnf clean all >/dev/null
elif command -v zypper >/dev/null; then
	zypper -n -q install --no-recommends \
		systemd dbus-1 openssh-server openssh-clients sudo python3 procps util-linux util-linux-systemd less tar shadow \
		gcc make pkg-config systemd-devel glibc-locale
	for p in zsh fish ksh dash; do try zypper -n -q install --no-recommends $p; done
	# SLES 15 has Python 3.6, too old for the scenarios: a newer one, if there is
	try zypper -n -q install --no-recommends python311
	[ -x /usr/bin/python3.11 ] && ln -sf /usr/bin/python3.11 /usr/local/bin/python3
	zypper -n -q clean -a >/dev/null
elif command -v pacman >/dev/null; then
	# the Arch image leaves out the locale definitions: allowed again for the Italian one
	sed -i '/^NoExtract.*usr\/share\/i18n/d; /^NoExtract.*usr\/share\/locale/d' /etc/pacman.conf
	pacman -Syu --noconfirm --needed \
		systemd openssh sudo python procps-ng util-linux less tar shadow gcc make pkgconf glibc
	for p in zsh fish mksh dash; do try pacman -S --noconfirm --needed $p; done
	pacman -Scc --noconfirm >/dev/null 2>&1 || true
	sed -i 's/^# *\(it_IT.UTF-8\|en_US.UTF-8\)/\1/' /etc/locale.gen && try locale-gen
else
	echo "setup: unknown package manager" >&2
	exit 1
fi

# the machine ID: the Arch image leaves it out (on a real installation the systemd
# package writes it); without it dbus-broker does not start and logind records no session
if [ ! -s /etc/machine-id ] || grep -qx uninitialized /etc/machine-id; then
	rm -f /etc/machine-id
	systemd-machine-id-setup
fi

# the system language is Italian on purpose: RootSpeak must speak English anyway
echo 'LANG=it_IT.UTF-8' >/etc/locale.conf
[ -d /etc/default ] && echo 'LANG=it_IT.UTF-8' >/etc/default/locale

# the container images of RHEL (UBI) and AlmaLinux mask logind, which every real
# installation runs: without it there are no sessions (pam_systemd, «online»)
systemctl unmask systemd-logind.service >/dev/null 2>&1 || rm -f /etc/systemd/system/systemd-logind.service

ssh-keygen -A >/dev/null
systemctl enable ssh 2>/dev/null || systemctl enable sshd
# the administrators' group of the distribution: sudo on Debian and Ubuntu, wheel elsewhere
if getent group sudo >/dev/null; then admins=sudo; else getent group wheel >/dev/null || groupadd wheel; admins=wheel; fi
nologin=$(command -v nologin || echo /sbin/nologin)
ksh=$(command -v ksh || command -v mksh || true)
# openSUSE: /usr/bin/ksh is libalternatives' alts, which exits 255 when started as a
# login shell (argv[0] «-ksh»): no ksh user could log in there, with or without RootSpeak
case $(readlink -f "${ksh:-/}") in */alts) ksh=$(command -v ksh93) ;; esac

# the users the image brings (ubuntu in Ubuntu's): the scenarios know only theirs
for u in $(awk -F: '$3 >= 1000 && $3 < 60000 {print $1}' /etc/passwd); do userdel -r "$u" 2>/dev/null || userdel "$u"; done
groupadd developers
useradd -m -s /bin/bash -G "$admins" admin
useradd -m -s /bin/bash -G developers mario
useradd -m -s /bin/bash -G developers anna
useradd -m -s /bin/bash luca
useradd -m -s "$nologin" service
users="admin mario anna luca"
# users of the other shells, only if the shell is there
add() { [ -n "$2" ] || return 0; useradd -m -s "$2" "$1"; users="$users $1"; }
add zeno "$(command -v zsh || true)"
# (the group of each user from id: openSUSE puts them all in «users»)
[ ! -d /home/zeno ] || install -m 644 -o zeno -g "$(id -gn zeno)" /dev/null /home/zeno/.zshrc
add fabio "$(command -v fish || true)"
add kora "$ksh"
add dario "$(command -v dash || true)"
for sh in $(command -v zsh fish dash) $ksh; do grep -qx "$sh" /etc/shells || echo "$sh" >>/etc/shells; done

install -d -m 700 /root/.ssh
ssh-keygen -q -t ed25519 -N '' -f /root/.ssh/id_ed25519
for u in $users; do
	g=$(id -gn $u)
	install -d -m 700 -o $u -g "$g" /home/$u/.ssh
	install -m 600 -o $u -g "$g" /root/.ssh/id_ed25519.pub /home/$u/.ssh/authorized_keys
done
printf 'Host localhost\n  StrictHostKeyChecking no\n  UserKnownHostsFile /dev/null\n  LogLevel ERROR\n' >/root/.ssh/config
install -d -m 750 /etc/sudoers.d
echo 'admin ALL=(ALL) NOPASSWD: ALL' >/etc/sudoers.d/admin
chmod 440 /etc/sudoers.d/admin
