from build import arrow, box, c, code, fig, note, p, seq, table, text, ul, zone


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


SYMLINK = fig(
    zone(20, 44, 420, 214, "If root wrote directly", "#fdf2f2")
    + box(44, 84, 150, 54, "rspeak (root)", "writes inbox/12", "navy")
    + box(262, 84, 156, 54, "users/mario/inbox", "replaced by Mario…", "amber", 12)
    + box(262, 176, 156, 54, "/etc", "…with a symlink", "grey")
    + arrow(196, 111, 260, 111, "#b91c1c")
    + arrow(340, 140, 340, 174, "#b91c1c", True)
    + text(130, 206, "root would write", 11.5, "#b91c1c", "700")
    + text(130, 224, "inside /etc", 11.5, "#b91c1c", "700")
    + zone(470, 44, 410, 214, "With as_user", "#f0fdf4")
    + box(494, 84, 150, 54, "rspeak (root)", "as_user(mario)", "navy")
    + box(704, 84, 156, 54, "child (mario)", "writes inbox/12", "light")
    + box(704, 176, 156, 54, "/etc", "permission denied", "grey")
    + arrow(646, 111, 702, 111, "#16a34a")
    + arrow(782, 140, 782, 174, "#475569", True)
    + text(580, 206, "worst case: Mario", 11.5, "#166534", "700")
    + text(580, 224, "spoils his own mailbox", 11.5, "#166534", "700"),
    900, 276, "«FIG» — Why root accesses the mailboxes with the user's identity",
    "The danger of symbolic links")

S1 = p("The mailbox " + c("users/U") + " belongs to the user, who can replace its subfolders with "
       "symbolic links, pipes or odd files. If root wrote into it directly, it would follow the link "
       "and could write anywhere; if it read from it, it could show files the user is not allowed to read. This is "
       "why <b>every access by root to the contents of a mailbox happens in a child process with the user's "
       "identity</b>: " + c("as_user") + " in " + c("src/user.c") + ", in place of the " + c("runuser")
       + " used by the prototype.", lead=True) + SYMLINK + \
    p("In the child the user's permissions apply: a link to " + c("/etc") + " leads to «permission "
      "denied», and the worst the user can achieve is to spoil their own copy. Scenario G1 on the test "
      "machine checks this: with the mailbox turned into a link to " + c("/etc") + ", " + c("rspeak send") + " "
      "writes nothing in " + c("/etc") + " and the recipient stays “sent, not delivered”.") + \
    note("only the folder " + c("users/U") + " itself is touched by root: root creates it (" + c("700") + ") inside "
         + c("users/") + ", which belongs to root, and hands it over to U with " + c("lchown") + ". If it already "
         "exists it must be a real folder (" + c("lstat") + "); if it is still owned by root, because a send was "
         "interrupted between creation and handover, it is handed over at the next send (scenario F6).")

CHILD = seq([("rspeak (root)", "as_user", "navy"), ("pipe", "stdin · stdout", "soft"),
              ("child", "fork", "dark"), ("child as U", "fn(arg)", "blue")], [
    (0, 2, "fork"),
    ("note", 2, "stdin and stdout on pipes"),
    (2, 3, "initgroups, setresgid, setresuid"),
    ("note", 3, "setuid(0) must fail".ljust(22)),
    (0, 1, "data on stdin"),
    (3, 1, "output, at most max bytes", True),
    ("sep", "within the time limit".ljust(22)),
    (3, 0, "exit code (waitpid)", True),
    ("note", 0, "timed out: SIGKILL".ljust(22)),
], "«FIG» — How the child process starts and ends", "A child with the user's identity")

S2 = p(c("as_user(u, fn, arg, in, out, max, seconds)") + " runs " + c("fn(arg)") + " in a child process "
       "with the identity of " + c("u") + ". The parent passes it data on stdin, collects its output on a pipe and "
       "waits for it to finish, always with a time limit.", lead=True) + CHILD + code("""static void child(const user_t *u, as_user_fn fn, void *arg, int in, int out)
{
	int nul = open("/dev/null", O_RDWR | O_CLOEXEC);

	if (nul < 0 || dup2(in >= 0 ? in : nul, 0) < 0 || dup2(out >= 0 ? out : nul, 1) < 0 || dup2(nul, 2) < 0)
		_exit(126);
	if (geteuid() == 0 && !rspeak_test) {
		/* the user's full identity: supplementary groups, then group, then user */
		if (initgroups(u->name, u->gid) < 0 || setresgid(u->gid, u->gid, u->gid) < 0 ||
		    setresuid(u->uid, u->uid, u->uid) < 0)
			_exit(126);
		if (getuid() != u->uid || geteuid() != u->uid || getegid() != u->gid || setuid(0) == 0)
			_exit(126);
	}
	if (chdir("/") < 0)
		_exit(126);
	umask(022);
	signal(SIGPIPE, SIG_DFL);
	{
		int r = fn(arg);

		fflush(stdout);
		_exit(r & 0xff);
	}
}""", "c", "src/user.c") + ul([
    "The order matters: first the supplementary groups (" + c("initgroups") + "), then the group, then the user; after "
    + c("setresuid") + " the group can no longer be changed.",
    "The child checks that it can <b>not</b> become root again: if " + c("setuid(0)") + " succeeded, the identity "
    "would not really have been assumed. Any anomaly ends with exit code 126, which the parent turns into an error.",
    "After the identity change the kernel makes the process non-inspectable by the user (not «dumpable»): U cannot "
    "read its memory while it works.",
    "In test mode, without root, the child keeps the identity of whoever runs the test.",
])

