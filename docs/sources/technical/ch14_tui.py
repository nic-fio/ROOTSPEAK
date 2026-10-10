# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

from build import arrow, box, c, fig, key, note, p, path, tui_screen, table, text, ul, warn, zone


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


ARCH = fig(
    zone(20, 44, 300, 250, "The TUI · src/tui.c")
    + box(40, 80, 260, 50, "list", "load_list → summarise", "blue", 12)
    + box(40, 144, 260, 50, "detail", "recipients · history", "blue", 12)
    + box(40, 208, 260, 50, "new message", "form, Ctrl+E, Ctrl+S", "blue", 12)
    + zone(360, 44, 240, 250, "Same functions as rspeak")
    + box(380, 80, 200, 50, "summarise", "like rspeak list", "dark", 12)
    + box(380, 144, 200, 50, "recipients", "like rspeak status", "dark", 12)
    + box(380, 208, 200, 50, "mailboxes_empty", "at every refresh", "soft", 12)
    + zone(640, 44, 240, 250, "In a child process")
    + box(660, 80, 200, 40, "cmd_send", "", "navy", 12)
    + box(660, 128, 200, 40, "cmd_revoke · cmd_remind", "", "navy", 12)
    + box(660, 176, 200, 40, "cmd_purge", "", "navy", 12)
    + box(660, 224, 200, 40, "cmd_log · recipient count", "", "navy", 11)
    + arrow(302, 105, 378, 105) + arrow(302, 169, 378, 169)
    + path([(300, 150), (330, 150), (330, 30), (620, 30), (620, 100), (658, 100)], "#0050C0", True, "actions", 475, 24)
    + text(460, 312, "output and errors collected on a pipe and shown in a window", 11.5, "#475569", "600"),
    900, 330, "«FIG» — The TUI reads with the commands' functions and runs the commands themselves", "No way of its own")

S1 = p(c("rspeak") + " without arguments, with stdin and stdout on a terminal of at least 80 × 20, opens the TUI of "
       + c("src/tui.c") + " after recovery; in a pipe, or on a smaller terminal, it shows the help. The TUI "
       "<b>has no way of its own of doing things</b> and <b>no states of its own</b>: it reads the store with the "
       "functions of " + c("rspeak list") + " and " + c("rspeak status") + ", and every action is the command itself.",
       lead=True) + ARCH + ul([
    "<b>Same functions for reading</b>: the list uses " + c("summarise") + " (the recipients counted in the three "
    "states, revoked and expired), the detail uses " + c("recipients") + " (the same line as " + c("rspeak status") + ").",
    "<b>The actions are the commands</b>: sending, revoking, reminding and purging run in a child process that calls "
    + c("cmd_send") + ", " + c("cmd_revoke") + ", " + c("cmd_remind") + ", " + c("cmd_purge") + " with stdout and "
    "stderr collected on a pipe and shown in a window. An error of the command (" + c("die") + ") ends only the "
    "child; the child's exit status gives the result. The recipients preview and the history (" + c("cmd_log")
    + ") also come from a child.",
    "The decision of the user who wanted the TUI is also a design constraint: while discussing the previews, "
    "invented states had appeared (“pending”, “complete”, “incomplete”, “cancelled”) and were removed; " + c("tests/tui.py") + " checks that none of these words appears "
    "on the screen.",
])

S2 = p("The list shows the messages from the most recent, one per row, with the recipients summary: a three-colour "
       "bar and a phrase. It refreshes by itself every 3 seconds.", lead=True) + \
    tui_screen("list", "«FIG» — The message list (real screenshot, captured by tools/tui-screenshots.sh)") + \
    table(["Column", "Content"], [
        ["ID, DATE", "number and date of sending; " + c(">") + " marks the selected row, drawn in reverse video"],
        ["MESSAGE", c("[revoked]") + " and " + c("[expired]") + " in grey, the title in bold, the first line of the "
         "text, cut to the available width"],
        ["RECIPIENTS", "the 12-cell bar and the summary phrase (" + cap(10, 3) + "); below 106 inner "
         "columns, instead of the phrase, “confirmed/total” (for example " + c("4/8") + ")"],
        ["legend", "always at the bottom: " + c("█") + " confirmed, " + c("▒") + " delivered, " + c("░") + " sent; "
         "with an active search, the searched text"],
    ], "«TAB» — The columns of the list") + table(["Key", "Effect"], [
    [key("↑") + " " + key("↓") + " " + key("PgUp") + " " + key("PgDn") + " " + key("Home") + " " + key("End"),
     "scrolls the list"],
    [key("Enter"), "opens the detail of the selected message"],
    [key("n"), "writes and sends a new message"],
    [key("r"), "revokes the selected message, if it is not already revoked (with confirmation)"],
    [key("m"), "reminds whoever has not confirmed: only if the message is neither revoked nor expired and has at "
     "least one delivered recipient (with confirmation)"],
    [key("p"), "deletes the messages older than a duration (with confirmation; suggested " + c("90d") + ")"],
    [key("/"), "searches by text or title, case-insensitively; " + key("Esc") + " clears the "
     "search"],
    [key("?"), "the key guide"],
    [key("q"), "quits and gives the terminal back as it was"],
], "«TAB» — The keys of the list")

