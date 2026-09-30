#!/bin/bash
# AMS - Advanced Messaging System
# Schermate vere della TUI per i manuali: nella macchina di prova (container
# con utenti e sessioni reali) prepara alcuni messaggi, fa confermare e
# rimandare gli utenti, apre la TUI come root su un terminale virtuale di
# 116×30, preme i tasti e salva ogni schermata, con i suoi colori, in
# docs/sources/screens/NOME.ans. Il generatore dei manuali le converte in HTML.
#   tools/tui-screenshots.sh        (dopo make; usa l'immagine di tests/container)
set -uo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
NOME=ams-schermate
OUT=$ROOT/docs/sources/screens
mkdir -p "$OUT"
podman image exists ams-prova || podman build -q -t ams-prova -f "$ROOT/tests/container/Containerfile" "$ROOT/tests/container" >/dev/null
podman rm -f $NOME >/dev/null 2>&1
podman run -d --name $NOME --systemd=always -v "$ROOT:/opt/ams-src:ro,Z" -v "$OUT:/opt/schermate:Z" ams-prova >/dev/null || exit 1
trap 'podman rm -f $NOME >/dev/null 2>&1' EXIT
for i in $(seq 1 30); do
	s=$(podman exec $NOME systemctl is-system-running 2>/dev/null)
	[ "$s" = running ] || [ "$s" = degraded ] && break
	sleep 1
done
podman exec $NOME /opt/ams-src/install.sh >/dev/null 2>&1
podman exec -i -e LANG=it_IT.UTF-8 -e TERM=xterm-256color $NOME python3 - <<'PY'
import fcntl, os, pty, select, struct, subprocess, termios, time

def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True)

A = "/usr/local/bin/ams"
V = "/var/lib/ams"
sh(f'{A} send --to @sviluppo,luca --expires 1d --title "Aggiornamento del server" "Stanotte alle 23 il server di posta viene aggiornato."')
sh(f'{A} send --to all --title Manutenzione "Sabato dalle 8 alle 12 il server sarà spento per la manutenzione dei dischi.\nSalvate il lavoro entro venerdì sera."')
sh(f'{A} send --to mario "Il tuo account scade venerdì: passa dall\'ufficio IT."')
sh(f'{A} send --to mario,anna --expires 15m --title Riavvio "Riavvio alle 13:00."')
sh(f'{A} revoke 4')
now = int(time.time())
def conferma(u, mid, canale):
    sh(f"runuser -u {u} -- sh -c 'printf \"%s %s\\n\" {now} \"{canale}\" > {V}/users/{u}/acks/{mid}; mv {V}/users/{u}/inbox/{mid} {V}/users/{u}/read/{mid}'")
def rimanda(u, mid):
    sh(f"runuser -u {u} -- touch {V}/users/{u}/state/{mid}.term")
for u in ("anna", "mario", "luca"):
    conferma(u, 1, "desktop" if u == "anna" else "terminale pts/1")
for u, c in (("anna", "desktop"), ("zeno", "terminale pts/2"), ("admin", "terminale pts/0"), ("fabio", "desktop")):
    conferma(u, 2, c)
rimanda("mario", 2)
rimanda("kora", 2)
# una copia che non è arrivata: la casella di dario non si può scrivere
sh(f"rm -rf {V}/users/dario; install -d -m 700 -o root {V}/users/dario")
sh(f"rm -f {V}/sent/2/delivery.tmp; grep -v '^dario ' {V}/sent/2/delivery > {V}/sent/2/d; mv {V}/sent/2/d {V}/sent/2/delivery")

pid, fd = pty.fork()
if pid == 0:
    os.execvp(A, ["ams"])
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 30, 116, 0, 0))

def fotogramma(t=1.2):
    out, t0 = b"", time.time()
    while time.time() - t0 < t:
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            out += os.read(fd, 65536)
    return out.split(b"\x1b[H")[-1]

def salva(nome, t=1.2):
    fr = fotogramma(t)
    fr = fr.split(b"\x1b[J")[0]
    open(f"/opt/schermate/{nome}.ans", "wb").write(fr)

def tasti(b, pausa=0.4):
    os.write(fd, b)
    time.sleep(pausa)

fotogramma(1.5)
tasti(b"\x1b[B")
tasti(b"\x1b[B")
salva("list")
tasti(b"\r")
salva("detail")
tasti(b"\t")
salva("history")
tasti(b"\x1b")
tasti(b"s", 0.8)
salva("reminder")
tasti(b"n")
tasti(b"n", 0.8)
for c in [b"@sviluppo", b"\t", "Manutenzione".encode(), b"\t", b"2d", b"\t",
          "Sabato dalle 8 alle 12 il server sarà spento.\rSalvate il lavoro entro venerdì sera.".encode()]:
    tasti(c, 0.6)
salva("new")
tasti(b"\x13", 0.8)
salva("send")
tasti(b"n")
tasti(b"\x1b")
tasti(b"s")
tasti(b"q")
PY
ls "$OUT"
