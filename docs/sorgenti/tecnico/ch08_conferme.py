from build import c, code, p, seq, ul

RACE = seq([("Finestra", "ack … desktop", "blue"), ("acks/ID", "set -C", "green"), ("Terminale", "ack … terminale", "blue")], [
    (0, 1, "crea il file: riesce"),
    (2, 1, "crea il file: fallisce, esiste già", True),
    (2, 2, "si limita a mark_read"),
    (0, 0, "registra nel journal"),
], "«FIG» — Due conferme quasi contemporanee: vale la prima", "La prima conferma vince")

S1 = p(c("ack ID CANALE") + " scrive " + c("acks/ID") + " in una subshell con " + c("set -C") + " (noclobber): la "
       "creazione fallisce se il file esiste già.", lead=True) + code(
    """ack() {
	if ! (set -C; printf '%s %s\\n' "$(date +%s)" "$2" >"$D/acks/$1") 2>/dev/null; then
		mark_read "$1"
		return
	fi
	mark_read "$1"
	ams_log "utente $U: confermata la lettura del messaggio $1 ($2)"
}""", "bash", "lib/ams-user") + RACE + \
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
