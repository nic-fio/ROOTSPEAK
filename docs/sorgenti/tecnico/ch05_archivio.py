from build import arrow, box, c, code, fig, note, p, path, seq, table, text, tree, ul, warn, zone


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


S1 = p("L'archivio è fatto di file e cartelle sotto " + c("/var/lib/ams") + ". Una parte appartiene a root, una "
       "parte a ciascun utente: il confine tra le due è il cuore della sicurezza di AMS. Non c'è un database né un "
       "indice: ogni informazione sta in un file che si può leggere con " + c("cat") + ".", lead=True) + tree([
    "/var/lib/ams/                   # root 755",
    "├── sent/                       # root 700 · solo root",
    "│   ├── .seq  .seq.lock         # ultimo ID assegnato; lock per flock",
    "│   ├── 12/",
    "│   │   ├── msg                 # il messaggio (copia di riferimento)",
    "│   │   ├── recipients          # un destinatario per riga",
    "│   │   ├── delivery            # «utente data terminali» per ogni copia consegnata",
    "│   │   ├── lock                # tenuto da ams send finché consegna (flock)",
    "│   │   ├── incomplete          # segno: invio in corso o da completare",
    "│   │   ├── revoked             # data del ritiro, se ritirato",
    "│   │   ├── ritiro              # segno: copie ritirate ancora da togliere",
    "│   │   └── failed              # segno: invio interrotto prima del salvataggio",
    "│   └── .cancella-9/            # un messaggio che ams purge sta cancellando",
    "└── users/                      # root 755",
    "    └── mario/                  # mario 700 · la casella: solo Mario e root",
    "        ├── inbox/12            # da mostrare",
    "        ├── read/11             # confermati o scaduti",
    "        ├── acks/11             # «data canale» della conferma",
    "        └── state/12.term       # rinvio: conta la data di modifica del file",
], "«FIG» — L'archivio, con il messaggio 12 ancora da confermare e l'11 confermato") + \
    note("i file " + c("incomplete") + ", " + c("ritiro") + " e " + c("failed") + " sono <b>segni interni del "
         "recupero</b>: dicono che un'operazione va completata o è stata annullata. Non sono stati di un messaggio né "
         "di un destinatario, e nessun comando li mostra come tali (" + cap(20, 2) + ").")

S2 = p("Un messaggio è un file di testo UTF-8: un'intestazione " + c("chiave: valore") + ", una riga vuota, il testo. "
       "Lo stesso file, byte per byte, è la copia di riferimento in " + c("sent/ID/msg") + " e la copia nella casella "
       "di ogni destinatario.", lead=True) + code("""format: 1
id: 12
from: admin
date: 1790714288
title: Manutenzione
expires: 1790800688

Sabato dalle 8 alle 12 il server sarà spento.""", "text", "sent/12/msg") + table(["Campo", "Contenuto"], [
    [c("format"), "versione del formato: 1. Chi legge ignora le chiavi che non conosce; un formato diverso va letto "
     "con un'implementazione che lo conosce"],
    [c("id"), "numero progressivo, da " + c("prossimo_id")],
    [c("from"), "l'amministratore: " + c("SUDO_USER") + " se è un utente esistente, altrimenti l'utente che esegue "
     + c("ams")],
    [c("date"), "secondi dall'epoca Unix; <b>obbligatoria</b>: un messaggio senza data valida è rifiutato"],
    [c("title"), "titolo, eventualmente vuoto, su una sola riga (a capo e tabulazioni diventano spazi)"],
    [c("expires"), "secondi dall'epoca Unix; vuoto: nessuna scadenza"],
], "«TAB» — L'intestazione di un messaggio") + table(["Funzione (src/testo.c)", "Cosa fa"], [
    [c("msg_formatta"), "scrive l'intestazione nell'ordine della figura, poi il testo"],
    [c("msg_da_testo"), "legge riga per riga fino alla prima riga vuota; accetta anche " + c("chiave:")
     + " senza valore; ciò che segue è il testo"],
    [c("msg_leggi"), "legge un file normale, senza seguire collegamenti, al più " + c("AMS_MAX_MSG")
     + " byte (65536 + 8192), poi " + c("msg_da_testo")],
    [c("msg_scaduto"), "vero se " + c("expires") + " c'è ed è minore o uguale all'ora data"],
    [c("msg_intestazione"), "«Titolo · 29/09 22:15», oppure solo la data: la riga che precede il testo nel "
     "terminale, nella finestra e in " + c("ams status")],
], "«TAB» — Leggere e scrivere un messaggio")

