# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

from build import arrow, box, c, code, dl, fig, note, p, table, text


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


MAP = fig(
    box(20, 40, 170, 56, "msg_t", "sent/ID/msg, parsed", "navy")
    + box(250, 40, 190, 56, "summary_t", "msg_t + three counts", "blue")
    + box(500, 40, 170, 56, "list_t (TUI)", "the summaries, in order", "soft")
    + box(250, 130, 190, 56, "state_e", "SENT · DELIVERED · …", "green", 12)
    + box(500, 130, 170, 56, "recipient_t", "user, state, line", "blue")
    + box(20, 130, 170, 56, "deliveries_t", "sent/ID/delivery", "dark")
    + box(20, 220, 170, 56, "mailbox_t", "entries read as U", "dark")
    + box(250, 220, 190, 56, "state_t", "state, date, channel", "light")
    + box(720, 40, 160, 56, "user_t", "name, uid, gid", "dark")
    + box(720, 130, 160, 56, "op_t", "mailbox, ID", "soft")
    + box(720, 220, 160, 56, "conf_t", "postponement, polling", "soft")
    + arrow(192, 68, 248, 68) + arrow(442, 68, 498, 68)
    + arrow(192, 158, 248, 238) + arrow(192, 248, 248, 250)
    + arrow(345, 218, 345, 188) + arrow(442, 158, 498, 158)
    + arrow(345, 128, 345, 98, "#16a34a")
    + arrow(800, 98, 800, 128, "#475569", True)
    + text(450, 300, "the state is computed every time: none of these structures is saved", 11.5, "#475569",
           "600"),
    900, 316, "«FIG» — The data structures and how they fit together", "Structures")

S1 = p("This appendix collects the data structures of RootSpeak, with the file that defines each one and the chapter "
       "that covers it in depth. They are the “contracts” that run through the code. None is written to disk as "
       "it is: only the text formats of " + cap(19, 8) + " go into files.", lead=True) + MAP + table(
    ["Structure", "Defined in", "Role", "Chapter"], [
        [c("msg_t"), c("src/text.h"), "a message that has been read or is to be written", cap(5, 2)],
        [c("conf_t"), c("src/text.h"), "the configuration", cap(4, 5)],
        [c("state_e"), c("src/rspeak.h"), "the three states of a recipient", cap(10, 1)],
        [c("summary_t"), c("src/rspeak.h"), "a message with its recipients counted in the three states", cap(10, 3)],
        [c("recipient_t") + ", " + c("recipients_t"), c("src/rspeak.h"), "the recipients with the line from "
         + c("rspeak status"), cap(10, 4)],
        [c("mailbox_item_t") + ", " + c("mailbox_t"), c("src/store.h"), "confirmations and postponements read from a "
         "mailbox", cap(10, 2)],
        [c("user_t"), c("src/user.h"), "a user: name, UID, primary group", cap(7, 2)],
        [c("as_user_fn"), c("src/user.h"), "the function run in the child", cap(7, 2)],
        [c("op_t"), c("src/store.c"), "argument of the mailbox operations", cap(7, 4)],
        [c("deliveries_t"), c("src/rspeak.c"), "the " + c("delivery") + " lines of a message", cap(10, 1)],
        [c("state_t"), c("src/rspeak.c"), "the state of a recipient, with date and channel of the confirmation", cap(10, 1)],
        [c("buf_t") + ", " + c("strv_t"), c("src/common.h"), "growing texts and lists of strings", cap(5, 5)],
        [c("screen_t") + ", " + c("list_t") + ", " + c("form_t") + ", " + c("launch_t"), c("src/tui.c"),
         "screen, list, form and command to run in the TUI", cap(14)],
    ], "«TAB» — Index of the data structures")

