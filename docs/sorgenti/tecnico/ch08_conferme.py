from build import c, code, p, seq, table, ul

RACE = seq([("Finestra", "conferma … desktop", "blue"), ("acks/ID", "link: esclusivo", "green"), ("Terminale", "conferma … terminale", "blue")], [
    (0, 1, "crea il file: riesce"),
    (2, 1, "crea il file: fallisce, esiste già", True),
    (2, 2, "si limita a segna_letto"),
    (0, 0, "registra nel journal"),
], "«FIG» — Due conferme quasi contemporanee: vale la prima", "La prima conferma vince")

S1 = p(c("conferma(ID, CANALE)") + " scrive la conferma in un file temporaneo, lo porta su disco e lo pubblica con "
       + c("link") + ", che fallisce "
       "se " + c("acks/ID") + " esiste già. La conferma nasce quindi completa o non nasce, e «già confermato» resta "
       "distinto da «scrittura fallita».", lead=True) + code(
    """static int conferma(long long id, const char *canale)
{
	if (esiste(ack)) { segna_letto(id); return 0; }       /* vale la prima */
	if (!c_e("inbox", id, "")) return 3;                 /* ritirato: niente conferma */
	if (scaduto(id)) { segna_letto(id); return 2; }
	fd = open(tmp, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0644);
	if (fd < 0 || scrivi_tutto(fd, riga, n) < 0 || fsync(fd) < 0 || close(fd) < 0 ||
	    link(tmp, ack) < 0) {                              /* link fallisce se acks/ID esiste */
		unlink(tmp);
		if (esiste(ack)) { segna_letto(id); return 0; }
		evento("CONFERMA_FALLITA", id, U, canale, strerror(errno), "");
		return 1;                                         /* il messaggio resta nella casella */
	}
	unlink(tmp);
	sync_path(acks);                                      /* su disco prima di «Confermato» */
	segna_letto(id);
	evento("CONFERMATO", id, U, canale, "", "");
	return 0;
}""", "c", "src/ams-user.c (in breve)") + table(["Caso", "Esito", "Messaggio"], [
        ["conferma scritta", "0", "passa in " + c("read/") + "; evento nel registro"],
        [c("acks/ID") + " già presente", "0", "passa in " + c("read/") + "; resta la prima conferma"],
        ["scrittura fallita (disco pieno, permessi)", "1", "<b>resta in " + c("inbox/")
         + "</b>; l'utente è avvisato, l'errore va nel registro, la domanda o la finestra tornano"],
        ["messaggio scaduto", "2", "passa in " + c("read/") + " senza conferma: una conferma dopo la scadenza non vale"],
        ["copia sparita (messaggio ritirato)", "3", "nessuna conferma; se il ritiro arriva fra il controllo e "
         + c("link") + ", " + c("ams status") + " non conta la conferma perché la sua data è successiva al ritiro"],
    ], "«TAB» — Gli esiti di conferma") + RACE + \
    p("Due conferme quasi contemporanee, dalla finestra e da un terminale, producono una sola registrazione. Il canale è "
      + c("desktop") + " oppure " + c("terminale pts/N") + " (" + c("terminale tty3") + " per una console).")

S2 = p(c("ams status") + " legge le conferme dalla casella, che l'utente controlla. Per questo le tratta come dati non "
       "fidati:", lead=True) + ul([
    "le legge <b>come l'utente</b>, in un processo figlio con la sua identità: un collegamento simbolico verso un file riservato non "
    "funziona, perché l'utente non potrebbe leggerlo;",
    "ne legge al massimo <b>200 byte</b>, solo da un file normale (non una pipe né un dispositivo), ripuliti con " + c("pulisci") + ";",
    "della riga usa un <b>numero</b> (la data, 0 se non lo è) e il resto come nome del canale.",
]) + p("Una conferma fabbricata dall'utente non può quindi far leggere a root file d'altri, né portare sequenze di escape "
       "nel terminale dell'amministratore. Resta una dichiarazione dell'utente, come il clic su «Ho letto».")

CHAPTER = ("Le conferme", [
    ("Vale la prima", S1),
    ("Lettura da parte di root", S2),
])
