from build import arrow, box, c, diamond, fig, flow, note, p, path, seq, table, text, ul, zone

S1 = flow([("Ambiente", "AMS_TEST e lingua", "dark"), ("Root?", "altrimenti execvp sudo", "navy"),
           ("Guida, versione", "help, --help, version", "blue"), ("Comando", "recupero, poi il comando", "blue")],
          "«FIG» — L'avvio di ams") + \
    p(c("main") + " di " + c("src/ams.c") + " legge l'ambiente (" + c("ams_init") + ": le variabili di prova valgono "
      "solo con " + c("AMS_TEST") + ") e sceglie la lingua; se non è root e non è in modalità di prova, si rilancia "
      "con " + c("sudo -- /proc/self/exe argomenti…") + ". Solo dopo guarda il comando: guida e versione comprese, "
      "nulla gira senza root. Un comando sconosciuto termina con " + c("die") + ", che stampa " + c("ams: …")
      + " ed esce con 1.")

S2 = table(["Funzione", "Cosa restituisce"], [
    [c("risolvi_destinatari DEST"), "divide " + c("DEST") + " sulle virgole, risolve ogni parte e toglie i doppioni; un nome "
     "inesistente è un errore"],
    [c("utenti_umani"), "gli utenti con UID fra " + c("UID_MIN") + " e " + c("UID_MAX") + " di " + c("/etc/login.defs")
     + " (predefiniti 1000 e 60000) e una shell che non finisce con " + c("nologin") + " o " + c("false")],
    [c("utenti_online"), "gli utenti di " + c("utenti_umani") + " con almeno una sessione logind di classe " + c("user")
     + ": root e gli account di sistema restano esclusi anche se collegati (difetto trovato dalla VM di prova, "
     "scenario B5)"],
    [c("membri_gruppo G"), "i membri elencati nel gruppo più gli utenti che hanno G come gruppo principale"],
    [c("terminali_utente U"), "gli pseudo-terminali in " + c("/dev/pts") + " di proprietà di U, più le console delle sue "
     "sessioni di tipo " + c("tty") + " (sessioni, tipo e terminale da " + c("sd-login") + ")"],
    [c("sessione_grafica U"), "vero se U ha una sessione " + c("x11") + " o " + c("wayland")],
], "«TAB» — Destinatari e sessioni (src/sessioni.c)")

SYMLINK = fig(
    zone(20, 44, 420, 214, "Se root scrivesse direttamente", "#fdf2f2")
    + box(44, 84, 150, 54, "ams (root)", "cat > inbox/12", "navy")
    + box(262, 84, 156, 54, "users/mario/inbox", "sostituita da Mario…", "amber")
    + box(262, 176, 156, 54, "/etc", "…con un collegamento", "grey")
    + arrow(196, 111, 260, 111, "#b91c1c")
    + arrow(340, 140, 340, 174, "#b91c1c", True, "segue il link", 390, 160)
    + text(230, 250, "root scriverebbe in /etc", 11.5, "#b91c1c", "700")
    + zone(470, 44, 410, 214, "Con come_utente: un figlio con l'identità di mario", "#f0fdf4")
    + box(494, 84, 150, 54, "ams (root)", "come_utente(mario…)", "navy")
    + box(704, 84, 156, 54, "figlio (mario)", "scrive inbox/12", "light")
    + box(704, 176, 156, 54, "/etc", "permesso negato", "grey")
    + arrow(646, 111, 702, 111, "#16a34a")
    + arrow(782, 140, 782, 174, "#475569", True)
    + text(675, 250, "il peggio: Mario rovina la sua casella", 11.5, "#166534", "700"),
    900, 276, "«FIG» — Perché root accede alle caselle con l'identità dell'utente", "Il pericolo dei collegamenti simbolici")

