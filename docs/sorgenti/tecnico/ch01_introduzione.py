from build import arrow, box, c, dl, fig, note, p, path, table, text, zone


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


OVERVIEW = fig(
    zone(20, 44, 250, 262, "Amministratore · root")
    + box(44, 78, 202, 58, "ams", "comando in C, via sudo", "navy")
    + box(44, 150, 202, 50, "TUI · guida", "ams da solo · ams --help", "soft")
    + box(44, 214, 202, 50, "journal", "eventi AMS_*", "soft")
    + zone(318, 44, 240, 262, "Archivio · /var/lib/ams")
    + box(340, 78, 196, 58, "sent/ID/", "copia di riferimento · root", "dark")
    + box(340, 184, 196, 58, "users/U/", "casella di U · di U", "blue")
    + zone(606, 44, 274, 262, "Utente · U")
    + box(628, 78, 230, 58, "ams-user prompt", "aggancio della shell", "light")
    + box(628, 184, 230, 58, "ams-user agent", "avvio automatico del desktop", "light")
    + text(743, 280, "terminali /dev/pts/N · finestra zenity", 11, "#475569")
    + arrow(248, 104, 338, 104)
    + path([(248, 124), (294, 124), (294, 212), (338, 212)], "#0050C0", False, "come U", 300, 170)
    + arrow(538, 202, 626, 110, "#16a34a", True)
    + arrow(538, 214, 626, 214, "#16a34a", True)
    + text(582, 250, "legge, conferma", 11, "#166534", "600"),
    900, 326, "«FIG» — I tre ambiti di AMS: il comando di root, l'archivio, l'aiutante che gira come utente",
    "AMS in una figura")

S1 = p("<b>AMS — Advanced Messaging System for linux</b> è lo strumento con cui gli amministratori di una macchina "
       "Linux mandano messaggi di testo agli utenti e sanno chi ha confermato di averli letti. Risponde a una domanda "
       "che gli strumenti del sistema lasciano aperta: <b>«chi non ha ancora letto?»</b>", lead=True) + \
    p(c("wall") + " e " + c("write") + " scrivono sui terminali dei collegati senza tenere traccia di nulla; "
      + c("notify-send") + " mostra una notifica che può sparire; il " + c("motd") + " e i banner di accesso sono "
      "testi fissi. Nessuno di questi tiene uno <b>stato per messaggio e per utente</b>. AMS mette insieme i pezzi "
      "(logind, i terminali, l'avvio automatico del desktop, zenity, il journal) e aggiunge proprio questo stato.") + \
    OVERVIEW + \
    p("La versione 0.2.0 è scritta in C (il prototipo 0.1.0 era in bash): due programmi, nessun demone, nessun "
      "database. Il comando " + c("ams") + " gira sempre come root e scrive nell'archivio; dalla parte dell'utente "
      "l'aiutante " + c("ams-user") + " legge la casella e registra la conferma, in due modi: nel prompt della shell "
      "(" + c("ams-user prompt") + ") e nella sessione grafica (" + c("ams-user agent") + ").") + \
    note("questo manuale descrive <b>come</b> AMS funziona. Il <b>contratto</b> che ogni versione deve rispettare "
         "(stati, invarianti, interruzioni, formato dell'archivio) è il " + cap(20) + ", «Specifica»; il manuale "
         "utente spiega l'uso, senza gergo tecnico.")

STATI = fig(
    box(40, 60, 200, 60, "inviato", "nessuna copia nella casella", "light")
    + box(350, 60, 200, 60, "consegnato", "copia in users/U/inbox", "blue")
    + box(660, 60, 200, 60, "confermato", "dichiarazione in acks/ID", "green")
    + arrow(242, 90, 348, 90, "#0050C0", False, "copia verificata", 295, 80)
    + arrow(552, 90, 658, 90, "#16a34a", False, "«Ho letto» o «s»", 605, 80)
    + box(250, 160, 400, 46, "proprietà del messaggio: ritirato · scaduto", "", "soft", 12)
    + text(450, 232, "un messaggio si riassume contando i destinatari nei tre stati", 11.5, "#475569", "600"),
    900, 250, "«FIG» — I tre stati di un destinatario; ritiro e scadenza sono proprietà del messaggio",
    "Tre stati, due proprietà")

S2 = p("Pochi concetti bastano a leggere il resto del manuale. Sono gli stessi nel codice, nelle prove e nei "
       "manuali.", lead=True) + dl([
    ("Messaggio", "un testo (al più 65536 byte) con un titolo facoltativo e una scadenza facoltativa, identificato "
     "da un numero progressivo, l'<b>ID</b>. Chi lo manda è l'amministratore che ha lanciato " + c("ams") + "."),
    ("Destinatario", "un utente umano della macchina a cui il messaggio è indirizzato: per nome, per gruppo "
     "(" + c("@gruppo") + "), tutti (" + c("all") + ") o i collegati (" + c("online") + ")."),
    ("Copia di riferimento", "il messaggio in " + c("/var/lib/ams/sent/ID/") + ", leggibile solo da root: ciò che è "
     "stato inviato, a chi, quando, con quale scadenza. È la fonte autorevole."),
    ("Casella", "la cartella " + c("/var/lib/ams/users/U/") + " di un utente: una copia di lavoro che l'utente "
     "controlla, con le sottocartelle " + c("inbox") + ", " + c("read") + ", " + c("acks") + " e " + c("state") + "."),
    ("Canale", "da dove l'utente vede il messaggio e conferma: un terminale (" + c("terminale pts/N") + ", "
     + c("terminale tty3") + ") o il desktop (" + c("desktop") + ")."),
    ("Conferma", "la dichiarazione di lettura dell'utente, scritta nella sua casella in " + c("acks/ID")
     + " con data e canale. Vale la prima."),
    ("Rinvio", "la risposta «no» nel terminale o «Più tardi» sul desktop: la domanda torna dopo "
     + c("AMS_REMIND_MINUTES") + " minuti, o al login successivo."),
    ("Stato", "per ogni destinatario <b>uno solo di tre</b>: inviato, consegnato, confermato. Ritirato e scaduto "
     "sono proprietà del messaggio, non stati."),
]) + STATI

