import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import arrow, box, c, diamond, fig, flow, key, note, p, path, steps, table, term, text, tip, warn  # noqa: E402
from _helpers import CONFIRMED, DELIVERED, SENT, ref  # noqa: E402

S1 = p("When a command fails, " + c("rspeak") + " prints a line in red that starts with " + c("rspeak:")
       + ", says what to correct and exits with status 1. In the TUI the same line appears in the result "
       "dialog.", lead=True) + term(
    'admin@server:~$ rspeak send --to mrio "Meeting at 11."\n'
    "rspeak: no such user: mrio", "A typical error: a misspelt user name") + \
    table(["Message", "What it means", "What to do"], [
        [c("missing --to"), "no recipient", "add " + c("--to") + " (" + ref(5, 1) + ")"],
        [c("missing value for --to"), "an option without its value (the same applies to " + c("--title") + ", "
         + c("--expires") + ", " + c("--file") + ")", "write the value after the option"],
        [c("no such user: NAME"), "the name is not a user of the machine", "check the name"],
        [c("no such group: NAME"), "the group after " + c("@") + " does not exist", "check the group name"],
        [c("no recipients"), "the recipients given are empty, for example " + c("online") + " when nobody is "
         "logged in", "choose other recipients"],
        [c("empty message"), "the text is missing, or contains only spaces", "write the text"],
        [c("message too long: N bytes (at most 65536)"), "the text exceeds 64 KB",
         "shorten it, or put the full text in a shared file and send the message with its path"],
        [c("invalid expiry: X"), "the expiry was not understood", "use " + c("2h") + " or "
         + c('"2026-10-04 12:00"') + " (" + ref(5, 3) + ")"],
        [c("the expiry is already in the past"), "the date given is in the past", "correct the date"],
        [c("unknown option: X"), "misspelt option", c("rspeak --help")],
        [c("unknown command: X (rspeak --help for the guide)"), "misspelt command", c("rspeak --help")],
        [c("missing message ID"), c("status") + ", " + c("revoke") + ", " + c("remind") + " or " + c("log")
         + " without a number", "add the number, taken from " + c("rspeak list")],
        [c("no such message: ID"), "no message with that number (or already deleted)", "check with "
         + c("rspeak list")],
        [c("missing duration, for example 90d") + "<br>" + c("invalid duration: X (for example 90d, 12h, 30m)"),
         c("rspeak purge") + " without a duration or with a misspelt duration", "write a number followed by "
         + c("d") + ", " + c("h") + " or " + c("m")],
        [c("message N has been revoked: nobody to remind") + "<br>" + c("message N has expired: nobody to remind"),
         "reminder for a message that is no longer shown", "nothing; to ask again, send a new message"],
        [c("message N not delivered to: … (see the log; the next rspeak command will retry)"),
         "the copy could not be written for those users; the others received it",
         "fix the cause, often a full disk (" + ref(12, 4) + ")"],
        [c("message N revoked, but some copies could not be removed from the mailboxes: the next rspeak command "
           "will retry"), "during the revocation a user's mailbox could not be reached", "nothing: RootSpeak retries"],
        [c("FILE: …"), "with " + c("--file") + ": the file does not exist or cannot be read; the explanation is the "
         "system's own (for example " + c("No such file or directory") + ")", "check the path"],
    ], "«TAB» — The error messages")

S2 = table(["Problem", "Likely cause", "Remedy"], [
    [c("rspeak: command not found"), "RootSpeak is not installed", "run " + c("./install.sh") + " (" + ref(2, 2) + ")"],
    [c("Permission denied"), "whoever runs it is not an administrator", "this is intended (" + ref(11, 1) + ")"],
    [c("rspeak") + " on its own shows the help instead of the TUI", "the terminal is smaller than 80 columns or 20 "
     "rows, or the output is not a terminal", "enlarge the window, or use the commands"],
    ["the TUI closed by itself", "the window was shrunk below 80 × 20", "enlarge it and reopen " + c("rspeak")],
    ["the text reaches the terminal but the question does not", "the terminal window was open before the "
     "installation; or the shell is sh, dash or ksh (question only at login) or tcsh (no question); "
     "or zsh was installed after RootSpeak", "open a new window or log in again; for zsh installed later, "
     "run " + c("./install.sh") + " again (" + ref(8, 3) + ")"],
    ["no dialog appears on the desktop", c("zenity") + " is missing, or the graphical session was "
     "started before the installation and the agent did not start", "install " + c("zenity") + "; the agent "
     "starts by itself with the first new message or at the next login"],
    ["two identical dialogs", "the same message was sent twice (two different numbers in the list)",
     "revoke the duplicate (" + ref(7, 1) + ")"],
    ["a user who logged in with " + c("su") + " does not see the text when it is sent", "with " + c("su")
     + " the terminal window still belongs to whoever opened it", "they still see the question at the next "
     "prompt; with " + c("ssh") + " everything works normally"],
    ["a user sees “The confirmation could not be recorded”",
     "their mailbox is not writable, for example because the disk is full",
     "free some space: the message is asked again and the confirmation is not lost"],
    ["a recipient stays " + SENT, "their copy could not be written", "see " + ref(12, 4)],
    [key("Ctrl", "E") + " opens nano and not my editor", "sudo does not keep " + c("VISUAL") + " and "
     + c("EDITOR"), ref(10, 3)],
    ["a user says they saw nothing", "—", "follow the procedure in " + ref(12, 3)],
], "«TAB» — Frequent problems")

