from build import arrow, box, c, code, fig, note, p, seq, table, term, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


FLUSSO = fig(
    box(20, 40, 180, 56, "ams (root)", "send, revoke, remind…", "navy")
    + box(20, 130, 180, 56, "ams-user (U)", "postpone, confirm", "blue")
    + box(260, 84, 180, 58, "evento()", "src/evento.c", "dark")
    + box(500, 40, 180, 56, "journal", "sd_journal_send", "green")
    + box(500, 130, 180, 56, "syslog", "if the journal is missing", "soft")
    + box(740, 40, 140, 56, "journalctl", "-t ams", "light")
    + box(740, 130, 140, 56, "ams log ID", "and the TUI history", "light", 12)
    + arrow(202, 68, 258, 104) + arrow(202, 158, 258, 124)
    + arrow(442, 104, 498, 70) + arrow(442, 122, 498, 156, "#475569", True)
    + arrow(682, 68, 738, 68) + arrow(682, 80, 738, 150)
    + text(350, 218, "readable text in the system language, plus the AMS_* fields; the journal adds _UID", 11.5,
           "#475569", "600"),
    900, 236, "«FIG» — From events to the log, and back", "The log")

S1 = p("Every relevant fact in the life of a message becomes a <b>structured event</b> in the system journal. "
       "The log answers a different question from " + c("ams status") + ": not “where does it stand” but “what "
       "happened, when, and by whose hand”.", lead=True) + FLUSSO + ul([
    c("evento(EVENTO, ID, UTENTE, CANALE, DETTAGLI, AUTORE)") + " (“event(EVENT, ID, USER, CHANNEL, DETAILS, "
    "AUTHOR)”) in " + c("src/evento.c") + " writes with "
    + c("sd_journal_send") + " a readable text (" + c("MESSAGE") + ") and the structured fields. If the journal does "
    "not respond, it writes at least the text with " + c("syslog") + ".",
    "The readable text is in the <b>system language</b> (" + c("/etc/default/locale") + " or "
    + c("/etc/locale.conf") + "), the same for everyone; " + c("ams log") + " rewrites it from the fields in the "
    "reader's language (scenario L4).",
    "The details fit on a single line: line breaks become spaces.",
    "The log is the <b>history</b>, not the state: states are always derived from the message store, never from the journal ("
    + cap(20, 1) + "). Retention of the events follows the journal's rules, not those of AMS: " + c("ams purge")
    + " does not touch them.",
])

S2 = table(["Field", "Content", "Set by"], [
    [c("SYSLOG_IDENTIFIER"), c("ams") + ", for all events, including those of " + c("ams-user"), "AMS"],
    [c("MESSAGE"), "the readable text, in the system language", "AMS"],
    [c("PRIORITY"), "6 (informational)", "AMS"],
    [c("AMS_EVENTO") + " (“event”)", "the name of the event: " + c("INVIATO") + " (“sent”), " + c("CONFERMATO")
     + " (“confirmed”)…", "AMS"],
    [c("AMS_MESSAGGIO") + " (“message”)", "the message number", "AMS"],
    [c("AMS_UTENTE") + " (“user”)", "the recipient, where relevant", "AMS"],
    [c("AMS_CANALE") + " (“channel”)", c("terminale pts/N") + ", " + c("desktop") + "; for postponements "
     + c("terminale") + " (“terminal”) or " + c("desktop"), "AMS"],
    [c("AMS_DETTAGLI") + " (“details”)", "recipients, terminals written, number reminded or recovered, duration, error", "AMS"],
    [c("AMS_AUTORE") + " (“author”)", "the administrator (" + c("SUDO_USER") + ")", "AMS"],
    [c("_UID") + ", " + c("_PID") + ", time", "who actually wrote the event, and when", "the journal"],
], "«TAB» — The fields of an event") + \
    p("For an audit, " + c("journalctl AMS_MESSAGGIO=12 -o verbose") + " shows all the fields, " + c("_UID")
      + " included; " + c("journalctl -t ams") + " shows the text of all AMS events.")

