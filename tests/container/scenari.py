#!/usr/bin/env python3
"""AMS - Advanced Messaging System for linux
Scenari di prova dal vero: gira come root dentro la macchina di prova
(tests/container), con AMS installato, utenti veri e sessioni ssh vere.

Ogni scenario invia messaggi da root o da un amministratore agli utenti,
simula ciò che fanno gli utenti (collegarsi, rispondere, rimandare, guastare la
propria casella), misura i tempi e registra l'esito in RISULTATI (JSON) e in
un rapporto leggibile (Markdown).

    python3 scenari.py CARTELLA_RISULTATI
"""
import json
import os
import pty
import pwd
import shlex
import re
import select
import signal
import subprocess
import sys
import time

OUT = sys.argv[1] if len(sys.argv) > 1 else "/opt/risultati"
VAR = "/var/lib/ams"
AMS = "/usr/local/bin/ams"
DESK = os.environ.get("AMS_PROVA_DESKTOP")   # utente con sessione grafica (solo nella VM)
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b\][^\x07]*\x07|\r")
risultati = []
# utenti con una shell diversa da bash, e il loro prompt
SHELL_PROVA = {"zeno": ("zsh", r"% $"), "fabio": ("fish", r"> $"), "kora": ("ksh", r"\$ $"), "dario": ("dash", r"\$ $")}


# ---- strumenti ----

def sh(cmd, check=False, **kw):
    r = subprocess.run(cmd, shell=True, executable="/bin/bash", capture_output=True, text=True, **kw)
    if check and r.returncode:
        raise RuntimeError(f"{cmd}: {r.stderr}")
    return r


def ams(args, come="root"):
    """Lancia ams da root, o da un altro utente (che passa da sudo)."""
    pre = "" if come == "root" else f"runuser -u {come} -- "
    return sh(f"{pre}{AMS} {args}")


def negato(err):
    """Permesso negato, nella lingua del sistema di prova o in inglese."""
    return "Permission denied" in err or "Permesso negato" in err


def azzera():
    """Chiude le sessioni degli utenti, le finestre di AMS rimaste sul desktop e svuota l'archivio.
    Le finestre vanno chiuse prima: l'archivio ricomincia dal messaggio 1, e una finestra vecchia
    ritroverebbe un messaggio nuovo con il suo stesso numero."""
    for u in ("mario", "anna", "luca", "admin", *SHELL_PROVA):
        sh(f"loginctl terminate-user {u}")
    if DESK:
        # l'agente si ferma con le sue finestre, e riparte dopo, ad archivio vuoto
        sh(f"pkill -u {DESK} -f '^/bin/bash /usr/local/lib/ams/ams-user agent$'; pkill -u {DESK} -x zenity")
        time.sleep(1)
    time.sleep(0.5)
    sh(f"rm -rf {VAR}/sent/* {VAR}/sent/.seq* {VAR}/users/*")
    if DESK and sh(f"loginctl show-user {DESK} -p Display --value").stdout.strip():
        sh(f"systemd-run --user --machine={DESK}@.host --collect --quiet /usr/local/lib/ams/ams-user agent")
        time.sleep(1)


def stato(mid, utente):
    out = ams(f"status {mid}").stdout
    for line in out.splitlines():
        parts = line.split(None, 1)
        if parts and parts[0] == utente:
            return parts[1].strip() if len(parts) > 1 else ""
    return None


class Sessione:
    """Una connessione ssh con terminale di un utente, come la aprirebbe una persona."""

    def __init__(self, utente, prompt=r"\$ $", comando=None):
        self.utente = utente
        self.buf = ""
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            os.execvp("ssh", ["ssh", "-tt", f"{utente}@localhost"] + ([comando] if comando else []))
        self.leggi_fino(prompt, 15)

    def leggi(self, tempo=0.3):
        fine = time.time() + tempo
        while time.time() < fine:
            r, _, _ = select.select([self.fd], [], [], 0.05)
            if r:
                try:
                    dati = os.read(self.fd, 65536)
                except OSError:
                    break
                if not dati:
                    break
                self.buf += dati.decode("utf-8", "replace")
        return self.buf

    def leggi_fino(self, schema, tempo=10):
        """Attende che l'uscita (senza colori) contenga lo schema; restituisce i secondi attesi."""
        t0 = time.time()
        while time.time() - t0 < tempo:
            self.leggi(0.05)
            if re.search(schema, ANSI.sub("", self.buf), re.M):
                return time.time() - t0
        return None

    def scrivi(self, testo):
        os.write(self.fd, testo.encode())

    def pulisci(self):
        self.buf = ""

    def testo(self):
        return ANSI.sub("", self.buf)

    def chiudi(self):
        try:
            os.write(self.fd, b"exit\n")
            time.sleep(0.2)
            os.kill(self.pid, signal.SIGKILL)
        except OSError:
            pass
        try:
            os.waitpid(self.pid, 0)
        except ChildProcessError:
            pass


def registra(codice, area, descrizione, atteso, ok, dettagli="", **misure):
    """ok: True riuscito, False fallito, None non provato (non conta fra i riusciti)."""
    esito = "NON PROVATO" if ok is None else "OK" if ok else "NO"
    risultati.append(dict(codice=codice, area=area, descrizione=descrizione, atteso=atteso,
                          esito=esito, dettagli=dettagli, misure=misure))
    print(f"  {dict(OK='ok', NO='NO').get(esito, '--')}  {codice}  {descrizione}" + (f"  [{misure}]" if misure else ""))