MODULI = fig(
    zone(20, 40, 430, 146, "ams (root)")
    + box(40, 74, 124, 44, "ams.c", "comandi, recupero", "navy", 12)
    + box(174, 74, 124, 44, "tui.c", "la TUI", "navy", 12)
    + box(308, 74, 124, 44, "guida.c", "ams --help", "navy", 12)
    + box(40, 128, 190, 44, "archivio.c", "caselle, terminali", "blue", 12)
    + box(242, 128, 190, 44, "ams.h", "parti usate dalla TUI", "soft", 12)
    + zone(470, 40, 410, 146, "ams-user (utente)")
    + box(490, 74, 370, 44, "ams-user.c", "prompt · agent · conferma", "light", 12)
    + text(675, 150, "nessun modulo proprio oltre a questo", 11, "#475569")
    + zone(20, 200, 860, 100, "Parti comuni, collegate in entrambi i programmi")
    + box(40, 236, 124, 44, "comune.c", "file, memoria", "dark", 12)
    + box(178, 236, 124, 44, "testo.c", "pulizia, formato", "dark", 12)
    + box(316, 236, 124, 44, "lingua.c", "cataloghi .mo", "dark", 12)
    + box(454, 236, 124, 44, "evento.c", "journal", "dark", 12)
    + box(592, 236, 124, 44, "utente.c", "come_utente", "dark", 12)
    + box(730, 236, 130, 44, "sessioni.c", "logind", "dark", 12),
    900, 316, "«FIG» — I moduli di src/ e il programma in cui entrano (Makefile)", "I moduli")

S3 = p("Il codice sta in " + c("src/") + " ed è organizzato in moduli piccoli con responsabilità nette. Questa è la "
       "mappa che il manuale approfondisce capitolo per capitolo.", lead=True) + MODULI + dl([
    (c("ams.c"), "il comando degli amministratori: rilancio con sudo, " + c("send") + ", " + c("list") + ", "
     + c("status") + ", " + c("revoke") + ", " + c("remind") + ", " + c("log") + ", " + c("purge")
     + ", recupero degli invii interrotti (" + cap(4) + ", " + cap(8) + ", " + cap(9) + ", " + cap(10) + ")."),
    (c("ams-user.c"), "l'aiutante che gira come utente: la domanda al prompt, l'agente del desktop, la "
     "registrazione della conferma (" + cap(11) + ", " + cap(12) + ", " + cap(13) + ")."),
    (c("archivio.c"), "le operazioni sulle caselle, sempre con l'identità dell'utente; la scrittura nei terminali; "
     "la sveglia dell'agente (" + cap(7) + ", " + cap(8) + ")."),
    (c("utente.c"), c("come_utente") + ": un processo figlio con l'identità di un utente e un tempo massimo "
     "(" + cap(7) + ")."),
    (c("sessioni.c"), "utenti umani, gruppi, sessioni e terminali, da passwd e da logind (" + cap(6) + ")."),
    (c("testo.c"), "pulizia del testo, formato dei messaggi, configurazione (" + cap(5) + ", " + cap(4) + ")."),
    (c("lingua.c"), "scelta della lingua e lettore dei cataloghi " + c(".mo") + " (" + cap(16) + ")."),
    (c("evento.c"), "gli eventi strutturati nel journal e il loro testo in ogni lingua (" + cap(18) + ")."),
    (c("tui.c"), "la TUI per gli amministratori (" + cap(14) + ")."),
    (c("guida.c"), "la guida integrata di " + c("ams --help") + " (" + cap(15) + ")."),
    (c("comune.c"), "ambiente, errori, memoria, testi che crescono, lettura e scrittura sicura dei file "
     "(" + cap(5, 5) + ", " + cap(19) + ")."),
])

S4 = table(["Se la domanda è…", "Dove"], [
    ["Che cosa deve essere sempre vero, qualunque cosa succeda?", cap(20) + " · Specifica"],
    ["Com'è fatto l'archivio e chi può scriverci?", cap(5) + " e " + cap(17)],
    ["Che cosa succede, passo per passo, durante un invio?", cap(8)],
    ["Perché root non scrive mai direttamente nelle caselle?", cap(7)],
    ["Come arriva la domanda nel terminale, e sul desktop?", cap(11) + " e " + cap(12)],
    ["Che cosa vuol dire, esattamente, «confermato»?", cap(13) + " e " + cap(20, 1)],
    ["Com'è fatta la TUI, e perché non ha stati suoi?", cap(14)],
    ["Dove si vede la storia di un messaggio?", cap(18)],
    ["Quali errori può dare AMS, e che cosa vogliono dire?", cap(19)],
    ["Come si prova una modifica, e con quali risultati?", cap(3, 5) + " e " + cap(21)],
    ["Quali difetti sono già stati trovati e corretti?", cap(22)],
], "«TAB» — Dove trovare le risposte")

CHAPTER = ("Introduzione e concetti", [
    ("Che cos'è AMS", S1),
    ("I concetti di base", S2),
    ("Sottosistemi in breve", S3),
    ("Come leggere questo manuale", S4),
])
