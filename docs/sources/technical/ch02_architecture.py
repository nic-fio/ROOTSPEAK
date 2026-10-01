from build import arrow, box, c, fig, note, p, path, seq, table, text, ul, zone


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


PRINCIPI = fig(
    box(20, 50, 205, 64, "No daemon", "delivery at send time", "navy")
    + box(245, 50, 205, 64, "Always as root", "sudo before anything", "navy")
    + box(470, 50, 205, 64, "Never block", "one can always postpone", "navy")
    + box(695, 50, 185, 64, "Three states", "for each recipient", "navy")
    + box(20, 140, 205, 64, "Root does not trust", "mailboxes as the user", "blue")
    + box(245, 140, 205, 64, "Data, not code", "rootspeak.conf, messages, .mo", "blue")
    + box(470, 140, 205, 64, "No written state", "deduced from the files", "blue")
    + box(695, 140, 185, 64, "A single source", "for states and texts", "blue"),
    900, 228, "«FIG» — The eight principles that guide the code", "Principles")

S1 = p("RootSpeak is small on purpose: two programs, files in a single folder, the systemd libraries already present "
       "on the system. The design favours <b>verifiability</b>: every state can be reconstructed by looking at the "
       "files, and every step that can be interrupted leaves a mark that the next command knows how to "
       "repair.", lead=True) + PRINCIPI + table(["Principle", "What it means in the code"], [
    ["<b>No daemon</b>", "Delivery is done by " + c("rspeak send") + " at the moment of sending; the rest is done by "
     "the shell hook and the desktop agent, which start with the user's sessions. Recovery of interrupted sends "
     "runs at the start of the following commands."],
    ["<b>" + c("rspeak") + " always as root</b>", "The command relaunches itself with " + c("sudo") + " before looking "
     "at its arguments, including " + c("--help") + " and " + c("version") + " (" + cap(4, 1) + ")."],
    ["<b>Never block</b>", "Every message asks for confirmation and insists with reminders, but the user can always "
     "postpone. Sessions without a terminal are not touched."],
    ["<b>Three states</b>", "For each recipient: sent, delivered, confirmed. Expiry and revocation are properties "
     "of the message; the " + c("stato_e") + " enumeration in " + c("src/rspeak.h") + " has only three values."],
    ["<b>Root does not trust the mailboxes</b>", "Every access by root to " + c("users/U") + " happens in a child "
     "process with U's identity, with a time limit (" + cap(7) + ")."],
    ["<b>Data, not code</b>", "Configuration, messages, confirmations and catalogs are data files read with size "
     "limits; nothing that comes from outside is executed."],
    ["<b>No written state</b>", "The state of a recipient is not written anywhere: it is deduced from "
     + c("sent/ID/delivery") + " and from the mailbox (" + cap(10, 1) + ")."],
    ["<b>A single source</b>", "The TUI uses the same functions as " + c("rspeak list") + " and " + c("rspeak status")
     + "; the built-in help and the user manual's reference come from the same texts."],
], "«TAB» — The principles and their consequences")

AMBITI = fig(
    zone(20, 44, 270, 250, "Trusted · root")
    + box(42, 80, 226, 56, "rspeak", "root:admin group · 750", "navy")
    + box(42, 150, 226, 56, "sent/ · rootspeak.conf", "written only by root", "dark")
    + box(42, 220, 226, 56, "journal", "_UID set by the system", "soft")
    + zone(315, 44, 270, 250, "Boundary")
    + box(337, 80, 226, 56, "come_utente", "child with U's identity", "green")
    + box(337, 150, 226, 56, "pulisci", "texts and confirmations cleaned", "green")
    + box(337, 220, 226, 56, "size and time limits", "200 bytes, 20 seconds", "green", 12)
    + zone(610, 44, 270, 250, "Untrusted · user U")
    + box(632, 80, 226, 56, "users/U/", "U can do anything in the mailbox", "amber")
    + box(632, 150, 226, 56, "rootspeak-user", "runs as U", "amber")
    + box(632, 220, 226, 56, "U's terminals", "U's /dev/pts/N", "amber")
    + arrow(270, 108, 335, 108) + arrow(565, 108, 630, 108)
    + arrow(630, 178, 565, 178, "#d97706") + arrow(335, 178, 270, 178, "#d97706"),
    900, 312, "«FIG» — The three privilege domains and the boundary between root and the users", "Who is trusted")

