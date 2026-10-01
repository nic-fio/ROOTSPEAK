from build import arrow, box, c, code, fig, note, p, seq, table, term, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


FLOW = fig(
    box(20, 40, 180, 56, "rspeak (root)", "send, revoke, remind…", "navy")
    + box(20, 130, 180, 56, "rootspeak-user (U)", "postpone, confirm", "blue")
    + box(260, 84, 180, 58, "event()", "src/event.c", "dark")
    + box(500, 40, 180, 56, "journal", "sd_journal_send", "green")
    + box(500, 130, 180, 56, "syslog", "if the journal is missing", "soft")
    + box(740, 40, 140, 56, "journalctl", "-t rspeak", "light")
    + box(740, 130, 140, 56, "rspeak log ID", "and the TUI history", "light", 12)
    + arrow(202, 68, 258, 104) + arrow(202, 158, 258, 124)
    + arrow(442, 104, 498, 70) + arrow(442, 122, 498, 156, "#475569", True)
    + arrow(682, 68, 738, 68) + arrow(682, 80, 738, 150)
    + text(350, 218, "readable text in English, plus the RSPEAK_* fields; the journal adds _UID", 11.5,
           "#475569", "600"),
    900, 236, "«FIG» — From events to the log, and back", "The log")

S1 = p("Every relevant fact in the life of a message becomes a <b>structured event</b> in the system journal. "
       "The log answers a different question from " + c("rspeak status") + ": not “where does it stand” but “what "
       "happened, when, and by whose hand”.", lead=True) + FLOW + ul([
    c("event(EV, ID, USER, CHANNEL, DETAILS, AUTHOR)") + " in " + c("src/event.c") + " writes with "
    + c("sd_journal_send") + " a readable text (" + c("MESSAGE") + ") and the structured fields. If the journal does "
    "not respond, it writes at least the text with " + c("syslog") + ".",
    "The readable text is in English, whatever the language of the system; " + c("rspeak log")
    + " rewrites it from the fields with the same function, " + c("event_text") + ".",
    "The details fit on a single line: line breaks become spaces.",
    "The log is the <b>history</b>, not the state: states are always derived from the message store, never from the journal ("
    + cap(19, 1) + "). Retention of the events follows the journal's rules, not those of RootSpeak: " + c("rspeak purge")
    + " does not touch them.",
])

S2 = table(["Field", "Content", "Set by"], [
    [c("SYSLOG_IDENTIFIER"), c("rspeak") + ", for all events, including those of " + c("rootspeak-user"), "RootSpeak"],
    [c("MESSAGE"), "the readable text, in English", "RootSpeak"],
    [c("PRIORITY"), "6 (informational)", "RootSpeak"],
    [c("RSPEAK_EVENT"), "the name of the event: " + c("SENT") + ", " + c("CONFIRMED") + "…", "RootSpeak"],
    [c("RSPEAK_MESSAGE"), "the message number", "RootSpeak"],
    [c("RSPEAK_USER"), "the recipient, where relevant", "RootSpeak"],
    [c("RSPEAK_CHANNEL"), c("terminal pts/N") + ", " + c("desktop") + "; for postponements "
     + c("terminal") + " or " + c("desktop"), "RootSpeak"],
    [c("RSPEAK_DETAILS"), "recipients, terminals written, number reminded or recovered, duration, error", "RootSpeak"],
    [c("RSPEAK_AUTHOR"), "the administrator (" + c("SUDO_USER") + ")", "RootSpeak"],
    [c("_UID") + ", " + c("_PID") + ", time", "who actually wrote the event, and when", "the journal"],
], "«TAB» — The fields of an event") + \
    p("For an audit, " + c("journalctl RSPEAK_MESSAGE=12 -o verbose") + " shows all the fields, " + c("_UID")
      + " included; " + c("journalctl -t rspeak") + " shows the text of all RootSpeak events.")

