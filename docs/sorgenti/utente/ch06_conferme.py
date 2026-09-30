import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import arrow, box, c, fig, key, note, p, schermata, table, term, text, tip, ui, ul, warn  # noqa: E402
from _aiuti import CONFERMATO, CONSEGNATO, INVIATO, RITIRATO, SCADUTO, rif, schermata_u  # noqa: E402


def colonna(s, w):
    return s[:w] + " " * (w - len(s[:w]))


def lista(righe):
    """L'uscita di ams list, con le stesse larghezze del programma."""
    out = ["admin@server:~$ ams list", f"{'ID':<5} {'DATA':<12} " + colonna("TESTO", 40) + "  DESTINATARI"]
    for i, data, testo, frase in righe:
        out.append(f"{i:<5} {data:<12} " + colonna(testo, 40) + "  " + frase)
    return "\n".join(out)


def stato(intestazione, corpo, righe, cmd):
    out = [f"admin@server:~$ {cmd}", intestazione]
    out += [f"  │ {r}" for r in corpo]
    out += ["", f"{'UTENTE':<16} STATO"]
    out += [f"{u:<16} {s}" for u, s in righe]
    return "\n".join(out)


LISTA = lista([
    ("1", "30/09 16:55", "Stanotte alle 23 il server di posta viene aggiornato.", "tutti confermato (3)"),
    ("2", "30/09 16:55", "Sabato dalle 8 alle 12 il server sarà spento per la manutenzione dei dischi.",
     "4 confermato · 3 consegnato · 1 inviato"),
    ("3", "30/09 16:55", "Il tuo account scade venerdì: passa dall'ufficio IT.", "1 consegnato"),
    ("4", "30/09 16:55", "[ritirato] Riavvio alle 13:00.", "2 consegnato"),
])

S1 = p("The main screen of the TUI (" + rif(3, 2) + ") and the " + c("ams list") + " command show all the "
       "messages sent, each summarised by its recipients in the three states. The TUI puts the most recent first and "
       "updates by itself; " + c("ams list") + " lists them from the oldest, once.", lead=True) + \
    term(LISTA, "The same four messages as in the screenshot in chapter 3") + \
    table(["Column", "In the TUI", "In " + c("ams list")], [
        ["ID", "the message number", "the same: it is used for " + c("status") + ", " + c("log") + ", "
         + c("revoke") + " and " + c("remind")],
        ["DATA (DATE)", "day and time of sending (day/month hours:minutes)", "the same"],
        ["MESSAGGIO / TESTO (MESSAGE / TEXT)", "title in bold, then the first line of the text", "the first line of "
         "the text, cut at 40 characters"],
        ["DESTINATARI (RECIPIENTS)", "three-colour bar and phrase (below 110 columns, confirmations out of the total)",
         "the phrase"],
    ], "«TAB» — The columns of the list") + \
    table(["Mark in front of the text", "Meaning"], [
        [c("[ritirato]"), "the message has been revoked (" + rif(7, 1) + "): it is no longer shown"],
        [c("[scaduto]"), "the expiry has passed: it is no longer shown"],
        [c("[invio annullato: interrotto prima del salvataggio]"), "only in " + c("ams list") + ": a sending "
         "stopped before the message was even saved (" + rif(12, 4) + ")"],
    ], "«TAB» — The marks in the list") + \
    note("the phrase counts recipients, not the people who have seen the message: «3 consegnato» (“3 delivered”) "
         "means three people with the copy in their mailbox who have not confirmed yet, logged in or not.",
         "Recipients.")

DETTAGLIO_CLI = stato(
    "Messaggio 2 · Manutenzione · 30/09 16:55 · da root",
    ["Sabato dalle 8 alle 12 il server sarà spento per la manutenzione dei dischi.",
     "Salvate il lavoro entro venerdì sera."],
    [("admin", "confermato il 30/09 16:55 (terminale pts/0)"),
     ("anna", "confermato il 30/09 16:55 (desktop)"),
     ("dario", "inviato, non consegnato"),
     ("fabio", "confermato il 30/09 16:55 (desktop)"),
     ("kora", "consegnato, rimandato il 30/09 16:55"),
     ("luca", "consegnato"),
     ("mario", "consegnato, rimandato il 30/09 16:55"),
     ("zeno", "confermato il 30/09 16:55 (terminale pts/2)")],
    "ams status 2")

