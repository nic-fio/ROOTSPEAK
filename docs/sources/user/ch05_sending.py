import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import arrow, box, c, code, diamond, fig, key, note, p, tui_screen, seq, steps, table, term, text, tip, ui, ul, warn  # noqa: E402
from _helpers import DELIVERED, SENT, ref  # noqa: E402

SETS = fig(
    '<rect x="20" y="44" width="860" height="236" rx="18" fill="#eef4ff" stroke="#0050C0" stroke-width="2"/>'
    + text(40, 70, "all: every user of the machine", 13, "#003a90", "700", "start")
    + text(40, 88, "with a UID of 1000 or above and a real shell; no root, no service accounts", 11, "#475569", "400", "start")
    + '<ellipse cx="330" cy="182" rx="210" ry="76" fill="#0050C0" fill-opacity="0.13" stroke="#0050C0" stroke-width="1.6"/>'
    + text(210, 170, "online", 13, "#003a90", "700")
    + text(210, 188, "whoever is logged in now", 11, "#334155")
    + '<ellipse cx="560" cy="182" rx="200" ry="70" fill="#d97706" fill-opacity="0.14" stroke="#d97706" stroke-width="1.6"/>'
    + text(670, 170, "@developers", 13, "#92400e", "700")
    + text(670, 188, "the members of a group", 11, "#334155")
    + text(446, 176, "logged in and", 11, "#334155") + text(446, 192, "in the group", 11, "#334155")
    + '<circle cx="818" cy="112" r="7" fill="#003a90"/>' + text(818, 134, "mario", 11.5, "#003a90", "700")
    + text(818, 150, "one user", 10.5, "#475569"),
    900, 300, "«FIG» — Recipients can be combined: --to mario,@developers sends to Mario and to the whole group",
    "Who receives the message")

S1 = p("The " + ui("To") + " field of the TUI and the " + c("--to") + " option of the commands say who receives "
       "the message. Several recipients can be given, separated by commas and without spaces: anyone who appears more "
       "than once, for example because they belong to two groups, receives the message only once.", lead=True) + \
    table(["You write", "Who receives it", "Example"], [
        ["a name", "that user, even if not logged in", c("mario")],
        ["several names", "each of them", c("mario,anna,luca")],
        [c("@group"), "the members of a system group, including those who have it as their primary group",
         c("@developers")],
        [c("all"), "every user of the machine, logged in or not: UID of 1000 or above (the limits in "
         + c("/etc/login.defs") + ") and a real shell, that is, not " + c("nologin") + " or " + c("false"), c("all")],
        [c("online"), "among the users of " + c("all") + ", whoever is logged in right now, in any way "
         "(desktop, console, ssh)", c("online")],
        ["a combination", "the union of all of them", c("mario,@developers")],
    ], "«TAB» — How to specify the recipients") + SETS + \
    note("a group given with " + c("@") + " includes all its members, even the accounts that " + c("all") + " leaves out. "
         "In the TUI, when you move from the " + ui("To") + " field to the next one, the number of recipients appears on "
         "the right, or an error if a name does not exist: this is checked before sending.", "Good to know.") + \
    warn(c("online") + " is evaluated at the moment of sending: someone who logs in a minute later does not receive "
         "the message. For a notice that must reach everyone sooner or later, use " + c("all") + ".",
         "online is a snapshot.")

S2 = p("The <b>title</b> is optional and fits on one line: it appears at the top of the message in the terminal, in "
       "the desktop dialog and in the TUI list. The <b>text</b> can have several lines.", lead=True) + \
    table(["How", "Where", "Example"], [
        ["typed in the TUI", "the " + ui("Text") + " field; " + key("Enter") + " starts a new line", "—"],
        ["typed in your own editor", "TUI, " + key("Ctrl", "E") + " (" + ref(5, 5) + ")", "—"],
        ["in quotes, at the end of the command", c("rspeak send"), c('rspeak send --to mario "Message text"')],
        ["from a file", c("rspeak send --file"), c("rspeak send --to @developers --file notice.txt")],
        ["from another command", c("rspeak send") + ", with no text and no " + c("--file"), c("df -h | rspeak send --to anna")],
        ["typed on the spot", c("rspeak send") + " in a terminal: type the text, then " + key("Ctrl", "D"),
         c("rspeak send --to mario")],
    ], "«TAB» — The ways to supply the text") + \
    code("From Monday 19 October passwords expire every 90 days.\n"
         "At the first login after the expiry the system will ask you to change it.\n"
         "For problems: IT office, extension 214.", "text",
         "notice.txt, sent below to everyone with a title") + \
    term('admin@server:~$ rspeak send --to all --title "New rule for passwords" --file notice.txt\n'
         "Message 3 sent to 24 users.") + \
    table(["Rule", "Why"], [
        ["at most 64 KB of text (65536 bytes: about 30 pages)", "beyond that, the desktop dialog could not "
         "show it; RootSpeak refuses with “message too long”. The TUI shows the count below the "
         "text, in red when the limit is exceeded"],
        ["the text cannot be empty or made only of spaces", "RootSpeak refuses with “empty message”"],
        ["blank lines at the end of the text are removed", "the message ends with the last line written"],
        ["the title fits on one line", "line breaks and tabs in the title become spaces"],
        ["invisible characters and colour codes are removed", "a message cannot disrupt the users' "
         "terminals (" + ref(11, 4) + ")"],
    ], "«TAB» — The rules for the text") + \
    note("in commands, the options must be written <b>before</b> the text: everything after the first word that is "
         "not an option is part of the message.", "Order matters.")

