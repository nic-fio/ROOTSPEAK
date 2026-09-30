from build import arrow, box, c, dl, fig, note, p, path, table, text, zone


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


OVERVIEW = fig(
    zone(20, 44, 250, 262, "Administrator · root")
    + box(44, 78, 202, 58, "ams", "C command, via sudo", "navy")
    + box(44, 150, 202, 50, "TUI · help", "ams alone · ams --help", "soft")
    + box(44, 214, 202, 50, "journal", "AMS_* events", "soft")
    + zone(318, 44, 240, 262, "Message store · /var/lib/ams")
    + box(340, 78, 196, 58, "sent/ID/", "reference copy · root", "dark")
    + box(340, 184, 196, 58, "users/U/", "U's mailbox · owned by U", "blue")
    + zone(606, 44, 274, 262, "User · U")
    + box(628, 78, 230, 58, "ams-user prompt", "shell hook", "light")
    + box(628, 184, 230, 58, "ams-user agent", "desktop autostart", "light")
    + text(743, 280, "terminals /dev/pts/N · zenity dialog", 11, "#475569")
    + arrow(248, 104, 338, 104)
    + path([(248, 124), (294, 124), (294, 212), (338, 212)], "#0050C0", False, "as U", 300, 170)
    + arrow(538, 202, 626, 110, "#16a34a", True)
    + arrow(538, 214, 626, 214, "#16a34a", True)
    + text(582, 250, "reads, confirms", 11, "#166534", "600"),
    900, 326, "«FIG» — The three domains of AMS: the root command, the message store, the helper that runs as the user",
    "AMS in one figure")

S1 = p("<b>AMS — Advanced Messaging System</b> is the tool with which the administrators of a Linux machine "
       "send text messages to users and know who has confirmed reading them. It answers a question that the "
       "system's own tools leave open: <b>“who has not read it yet?”</b>", lead=True) + \
    p(c("wall") + " and " + c("write") + " write to the terminals of logged-in users without keeping track of "
      "anything; " + c("notify-send") + " shows a notification that may disappear; the " + c("motd") + " and login "
      "banners are fixed texts. None of them keeps a <b>state per message and per user</b>. AMS puts the pieces "
      "together (logind, the terminals, desktop autostart, zenity, the journal) and adds exactly this state.") + \
    OVERVIEW + \
    p("Version 0.2.0 is written in C (the 0.1.0 prototype was in bash): two programs, no daemon, no database. The "
      + c("ams") + " command always runs as root and writes to the message store; on the user's side the helper "
      + c("ams-user") + " reads the mailbox and records the confirmation, in two ways: in the shell prompt ("
      + c("ams-user prompt") + ") and in the graphical session (" + c("ams-user agent") + ").") + \
    note("this manual describes <b>how</b> AMS works. The <b>contract</b> that every version must honour "
         "(states, invariants, interruptions, message store format) is " + cap(20) + ", “Specification”; the user "
         "manual explains how to use AMS, without technical jargon.")

STATI = fig(
    box(40, 60, 200, 60, "sent", "no copy in the mailbox", "light")
    + box(350, 60, 200, 60, "delivered", "copy in users/U/inbox", "blue")
    + box(660, 60, 200, 60, "confirmed", "statement in acks/ID", "green")
    + arrow(242, 90, 348, 90, "#0050C0", False, "verified copy", 295, 80)
    + arrow(552, 90, 658, 90, "#16a34a", False, "«Ho letto» or «s»", 605, 80)
    + box(250, 160, 400, 46, "message properties: revoked · expired", "", "soft", 12)
    + text(450, 232, "a message is summarised by counting its recipients in the three states", 11.5, "#475569", "600"),
    900, 250, "«FIG» — The three states of a recipient; revocation and expiry are properties of the message",
    "Three states, two properties")

S2 = p("A few concepts are enough to read the rest of the manual. They are the same in the code, in the tests and "
       "in the manuals.", lead=True) + dl([
    ("Message", "a text (at most 65536 bytes) with an optional title and an optional expiry, identified by a "
     "sequential number, the <b>ID</b>. The sender is the administrator who ran " + c("ams") + "."),
    ("Recipient", "a human user of the machine to whom the message is addressed: by name, by group ("
     + c("@gruppo") + "), everyone (" + c("all") + ") or the logged-in users (" + c("online") + ")."),
    ("Reference copy", "the message in " + c("/var/lib/ams/sent/ID/") + ", readable only by root: what was sent, "
     "to whom, when, with which expiry. It is the authoritative source."),
    ("Mailbox", "a user's " + c("/var/lib/ams/users/U/") + " folder: a working copy that the user controls, with "
     "the subfolders " + c("inbox") + ", " + c("read") + ", " + c("acks") + " and " + c("state") + "."),
    ("Channel", "where the user sees the message and confirms it: a terminal (" + c("terminale pts/N") + ", "
     + c("terminale tty3") + ") or the desktop (" + c("desktop") + ")."),
    ("Confirmation", "the user's statement of having read the message, written into their mailbox in "
     + c("acks/ID") + " with date and channel. The first one counts."),
    ("Postponement", "the answer “no” in the terminal or «Più tardi» (“Later”) on the desktop: the question "
     "comes back after " + c("AMS_REMIND_MINUTES") + " minutes, or at the next login."),
    ("State", "for each recipient <b>exactly one of three</b>: sent, delivered, confirmed. Revoked and expired "
     "are properties of the message, not states."),
]) + STATI