S3 = p("The child runs with the user's identity, so the user can stop it (" + c("SIGSTOP") + ") or "
       "slow it down. " + c("rspeak") + " must not hang: the time limit applies both while the child is writing and "
       "afterwards, until it exits.", lead=True) + table(["Result of as_user", "When"], [
    ["the exit code of " + c("fn") + " (0–125, 127–255)", "the child exited normally"],
    [c("-1"), "the child did not start (" + c("pipe2") + ", " + c("fork") + "); it could not assume the identity "
     "(code 126); it was killed by a signal; the time ran out (the parent kills it with " + c("SIGKILL") + ")"],
], "«TAB» — The results of as_user") + table(["Call", "Time limit", "Output collected"], [
    ["delivery, revocation, reminder, deletion", "20 s", "none: the exit code is what counts"],
    ["reading a mailbox (" + c("read_mailbox") + ")", "20 s", "at most 4 MiB"],
    ["waking the agent", "5 s", "none"],
], "«TAB» — The time limits") + \
    p("The pipes are created with " + c("O_CLOEXEC") + "; the child's stdin is written in non-blocking mode, "
      "alternating with reading the output via " + c("poll") + " (at most one second per round), so a child that "
      "does not read does not block the parent. gcc's static analysis found pipes left open in an error path of "
      + c("as_user") + ": fixed (" + cap(20, 7) + ").")

S4 = p("All operations on the mailboxes are functions in " + c("src/store.c") + " that run inside the child. "
       "They are small on purpose: each does one thing, with paths built from the message number.", lead=True) + \
    table(["Operation", "Called by", "In the child (as U)", "Result"], [
        [c("op_deliver"), c("deliver_copy") + ": sending and recovery", "creates " + c("inbox read acks state")
         + " if missing; if the message is already in " + c("read/") + " or " + c("acks/") + " it does nothing; "
         "otherwise it writes " + c("inbox/ID.tmp") + " (" + c("O_EXCL|O_NOFOLLOW") + "), renames it and checks that "
         + c("inbox/ID") + " is a regular, non-empty file", "0 if the copy is there (or was already read)"],
        [c("op_take"), c("remove_copy") + ": revocation", "removes " + c("inbox/ID") + ", " + c("state/ID.term")
         + " and " + c("state/ID.gui"), "0 if the copy is no longer there"],
        [c("op_clear_postponements"), c("clear_postponements") + ": reminder", "removes " + c("state/ID.term") + " and "
         + c("state/ID.gui"), "0 if none are left"],
        [c("op_remove"), c("remove_copies") + ": deletion", "removes " + c("inbox/ID") + ", " + c("read/ID")
         + ", " + c("acks/ID") + " and the postponements", "always 0"],
        [c("op_read"), c("read_mailbox") + ": " + c("list") + ", " + c("status") + ", TUI", "for each ID received "
         "on stdin: first line of " + c("acks/ID") + " (at most 200 bytes, only from a regular file) and most "
         "recent date of " + c("state/ID.*"), "lines «A ID line» and «S ID date» (" + cap(10, 2) + ")"],
        [c("op_wake"), c("wake_agent"), "reads the ready PID, checks the command line, sends "
         + c("SIGUSR1"), "0 if woken (" + cap(8, 5) + ")"],
    ], "«TAB» — The operations performed as the user") + \
    note("revocation and deletion do not ask the user whether the folder exists: if " + c("users/U")
         + " is not there (a user never reached) there is nothing to remove and the operation succeeds without "
         "starting the child.")

CHAPTER = ("Root with the user's identity", [
    ("The danger of symbolic links", S1),
    ("How the child process starts", S2),
    ("Time limits and results", S3),
    ("Operations on the mailboxes", S4),
])
