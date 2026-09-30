from build import arrow, box, c, code, diamond, fig, flow, note, p, path, seq, table, term, text, ul, warn


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


S1 = p(c("cmd_send") + " in " + c("src/ams.c") + " checks everything it can check <b>before</b> "
       "writing to the message store: options, text, expiry, recipients. An error at this stage ends with "
       + c("die") + " and leaves nothing behind.", lead=True) + table(["Option", "Value", "Check"], [
    [c("--to DEST"), "recipients separated by commas", "mandatory («manca --to»); resolved after the text ("
     + cap(6, 1) + ")"],
    [c("--title TITOLO"), "one line", "cleaned like the text; newlines and tabs become spaces"],
    [c("--expires DURATA"), c("30m") + ", " + c("2h") + ", " + c("3d") + " or a date", "computed at once; it must "
     "be in the future («la scadenza è già passata»)"],
    [c("--file FILE"), "the text from a file", "read up to 64 MiB; it counts only if there is no text on the command "
     "line"],
    [c("--"), "—", "end of options: whatever follows is text even if it starts with " + c("-")],
], "«TAB» — The options of ams send") + ul([
    "Options end at the first argument that is not an option: from there on the arguments, joined by a "
    "space, are the text. Without text and without " + c("--file") + " the text is read from stdin (at most 64 MiB).",
    "An unknown option («opzione sconosciuta: --level») or one without a value («manca il valore di --to») ends "
    "at once. " + c("--level") + " belonged to version 0.1.0 and is rejected (" + c("tests/engine.sh")
    + ", group 3).",
    "A duration is a number followed by " + c("m") + ", " + c("h") + " or " + c("d") + "; everything else is "
    "interpreted by " + c("date -d … +%s") + " in a child process (for example " + c("\"2026-10-04 12:00\"") + "). "
    "Dates in words are those understood by " + c("date") + ", in English.",
    "Trailing newlines are removed from the text, which is then cleaned (" + cap(8, 7) + "). A text made only of "
    "spaces is «messaggio vuoto»; beyond 65536 bytes, after cleaning, it is «messaggio troppo lungo»: the desktop "
    "dialog receives the text as an argument to zenity, and Linux does not accept an argument larger than 128 KiB.",
])

INVIO = fig(
    box(20, 40, 150, 56, "prepara_archivio", "var, users, sent", "dark", 12)
    + box(190, 40, 130, 56, "prossimo_id", "flock su .seq.lock", "dark", 12)
    + box(340, 40, 130, 56, "lock + marker", "lock, incomplete", "navy", 12)
    + box(490, 40, 180, 56, "msg, recipients", "scrivi_atomico, sync", "navy", 12)
    + box(690, 40, 190, 56, "for each recipient", "in alphabetical order", "blue", 12)
    + diamond(785, 150, 170, 60, "revoked?", "amber")
    + box(560, 204, 170, 56, "consegna_copia", "as U, verified", "blue", 12)
    + box(370, 204, 170, 56, "terminals", "text, at most 3 s each", "blue", 12)
    + box(180, 204, 170, 56, "sveglia_agente", "SIGUSR1 o systemd-run", "blue", 12)
    + box(20, 204, 140, 56, "delivery", "user date n", "green", 12)
    + box(20, 300, 250, 56, "INVIATO event", "list of recipients, author", "soft", 12)
    + diamond(420, 328, 180, 60, "missing copies?", "amber")
    + box(560, 300, 150, 56, "die, exit 1", "incomplete stays", "grey", 12)
    + box(730, 300, 150, 56, "syncfs, sync", "incomplete removed", "green", 12)
    + arrow(172, 68, 188, 68) + arrow(322, 68, 338, 68) + arrow(472, 68, 488, 68) + arrow(672, 68, 688, 68)
    + arrow(785, 98, 785, 118)
    + path([(700, 150), (645, 150), (645, 202)], "#0050C0", False, "no", 672, 142)
    + arrow(558, 232, 542, 232) + arrow(368, 232, 352, 232) + arrow(178, 232, 162, 232)
    + path([(870, 150), (890, 150), (890, 286), (282, 286), (282, 312), (274, 312)], "#b45309", True,
           "yes: stops", 840, 236)
    + arrow(145, 262, 145, 298) + arrow(272, 328, 328, 328)
    + arrow(512, 328, 558, 328, "#475569", False, "yes", 535, 318)
    + path([(420, 360), (420, 372), (805, 372), (805, 358)], "#16a34a", False, "no", 610, 366),
    900, 390, "«FIG» — The sequence of ams send", "A send, step by step")

