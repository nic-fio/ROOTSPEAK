from build import arrow, box, c, code, dialog, fig, notification, note, p, path, seq, table, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


LOOP = fig(
    box(20, 110, 160, 58, "flock LOCK_NB", "one agent per user", "dark")
    + box(215, 110, 150, 58, "rootspeak-agent.pronto", "the PID, for wake-ups", "dark", 12)
    + box(400, 110, 170, 58, "graphical session?", "sd-login, every round", "navy", 12)
    + box(605, 110, 150, 58, "for each message", "not postponed", "blue", 12)
    + box(790, 110, 90, 58, "wait", "ppoll 1 s", "soft", 12)
    + arrow(182, 139, 213, 139) + arrow(367, 139, 398, 139) + arrow(572, 139, 603, 139) + arrow(757, 139, 788, 139)
    + path([(835, 108), (835, 30), (485, 30), (485, 108)], "#475569", True,
           "end of wait: RSPEAK_AGENT_POLL seconds or SIGUSR1", 660, 22)
    + path([(485, 170), (485, 200)], "#b91c1c") + text(485, 216, "no: the agent exits", 11, "#b91c1c", "600")
    + text(100, 196, "lock taken:", 11, "#475569") + text(100, 212, "exits at once", 11, "#475569"),
    900, 236, "«FIG» — The desktop agent's loop", "The agent's loop")

S1 = p("The agent, " + c("rootspeak-user agent") + ", starts with the desktop's autostart ("
       + c("/etc/xdg/autostart/rootspeak-agent.desktop") + ") or from " + c("systemd-run") + " when " + c("rspeak send")
       + " does not find one, and lives as long as the graphical session.", lead=True) + LOOP + ul([
    "<b>Only one agent per user</b>: " + c("flock(LOCK_EX | LOCK_NB)") + " on " + c("$XDG_RUNTIME_DIR/rootspeak-agent.lock")
    + "; if the lock is taken the agent exits at once, without an error. The descriptor is opened with " + c("O_CLOEXEC")
    + " and is not passed on to zenity: otherwise, if the agent died, one of its orphaned dialogs would hold the lock and "
    "the agent started in its place would exit at once (a defect found by the test VM).",
    "<b>Ready</b>: after taking the lock the agent writes its PID to " + c("$XDG_RUNTIME_DIR/rootspeak-agent.pronto")
    + " and deletes it on exit (" + c("atexit") + "). " + c("rspeak send") + " wakes only that PID (" + cap(8, 5)
    + ").",
    "<b>Lives as long as the session</b>: the loop goes on as long as " + c("sessione_grafica(getuid())") + " finds an "
    "X11 or Wayland session of the user, or until a termination signal arrives.",
    "<b>Configuration always current</b>: " + c("conf_leggi") + " at every round; a change to "
    + c("RSPEAK_REMIND_MINUTES") + " or " + c("RSPEAK_AGENT_POLL") + " applies from the next round.",
    "<b>One dialog at a time</b>: the messages not postponed on the desktop channel (" + c("state/ID.gui")
    + "), oldest first (scenario I7).",
])

SEGNALI = fig(
    box(20, 50, 200, 60, "always blocked", "USR1 TERM HUP INT CHLD", "dark")
    + box(260, 50, 200, 60, "ppoll(…, &attesa)", "unblocked only here", "navy")
    + box(500, 30, 180, 44, "SIGUSR1", "sveglia = 1", "blue", 12)
    + box(500, 84, 180, 44, "SIGTERM, HUP, INT", "fine = 1", "amber", 12)
    + box(500, 138, 180, 44, "SIGCHLD", "zenity has closed", "green", 12)
    + box(720, 30, 160, 44, "new round now", "new message", "light", 12)
    + box(720, 84, 160, 44, "exits", "at the first safe point", "light", 12)
    + box(720, 138, 160, 44, "records", "the answer, at once", "light", 12)
    + arrow(222, 80, 258, 80) + arrow(462, 70, 498, 52) + arrow(462, 80, 498, 106) + arrow(462, 90, 498, 160)
    + arrow(682, 52, 718, 52) + arrow(682, 106, 718, 106) + arrow(682, 160, 718, 160)
    + text(240, 200, "a signal that arrives outside the wait stays pending: it is not lost", 11.5, "#166534", "600"),
    900, 220, "«FIG» — The agent's signals: blocked except during the waits", "No signal lost")

S2 = p("The agent must react to three things: a new message (" + c("SIGUSR1") + " from " + c("rspeak send") + "), the "
       "end of the session (" + c("SIGTERM") + " from logind) and the closing of the dialog (" + c("SIGCHLD")
       + "). It handles them without losing signals and without interrupting a confirmation halfway.", lead=True) + SEGNALI + \
    table(["Signal", "Handler", "Effect"], [
        [c("SIGUSR1"), c("su_sveglia") + ": " + c("sveglia = 1"), "the wait ends and the round starts again at once; it "
         "is installed as the <b>first statement</b> of " + c("main") + ", because by default " + c("SIGUSR1")
         + " terminates the process (in the prototype, 20 out of 20 agents woken while starting up died)"],
        [c("SIGTERM") + ", " + c("SIGHUP") + ", " + c("SIGINT"), c("su_fine") + ": " + c("fine = 1"),
         "the agent finishes recording an answer already given and exits at the first safe point"],
        [c("SIGCHLD"), c("su_figlio") + ": nothing", "interrupts the wait: the dialog's answer is recorded within "
         "a few milliseconds"],
    ], "«TAB» — The agent's signals") + ul([
    "The five signals stay blocked with " + c("sigprocmask") + " all the time, except during the waits, "
    "done with " + c("ppoll") + ", which unblocks and re-blocks them atomically: a signal that arrives while the agent "
    "is working stays pending and interrupts the next wait.",
    "Each wait lasts at most one second; the one between two rounds lasts "
    + c("RSPEAK_AGENT_POLL") + " seconds (60) in total, and ends earlier if a wake-up or termination arrives. The "
    "periodic check stays as a safety net: a lost signal delays the dialog, it does not lose it.",
    "The wake-up clears its flag at the <b>start</b> of the round: a wake-up that arrives while a dialog is open "
    "makes the next round start at once.",
])

