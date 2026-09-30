from build import arrow, box, c, code, diamond, fig, flow, note, p, path, seq, table, term, text, ul, warn


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


RITIRO = seq([("ams revoke", "root", "navy"), ("sent/ID", "archivio", "dark"), ("ams send", "in corso", "light"),
              ("Casella U", "users/U", "blue"), ("Domanda, finestra", "di U", "soft")], [
    (0, 1, "segno ritiro"),
    (0, 1, "revoked ← data (su disco)"),
    ("nota", 0, "evento RITIRATO"),
    (0, 1, "flock(lock): attende", True),
    (2, 1, "revoked? sì: si ferma"),
    (2, 1, "rilascia il lock", True),
    (0, 3, "come U: via inbox/ID, rinvii"),
    (0, 1, "via il segno ritiro"),
    (4, 3, "inbox/ID sparito?"),
    ("nota", 4, "si chiudono entro 1 s"),
], "«FIG» — Un ritiro durante un invio in corso", "ams revoke", width=920)

S1 = p(c("ams revoke ID") + " ritira un messaggio: chi non l'ha ancora visto non lo vedrà, domande e finestre "
       "aperte si chiudono da sole. Il ritiro <b>avviene</b> nell'istante in cui compare " + c("sent/ID/revoked")
       + ": da lì nessuna nuova consegna, e nessuna conferma con data successiva vale.", lead=True) + RITIRO + \
    table(["Passo", "Che cosa", "Perché"], [
        ["1", "segno " + c("sent/ID/ritiro"), "se il comando si interrompe, il recupero sa che ci sono copie da "
         "togliere"],
        ["2", c("sent/ID/revoked") + " con la data, scritto con " + c("scrivi_atomico") + "; " + c("fsync")
         + " di " + c("ritiro") + " e della cartella; evento " + c("RITIRATO"), "il ritiro è su disco prima di "
         "toccare le caselle; un secondo ritiro dello stesso messaggio non riscrive la data né l'evento"],
        ["3", c("flock") + " su " + c("sent/ID/lock") + ", <b>bloccante</b>", "aspetta un " + c("ams send")
         + " in corso, che controlla " + c("revoked") + " prima di ogni destinatario e si ferma"],
        ["4", "per ogni destinatario, come l'utente: via " + c("inbox/ID") + ", " + c("state/ID.term") + ", "
         + c("state/ID.gui"), "le copie già lette o confermate (" + c("read/") + ", " + c("acks/")
         + ") restano: sono la storia"],
        ["5", "tutte tolte: via " + c("ritiro") + "; «Messaggio N ritirato.»", "altrimenti " + c("die")
         + ": «alcune copie non si sono potute togliere…», e il recupero riprova"],
    ], "«TAB» — I passi del ritiro") + ul([
    "Il ritiro serializzato con l'invio nasce dalla seconda revisione: prima una copia poteva arrivare dopo il "
    "ritiro. " + c("tests/engine.sh") + " (gruppo 9) verifica che " + c("ams revoke") + " aspetti un lock tenuto "
    "per 2 secondi; lo scenario F7 ritira un invio a molti utenti mentre è in corso, senza che resti alcuna copia.",
    "Se il ritiro arriva durante l'invio, " + c("ams send") + " termina con «Messaggio N ritirato durante l'invio: "
    "consegna interrotta.»: i destinatari non ancora raggiunti restano «inviato».",
    "La domanda nel terminale e la finestra controllano " + c("inbox/ID") + " ogni secondo e si chiudono (scenari "
    "E3 e I6); una conferma arrivata fra il loro ultimo controllo e il ritiro non conta, perché la sua data è "
    "successiva a " + c("revoked") + " (" + cap(13, 1) + ").",
])

SOLL = fig(
    box(20, 70, 160, 56, "ams remind ID", "o il tasto s nella TUI", "navy")
    + diamond(300, 98, 200, 64, "ritirato o scaduto?", "amber")
    + box(210, 170, 180, 48, "die", "nessuno da sollecitare", "grey", 12)
    + box(420, 70, 170, 56, "destinatari()", "stato di ciascuno", "dark")
    + box(630, 20, 250, 50, "consegnato", "via state/ID.* come U, sveglia", "blue", 12)
    + box(630, 90, 250, 50, "inviato", "nulla: non ha la copia", "soft", 12)
    + box(630, 160, 250, 50, "confermato", "nulla", "soft", 12)
    + arrow(182, 98, 198, 98) + arrow(300, 132, 300, 168, "#475569", False, "sì", 314, 152)
    + arrow(402, 98, 418, 98, "#0050C0", False, "no", 410, 88)
    + arrow(592, 90, 628, 45) + arrow(592, 98, 628, 115) + arrow(592, 106, 628, 185)
    + text(450, 250, "evento SOLLECITATO con il numero dei sollecitati e l'autore", 11.5, "#475569", "600"),
    900, 266, "«FIG» — ams remind: solo chi ha la copia e non ha confermato", "Il sollecito")

