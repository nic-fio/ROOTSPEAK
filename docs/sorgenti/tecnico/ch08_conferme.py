from build import c, code, p, seq, table, ul

RACE = seq([("Finestra", "ack … desktop", "blue"), ("acks/ID", "ln: esclusivo", "green"), ("Terminale", "ack … terminale", "blue")], [
    (0, 1, "crea il file: riesce"),
    (2, 1, "crea il file: fallisce, esiste già", True),
    (2, 2, "si limita a mark_read"),
    (0, 0, "registra nel journal"),
], "«FIG» — Due conferme quasi contemporanee: vale la prima", "La prima conferma vince")

S1 = p(c("ack ID CANALE") + " scrive la conferma in un file temporaneo e la pubblica con " + c("ln") + ", che fallisce "
       "se " + c("acks/ID") + " esiste già. La conferma nasce quindi completa o non nasce, e «già confermato» resta "
       "distinto da «scrittura fallita».", lead=True) + code(
    """ack() {
	local tmp=$D/acks/.$1.$$ err
	if [ -e "$D/acks/$1" ]; then mark_read "$1"; return 0; fi
	if ! err=$({ printf '%s %s\\n' "$(date +%s)" "$2" >"$tmp" && ln "$tmp" "$D/acks/$1"; } 2>&1); then
		rm -f "$tmp"
		if [ -e "$D/acks/$1" ]; then mark_read "$1"; return 0; fi
		ams_log "utente $U: ERRORE, conferma del messaggio $1 non registrata ($2): $err"
		return 1
	fi
	rm -f "$tmp"
	mark_read "$1"
	ams_log "utente $U: confermata la lettura del messaggio $1 ($2)"
}""", "bash", "lib/ams-user") + table(["Caso", "Esito", "Messaggio"], [
        ["conferma scritta", "0", "passa in " + c("read/") + "; evento nel registro"],
        [c("acks/ID") + " già presente", "0", "passa in " + c("read/") + "; resta la prima conferma"],
        ["scrittura fallita (disco pieno, permessi)", "1", "<b>resta in " + c("inbox/")
         + "</b>; l'utente è avvisato, l'errore va nel registro, la domanda o la finestra tornano"],
    ], "«TAB» — Gli esiti di ack") + RACE + \
    p("Due conferme quasi contemporanee, dalla finestra e da un terminale, producono una sola registrazione. Il canale è "
      + c("desktop") + " oppure " + c("terminale pts/N") + " (" + c("terminale tty3") + " per una console).")

S2 = p(c("ams status") + " legge le conferme dalla casella, che l'utente controlla. Per questo le tratta come dati non "
       "fidati:", lead=True) + ul([
    "le legge <b>come l'utente</b> (" + c("as_user U cat") + "): un collegamento simbolico verso un file riservato non "
    "funziona, perché l'utente non potrebbe leggerlo;",
    "ne legge al massimo <b>200 byte</b>, ripuliti con " + c("ams_sanitize") + ";",
    "della riga usa un <b>numero</b> (la data, 0 se non lo è) e il resto come nome del canale.",
]) + p("Una conferma fabbricata dall'utente non può quindi far leggere a root file d'altri, né portare sequenze di escape "
       "nel terminale dell'amministratore. Resta una dichiarazione dell'utente, come il clic su «Ho letto».")

CHAPTER = ("Le conferme", [
    ("Vale la prima", S1),
    ("Lettura da parte di root", S2),
])
