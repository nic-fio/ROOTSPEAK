import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import arrow, box, c, fig, key, note, p, tui_screen, table, term, text, tip, ui, ul, warn  # noqa: E402
from _helpers import CONFIRMED, DELIVERED, SENT, REVOKED, EXPIRED, ref, screen  # noqa: E402


def column(s, w):
    return s[:w] + " " * (w - len(s[:w]))


def list_output(rows):
    """The output of rspeak list, with the same widths as the program."""
    out = ["admin@server:~$ rspeak list", f"{'ID':<5} {'DATE':<12} " + column("TEXT", 40) + "  RECIPIENTS"]
    for i, date, text_, phrase in rows:
        out.append(f"{i:<5} {date:<12} " + column(text_, 40) + "  " + phrase)
    return "\n".join(out)


def status_output(heading, body, rows, cmd):
    out = [f"admin@server:~$ {cmd}", heading]
    out += [f"  │ {r}" for r in body]
    out += ["", f"{'USER':<16} STATE"]
    out += [f"{u:<16} {s}" for u, s in rows]
    return "\n".join(out)


LIST = list_output([
    ("1", "01/10 10:49", "Tonight at 11 pm the mail server is updated.", "all confirmed (3)"),
    ("2", "01/10 10:49", "On Saturday from 8 am to 12 noon the server will be off for disk maintenance.",
     "4 confirmed · 3 delivered · 1 sent"),
    ("3", "01/10 10:49", "Your account expires on Friday: please drop by the IT office.", "1 delivered"),
    ("4", "01/10 10:49", "[revoked] Reboot at 1 pm.", "2 delivered"),
])

S1 = p("The main screen of the TUI (" + ref(3, 2) + ") and the " + c("rspeak list") + " command show all the "
       "messages sent, each summarised by its recipients in the three states. The TUI puts the most recent first and "
       "updates by itself; " + c("rspeak list") + " lists them from the oldest, once.", lead=True) + \
    term(LIST, "The same four messages as in the screenshot in chapter 3") + \
    table(["Column", "In the TUI", "In " + c("rspeak list")], [
        ["ID", "the message number", "the same: it is used for " + c("status") + ", " + c("log") + ", "
         + c("revoke") + " and " + c("remind")],
        ["DATE", "day and time of sending (day/month hours:minutes)", "the same"],
        ["MESSAGE / TEXT", "title in bold, then the first line of the text", "the first line of "
         "the text, cut at 40 characters"],
        ["RECIPIENTS", "three-colour bar and phrase (below 110 columns, confirmations out of the total)",
         "the phrase"],
    ], "«TAB» — The columns of the list") + \
    table(["Mark in front of the text", "Meaning"], [
        [c("[revoked]"), "the message has been revoked (" + ref(7, 1) + "): it is no longer shown"],
        [c("[expired]"), "the expiry has passed: it is no longer shown"],
        [c("[send cancelled: interrupted before it was saved]"), "only in " + c("rspeak list") + ": a sending "
         "stopped before the message was even saved (" + ref(12, 4) + ")"],
    ], "«TAB» — The marks in the list") + \
    note("the phrase counts recipients, not the people who have seen the message: “3 delivered” "
         "means three people with the copy in their mailbox who have not confirmed yet, logged in or not.",
         "Recipients.")

STATUS_CLI = status_output(
    "Message 2 · Maintenance · 01/10 10:49 · from root",
    ["On Saturday from 8 am to 12 noon the server will be off for disk maintenance.",
     "Please save your work by Friday evening."],
    [("admin", "confirmed on 01/10 10:49 (terminal pts/0)"),
     ("anna", "confirmed on 01/10 10:49 (desktop)"),
     ("dario", "sent, not delivered: the copy could not be written (see the log; the next rspeak command will retry)"),
     ("fabio", "confirmed on 01/10 10:49 (desktop)"),
     ("kora", "delivered, postponed on 01/10 10:49"),
     ("luca", "delivered"),
     ("mario", "delivered, postponed on 01/10 10:49"),
     ("zeno", "confirmed on 01/10 10:49 (terminal pts/2)")],
    "rspeak status 2")

