# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

from build import arrow, box, c, code, diamond, dl, fig, note, p, path, table, term, text, ul, warn


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


STARTUP = fig(
    box(20, 120, 170, 56, "rspeak_init", "environment, RSPEAK_TEST", "dark")
    + diamond(330, 148, 220, 76, "root or RSPEAK_TEST?", "navy")
    + box(250, 232, 160, 50, "execvp sudo", "sudo -- /proc/self/exe", "grey")
    + diamond(600, 148, 200, 76, "no arguments?", "navy")
    + box(520, 232, 160, 50, "recovery, TUI", "stdin and stdout tty", "blue")
    + box(720, 40, 160, 50, "help, version", "help, --help, version", "light")
    + box(720, 120, 160, 56, "command", "recovery, then the command", "blue")
    + box(720, 232, 160, 50, "die", "“rspeak: unknown command”", "amber")
    + path([(192, 148), (218, 148)], "#0050C0")
    + arrow(330, 188, 330, 230, "#475569", False, "no", 346, 212)
    + arrow(442, 148, 498, 148, "#0050C0", False, "yes", 470, 138)
    + arrow(600, 188, 600, 230, "#0050C0", False, "yes", 616, 212)
    + path([(700, 148), (710, 148), (710, 65), (718, 65)], "#0050C0")
    + arrow(700, 148, 718, 148, "#0050C0")
    + path([(700, 160), (706, 160), (706, 257), (718, 257)], "#b45309", True)
    + text(160, 250, "relaunches unchanged", 11, "#475569"),
    900, 300, "«FIG» — Starting rspeak: environment, root, then the command", "Starting rspeak")

S1 = p("The " + c("main") + " of " + c("src/rspeak.c") + " is short and its order is a rule: <b>nothing runs without "
       "root</b>, not even the help. Before looking at the arguments it reads the environment; then, "
       "if it is not root and not in test mode, it relaunches itself with sudo.", lead=True) + STARTUP + code("""int main(int argc, char **argv)
{
	const char *cmd = argc > 1 ? argv[1] : "";

	rspeak_init("rspeak");
	/* As a non-root administrator, rspeak re-runs itself with sudo, even for
	 * the help and the version. */
	if (geteuid() != 0 && !rspeak_test)
		rerun_with_sudo(argv);
	umask(022);

	/* rspeak alone in a terminal opens the TUI; in a pipe, or with a
	 * terminal too small, the help */
	if (!*cmd && isatty(0) && isatty(1)) {
		recover();
		if (rspeak_tui())
			return 0;
	}
	if (!*cmd || !strcmp(cmd, "help") || !strcmp(cmd, "-h") || !strcmp(cmd, "--help")) {
		rspeak_help();
		return 0;
	}
	if (!strcmp(cmd, "version") || !strcmp(cmd, "--version")) {
		printf("RootSpeak - Advanced Messaging System for Linux %s\\n", RSPEAK_VERSION);
		return 0;
	}
	if (strcmp(cmd, "send") && strcmp(cmd, "list") && strcmp(cmd, "status") && strcmp(cmd, "revoke") &&
	    strcmp(cmd, "remind") && strcmp(cmd, "log") && strcmp(cmd, "purge"))
		die("unknown command: %s (rspeak --help for the guide)", cmd);
	…
}""", "c", "src/rspeak.c (in brief)") + ul([
    c("rerun_with_sudo") + " reads its own path from " + c("/proc/self/exe") + " and calls "
    + c("execvp(\"sudo\", [\"sudo\", \"--\", path, arguments…])") + ": the arguments arrive unchanged, and "
    + c("--") + " prevents them from being taken as sudo options.",
    "Under sudo the environment is what sudo preserves: " + c("RSPEAK_TEST") + " is not kept. " + c("SUDO_USER") + " tells who launched the command: it becomes the sender ("
    + c("from") + ") and the author of the events.",
    "Recovery of interrupted sends (" + cap(8, 6) + ") runs before " + c("send") + ", " + c("list") + ", "
    + c("status") + ", " + c("revoke") + ", " + c("remind") + ", " + c("log") + " and the TUI; not before "
    + c("purge") + ", which skips incomplete sends by itself.",
    "An unknown command ends with " + c("die") + ": " + c("rspeak: unknown command: X (rspeak --help for the guide)")
    + ", exit status 1.",
])

S2 = p(c("rootspeak-user") + " never relaunches itself: it runs with the identity of whoever launches it, that is the "
       "user. Its " + c("main") + " has a different order, dictated by the desktop agent.", lead=True) + table(
    ["Step", "Why"], [
        ["1. handler for " + c("SIGUSR1"), "it is the <b>first statement</b>: by default " + c("SIGUSR1") + " terminates the "
         "process, and " + c("rspeak send") + " might send it to an agent that has just started (" + cap(12, 2) + ")"],
        ["2. " + c("rspeak_init(\"rootspeak-user\")") + ", " + c("conf_read"),
         "environment, configuration"],
        ["3. user from " + c("getuid") + " and " + c("getpwuid"), "the mailbox is " + c("users/<name>") + ": the name "
         "never comes from an argument"],
        ["4. " + c("prompt [--login]"), "the question in the terminal (" + cap(11) + ")"],
        ["5. " + c("agent"), "the desktop agent (" + cap(12) + ")"],
        ["6. " + c("confirm ID CHANNEL"), "only in test mode: recording the confirmation on its own, for "
         + c("tests/engine.sh")],
        ["otherwise", "“rootspeak-user: internal RootSpeak helper, not meant to be run directly”, exit status 1"],
    ], "«TAB» — Starting rootspeak-user")

