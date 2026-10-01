from build import arrow, box, c, fig, note, p, table, text, ul, zone


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


TRUST = fig(
    zone(20, 44, 270, 220, "Trusted: administrators")
    + box(44, 84, 222, 56, "rspeak (root)", "sudo, admin group, 750", "navy")
    + box(44, 158, 222, 56, "sent/ · rootspeak.conf · .mo", "only root writes", "dark")
    + zone(330, 44, 240, 220, "Boundary")
    + box(352, 84, 196, 56, "come_utente", "child with U's identity", "green")
    + box(352, 158, 196, 56, "pulisci, limits", "texts, 200 bytes, times", "green")
    + zone(610, 44, 270, 220, "Untrusted: users")
    + box(634, 84, 222, 56, "users/U/", "mailbox: U can do anything", "amber")
    + box(634, 158, 222, 56, "acks/ID · environ", "written by the user", "amber")
    + arrow(268, 112, 350, 112) + arrow(550, 112, 632, 112)
    + arrow(632, 186, 550, 186, "#d97706") + arrow(350, 186, 268, 186, "#d97706")
    + text(450, 238, "everything that crosses", 11.5, "#166534", "700") + text(450, 254, "the boundary goes through here", 11.5, "#166534", "700"),
    900, 282, "«FIG» — The RootSpeak trust model", "Who is trusted")

S1 = p("Administrators are trusted: they can already do anything on the machine, and RootSpeak does not protect them from "
       "themselves. Users are <b>not</b> trusted: they control their own mailbox, their own terminals, the environment "
       "of their own processes, and they can write to the journal. Everything that goes from root to a user, or comes "
       "back from a user to root, crosses a controlled boundary.", lead=True) + TRUST + table(["Direction", "What crosses", "Control"], [
    ["root → mailbox", "copies, revocations, reminders, deletions", "always as the user, with a time limit ("
     + cap(7) + ")"],
    ["root → terminal", "the message text", "cleaned; owner of the opened terminal; 3 s at most ("
     + cap(8, 4) + ")"],
    ["root → agent", c("SIGUSR1"), "from a child running as the user, only to the ready PID with the exact command line"],
    ["mailbox → root", "confirmations and postponement dates", "read as the user, 200 bytes, regular files only, cleaned ("
     + cap(10, 2) + ")"],
    ["process → root", "the environment for the language", "at most 1 MiB; valid language codes only ("
     + cap(16, 2) + ")"],
    ["journal → root", "events with the " + c("RSPEAK_*") + " fields", c("_UID") + " compared with who was supposed to "
     "write them; states never taken from the journal (" + cap(18, 4) + ")"],
], "«TAB» — The boundary, direction by direction")

