from build import arrow, box, c, code, diamond, fig, note, p, path, seq, table, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


FLUSSO = fig(
    diamond(110, 70, 180, 60, "acks/ID there?", "navy")
    + box(30, 140, 160, 50, "result 0", "the first one counts", "green", 12)
    + diamond(320, 70, 190, 60, "inbox/ID there?", "navy")
    + box(240, 140, 160, 50, "result 3", "revoked", "grey", 12)
    + diamond(530, 70, 170, 60, "expired?", "navy")
    + box(450, 140, 160, 50, "result 2", "to read/, no confirmation", "grey", 12)
    + box(650, 40, 230, 60, "acks/.ID.PID", "date channel · fsync", "blue", 12)
    + box(650, 130, 230, 60, "link(tmp, acks/ID)", "fails if it already exists", "navy", 12)
    + box(650, 220, 230, 60, "fsync(acks/), read/", "event CONFIRMED", "green", 12)
    + box(380, 230, 200, 50, "result 1 or 0", "failed, or it appeared meanwhile", "amber", 12)
    + arrow(110, 100, 110, 138, "#16a34a", False, "yes", 124, 122)
    + arrow(200, 70, 223, 70, "#0050C0", False, "no", 212, 60)
    + arrow(320, 100, 320, 138, "#475569", False, "no", 334, 122)
    + arrow(415, 70, 443, 70, "#0050C0", False, "yes", 429, 60)
    + arrow(530, 100, 530, 138, "#475569", False, "yes", 544, 122)
    + arrow(615, 70, 648, 70, "#0050C0", False, "no", 630, 60)
    + arrow(765, 102, 765, 128) + arrow(765, 192, 765, 218, "#16a34a", False, "succeeds", 800, 208)
    + path([(648, 160), (620, 160), (620, 255), (582, 255)], "#b45309", True, "error", 588, 212),
    900, 300, "«FIG» — confirm(ID, CHANNEL): the checks and the exclusive publication",
    "How a confirmation is born")

S1 = p(c("confirm(ID, CHANNEL)") + " in " + c("src/rootspeak-user.c") + " is the only place where a confirmation is born. "
       "It writes it to a temporary file, flushes it to disk and publishes it with " + c("link") + ", which fails if "
       + c("acks/ID") + " already exists: the confirmation is born <b>whole or not at all</b>, and “already confirmed” "
       "stays distinct from “write failed”.", lead=True) + FLUSSO + code("""static int confirm(long long id, const char *channel)
{
	if (exists(ack)) { mark_read(id); return 0; }          /* the first one counts */
	if (!has_entry("inbox", id, "")) return 3;             /* revoked: no confirmation */
	if (expired(id)) { mark_read(id); return 2; }
	fd = open(tmp, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, 0644);
	if (fd < 0 || n <= 0 || write_all(fd, line, (size_t)n) < 0 || fsync(fd) < 0 || close(fd) < 0 ||
	    link(tmp, ack) < 0) {                              /* link fails if acks/ID exists */
		unlink(tmp);
		if (exists(ack)) { mark_read(id); return 0; }  /* another confirmation came first */
		event("CONFIRMATION_FAILED", id, U, channel, err, "");
		return 1;                                      /* the message stays in the mailbox */
	}
	unlink(tmp);
	sync_path(dir);                                        /* on disk before “Confirmed” */
	mark_read(id);
	event("CONFIRMED", id, U, channel, "", "");
	return 0;
}""", "c", "src/rootspeak-user.c (in short)") + table(["Case", "Result", "What happens"], [
    ["confirmation written", "0", "the message moves to " + c("read/") + ", the postponements are removed; event in the log"],
    [c("acks/ID") + " already present", "0", "moves to " + c("read/") + "; the first confirmation stays"],
    ["write failed (disk full, permissions)", "1", "<b>stays in " + c("inbox/") + "</b>; the user is told, "
     "the error goes to the log, the question or the dialog comes back (" + c("tests/engine.sh") + ", group 1; scenario "
     "F4)"],
    ["message expired", "2", "moves to " + c("read/") + " without a confirmation: a confirmation after the expiry does not count"],
    ["copy gone (revoked)", "3", "no confirmation"],
], "«TAB» — The results of confirm") + ul([
    "The line is " + c("date channel") + ": seconds since the Unix epoch, a space, the channel as it is shown ("
    + c("desktop") + ", " + c("terminal pts/3") + ", " + c("terminal tty3") + ").",
    "The temporary file " + c("acks/.ID.PID") + " starts with a dot: it is never mistaken for a confirmation. If "
    "an interruption leaves it behind, it is ignored.",
    "If the revocation arrives between the check of " + c("inbox/ID") + " and " + c("link") + ", the confirmation is "
    "born, but " + c("rspeak status") + " does not count it: its date is later than " + c("sent/ID/revoked") + " ("
    + cap(10, 1) + ").",
    c("mark_read") + " renames " + c("inbox/ID") + " to " + c("read/ID") + " and removes the postponements. If it "
    "is interrupted between the confirmation and the move, whoever reads the mailbox next completes the move without "
    "asking again (" + c("tests/engine.sh") + ", group 1).",
])

