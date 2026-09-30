from build import arrow, box, c, fig, note, p, path, table, text, ul

S1 = p("Questo capitolo è il contratto di AMS: ciò che qualunque implementazione deve rispettare, indipendentemente da "
       "come è scritta. Il resto del manuale descrive come la versione in C lo realizza; il prototipo in bash (0.1.0) "
       "lavorava sullo stesso archivio, e le stesse prove valgono per entrambi.",
       lead=True) + table(["Fonte", "Autorità", "Chi la scrive"], [
    [c("sent/ID/") + " (msg, recipients, delivery, revoked, incomplete, ritiro, failed, lock)", "<b>autorevole</b>: cosa è "
     "stato inviato, a chi, quando, con quale scadenza, a chi è stato consegnato", "solo root"],
    [c("users/U/") + " (inbox, read, acks, state)", "<b>copia di lavoro</b>, controllata dall'utente: può essere "
     "cancellata o alterata, e il sistema deve restare coerente", "l'utente (e root, come l'utente)"],
    ["journal (" + c("SYSLOG_IDENTIFIER=ams") + ")", "<b>storia</b>: eventi con data e " + c("_UID")
     + ", l'utente che li ha scritti (lo mette il journal). Chiunque può scrivere un evento con i campi " + c("AMS_*")
     + ": " + c("_UID") + " dice chi l'ha scritto, non che sia vero; " + c("ams log") + " segnala come non "
     "attendibile un evento scritto dall'utente sbagliato. Gli stati si deducono dall'archivio, mai dal journal",
     "root e l'utente"],
], "«TAB» — Le fonti di verità") + ul([
    "Una conferma è un fatto dichiarato dall'utente nella propria casella; vale solo se non contraddice "
    "l'archivio di root: la sua data non deve essere successiva alla scadenza scritta in " + c("sent/ID/msg")
    + " né al ritiro (" + c("sent/ID/revoked") + ").",
    "<b>«Confermato» vuol dire</b>: nella casella c'è una dichiarazione di lettura valida dell'utente. Non è "
    "un'azione osservata da AMS né una prova di lettura: l'utente controlla la propria casella e potrebbe scriverla "
    "da sé. Chi usa " + c("ams status") + " per un audit deve leggerlo così.",
    "Se l'utente cancella la propria copia, il messaggio risulta semplicemente non confermato; se la altera (testo, "
    "scadenza), cambia solo ciò che vede lui.",
])

STATI = fig(
    box(20, 130, 180, 64, "INVIATO", "in recipients, non in delivery", "light")
    + box(290, 130, 230, 64, "CONSEGNATO", "riga in delivery, nessuna conferma valida", "blue")
    + box(640, 130, 240, 64, "CONFERMATO", "acks/ID con data ≤ scadenza e ritiro", "green")
    + arrow(202, 162, 288, 162, "#0050C0", False, "copia verificata", 245, 152)
    + arrow(522, 162, 638, 162, "#16a34a", False, "conferma", 580, 152)
    + text(580, 212, "(non scaduto, non ritirato)", 11, "#166534", "600")
    + path([(365, 196), (365, 232), (445, 232), (445, 196)], "#d97706")
    + text(405, 252, "rinvio: state/ID.*", 11, "#92400e", "600")
    + box(560, 20, 320, 48, "Proprietà del messaggio", "RITIRATO · SCADUTO", "soft", 12)
    + text(560, 90, "segni interni del recupero, non stati:", 11, "#475569", "400", "start")
    + text(560, 106, "incomplete · failed · ritiro", 11, "#475569", "400", "start"),
    900, 272, "«FIG» — Gli stati di un destinatario e le proprietà di un messaggio", "La macchina a stati")

