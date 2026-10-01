#!/usr/bin/env python3
"""RootSpeak - Advanced Messaging System for Linux
Prova la TUI degli amministratori (rspeak senza argomenti) su un terminale
virtuale, in modalità di prova su un archivio temporaneo: la apre, preme dei
tasti come farebbe una persona e controlla lo schermo e l'archivio dopo ognuno.
    tests/tui.py [-v]        (-v stampa gli schermi)
Usa i programmi in build/ (RSPEAK_BUILD per un'altra cartella)."""
import fcntl, os, pty, re, select, shutil, struct, subprocess, sys, tempfile, termios, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.environ.get("RSPEAK_BUILD", os.path.join(ROOT, "build"))
VERBOSE = "-v" in sys.argv
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
U = subprocess.run(["id", "-un"], capture_output=True, text=True).stdout.strip()
TMP = tempfile.mkdtemp()
ENV = dict(os.environ, RSPEAK_TEST="1", RSPEAK_VAR=f"{TMP}/var", RSPEAK_LIB=B, RSPEAK_LOCALEDIR=f"{B}/locale",
           RSPEAK_CONF="/dev/null", RSPEAK_TEST_TTY="", LANG="it_IT.UTF-8", TERM="xterm-256color",
           EDITOR="sed -i s/seconda/SECONDA/")
ENV.pop("LANGUAGE", None), ENV.pop("LC_ALL", None), ENV.pop("LC_MESSAGES", None)
falliti = []


def rspeak(*args, stdin=None):
    return subprocess.run([f"{B}/rspeak", *args], env=ENV, input=stdin, capture_output=True, text=True)


def avvia(righe, colonne):
    pid, fd = pty.fork()
    if pid == 0:
        os.execvpe(f"{B}/rspeak", ["rspeak"], ENV)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", righe, colonne, 0, 0))
    return pid, fd


def leggi_byte(fd, t=1.0):
    out, t0 = b"", time.time()
    while time.time() - t0 < t:
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            try:
                out += os.read(fd, 65536)
            except OSError:
                break
    return out


def leggi(fd, t=1.0):
    """Ciò che arriva in t secondi."""
    return leggi_byte(fd, t).decode("utf-8", "replace")


def leggi_schermo(fd, t=1.0, limite=6.0):
    """Legge finché l'ultimo disegno è completo (ha l'angolo in basso a destra)."""
    raw, t0 = leggi_byte(fd, t), time.time()
    while not (b"\x1b[H" in raw and "┘".encode() in raw.split(b"\x1b[H")[-1]) and time.time() - t0 < limite:
        raw += leggi_byte(fd, 0.3)
    return raw.decode("utf-8", "replace")


def schermo(raw):
    fr = raw.split("\x1b[H")[-1]
    return [ANSI.sub("", l).rstrip("\r") for l in fr.split("\n")]


def controlla(nome, ok, righe):
    if VERBOSE or not ok:
        print(f"--- {nome}")
        print("\n".join(l for l in righe if l.strip("│ ")))
    if not ok:
        falliti.append(nome)


def testo(righe):
    return "\n".join(righe)


