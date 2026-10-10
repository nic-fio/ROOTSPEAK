# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import box, c, fig, note, p, table, term, text, tip, tree, ul, warn, zone  # noqa: E402
from _helpers import CONFIRMED, ref  # noqa: E402

S1 = p("Only the machine's administrators can use " + c("rspeak") + ": the members of the " + c("sudo")
       + " group (" + c("wheel") + " on Fedora and similar systems). RootSpeak keeps no list of its own: whoever joins or "
       "leaves the group gains or loses access from their next login to the machine (" + ref(2, 6) + ").",
       lead=True) + term(
    "mario@server:~$ rspeak list\n"
    "bash: /usr/bin/rspeak: Permission denied",
    "An ordinary user cannot even start the command") + \
    ul([
        c("rspeak") + " always works as administrator, even to show the help or the version: if it is not already "
        "root, it restarts itself with sudo, which asks for the password.",
        "In messages and in the log the author is the administrator who used sudo, not a generic “root”: “message "
        "3 sent by admin to: …”. Whoever runs " + c("rspeak") + " directly as root (for example from cron) appears "
        "as " + c("root") + ".",
        "Users have no RootSpeak command at all: they can neither send messages nor see who has confirmed.",
    ])

CASELLE = fig(
    zone(20, 44, 860, 110, "/var/lib/rootspeak/sent/: the reference copies")
    + box(44, 84, 250, 52, "root only", "the administrators, with rspeak", "dark")
    + text(600, 104, "message, recipients, deliveries, revocation:", 12, "#334155")
    + text(600, 122, "this is where rspeak status reads who has been reached", 12, "#334155")
    + zone(20, 170, 860, 150, "/var/lib/rootspeak/users/: one mailbox per user")
    + box(44, 210, 190, 52, "users/mario/", "Mario only (and root)", "blue")
    + box(254, 210, 190, 52, "users/anna/", "Anna only (and root)", "blue")
    + box(464, 210, 190, 52, "users/luca/", "Luca only (and root)", "blue")
    + text(770, 232, "to be read", 12, "#334155") + text(770, 250, "confirmations, postponements", 12, "#334155")
    + text(450, 296, "Anna cannot open Mario's mailbox, and no user can open sent/", 12, "#991b1b", "600"),
    900, 340, "«FIG» — Who can read what in the RootSpeak message store", "The message store")

S2 = p("Each user sees only the messages sent to them. The message store in " + c("/var/lib/rootspeak/") + " is split into "
       "two parts with different permissions.", lead=True) + CASELLE + \
    tree([
        "/var/lib/rootspeak/  # root, readable by everyone (listing only)",
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
    note("RootSpeak always enters a user's mailbox with that user's identity, even when the administrator is in "
         "command: this way a user cannot trick root into writing where it should not.",
         "Root does not go in as root.")

S3 = p("The confirmation records that the user <b>states</b> they have read the message, with date, time and channel, "
       "like the read receipts of a messaging app. It cannot prove that they really read it.", lead=True) + \
    table(["The confirmation says", "The confirmation does not say"], [
        ["that the user pressed “I have read it” or answered “y”", "that they read it carefully"],
        ["when (day and time) and from where (desktop or which terminal)", "who was in front of the screen"],
        ["that the message had neither expired nor been revoked at that moment", "that they understood the content"],
    ], "«TAB» — What a confirmation is worth") + \
    note("the mailbox belongs to the user: an expert user could record a confirmation without opening the dialog. "
         "It is still their own statement, like the click on “I have read it”.", "A statement.") + \
    tip("for notices that require a real commitment (a rule to follow, an authorisation) the RootSpeak confirmation "
        "is a reminder, not a signature: a separate document is needed.", "When more is needed.")

PULIZIA = fig(
    box(30, 60, 250, 70, "Pasted text", "with colours, titles, invisible characters", "grey")
    + box(325, 60, 250, 70, "RootSpeak cleans it", "before saving it", "navy")
    + box(620, 60, 250, 70, "Safe text", "letters, tabs, line breaks", "green")
    + '<path d="M282 95 H 321" stroke="#0050C0" stroke-width="2.2"/><path d="M577 95 H 616" stroke="#0050C0" stroke-width="2.2"/>'
    + text(450, 160, "no message can change the colours, title or behaviour of a user's terminal",
           11.5, "#334155", "600"),
    900, 180, "«FIG» — The text of every message is cleaned before it is saved", "Safe text")

S4 = p("Before saving a message, RootSpeak removes from the text and the title the invisible characters and the codes that "
       "change the colours, title or behaviour of terminal windows. A message therefore cannot alter users' "
       "terminals, even if the text was pasted from an unknown source.", lead=True) + PULIZIA + \
    table(["In the text", "What happens"], [
        ["letters, digits, punctuation, accented letters, symbols", "kept"],
        ["tabs and line breaks", "kept (in the title, line breaks become spaces)"],
        ["colour and cursor-movement codes", "removed"],
        ["codes that change the terminal window's title", "removed"],
        ["other invisible control characters", "removed"],
    ], "«TAB» — What is left of the text") + \
    p("What RootSpeak reads from the users' mailboxes (confirmations, postponements) is also cleaned before it is shown "
      "to the administrator.")

S5 = p("The system log is a convenient trail, but anyone on the machine can write lines tagged "
       + c("rspeak") + " into it. That is why " + c("rspeak log") + " and the TUI check who really wrote each event and "
       "flag the suspicious ones.", lead=True) + term(
    "admin@server:~$ rspeak log 3\n"
    "Message 3 · New password rule · 30/09 19:05\n"
    "2026-09-30 19:05:12  message 3 delivered to anna (terminals written: 1)\n"
    "2026-09-30 19:05:12  message 3 sent by admin to: anna luca\n"
    "2026-09-30 19:06:40  [not trustworthy: written by UID 1003] user anna: confirmed reading message 3 (desktop)",
    "A forged confirmation: Luca (UID 1003) wrote a line in Anna's name; the other lines are ordinary ones, "
    "like those in chapter 6.4") + \
    table(["Event", "Must have been written by"], [
        ["sending, delivery, reminder, revocation, deletion", "root (that is, " + c("rspeak") + ")"],
        ["postponement, confirmation, confirmation not recorded", "the user it refers to"],
    ], "«TAB» — Who writes each event") + \
    warn("a line marked “not trustworthy” must be disregarded. The true state of a "
         "recipient is the one shown in the message details and by " + c("rspeak status") + ", which comes not from "
         "the log but from the message store: there " + CONFIRMED
         + " means that the confirmation is in the user's mailbox.", "Trust the state.")

CHAPTER = ("Security and privacy", [
    ("Who can use RootSpeak", S1),
    ("Who sees the messages", S2),
    ("What a confirmation is worth", S3),
    ("Safe text", S4),
    ("How reliable the log is", S5),
])
