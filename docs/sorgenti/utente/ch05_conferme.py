from build import arrow, box, c, fig, p, path, pill, table, term, text, ul, warn

S1 = p(c("ams list") + " mostra tutti i messaggi mandati, dal più vecchio al più recente.", lead=True) + term(
    "admin@server:~$ ams list\n"
    "ID    DATA         LIV.  CONFERME  TESTO\n"
    "1     03/10 18:30  ack   1/1       Sabato dalle 8 alle 12 il server sarà spento.\n"
    "2     03/10 18:42  info  3/3       Il servizio web riparte tra 5 minuti.\n"
    "3     03/10 19:05  ack   17/24     Da lunedì 15 ottobre le password scadono ogni 90 giorni.\n"
    "4     04/10 09:10  ack   0/5       [ritirato] Riunione spostata alle 11.\n"
    "5     04/10 09:30  ack   3/8       [scaduto] Consegna dei progetti entro giovedì alle 18.") + \
    table(["Colonna", "Significato"], [
        ["ID", "il numero del messaggio, da usare con " + c("ams status") + " e " + c("ams revoke")],
        ["DATA", "giorno e ora dell'invio"],
        ["LIV.", c("ack") + " (con conferma) o " + c("info") + " (solo avviso)"],
        ["CONFERME", "per " + c("ack") + ": chi ha confermato sul totale; per " + c("info") + ": a chi è stato mostrato"],
        ["TESTO", "la prima riga; " + c("[ritirato]") + " e " + c("[scaduto]") + " segnalano i messaggi non più mostrati"],
    ], "«TAB» — Le colonne di ams list")

S2 = p(c("ams status") + " seguito dal numero mostra il testo del messaggio e la situazione di ogni destinatario.",
       lead=True) + term(
    "admin@server:~$ ams status 3\n"
    "Messaggio 3 · ack · Nuova regola per le password · 03/10 19:05 · da admin\n"
    "  │ Da lunedì 15 ottobre le password scadono ogni 90 giorni.\n"
    "  │ Al primo accesso dopo la scadenza il sistema chiederà di cambiarla.\n"
    "\n"
    "UTENTE           STATO\n"
    "anna             confermato il 03/10 19:06 (desktop)\n"
    "luca             confermato il 03/10 19:20 (terminale pts/2)\n"
    "mario            da confermare (scritto su 1 terminale)\n"
    "paolo            da confermare") + table(["Stato", "Cosa vuol dire"], [
        [pill("confermato il … (desktop)", "ok"), "ha premuto «Ho letto» nella finestra"],
        [pill("confermato il … (terminale pts/2)", "ok"), "ha risposto «s» in una finestra di terminale (" + c("tty3")
         + " se era la console)"],
        [pill("da confermare (scritto su 1 terminale)", "wait"), "era collegato: il testo gli è comparso, ma non ha ancora confermato"],
        [pill("da confermare", "wait"), "non l'ha ancora visto, oppure l'ha rimandato; se non era collegato, lo vedrà al prossimo accesso"],
        [pill("mostrato", "info"), "solo per " + c("info") + ": l'avviso gli è stato mostrato"],
        [pill("non ancora mostrato", "info"), "solo per " + c("info") + ": non l'ha ancora visto"],
        [pill("non confermato", "off"), "il messaggio è scaduto o è stato ritirato prima della conferma"],
    ], "«TAB» — Gli stati di un destinatario")

