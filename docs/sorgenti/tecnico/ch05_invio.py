from build import arrow, box, c, diamond, fig, flow, note, p, path, seq, table, text, ul, zone

S1 = flow([("Libreria", "AMS_LIB o accanto a sé", "dark"), ("Root?", "altrimenti exec sudo", "navy"),
           ("Guida, versione", "help, --help, version", "blue"), ("Comando", "send, list, status, revoke", "blue")],
          "«FIG» — L'avvio di bin/ams") + \
    p(c("bin/ams") + " gira con " + c("set -euo pipefail") + ". Carica la libreria da " + c("AMS_LIB") + " (o da "
      + c("../lib") + " accanto a sé, nel repository) e, se non è root e " + c("AMS_TEST") + " non è impostata, "
      "si rilancia con " + c('exec sudo -- "$(readlink -f "$0")" "$@"') + ". Solo dopo guarda il comando: guida e "
      "versione comprese, nulla gira senza root. Un comando sconosciuto termina con " + c("ams_die") + ".")

S2 = table(["Funzione", "Cosa restituisce"], [
    [c("resolve_recipients DEST"), "divide " + c("DEST") + " sulle virgole, risolve ogni parte e toglie i doppioni; un nome "
     "inesistente è un errore"],
    [c("human_users"), "gli utenti con UID fra " + c("UID_MIN") + " e " + c("UID_MAX") + " di " + c("/etc/login.defs")
     + " (predefiniti 1000 e 60000) e una shell che non finisce con " + c("nologin") + " o " + c("false")],
    [c("online_users"), "gli utenti di " + c("human_users") + " con almeno una sessione logind di classe " + c("user")
     + ": root e gli account di sistema restano esclusi anche se collegati (difetto trovato dalla VM di prova, "
     "scenario B5)"],
    [c("group_members G"), "i membri elencati nel gruppo più gli utenti che hanno G come gruppo principale"],
    [c("user_sessions U"), "le sessioni " + c("user") + " di U, con tipo e terminale da " + c("loginctl show-session")],
    [c("user_terminals U"), "gli pseudo-terminali in " + c("/dev/pts") + " di proprietà di U, più le console delle sue "
     "sessioni di tipo " + c("tty")],
    [c("has_graphical_session U"), "vero se U ha una sessione " + c("x11") + " o " + c("wayland")],
], "«TAB» — Destinatari e sessioni")

SYMLINK = fig(
    zone(20, 44, 420, 214, "Senza as_user: root scrive direttamente", "#fdf2f2")
    + box(44, 84, 150, 54, "ams (root)", "cat > inbox/12", "navy")
    + box(262, 84, 156, 54, "users/mario/inbox", "sostituita da Mario…", "amber")
    + box(262, 176, 156, 54, "/etc", "…con un collegamento", "grey")
    + arrow(196, 111, 260, 111, "#b91c1c")
    + arrow(340, 140, 340, 174, "#b91c1c", True, "segue il link", 390, 160)
    + text(230, 250, "root scriverebbe in /etc", 11.5, "#b91c1c", "700")
    + zone(470, 44, 410, 214, "Con as_user: runuser -u mario", "#f0fdf4")
    + box(494, 84, 150, 54, "ams (root)", "as_user mario …", "navy")
    + box(704, 84, 156, 54, "processo di mario", "cat > inbox/12", "light")
    + box(704, 176, 156, 54, "/etc", "permesso negato", "grey")
    + arrow(646, 111, 702, 111, "#16a34a")
    + arrow(782, 140, 782, 174, "#475569", True)
    + text(675, 250, "il peggio: Mario rovina la sua casella", 11.5, "#166534", "700"),
    900, 276, "«FIG» — Perché root accede alle caselle con l'identità dell'utente", "Il pericolo dei collegamenti simbolici")