S2 = p("Pressing " + key("Enter") + " on the list opens the selected message: at the top title, date, sender, expiry "
       "and any revocation, then the first lines of the text, then two tabs. The " + ui("Recipients")
       + " tab shows the state of each user, with the colours of the bar.", lead=True) + \
    tui_screen("detail", "«FIG» — A message opened in the TUI: the state of each recipient") + \
    p("The same list, for one message at a time, is obtained with " + c("rspeak status") + " followed by the number:") + \
    term(STATUS_CLI, "The state of the recipients with a command; each status line is explained in the table below") + \
    table(["Status line", "State", "What it means"], [
        [c("sent, not delivered"), SENT, "the copy is not yet in the mailbox: RootSpeak retries"],
        [c("sent, not delivered: the copy could not be written (see the log; the next rspeak command will retry)"),
         SENT, "the sending ran into an error for this user, usually a full disk"],
        [c("delivered"), DELIVERED, "has the copy; has not confirmed yet"],
        [c("delivered, written to 2 terminals"), DELIVERED, "was logged in when the message was sent, and the text "
         "appeared in two terminal windows"],
        [c("delivered, postponed on 01/10 10:49"), DELIVERED, "answered “Later” or " + c("n") + "; the time is "
         "that of the last postponement"],
        [c("delivered, not confirmed (revoked)"), DELIVERED, "the message was revoked before this user confirmed"],
        [c("delivered, not confirmed (expired)"), DELIVERED, "the message expired before this user confirmed"],
        [c("delivered, not confirmed (expired; confirmation arrived after the expiry)"), DELIVERED,
         "confirmed, but too late: the confirmation does not count"],
        [c("confirmed on 01/10 10:49 (desktop)"), CONFIRMED, "pressed “I have read it” in the dialog"],
        [c("confirmed on 01/10 10:49 (terminal pts/2)"), CONFIRMED, "answered " + c("y") + " in a terminal "
         "window or in an ssh connection (" + c("pts") + ")"],
        [c("confirmed on 01/10 10:49 (terminal tty3)"), CONFIRMED, "answered " + c("y") + " on a console of the machine"],
    ], "«TAB» — The status lines of a recipient") + \
    p("Above the list, " + c("rspeak status") + " writes " + c("REVOKED on …") + " if the message has "
      "been revoked and " + c("EXPIRED") + " if the expiry has passed. In the TUI the same information is in "
      "the line at the top, in red for a revocation.") + \
    tip("in the " + ui("Recipients") + " tab you scroll with " + key("↑") + " " + key("↓") + " and "
        + key("PgUp") + " " + key("PgDn") + "; " + key("m") + " reminds and " + key("r") + " revokes this very "
        "message; " + key("Esc") + " returns to the list.", "Message keys.")

LIFE = fig(
    '<line x1="60" y1="170" x2="860" y2="170" stroke="#94a3b8" stroke-width="2"/>'
    + "".join(f'<line x1="{x}" y1="164" x2="{x}" y2="176" stroke="#94a3b8" stroke-width="2"/>'
              + text(x, 196, t, 11.5, "#475569", "600") for x, t in
              [(100, "16:55"), (290, "17:02"), (480, "17:32"), (660, "17:40"), (820, "17:41")])
    + box(30, 70, 140, 60, "sent", "rspeak send", "grey")
    + box(220, 70, 140, 60, "delivered", "copy in the mailbox", "amber")
    + box(410, 70, 140, 60, "postponed", "stays delivered", "amber", 12)
    + box(590, 70, 140, 60, "reminded", "rspeak remind", "blue", 12)
    + box(760, 70, 120, 60, "confirmed", "“I have read it”", "green")
    + arrow(100, 132, 100, 164, "#475569") + arrow(290, 132, 290, 164, "#475569")
    + arrow(480, 132, 480, 164, "#475569") + arrow(660, 132, 660, 164, "#475569")
    + arrow(820, 132, 820, 164, "#475569")
    + text(450, 236, "There are only three states: postponing and reminding are events",
           11.5, "#334155", "600")
    + text(450, 256, "that stay in the log, and the state remains “delivered” until the confirmation.", 11.5, "#334155", "600"),
    900, 280, "«FIG» — The life of a message for one recipient, from sending to confirmation", "States and events")

S3 = p("Every message has a history made of <b>events</b>: the sending, the delivery to each recipient, the "
       "postponements, the reminders, the confirmations, a possible revocation. Events change the state of a recipient "
       "at only two points: when the copy arrives in the mailbox and when the user confirms.", lead=True) + LIFE + \
    table(["Event", "Who causes it", "Effect on the recipient's state"], [
        ["sending", "the administrator", "everyone " + SENT + " for an instant"],
        ["delivery", "RootSpeak", SENT + " → " + DELIVERED],
        ["postponement", "the user: “Later” or " + c("n"), "none: stays " + DELIVERED],
        ["reminder", "the administrator (" + key("m") + ", " + c("rspeak remind") + ")", "none: stays "
         + DELIVERED + ", but is asked again immediately"],
        ["confirmation", "the user: “I have read it” or " + c("y"), DELIVERED + " → " + CONFIRMED],
        ["revocation", "the administrator (" + key("r") + ", " + c("rspeak revoke") + ")", "none; the message becomes "
         + REVOKED + " and is no longer shown"],
        ["expiry", "time", "none; the message becomes " + EXPIRED + " and is no longer shown"],
    ], "«TAB» — Events and states") + \
    warn("a confirmation is final: it cannot be undone, neither from the TUI nor from the commands. To ask everyone "
         "again, send a new message.", "No going back.")

