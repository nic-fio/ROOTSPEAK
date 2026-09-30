from build import arrow, box, c, fig, note, p, path, table, text, ul

S1 = p("Questo capitolo è il contratto di AMS: ciò che qualunque implementazione deve rispettare, indipendentemente da "
       "come è scritta. Il resto del manuale descrive come la versione in bash lo realizza; una seconda "
       "implementazione, per esempio compilata, dovrebbe poter lavorare sullo stesso archivio e dare gli stessi esiti.",
       lead=True) + table(["Fonte", "Autorità", "Chi la scrive"], [
    [c("sent/ID/") + " (msg, recipients, delivery, revoked, incomplete, failed, lock)", "<b>autorevole</b>: cosa è "
     "stato inviato, a chi, quando, con quale scadenza, a chi è stato consegnato", "solo root"],
    [c("users/U/") + " (inbox, read, acks, state)", "<b>copia di lavoro</b>, controllata dall'utente: può essere "
     "cancellata o alterata, e il sistema deve restare coerente", "l'utente (e root, come l'utente)"],
    ["journal (" + c("SYSLOG_IDENTIFIER=ams") + ")", "<b>storia</b>: eventi con data, e " + c("_UID")
     + " di chi li ha scritti, non falsificabile", "root e l'utente"],
], "«TAB» — Le fonti di verità") + ul([
    "Una conferma è un fatto dichiarato dall'utente nella propria casella; vale solo se non contraddice "
    "la copia di riferimento: la sua data deve precedere la scadenza scritta in " + c("sent/ID/msg") + ".",
    "Se l'utente cancella la propria copia, il messaggio risulta semplicemente non confermato; se la altera (testo, "
    "scadenza), cambia solo ciò che vede lui.",
])

STATI = fig(
    box(20, 130, 180, 64, "INVIATO", "in recipients, non in delivery", "light")
    + box(290, 130, 230, 64, "CONSEGNATO", "riga in delivery, nessuna conferma valida", "blue")
    + box(640, 130, 240, 64, "CONFERMATO", "acks/ID con data ≤ scadenza", "green")
    + arrow(202, 162, 288, 162, "#0050C0", False, "copia verificata", 245, 152)
    + arrow(522, 162, 638, 162, "#16a34a", False, "conferma", 580, 152)
    + text(580, 212, "(non scaduto, non ritirato)", 11, "#166534", "600")
    + path([(365, 196), (365, 232), (445, 232), (445, 196)], "#d97706")
    + text(405, 252, "rinvio: state/ID.*", 11, "#92400e", "600")
    + box(560, 20, 320, 48, "Proprietà del messaggio", "RITIRATO · SCADUTO · INCOMPLETO", "soft", 12)
    + text(560, 90, "ANNULLATO: invio interrotto prima del salvataggio", 11, "#475569", "400", "start")
    + text(560, 106, "CANCELLATO: ams purge", 11, "#475569", "400", "start"),
    900, 272, "«FIG» — Gli stati di un destinatario e le proprietà di un messaggio", "La macchina a stati")

S2 = p("Ogni destinatario di un messaggio è in uno di tre stati; lo stato si deduce dai file, secondo regole fisse. "
       "Ritiro, scadenza e interruzione dell'invio sono proprietà del messaggio, non stati del destinatario.",
       lead=True) + STATI + table(["Transizione", "Precondizione", "Operazione atomica", "Effetto", "Evento"], [
    ["invio", "destinatari risolti, testo pulito", "ID con " + c("flock") + "; " + c("incomplete") + " e lock prima di "
     "tutto; " + c("msg") + " e " + c("recipients") + " scritti e rinominati", "tutti INVIATO", c("INVIATO")],
    ["consegna", "lock dell'invio tenuto", "copia scritta come l'utente e rinominata, poi verificata; poi riga in "
     + c("delivery"), "INVIATO → CONSEGNATO", c("CONSEGNATO") + " (o " + c("NON_CONSEGNATO") + ")"],
    ["conferma", "copia in " + c("inbox/") + ", non scaduta, nessuna conferma presente",
     "file temporaneo + " + c("ln") + " (fallisce se esiste)", "CONSEGNATO → CONFERMATO", c("CONFERMATO")],
    ["rinvio", "CONSEGNATO", c("touch state/ID.term|gui"), "resta CONSEGNATO", c("RINVIATO")],
    ["ritiro", "messaggio esistente", c("sent/ID/revoked") + ", poi copie tolte", "nessuno stato cambia; non si "
     "mostra più", c("RITIRATO")],
    ["scadenza", "—", "nessuna (il tempo passa)", "non si mostra più; una conferma dopo non vale", "—"],
    ["recupero", c("incomplete") + " presente e lock libero", "consegna delle copie mancanti", "INVIATO → CONSEGNATO",
     c("CONSEGNATO") + ", " + c("RECUPERATO")],
    ["cancellazione", "più vecchio della durata, lock libero, completo", "copie tolte come l'utente, poi " + c("sent/ID")
     + " rimossa", "il messaggio non esiste più", c("CANCELLATO")],
], "«TAB» — Le transizioni")

