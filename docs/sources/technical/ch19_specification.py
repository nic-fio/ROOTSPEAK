from build import arrow, box, c, fig, note, p, path, table, text, ul, zone


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


SOURCES = fig(
    zone(20, 44, 280, 150, "Authoritative · root")
    + box(40, 80, 240, 90, "sent/ID/", "what, to whom, when, expiry, revocation", "navy")
    + zone(310, 44, 280, 150, "Working copy · user")
    + box(330, 80, 240, 90, "users/U/", "copy, confirmation, postponements", "blue")
    + zone(600, 44, 280, 150, "History · journal")
    + box(620, 80, 240, 90, "RSPEAK_* events", "with the _UID of whoever wrote them", "soft")
    + text(450, 222, "a recipient's state: sent/ compared with users/U; never from the journal", 11.5, "#003a90",
           "700"),
    900, 240, "«FIG» — The three sources and their authority", "Sources of truth")

S1 = p("This chapter is the <b>contract</b> of RootSpeak: what any implementation must respect, regardless of how it is "
       "written. The rest of the manual describes how the C version implements it; the bash prototype (0.1.0) "
       "worked on the same message store, and the same tests apply to both. Every change to the code respects this "
       "chapter or updates it explicitly.", lead=True) + SOURCES + \
    table(["Source", "Authority", "Written by"], [
        [c("sent/ID/") + " (msg, recipients, delivery, revoked, incomplete, revoking, failed, lock)", "<b>authoritative</b>: "
         "what was sent, to whom, when, with which expiry, to whom it was delivered, whether and when it was "
         "revoked", "root only"],
        [c("users/U/") + " (inbox, read, acks, state)", "<b>working copy</b>, controlled by the user: it can be "
         "deleted or altered, and the system must stay consistent", "the user (and root, as the user)"],
        ["journal (" + c("SYSLOG_IDENTIFIER=rspeak") + ")", "<b>history</b>: events with a date and " + c("_UID")
         + ", the user who wrote them (set by the journal). Anyone can write an event with the "
         + c("RSPEAK_*") + " fields: " + c("_UID") + " says who wrote it, not that it is true; " + c("rspeak log") + " flags "
         "as not trustworthy an event written by the wrong user. States are derived from the message store, never from "
         "the journal", "root and the user"],
    ], "«TAB» — The sources of truth") + ul([
    "A confirmation is a fact declared by the user in their own mailbox; it is valid only if it does not contradict "
    "root's message store: its date must not be later than the expiry written in " + c("sent/ID/msg") + " nor than the revocation ("
    + c("sent/ID/revoked") + ").",
    "<b>“Confirmed” means</b>: the mailbox contains a valid read statement from the user. It is not an action "
    "observed by RootSpeak, nor proof of reading: the user controls their own mailbox and could write it themselves. "
    "Anyone using " + c("rspeak status") + " for an audit must read it this way.",
    "If the user deletes their own copy, the message simply shows as not confirmed; if they alter it (text, "
    "expiry), only what they see changes.",
])

STATES = fig(
    box(20, 130, 200, 64, "SENT", "in recipients, not in delivery", "light")
    + box(300, 130, 250, 64, "DELIVERED", "in delivery, no valid confirmation", "blue")
    + box(640, 130, 240, 64, "CONFIRMED", "acks/ID with a valid date", "green")
    + arrow(222, 162, 298, 162, "#0050C0", False, "copy verified", 260, 152)
    + arrow(552, 162, 638, 162, "#16a34a", False, "confirmation", 595, 152)
    + text(595, 212, "(not expired, not revoked)", 11, "#166534", "600")
    + path([(385, 196), (385, 232), (465, 232), (465, 196)], "#d97706")
    + text(425, 252, "postponement: state/ID.*", 11, "#92400e", "600")
    + box(560, 20, 320, 48, "Properties of the message", "REVOKED · EXPIRED", "soft", 12)
    + text(40, 88, "internal recovery marks, not states:", 11, "#475569", "400", "start")
    + text(40, 106, "incomplete · failed · revoking · .deleting-ID", 11, "#475569", "400", "start"),
    900, 272, "«FIG» — The states of a recipient and the properties of a message", "The state machine")