def scenario(fn):
    """Esegue uno scenario su un archivio vuoto; un'eccezione è un esito NO."""
    azzera()
    try:
        fn()
    except Exception as e:  # noqa: BLE001
        registra(fn.__name__, "errore", f"eccezione in {fn.__name__}", "nessuna eccezione", False, repr(e))


# ---- A. accesso e permessi ----

def a_accesso():
    r = ams('send --to mario "da root"')
    registra("A1", "Accesso", "root invia un messaggio", "invio riuscito",
             r.returncode == 0 and "inviato a 1 utente" in r.stdout, r.stdout.strip() + r.stderr.strip())
    t0 = time.time()
    r = ams('send --to anna "da admin"', "admin")
    dt = time.time() - t0
    frm = sh(f"grep '^from:' {VAR}/sent/2/msg").stdout.strip()
    registra("A2", "Accesso", "un amministratore (gruppo sudo) invia: ams si rilancia con sudo",
             "invio riuscito, mittente admin", r.returncode == 0 and frm == "from: admin", frm, secondi=round(dt, 3))
    r = ams('send --to anna "da mario"', "mario")
    registra("A3", "Accesso", "un utente normale non può eseguire ams", "permesso negato, nessun messaggio",
             r.returncode != 0 and negato(r.stderr) and not os.path.exists(f"{VAR}/sent/3"),
             r.stderr.strip())
    r = ams("--help", "mario")
    registra("A4", "Accesso", "un utente normale non può aprire nemmeno la guida", "permesso negato",
             r.returncode != 0 and negato(r.stderr), r.stderr.strip())


# ---- B. destinatari ----

def b_destinatari():
    def dest(mid):
        return sh(f"cat {VAR}/sent/{mid}/recipients").stdout.split()

    ams('send --to mario "uno"')
    registra("B1", "Destinatari", "un utente", "mario", dest(1) == ["mario"], str(dest(1)))
    ams('send --to mario,anna,mario "lista"')
    registra("B2", "Destinatari", "lista con un doppione", "anna, mario (una volta)", dest(2) == ["anna", "mario"], str(dest(2)))
    ams('send --to @sviluppo "gruppo"')
    registra("B3", "Destinatari", "gruppo @sviluppo", "anna, mario", dest(3) == ["anna", "mario"], str(dest(3)))
    ams('send --to all "tutti"')
    shell = [u for u in SHELL_PROVA if sh(f"getent passwd {u}").returncode == 0]   # solo nel container
    tutti = sorted(["admin", "anna", "luca", "mario", *shell] + ([DESK] if DESK else []))
    registra("B4", "Destinatari", "all: utenti umani, esclusi root e chi ha nologin",
             ", ".join(tutti), dest(4) == tutti, str(dest(4)))
    s = Sessione("luca")
    ams('send --to online "collegati"')
    online = sorted(["luca"] + ([DESK] if DESK else []))
    registra("B5", "Destinatari", "online: solo chi ha una sessione aperta", ", ".join(online), dest(5) == online, str(dest(5)))
    s.chiudi()
    r = ams('send --to pippo "x"')
    registra("B6", "Destinatari", "utente inesistente", "errore, nessun messaggio creato",
             r.returncode != 0 and "utente inesistente" in r.stderr and not os.path.exists(f"{VAR}/sent/6"), r.stderr.strip())
    sh("groupadd -f vuoto")
    r = ams('send --to @vuoto "x"')
    registra("B7", "Destinatari", "gruppo senza membri", "errore «nessun destinatario»",
             r.returncode != 0 and "nessun destinatario" in r.stderr, r.stderr.strip())


# ---- C. consegna secondo lo stato delle sessioni ----