S3 = p(c("rspeak_init") + " in " + c("src/common.c") + " sets the working folders. The defaults are compiled into "
       "the program; the environment variables count <b>only in test mode</b>: a root program does not take folders "
       "from the environment of whoever launches it.", lead=True) + table(
    ["Global variable", "Default", "In test mode"], [
        [c("rspeak_var"), c("/var/lib/rootspeak"), c("RSPEAK_VAR")],
        [c("rspeak_libdir"), c("LIBDIR") + " from the Makefile (" + c("PREFIX/lib/rootspeak") + ")", c("RSPEAK_LIB")],
        [c("rspeak_conf_path"), c("/etc/rootspeak/rootspeak.conf"), c("RSPEAK_CONF")],
        [c("rspeak_test"), "false", "true if " + c("RSPEAK_TEST") + " is not empty"],
        [c("rspeak_name"), "—", c("\"rspeak\"") + " or " + c("\"rootspeak-user\"") + ": the prefix of error messages"],
    ], "«TAB» — The RootSpeak environment") + dl([
    ("RSPEAK_TEST=1", c("rspeak") + " does not relaunch itself with sudo, does not wake or start agents, does not change "
     "identity in child processes and writes only to the “terminal” " + c("RSPEAK_TEST_TTY") + ". An ordinary user who "
     "sets it keeps their own permissions (scenario G4: “Permission denied” as soon as "
     + c("rspeak") + " is executed), and sudo removes it from the environment."),
    ("RSPEAK_TEST_TTY=file", "the “terminal” that " + c("rspeak send") + " writes to in test mode; empty: none."),
    ("RSPEAK_BUILD=folder", "for the tests: the folder of the programs to test (for example " + c("build-san") + ")."),
])

S4 = p("The code is tested from the repository folder as an ordinary user, on a test message store, after "
       + c("make") + ". This is how " + c("tests/engine.sh") + ", " + c("tests/tui.py") + " and "
       + c("tests/help-tui.py") + " run.", lead=True) + term(
    "nicfio@server:~/ROOTSPEAK$ make\n"
    "nicfio@server:~/ROOTSPEAK$ export RSPEAK_TEST=1 RSPEAK_LIB=$PWD/build\n"
    "nicfio@server:~/ROOTSPEAK$ export RSPEAK_VAR=/tmp/test-store RSPEAK_CONF=/dev/null RSPEAK_TEST_TTY=/tmp/tty\n"
    "nicfio@server:~/ROOTSPEAK$ build/rspeak send --to nicfio \"Test\"\n"
    "Message 1 sent to 1 user.\n"
    "nicfio@server:~/ROOTSPEAK$ script -qec 'build/rootspeak-user prompt' /dev/null",
    "A test without root") + \
    warn("without " + c("RSPEAK_TEST") + ", " + c("build/rspeak") + " goes through sudo; if the sudo credentials are still "
         "valid it starts as root without asking anything, on the real message store. In tests always set "
         "test mode.") + \
    note("in test mode the recipients are real users of the machine (" + c("getpwnam") + "), but their "
         "mailboxes are folders of the test message store written with the identity of whoever runs the test: "
         + c("tests/engine.sh") + " uses " + c("root") + " as its second recipient.")

CONF = fig(
    box(20, 50, 200, 60, "/etc/rootspeak/rootspeak.conf", "read with read_file", "dark")
    + box(270, 50, 200, 60, "conf_from_text", "line by line", "navy")
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
       + c("source") + ", by root and by the users, and could execute code. Now " + c("conf_read") + " in "
       + c("src/text.c") + " reads at most 65536 bytes of it and " + c("conf_from_text") + " accepts only two keys, "
       "with positive integers.", lead=True) + code("""# RootSpeak - Advanced Messaging System for Linux: configuration
# A data file, not a script: KEY=value lines with positive whole numbers.
# Unknown keys and invalid values are ignored.

# After how many minutes a message postponed by the user is shown again
RSPEAK_REMIND_MINUTES=30

# Every how many seconds the desktop agent checks the messages again
# (new messages wake it at once anyway)
RSPEAK_AGENT_POLL=60""", "conf", "etc/rootspeak/rootspeak.conf") + CONF + table(["Key", "Default", "Who uses it", "When it is re-read"], [
    [c("RSPEAK_REMIND_MINUTES"), "30", c("rootspeak-user prompt") + " and the agent: how long a postponement lasts",
     "at every " + c("rootspeak-user prompt") + "; at every round of the agent"],
    [c("RSPEAK_AGENT_POLL"), "60", "the agent: the periodic check, in addition to the wake-up", "at every round of the agent"],
], "«TAB» — The configuration keys") + ul([
    "Each line loses its comment (from " + c("#") + " onwards) and all spaces; a line that is still longer than 255 "
    "characters is not valid.",
    "The value must consist of digits only, at most 6, and be greater than zero: " + c("0") + ", " + c("-3") + ", "
    + c("abc") + " and " + c("$(…)") + " are ignored and the default stays (" + c("tests/engine.sh") + ", group 5).",
    "Unknown keys are ignored; a missing file, or one that is not a regular file, counts as empty.",
    c("rspeak") + " itself does not read the configuration: the two keys concern only what " + c("rootspeak-user") + " does.",
])

CHAPTER = ("Startup and configuration", [
    ("Starting rspeak", S1),
    ("Starting rootspeak-user", S2),
    ("The environment and test mode", S3),
    ("Testing without root", S4),
    ("The configuration: rootspeak.conf", S5),
])