S3 = table(["Event", "Written by", "When", "Text (Italian)"], [
    [c("INVIATO") + " (“sent”)", "ams (root)", "at the end of " + c("ams send") + ", after the deliveries",
     "messaggio 12 inviato da admin a: anna mario (“message 12 sent by admin to: anna mario”)"],
    [c("CONSEGNATO") + " (“delivered”)", "ams (root)", "for every copy written and verified; also by recovery",
     "messaggio 12 consegnato a mario (terminali scritti: 1) · (recupero) (“message 12 delivered to mario (terminals "
     "written: 1) · (recovery)”)"],
    [c("NON_CONSEGNATO") + " (“not delivered”)", "ams (root)", "copy not written", "messaggio 12: ERRORE, copia per "
     "anna non scritta (“message 12: ERROR, copy for anna not written”)"],
    [c("RECUPERATO") + " (“recovered”)", "ams (root)", "recovery of an interrupted sending", "messaggio 12: consegna "
     "completata per 3 destinatari dopo un'interruzione (“message 12: delivery completed for 3 recipients after an "
     "interruption”)"],
    [c("ANNULLATO") + " (“cancelled”)", "ams (root)", "recovery of a sending that was not saved", "messaggio 12: invio "
     "interrotto prima del salvataggio, annullato (“message 12: sending interrupted before it was saved, cancelled”)"],
    [c("RITIRATO") + " (“revoked”)", "ams (root)", c("ams revoke") + ", the first time", "messaggio 12 ritirato da "
     "admin (“message 12 revoked by admin”)"],
    [c("SOLLECITATO") + " (“reminded”)", "ams (root)", c("ams remind"), "messaggio 12: sollecitati 3 destinatari da "
     "admin (“message 12: 3 recipients reminded by admin”)"],
    [c("CANCELLATO") + " (“deleted”)", "ams (root)", c("ams purge") + ", at the rename", "messaggio 12 cancellato da "
     "admin (più vecchio di 90d) (“message 12 deleted by admin (older than 90d)”)"],
    [c("RINVIATO") + " (“postponed”)", "ams-user (U)", "«Più tardi» (“Later”) or an answer other than yes", "utente "
     "mario: rimandato il messaggio 12 (terminale) (“user mario: postponed message 12 (terminal)”)"],
    [c("CONFERMATO") + " (“confirmed”)", "ams-user (U)", "confirmation recorded", "utente mario: confermata la lettura "
     "del messaggio 12 (desktop) (“user mario: confirmed reading message 12 (desktop)”)"],
    [c("CONFERMA_FALLITA") + " (“confirmation failed”)", "ams-user (U)", "confirmation could not be recorded", "utente "
     "mario: ERRORE, conferma del messaggio 12 non registrata (desktop): … (“user mario: ERROR, confirmation of "
     "message 12 not recorded (desktop): …”)"],
], "«TAB» — The events")

LOG = seq([("ams log 12", "root", "navy"), ("journal", "sd_journal", "green"), ("Reader", "terminal, TUI", "light")], [
    ("nota", 0, "loads sent/12/msg: the date"),
    (0, 1, "ams and AMS_MESSAGGIO=12"),
    (0, 1, "from the sending date minus 1 s"),
    (1, 0, "one event at a time, with _UID", True),
    ("nota", 0, "_UID expected? no: «non attendibile»".ljust(37)),
    (0, 2, "text in the reader's language, cleaned"),
], "«FIG» — ams log: the history of a message, rewritten from the fields; «non attendibile» means “not trustworthy”",
   "ams log")

S4 = p(c("ams log ID") + " reconstructs the history of a message from the events, in the language of whoever runs "
       "it; the History tab of the TUI shows the same output.", lead=True) + LOG + ul([
    "Events are searched with two conditions together: " + c("SYSLOG_IDENTIFIER=ams") + " and " + c("AMS_MESSAGGIO=ID")
    + ", and only <b>from the sending date</b> of the message (minus one second): a message store that has been reset "
    "reuses the numbers, the journal does not.",
    "Anyone can write an event with the " + c("AMS_*") + " fields to the journal: " + c("_UID") + " says who "
    "wrote it, not that it is true. " + c("ams log") + " expects root (in test mode, whoever runs it) for the "
    "administrator's events and the recipient themselves for " + c("RINVIATO") + ", " + c("CONFERMATO") + " and "
    + c("CONFERMA_FALLITA") + "; if " + c("_UID") + " differs, the line begins with «[non attendibile: scritto "
    "da UID N]» (“[not trustworthy: written by UID N]” in English) (scenario J3).",
    "An event with an unknown name is shown with its " + c("MESSAGE") + "; every line goes through " + c("pulisci")
    + " before it reaches the terminal.",
]) + term("admin@server:~$ sudo ams log 1\n"
          "Messaggio 1 · Manutenzione · 30/09 20:42\n"
          "2026-09-30 20:42:25  messaggio 1 consegnato a mario (terminali scritti: 1)\n"
          "2026-09-30 20:42:25  messaggio 1 consegnato a anna (terminali scritti: 0)\n"
          "2026-09-30 20:42:25  messaggio 1 inviato da admin a: anna mario\n"
          "2026-09-30 20:43:02  utente mario: confermata la lettura del messaggio 1 (terminale pts/2)",
          "A history: «Messaggio 1 · Manutenzione» (“Message 1 · Maintenance”), «consegnato a … (terminali scritti: 1)» "
          "(“delivered to … (terminals written: 1)”), «inviato da admin a:» (“sent by admin to:”), «utente mario: "
          "confermata la lettura del messaggio 1 (terminale pts/2)» (“user mario: confirmed reading message 1 (terminal "
          "pts/2)”)") + \
    note("writing an event is a separate action from the change it records: if the journal does not respond, "
         "the state in the message store stays correct; of the history only the text written with " + c("syslog") + " remains, which "
         + c("ams log") + " does not read.")

CHAPTER = ("The event log", [
    ("Structured events in the journal", S1),
    ("The fields of an event", S2),
    ("The events", S3),
    ("ams log and trustworthiness", S4),
])
