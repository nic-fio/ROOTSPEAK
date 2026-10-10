# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import arrow, box, c, diamond, fig, key, note, p, table, term, text, tip  # noqa: E402
from _helpers import ref, screen  # noqa: E402

S1 = p("Everything needed to use " + c("rspeak") + " is also inside the command itself: " + c("rspeak --help")
       + " (or " + c("rspeak help") + " or " + c("rspeak -h") + ") opens a full-screen guide, divided into five "
       "tabs.", lead=True) + \
    screen("guide-info", "«FIG» — The built-in help, Info tab (real screenshot, 78-column terminal)") + \
    table(["Tab", "Contains"], [
        ["Info", "name, syntax of all the commands, description of RootSpeak, version and path of this manual"],
        ["Commands", c("rspeak") + " on its own, " + c("send") + ", " + c("list") + ", " + c("status") + ", "
         + c("revoke") + ", " + c("remind") + ", " + c("log") + ", " + c("purge") + ", " + c("version") + ", "
         + c("help")],
        ["Options", "the options of " + c("send") + ": recipients, title, expiry, file"],
        ["Examples", "ready-to-copy commands"],
        ["Files", "where settings, messages, log and manual are"],
    ], "«TAB» — The tabs of the built-in help") + \
    screen("guide-options", "«FIG» — The Options tab") + \
    note("like every " + c("rspeak") + " command, the built-in help also asks for the sudo password. The texts of the "
         "Commands and Options tabs are the same as in " + ref(13) + " of this manual.", "Always with sudo.")

S2 = table(["Keys", "Action"], [
    [key("←") + " " + key("→") + ", " + key("Tab") + " " + key("Shift", "Tab") + ", " + key("h") + " " + key("l"),
     "previous or next tab"],
    [key("Enter"), "next tab"],
    [key("1") + " … " + key("5"), "go straight to a tab"],
    [key("↑") + " " + key("↓") + ", " + key("k") + " " + key("j"), "scroll by one line"],
    [key("PgUp") + " " + key("PgDn") + ", " + key("b") + " " + key("Space"), "scroll by one page"],
    [key("g") + " " + key("G") + ", " + key("Home") + " " + key("End"), "start or end of the tab"],
    [key("q") + ", " + key("Esc"), "leave the built-in help"],
], "«TAB» — The keys of the built-in help") + \
    p("At the bottom right the help shows which lines of the tab are being viewed, for example “lines 1-16/25”. Each tab remembers where you had got to. The help adapts when the window is "
      "resized; on exit the terminal goes back exactly as it was.") + \
    tip("the keys " + key("h") + " " + key("j") + " " + key("k") + " " + key("l") + " are the same as in vi and "
        "less: if you know them, you can use them here too.", "For vi users.")

FORME = fig(
    diamond(180, 130, 250, 96, "Is the output a terminal?", "navy")
    + diamond(520, 130, 250, 96, "At least 44 × 10?", "navy")
    + box(700, 44, 180, 60, "Tabbed guide", "as in the figures above", "green")
    + box(700, 156, 180, 60, "Single page", "with less (or PAGER)", "blue")
    + box(90, 236, 180, 60, "Plain text", "80 columns, no colours", "dark")
    + arrow(305, 130, 393, 130, "#0050C0", False, "yes", 349, 120)
    + arrow(180, 178, 180, 234, "#475569", False, "no, a pipe", 232, 212)
    + arrow(630, 110, 698, 76, "#16a34a", False, "yes", 664, 84)
    + arrow(630, 150, 698, 184, "#475569", False, "no", 664, 180),
    900, 316, "«FIG» — The help picks by itself the form that suits where it is shown", "Three forms of the same guide")

S3 = p("The same guide has three forms, and " + c("rspeak") + " picks the right one by itself.", lead=True) + FORME + \
    table(["Situation", "What " + c("rspeak --help") + " shows"], [
        ["a normal terminal", "the tabbed guide"],
        ["a very small terminal (fewer than 44 columns or 10 lines)", "the same guide as a single page, to "
         "scroll through with the pager: " + c("less") + ", or the program set in " + c("PAGER") + "; " + key("q")
         + " to quit"],
        ["the output goes to a file or to another command", "plain text at 80 columns, without colours; compared "
         "with the tabs it also has the environment variables and the exit status of the commands ("
         + ref(13, 5) + ")"],
    ], "«TAB» — The built-in help in the different situations") + \
    term("admin@server:~$ rspeak --help | grep -A2 -- '--expires DURATION'\n"
         "       --expires DURATION\n"
         "              Expiry, after which the message is no longer shown: 30m, 2h, 3d or\n"
         "              a date and time (\"2026-10-04 12:00\").",
         "Searching the built-in help with grep") + \
    note("" + c("rspeak") + " on its own, too, in a pipe or in a terminal smaller than 80 columns or 20 lines, "
         "shows the built-in help instead of the TUI.", "And rspeak on its own?")

CHAPTER = ("The built-in help", [
    ("Opening the built-in help", S1),
    ("Moving around the built-in help", S2),
    ("Small terminals and plain text", S3),
])
