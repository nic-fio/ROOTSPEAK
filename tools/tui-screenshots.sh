#!/bin/bash
# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# RootSpeak - Advanced Messaging System for Linux
# Real TUI screenshots for the manuals: in the test machine (a container with
# real users and sessions) it prepares a few messages, has the users confirm and
# postpone, opens the TUI as root on a 116×30 virtual terminal, presses keys and
# saves each screen, with its colours, in docs/sources/screens/NAME.ans. The
# manual generator turns them into HTML.
#   tools/tui-screenshots.sh        (after make; uses the image of tests/container)
set -uo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
NAME=rootspeak-screenshots
OUT=$ROOT/docs/sources/screens
mkdir -p "$OUT"
podman image exists rootspeak-test || podman build -q -t rootspeak-test -f "$ROOT/tests/container/Containerfile" "$ROOT/tests/container" >/dev/null
podman rm -f $NAME >/dev/null 2>&1
podman run -d --name $NAME --systemd=always -v "$ROOT:/opt/rootspeak-src:ro,Z" -v "$OUT:/opt/screens:Z" rootspeak-test >/dev/null || exit 1
trap 'podman rm -f $NAME >/dev/null 2>&1' EXIT
for i in $(seq 1 30); do
	s=$(podman exec $NAME systemctl is-system-running 2>/dev/null)
	[ "$s" = running ] || [ "$s" = degraded ] && break
	sleep 1
done
podman exec $NAME /opt/rootspeak-src/install.sh >/dev/null 2>&1
podman exec -i -e TERM=xterm-256color $NAME python3 - <<'PY'
import fcntl, os, pty, select, struct, subprocess, termios, time

def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True)

A = "/usr/local/bin/rspeak"
V = "/var/lib/rootspeak"
sh(f'{A} send --to @developers,luca --expires 1d --title "Server update" "Tonight at 11 pm the mail server is updated."')
# a copy that cannot arrive: dario's mailbox belongs to someone else
sh(f"install -d -m 700 -o nobody {V}/users/dario")
sh(f'{A} send --to all --title Maintenance "On Saturday from 8 am to 12 noon the server will be off for disk maintenance.\nPlease save your work by Friday evening."')
sh(f'{A} send --to mario "Your account expires on Friday: please drop by the IT office."')
sh(f'{A} send --to mario,anna --expires 15m --title Reboot "Reboot at 1 pm."')
sh(f'{A} revoke 4')
now = int(time.time())
def confirm(u, mid, channel):
    sh(f"runuser -u {u} -- sh -c 'printf \"%s %s\\n\" {now} \"{channel}\" > {V}/users/{u}/acks/{mid}; mv {V}/users/{u}/inbox/{mid} {V}/users/{u}/read/{mid}'")
def postpone(u, mid):
    sh(f"runuser -u {u} -- touch {V}/users/{u}/state/{mid}.term")
for u in ("anna", "mario", "luca"):
    confirm(u, 1, "desktop" if u == "anna" else "terminal pts/1")
for u, c in (("anna", "desktop"), ("zeno", "terminal pts/2"), ("admin", "terminal pts/0"), ("fabio", "desktop")):
    confirm(u, 2, c)
postpone("mario", 2)
postpone("kora", 2)

pid, fd = pty.fork()
if pid == 0:
    os.execvp(A, ["rspeak"])
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 30, 116, 0, 0))

def frame(t=1.2):
    out, t0 = b"", time.time()
    while time.time() - t0 < t:
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            out += os.read(fd, 65536)
    return out.split(b"\x1b[H")[-1]

def save(name, t=1.2):
    fr = frame(t)
    fr = fr.split(b"\x1b[J")[0]
    open(f"/opt/screens/{name}.ans", "wb").write(fr)

def keys(b, pause=0.4):
    os.write(fd, b)
    time.sleep(pause)

frame(1.5)
keys(b"\x1b[B")
keys(b"\x1b[B")
save("list")
keys(b"\r")
save("detail")
keys(b"\t")
save("history")
keys(b"\x1b")
keys(b"m", 0.8)
save("reminder")
keys(b"n")
keys(b"n", 0.8)
for c in [b"@developers", b"\t", b"Maintenance", b"\t", b"2d", b"\t",
          b"On Saturday from 8 am to 12 noon the server will be off.\rPlease save your work by Friday evening."]:
    keys(c, 0.6)
save("new")
keys(b"\x13", 0.8)
save("send")
keys(b"n")
keys(b"\x1b")
keys(b"y")
keys(b"q")
PY
ls "$OUT"
