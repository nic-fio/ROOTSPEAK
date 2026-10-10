# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import arrow, box, c, dl, fig, text, zone  # noqa: E402

MAP = fig(
    box(30, 60, 190, 60, "Message", "number, title, text", "navy")
    + box(30, 170, 190, 60, "Properties", "expiry, revocation", "grey")
    + box(300, 60, 190, 60, "Recipients", "names, @group, all, online", "dark")
    + zone(560, 40, 320, 206, "State of each recipient")
    + box(590, 76, 260, 44, "sent", "", "grey", 13)
    + box(590, 130, 260, 44, "delivered", "", "amber", 13)
    + box(590, 184, 260, 44, "confirmed", "", "green", 13)
    + arrow(222, 90, 298, 90) + arrow(125, 122, 125, 168, "#475569")
    + arrow(492, 90, 556, 98)
    + box(300, 260, 190, 56, "Events", "in the log and in the history", "light")
    + arrow(395, 122, 395, 258, "#475569", True)
    + text(720, 276, "sessions: desktop, terminals, login", 11.5, "#334155", "600")
    + text(720, 296, "confirmation channel: desktop or terminal", 11.5, "#334155", "600"),
    900, 330, "«FIG» — The words of RootSpeak and how they fit together", "Map of the terms")

S1 = MAP + dl(sorted([
    ("desktop agent", "The small RootSpeak program that starts at every graphical login and shows the confirmation "
     "dialogs. It is not a command: it starts by itself."),
    ("all", "Special recipient: all the users of the machine with a UID of 1000 or above and a real shell."),
    ("message store", "The folder " + c("/var/lib/rootspeak/") + ": the reference copies of the messages and the users' "
     "mailboxes."),
    ("channel", "Where a confirmation came from: " + c("desktop") + " or " + c("terminal pts/N") + " or "
     + c("terminal ttyN") + "."),
    ("mailbox", "The space where RootSpeak keeps a user's messages, their confirmations and their postponements. Only "
     "they (and root) can open it."),
    ("confirmation", "The user's statement that they have read a message: a click on “I have read it” "
     "or the answer “y”. It is final and applies to all their sessions."),
    ("confirmed", "Third state of a recipient: they have stated that they read the message. It is "
     "their statement, not proof that they really read it."),
    ("delivered", "Second state: the copy of the message is in the user's mailbox, and the user has "
     "not confirmed yet. Whoever postpones stays delivered."),
    ("recipients", "The users who receive a message: names, " + c("@group") + ", " + c("all") + ", "
     + c("online") + "."),
    ("event", "A fact in the history of a message (sending, delivery, postponement, reminder, confirmation, "
     "revocation, deletion), written to the system log."),
    ("built-in help", "The tabbed help that opens with " + c("rspeak --help") + "."),
    ("sent", "First state: the message has left, but the copy is not yet in the user's mailbox."),
    ("online", "Special recipient: among the users of " + c("all") + ", those logged in at the moment of "
     "sending."),
    ("purge", "Deleting the messages older than a given duration: " + c("rspeak purge") + " or the " + c("p")
     + " key in the TUI."),
    ("recovery", "The automatic completion of a sending left halfway, the next time " + c("rspeak") + " is used."),
    ("system log", "The machine's log (the journal), where RootSpeak writes its events with the tag "
     + c("rspeak") + "."),
    ("postpone", "Pressing “Later” or answering anything other than “y”: the message is shown again after 30 minutes. "
     "It is not a state."),
    ("revoke", "Withdrawing a message with " + c("rspeak revoke") + " or the " + c("r") + " key: whoever has not seen "
     "it will no longer see it. Revoked is a property of the message, not a state of the recipients."),
    ("expiry", "The moment after which a message is no longer shown (" + c("--expires") + "). Expired is "
     "a property of the message, not a state of the recipients."),
    ("session", "A user's access to the machine: the desktop, a console, an ssh connection."),
    ("remind", "Asking again, immediately, for the confirmation from those who are still delivered: "
     + c("rspeak remind") + " or the " + c("m") + " key in the TUI."),
    ("TUI", "The full-screen interface, inside the terminal, that opens when you type " + c("rspeak") + " on its own."),
], key=lambda term: term[0].lower()), cls="gloss")

CHAPTER = ("Glossary", [
    ("Terms", S1),
])
