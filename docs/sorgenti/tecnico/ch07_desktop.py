from build import arrow, box, c, fig, p, path, seq, table, text, ul

LOOP = fig(
    box(20, 110, 160, 58, "flock LOCK_NB", "un agente per utente", "dark")
    + box(230, 110, 176, 58, "sessione grafica?", "loginctl show-user", "navy")
    + box(456, 110, 190, 58, "per ogni messaggio", "mostra_finestra se non rimandato", "blue")
    + box(700, 110, 180, 58, "attesa", "ppoll, al più POLL s", "soft")
    + arrow(182, 139, 228, 139) + arrow(408, 139, 454, 139) + arrow(648, 139, 698, 139)
    + path([(790, 110), (790, 30), (318, 30), (318, 108)], "#475569", True, "fine attesa: POLL secondi o SIGUSR1", 560, 24)
    + path([(318, 170), (318, 200)], "#b91c1c") + text(318, 216, "no: l'agente termina", 11, "#b91c1c", "600"),
    900, 240, "«FIG» — Il ciclo dell'agente del desktop", "")

S1 = p("L'agente, " + c("ams-user agent") + ", parte con l'avvio automatico del desktop e vive quanto la sessione "
       "grafica.", lead=True) + LOOP + ul([
    "<b>Pronto</b>: la ricezione del segnale è la prima istruzione dello script; dopo il lock l'agente scrive il suo "
    "PID in " + c("$XDG_RUNTIME_DIR/ams-agent.pronto") + " e lo cancella all'uscita. " + c("ams send") + " sveglia solo "
    "quel PID (capitolo 5.6).",
    "<b>Un solo agente per utente</b>: " + c("flock(LOCK_EX | LOCK_NB)") + " su " + c("$XDG_RUNTIME_DIR/ams-agent.lock")
    + ". Il descrittore del lock è aperto con " + c("O_CLOEXEC") + " e non passa a " + c("zenity")
    + ": altrimenti, se l'agente muore, una sua finestra rimasta orfana terrebbe il lock "
    "fino a 60 secondi, e l'agente avviato al suo posto da " + c("ams send") + " uscirebbe subito (difetto trovato "
    "dalla VM di prova).",
    "<b>Configurazione sempre attuale</b>: " + c("ams_load_conf") + " a ogni giro.",
    "<b>Vive quanto la sessione</b>: il ciclo continua finché " + c("loginctl show-user U -p Display")
    + " indica una sessione grafica.",
    "<b>Una finestra alla volta</b>: i messaggi non rimandati, dal più vecchio.",
    "<b>Attesa interrompibile, senza segnali persi</b>: i segnali restano bloccati tranne durante le attese, fatte con "
    + c("ppoll") + " che li sblocca in modo atomico. Il segnale di " + c("ams send") + " interrompe l'attesa: la finestra "
    "compare in circa mezzo secondo; una sveglia arrivata con una finestra aperta fa ripartire subito il giro. Il "
    "controllo periodico, ogni 60 secondi, resta come rete di sicurezza.",
    "<b>Uscita pulita</b>: all'uscita dalla sessione logind manda " + c("SIGTERM") + " a tutti i processi dell'utente. "
    "L'agente lo annota (" + c("SIGTERM") + ", " + c("SIGHUP") + ", " + c("SIGINT") + " impostano " + c("fine") + "), finisce di registrare la risposta già data ed "
    "esce al primo punto sicuro: una conferma interrotta a metà andrebbe persa.",
])

DIALOG = seq([("mostra_finestra", "", "navy"), ("zenity", "--question --no-markup", "blue"), ("Casella", "users/U", "soft"),
              ("Utente", "", "dark")], [
    (0, 1, "avvia in background"),
    (1, 3, "finestra «Ho letto» / «Più tardi»"),
    (0, 2, "ogni secondo: acks/ID? inbox/ID?"),
    ("sep", "tre modi di finire"),
    (3, 1, "«Ho letto»: codice 0 → conferma desktop"),
    (3, 1, "«Più tardi» o chiusura (codice 1) → rinvio gui", True),
    (0, 1, "confermato altrove o ritirato → kill", True),
], "«FIG» — La finestra di conferma", "")

S2 = p(c("mostra_finestra") + " avvia " + c("zenity --question --no-markup") + " (il testo non è interpretato come "
       "markup; titolo e pulsanti nella lingua della sessione) e ne controlla la fine con " + c("waitpid") + " ogni "
       "secondo, così registra la risposta appena arriva. Nello stesso giro guarda la casella e chiude la finestra se il "
       "messaggio è stato confermato altrove, ritirato o è scaduto. All'uscita dalla sessione aspetta la finestra al "
       "più 2 secondi, poi la chiude: una conferma già data non va persa (scenario I10).", lead=True) + DIALOG + table(["Uscita di zenity", "Effetto"], [
    ["codice 0 («Ho letto»)", c("conferma(ID, \"desktop\")") + "; se la scrittura fallisce, una notifica lo dice e la finestra torna al giro successivo"],
    ["codice 1 («Più tardi», finestra chiusa dall'utente)", c("rimanda(ID, \"gui\")") + ": tocca " + c("state/ID.gui")],
    ["finestra chiusa dall'agente", "nulla: la conferma o il ritiro sono già avvenuti"],
    ["altri codici (finestra uccisa, per esempio all'uscita dalla sessione)", "nulla: non è una scelta dell'utente; "
     "la finestra torna al giro successivo o al prossimo login"],
], "«TAB» — Come finisce una finestra") + \
    p("Il segnale di sveglia di " + c("ams send") + " non chiude la finestra: l'agente continua ad aspettarla. Nel "
      "prototipo in bash il segnale interrompeva " + c("wait") + " e l'agente dava per chiusa la finestra, registrando "
      "un rinvio mai scelto (VM di prova, scenario I7).")

S3 = p("L'agente usa " + c("notify-send") + ", se è installato, per un solo caso: dire all'utente che la sua conferma non "
       "è stata registrata. Il testo è fisso: nessun contenuto dei messaggi passa per le notifiche.", lead=True)

CHAPTER = ("La ricezione sul desktop", [
    ("Il ciclo dell'agente", S1),
    ("La finestra di conferma", S2),
    ("La notifica d'errore", S3),
])
