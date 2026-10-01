from build import arrow, box, c, code, dialog, fig, notification, note, p, path, seq, table, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


LOOP = fig(
    box(20, 110, 160, 58, "flock LOCK_NB", "one agent per user", "dark")
    + box(215, 110, 150, 58, "rootspeak-agent.ready", "the PID, for wake-ups", "dark", 12)
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
    "<b>Ready</b>: after taking the lock the agent writes its PID to " + c("$XDG_RUNTIME_DIR/rootspeak-agent.ready")
    + " and deletes it on exit (" + c("atexit") + "). " + c("rspeak send") + " wakes only that PID (" + cap(8, 5)
    + ").",
    "<b>Lives as long as the session</b>: the loop goes on as long as " + c("graphical_session(getuid())") + " finds an "
    "X11 or Wayland session of the user, or until a termination signal arrives.",
    "<b>Configuration always current</b>: " + c("conf_read") + " at every round; a change to "
    + c("RSPEAK_REMIND_MINUTES") + " or " + c("RSPEAK_AGENT_POLL") + " applies from the next round.",
    "<b>One dialog at a time</b>: the messages not postponed on the desktop channel (" + c("state/ID.gui")
    + "), oldest first (scenario I7).",
])

SEGNALI = fig(
    box(20, 50, 200, 60, "always blocked", "USR1 TERM HUP INT CHLD", "dark")
    + box(260, 50, 200, 60, "ppoll(…, &waiting)", "unblocked only here", "navy")
    + box(500, 30, 180, 44, "SIGUSR1", "wake = 1", "blue", 12)
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
        [c("SIGUSR1"), c("on_wake") + ": " + c("wake = 1"), "the wait ends and the round starts again at once; it "
         "is installed as the <b>first statement</b> of " + c("main") + ", because by default " + c("SIGUSR1")
         + " terminates the process (in the prototype, 20 out of 20 agents woken while starting up died)"],
        [c("SIGTERM") + ", " + c("SIGHUP") + ", " + c("SIGINT"), c("on_end") + ": " + c("fine = 1"),
         "the agent finishes recording an answer already given and exits at the first safe point"],
        [c("SIGCHLD"), c("on_child") + ": nothing", "interrupts the wait: the dialog's answer is recorded within "
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

FIN = seq([("show_dialog", "agent", "navy"), ("zenity", "--question --no-markup", "blue"),
           ("User", "", "dark"), ("Mailbox", "users/U", "soft")], [
    (0, 1, "fork, exec (signals restored)"),
    (1, 2, "“I have read it” / “Later”"),
    ("note", 0, "every second: waitpid"),
    (0, 3, "acks/ID? inbox/ID? expired?"),
    ("sep", "three ways to end".ljust(18)),
    (2, 1, "“I have read it”: exit 0"),
    (1, 0, "SIGCHLD → desktop confirmation", True),
    (2, 1, "“Later”, closed: exit 1"),
    (0, 3, "postponement: state/ID.gui"),
    ("note", 0, "elsewhere/revoked: SIGTERM".ljust(27)),
], "«FIG» — The confirmation dialog",
   "A dialog, from opening to answer")

S3 = p(c("show_dialog") + " starts " + c("zenity --question --no-markup --width=460") + " with title, text and "
       "buttons in English, whatever the language of the session, and waits for it to finish, checking the mailbox every second as well.",
       lead=True) + dialog("RootSpeak · Message from the administrator", "Maintenance · 01/10 10:49",
                           "On Saturday from 8 am to 12 noon the server will be off for disk maintenance.",
                           "«FIG» — The dialog as zenity draws it on GNOME (reconstruction), with the buttons “Later” "
                           "and “I have read it”") + FIN + table(
    ["How it ends", "Effect"], [
        ["exit 0 (“I have read it”)", c("confirm(ID, \"desktop\")") + "; if writing fails "
         "and the message is still in the mailbox, a notification says so and the dialog comes back at the next "
         "round"],
        ["exit 1 (“Later”, or dialog closed by the user)", c("postpone(ID, \"gui\")")
         + ": touches " + c("state/ID.gui") + ", event " + c("POSTPONED") + "; only if the display is still "
         "there: zenity also exits with 1 when it loses the display (session ended, display manager restarted)"],
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
    "milliseconds, so an " + c("rspeak remind") + " arriving right after a “Later” finds the postponement already "
    "written and removes it (scenario I11; with a check once a second, the VM had found the reminder lost).",
    "The wake-up signal does not close the dialog: the agent keeps waiting for it. In the bash prototype the "
    "signal interrupted " + c("wait") + " and the agent took the dialog as closed, recording a postponement never "
    "chosen (test VM, scenario I7).",
    "When the session ends the agent waits for the dialog at most 2 seconds, then closes it: a confirmation already "
    "given is not lost (scenario I10: logout as soon as zenity has exited with the answer, confirmation recorded).",
    "After an exit 1 the agent tells “Later” from a lost display: the session must still be there for logind (not "
    + c("closing") + ") and the display socket (" + c("$WAYLAND_DISPLAY") + " or " + c("/tmp/.X11-unix/X") + "N) must "
    "accept a connection. Otherwise nothing is recorded and the dialog comes back at the "
    "next login (scenario I13). Until 1 October 2026 the end of the session was recorded as a postponement, and "
    "the dialog came back only after " + c("RSPEAK_REMIND_MINUTES") + ": the tests on Ubuntu, Fedora with KDE "
    "Plasma and Cinnamon found it.",
    "Timings of the last run recorded in the VM: dialog after sending 0.58 s (I1), closing after a "
    "confirmation from the terminal 0.65 s (I5), after a revocation 0.67 s (I6), at graphical login 2.64 s after "
    "the login manager restart (I9).",
])

S4 = p("The agent uses " + c("notify-send") + ", if it is installed, for one case only: telling the user that their "
       "confirmation has <b>not</b> been recorded (disk full, permissions). The text is fixed: no message content "
       "goes through notifications, which may disappear by themselves or be ignored.", lead=True) + \
    notification("RootSpeak · Confirmation not recorded",
                 "The confirmation could not be recorded: the message will be shown again.",
                 "«FIG» — The only notification of RootSpeak (reconstruction)") + \
    note("for the confirmation RootSpeak uses a dialog and not a notification: a GNOME notification may disappear by "
         "itself or be ignored, whereas the zenity dialog stays open until the user chooses.")

CHAPTER = ("Receiving on the desktop", [
    ("The agent's loop", S1),
    ("Signals and waits without losses", S2),
    ("The confirmation dialog", S3),
    ("The error notification", S4),
])
