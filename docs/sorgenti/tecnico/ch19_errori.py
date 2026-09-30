from build import arrow, box, c, code, fig, note, p, path, table, term, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


TIPI = fig(
    box(20, 40, 200, 60, "controlli iniziali", "opzioni, testo, destinatari", "dark")
    + box(20, 130, 200, 60, "guasti durante il lavoro", "una casella, un terminale", "dark")
    + box(20, 220, 200, 60, "interruzioni", "segnale, corrente, SIGKILL", "dark")
    + box(300, 40, 220, 60, "die", "«ams: …», uscita 1, nulla scritto", "amber")
    + box(300, 130, 220, 60, "evento + si prosegue", "NON_CONSEGNATO, poi die", "amber")
    + box(300, 220, 220, 60, "segni nell'archivio", "incomplete, ritiro, .cancella", "amber")
    + box(600, 40, 280, 60, "l'amministratore corregge", "e rilancia il comando", "light")
    + box(600, 130, 280, 60, "il comando successivo riprova", "recupero, " + "avviso su stderr", "green")
    + box(600, 220, 280, 60, "il comando successivo ripara", "recupera(), idempotente", "green")
    + arrow(222, 70, 298, 70) + arrow(222, 160, 298, 160) + arrow(222, 250, 298, 250)
    + arrow(522, 70, 598, 70) + arrow(522, 160, 598, 160) + arrow(522, 250, 598, 250),
    900, 300, "«FIG» — Tre famiglie di errori e chi le ripara", "Come fallisce AMS")

S1 = p("AMS distingue tre famiglie di errori. Quelli che si possono scoprire prima di scrivere fermano il comando "
       "senza lasciare tracce; quelli che capitano durante il lavoro non fermano gli altri destinatari e lasciano "
       "un segno; le interruzioni lasciano uno stato che il comando successivo sa riparare.", lead=True) + TIPI + \
    table(["Funzione (src/comune.c)", "Che cosa fa", "Chi la usa"], [
        [c("die(fmt, …)"), "svuota stdout, scrive «" + c("ams: ") + "…» (o «" + c("ams-user: ") + "…») su stderr, "
         "esce con 1", c("ams") + ": ogni errore che ferma il comando"],
        [c("avviso(fmt, …)"), "come " + c("die") + ", ma il programma continua", "il recupero, per dire che cosa ha "
         "completato o annullato"],
        [c("xmalloc") + ", " + c("xrealloc") + ", " + c("xasprintf"), "se la memoria finisce: «memoria esaurita» e "
         "uscita 1", "tutti"],
    ], "«TAB» — Come si segnala un errore") + ul([
    "I messaggi d'errore sono tradotti come ogni altro testo, tranne «memoria esaurita» e «formato non valido», "
    "scritti in italiano nel codice.",
    c("ams-user") + " non usa " + c("die") + " nel lavoro normale: gira dentro il prompt o nella sessione grafica, e "
    "ogni suo problema diventa «non fare nulla» o un avviso all'utente (" + cap(11, 3) + ").",
    "Nella TUI un " + c("die") + " del comando chiude solo il processo figlio: il suo messaggio compare nella "
    "finestra d'esito (" + cap(14, 1) + ").",
])

S2 = table(["Messaggio (italiano)", "Quando", "Che cosa resta"], [
    ["comando sconosciuto: X (ams --help per la guida)", "primo argomento non riconosciuto", "nulla"],
    ["manca --to · manca il valore di --title · opzione sconosciuta: --level", "opzioni di " + c("send"), "nulla"],
    ["scadenza non valida: X · la scadenza è già passata", c("--expires") + " non interpretabile, o nel passato",
     "nulla"],
    ["FILE: seguito dalla spiegazione del sistema", c("--file") + " non leggibile", "nulla"],
    ["messaggio vuoto · messaggio troppo lungo: N byte (al massimo 65536)", "testo dopo la pulizia", "nulla"],
    ["utente inesistente: X · gruppo inesistente: X · nessun destinatario", c("--to"), "nulla"],
    ["Messaggio N consegnato a K destinatari su M. · messaggio N non consegnato a: … (vedi il registro; il prossimo "
     "comando ams riproverà)", "qualche copia non scritta", c("incomplete") + ": il recupero riprova"],
    ["manca l'ID del messaggio · messaggio inesistente: X", c("status") + ", " + c("revoke") + ", " + c("remind")
     + ", " + c("log"), "nulla"],
    ["il messaggio N è stato annullato: l'invio si era interrotto prima del salvataggio", c("status")
     + " di un invio annullato", "—"],
    ["messaggio N ritirato, ma alcune copie non si sono potute togliere dalle caselle: il prossimo comando ams "
     "riproverà", c("revoke"), c("revoked") + " e " + c("ritiro") + ": il recupero riprova"],
    ["il messaggio N è stato ritirato: nessuno da sollecitare · il messaggio N è scaduto: nessuno da sollecitare",
     c("remind"), "nulla"],
    ["manca la durata, per esempio 90d · durata non valida: X (per esempio 90d, 12h, 30m)", c("purge"), "nulla"],
    [c("/var/lib/ams: …") + " · " + c("…/sent/.seq.lock: …") + " · " + c("sudo: …"), "l'archivio non si crea, il "
     "lock non si prende, sudo non si avvia (messaggi del sistema)", "nulla, o un numero saltato"],
], "«TAB» — Gli errori di ams") + term("admin@server:~$ sudo ams send --to pippo \"Prova\"\n"
                                       "ams: utente inesistente: pippo\n"
                                       "admin@server:~$ sudo ams purge 7x\n"
                                       "ams: durata non valida: 7x (per esempio 90d, 12h, 30m)",
                                       "Due errori, e nulla è stato scritto")