S3 = table(["#", "Invariante"], [
    ["I1", "Ogni " + c("sent/ID") + " completo ha " + c("msg") + " e " + c("recipients") + "; uno incompleto ha "
     + c("incomplete") + ", uno annullato ha " + c("failed") + "."],
    ["I2", c("delivery") + " contiene al più una riga per destinatario, e solo di destinatari: consegna e recupero "
     "tengono lo stesso lock."],
    ["I3", "Una riga in " + c("delivery") + " vuol dire che la copia era nella casella, verificata, in quel momento."],
    ["I4", "Una conferma nasce intera o non nasce, e una volta scritta non cambia: vale la prima."],
    ["I5", "Una conferma valida ha una data non successiva alla scadenza della copia di riferimento."],
    ["I6", "Un messaggio con " + c("incomplete") + " e lock libero è un invio interrotto: il primo comando " + c("ams")
     + " successivo lo completa o, se non era stato salvato, lo annulla."],
    ["I7", "Root non legge né scrive il contenuto di una casella con la propria identità: sempre come l'utente."],
    ["I8", "Testo e titolo salvati non contengono caratteri di controllo né sequenze di escape."],
    ["I9", "Gli ID crescono sempre (sequenza con " + c("flock") + "); si riusano solo se l'archivio viene azzerato."],
    ["I10", "AMS non blocca mai una sessione e non tocca le sessioni senza terminale."],
    ["I11", "Il segnale di sveglia va solo a un agente pronto; la casella resta la coda autorevole: un segnale perso "
     "ritarda la finestra al più di " + c("AMS_AGENT_POLL") + " secondi, non la perde. Il segnale non chiude né "
     "cambia una finestra già aperta."],
    ["I12", "Un rinvio si registra solo per una scelta dell'utente («Più tardi», finestra chiusa, risposta diversa da "
     "sì): una finestra chiusa dal sistema non è un rinvio."],
], "«TAB» — Le invarianti")

S4 = p("Per ogni punto in cui un processo può interrompersi, lo stato che resta e chi lo ripara.", lead=True) + \
    table(["Interruzione", "Stato che resta", "Riparazione"], [
        ["dopo l'ID, prima della cartella", "un numero saltato", "nessuna (innocuo)"],
        ["cartella e " + c("incomplete") + ", senza " + c("msg") + " o " + c("recipients"), "invio non salvato",
         "il comando successivo lo annulla (" + c("failed") + ", evento " + c("ANNULLATO") + ")"],
        ["durante le consegne", "alcuni destinatari INVIATO", "il comando successivo consegna le copie mancanti"],
        ["dopo le consegne, prima di togliere " + c("incomplete"), "tutto consegnato, segno rimasto",
         "il comando successivo toglie il segno"],
        ["dentro " + c("ack") + ", prima di " + c("ln"), "un file temporaneo " + c("acks/.ID.PID")
         + ", nessuna conferma", "la domanda torna; il file temporaneo è ignorato"],
        ["dopo " + c("ln") + ", prima dello spostamento in " + c("read/"), "conferma presente, copia ancora in "
         + c("inbox/"), "chi legge la casella completa lo spostamento senza chiedere di nuovo"],
        ["uscita dalla sessione subito dopo «Ho letto»", "conferma registrata: l'agente attende la finestra, scrive "
         "la risposta appena arriva e rimanda il SIGTERM a dopo la scrittura", "nessuna (scenario I10: uscita dopo 0,1 s)"],
        ["uscita dalla sessione con la finestra aperta", "nessun rinvio registrato: la finestra torna al prossimo login",
         "nessuna"],
        ["l'agente del desktop muore", "lock rilasciato; una sua finestra può restare aperta", c("ams send")
         + " o il login avviano un nuovo agente; la finestra orfana non registra più nulla"],
    ], "«TAB» — Comportamento dopo un'interruzione") + \
    note("le riparazioni sono provate: interruzioni simulate in " + c("tests/engine.sh") + " (gruppi 1 e 2) e un "
         + c("ams send") + " ucciso davvero con SIGKILL nella suite dal vero (scenario F3).")