S2 = p("Ogni destinatario di un messaggio è in uno di tre stati; lo stato si deduce dai file, secondo regole fisse. "
       "Gli stati sono solo questi tre (decisione dell'utente): ritiro e scadenza sono proprietà del messaggio, non "
       "stati; " + c("incomplete") + ", " + c("failed") + " e " + c("ritiro") + " sono segni interni con cui il recupero "
       "completa o annulla un'operazione interrotta, e non si mostrano come stati. Un invio interrotto si vede da sé: "
       "qualche destinatario resta INVIATO.",
       lead=True) + STATI + table(["Transizione", "Precondizione", "Operazione atomica", "Effetto", "Evento"], [
    ["invio", "destinatari risolti, testo pulito, al più 65536 byte", "ID con " + c("flock") + "; " + c("incomplete")
     + " e lock prima di tutto; " + c("msg") + " e " + c("recipients") + " scritti, rinominati e portati su disco ("
     + c("sync") + ")", "tutti INVIATO", c("INVIATO")],
    ["consegna", "lock dell'invio tenuto, messaggio non ritirato", "copia scritta come l'utente e rinominata, poi "
     "verificata; poi riga in " + c("delivery") + "; a fine invio tutto su disco, poi via " + c("incomplete"),
     "INVIATO → CONSEGNATO", c("CONSEGNATO") + " (o " + c("NON_CONSEGNATO") + ")"],
    ["conferma", "copia in " + c("inbox/") + ", non scaduta, nessuna conferma presente",
     "file temporaneo + " + c("ln") + " (fallisce se esiste), poi " + c("sync"), "CONSEGNATO → CONFERMATO", c("CONFERMATO")],
    ["rinvio", "CONSEGNATO", c("touch state/ID.term|gui"), "resta CONSEGNATO", c("RINVIATO")],
    ["ritiro", "messaggio esistente", c("sent/ID/ritiro") + " e " + c("sent/ID/revoked") + " (su disco); poi il lock "
     "(attende un invio in corso); poi copie tolte come l'utente e via " + c("ritiro"), "nessuno stato cambia; non si "
     "mostra più; conferme successive non valgono", c("RITIRATO")],
    ["scadenza", "—", "nessuna (il tempo passa)", "non si mostra più; una conferma dopo non vale", "—"],
    ["recupero", c("incomplete") + " presente e lock libero", "consegna delle copie mancanti e controllo di quelle "
     "già annotate", "INVIATO → CONSEGNATO", c("CONSEGNATO") + ", " + c("RECUPERATO")],
    ["recupero del ritiro", c("ritiro") + " presente e lock libero", "copie rimaste tolte", "—", "—"],
    ["sollecito", "messaggio non ritirato né scaduto", "come ogni destinatario CONSEGNATO: rinvii tolti " + c("state/ID.*")
     + ", agente svegliato", "resta CONSEGNATO; la domanda e la finestra tornano subito", c("SOLLECITATO")],
    ["cancellazione", "più vecchio della durata, lock libero, completo", c("sent/ID") + " rinominata in "
     + c("sent/.cancella-ID") + "; poi copie, conferme e rinvii tolti come l'utente; poi la cartella rimossa",
     "il messaggio non esiste più", c("CANCELLATO")],
], "«TAB» — Le transizioni")

SM = p("Nella lista dei messaggi (TUI e " + c("ams list") + ") un messaggio si riassume con i suoi destinatari: "
       "quanti sono in ciascuno dei tre stati, a parole e con una barra (confermato, consegnato, inviato), più le "
       "proprietà ritirato e scaduto. Nessun'altra parola descrive lo stato di un messaggio.", lead=True)

S2B = p("Per ogni comando che cambia l'archivio: che lock tiene, in quale istante l'operazione si considera "
        "avvenuta (il <b>punto di linearizzazione</b>: prima di quell'istante non è avvenuta, dopo sì, per chiunque "
        "osservi) e che cosa succede con gli altri comandi nello stesso momento.", lead=True) + \
    table(["Operazione", "Lock", "Avviene quando", "In concorrenza"], [
        [c("send"), c("sent/.seq.lock") + " per l'ID; " + c("sent/ID/lock") + " esclusivo per tutta la consegna",
         "il messaggio: " + c("recipients") + " rinominato; ogni consegna: la sua riga in " + c("delivery"),
         "recupero e cancellazione saltano il messaggio; il ritiro lo ferma al destinatario successivo"],
        ["recupero", c("sent/ID/lock") + " se libero, altrimenti salta", "come la consegna",
         "non lavora mai insieme a un invio in corso"],
        [c("revoke"), c("sent/ID/lock") + " atteso dopo aver scritto " + c("revoked"), c("sent/ID/revoked")
         + " rinominato al suo posto", "l'invio in corso non consegna altro; le conferme con data successiva non "
         "valgono; le copie si tolgono quando l'invio ha lasciato il lock"],
        ["conferma (" + c("ack") + ")", "nessuno: " + c("ln") + " esclusivo", c("acks/ID") + " creato; conta la "
         "data scritta dentro", "fra due conferme vince la prima; con il ritiro decide la data: uguale o precedente "
         "vale, successiva no; senza copia in " + c("inbox/") + " non si conferma"],
        [c("purge"), c("sent/ID/lock") + " se libero, altrimenti salta", c("sent/ID") + " rinominata in "
         + c("sent/.cancella-ID"), "da quell'istante nessun comando vede il messaggio; " + c("list") + " legge ciò "
         "che le serve prima e salta un messaggio sparito nel frattempo"],
        [c("remind"), "nessuno", "ogni rinvio tolto", "con una conferma arrivata nel frattempo: quel destinatario "
         "non è più CONSEGNATO e togliere i suoi rinvii non ha effetto"],
        [c("list") + ", " + c("status") + ", " + c("log") + ", la TUI", "nessuno (sola lettura)", "—",
         "vedono lo stato di quel momento: durante un invio, i destinatari non ancora raggiunti sono INVIATO"],
    ], "«TAB» — Lock e punti di linearizzazione")

