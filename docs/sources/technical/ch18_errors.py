from build import arrow, box, c, code, fig, note, p, path, table, term, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


FAMILIES = fig(
    box(20, 40, 200, 60, "initial checks", "options, text, recipients", "dark")
    + box(20, 130, 200, 60, "failures during the work", "a mailbox, a terminal", "dark")
    + box(20, 220, 200, 60, "interruptions", "signal, power, SIGKILL", "dark")
    + box(300, 40, 220, 60, "die", "“rspeak: …”, exit 1, nothing written", "amber")
    + box(300, 130, 220, 60, "event + carry on", "NOT_DELIVERED, then die", "amber")
    + box(300, 220, 220, 60, "marks in the store", "incomplete, revoking, .deleting", "amber")
    + box(600, 40, 280, 60, "the administrator corrects", "and runs the command again", "light")
    + box(600, 130, 280, 60, "the next command retries", "recovery, " + "warning on stderr", "green")
    + box(600, 220, 280, 60, "the next command repairs", "recover(), idempotent", "green")
    + arrow(222, 70, 298, 70) + arrow(222, 160, 298, 160) + arrow(222, 250, 298, 250)
    + arrow(522, 70, 598, 70) + arrow(522, 160, 598, 160) + arrow(522, 250, 598, 250),
    900, 300, "«FIG» — Three families of errors and who repairs them", "How RootSpeak fails")

S1 = p("RootSpeak distinguishes three families of errors. Those that can be detected before writing stop the command "
       "without leaving traces; those that happen during the work do not stop the other recipients and leave "
       "a mark; interruptions leave a state that the next command knows how to repair.", lead=True) + FAMILIES + \
    table(["Function (src/common.c)", "What it does", "Used by"], [
        [c("die(fmt, …)"), "flushes stdout, writes “" + c("rspeak: ") + "…” (or “" + c("rootspeak-user: ") + "…”) to stderr, "
         "exits with 1", c("rspeak") + ": every error that stops the command"],
        [c("notice(fmt, …)"), "like " + c("die") + ", but the program continues", "recovery, to say what it has "
         "completed or cancelled"],
        [c("xmalloc") + ", " + c("xrealloc") + ", " + c("xasprintf"), "if memory runs out: “out of memory” and exit 1", "everyone"],
    ], "«TAB» — How an error is reported") + ul([
    c("rootspeak-user") + " does not use " + c("die") + " in normal work: it runs inside the prompt or in the graphical "
    "session, and every problem it meets becomes “do nothing” or a notice to the user (" + cap(11, 3) + ").",
    "In the TUI a " + c("die") + " of the command closes only the child process: its message appears in the "
    "result dialog (" + cap(14, 1) + ").",
])

S2 = table(["Message", "When", "What remains"], [
    ["unknown command: X (rspeak --help for the guide)", "first argument not recognised", "nothing"],
    ["missing --to · missing value for --title · unknown option: --level", "options of " + c("send"), "nothing"],
    ["invalid expiry: X · the expiry is already in the past", c("--expires") + " cannot be interpreted, or is in the "
     "past", "nothing"],
    ["FILE: followed by the system's explanation", c("--file") + " not readable", "nothing"],
    ["empty message · message too long: N bytes (at most 65536)", "text after cleaning", "nothing"],
    ["no such user: X · no such group: X · no recipients", c("--to"), "nothing"],
    ["Message N delivered to K of M recipients. · message N not delivered to: … (see the log; the next rspeak command "
     "will retry)", "some copies not written", c("incomplete") + ": recovery retries"],
    ["missing message ID · no such message: X", c("status") + ", " + c("revoke") + ", " + c("remind")
     + ", " + c("log"), "nothing"],
    ["message N was cancelled: sending was interrupted before it was saved", c("status")
     + " of a cancelled sending", "—"],
    ["message N revoked, but some copies could not be removed from the mailboxes: the next rspeak command will retry",
     c("revoke"), c("revoked") + " and " + c("revoking") + ": recovery retries"],
    ["message N has been revoked: nobody to remind · message N has expired: nobody to remind",
     c("remind"), "nothing"],
    ["missing duration, for example 90d · invalid duration: X (for example 90d, 12h, 30m)", c("purge"), "nothing"],
    [c("/var/lib/rootspeak: …") + " · " + c("…/sent/.seq.lock: …") + " · " + c("sudo: …"), "the message store cannot be "
     "created, the lock cannot be taken, sudo does not start (system messages)", "nothing, or a skipped number"],
], "«TAB» — The errors of rspeak") + term("admin@server:~$ sudo rspeak send --to nobodyhere \"Test\"\n"
                                       "rspeak: no such user: nobodyhere\n"
                                       "admin@server:~$ sudo rspeak purge 7x\n"
                                       "rspeak: invalid duration: 7x (for example 90d, 12h, 30m)",
                                       "Two errors, and nothing was written")

