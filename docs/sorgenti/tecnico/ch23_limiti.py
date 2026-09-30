from build import box, c, fig, note, p, table, text


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


def cella(x, y, ok, testo):
    return box(x, y, 150, 34, testo, "", "green" if ok else "soft", 11.5)


COPERTURA = fig(
    text(180, 58, "text on sending", 12, "#003a90", "700")
    + text(340, 58, "question at login", 12, "#003a90", "700")
    + text(500, 58, "question at prompt", 12, "#003a90", "700")
    + text(660, 58, "dialog", 12, "#003a90", "700")
    + text(820, 58, "tested by", 12, "#003a90", "700")
    + text(20, 94, "bash", 12.5, "#334155", "700", "start")
    + cella(105, 76, True, "yes") + cella(265, 76, True, "yes") + cella(425, 76, True, "yes")
    + cella(585, 76, False, "if there is a desktop") + text(820, 98, "suites", 11.5)
    + text(20, 136, "zsh, fish", 12.5, "#334155", "700", "start")
    + cella(105, 118, True, "yes") + cella(265, 118, True, "yes") + cella(425, 118, True, "yes")
    + cella(585, 118, False, "if there is a desktop") + text(820, 140, "scenarios K", 11.5)
    + text(20, 178, "ksh, dash, sh", 12.5, "#334155", "700", "start")
    + cella(105, 160, True, "yes") + cella(265, 160, True, "yes") + cella(425, 160, False, "no")
    + cella(585, 160, False, "if there is a desktop") + text(820, 182, "scenarios K", 11.5)
    + text(20, 220, "other shells", 12.5, "#334155", "700", "start")
    + cella(105, 202, True, "yes") + cella(265, 202, False, "if they read profile") + cella(425, 202, False, "no")
    + cella(585, 202, False, "if there is a desktop") + text(820, 224, "no", 11.5),
    900, 246, "«FIG» — Where a message gets to, shell by shell", "Shell coverage")

S1 = p("The limits below are known and accepted: they stem from the project's decisions or from what the system "
       "offers. Each one says what happens, so that whoever administers the machine knows what to expect.",
       lead=True) + \
    COPERTURA + table(["Limit", "Consequence"], [
        ["sh, dash, ksh and similar shells have no hook before the prompt", "the question arrives at login (and from "
         "the desktop); during the session only the text arrives, on sending"],
        ["zsh installed after AMS", "you need to run " + c("install.sh") + " again to add the line to the zshrc"],
        ["the heading written on sending uses the language the shell started with", "if the user changes "
         + c("LANG") + " inside the shell (for example in " + c(".bashrc") + "), the heading stays in the login "
         "language; the question and the answers follow the new one"],
        ["languages: Italian and English", "other languages see English; the manuals are in English only"],
        [c("--expires") + " dates in words, in English", "they are interpreted by " + c("date -d") + "; the ISO "
         "format always works"],
        [c("su") + " does not change the owner of the terminal", c("ams send") + " does not write to that terminal "
         "on sending; the question still arrives at the prompt"],
        ["if the desktop agent dies, its dialog stays open", "the agent that replaces it opens a second dialog for "
         "the same message; the first one no longer records anything"],
        ["a single agent per user, even with several graphical sessions", "the lock is one per user; the behaviour "
         "with several desktops open by the same user has not been tested"],
        [c("ams-agent.pronto") + " is written in " + c("$XDG_RUNTIME_DIR") + " (or in " + c("/tmp") + " if it is "
         "missing) and looked for in " + c("/run/user/UID"), "they coincide in logind sessions; otherwise the "
         "wake-up does not find the agent, and this case has not been tested"],
        ["the postponement on the desktop also holds after a new graphical login", "unlike the terminal, where the "
         "question always comes back at login (" + cap(20, 7) + ")"],
        ["without " + c("/dev/tty") + " the question counts as “no”", "a postponement is recorded; in practice the "
         "hook runs " + c("ams-user prompt") + " only with a terminal"],
        ["events written with " + c("syslog") + " when the journal is missing", c("ams log") + " does not read them"],
        ["the TUI search is case-insensitive only for unaccented letters", "“è” does not find “È”"],
        ["backup and restore of the message store, a real power loss", "not tested (" + cap(5, 6) + ", "
         + cap(20, 6) + ")"],
    ], "«TAB» — Known limits")

S2 = table(["Item", "Status"], [
    ["live test of the C version on the user's PC", "to do (only the 0.1.0 prototype was tested live)"],
    ["scheduled sending (" + c("--at") + ")", "planned, second version"],
    ["reusable message templates", "planned, second version"],
    ["CSV or JSON export for audit", "planned, second version"],
    ["deb and rpm packages", "planned, second version"],
    [c("ams remind") + ": manual reminder", "done (" + cap(9, 2) + ")"],
    ["tabbed interface for the administrator", "done: the TUI (" + cap(14) + ")"],
    ["rewrite in a compiled language", "done: version 0.2.0 in C (decision of 30 September)"],
    ["confirmation question in all shells", "done where the shell allows it (" + cap(11, 1) + ")"],
    ["interface in each user's language", "done: Italian and English (" + cap(16) + ")"],
    ["user reply to the administrator", "not planned (decision of 30 September)"],
    [c("block") + " level, disconnections, full-screen lock", "excluded: the user can always postpone"],
], "«TAB» — Open and settled items") + \
    note("decisions already taken are not reopened: the reasons for them are in " + c("docs/decisioni-e-storia.md")
         + ".")

CHAPTER = ("Known limits and open items", [
    ("Known limits", S1),
    ("Open items", S2),
])
