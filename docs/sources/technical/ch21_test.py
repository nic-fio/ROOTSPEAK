from build import arrow, box, c, fig, note, p, risultati_prove, table, term, text, ul, warn, zone


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


LIVELLI = fig(
    box(330, 20, 240, 44, "live", "after install.sh, by the user", "grey", 12)
    + box(250, 72, 400, 44, "tests/vm", "VM with GNOME on Wayland, root, real dialogs", "navy", 12)
    + box(170, 124, 560, 44, "tests/container", "Debian 13 with systemd, root, real ssh sessions, nine users", "navy",
          12)
    + box(90, 176, 720, 44, "tests/engine.sh · tests/tui.py · tests/help-tui.py",
          "test mode, no root, temporary message store, virtual terminals", "blue", 12)
    + box(20, 228, 860, 44, "make prove · make analizza · make sanitizer · tests/fuzz",
          "internal parts, static analysis, AddressSanitizer and UBSan, libFuzzer", "dark", 12)
    + text(450, 300, "going up: closer to real use, slower; going down: faster, more repeatable", 11.5,
           "#475569", "600"),
    900, 318, "«FIG» — The levels of testing", "The tests")

S1 = p("Every statement about how AMS behaves comes from a run. The tests are organised in levels: at the bottom "
       "the internal parts and the engine, fast and without root; at the top the test machine and the VM, where AMS "
       "runs as root with real users, sessions and dialogs.", lead=True) + LIVELLI + \
    p("Test figures are never written by hand: each suite records its result together with the commit and the "
      "<b>fingerprint</b> of the code under test (" + c("tools/fingerprint.sh") + ": SHA-256 of " + c("src/") + ", "
      + c("po/") + ", " + c("Makefile") + ", " + c("etc/") + " and " + c("install.sh") + "), and this table reads "
      "them every time the manual is generated. “Valid for the current code” says whether the recorded fingerprint "
      "is that of the code this manual describes.") + risultati_prove() + \
    note("the container has no graphical session: the dialog scenario shows up there as “not tested” and is tested "
         "in the VM. The VM has no users with zsh, fish, ksh or dash: the shells are tested only in the container.")

S2 = p(c("tests/engine.sh") + " tests the engine in test mode, without root, on a fresh temporary message store for "
       "each case, with the programs in " + c("build/") + " (or in " + c("AMS_BUILD") + ", for example the sanitizer "
       "build). Every defect that gets fixed adds checks that fail without the fix.", lead=True) + \
    table(["Group", "Checks"], [
        ["1. confirmations", "normal confirmation; write impossible (the message stays, the user is warned, no "
         "temporary file, the question comes back and then succeeds); confirmation already present (the first one "
         "is kept); confirmation recorded but not moved"],
        ["2. delivery", "normal sending to two recipients; copy not writable for one of them (error, the other one "
         "receives it, «inviato, non consegnato» (“sent, not delivered”), incomplete-sending marker); fault fixed and recovery; simulated "
         "interruption halfway; recovery that does not bring back a confirmed message; unsaved sending cancelled; "
         "sending in progress (lock held) left alone, then completed without duplicates; sending just started not "
         "cancelled"],
        ["3. states", c("--level") + " rejected; delivered after sending; no level in the message; postponement "
         "shown as a detail and not asked again at once; confirmed at the next login; " + c("ams list")
         + " with the recipients in the three states and no invented state; expired shown as «consegnato, non "
         "confermato (scaduto)» (“delivered, not confirmed (expired)”)"],
        ["4. expiry", "the question stops if the message expires while it is open, no confirmation recorded; a "
         "confirmation timed after the expiry of the reference copy is not valid and is not counted"],
        ["5. configuration", "the file is not executed as code; valid values read, invalid, unknown, zero and "
         "negative values ignored; the message declares " + c("format: 1")],
        ["6. purge", c("ams purge 7d") + " deletes a message from 10 days ago with its copies and confirmations, "
         "keeps the recent one and incomplete or in-progress sendings, rejects an invalid duration"],
        ["7. agent", "PID written to " + c("ams-agent.pronto") + " when it is ready; the wake-up signal to that PID "
         "does not kill it; the file disappears on exit (only with a graphical session, otherwise skipped)"],
        ["8. language", "language chosen according to the gettext rules (9 cases, odd values included); user, "
         "administrator, errors and help in English and in Italian; confirmation channel translated"],
        ["9. second review", c("ams revoke") + " waits for a sending in progress; a confirmation later than the "
         "revocation is not valid, one in the same second is valid; copy removed while the user is answering; "
         "another user's terminal not written to; copy lost after an interruption rewritten by recovery; "
         "interrupted revocation and deletion completed; 5000 fake files in " + c("acks/") + " without slowdowns; "
         "a pipe in place of the confirmation; text over 65536 bytes rejected, of 65536 accepted; comments in "
         + c("ams.conf")],
        ["10. reminder", "a postponed question does not come back at once; " + c("ams remind") + " brings it back; "
         "those who have confirmed are not reminded; a revoked message cannot be reminded"],
    ], "«TAB» — The groups of tests/engine.sh") + \
    p("At the end " + c("tests/engine.sh") + " writes " + c("tests/results/engine.json") + " with date, commit, "
      "fingerprint and counts; " + c("tools/check-docs.py") + " fails if that fingerprint is not the one of the "
      "current code. " + c("tests/unit-tests.c") + " (" + c("make prove") + ") tests the internal parts one by one: "
      "text cleaning, languages, messages, configuration, event texts.")

