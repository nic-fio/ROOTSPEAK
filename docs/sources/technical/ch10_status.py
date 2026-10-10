# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

from build import arrow, box, c, code, diamond, fig, note, p, path, seq, table, term, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


DECIDE = fig(
    diamond(120, 70, 200, 64, "line in delivery?", "navy")
    + box(40, 150, 160, 50, "SENT", "", "light")
    + diamond(355, 70, 220, 64, "confirmation in acks/ID?", "navy")
    + box(275, 150, 160, 50, "DELIVERED", "no confirmation", "blue", 12)
    + diamond(585, 70, 200, 64, "date ≤ expiry?", "navy")
    + box(705, 45, 185, 50, "DELIVERED", "late confirmation", "blue", 12)
    + diamond(585, 190, 200, 64, "date ≤ revocation?", "navy")
    + box(705, 165, 185, 50, "DELIVERED", "confirmed after revocation", "blue", 12)
    + box(505, 260, 160, 50, "CONFIRMED", "date and channel", "green", 12)
    + arrow(220, 70, 243, 70, "#0050C0", False, "yes", 232, 60)
    + arrow(120, 104, 120, 148, "#475569", False, "no", 136, 128)
    + arrow(465, 70, 483, 70, "#0050C0", False, "yes", 474, 60)
    + arrow(355, 104, 355, 148, "#475569", False, "no", 371, 128)
    + arrow(685, 70, 703, 70, "#475569", False, "no", 694, 60)
    + arrow(585, 104, 585, 156, "#0050C0", False, "yes", 601, 132)
    + arrow(685, 190, 703, 190, "#475569", False, "no", 694, 180)
    + arrow(585, 224, 585, 258, "#16a34a", False, "yes", 601, 244),
    900, 330, "«FIG» — recipient_state: a recipient's state, deduced from the files", "How the state is decided")

S1 = p("A recipient's state is not written anywhere: " + c("recipient_state") + " in "
       + c("src/rspeak.c") + " deduces it every time from " + c("sent/ID/delivery") + ", from the confirmation in the "
       "mailbox and from the reference copy. The expiry and revocation that count are <b>root's</b>, not those of the "
       "copy, which the user might have altered.", lead=True) + DECIDE + table(["Condition", "State",
                                                                                 "Line in rspeak status"], [
    ["no line for U in " + c("delivery"), "sent", "“sent, not delivered”; if there is " + c("incomplete")
     + ": “sent, not delivered: the copy could not be written (see the log; the next rspeak command will retry)”"],
    ["line in " + c("delivery") + ", no confirmation", "delivered", "“delivered”, plus the details: "
     "“, written to N terminals”, “, postponed on …”; or “, not confirmed (revoked)” or “, not confirmed (expired)”"],
    ["confirmation dated after the expiry in " + c("sent/ID/msg"), "delivered", "“delivered, not confirmed "
     "(expired; confirmation arrived after the expiry)”"],
    ["confirmation dated after " + c("sent/ID/revoked"), "delivered", "“delivered, not confirmed (revoked)”"],
    ["valid confirmation", "confirmed", "“confirmed on 01/10 17:10 (terminal pts/2)”"],
], "«TAB» — The state deduced from the files") + ul([
    "The date of the confirmation is the number before the space in " + c("acks/ID") + " (0 if it is not a number); "
    "the rest of the line is the channel, stored as it is shown (“terminal pts/2”, “desktop”; " + c("channel_text") + ").",
    "A confirmation with the same date as the revocation counts; one from the second after does not ("
    + c("tests/engine.sh") + ", group 9).",
    "A recipient is in <b>exactly one</b> of the three states: the function returns a value of " + c("state_e")
    + " (" + c("SENT") + ", " + c("DELIVERED") + ", " + c("CONFIRMED") + ") plus, separately, if the "
    "confirmation was late, its date and channel.",
])

READING = seq([("rspeak (root)", "list, status, TUI", "navy"), ("child as U", "op_read, 20 s", "dark"),
               ("Mailbox U", "users/U", "blue")], [
    (0, 1, "IDs from sent/, one per line"),
    (1, 2, "acks/ID: at most 200 bytes"),
    (1, 2, "stat of state/ID.term and .gui"),
    (1, 0, "“A ID line” · “S ID date”", True),
    ("note", 0, "clean_text then mailbox_from_text"),
], "«FIG» — A mailbox is read once, as the user", "Reading the mailboxes")

S2 = p(c("rspeak status") + " and " + c("rspeak list") + " read the confirmations from the mailboxes, which the users "
       "control. " + c("read_mailbox") + " in " + c("src/store.c") + " treats them as <b>untrusted data</b> and "
       "reads them <b>once per user</b>, in a single child process.", lead=True) + READING + ul([
    "The child receives on stdin the numbers of the messages that exist in " + c("sent/") + " and looks only for "
    "those: thousands of fake files in " + c("acks/") + " do not matter (5000 files: " + c("rspeak list") + " under a "
    "second, " + c("tests/engine.sh") + " group 9; before the fix, 3.9 s).",
    "Of " + c("acks/ID") + " it reads at most 200 bytes, and only if it is a regular file opened without blocking: a "
    "pipe in place of the confirmation does not block " + c("rspeak status") + " (group 9).",
    "Of " + c("state/ID.*") + " it reads the most recent modification date: that is the time of the postponement.",
    "The child's output (at most 4 MiB) goes through " + c("clean_text") + " before it is interpreted: a confirmation "
    "forged with escape sequences does not reach the administrator's terminal (scenario G3).",
    "The mailboxes read stay in memory for the whole command; the TUI forgets them at every refresh ("
    + c("mailboxes_empty") + "). Deliveries are read once per message (" + c("read_deliveries") + ").",
])