S2 = p("Each recipient of a message is in <b>one of three states</b>; the state is derived from the files, according "
       "to fixed rules (" + cap(10, 1) + "). There are only these three states (the owner's decision): revocation and "
       "expiry are properties of the message, not states; " + c("incomplete") + ", " + c("failed") + ", " + c("revoking")
       + " and " + c(".deleting-ID") + " are internal marks with which recovery completes or cancels an interrupted "
       "operation, and they are not shown as states. An interrupted sending shows for itself: some recipients stay "
       "sent.", lead=True) + STATES + table(["Transition", "Precondition", "Atomic operation", "Effect",
                                               "Event"], [
    ["sending", "recipients resolved, text cleaned, at most 65536 bytes", "ID with " + c("flock") + "; lock and "
     + c("incomplete") + " before anything else; " + c("msg") + " and " + c("recipients") + " written, renamed and "
     "flushed to disk (" + c("fsync") + ")", "all SENT", c("SENT") + " (at the end of sending)"],
    ["delivery", "sending lock held, message not revoked", "copy written as the user and renamed, then "
     "verified; then a line in " + c("delivery") + "; at the end of sending everything to disk, then " + c("incomplete")
     + " removed", "SENT → DELIVERED", c("DELIVERED") + " (or " + c("NOT_DELIVERED") + ")"],
    ["confirmation", "copy in " + c("inbox/") + ", not expired, no confirmation present", "temporary file + "
     + c("link") + " (fails if it exists), then " + c("fsync"), "DELIVERED → CONFIRMED", c("CONFIRMED")],
    ["postponement", "DELIVERED", "modification time of " + c("state/ID.term") + " or " + c("state/ID.gui"),
     "stays DELIVERED", c("POSTPONED")],
    ["revocation", "existing message", c("sent/ID/revoking") + " and " + c("sent/ID/revoked") + " (on disk); then the lock "
     "(waits for a sending in progress); then copies removed as the user and " + c("revoking") + " removed", "no state "
     "changes; it is no longer shown; later confirmations are not valid", c("REVOKED")],
    ["expiry", "—", "none (time passes)", "it is no longer shown; a confirmation after it is not valid", "—"],
    ["recovery", c("incomplete") + " present and lock free", "delivery of the missing copies and check of those "
     "already recorded", "SENT → DELIVERED", c("DELIVERED") + ", " + c("RECOVERED")],
    ["revocation recovery", c("revoking") + " present and lock free", "remaining copies removed", "—", "—"],
    ["reminder", "message neither revoked nor expired", "for each DELIVERED recipient: postponements " + c("state/ID.*")
     + " removed, agent woken up", "stays DELIVERED; the question and the dialog come back at once", c("REMINDED")],
    ["deletion", "older than the duration, lock free, complete", c("sent/ID") + " renamed to "
     + c("sent/.deleting-ID") + "; then copies, confirmations and postponements removed as the user; then the folder removed",
     "the message no longer exists", c("DELETED")],
], "«TAB» — The transitions")

SUMMARY = fig(
    box(20, 40, 260, 56, "recipients of sent/ID", "recipients", "dark")
    + box(330, 40, 180, 56, "recipient_state", "one of the three, for each", "navy")
    + box(560, 20, 320, 40, "14 confirmed · 5 delivered · 2 sent", "", "blue", 12)
    + box(560, 70, 320, 40, "████████▒▒▒░  and  [revoked] [expired]", "", "soft", 12)
    + arrow(282, 68, 328, 68) + arrow(512, 60, 558, 40) + arrow(512, 76, 558, 90)
    + text(450, 138, "no other word describes the state of a message", 11.5, "#b91c1c", "700"),
    900, 158, "«FIG» — A message is summarised by the counts of its recipients: “14 confirmed · 5 delivered · 2 "
    "sent”, the bar and the marks “[revoked]” and “[expired]”", "The summary")