S3 = p("Dentro AMS le funzioni si parlano con esiti numerici. Sono il contratto fra le parti, e i capitoli che "
       "le descrivono li usano con questi valori.", lead=True) + table(["Funzione", "Esiti"], [
    [c("conferma") + " (" + c("ams-user") + ")", "0 registrata o già presente · 1 non registrata, il messaggio resta "
     "· 2 scaduto · 3 ritirato (" + cap(13, 1) + ")"],
    [c("chiedi") + " (" + c("ams-user") + ")", "0 sì · 1 no, o nessuna risposta · 2 confermato altrove · 3 ritirato "
     "· 4 scaduto mentre la domanda era aperta (" + cap(11, 3) + ")"],
    ["zenity", "0 «Ho letto» · 1 «Più tardi» o finestra chiusa dall'utente · altro: non una scelta (" + cap(12, 3)
     + ")"],
    [c("come_utente"), "il codice di " + c("fn") + " · −1 figlio non partito, identità non assunta (126), tempo "
     "scaduto, figlio ucciso (" + cap(7, 3) + ")"],
    [c("op_consegna") + ", " + c("op_togli") + ", " + c("op_togli_rinvii"), "0 riuscita · 1 no"],
    [c("leggi_file") + ", " + c("scrivi_atomico"), "0 · −1 con " + c("errno") + " (" + c("EINVAL") + " se non è un "
     "file normale, " + c("EFBIG") + " se troppo grande)"],
    [c("msg_leggi") + ", " + c("msg_da_testo"), "0 · −1 se il file manca, non è normale, è troppo grande o non ha "
     "una data valida"],
    [c("riassumi"), "vero · falso se il messaggio non c'è più, non ha destinatari o è stato annullato"],
], "«TAB» — Gli esiti interni") + \
    note("il codice 126 è riservato: un figlio che non riesce ad assumere l'identità esce con 126, e "
         + c("come_utente") + " lo tratta come un fallimento anche se " + c("fn") + " avesse potuto restituirlo.")

S4 = table(["Avviso (stderr)", "Che cosa è successo", "Evento"], [
    ["completata la consegna del messaggio N a K destinatari", "un invio interrotto è stato completato", c("RECUPERATO")],
    ["messaggio N ancora non consegnato a K destinatari (vedi ams status N)", "il recupero non è riuscito a "
     "scrivere qualche copia; riproverà", "—"],
    ["il messaggio N era stato interrotto prima di essere salvato ed è stato annullato", "un invio senza "
     + c("msg") + " o " + c("recipients") + " è stato chiuso con " + c("failed"), c("ANNULLATO")],
], "«TAB» — Gli avvisi del recupero") + \
    p("Gli avvisi compaiono all'inizio di qualunque comando che esegue il recupero, anche di uno che non riguarda "
      "quel messaggio: " + c("ams list") + " può quindi dire «completata la consegna del messaggio 2 a 64 "
      "destinatari» (scenario F3). Il comando poi prosegue normalmente.") + table(["Codice", "Significato"], [
    ["0", "completato"],
    ["1", "errore: il messaggio, che inizia con «ams:», dice quale"],
    ["altro", "un codice di sudo, prima che " + c("ams") + " parta"],
], "«TAB» — Lo stato di uscita di ams")

CHAPTER = ("Tassonomia degli errori", [
    ("Tre famiglie di errori", S1),
    ("Gli errori di ams", S2),
    ("Gli esiti interni", S3),
    ("Avvisi del recupero e stato di uscita", S4),
])