def c_consegna():
    # C1: scollegato, poi accede
    ams('send --to mario --title Manutenzione "Server spento sabato"')
    st = stato(1, "mario")
    registra("C1a", "Consegna", "utente scollegato: la copia aspetta nella casella", "consegnato",
             st == "consegnato" and os.path.exists(f"{VAR}/users/mario/inbox/1"), st)
    s = Sessione.__new__(Sessione)
    s.utente, s.buf = "mario", ""
    t0 = time.time()
    s.pid, s.fd = pty.fork()
    if s.pid == 0:
        os.execvp("ssh", ["ssh", "-tt", "mario@localhost"])
    dt = s.leggi_fino(r"Confermi di aver letto il messaggio\?", 15)
    registra("C1b", "Consegna", "al login il messaggio e la domanda compaiono prima del primo prompt",
             "testo e domanda al login", dt is not None and "Server spento sabato" in s.testo(),
             secondi_dal_login=round(time.time() - t0, 3) if dt else None)
    s.scrivi("s\n")
    s.leggi_fino(r"\$ $", 5)
    registra("C1c", "Consegna", "conferma al login", "confermato (terminale)",
             (stato(1, "mario") or "").startswith("confermato"), stato(1, "mario"))
    s.chiudi()

    # C2: collegato con terminale: tempo perché il testo compaia
    s = Sessione("anna")
    s.pulisci()
    t0 = time.time()
    ams('send --to anna "Riunione alle 11"')
    dt_invio = time.time() - t0
    dt = s.leggi_fino(r"Riunione alle 11", 5)
    registra("C2a", "Consegna", "utente collegato: il testo compare nel suo terminale", "testo nel terminale",
             dt is not None, secondi_invio=round(dt_invio, 3),
             secondi_al_terminale=round(dt_invio + (dt or 0), 3) if dt is not None else None)
    st = stato(2, "anna")
    registra("C2b", "Consegna", "stato dopo la scrittura nel terminale", "consegnato, scritto su 1 terminale",
             st == "consegnato, scritto su 1 terminale", st)
    s.pulisci()
    s.scrivi("\n")
    dt = s.leggi_fino(r"Confermi di aver letto il messaggio\?", 5)
    registra("C2c", "Consegna", "premendo Invio compare la domanda", "domanda al prompt successivo", dt is not None,
             secondi=round(dt, 3) if dt else None)
    s.scrivi("s\n")
    s.leggi_fino(r"Confermato\.", 5)
    s.chiudi()

    # C3: ssh senza terminale
    p = subprocess.Popen(["ssh", "luca@localhost", "sleep 4"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    r = ams('send --to luca "Solo casella"')
    p.wait()
    st = stato(3, "luca")
    registra("C3", "Consegna", "sessione ssh senza terminale: non viene toccata, la copia va nella casella",
             "invio riuscito, consegnato, nessun terminale scritto", r.returncode == 0 and st == "consegnato", st)

    # C4: due sessioni dello stesso utente
    s1, s2 = Sessione("mario"), Sessione("mario")
    for s in (s1, s2):
        s.pulisci()
    ams('send --to mario "Due sessioni"')
    ok1 = s1.leggi_fino("Due sessioni", 5) is not None
    ok2 = s2.leggi_fino("Due sessioni", 5) is not None
    st = stato(4, "mario")
    registra("C4a", "Consegna", "due sessioni aperte: il testo compare in entrambe", "testo in 2 terminali",
             ok1 and ok2 and st == "consegnato, scritto su 2 terminali", st)
    s1.pulisci(); s2.pulisci()
    s1.scrivi("\n"); s2.scrivi("\n")
    s1.leggi_fino(r"Confermi", 5); s2.leggi_fino(r"Confermi", 5)
    t0 = time.time()
    s1.scrivi("s\n")
    dt = s2.leggi_fino(r"già confermato altrove", 5)
    registra("C4b", "Consegna", "confermando in una sessione, la domanda nell'altra si ferma",
             "«già confermato altrove» nell'altra", dt is not None, secondi=round(time.time() - t0, 3))
    s1.chiudi(); s2.chiudi()


# ---- D. conferma, rinvio, solleciti ----

def d_conferma():
    s = Sessione("luca")
    ams('send --to luca "Rinvio"')
    s.pulisci(); s.scrivi("\n")
    s.leggi_fino(r"Confermi", 5)
    s.scrivi("n\n")
    s.leggi_fino(r"riproposta tra", 5)
    st = stato(1, "luca")
    registra("D1", "Conferma", "l'utente rimanda", "consegnato, rimandato il …", (st or "").startswith("consegnato") and "rimandato" in st, st)
    s.pulisci(); s.scrivi("true\n")
    s.leggi_fino(r"\$ $", 5)
    registra("D2", "Conferma", "dopo il rinvio, al prompt solo un promemoria", "«Hai 1 messaggio…», nessuna domanda",
             "Hai 1 messaggio" in s.testo() and "Confermi" not in s.testo(), s.testo()[-160:])
    s.chiudi()
    s = Sessione.__new__(Sessione)
    s.utente, s.buf = "luca", ""
    s.pid, s.fd = pty.fork()
    if s.pid == 0:
        os.execvp("ssh", ["ssh", "-tt", "luca@localhost"])
    ok = s.leggi_fino(r"Confermi", 10) is not None
    registra("D3", "Conferma", "al login successivo il rinvio non vale: la domanda torna", "domanda al login", ok)
    s.scrivi("s\n"); s.leggi_fino(r"\$ $", 5)
    ack = sh(f"cat {VAR}/users/luca/acks/1").stdout.strip()
    registra("D4", "Conferma", "conferma registrata con data e canale", "«EPOCH terminale pts/N»",
             bool(re.fullmatch(r"\d+ terminale pts/\d+", ack)), ack)
    s.chiudi()


# ---- E. scadenza e ritiro ----

def e_scadenza_ritiro():
    ams('send --to mario --expires 1m "Scade"')
    sh(f"sed -i 's/^expires: .*/expires: {int(time.time()) - 5}/' {VAR}/sent/1/msg {VAR}/users/mario/inbox/1")
    s = Sessione("mario")
    registra("E1", "Scadenza", "un messaggio scaduto non viene mostrato al login", "nessun testo",
             "Scade" not in s.testo(), "")
    st = stato(1, "mario")
    registra("E2", "Scadenza", "stato di un messaggio scaduto", "consegnato, non confermato (scaduto)",
             st == "consegnato, non confermato (scaduto)", st)
    ams('send --to mario "Da ritirare"')
    s.pulisci(); s.scrivi("\n")
    s.leggi_fino(r"Confermi", 5)
    t0 = time.time()
    ams("revoke 2")
    dt = s.leggi_fino(r"ritirato il messaggio", 5)
    registra("E3", "Ritiro", "ritiro con la domanda in attesa: la domanda si interrompe",
             "«L'amministratore ha ritirato il messaggio»", dt is not None, secondi=round(time.time() - t0, 3))
    st = stato(2, "mario")
    registra("E4", "Ritiro", "stato dopo il ritiro", "consegnato, non confermato (ritirato)",
             st == "consegnato, non confermato (ritirato)", st)
    s.chiudi()
    ams('send --to anna "Ritirato prima"')
    ams("revoke 3")
    s = Sessione("anna")
    registra("E5", "Ritiro", "un messaggio ritirato prima del login non viene mostrato", "nessun testo",
             "Ritirato prima" not in s.testo())
    s.chiudi()


# ---- F. guasti e recupero ----

def f_guasti():
    sh(f"install -d -m 700 -o anna -g anna {VAR}/users/anna; "
       f"install -d -m 555 -o root {VAR}/users/anna/inbox")
    r = ams('send --to mario,anna "Guasto"')
    st = stato(1, "anna")
    registra("F1", "Guasti", "la copia per un utente non si può scrivere: gli altri la ricevono",
             "errore, anna «inviato, non consegnato», mario consegnato",
             r.returncode != 0 and (st or "").startswith("inviato, non consegnato") and stato(1, "mario") == "consegnato",
             f"{r.stderr.strip()} | anna: {st}")
    sh(f"chown anna:anna {VAR}/users/anna/inbox; chmod 755 {VAR}/users/anna/inbox")
    r = ams("list")
    registra("F2", "Guasti", "guasto risolto: il comando successivo completa la consegna", "anna consegnato",
             stato(1, "anna") == "consegnato" and not os.path.exists(f"{VAR}/sent/1/incomplete"), r.stderr.strip())

    # invio interrotto davvero: SIGKILL durante la consegna a molti utenti
    for i in range(60):
        sh(f"id u{i:02d} >/dev/null 2>&1 || useradd -m -s /bin/bash u{i:02d}")
    # si uccide proprio ams send (non una shell che lo contiene)
    p = subprocess.Popen([AMS, "send", "--to", "all", "Interrotto"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.8)
    p.kill(); p.wait()
    ids = sorted(int(x) for x in os.listdir(f"{VAR}/sent") if x.isdigit())
    mid = ids[-1]
    n_prima = len(sh(f"cat {VAR}/sent/{mid}/delivery 2>/dev/null").stdout.splitlines())
    n_tot = len(sh(f"cat {VAR}/sent/{mid}/recipients 2>/dev/null").stdout.split())
    t0 = time.time()
    r = ams("list")
    dt = time.time() - t0
    n_dopo = len(sh(f"cat {VAR}/sent/{mid}/delivery").stdout.splitlines())
    registra("F3", "Guasti", "ams send ucciso a metà (SIGKILL): il comando successivo completa",
             "tutte le copie consegnate, nessun segno di invio incompleto",
             n_tot > 0 and n_dopo == n_tot and not os.path.exists(f"{VAR}/sent/{mid}/incomplete"),
             f"consegnati prima {n_prima}/{n_tot}, dopo {n_dopo}/{n_tot}; {r.stderr.strip()[:120]}",
             consegnati_al_kill=n_prima, destinatari=n_tot, secondi_recupero=round(dt, 3))

    # invio ucciso fra la creazione della cartella dell'utente e il suo chown
    sh(f"rm -rf {VAR}/users/luca && install -d -m 700 {VAR}/users/luca")
    r = ams('send --to luca "Dopo la cartella a metà"')
    mid = max(int(x) for x in os.listdir(f"{VAR}/sent") if x.isdigit())
    st = stato(mid, "luca")
    registra("F6", "Guasti", "cartella dell'utente rimasta di root da un invio interrotto: la consegna la sistema",
             "consegnato", r.returncode == 0 and st == "consegnato", f"{st}; {r.stderr.strip()[:120]}")
    # invio in corso e, nello stesso momento, altri comandi ams che fanno il recupero
    azzera()
    p = subprocess.Popen([AMS, "send", "--to", "all", "Concorrente"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    giri = 0
    while p.poll() is None:
        ams("list"); giri += 1
    ams("list")
    righe = sh(f"cut -d' ' -f1 {VAR}/sent/1/delivery").stdout.split()
    n_tot = len(sh(f"cat {VAR}/sent/1/recipients").stdout.split())
    registra("F5", "Guasti", "ams list ripetuto mentre ams send consegna: il recupero non interferisce",
             "una consegna per destinatario, nessun doppione, invio completo",
             len(righe) == n_tot == len(set(righe)) and p.returncode == 0 and not os.path.exists(f"{VAR}/sent/1/incomplete"),
             f"{len(righe)} consegne annotate per {n_tot} destinatari, {len(set(righe))} distinte",
             ams_list_durante_invio=giri)
    for i in range(60):
        sh(f"userdel -r u{i:02d} 2>/dev/null")

    # conferma non scrivibile
    azzera()
    s = Sessione("luca")
    ams('send --to luca "Conferma impossibile"')
    sh(f"chown root {VAR}/users/luca/acks; chmod 555 {VAR}/users/luca/acks")
    s.pulisci(); s.scrivi("\n"); s.leggi_fino(r"Confermi", 5)
    s.scrivi("s\n")
    ok = s.leggi_fino(r"Non è stato possibile registrare la conferma", 5) is not None
    st = stato(1, "luca")
    registra("F4", "Guasti", "la conferma non si può scrivere: il messaggio resta e l'utente è avvisato",
             "avviso; stato consegnato; messaggio ancora nella casella",
             ok and (st or "").startswith("consegnato") and os.path.exists(f"{VAR}/users/luca/inbox/1"), st)
    s.chiudi()


# ---- G. sicurezza ----

def g_sicurezza():
    ams('send --to mario "prima"')
    sh(f"rm -rf {VAR}/users/mario/inbox; ln -s /etc {VAR}/users/mario/inbox; chown -h mario:mario {VAR}/users/mario/inbox")
    r = ams('send --to mario "attacco"')
    registra("G1", "Sicurezza", "la casella è un collegamento a /etc: root non ci scrive",
             "nessun file 2 in /etc; mario «inviato, non consegnato»",
             not os.path.exists("/etc/2") and not os.path.exists("/etc/2.tmp")
             and (stato(2, "mario") or "").startswith("inviato"), r.stderr.strip()[:160])
    sh(f"rm -f {VAR}/users/mario/inbox")
    s = Sessione("anna")
    s.pulisci()
    ams("send --to anna $'Testo \\e[31mrosso\\e[0m \\e]0;titolo\\a \\a fine'")
    s.leggi_fino("fine", 5)
    registra("G2", "Sicurezza", "sequenze di escape nel testo: non arrivano al terminale", "nessun ESC nel testo ricevuto",
             "Testo rosso" in ANSI.sub("", s.buf) and "\x1b[31m" not in s.buf and "\x1b]0;" not in s.buf and "\x07" not in s.buf.split("Testo")[-1],
             repr(s.buf[s.buf.find("Testo"):s.buf.find("Testo") + 40]))
    s.chiudi()
    ams('send --to luca "falso"')
    sh(f"printf '1 \\033[31mfinto\\033]0;x\\007%0500d' 0 > {VAR}/users/luca/acks/4; chown luca {VAR}/users/luca/acks/4")
    out = ams("status 4").stdout
    registra("G3", "Sicurezza", "conferma fabbricata con escape e 500 byte: ams status resta pulito",
             "nessun ESC nell'uscita, al massimo 200 byte letti", "\x1b" not in out and len(out) < 1000, out.splitlines()[-1][:120])
    r = sh("runuser -u mario -- env AMS_TEST=1 /usr/local/bin/ams list")
    registra("G4", "Sicurezza", "un utente normale con AMS_TEST=1 non ottiene nulla", "permesso negato",
             r.returncode != 0 and negato(r.stderr), r.stderr.strip())


# ---- K. shell diverse da bash ----

def k_shell():
    """zsh e fish: domanda al login e a ogni prompt; ksh e dash (che leggono /etc/profile):
    domanda al login; per tutte, il testo nel terminale all'invio."""
    mid = 0
    for utente, (shell, prompt) in SHELL_PROVA.items():
        if sh(f"getent passwd {utente}").returncode:
            registra(f"K-{shell}", "Shell", f"{shell}: utente di prova {utente}", "presente", None, "utente assente")
            continue
        mid += 1
        ams(f'send --to {utente} "Al login con {shell}"')
        s = Sessione.__new__(Sessione)
        s.utente, s.buf = utente, ""
        s.pid, s.fd = pty.fork()
        if s.pid == 0:
            os.execvp("ssh", ["ssh", "-tt", f"{utente}@localhost"])
        dt = s.leggi_fino(r"Confermi di aver letto il messaggio\?", 15)
        registra(f"K1-{shell}", "Shell", f"{shell}: al login il messaggio e la domanda", "testo e domanda al login",
                 dt is not None and f"Al login con {shell}" in s.testo(), s.testo()[-80:] if dt is None else "")
        s.scrivi("s\n")
        s.leggi_fino(prompt, 8)
        st = stato(mid, utente) or ""
        registra(f"K2-{shell}", "Shell", f"{shell}: conferma al login", "confermato (terminale)",
                 st.startswith("confermato"), st)
        mid += 1
        s.pulisci()
        ams(f'send --to {utente} "Durante la sessione {shell}"')
        dt = s.leggi_fino(f"Durante la sessione {shell}", 5)
        registra(f"K3-{shell}", "Shell", f"{shell}: utente collegato, il testo compare nel terminale",
                 "testo nel terminale", dt is not None, s.testo()[-80:] if dt is None else "")
        s.pulisci()
        s.scrivi("\n")
        if shell in ("zsh", "fish"):
            dt = s.leggi_fino(r"Confermi di aver letto il messaggio\?", 5)
            registra(f"K4-{shell}", "Shell", f"{shell}: premendo Invio compare la domanda",
                     "domanda al prompt successivo", dt is not None, s.testo()[-80:] if dt is None else "",
                     secondi=round(dt, 3) if dt else None)
            s.scrivi("s\n")
            s.leggi_fino(r"Confermato\.", 5)
            st = stato(mid, utente) or ""
            registra(f"K5-{shell}", "Shell", f"{shell}: conferma al prompt", "confermato (terminale)",
                     st.startswith("confermato"), st)
        else:
            s.leggi_fino(prompt, 3)
            st = stato(mid, utente) or ""
            registra(f"K4-{shell}", "Shell", f"{shell}: al prompt nessuna domanda (arriva al login successivo)",
                     "nessuna domanda, consegnato", "Confermi" not in s.testo() and st.startswith("consegnato"), st)
        s.chiudi()


# ---- L. lingua: ognuno legge AMS nella sua ----

def l_lingua():
    """Il sistema è in italiano; luca lavora in inglese (la sua shell ha LANG=en_US.UTF-8)."""
    luca = Sessione("luca", comando="LANG=en_US.UTF-8 exec bash -il")
    mario = Sessione("mario")
    luca.pulisci(); mario.pulisci()
    ams('send --to luca,mario "Testo uguale per tutti"')
    ok_en = luca.leggi_fino(r"Message from the administrator", 5) is not None
    ok_it = mario.leggi_fino(r"Messaggio dall'amministratore", 5) is not None
    registra("L1", "Lingua", "all'invio ciascun terminale riceve l'intestazione nella lingua del suo utente",
             "luca in inglese, mario in italiano, testo non tradotto",
             ok_en and ok_it and "Testo uguale per tutti" in luca.testo(), luca.testo()[-100:] if not ok_en else "")
    luca.pulisci()
    luca.scrivi("\n")
    ok = luca.leggi_fino(r"Do you confirm you have read the message\? \[y/N\]", 5) is not None
    luca.scrivi("y\n")
    ok = ok and luca.leggi_fino(r"Confirmed\.", 5) is not None
    registra("L2", "Lingua", "la domanda e la conferma nella lingua dell'utente", "domanda in inglese, «y» conferma",
             ok and (stato(1, "luca") or "").startswith("confermato"), stato(1, "luca") or "")
    luca.chiudi(); mario.chiudi()
    out = sh(f"LANG=en_US.UTF-8 {AMS} status 1").stdout
    registra("L3", "Lingua", "un amministratore in inglese legge ams status in inglese", "USER STATE, confirmed on … (terminal …)",
             "USER" in out and "confirmed on" in out and "(terminal pts/" in out, " / ".join(out.splitlines()[-2:]))
    time.sleep(1)
    log_en = sh(f"LANG=en_US.UTF-8 {AMS} log 1").stdout
    log_it = ams("log 1").stdout
    grezzo = sh("journalctl -q -o cat SYSLOG_IDENTIFIER=ams AMS_MESSAGGIO=1 AMS_EVENTO=CONFERMATO").stdout
    registra("L4", "Lingua", "il registro è nella lingua del sistema; ams log lo riscrive in quella di chi legge",
             "journal in italiano; ams log in inglese e in italiano",
             "user luca: confirmed reading message 1 (terminal" in log_en
             and "utente luca: confermata la lettura del messaggio 1 (terminale" in log_it
             and "confermata la lettura" in grezzo, (log_en.splitlines() or [""])[-1][:120])


# ---- J. registro degli eventi ----

def j_registro():
    s = Sessione("mario")
    ams('send --to mario,anna "Storia"')
    s.pulisci(); s.scrivi("\n"); s.leggi_fino(r"Confermi", 5)
    s.scrivi("n\n"); s.leggi_fino(r"riproposta", 5)
    s.chiudi()
    s = apri("mario")
    s.leggi_fino(r"Confermi", 10); s.scrivi("s\n"); s.leggi_fino(r"Confermato", 5)
    s.chiudi()
    ams("revoke 1")
    time.sleep(1)
    out = ams("log 1").stdout
    attesi = ["inviato da root", "consegnato a anna", "consegnato a mario", "rimandato il messaggio 1 (terminale)",
              "confermata la lettura del messaggio 1 (terminale", "ritirato da root"]
    mancanti = [a for a in attesi if a not in out]
    registra("J1", "Registro", "ams log: la storia del messaggio", "invio, consegne, rinvio, conferma, ritiro",
             not mancanti, "mancano: " + ", ".join(mancanti) if mancanti else f"{len(out.splitlines()) - 1} eventi")
    uid = pwd.getpwnam("mario").pw_uid
    ev = sh(f"journalctl -q -o cat --output-fields=_UID AMS_MESSAGGIO=1 AMS_EVENTO=CONFERMATO AMS_UTENTE=mario").stdout.split()
    registra("J2", "Registro", "la conferma nel journal porta l'utente vero (_UID), non falsificabile",
             f"_UID {uid}", str(uid) in ev, " ".join(ev))


# ---- H. prestazioni ----

def h_prestazioni():
    n_utenti = 50
    for i in range(n_utenti):
        sh(f"id p{i:02d} >/dev/null 2>&1 || useradd -m -s /bin/bash p{i:02d}")
    t0 = time.time()
    ams('send --to all "Misura"')
    t_send = time.time() - t0
    for k in range(9):
        ams(f'send --to all "Misura {k}"')
    n_dest = len(sh(f"cat {VAR}/sent/1/recipients").stdout.split())
    t0 = time.time()
    ams("list")
    t_list = time.time() - t0
    t0 = time.time()
    ams("status 1")
    t_status = time.time() - t0
    registra("H1", "Prestazioni", f"invio a tutti ({n_dest} destinatari)", "misura", True,
             secondi=round(t_send, 2), ms_per_destinatario=round(1000 * t_send / n_dest, 1))
    registra("H2", "Prestazioni", f"ams list con 10 messaggi × {n_dest} destinatari", "misura (punto 15 della revisione)", True,
             secondi=round(t_list, 2))
    registra("H3", "Prestazioni", f"ams status di un messaggio con {n_dest} destinatari", "misura", True,
             secondi=round(t_status, 2))
    for i in range(n_utenti):
        sh(f"userdel -r p{i:02d} 2>/dev/null")


# ---- I. desktop ----

def desk(*args):
    """Guarda o usa le finestre di AMS nella sessione grafica di DESK (tests/vm/desktop.py)."""
    uid = pwd.getpwnam(DESK).pw_uid
    env = f"DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus XDG_RUNTIME_DIR=/run/user/{uid}"
    return sh(f"runuser -u {DESK} -- env {env} python3 /opt/ams-src/tests/vm/desktop.py "
              + " ".join(shlex.quote(a) for a in args)).stdout.strip()


def n_finestre():
    try:
        return int(desk("finestre") or 0)
    except ValueError:
        return 0


def attendi_finestre(n, tempo):
    """Attende che le finestre di AMS aperte siano n; restituisce i secondi, o None."""
    t0 = time.time()
    while time.time() - t0 < tempo:
        if n_finestre() == n:
            return round(time.time() - t0, 2)
        time.sleep(0.2)
    return None


def testo_finestra(tempo=6):
    """Il testo della prima finestra di AMS; subito dopo un login l'accessibilità di
    GNOME può esporre la finestra prima del suo contenuto, quindi si riprova."""
    t0 = time.time()
    t = ""
    while time.time() - t0 < tempo:
        t = desk("testo")
        if "|" in t:
            break
        time.sleep(0.3)
    return t


def attendi_stato(mid, utente, prova, tempo=8):
    """Attende che lo stato del destinatario soddisfi prova(stato): l'agente registra
    conferme e rinvii un istante dopo la chiusura della finestra."""
    t0 = time.time()
    st = ""
    while time.time() - t0 < tempo:
        st = stato(mid, utente) or ""
        if prova(st):
            break
        time.sleep(0.2)
    return st


def cattura(nome):
    """Chiede a esegui.sh (fuori dalla VM) una schermata, e lascia il tempo di farla."""
    print(f"@@CATTURA {nome}", flush=True)
    time.sleep(2.5)


def agente_attivo():
    return sh(f"pgrep -u {DESK} -f '^/bin/bash /usr/local/lib/ams/ams-user agent$'").returncode == 0


def apri(utente):
    """Una sessione ssh con terminale, senza attendere il prompt (al login può esserci la domanda)."""
    s = Sessione.__new__(Sessione)
    s.utente, s.buf = utente, ""
    s.pid, s.fd = pty.fork()
    if s.pid == 0:
        os.execvp("ssh", ["ssh", "-tt", f"{utente}@localhost"])
    return s


ETICHETTE = {}


def testi(lingua):
    """I testi di AMS nella lingua data, dal suo file in lib/lingue."""
    src = open(f"/usr/local/lib/ams/lingue/{lingua}.sh").read()
    return dict(re.findall(r'^\t\[(\w+)\]="((?:[^"\\]|\\.)*)"$', src, re.M))


def i_desktop():
    if not DESK:
        registra("I1", "Desktop", "finestra di conferma nella sessione grafica", "finestra «Ho letto»",
                 None, "il container non ha una sessione grafica: la finestra si prova nella VM (tests/vm)")
        return
    grafica = sh(f"loginctl show-user {DESK} -p Display --value").stdout.strip()
    # la finestra è nella lingua della sessione grafica, cioè dell'ambiente dell'agente
    pid = sh(f"pgrep -u {DESK} -f '^/bin/bash /usr/local/lib/ams/ams-user agent$'").stdout.split()
    lingua = sh(f"AMS_LIB=/usr/local/lib/ams bash -c '. $AMS_LIB/ams-common.sh; ams_env_lang </proc/{pid[0]}/environ; "
                "echo $_LINGUA'").stdout.strip() if pid else "en"
    ETICHETTE.update(testi(lingua))
    registra("I0", "Desktop", f"{DESK} ha una sessione grafica con l'agente di AMS attivo "
             "(l'avvio dal login automatico lo verifica esegui.sh prima degli scenari)",
             "sessione grafica, agente attivo", bool(grafica) and agente_attivo(), f"sessione {grafica}")

    t0 = time.time()
    ams(f'send --to {DESK} --title Manutenzione "Server spento sabato dalle 8 alle 12."')
    dt = attendi_finestre(1, 20)
    testo = testo_finestra()
    titolo = desk("titolo")
    registra("I1", "Desktop", "la finestra compare da sola dopo l'invio, nella lingua della sessione",
             f"finestra «{ETICHETTE['dlg_title']}» ({lingua}) con titolo e testo",
             dt is not None and "Server spento sabato" in testo and titolo == ETICHETTE["dlg_title"],
             f"{titolo} | {testo[:120]}",
             secondi_alla_finestra=round(time.time() - t0, 2) if dt is not None else None)
    cattura("I1-finestra")
    desk("clicca", ETICHETTE["dlg_ok"])
    chiusa = attendi_finestre(0, 10)
    st = attendi_stato(1, DESK, lambda x: x.startswith("confermato"))
    registra("I2", "Desktop", "«Ho letto»: la finestra si chiude e la conferma è registrata",
             "confermato (desktop)", chiusa is not None and st.startswith("confermato") and st.endswith("(desktop)"), st)

    # solleciti rapidi per la prova; l'agente riparte e rilegge la configurazione
    sh("printf 'AMS_REMIND_MINUTES=1\nAMS_AGENT_POLL=5\n' > /etc/ams/ams.conf")
    sh(f"pkill -u {DESK} -f '^/bin/bash /usr/local/lib/ams/ams-user agent$'")
    time.sleep(1)
    t0 = time.time()
    ams(f'send --to {DESK} "Secondo messaggio"')
    dt = attendi_finestre(1, 30)
    registra("I8", "Desktop", "agente assente: ams send lo avvia (systemd-run) e la finestra compare",
             "agente attivo, finestra", dt is not None and agente_attivo(),
             secondi_alla_finestra=round(time.time() - t0, 2) if dt is not None else None)
    desk("clicca", ETICHETTE["dlg_later"])
    attendi_finestre(0, 10)
    st = attendi_stato(2, DESK, lambda x: "rimandato" in x)
    registra("I3", "Desktop", "«Più tardi»: la finestra si chiude, il messaggio resta consegnato",
             "consegnato, rimandato il …", st.startswith("consegnato") and "rimandato" in st, st)
    t0 = time.time()
    dt = attendi_finestre(1, 120)
    registra("I4", "Desktop", "dopo il rinvio (1 minuto per la prova) la finestra ricompare",
             "finestra di nuovo, dopo circa 60 s", dt is not None, secondi_alla_ricomparsa=dt)
    desk("clicca", ETICHETTE["dlg_ok"])
    attendi_finestre(0, 10)

    ams(f'send --to {DESK} "Confermato dal terminale"')
    attendi_finestre(1, 20)
    s = apri(DESK)
    s.leggi_fino(r"Confermi", 15)
    t0 = time.time()
    s.scrivi("s\n")
    dt = attendi_finestre(0, 10)
    st = attendi_stato(3, DESK, lambda x: x.startswith("confermato"))
    registra("I5", "Desktop", "conferma da un terminale con la finestra aperta: la finestra si chiude da sola",
             "finestra chiusa, confermato (terminale)", dt is not None and "(terminale" in st, st,
             secondi_alla_chiusura=round(time.time() - t0, 2) if dt is not None else None)
    s.chiudi()

    ams(f'send --to {DESK} "Da ritirare"')
    attendi_finestre(1, 20)
    t0 = time.time()
    ams("revoke 4")
    dt = attendi_finestre(0, 10)
    registra("I6", "Desktop", "ritiro con la finestra aperta: la finestra si chiude da sola", "finestra chiusa",
             dt is not None, secondi_alla_chiusura=round(time.time() - t0, 2) if dt is not None else None)

    ams(f'send --to {DESK} "Primo di due"')
    ams(f'send --to {DESK} "Secondo di due"')
    attendi_finestre(1, 20)
    t1 = testo_finestra()
    desk("clicca", ETICHETTE["dlg_ok"])
    time.sleep(1)
    dt = attendi_finestre(1, 15)
    t2 = testo_finestra()
    desk("clicca", ETICHETTE["dlg_ok"])
    st = attendi_stato(6, DESK, lambda x: x.startswith("confermato"))
    registra("I7", "Desktop", "due messaggi: le finestre compaiono una dopo l'altra, dal più vecchio",
             "«Primo di due», poi «Secondo di due», entrambi confermati",
             "Primo di due" in t1 and dt is not None and "Secondo di due" in t2 and st.startswith("confermato"),
             f"{t1[-30:]} → {t2[-30:]}; {st}")
    attendi_finestre(0, 10)

    # «Ho letto» e uscita immediata dalla sessione: la conferma non deve perdersi
    ams(f'send --to {DESK} "Clic e via"')
    attendi_finestre(1, 20)
    desk("clicca", ETICHETTE["dlg_ok"])
    time.sleep(0.1)
    sh(f"loginctl terminate-user {DESK}")
    time.sleep(2)
    st = stato(7, DESK) or ""
    registra("I10", "Desktop", "«Ho letto» e subito fuori dalla sessione (0,1 s): la conferma resta",
             "confermato (desktop)", st.startswith("confermato"), st)

    # messaggio in attesa, poi login grafico
    time.sleep(1)
    ams(f'send --to {DESK} "In attesa del login"')
    t0 = time.time()
    sh("systemctl restart gdm")
    dt = attendi_finestre(1, 90)
    t9 = testo_finestra()
    registra("I9", "Desktop", "messaggio mandato a desktop chiuso: la finestra compare al login grafico",
             "finestra dopo il login automatico", dt is not None and "In attesa del login" in t9, t9[-60:],
             secondi_dal_riavvio_del_login=round(time.time() - t0, 2) if dt is not None else None)
    cattura("I9-login")
    desk("clicca", ETICHETTE["dlg_ok"])
    attendi_finestre(0, 10)
    sh("printf 'AMS_REMIND_MINUTES=30\nAMS_AGENT_POLL=60\n' > /etc/ams/ams.conf")


# ---- rapporto ----

def rapporto():
    os.makedirs(OUT, exist_ok=True)
    meta = dict(data=time.strftime("%Y-%m-%d %H:%M:%S %Z"), versione=sh(f"{AMS} version").stdout.strip(),
                sistema=sh(". /etc/os-release; echo $PRETTY_NAME").stdout.strip()
                + (f", VM con GNOME, desktop di {DESK}" if DESK else ", container con systemd"),
                ok=sum(r["esito"] == "OK" for r in risultati), no=sum(r["esito"] == "NO" for r in risultati),
                non_provati=sum(r["esito"] == "NON PROVATO" for r in risultati), totale=len(risultati))
    with open(f"{OUT}/risultati.json", "w") as f:
        json.dump(dict(meta=meta, risultati=risultati), f, ensure_ascii=False, indent=1)
    righe = [f"# Prove di AMS {'nella VM con desktop' if DESK else 'nella macchina di prova'}\n",
             f"- Data: {meta['data']}", f"- {meta['versione']}", f"- Sistema: {meta['sistema']}",
             f"- Esito: **{meta['ok']} riusciti, {meta['no']} falliti, {meta['non_provati']} non provati** "
             f"su {meta['totale']} scenari\n",
             "| Codice | Area | Scenario | Atteso | Esito | Misure / dettagli |", "|---|---|---|---|---|---|"]
    for r in risultati:
        mis = ", ".join(f"{k} {v}" for k, v in r["misure"].items() if v is not None)
        det = (mis + ("; " if mis and r["dettagli"] else "") + (r["dettagli"] or "")).replace("|", "¦").replace("\n", " ")
        righe.append(f"| {r['codice']} | {r['area']} | {r['descrizione']} | {r['atteso']} | {r['esito']} | {det[:200]} |")
    with open(f"{OUT}/rapporto.md", "w") as f:
        f.write("\n".join(righe) + "\n")
    print(f"\n{meta['ok']} riusciti, {meta['no']} falliti, {meta['non_provati']} non provati su {meta['totale']}; "
          f"risultati in {OUT}")
    return meta["no"] == 0


if __name__ == "__main__":
    for fn in (a_accesso, b_destinatari, c_consegna, d_conferma, e_scadenza_ritiro, f_guasti, g_sicurezza,
               j_registro, k_shell, l_lingua, h_prestazioni, i_desktop):
        print(fn.__name__)
        scenario(fn)
    sys.exit(0 if rapporto() else 1)