S3 = p("Inside RootSpeak the functions talk to each other through numeric results. They are the contract between the "
       "parts, and the chapters that describe them use them with these values.", lead=True) + table(["Function", "Results"], [
    [c("confirm") + " (" + c("rootspeak-user") + ")", "0 recorded or already present · 1 not recorded, the message stays "
     "· 2 expired · 3 revoked (" + cap(13, 1) + ")"],
    [c("ask") + " (" + c("rootspeak-user") + ")", "0 yes · 1 no, or no answer · 2 confirmed elsewhere · 3 revoked "
     "· 4 expired while the question was open (" + cap(11, 3) + ")"],
    ["zenity", "0 “I have read it” · 1 “Later” or dialog closed by the user · other: not a choice (" + cap(12, 3) + ")"],
    [c("as_user"), "the code of " + c("fn") + " · −1 child not started, identity not assumed (126), time "
     "limit exceeded, child killed (" + cap(7, 3) + ")"],
    [c("op_deliver") + ", " + c("op_take") + ", " + c("op_clear_postponements"), "0 success · 1 failure"],
    [c("read_file") + ", " + c("write_atomic"), "0 · −1 with " + c("errno") + " (" + c("EINVAL") + " if it is not a "
     "regular file, " + c("EFBIG") + " if too large)"],
    [c("msg_read") + ", " + c("msg_from_text"), "0 · −1 if the file is missing, is not regular, is too large or does "
     "not have a valid date"],
    [c("summarise"), "true · false if the message no longer exists, has no recipients or has been cancelled"],
], "«TAB» — Internal results") + \
    note("code 126 is reserved: a child that cannot assume the identity exits with 126, and "
         + c("as_user") + " treats it as a failure even if " + c("fn") + " could have returned it.")

S4 = table(["Warning (stderr)", "What happened", "Event"], [
    ["completed delivery of message N to K recipients", "an interrupted sending has been completed", c("RECOVERED")],
    ["message N still not delivered to K recipients (see rspeak status N)", "recovery could not "
     "write some copies; it will retry", "—"],
    ["message N was interrupted before being saved and has been cancelled", "a sending without "
     + c("msg") + " or " + c("recipients") + " has been closed with " + c("failed"), c("CANCELLED")],
], "«TAB» — Recovery warnings") + \
    p("The warnings appear at the start of any command that runs recovery, even one that has nothing to do with "
      "that message: " + c("rspeak list") + " can therefore say “rspeak: completed delivery of message 2 to 64 "
      "recipients” (scenario F3). The command then carries on "
      "normally.") + table(["Code", "Meaning"], [
    ["0", "completed"],
    ["1", "error: the message, which begins with “rspeak:”, says which"],
    ["other", "a sudo code, before " + c("rspeak") + " starts"],
], "«TAB» — The exit status of rspeak")

CHAPTER = ("Error taxonomy", [
    ("Three families of errors", S1),
    ("The errors of rspeak", S2),
    ("Internal results", S3),
    ("Recovery warnings and exit status", S4),
])
