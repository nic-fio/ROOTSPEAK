import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import box, c, fig, note, p, table, term, text, tip, tree, ul, warn, zone  # noqa: E402
from _aiuti import CONFERMATO, rif  # noqa: E402

S1 = p("Only the machine's administrators can use " + c("ams") + ": the members of the " + c("sudo")
       + " group (" + c("wheel") + " on Fedora and similar systems). AMS keeps no list of its own: whoever joins or "
       "leaves the group gains or loses access from their next login to the machine (" + rif(2, 4) + ").",
       lead=True) + term(
    "mario@server:~$ ams list\n"
    "bash: /usr/local/bin/ams: Permesso negato",
    "An ordinary user cannot even start the command: «Permesso negato» (“Permission denied”)") + \
    ul([
        c("ams") + " always works as administrator, even to show the help or the version: if it is not already "
        "root, it restarts itself with sudo, which asks for the password.",
        "In messages and in the log the author is the administrator who used sudo, not a generic “root”: “message "
        "3 sent by admin to: …”. Whoever runs " + c("ams") + " directly as root (for example from cron) appears "
        "as " + c("root") + ".",
        "Users have no AMS command at all: they can neither send messages nor see who has confirmed.",
    ])

CASELLE = fig(
    zone(20, 44, 860, 110, "/var/lib/ams/sent/: the reference copies")
    + box(44, 84, 250, 52, "root only", "the administrators, with ams", "dark")
    + text(600, 104, "message, recipients, deliveries, revocation:", 12, "#334155")
    + text(600, 122, "this is where ams status reads who has been reached", 12, "#334155")
    + zone(20, 170, 860, 150, "/var/lib/ams/users/: one mailbox per user")
    + box(44, 210, 190, 52, "users/mario/", "Mario only (and root)", "blue")
    + box(254, 210, 190, 52, "users/anna/", "Anna only (and root)", "blue")
    + box(464, 210, 190, 52, "users/luca/", "Luca only (and root)", "blue")
    + text(770, 232, "to be read", 12, "#334155") + text(770, 250, "confirmations, postponements", 12, "#334155")
    + text(450, 296, "Anna cannot open Mario's mailbox, and no user can open sent/", 12, "#991b1b", "600"),
    900, 340, "«FIG» — Who can read what in the AMS message store", "The message store")

S2 = p("Each user sees only the messages sent to them. The message store in " + c("/var/lib/ams/") + " is split into "
       "two parts with different permissions.", lead=True) + CASELLE + \
    tree([
        "/var/lib/ams/  # root, readable by everyone (listing only)",
        "├── sent/  # root, 700: root only",
        "│   └── 3/  # message 3: text, recipients, deliveries, revocation",
        "└── users/",
        "    └── mario/  # Mario's, 700: Mario and root only",
        "        ├── inbox/  # messages to confirm",
        "        ├── read/  # confirmed or expired messages",
        "        ├── acks/  # the confirmations, with date and channel",
        "        └── state/  # the postponements",
    ], "«FIG» — The message store seen from above") + \
    table(["Who", "What they see"], [
        ["an administrator", "all the messages sent, the recipients, the confirmations, the history"],
        ["a user", "only the messages addressed to them, one at a time, until they confirm them"],
        ["the other users", "nothing of a colleague's messages, not even that they exist"],
    ], "«TAB» — Who sees what") + \
    note("AMS always enters a user's mailbox with that user's identity, even when the administrator is in "
         "command: this way a user cannot trick root into writing where it should not.",
         "Root does not go in as root.")