S2 = p("After the checks, sending is a fixed sequence. The order is chosen so that every interruption leaves a "
       "state that the next command can recognise and repair.", lead=True) + INVIO + table(["Step", "What",
                                                                                               "Why here"], [
    ["1", c("prepara_archivio") + ": creates " + c("/var/lib/ams") + ", " + c("users/") + " (" + c("755") + ") and "
     + c("sent/") + " (" + c("700") + ") if missing", "AMS also works without " + c("install.sh")
     + " (test mode)"],
    ["2", c("prossimo_id") + ": the number and the folder " + c("sent/ID/"), "under flock: unique numbers ("
     + cap(5, 3) + ")"],
    ["3", c("sent/ID/lock") + " taken exclusively, then the marker " + c("incomplete"), "from here on recovery, "
     "revocation and deletion know that a send is in progress"],
    ["4", c("msg") + " and " + c("recipients") + " with " + c("scrivi_atomico") + "; " + c("fsync") + " of "
     + c("incomplete") + ", of " + c("sent/ID/") + " and of " + c("sent/"), "message, recipients and marker on disk "
     "before any delivery"],
    ["5", "for each recipient: if " + c("revoked") + " exists, stop; otherwise copy, terminals, wake-up, "
     "line in " + c("delivery") + ", event " + c("CONSEGNATO"), "a revocation stops the send at the next recipient"],
    ["6", "event " + c("INVIATO") + " with the list of recipients and the author", "after the deliveries: in the log "
     "the send appears last"],
    ["7a", "missing copies: «Messaggio N consegnato a X destinatari su Y.», then " + c("die") + " with the names",
     c("incomplete") + " stays; the lock is released on exit; the next command retries"],
    ["7b", "everything delivered: " + c("syncfs") + " of " + c("users/") + ", " + c("fsync") + " of " + c("sent/ID/")
     + ", " + c("incomplete") + " removed, " + c("fsync") + " again", "when the marker disappears, copies and "
     "deliveries are on disk"],
], "«TAB» — The steps of sending") + term(
    "admin@server:~$ sudo ams send --to @sviluppo --title Manutenzione --expires 2d \"Sabato dalle 8 alle 12 il server sarà spento.\"\n"
    "Messaggio 12 inviato a 2 utenti.", "A successful send")

CONS = fig(
    box(20, 70, 170, 56, "prepara_casella", "root: users/U 700, lchown", "navy", 12)
    + box(230, 70, 150, 56, "come_utente", "20 s", "dark", 12)
    + diamond(480, 98, 150, 64, "already read?", "amber")
    + box(580, 20, 150, 50, "result 0", "nothing to write", "green", 12)
    + box(580, 120, 150, 56, "inbox/ID.tmp", "O_EXCL, O_NOFOLLOW", "blue", 12)
    + box(750, 120, 130, 56, "rename, stat", "regular, not empty", "blue", 12)
    + box(750, 20, 130, 50, "delivery", "only if result 0", "green", 12)
    + arrow(192, 98, 228, 98) + arrow(382, 98, 403, 98)
    + path([(480, 66), (480, 45), (578, 45)], "#16a34a", False, "yes", 500, 38)
    + path([(557, 98), (570, 98), (570, 148), (578, 148)], "#0050C0", False, "no", 590, 106)
    + arrow(732, 148, 748, 148) + arrow(815, 118, 815, 72, "#16a34a") + arrow(732, 45, 748, 45, "#16a34a"),
    900, 196, "«FIG» — consegna_copia: the copy is written as the user and verified", "Verified delivery")

S3 = p("«Delivered» means that the copy <b>was</b> in the mailbox, verified, at the time of delivery. "
       + c("consegna_copia") + " in " + c("src/archivio.c") + " writes and checks in the same child process; "
       "only if it succeeds does " + c("ams send") + " record the line in " + c("delivery") + ".", lead=True) + CONS + ul([
    "Root prepares only " + c("users/U") + " (" + cap(7, 1) + "); the subfolders and the copy are written by the "
    "child with U's identity.",
    "If the message is already in " + c("read/") + " or " + c("acks/") + " the copy is not rewritten: recovery does "
    "not present again to a user a message already read or confirmed (" + c("tests/engine.sh") + ", group 2).",
    "The copy is born as " + c("inbox/ID.tmp") + " and becomes " + c("inbox/ID") + " through a rename: "
    + c("ams-user") + ", which lists only names made of digits, never sees a half-written file.",
    "A failure for one recipient (mailbox not writable, link to " + c("/etc") + ", timeout) does not "
    "stop the others: the event " + c("NON_CONSEGNATO") + " goes to the log and sending continues (scenario F1).",
])