S3 = p(c("tests/container/run.sh") + " tests AMS <b>for real</b> in an isolated test machine: a Debian 13 "
       "container with systemd running (logind, sshd), without root on the host system. AMS is installed there with "
       + c("install.sh") + "; the users are " + c("admin") + " (group sudo), " + c("mario") + " and " + c("anna")
       + " (group sviluppo), " + c("luca") + ", " + c("servizio") + " (without a shell) and four users with other "
       "shells: " + c("zeno") + " (zsh), " + c("fabio") + " (fish), " + c("kora") + " (ksh), " + c("dario")
       + " (dash). " + c("scenarios.py") + " runs as root, opens real ssh sessions with a terminal, answers the "
       "questions as a person would, measures the timings and records every result.", lead=True) + table(
    ["Area", "Scenarios"], [
        ["A. Access", "root sends; an administrator sends through sudo; an ordinary user cannot run "
         + c("ams") + ", not even the help"],
        ["B. Recipients", "user, list with duplicates, group, " + c("all") + " (root and nologin excluded), "
         + c("online") + ", non-existent user, empty group"],
        ["C. Delivery", "user logged out, then at login; user logged in (time to reach the terminal); ssh without a "
         "terminal; two sessions, confirmation in one stopping the other"],
        ["D. Confirmation", "postponement, reminder at the prompt, reminder by the administrator, question again at "
         "login, confirmation with its channel"],
        ["E. Expiry and revocation", "expired message not shown; revocation with the question pending; revocation "
         "before login"],
        ["F. Faults", "copy not writable and recovery; " + c("ams send") + " killed with SIGKILL halfway; user "
         "folder left owned by root; " + c("ams revoke") + " during a sending to many users; recovery concurrent "
         "with a sending in progress; confirmation not writable"],
        ["G. Security", "mailbox turned into a link to " + c("/etc") + "; escape sequences; forged "
         "confirmation; " + c("AMS_TEST") + " from an ordinary user"],
        ["J. Log", c("ams log") + " rebuilds the history; the confirmation carries the " + c("_UID") + " of whoever "
         "wrote it; a fake event written by a user is flagged"],
        ["T. TUI", c("ams") + " on its own as root: list with the recipients in the three states, detail and "
         "history, exit"],
        ["K. Shells", "zsh, fish, ksh and dash: question at login; text on sending; question at the prompt in zsh "
         "and fish, not in ksh and dash"],
        ["L. Language", "same message to a user in English and to one in Italian; question, confirmation, "
         + c("ams status") + " and " + c("ams log") + " in the reader's language"],
        ["H. Performance", "sending to everybody (about sixty users); " + c("list") + " with 10 messages; "
         + c("status")],
        ["I. Desktop", "not tested in the container (no graphical session); tested in the VM"],
    ], "«TAB» — The real-world scenarios") + \
    p(c("tests/vm/run.sh") + " runs the same scenarios in a <b>virtual machine with a desktop</b>, on the test "
      "server (QEMU with KVM, without root or libvirt), plus the dialog scenarios. The VM is Debian 13 with GNOME on "
      "Wayland; " + c("sara") + " logs into the desktop automatically. Each run starts from a clean copy of a base "
      "disk prepared once (" + c("prepare.sh") + ", cloud-init). The dialog buttons are pressed through GNOME "
      "accessibility (" + c("desktop.py") + ", AT-SPI), as a person would, and the screenshots come from the QEMU "
      "monitor (" + c("capture.py") + ").") + table(
    ["Scenario", "Result and measurement (last recorded run)"], [
        ["I1 · the dialog appears after sending, in the session's language", "0.58 s"],
        ["I2 · «Ho letto» (“I have read it”) closes the dialog and records the confirmation (desktop)", "passed"],
        ["I3, I4 · «Più tardi» (“Later”), then the dialog comes back (test postponement: 1 minute)",
         "comes back after 60.23 s"],
        ["I11 · " + c("ams remind") + " after «Più tardi» (“Later”): the dialog comes back at once", "0.37 s"],
        ["I5 · confirmation from a terminal with the dialog open", "the dialog closes in 0.65 s"],
        ["I6 · revocation with the dialog open", "the dialog closes in 0.67 s"],
        ["I7 · two messages, one dialog after the other, oldest first", "passed"],
        ["I8 · agent not running: " + c("ams send") + " starts it", "dialog in 0.53 s"],
        ["I9 · message while the desktop is closed, then graphical login", "dialog 2.64 s after the login restarts"],
        ["I10 · «Ho letto» (“I have read it”) and logout from the session after 0.1 s", "confirmation recorded"],
    ], "«TAB» — The desktop scenarios in the VM") + ul([
    "The test desktop is in Italian; " + c("AMS_PROVA_LINGUA=en") + " switches it to English, "
    + c("AMS_PROVA_SOLO=i_desktop") + " runs only the desktop scenarios.",
    "Each run writes " + c("results.json") + " and " + c("report.md") + " to " + c("tests/container/results/")
    + " and " + c("tests/vm/results/") + ", with the measurements of every scenario.",
])

