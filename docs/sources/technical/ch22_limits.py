# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

from build import box, c, fig, note, p, table, text


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


def cell(x, y, ok, label):
    return box(x, y, 146, 34, label, "", "green" if ok else "soft", 11.5)


COVERAGE = fig(
    text(191, 58, "text on sending", 12, "#003a90", "700")
    + text(347, 58, "question at login", 12, "#003a90", "700")
    + text(503, 58, "question at prompt", 12, "#003a90", "700")
    + text(659, 58, "dialog", 12, "#003a90", "700")
    + text(820, 58, "tested by", 12, "#003a90", "700")
    + text(20, 98, "bash", 12.5, "#334155", "700", "start")
    + cell(118, 76, True, "yes") + cell(274, 76, True, "yes") + cell(430, 76, True, "yes")
    + cell(586, 76, False, "if there is a desktop") + text(820, 98, "suites", 11.5)
    + text(20, 140, "zsh, fish", 12.5, "#334155", "700", "start")
    + cell(118, 118, True, "yes") + cell(274, 118, True, "yes") + cell(430, 118, True, "yes")
    + cell(586, 118, False, "if there is a desktop") + text(820, 140, "scenarios K", 11.5)
    + text(20, 182, "ksh, dash, sh", 12.5, "#334155", "700", "start")
    + cell(118, 160, True, "yes") + cell(274, 160, True, "yes") + cell(430, 160, False, "no")
    + cell(586, 160, False, "if there is a desktop") + text(820, 182, "scenarios K", 11.5)
    + text(20, 224, "other shells", 12.5, "#334155", "700", "start")
    + cell(118, 202, True, "yes") + cell(274, 202, False, "if they read profile") + cell(430, 202, False, "no")
    + cell(586, 202, False, "if there is a desktop") + text(820, 224, "no", 11.5),
    900, 246, "«FIG» — Where a message gets to, shell by shell", "Shell coverage")

S1 = p("The limits below are known and accepted: they stem from the project's decisions or from what the system "
       "offers. Each one says what happens, so that whoever administers the machine knows what to expect.",
       lead=True) + \
    COVERAGE + table(["Limit", "Consequence"], [
        ["sh, dash, ksh and similar shells have no hook before the prompt", "the question arrives at login (and from "
         "the desktop); during the session only the text arrives, on sending"],
        ["zsh installed after RootSpeak", "you need to run " + c("install.sh") + " again to add the line to the zshrc"],
        [c("--expires") + " dates in words, in English", "they are interpreted by " + c("date -d") + "; the ISO "
         "format always works"],
        [c("su") + " does not change the owner of the terminal", c("rspeak send") + " does not write to that terminal "
         "on sending; the question still arrives at the prompt"],
        ["if the desktop agent dies, its dialog stays open", "the agent that replaces it opens a second dialog for "
         "the same message; the first one no longer records anything"],
        ["a single agent per user, even with several graphical sessions", "the lock is one per user; the behaviour "
         "with several desktops open by the same user has not been tested"],
        [c("rootspeak-agent.ready") + " is written in " + c("$XDG_RUNTIME_DIR") + " (or in " + c("/tmp") + " if it is "
         "missing) and looked for in " + c("/run/user/UID"), "they coincide in logind sessions; otherwise the "
         "wake-up does not find the agent, and this case has not been tested"],
        ["the postponement on the desktop also holds after a new graphical login", "unlike the terminal, where the "
         "question always comes back at login (" + cap(19, 7) + ")"],
        ["without " + c("/dev/tty") + " the question counts as “no”", "a postponement is recorded; in practice the "
         "hook runs " + c("rootspeak-user prompt") + " only with a terminal"],
        ["events written with " + c("syslog") + " when the journal is missing", c("rspeak log") + " does not read them"],
        ["the TUI search is case-insensitive only for unaccented letters", "“ä” does not find “Ä”"],
        ["backup and restore of the message store, a real power loss", "not tested (" + cap(5, 6) + ", "
         + cap(19, 6) + ")"],
    ], "«TAB» — Known limits")

S2 = table(["Item", "Status"], [
    ["live test of the C version on the user's PC", "done on 1 October 2026: sending (also from an ssh session), the "
     "dialog, postponement, reminder, the question in a desktop terminal, revocation, the TUI over ssh; still to "
     "do: expiry, the question in a terminal opened over ssh"],
    ["scheduled sending (" + c("--at") + ")", "planned, second version"],
    ["reusable message templates", "planned, second version"],
    ["CSV or JSON export for audit", "planned, second version"],
    ["deb and rpm packages", "planned for version 1.0"],
    ["tests on other distributions and desktops", "done: 22 distributions and 5 desktops (" + cap(20, 4) + ", "
     + cap(20, 3) + ")"],
    [c("rspeak remind") + ": manual reminder", "done (" + cap(9, 2) + ")"],
    ["tabbed interface for the administrator", "done: the TUI (" + cap(14) + ")"],
    ["rewrite in a compiled language", "done: version 0.2.0 in C (decision of 30 September)"],
    ["confirmation question in all shells", "done where the shell allows it (" + cap(11, 1) + ")"],
    ["interface in each user's language", "done in 0.2.0, then removed: RootSpeak is for administrators and speaks "
     "English only (decision of 1 October)"],
    ["user reply to the administrator", "not planned (decision of 30 September)"],
    [c("block") + " level, disconnections, full-screen lock", "excluded: the user can always postpone"],
], "«TAB» — Open and settled items") + \
    note("decisions already taken are not reopened: the reasons for them are in " + c("docs/decisions-and-history.md")
         + ".")

CHAPTER = ("Known limits and open items", [
    ("Known limits", S1),
    ("Open items", S2),
])