S2 = p("A message crosses three domains with different privileges. The rule is simple: <b>everything that passes "
       "between root and a user crosses a controlled boundary</b>, in both directions.", lead=True) + AMBITI + \
    table(["Domain", "Who", "Writes", "Reads"], [
        ["administrator", c("rspeak") + ", as root", c("sent/") + ", the mailboxes (only as the user), the users' "
         "terminals, the journal", "the whole message store; the mailboxes only as the user"],
        ["user", c("rootspeak-user") + ", as U", "their own mailbox, the journal (with their own " + c("_UID") + ")",
         "their own mailbox; never " + c("sent/")],
    ], "«TAB» — Who writes and who reads") + \
    note("the TUI is not a separate domain: it is " + c("rspeak") + " itself, and its actions are the commands run in "
         "a child process (" + cap(14, 1) + ").")

PROGRAMMI = fig(
    box(20, 60, 190, 60, "src/*.c", "11 modules, 9 headers", "dark")
    + box(290, 30, 250, 56, "build/rspeak", "rspeak, tui, guida, archivio + common", "navy")
    + box(290, 110, 250, 56, "build/rootspeak-user", "rootspeak-user + common", "blue")
    + box(620, 30, 260, 56, "$PREFIX/bin/rspeak", "root:sudo · 750", "navy")
    + box(620, 110, 260, 56, "$PREFIX/lib/rootspeak/rootspeak-user", "outside the PATH · 755", "blue", 12)
    + box(290, 190, 250, 56, "build/locale/*/rootspeak.mo", "msgfmt --check from po/", "soft")
    + box(620, 190, 260, 56, "$PREFIX/share/locale/", "one .mo per language", "soft")
    + arrow(212, 72, 288, 58) + arrow(212, 90, 288, 138) + arrow(212, 108, 288, 218)
    + arrow(542, 58, 618, 58) + arrow(542, 138, 618, 138) + arrow(542, 218, 618, 218)
    + text(115, 144, "make", 11, "#475569", "600") + text(580, 100, "install.sh", 11, "#475569", "600"),
    900, 272, "«FIG» — From the sources to the installed programs", "Two programs")

S3 = p("The Makefile produces two executables and one catalog per language. The common parts ("
       + c("comune testo lingua evento utente sessioni") + ") go into both; " + c("rspeak") + " adds "
       + c("rspeak.o") + ", " + c("guida.o") + ", " + c("archivio.o") + " and " + c("tui.o") + ".", lead=True) + \
    PROGRAMMI + table(["Program", "Where", "Permissions", "Who runs it"], [
        [c("rspeak"), c("/usr/local/bin/rspeak"), c("750") + ", " + c("root:") + " administrators' group",
         "an administrator; it relaunches itself with sudo"],
        [c("rootspeak-user"), c("/usr/local/lib/rootspeak/rootspeak-user"), c("755"), "the shell hook ("
         + c("prompt") + ") and desktop autostart (" + c("agent") + "); never the user by hand"],
    ], "«TAB» — The two programs") + \
    p("Both depend only on glibc and libsystemd (" + c("sd-login") + " for sessions, "
      + c("sd-journal") + " for the log). At run time they also need " + c("sudo") + ", " + c("zenity")
      + ", " + c("systemd-run") + " and " + c("date") + "; " + c("notify-send") + " if available.")

