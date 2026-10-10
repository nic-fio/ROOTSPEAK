# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

from build import arrow, box, c, code, diamond, fig, flow, note, p, path, seq, table, term, text, ul, warn


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


RITIRO = seq([("rspeak revoke", "root", "navy"), ("sent/ID", "store", "dark"), ("rspeak send", "in progress", "light"),
              ("Mailbox U", "users/U", "blue"), ("Question, dialog", "of U", "soft")], [
    (0, 1, "revoking marker"),
    (0, 1, "revoked ← date (on disk)"),
    ("note", 0, "REVOKED event".ljust(15)),
    (0, 1, "flock(lock): waits", True),
    (2, 1, "revoked? yes: stops"),
    (2, 1, "releases the lock", True),
    (0, 3, "as U: removes inbox/ID, postponements"),
    (0, 1, "removes the revoking marker"),
    (4, 3, "inbox/ID gone?"),
    ("note", 4, "they close within 1 s"),
], "«FIG» — A revocation during a send in progress", "rspeak revoke", width=920)

S1 = p(c("rspeak revoke ID") + " revokes a message: whoever has not seen it yet will not see it, open questions and "
       "dialogs close by themselves. The revocation <b>takes place</b> at the instant " + c("sent/ID/revoked")
       + " appears: from then on no new delivery, and no confirmation with a later date counts.", lead=True) + RITIRO + \
    table(["Step", "What", "Why"], [
        ["1", "marker " + c("sent/ID/revoking"), "if the command is interrupted, recovery knows there are copies to "
         "remove"],
        ["2", c("sent/ID/revoked") + " with the date, written with " + c("write_atomic") + "; " + c("fsync")
         + " of " + c("revoking") + " and of the folder; event " + c("REVOKED"), "the revocation is on disk before "
         "the mailboxes are touched; a second revocation of the same message rewrites neither the date nor the event"],
        ["3", c("flock") + " on " + c("sent/ID/lock") + ", <b>blocking</b>", "waits for an " + c("rspeak send")
         + " in progress, which checks " + c("revoked") + " before each recipient and stops"],
        ["4", "for each recipient, as the user: removes " + c("inbox/ID") + ", " + c("state/ID.term") + ", "
         + c("state/ID.gui"), "copies already read or confirmed (" + c("read/") + ", " + c("acks/")
         + ") stay: they are the history"],
        ["5", "all removed: " + c("revoking") + " removed; “Message N revoked.”", "otherwise "
         + c("die") + ": “message N revoked, but some copies could not be removed from the mailboxes: the next "
         "rspeak command will retry”"],
    ], "«TAB» — The steps of a revocation") + ul([
    "Serialising revocation with sending comes from the second review: before, a copy could arrive after the "
    "revocation. " + c("tests/engine.sh") + " (group 9) checks that " + c("rspeak revoke") + " waits for a lock held "
    "for 2 seconds; scenario F7 revokes a send to many users while it is in progress, and no copy is left behind.",
    "If the revocation arrives during the send, " + c("rspeak send") + " ends with “Message N revoked while sending: "
    "delivery stopped.”: the recipients not yet reached stay sent.",
    "The question in the terminal and the dialog check " + c("inbox/ID") + " every second and close (scenarios "
    "E3 and I6); a confirmation that arrives between their last check and the revocation does not count, because its "
    "date is later than " + c("revoked") + " (" + cap(13, 1) + ").",
])

SOLL = fig(
    box(20, 70, 160, 56, "rspeak remind ID", "or the m key in the TUI", "navy")
    + diamond(300, 98, 200, 64, "revoked or expired?", "amber")
    + box(210, 170, 180, 48, "die", "nobody to remind", "grey", 12)
    + box(420, 70, 170, 56, "recipients()", "state of each one", "dark")
    + box(630, 20, 250, 50, "delivered", "removes state/ID.* as U, wake-up", "blue", 12)
    + box(630, 90, 250, 50, "sent", "nothing: has no copy", "soft", 12)
    + box(630, 160, 250, 50, "confirmed", "nothing", "soft", 12)
    + arrow(182, 98, 198, 98) + arrow(300, 132, 300, 168, "#475569", False, "yes", 314, 152)
    + arrow(402, 98, 418, 98, "#0050C0", False, "no", 410, 88)
    + arrow(592, 90, 628, 45) + arrow(592, 98, 628, 115) + arrow(592, 106, 628, 185)
    + text(450, 250, "REMINDED event with the number of reminded recipients and the author", 11.5, "#475569", "600"),
    900, 266, "«FIG» — rspeak remind: only those who have the copy and have not confirmed", "The reminder")

