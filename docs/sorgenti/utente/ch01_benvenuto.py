from build import arrow, box, c, fig, p, path, pill, table, text, ul

OVERVIEW = fig(
    box(20, 128, 160, 64, "Amministratore", "ams send", "dark")
    + box(232, 128, 176, 64, "AMS", "una casella per utente", "navy")
    + box(462, 38, 214, 64, "Nel terminale", "testo subito, domanda al prompt", "blue")
    + box(462, 128, 214, 64, "Sul desktop", "finestra «Ho letto»", "blue")
    + box(462, 218, 214, 64, "Al prossimo accesso", "per chi non è collegato", "light")
    + box(726, 128, 154, 64, "Conferma ✓", "chi, quando, da dove", "green")
    + arrow(182, 160, 230, 160)
    + path([(410, 150), (436, 150), (436, 70), (460, 70)])
    + arrow(410, 160, 460, 160)
    + path([(410, 170), (436, 170), (436, 250), (460, 250)])
    + path([(678, 70), (702, 70), (702, 150), (724, 150)], "#16a34a", True)
    + arrow(678, 160, 724, 160, "#16a34a", True)
    + path([(678, 250), (702, 250), (702, 170), (724, 170)], "#16a34a", True)
    + path([(803, 194), (803, 318), (100, 318), (100, 194)], "#475569", True)
    + text(452, 308, "ams status: chi ha confermato e chi no", 11.5, "#334155", "600"),
    900, 340, "«FIG» — Un messaggio va a ogni sessione dell'utente; la prima conferma torna all'amministratore",
    "Il percorso di un messaggio")

S1 = p("AMS permette a chi amministra una macchina Linux di mandare un messaggio agli utenti e di sapere, "
       "per ciascuno, se l'ha letto. È pensato per gli avvisi che contano: una manutenzione, una nuova regola, "
       "un account in scadenza.", lead=True) + \
    p("L'amministratore scrive un comando. AMS fa arrivare il messaggio dovunque l'utente si trovi: nelle finestre di "
      "terminale, sul desktop, oppure al prossimo accesso se in quel momento non è collegato. L'utente conferma con un "
      "clic o con una lettera, e l'amministratore vede chi ha confermato, quando e da dove.") + OVERVIEW

S2 = table(["", c("wall") + " / " + c("write"), "AMS"], [
    ["Scrive nei terminali degli utenti collegati", "sì", "sì"],
    ["Compare sul desktop (X11 e Wayland)", "no", "sì, in una finestra"],
    ["Raggiunge chi non è collegato", "no", "sì, al prossimo accesso"],
    ["Chiede la conferma di lettura", "no", "sì, se il messaggio lo richiede"],
    ["Sollecita chi non ha confermato", "no", "sì, ogni 30 minuti"],
    ["Dice all'amministratore chi ha letto", "no", "sì, con data, ora e canale"],
], "«TAB» — AMS e i comandi classici di Linux") + \
    p("AMS invece <b>non</b> fa queste cose, per scelta:") + ul([
        "<b>Non blocca nessuno.</b> Nessuna schermata bloccata, nessun accesso negato, nessuna disconnessione: "
        "l'utente può sempre rimandare e continuare a lavorare.",
        "<b>Non è una chat.</b> Gli utenti ricevono e confermano; non rispondono e non hanno comandi da imparare.",
        "<b>Non va in rete.</b> Raggiunge gli utenti di questa macchina, anche quelli collegati da remoto con ssh.",
        "<b>Non disturba i programmi automatici.</b> Backup, cron, copie con " + c("scp") + " o " + c("rsync")
        + " non vedono mai AMS.",
    ])

S3 = p("Il manuale segue l'ordine in cui di solito servono le cose:") + table(["Capitoli", "Per"], [
    ["2 e 3", "installare AMS e mandare il primo messaggio"],
    ["4 e 5", "scegliere destinatari e livello, poi controllare chi ha letto"],
    ["6", "sapere cosa vedono gli utenti, per poterlo spiegare"],
    ["7 e 8", "usare la guida integrata e cambiare le impostazioni"],
    ["9 e 10", "sicurezza, e cosa fare quando qualcosa non va"],
    ["11 e 12", "il riferimento di tutti i comandi e il glossario"],
], "«TAB» — Come è organizzato il manuale") + \
    p("Negli esempi " + c("admin") + " è un amministratore; " + c("mario") + ", " + c("anna") + " e " + c("luca")
      + " sono utenti della macchina " + c("server") + ". Nei riquadri scuri le righe che iniziano con il prompt sono "
      "comandi da scrivere; le righe arancioni sono quelle che AMS mostra agli utenti. Gli stati di un messaggio "
      "hanno sempre lo stesso colore: " + pill("da confermare", "wait") + " " + pill("rimandato", "snooze") + " "
      + pill("confermato", "ok") + " " + pill("scaduto o ritirato", "off") + ".")

CHAPTER = ("Benvenuto", [
    ("Che cos'è AMS", S1),
    ("Cosa fa, e cosa no", S2),
    ("Come leggere questo manuale", S3),
])