S3 = p("In the list of messages, in " + c("rspeak list") + " and in the TUI, a message is summarised <b>by its "
       "recipients</b>: how many are in each of the three states, in words and with a bar, plus the properties "
       "revoked and expired. No other word describes the state of a message (" + cap(19, 3) + ").", lead=True) + \
    code("""/* A message summarised with its recipients. */
typedef struct {
	long long id;
	msg_t m;
	int confirmed, delivered, sent;
	bool revoked, expired;
} summary_t;""", "c", "src/rspeak.h") + table(["Function", "What it does"], [
    [c("summarise(id, r)"), "reads message, recipients, deliveries and revocation date <b>before</b> counting; "
     "false if the message no longer exists, has no recipients or if the send was cancelled (" + c("failed") + ")"],
    [c("summary_text(r, out)"), "“14 confirmed · 5 delivered · 2 sent”, omitting zero counts; “all confirmed (58)” "
     "if nobody is missing"],
    ["the TUI bar", "12 marks: " + c("█") + " confirmed (green), " + c("▒") + " delivered (yellow), "
     + c("░") + " sent (red); a single sent recipient still gets at least one mark"],
], "«TAB» — Summarising a message") + \
    note("the phrase always uses the name of the state (“5 delivered”, “1 confirmed”): it is the same word as in the "
         "STATE column of " + c("rspeak status") + ".")

LIST = ("admin@server:~$ sudo rspeak list\n"
        "ID    DATE         TEXT                                      RECIPIENTS\n"
        "1     01/10 10:49  Tonight at 11 pm the mail server is upda  all confirmed (3)\n"
        "2     01/10 10:49  On Saturday from 8 am to 12 noon the ser  4 confirmed · 3 delivered · 1 sent\n"
        "3     01/10 10:49  Your account expires on Friday: please d  1 delivered\n"
        "4     01/10 10:49  [revoked] Reboot at 1 pm.                 2 delivered")

STATUS = ("admin@server:~$ sudo rspeak status 2\n"
          "Message 2 · Maintenance · 01/10 10:49 · from root\n"
          "  │ On Saturday from 8 am to 12 noon the server will be off for disk maintenance.\n"
          "  │ Please save your work by Friday evening.\n"
          "\n"
          "USER             STATE\n"
          "admin            confirmed on 01/10 10:49 (terminal pts/0)\n"
          "anna             confirmed on 01/10 10:49 (desktop)\n"
          "dario            sent, not delivered: the copy could not be written (see the log; the next rspeak "
          "command will retry)\n"
          "fabio            confirmed on 01/10 10:49 (desktop)\n"
          "kora             delivered, postponed on 01/10 10:49\n"
          "luca             delivered\n"
          "mario            delivered, postponed on 01/10 10:49\n"
          "zeno             confirmed on 01/10 10:49 (terminal pts/2)")

S4 = p("The two query commands show the same state at two levels: the list of messages and the detail "
       "of one. Both run recovery first; after that, only reads, without locks.", lead=True) + \
    term(LIST, "rspeak list: one message per line (the messages in the screenshots of chapter 14)") + ul([
    "Columns: ID, sending date (“01/10 10:49”), the first 40 columns of the first line of the text (preceded by "
    + c("[revoked]") + " and " + c("[expired]") + "), the summary phrase.",
    "A cancelled send appears as “[send cancelled: interrupted before it was saved]”: it reports an internal marker, "
    "not a state.",
]) + term(STATUS, "rspeak status: one recipient per line, with the state lines of the first table of this chapter") + ul([
    "Header: number, title and date, sender; then “REVOKED on …” and “EXPIRED” if they apply; then the text, indented.",
    "One line per recipient, in the order of " + c("recipients") + " (alphabetical), with the state line from the "
    "previous table; the same lines appear in the TUI's detail view.",
    "A non-existent or cancelled message ends with an error: “no such message: 99”, “message N was cancelled: "
    "sending was interrupted before it was saved”.",
]) + p("Times measured in the last recorded run (scenarios H2 and H3, 10 messages to 58 recipients "
       "on the test machine): " + c("rspeak list") + " 0.24 s, " + c("rspeak status") + " 0.28 s. In the prototype, "
       "before reading per user, " + c("rspeak list") + " took about 6 s.")

CHAPTER = ("State: list, status and the summary", [
    ("The state deduced from the files", S1),
    ("Reading the mailboxes", S2),
    ("A message's summary", S3),
    ("rspeak list and rspeak status", S4),
])