S4 = p("For each terminal from " + c("terminali_utente") + " (" + cap(6, 3) + "), " + c("ams send") + " writes the "
       "formatted text in the language of whoever uses <b>that</b> terminal. Writing to the terminal does not count "
       "as confirmation: the question comes at the next prompt.", lead=True) + term(
    "\n── AMS · Messaggio dall'amministratore · Manutenzione · 30/09 16:55 ──\n"
    "Sabato dalle 8 alle 12 il server sarà spento.\n"
    "────────────────────────────────────────", "The text written to the terminal of an Italian-speaking user") + \
    table(["Step", "What", "Why"], [
        [c("lingua_terminale"), "looks in " + c("/proc") + " for the first process with that terminal (usually the "
         "shell) and reads its environment; if root cannot (a container without " + c("CAP_SYS_PTRACE") + "), the "
         "user reads it in a child", "everyone reads in their own language (" + cap(16, 1) + "); with no processes, "
         "the system language"],
        [c("testo_terminale"), "header with title and date, text, closing line; every " + c("\\n")
         + " becomes " + c("\\r\\n"), "the terminal may be in raw mode, for example inside an editor"],
        [c("scrivi_terminale"), "opens with " + c("O_WRONLY|O_NOCTTY|O_NONBLOCK") + "; " + c("fstat")
         + " of the <b>opened</b> terminal: a character device whose owner is the recipient",
         "between the search and the open, " + c("/dev/pts/N") + " may pass to another user"],
        ["writing", "in pieces, with a " + c("poll") + " of 100 ms between attempts, for at most 3 seconds",
         "a blocked terminal (Ctrl+S, slow network) does not stop the send"],
        ["count", "the terminals written in full end up in the " + c("delivery") + " line", "«scritto su 2 "
         "terminali» in " + c("ams status")],
    ], "«TAB» — Writing to the terminals") + \
    note("in test mode the only «terminal» is the file " + c("AMS_TEST_TTY") + ", and the check on the file type "
         "is skipped; the one on the owner remains: " + c("tests/engine.sh") + " (group 9) checks that "
         + c("/dev/null") + ", owned by root, is not written to.")

WAKE = seq([("ams send", "root", "navy"), ("child as U", "5 s", "dark"), ("U's agent", "ppoll", "blue"),
            ("systemd --user", "of U", "soft")], [
    ("nota", 0, "sessione_grafica(U)?"),
    (0, 1, "come_utente(op_sveglia)"),
    ("nota", 1, "PID in ams-agent.pronto"),
    ("nota", 1, "cmdline = …/ams-user agent?"),
    (1, 2, "kill(PID, SIGUSR1)"),
    ("nota", 2, "wait is interrupted".ljust(22)),
    ("sep", "no ready agent".ljust(20)),
    (0, 3, "systemd-run --user --machine=U@.host"),
    (3, 2, "starts ams-user agent", True),
], "«FIG» — Waking the desktop agent, or starting it", "Wake-up or start")

S5 = p("After the copy, " + c("sveglia_agente") + " makes the dialog appear on the desktop at once, without waiting "
       "for the agent's periodic check. If the user has no graphical session (or in test mode) it does "
       "nothing.", lead=True) + WAKE + ul([
    "The signal goes only to a <b>ready</b> agent: the PID written in " + c("/run/user/UID/ams-agent.pronto")
    + " (at most 64 bytes, without following links), which the agent writes after it has prepared to receive the "
    "signal (" + cap(12, 2) + ").",
    "The signal is sent from a child <b>with U's identity</b>, and only if " + c("/proc/PID/cmdline") + " is "
    "<b>exactly</b> " + c("LIBDIR/ams-user") + " followed by " + c("agent") + ": it cannot reach other users' "
    "processes, nor a process of U that had inherited an old PID.",
    "If there is no ready agent, " + c("systemd-run --user --machine=U@.host --collect --quiet") + " starts one "
    "in the systemd user manager, which already knows the graphical environment of the session. If an agent was "
    "starting, the new one finds the lock and exits; the one that was starting reads the mailbox anyway on its first "
    "round (scenario I8: dialog in about half a second).",
]) + note("the agent writes " + c("ams-agent.pronto") + " in " + c("$XDG_RUNTIME_DIR") + ", while " + c("ams send")
          + " looks for it in " + c("/run/user/UID") + ": they coincide in sessions started by logind, which is the "
          "supported case.")

RECOVER = seq([("ams send", "root", "navy"), ("sent/ID", "", "dark"), ("Mailbox U1", "", "blue"),
               ("Mailbox U2", "", "blue"), ("ams (later)", "any command", "light")], [
    (0, 1, "lock, incomplete, msg"),
    (0, 2, "copy, verify"),
    (0, 1, "delivery: U1"),
    ("sep", "interrupted: U2 has no copy".ljust(32)),
    (4, 1, "incomplete? lock free?"),
    (4, 2, "rechecks the copy"),
    (4, 3, "writes the copy"),
    (4, 1, "delivery: U2; removes incomplete"),
], "«FIG» — An interrupted send is completed by the next command", "Recovery", width=920)

