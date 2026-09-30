from build import arrow, box, c, code, fig, p, path, table, text, tree

S1 = p("L'archivio è fatto di file e cartelle. Una parte appartiene a root, una parte a ciascun utente: il confine "
       "tra le due è il cuore della sicurezza di AMS.", lead=True) + tree([
    "/var/lib/ams/                   # root 755",
    "├── sent/                       # root 700 · solo root",
    "│   ├── .seq  .seq.lock         # ultimo ID assegnato, lock per flock",
    "│   └── 12/",
    "│       ├── msg                 # il messaggio (copia di riferimento)",
    "│       ├── recipients          # un destinatario per riga",
    "│       ├── delivery            # «utente data terminali-scritti» per ogni copia consegnata",
    "│       ├── incomplete          # solo durante l'invio, o se non è stato completato",
    "│       ├── lock                # tenuto da ams send finché consegna (flock)",
    "│       ├── failed              # invio interrotto prima del salvataggio: annullato",
    "│       └── revoked             # data del ritiro, se ritirato",
    "└── users/                      # root 755",
    "    └── mario/                  # mario 700 · la casella: solo Mario e root",
    "        ├── inbox/12            # da mostrare",
    "        ├── read/11             # confermati o scaduti",
    "        ├── acks/11             # «data canale» della conferma",
    "        └── state/12.term       # rinvio: conta la data di modifica del file",
], "«FIG» — L'archivio, con il messaggio 12 ancora da confermare e l'11 confermato")

S2 = p("Un messaggio è un file di testo: un'intestazione " + c("chiave: valore") + ", una riga vuota, il testo.",
       lead=True) + code("""format: 1
id: 12
from: admin
date: 1790714288
title: Manutenzione
expires: 1790800688

Sabato dalle 8 alle 12 il server sarà spento.""", "text", "sent/12/msg") + table(["Campo", "Contenuto"], [
    [c("format"), "versione del formato: 1. Chi legge ignora le chiavi che non conosce; un formato diverso "
     "va letto con un'implementazione che lo conosce"],
    [c("id"), "numero progressivo, da " + c("next_id")],
    [c("from"), c("SUDO_USER") + ": l'amministratore che ha lanciato " + c("ams")],
    [c("date"), "secondi dall'epoca Unix"],
    [c("title"), "titolo, eventualmente vuoto, su una sola riga"],
    [c("expires"), "secondi dall'epoca Unix; vuoto: nessuna scadenza"],
], "«TAB» — L'intestazione di un messaggio") + \
    p("Le funzioni " + c("ams_msg_get") + ", " + c("ams_msg_body") + ", " + c("ams_msg_expired") + ", "
      + c("ams_msg_heading") + " e " + c("ams_msg_term") + " di " + c("lib/ams-common.sh") + " leggono e formattano "
      "questo formato. " + c("next_id") + " incrementa " + c("sent/.seq") + " tenendo un " + c("flock") + " su "
      + c(".seq.lock") + ": due invii contemporanei non ottengono lo stesso numero.")

FILES = fig(
    box(20, 110, 150, 58, "inbox/ID", "da mostrare", "light")
    + box(330, 40, 170, 58, "acks/ID", "conferma: data canale", "green")
    + box(330, 180, 170, 58, "state/ID.term|gui", "rinvio per canale", "amber")
    + box(660, 110, 200, 58, "read/ID", "confermato o scaduto", "dark")
    + path([(172, 128), (250, 128), (250, 69), (328, 69)], "#16a34a", False, "ack()", 250, 118)
    + arrow(502, 69, 658, 128, "#16a34a", False, "mark_read", 560, 88)
    + path([(172, 150), (250, 150), (250, 209), (328, 209)], "#d97706", False, "snooze()", 250, 172)
    + path([(330, 238), (95, 238), (95, 170)], "#d97706", True, "dopo AMS_REMIND_MINUTES", 212, 256)
    + path([(95, 108), (95, 18), (760, 18), (760, 108)], "#475569", True, "scaduto", 430, 12),
    900, 276, "«FIG» — Come si muove un messaggio nella casella dell'utente", "")

S3 = p("Lo stato di un destinatario, uno dei tre (inviato, consegnato, confermato), non è scritto da nessuna parte: si deduce dai file.", lead=True) + FILES + \
    table(["Condizione", "Stato (recipient_state)", "Come appare in ams status"], [
        ["nessuna riga in " + c("sent/ID/delivery"), c("inviato"), "inviato, non consegnato (con la causa, se " + c("incomplete") + ")"],
        [c("acks/ID") + " con data dopo la scadenza di " + c("sent/ID/msg"), c("consegnato tardiva"),
         "consegnato, non confermato (scaduto; conferma arrivata dopo la scadenza)"],
        [c("acks/ID") + " esiste", c("confermato DATA CANALE"), "confermato il … (canale)"],
        ["altrimenti", c("consegnato"), "consegnato; dettagli: terminali scritti (da " + c("delivery") + "), «rimandato il …» (data "
         "di " + c("state/ID.*") + "), «non confermato (scaduto)» o «(ritirato)»"],
    ], "«TAB» — Lo stato dedotto dai file")

S4 = table(["Percorso", "Proprietario", "Permessi", "Perché"], [
    [c("/var/lib/ams"), "root", c("755"), "attraversabile da tutti per raggiungere la propria casella"],
    [c("sent/"), "root", c("700"), "messaggi e destinatari visibili solo agli amministratori"],
    [c("users/"), "root", c("755"), "solo root crea le caselle: un utente non può crearne o spostarne"],
    [c("users/U/"), "U", c("700"), "solo U (e root) entra nella casella; U scrive le conferme"],
    [c("users/U/inbox") + ", " + c("read") + ", …", "U", "secondo la umask di U", "creati da U con " + c("runuser") + "; protetti dalla cartella " + c("700")],
], "«TAB» — Proprietari e permessi") + \
    p("Un utente può cancellare o modificare i file della propria casella: rovina solo la propria copia. La copia di "
      "riferimento resta in " + c("sent/") + ", e un messaggio cancellato risulta semplicemente non confermato.")

CHAPTER = ("L'archivio dei messaggi", [
    ("Struttura", S1),
    ("Formato di un messaggio", S2),
    ("Stati e movimenti", S3),
    ("Proprietari e permessi", S4),
])