S3 = p("La casella " + c("users/U") + " appartiene all'utente, che può sostituirne le cartelle con collegamenti "
       "simbolici. Se root ci scrivesse direttamente, seguirebbe il collegamento e potrebbe scrivere ovunque. Per questo "
       "ogni accesso di root alle caselle avviene in un <b>processo figlio con l'identità dell'utente</b>: "
       + c("come_utente") + " di " + c("src/utente.c") + ", al posto di " + c("runuser") + ".", lead=True) + SYMLINK + ul([
        "Il figlio assume gruppi, gruppo e utente di U (" + c("initgroups") + ", " + c("setresgid") + ", "
        + c("setresuid") + ") e controlla di non poter tornare root; se qualcosa non riesce, esce senza fare nulla.",
        "Il figlio riceve i dati su stdin e restituisce l'uscita su una pipe, con un <b>tempo massimo</b> (20 s per le "
        "caselle): se l'utente lo ferma o lo rallenta, ams lo termina e va avanti. Dopo il cambio d'identità il "
        "processo non è più ispezionabile dall'utente (il kernel lo rende non «dumpable»).",
        "Solo la cartella " + c("users/U") + " è creata da root, dentro " + c("users/") + " che appartiene a root, e poi "
        "ceduta a U; le sottocartelle le crea U. Una cartella rimasta di root (un invio interrotto fra la creazione e "
        "la cessione) viene ceduta al primo invio.",
        "Il messaggio viene scritto in " + c("inbox/ID.tmp") + " e poi rinominato: " + c("ams-user") + " non vede mai un "
        "file a metà. Consegna, controllo e creazione delle sottocartelle avvengono in un solo figlio.",
        c("revoke") + " e " + c("purge") + " tolgono i file come U; " + c("status") + " legge le conferme come U (capitolo 8.2).",
    ])

RECOVER = seq([("ams send", "root", "navy"), ("sent/ID", "", "dark"), ("Casella U1", "", "blue"), ("Casella U2", "", "blue"),
               ("ams (dopo)", "qualunque comando", "light")], [
    (0, 1, "incomplete, msg, recipients"),
    (0, 2, "copia, verifica"),
    (0, 1, "delivery: U1"),
    ("sep", "interruzione: U2 non ha la copia"),
    (4, 1, "recupero: incomplete?"),
    (4, 3, "copia mancante, verifica"),
    (4, 1, "delivery: U2; toglie incomplete"),
], "«FIG» — Un invio interrotto viene completato dal comando successivo", "Consegna verificata e recupero")

SD = p("L'invio è una sequenza di passi; se si interrompe a metà, il comando " + c("ams") + " successivo lo completa.",
       lead=True) + RECOVER + table(["Regola", "Come"], [
    ["l'invio si vede finché non è completo", c("sent/ID/incomplete") + " nasce prima di tutto e sparisce solo quando ogni "
     "destinatario ha la sua copia"],
    [c("msg") + " e " + c("recipients") + " sono interi o assenti", "scritti in un file temporaneo e rinominati"],
    ["«consegnato» vuol dire copia verificata", c("consegna_copia") + " scrive la copia come l'utente e controlla che esista; "
     "solo allora la riga va in " + c("delivery")],
    ["un guasto non ferma gli altri destinatari", "la copia non scritta viene annotata nel registro; " + c("ams send")
     + " prosegue, poi termina con errore e lascia " + c("incomplete")],
    ["il recupero è idempotente", c("recupera") + " gira all'avvio di " + c("send") + ", " + c("list") + ", " + c("status")
     + ", " + c("revoke") + ", " + c("log") + " e riscrive solo le copie che mancano (anche quelle già annotate: "
     "dopo un'interruzione di corrente potrebbero non essere su disco); non riscrive la copia a chi l'ha già letta o confermata"],
    ["un invio in corso non è un invio interrotto", c("ams send") + " tiene " + c("flock") + " su " + c("sent/ID/lock")
     + " per tutta la consegna; il recupero salta i messaggi con il lock occupato. Se " + c("ams send")
     + " muore, anche con SIGKILL, il kernel rilascia il lock. Senza questa regola il recupero, lanciato durante un "
     "invio lungo, consegnava in parallelo e annotava doppioni (trovato dalla suite dal vero, scenario F3)"],
    ["un invio non salvato si annulla", "senza " + c("msg") + " o " + c("recipients") + ", e con il lock libero, il "
     "messaggio diventa " + c("failed") + " e viene segnalato"],
    ["ritirati e scaduti non si completano", "il recupero toglie il segno senza consegnare"],
], "«TAB» — Le regole della consegna")

