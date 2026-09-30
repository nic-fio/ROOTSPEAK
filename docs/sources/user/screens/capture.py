"""Schermate vere per il manuale utente, prese in modalità di prova (senza root).

Completano quelle di docs/sources/screens/ (prese nella macchina di prova da
tools/tui-screenshots.sh) con le finestre sovrapposte della TUI (tasti, ritiro,
pulizia, ricerca) e con la guida integrata. Prepara un archivio di prova con
tre messaggi per due utenti della macchina, apre ams su un terminale virtuale,
preme i tasti e salva ogni schermata con i suoi colori.

    make
    python3 docs/sources/user/screens/capture.py              TUI (116x30)
    MODO=guida python3 docs/sources/user/screens/capture.py   guida (78x22)

Gli utenti devono esistere nella macchina: si cambiano in UTENTI.
"""
import fcntl, os, pathlib, pty, select, shutil, struct, subprocess, tempfile, termios, time

OUT = pathlib.Path(__file__).resolve().parent
ROOT = OUT.parents[3]
UTENTI = ("nicfio", "user")
VAR = tempfile.mkdtemp(prefix="ams-schermate-")
env = dict(os.environ, AMS_TEST="1", AMS_CONF="/dev/null", AMS_TEST_TTY="", AMS_LIB=f"{ROOT}/build",
           AMS_LOCALEDIR=f"{ROOT}/build/locale", LANG="it_IT.UTF-8", AMS_VAR=f"{VAR}/var", TERM="xterm-256color")
for k in ("LC_ALL", "LC_MESSAGES", "LANGUAGE", "NO_COLOR"):
    env.pop(k, None)
A = f"{ROOT}/build/ams"


def sh(*a):
    return subprocess.run([A, *a], env=env, capture_output=True, text=True)


u1, u2 = UTENTI
sh("send", "--to", f"{u1},{u2}", "--expires", "1d", "--title", "Aggiornamento del server",
   "Stanotte alle 23 il server di posta viene aggiornato.")
sh("send", "--to", "all", "--title", "Manutenzione",
   "Sabato dalle 8 alle 12 il server sarà spento per la manutenzione dei dischi.\nSalvate il lavoro entro venerdì sera.")
sh("send", "--to", u2, "Il tuo account scade venerdì: passa dall'ufficio IT.")
now = int(time.time())
for u, mid, ch in ((u1, 1, "desktop"), (u2, 1, "terminale pts/1"), (u1, 2, "desktop")):
    d = f"{VAR}/var/users/{u}"
    open(f"{d}/acks/{mid}", "w").write(f"{now} {ch}\n")
    os.rename(f"{d}/inbox/{mid}", f"{d}/read/{mid}")

MODO = os.environ.get("MODO", "tui")
pid, fd = pty.fork()
if pid == 0:
    os.execve(A, ["ams"] if MODO == "tui" else ["ams", "--help"], env)
righe, colonne = (30, 116) if MODO == "tui" else (22, 78)
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", righe, colonne, 0, 0))


def fotogramma(t=1.2):
    out, t0 = b"", time.time()
    while time.time() - t0 < t:
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            try:
                out += os.read(fd, 65536)
            except OSError:
                break
    return out.split(b"\x1b[H")[-1]


def salva(nome, t=1.2):
    (OUT / f"{nome}.ans").write_bytes(fotogramma(t).split(b"\x1b[J")[0])


def tasti(b, pausa=0.4):
    os.write(fd, b)
    time.sleep(pausa)


fotogramma(1.5)
if MODO == "tui":
    tasti(b"?")
    salva("help")
    tasti(b"x")
    tasti(b"\x1b[B")
    tasti(b"r")
    salva("revoke")
    tasti(b"n")
    tasti(b"p")
    salva("purge")
    tasti(b"\x1b")
    fotogramma(0.5)
    tasti(b"/")
    tasti(b"server")
    salva("search")
    tasti(b"\r")
    salva("search-results")
    tasti(b"q")
else:
    tasti(b"2")
    tasti(b"1")
    salva("guide-info")
    tasti(b"3")
    salva("guide-options")
    tasti(b"q")
fotogramma(0.5)
shutil.rmtree(VAR, ignore_errors=True)
