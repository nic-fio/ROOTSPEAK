#!/bin/sh
# RootSpeak - Advanced Messaging System for Linux
# Runs inside a test VM, once, while cloud-init prepares the base disk
# (prepare.sh puts it there, the desktop profile runs it): the users of the
# scenarios as in the container, «sara» with the graphical session, root's ssh
# key for the scenarios' sessions, the Italian locale. Any family of distribution.
set -eu

# the administrators' group of the distribution: sudo on Debian and Ubuntu, wheel elsewhere
if getent group sudo >/dev/null; then admins=sudo; else admins=wheel; fi
nologin=$(command -v nologin || echo /sbin/nologin)
# a user whose name is already a group (Ubuntu's cloud image has an «admin» group) gets it as primary group
mkuser() { u=$1; shift; if getent group "$u" >/dev/null; then useradd -m -g "$u" "$@" "$u"; else useradd -m "$@" "$u"; fi; }
groupadd -f developers
mkuser admin -s /bin/bash -G "$admins"
mkuser mario -s /bin/bash -G developers
mkuser anna -s /bin/bash -G developers
mkuser luca -s /bin/bash
mkuser sara -s /bin/bash
mkuser service -s "$nologin"
echo 'admin ALL=(ALL) NOPASSWD: ALL' >/etc/sudoers.d/admin
chmod 440 /etc/sudoers.d/admin

# no first-start assistant for the desktop user
install -d -m 700 -o sara -g "$(id -gn sara)" /home/sara/.config
install -m 644 -o sara -g "$(id -gn sara)" /dev/null /home/sara/.config/gnome-initial-setup-done

install -d -m 700 /root/.ssh
[ -f /root/.ssh/id_ed25519 ] || ssh-keygen -q -t ed25519 -N '' -f /root/.ssh/id_ed25519
for u in admin mario anna luca sara; do
	g=$(id -gn $u)
	install -d -m 700 -o $u -g "$g" /home/$u/.ssh
	install -m 600 -o $u -g "$g" /root/.ssh/id_ed25519.pub /home/$u/.ssh/authorized_keys
done
printf 'Host localhost\n  StrictHostKeyChecking no\n  UserKnownHostsFile /dev/null\n  LogLevel ERROR\n' >/root/.ssh/config

# the Italian locale (the language of the system is chosen by run.sh at each run)
# (Debian reads /etc/locale.gen, Ubuntu takes the names; Fedora and RHEL have langpacks)
. /etc/os-release
if [ "$ID" = debian ]; then
	sed -i 's/^# *\(it_IT.UTF-8\|en_US.UTF-8\)/\1/' /etc/locale.gen
	locale-gen >/dev/null
elif command -v locale-gen >/dev/null; then
	locale-gen it_IT.UTF-8 en_US.UTF-8 >/dev/null
fi
systemctl set-default graphical.target
touch /var/lib/rootspeak-test-ready
# prepare.sh looks for this line in the serial console
echo 'rootspeak-test-users: done' >/dev/ttyS0 2>/dev/null || echo 'rootspeak-test-users: done' >/dev/console
