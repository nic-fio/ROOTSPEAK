from build import arrow, box, c, code, fig, note, p, path, seq, table, text, tree, ul, warn, zone


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


S1 = p("The message store is made of files and folders under " + c("/var/lib/rootspeak") + ". One part belongs to root, "
       "one part to each user: the boundary between the two is the heart of RootSpeak security. There is no database and no "
       "index: every piece of information is in a file that can be read with " + c("cat") + ".", lead=True) + tree([
    "/var/lib/rootspeak/                   # root 755",
    "├── sent/                       # root 700 · root only",
    "│   ├── .seq  .seq.lock         # last ID assigned; lock for flock",
    "│   ├── 12/",
    "│   │   ├── msg                 # the message (reference copy)",
    "│   │   ├── recipients          # one recipient per line",
    "│   │   ├── delivery            # “user date terminals” for each delivered copy",
    "│   │   ├── lock                # held by rspeak send while delivering (flock)",
    "│   │   ├── incomplete          # marker: send in progress or to be completed",
    "│   │   ├── revoked             # date of revocation, if revoked",
    "│   │   ├── revoking            # marker: revoked copies still to be removed",
    "│   │   └── failed              # marker: send interrupted before it was saved",
    "│   └── .deleting-9/            # a message that rspeak purge is deleting",
    "└── users/                      # root 755",
    "    └── mario/                  # mario 700 · the mailbox: only Mario and root",
    "        ├── inbox/12            # to be shown",
    "        ├── read/11             # confirmed or expired",
    "        ├── acks/11             # “date channel” of the confirmation",
    "        └── state/12.term       # postponement: the file's modification time counts",
], "«FIG» — The message store, with message 12 still to be confirmed and message 11 confirmed") + \
    note("the files " + c("incomplete") + ", " + c("revoking") + " and " + c("failed") + " are <b>internal recovery "
         "markers</b>: they say that an operation must be completed or has been cancelled. They are not states of a "
         "message or of a recipient, and no command shows them as such (" + cap(19, 2) + ").")

S2 = p("A message is a UTF-8 text file: a " + c("key: value") + " header, an empty line, the text. "
       "The same file, byte for byte, is the reference copy in " + c("sent/ID/msg") + " and the copy in the mailbox "
       "of each recipient.", lead=True) + code("""format: 1
id: 12
from: admin
date: 1790714288
title: Maintenance
expires: 1790800688

On Saturday from 8 am to 12 noon the server will be off for disk maintenance.""", "text", "sent/12/msg") + table(["Field", "Contents"], [
    [c("format"), "format version: 1. Readers ignore the keys they do not know; a different format must be read "
     "by an implementation that knows it"],
    [c("id"), "sequential number, from " + c("next_id")],
    [c("from"), "the administrator: " + c("SUDO_USER") + " if it is an existing user, otherwise the user running "
     + c("rspeak")],
    [c("date"), "seconds since the Unix epoch; <b>mandatory</b>: a message without a valid date is rejected"],
    [c("title"), "title, possibly empty, on a single line (newlines and tabs become spaces)"],
    [c("expires"), "seconds since the Unix epoch; empty: no expiry"],
], "«TAB» — The header of a message") + table(["Function (src/text.c)", "What it does"], [
    [c("msg_format"), "writes the header in the order shown in the figure, then the text"],
    [c("msg_from_text"), "reads line by line up to the first empty line; also accepts " + c("key:")
     + " without a value; what follows is the text"],
    [c("msg_read"), "reads a regular file, without following links, at most " + c("RSPEAK_MAX_MSG")
     + " bytes (65536 + 8192), then " + c("msg_from_text")],
    [c("msg_expired"), "true if " + c("expires") + " is present and is less than or equal to the given time"],
    [c("msg_header"), "“Title · 29/09 22:15”, or just the date: the line that precedes the text in the "
     "terminal, in the dialog and in " + c("rspeak status")],
], "«TAB» — Reading and writing a message")

SEQ = seq([("rspeak send A", "", "navy"), ("sent/.seq.lock", "exclusive flock", "dark"), ("sent/", "", "soft"),
           ("rspeak send B", "", "navy")], [
    (0, 1, "flock: taken"),
    (3, 1, "flock: waits", True),
    (0, 2, ".seq = 11 → mkdir 12"),
    (0, 2, ".seq ← 12 (write_atomic)"),
    (0, 1, "releases"),
    (3, 2, ".seq = 12 → mkdir 13"),
], "«FIG» — Two simultaneous sends get different numbers", "Sequential numbers")

S3 = p("Every message has a sequential number. " + c("next_id") + " in " + c("src/rspeak.c") + " takes it under "
       "an exclusive " + c("flock") + " on " + c("sent/.seq.lock") + ": two simultaneous " + c("rspeak send") + " runs never "
       "get the same number.", lead=True) + SEQ + ul([
    "It reads the last number from " + c("sent/.seq") + " (0 if missing or not a number), increments it and creates the "
    "folder with " + c("mkdir(…, 0700)") + ".",
    "If the folder already exists, it moves on to the next number: this happens if " + c(".seq") + " went backwards, for "
    "example after a power failure that lost the last write. No message is ever "
    "overwritten.",
    "It writes the new value with " + c("write_atomic") + " and releases the lock by closing the descriptor.",
    "A number taken and never used (an interruption right afterwards) remains a gap in the numbering: harmless.",
])