DIAGNOSI = fig(
    diamond(170, 110, 260, 90, "What state is it?", "navy")
    + box(360, 40, 240, 54, "sent", "the copy did not arrive: 12.4", "grey")
    + box(360, 118, 240, 54, "delivered", "has the copy, has not confirmed", "amber")
    + box(360, 196, 240, 54, "confirmed", "stated they have read it", "green")
    + box(650, 118, 230, 54, "Logged in? Postponing?", "message details and history", "blue")
    + box(650, 196, 230, 54, "From where, and when", "desktop or terminal, with the time", "blue")
    + path([(210, 80), (210, 67), (356, 67)], "#475569")
    + arrow(300, 110, 356, 140, "#475569")
    + path([(210, 140), (210, 223), (356, 223)], "#475569")
    + arrow(602, 145, 646, 145, "#0050C0") + arrow(602, 223, 646, 223, "#0050C0")
    + text(450, 290, "The starting point is always the message details (Enter in the TUI, or rspeak status)",
           11.5, "#334155", "600"),
    900, 310, "«FIG» — Where to start when a user says they did not see a message", "The diagnosis")

S3 = p("It is the most common question. The answer is almost always in the message details and in its history.",
       lead=True) + DIAGNOSI + steps([
        "Open the message in the TUI (" + key("Enter") + ") or run " + c("rspeak status ID") + ", and find "
        "the user's line.",
        "If it is " + CONFIRMED + ", the line says when and from where: for example “confirmed on 30/09 16:56 "
        "(desktop)”. The user has confirmed, perhaps without reading carefully ("
        + ref(11, 3) + ").",
        "If it is " + DELIVERED + ", look at the details: “written to 2 terminals” "
        "means that the text appeared on their screens; “postponed on …” that they saw the "
        "question or the dialog and postponed it. If neither is there, they have probably not logged in yet.",
        "If it is " + SENT + ", the copy did not reach their mailbox: see " + ref(12, 4) + ".",
        "In the History tab (" + key("Tab") + "), or with " + c("rspeak log ID")
        + ", you find all the events, postponements included, to the second.",
        "If needed, remind them (" + ref(7, 2) + "): the dialog comes back on their desktop at once.",
    ]) + tip("a user who works only through ssh and with a shell such as tcsh does not get the question in the "
             "terminal: they see the text when it is sent, but can confirm only from the desktop. With bash, zsh "
             "or fish the problem does not arise.",
             "Unusual shells.")

RECUPERO = flow([("Sending interrupted", "full disk, power cut…", "grey"), ("Next rspeak", "list, status, TUI…", "navy"),
                 ("Recovery", "rewrites the missing copies", "blue"), ("All delivered", "or a notice of who is missing", "green")],
                "«FIG» — RootSpeak completes the deliveries left behind by itself", "Recovery")

S4 = p("If a sending is interrupted halfway (the disk fills up, " + c("rspeak") + " is stopped, the power goes) "
       "RootSpeak does not lose the message: the next time it is used, it resumes from where it stopped.", lead=True) + \
    RECUPERO + \
    table(["Notice", "What it means", "What to do"], [
        [c("rspeak: completed delivery of message N to K recipients"), "the missing copies have been written: those recipients are now " + DELIVERED,
         "nothing"],
        [c("rspeak: message N still not delivered to K recipients (see rspeak status N)"), "for someone the copy still cannot be written", "fix the cause, usually disk space; then "
         "use " + c("rspeak") + " again"],
        [c("rspeak: message N was interrupted before being saved and has been cancelled"), "the sending stopped before the message was "
         "even saved: nobody received it", "send it again"],
        [c("[send cancelled: interrupted before it was saved]") + " in " + c("rspeak list"), "the same case, in the list", "send it again"],
    ], "«TAB» — The recovery notices") + \
    note("recovery starts at the beginning of " + c("rspeak send") + ", " + c("list") + ", " + c("status") + ", "
         + c("revoke") + ", " + c("remind") + ", " + c("log") + " and when the TUI opens. Nothing is needed "
         "other than using RootSpeak.", "When it starts.") + \
    warn("with a full disk the users' confirmations cannot be saved either: users see “The confirmation could not "
         "be recorded” and the message is asked "
         "again. Freeing space in " + c("/var/lib") + " solves both.", "Full disk.")

S5 = table(["What", "Where"], [
    ["the command", c("/usr/local/bin/rspeak")],
    ["the settings", c("/etc/rootspeak/rootspeak.conf")],
    ["messages and confirmations", c("/var/lib/rootspeak/")],
    ["the log", c("sudo journalctl -t rspeak")],
    ["the help", c("rspeak --help")],
    ["the manuals", c("/usr/local/share/doc/rootspeak/User Manual.html") + " and " + c("Technical Manual.html")],
    ["the shell hooks", c("/etc/profile.d/rootspeak.sh") + ", " + c("/usr/local/lib/rootspeak/rootspeak.bash") + ", "
     + c("rootspeak.zsh") + ", " + c("/etc/fish/conf.d/rootspeak.fish")],
    ["the desktop autostart", c("/etc/xdg/autostart/rootspeak-agent.desktop")],
    ["the code", c("https://github.com/nic-fio/ROOTSPEAK") + " (private)"],
], "«TAB» — Where to find things") + \
    tip("when something does not add up, the places to look are, in order: the message details, its history, "
        "the log with " + c("sudo journalctl -t rspeak") + ", and the built-in help.", "Where to look.")

CHAPTER = ("Troubleshooting", [
    ("Error messages", S1),
    ("Frequent problems", S2),
    ("“I didn't see any message”", S3),
    ("Interrupted sendings", S4),
    ("Useful files and folders", S5),
])