LOG = ("admin@server:~$ rspeak log 2\n"
       "Message 2 · Maintenance · 01/10 10:49\n"
       "2026-10-01 10:49:29  message 2 delivered to admin (terminals written: 0)\n"
       "2026-10-01 10:49:29  message 2 delivered to anna (terminals written: 0)\n"
       "2026-10-01 10:49:29  message 2: ERROR, copy for dario not written\n"
       "2026-10-01 10:49:29  message 2 delivered to mario (terminals written: 0)\n"
       "2026-10-01 10:49:29  message 2 sent by root to: admin anna dario fabio kora luca mario zeno\n"
       "2026-10-01 10:49:42  user anna: confirmed reading message 2 (desktop)\n"
       "2026-10-01 10:50:03  user mario: postponed message 2 (terminal)\n"
       "2026-10-01 10:56:36  message 2: 3 recipients reminded by admin")

S4 = p("The message's " + ui("History") + " tab, opened with " + key("Tab") + ", lists the events of the "
       "message taken from the system log, oldest first, with date and time to the second.", lead=True) + \
    tui_screen("history", "«FIG» — The history of a message in the TUI") + \
    p("With a command, the same history is read with " + c("rspeak log") + ":") + term(
        LOG, "The history with a command; each kind of line is explained in the table below") + \
    table(["Line", "When it appears"], [
        [c("message N delivered to U (terminals written: K)"), "for each copy that reached a mailbox; K is the "
         "number of terminal windows in which the text appeared when it was sent"],
        [c("message N sent by A to: …"), "at the end of each sending, with the list of recipients"],
        [c("message N: ERROR, copy for U not written"), "when a delivery fails"],
        [c("message N delivered to U (recovery)"), "when RootSpeak completes a delivery that had been left behind"],
        [c("user U: postponed message N (terminal)") + " or " + c("(desktop)"), "when the user postpones"],
        [c("user U: confirmed reading message N (channel)"), "on confirmation"],
        [c("user U: ERROR, confirmation of message N not recorded (…)"), "when the confirmation could not be "
         "saved, for example with a full disk"],
        [c("message N: K recipients reminded by A"), "at each reminder"],
        [c("message N revoked by A"), "on revocation"],
    ], "«TAB» — The lines of the history") + \
    note("the history comes from the system log, which the machine may rotate and delete after a while according to "
         "its settings. The state of the recipients, on the other hand, comes from the RootSpeak message store and remains "
         "until the message is deleted.", "History and state.")

S5 = p("Every event is also written to the machine's system log, with the tag " + c("rspeak") + ". It is the "
       "trail to use if someone asks “who sent what, and when”, even for messages that have already been deleted.",
       lead=True) + term(
    "admin@server:~$ sudo journalctl -t rspeak --since today\n"
    "Oct 01 10:49:29 server rspeak[20914]: message 2 delivered to anna (terminals written: 0)\n"
    "Oct 01 10:49:29 server rspeak[20914]: message 2 sent by root to: admin anna dario fabio kora luca mario zeno\n"
    "Oct 01 10:49:42 server rspeak[21310]: user anna: confirmed reading message 2 (desktop)",
    "The system log: the same lines as in the history above") + \
    table(["To see…", "Command"], [
        ["all of today's RootSpeak events", c("sudo journalctl -t rspeak --since today")],
        ["the events of the last hour", c('sudo journalctl -t rspeak --since "1 hour ago"')],
        ["the events as they arrive", c("sudo journalctl -t rspeak -f")],
        ["the history of one message, neatly ordered", c("rspeak log 2")],
    ], "«TAB» — Reading the log") + \
    ul([
        "User events (postponements, confirmations) are written by the users themselves: " + c("rspeak log") + " checks "
        "who wrote them and flags suspicious ones (" + ref(11, 5) + ").",
        "Deleting with " + c("rspeak purge") + " removes the message from the message store, but its events remain in the "
        "log.",
    ])

S6 = p("When there are many messages, the " + key("/") + " key of the TUI shows only those that contain a given "
       "text, searched in the title and in the whole message, ignoring upper and lower case.", lead=True) + \
    screen("search", "«FIG» — Searching: type the text and press Enter") + \
    screen("search-results", "«FIG» — The result: the searched text at the bottom right") + \
    table(["Key", "What it does"], [
        [key("/"), "opens the search; if there already was one, offers it again for editing"],
        [key("Enter"), "applies the search"],
        [key("Esc") + " in the search dialog", "leaves the list as it was"],
        [key("Esc") + " in the list", "clears the search and shows all the messages again"],
    ], "«TAB» — The search keys") + \
    note("if no message contains the text, the list says “No message contains the search text.” Accented letters must be typed in the same upper or lower case as in the "
         "message.", "No results.")

CHAPTER = ("Following the confirmations", [
    ("The list of messages", S1),
    ("The state of each recipient", S2),
    ("The life of a message", S3),
    ("The history of a message", S4),
    ("The system log", S5),
    ("Searching for a message", S6),
])