S4 = p("The two full-screen interfaces are tested on a pseudo-terminal, pressing keys as a person would and checking "
       "the last screen drawn after each one.", lead=True) + table(["Test", "Check"], [
    ["opening", "list with bar and sentence, correct size; no invented state"],
    [c("Invio") + " (Enter), " + c("Tab"), "detail with the recipients and the state from " + c("ams status") + "; history "
     "from the log"],
    [c("n") + ", " + c("Ctrl+E") + ", " + c("Ctrl+S"), "form, preview of the recipients, text on two lines; the "
     "text goes through the editor and comes back; confirmation with recipients, title and expiry; sending result "
     "in a single dialog; the message is in the message store and at the top of the list"],
    [c("s") + ", " + c("r"), "reminder carried out; confirmation before revoking, revocation cancelled with "
     + c("n") + ", then carried out: «[ritirato]» (“[revoked]”) in the list and in the message store"],
    [c("/"), "the search shows only the messages containing the text"],
    ["80 × 24", "bar and “confirmed/total” instead of the sentence"],
    [c("q"), "clean exit"],
    ["60 × 15, pipe", "no TUI: the help"],
], "«TAB» — The tests of tests/tui.py") + table(["Test", "Check"], [
    ["opening at 100 × 30", "alternate screen, frame, Info tab"],
    [c("→"), "Comandi (Commands) tab"],
    [c("3"), "Opzioni (Options) tab"],
    [c("4") + " " + c("G"), "end of the Esempi (Examples) tab"],
    [c("PgUp") + " " + c("g"), "start of the tab"],
    ["resize to 70 × 20", "20 lines of 70 columns"],
    [c("q"), "back to the main screen, exit with code 0"],
    ["terminal 40 × 8", "manual-style page through the pager"],
], "«TAB» — The tests of tests/help-tui.py") + \
    p(c("tools/tui-screenshots.sh") + " uses the test machine to capture the real TUI screens shown in "
      + cap(14) + ": the colours are the ones the administrator sees.")