S6 = p(c("recupera") + " runs at the start of almost every command (" + cap(4, 1) + ") and repairs what an "
       "interrupted command left half done: sends, revocations, deletions. It is <b>idempotent</b>: repeating it "
       "changes nothing.", lead=True) + RECOVER + table(["Finds", "Condition", "Does"], [
    [c("sent/ID/incomplete"), "lock free, but " + c("msg") + " or " + c("recipients") + " missing or unreadable",
     "writes " + c("failed") + " with the date, removes " + c("incomplete") + ", event " + c("ANNULLATO")
     + ", warning «il messaggio N era stato interrotto prima di essere salvato ed è stato annullato»"],
    [c("sent/ID/incomplete"), "lock free, message revoked or expired", "removes the marker without delivering"],
    [c("sent/ID/incomplete"), "lock free, valid message", "for each recipient " + c("consegna_copia")
     + ", <b>including those already recorded</b>; for the new ones: line in " + c("delivery") + " with 0 terminals, "
     "event " + c("CONSEGNATO") + ", wake-up; if none is missing: " + c("syncfs") + ", " + c("fsync") + ", removes "
     + c("incomplete") + "; event " + c("RECUPERATO") + " with the number of new ones"],
    [c("sent/ID/ritiro"), "lock free", "removes the remaining copies (" + cap(9, 1) + ")"],
    [c("sent/.cancella-ID/"), "always", "completes the deletion (" + cap(9, 3) + ")"],
    ["any marker", "lock held", "nothing: it is a send in progress, not an interrupted send"],
], "«TAB» — What recovery repairs") + ul([
    "The lock tells a send <b>in progress</b> from an <b>interrupted</b> one: " + c("ams send") + " holds it for the "
    "whole delivery and the kernel releases it when the process dies, even with " + c("SIGKILL") + ". Without this "
    "rule recovery, started during a long send, delivered in parallel and recorded duplicates (found "
    "by the real-world suite; scenarios F3 and F5).",
    "Copies already recorded are checked again because, after a power failure, a " + c("delivery")
    + " line might be on disk while the copy is not (" + c("tests/engine.sh") + ", group 9).",
    "In the last recorded run on the test machine (scenario F3), an " + c("ams send") + " killed with "
    + c("SIGKILL") + " after 4 deliveries out of 68 was completed by the next command in less than a second.",
]) + warn("recovering a send in which some copy still cannot be written leaves " + c("incomplete")
          + " and warns: «messaggio N ancora non consegnato a K destinatari (vedi ams status N)». Every following "
          "command retries.")

S7 = p("A message's text and title come from an administrator but end up in the users' terminals: "
       "they must not be able to move the cursor, change the window title or write to the clipboard. "
       + c("pulisci") + " in " + c("src/testo.c") + " removes, in three passes, everything a terminal could "
       "interpret as a command.", lead=True) + table(["Pass", "Removed", "Example", "Why"], [
    ["1, per line", "CSI sequences: " + c("ESC [") + ", digits, " + c(";") + " or " + c("?") + ", a final character",
     c("ESC [ 31 m"), "colours, cursor movements, erasures"],
    ["1, per line", "OSC sequences: " + c("ESC ]") + " … " + c("BEL"), c("ESC ] 0 ; titolo BEL"),
     "window title, hyperlinks, clipboard"],
    ["2", "C0 control characters, except tab and newline; " + c("DEL"), c("0x01") + ", " + c("\\r") + ", "
     + c("0x7F"), "bell, carriage return, leftover lone escapes"],
    ["3", "C1 characters in UTF-8", c("C2 80") + " … " + c("C2 9F"), "some terminals interpret them as commands"],
], "«TAB» — What pulisci removes, in order") + ul([
    "An OSC sequence without a final " + c("BEL") + " is not removed as a sequence: its " + c("ESC") + " disappears "
    "in pass 2 and the rest remains as harmless text (" + c("tests/prove-unita.c") + ").",
    "Normal UTF-8 text stays intact, including non-breaking spaces (" + c("C2 A0") + ").",
    c("pulisci") + " is applied to text and title before they are saved, to what " + c("ams") + " reads from the "
    "mailboxes (" + cap(10, 2) + "), to the lines of " + c("ams log") + " and to what the TUI shows of the commands "
    "it ran.",
    "It gives the same result as the bash prototype (" + c("sed") + " and " + c("tr") + "): the two were compared on "
    "2000 random texts full of sequences and control characters before the prototype was removed. Scenario G2 "
    "checks that no " + c("ESC") + " reaches the terminal.",
])

CHAPTER = ("Sending and recovery", [
    ("Options and text", S1),
    ("The sending sequence", S2),
    ("Verified delivery", S3),
    ("Writing to the terminals", S4),
    ("Waking or starting the agent", S5),
    ("Recovery", S6),
    ("Cleaning the text", S7),
])