EXPIRY_FIG = fig(
    diamond(250, 150, 280, 104, "Stops mattering after a while?", "navy")
    + box(566, 48, 314, 72, "expiry: 15m, 2h, 3d…", "afterwards it is no longer shown or asked again", "blue")
    + box(566, 180, 314, 72, "no expiry", "stays until everyone confirms", "dark")
    + arrow(390, 140, 562, 90, "#0050C0", False, "yes", 474, 104)
    + arrow(390, 160, 562, 212, "#475569", False, "no", 474, 204)
    + text(250, 238, "in both cases confirmation is requested", 11.5, "#334155", "600"),
    900, 272, "«FIG» — The expiry is for notices that are only valid for a short time", "Expiry or not")

S3 = p("Every message asks for confirmation. For notices that are only valid for a short time, such as “the service "
       "restarts in 5 minutes”, you add an <b>expiry</b>: once that moment has passed the message is no longer shown "
       "or asked again, and whoever has not seen it in time will never see it.", lead=True) + EXPIRY_FIG + \
    table(["You write (the " + ui("Expires") + " field or " + c("--expires") + ")", "The message expires"], [
        [c("30m"), "in 30 minutes"],
        [c("2h"), "in 2 hours"],
        [c("3d"), "in 3 days"],
        [c("2026-10-04 12:00"), "Sunday 4 October 2026 at 12:00 (in the command, in quotes: "
         + c('--expires "2026-10-04 12:00"') + ")"],
        [c("tomorrow 18:00"), "tomorrow at 18:00"],
    ], "«TAB» — How to specify the expiry. In the example below the message expires after 15 minutes") + \
    term('admin@server:~$ rspeak send --to online --expires 15m "The web service restarts at 13:00."\n'
         "Message 2 sent to 3 users.") + ul([
        "On expiry, a dialog that is still open closes by itself, and a question waiting in the terminal is "
        "interrupted with “[RootSpeak] The message has expired.”",
        "A confirmation given after the expiry does not count: the recipient stays " + DELIVERED + ", “not "
        "confirmed (expired)”.",
        "In the list the message appears with " + c("[expired]") + " in front; the detail view says when "
        "it expired.",
    ]) + note("dates in words are read by the system's " + c("date") + " command, which understands them in "
              "English only (" + c('"saturday 12:00"') + ", " + c('"tomorrow 18:00"') + "). The year-month-day "
              "hours:minutes format always works. A date already in the past is refused with “the expiry is already "
              "in the past”.", "Dates.")

S4 = p("In the TUI the " + key("n") + " key opens the " + ui("New message") + " screen: three one-line fields "
       "and the text box below them.", lead=True) + \
    tui_screen("new", "«FIG» — The New message screen (real screenshot)") + \
    table(["Field", "What to write", "Required"], [
        [ui("To"), "the recipients, as in " + ref(5, 1) + "; on the right, when you leave the field, how many there are", "yes"],
        [ui("Title"), "one line", "no"],
        [ui("Expires"), c("30m") + ", " + c("2h") + ", " + c("3d") + " or a date, as in " + ref(5, 3), "no"],
        [ui("Text"), "the message, on several lines; below it, the count, for example “97 of 65536 bytes”", "yes"],
    ], "«TAB» — The fields of a new message") + \
    table(["Keys", "What they do"], [
        [key("Tab") + " / " + key("Shift", "Tab"), "next / previous field, including the text"],
        [key("Enter") + " or " + key("↓") + " in a field", "moves to the field below"],
        [key("Enter") + " in the text", "starts a new line"],
        [key("←") + " " + key("→") + " " + key("↑") + " " + key("↓") + ", " + key("Home") + " " + key("End"),
         "move the cursor"],
        [key("⌫") + " " + key("Del"), "delete a character"],
        [key("Ctrl", "E"), "opens the text in your own editor (" + ref(5, 5) + ")"],
        [key("Ctrl", "S"), "sends, after the summary"],
        [key("Esc"), "discards; if something has already been written it asks for confirmation: "
         + ui("Discard the message?")],
    ], "«TAB» — The keys of a new message") + \
    p(key("Ctrl", "S") + " shows a summary with the recipients (and how many there are), title, expiry and length of the "
      "text. " + key("y") + " sends, " + key("n") + " or " + key("Esc") + " returns to the message without losing "
      "anything.") + \
    tui_screen("send", "«FIG» — The summary before sending") + \
    ul([
        "If sending succeeds, " + ui("Message sent") + " appears with the reply from RootSpeak; any key "
        "returns to the list.",
        "If something goes wrong, " + ui("Sending result") + " appears with the reason: a wrong "
        "recipient (for example “rspeak: no such user: mrio”) stops the sending, and any key returns "
        "to the message so it can be corrected; a copy that could not be written is listed, and RootSpeak retries by itself "
        "at the next command.",
    ])

