from build import arrow, box, c, code, fig, note, p, seq, table, text, ul, zone


def cap(n, s=None):
    return f'<a href="#ch{n}{"s" + str(s) if s else ""}">capitolo {n}{"." + str(s) if s else ""}</a>'


SYMLINK = fig(
    zone(20, 44, 420, 214, "Se root scrivesse direttamente", "#fdf2f2")
    + box(44, 84, 150, 54, "ams (root)", "scrive inbox/12", "navy")
    + box(262, 84, 156, 54, "users/mario/inbox", "sostituita da Mario…", "amber", 12)
    + box(262, 176, 156, 54, "/etc", "…con un collegamento", "grey")
    + arrow(196, 111, 260, 111, "#b91c1c")
    + arrow(340, 140, 340, 174, "#b91c1c", True)
    + text(130, 206, "root scriverebbe", 11.5, "#b91c1c", "700")
    + text(130, 224, "dentro /etc", 11.5, "#b91c1c", "700")
    + zone(470, 44, 410, 214, "Con come_utente", "#f0fdf4")
    + box(494, 84, 150, 54, "ams (root)", "come_utente(mario)", "navy")
    + box(704, 84, 156, 54, "figlio (mario)", "scrive inbox/12", "light")
    + box(704, 176, 156, 54, "/etc", "permesso negato", "grey")
    + arrow(646, 111, 702, 111, "#16a34a")
    + arrow(782, 140, 782, 174, "#475569", True)
    + text(580, 206, "il peggio: Mario", 11.5, "#166534", "700")
    + text(580, 224, "rovina la sua casella", 11.5, "#166534", "700"),
    900, 276, "«FIG» — Perché root accede alle caselle con l'identità dell'utente",
    "Il pericolo dei collegamenti simbolici")

S1 = p("La casella " + c("users/U") + " appartiene all'utente, che può sostituirne le sottocartelle con "
       "collegamenti simbolici, pipe o file strani. Se root ci scrivesse direttamente, seguirebbe il collegamento "
       "e potrebbe scrivere ovunque; se ci leggesse, potrebbe mostrare file che l'utente non può leggere. Per questo "
       "<b>ogni accesso di root al contenuto di una casella avviene in un processo figlio con l'identità "
       "dell'utente</b>: " + c("come_utente") + " di " + c("src/utente.c") + ", al posto di " + c("runuser")
       + " usato dal prototipo.", lead=True) + SYMLINK + \
    p("Nel figlio valgono i permessi dell'utente: un collegamento verso " + c("/etc") + " porta a «permesso "
      "negato», e il peggio che l'utente può ottenere è rovinare la propria copia. Lo scenario G1 della macchina di "
      "prova lo verifica: con la casella trasformata in collegamento a " + c("/etc") + ", " + c("ams send") + " non "
      "scrive nulla in " + c("/etc") + " e il destinatario resta «inviato, non consegnato».") + \
    note("solo la cartella " + c("users/U") + " stessa è toccata da root: la crea (" + c("700") + ") dentro "
         + c("users/") + ", che appartiene a root, e la cede a U con " + c("lchown") + ". Se esiste già deve essere "
         "una cartella vera (" + c("lstat") + "); se è rimasta di root, per un invio interrotto fra la creazione e la "
         "cessione, viene ceduta al primo invio (scenario F6).")

FIGLIO = seq([("ams (root)", "come_utente", "navy"), ("pipe", "stdin · stdout", "soft"),
              ("figlio", "fork", "dark"), ("figlio come U", "fn(arg)", "blue")], [
    (0, 2, "fork"),
    ("nota", 2, "stdin e stdout sulle pipe"),
    (2, 3, "initgroups, setresgid, setresuid"),
    ("nota", 3, "setuid(0) deve fallire"),
    (0, 1, "dati su stdin"),
    (3, 1, "uscita, al più max byte", True),
    ("sep", "entro il tempo massimo"),
    (3, 0, "codice di uscita (waitpid)", True),
    ("nota", 0, "tempo scaduto: SIGKILL"),
], "«FIG» — Come nasce e come finisce il processo figlio", "Un figlio con l'identità dell'utente")

S2 = p(c("come_utente(u, fn, arg, in, out, max, secondi)") + " esegue " + c("fn(arg)") + " in un processo figlio "
       "con l'identità di " + c("u") + ". Il padre gli passa dati su stdin, ne raccoglie l'uscita su una pipe e ne "
       "attende la fine, sempre con un tempo massimo.", lead=True) + FIGLIO + code("""static void figlio(const utente_t *u, come_utente_fn fn, void *arg, int in, int out)
{
	/* stdin e stdout sulle pipe, stderr su /dev/null */
	if (geteuid() == 0 && !ams_test) {
		/* identità completa dell'utente: gruppi, poi gruppo, poi utente */
		if (initgroups(u->nome, u->gid) < 0 || setresgid(u->gid, u->gid, u->gid) < 0 ||
		    setresuid(u->uid, u->uid, u->uid) < 0)
			_exit(126);
		if (getuid() != u->uid || geteuid() != u->uid || getegid() != u->gid || setuid(0) == 0)
			_exit(126);                       /* se torna root, qualcosa non va */
	}
	if (chdir("/") < 0)
		_exit(126);
	umask(022);
	_exit(fn(arg) & 0xff);
}""", "c", "src/utente.c (in breve)") + ul([
    "L'ordine conta: prima i gruppi supplementari (" + c("initgroups") + "), poi il gruppo, poi l'utente; dopo "
    + c("setresuid") + " non si può più cambiare gruppo.",
    "Il figlio verifica di <b>non</b> poter tornare root: se " + c("setuid(0)") + " riuscisse, l'identità non "
    "sarebbe stata assunta davvero. Qualunque anomalia termina con il codice 126, che il padre traduce in errore.",
    "Dopo il cambio d'identità il kernel rende il processo non ispezionabile dall'utente (non «dumpable»): U non "
    "può leggerne la memoria mentre lavora.",
    "In modalità di prova, senza root, il figlio resta con l'identità di chi lancia la prova.",
])