try:
    rspeak("send", "--to", U, "--title", "Manutenzione", "Sabato dalle 8 alle 12 il server sarà spento.")
    rspeak("send", "--to", U, "Seconda prova")
    subprocess.run(["script", "-qec", f"{B}/rootspeak-user prompt", "/dev/null"], env=ENV, input="s\n",
                   capture_output=True, text=True)

    pid, fd = avvia(28, 120)
    raw = leggi_schermo(fd, 1.5)
    s = schermo(raw)
    controlla("apertura: lista con barra e frase, dimensioni giuste",
              "\x1b[?1049h" in raw and s[0].startswith("┌─ RootSpeak · messaggi inviati") and len(s) == 28
              and all(len(l) == 120 for l in s) and "tutti confermato (1)" in testo(s) and "1 consegnato" in testo(s)
              and "█ confermato" in testo(s), s)
    controlla("nessuno stato inventato", not re.search(r"in attesa|completo|incompleto|annullato", testo(s)), s)

    os.write(fd, b"\r")
    s = schermo(leggi_schermo(fd))
    controlla("Invio: dettaglio con i destinatari e lo stato di rspeak status",
              "Messaggio 2" in s[0] and "Seconda prova" in testo(s) and f"{U}" in testo(s) and "consegnato" in testo(s), s)
    os.write(fd, b"\t")
    s = schermo(leggi_schermo(fd))
    controlla("Tab: storia dal registro (o nessun evento)",
              "consegnato a" in testo(s) or "Nessun evento nel registro" in testo(s), s)
    os.write(fd, b"\x1b")
    leggi(fd, 0.6)

    os.write(fd, b"n")
    leggi(fd, 0.5)
    os.write(fd, U.encode() + b"\t")
    leggi(fd, 0.8)
    os.write(fd, "Prova TUI è ok".encode() + b"\t2h\t")
    leggi(fd, 0.5)
    os.write(fd, "prima riga\rseconda riga".encode())
    s = schermo(leggi_schermo(fd))
    controlla("modulo: campi, anteprima dei destinatari, testo su due righe",
              "1 destinatario" in testo(s) and "Prova TUI è ok" in testo(s) and "prima riga" in testo(s)
              and "seconda riga" in testo(s), s)
    os.write(fd, b"\x05")
    s = schermo(leggi_schermo(fd, 1.5))
    controlla("Ctrl+E: il testo passa dall'editor e torna", "SECONDA riga" in testo(s), s)
    os.write(fd, b"\x13")
    s = schermo(leggi_schermo(fd))
    controlla("Ctrl+S: conferma con destinatari, titolo e scadenza",
              "Inviare il messaggio?" in testo(s) and "A: " + U in testo(s) and "Scadenza: 2h" in testo(s), s)
    os.write(fd, b"s")
    s = schermo(leggi_schermo(fd, 1.5))
    controlla("invio: esito del comando, una sola finestra",
              "Messaggio 3 inviato a 1 utente." in testo(s) and testo(s).count("┌─ ") == 2, s)
    st = rspeak("status", "3").stdout
    controlla("il messaggio inviato dalla TUI è nell'archivio", "Prova TUI è ok" in st and "SECONDA riga" in st, [st])
    os.write(fd, b" ")
    s = schermo(leggi_schermo(fd))
    controlla("dopo l'invio la lista mostra il nuovo messaggio in cima", ">  3" in testo(s), s)

    os.write(fd, b"s")
    leggi(fd, 0.6)
    os.write(fd, b"s")
    s = schermo(leggi_schermo(fd, 1.5))
    controlla("s: sollecito eseguito", "sollecitato 1 destinatario" in testo(s), s)
    os.write(fd, b" ")
    leggi(fd, 0.6)
    os.write(fd, b"r")
    s = schermo(leggi_schermo(fd))
    controlla("r: conferma prima del ritiro", "Ritirare il messaggio 3?" in testo(s), s)
    os.write(fd, b"n")
    leggi(fd, 0.6)
    controlla("n: ritiro annullato, messaggio intatto", "RITIRATO" not in rspeak("status", "3").stdout, [])
    os.write(fd, b"r")
    leggi(fd, 0.6)
    os.write(fd, b"s")
    leggi(fd, 1.5)
    os.write(fd, b" ")
    s = schermo(leggi_schermo(fd))
    controlla("ritiro: [ritirato] nella lista e nell'archivio",
              "[ritirato]" in testo(s) and "RITIRATO" in rspeak("status", "3").stdout, s)

    os.write(fd, b"/Manut\r")
    s = schermo(leggi_schermo(fd))
    controlla("/: ricerca", "Manutenzione" in testo(s) and "Seconda prova" not in testo(s), s)
    os.write(fd, b"\x1b")
    leggi(fd, 0.6)

    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))
    s = schermo(leggi_schermo(fd, 1.5))
    controlla("80x24: barra e confermati su totale", len(s) == 24 and all(len(l) == 80 for l in s)
              and "1/1" in testo(s), s)

    os.write(fd, b"q")
    raw = leggi(fd, 1.0)
    _, stato = os.waitpid(pid, 0)
    controlla("q: uscita pulita", "\x1b[?1049l" in raw and os.WEXITSTATUS(stato) == 0, [repr(raw[-60:])])

    # terminale troppo piccolo: niente TUI, la guida
    pid, fd = avvia(15, 60)
    raw = leggi(fd, 1.5)
    os.write(fd, b"q")
    leggi(fd, 0.5)
    os.waitpid(pid, 0)
    controlla("60x15: niente TUI, la guida", "RootSpeak · messaggi inviati" not in raw and ("rspeak — guida" in raw or "RSPEAK(1)" in raw),
              schermo(raw)[:5])
    # in una pipe: la guida in testo semplice
    out = subprocess.run([f"{B}/rspeak"], env=ENV, capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout
    controlla("in una pipe: la guida", "SINTASSI" in out, out.splitlines()[:3])
finally:
    shutil.rmtree(TMP, ignore_errors=True)

print("OK" if not falliti else "FALLITI: " + ", ".join(falliti))
sys.exit(1 if falliti else 0)
