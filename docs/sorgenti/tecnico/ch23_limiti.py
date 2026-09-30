from build import box, c, fig, note, p, table, text


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


def cella(x, y, ok, testo):
    return box(x, y, 150, 34, testo, "", "green" if ok else "soft", 11.5)


COPERTURA = fig(
    text(180, 58, "testo all'invio", 12, "#003a90", "700")
    + text(340, 58, "domanda al login", 12, "#003a90", "700")
    + text(500, 58, "domanda al prompt", 12, "#003a90", "700")
    + text(660, 58, "finestra", 12, "#003a90", "700")
    + text(820, 58, "prova", 12, "#003a90", "700")
    + text(20, 94, "bash", 12.5, "#334155", "700", "start")
    + cella(105, 76, True, "sì") + cella(265, 76, True, "sì") + cella(425, 76, True, "sì")
    + cella(585, 76, False, "se c'è un desktop") + text(820, 98, "suite", 11.5)
    + text(20, 136, "zsh, fish", 12.5, "#334155", "700", "start")
    + cella(105, 118, True, "sì") + cella(265, 118, True, "sì") + cella(425, 118, True, "sì")
    + cella(585, 118, False, "se c'è un desktop") + text(820, 140, "scenari K", 11.5)
    + text(20, 178, "ksh, dash, sh", 12.5, "#334155", "700", "start")
    + cella(105, 160, True, "sì") + cella(265, 160, True, "sì") + cella(425, 160, False, "no")
    + cella(585, 160, False, "se c'è un desktop") + text(820, 182, "scenari K", 11.5)
    + text(20, 220, "altre shell", 12.5, "#334155", "700", "start")
    + cella(105, 202, True, "sì") + cella(265, 202, False, "se leggono profile") + cella(425, 202, False, "no")
    + cella(585, 202, False, "se c'è un desktop") + text(820, 224, "no", 11.5),
    900, 246, "«FIG» — Dove arriva un messaggio, shell per shell", "Copertura delle shell")

S1 = p("I limiti che seguono sono noti e accettati: nascono dalle decisioni del progetto o da ciò che il sistema "
       "offre. Ognuno dice che cosa succede, così chi amministra la macchina sa che cosa aspettarsi.", lead=True) + \
    COPERTURA + table(["Limite", "Conseguenza"], [
        ["sh, dash, ksh e simili non hanno un aggancio prima del prompt", "la domanda arriva al login (e dal "
         "desktop); durante la sessione arriva solo il testo, all'invio"],
        ["zsh installata dopo AMS", "serve rilanciare " + c("install.sh") + " per la riga nello zshrc"],
        ["l'intestazione scritta all'invio usa la lingua con cui è partita la shell", "se l'utente cambia "
         + c("LANG") + " dentro la shell (per esempio nel " + c(".bashrc") + "), l'intestazione resta nella lingua "
         "del login; domanda e risposte seguono quella nuova"],
        ["lingue: italiano e inglese", "le altre lingue vedono l'inglese; i manuali sono solo in italiano"],
        ["date di " + c("--expires") + " a parole in inglese", "le interpreta " + c("date -d") + "; il formato ISO "
         "funziona sempre"],
        [c("su") + " non cambia il proprietario del terminale", c("ams send") + " non scrive in quel terminale "
         "all'invio; la domanda arriva comunque al prompt"],
        ["se l'agente del desktop muore, la sua finestra resta aperta", "l'agente che lo sostituisce apre una seconda "
         "finestra per lo stesso messaggio; la prima non registra più nulla"],
        ["un solo agente per utente, anche con più sessioni grafiche", "il lock è unico per utente; il comportamento "
         "con più desktop aperti dallo stesso utente non è stato provato"],
        [c("ams-agent.pronto") + " si scrive in " + c("$XDG_RUNTIME_DIR") + " (o in " + c("/tmp") + " se manca) e si "
         "cerca in " + c("/run/user/UID"), "coincidono nelle sessioni di logind; altrimenti la sveglia non trova "
         "l'agente, e il caso non è stato provato"],
        ["il rinvio sul desktop vale anche dopo un nuovo login grafico", "a differenza del terminale, dove al login "
         "la domanda torna sempre (" + cap(20, 7) + ")"],
        ["senza " + c("/dev/tty") + " la domanda vale «no»", "si registra un rinvio; in pratica l'aggancio lancia "
         + c("ams-user prompt") + " solo con un terminale"],
        ["gli eventi scritti con " + c("syslog") + " quando il journal manca", c("ams log") + " non li legge"],
        ["la ricerca della TUI ignora maiuscole e minuscole solo per le lettere senza accento", "«è» non trova «È»"],
        ["salvataggio e ripristino dell'archivio, interruzione di corrente vera", "non provati (" + cap(5, 6) + ", "
         + cap(20, 6) + ")"],
    ], "«TAB» — Limiti noti")

S2 = table(["Punto", "Stato"], [
    ["prova dal vivo della versione in C sul PC dell'utente", "da fare (provato dal vivo solo il prototipo 0.1.0)"],
    ["invio programmato (" + c("--at") + ")", "previsto, seconda versione"],
    ["modelli di messaggio riutilizzabili", "previsto, seconda versione"],
    ["esportazione CSV o JSON per audit", "previsto, seconda versione"],
    ["pacchetti deb e rpm", "previsto, seconda versione"],
    [c("ams remind") + ": sollecito manuale", "fatto (" + cap(9, 2) + ")"],
    ["interfaccia a schede per l'amministratore", "fatta: la TUI (" + cap(14) + ")"],
    ["riscrittura in un linguaggio compilato", "fatta: versione 0.2.0 in C (decisione del 30 settembre)"],
    ["domanda di conferma in tutte le shell", "fatta dove la shell lo permette (" + cap(11, 1) + ")"],
    ["interfaccia nella lingua di ciascun utente", "fatta: italiano e inglese (" + cap(16) + ")"],
    ["risposta dell'utente all'amministratore", "non prevista (decisione del 30 settembre)"],
    ["livello " + c("block") + ", disconnessioni, blocco a schermo intero", "esclusi: l'utente può sempre rimandare"],
], "«TAB» — Punti aperti e decisi") + \
    note("le decisioni prese non si riaprono: il loro perché è in " + c("docs/decisioni-e-storia.md") + ".")

CHAPTER = ("Limiti noti e punti aperti", [
    ("Limiti noti", S1),
    ("Punti aperti", S2),
])