SEQ = seq([("ams send A", "", "navy"), ("sent/.seq.lock", "flock esclusivo", "dark"), ("sent/", "", "soft"),
           ("ams send B", "", "navy")], [
    (0, 1, "flock: preso"),
    (3, 1, "flock: attende", True),
    (0, 2, ".seq = 11 → mkdir 12"),
    (0, 2, ".seq ← 12 (scrivi_atomico)"),
    (0, 1, "rilascia"),
    (3, 2, ".seq = 12 → mkdir 13"),
], "«FIG» — Due invii contemporanei ottengono numeri diversi", "Numeri progressivi")

S3 = p("Ogni messaggio ha un numero progressivo. " + c("prossimo_id") + " di " + c("src/ams.c") + " lo prende sotto "
       "un " + c("flock") + " esclusivo su " + c("sent/.seq.lock") + ": due " + c("ams send") + " contemporanei non "
       "ottengono lo stesso numero.", lead=True) + SEQ + ul([
    "Legge l'ultimo numero da " + c("sent/.seq") + " (0 se manca o non è un numero), lo incrementa e crea la "
    "cartella con " + c("mkdir(…, 0700)") + ".",
    "Se la cartella esiste già, passa al numero successivo: succede se " + c(".seq") + " è tornato indietro, per "
    "esempio dopo un'interruzione di corrente che ha perso l'ultima scrittura. Nessun messaggio viene mai "
    "sovrascritto.",
    "Scrive il nuovo valore con " + c("scrivi_atomico") + " e rilascia il lock chiudendo il descrittore.",
    "Un numero preso e mai usato (un'interruzione subito dopo) resta un buco nella numerazione: innocuo.",
])

S4 = table(["Percorso", "Proprietario", "Permessi", "Perché"], [
    [c("/var/lib/ams"), "root", c("755"), "attraversabile da tutti per raggiungere la propria casella"],
    [c("sent/"), "root", c("700"), "messaggi e destinatari visibili solo agli amministratori"],
    [c("sent/ID/"), "root", c("700"), "creata da " + c("prossimo_id")],
    [c("sent/ID/*"), "root", c("600"), "scritti da " + c("ams") + " con " + c("O_NOFOLLOW")],
    [c("users/"), "root", c("755"), "solo root crea le caselle: un utente non può crearne né spostarne"],
    [c("users/U/"), "U", c("700"), "creata da root e ceduta a U; solo U (e root) vi entra"],
    [c("users/U/inbox") + ", " + c("read") + ", " + c("acks") + ", " + c("state"), "U", c("755"),
     "create da U, in un figlio con la sua identità; protette dalla cartella " + c("700")],
    [c("inbox/ID") + ", " + c("acks/ID") + ", " + c("state/ID.*"), "U", c("644"), "scritti da U"],
], "«TAB» — Proprietari e permessi") + \
    p("Un utente può cancellare o modificare i file della propria casella: rovina solo la propria copia. La copia di "
      "riferimento resta in " + c("sent/") + ", e un messaggio cancellato dalla casella risulta semplicemente non "
      "confermato. Una conferma scritta a mano resta una dichiarazione dell'utente (" + cap(20, 1) + ").") + \
    warn("i permessi effettivi dei file creati da U dipendono anche dalla umask del processo: il figlio di "
         + c("come_utente") + " la imposta a " + c("022") + ", " + c("ams-user") + " usa quella della sessione "
         "dell'utente. La protezione vera è la cartella " + c("users/U") + " a " + c("700") + ".")

ATOM = fig(
    box(20, 60, 170, 56, "path.tmp", "O_EXCL, O_NOFOLLOW", "light", 12)
    + box(250, 60, 150, 56, "scrivi_tutto", "anche le parziali", "blue")
    + box(460, 60, 120, 56, "fsync", "su disco", "blue")
    + box(640, 60, 110, 56, "rename", "atomico", "green")
    + box(790, 60, 90, 56, "path", "intero", "green")
    + arrow(192, 88, 248, 88) + arrow(402, 88, 458, 88) + arrow(582, 88, 638, 88) + arrow(752, 88, 788, 88)
    + path([(515, 118), (515, 160), (105, 160), (105, 118)], "#b91c1c", True, "errore: unlink(path.tmp)", 310, 176),
    900, 196, "«FIG» — scrivi_atomico: chi legge vede il file vecchio o quello nuovo, mai uno a metà",
    "Scrittura atomica")