MODULI = fig(
    zone(20, 40, 430, 146, "ams (root)")
    + box(40, 74, 124, 44, "ams.c", "commands, recovery", "navy", 12)
    + box(174, 74, 124, 44, "tui.c", "the TUI", "navy", 12)
    + box(308, 74, 124, 44, "guida.c", "ams --help", "navy", 12)
    + box(40, 128, 190, 44, "archivio.c", "mailboxes, terminals", "blue", 12)
    + box(242, 128, 190, 44, "ams.h", "parts used by the TUI", "soft", 12)
    + zone(470, 40, 410, 146, "ams-user (user)")
    + box(490, 74, 370, 44, "ams-user.c", "prompt · agent · confirmation", "light", 12)
    + text(675, 150, "no module of its own besides this one", 11, "#475569")
    + zone(20, 200, 860, 100, "Common parts, linked into both programs")
    + box(40, 236, 124, 44, "comune.c", "files, memory", "dark", 12)
    + box(178, 236, 124, 44, "testo.c", "cleaning, format", "dark", 12)
    + box(316, 236, 124, 44, "lingua.c", ".mo catalogs", "dark", 12)
    + box(454, 236, 124, 44, "evento.c", "journal", "dark", 12)
    + box(592, 236, 124, 44, "utente.c", "come_utente", "dark", 12)
    + box(730, 236, 130, 44, "sessioni.c", "logind", "dark", 12),
    900, 316, "«FIG» — The modules of src/ and the program each one goes into (Makefile)", "The modules")

S3 = p("The code lives in " + c("src/") + " and is organised in small modules with clear-cut responsibilities. "
       "This is the map that the manual explores chapter by chapter.", lead=True) + MODULI + dl([
    (c("ams.c"), "the administrators' command: relaunch through sudo, " + c("send") + ", " + c("list") + ", "
     + c("status") + ", " + c("revoke") + ", " + c("remind") + ", " + c("log") + ", " + c("purge")
     + ", recovery of interrupted sends (" + cap(4) + ", " + cap(8) + ", " + cap(9) + ", " + cap(10) + ")."),
    (c("ams-user.c"), "the helper that runs as the user: the question at the prompt, the desktop agent, the "
     "recording of the confirmation (" + cap(11) + ", " + cap(12) + ", " + cap(13) + ")."),
    (c("archivio.c"), "the operations on the mailboxes, always with the user's identity; writing to the "
     "terminals; waking up the agent (" + cap(7) + ", " + cap(8) + ")."),
    (c("utente.c"), c("come_utente") + ": a child process with a user's identity and a time limit "
     "(" + cap(7) + ")."),
    (c("sessioni.c"), "human users, groups, sessions and terminals, from passwd and from logind (" + cap(6) + ")."),
    (c("testo.c"), "text cleaning, message format, configuration (" + cap(5) + ", " + cap(4) + ")."),
    (c("lingua.c"), "language selection and the reader of the " + c(".mo") + " catalogs (" + cap(16) + ")."),
    (c("evento.c"), "the structured events in the journal and their text in each language (" + cap(18) + ")."),
    (c("tui.c"), "the TUI for administrators (" + cap(14) + ")."),
    (c("guida.c"), "the built-in help of " + c("ams --help") + " (" + cap(15) + ")."),
    (c("comune.c"), "environment, errors, memory, growable strings, safe reading and writing of files "
     "(" + cap(5, 5) + ", " + cap(19) + ")."),
])

S4 = table(["If the question is…", "Where"], [
    ["What must always be true, whatever happens?", cap(20) + " · Specification"],
    ["How is the message store organised, and who can write to it?", cap(5) + " and " + cap(17)],
    ["What happens, step by step, during a send?", cap(8)],
    ["Why does root never write directly into the mailboxes?", cap(7)],
    ["How does the question reach the terminal, and the desktop?", cap(11) + " and " + cap(12)],
    ["What exactly does “confirmed” mean?", cap(13) + " and " + cap(20, 1)],
    ["How is the TUI built, and why does it have no states of its own?", cap(14)],
    ["Where can the history of a message be seen?", cap(18)],
    ["Which errors can AMS report, and what do they mean?", cap(19)],
    ["How is a change tested, and with what results?", cap(3, 5) + " and " + cap(21)],
    ["Which defects have already been found and fixed?", cap(22)],
], "«TAB» — Where to find the answers")

CHAPTER = ("Introduction and concepts", [
    ("What AMS is", S1),
    ("Basic concepts", S2),
    ("Subsystems at a glance", S3),
    ("How to read this manual", S4),
])
