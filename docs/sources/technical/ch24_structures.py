from build import arrow, box, c, code, dl, fig, note, p, table, text


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


MAPPA = fig(
    box(20, 40, 170, 56, "msg_t", "sent/ID/msg, parsed", "navy")
    + box(250, 40, 190, 56, "riassunto_t", "msg_t + three counts", "blue")
    + box(500, 40, 170, 56, "elenco_t (TUI)", "the summaries, in order", "soft")
    + box(250, 130, 190, 56, "stato_e", "INVIATO · CONSEGNATO · …", "green", 12)
    + box(500, 130, 170, 56, "destinatario_t", "user, state, line", "blue")
    + box(20, 130, 170, 56, "consegne_t", "sent/ID/delivery", "dark")
    + box(20, 220, 170, 56, "casella_t", "entries read as U", "dark")
    + box(250, 220, 190, 56, "stato_t", "state, date, channel", "light")
    + box(720, 40, 160, 56, "utente_t", "name, uid, gid", "dark")
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
       "it is: only the text formats of " + cap(20, 8) + " go into files.", lead=True) + MAPPA + table(
    ["Structure", "Defined in", "Role", "Chapter"], [
        [c("msg_t"), c("src/testo.h"), "a message that has been read or is to be written", cap(5, 2)],
        [c("conf_t"), c("src/testo.h"), "the configuration", cap(4, 5)],
        [c("stato_e"), c("src/rspeak.h"), "the three states of a recipient", cap(10, 1)],
        [c("riassunto_t"), c("src/rspeak.h"), "a message with its recipients counted in the three states", cap(10, 3)],
        [c("destinatario_t") + ", " + c("destinatari_t"), c("src/rspeak.h"), "the recipients with the line from "
         + c("rspeak status"), cap(10, 4)],
        [c("voce_casella_t") + ", " + c("casella_t"), c("src/archivio.h"), "confirmations and postponements read from a mailbox",
         cap(10, 2)],
        [c("utente_t"), c("src/utente.h"), "a user: name, UID, primary group", cap(7, 2)],
        [c("come_utente_fn"), c("src/utente.h"), "the function run in the child", cap(7, 2)],
        [c("op_t"), c("src/archivio.c"), "argument of the mailbox operations", cap(7, 4)],
        [c("consegne_t"), c("src/rspeak.c"), "the " + c("delivery") + " lines of a message", cap(10, 1)],
        [c("stato_t"), c("src/rspeak.c"), "the state of a recipient, with date and channel of the confirmation", cap(10, 1)],
        [c("catalogo_t"), c("src/lingua.c"), "a " + c(".mo") + " catalog in memory", cap(16, 3)],
        [c("buf_t") + ", " + c("strv_t"), c("src/comune.h"), "growing texts and lists of strings", cap(5, 5)],
        [c("schermo_t") + ", " + c("elenco_t") + ", " + c("modulo_t") + ", " + c("lancio_t"), c("src/tui.c"),
         "screen, list, form and command to run in the TUI", cap(14)],
    ], "«TAB» — Index of the data structures")

S2 = code("""typedef struct {
	long long id;
	char *from;         /* l'amministratore */
	long long date;     /* secondi dall'epoca Unix; obbligatoria */
	char *title;        /* una riga, eventualmente vuota */
	long long expires;  /* 0: nessuna scadenza */
	char *body;         /* il testo, con l'a capo finale */
} msg_t;""", "c", "src/testo.h") + table(["Field", "Type", "Description"], [
    [c("id"), c("long long"), "the message number (" + c("id:") + ")"],
    [c("from"), c("char *"), "never null after reading (empty if missing)"],
    [c("date"), c("long long"), "a message without a valid " + c("date") + " is not read"],
    [c("title"), c("char *"), "never null after reading"],
    [c("expires"), c("long long"), c("msg_scaduto") + " is true if it is not 0 and is less than or equal to the given time"],
    [c("body"), c("char *"), "everything after the first empty line"],
], "«TAB» — The fields of msg_t") + \
    p(c("msg_libera") + " frees the three texts and zeroes the structure: a zeroed " + c("msg_t") + " can be freed "
      "safely.")

