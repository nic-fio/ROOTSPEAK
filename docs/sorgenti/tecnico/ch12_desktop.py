from build import arrow, box, c, code, dialog, fig, notification, note, p, path, seq, table, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


LOOP = fig(
    box(20, 110, 160, 58, "flock LOCK_NB", "un agente per utente", "dark")
    + box(215, 110, 150, 58, "ams-agent.pronto", "il PID, per la sveglia", "dark", 12)
    + box(400, 110, 170, 58, "sessione grafica?", "sd-login, a ogni giro", "navy", 12)
    + box(605, 110, 150, 58, "per ogni messaggio", "non rimandato", "blue", 12)
    + box(790, 110, 90, 58, "attesa", "ppoll 1 s", "soft", 12)
    + arrow(182, 139, 213, 139) + arrow(367, 139, 398, 139) + arrow(572, 139, 603, 139) + arrow(757, 139, 788, 139)
    + path([(835, 108), (835, 30), (485, 30), (485, 108)], "#475569", True,
           "fine attesa: AMS_AGENT_POLL secondi o SIGUSR1", 660, 22)
    + path([(485, 170), (485, 200)], "#b91c1c") + text(485, 216, "no: l'agente esce", 11, "#b91c1c", "600")
    + text(100, 196, "lock occupato:", 11, "#475569") + text(100, 212, "esce subito", 11, "#475569"),
    900, 236, "«FIG» — Il ciclo dell'agente del desktop", "Il ciclo dell'agente")

S1 = p("L'agente, " + c("ams-user agent") + ", parte con l'avvio automatico del desktop ("
       + c("/etc/xdg/autostart/ams-agent.desktop") + ") o da " + c("systemd-run") + " quando " + c("ams send")
       + " non ne trova uno, e vive quanto la sessione grafica.", lead=True) + LOOP + ul([
    "<b>Un solo agente per utente</b>: " + c("flock(LOCK_EX | LOCK_NB)") + " su " + c("$XDG_RUNTIME_DIR/ams-agent.lock")
    + "; se il lock è occupato l'agente esce subito, senza errore. Il descrittore è aperto con " + c("O_CLOEXEC")
    + " e non passa a zenity: altrimenti, se l'agente muore, una sua finestra orfana terrebbe il lock e l'agente "
    "avviato al suo posto uscirebbe subito (difetto trovato dalla VM di prova).",
    "<b>Pronto</b>: dopo il lock l'agente scrive il suo PID in " + c("$XDG_RUNTIME_DIR/ams-agent.pronto")
    + " e lo cancella all'uscita (" + c("atexit") + "). " + c("ams send") + " sveglia solo quel PID (" + cap(8, 5)
    + ").",
    "<b>Vive quanto la sessione</b>: il ciclo continua finché " + c("sessione_grafica(getuid())") + " trova una "
    "sessione X11 o Wayland dell'utente, oppure finché non arriva un segnale di fine.",
    "<b>Configurazione sempre attuale</b>: " + c("conf_leggi") + " a ogni giro; una modifica di "
    + c("AMS_REMIND_MINUTES") + " o " + c("AMS_AGENT_POLL") + " vale dal giro successivo.",
    "<b>Una finestra alla volta</b>: i messaggi non rimandati sul canale del desktop (" + c("state/ID.gui")
    + "), dal più vecchio (scenario I7).",
])