S2 = table(["Risk", "Countermeasure", "Test"], [
    ["an ordinary user runs " + c("rspeak"), "permissions " + c("750 root:gruppo admin") + " (gruppo admin: “admin "
     "group”); re-launch with sudo, which "
     "applies its own rules", "scenarios A3, A4"],
    [c("RSPEAK_TEST") + " used to bypass sudo", "it grants nothing: without root a user keeps their own permissions; "
     "the test variables apply only in test mode", "scenario G4"],
    ["symbolic links in the mailbox", "every access by root to the mailboxes happens in a child with the user's "
     "identity, with a time limit", "scenario G1"],
    ["abnormal mailboxes (pipes, thousands of files) against root's commands", "only regular files and only "
     "existing messages are read, with a time limit", c("engine.sh") + ", group 9"],
    ["escape sequences in messages", c("pulisci") + " on text and title; " + c("--no-markup") + " in zenity",
     "scenario G2"],
    ["forged confirmations", "read as the user, at most 200 bytes, cleaned; a confirmation remains a statement "
     "by the user, not a proof", "scenario G3"],
    ["fake events in the journal", "the journal adds " + c("_UID") + "; " + c("rspeak log") + " flags as «non "
     "attendibile» (“not trustworthy”) an event written by the wrong user; states are read from the message store", "scenario J3"],
    ["text meant for one user written to another user's terminal", "the owner of the terminal is checked "
     "after opening it, not the name " + c("/dev/pts/N"), c("engine.sh") + ", group 9"],
    ["signals to the wrong processes", "the signal is sent from a child with the user's identity, and only to the "
     "ready PID with the agent's exact command line", c("engine.sh") + ", group 7"],
    ["a stuck terminal halts sending", "non-blocking write, at most 3 s per terminal", "—"],
    ["a user stops root's child (" + c("SIGSTOP") + ")", "time limit even after the output has ended, then "
     + c("SIGKILL"), "—"],
    ["configuration as code", c("rootspeak.conf") + " is a data file: two keys, positive integers", c("engine.sh")
     + ", group 5"],
    ["an editor opened as root from the TUI", "the editor runs with the identity of the administrator in "
     + c("SUDO_USER"), "—"],
    ["text too long for the dialog", "at most 65536 bytes: zenity receives the text as an argument, and Linux does "
     "not accept arguments over 128 KiB", c("engine.sh") + ", group 9"],
    ["messages read by other users", "mailboxes " + c("700") + "; root's " + c("sent/") + " " + c("700"), "—"],
    ["memory errors in a root program", "compiler hardening, static analysis, sanitizers, "
     "fuzzing (" + cap(17, 3) + ")", cap(21, 7)],
], "«TAB» — Risks and countermeasures") + \
    note("outside the model: a symbolic link " + c("/var/lib/rootspeak") + " created before installation. "
         "Only root writes in " + c("/var/lib") + ", and root is already trusted (second review, finding not accepted).")

S3 = p("A root program in C that reads user data must not have memory errors. Besides the coding rules "
       "(" + c("buf_t") + " for every text that comes from outside, no variable-length arrays, "
       + c("O_CLOEXEC") + " everywhere), the code is compiled with the hardening that gcc and the linker offer.", lead=True) + \
    table(["Option", "What it does"], [
        [c("-Wall -Wextra -Wpedantic … -Werror"), "all the useful warnings, as errors: among others formats ("
         + c("-Wformat=2") + ", " + c("-Wformat-security") + "), shadowed names (" + c("-Wshadow")
         + "), null pointers (" + c("-Wnull-dereference") + "), variable-length arrays (" + c("-Wvla") + ")"],
        [c("-D_FORTIFY_SOURCE=3"), "size checks in library functions (copies, formats)"],
        [c("-fstack-protector-strong"), "a stack canary in functions with arrays or addresses of local "
         "variables"],
        [c("-fstack-clash-protection"), "the stack cannot jump past the guard page"],
        [c("-fcf-protection"), "control-flow protection (where the processor provides it)"],
        [c("-fPIE -pie"), "position-independent executable at random addresses"],
        [c("-z relro -z now"), "linkage tables read-only after startup"],
        [c("-z noexecstack"), "non-executable stack"],
        [c("-fanalyzer") + " (" + c("make analizza") + ")", "gcc static analysis: error paths, descriptors "
         "not closed, use after free"],
        [c("-fsanitize=address,undefined") + " (" + c("make sanitizer") + ")", "AddressSanitizer and UBSan in the "
         "tests: any out-of-bounds access or undefined behaviour stops the test"],
    ], "«TAB» — Compiler hardening (Makefile)") + ul([
    "Fuzzing with libFuzzer (" + c("tests/fuzz/") + ") exercises, with AddressSanitizer and UBSan, everything that reads "
    "untrusted data: text cleaning, message format, the output of mailbox reading, a process's environment, "
    "configuration, " + c(".mo") + " catalogs.",
    "The choice of C, rather than a language that avoids memory errors by construction, is the owner's: the "
    "hardening in this table is the condition under which it was made (" + cap(22, 3) + ").",
])

CHAPTER = ("Security", [
    ("The trust model", S1),
    ("Risks and countermeasures", S2),
    ("Compiler hardening", S3),
])
