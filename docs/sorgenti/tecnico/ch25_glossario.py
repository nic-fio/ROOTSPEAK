from build import arrow, box, c, dl, fig, text


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


MAPPA = fig(
    box(20, 60, 150, 50, "message", "sent/ID/msg", "navy", 12)
    + box(220, 60, 150, 50, "recipient", "one per line", "navy", 12)
    + box(420, 20, 150, 50, "mailbox", "users/U/", "blue", 12)
    + box(420, 100, 150, 50, "state", "one of three", "green", 12)
    + box(620, 20, 120, 50, "channel", "terminal, desktop", "light", 11)
    + box(620, 100, 120, 50, "confirmation", "acks/ID", "green", 12)
    + box(780, 60, 100, 50, "event", "journal", "soft", 12)
    + arrow(172, 85, 218, 85) + arrow(372, 78, 418, 50) + arrow(372, 92, 418, 122)
    + arrow(572, 45, 618, 45) + arrow(572, 125, 618, 125) + arrow(680, 72, 680, 98)
    + arrow(742, 115, 778, 92, "#475569", True)
    + text(450, 176, "the glossary terms and how they are connected", 11.5, "#475569", "600"),
    900, 192, "«FIG» — The main terms", "Map of the terms")

S1 = MAPPA + dl([
    ("agent (it. agente)", c("ams-user agent") + ": shows the confirmation dialogs in the graphical session; one per "
     "user (" + cap(12) + ")."),
    ("hook (it. aggancio)", "the file that connects AMS to the shell: " + c("ams.bash") + ", " + c("ams.zsh") + ", "
     + c("ams.fish") + " and, for the other shells, " + c("/etc/profile.d/ams.sh") + " (" + cap(11) + ")."),
    ("message store (it. archivio)", "the folder " + c("/var/lib/ams") + ": root's " + c("sent/") + " and the users' "
     "mailboxes (" + cap(5) + ")."),
    ("author (it. autore)", "the administrator who ran " + c("ams") + " (" + c("SUDO_USER") + "): the sender of the "
     "messages and the author of the events."),
    ("channel (it. canale)", "where a confirmation comes from: " + c("desktop") + " or " + c("terminale pts/N")
     + "; it is saved without a language and translated when shown."),
    ("mailbox (it. casella)", "a user's folder " + c("/var/lib/ams/users/U") + ", owned by the user, with "
     "permissions " + c("700") + "."),
    ("catalog (it. catalogo)", "the " + c(".mo") + " file with the translations of a language, compiled from "
     + c("po/LINGUA.po") + " (" + cap(16, 3) + ")."),
    ("come_utente", "the function in " + c("src/utente.c") + " that runs an operation in a child process with a "
     "user's identity, with a time limit (" + cap(7) + ")."),
    ("confirmation (it. conferma)", "the user's statement of having read the message, in " + c("acks/ID")
     + ", with date and channel; the first one counts (" + cap(13) + ")."),
    ("confirmed (it. confermato)", "state of a recipient with a valid confirmation: not later than the expiry or "
     "the revocation. It is a statement by the user, not a proof of reading."),
    ("delivered (it. consegnato)", "state of a recipient whose copy has been written and verified in the mailbox "
     "(line in " + c("sent/ID/delivery") + ") and who has no valid confirmation."),
    ("reference copy (it. copia di riferimento)", "the message in " + c("sent/ID/msg") + ", accessible only to "
     "root: the only expiry that counts."),
    ("recipient (it. destinatario)", "a user the message is addressed to; the list is in "
     + c("sent/ID/recipients") + "."),
    ("event (it. evento)", "a structured line in the journal, with the " + c("AMS_*") + " fields (" + cap(18) + ")."),
    ("administrators' group (it. gruppo degli amministratori)", "the existing group " + c("sudo") + ", "
     + c("wheel") + " or " + c("admin") + ": AMS has no group of its own."),
    ("fingerprint (it. impronta)", "the abbreviated SHA-256 of the code (" + c("tools/impronta.sh") + "), recorded "
     "with the test results (" + cap(21, 1) + ")."),
    ("sent (it. inviato)", "state of a recipient who does not yet have the copy in the mailbox."),
    ("lock", "the file " + c("sent/ID/lock") + " used with " + c("flock") + ": held by " + c("ams send")
     + " for the whole delivery, it tells a sending in progress from an interrupted one."),
], cls="gloss")

S2 = dl([
    ("message (it. messaggio)", "a text with an optional title and expiry and a sequential number (ID)."),
    ("test mode (it. modalità di prova)", c("AMS_TEST=1") + " with a test message store: the code is tested "
     "without root (" + cap(4, 3) + ")."),
    ("message properties (it. proprietà del messaggio)", "revoked and expired: they apply to the message, not to a "
     "recipient, and they are not states."),
    ("ready (it. pronto)", "an agent that has set up the reception of the wake-up signal and has written its PID to "
     + c("ams-agent.pronto") + "."),
    ("linearisation point (it. punto di linearizzazione)", "the instant at which an operation is considered to "
     "have happened for any observer (" + cap(20, 4) + ")."),
    ("recovery (it. recupero)", c("recupera") + ": completes interrupted sendings, revocations and deletions at the "
     "start of the following commands (" + cap(8, 6) + ")."),
    ("summary (it. riassunto)", "a message described by the counts of its recipients in the three states, in words "
     "and with a bar (" + cap(10, 3) + ")."),
    ("postponement (it. rinvio)", "the answer “no” or «Più tardi» (“Later”): the file " + c("state/ID.term")
     + " or " + c("state/ID.gui") + ", whose modification time counts for " + c("AMS_REMIND_MINUTES")
     + " minutes."),
    ("revoked (it. ritirato)", "property of a message with " + c("sent/ID/revoked") + ": it is no longer shown, and "
     "later confirmations are not valid."),
    ("expired (it. scaduto)", "property of a message whose expiry has passed: it is no longer shown, and later "
     "confirmations are not valid."),
    ("internal marker (it. segno interno)", c("incomplete") + ", " + c("ritiro") + ", " + c("failed") + ", "
     + c(".cancella-ID") + ": files through which recovery knows what to complete or cancel. They are not "
     "states."),
    ("reminder (it. sollecito)", c("ams remind") + ": removes the postponements of the delivered recipients and "
     "wakes up their agent (" + cap(9, 2) + ")."),
    ("wake-up (it. sveglia)", "the " + c("SIGUSR1") + " signal that " + c("ams send") + " and " + c("ams remind")
     + " send to the ready agent."),
    ("TUI", "the full-screen interface for administrators: " + c("ams") + " without arguments in a terminal "
     "(" + cap(14) + ")."),
    ("zenity", "the program that draws the «Ho letto» / «Più tardi» (“I have read it” / “Later”) dialog on the "
     "desktop."),
], cls="gloss")

CHAPTER = ("Glossary", [
    ("Terms A–L (Italian names)", S1),
    ("Terms M–Z (Italian names)", S2),
])
