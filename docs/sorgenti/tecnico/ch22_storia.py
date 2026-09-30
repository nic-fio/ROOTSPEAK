from build import arrow, box, c, fig, note, p, table, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


TEMPI = fig(
    '<line x1="40" y1="120" x2="860" y2="120" stroke="#94a3b8" stroke-width="3"/>'
    + box(30, 40, 150, 54, "29/9 sera", "prototipo in bash", "dark", 12)
    + box(195, 40, 150, 54, "29/9 notte", "prove dal vivo, 0.1.0", "dark", 12)
    + box(360, 40, 160, 54, "30/9 mattina", "revisioni A e B", "amber", 12)
    + box(535, 40, 160, 54, "30/9 pomeriggio", "revisioni C e D; C", "amber", 12)
    + box(710, 40, 160, 54, "30/9 sera", "TUI, sollecito", "navy", 12)
    + arrow(105, 96, 105, 114, "#94a3b8") + arrow(270, 96, 270, 114, "#94a3b8") + arrow(440, 96, 440, 114, "#94a3b8")
    + arrow(615, 96, 615, 114, "#94a3b8") + arrow(790, 96, 790, 114, "#94a3b8")
    + text(270, 150, "doppia conferma, finestra lenta", 11, "#475569")
    + text(440, 168, "specifica, tre stati, suite", 11, "#475569")
    + text(615, 150, "ritiro, corrente; 0.2.0 in C", 11, "#475569")
    + text(790, 168, "stati inventati tolti", 11, "#475569"),
    900, 186, "«FIG» — Le tappe del progetto e ciò che ciascuna ha cambiato", "Storia in breve")

S1 = p("Il progetto è stato sottoposto a due revisioni critiche esterne, fatte da modelli linguistici sul manuale "
       "tecnico, senza il codice. Ogni rilievo è stato verificato sul codice o con una prova prima di essere "
       "accolto; il dettaglio punto per punto è in " + c("docs/revisione-avversariale.md") + ".", lead=True) + \
    TEMPI + table(["Revisione", "Su che cosa", "Che cosa ne è uscito"], [
        ["prima (A e B), sulla versione 0.1.0", "difetti reali, specifica, robustezza, prove", "conferme mai perse in "
         "silenzio; consegna verificata con recupero; tre stati per ogni messaggio, senza livelli; eventi strutturati "
         "e " + c("ams log") + "; " + c("ams purge") + "; configurazione come dati; il capitolo «Specifica»; le suite "
         "dal vero nel container e nella VM"],
        ["seconda (C e D), sul manuale con la nota di accompagnamento", "gare, durata, confini", "ritiro serializzato "
         "con l'invio; conferme successive al ritiro non valide; terminale controllato dopo l'apertura; durata dopo "
         "un'interruzione di corrente; cancellazione in un colpo solo; caselle anomale; testi oltre 65536 byte "
         "rifiutati; numeri delle prove legati all'impronta del codice; «supportato» distinto da «verificato»; "
         "punti di linearizzazione"],
    ], "«TAB» — Le due revisioni") + ul([
    "Critiche non accolte, con il loro perché: «la conferma non prova la lettura» (voluto: mai bloccare, "
    + cap(20, 1) + "); «se il terminale è bloccato il messaggio non arriva» (inesatto: la casella fa da coda); "
    "«riscrivere subito in un linguaggio compilato» (prima la specifica; la riscrittura è venuta dopo); " + c("ams")
    + " sempre root (decisione dell'utente); una pipe al posto di " + c("acks/ID") + " che blocca " + c("ams status")
    + " e un commento a fine riga in " + c("ams.conf") + " (inesatti, provati); un " + c("/var/lib/ams")
    + " preparato prima dell'installazione (fuori dal modello).",
    "Una critica respinta per errore e poi accolta: i lock rimasti bloccati. Il kernel rilascia il lock alla morte "
    "del processo, ma la VM di prova ha mostrato che il lock dell'agente passava ai suoi figli.",
])