S3 = p("La casella " + c("users/U") + " appartiene all'utente, che può sostituirne le cartelle con collegamenti "
       "simbolici. Se root ci scrivesse direttamente, seguirebbe il collegamento e potrebbe scrivere ovunque. Per questo "
       "ogni accesso di root alle caselle passa da " + c("as_user U comando…") + ", cioè " + c("runuser -u U -- comando…")
       + ".", lead=True) + SYMLINK + ul([
        "Solo la cartella " + c("users/U") + " è creata da root, dentro " + c("users/") + " che appartiene a root, e poi "
        "ceduta a U; le sottocartelle le crea U.",
        "Il messaggio viene scritto in " + c("inbox/ID.tmp") + " e poi rinominato: " + c("ams-user") + " non vede mai un "
        "file a metà.",
        c("revoke") + " toglie i file come U; " + c("status") + " legge le conferme come U (capitolo 8.2).",
    ])

RECOVER = seq([("ams send", "root", "navy"), ("sent/ID", "", "dark"), ("Casella U1", "", "blue"), ("Casella U2", "", "blue"),
               ("ams (dopo)", "qualunque comando", "light")], [
    (0, 1, "incomplete, msg, recipients"),
    (0, 2, "copia, verifica"),
    (0, 1, "delivery: U1"),
    ("sep", "interruzione: U2 non ha la copia"),
    (4, 1, "recover: incomplete?"),
    (4, 3, "copia mancante, verifica"),
    (4, 1, "delivery: U2; toglie incomplete"),
], "«FIG» — Un invio interrotto viene completato dal comando successivo", "Consegna verificata e recupero")

SD = p("L'invio è una sequenza di passi; se si interrompe a metà, il comando " + c("ams") + " successivo lo completa.",
       lead=True) + RECOVER + table(["Regola", "Come"], [
    ["l'invio si vede finché non è completo", c("sent/ID/incomplete") + " nasce prima di tutto e sparisce solo quando ogni "
     "destinatario ha la sua copia"],
    [c("msg") + " e " + c("recipients") + " sono interi o assenti", "scritti in un file temporaneo e rinominati"],
    ["«consegnato» vuol dire copia verificata", c("deliver_copy") + " scrive la copia come l'utente e controlla che esista; "
     "solo allora la riga va in " + c("delivery")],
    ["un guasto non ferma gli altri destinatari", "la copia non scritta viene annotata nel registro; " + c("ams send")
     + " prosegue, poi termina con errore e lascia " + c("incomplete")],
    ["il recupero è idempotente", c("recover") + " gira all'avvio di " + c("send") + ", " + c("list") + ", " + c("status")
     + ", " + c("revoke") + " e consegna solo le copie mancanti; non riscrive la copia a chi l'ha già letta o confermata"],
    ["un invio in corso non è un invio interrotto", c("ams send") + " tiene " + c("flock") + " su " + c("sent/ID/lock")
     + " per tutta la consegna; " + c("recover") + " salta i messaggi con il lock occupato. Se " + c("ams send")
     + " muore, anche con SIGKILL, il kernel rilascia il lock. Senza questa regola il recupero, lanciato durante un "
     "invio lungo, consegnava in parallelo e annotava doppioni (trovato dalla suite dal vero, scenario F3)"],
    ["un invio non salvato si annulla", "senza " + c("msg") + " o " + c("recipients") + ", e con il lock libero, il "
     "messaggio diventa " + c("failed") + " e viene segnalato"],
    ["ritirati e scaduti non si completano", c("recover") + " toglie il segno senza consegnare"],
], "«TAB» — Le regole della consegna")

S4 = p("Per ogni terminale di " + c("user_terminals") + ", " + c("ams_msg_term") + " formatta il messaggio, " + c("sed")
       + " aggiunge un ritorno a capo " + c("\\r") + " a fine riga (il terminale può essere in modo grezzo, per esempio "
       "dentro un editor) e " + c("timeout 3 tee") + " lo scrive: un terminale bloccato non ferma l'invio. Il numero di "
       "terminali scritti finisce in " + c("sent/ID/delivery") + ". Scrivere su un terminale non vale come conferma: il "
       "messaggio resta nella casella, e la domanda arriva al prompt successivo.", lead=True)