S5 = p("For long texts your own editor is more convenient. " + key("Ctrl", "E") + " closes the TUI for a moment and "
       "opens the text written so far in the editor; when you save and quit you return to the TUI with the updated "
       "text.", lead=True) + steps([
        "In the new message, press " + key("Ctrl", "E") + ".",
        "Write or paste the text in the editor, save and quit (with nano: " + key("Ctrl", "O") + ", "
        + key("Enter") + ", " + key("Ctrl", "X") + ").",
        "Check the text in the box and send with " + key("Ctrl", "S") + ".",
    ]) + table(["Editor used", "When"], [
        ["the one set in " + c("VISUAL") + " or, if that is missing, in " + c("EDITOR"), "if sudo keeps these "
         "variables (" + ref(10, 3) + ")"],
        [c("nano"), "otherwise"],
        [c("vi"), "if nano is not installed"],
    ], "«TAB» — Which editor opens") + \
    note("the editor runs with the administrator's identity, not as root: it opens a temporary file that belongs "
         "to the administrator and that RootSpeak deletes on return.", "Security.")

SENDING = seq([("Administrator", "Ctrl+S or rspeak send", "dark"), ("RootSpeak", "message store", "navy"),
             ("Mario's mailbox", "/var/lib/rootspeak/users", "light"), ("Mario's sessions", "terminals and desktop", "blue")], [
    (0, 1, "message and recipients"),
    (1, 1, "reference copy, number 3"),
    (1, 2, "copy for Mario (as Mario)"),
    ("note", 2, "delivered".ljust(10)),
    (1, 3, "text in every open terminal"),
    (1, 3, "wakes the desktop agent: dialog"),
    (1, 0, "“Message 3 sent to 1 user.”", True),
    ("sep", "later, at the next prompt or at login".ljust(40)),
    (2, 3, "confirmation question, until confirmed"),
], "«FIG» — What happens when a message is sent to Mario", "Sending step by step")

S6 = p("When a message is sent, RootSpeak saves it, puts a copy in each recipient's mailbox and makes it appear at once "
       "wherever the user is logged in. It all happens in a few moments.", lead=True) + SENDING + \
    table(["Reply from RootSpeak", "What it means"], [
        [c("Message 3 sent to 24 users."), "All the copies are in the mailboxes: every recipient is "
         + DELIVERED + "."],
        [c("Message 3 delivered to 23 of 24 recipients.") + "<br>"
         + c("rspeak: message 3 not delivered to: sara (see the log; the next rspeak command will retry)"), "A copy could not be written, usually because "
         "the disk is full: Sara is " + SENT + ". RootSpeak retries by itself (" + ref(12, 4) + ")."],
        [c("Message 3 revoked while sending: delivery stopped."), "Another administrator revoked it "
         "while it was being sent."],
        [c("rspeak: …"), "An error: the message was not sent (" + ref(12, 1) + ")."],
    ], "«TAB» — The replies when sending") + \
    p("The text written to the terminals when the message is sent appears even if the user is working; the "
      "confirmation question, instead, only arrives when the user is back at the prompt, so as not to interrupt a "
      "command halfway.")

S7 = table(["I want to…", "Command"], [
    ["notify a user and know whether they have read it", c('rspeak send --to anna "Your account expires on Friday."')],
    ["warn whoever is logged in that I am about to reboot",
     c('rspeak send --to online --expires 15m "Reboot at 13:00: save your work."')],
    ["tell everyone about a new rule", c('rspeak send --to all --title "Password" --file rule.txt')],
    ["write to a work group", c('rspeak send --to @developers --expires 2d "Deadline: Thursday at 18:00."')],
    ["write to two people and a group", c('rspeak send --to mario,anna,@interns "Meeting at 11."')],
    ["send the output of a command", c("df -h /home | rspeak send --to anna --title \"Disk space\"")],
    ["send a notice from cron, every Monday at 8:00", c("0 8 * * 1  /usr/local/bin/rspeak send --to all --file /etc/weekly-notice.txt")],
], "«TAB» — Ready-made commands for the most common cases") + \
    tip("in cron (root's crontab, " + c("sudo crontab -e") + ") " + c("rspeak") + " is already root and does not ask for "
        "the password. It is best to give the full path of the command.", "Automatic sending.")

CHAPTER = ("Writing and sending messages", [
    ("Choosing the recipients", S1),
    ("Title and text", S2),
    ("The expiry", S3),
    ("Writing in the TUI", S4),
    ("Your own editor", S5),
    ("What happens when sending", S6),
    ("Ready-made commands", S7),
])
