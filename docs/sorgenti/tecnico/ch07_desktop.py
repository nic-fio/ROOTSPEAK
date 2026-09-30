from build import arrow, box, c, fig, p, path, seq, table, text, ul

LOOP = fig(
    box(20, 110, 160, 58, "flock -n", "un agente per utente", "dark")
    + box(230, 110, 176, 58, "sessione grafica?", "loginctl show-user", "navy")
    + box(456, 110, 190, 58, "per ogni messaggio", "show_dialog se non rimandato", "blue")
    + box(700, 110, 180, 58, "attesa", "sleep POLL & wait", "soft")
    + arrow(182, 139, 228, 139) + arrow(408, 139, 454, 139) + arrow(648, 139, 698, 139)
    + path([(790, 110), (790, 30), (318, 30), (318, 108)], "#475569", True, "fine attesa: POLL secondi o SIGUSR1", 560, 24)
    + path([(318, 170), (318, 200)], "#b91c1c") + text(318, 216, "no: l'agente termina", 11, "#b91c1c", "600"),
    900, 240, "«FIG» — Il ciclo dell'agente del desktop", "")

S1 = p("L'agente, " + c("ams-user agent") + ", parte con l'avvio automatico del desktop e vive quanto la sessione "
       "grafica.", lead=True) + LOOP + ul([
    "<b>Pronto</b>: la ricezione del segnale è la prima istruzione dello script; dopo il lock l'agente scrive il suo "
    "PID in " + c("$XDG_RUNTIME_DIR/ams-agent.pronto") + " e lo cancella all'uscita. " + c("ams send") + " sveglia solo "
    "quel PID (capitolo 5.6).",
    "<b>Un solo agente per utente</b>: " + c("flock -n") + " su " + c("$XDG_RUNTIME_DIR/ams-agent.lock")
    + ". Il descrittore del lock non passa ai figli (" + c("9>&-") + " su " + c("zenity") + " e " + c("sleep")
    + "): altrimenti, se l'agente muore, un suo " + c("sleep") + " o una sua finestra rimasti orfani terrebbero il lock "
    "fino a 60 secondi, e l'agente avviato al suo posto da " + c("ams send") + " uscirebbe subito (difetto trovato "
    "dalla VM di prova).",
    "<b>Configurazione sempre attuale</b>: " + c("ams_load_conf") + " a ogni giro.",
    "<b>Vive quanto la sessione</b>: il ciclo continua finché " + c("loginctl show-user U -p Display")
    + " indica una sessione grafica.",
    "<b>Una finestra alla volta</b>: i messaggi non rimandati, dal più vecchio.",
    "<b>Attesa interrompibile</b>: " + c("sleep AMS_AGENT_POLL & wait $!") + " con " + c("trap : USR1") + ". Il segnale "
    "di " + c("ams send") + " interrompe " + c("wait") + ": la finestra compare in circa un decimo di secondo. Il "
    "controllo periodico, ogni 60 secondi, resta come rete di sicurezza.",
    "<b>Uscita pulita</b>: all'uscita dalla sessione logind manda " + c("SIGTERM") + " a tutti i processi dell'utente. "
    "L'agente lo annota (" + c("trap 'AMS_FINE=1' TERM HUP INT") + "), finisce di registrare la risposta già data ed "
    "esce al primo punto sicuro: una conferma interrotta a metà andrebbe persa.",
])

DIALOG = seq([("show_dialog", "", "navy"), ("zenity", "--question --no-markup", "blue"), ("Casella", "users/U", "soft"),
              ("Utente", "", "dark")], [
    (0, 1, "avvia in background"),
    (1, 3, "finestra «Ho letto» / «Più tardi»"),
    (0, 2, "ogni secondo: acks/ID? inbox/ID?"),
    ("sep", "tre modi di finire"),
    (3, 1, "«Ho letto»: codice 0 → ack desktop"),
    (3, 1, "«Più tardi» o chiusura (codice 1) → snooze gui", True),
    (0, 1, "confermato altrove o ritirato → kill", True),
], "«FIG» — La finestra di conferma", "")

S2 = p(c("show_dialog") + " apre " + c("zenity --question --no-markup") + " in background (il testo non è interpretato "
       "come markup) e ne <b>attende direttamente</b> la chiusura, così registra la risposta appena arriva. Un "
       "controllore separato guarda la casella ogni secondo e chiude la finestra se il messaggio è stato confermato "
       "altrove, ritirato o è scaduto. Prima era l'agente stesso a controllare ogni secondo: un'uscita dalla sessione "
       "subito dopo «Ho letto» poteva perdere la conferma (trovato dalla VM di prova, scenario I10).", lead=True) + DIALOG + table(["Uscita di zenity", "Effetto"], [
    ["codice 0 («Ho letto»)", c("ack ID desktop") + "; se la scrittura fallisce, una notifica lo dice e la finestra torna al giro successivo"],
    ["codice 1 («Più tardi», finestra chiusa dall'utente)", c("snooze ID gui") + ": tocca " + c("state/ID.gui")],
    ["processo chiuso da show_dialog", "nulla: la conferma o il ritiro sono già avvenuti"],
    ["altri codici (finestra uccisa, per esempio all'uscita dalla sessione)", "nulla: non è una scelta dell'utente; "
     "la finestra torna al giro successivo o al prossimo login"],
], "«TAB» — Come finisce una finestra") + \
    p("Il segnale di sveglia di " + c("ams send") + " interrompe anche l'attesa sulla finestra (" + c("wait")
      + " esce con 138 mentre zenity è ancora aperto): in quel caso " + c("show_dialog") + " attende di nuovo. Prima "
      "l'agente dava per chiusa la finestra e registrava un rinvio mai scelto; il difetto è comparso quando le "
      "traduzioni hanno ritardato di poco l'apertura della finestra (VM di prova, scenario I7).")

S3 = p("L'agente usa " + c("notify-send") + ", se è installato, per un solo caso: dire all'utente che la sua conferma non "
       "è stata registrata. Il testo è fisso: nessun contenuto dei messaggi passa per le notifiche.", lead=True)

CHAPTER = ("La ricezione sul desktop", [
    ("Il ciclo dell'agente", S1),
    ("La finestra di conferma", S2),
    ("La notifica d'errore", S3),
])
