from build import arrow, box, c, code, diamond, dl, fig, note, p, path, table, term, text, ul, warn


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


AVVIO = fig(
    box(20, 40, 170, 56, "ams_init", "environment, AMS_TEST", "dark")
    + box(20, 120, 170, 56, "lingua_init", "LANG, LANGUAGE…", "dark")
    + diamond(330, 148, 220, 76, "root or AMS_TEST?", "navy")
    + box(250, 232, 160, 50, "execvp sudo", "sudo -- /proc/self/exe", "grey")
    + diamond(600, 148, 200, 76, "no arguments?", "navy")
    + box(520, 232, 160, 50, "recovery, TUI", "stdin and stdout tty", "blue")
    + box(720, 40, 160, 50, "help, version", "help, --help, version", "light")
    + box(720, 120, 160, 56, "command", "recovery, then the command", "blue")
    + box(720, 232, 160, 50, "die", "«ams: comando sconosciuto»", "amber")
    + arrow(105, 98, 105, 118) + path([(192, 148), (218, 148)], "#0050C0")
    + arrow(330, 188, 330, 230, "#475569", False, "no", 346, 212)
    + arrow(442, 148, 498, 148, "#0050C0", False, "yes", 470, 138)
    + arrow(600, 188, 600, 230, "#0050C0", False, "yes", 616, 212)
    + path([(700, 148), (710, 148), (710, 65), (718, 65)], "#0050C0")
    + arrow(700, 148, 718, 148, "#0050C0")
    + path([(700, 160), (706, 160), (706, 257), (718, 257)], "#b45309", True)
    + text(160, 250, "relaunches unchanged", 11, "#475569"),
    900, 300, "«FIG» — Starting ams: environment, language, root, then the command", "Starting ams")

S1 = p("The " + c("main") + " of " + c("src/ams.c") + " is short and its order is a rule: <b>nothing runs without "
       "root</b>, not even the help. Before looking at the arguments it reads the environment and the language; then, "
       "if it is not root and not in test mode, it relaunches itself with sudo.", lead=True) + AVVIO + code("""int main(int argc, char **argv)
{
	const char *cmd = argc > 1 ? argv[1] : "";

	ams_init("ams");
	lingua_init();
	if (geteuid() != 0 && !ams_test)       /* anche per la guida e la versione */
		rilancia_con_sudo(argv);           /* execvp("sudo", "--", /proc/self/exe, …) */
	umask(022);
	if (!*cmd && isatty(0) && isatty(1)) { /* ams da solo in un terminale */
		recupera();
		if (ams_tui())
			return 0;                      /* terminale troppo piccolo: la guida */
	}
	if (!*cmd || !strcmp(cmd, "help") || !strcmp(cmd, "-h") || !strcmp(cmd, "--help"))
		{ ams_guida(); return 0; }
	if (!strcmp(cmd, "version") || !strcmp(cmd, "--version")) { … }
	/* comando sconosciuto: die(); purge escluso, prima di ogni comando: recupera() */
	…
}""", "c", "src/ams.c (in brief)") + ul([
    c("rilancia_con_sudo") + " reads its own path from " + c("/proc/self/exe") + " and calls "
    + c("execvp(\"sudo\", [\"sudo\", \"--\", percorso, argomenti…])") + ": the arguments arrive unchanged, and "
    + c("--") + " prevents them from being taken as sudo options.",
    "Under sudo the environment is what sudo preserves: usually " + c("LANG") + " and the language variables are kept, "
    + c("AMS_TEST") + " is not. " + c("SUDO_USER") + " tells who launched the command: it becomes the sender ("
    + c("from") + ") and the author of the events.",
    "Recovery of interrupted sends (" + cap(8, 6) + ") runs before " + c("send") + ", " + c("list") + ", "
    + c("status") + ", " + c("revoke") + ", " + c("remind") + ", " + c("log") + " and the TUI; not before "
    + c("purge") + ", which skips incomplete sends by itself.",
    "An unknown command ends with " + c("die") + ": " + c("ams: comando sconosciuto: X (ams --help per la guida)")
    + " (in English: “unknown command: X (ams --help for the guide)”), exit status 1.",
])