S2 = p("Pressing " + key("Enter") + " on the list opens the selected message: at the top title, date, sender, expiry "
       "and any revocation, then the first lines of the text, then two tabs. The " + ui("Destinatari")
       + " (“Recipients”) tab shows the state of each user, with the colours of the bar.", lead=True) + \
    schermata("dettaglio", "«FIG» — A message opened in the TUI: the state of each recipient") + \
    p("The same list, for one message at a time, is obtained with " + c("ams status") + " followed by the number:") + \
    term(DETTAGLIO_CLI, "The state of the recipients with a command") + \
    table(["Status line", "State", "What it means"], [
        [c("inviato, non consegnato"), INVIATO, "the copy is not yet in the mailbox: AMS retries"],
        [c("inviato, non consegnato: la copia non è stata scritta (vedi il registro; il prossimo comando ams "
           "riproverà)"), INVIATO, "the sending ran into an error for this user, usually a full disk"],
        [c("consegnato"), CONSEGNATO, "has the copy; has not confirmed yet"],
        [c("consegnato, scritto su 2 terminali"), CONSEGNATO, "was logged in when the message was sent, and the text "
         "appeared in two terminal windows"],
        [c("consegnato, rimandato il 30/09 16:55"), CONSEGNATO, "answered «Più tardi» (“Later”) or «n»; the time is "
         "that of the last postponement"],
        [c("consegnato, non confermato (ritirato)"), CONSEGNATO, "the message was revoked before this user confirmed"],
        [c("consegnato, non confermato (scaduto)"), CONSEGNATO, "the message expired before this user confirmed"],
        [c("consegnato, non confermato (scaduto; conferma arrivata dopo la scadenza)"), CONSEGNATO,
         "confirmed, but too late: the confirmation does not count"],
        [c("confermato il 30/09 16:55 (desktop)"), CONFERMATO, "pressed «Ho letto» (“I have read it”) in the dialog"],
        [c("confermato il 30/09 16:55 (terminale pts/2)"), CONFERMATO, "answered «s» (“y” in English) in a terminal "
         "window or in an ssh connection (" + c("pts") + ")"],
        [c("confermato il 30/09 16:55 (terminale tty3)"), CONFERMATO, "answered «s» on a console of the machine"],
    ], "«TAB» — The status lines of a recipient") + \
    p("Above the list, " + c("ams status") + " writes " + c("RITIRATO il …") + " (“REVOKED on …”) if the message has "
      "been revoked and " + c("SCADUTO") + " (“EXPIRED”) if the expiry has passed. In the TUI the same information is in "
      "the line at the top, in red for a revocation.") + \
    tip("in the " + ui("Destinatari") + " tab you scroll with " + key("↑") + " " + key("↓") + " and "
        + key("PgUp") + " " + key("PgDn") + "; " + key("s") + " reminds and " + key("r") + " revokes this very "
        "message; " + key("Esc") + " returns to the list.", "Message keys.")

VITA = fig(
    '<line x1="60" y1="170" x2="860" y2="170" stroke="#94a3b8" stroke-width="2"/>'
    + "".join(f'<line x1="{x}" y1="164" x2="{x}" y2="176" stroke="#94a3b8" stroke-width="2"/>'
              + text(x, 196, t, 11.5, "#475569", "600") for x, t in
              [(100, "16:55"), (290, "17:02"), (480, "17:32"), (660, "17:40"), (820, "17:41")])
    + box(30, 70, 140, 60, "sent", "ams send", "grey")
    + box(220, 70, 140, 60, "delivered", "copy in the mailbox", "amber")
    + box(410, 70, 140, 60, "postponed", "stays delivered", "amber", 12)
    + box(590, 70, 140, 60, "reminded", "ams remind", "blue", 12)
    + box(760, 70, 120, 60, "confirmed", "«Ho letto»", "green")
    + arrow(100, 132, 100, 164, "#475569") + arrow(290, 132, 290, 164, "#475569")
    + arrow(480, 132, 480, 164, "#475569") + arrow(660, 132, 660, 164, "#475569")
    + arrow(820, 132, 820, 164, "#475569")
    + text(450, 236, "Mario's history for message 2: there are only three states; postponing and reminding are events",
           11.5, "#334155", "600")
    + text(450, 256, "that stay in the log, and the state remains “delivered” until the confirmation.", 11.5, "#334155", "600"),
    900, 280, "«FIG» — The life of a message for one recipient, from sending to confirmation", "States and events")

S3 = p("Every message has a history made of <b>events</b>: the sending, the delivery to each recipient, the "
       "postponements, the reminders, the confirmations, a possible revocation. Events change the state of a recipient "
       "at only two points: when the copy arrives in the mailbox and when the user confirms.", lead=True) + VITA + \
    table(["Event", "Who causes it", "Effect on the recipient's state"], [
        ["sending", "the administrator", "everyone " + INVIATO + " for an instant"],
        ["delivery", "AMS", INVIATO + " → " + CONSEGNATO],
        ["postponement", "the user («Più tardi», «n»)", "none: stays " + CONSEGNATO],
        ["reminder", "the administrator (" + key("s") + ", " + c("ams remind") + ")", "none: stays "
         + CONSEGNATO + ", but is asked again immediately"],
        ["confirmation", "the user («Ho letto», «s»)", CONSEGNATO + " → " + CONFERMATO],
        ["revocation", "the administrator (" + key("r") + ", " + c("ams revoke") + ")", "none; the message becomes "
         + RITIRATO + " and is no longer shown"],
        ["expiry", "time", "none; the message becomes " + SCADUTO + " and is no longer shown"],
    ], "«TAB» — Events and states") + \
    warn("a confirmation is final: it cannot be undone, neither from the TUI nor from the commands. To ask everyone "
         "again, send a new message.", "No going back.")

