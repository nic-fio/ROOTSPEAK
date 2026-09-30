from build import arrow, box, c, fig, p, path, seq, table, text, ul

LOOP = fig(
    box(20, 120, 160, 58, "flock -n", "un agente per utente", "dark")
    + box(230, 120, 176, 58, "sessione grafica?", "loginctl show-user", "navy")
    + box(456, 40, 190, 58, "1° giro: info", "notify-send, mark_shown", "light")
    + box(456, 200, 190, 58, "2° giro: ack", "show_dialog se non rimandato", "blue")
    + box(700, 120, 180, 58, "attesa", "sleep POLL & wait", "soft")
    + arrow(182, 149, 228, 149)
    + path([(408, 140), (430, 140), (430, 69), (454, 69)])
    + arrow(551, 100, 551, 198)
    + path([(648, 229), (676, 229), (676, 160), (698, 160)])
    + path([(790, 120), (790, 20), (318, 20), (318, 118)], "#475569", True, "fine attesa: POLL secondi o SIGUSR1", 560, 14)
    + text(318, 204, "no: l'agente termina", 11, "#b91c1c", "600")
    + path([(318, 180), (318, 190)], "#b91c1c"),
    900, 276, "«FIG» — Il ciclo dell'agente del desktop", "")

S1 = p("L'agente, " + c("ams-user agent") + ", parte con l'avvio automatico del desktop e vive quanto la sessione "
       "grafica.", lead=True) + LOOP + ul([
    "<b>Un solo agente per utente</b>: " + c("flock -n") + " su " + c("$XDG_RUNTIME_DIR/ams-agent.lock") + ".",
    "<b>Vive quanto la sessione</b>: il ciclo continua finché " + c("loginctl show-user U -p Display")
    + " indica una sessione grafica.",
    "<b>Prima gli avvisi</b>: un primo giro mostra gli " + c("info") + " con " + c("notify-send") + "; un secondo apre le "
    "finestre degli " + c("ack") + " non rimandati. Un avviso non resta in coda dietro una finestra in attesa di clic.",
    "<b>Attesa interrompibile</b>: " + c("sleep AMS_AGENT_POLL & wait $!") + " con " + c("trap : USR1") + ". Il segnale "
    "di " + c("ams send") + " interrompe " + c("wait") + ": la finestra compare in circa un decimo di secondo. Il "
    "controllo periodico, ogni 60 secondi, resta come rete di sicurezza.",
])

DIALOG = seq([("show_dialog", "", "navy"), ("zenity", "--question --no-markup", "blue"), ("Casella", "users/U", "soft"),
              ("Utente", "", "dark")], [
    (0, 1, "avvia in background"),
    (1, 3, "finestra «Ho letto» / «Più tardi»"),
    (0, 2, "ogni secondo: acks/ID? inbox/ID?"),
    ("sep", "tre modi di finire"),
    (3, 1, "«Ho letto»: codice 0 → ack desktop"),
    (3, 1, "«Più tardi» o chiusura → snooze gui", True),
    (0, 1, "confermato altrove o ritirato → kill", True),
], "«FIG» — La finestra di conferma", "")

S2 = p(c("show_dialog") + " apre " + c("zenity --question --no-markup") + " in background: il testo non è interpretato "
       "come markup. Poi controlla ogni secondo la casella e chiude la finestra se il messaggio è stato confermato "
       "altrove o ritirato.", lead=True) + DIALOG + table(["Uscita di zenity", "Effetto"], [
    ["codice 0 («Ho letto»)", c("ack ID desktop")],
    ["altro codice («Più tardi», finestra chiusa)", c("snooze ID gui") + ": tocca " + c("state/ID.gui")],
    ["processo chiuso da show_dialog", "nulla: la conferma o il ritiro sono già avvenuti"],
], "«TAB» — Come finisce una finestra")

S3 = p("Gli avvisi " + c("info") + " usano " + c("notify-send -a AMS") + ". I server di notifica interpretano il markup, "
       "quindi " + c("escape_markup") + " protegge " + c("&") + ", " + c("<") + " e " + c(">") + " nel titolo e nel "
       "testo. Una notifica non ha pulsanti e non chiede conferma: l'avviso passa subito in " + c("read/") + ".",
       lead=True)

CHAPTER = ("La ricezione sul desktop", [
    ("Il ciclo dell'agente", S1),
    ("La finestra di conferma", S2),
    ("Le notifiche", S3),
])