FIN = seq([("mostra_finestra", "agent", "navy"), ("zenity", "--question --no-markup", "blue"),
           ("Mailbox", "users/U", "soft"), ("User", "", "dark")], [
    (0, 1, "fork, exec (signals restored)"),
    (1, 3, "«Ho letto» / «Più tardi»"),
    ("nota", 0, "every second: waitpid"),
    (0, 2, "acks/ID? inbox/ID? expired?"),
    ("sep", "three ways to end".ljust(18)),
    (3, 1, "«Ho letto»: exit 0"),
    (1, 0, "SIGCHLD → desktop confirmation", True),
    (3, 1, "«Più tardi», closed: exit 1"),
    (0, 2, "postponement: state/ID.gui"),
    ("nota", 0, "elsewhere/revoked: SIGTERM".ljust(27)),
], "«FIG» — The confirmation dialog; the buttons «Ho letto» and «Più tardi» are “I have read it” and “Later”",
   "A dialog, from opening to answer")

S3 = p(c("mostra_finestra") + " starts " + c("zenity --question --no-markup --width=460") + " with title, text and "
       "buttons in the session's language, and waits for it to finish, checking the mailbox every second as well.",
       lead=True) + dialog("RootSpeak · Messaggio dall'amministratore", "Manutenzione · 30/09 16:55",
                           "Sabato dalle 8 alle 12 il server sarà spento.",
                           "«FIG» — The dialog as zenity draws it on GNOME (reconstruction): «RootSpeak · Messaggio "
                           "dall'amministratore» (“RootSpeak · Message from the administrator”), «Manutenzione» "
                           "(“Maintenance”), «Sabato dalle 8 alle 12 il server sarà spento.» (“On Saturday from 8 to 12 "
                           "the server will be switched off.”), buttons «Più tardi» (“Later”) and «Ho letto» (“I have "
                           "read it”)") + FIN + table(
    ["How it ends", "Effect"], [
        ["exit 0 («Ho letto», “I have read it” in English)", c("conferma(ID, \"desktop\")") + "; if writing fails "
         "and the message is still in the mailbox, a notification says so and the dialog comes back at the next "
         "round"],
        ["exit 1 («Più tardi», “Later” in English, or dialog closed by the user)", c("rimanda(ID, \"gui\")")
         + ": touches " + c("state/ID.gui") + ", event " + c("RINVIATO")],
        ["closed by the agent: confirmation elsewhere, revocation or expiry", "nothing: if it has expired, the "
         "message moves to " + c("read/")],
        ["other results (dialog killed, for example when the session ends)", "nothing: it is not the user's "
         "choice; the dialog comes back at the next round or at the next login"],
    ], "«TAB» — How a dialog ends") + ul([
    c("--no-markup") + ": the message text is not interpreted as zenity markup. The text has already been "
    "cleaned at send time (" + cap(8, 7) + ").",
    "The child that becomes zenity restores the signal mask and handlers before " + c("exec") + ": zenity does not "
    "inherit the agent's blocked signals.",
    "The end of zenity interrupts the wait at once (" + c("SIGCHLD") + "): the answer is recorded within a few "
    "milliseconds, so an " + c("rspeak remind") + " arriving right after a «Più tardi» (“Later”) finds the postponement already "
    "written and removes it (scenario I11; with a check once a second, the VM had found the reminder lost).",
    "The wake-up signal does not close the dialog: the agent keeps waiting for it. In the bash prototype the "
    "signal interrupted " + c("wait") + " and the agent took the dialog as closed, recording a postponement never "
    "chosen (test VM, scenario I7).",
    "When the session ends the agent waits for the dialog at most 2 seconds, then closes it: a confirmation already "
    "given is not lost (scenario I10: «Ho letto» (“I have read it”) and logout after 0.1 s, confirmation recorded).",
    "Timings of the last run recorded in the VM: dialog after sending 0.58 s (I1), closing after a "
    "confirmation from the terminal 0.65 s (I5), after a revocation 0.67 s (I6), at graphical login 2.64 s after "
    "the login manager restart (I9).",
])

S4 = p("The agent uses " + c("notify-send") + ", if it is installed, for one case only: telling the user that their "
       "confirmation has <b>not</b> been recorded (disk full, permissions). The text is fixed: no message content "
       "goes through notifications, which may disappear by themselves or be ignored.", lead=True) + \
    notification("RootSpeak · Conferma non registrata",
                 "Non è stato possibile registrare la conferma: il messaggio verrà riproposto.",
                 "«FIG» — The only notification of RootSpeak (reconstruction): «RootSpeak · Conferma non registrata» (“RootSpeak · "
                 "Confirmation not recorded”), «Non è stato possibile registrare la conferma: il messaggio verrà "
                 "riproposto.» (“The confirmation could not be recorded: the message will be shown again.”)") + \
    note("for the confirmation RootSpeak uses a dialog and not a notification: a GNOME notification may disappear by "
         "itself or be ignored, whereas the zenity dialog stays open until the user chooses.")

CHAPTER = ("Receiving on the desktop", [
    ("The agent's loop", S1),
    ("Signals and waits without losses", S2),
    ("The confirmation dialog", S3),
    ("The error notification", S4),
])