S3 = table(["Event", "Written by", "When", "Text"], [
    [c("SENT"), "rspeak (root)", "at the end of " + c("rspeak send") + ", after the deliveries",
     "message 12 sent by admin to: anna mario"],
    [c("DELIVERED"), "rspeak (root)", "for every copy written and verified; also by recovery",
     "message 12 delivered to mario (terminals written: 1) · message 12 delivered to mario (recovery)"],
    [c("NOT_DELIVERED"), "rspeak (root)", "copy not written", "message 12: ERROR, copy for anna not written"],
    [c("RECOVERED"), "rspeak (root)", "recovery of an interrupted sending", "message 12: delivery completed for 3 "
     "recipients after an interruption"],
    [c("CANCELLED"), "rspeak (root)", "recovery of a sending that was not saved", "message 12: sending interrupted "
     "before it was saved, cancelled"],
    [c("REVOKED"), "rspeak (root)", c("rspeak revoke") + ", the first time", "message 12 revoked by admin"],
    [c("REMINDED"), "rspeak (root)", c("rspeak remind"), "message 12: 3 recipients reminded by admin"],
    [c("DELETED"), "rspeak (root)", c("rspeak purge") + ", at the rename", "message 12 deleted by admin (older "
     "than 90d)"],
    [c("POSTPONED"), "rootspeak-user (U)", "“Later” or an answer other than yes", "user mario: postponed message 12 "
     "(terminal)"],
    [c("CONFIRMED"), "rootspeak-user (U)", "confirmation recorded", "user mario: confirmed reading message 12 "
     "(desktop)"],
    [c("CONFIRMATION_FAILED"), "rootspeak-user (U)", "confirmation could not be recorded", "user mario: ERROR, "
     "confirmation of message 12 not recorded (desktop): …"],
], "«TAB» — The events")

LOG = seq([("rspeak log 12", "root", "navy"), ("journal", "sd_journal", "green"), ("Reader", "terminal, TUI", "light")], [
    ("note", 0, "loads sent/12/msg: the date"),
    (0, 1, "rspeak and RSPEAK_MESSAGE=12"),
    (0, 1, "from the sending date minus 1 s"),
    (1, 0, "one event at a time, with _UID", True),
    ("note", 0, "_UID expected? no: not trustworthy".ljust(37)),
    (0, 2, "text rewritten from the fields, cleaned"),
], "«FIG» — rspeak log: the history of a message, rewritten from the fields",
   "rspeak log")

S4 = p(c("rspeak log ID") + " reconstructs the history of a message from the events; the History tab of the TUI shows the same output.", lead=True) + LOG + ul([
    "Events are searched with two conditions together: " + c("SYSLOG_IDENTIFIER=rspeak") + " and " + c("RSPEAK_MESSAGE=ID")
    + ", and only <b>from the sending date</b> of the message (minus one second): a message store that has been reset "
    "reuses the numbers, the journal does not.",
    "Anyone can write an event with the " + c("RSPEAK_*") + " fields to the journal: " + c("_UID") + " says who "
    "wrote it, not that it is true. " + c("rspeak log") + " expects root (in test mode, whoever runs it) for the "
    "administrator's events and the recipient themselves for " + c("POSTPONED") + ", " + c("CONFIRMED") + " and "
    + c("CONFIRMATION_FAILED") + "; if " + c("_UID") + " differs, the line begins with “[not trustworthy: written "
    "by UID N]” (scenario J3).",
    "An event with an unknown name is shown with its " + c("MESSAGE") + "; every line goes through " + c("clean_text")
    + " before it reaches the terminal.",
]) + term("admin@server:~$ sudo rspeak log 1\n"
          "Message 1 · Maintenance · 30/09 20:42\n"
          "2026-09-30 20:42:25  message 1 delivered to mario (terminals written: 1)\n"
          "2026-09-30 20:42:25  message 1 delivered to anna (terminals written: 0)\n"
          "2026-09-30 20:42:25  message 1 sent by admin to: anna mario\n"
          "2026-09-30 20:43:02  user mario: confirmed reading message 1 (terminal pts/2)",
          "A history: two deliveries, the sending and a confirmation from a terminal") + \
    note("writing an event is a separate action from the change it records: if the journal does not respond, "
         "the state in the message store stays correct; of the history only the text written with " + c("syslog") + " remains, which "
         + c("rspeak log") + " does not read.")

CHAPTER = ("The event log", [
    ("Structured events in the journal", S1),
    ("The fields of an event", S2),
    ("The events", S3),
    ("rspeak log and trustworthiness", S4),
])