S2 = p(c("ams-user") + " never relaunches itself: it runs with the identity of whoever launches it, that is the "
       "user. Its " + c("main") + " has a different order, dictated by the desktop agent.", lead=True) + table(
    ["Step", "Why"], [
        ["1. handler for " + c("SIGUSR1"), "it is the <b>first statement</b>: by default " + c("SIGUSR1") + " terminates the "
         "process, and " + c("ams send") + " might send it to an agent that has just started (" + cap(12, 2) + ")"],
        ["2. " + c("ams_init(\"ams-user\")") + ", " + c("lingua_init") + ", " + c("conf_leggi"),
         "environment, the user's language, configuration"],
        ["3. user from " + c("getuid") + " and " + c("getpwuid"), "the mailbox is " + c("users/<nome>") + ": the name "
         "never comes from an argument"],
        ["4. " + c("prompt [--login]"), "the question in the terminal (" + cap(11) + ")"],
        ["5. " + c("agent"), "the desktop agent (" + cap(12) + ")"],
        ["6. " + c("conferma ID CANALE"), "only in test mode: recording the confirmation on its own, for "
         + c("tests/engine.sh")],
        ["otherwise", "«ams-user: helper interno di AMS, non va usato direttamente» (in English: “ams-user: internal "
         "AMS helper, not meant to be run directly”), exit status 1"],
    ], "«TAB» — Starting ams-user")

S3 = p(c("ams_init") + " in " + c("src/comune.c") + " sets the working folders. The defaults are compiled into "
       "the program; the environment variables count <b>only in test mode</b>: a root program does not take folders "
       "from the environment of whoever launches it.", lead=True) + table(
    ["Global variable", "Default", "In test mode"], [
        [c("ams_var"), c("/var/lib/ams"), c("AMS_VAR")],
        [c("ams_libdir"), c("LIBDIR") + " from the Makefile (" + c("/usr/local/lib/ams") + ")", c("AMS_LIB")],
        [c("ams_localedir"), c("LOCALEDIR") + " (" + c("/usr/local/share/locale") + ")", c("AMS_LOCALEDIR")],
        [c("ams_conf_path"), c("/etc/ams/ams.conf"), c("AMS_CONF")],
        [c("ams_test"), "false", "true if " + c("AMS_TEST") + " is not empty"],
        [c("ams_nome"), "—", c("\"ams\"") + " or " + c("\"ams-user\"") + ": the prefix of error messages"],
    ], "«TAB» — The AMS environment") + dl([
    ("AMS_TEST=1", c("ams") + " does not relaunch itself with sudo, does not wake or start agents, does not change "
     "identity in child processes and writes only to the “terminal” " + c("AMS_TEST_TTY") + ". An ordinary user who "
     "sets it keeps their own permissions (scenario G4: «Permesso negato», “Permission denied”, as soon as "
     + c("ams") + " is executed), and sudo removes it from the environment."),
    ("AMS_TEST_TTY=file", "the “terminal” that " + c("ams send") + " writes to in test mode; empty: none."),
    ("AMS_BUILD=cartella", "for the tests: the programs to test (for example " + c("build-san") + ")."),
])