SM = p("In the message list (TUI and " + c("rspeak list") + ") a message is summarised by its recipients: "
       "how many are in each of the three states, in words and with a bar (confirmed, delivered, sent), plus the "
       "properties revoked and expired. No other word describes the state of a message.", lead=True) + SUMMARY + \
    ul([
        "The phrase leaves out zero counts; if everyone has confirmed it says “all confirmed (N)”.",
        "Words such as “pending”, “complete”, “incomplete sending”, “cancelled” are not states and do not "
        "appear: "
        + c("tests/engine.sh") + " (group 3) and " + c("tests/tui.py") + " check this.",
        "A sending cancelled before it was saved has no recipients to count: " + c("rspeak list") + " reports it "
        "with a warning line, the TUI does not show it (" + cap(10, 4) + ").",
    ])

TIMELINE = fig(
    zone(20, 40, 860, 84, "Instants at which an operation happens for everyone")
    + box(30, 74, 160, 32, "send: rename recipients", "", "navy", 10.5)
    + box(200, 74, 160, 32, "delivery: delivery line", "", "blue", 10.5)
    + box(370, 74, 160, 32, "revoke: rename revoked", "", "amber", 10.5)
    + box(540, 74, 150, 32, "ack: link of acks/ID", "", "green", 10.5)
    + box(700, 74, 170, 32, "purge: rename .deleting", "", "dark", 10.5)
    + text(450, 150, "before that instant the operation has not happened, after it has, for any observer", 11.5,
           "#475569", "600"),
    900, 168, "«FIG» — The linearisation points of the operations that change the message store", "When it happens")

S2B = p("For each command that changes the message store: which lock it holds, at which instant the operation is "
        "considered to have happened (the <b>linearisation point</b>: before that instant it has not happened, after "
        "it has, for any observer) and what happens with other commands at the same time.", lead=True) + TIMELINE + \
    table(["Operation", "Lock", "Happens when", "Concurrently"], [
        [c("send"), c("sent/.seq.lock") + " for the ID; " + c("sent/ID/lock") + " exclusive for the whole delivery",
         "the message: " + c("recipients") + " renamed; each delivery: its line in " + c("delivery"),
         "recovery and deletion skip the message; revocation stops it at the next recipient"],
        ["recovery", c("sent/ID/lock") + " if free, otherwise skips", "like delivery",
         "never works at the same time as a sending in progress"],
        [c("revoke"), c("sent/ID/lock") + " waited for after writing " + c("revoked"), c("sent/ID/revoked")
         + " renamed into place", "the sending in progress delivers nothing more; confirmations with a later date are "
         "not valid; the copies are removed once the sending has released the lock"],
        ["confirmation (" + c("rootspeak-user") + ")", "none: exclusive " + c("link"), c("acks/ID") + " created; what counts "
         "is the date written inside", "between two confirmations the first one wins; with revocation the date decides: "
         "equal or earlier is valid, later is not; without a copy in " + c("inbox/") + " there is no confirmation"],
        [c("purge"), c("sent/ID/lock") + " if free, otherwise skips", c("sent/ID") + " renamed to "
         + c("sent/.deleting-ID"), "from that instant no command sees the message; " + c("list") + " reads what it "
         "needs beforehand and skips a message that has disappeared in the meantime"],
        [c("remind"), "none", "each postponement removed", "with a confirmation that arrived in the meantime: that "
         "recipient is no longer DELIVERED and removing their postponements has no effect"],
        [c("list") + ", " + c("status") + ", " + c("log") + ", the TUI", "none (read-only)", "—",
         "they see the state at that moment: during a sending, the recipients not yet reached are SENT"],
    ], "«TAB» — Locks and linearisation points")

