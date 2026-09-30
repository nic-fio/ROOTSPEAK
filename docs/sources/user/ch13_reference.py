import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import c, esc, help_items, help_reference, note, p, table, term  # noqa: E402
from _helpers import rif  # noqa: E402

SINTASSI = ("admin@server:~$ ams --help | head -16\n"
            "AMS(1)                           Manuale di ams                           AMS(1)\n"
            "\n"
            "NOME\n"
            "       ams — invia messaggi agli utenti della macchina e ne segue la conferma di\n"
            "       lettura\n"
            "\n"
            "SINTASSI\n"
            "       ams send --to DEST [opzioni] [TESTO]\n"
            "       ams list\n"
            "       ams status ID\n"
            "       ams\n"
            "       ams revoke ID\n"
            "       ams remind ID\n"
            "       ams log ID\n"
            "       ams purge DURATA\n"
            "       ams version")

S1 = p("This chapter lists all the commands and options of " + c("ams") + ". The texts of the commands, options "
       "and examples are the same as those of the built-in help (" + c("ams --help") + ", " + rif(9) + "): this page "
       "is generated from its English source texts, so the two cannot diverge. The help itself speaks the language "
       "of the session; the example below comes from an Italian session.", lead=True) + \
    term(SINTASSI, "The syntax, from the help in text form: «Manuale di ams» (“ams manual”), «NOME» (“NAME”): «ams — "
         "invia messaggi agli utenti della macchina e ne segue la conferma di lettura» (“ams — sends messages to the "
         "users of the machine and tracks their read confirmation”), «SINTASSI» (“SYNOPSIS”)") + \
    table(["Part", "Meaning"], [
        [c("ID"), "the number of a message, as it appears in the list"],
        [c("DEST"), "the recipients: names, " + c("@gruppo") + ", " + c("all") + ", " + c("online") + ", separated "
         "by commas without spaces (@group: a group name after the @)"],
        [c("DURATA"), "a number followed by " + c("m") + " (minutes), " + c("h") + " (hours) or " + c("d")
         + " (days); for " + c("--expires") + " also a date and a time (DURATION in the English help)"],
        [c("[opzioni]") + ", " + c("[TESTO]"), "the parts in square brackets can be omitted ([options] and [TEXT] "
         "in the English help)"],
    ], "«TAB» — How to read the syntax") + \
    note("every command, " + c("version") + " and " + c("--help") + " included, restarts itself with sudo if it is "
         "not already root.", "Always as root.")

S2 = p("The commands of " + c("ams") + ", with the text of the built-in help.", lead=True) + \
    help_reference("AMS_HELP_COMMANDS", "command")

S3 = p("The options of " + c("ams send") + ". They must be written before the text of the message; in the TUI they "
       "correspond to the fields of the new message (" + rif(5, 4) + ").", lead=True) + \
    help_reference("AMS_HELP_OPTIONS", "option") + \
    table(["Option", "TUI field"], [
        [c("--to"), "A (“To” in English)"],
        [c("--title"), "Titolo (“Title”)"],
        [c("--expires"), "Scadenza (“Expires”)"],
        [c("--file"), "Testo (“Text”), or " + "Ctrl+E" + " to open it in the editor"],
    ], "«TAB» — Options and TUI fields")

S4 = table(["Command", "What it does"], [[c(cmd), esc(desc)] for cmd, desc in help_items("AMS_HELP_EXAMPLES")],
           "«TAB» — The examples of the built-in help")

S5 = table(["Exit status", "Meaning"], [
    [c("0"), "Completed successfully."],
    [c("1"), "Error: the error message, starting with «ams:», says which (" + rif(12, 1) + ")."],
], "«TAB» — The exit status of the commands") + \
    p("The exit status makes it possible to use " + c("ams") + " in scripts:") + \
    term('admin@server:~$ ams send --to online --expires 15m "Riavvio alle 13:00." || echo "invio non riuscito"\n'
         "Messaggio 7 inviato a 3 utenti.", "In a script: «Riavvio alle 13:00.» (“Reboot at 13:00.”), «invio non "
         "riuscito» (“sending failed”), «Messaggio 7 inviato a 3 utenti.» (“Message 7 sent to 3 users.”)") + \
    table(["Variable", "Effect"], [
        [c("PAGER"), "the program that pages the help on small terminals (default: less)"],
        [c("NO_COLOR"), "if set, disables colours"],
        [c("VISUAL") + ", " + c("EDITOR"), "the editor opened with Ctrl+E in the new message"],
    ], "«TAB» — The environment variables (they reach ams only if sudo keeps them, " + rif(10, 3) + ")")

CHAPTER = ("Command reference", [
    ("Syntax", S1),
    ("Commands", S2),
    ("Send options", S3),
    ("Examples", S4),
    ("Exit status and environment", S5),
])