PERCORSO = seq([("rspeak send", "root", "navy"), ("sent/ID", "message store", "dark"), ("U's mailbox", "users/U", "blue"),
                ("Terminals", "/dev/pts/N", "blue"), ("U's agent", "desktop", "light")], [
    (0, 1, "incomplete, msg, recipients"),
    (0, 2, "copy as U, check"),
    (0, 1, "line in delivery"),
    (0, 3, "text, at most 3 s"),
    (0, 4, "SIGUSR1 (as U)"),
    ("sep", "the user replies".ljust(17)),
    (4, 2, "reads inbox/ID"),
    (4, 2, "«Ho letto»: acks/ID"),
    ("nota", 2, "inbox/ID → read/ID"),
], "«FIG» — The path of a message, from sending to confirmation; «Ho letto» is the “I have read it” button",
   "The path of a message", width=920)

S4 = p("The complete path touches every subsystem. Here it is in brief; each step has its own chapter.",
       lead=True) + PERCORSO + table(["Step", "Who", "Effect", "Where"], [
    ["1", c("rspeak send"), "resolves the recipients, cleans text and title, takes an ID, writes " + c("sent/ID/")
     + " with the " + c("incomplete") + " marker", cap(8, 2)],
    ["2", c("rspeak send") + " as U", "writes " + c("users/U/inbox/ID") + " (first " + c(".tmp") + ", then renames), "
     "checks that it is there, then records the delivery in " + c("sent/ID/delivery"), cap(8, 3)],
    ["3", c("rspeak send"), "writes the text to each of U's terminals, in the language of that terminal", cap(8, 4)],
    ["4", c("rspeak send") + " as U", "wakes the desktop agent with " + c("SIGUSR1") + ", or starts it with "
     + c("systemd-run --user"), cap(8, 5)],
    ["5", "hook or agent", "show the message and ask for confirmation", cap(11) + ", " + cap(12)],
    ["6", c("rootspeak-user"), "creates " + c("acks/ID") + " (the first one counts) and moves the message to " + c("read/"), cap(13)],
    ["7", c("rspeak status") + ", TUI", "deduce the state by comparing " + c("sent/ID") + " with the mailboxes", cap(10)],
], "«TAB» — The steps of a message")

S5 = p("RootSpeak does not use utmp, which does not record many modern terminals, but <b>logind</b> and the terminal "
       "devices. The useful question is not “how is the user logged in” but “on which channels can I reach them "
       "right now”.", lead=True) + table(["User session", "How RootSpeak finds it", "Channel"], [
    ["text console (" + c("tty3") + ")", "logind session of type " + c("tty") + " with terminal " + c("tty3"),
     "terminal"],
    ["ssh with a terminal", "pseudo-terminal " + c("/dev/pts/N") + " owned by the user", "terminal"],
    ["desktop terminal, tmux", "pseudo-terminal owned by the user", "terminal"],
    ["X11 or Wayland desktop", "logind session of type " + c("x11") + " or " + c("wayland"), "desktop agent"],
    ["ssh without a terminal, scp, cron", "no terminal", "none: they are not touched"],
    ["user not logged in", "—", "the mailbox, read at the next login"],
], "«TAB» — Sessions and delivery channels") + ul([
    "The mailbox acts as a queue: a message that reaches no channel when it is sent appears at the next login "
    "(question in the terminal) or at the agent's first round (dialog).",
    "Writing the text to a terminal does not count as a confirmation: the question arrives at the next prompt.",
]) + note("a terminal in which the user switched identity with " + c("su") + " still belongs to whoever opened it: "
          + c("rspeak send") + " does not write to it. The shell hook reaches the user anyway at the next prompt.")

CHAPTER = ("General architecture", [
    ("Architectural principles", S1),
    ("The three privilege domains", S2),
    ("The two programs", S3),
    ("The path of a message", S4),
    ("Sessions and channels", S5),
])