S3 = table(["#", "Invariant"], [
    ["I1", "Every complete " + c("sent/ID") + " has " + c("msg") + " and " + c("recipients") + "; an incomplete one has "
     + c("incomplete") + ", a cancelled one has " + c("failed") + "."],
    ["I2", c("delivery") + " contains at most one line per recipient, and only for recipients: delivery and recovery "
     "hold the same lock."],
    ["I3", "A line in " + c("delivery") + " means that the copy was in the mailbox, verified, at that moment."],
    ["I4", "A confirmation comes into being whole or not at all, and once written it does not change: the first one counts."],
    ["I5", "A valid confirmation has a date no later than the expiry of the reference copy nor than the revocation."],
    ["I6", "A message with " + c("incomplete") + " and a free lock is an interrupted sending: the first subsequent "
     + c("rspeak") + " command completes it or, if it had not been saved, cancels it."],
    ["I7", "Root never reads or writes the contents of a mailbox with its own identity: always as the user."],
    ["I8", "The saved text and title contain no control characters or escape sequences."],
    ["I9", "IDs always increase (a sequence with " + c("flock") + "); they are reused only if the message store is reset."],
    ["I10", "RootSpeak never locks a session and does not touch sessions without a terminal."],
    ["I11", "The wake-up signal goes only to a ready agent; the mailbox remains the authoritative queue: a lost signal "
     "delays the dialog by at most " + c("RSPEAK_AGENT_POLL") + " seconds, it does not lose it. The signal neither closes "
     "nor changes a dialog that is already open."],
    ["I12", "A postponement is recorded only for a choice by the user (“Later”, dialog closed, an answer "
     "other than yes): a dialog closed by the system is not a postponement."],
    ["I13", "Durability: when " + c("incomplete") + " is gone, copies and " + c("delivery") + " lines are on "
     "disk; a confirmation is on disk before the user reads “Confirmed.”; " + c("revoked") + " is on "
     "disk before " + c("rspeak revoke") + " touches the mailboxes. After a power failure with " + c("incomplete")
     + " present, recovery rechecks all the copies, including those already recorded."],
    ["I14", "The text is written to a terminal only if the terminal, once opened, belongs to the recipient: "
     "the name " + c("/dev/pts/N") + " does not identify a session."],
    ["I15", "No root command reads from the mailboxes more than what concerns the messages in " + c("sent/")
     + ", and every read has a time limit: an abnormal mailbox neither blocks nor slows down " + c("rspeak") + "."],
], "«TAB» — The invariants")

