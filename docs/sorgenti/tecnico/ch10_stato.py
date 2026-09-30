from build import arrow, box, c, code, diamond, fig, note, p, path, seq, table, term, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">chapter {n}{"." + str(s) if s else ""}</a>'


DECIDE = fig(
    diamond(120, 70, 200, 64, "line in delivery?", "navy")
    + box(40, 150, 160, 50, "INVIATO", "", "light")
    + diamond(355, 70, 220, 64, "confirmation in acks/ID?", "navy")
    + box(275, 150, 160, 50, "CONSEGNATO", "no confirmation", "blue", 12)
    + diamond(585, 70, 200, 64, "date ≤ expiry?", "navy")
    + box(705, 45, 185, 50, "CONSEGNATO", "late confirmation", "blue", 12)
    + diamond(585, 190, 200, 64, "date ≤ revocation?", "navy")
    + box(705, 165, 185, 50, "CONSEGNATO", "confirmed after revocation", "blue", 12)
    + box(505, 260, 160, 50, "CONFERMATO", "date and channel", "green", 12)
    + arrow(220, 70, 243, 70, "#0050C0", False, "yes", 232, 60)
    + arrow(120, 104, 120, 148, "#475569", False, "no", 136, 128)
    + arrow(465, 70, 483, 70, "#0050C0", False, "yes", 474, 60)
    + arrow(355, 104, 355, 148, "#475569", False, "no", 371, 128)
    + arrow(685, 70, 703, 70, "#475569", False, "no", 694, 60)
    + arrow(585, 104, 585, 156, "#0050C0", False, "yes", 601, 132)
    + arrow(685, 190, 703, 190, "#475569", False, "no", 694, 180)
    + arrow(585, 224, 585, 258, "#16a34a", False, "yes", 601, 244),
    900, 330, "«FIG» — stato_destinatario: a recipient's state, deduced from the files", "How the state is decided")

S1 = p("A recipient's state is not written anywhere: " + c("stato_destinatario") + " in "
       + c("src/ams.c") + " deduces it every time from " + c("sent/ID/delivery") + ", from the confirmation in the "
       "mailbox and from the reference copy. The expiry and revocation that count are <b>root's</b>, not those of the "
       "copy, which the user might have altered.", lead=True) + DECIDE + table(["Condition", "State",
                                                                                 "Line in ams status"], [
    ["no line for U in " + c("delivery"), "sent", "«inviato, non consegnato»; if there is " + c("incomplete")
     + ": «…: la copia non è stata scritta (vedi il registro; il prossimo comando ams riproverà)»"],
    ["line in " + c("delivery") + ", no confirmation", "delivered", "«consegnato», plus the details: «scritto su N "
     "terminali», «rimandato il …»; or «non confermato (ritirato)» or «(scaduto)»"],
    ["confirmation dated after the expiry in " + c("sent/ID/msg"), "delivered", "«consegnato, non confermato "
     "(scaduto; conferma arrivata dopo la scadenza)»"],
    ["confirmation dated after " + c("sent/ID/revoked"), "delivered", "«consegnato, non confermato (ritirato)»"],
    ["valid confirmation", "confirmed", "«confermato il 30/09 17:10 (terminale pts/2)»"],
], "«TAB» — The state deduced from the files") + ul([
    "The date of the confirmation is the number before the space in " + c("acks/ID") + " (0 if it is not a number); "
    "the rest of the line is the channel, translated only when it is shown (" + c("canale_testo") + ").",
    "A confirmation with the same date as the revocation counts; one from the second after does not ("
    + c("tests/engine.sh") + ", group 9).",
    "A recipient is in <b>exactly one</b> of the three states: the function returns a value of " + c("stato_e")
    + " (" + c("INVIATO") + ", " + c("CONSEGNATO") + ", " + c("CONFERMATO") + ") plus, separately, if the "
    "confirmation was late, its date and channel.",
])

LETTURA = seq([("ams (root)", "list, status, TUI", "navy"), ("child as U", "op_leggi, 20 s", "dark"),
               ("Mailbox U", "users/U", "blue")], [
    (0, 1, "IDs from sent/, one per line"),
    (1, 2, "acks/ID: at most 200 bytes"),
    (1, 2, "stat of state/ID.term and .gui"),
    (1, 0, "«A ID line» · «S ID date»", True),
    ("nota", 0, "pulisci then casella_da_testo"),
], "«FIG» — A mailbox is read once, as the user", "Reading the mailboxes")

S2 = p(c("ams status") + " and " + c("ams list") + " read the confirmations from the mailboxes, which the users "
       "control. " + c("leggi_casella") + " in " + c("src/archivio.c") + " treats them as <b>untrusted data</b> and "
       "reads them <b>once per user</b>, in a single child process.", lead=True) + LETTURA + ul([
    "The child receives on stdin the numbers of the messages that exist in " + c("sent/") + " and looks only for "
    "those: thousands of fake files in " + c("acks/") + " do not matter (5000 files: " + c("ams list") + " under a "
    "second, " + c("tests/engine.sh") + " group 9; before the fix, 3.9 s).",
    "Of " + c("acks/ID") + " it reads at most 200 bytes, and only if it is a regular file opened without blocking: a "
    "pipe in place of the confirmation does not block " + c("ams status") + " (group 9).",
    "Of " + c("state/ID.*") + " it reads the most recent modification date: that is the time of the postponement.",
    "The child's output (at most 4 MiB) goes through " + c("pulisci") + " before it is interpreted: a confirmation "
    "forged with escape sequences does not reach the administrator's terminal (scenario G3).",
    "The mailboxes read stay in memory for the whole command; the TUI forgets them at every refresh ("
    + c("caselle_svuota") + "). Deliveries are read once per message (" + c("leggi_consegne") + ").",
])