SEGNALI = fig(
    box(20, 50, 200, 60, "sempre bloccati", "USR1 TERM HUP INT CHLD", "dark")
    + box(260, 50, 200, 60, "ppoll(…, &attesa)", "sbloccati solo qui", "navy")
    + box(500, 30, 180, 44, "SIGUSR1", "sveglia = 1", "blue", 12)
    + box(500, 84, 180, 44, "SIGTERM, HUP, INT", "fine = 1", "amber", 12)
    + box(500, 138, 180, 44, "SIGCHLD", "zenity si è chiusa", "green", 12)
    + box(720, 30, 160, 44, "giro subito", "nuovo messaggio", "light", 12)
    + box(720, 84, 160, 44, "esce", "al primo punto sicuro", "light", 12)
    + box(720, 138, 160, 44, "registra", "la risposta, subito", "light", 12)
    + arrow(222, 80, 258, 80) + arrow(462, 70, 498, 52) + arrow(462, 80, 498, 106) + arrow(462, 90, 498, 160)
    + arrow(682, 52, 718, 52) + arrow(682, 106, 718, 106) + arrow(682, 160, 718, 160)
    + text(240, 200, "un segnale arrivato fuori dall'attesa resta in sospeso: non va perso", 11.5, "#166534", "600"),
    900, 220, "«FIG» — I segnali dell'agente: bloccati tranne durante le attese", "Nessun segnale perso")

S2 = p("L'agente deve reagire a tre cose: un messaggio nuovo (" + c("SIGUSR1") + " da " + c("ams send") + "), la "
       "fine della sessione (" + c("SIGTERM") + " da logind) e la chiusura della finestra (" + c("SIGCHLD")
       + "). Le gestisce senza perdere segnali e senza interrompere a metà una conferma.", lead=True) + SEGNALI + \
    table(["Segnale", "Gestore", "Effetto"], [
        [c("SIGUSR1"), c("su_sveglia") + ": " + c("sveglia = 1"), "l'attesa finisce e il giro riparte subito; è "
         "installato come <b>prima istruzione</b> di " + c("main") + ", perché per difetto " + c("SIGUSR1")
         + " termina il processo (nel prototipo, 20 agenti su 20 svegliati mentre partivano morivano)"],
        [c("SIGTERM") + ", " + c("SIGHUP") + ", " + c("SIGINT"), c("su_fine") + ": " + c("fine = 1"),
         "l'agente finisce di registrare la risposta già data ed esce al primo punto sicuro"],
        [c("SIGCHLD"), c("su_figlio") + ": nulla", "interrompe l'attesa: la risposta della finestra si registra in "
         "pochi millisecondi"],
    ], "«TAB» — I segnali dell'agente") + ul([
    "I cinque segnali restano bloccati con " + c("sigprocmask") + " per tutto il tempo, tranne durante le attese, "
    "fatte con " + c("ppoll") + " che li sblocca e li riblocca in modo atomico: un segnale arrivato mentre l'agente "
    "lavora resta in sospeso e interrompe l'attesa successiva.",
    "Le attese durano al più un secondo ciascuna; quella fra un giro e l'altro dura in tutto "
    + c("AMS_AGENT_POLL") + " secondi (60), e finisce prima se arriva la sveglia o la fine. Il controllo periodico "
    "resta come rete di sicurezza: un segnale perso ritarda la finestra, non la perde.",
    "La sveglia azzera il suo indicatore all'<b>inizio</b> del giro: una sveglia arrivata con una finestra aperta "
    "fa ripartire subito il giro successivo.",
])

FIN = seq([("mostra_finestra", "agente", "navy"), ("zenity", "--question --no-markup", "blue"),
           ("Casella", "users/U", "soft"), ("Utente", "", "dark")], [
    (0, 1, "fork, exec (segnali ripristinati)"),
    (1, 3, "«Ho letto» / «Più tardi»"),
    ("nota", 0, "ogni secondo: waitpid"),
    (0, 2, "acks/ID? inbox/ID? scaduto?"),
    ("sep", "tre modi di finire"),
    (3, 1, "«Ho letto»: uscita 0"),
    (1, 0, "SIGCHLD → conferma desktop", True),
    (3, 1, "«Più tardi», chiusura: uscita 1"),
    (0, 2, "rinvio: state/ID.gui"),
    ("nota", 0, "altrove o ritirato: SIGTERM"),
], "«FIG» — La finestra di conferma", "Una finestra, dall'apertura alla risposta")