S3 = code("""/* Gli stati di un destinatario: gli unici tre (capitolo «Specifica»). */
typedef enum { INVIATO, CONSEGNATO, CONFERMATO } stato_e;

typedef struct {
	long long id;
	msg_t m;
	int confermato, consegnato, inviato;
	bool ritirato, scaduto;
} riassunto_t;

typedef struct {
	char *utente;
	stato_e stato;
	char *riga;        /* la riga di rspeak status, nella lingua di chi legge */
} destinatario_t;""", "c", "src/rspeak.h") + dl([
    (c("stato_e"), "the only place in the code where the states are enumerated. Revoked and expired are not "
     "there: they are the two " + c("bool") + " fields of " + c("riassunto_t") + "."),
    (c("riassunto_t"), "produced by " + c("riassumi") + "; " + c("confermato + consegnato + inviato") + " is the "
     "number of recipients. " + c("riassunto_libera") + " frees the message it contains."),
    (c("destinatario_t"), "produced by " + c("destinatari") + " for " + c("rspeak status") + ", for the TUI and for "
     + c("rspeak remind") + ", which reminds those with " + c("stato == CONSEGNATO") + "."),
])

S4 = code("""typedef struct {
	long long id;
	char *conferma;     /* prima riga di acks/ID, o NULL */
	long long rinvio;   /* data di modifica più recente di state/ID.*, o 0 */
} voce_casella_t;

typedef struct {
	voce_casella_t *v;
	size_t n;
} casella_t;""", "c", "src/archivio.h") + \
    p("A " + c("casella_t") + " is built by " + c("casella_da_testo") + ", which parses the child's output ("
      + c("A ID riga") + " (“A ID line”) for confirmations, " + c("S ID data") + " (“S ID date”) for postponements), already cleaned; malformed "
      "lines are discarded, and for each ID the first confirmation and the most recent postponement count. "
      + c("casella_da_testo") + " is also exposed for the tests and for fuzzing.")

S5 = code("""typedef struct { char *nome; uid_t uid; gid_t gid; } utente_t;
typedef int (*come_utente_fn)(void *arg);
typedef struct { long remind_minutes; long agent_poll; } conf_t;   /* 30, 60 */
typedef struct { char *s; size_t n, cap; } buf_t;    /* s sempre terminato da '\\0' */
typedef struct { char **v; size_t n, cap; } strv_t;""", "c", "src/utente.h, src/testo.h, src/comune.h (in brief)") + dl([
    (c("utente_t"), "from " + c("utente_cerca") + " (by name) or " + c("utente_da_uid") + "; the name is copied."),
    (c("conf_t"), "filled in by " + c("conf_leggi") + " with the default values and the valid keys of the file."),
    (c("buf_t"), "every text that comes from outside ends up here: " + c("buf_add") + " checks for size "
     "overflow, and the memory grows by doubling. " + c("buf_free") + " brings it back to empty."),
    (c("strv_t"), "lists of recipients, of IDs, of terminals; " + c("strv_sort") + " in alphabetical order, "
     + c("elenca_numeri") + " in numerical order."),
]) + note("all structures are initialised to zero (" + c("{0}") + ") and have a function that frees them; "
          "fuzzing found precisely a function that assumed an already zeroed structure (" + cap(21, 7) + ").")

CHAPTER = ("Appendix A — Data structures", [
    ("Index of the data structures", S1),
    ("msg_t: a message", S2),
    ("stato_e, riassunto_t, destinatario_t", S3),
    ("voce_casella_t and casella_t", S4),
    ("utente_t, conf_t, buf_t, strv_t", S5),
])