S3 = p("In the list of messages, in " + c("ams list") + " and in the TUI, a message is summarised <b>by its "
       "recipients</b>: how many are in each of the three states, in words and with a bar, plus the properties "
       "revoked and expired. No other word describes the state of a message (" + cap(20, 3) + ").", lead=True) + \
    code("""typedef struct {
	long long id;
	msg_t m;                              /* il messaggio letto da sent/ID/msg */
	int confermato, consegnato, inviato;  /* i destinatari nei tre stati */
	bool ritirato, scaduto;               /* proprietà del messaggio */
} riassunto_t;""", "c", "src/ams.h") + table(["Function", "What it does"], [
    [c("riassumi(id, r)"), "reads message, recipients, deliveries and revocation date <b>before</b> counting; "
     "false if the message no longer exists, has no recipients or if the send was cancelled (" + c("failed") + ")"],
    [c("riassunto_frase(r, out)"), "«14 confermato · 5 consegnato · 2 inviato», omitting zero counts; "
     "«tutti confermato (58)» if nobody is missing"],
    ["the TUI bar", "12 marks: " + c("█") + " confirmed (green), " + c("▒") + " delivered (yellow), "
     + c("░") + " sent (red); a single sent recipient still gets at least one mark"],
], "«TAB» — Summarising a message") + \
    note("the phrase always uses the name of the state («5 consegnato»), not an adjective agreeing in number: it is "
         "the same word as in the STATO column of " + c("ams status") + ", in every language.")

LIST = ("admin@server:~$ sudo ams list\n"
        "ID    DATA         TESTO                                     DESTINATARI\n"
        "1     30/09 16:55  Stanotte alle 23 il server di posta vien  tutti confermato (3)\n"
        "2     30/09 16:55  Sabato dalle 8 alle 12 il server sarà sp  4 confermato · 3 consegnato · 1 inviato\n"
        "3     30/09 16:55  Il tuo account scade venerdì: passa dall  1 consegnato\n"
        "4     30/09 16:55  [ritirato] Riavvio alle 13:00.            2 consegnato")

STATUS = ("admin@server:~$ sudo ams status 2\n"
          "Messaggio 2 · Manutenzione · 30/09 16:55 · da root\n"
          "  │ Sabato dalle 8 alle 12 il server sarà spento per la manutenzione dei dischi.\n"
          "  │ Salvate il lavoro entro venerdì sera.\n"
          "\n"
          "UTENTE           STATO\n"
          "admin            confermato il 30/09 16:55 (terminale pts/0)\n"
          "anna             confermato il 30/09 16:55 (desktop)\n"
          "dario            inviato, non consegnato\n"
          "fabio            confermato il 30/09 16:55 (desktop)\n"
          "kora             consegnato, rimandato il 30/09 16:55\n"
          "luca             consegnato\n"
          "mario            consegnato, rimandato il 30/09 16:55\n"
          "zeno             confermato il 30/09 16:55 (terminale pts/2)")

S4 = p("The two query commands show the same state at two levels: the list of messages and the detail "
       "of one. Both run recovery first; after that, only reads, without locks.", lead=True) + \
    term(LIST, "ams list: one message per line (the messages in the screenshots of chapter 14)") + ul([
    "Columns: ID, sending date («30/09 16:55»), the first 40 columns of the first line of the text (preceded by "
    + c("[ritirato]") + " and " + c("[scaduto]") + "), the summary phrase.",
    "A cancelled send appears as «[invio annullato: interrotto prima del salvataggio]»: it reports an internal "
    "marker, not a state.",
]) + term(STATUS, "ams status: one recipient per line") + ul([
    "Header: number, title and date, sender; then «RITIRATO il …» and «SCADUTO» if they apply; then the text, "
    "indented.",
    "One line per recipient, in the order of " + c("recipients") + " (alphabetical), with the state line from the "
    "previous table; the same lines appear in the TUI's detail view.",
    "A non-existent or cancelled message ends with an error: «messaggio inesistente: 99», «il messaggio N è stato "
    "annullato: l'invio si era interrotto prima del salvataggio».",
]) + p("Times measured in the last recorded run (scenarios H2 and H3, 10 messages to 58 recipients "
       "on the test machine): " + c("ams list") + " 0.24 s, " + c("ams status") + " 0.28 s. In the prototype, "
       "before reading per user, " + c("ams list") + " took about 6 s.")

CHAPTER = ("State: list, status and the summary", [
    ("The state deduced from the files", S1),
    ("Reading the mailboxes", S2),
    ("A message's summary", S3),
    ("ams list and ams status", S4),
])