LIFE = fig(
    box(20, 128, 150, 64, "Inviato", "ams send", "dark")
    + box(214, 128, 170, 64, "Da confermare", "aspetta l'utente", "light")
    + box(430, 128, 176, 64, "Mostrato", "finestra o domanda", "blue")
    + box(700, 128, 180, 64, "Confermato ✓", "«Ho letto» o «s»", "green")
    + box(430, 262, 176, 64, "Rimandato", "«Più tardi» o «no»", "amber")
    + box(214, 20, 170, 54, "Scaduto", "--expires", "grey")
    + box(430, 20, 176, 54, "Ritirato", "ams revoke", "grey")
    + arrow(172, 160, 212, 160) + arrow(386, 160, 428, 160, "#0050C0", False, "l'utente c'è", 407, 150)
    + arrow(608, 160, 698, 160, "#16a34a", False, "conferma", 652, 150)
    + path([(500, 194), (500, 260)], "#d97706") + text(478, 232, "rimanda", 11, "#92400e", "600", "end")
    + path([(540, 260), (540, 194)], "#475569", True) + text(552, 232, "dopo 30 minuti", 11, "#334155", "600", "start")
    + path([(299, 126), (299, 76)], "#94a3b8", True)
    + path([(330, 126), (330, 100), (518, 100), (518, 76)], "#94a3b8", True),
    900, 344, "«FIG» — La vita di un messaggio con conferma, per ogni destinatario", "Da confermare a confermato")

S3 = p("Per ogni destinatario un messaggio " + c("ack") + " passa per pochi stati. Finché non è confermato, "
       "scaduto o ritirato, AMS continua a riproporlo.", lead=True) + LIFE + ul([
        pill("Da confermare", "wait") + ": il messaggio aspetta nella casella dell'utente.",
        pill("Rimandato", "snooze") + ": l'utente ha premuto «Più tardi» o risposto «no»; dopo 30 minuti glielo si "
        "ripropone (il tempo si cambia nelle impostazioni, capitolo 8).",
        pill("Confermato", "ok") + ": fine. La conferma vale per tutte le sessioni dell'utente.",
        pill("Scaduto", "off") + " o " + pill("Ritirato", "off") + ": il messaggio non viene più mostrato.",
    ])

S4 = p(c("ams revoke") + " ritira un messaggio mandato per errore o non più valido.", lead=True) + term(
    "admin@server:~$ ams revoke 4\n"
    "Messaggio 4 ritirato.") + ul([
        "Chi non l'ha ancora visto non lo vedrà più.",
        "Una finestra di conferma ancora aperta si chiude da sola; una domanda in attesa nel terminale si interrompe "
        "con «L'amministratore ha ritirato il messaggio».",
        "Le conferme già arrivate restano, e " + c("ams status") + " le mostra con l'indicazione RITIRATO.",
    ]) + warn("il testo già comparso nei terminali al momento dell'invio non si può cancellare: è già sullo schermo "
              "dell'utente.")

S5 = p("Ogni invio, conferma, avviso mostrato e ritiro viene scritto nel registro di sistema, con l'etichetta "
       + c("ams") + ". È la traccia da usare se qualcuno chiede «chi ha mandato cosa, e quando».", lead=True) + term(
    "admin@server:~$ sudo journalctl -t ams --since today\n"
    "ott 03 19:05:12 server ams[21044]: messaggio 3 (ack) inviato da admin a: anna luca mario paolo\n"
    "ott 03 19:06:40 server ams[21310]: utente anna: confermata la lettura del messaggio 3 (desktop)\n"
    "ott 03 19:20:02 server ams[22187]: utente luca: confermata la lettura del messaggio 3 (terminale pts/2)") + \
    table(["Riga del registro", "Quando compare"], [
        [c("messaggio N (livello) inviato da X a: …"), "a ogni " + c("ams send")],
        [c("utente U: confermata la lettura del messaggio N (canale)"), "alla conferma"],
        [c("utente U: mostrato il messaggio informativo N (…)"), "quando un avviso " + c("info") + " viene mostrato"],
        [c("messaggio N ritirato da X"), "a ogni " + c("ams revoke")],
    ], "«TAB» — Le righe che AMS scrive nel registro")

CHAPTER = ("Controllare chi ha letto", [
    ("L'elenco dei messaggi", S1),
    ("La situazione di ogni utente", S2),
    ("La vita di un messaggio", S3),
    ("Ritirare un messaggio", S4),
    ("Il registro di sistema", S5),
])