S3 = table(["#", "Invariante"], [
    ["I1", "Ogni " + c("sent/ID") + " completo ha " + c("msg") + " e " + c("recipients") + "; uno incompleto ha "
     + c("incomplete") + ", uno annullato ha " + c("failed") + "."],
    ["I2", c("delivery") + " contiene al più una riga per destinatario, e solo di destinatari: consegna e recupero "
     "tengono lo stesso lock."],
    ["I3", "Una riga in " + c("delivery") + " vuol dire che la copia era nella casella, verificata, in quel momento."],
    ["I4", "Una conferma nasce intera o non nasce, e una volta scritta non cambia: vale la prima."],
    ["I5", "Una conferma valida ha una data non successiva alla scadenza della copia di riferimento né al ritiro."],
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
    ["I13", "Durata: quando " + c("incomplete") + " non c'è più, copie e righe di " + c("delivery") + " sono su disco; "
     "una conferma è su disco prima che l'utente legga «Confermato»; " + c("revoked") + " è su disco prima che "
     + c("ams revoke") + " tocchi le caselle. Dopo un'interruzione di corrente con " + c("incomplete") + " presente, "
     "il recupero ricontrolla tutte le copie, anche quelle già annotate."],
    ["I14", "Il testo si scrive in un terminale solo se il terminale, una volta aperto, appartiene al destinatario: "
     "il nome " + c("/dev/pts/N") + " non identifica una sessione."],
    ["I15", "Nessun comando di root legge dalle caselle più di ciò che riguarda i messaggi in " + c("sent/")
     + ", e ogni lettura ha un tempo massimo: una casella anomala non blocca né rallenta " + c("ams") + "."],
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
        [c("ams revoke") + " dopo " + c("revoked") + ", prima di togliere le copie", c("revoked") + " e "
         + c("ritiro") + "; qualche copia ancora nelle caselle", "il comando " + c("ams") + " successivo toglie le "
         "copie (i destinatari non le vedono come ritirate prima di allora)"],
        ["una casella non raggiungibile durante il ritiro", c("ritiro") + " resta", "il comando successivo riprova"],
        [c("ams purge") + " dopo la rinomina", c("sent/.cancella-ID") + ", qualche copia nelle caselle",
         "il comando " + c("ams") + " successivo toglie copie, conferme, rinvii e la cartella"],
        ["interruzione di corrente durante l'invio", c("incomplete") + " su disco; copie e righe di " + c("delivery")
         + " forse no", "il recupero riscrive ogni copia che manca, anche se annotata"],
        ["interruzione di corrente dopo «Confermato»", "conferma su disco", "nessuna"],
        ["interruzione di corrente in altri momenti", "possono mancare le scritture non portate su disco: un rinvio "
         "(la domanda torna prima) o lo spostamento in " + c("read/") + " (si completa alla lettura successiva)",
         "nessuna necessaria"],
    ], "«TAB» — Comportamento dopo un'interruzione") + \
    note("le riparazioni sono provate: interruzioni simulate in " + c("tests/engine.sh") + " (gruppi 1, 2 e 9: "
         "copia sparita dopo un'interruzione, ritiro e cancellazione interrotti), un " + c("ams send")
         + " ucciso davvero con SIGKILL (scenario F3) e un ritiro durante un invio a 68 utenti (scenario F7). "
         "Un'interruzione di corrente vera non è provata: la durata si basa su " + c("sync") + " (fsync di file e "
         "cartelle, syncfs a fine invio).")

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
    ["conferme già date", "restano valide se con data non successiva al ritiro", "restano valide se con data non "
     "successiva alla scadenza"],
    ["durante l'invio", "l'invio si ferma al destinatario successivo", "l'invio continua: chi riceve la copia dopo la "
     "scadenza non la vede mai («consegnato, non confermato (scaduto)»)"],
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
        [c("sent/ID/delivery"), "una riga per consegna: " + c("utente data terminali") + ", campi separati da uno "
         "spazio; " + c("data") + " in secondi dall'epoca Unix, " + c("terminali") + " il numero di terminali scritti "
         "(0 nel recupero)"],
        [c("sent/ID/revoked"), "la data del ritiro, in secondi dall'epoca Unix"],
        [c("sent/ID/incomplete") + ", " + c("ritiro") + ", " + c("failed") + ", " + c("lock"), "segni (il contenuto "
         "non conta): invio incompleto, ritiro da completare, invio annullato; " + c("lock") + " si usa con " + c("flock")],
        [c("sent/.cancella-ID/"), "un messaggio che " + c("ams purge") + " sta cancellando"],
        [c("users/U/inbox/ID") + ", " + c("read/ID"), "copia di " + c("msg")],
        [c("users/U/acks/ID"), c("data canale") + ": data in secondi dall'epoca Unix, uno spazio, canale ("
         + c("desktop") + " o " + c("terminale pts/N") + "); conta la prima riga, al più 200 byte"],
        [c("users/U/state/ID.term") + ", " + c("ID.gui"), "vuoti; conta la data di modifica"],
    ], "«TAB» — Il formato dell'archivio")