S5 = table(["Check", "Fails if"], [
    ["manuals up to date", "the two manuals in " + c("docs/") + " differ from the ones regenerated from the sources"],
    ["reference", "a command or option entry of the built-in help is missing from the user manual, has a different "
     "description from the English source text extracted from src/guida.c, or the manual documents one that does "
     "not exist"],
    ["file map", "a code file does not appear in the map in " + cap(3, 1) + ", or the map lists one that does not "
     "exist"],
    ["version", c("AMS_VERSION") + " does not appear in both manuals"],
    ["links", "a " + c("#ancora") + " link does not lead to any id"],
    ["languages", "a " + c("po/*.po") + " catalog does not pass " + c("msgfmt --check") + ", has translations to "
     "review, or lacks texts present in the code (extracted again with " + c("xgettext") + ")"],
    ["tests", "the last run of " + c("tests/engine.sh") + " does not have the fingerprint of the current code, or "
     "has failed checks"],
], "«TAB» — The checks of tools/check-docs.py") + \
    p(c("tools/check-docs.py") + " is the last step before recording a change (" + cap(3, 5) + "): if it passes, "
      "it prints «documentazione allineata» (“documentation aligned”) with the number of help entries, the number "
      "of files in the map, the version and the languages.")

S6 = p("Before the rewrite in C, the 0.1.0 prototype was also tested <b>live</b> on Debian 13 with GNOME 48 on "
       "Wayland, with two accounts. The C version has not yet been tested live on the user's PC: its tests are "
       "those of the suites.", lead=True) + table(["Tested (0.1.0 prototype)", "How"], [
    ["immediate dialog for a logged-in user", "live"],
    ["dialog at login for a user who was not logged in", "live, with a second account"],
    ["text and question in the terminal, also over ssh", "live, with " + c("ssh user@localhost")],
    ["single confirmation across dialog and terminal", "live"],
    [c("list") + ", " + c("status"), "live"],
    [c("revoke") + " with a pending question, expiries, errors, text cleaning", "in test mode"],
], "«TAB» — The live tests") + \
    warn("live tests as root are run by whoever has the root password, after " + c("./install.sh") + "; in tests "
         "run by those working on the code, test mode must always be set (" + cap(4, 4) + ").")

S7 = p("A root program in C that reads user data must have no memory errors. Besides the behaviour tests, "
       "version 0.2.0 has these defences, to be run again whenever the code that reads data changes.",
       lead=True) + table(["Defence", "How it is run", "What it found"], [
    ["all gcc warnings as errors, and the compiler hardening (" + cap(17, 3) + ")", c("make"),
     "nothing to fix: the code was written that way from the start"],
    ["tests of the internal parts (" + c("tests/unit-tests.c") + ")", c("make prove"), "—"],
    ["AddressSanitizer and UBSan on all the engine and help tests, with reports written to files (none allowed)",
     c("make sanitizer") + ", then " + c("AMS_BUILD=build-san tests/engine.sh"), "no memory errors"],
    ["gcc static analysis", c("make analizza"), "pipes not closed in an error path of " + c("come_utente")
     + " (fixed); 3 false alarms remain about the copies of the standard descriptors in a child that exits at once"],
    ["fuzzing with libFuzzer, in a container with clang, of: text cleaning, message format, output of the mailbox "
     "reading, process environment, configuration, " + c(".mo") + " catalogs",
     c("tests/fuzz/run.sh SECONDI") + " (SECONDI: “SECONDS”)", "a function that assumed an already zeroed structure (fixed); then "
     "30 minutes without defects"],
    ["comparison with the prototype: text cleaning in C and in bash on 2000 random texts", "(before removing the "
     "prototype)", "identical results"],
], "«TAB» — The defences of the C code") + \
    note("the results of static analysis, sanitizers and fuzzing have no results file with the fingerprint: they "
         "are those of the last run made at the time of the rewrite (30 September 2026).")

CHAPTER = ("Tests and checks", [
    ("The tests and their results", S1),
    ("The engine: tests/engine.sh", S2),
    ("For real: the test machine and the VM", S3),
    ("The interfaces: tests/tui.py and tests/help-tui.py", S4),
    ("The documentation: tools/check-docs.py", S5),
    ("Live tests", S6),
    ("The defences of the C code", S7),
])