S4 = p("Per ogni terminale di " + c("terminali_utente") + ", " + c("testo_terminale") + " formatta il messaggio "
       "nella lingua di chi usa quel terminale (" + c("lingua_terminale") + ": l'ambiente del primo processo del "
       "terminale; se root non può leggerlo, lo legge l'utente stesso), con un ritorno a capo " + c("\\r")
       + " a fine riga (il terminale può essere in modo grezzo, per esempio dentro un editor), e "
       + c("scrivi_terminale") + " lo scrive: apre il terminale (" + c("O_NONBLOCK") + ", " + c("O_NOCTTY")
       + "), controlla con " + c("fstat") + " che il terminale <b>aperto</b> sia un dispositivo a caratteri del "
       "destinatario, e scrive per al più 3 secondi. Il controllo sul terminale aperto, e non sul nome " + c("/dev/pts/N") + ", chiude la gara "
       "in cui fra la ricerca e la scrittura quel numero passa a un altro utente; un terminale bloccato non ferma "
       "l'invio. Prima di ogni consegna l'invio controlla " + c("sent/ID/revoked") + ": un ritiro lo ferma. Il numero di "
       "terminali scritti finisce in " + c("sent/ID/delivery") + ". Scrivere su un terminale non vale come conferma: il "
       "messaggio resta nella casella, e la domanda arriva al prompt successivo.", lead=True)

WAKE = seq([("ams send", "root", "navy"), ("figlio (come U)", "", "dark"), ("Agente di U", "ppoll", "blue"),
            ("systemd --user", "di U", "soft")], [
    (0, 0, "sessione_grafica U?"),
    (0, 1, "ams-agent.pronto, /proc/PID/cmdline"),
    (1, 2, "kill SIGUSR1: l'attesa si interrompe"),
    (2, 2, "controlla subito la casella"),
    ("sep", "se nessun agente risponde"),
    (0, 3, "systemd-run --user --machine=U@.host --collect ams-user agent"),
    (3, 2, "avvia l'agente con l'ambiente grafico"),
], "«FIG» — La sveglia dell'agente del desktop", "Sveglia o avvio dell'agente")

S5 = p("Dopo aver scritto la casella, " + c("sveglia_agente U") + " fa comparire subito la finestra.", lead=True) + WAKE + ul([
    "Il segnale va solo a un agente <b>pronto</b>: quello il cui PID è in " + c("/run/user/UID/ams-agent.pronto")
    + ", scritto dall'agente dopo aver preparato la ricezione del segnale (la prima istruzione di " + c("main")
    + "). Nel prototipo un agente svegliato mentre partiva moriva (20 su 20 in una prova): " + c("SIGUSR1")
    + " per difetto termina il processo.",
    "Il segnale parte da un figlio <b>con l'identità di U</b>, e solo se la riga di comando del PID è "
    "<b>esattamente</b> quella dell'agente (" + c(".../ams-user agent") + "): non può raggiungere processi d'altri, né un "
    "processo di U che avesse ereditato un PID vecchio.",
    "Se non c'è un agente pronto, " + c("systemd-run --user") + " ne avvia uno nel gestore utente di systemd, che "
    "conosce già l'ambiente grafico. Se un agente stava partendo, il nuovo trova il lock ed esce; quello che partiva "
    "legge comunque la casella al primo giro.",
])

S6 = table(["Tolto", "Esempio", "Perché"], [
    ["sequenze CSI", c("ESC [ 31 m"), "colori, movimenti del cursore, cancellazioni"],
    ["sequenze OSC", c("ESC ] 0 ; titolo BEL"), "titolo della finestra, collegamenti, appunti"],
    ["caratteri di controllo C0", "tranne tabulazione e a capo", "campanello, ritorno carrello, escape isolati"],
    [c("DEL"), c("0x7F"), "cancellazioni"],
    ["caratteri C1 in UTF-8", c("C2 80") + " … " + c("C2 9F"), "alcuni terminali li interpretano come comandi"],
], "«TAB» — Cosa toglie pulisci, nell'ordine") + \
    p(c("pulisci") + " di " + c("src/testo.c") + " si applica a testo e titolo prima di salvarli, alle conferme che "
      + c("ams status") + " legge dalle caselle e alle righe di " + c("ams log") + ". Dà esattamente lo stesso "
      "risultato del prototipo in bash (" + c("sed") + " e " + c("tr") + "): confrontati su 2000 testi casuali pieni "
      "di sequenze e caratteri di controllo prima di togliere il prototipo.")