S2 = p(c("rspeak remind ID") + " brings the question back at once to those who have not confirmed yet, even if they "
       "had postponed it. It rewrites nothing: it removes the postponements and wakes the agent.", lead=True) + SOLL + ul([
    "A revoked or expired message cannot be reminded: “message N has been revoked: nobody to remind” "
    "(" + c("tests/engine.sh") + ", group 10).",
    "The recipients' state comes from " + c("recipients") + ", the same function used by " + c("rspeak status")
    + ": the reminder goes to those who are <b>delivered</b>. Those who are sent do not have the copy (recovery will "
    "complete it), those who have confirmed must not be disturbed. If everyone has already confirmed, the command says so "
    "(“Message N: everyone has already confirmed, nobody to remind.”) instead of “0 recipients reminded”, which "
    "looked like a fault in the first live test (" + c("tests/engine.sh") + ", group 10).",
    "For each of them, as the user, " + c("state/ID.term") + " and " + c("state/ID.gui") + " are removed; then "
    + c("wake_agent") + ". The question comes back at the next prompt (scenario D5); the dialog reappears at once "
    "(scenario I11: 0.37 s in the last recorded run).",
    "The reminder takes no lock: if a confirmation arrives in the meantime, removing the postponements of someone "
    "who has confirmed has no effect (" + cap(19, 4) + ").",
]) + term("admin@server:~$ sudo rspeak remind 12\nMessage 12: 3 recipients reminded.",
          "A reminder") + \
    note("before the reminder existed, the test VM found an edge case: an " + c("rspeak remind") + " arriving within "
         "a second of “Later” was lost, because the agent recorded the postponement on its next round. "
         "Now the agent records the answer as soon as zenity closes (" + cap(12, 3) + ").")

PURGE = flow([("Duration", "90d, 12h, 30m", "dark"), ("Older?", "date of sending", "navy"),
              ("Lock free?", "and not incomplete", "navy"), ("Rename", "sent/.deleting-ID", "amber"),
              ("Mailboxes", "as each user", "blue"), ("Folder", "files and rmdir", "green")],
             "«FIG» — rspeak purge: the message disappears with a rename, then the mailboxes are cleaned")

S3 = p(c("rspeak purge DURATION") + " deletes the messages sent more than " + c("DURATION") + " ago, together with the "
       "copies, confirmations and postponements in the mailboxes. The events stay in the journal.", lead=True) + PURGE + table(
    ["Step", "What"], [
        ["duration", "a number followed by " + c("m") + ", " + c("h") + " or " + c("d") + "; otherwise “invalid duration: 7x (for example 90d, 12h, 30m)”"],
        ["selection", "for each message: the sending date from " + c("msg") + " (or, if the file cannot be read, the "
         "modification date of the folder); a message with " + c("incomplete") + " is skipped"],
        ["lock", "non-blocking " + c("flock") + " on " + c("sent/ID/lock") + ": a send in progress is skipped"],
        ["rename", c("sent/ID") + " → " + c("sent/.deleting-ID") + ", " + c("fsync") + " of " + c("sent/")
         + ", lock released, event " + c("DELETED") + " with duration and author"],
        ["mailboxes", "for each recipient, as the user: removes " + c("inbox/ID") + ", " + c("read/ID") + ", "
         + c("acks/ID") + " and the postponements"],
        ["folder", "removes the files in " + c("sent/.deleting-ID/") + " and the folder itself"],
    ], "«TAB» — The steps of a deletion") + ul([
    "The rename is the point at which the message stops existing for all commands: " + c("list_numbers")
    + " sees only names made of digits. " + c("rspeak list") + " reads what it needs from each message before "
    "using it and skips a message that has disappeared in the meantime (" + c("summarise") + " returns false).",
    "A deletion interrupted after the rename is completed by the recovery of the next command ("
    + c("tests/engine.sh") + ", group 9).",
    c("rspeak purge") + " does not run recovery before itself: it skips incomplete sends anyway.",
]) + term("admin@server:~$ sudo rspeak purge 90d\nDeleted 4 messages older than 90d.",
          "A purge") + \
    warn("after the deletion message numbers are not reused (the " + c(".seq") + " sequence stays), but "
         + c("rspeak log") + " of a deleted number no longer finds the message: its history can then be read "
         "only with " + c("journalctl RSPEAK_MESSAGE=ID") + ".")

CHAPTER = ("Revocation, reminders and deletion", [
    ("Revoking: rspeak revoke", S1),
    ("Reminding: rspeak remind", S2),
    ("Deleting: rspeak purge", S3),
])