S4 = table(["Path", "Owner", "Permissions", "Why"], [
    [c("/var/lib/rootspeak"), "root", c("755"), "traversable by everyone to reach their own mailbox"],
    [c("sent/"), "root", c("700"), "messages and recipients visible only to administrators"],
    [c("sent/ID/"), "root", c("700"), "created by " + c("next_id")],
    [c("sent/ID/*"), "root", c("600"), "written by " + c("rspeak") + " with " + c("O_NOFOLLOW")],
    [c("users/"), "root", c("755"), "only root creates mailboxes: a user can neither create nor move them"],
    [c("users/U/"), "U", c("700"), "created by root and handed over to U; only U (and root) can enter it"],
    [c("users/U/inbox") + ", " + c("read") + ", " + c("acks") + ", " + c("state"), "U", c("755"),
     "created by U, in a child with U's identity; protected by the " + c("700") + " folder"],
    [c("inbox/ID") + ", " + c("acks/ID") + ", " + c("state/ID.*"), "U", c("644"), "written by U"],
], "«TAB» — Owners and permissions") + \
    p("A user can delete or modify the files in their own mailbox: they only spoil their own copy. The reference "
      "copy stays in " + c("sent/") + ", and a message deleted from the mailbox simply shows up as not "
      "confirmed. A confirmation written by hand remains a statement by the user (" + cap(19, 1) + ").") + \
    warn("the effective permissions of the files created by U also depend on the process umask: the child of "
         + c("as_user") + " sets it to " + c("022") + ", " + c("rootspeak-user") + " uses the one of the user's "
         "session. The real protection is the " + c("users/U") + " folder at " + c("700") + ".")

ATOM = fig(
    box(20, 60, 170, 56, "path.tmp", "O_EXCL, O_NOFOLLOW", "light", 12)
    + box(250, 60, 150, 56, "write_all", "partial ones too", "blue")
    + box(460, 60, 120, 56, "fsync", "to disk", "blue")
    + box(640, 60, 110, 56, "rename", "atomic", "green")
    + box(790, 60, 90, 56, "path", "complete", "green")
    + arrow(192, 88, 248, 88) + arrow(402, 88, 458, 88) + arrow(582, 88, 638, 88) + arrow(752, 88, 788, 88)
    + path([(515, 118), (515, 160), (105, 160), (105, 118)], "#b91c1c", True, "error: unlink(path.tmp)", 310, 176),
    900, 196, "«FIG» — write_atomic: a reader sees the old file or the new one, never a half-written one",
    "Atomic writing")

S5 = p("All file I/O goes through a few functions in " + c("src/common.c") + " with fixed rules. These are the "
       "functions that make it safe to read what users write and that guarantee durability after "
       "an interruption.", lead=True) + table(["Function", "Rule"], [
    [c("read_file(path, max, nofollow, out)"), "opens with " + c("O_NONBLOCK") + " (a pipe does not block the open) and, "
     "if requested, " + c("O_NOFOLLOW") + "; rejects anything that is not a regular file and files larger than " + c("max")],
    [c("read_fd(fd, max, out)"), "reads to the end, keeps at most " + c("max") + " bytes and discards the rest"],
    [c("write_all(fd, p, n)"), "retries after partial writes and signal interruptions"],
    [c("write_atomic(path, p, n, mode)"), "writes " + c("path.tmp") + " (" + c("O_EXCL|O_NOFOLLOW") + "), "
     + c("fsync") + ", renames; on error removes the temporary file"],
    [c("sync_path") + ", " + c("syncfs_path"), c("fsync") + " of a file or a folder; " + c("syncfs")
     + " of the file system that contains it"],
    [c("exists") + ", " + c("is_folder"), "with " + c("lstat") + ": a symbolic link is not the folder it "
     "points to"],
    [c("list_numbers(dir, out)"), "only names made of digits (at most 18), in numeric order"],
    [c("read_number(s, out)"), "digits only, at most 18: no sign, no spaces, no overflow"],
], "«TAB» — The I/O rules") + ATOM + \
    p("Every descriptor is opened with " + c("O_CLOEXEC") + ": no open file is passed on to the programs launched by RootSpeak "
      "(zenity, sudo, systemd-run, the editor). Memory is requested with " + c("xmalloc") + " and texts grow in a "
      + c("buf_t") + " (" + cap(23, 5) + "): no fixed-length buffer receives data that comes from outside.")

S6 = p("RootSpeak has no backup or restore command: the message store is made of files, and the only tools "
       "provided are the purge of old messages (" + c("rspeak purge") + ", " + cap(9, 3) + ") and complete "
       "removal (" + c("install.sh --purge") + ").", lead=True) + table(["What", "Where", "Note"], [
    ["messages, recipients, deliveries, revocations", c("/var/lib/rootspeak/sent/"), "authoritative; root only"],
    ["copies, confirmations, postponements", c("/var/lib/rootspeak/users/"), "per user; the confirmations are the state"],
    ["event history", "system journal", "kept according to the journal's rules, not RootSpeak's"],
    ["configuration", c("/etc/rootspeak/rootspeak.conf"), "not overwritten by upgrades"],
], "«TAB» — Where the data lives") + ul([
    "A reset message store reuses message numbers, the journal does not: this is why " + c("rspeak log ID") + " reads only "
    "the events after the message's sending date (" + cap(17, 4) + ").",
    "A copy taken while a send is in progress contains the " + c("incomplete") + " marker: given how recovery "
    "works (" + cap(8, 6) + "), after a restore that send would be completed by the first " + c("rspeak") + " command.",
]) + warn("backing up and restoring the message store have not been tested: whoever does it must preserve "
          "owners and permissions (in particular U's " + c("users/U") + " with " + c("700") + " and root's " + c("sent/")
          + " with " + c("700") + ").")

CHAPTER = ("The message store", [
    ("Structure", S1),
    ("Format of a message", S2),
    ("Message numbers", S3),
    ("Owners and permissions", S4),
    ("Reading and writing files safely", S5),
    ("Preserving the message store", S6),
])
