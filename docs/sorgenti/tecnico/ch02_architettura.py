from build import c, note, p, seq, table

SEND = seq([("ams send", "root", "navy"), ("Casella U", "users/U", "dark"), ("Terminali di U", "/dev/pts/N", "blue"),
            ("Agente di U", "sessione grafica", "blue"), ("Journal", "logger -t ams", "soft")], [
    (0, 0, "destinatari, pulizia del testo, ID"),
    (0, 1, "inbox/ID (come U, runuser)"),
    (0, 2, "testo formattato (timeout 3)"),
    (0, 3, "SIGUSR1 (pkill come U)"),
    (0, 4, "«messaggio N inviato…»", True),
    ("sep", "l'utente risponde"),
    (3, 1, "legge inbox/ID, apre zenity"),
    (3, 1, "«Ho letto»: acks/ID, sposta in read/"),
    (3, 4, "«confermata la lettura…»", True),
], "«FIG» — Invio e conferma: chi scrive cosa", "Il percorso di un messaggio", width=920)

S1 = p("Un messaggio attraversa tre ambiti con privilegi diversi. " + c("ams send") + ", come root, scrive la copia di "
       "riferimento e la casella; da lì i componenti dell'utente, con i suoi soli permessi, lo mostrano e ne "
       "registrano la conferma.", lead=True) + SEND + table(["Passo", "Chi", "Effetto"], [
    ["1", c("ams send"), "risolve i destinatari, pulisce testo e titolo, prende un ID, scrive " + c("sent/ID/")],
    ["2", c("ams send") + " come U", "scrive " + c("users/U/inbox/ID") + " (prima " + c(".tmp") + ", poi rinomina), verifica "
     "che ci sia, e solo allora annota la consegna in " + c("sent/ID/delivery")],
    ["3", c("ams send"), "scrive il testo su ogni terminale di U; per " + c("info") + ", se almeno uno riceve, lo segna mostrato"],
    ["4", c("ams send") + " come U", "sveglia l'agente con " + c("SIGUSR1") + ", o lo avvia con " + c("systemd-run --user")],
    ["5", "aggancio o agente", "mostrano il messaggio; la conferma crea " + c("acks/ID") + " e sposta il messaggio in " + c("read/")],
    ["6", c("ams status"), "confronta " + c("sent/ID/recipients") + " con le caselle"],
], "«TAB» — I passi dell'invio")

S2 = p("AMS non usa utmp, che non registra molti terminali moderni, ma logind e i dispositivi dei terminali.",
       lead=True) + table(["Sessione dell'utente", "Come la trova AMS", "Canale"], [
    ["console di testo (" + c("tty3") + ")", "sessione logind di tipo " + c("tty") + " con " + c("TTY=tty3"), "terminale"],
    ["ssh con terminale", "pseudo-terminale " + c("/dev/pts/N") + " di proprietà dell'utente", "terminale"],
    ["terminale del desktop, tmux", "pseudo-terminale di proprietà dell'utente", "terminale (aggancio della shell)"],
    ["desktop X11 o Wayland", "sessione logind di tipo " + c("x11") + " o " + c("wayland"), "agente del desktop"],
    ["ssh senza terminale, scp, cron", "nessun terminale", "nessuno: non vengono toccate"],
    ["utente non collegato", "—", "la casella, letta al prossimo accesso"],
], "«TAB» — Le sessioni e i canali di consegna") + \
    note("un terminale in cui l'utente è entrato con " + c("su") + " resta di proprietà di chi l'ha aperto: "
         + c("ams send") + " non lo trova. L'aggancio della shell lo raggiunge comunque al prompt successivo.")

CHAPTER = ("Architettura", [
    ("Il percorso di un messaggio", S1),
    ("Sessioni e canali", S2),
])