LOG = ("admin@server:~$ ams log 2\n"
       "Messaggio 2 · Manutenzione · 30/09 16:55\n"
       "2026-09-30 16:55:57  messaggio 2 consegnato a admin (terminali scritti: 0)\n"
       "2026-09-30 16:55:57  messaggio 2 consegnato a anna (terminali scritti: 0)\n"
       "2026-09-30 16:55:57  messaggio 2 consegnato a mario (terminali scritti: 0)\n"
       "2026-09-30 16:55:57  messaggio 2 inviato da root a: admin anna dario fabio kora luca mario zeno\n"
       "2026-09-30 16:56:10  utente anna: confermata la lettura del messaggio 2 (desktop)\n"
       "2026-09-30 16:56:31  utente mario: rimandato il messaggio 2 (terminale)\n"
       "2026-09-30 17:02:04  messaggio 2: sollecitati 3 destinatari da admin")

S4 = p("The message's " + ui("Storia") + " (“History”) tab, opened with " + key("Tab") + ", lists the events of the "
       "message taken from the system log, oldest first, with date and time to the second.", lead=True) + \
    schermata("storia", "«FIG» — The history of a message in the TUI") + \
    p("With a command, the same history is read with " + c("ams log") + ":") + term(LOG, "The history with a command") + \
    table(["Line", "When it appears"], [
        [c("messaggio N consegnato a U (terminali scritti: K)"), "for each copy that reached a mailbox; K is the "
         "number of terminal windows in which the text appeared when it was sent"],
        [c("messaggio N inviato da A a: …"), "at the end of each sending, with the list of recipients"],
        [c("messaggio N: ERRORE, copia per U non scritta"), "when a delivery fails"],
        [c("messaggio N consegnato a U (recupero)"), "when AMS completes a delivery that had been left behind"],
        [c("utente U: rimandato il messaggio N (terminale)") + " or " + c("(desktop)"), "when the user postpones"],
        [c("utente U: confermata la lettura del messaggio N (canale)"), "on confirmation"],
        [c("utente U: ERRORE, conferma del messaggio N non registrata (…)"), "when the confirmation could not be "
         "saved, for example with a full disk"],
        [c("messaggio N: sollecitati K destinatari da A"), "at each reminder"],
        [c("messaggio N ritirato da A"), "on revocation"],
    ], "«TAB» — The lines of the history") + \
    note("the history comes from the system log, which the machine may rotate and delete after a while according to "
         "its settings. The state of the recipients, on the other hand, comes from the AMS message store and remains "
         "until the message is deleted.", "History and state.")

S5 = p("Every event is also written to the machine's system log, with the tag " + c("ams") + ". It is the "
       "trail to use if someone asks “who sent what, and when”, even for messages that have already been deleted.",
       lead=True) + term(
    "admin@server:~$ sudo journalctl -t ams --since today\n"
    "set 30 16:55:57 server ams[20914]: messaggio 2 consegnato a anna (terminali scritti: 0)\n"
    "set 30 16:55:57 server ams[20914]: messaggio 2 inviato da root a: admin anna dario fabio kora luca mario zeno\n"
    "set 30 16:56:10 server ams[21310]: utente anna: confermata la lettura del messaggio 2 (desktop)",
    "The system log") + \
    table(["To see…", "Command"], [
        ["all of today's AMS events", c("sudo journalctl -t ams --since today")],
        ["the events of the last hour", c('sudo journalctl -t ams --since "1 hour ago"')],
        ["the events as they arrive", c("sudo journalctl -t ams -f")],
        ["the history of one message, neatly ordered", c("ams log 2")],
    ], "«TAB» — Reading the log") + \
    ul([
        "In the log the lines are in the machine's language; " + c("ams log") + " and the TUI rewrite them in the "
        "language of the reader.",
        "User events (postponements, confirmations) are written by the users themselves: " + c("ams log") + " checks "
        "who wrote them and flags suspicious ones (" + rif(11, 5) + ").",
        "Deleting with " + c("ams purge") + " removes the message from the message store, but its events remain in the "
        "log.",
    ])

S6 = p("When there are many messages, the " + key("/") + " key of the TUI shows only those that contain a given "
       "text, searched in the title and in the whole message, ignoring upper and lower case.", lead=True) + \
    schermata_u("cerca", "«FIG» — Searching: type the text and press Enter") + \
    schermata_u("cercato", "«FIG» — The result: the searched text at the bottom right") + \
    table(["Key", "What it does"], [
        [key("/"), "opens the search; if there already was one, offers it again for editing"],
        [key("Enter"), "applies the search"],
        [key("Esc") + " in the search dialog", "leaves the list as it was"],
        [key("Esc") + " in the list", "clears the search and shows all the messages again"],
    ], "«TAB» — The search keys") + \
    note("if no message contains the text, the list says «Nessun messaggio contiene il testo cercato.» (“No message "
         "contains the search text.”). Accented letters must be typed in the same upper or lower case as in the "
         "message.", "No results.")

CHAPTER = ("Following the confirmations", [
    ("The list of messages", S1),
    ("The state of each recipient", S2),
    ("The life of a message", S3),
    ("The history of a message", S4),
    ("The system log", S5),
    ("Searching for a message", S6),
])