S2 = code("""/* Format 1: header "key: value", blank line, text. */
typedef struct {
	long long id;
	char *from;
	long long date;
	char *title;
	long long expires; /* 0: no expiry */
	char *body;
} msg_t;""", "c", "src/text.h") + table(["Field", "Type", "Description"], [
    [c("id"), c("long long"), "the message number (" + c("id:") + ")"],
    [c("from"), c("char *"), "the administrator; never null after reading (empty if missing)"],
    [c("date"), c("long long"), "seconds since the Unix epoch; a message without a valid " + c("date") + " is not read"],
    [c("title"), c("char *"), "one line, possibly empty; never null after reading"],
    [c("expires"), c("long long"), c("msg_expired") + " is true if it is not 0 and is less than or equal to the given time"],
    [c("body"), c("char *"), "everything after the first empty line, with the final line break"],
], "«TAB» — The fields of msg_t") + \
    p(c("msg_free") + " frees the three texts and zeroes the structure: a zeroed " + c("msg_t") + " can be freed "
      "safely.")

S3 = code("""/* The states of a recipient: the only three («Specification» chapter). */
typedef enum { SENT, DELIVERED, CONFIRMED } state_e;

/* A message summarised with its recipients. */
typedef struct {
	long long id;
	msg_t m;
	int confirmed, delivered, sent;
	bool revoked, expired;
} summary_t;

/* The recipients of a message with the status line of rspeak status. */
typedef struct {
	char *user;
	state_e state;
	char *line;
} recipient_t;""", "c", "src/rspeak.h") + dl([
    (c("state_e"), "the only place in the code where the states are enumerated. Revoked and expired are not "
     "there: they are the two " + c("bool") + " fields of " + c("summary_t") + "."),
    (c("summary_t"), "produced by " + c("summarise") + "; " + c("confirmed + delivered + sent") + " is the "
     "number of recipients. " + c("summary_free") + " frees the message it contains."),
    (c("recipient_t"), "produced by " + c("recipients") + " for " + c("rspeak status") + ", for the TUI and for "
     + c("rspeak remind") + ", which reminds those with " + c("state == DELIVERED") + "."),
])

S4 = code("""typedef struct {
	long long id;
	char *confirm; /* first line of acks/ID, or NULL */
	long long postponement;  /* most recent modification time of state/ID.*, or 0 */
} mailbox_item_t;
typedef struct {
	mailbox_item_t *v;
	size_t n;
} mailbox_t;""", "c", "src/store.h") + \
    p("A " + c("mailbox_t") + " is built by " + c("mailbox_from_text") + ", which parses the child's output ("
      + c("A ID line") + " for confirmations, " + c("S ID date") + " for postponements), already cleaned; malformed "
      "lines are discarded, and for each ID the first confirmation and the most recent postponement count. "
      + c("mailbox_from_text") + " is also exposed for the tests and for fuzzing.")

S5 = code("""typedef struct { char *name; uid_t uid; gid_t gid; } user_t;
typedef int (*as_user_fn)(void *arg);
typedef struct { long remind_minutes; long agent_poll; } conf_t;   /* 30, 60 */
typedef struct { char *s; size_t n, cap; } buf_t;    /* s always terminated by '\\0' */
typedef struct { char **v; size_t n, cap; } strv_t;""", "c", "src/user.h, src/text.h, src/common.h (in brief)") + dl([
    (c("user_t"), "from " + c("user_find") + " (by name) or " + c("user_from_uid") + "; the name is copied."),
    (c("conf_t"), "filled in by " + c("conf_read") + " with the default values and the valid keys of the file."),
    (c("buf_t"), "every text that comes from outside ends up here: " + c("buf_add") + " checks for size "
     "overflow, and the memory grows by doubling. " + c("buf_free") + " brings it back to empty."),
    (c("strv_t"), "lists of recipients, of IDs, of terminals; " + c("strv_sort") + " in alphabetical order, "
     + c("list_numbers") + " in numerical order."),
]) + note("all structures are initialised to zero (" + c("{0}") + ") and have a function that frees them; "
          "fuzzing found precisely a function that assumed an already zeroed structure (" + cap(20, 7) + ").")

CHAPTER = ("Appendix A — Data structures", [
    ("Index of the data structures", S1),
    ("msg_t: a message", S2),
    ("state_e, summary_t, recipient_t", S3),
    ("mailbox_item_t and mailbox_t", S4),
    ("user_t, conf_t, buf_t, strv_t", S5),
])