EV = p("Ogni fatto rilevante diventa un <b>evento strutturato</b> nel journal (" + c("evento") + ", con "
       + c("sd_journal_send") + "): il testo leggibile per " + c("journalctl -t ams") + " più i campi "
       + c("AMS_EVENTO") + ", " + c("AMS_MESSAGGIO") + ", " + c("AMS_UTENTE") + ", " + c("AMS_CANALE") + ", "
       + c("AMS_DETTAGLI") + " (destinatari, terminali scritti, durata, errore) e " + c("AMS_AUTORE")
       + " (l'amministratore). Il journal aggiunge da sé " + c("_UID") + ": un evento scritto da un utente porta il "
       "suo UID vero. Il testo leggibile è nella lingua del sistema (" + c("/etc/default/locale") + " o "
       + c("/etc/locale.conf") + "), uguale per tutti.", lead=True) + \
    table(["Evento", "Chi lo scrive", "Quando"], [
        [c("INVIATO"), "ams (root)", "alla fine di " + c("ams send")],
        [c("CONSEGNATO"), "ams (root)", "per ogni copia scritta e verificata, anche dal recupero"],
        [c("NON_CONSEGNATO"), "ams (root)", "copia non scritta"],
        [c("RECUPERATO") + ", " + c("ANNULLATO"), "ams (root)", "recupero di un invio interrotto"],
        [c("RITIRATO"), "ams (root)", c("ams revoke")],
        [c("CANCELLATO"), "ams (root)", c("ams purge") + ": messaggio tolto dall'archivio"],
        [c("RINVIATO"), "ams-user (utente)", "«Più tardi» o «no»"],
        [c("CONFERMATO") + ", " + c("CONFERMA_FALLITA"), "ams-user (utente)", "conferma registrata o non registrabile"],
    ], "«TAB» — Gli eventi nel journal") + \
    p(c("ams log ID") + " mostra gli eventi di un messaggio dalla sua data di invio (un archivio azzerato riusa i "
      "numeri, il journal no), letti con " + c("sd_journal") + " e riscritti dai campi " + c("AMS_*") + " nella lingua "
      "di chi lo lancia. Un evento scritto dall'utente sbagliato (" + c("_UID") + " diverso da root per gli eventi "
      "dell'amministratore, o dal destinatario per rinvii e conferme) è segnalato come non attendibile. Per un audit: " + c("journalctl AMS_MESSAGGIO=12 -o verbose") + " mostra tutti i "
      "campi, " + c("_UID") + " compreso.")

S7 = p(c("ams list") + " e " + c("ams status") + " leggono " + c("sent/") + " e chiamano " + c("stato_destinatario")
       + " per ogni destinatario. Le caselle si leggono <b>una volta per utente</b>: un solo figlio con l'identità "
       "dell'utente restituisce tutte le conferme (prima riga, al più 200 byte, solo da file normali) e le date dei "
       "rinvii (" + c("leggi_casella") + "), ripulite con " + c("pulisci") + " e controllate lato root; le consegne si "
       "leggono una volta per messaggio (" + c("leggi_consegne") + "). Con 10 messaggi a 58 destinatari " + c("ams list")
       + " impiega circa 0,4 s (circa 6 s nella prima versione del prototipo). " + c("leggi_casella")
       + " cerca solo i messaggi che esistono in " + c("sent/") + " (non tutto ciò che c'è nella casella: migliaia di "
       "file finti in " + c("acks/") + " non rallentano) e ha un tempo massimo di 20 s. " + c("ams list")
       + " legge ciò che gli serve di ogni messaggio prima di usarlo e salta un messaggio sparito nel frattempo. "
       + c("ams revoke") + " scrive " + c("sent/ID/ritiro") + " e " + c("sent/ID/revoked") + " (su disco), attende "
       "il lock di un invio in corso, poi toglie " + c("inbox/ID") + " e i rinvii da ogni casella, come l'utente, e "
       "infine " + c("ritiro") + ": finestre e domande aperte se ne accorgono entro un secondo (capitoli 6.3 e 7.2); "
       "se una casella non si raggiunge, " + c("ritiro") + " resta e il comando successivo riprova. "
       + c("ams purge DURATA") + " cancella i messaggi inviati prima di quel tempo: rinomina " + c("sent/ID")
       + " in " + c("sent/.cancella-ID") + " (da lì il messaggio non esiste più per nessun comando), poi, con "
       "l'identità di ogni destinatario, toglie copie, conferme e rinvii e infine la cartella; salta gli invii "
       "incompleti o con il lock occupato, e una cancellazione interrotta la completa il comando successivo. "
       "I dettagli di concorrenza e interruzioni sono nella specifica (capitolo 14).", lead=True)

CHAPTER = ("L'invio: ams", [
    ("Avvio e rilancio con sudo", S1),
    ("Destinatari e sessioni", S2),
    ("Scrivere nelle caselle: come_utente", S3),
    ("Consegna verificata e recupero", SD),
    ("Scrivere nei terminali", S4),
    ("Svegliare l'agente del desktop", S5),
    ("Pulizia del testo", S6),
    ("Il registro degli eventi", EV),
    ("list, status, revoke", S7),
])
