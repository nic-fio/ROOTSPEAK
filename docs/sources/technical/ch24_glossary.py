from build import arrow, box, c, dl, fig, text


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


MAP = fig(
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

S1 = MAP + dl([
    ("administrators' group", "the existing group " + c("sudo") + ", " + c("wheel") + " or " + c("admin") + ": RootSpeak has no group of its own."),
    ("agent", c("rootspeak-user agent") + ": shows the confirmation dialogs in the graphical session; one per user (" + cap(12) + ")."),
    ("as_user", "the function in " + c("src/user.c") + " that runs an operation in a child process with a user's identity, with a time limit (" + cap(7) + ")."),
    ("author", "the administrator who ran " + c("rspeak") + " (" + c("SUDO_USER") + "): the sender of the messages and the author of the events."),
    ("channel", "where a confirmation comes from: " + c("desktop") + " or " + c("terminal pts/N") + "; it is stored as it is shown."),
    ("confirmation", "the user's statement of having read the message, in " + c("acks/ID") + ", with date and channel; the first one counts (" + cap(13) + ")."),
    ("confirmed", "state of a recipient with a valid confirmation: not later than the expiry or the revocation. It is a statement by the user, not a proof of reading."),
    ("delivered", "state of a recipient whose copy has been written and verified in the mailbox (line in " + c("sent/ID/delivery") + ") and who has no valid confirmation."),
    ("event", "a structured line in the journal, with the " + c("RSPEAK_*") + " fields (" + cap(17) + ")."),
    ("expired", "property of a message whose expiry has passed: it is no longer shown, and later confirmations are not valid."),
    ("fingerprint", "the abbreviated SHA-256 of the code (" + c("tools/fingerprint.sh") + "), recorded with the test results (" + cap(20, 1) + ")."),
    ("hook", "the file that connects RootSpeak to the shell: " + c("rootspeak.bash") + ", " + c("rootspeak.zsh") + ", " + c("rootspeak.fish") + " and, for the other shells, " + c("/etc/profile.d/rootspeak.sh") + " (" + cap(11) + ")."),
    ("internal marker", c("incomplete") + ", " + c("revoking") + ", " + c("failed") + ", " + c(".deleting-ID") + ": files through which recovery knows what to complete or cancel. They are not states."),
    ("linearisation point", "the instant at which an operation is considered to have happened for any observer (" + cap(19, 4) + ")."),
    ("lock", "the file " + c("sent/ID/lock") + " used with " + c("flock") + ": held by " + c("rspeak send") + " for the whole delivery, it tells a sending in progress from an interrupted one."),
], cls="gloss")

S2 = dl([
    ("mailbox", "a user's folder " + c("/var/lib/rootspeak/users/U") + ", owned by the user, with permissions " + c("700") + "."),
    ("message", "a text with an optional title and expiry and a sequential number (ID)."),
    ("message properties", "revoked and expired: they apply to the message, not to a recipient, and they are not states."),
    ("message store", "the folder " + c("/var/lib/rootspeak") + ": root's " + c("sent/") + " and the users' mailboxes (" + cap(5) + ")."),
    ("postponement", "the answer “no” or “Later”: the file " + c("state/ID.term") + " or " + c("state/ID.gui") + ", whose modification time counts for " + c("RSPEAK_REMIND_MINUTES") + " minutes."),
    ("ready", "an agent that has set up the reception of the wake-up signal and has written its PID to " + c("rootspeak-agent.ready") + "."),
    ("recipient", "a user the message is addressed to; the list is in " + c("sent/ID/recipients") + "."),
    ("recovery", c("recover") + ": completes interrupted sendings, revocations and deletions at the start of the following commands (" + cap(8, 6) + ")."),
    ("reference copy", "the message in " + c("sent/ID/msg") + ", accessible only to root: the only expiry that counts."),
    ("reminder", c("rspeak remind") + ": removes the postponements of the delivered recipients and wakes up their agent (" + cap(9, 2) + ")."),
    ("revoked", "property of a message with " + c("sent/ID/revoked") + ": it is no longer shown, and later confirmations are not valid."),
    ("sent", "state of a recipient who does not yet have the copy in the mailbox."),
    ("summary", "a message described by the counts of its recipients in the three states, in words and with a bar (" + cap(10, 3) + ")."),
    ("test mode", c("RSPEAK_TEST=1") + " with a test message store: the code is tested without root (" + cap(4, 3) + ")."),
    ("TUI", "the full-screen interface for administrators: " + c("rspeak") + " without arguments in a terminal (" + cap(14) + ")."),
    ("wake-up", "the " + c("SIGUSR1") + " signal that " + c("rspeak send") + " and " + c("rspeak remind") + " send to the ready agent."),
    ("zenity", "the program that draws the “I have read it” / “Later” dialog on the desktop."),
], cls="gloss")

CHAPTER = ("Glossary", [
    ("Terms A–L", S1),
    ("Terms M–Z", S2),
])
