from build import arrow, box, c, fig, p, path, pill, table, term, text, ul, warn

S1 = p(c("ams list") + " mostra tutti i messaggi mandati, dal più vecchio al più recente.", lead=True) + term(
    "admin@server:~$ ams list\n"
    "ID    DATA         CONFERME  TESTO\n"
    "1     03/10 18:30  1/1       Sabato dalle 8 alle 12 il server sarà spento.\n"
    "2     03/10 18:42  3/3       [scaduto] Il servizio web riparte alle 13:00.\n"
    "3     03/10 19:05  17/24     Da lunedì 15 ottobre le password scadono ogni 90 giorni.\n"
    "4     04/10 09:10  0/5       [ritirato] Riunione spostata alle 11.\n"
    "5     04/10 09:30  3/8       [scaduto] Consegna dei progetti entro giovedì alle 18.") + \
    table(["Colonna", "Significato"], [
        ["ID", "il numero del messaggio, da usare con " + c("ams status") + " e " + c("ams revoke")],
        ["DATA", "giorno e ora dell'invio"],
        ["CONFERME", "chi ha confermato, sul totale dei destinatari"],
        ["TESTO", "la prima riga; " + c("[ritirato]") + " e " + c("[scaduto]") + " segnalano i messaggi non più mostrati, "
         + c("[2 non consegnati]") + " i destinatari la cui copia non è stata scritta"],
    ], "«TAB» — Le colonne di ams list")

S2 = p(c("ams status") + " seguito dal numero mostra il testo del messaggio e lo stato di ogni destinatario.",
       lead=True) + term(
    "admin@server:~$ ams status 3\n"
    "Messaggio 3 · Nuova regola per le password · 03/10 19:05 · da admin\n"
    "  │ Da lunedì 15 ottobre le password scadono ogni 90 giorni.\n"
    "  │ Al primo accesso dopo la scadenza il sistema chiederà di cambiarla.\n"
    "\n"
    "UTENTE           STATO\n"
    "anna             confermato il 03/10 19:06 (desktop)\n"
    "luca             confermato il 03/10 19:20 (terminale pts/2)\n"
    "mario            consegnato, scritto su 1 terminale, rimandato il 03/10 19:07\n"
    "paolo            consegnato\n"
    "sara             inviato, non consegnato") + table(["Stato", "Cosa vuol dire"], [
        [pill("inviato", "info"), "il messaggio è partito, ma la copia non è ancora nella casella dell'utente: di solito "
         "perché non si è potuta scrivere (per esempio disco pieno). Il prossimo comando " + c("ams") + " riprova da solo"],
        [pill("consegnato", "wait"), "la copia è nella casella: l'utente la vede subito se è collegato, altrimenti al "
         "prossimo accesso. Può essere accompagnato da dettagli: «scritto su N terminali» (era collegato all'invio), "
         "«rimandato il …» (ha premuto «Più tardi» o risposto «no»), «non confermato (scaduto)» o «(ritirato)». Una conferma "
         "data dopo la scadenza non vale: «non confermato (scaduto; conferma arrivata dopo la scadenza)»"],
        [pill("confermato", "ok"), "l'utente ha dichiarato di averlo letto: data, ora e canale (" + c("desktop")
         + ", " + c("terminale pts/2") + ", " + c("terminale tty3") + " per una console)"],
    ], "«TAB» — I tre stati di un destinatario")

LIFE = fig(
    box(20, 128, 170, 64, "Inviato", "ams send", "light")
    + box(270, 128, 190, 64, "Consegnato", "copia nella casella", "blue")
    + box(560, 128, 180, 64, "Confermato ✓", "«Ho letto» o «s»", "green")
    + box(270, 262, 190, 56, "rimandato", "riproposto dopo 30 minuti", "amber", 12)
    + box(560, 20, 150, 50, "scaduto", "--expires", "grey", 12)
    + box(730, 20, 150, 50, "ritirato", "ams revoke", "grey", 12)
    + arrow(192, 160, 268, 160, "#0050C0", False, "copia scritta", 230, 150)
    + arrow(462, 160, 558, 160, "#16a34a", False, "conferma", 510, 150)
    + path([(335, 194), (335, 260)], "#d97706") + text(322, 232, "Più tardi / no", 11, "#92400e", "600", "end")
    + path([(395, 260), (395, 194)], "#475569", True) + text(407, 232, "dopo 30 minuti", 11, "#334155", "600", "start")
    + path([(365, 126), (365, 45), (558, 45)], "#94a3b8", True)
    + path([(365, 45), (365, 10), (805, 10), (805, 18)], "#94a3b8", True),
    900, 336, "«FIG» — I tre stati di un destinatario; scadenza e ritiro fermano i solleciti", "Inviato, consegnato, confermato")