S4 = p("The code is tested from the repository folder as an ordinary user, on a test message store, after "
       + c("make") + ". This is how " + c("tests/engine.sh") + ", " + c("tests/tui.py") + " and "
       + c("tests/help-tui.py") + " run.", lead=True) + term(
    "nicfio@server:~/AMS$ make\n"
    "nicfio@server:~/AMS$ export AMS_TEST=1 AMS_LIB=$PWD/build AMS_LOCALEDIR=$PWD/build/locale\n"
    "nicfio@server:~/AMS$ export AMS_VAR=/tmp/prova AMS_CONF=/dev/null AMS_TEST_TTY=/tmp/tty\n"
    "nicfio@server:~/AMS$ build/ams send --to nicfio \"Prova\"\n"
    "Messaggio 1 inviato a 1 utente.\n"
    "nicfio@server:~/AMS$ script -qec 'build/ams-user prompt' /dev/null", "A test without root") + \
    warn("without " + c("AMS_TEST") + ", " + c("build/ams") + " goes through sudo; if the sudo credentials are still "
         "valid it starts as root without asking anything, on the real message store. In tests always set "
         "test mode.") + \
    note("in test mode the recipients are real users of the machine (" + c("getpwnam") + "), but their "
         "mailboxes are folders of the test message store written with the identity of whoever runs the test: "
         + c("tests/engine.sh") + " uses " + c("root") + " as its second recipient.")

CONF = fig(
    box(20, 50, 200, 60, "/etc/ams/ams.conf", "read with leggi_file", "dark")
    + box(270, 50, 200, 60, "conf_da_testo", "line by line", "navy")
    + diamond(600, 80, 200, 70, "known key?", "navy")
    + box(740, 50, 140, 60, "conf_t", "remind, poll", "green")
    + box(520, 160, 160, 48, "ignored", "", "grey")
    + arrow(222, 80, 268, 80) + arrow(472, 80, 498, 80)
    + arrow(702, 80, 738, 80, "#16a34a", False, "yes", 720, 70)
    + arrow(600, 117, 600, 158, "#475569", False, "no", 616, 140)
    + text(370, 150, "# comments and spaces removed; at most 255 characters", 11, "#475569")
    + text(370, 168, "value: digits only, at most 6, greater than zero", 11, "#475569"),
    900, 228, "«FIG» — How the configuration is read", "Data, not code")

S5 = p("The configuration is a <b>data</b> file, not a script: in the bash prototype it was read with "
       + c("source") + ", by root and by the users, and could execute code. Now " + c("conf_leggi") + " in "
       + c("src/testo.c") + " reads at most 65536 bytes of it and " + c("conf_da_testo") + " accepts only two keys, "
       "with positive integers.", lead=True) + code("""# Dopo quanti minuti riproporre un messaggio rimandato dall'utente
AMS_REMIND_MINUTES=30

# Ogni quanti secondi l'agente del desktop ricontrolla i messaggi
# (i nuovi messaggi lo svegliano comunque subito)
AMS_AGENT_POLL=60""", "conf", "etc/ams/ams.conf") + CONF + table(["Key", "Default", "Who uses it", "When it is re-read"], [
    [c("AMS_REMIND_MINUTES"), "30", c("ams-user prompt") + " and the agent: how long a postponement lasts",
     "at every " + c("ams-user prompt") + "; at every round of the agent"],
    [c("AMS_AGENT_POLL"), "60", "the agent: the periodic check, in addition to the wake-up", "at every round of the agent"],
], "«TAB» — The configuration keys") + ul([
    "Each line loses its comment (from " + c("#") + " onwards) and all spaces; a line that is still longer than 255 "
    "characters is not valid.",
    "The value must consist of digits only, at most 6, and be greater than zero: " + c("0") + ", " + c("-3") + ", "
    + c("abc") + " and " + c("$(…)") + " are ignored and the default stays (" + c("tests/engine.sh") + ", group 5).",
    "Unknown keys are ignored; a missing file, or one that is not a regular file, counts as empty.",
    c("ams") + " itself does not read the configuration: the two keys concern only what " + c("ams-user") + " does.",
])

CHAPTER = ("Startup and configuration", [
    ("Starting ams", S1),
    ("Starting ams-user", S2),
    ("The environment and test mode", S3),
    ("Testing without root", S4),
    ("The configuration: ams.conf", S5),
])