S3 = p("The confirmation records that the user <b>states</b> they have read the message, with date, time and channel, "
       "like the read receipts of a messaging app. It cannot prove that they really read it.", lead=True) + \
    table(["The confirmation says", "The confirmation does not say"], [
        ["that the user pressed «Ho letto» (“I have read it” on an English desktop) or answered «s» (“y” in "
         "English)", "that they read it carefully"],
        ["when (day and time) and from where (desktop or which terminal)", "who was in front of the screen"],
        ["that the message had neither expired nor been revoked at that moment", "that they understood the content"],
    ], "«TAB» — What a confirmation is worth") + \
    note("the mailbox belongs to the user: an expert user could record a confirmation without opening the dialog. "
         "It is still their own statement, like the click on «Ho letto» (“I have read it”).", "A statement.") + \
    tip("for notices that require a real commitment (a rule to follow, an authorisation) the AMS confirmation "
        "is a reminder, not a signature: a separate document is needed.", "When more is needed.")

PULIZIA = fig(
    box(30, 60, 250, 70, "Pasted text", "with colours, titles, invisible characters", "grey")
    + box(325, 60, 250, 70, "AMS cleans it", "before saving it", "navy")
    + box(620, 60, 250, 70, "Safe text", "letters, tabs, line breaks", "green")
    + '<path d="M282 95 H 321" stroke="#0050C0" stroke-width="2.2"/><path d="M577 95 H 616" stroke="#0050C0" stroke-width="2.2"/>'
    + text(450, 160, "no message can change the colours, title or behaviour of a user's terminal",
           11.5, "#334155", "600"),
    900, 180, "«FIG» — The text of every message is cleaned before it is saved", "Safe text")

S4 = p("Before saving a message, AMS removes from the text and the title the invisible characters and the codes that "
       "change the colours, title or behaviour of terminal windows. A message therefore cannot alter users' "
       "terminals, even if the text was pasted from an unknown source.", lead=True) + PULIZIA + \
    table(["In the text", "What happens"], [
        ["letters, digits, punctuation, accented letters, symbols", "kept"],
        ["tabs and line breaks", "kept (in the title, line breaks become spaces)"],
        ["colour and cursor-movement codes", "removed"],
        ["codes that change the terminal window's title", "removed"],
        ["other invisible control characters", "removed"],
    ], "«TAB» — What is left of the text") + \
    p("What AMS reads from the users' mailboxes (confirmations, postponements) is also cleaned before it is shown "
      "to the administrator.")

S5 = p("The system log is a convenient trail, but anyone on the machine can write lines tagged "
       + c("ams") + " into it. That is why " + c("ams log") + " and the TUI check who really wrote each event and "
       "flag the suspicious ones.", lead=True) + term(
    "admin@server:~$ ams log 3\n"
    "Messaggio 3 · Nuova regola per le password · 30/09 19:05\n"
    "2026-09-30 19:05:12  messaggio 3 consegnato a anna (terminali scritti: 1)\n"
    "2026-09-30 19:05:12  messaggio 3 inviato da admin a: anna luca\n"
    "2026-09-30 19:06:40  [non attendibile: scritto da UID 1003] utente anna: confermata la lettura del messaggio 3 (desktop)",
    "A forged confirmation: Luca (UID 1003) wrote a line in Anna's name. «Nuova regola per le password» (“New rule for "
    "passwords”); «[non attendibile: scritto da UID 1003]» (“[not trustworthy: written by UID 1003]”); the other "
    "lines are those of the history in chapter 6.4: delivered, sent, «confermata la lettura» (“confirmed reading”)") + \
    table(["Event", "Must have been written by"], [
        ["sending, delivery, reminder, revocation, deletion", "root (that is, " + c("ams") + ")"],
        ["postponement, confirmation, confirmation not recorded", "the user it refers to"],
    ], "«TAB» — Who writes each event") + \
    warn("a line marked «non attendibile» (“not trustworthy” in English) must be disregarded. The true state of a "
         "recipient is the one shown in the message details and by " + c("ams status") + ", which comes not from "
         "the log but from the message store: there " + CONFERMATO
         + " means that the confirmation is in the user's mailbox.", "Trust the state.")

CHAPTER = ("Security and privacy", [
    ("Who can use AMS", S1),
    ("Who sees the messages", S2),
    ("What a confirmation is worth", S3),
    ("Safe text", S4),
    ("How reliable the log is", S5),
])