S3 = p("Ogni destinatario passa per tre stati. Finché non conferma, AMS continua a riproporgli il messaggio, a meno che "
       "il messaggio non scada o venga ritirato.", lead=True) + LIFE + ul([
        pill("Inviato", "info") + ": il messaggio è partito, la copia non è ancora nella casella.",
        pill("Consegnato", "wait") + ": la copia è nella casella; l'utente lo vede appena è collegato. Se rimanda, "
        "resta consegnato e gli viene riproposto dopo 30 minuti (il tempo si cambia nelle impostazioni, capitolo 8).",
        pill("Confermato", "ok") + ": fine. La conferma vale per tutte le sessioni dell'utente.",
        pill("Scaduto", "off") + " e " + pill("ritirato", "off") + " non sono stati dell'utente ma del messaggio: da "
        "quel momento non viene più mostrato, e chi non aveva confermato resta «consegnato, non confermato».",
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

S5 = p("Ogni invio, conferma e ritiro viene scritto nel registro di sistema, con l'etichetta "
       + c("ams") + ". È la traccia da usare se qualcuno chiede «chi ha mandato cosa, e quando».", lead=True) + term(
    "admin@server:~$ sudo journalctl -t ams --since today\n"
    "ott 03 19:05:12 server ams[21044]: messaggio 3 inviato da admin a: anna luca mario paolo\n"
    "ott 03 19:06:40 server ams[21310]: utente anna: confermata la lettura del messaggio 3 (desktop)\n"
    "ott 03 19:20:02 server ams[22187]: utente luca: confermata la lettura del messaggio 3 (terminale pts/2)") + \
    table(["Riga del registro", "Quando compare"], [
        [c("messaggio N inviato da X a: …"), "a ogni " + c("ams send")],
        [c("messaggio N consegnato a U (…)"), "per ogni copia scritta nella casella di un utente"],
        [c("utente U: rimandato il messaggio N (canale)"), "quando l'utente preme «Più tardi» o risponde «no»"],
        [c("utente U: confermata la lettura del messaggio N (canale)"), "alla conferma"],
        [c("messaggio N: ERRORE, copia per U non scritta"), "quando una consegna fallisce"],
        [c("messaggio N ritirato da X"), "a ogni " + c("ams revoke")],
    ], "«TAB» — Le righe che AMS scrive nel registro") + \
    p("Per vedere la storia completa di un solo messaggio c'è " + c("ams log") + ":") + term(
    "admin@server:~$ ams log 3\n"
    "Messaggio 3 · Nuova regola per le password · 03/10 19:05\n"
    "2026-10-03T19:05:12+0200  messaggio 3 inviato da admin a: anna luca mario paolo\n"
    "2026-10-03T19:05:12+0200  messaggio 3 consegnato a anna (terminali scritti: 0)\n"
    "2026-10-03T19:05:12+0200  messaggio 3 consegnato a luca (terminali scritti: 1)\n"
    "2026-10-03T19:06:40+0200  utente anna: confermata la lettura del messaggio 3 (desktop)\n"
    "2026-10-03T19:07:02+0200  utente mario: rimandato il messaggio 3 (terminale)\n"
    "2026-10-03T19:20:02+0200  utente luca: confermata la lettura del messaggio 3 (terminale pts/2)")

S6 = p("I messaggi e le conferme restano nell'archivio finché non vengono cancellati. " + c("ams purge")
       + " toglie quelli più vecchi di un certo tempo, con le copie e le conferme nelle caselle degli utenti.", lead=True) + \
    term("admin@server:~$ ams purge 90d\nCancellati 12 messaggi più vecchi di 90d.") + ul([
        "La durata si scrive come per la scadenza: " + c("90d") + ", " + c("12h") + ", " + c("30m") + ".",
        "Un messaggio cancellato sparisce da " + c("ams list") + " e da " + c("ams status") + "; se qualcuno non l'aveva "
        "ancora confermato, non gli verrà più chiesto.",
        "Un invio ancora in corso o rimasto a metà non viene toccato.",
        "Nel registro di sistema restano gli eventi del messaggio e quello della cancellazione.",
    ])

CHAPTER = ("Controllare chi ha letto", [
    ("L'elenco dei messaggi", S1),
    ("La situazione di ogni utente", S2),
    ("La vita di un messaggio", S3),
    ("Ritirare un messaggio", S4),
    ("Il registro di sistema", S5),
    ("Fare pulizia", S6),
])