S5 = p("Tutto l'I/O su file passa da poche funzioni di " + c("src/comune.c") + " con regole fisse. Sono le "
       "funzioni che rendono sicuro leggere ciò che scrivono gli utenti e che garantiscono la durata dopo "
       "un'interruzione.", lead=True) + table(["Funzione", "Regola"], [
    [c("leggi_file(path, max, nofollow, out)"), "apre con " + c("O_NONBLOCK") + " (una pipe non blocca l'apertura) e, "
     "se chiesto, " + c("O_NOFOLLOW") + "; rifiuta ciò che non è un file normale e i file più grandi di " + c("max")],
    [c("leggi_fd(fd, max, out)"), "legge fino alla fine, tiene al più " + c("max") + " byte e scarta il resto"],
    [c("scrivi_tutto(fd, p, n)"), "ripete dopo le scritture parziali e le interruzioni da segnale"],
    [c("scrivi_atomico(path, p, n, mode)"), "scrive " + c("path.tmp") + " (" + c("O_EXCL|O_NOFOLLOW") + "), "
     + c("fsync") + ", rinomina; in caso d'errore toglie il temporaneo"],
    [c("sync_path") + ", " + c("syncfs_path"), c("fsync") + " di un file o di una cartella; " + c("syncfs")
     + " del file system che la contiene"],
    [c("esiste") + ", " + c("e_cartella"), "con " + c("lstat") + ": un collegamento simbolico non è la cartella a cui "
     "punta"],
    [c("elenca_numeri(dir, out)"), "solo nomi fatti di cifre (al più 18), in ordine numerico"],
    [c("leggi_numero(s, out)"), "solo cifre, al più 18: nessun segno, nessuno spazio, nessun trabocco"],
], "«TAB» — Le regole dell'I/O") + ATOM + \
    p("Ogni descrittore è aperto con " + c("O_CLOEXEC") + ": nessun file aperto passa ai programmi lanciati da AMS "
      "(zenity, sudo, systemd-run, l'editor). La memoria si chiede con " + c("xmalloc") + " e i testi crescono in un "
      + c("buf_t") + " (" + cap(24, 5) + "): nessun buffer di lunghezza fissa riceve dati che vengono da fuori.")

S6 = p("AMS non ha un comando di salvataggio né di ripristino: l'archivio è fatto di file, e i soli strumenti "
       "previsti sono la pulizia dei messaggi vecchi (" + c("ams purge") + ", " + cap(9, 3) + ") e la rimozione "
       "completa (" + c("install.sh --purge") + ").", lead=True) + table(["Cosa", "Dove", "Nota"], [
    ["messaggi, destinatari, consegne, ritiri", c("/var/lib/ams/sent/"), "autorevoli; solo root"],
    ["copie, conferme, rinvii", c("/var/lib/ams/users/"), "di ciascun utente; le conferme sono lo stato"],
    ["storia degli eventi", "journal di sistema", "conservata secondo le regole del journal, non di AMS"],
    ["configurazione", c("/etc/ams/ams.conf"), "non sovrascritta dagli aggiornamenti"],
], "«TAB» — Dove stanno i dati") + ul([
    "Un archivio azzerato riusa i numeri dei messaggi, il journal no: per questo " + c("ams log ID") + " legge solo "
    "gli eventi successivi alla data d'invio del messaggio (" + cap(18, 4) + ").",
    "Una copia fatta mentre un invio è in corso contiene il segno " + c("incomplete") + ": per come è fatto il "
    "recupero (" + cap(8, 6) + "), dopo un ripristino quell'invio verrebbe completato dal primo comando " + c("ams") + ".",
]) + warn("il salvataggio e il ripristino dell'archivio non sono stati provati: chi li fa deve conservare "
          "proprietari e permessi (in particolare " + c("users/U") + " di U con " + c("700") + " e " + c("sent/")
          + " di root con " + c("700") + ").")

CHAPTER = ("L'archivio dei messaggi", [
    ("Struttura", S1),
    ("Formato di un messaggio", S2),
    ("I numeri dei messaggi", S3),
    ("Proprietari e permessi", S4),
    ("Leggere e scrivere file in sicurezza", S5),
    ("Conservare l'archivio", S6),
])
