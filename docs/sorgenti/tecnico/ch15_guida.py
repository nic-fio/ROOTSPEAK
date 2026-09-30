from build import arrow, box, c, code, diamond, fig, key, note, p, path, table, term, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


SOURCES = fig(
    box(20, 120, 190, 64, "src/guida.c", "entries «label¦text»", "navy")
    + box(290, 30, 190, 54, "tabbed help", "guida_a_schede", "blue")
    + box(290, 110, 190, 54, "page with pager", "pagina(), in colour", "blue")
    + box(290, 190, 190, 54, "plain text", "pagina(), 80 columns", "blue")
    + box(570, 20, 150, 54, "po/ams.pot", "English source texts", "soft")
    + box(570, 110, 150, 54, "build.py", "help_reference", "dark")
    + box(760, 110, 120, 54, "User", "Manual", "light")
    + box(570, 200, 310, 54, "tools/check-docs.py", "generated manual = src/guida.c", "green")
    + arrow(212, 140, 288, 60) + arrow(212, 152, 288, 137) + arrow(212, 164, 288, 214)
    + path([(200, 118), (200, 10), (560, 10), (560, 40), (568, 40)], "#0050C0", False, "make pot (xgettext)", 380, 22)
    + arrow(645, 76, 645, 108)
    + arrow(722, 137, 758, 137)
    + arrow(645, 166, 645, 198, "#16a34a", True),
    900, 272, "«FIG» — A single source for the help, the page, the text and the manual's reference", "Where the texts come from")

S1 = p("The built-in help of " + c("ams --help") + " is modelled on that of MTERM: no system manual pages, but a "
       "tabbed help in the terminal. Its texts live in " + c("src/guida.c") + ", in "
       "English, as " + c("\"label¦description\"") + " entries with one context per group; the translations live "
       "in the " + c("po/") + " catalogs, like all the other texts (" + cap(16) + ").", lead=True) + SOURCES + \
    table(["Context", "Content", "In the user manual"], [
        [c("guida-comandi"), "the commands: " + c("send") + ", " + c("list") + ", " + c("status") + ", " + c("revoke")
         + ", " + c("remind") + ", " + c("log") + ", " + c("purge") + ", " + c("version") + ", " + c("help")
         + " and " + c("ams") + " on its own", "reference, with " + c("data-help")],
        [c("guida-opzioni"), c("--to") + ", " + c("--title") + ", " + c("--expires") + ", " + c("--file"),
         "reference, with " + c("data-help")],
        [c("guida-esempi"), "example commands with their explanation", "—"],
        [c("guida-file"), "configuration, message store, log, manual", "—"],
        [c("guida-sintassi"), "the synopsis lines", "—"],
    ], "«TAB» — The groups of help texts") + \
    p("The manual generator reads the English source entries from " + c("po/ams.pot") + " (extracted from "
      "src/guida.c by make pot), in code order, and builds from them the user manual's reference, with the "
      + c("data-help") + " attribute on every entry; " + c("tools/check-docs.py") + " extracts the texts from "
      "src/guida.c again at check time and verifies that commands and options match, word for word (" + cap(21, 5)
      + ").")

LEVELS = fig(
    diamond(170, 90, 240, 80, "stdin and stdout tty?", "navy")
    + diamond(470, 90, 230, 80, "at least 44 × 10?", "navy")
    + box(640, 62, 240, 56, "tabbed help", "guida_a_schede", "blue")
    + box(50, 190, 240, 56, "plain text, 80 columns", "no colours", "dark", 12)
    + box(355, 190, 240, 56, "manual-style page", "$PAGER or less -R -F -X", "light", 12)
    + arrow(292, 90, 353, 90, "#0050C0", False, "yes", 322, 80)
    + arrow(587, 90, 638, 90, "#0050C0", False, "yes", 612, 80)
    + arrow(170, 132, 170, 188, "#475569", False, "no", 186, 164)
    + arrow(470, 132, 470, 188, "#475569", False, "no", 486, 164)
    + text(760, 150, "shrunk below 44 × 10:", 11, "#475569")
    + text(760, 166, "the help exits", 11, "#475569"),
    900, 266, "«FIG» — Which form ams --help takes", "Three forms")

