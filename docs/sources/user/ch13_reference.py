import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import c, esc, help_items, help_reference, note, p, table, term  # noqa: E402
from _helpers import ref  # noqa: E402

SYNOPSIS = ("admin@server:~$ rspeak --help | head -16\n"
            "RSPEAK(1)                        rspeak manual                         RSPEAK(1)\n"
            "\n"
            "NAME\n"
            "       rspeak — sends messages to the users of the machine and tracks their read\n"
            "       confirmation\n"
            "\n"
            "SYNOPSIS\n"
            "       rspeak send --to DEST [options] [TEXT]\n"
            "       rspeak list\n"
            "       rspeak status ID\n"
            "       rspeak\n"
            "       rspeak revoke ID\n"
            "       rspeak remind ID\n"
            "       rspeak log ID\n"
            "       rspeak purge DURATION\n"
            "       rspeak version")

S1 = p("This chapter lists all the commands and options of " + c("rspeak") + ". The texts of the commands, options "
       "and examples are the same as those of the built-in help (" + c("rspeak --help") + ", " + ref(9) + "): this page "
       "is generated from the same texts, so the two cannot diverge.", lead=True) + \
    term(SYNOPSIS, "The syntax, from the help in text form") + \
    table(["Part", "Meaning"], [
        [c("ID"), "the number of a message, as it appears in the list"],
        [c("DEST"), "the recipients: names, " + c("@group") + ", " + c("all") + ", " + c("online") + ", separated "
         "by commas without spaces"],
        [c("DURATION"), "a number followed by " + c("m") + " (minutes), " + c("h") + " (hours) or " + c("d")
         + " (days); for " + c("--expires") + " also a date and a time"],
        [c("[options]") + ", " + c("[TEXT]"), "the parts in square brackets can be omitted"],
    ], "«TAB» — How to read the syntax") + \
    note("every command, " + c("version") + " and " + c("--help") + " included, restarts itself with sudo if it is "
         "not already root.", "Always as root.")

S2 = p("The commands of " + c("rspeak") + ", with the text of the built-in help.", lead=True) + \
    help_reference("RSPEAK_HELP_COMMANDS", "command")

S3 = p("The options of " + c("rspeak send") + ". They must be written before the text of the message; in the TUI they "
       "correspond to the fields of the new message (" + ref(5, 4) + ").", lead=True) + \
    help_reference("RSPEAK_HELP_OPTIONS", "option") + \
    table(["Option", "TUI field"], [
        [c("--to"), "To"],
        [c("--title"), "Title"],
        [c("--expires"), "Expires"],
        [c("--file"), "Text, or " + "Ctrl+E" + " to open it in the editor"],
    ], "«TAB» — Options and TUI fields")

S4 = table(["Command", "What it does"], [[c(cmd), esc(desc)] for cmd, desc in help_items("RSPEAK_HELP_EXAMPLES")],
           "«TAB» — The examples of the built-in help")

S5 = table(["Exit status", "Meaning"], [
    [c("0"), "Completed successfully."],
    [c("1"), "Error: the error message, starting with “rspeak:”, says which (" + ref(12, 1) + ")."],
], "«TAB» — The exit status of the commands") + \
    p("The exit status makes it possible to use " + c("rspeak") + " in scripts:") + \
    term('admin@server:~$ rspeak send --to online --expires 15m "Reboot at 1 pm." || echo "sending failed"\n'
         "Message 7 sent to 3 users.", "In a script") + \
    table(["Variable", "Effect"], [
        [c("PAGER"), "the program that pages the help on small terminals (default: less)"],
        [c("NO_COLOR"), "if set, disables colours"],
        [c("VISUAL") + ", " + c("EDITOR"), "the editor opened with Ctrl+E in the new message"],
    ], "«TAB» — The environment variables (they reach rspeak only if sudo keeps them, " + ref(10, 3) + ")")

CHAPTER = ("Command reference", [
    ("Syntax", S1),
    ("Commands", S2),
    ("Send options", S3),
    ("Examples", S4),
    ("Exit status and environment", S5),
])