S4 = p("For each point at which a process can be interrupted, the state that remains and who repairs it.", lead=True) + \
    table(["Interruption", "Remaining state", "Repair"], [
        ["after the ID, before the folder", "a skipped number", "none (harmless)"],
        ["folder and " + c("incomplete") + ", without " + c("msg") + " or " + c("recipients"), "sending not saved",
         "the next command cancels it (" + c("failed") + ", event " + c("CANCELLED") + ")"],
        ["during the deliveries", "some recipients SENT", "the next command delivers the missing copies"],
        ["after the deliveries, before removing " + c("incomplete"), "everything delivered, mark left behind",
         "the next command removes the mark"],
        ["inside the confirmation, before " + c("link"), "a temporary file " + c("acks/.ID.PID")
         + ", no confirmation", "the question comes back; the temporary file is ignored"],
        ["after " + c("link") + ", before the move to " + c("read/"), "confirmation present, copy still in "
         + c("inbox/"), "whoever reads the mailbox completes the move without asking again"],
        ["leaving the session right after “I have read it”", "confirmation recorded: the agent waits for "
         "the dialog, writes the answer as soon as it arrives and defers SIGTERM until after the write", "none "
         "(scenario I10: exit as soon as zenity has the answer)"],
        ["leaving the session with the dialog open", "no postponement recorded (zenity's exit 1 counts as “Later” "
         "only if the display is still there): the dialog comes back at the next login", "none (scenario I13)"],
        ["the desktop agent dies", "lock released; one of its dialogs may stay open", c("rspeak send")
         + " or the login start a new agent; the orphaned dialog no longer records anything"],
        [c("rspeak revoke") + " after " + c("revoked") + ", before removing the copies", c("revoked") + " and "
         + c("revoking") + "; some copies still in the mailboxes", "the next " + c("rspeak") + " command removes the "
         "copies (until then the recipients do not see them as revoked)"],
        ["a mailbox unreachable during revocation", c("revoking") + " remains", "the next command retries"],
        [c("rspeak purge") + " after the rename", c("sent/.deleting-ID") + ", some copies in the mailboxes",
         "the next " + c("rspeak") + " command removes copies, confirmations, postponements and the folder"],
        ["power failure during sending", c("incomplete") + " on disk; copies and " + c("delivery")
         + " lines perhaps not", "recovery rewrites every missing copy, even if recorded"],
        ["power failure after “Confirmed.”", "confirmation on disk", "none"],
        ["power failure at other moments", "writes not flushed to disk may be missing: a postponement "
         "(the question comes back earlier) or the move to " + c("read/") + " (completed at the next read)",
         "none needed"],
    ], "«TAB» — Behaviour after an interruption") + \
    note("the repairs are tested: interruptions simulated in " + c("tests/engine.sh") + " (groups 1, 2 and 9: "
         "copy gone after an interruption, interrupted revocation and deletion), an " + c("rspeak send")
         + " actually killed with SIGKILL (scenario F3) and a revocation during a sending to many users (scenario F7). "
         "A real power failure is not tested: durability relies on " + c("fsync") + " of files and "
         "folders and on " + c("syncfs") + " at the end of sending.")

S5 = table(["Aspect", "Rule"], [
    ["reference", "all dates are seconds since the Unix epoch on the machine's clock; users and root use the "
     "same clock"],
    ["expiry", "compared with the current time when a message is about to be shown, while a question or a "
     "dialog is open (every second), and when the confirmation is recorded; in " + c("rspeak status") + " with the date "
     "of the confirmation"],
    ["postponement", "lasts " + c("RSPEAK_REMIND_MINUTES") + " from the modification time of " + c("state/ID.term") + " or "
     + c("state/ID.gui") + ", each for its own channel; in the terminal, the postponement does not apply at login; for "
     "the dialog it applies even after a new graphical login"],
    ["clock set back", "expiries and postponements last longer; no message is lost"],
    ["clock set forward", "expiries and postponements arrive earlier"],
    ["suspend and resume", "the agent resumes at the next round (at most " + c("RSPEAK_AGENT_POLL") + " seconds); the "
     "elapsed time counts for expiries and postponements"],
], "«TAB» — Time") + table(["Situation", "Revocation", "Expiry"], [
    ["copy not yet shown", "removed from the mailbox; not shown", "stays; no longer shown"],
    ["dialog or question open", "they close (within 1 s)", "they close (within 1 s)"],
    ["confirmations already given", "remain valid if dated no later than the revocation", "remain valid if dated no "
     "later than the expiry"],
    ["during sending", "sending stops at the next recipient", "sending continues: whoever receives the copy after the "
     "expiry never sees it (“delivered, not confirmed (expired)”)"],
    ["text already written to the terminals", "stays on screen", "stays on screen"],
    ["in " + c("rspeak status"), "“delivered, not confirmed (revoked)”", "“delivered, not confirmed (expired)”"],
], "«TAB» — Revocation and expiry")