S2 = p(c("ams_guida") + " chooses the form according to where the output goes. All three have the same content.",
       lead=True) + LEVELS + table(["Form", "When", "How"], [
    ["tabbed help", "stdin and stdout on a terminal of at least 44 × 10", "five tabs: Info, Commands, Options, "
     "Examples, Files"],
    ["manual-style page", "smaller terminal", "the page (NAME, SYNOPSIS, DESCRIPTION, COMMANDS, SEND OPTIONS, "
     "EXAMPLES, FILES, ENVIRONMENT, EXIT STATUS, SEE ALSO) as wide as the terminal, between 60 and 100 "
     "columns, through " + c("$PAGER") + " or " + c("less -R -F -X") + " if it is in the " + c("PATH") + "; otherwise "
     "directly"],
    ["plain text", "stdin or stdout is not a terminal (a pipe, a file)", "the same page, 80 columns, "
     "without colours"],
], "«TAB» — The three forms of the help") + ul([
    "Colours are turned off with " + c("NO_COLOR") + "; " + c("PAGER") + " and " + c("NO_COLOR") + " reach "
    + c("ams") + " only if sudo preserves them (" + c("env_keep") + " in sudoers): the help says so in the "
    "ENVIRONMENT section.",
    "The help too requires root: " + c("ams --help") + " re-runs itself with sudo like every other command ("
    + cap(4, 1) + "). It is the user's decision, at the cost of asking for the password even for the help.",
    c("ams") + " on its own in a pipe shows the help as plain text (" + c("tests/tui.py") + ").",
]) + term("admin@server:~$ sudo ams --help | head -5\n"
          "AMS(1)                           Manuale di ams                           AMS(1)\n"
          "\n"
          "NOME\n"
          "       ams — invia messaggi agli utenti della macchina e ne segue la conferma di\n"
          "       lettura",
          "The help in a pipe (beginning)")

S3 = table(["Part", "How it works"], [
    ["terminal", c("/dev/tty") + " without echo or canonical mode (" + c("termios") + "), alternate screen and "
     "hidden cursor; on exit and on " + c("SIGINT") + ", " + c("SIGTERM") + ", " + c("SIGHUP") + " everything goes "
     "back to how it was"],
    ["keys", "one byte at a time with a " + c("poll") + " of 0.3 s; after " + c("ESC") + " the rest with a wait of "
     "50 ms: " + key("Esc") + " on its own quits; arrows, " + key("PgUp") + ", " + key("PgDn") + ", " + key("Home")
     + ", " + key("End") + " are recognised"],
    ["tabs", key("←") + " " + key("→") + ", " + key("Tab") + ", " + key("Shift", "Tab") + ", " + key("h") + " "
     + key("l") + ", " + key("Enter") + ", or the digits " + key("1") + "…" + key("5")],
    ["scrolling", key("↑") + " " + key("↓") + " (" + key("k") + " " + key("j") + "), " + key("PgUp") + " "
     + key("PgDn") + " (" + key("b") + " " + key("Space") + "), " + key("g") + " " + key("G") + "; each tab "
     "remembers its position; at the bottom “lines 1-20/57”"],
    ["resizing", "at every 0.3 s wait the help compares the size (" + c("TIOCGWINSZ")
     + ") with the last one and redraws; below 44 × 10 it exits"],
    ["drawing", "the tab's lines are prepared without colours, so the lengths are the visible ones; frame, "
     "tabs and status line are written in a single write; the status line is shortened if it does not fit"],
    ["exit", key("q") + " or " + key("Esc") + ": main screen restored, exit code 0"],
], "«TAB» — The tabbed help") + \
    p(c("tests/help-tui.py") + " opens the help on a 100 × 30 pseudo-terminal, presses keys like a person and "
      "checks every screen: opening and frame, tab switching with arrow and digit, end and start of a tab, "
      "resizing to 70 × 20, clean exit, and the page with the pager on a 40 × 8 terminal ("
      + cap(21, 4) + ").")

CHAPTER = ("The built-in help", [
    ("A single source", S1),
    ("The three forms", S2),
    ("The tabbed help", S3),
])