S2 = p(c("ams remind ID") + " fa tornare subito la domanda a chi non ha ancora confermato, anche se aveva "
       "rimandato. Non riscrive nulla: toglie i rinvii e sveglia l'agente.", lead=True) + SOLL + ul([
    "Un messaggio ritirato o scaduto non si sollecita: «il messaggio N è stato ritirato: nessuno da sollecitare» "
    "(" + c("tests/engine.sh") + ", gruppo 10).",
    "Lo stato dei destinatari viene da " + c("destinatari") + ", la stessa funzione di " + c("ams status")
    + ": si sollecita chi è <b>consegnato</b>. Chi è inviato non ha la copia (lo completerà il recupero), chi ha "
    "confermato non va disturbato («sollecitati 0 destinatari»).",
    "Per ciascuno, come l'utente, si tolgono " + c("state/ID.term") + " e " + c("state/ID.gui") + "; poi "
    + c("sveglia_agente") + ". La domanda torna al prompt successivo (scenario D5); la finestra ricompare subito "
    "(scenario I11: 0,37 s nell'ultima esecuzione registrata).",
    "Il sollecito non prende lock: con una conferma arrivata nel frattempo, togliere i rinvii di chi ha confermato "
    "non ha effetto (" + cap(20, 4) + ").",
]) + term("admin@server:~$ sudo ams remind 12\nMessaggio 12: sollecitati 3 destinatari.", "Un sollecito") + \
    note("prima del sollecito la VM di prova ha trovato un caso limite: un " + c("ams remind") + " arrivato entro "
         "un secondo da «Più tardi» andava perso, perché l'agente registrava il rinvio al giro successivo. Ora "
         "l'agente registra la risposta appena zenity si chiude (" + cap(12, 3) + ").")

PURGE = flow([("Durata", "90d, 12h, 30m", "dark"), ("Più vecchio?", "data dell'invio", "navy"),
              ("Lock libero?", "e non incompleto", "navy"), ("Rinomina", "sent/.cancella-ID", "amber"),
              ("Caselle", "come ogni utente", "blue"), ("Cartella", "file e rmdir", "green")],
             "«FIG» — ams purge: il messaggio sparisce con una rinomina, poi si puliscono le caselle")

S3 = p(c("ams purge DURATA") + " cancella i messaggi inviati prima di " + c("DURATA") + " fa, con le copie, le "
       "conferme e i rinvii nelle caselle. Gli eventi restano nel journal.", lead=True) + PURGE + table(
    ["Passo", "Che cosa"], [
        ["durata", "un numero seguito da " + c("m") + ", " + c("h") + " o " + c("d") + "; altrimenti «durata non "
         "valida: 7x (per esempio 90d, 12h, 30m)»"],
        ["scelta", "per ogni messaggio: la data d'invio da " + c("msg") + " (o, se il file non si legge, la data di "
         "modifica della cartella); si salta un messaggio con " + c("incomplete")],
        ["lock", c("flock") + " non bloccante su " + c("sent/ID/lock") + ": un invio in corso si salta"],
        ["rinomina", c("sent/ID") + " → " + c("sent/.cancella-ID") + ", " + c("fsync") + " di " + c("sent/")
         + ", lock rilasciato, evento " + c("CANCELLATO") + " con durata e autore"],
        ["caselle", "per ogni destinatario, come l'utente: via " + c("inbox/ID") + ", " + c("read/ID") + ", "
         + c("acks/ID") + " e i rinvii"],
        ["cartella", "via i file di " + c("sent/.cancella-ID/") + " e la cartella stessa"],
    ], "«TAB» — I passi della cancellazione") + ul([
    "La rinomina è il punto in cui il messaggio smette di esistere per tutti i comandi: " + c("elenca_numeri")
    + " vede solo nomi fatti di cifre. " + c("ams list") + " legge ciò che gli serve di ogni messaggio prima di "
    "usarlo e salta un messaggio sparito nel frattempo (" + c("riassumi") + " restituisce falso).",
    "Una cancellazione interrotta dopo la rinomina la completa il recupero del comando successivo ("
    + c("tests/engine.sh") + ", gruppo 9).",
    c("ams purge") + " non esegue il recupero prima di sé: gli invii incompleti li salta comunque.",
]) + term("admin@server:~$ sudo ams purge 90d\nCancellati 4 messaggi più vecchi di 90d.", "Una pulizia") + \
    warn("dopo la cancellazione i numeri dei messaggi non si riusano (la sequenza " + c(".seq") + " resta), ma "
         + c("ams log") + " di un numero cancellato non trova più il messaggio: la sua storia resta leggibile "
         "solo con " + c("journalctl AMS_MESSAGGIO=ID") + ".")

CHAPTER = ("Ritiro, sollecito e cancellazione", [
    ("Il ritiro: ams revoke", S1),
    ("Il sollecito: ams remind", S2),
    ("La cancellazione: ams purge", S3),
])
