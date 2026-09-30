from build import arrow, box, c, code, diamond, fig, note, p, path, seq, table, text, ul


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


FLUSSO = fig(
    diamond(110, 70, 180, 60, "acks/ID c'è?", "navy")
    + box(30, 140, 160, 50, "esito 0", "vale la prima", "green", 12)
    + diamond(320, 70, 190, 60, "inbox/ID c'è?", "navy")
    + box(240, 140, 160, 50, "esito 3", "ritirato", "grey", 12)
    + diamond(530, 70, 170, 60, "scaduto?", "navy")
    + box(450, 140, 160, 50, "esito 2", "in read/, niente conferma", "grey", 12)
    + box(650, 40, 230, 60, "acks/.ID.PID", "data canale · fsync", "blue", 12)
    + box(650, 130, 230, 60, "link(tmp, acks/ID)", "fallisce se esiste già", "navy", 12)
    + box(650, 220, 230, 60, "fsync(acks/), read/", "evento CONFERMATO", "green", 12)
    + box(380, 230, 200, 50, "esito 1 o 0", "fallita, o nel frattempo c'è", "amber", 12)
    + arrow(110, 100, 110, 138, "#16a34a", False, "sì", 124, 122)
    + arrow(200, 70, 223, 70, "#0050C0", False, "no", 212, 60)
    + arrow(320, 100, 320, 138, "#475569", False, "no", 334, 122)
    + arrow(415, 70, 443, 70, "#0050C0", False, "sì", 429, 60)
    + arrow(530, 100, 530, 138, "#475569", False, "sì", 544, 122)
    + arrow(615, 70, 648, 70, "#0050C0", False, "no", 630, 60)
    + arrow(765, 102, 765, 128) + arrow(765, 192, 765, 218, "#16a34a", False, "riesce", 800, 208)
    + path([(648, 160), (620, 160), (620, 255), (582, 255)], "#b45309", True, "errore", 588, 212),
    900, 300, "«FIG» — conferma(ID, CANALE): i controlli e la pubblicazione esclusiva", "Come nasce una conferma")

S1 = p(c("conferma(ID, CANALE)") + " di " + c("src/ams-user.c") + " è l'unico punto in cui nasce una conferma. "
       "La scrive in un file temporaneo, la porta su disco e la pubblica con " + c("link") + ", che fallisce se "
       + c("acks/ID") + " esiste già: la conferma nasce <b>intera o non nasce</b>, e «già confermato» resta distinto "
       "da «scrittura fallita».", lead=True) + FLUSSO + code("""static int conferma(long long id, const char *canale)
{
	if (esiste(ack)) { segna_letto(id); return 0; }        /* vale la prima */
	if (!c_e("inbox", id, "")) return 3;                  /* ritirato: niente conferma */
	if (scaduto(id)) { segna_letto(id); return 2; }
	fd = open(tmp, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, 0644);
	if (fd < 0 || scrivi_tutto(fd, riga, n) < 0 || fsync(fd) < 0 || close(fd) < 0 ||
	    link(tmp, ack) < 0) {                               /* link fallisce se acks/ID esiste */
		unlink(tmp);
		if (esiste(ack)) { segna_letto(id); return 0; }   /* un'altra conferma è arrivata prima */
		evento("CONFERMA_FALLITA", id, U, canale, strerror(errno), "");
		return 1;                                          /* il messaggio resta nella casella */
	}
	unlink(tmp);
	sync_path(acks);                                       /* su disco prima di «Confermato» */
	segna_letto(id);
	evento("CONFERMATO", id, U, canale, "", "");
	return 0;
}""", "c", "src/ams-user.c (in breve)") + table(["Caso", "Esito", "Che cosa succede"], [
    ["conferma scritta", "0", "il messaggio passa in " + c("read/") + ", i rinvii si tolgono; evento nel registro"],
    [c("acks/ID") + " già presente", "0", "passa in " + c("read/") + "; resta la prima conferma"],
    ["scrittura fallita (disco pieno, permessi)", "1", "<b>resta in " + c("inbox/") + "</b>; l'utente è avvisato, "
     "l'errore va nel registro, la domanda o la finestra tornano (" + c("tests/engine.sh") + ", gruppo 1; scenario "
     "F4)"],
    ["messaggio scaduto", "2", "passa in " + c("read/") + " senza conferma: una conferma dopo la scadenza non vale"],
    ["copia sparita (ritirato)", "3", "nessuna conferma"],
], "«TAB» — Gli esiti di conferma") + ul([
    "La riga è " + c("data canale") + ": secondi dall'epoca Unix, uno spazio, il canale senza lingua ("
    + c("desktop") + ", " + c("terminale pts/3") + ", " + c("terminale tty3") + ").",
    "Il file temporaneo " + c("acks/.ID.PID") + " comincia con un punto: non è mai scambiato per una conferma. Se "
    "un'interruzione lo lascia, resta ignorato.",
    "Se il ritiro arriva fra il controllo di " + c("inbox/ID") + " e " + c("link") + ", la conferma nasce, ma "
    + c("ams status") + " non la conta: la sua data è successiva a " + c("sent/ID/revoked") + " (" + cap(10, 1) + ").",
    c("segna_letto") + " rinomina " + c("inbox/ID") + " in " + c("read/ID") + " e toglie i rinvii. Se si "
    "interrompe fra la conferma e lo spostamento, chi legge la casella dopo completa lo spostamento senza chiedere "
    "di nuovo (" + c("tests/engine.sh") + ", gruppo 1).",
])

