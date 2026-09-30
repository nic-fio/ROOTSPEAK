from build import arrow, box, c, fig, note, p, table, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


TEMPI = fig(
    '<line x1="40" y1="120" x2="860" y2="120" stroke="#94a3b8" stroke-width="3"/>'
    + box(30, 40, 150, 54, "29/9 evening", "bash prototype", "dark", 12)
    + box(195, 40, 150, 54, "29/9 night", "live tests, 0.1.0", "dark", 12)
    + box(360, 40, 160, 54, "30/9 morning", "reviews A and B", "amber", 12)
    + box(535, 40, 160, 54, "30/9 afternoon", "reviews C and D; C", "amber", 12)
    + box(710, 40, 160, 54, "30/9 evening", "TUI, reminder", "navy", 12)
    + arrow(105, 96, 105, 114, "#94a3b8") + arrow(270, 96, 270, 114, "#94a3b8") + arrow(440, 96, 440, 114, "#94a3b8")
    + arrow(615, 96, 615, 114, "#94a3b8") + arrow(790, 96, 790, 114, "#94a3b8")
    + text(270, 150, "double confirmation, slow dialog", 11, "#475569")
    + text(440, 168, "specification, three states, suites", 11, "#475569")
    + text(615, 150, "revocation, power loss; 0.2.0 in C", 11, "#475569")
    + text(790, 168, "invented states removed", 11, "#475569"),
    900, 186, "«FIG» — The milestones of the project and what each one changed", "History in brief")

S1 = p("The project went through two external critical reviews, carried out by language models on the technical "
       "manual, without the code. Every finding was verified on the code or with a test before being accepted; the "
       "point-by-point detail is in " + c("docs/revisione-avversariale.md") + ".", lead=True) + \
    TEMPI + table(["Review", "On what", "What came out of it"], [
        ["first (A and B), on version 0.1.0", "real defects, specification, robustness, tests", "confirmations never "
         "silently lost; verified delivery with recovery; three states for every message, without levels; "
         "structured events and " + c("ams log") + "; " + c("ams purge") + "; configuration as data; the "
         "“Specification” chapter; the real-world suites in the container and in the VM"],
        ["second (C and D), on the manual with the covering note", "races, durability, boundaries", "revocation "
         "serialised with sending; confirmations later than the revocation not valid; terminal checked after "
         "opening; durability after a power loss; deletion in a single step; anomalous mailboxes; texts over 65536 "
         "bytes rejected; test figures tied to the code fingerprint; “supported” distinguished from “verified”; "
         "linearisation points"],
    ], "«TAB» — The two reviews") + ul([
    "Criticisms not accepted, with the reason: “the confirmation does not prove reading” (intended: never block, "
    + cap(20, 1) + "); “if the terminal is blocked the message does not arrive” (inaccurate: the mailbox acts as a "
    "queue); “rewrite in a compiled language right away” (the specification first; the rewrite came later); " + c("ams")
    + " always as root (the user's decision); a pipe in place of " + c("acks/ID") + " blocking " + c("ams status")
    + " and an end-of-line comment in " + c("ams.conf") + " (inaccurate, tested); a " + c("/var/lib/ams")
    + " prepared before installation (outside the model).",
    "A criticism rejected by mistake and then accepted: locks left stuck. The kernel releases the lock when the "
    "process dies, but the test VM showed that the agent's lock was inherited by its children.",
])

