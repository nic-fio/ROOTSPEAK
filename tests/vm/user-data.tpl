#cloud-config
# RootSpeak - Advanced Messaging System for Linux
# Macchina virtuale di prova con desktop: Debian 13, GNOME su Wayland, login
# automatico di «sara»; gli altri utenti come nel container (tests/container).
# @CHIAVI@ viene sostituito da prepare.sh con le chiavi ssh autorizzate per root.
hostname: rootspeak-desktop
disable_root: false
ssh_pwauth: false
users:
  - name: root
    ssh_authorized_keys: [@CHIAVI@]
package_update: true
packages:
  - gnome-core
  - gdm3
  - zenity
  - python3-dogtail
  - python3-pyatspi
  - at-spi2-core
  - dbus-user-session
  - openssh-server
  - sudo
  - python3
  - procps
write_files:
  - path: /etc/gdm3/daemon.conf
    content: |
      [daemon]
      AutomaticLoginEnable=true
      AutomaticLogin=sara
      [security]
      [xdmcp]
      [chooser]
      [debug]
  - path: /etc/dconf/profile/user
    content: |
      user-db:user
      system-db:local
  - path: /etc/dconf/db/local.d/00-rootspeak-prova
    content: |
      [org/gnome/desktop/session]
      idle-delay=uint32 0
      [org/gnome/desktop/screensaver]
      lock-enabled=false
      [org/gnome/desktop/interface]
      toolkit-accessibility=true
      [org/gnome/shell]
      welcome-dialog-last-shown-version='999'
      [org/gnome/software]
      download-updates=false
      allow-updates=false
  - path: /etc/sudoers.d/admin
    content: "admin ALL=(ALL) NOPASSWD: ALL\n"
runcmd:
  - groupadd -f sviluppo
  - useradd -m -s /bin/bash -G sudo admin
  - useradd -m -s /bin/bash -G sviluppo mario
  - useradd -m -s /bin/bash -G sviluppo anna
  - useradd -m -s /bin/bash luca
  - useradd -m -s /bin/bash sara
  - useradd -m -s /usr/sbin/nologin servizio
  - install -d -m 700 -o sara -g sara /home/sara/.config
  - touch /home/sara/.config/gnome-initial-setup-done && chown sara:sara /home/sara/.config/gnome-initial-setup-done
  - dconf update
  - apt-get -y purge gnome-tour gnome-software || true
  - mkdir -p /root/.ssh && ssh-keygen -q -t ed25519 -N '' -f /root/.ssh/id_ed25519
  - for u in admin mario anna luca sara; do install -d -m 700 -o $u -g $u /home/$u/.ssh; install -m 600 -o $u -g $u /root/.ssh/id_ed25519.pub /home/$u/.ssh/authorized_keys; done
  - printf 'Host localhost\n  StrictHostKeyChecking no\n  UserKnownHostsFile /dev/null\n  LogLevel ERROR\n' > /root/.ssh/config
  - systemctl set-default graphical.target
  - touch /var/lib/rootspeak-prova-pronta
power_state:
  mode: poweroff
  condition: true