RACE = seq([("Finestra", "conferma … desktop", "blue"), ("acks/ID", "link: esclusivo", "green"),
            ("Terminale", "conferma … pts/3", "blue")], [
    (0, 1, "link: riesce"),
    (2, 1, "link: fallisce, esiste già", True),
    ("nota", 2, "esiste(ack): segna_letto, esito 0"),
    ("nota", 0, "CONFERMATO (desktop)"),
    ("sep", "un secondo dopo, l'altra domanda aperta"),
    (2, 1, "acks/ID comparso?"),
    ("nota", 2, "«già confermato altrove»"),
], "«FIG» — Due conferme quasi contemporanee: vale la prima", "La prima conferma vince")

S2 = p("Un utente può avere la finestra aperta sul desktop e la domanda in due terminali. La conferma dev'essere "
       "<b>una</b>: la prima che arriva.", lead=True) + RACE + ul([
    "Due conferme quasi contemporanee producono una sola registrazione: " + c("link") + " riesce una volta sola; "
    "l'altra trova " + c("acks/ID") + " e si limita a spostare il messaggio.",
    "Le domande e le finestre ancora aperte se ne accorgono al loro controllo successivo (entro un secondo) e si "
    "chiudono: «Messaggio già confermato altrove (per esempio dal desktop).» nel terminale, la finestra si chiude "
    "da sola (scenari C4b e I5).",
    "Questa regola è nata da una prova dal vivo del prototipo: l'utente doveva confermare due volte, dalla "
    "finestra e dal terminale.",
])

S3 = p(c("ams status") + " legge le conferme dalla casella, che l'utente controlla. Per questo le tratta come "
       "<b>dati non fidati</b>, e il loro significato è volutamente limitato.", lead=True) + table(
    ["Rischio", "Regola"], [
        ["un collegamento simbolico " + c("acks/ID") + " verso un file riservato", "la lettura avviene come l'utente "
         "(" + cap(7) + "): un file che l'utente non può leggere non si legge"],
        ["una pipe o un dispositivo al posto della conferma", "si legge solo un file normale, aperto senza bloccarsi"],
        ["una conferma enorme", "si leggono al più 200 byte, e della prima riga"],
        ["sequenze di escape nel canale", "l'uscita passa da " + c("pulisci") + " (scenario G3)"],
        ["una data fasulla", "è un numero qualunque: vale solo se non supera scadenza e ritiro di " + c("sent/")],
    ], "«TAB» — Le conferme lette da root") + \
    note("<b>«Confermato» vuol dire</b>: nella casella c'è una dichiarazione di lettura valida dell'utente. Non è "
         "un'azione osservata da AMS né una prova di lettura: l'utente controlla la propria casella e potrebbe "
         "scriverla da sé, come potrebbe premere «Ho letto» senza leggere. Chi usa " + c("ams status")
         + " per un audit deve leggerlo così (" + cap(20, 1) + ").")

CHAPTER = ("Le conferme", [
    ("Vale la prima", S1),
    ("Due conferme contemporanee", S2),
    ("Le conferme lette da root", S3),
])