WAKE = seq([("ams send", "root", "navy"), ("pkill (come U)", "", "dark"), ("Agente di U", "sleep & wait", "blue"),
            ("systemd --user", "di U", "soft")], [
    (0, 0, "has_graphical_session U?"),
    (0, 1, "runuser -u U pkill -USR1 -f ^…ams-user agent$"),
    (1, 2, "SIGUSR1: wait si interrompe"),
    (2, 2, "controlla subito la casella"),
    ("sep", "se nessun agente risponde"),
    (0, 3, "systemd-run --user --machine=U@.host --collect ams-user agent"),
    (3, 2, "avvia l'agente con l'ambiente grafico"),
], "«FIG» — La sveglia dell'agente del desktop", "Sveglia o avvio dell'agente")

S5 = p("Dopo aver scritto la casella, " + c("wake_agent U") + " fa comparire subito la finestra.", lead=True) + WAKE + ul([
    "Il segnale va solo a un agente <b>pronto</b>: quello il cui PID è in " + c("/run/user/UID/ams-agent.pronto")
    + ", scritto dall'agente dopo aver preparato la ricezione del segnale. Un agente svegliato mentre partiva moriva "
    "(20 su 20 in una prova): bash non ha ancora letto la prima riga, e " + c("SIGUSR1") + " per difetto termina il "
    "processo.",
    "Il segnale parte con " + c("pkill -F ams-agent.pronto") + " eseguito <b>come U</b> e sulla riga di comando "
    "<b>esatta</b> dell'agente (" + c("^/bin/bash …/ams-user agent$") + "): non può raggiungere processi d'altri, né un "
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
], "«TAB» — Cosa toglie ams_sanitize, nell'ordine") + \
    p(c("ams_sanitize") + " si applica a testo e titolo prima di salvarli, e alle conferme che " + c("ams status")
      + " legge dalle caselle.")

EV = p("Ogni fatto rilevante diventa un <b>evento strutturato</b> nel journal (" + c("ams_event") + ", con "
       + c("logger --journald") + "): il testo leggibile per " + c("journalctl -t ams") + " più i campi "
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
      "numeri, il journal no), riscritti dai campi " + c("AMS_*") + " nella lingua di chi lo lancia; legge solo quei "
      "campi (" + c("--output-fields") + "), perché i campi binari del formato " + c("export") + " spezzerebbero "
      "la lettura per righe. Per un audit: " + c("journalctl AMS_MESSAGGIO=12 -o verbose") + " mostra tutti i "
      "campi, " + c("_UID") + " compreso.")

S7 = p(c("ams list") + " e " + c("ams status") + " leggono " + c("sent/") + " e chiamano " + c("recipient_state")
       + " per ogni destinatario. Le caselle si leggono <b>una volta per utente</b>: un solo " + c("runuser")
       + " restituisce tutte le conferme e le date dei rinvii (" + c("load_user") + "), ripulite con " + c("ams_sanitize")
       + " e controllate lato root; le consegne si leggono una volta per messaggio (" + c("load_delivery") + "). Con 10 "
       "messaggi a 54 destinatari " + c("ams list") + " è passato da circa 6 s a circa 0,7 s. " + c("ams revoke") + " scrive " + c("sent/ID/revoked") + " e toglie " + c("inbox/ID")
       + " e i rinvii da ogni casella, come l'utente: finestre e domande aperte se ne accorgono entro un secondo "
       "(capitoli 6.3 e 7.2). " + c("ams purge DURATA") + " cancella i messaggi inviati prima di quel tempo: la cartella in "
       + c("sent/") + " e, con l'identità di ogni destinatario, copie, conferme e rinvii nella sua casella; salta "
       "gli invii incompleti o con il lock occupato.", lead=True)

CHAPTER = ("L'invio: ams", [
    ("Avvio e rilancio con sudo", S1),
    ("Destinatari e sessioni", S2),
    ("Scrivere nelle caselle: as_user", S3),
    ("Consegna verificata e recupero", SD),
    ("Scrivere nei terminali", S4),
    ("Svegliare l'agente del desktop", S5),
    ("Pulizia del testo", S6),
    ("Il registro degli eventi", EV),
    ("list, status, revoke", S7),
])