S5 = table(["Aspetto", "Regola"], [
    ["riferimento", "tutte le date sono secondi dall'epoca Unix sull'orologio della macchina; utenti e root usano lo "
     "stesso orologio"],
    ["scadenza", "confrontata con l'ora corrente quando un messaggio sta per essere mostrato, mentre una domanda o una "
     "finestra sono aperte (ogni secondo), e quando si registra la conferma; in " + c("ams status") + " con la data "
     "della conferma"],
    ["rinvio", "vale " + c("AMS_REMIND_MINUTES") + " dalla data di modifica di " + c("state/ID.*") + "; al login il "
     "rinvio non vale"],
    ["orologio spostato indietro", "scadenze e rinvii durano di più; nessun messaggio si perde"],
    ["orologio spostato avanti", "scadenze e rinvii arrivano prima"],
    ["sospensione e ripresa", "l'agente riprende al giro successivo (al più " + c("AMS_AGENT_POLL") + " secondi); il "
     "tempo trascorso conta per scadenze e rinvii"],
], "«TAB» — Il tempo") + table(["Situazione", "Ritiro", "Scadenza"], [
    ["copia non ancora mostrata", "tolta dalla casella; non si mostra", "resta; non si mostra più"],
    ["finestra o domanda aperte", "si chiudono (entro 1 s)", "si chiudono (entro 1 s)"],
    ["conferme già date", "restano valide", "restano valide se precedenti alla scadenza"],
    ["testo già scritto nei terminali", "resta sullo schermo", "resta sullo schermo"],
    ["in " + c("ams status"), "«consegnato, non confermato (ritirato)»", "«consegnato, non confermato (scaduto)»"],
], "«TAB» — Ritiro e scadenza")

S6 = p("Formato 1 dell'archivio. Chi legge ignora le chiavi di intestazione che non conosce.", lead=True) + \
    table(["File", "Contenuto"], [
        [c("sent/.seq"), "l'ultimo ID assegnato, un numero"],
        [c("sent/ID/msg"), "intestazione " + c("chiave: valore") + " (" + c("format") + ", " + c("id") + ", " + c("from")
         + ", " + c("date") + ", " + c("title") + ", " + c("expires") + "), riga vuota, testo; UTF-8 senza caratteri di "
         "controllo"],
        [c("sent/ID/recipients"), "un nome utente per riga, senza doppioni"],
        [c("sent/ID/delivery"), c("utente data terminali-scritti") + ", una riga per consegna"],
        [c("sent/ID/revoked"), "la data del ritiro"],
        [c("sent/ID/incomplete") + ", " + c("failed") + ", " + c("lock"), "segni (il contenuto non conta); "
         + c("lock") + " si usa con " + c("flock")],
        [c("users/U/inbox/ID") + ", " + c("read/ID"), "copia di " + c("msg")],
        [c("users/U/acks/ID"), c("data canale") + ", una riga; canale " + c("desktop") + " o " + c("terminale pts/N")],
        [c("users/U/state/ID.term") + ", " + c("ID.gui"), "vuoti; conta la data di modifica"],
    ], "«TAB» — Il formato dell'archivio")

S7 = table(["", "Requisito"], [
    ["sistema", "Linux con systemd e logind (sessioni, " + c("loginctl") + ", " + c("systemd-run --user") + ")"],
    ["strumenti", "bash 5, sudo, util-linux (" + c("runuser") + ", " + c("flock") + ", " + c("logger --journald")
     + "), procps (" + c("pkill -F") + "), coreutils GNU (" + c("date -d") + ", " + c("stat -c") + ")"],
    ["desktop", "zenity; una sessione che esegue l'avvio automatico XDG (" + c("/etc/xdg/autostart") + ")"],
    ["domanda nel terminale", "bash interattiva; con altre shell arriva solo il testo"],
], "«TAB» — Cosa serve") + table(["Ambiente", "Stato"], [
    ["Debian 13, GNOME 48 su Wayland (PC di sviluppo)", "provato dal vivo"],
    ["Debian 13 in container con systemd", "suite dal vero automatica (" + c("tests/container") + ")"],
    ["Debian 13, GNOME su Wayland in VM", "suite dal vero automatica con il desktop (" + c("tests/vm") + ")"],
    ["X11, altri desktop (KDE, XFCE), altre distribuzioni", "non provato: dovrebbe funzionare se i requisiti ci sono"],
    ["sistemi senza systemd (sysvinit, OpenRC)", "non supportato"],
], "«TAB» — Il perimetro")

CHAPTER = ("Specifica", [
    ("Fonti autorevoli", S1),
    ("Stati e transizioni", S2),
    ("Invarianti", S3),
    ("Interruzioni e recupero", S4),
    ("Tempo, ritiro e scadenza", S5),
    ("Formato dell'archivio", S6),
    ("Perimetro supportato", S7),
])