RACE = seq([("Dialog", "confirm … desktop", "blue"), ("acks/ID", "link: exclusive", "green"),
            ("Terminal", "confirm … pts/3", "blue")], [
    (0, 1, "link: succeeds"),
    (2, 1, "link: fails, already exists", True),
    ("note", 2, "exists(ack): mark_read, code 0".ljust(33)),
    ("note", 0, "CONFIRMED (desktop)"),
    ("sep", "a second later, the other open question"),
    (2, 1, "acks/ID appeared?"),
    ("note", 2, "“already confirmed elsewhere”".ljust(29)),
], "«FIG» — Two almost simultaneous confirmations: the first one counts", "The first confirmation wins")

S2 = p("A user may have the dialog open on the desktop and the question in two terminals. The confirmation must be "
       "<b>one</b>: the first to arrive.", lead=True) + RACE + ul([
    "Two almost simultaneous confirmations produce a single record: " + c("link") + " succeeds only once; "
    "the other finds " + c("acks/ID") + " and only moves the message.",
    "The questions and dialogs still open notice it at their next check (within a second) and "
    "close: “[RootSpeak] Message already confirmed elsewhere (for example on the desktop).” in the terminal, while the dialog "
    "closes by itself (scenarios C4b and I5).",
    "This rule came from a live test of the prototype: the user had to confirm twice, from the "
    "dialog and from the terminal.",
])

S3 = p(c("rspeak status") + " reads the confirmations from the mailbox, which the user controls. That is why it treats "
       "them as <b>untrusted data</b>, and their meaning is deliberately limited.", lead=True) + table(
    ["Risk", "Rule"], [
        ["a symbolic link " + c("acks/ID") + " pointing to a restricted file", "the read happens as the user "
         "(" + cap(7) + "): a file the user cannot read is not read"],
        ["a pipe or a device in place of the confirmation", "only a regular file is read, opened without blocking"],
        ["a huge confirmation", "at most 200 bytes are read, and only the first line"],
        ["escape sequences in the channel", "the output goes through " + c("clean_text") + " (scenario G3)"],
        ["a bogus date", "it is just a number: it counts only if it is not later than the expiry and revocation in "
         + c("sent/")],
    ], "«TAB» — The confirmations read by root") + \
    note("<b>“Confirmed” means</b>: the mailbox holds a valid declaration of reading by the user. It is not "
         "an action observed by RootSpeak nor a proof of reading: the user controls their own mailbox and could "
         "write it themselves, just as they could press “I have read it” without reading. Whoever uses " + c("rspeak status")
         + " for an audit must read it this way (" + cap(19, 1) + ").")

CHAPTER = ("Confirmations", [
    ("The first one counts", S1),
    ("Two simultaneous confirmations", S2),
    ("The confirmations read by root", S3),
])