S7 = table(["", "Requisito"], [
    ["sistema", "Linux con systemd e logind (sessioni, " + c("loginctl") + ", " + c("systemd-run --user") + ")"],
    ["librerie e strumenti", "glibc, libsystemd (sessioni e journal), sudo, " + c("systemd-run") + " e " + c("date -d")
     + " (coreutils GNU); per compilare: gcc, make, pkg-config, libsystemd-dev, gettext"],
    ["desktop", "zenity; una sessione che esegue l'avvio automatico XDG (" + c("/etc/xdg/autostart") + ")"],
    ["domanda nel terminale", "bash, zsh o fish a ogni prompt; sh, dash, ksh e le altre shell che leggono "
     + c("/etc/profile") + " al login; il testo all'invio con qualunque shell"],
], "«TAB» — Cosa serve") + \
    p("<b>Supportato</b> vuol dire che i requisiti sono soddisfatti e AMS è pensato per funzionare; <b>verificato</b> "
      "che è stato provato, e come. Le due cose sono distinte.") + \
    table(["Ambiente", "Supportato", "Verificato"], [
        ["Debian 13, GNOME 48 su Wayland", "sì", "sì: dal vivo e con la suite automatica nella VM (" + c("tests/vm") + ")"],
        ["Debian 13 senza desktop: console, ssh, tmux", "sì", "sì: suite automatica nel container (" + c("tests/container") + ")"],
        ["zsh, fish, ksh, dash su Debian 13", "sì", "sì: scenari K nel container"],
        ["altre distribuzioni con systemd (Ubuntu, Fedora, Arch…)", "sì", "no"],
        ["X11; desktop diversi da GNOME (KDE, XFCE…)", "sì, con zenity e avvio automatico XDG", "no"],
        ["sistemi senza systemd (sysvinit, OpenRC)", "no", "—"],
    ], "«TAB» — Il perimetro: supportato e verificato")

CHAPTER = ("Specifica", [
    ("Fonti autorevoli", S1),
    ("Stati e transizioni", S2),
    ("Come si riassume un messaggio", SM),
    ("Operazioni concorrenti", S2B),
    ("Invarianti", S3),
    ("Interruzioni e recupero", S4),
    ("Tempo, ritiro e scadenza", S5),
    ("Formato dell'archivio", S6),
    ("Perimetro supportato", S7),
])