S2 = table(["Defect", "Found by", "Fix", "Where"], [
    ["an unwritable confirmation was treated as “already confirmed”: the message disappeared without a confirmation",
     "review A", "publication with an exclusive " + c("link") + "; exit status 1, the message stays", cap(13, 1)],
    ["an interrupted " + c("ams send") + " left recipients without a copy, never recovered", "review A",
     "delivery verified and recorded; " + c("incomplete") + "; recovery", cap(8, 6)],
    ["an agent woken up while starting died (20 out of 20)", "review A, test", "handler for " + c("SIGUSR1")
     + " as the first instruction; " + c("ams-agent.pronto"), cap(12, 2)],
    ["open dialogs and questions accepted the confirmation after the expiry", "review A", "they close at the "
     "expiry; confirmation rejected; date compared with " + c("sent/"), cap(20, 7)],
    ["recovery, during a long sending, delivered in parallel and recorded duplicates", "container, F3 and F5",
     c("sent/ID/lock") + " held for the whole delivery", cap(8, 6)],
    [c("online") + " included root and logged-in system accounts", "VM, B5", "filter for human users",
     cap(6, 2)],
    ["the agent's lock was inherited by its children: an orphaned dialog blocked the new agent", "VM",
     c("O_CLOEXEC") + " (in the prototype, closing the descriptor)", cap(12, 1)],
    ["logging out of the session right after «Ho letto» (“I have read it”) could lose the confirmation", "VM, I10", "signals blocked "
     "outside the waits; the dialog is waited for 2 s", cap(12, 3)],
    ["the wake-up interrupted the wait for the dialog and recorded a postponement never chosen", "VM, I7", "the "
     "wake-up does not close the dialog", cap(12, 3)],
    ["a dialog closed by the system counted as a postponement", "VM", "postponement only with zenity exit status 1",
     cap(12, 3)],
    ["a reminder within one second of «Più tardi» (“Later”) was lost", "VM, I11", "the answer is recorded as soon as "
     "zenity closes (" + c("SIGCHLD") + ")", cap(12, 3)],
    [c("ams revoke") + " did not wait for a sending in progress", "review C", "revocation on disk, then the lock",
     cap(9, 1)],
    ["a confirmation could come into being after the revocation", "review C", "no confirmation without a copy; date "
     "compared with the revocation", cap(13, 1)],
    ["the text could end up on another user's terminal", "review C", "owner of the opened terminal",
     cap(8, 4)],
    ["no guarantee after a power loss", "review C", c("fsync") + ", " + c("syncfs")
     + ", recorded copies checked again", cap(20, 6)],
    [c("ams purge") + " together with " + c("ams list") + ": a message disappeared halfway through reading",
     "review D", "rename to " + c(".cancella-ID") + "; read before use", cap(9, 3)],
    ["5000 fake files in " + c("acks/") + ": " + c("ams list") + " took 3.9 s", "review D", "only the messages in "
     + c("sent/") + ", with a time limit", cap(10, 2)],
    ["texts over 128 KiB did not reach the dialog", "review D", "limit of 65536 bytes on sending", cap(8, 1)],
    ["the TUI's sending child never saw the end of the text", c("tests/tui.py"), "it closes the pipe end it does "
     "not use", cap(14, 4)],
    ["pipes not closed in an error path of " + c("come_utente"), c("-fanalyzer"), "closed", cap(7, 3)],
    ["a function assumed an already zeroed structure", "fuzzing", "fixed", cap(21, 7)],
    ["states invented in the TUI and in the specification («in attesa», «completo», «invio incompleto», «annullato»: "
     "“pending”, “complete”, “incomplete sending”, “cancelled”)", "the user, on the previews", "only the three states; summary with the counts", cap(20, 3)],
], "«TAB» — The defects found and fixed") + \
    p("The live tests of the prototype also gave rise to three rules: the first confirmation counts for all "
      "channels (one had to confirm twice), waking the agent with a signal (the dialog arrived after 3-4 seconds) "
      "and the command in " + c("/usr/local/bin") + " instead of " + c("sbin") + " (on Debian " + c("sbin")
      + " is not in the PATH of non-root users).")

S3 = p("Version 0.2.0 is a complete rewrite in C of the bash prototype, decided by the user after the second "
       "review: the defects found almost all stemmed from bash (races between check and use, time limits, one "
       "process per operation). A language that avoids memory errors by construction had been proposed; the user "
       "chose C, with mandatory defences.", lead=True) + table(["In the prototype (bash)", "In the "
                                                               "C version"], [
    [c("runuser -u U -- …") + " for every access to a mailbox", c("come_utente") + ": a child with the identity of "
     "U and a time limit; a mailbox is read in a single child (" + cap(7) + ")"],
    [c("set -C") + ", then " + c("ln") + " for the confirmation", c("open(O_EXCL)") + ", " + c("fsync") + ", "
     + c("link") + " (" + cap(13, 1) + ")"],
    [c("pkill -F") + " for the wake-up", c("op_sveglia") + ": ready PID, exact command line, " + c("kill")
     + " as the user (" + cap(8, 5) + ")"],
    [c("sed") + " and " + c("tr") + " for text cleaning", c("pulisci") + ", with the same result on 2000 "
     "random texts (" + cap(8, 7) + ")"],
    ["configuration read with " + c("source"), "data file, two keys (" + cap(4, 5) + ")"],
    ["language texts in shell files", "gettext catalogs read by AMS (" + cap(16, 3) + ")"],
    [c("wait") + " interrupted by the wake-up", c("ppoll") + " with signals blocked outside the waits ("
     + cap(12, 2) + ")"],
], "«TAB» — From bash to C") + \
    note("the bash prototype was removed when the C version passed all the tests; it remains in the repository "
         "history. The shell hooks remain scripts, and the dialog remains zenity.")

CHAPTER = ("Defects found and reviews", [
    ("The two external reviews", S1),
    ("The defects found and fixed", S2),
    ("From bash to C", S3),
])