S2 = table(["Difetto", "Trovato da", "Correzione", "Dove"], [
    ["la conferma non scrivibile era trattata come «già confermata»: il messaggio spariva senza conferma",
     "revisione A", "pubblicazione con " + c("link") + " esclusivo; esito 1, il messaggio resta", cap(13, 1)],
    ["un " + c("ams send") + " interrotto lasciava destinatari senza copia, mai recuperati", "revisione A",
     "consegna verificata e annotata; " + c("incomplete") + "; recupero", cap(8, 6)],
    ["un agente svegliato mentre partiva moriva (20 su 20)", "revisione A, prova", "gestore di " + c("SIGUSR1")
     + " come prima istruzione; " + c("ams-agent.pronto"), cap(12, 2)],
    ["finestre e domande aperte accettavano la conferma dopo la scadenza", "revisione A", "si chiudono alla "
     "scadenza; conferma rifiutata; data confrontata con " + c("sent/"), cap(20, 7)],
    ["il recupero, durante un invio lungo, consegnava in parallelo e annotava doppioni", "container, F3 e F5",
     c("sent/ID/lock") + " tenuto per tutta la consegna", cap(8, 6)],
    [c("online") + " includeva root e gli account di sistema collegati", "VM, B5", "filtro degli utenti umani",
     cap(6, 2)],
    ["il lock dell'agente passava ai figli: una finestra orfana bloccava il nuovo agente", "VM", c("O_CLOEXEC")
     + " (nel prototipo, chiusura del descrittore)", cap(12, 1)],
    ["un'uscita dalla sessione subito dopo «Ho letto» poteva perdere la conferma", "VM, I10", "segnali bloccati "
     "fuori dalle attese; la finestra si aspetta 2 s", cap(12, 3)],
    ["la sveglia interrompeva l'attesa della finestra e registrava un rinvio mai scelto", "VM, I7", "la sveglia non "
     "chiude la finestra", cap(12, 3)],
    ["una finestra chiusa dal sistema contava come rinvio", "VM", "rinvio solo con l'uscita 1 di zenity",
     cap(12, 3)],
    ["un sollecito entro un secondo da «Più tardi» andava perso", "VM, I11", "la risposta si registra appena "
     "zenity si chiude (" + c("SIGCHLD") + ")", cap(12, 3)],
    [c("ams revoke") + " non aspettava un invio in corso", "revisione C", "ritiro su disco, poi il lock", cap(9, 1)],
    ["una conferma poteva nascere dopo il ritiro", "revisione C", "niente conferma senza copia; data confrontata "
     "con il ritiro", cap(13, 1)],
    ["il testo poteva finire sul terminale di un altro utente", "revisione C", "proprietario del terminale aperto",
     cap(8, 4)],
    ["nessuna garanzia dopo un'interruzione di corrente", "revisione C", c("fsync") + ", " + c("syncfs")
     + ", copie annotate ricontrollate", cap(20, 6)],
    [c("ams purge") + " insieme ad " + c("ams list") + ": un messaggio spariva a metà lettura", "revisione D",
     "rinomina in " + c(".cancella-ID") + "; lettura prima dell'uso", cap(9, 3)],
    ["5000 file finti in " + c("acks/") + ": " + c("ams list") + " da 3,9 s", "revisione D", "solo i messaggi di "
     + c("sent/") + ", con tempo massimo", cap(10, 2)],
    ["testi oltre 128 KiB non arrivavano alla finestra", "revisione D", "limite di 65536 byte all'invio", cap(8, 1)],
    ["il figlio d'invio della TUI non vedeva mai la fine del testo", c("tests/tui.py"), "chiude il capo della pipe "
     "che non usa", cap(14, 4)],
    ["pipe non chiuse in un caso d'errore di " + c("come_utente"), c("-fanalyzer"), "chiuse", cap(7, 3)],
    ["una funzione presupponeva una struttura già azzerata", "fuzzing", "corretta", cap(21, 7)],
    ["stati inventati nella TUI e nella specifica («in attesa», «completo», «invio incompleto», «annullato»)",
     "l'utente, sulle anteprime", "solo i tre stati; riassunto con i conteggi", cap(20, 3)],
], "«TAB» — I difetti trovati e corretti") + \
    p("Dalle prove dal vivo del prototipo sono nate anche tre regole: la prima conferma vale per tutti i canali (si "
      "doveva confermare due volte), la sveglia dell'agente con un segnale (la finestra arrivava dopo 3-4 secondi) "
      "e il comando in " + c("/usr/local/bin") + " invece che in " + c("sbin") + " (su Debian " + c("sbin")
      + " non è nel PATH degli utenti non root).")

S3 = p("La versione 0.2.0 è una riscrittura completa in C del prototipo in bash, decisa dall'utente dopo la seconda "
       "revisione: i difetti trovati nascevano quasi tutti dal bash (gare fra controllo e uso, tempi massimi, un "
       "processo per operazione). Era stato proposto un linguaggio che eviti per costruzione gli errori di memoria; "
       "l'utente ha scelto il C, con difese obbligatorie.", lead=True) + table(["Nel prototipo (bash)", "Nella "
                                                                                "versione in C"], [
    [c("runuser -u U -- …") + " per ogni accesso a una casella", c("come_utente") + ": un figlio con l'identità di "
     "U e un tempo massimo; una casella si legge in un solo figlio (" + cap(7) + ")"],
    [c("set -C") + ", poi " + c("ln") + " per la conferma", c("open(O_EXCL)") + ", " + c("fsync") + ", " + c("link")
     + " (" + cap(13, 1) + ")"],
    [c("pkill -F") + " per la sveglia", c("op_sveglia") + ": PID pronto, riga di comando esatta, " + c("kill")
     + " come l'utente (" + cap(8, 5) + ")"],
    [c("sed") + " e " + c("tr") + " per la pulizia del testo", c("pulisci") + ", con lo stesso risultato su 2000 "
     "testi casuali (" + cap(8, 7) + ")"],
    ["configurazione letta con " + c("source"), "file di dati, due chiavi (" + cap(4, 5) + ")"],
    ["testi delle lingue in file della shell", "cataloghi gettext letti da AMS (" + cap(16, 3) + ")"],
    [c("wait") + " interrotto dalla sveglia", c("ppoll") + " con segnali bloccati fuori dalle attese (" + cap(12, 2)
     + ")"],
], "«TAB» — Dal bash al C") + \
    note("il prototipo in bash è stato tolto quando la versione in C ha passato tutte le prove; resta nella storia "
         "del repository. Gli agganci delle shell restano script, e la finestra resta zenity.")

CHAPTER = ("Difetti trovati e revisioni", [
    ("Le due revisioni esterne", S1),
    ("I difetti trovati e corretti", S2),
    ("Dal bash al C", S3),
])