S3 = p("The detail of a message has two tabs: the recipients, with the status line of " + c("rspeak status")
       + " coloured according to the state, and the history, that is the output of " + c("rspeak log") + ". It is "
       "re-read every 3 seconds and after every action; " + key("Esc") + " leaves it.", lead=True) + \
    tui_screen("detail", "«FIG» — The detail: one recipient per row, in the three states (real screenshot)") + \
    tui_screen("history", "«FIG» — The History tab: the log events, rewritten from the RSPEAK_* fields "
                        "(real screenshot)") + ul([
    "The header shows title, date, sender, expiry (“expires on …” or “expired on …”) and revocation (“revoked "
    "on …”, in red); then at most six lines of the text, indented.",
    "The tab row repeats bar and phrase: the summary stays visible while scrolling through the list.",
    "Colours of the STATE column: green confirmed, yellow delivered, red sent. They are the three states, "
    "and only those.",
    "Keys: " + key("Tab") + " switches tab, " + key("↑") + " " + key("↓") + " scroll, " + key("m") + " and "
    + key("r") + " remind and revoke with the same rules as the list.",
])

S4 = p("The new-message form has four fields: recipients, title, expiry and text. When the recipients field is "
       "left, a child performs the same resolution as " + c("rspeak send") + " and shows the number of recipients, "
       "or the error in red.", lead=True) + \
    tui_screen("new", "«FIG» — The new-message form, with the recipients preview (real screenshot)") + \
    tui_screen("send", "«FIG» — The confirmation before sending (real screenshot)") + table(["Key", "Effect"], [
    [key("Tab") + ", " + key("Shift", "Tab"), "next or previous field"],
    [key("Ctrl", "E"), "opens the text in the administrator's editor"],
    [key("Ctrl", "S"), "asks for confirmation and sends: " + c("cmd_send") + " in a child, with the text on stdin"],
    [key("Esc"), "discards the message, with confirmation if something has been written"],
], "«TAB» — The keys of the form") + ul([
    "One-line fields accept at most 1000 bytes; the text shows the count “97 of 65536 bytes”. "
    "The real checks are those of " + c("rspeak send") + ": an error arrives in the result window, “Sending result”.",
    "<b>Editor</b>: " + key("Ctrl", "E") + " writes the text to a temporary file in " + c("/tmp") + " ("
    + c("mkstemp") + "), hands it over to the administrator in " + c("SUDO_USER") + " and opens " + c("VISUAL") + ", "
    + c("EDITOR") + ", " + c("nano") + " or " + c("vi") + " <b>with their identity</b>, not as root; then it re-reads "
    "the file (at most twice the maximum length, without following links) and deletes it.",
    "After sending, the list reloads and the new message appears at the top (" + c("tests/tui.py") + ").",
]) + note("a defect found while writing " + c("tests/tui.py") + ": the child that performs the send also inherited "
          "the end of the pipe through which the parent writes the text, and never saw the end of the text. Now it "
          "closes it before calling " + c("cmd_send") + ".")

S5 = p("Revoking, reminding and purging always ask for a confirmation that describes the action with the real "
       "numbers; the result of the command then appears in a window.", lead=True) + \
    tui_screen("reminder", "«FIG» — The confirmation of a reminder, over the list (real screenshot)") + table(
    ["Action", "The confirmation says", "Then"], [
        ["revoke", "“Revoke message N?”, title and summary; “Whoever has not seen it yet will not see it; open "
         "dialogs and questions close by themselves.”", c("cmd_revoke") + " in a child"],
        ["remind", "how many recipients have not confirmed yet; “They are asked again now: at the next prompt and "
         "with the dialog on the desktop.”", c("cmd_remind") + " in a child"],
        ["purge", "first the duration (“Delete the messages sent more than (for example 90d, 12h):”), then “Messages "
         "older than D, with copies and confirmations. The events stay in the system log.”",
         c("cmd_purge") + " in a child"],
        ["send", "recipients with their number, title, expiry, bytes of the text", c("cmd_send") + " in a child"],
    ], "«TAB» — The actions with confirmation") + \
    p("Windows and confirmations are drawn on a copy of the base screen: a later window does not stay "
      "on top of the previous one. " + key("y") + " confirms, " + key("n") + " or " + key("Esc") + " cancels.")

S6 = table(["Part", "How it works"], [
    ["terminal", c("/dev/tty") + " without echo or canonical mode; without " + c("IXON") + " (so that " + key("Ctrl", "S")
     + " reaches the TUI) and without " + c("ICRNL") + "; alternate screen and hidden cursor. On exit, and on "
     + c("SIGINT") + ", " + c("SIGTERM") + ", " + c("SIGHUP") + ", everything goes back to how it was"],
    ["drawing", "without ncurses: every screen is composed in memory and written with a single write; lengths "
     "are counted in visible characters (UTF-8, without the colour sequences)"],
    ["keys", "one byte at a time with a " + c("poll") + " of 500 ms; after " + c("ESC") + " the rest of the sequence "
     "with a 40 ms wait: " + key("Esc") + " on its own, arrows, " + key("PgUp") + ", " + key("PgDn") + ", "
     + key("Home") + ", " + key("End") + ", " + key("Del") + " and " + key("Shift", "Tab") + " are recognised"],
    ["refresh", "every 6 empty waits (3 seconds) the list or the detail is re-read, forgetting the "
     "mailboxes already read (" + c("mailboxes_empty") + "); at the top right “updated at …”"],
    ["size", "at every wait the size is compared (" + c("TIOCGWINSZ") + ") and the screen redrawn; below "
     "80 × 20 the TUI exits"],
    ["colours", "turned off with " + c("NO_COLOR") + " (if sudo preserves it)"],
], "«TAB» — Terminal, keys and refresh") + \
    warn("the TUI runs as root. Everything it shows that comes from the users (confirmations, history) goes through "
         + c("clean_text") + " as in the commands; the only external program the TUI starts on its own, the editor, "
         "runs with the administrator's identity.")

CHAPTER = ("The TUI for administrators", [
    ("Architecture: same data, same commands", S1),
    ("The list", S2),
    ("The detail and the history", S3),
    ("Writing and sending", S4),
    ("The actions with confirmation", S5),
    ("Terminal, keys and refresh", S6),
])