S3 = p("Il figlio gira con l'identità dell'utente, quindi l'utente può fermarlo (" + c("SIGSTOP") + ") o "
       "rallentarlo. " + c("ams") + " non deve restare appeso: il tempo massimo vale sia mentre il figlio scrive sia "
       "dopo, finché non esce.", lead=True) + table(["Esito di come_utente", "Quando"], [
    ["il codice di uscita di " + c("fn") + " (0–125, 127–255)", "il figlio è uscito normalmente"],
    [c("-1"), "il figlio non è partito (" + c("pipe2") + ", " + c("fork") + "); non ha potuto assumere l'identità "
     "(codice 126); è stato ucciso da un segnale; il tempo è scaduto (il padre lo uccide con " + c("SIGKILL") + ")"],
], "«TAB» — Gli esiti di come_utente") + table(["Chiamata", "Tempo massimo", "Uscita raccolta"], [
    ["consegna, ritiro, sollecito, cancellazione", "20 s", "nessuna: conta il codice"],
    ["lettura di una casella (" + c("leggi_casella") + ")", "20 s", "al più 4 MiB"],
    ["sveglia dell'agente", "5 s", "nessuna"],
    ["ambiente di un processo del terminale", "5 s", "al più 1 MiB"],
], "«TAB» — I tempi massimi") + \
    p("Le pipe sono create con " + c("O_CLOEXEC") + "; lo stdin del figlio si scrive in modo non bloccante, "
      "alternato alla lettura dell'uscita con " + c("poll") + " (al più un secondo per giro), così un figlio che non "
      "legge non blocca il padre. L'analisi statica di gcc ha trovato pipe non chiuse in un caso d'errore di "
      + c("come_utente") + ": corrette (" + cap(21, 7) + ").")

S4 = p("Tutte le operazioni sulle caselle sono funzioni di " + c("src/archivio.c") + " che girano dentro il figlio. "
       "Sono piccole di proposito: fanno una cosa, con percorsi costruiti dal numero del messaggio.", lead=True) + \
    table(["Operazione", "Chiamata da", "Nel figlio (come U)", "Esito"], [
        [c("op_consegna"), c("consegna_copia") + ": invio e recupero", "crea " + c("inbox read acks state")
         + " se mancano; se il messaggio è già in " + c("read/") + " o " + c("acks/") + " non fa nulla; altrimenti "
         "scrive " + c("inbox/ID.tmp") + " (" + c("O_EXCL|O_NOFOLLOW") + "), lo rinomina e controlla che "
         + c("inbox/ID") + " sia un file normale non vuoto", "0 se la copia c'è (o era già letta)"],
        [c("op_togli"), c("togli_copia") + ": ritiro", "toglie " + c("inbox/ID") + ", " + c("state/ID.term")
         + " e " + c("state/ID.gui"), "0 se la copia non c'è più"],
        [c("op_togli_rinvii"), c("togli_rinvii") + ": sollecito", "toglie " + c("state/ID.term") + " e "
         + c("state/ID.gui"), "0 se non ne restano"],
        [c("op_cancella"), c("cancella_copie") + ": cancellazione", "toglie " + c("inbox/ID") + ", " + c("read/ID")
         + ", " + c("acks/ID") + " e i rinvii", "sempre 0"],
        [c("op_leggi"), c("leggi_casella") + ": " + c("list") + ", " + c("status") + ", TUI", "per ogni ID ricevuto "
         "su stdin: prima riga di " + c("acks/ID") + " (al più 200 byte, solo da un file normale) e data più "
         "recente di " + c("state/ID.*"), "righe «A ID riga» e «S ID data» (" + cap(10, 2) + ")"],
        [c("op_sveglia"), c("sveglia_agente"), "legge il PID pronto, controlla la riga di comando, manda "
         + c("SIGUSR1"), "0 se svegliato (" + cap(8, 5) + ")"],
        [c("op_environ"), c("lingua_terminale"), "legge " + c("/proc/PID/environ") + " quando root non può "
         "(un container senza " + c("CAP_SYS_PTRACE") + ")", "l'ambiente su stdout (" + cap(16, 1) + ")"],
    ], "«TAB» — Le operazioni eseguite come l'utente") + \
    note("il ritiro e la cancellazione non chiedono all'utente se la cartella esiste: se " + c("users/U")
         + " non c'è (utente mai raggiunto) non c'è nulla da togliere e l'operazione riesce senza lanciare il figlio.")

CHAPTER = ("Root con l'identità dell'utente", [
    ("Il pericolo dei collegamenti simbolici", S1),
    ("Come nasce il processo figlio", S2),
    ("Tempi massimi ed esiti", S3),
    ("Le operazioni sulle caselle", S4),
])