S6 = p("Message store format 1. Readers ignore header keys they do not know.", lead=True) + \
    table(["File", "Content"], [
        [c("sent/.seq"), "the last ID assigned, a number"],
        [c("sent/ID/msg"), "header " + c("key: value") + " (" + c("format") + ", " + c("id") + ", "
         + c("from") + ", " + c("date") + ", " + c("title") + ", " + c("expires") + "), blank line, text; UTF-8 "
         "without control characters"],
        [c("sent/ID/recipients"), "one user name per line, no duplicates"],
        [c("sent/ID/delivery"), "one line per delivery: " + c("user date terminals") + ", "
         "fields separated by a space; " + c("date") + " in seconds since the Unix epoch, " + c("terminals")
         + " the number of terminals written "
         "(0 in recovery)"],
        [c("sent/ID/revoked"), "the revocation date, in seconds since the Unix epoch"],
        [c("sent/ID/failed"), "the cancellation date; its presence is what counts"],
        [c("sent/ID/incomplete") + ", " + c("revoking") + ", " + c("lock"), "marks (the content does not matter): "
         "incomplete sending, revocation to be completed; " + c("lock") + " is used with " + c("flock")],
        [c("sent/.deleting-ID/"), "a message that " + c("rspeak purge") + " is deleting"],
        [c("users/U/inbox/ID") + ", " + c("read/ID"), "copy of " + c("msg")],
        [c("users/U/acks/ID"), c("date channel") + ": date in seconds since the Unix epoch, a space, "
         "channel (" + c("desktop") + " or " + c("terminal pts/N") + "); the first line counts, at most 200 bytes"],
        [c("users/U/state/ID.term") + ", " + c("ID.gui"), "empty; the modification time counts"],
    ], "«TAB» — The message store format")

S7 = table(["", "Requirement"], [
    ["system", "Linux with systemd and logind (sessions, " + c("systemd-run --user") + ")"],
    ["libraries and tools", "glibc, libsystemd (sessions and journal), sudo, " + c("systemd-run") + " and " + c("date -d")
     + " (GNU coreutils); to build: gcc, make, pkg-config and the systemd development files (" + c("libsystemd-dev") + " or "
     + c("systemd-devel") + ")"],
    ["desktop", "zenity; a session that runs XDG autostart (" + c("/etc/xdg/autostart") + ")"],
    ["question in the terminal", "bash, zsh or fish at every prompt; sh, dash, ksh and the other shells that read "
     + c("/etc/profile") + " at login; the text at sending time with any shell"],
], "«TAB» — Requirements") + \
    p("<b>Supported</b> means that the requirements are met and RootSpeak is designed to work; <b>verified</b> "
      "that it has been tested, and how. The two are distinct.") + \
    table(["Environment", "Supported", "Verified"], [
        ["Debian 13, GNOME on Wayland", "yes", "yes: the automated suite in the VM (" + c("tests/vm")
         + "); live on the user's PC with GNOME (sending, dialog, postponement, reminder, revocation, the question "
         "in a desktop terminal, sending and the TUI from an ssh session), and the 0.1.0 prototype on GNOME 48"],
        ["22 distributions with systemd without a desktop: Debian, Ubuntu, Fedora, CentOS Stream, RHEL, Rocky, "
         "Alma, Oracle, openSUSE, SLES, Arch", "yes", "yes: the automated suite in a container on each, built there "
         "(" + c("tests/distros") + ", " + cap(20, 4) + ")"],
        ["zsh, fish, ksh, dash", "yes", "yes: K scenarios in the containers, where the distribution packages the shell"],
        ["other desktops: GNOME on Ubuntu and Rocky (SELinux enforcing), KDE Plasma on Fedora, Cinnamon; Wayland and "
         "X11", "yes, with zenity and XDG autostart", "yes: the automated suite in a VM for each (" + c("tests/vm/desktops")
         + ")"],
        ["XFCE, MATE and other desktops", "yes, with zenity and XDG autostart", "no"],
        ["systems without systemd (sysvinit, OpenRC)", "no", "—"],
    ], "«TAB» — The scope: supported and verified")

CHAPTER = ("Specification", [
    ("Authoritative sources", S1),
    ("States and transitions", S2),
    ("How a message is summarised", SM),
    ("Concurrent operations", S2B),
    ("Invariants", S3),
    ("Interruptions and recovery", S4),
    ("Time, revocation and expiry", S5),
    ("Message store format", S6),
    ("Supported and verified scope", S7),
])