S3 = p(c("mostra_finestra") + " avvia " + c("zenity --question --no-markup --width=460") + " con titolo, testo e "
       "pulsanti nella lingua della sessione, e ne attende la fine controllando ogni secondo anche la casella.",
       lead=True) + dialog("AMS · Messaggio dall'amministratore", "Manutenzione · 30/09 16:55",
                           "Sabato dalle 8 alle 12 il server sarà spento.",
                           "«FIG» — La finestra come la disegna zenity su GNOME (ricostruzione)") + FIN + table(
    ["Come finisce", "Effetto"], [
        ["uscita 0 («Ho letto»)", c("conferma(ID, \"desktop\")") + "; se la scrittura fallisce e il messaggio è "
         "ancora nella casella, una notifica lo dice e la finestra torna al giro successivo"],
        ["uscita 1 («Più tardi», o finestra chiusa dall'utente)", c("rimanda(ID, \"gui\")") + ": tocca "
         + c("state/ID.gui") + ", evento " + c("RINVIATO")],
        ["chiusa dall'agente: conferma altrove, ritiro o scadenza", "nulla: se è scaduto, il messaggio passa in "
         + c("read/")],
        ["altri esiti (finestra uccisa, per esempio all'uscita dalla sessione)", "nulla: non è una scelta "
         "dell'utente; la finestra torna al giro successivo o al prossimo login"],
    ], "«TAB» — Come finisce una finestra") + ul([
    c("--no-markup") + ": il testo del messaggio non è interpretato come marcatura di zenity. Il testo è già "
    "ripulito all'invio (" + cap(8, 7) + ").",
    "Il figlio che diventa zenity ripristina maschera e gestori dei segnali prima di " + c("exec") + ": zenity non "
    "eredita i blocchi dell'agente.",
    "La fine di zenity interrompe subito l'attesa (" + c("SIGCHLD") + "): la risposta si registra in pochi "
    "millisecondi, così un " + c("ams remind") + " che arriva subito dopo un «Più tardi» trova il rinvio già "
    "scritto e lo toglie (scenario I11; con un controllo al secondo, la VM aveva trovato il sollecito perso).",
    "Il segnale di sveglia non chiude la finestra: l'agente continua ad aspettarla. Nel prototipo in bash il "
    "segnale interrompeva " + c("wait") + " e l'agente dava per chiusa la finestra, registrando un rinvio mai "
    "scelto (VM di prova, scenario I7).",
    "All'uscita dalla sessione l'agente aspetta la finestra al più 2 secondi, poi la chiude: una conferma già "
    "data non va persa (scenario I10: «Ho letto» e uscita dopo 0,1 s, conferma registrata).",
    "Tempi dell'ultima esecuzione registrata nella VM: finestra dopo l'invio 0,58 s (I1), chiusura dopo una "
    "conferma dal terminale 0,65 s (I5), dopo un ritiro 0,67 s (I6), al login grafico 2,64 s dopo il riavvio del "
    "login (I9).",
])

S4 = p("L'agente usa " + c("notify-send") + ", se è installato, per un solo caso: dire all'utente che la sua "
       "conferma <b>non</b> è stata registrata (disco pieno, permessi). Il testo è fisso: nessun contenuto dei "
       "messaggi passa per le notifiche, che possono sparire da sole o essere ignorate.", lead=True) + \
    notification("AMS · Conferma non registrata",
                 "Non è stato possibile registrare la conferma: il messaggio verrà riproposto.",
                 "«FIG» — L'unica notifica di AMS (ricostruzione)") + \
    note("per la conferma AMS usa una finestra e non una notifica: una notifica di GNOME può sparire da sola o "
         "essere ignorata, mentre la finestra di zenity resta aperta finché l'utente non sceglie.")

CHAPTER = ("La ricezione sul desktop", [
    ("Il ciclo dell'agente", S1),
    ("Segnali e attese senza perdite", S2),
    ("La finestra di conferma", S3),
    ("La notifica d'errore", S4),
])
